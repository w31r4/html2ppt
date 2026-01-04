"""Health check endpoints."""

from typing import Any

import httpx
from fastapi import APIRouter

from html2ppt import __version__
from html2ppt.agents.session_manager import get_session_manager
from html2ppt.config.logging import get_logger
from html2ppt.config.settings import get_settings

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status and version info
    """
    return {
        "status": "healthy",
        "version": __version__,
    }


@router.get("/ready")
async def readiness_check() -> dict[str, Any]:
    """Readiness check endpoint with external service status.

    Checks connectivity to:
    - LLM API (basic connectivity test)
    - Browserless (if visual review is enabled)
    - Vue Preview Service (if visual review is enabled)

    Returns:
        Readiness status with details for each service
    """
    settings = get_settings()
    session_manager = get_session_manager()

    checks: dict[str, dict[str, Any]] = {}
    overall_ready = True

    # Check LLM API connectivity
    llm_check = await _check_llm_connectivity(settings)
    checks["llm"] = llm_check
    if llm_check["status"] != "ok":
        overall_ready = False

    # Check Browserless (for visual review)
    reflection_config = settings.get_reflection_config()
    if reflection_config.enable_visual_review:
        browserless_check = await _check_browserless(reflection_config.renderer_url)
        checks["browserless"] = browserless_check
        # Browserless is optional, don't fail readiness

        vue_preview_check = await _check_vue_preview(reflection_config.vue_preview_url)
        checks["vue_preview"] = vue_preview_check
        # Vue preview is optional, don't fail readiness

    # Session count
    checks["sessions"] = {
        "status": "ok",
        "active_count": session_manager.get_session_count(),
    }

    return {
        "status": "ready" if overall_ready else "degraded",
        "checks": checks,
    }


async def _check_llm_connectivity(settings) -> dict[str, Any]:
    """Check LLM API connectivity.

    Returns:
        Status dict with connectivity info
    """
    try:
        # Just check if we can reach the base URL
        llm_config = settings.get_llm_config()
        base_url = llm_config.base_url or "https://api.openai.com/v1"

        # For Azure, use the Azure endpoint
        if llm_config.azure_endpoint:
            base_url = llm_config.azure_endpoint

        async with httpx.AsyncClient(timeout=5.0) as client:
            # Just try to reach the base, don't actually make an API call
            response = await client.get(base_url, follow_redirects=True)
            # Most LLM APIs return 401/403 without auth, which is fine
            return {
                "status": "ok",
                "provider": str(llm_config.provider.value),
                "model": llm_config.model,
            }
    except httpx.TimeoutException:
        return {"status": "timeout", "error": "LLM API connection timed out"}
    except httpx.ConnectError as e:
        return {"status": "unreachable", "error": str(e)}
    except Exception as e:
        logger.warning("LLM health check failed", error=str(e))
        return {"status": "error", "error": str(e)}


async def _check_browserless(url: str) -> dict[str, Any]:
    """Check Browserless service availability.

    Args:
        url: Browserless service URL

    Returns:
        Status dict with connectivity info
    """
    if not url:
        return {"status": "not_configured"}

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{url}/json/version")
            if response.status_code == 200:
                return {"status": "ok", "url": url}
            return {"status": "unhealthy", "http_status": response.status_code}
    except httpx.TimeoutException:
        return {"status": "timeout", "url": url}
    except httpx.ConnectError:
        return {"status": "unreachable", "url": url}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def _check_vue_preview(url: str) -> dict[str, Any]:
    """Check Vue Preview Service availability.

    Args:
        url: Vue preview service URL

    Returns:
        Status dict with connectivity info
    """
    if not url:
        return {"status": "not_configured"}

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return {"status": "ok", "url": url}
            return {"status": "unhealthy", "http_status": response.status_code}
    except httpx.TimeoutException:
        return {"status": "timeout", "url": url}
    except httpx.ConnectError:
        return {"status": "unreachable", "url": url}
    except Exception as e:
        return {"status": "error", "error": str(e)}
