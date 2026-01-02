"""Unit tests for visual reviewer and renderer."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from html2ppt.agents.state import OutlineSection
from html2ppt.agents.visual_reviewer import (
    VisualIssue,
    VisualReviewResult,
    VisualReviewer,
    VisualVerdict,
)
from html2ppt.config.reflection import ReflectionConfig
from html2ppt.services.renderer import ScreenshotRenderer, ScreenshotResult


class TestScreenshotResult:
    """Tests for ScreenshotResult dataclass."""

    def test_success_result(self):
        result = ScreenshotResult(
            success=True,
            image_bytes=b"fake_image_data",
        )
        assert result.success is True
        assert result.image_bytes == b"fake_image_data"
        assert result.error is None

    def test_failure_result(self):
        result = ScreenshotResult(
            success=False,
            error="Connection timeout",
        )
        assert result.success is False
        assert result.image_bytes is None
        assert result.error == "Connection timeout"


class TestVisualVerdict:
    """Tests for VisualVerdict model."""

    def test_no_issues(self):
        verdict = VisualVerdict(has_issues=False)
        assert verdict.has_issues is False
        assert verdict.issues == []
        assert verdict.fix_suggestions == []

    def test_with_issues(self):
        verdict = VisualVerdict(
            has_issues=True,
            issues=[
                VisualIssue(
                    type="text_overflow",
                    description="Title extends beyond container",
                    location="top-center",
                    severity="high",
                )
            ],
            fix_suggestions=["Reduce font size", "Add text-overflow: ellipsis"],
        )
        assert verdict.has_issues is True
        assert len(verdict.issues) == 1
        assert verdict.issues[0].type == "text_overflow"
        assert len(verdict.fix_suggestions) == 2

    def test_parse_from_dict(self):
        data = {
            "has_issues": True,
            "issues": [
                {
                    "type": "element_overlap",
                    "description": "Image covers text",
                    "location": "center",
                    "severity": "medium",
                }
            ],
            "fix_suggestions": ["Add z-index"],
        }
        verdict = VisualVerdict.model_validate(data)
        assert verdict.has_issues is True
        assert verdict.issues[0].type == "element_overlap"


class TestVisualReviewResult:
    """Tests for VisualReviewResult dataclass."""

    def test_result_with_screenshot(self):
        result = VisualReviewResult(
            code="<template><div>Test</div></template>",
            warnings=["Minor alignment issue"],
            visual_retry_count=1,
            screenshot_captured=True,
        )
        assert result.screenshot_captured is True
        assert result.visual_retry_count == 1
        assert len(result.warnings) == 1

    def test_result_without_screenshot(self):
        result = VisualReviewResult(
            code="<template><div>Test</div></template>",
            warnings=["Screenshot failed"],
            visual_retry_count=0,
            screenshot_captured=False,
        )
        assert result.screenshot_captured is False


class TestVisualReviewerDisabled:
    """Tests for VisualReviewer when disabled."""

    @pytest.mark.asyncio
    async def test_skips_when_disabled(self):
        config = ReflectionConfig(enabled=True, enable_visual_review=False)
        mock_vlm = MagicMock()
        mock_generator = MagicMock()

        reviewer = VisualReviewer(
            vlm=mock_vlm,
            generator_llm=mock_generator,
            config=config,
        )

        section = OutlineSection(title="Test Slide", points=["Point 1"])
        code = "<template><div class='h-full w-full'>Test</div></template>"

        result = await reviewer.review_and_fix(
            section=section,
            code=code,
            session_id="test-session",
        )

        assert result.code == code
        assert result.visual_retry_count == 0
        assert result.screenshot_captured is False
        assert result.warnings == []


class TestVisualReviewerEnabled:
    """Tests for VisualReviewer when enabled."""

    @pytest.mark.asyncio
    async def test_passes_when_no_issues(self):
        config = ReflectionConfig(
            enabled=True,
            enable_visual_review=True,
            max_visual_retries=2,
        )

        mock_vlm = AsyncMock()
        mock_vlm.ainvoke.return_value = MagicMock(
            content='{"has_issues": false, "issues": [], "fix_suggestions": []}'
        )

        mock_generator = AsyncMock()
        mock_renderer = AsyncMock(spec=ScreenshotRenderer)
        mock_renderer.capture_preview_screenshot.return_value = ScreenshotResult(
            success=True,
            image_bytes=b"fake_png_data",
        )

        reviewer = VisualReviewer(
            vlm=mock_vlm,
            generator_llm=mock_generator,
            config=config,
            renderer=mock_renderer,
        )

        section = OutlineSection(title="Test Slide", points=["Point 1"])
        code = "<template><div class='h-full w-full'>Test</div></template>"

        result = await reviewer.review_and_fix(
            section=section,
            code=code,
            session_id="test-session",
        )

        assert result.code == code
        assert result.visual_retry_count == 0
        assert result.screenshot_captured is True
        assert result.warnings == []

    @pytest.mark.asyncio
    async def test_fixes_issues(self):
        config = ReflectionConfig(
            enabled=True,
            enable_visual_review=True,
            max_visual_retries=2,
        )

        # First VLM call returns issues, second returns pass
        mock_vlm = AsyncMock()
        mock_vlm.ainvoke.side_effect = [
            MagicMock(
                content='{"has_issues": true, "issues": [{"type": "text_overflow", "description": "Title too long", "location": "top", "severity": "high"}], "fix_suggestions": ["Reduce font size"]}'
            ),
            MagicMock(
                content='{"has_issues": false, "issues": [], "fix_suggestions": []}'
            ),
        ]

        mock_generator = AsyncMock()
        mock_generator.ainvoke.return_value = MagicMock(
            content="```vue\n<template><div class='h-full w-full'>Fixed</div></template>\n```"
        )

        mock_renderer = AsyncMock(spec=ScreenshotRenderer)
        mock_renderer.capture_preview_screenshot.return_value = ScreenshotResult(
            success=True,
            image_bytes=b"fake_png_data",
        )

        reviewer = VisualReviewer(
            vlm=mock_vlm,
            generator_llm=mock_generator,
            config=config,
            renderer=mock_renderer,
        )

        section = OutlineSection(title="Test Slide", points=["Point 1"])
        code = "<template><div class='h-full w-full'>Original</div></template>"

        result = await reviewer.review_and_fix(
            section=section,
            code=code,
            session_id="test-session",
        )

        assert "Fixed" in result.code
        assert result.visual_retry_count == 1
        assert result.screenshot_captured is True

    @pytest.mark.asyncio
    async def test_handles_screenshot_failure(self):
        config = ReflectionConfig(
            enabled=True,
            enable_visual_review=True,
        )

        mock_vlm = AsyncMock()
        mock_generator = AsyncMock()
        mock_renderer = AsyncMock(spec=ScreenshotRenderer)
        mock_renderer.capture_preview_screenshot.return_value = ScreenshotResult(
            success=False,
            error="Connection refused",
        )

        reviewer = VisualReviewer(
            vlm=mock_vlm,
            generator_llm=mock_generator,
            config=config,
            renderer=mock_renderer,
        )

        section = OutlineSection(title="Test Slide", points=["Point 1"])
        code = "<template><div>Test</div></template>"

        result = await reviewer.review_and_fix(
            section=section,
            code=code,
            session_id="test-session",
        )

        assert result.code == code
        assert result.visual_retry_count == 0
        assert result.screenshot_captured is False
        assert "Screenshot failed" in result.warnings[0]

    @pytest.mark.asyncio
    async def test_respects_max_retries(self):
        config = ReflectionConfig(
            enabled=True,
            enable_visual_review=True,
            max_visual_retries=2,
        )

        # VLM always returns issues
        mock_vlm = AsyncMock()
        mock_vlm.ainvoke.return_value = MagicMock(
            content='{"has_issues": true, "issues": [{"type": "contrast", "description": "Poor contrast", "location": "center", "severity": "high"}], "fix_suggestions": ["Improve colors"]}'
        )

        mock_generator = AsyncMock()
        mock_generator.ainvoke.return_value = MagicMock(
            content="```vue\n<template><div>Still bad</div></template>\n```"
        )

        mock_renderer = AsyncMock(spec=ScreenshotRenderer)
        mock_renderer.capture_preview_screenshot.return_value = ScreenshotResult(
            success=True,
            image_bytes=b"fake_png",
        )

        reviewer = VisualReviewer(
            vlm=mock_vlm,
            generator_llm=mock_generator,
            config=config,
            renderer=mock_renderer,
        )

        section = OutlineSection(title="Test", points=[])
        code = "<template><div>Original</div></template>"

        result = await reviewer.review_and_fix(
            section=section,
            code=code,
            session_id="test",
        )

        assert result.visual_retry_count == 2  # Max retries reached
        assert "max retries" in result.warnings[-1].lower()


class TestScreenshotRenderer:
    """Tests for ScreenshotRenderer."""

    def test_initialization(self):
        renderer = ScreenshotRenderer(
            browserless_url="http://localhost:3000",
            vue_preview_url="http://localhost:5173",
            timeout_ms=15000,
        )
        assert renderer.browserless_url == "http://localhost:3000"
        assert renderer.vue_preview_url == "http://localhost:5173"
        assert renderer.timeout_ms == 15000

    def test_wrap_vue_in_html(self):
        renderer = ScreenshotRenderer()
        vue_code = "<template><div>Hello</div></template>"
        html = renderer._wrap_vue_in_html(vue_code)

        assert "<!DOCTYPE html>" in html
        assert "vue@3" in html
        assert "<div>Hello</div>" in html
        assert "#slide-root" in html

    def test_build_screenshot_payload(self):
        renderer = ScreenshotRenderer()
        payload = renderer._build_screenshot_payload(
            html="<html></html>",
            width=1280,
            height=720,
            selector="#slide-root",
        )

        assert payload["html"] == "<html></html>"
        assert payload["viewport"]["width"] == 1280
        assert payload["viewport"]["height"] == 720
        assert payload["selector"] == "#slide-root"
        assert payload["options"]["type"] == "png"
