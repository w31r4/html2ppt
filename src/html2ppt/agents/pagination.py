"""Rule-based pagination helpers for outline sections."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from html2ppt.agents.state import AnimationEffect, Outline, OutlineSection, VisualSuggestion
from html2ppt.config.settings import Settings


@dataclass(frozen=True)
class PaginationConfig:
    enabled: bool
    max_bullets: int
    max_chars: int
    max_table_rows: int
    max_passes: int
    max_splits_per_section: int
    refiner_enabled: bool
    continuation_suffix: str


@dataclass(frozen=True)
class TableBlock:
    header: str
    separator: str
    rows: list[str]


@dataclass
class SectionChunk:
    points: list[str]
    table_rows: list[str] | None = None


def build_pagination_config(settings: Settings) -> PaginationConfig:
    return PaginationConfig(
        enabled=settings.pagination_enabled,
        max_bullets=settings.pagination_max_bullets,
        max_chars=settings.pagination_max_chars,
        max_table_rows=settings.pagination_max_table_rows,
        max_passes=settings.pagination_max_passes,
        max_splits_per_section=settings.pagination_max_splits_per_section,
        refiner_enabled=settings.pagination_refiner_enabled,
        continuation_suffix=settings.pagination_continuation_suffix,
    )


def build_outline_markdown(outline: Outline) -> str:
    lines: list[str] = [f"# {outline.title}", ""]
    for index, section in enumerate(outline.sections, start=1):
        lines.extend(["---", "", f"### Page {index}: {section.title}", ""])
        if section.raw_content:
            lines.append(section.raw_content.strip())
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def estimate_section_units(section: OutlineSection) -> int:
    total = _weighted_length(section.title or "")
    if section.subtitle:
        total += _weighted_length(section.subtitle)
    if section.points:
        total += sum(_weighted_length(point) for point in section.points)
    if section.speaker_notes:
        total += min(_weighted_length(section.speaker_notes), _weighted_limit_units(200))
    return total


def estimate_raw_units(raw_content: str | None) -> int:
    if not raw_content:
        return 0
    return _weighted_length(raw_content)


def count_table_rows(raw_content: str | None) -> int:
    block = extract_table_block(raw_content)
    return len(block.rows) if block else 0


def section_overflows(section: OutlineSection, config: PaginationConfig) -> bool:
    max_units = _weighted_limit_units(config.max_chars)
    if section.points and len(section.points) > config.max_bullets:
        return True
    if estimate_section_units(section) > max_units:
        return True
    if count_table_rows(section.raw_content) > config.max_table_rows:
        return True
    if not section.points and estimate_raw_units(section.raw_content) > max_units:
        return True
    return False


def split_section_rules(
    section: OutlineSection,
    config: PaginationConfig,
) -> tuple[list[OutlineSection], list[str], bool, bool]:
    warnings: list[str] = []
    if not section.points and not section.raw_content:
        return [section], warnings, False, False

    table_block = extract_table_block(section.raw_content)
    expanded_points, points_expanded = _expand_points(section.points, config)
    point_groups = _group_points(expanded_points, config)

    chunks = _build_chunks(point_groups, table_block, config)
    if not chunks:
        return [section], warnings, False, False

    max_sections = 1 + max(config.max_splits_per_section, 0)
    if len(chunks) > max_sections:
        warnings.append(
            f"Pagination guardrail hit for '{section.title}': split count "
            f"{len(chunks)} exceeds max {max_sections}. Merging overflow content."
        )
        _merge_chunks(chunks, max_sections)

    sections = _build_sections_from_chunks(section, chunks, config)
    changed = points_expanded or len(sections) > 1 or _table_split(table_block, config)

    overflow = any(section_overflows(candidate, config) for candidate in sections)
    return sections, warnings, changed, overflow


def build_sections_from_groups(
    section: OutlineSection,
    groups: list[list[str]],
    config: PaginationConfig,
) -> list[OutlineSection]:
    if not groups:
        return [section]
    chunks = [SectionChunk(points=list(group)) for group in groups]
    return _build_sections_from_chunks(section, chunks, config)


def extract_table_block(raw_content: str | None) -> TableBlock | None:
    if not raw_content:
        return None

    lines = [line.rstrip() for line in raw_content.splitlines()]
    for idx in range(len(lines) - 1):
        header = lines[idx].strip()
        separator = lines[idx + 1].strip()
        if "|" not in header:
            continue
        if not _is_table_separator(separator):
            continue

        rows: list[str] = []
        for row_line in lines[idx + 2 :]:
            row = row_line.strip()
            if not row or "|" not in row:
                break
            rows.append(row)
        if rows:
            return TableBlock(header=header, separator=separator, rows=rows)

    return None


def _table_split(table_block: TableBlock | None, config: PaginationConfig) -> bool:
    if not table_block:
        return False
    return len(table_block.rows) > config.max_table_rows


def _build_chunks(
    point_groups: list[list[str]],
    table_block: TableBlock | None,
    config: PaginationConfig,
) -> list[SectionChunk]:
    chunks: list[SectionChunk] = []

    if point_groups:
        for group in point_groups:
            chunks.append(SectionChunk(points=list(group)))
    elif not table_block:
        return [SectionChunk(points=[])]

    if table_block:
        table_chunks = _chunk_list(table_block.rows, config.max_table_rows)
        if not point_groups:
            chunks = []
            for rows in table_chunks:
                chunks.append(SectionChunk(points=[], table_rows=list(rows)))
        else:
            for rows in table_chunks:
                chunks.append(SectionChunk(points=[], table_rows=list(rows)))

    return chunks


def _merge_chunks(chunks: list[SectionChunk], max_sections: int) -> None:
    if max_sections <= 0 or len(chunks) <= max_sections:
        return
    last = chunks[max_sections - 1]
    overflow = chunks[max_sections:]
    for extra in overflow:
        last.points.extend(extra.points)
        if extra.table_rows:
            if last.table_rows is None:
                last.table_rows = []
            last.table_rows.extend(extra.table_rows)
    del chunks[max_sections:]


def _build_sections_from_chunks(
    section: OutlineSection,
    chunks: list[SectionChunk],
    config: PaginationConfig,
) -> list[OutlineSection]:
    sections: list[OutlineSection] = []
    for idx, chunk in enumerate(chunks):
        title = _apply_continuation_suffix(section.title, idx, config.continuation_suffix)
        subtitle = section.subtitle if idx == 0 else None
        speaker_notes = section.speaker_notes if idx == 0 else None
        table_block = None
        if chunk.table_rows:
            original_table = extract_table_block(section.raw_content)
            if original_table:
                table_block = TableBlock(
                    header=original_table.header,
                    separator=original_table.separator,
                    rows=list(chunk.table_rows),
                )

        raw_content = _build_section_raw_content(
            title=title,
            subtitle=subtitle,
            points=chunk.points,
            visual_suggestions=section.visual_suggestions,
            animation_effects=section.animation_effects,
            speaker_notes=speaker_notes,
            table_block=table_block,
        )

        sections.append(
            OutlineSection(
                title=title,
                subtitle=subtitle,
                points=list(chunk.points),
                visual_suggestions=section.visual_suggestions,
                animation_effects=section.animation_effects,
                speaker_notes=speaker_notes,
                raw_content=raw_content,
            )
        )
    return sections


def _build_section_raw_content(
    *,
    title: str,
    subtitle: str | None,
    points: list[str],
    visual_suggestions: VisualSuggestion | None,
    animation_effects: AnimationEffect | None,
    speaker_notes: str | None,
    table_block: TableBlock | None,
) -> str:
    lines: list[str] = [f"*   **标题**: {title}"]
    if subtitle:
        lines.append(f"*   **副标题**: {subtitle}")

    if points or table_block:
        lines.append("")
        lines.append("*   **核心内容**:")
        if points:
            for point in points:
                lines.append(f"    *   {point}")
        else:
            lines.append("    *   表格内容如下。")

    if visual_suggestions:
        lines.append("")
        lines.append("*   **视觉建议**:")
        if visual_suggestions.background:
            lines.append(f"    *   **背景**: {visual_suggestions.background}")
        if visual_suggestions.core_image:
            lines.append(f"    *   **核心图片**: {visual_suggestions.core_image}")
        if visual_suggestions.layout:
            lines.append(f"    *   **布局**: {visual_suggestions.layout}")
        if visual_suggestions.image_url:
            lines.append(f"    *   **图片链接**: {visual_suggestions.image_url}")

    if animation_effects:
        lines.append("")
        lines.append("*   **动画效果**:")
        if animation_effects.elements:
            for elem in animation_effects.elements:
                lines.append(f"    *   {elem}")
        else:
            lines.append(f"    *   {animation_effects.description}")

    if table_block:
        lines.append("")
        lines.append(table_block.header)
        lines.append(table_block.separator)
        lines.extend(table_block.rows)

    if speaker_notes:
        lines.append("")
        lines.append("<!-- speaker notes")
        lines.append(speaker_notes)
        lines.append("-->")

    return "\n".join(lines).strip()


def _expand_points(points: list[str], config: PaginationConfig) -> tuple[list[str], bool]:
    if not points:
        return [], False

    max_units = _weighted_limit_units(config.max_chars)
    expanded: list[str] = []
    changed = False
    for point in points:
        if _weighted_length(point) > max_units:
            segments = _split_point_text(point, max_units)
            expanded.extend(segments)
            changed = True
        else:
            expanded.append(point)
    return expanded, changed


def _group_points(points: list[str], config: PaginationConfig) -> list[list[str]]:
    if not points:
        return []
    max_units = _weighted_limit_units(config.max_chars)
    groups: list[list[str]] = []
    current: list[str] = []
    current_units = 0

    for point in points:
        point_units = _weighted_length(point)
        if current and (
            (config.max_bullets > 0 and len(current) + 1 > config.max_bullets)
            or (max_units > 0 and current_units + point_units > max_units)
        ):
            groups.append(current)
            current = []
            current_units = 0
        current.append(point)
        current_units += point_units

    if current:
        groups.append(current)

    return groups


def _split_point_text(text: str, max_units: int) -> list[str]:
    sentences = _split_sentences(text)
    if not sentences:
        return _chunk_text(text, max_units)

    groups: list[str] = []
    current = ""
    current_units = 0
    for sentence in sentences:
        sentence_units = _weighted_length(sentence)
        if current and max_units > 0 and current_units + sentence_units > max_units:
            groups.append(current.strip())
            current = ""
            current_units = 0
        current = f"{current}{sentence}".strip()
        current_units += sentence_units
    if current:
        groups.append(current.strip())

    output: list[str] = []
    for group in groups:
        if _weighted_length(group) > max_units and max_units > 0:
            output.extend(_chunk_text(group, max_units))
        else:
            output.append(group)
    return output


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[。！？.!?;；])\\s+", text.strip()) if part.strip()]


def _chunk_text(text: str, max_units: int) -> list[str]:
    if max_units <= 0:
        return [text]
    chunks: list[str] = []
    buffer: list[str] = []
    units = 0
    for char in text:
        char_units = _weighted_length(char)
        if buffer and units + char_units > max_units:
            chunks.append("".join(buffer).strip())
            buffer = []
            units = 0
        buffer.append(char)
        units += char_units
    if buffer:
        chunks.append("".join(buffer).strip())
    return [chunk for chunk in chunks if chunk]


def _weighted_limit_units(limit: int) -> int:
    return max(limit, 0) * 2


def _weighted_length(text: str) -> int:
    total = 0
    for char in text:
        if char.isspace():
            continue
        total += 2 if _is_cjk(char) else 1
    return total


def _is_cjk(char: str) -> bool:
    code = ord(char)
    return (
        0x4E00 <= code <= 0x9FFF
        or 0x3400 <= code <= 0x4DBF
        or 0x20000 <= code <= 0x2A6DF
        or 0x2A700 <= code <= 0x2B73F
        or 0x2B740 <= code <= 0x2B81F
        or 0x2B820 <= code <= 0x2CEAF
        or 0xF900 <= code <= 0xFAFF
    )


def _is_table_separator(line: str) -> bool:
    return bool(re.match(r"^\s*\|?[\s:-]+\|[\s|:-]*\|?\s*$", line))


def _chunk_list(items: Iterable[str], size: int) -> list[list[str]]:
    if size <= 0:
        return [list(items)]
    chunked: list[list[str]] = []
    current: list[str] = []
    for item in items:
        if len(current) >= size:
            chunked.append(current)
            current = []
        current.append(item)
    if current:
        chunked.append(current)
    return chunked


def _apply_continuation_suffix(title: str, index: int, suffix: str) -> str:
    if index == 0 or not suffix:
        return title
    if title.endswith(suffix):
        return title
    return f"{title}{suffix}"
