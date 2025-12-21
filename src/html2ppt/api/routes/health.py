"""Health check endpoints."""

from fastapi import APIRouter

from html2ppt import __version__

router = APIRouter()


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
async def readiness_check() -> dict:
    """Readiness check endpoint.

    Returns:
        Readiness status
    """
    # TODO: Add LLM connectivity check
    return {
        "status": "ready",
    }
