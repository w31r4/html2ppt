"""Headless browser rendering service for visual feedback loop.

Uses Browserless Chrome to render Vue components and capture screenshots.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

import httpx

from html2ppt.config.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class ScreenshotResult:
    """Result of a screenshot capture operation."""

    success: bool
    image_bytes: bytes | None = None
    error: str | None = None


class ScreenshotRenderer:
    """Client for capturing screenshots via Browserless Chrome."""

    def __init__(
        self,
        browserless_url: str = "http://browserless:3000",
        vue_preview_url: str = "http://vue-preview:5173",
        timeout_ms: int = 30000,
    ) -> None:
        self.browserless_url = browserless_url.rstrip("/")
        self.vue_preview_url = vue_preview_url.rstrip("/")
        self.timeout_ms = timeout_ms

    async def capture_screenshot(
        self,
        vue_code: str,
        *,
        width: int = 1280,
        height: int = 720,
        selector: str = "#slide-root",
        session_id: str | None = None,
    ) -> ScreenshotResult:
        """Capture a screenshot of a rendered Vue component.

        Args:
            vue_code: The Vue SFC code to render
            width: Viewport width (default: 1280 for 16:9 slides)
            height: Viewport height (default: 720 for 16:9 slides)
            selector: CSS selector to capture (default: #slide-root)
            session_id: Optional session ID for logging

        Returns:
            ScreenshotResult with image bytes or error message
        """
        html_content = self._wrap_vue_in_html(vue_code)
        return await self._capture_html_screenshot(
            html_content=html_content,
            width=width,
            height=height,
            selector=selector,
            session_id=session_id,
        )

    async def capture_preview_screenshot(
        self,
        vue_code: str,
        *,
        width: int = 1280,
        height: int = 720,
        session_id: str | None = None,
    ) -> ScreenshotResult:
        """Capture screenshot by posting to vue-preview-service and then screenshotting.

        This method uses the existing vue-preview-service for proper Vite/Vue rendering,
        then captures a screenshot of the result.

        Args:
            vue_code: The Vue SFC code to render
            width: Viewport width
            height: Viewport height
            session_id: Optional session ID for logging

        Returns:
            ScreenshotResult with image bytes or error message
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as client:
                # First, send the code to vue-preview-service
                preview_response = await client.post(
                    f"{self.vue_preview_url}/api/preview",
                    json={"code": vue_code},
                )
                preview_response.raise_for_status()
                preview_data = preview_response.json()
                preview_id = preview_data.get("id")

                if not preview_id:
                    return ScreenshotResult(
                        success=False,
                        error="Failed to get preview ID from vue-preview-service",
                    )

                # Build the preview URL that Browserless will visit
                preview_page_url = f"{self.vue_preview_url}/preview/{preview_id}"

                # Use Browserless to capture the screenshot
                return await self._capture_url_screenshot(
                    url=preview_page_url,
                    width=width,
                    height=height,
                    session_id=session_id,
                )

        except httpx.TimeoutException:
            logger.warning(
                "Preview screenshot timeout",
                session_id=session_id,
            )
            return ScreenshotResult(
                success=False,
                error="Screenshot timeout",
            )
        except httpx.HTTPStatusError as e:
            logger.warning(
                "Preview service HTTP error",
                session_id=session_id,
                status_code=e.response.status_code,
            )
            return ScreenshotResult(
                success=False,
                error=f"Preview service error: {e.response.status_code}",
            )
        except Exception as e:
            logger.warning(
                "Preview screenshot failed",
                session_id=session_id,
                error=str(e),
            )
            return ScreenshotResult(
                success=False,
                error=str(e),
            )

    async def _capture_html_screenshot(
        self,
        html_content: str,
        *,
        width: int,
        height: int,
        selector: str,
        session_id: str | None,
    ) -> ScreenshotResult:
        """Capture screenshot of raw HTML content using Browserless."""
        # Browserless /screenshot endpoint with setContent
        payload = self._build_screenshot_payload(
            html=html_content,
            width=width,
            height=height,
            selector=selector,
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as client:
                response = await client.post(
                    f"{self.browserless_url}/screenshot",
                    json=payload,
                )
                response.raise_for_status()

                return ScreenshotResult(
                    success=True,
                    image_bytes=response.content,
                )

        except httpx.TimeoutException:
            logger.warning(
                "Screenshot capture timeout",
                session_id=session_id,
            )
            return ScreenshotResult(
                success=False,
                error="Screenshot timeout",
            )
        except httpx.HTTPStatusError as e:
            logger.warning(
                "Browserless HTTP error",
                session_id=session_id,
                status_code=e.response.status_code,
            )
            return ScreenshotResult(
                success=False,
                error=f"Browserless error: {e.response.status_code}",
            )
        except Exception as e:
            logger.warning(
                "Screenshot capture failed",
                session_id=session_id,
                error=str(e),
            )
            return ScreenshotResult(
                success=False,
                error=str(e),
            )

    async def _capture_url_screenshot(
        self,
        url: str,
        *,
        width: int,
        height: int,
        session_id: str | None,
    ) -> ScreenshotResult:
        """Capture screenshot of a URL using Browserless."""
        payload: dict[str, Any] = {
            "url": url,
            "options": {
                "fullPage": False,
                "type": "png",
            },
            "viewport": {
                "width": width,
                "height": height,
            },
            "waitFor": 2000,  # Wait for Vue to render
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as client:
                response = await client.post(
                    f"{self.browserless_url}/screenshot",
                    json=payload,
                )
                response.raise_for_status()

                return ScreenshotResult(
                    success=True,
                    image_bytes=response.content,
                )

        except httpx.TimeoutException:
            logger.warning(
                "URL screenshot timeout",
                session_id=session_id,
                url=url,
            )
            return ScreenshotResult(
                success=False,
                error="Screenshot timeout",
            )
        except httpx.HTTPStatusError as e:
            logger.warning(
                "Browserless HTTP error for URL",
                session_id=session_id,
                status_code=e.response.status_code,
                url=url,
            )
            return ScreenshotResult(
                success=False,
                error=f"Browserless error: {e.response.status_code}",
            )
        except Exception as e:
            logger.warning(
                "URL screenshot failed",
                session_id=session_id,
                error=str(e),
                url=url,
            )
            return ScreenshotResult(
                success=False,
                error=str(e),
            )

    def _build_screenshot_payload(
        self,
        *,
        html: str,
        width: int,
        height: int,
        selector: str,
    ) -> dict[str, Any]:
        """Build the Browserless screenshot API payload."""
        return {
            "html": html,
            "options": {
                "fullPage": False,
                "type": "png",
            },
            "viewport": {
                "width": width,
                "height": height,
            },
            "selector": selector,
            "waitFor": 1000,  # Wait for rendering
        }

    def _wrap_vue_in_html(self, vue_code: str) -> str:
        """Wrap Vue SFC code in a minimal HTML document with Vue runtime.

        Note: This is a simplified wrapper for standalone rendering.
        For production use with UnoCSS and full Vite features,
        prefer using capture_preview_screenshot with vue-preview-service.
        """
        # Escape the code for embedding in JS
        escaped_code = vue_code.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: white; }}
        #slide-root {{
            width: 1280px;
            height: 720px;
            overflow: hidden;
            position: relative;
        }}
    </style>
</head>
<body>
    <div id="slide-root"></div>
    <script type="module">
        // Simplified Vue SFC parsing - extract template and render
        const sfcCode = `{escaped_code}`;

        // Extract template content
        const templateMatch = sfcCode.match(/<template>([\\s\\S]*?)<\\/template>/);
        const templateContent = templateMatch ? templateMatch[1].trim() : '<div>No template</div>';

        // Create and mount Vue app
        const {{ createApp }} = Vue;
        const app = createApp({{
            template: templateContent,
        }});
        app.mount('#slide-root');
    </script>
</body>
</html>"""
