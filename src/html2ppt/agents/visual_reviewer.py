"""Visual reviewer agent for VLM-based screenshot analysis.

Uses Vision-Language Models to analyze rendered slide screenshots
and provide visual quality feedback.
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError

from html2ppt.agents.prompts import get_visual_fix_prompt, get_visual_review_prompt
from html2ppt.agents.state import OutlineSection
from html2ppt.config.logging import get_logger
from html2ppt.config.reflection import ReflectionConfig
from html2ppt.services.renderer import ScreenshotRenderer, ScreenshotResult

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

logger = get_logger(__name__)


class VisualIssue(BaseModel):
    """A single visual issue found in the screenshot."""

    type: str = Field(description="Issue category (e.g., text_overflow, element_overlap)")
    description: str = Field(description="Specific description of the issue")
    location: str = Field(default="unknown", description="Where on the slide")
    severity: str = Field(default="medium", description="high, medium, or low")


class VisualVerdict(BaseModel):
    """Structured verdict from visual analysis."""

    has_issues: bool = Field(default=False, description="Whether any visual issues were found")
    issues: list[VisualIssue] = Field(default_factory=list, description="List of visual issues")
    fix_suggestions: list[str] = Field(
        default_factory=list,
        description="Specific CSS/layout fixes to apply",
    )


@dataclass(frozen=True)
class VisualReviewResult:
    """Result of visual review for a single component."""

    code: str
    warnings: list[str]
    visual_retry_count: int
    screenshot_captured: bool = False


class VisualReviewer:
    """VLM-based visual quality reviewer for rendered components."""

    _VLM_SYSTEM_PROMPT = "You are a professional UI/UX design expert analyzing slide screenshots."
    _FIX_SYSTEM_PROMPT = "你是一位专业的Vue前端开发工程师，擅长修复视觉问题。"

    def __init__(
        self,
        vlm: "BaseChatModel",
        generator_llm: "BaseChatModel",
        config: ReflectionConfig,
        renderer: ScreenshotRenderer | None = None,
    ) -> None:
        self.vlm = vlm
        self.generator_llm = generator_llm
        self.config = config
        self.renderer = renderer or ScreenshotRenderer(
            browserless_url=config.renderer_url,
            vue_preview_url=config.vue_preview_url,
            timeout_ms=config.visual_review_timeout_ms,
        )

    async def review_and_fix(
        self,
        *,
        section: OutlineSection,
        code: str,
        design_system: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> VisualReviewResult:
        """Perform visual review and fix cycle on a component.

        Args:
            section: The outline section being reviewed
            code: Vue SFC code to review
            design_system: Optional design system for context
            session_id: Optional session ID for logging

        Returns:
            VisualReviewResult with potentially fixed code
        """
        if not self.config.enable_visual_review:
            return VisualReviewResult(
                code=code,
                warnings=[],
                visual_retry_count=0,
                screenshot_captured=False,
            )

        current_code = code
        visual_retry_count = 0
        warnings: list[str] = []
        screenshot_captured = False

        while visual_retry_count < self.config.max_visual_retries:
            # Capture screenshot
            screenshot_result = await self._capture_screenshot(
                code=current_code,
                session_id=session_id,
            )

            if not screenshot_result.success:
                logger.warning(
                    "Screenshot capture failed, skipping visual review",
                    session_id=session_id,
                    error=screenshot_result.error,
                )
                warnings.append(f"Screenshot failed: {screenshot_result.error}")
                break

            screenshot_captured = True

            # Analyze screenshot with VLM
            verdict = await self._analyze_screenshot(
                image_bytes=screenshot_result.image_bytes,
                section=section,
                design_system=design_system,
                session_id=session_id,
            )

            if not verdict.has_issues:
                logger.info(
                    "Visual review passed",
                    session_id=session_id,
                    section_title=section.title,
                )
                break

            # Log issues found
            issue_descriptions = [
                f"{i.type}({i.severity}): {i.description}" for i in verdict.issues
            ]
            logger.info(
                "Visual issues found",
                session_id=session_id,
                section_title=section.title,
                issues=issue_descriptions,
            )

            # Attempt to fix
            visual_retry_count += 1

            try:
                fixed_code = await self._fix_visual_issues(
                    section=section,
                    code=current_code,
                    verdict=verdict,
                    design_system=design_system,
                    session_id=session_id,
                )
                current_code = fixed_code
            except Exception as exc:
                logger.warning(
                    "Visual fix failed",
                    session_id=session_id,
                    error=str(exc),
                )
                warnings.extend(issue_descriptions)
                break

        # If we exhausted retries, add remaining issues as warnings
        if visual_retry_count >= self.config.max_visual_retries:
            warnings.append(
                f"Visual review reached max retries ({self.config.max_visual_retries})"
            )

        return VisualReviewResult(
            code=current_code,
            warnings=warnings,
            visual_retry_count=visual_retry_count,
            screenshot_captured=screenshot_captured,
        )

    async def _capture_screenshot(
        self,
        *,
        code: str,
        session_id: str | None,
    ) -> ScreenshotResult:
        """Capture screenshot of rendered component."""
        # Prefer using vue-preview-service for proper Vite/UnoCSS rendering
        return await self.renderer.capture_preview_screenshot(
            vue_code=code,
            width=1280,
            height=720,
            session_id=session_id,
        )

    async def _analyze_screenshot(
        self,
        *,
        image_bytes: bytes | None,
        section: OutlineSection,
        design_system: dict[str, Any] | None,
        session_id: str | None,
    ) -> VisualVerdict:
        """Analyze screenshot using VLM."""
        if not image_bytes:
            return VisualVerdict(has_issues=False)

        # Build requirement text from section
        requirement = f"Slide: {section.title}"
        if section.subtitle:
            requirement += f"\nSubtitle: {section.subtitle}"
        if section.points:
            requirement += "\nPoints: " + "; ".join(section.points[:5])

        prompt = get_visual_review_prompt(
            requirement=requirement,
            design_system=design_system,
        )

        # Encode image as base64
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Build multimodal message
        messages = [
            SystemMessage(content=self._VLM_SYSTEM_PROMPT),
            HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ]
            ),
        ]

        try:
            response = await self.vlm.ainvoke(messages)
            content = str(response.content)

            raw_json = self._extract_json(content)
            payload = json.loads(raw_json)

            return VisualVerdict.model_validate(payload)

        except json.JSONDecodeError as exc:
            logger.warning(
                "Visual verdict JSON parse failed",
                session_id=session_id,
                error=str(exc),
            )
            return VisualVerdict(has_issues=False)
        except ValidationError as exc:
            logger.warning(
                "Visual verdict validation failed",
                session_id=session_id,
                error=str(exc),
            )
            return VisualVerdict(has_issues=False)
        except Exception as exc:
            logger.warning(
                "VLM analysis failed",
                session_id=session_id,
                error=str(exc),
            )
            return VisualVerdict(has_issues=False)

    async def _fix_visual_issues(
        self,
        *,
        section: OutlineSection,
        code: str,
        verdict: VisualVerdict,
        design_system: dict[str, Any] | None,
        session_id: str | None,
    ) -> str:
        """Generate fixed code based on visual issues."""
        prompt = get_visual_fix_prompt(
            section_title=section.title,
            raw_outline=section.raw_content or "",
            original_code=code,
            visual_issues=[i.model_dump() for i in verdict.issues],
            fix_suggestions=verdict.fix_suggestions,
            design_system=design_system,
        )

        messages = [
            SystemMessage(content=self._FIX_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]

        response = await self.generator_llm.ainvoke(messages)
        return self._extract_code_block(str(response.content), "vue")

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from VLM response."""
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
        """Extract code block from LLM response."""
        pattern = rf"```{language}\s*([\s\S]*?)```"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

        match = re.search(r"```\s*([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()

        return text.strip()
