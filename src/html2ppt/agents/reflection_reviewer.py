"""Reflection reviewer for post-generation slide quality checks and rewrites."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError

from html2ppt.agents.prompts import get_reflection_review_prompt, get_reflection_rewrite_prompt, get_vue_fix_prompt
from html2ppt.agents.state import OutlineSection
from html2ppt.agents.validators import format_validation_errors_for_prompt, validate_vue_component
from html2ppt.config.logging import get_logger
from html2ppt.config.reflection import ReflectionConfig

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

    from html2ppt.agents.visual_reviewer import VisualReviewer

logger = get_logger(__name__)


_REVIEW_SYSTEM_PROMPT = "你是一位严格但务实的演示文稿审查员（Reflection Reviewer）。"
_REWRITE_SYSTEM_PROMPT = "你是一位专业的Vue前端开发工程师，擅长在保持内容的同时改进排版与可读性。"


class ReflectionVerdict(BaseModel):
    """Structured verdict for per-slide review."""

    should_rewrite: bool = Field(default=False, description="Whether to trigger a rewrite pass")
    issues: list[str] = Field(default_factory=list, description="Issue list, user-visible")
    rewrite_instructions: str = Field(
        default="",
        description="Concise rewrite instructions for the generator model",
    )


@dataclass(frozen=True)
class ReflectionResult:
    code: str
    warnings: list[str]
    retry_count: int
    visual_retry_count: int = 0


class ReflectionReviewer:
    """Review and optionally rewrite Vue components after generation."""

    def __init__(
        self,
        generator_llm: "BaseChatModel",
        evaluator_llm: "BaseChatModel",
        config: ReflectionConfig,
        visual_reviewer: "VisualReviewer | None" = None,
    ) -> None:
        self.generator_llm = generator_llm
        self.evaluator_llm = evaluator_llm
        self.config = config
        self.visual_reviewer = visual_reviewer

    async def review_and_rewrite(
        self,
        *,
        section: OutlineSection,
        code: str,
        design_system: Optional[dict[str, Any]] = None,
        session_id: str | None = None,
    ) -> ReflectionResult:
        if not self.config.enabled:
            return ReflectionResult(code=code, warnings=[], retry_count=0)

        retry_count = 0
        warnings: list[str] = []

        current_code = code
        while True:
            static_issues, root_fix_prompt = self._static_checks(section=section, code=current_code)

            verdict: ReflectionVerdict | None = None
            if self.config.enable_llm_review:
                verdict = await self._llm_review(
                    section=section,
                    code=current_code,
                    design_system=design_system,
                    static_issues=static_issues,
                    session_id=session_id,
                )

            should_rewrite = False
            rewrite_instructions = ""

            if root_fix_prompt:
                should_rewrite = True
                rewrite_instructions = ""
            elif static_issues:
                if verdict is None:
                    should_rewrite = True
                    rewrite_instructions = self._default_rewrite_instructions(static_issues)
                else:
                    should_rewrite = bool(verdict.should_rewrite)
                    rewrite_instructions = verdict.rewrite_instructions or ""
            else:
                if verdict and verdict.issues:
                    warnings = verdict.issues
                break

            if not should_rewrite or retry_count >= self.config.per_slide_max_rewrites:
                if root_fix_prompt:
                    warnings = static_issues
                elif verdict:
                    warnings = verdict.issues or static_issues
                else:
                    warnings = static_issues
                break

            retry_count += 1

            try:
                if root_fix_prompt:
                    next_code = await self._rewrite_with_prompt(
                        prompt=root_fix_prompt,
                        session_id=session_id,
                    )
                else:
                    rewrite_prompt = get_reflection_rewrite_prompt(
                        section_title=section.title,
                        raw_outline=section.raw_content or "",
                        original_code=current_code,
                        issues=(verdict.issues if verdict else static_issues),
                        rewrite_instructions=rewrite_instructions,
                        design_system=design_system,
                    )
                    next_code = await self._rewrite_with_prompt(
                        prompt=rewrite_prompt,
                        session_id=session_id,
                    )
            except Exception as exc:
                logger.warning(
                    "Reflection rewrite failed, keeping last version",
                    session_id=session_id,
                    error=str(exc),
                )
                warnings = (verdict.issues if verdict else []) or static_issues
                break

            current_code = next_code

        # Phase 2: Visual review (after static checks pass)
        visual_retry_count = 0
        if self.visual_reviewer and self.config.enable_visual_review:
            visual_result = await self.visual_reviewer.review_and_fix(
                section=section,
                code=current_code,
                design_system=design_system,
                session_id=session_id,
            )
            current_code = visual_result.code
            visual_retry_count = visual_result.visual_retry_count
            warnings.extend(visual_result.warnings)

            if visual_result.visual_retry_count > 0:
                logger.info(
                    "Visual review completed",
                    session_id=session_id,
                    section_title=section.title,
                    visual_retries=visual_result.visual_retry_count,
                    screenshot_captured=visual_result.screenshot_captured,
                )

        return ReflectionResult(
            code=current_code,
            warnings=warnings,
            retry_count=retry_count,
            visual_retry_count=visual_retry_count,
        )

    def _static_checks(self, *, section: OutlineSection, code: str) -> tuple[list[str], str | None]:
        issues: list[str] = []

        if self.config.enable_rule_point_density:
            if section.points and len(section.points) > self.config.max_points_per_slide:
                issues.append(
                    f"要点数量过多：{len(section.points)}，建议≤{self.config.max_points_per_slide}，可改为分栏/分组/图示呈现。"
                )
            if section.points:
                too_long = [p for p in section.points if len(p.strip()) > self.config.max_chars_per_point]
                if too_long:
                    issues.append(
                        f"单条要点过长：{len(too_long)} 条超过 {self.config.max_chars_per_point} 字符，建议缩短措辞或拆分。"
                    )

        if self.config.enable_rule_text_density:
            rough_chars = sum(len(p.strip()) for p in (section.points or []))
            if section.subtitle:
                rough_chars += len(section.subtitle.strip())
            if section.title:
                rough_chars += len(section.title.strip())
            if section.speaker_notes:
                rough_chars += min(len(section.speaker_notes.strip()), 200)
            if rough_chars > self.config.text_char_limit:
                issues.append(
                    f"文本密度偏高：估算字符数约 {rough_chars}，建议≤{self.config.text_char_limit}，可减少字数或改为图表/流程图。"
                )

        root_fix_prompt: str | None = None
        if self.config.enable_rule_root_container:
            validation_result = validate_vue_component(code)
            if not validation_result.is_valid:
                issues.extend(validation_result.errors + validation_result.warnings)
                error_text = format_validation_errors_for_prompt(validation_result)
                root_fix_prompt = get_vue_fix_prompt(code, error_text)

        return issues, root_fix_prompt

    async def _llm_review(
        self,
        *,
        section: OutlineSection,
        code: str,
        design_system: Optional[dict[str, Any]],
        static_issues: list[str],
        session_id: str | None,
    ) -> ReflectionVerdict:
        prompt = get_reflection_review_prompt(
            section_title=section.title,
            raw_outline=section.raw_content or "",
            vue_code=code,
            design_system=design_system,
            static_issues=static_issues,
        )

        messages = [
            SystemMessage(content=_REVIEW_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]

        response = await self.evaluator_llm.ainvoke(messages)
        content = str(response.content)

        raw_json = self._extract_json(content)
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            logger.warning(
                "Reflection verdict JSON parse failed",
                session_id=session_id,
                error=str(exc),
                raw_content=content[:500],
            )
            return ReflectionVerdict(
                should_rewrite=bool(static_issues),
                issues=static_issues,
                rewrite_instructions=self._default_rewrite_instructions(static_issues),
            )

        try:
            return ReflectionVerdict.model_validate(payload)
        except ValidationError as exc:
            logger.warning(
                "Reflection verdict validation failed",
                session_id=session_id,
                error=str(exc),
                payload=payload,
            )
            return ReflectionVerdict(
                should_rewrite=bool(static_issues),
                issues=static_issues,
                rewrite_instructions=self._default_rewrite_instructions(static_issues),
            )

    async def _rewrite_with_prompt(self, *, prompt: str, session_id: str | None) -> str:
        messages = [
            SystemMessage(content=_REWRITE_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        response = await self.generator_llm.ainvoke(messages)
        return self._extract_code_block(str(response.content), "vue")

    @staticmethod
    def _default_rewrite_instructions(issues: list[str]) -> str:
        if not issues:
            return ""
        return "；".join(issues)

    @staticmethod
    def _extract_json(text: str) -> str:
        match = re.search(r"```json\s*([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()

        match = re.search(r"```\s*([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1].strip()

        return text.strip()

    @staticmethod
    def _extract_code_block(text: str, language: str = "") -> str:
        pattern = rf"```{language}\s*([\s\S]*?)```"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

        match = re.search(r"```\s*([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()

        return text.strip()
