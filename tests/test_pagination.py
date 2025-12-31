import pytest

from html2ppt.agents.pagination import PaginationConfig, split_section_rules
from html2ppt.agents.state import OutlineSection


def _make_section(title: str, points: list[str], raw_content: str | None = None) -> OutlineSection:
    return OutlineSection(
        title=title,
        subtitle=None,
        points=points,
        visual_suggestions=None,
        animation_effects=None,
        speaker_notes=None,
        raw_content=raw_content,
    )


def _config(**overrides) -> PaginationConfig:
    base = PaginationConfig(
        enabled=True,
        max_bullets=5,
        max_chars=300,
        max_table_rows=2,
        max_passes=2,
        max_splits_per_section=3,
        refiner_enabled=False,
        continuation_suffix=" (续)",
    )
    return PaginationConfig(**{**base.__dict__, **overrides})


def test_split_section_by_bullets():
    points = [f"Point {i}" for i in range(7)]
    section = _make_section(
        "Intro",
        points,
        raw_content="*   **标题**: Intro\n\n*   **核心内容**:\n" + "\n".join(
            f"    *   {p}" for p in points
        ),
    )
    sections, warnings, changed, overflow = split_section_rules(section, _config())

    assert changed is True
    assert overflow is False
    assert warnings == []
    assert len(sections) == 2
    assert sections[0].title == "Intro"
    assert sections[1].title.endswith(" (续)")


def test_split_section_table_rows():
    raw_content = """*   **标题**: Table Slide

*   **核心内容**:
    *   对比表格如下。

| A | B |
| --- | --- |
| 1 | 2 |
| 3 | 4 |
| 5 | 6 |
"""
    section = _make_section("Table Slide", [], raw_content=raw_content)
    sections, warnings, changed, overflow = split_section_rules(section, _config(max_table_rows=2))

    assert changed is True
    assert overflow is False
    assert len(sections) == 2
    assert sections[0].title == "Table Slide"
    assert sections[1].title.endswith(" (续)")
    assert "| 1 | 2 |" in sections[0].raw_content
    assert "| 5 | 6 |" in sections[1].raw_content


def test_guardrail_merges_excess_splits():
    points = [f"Point {i}" for i in range(12)]
    section = _make_section("Guardrail", points)
    config = _config(max_bullets=3, max_splits_per_section=1)

    sections, warnings, changed, overflow = split_section_rules(section, config)

    assert changed is True
    assert len(sections) == 2
    assert warnings
