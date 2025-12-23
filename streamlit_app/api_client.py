"""API client for FastAPI backend."""

import httpx
from typing import Optional
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")


class APIError(Exception):
    """API error with status code and detail."""

    def __init__(self, message: str, status_code: int = 500, detail: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


def get_client() -> httpx.Client:
    """Create HTTP client with timeout."""
    return httpx.Client(base_url=API_BASE_URL, timeout=120.0)


async def get_async_client() -> httpx.AsyncClient:
    """Create async HTTP client with timeout."""
    return httpx.AsyncClient(base_url=API_BASE_URL, timeout=120.0)


def submit_requirements(content: str, supplement: Optional[str] = None) -> dict:
    """Submit requirements and get outline.

    Args:
        content: Requirement text
        supplement: Optional additional requirements

    Returns:
        Response with session_id, outline, and status
    """
    with get_client() as client:
        response = client.post("/requirements", json={"content": content, "supplement": supplement})
        if response.status_code != 200:
            detail = response.json().get("detail", "Unknown error")
            raise APIError(detail, response.status_code, detail)
        return response.json()


def get_outline(session_id: str) -> dict:
    """Get outline for a session.

    Args:
        session_id: Session ID

    Returns:
        Outline response
    """
    with get_client() as client:
        response = client.get(f"/outline/{session_id}")
        if response.status_code != 200:
            detail = response.json().get("detail", "Session not found")
            raise APIError(detail, response.status_code, detail)
        return response.json()


def update_outline(session_id: str, outline: str) -> dict:
    """Update outline content.

    Args:
        session_id: Session ID
        outline: Updated outline markdown

    Returns:
        Updated outline response
    """
    with get_client() as client:
        response = client.put(f"/outline/{session_id}", json={"outline": outline})
        if response.status_code != 200:
            detail = response.json().get("detail", "Update failed")
            raise APIError(detail, response.status_code, detail)
        return response.json()


def add_supplement(session_id: str, content: str) -> dict:
    """Add supplement and regenerate outline.

    Args:
        session_id: Session ID
        content: Supplement text

    Returns:
        Regenerated outline response
    """
    with get_client() as client:
        response = client.post(f"/outline/{session_id}/supplement", json={"content": content})
        if response.status_code != 200:
            detail = response.json().get("detail", "Supplement failed")
            raise APIError(detail, response.status_code, detail)
        return response.json()


def confirm_outline(session_id: str) -> dict:
    """Confirm outline and start generation.

    Args:
        session_id: Session ID

    Returns:
        Session status
    """
    with get_client() as client:
        response = client.post(f"/outline/{session_id}/confirm")
        if response.status_code != 200:
            detail = response.json().get("detail", "Confirm failed")
            raise APIError(detail, response.status_code, detail)
        return response.json()


def get_generation_status(session_id: str) -> dict:
    """Get generation status.

    Args:
        session_id: Session ID

    Returns:
        Status with stage and progress
    """
    with get_client() as client:
        response = client.get(f"/generation/{session_id}/status")
        if response.status_code != 200:
            detail = response.json().get("detail", "Status not found")
            raise APIError(detail, response.status_code, detail)
        return response.json()


def get_result(session_id: str) -> dict:
    """Get generation result.

    Args:
        session_id: Session ID

    Returns:
        Result with slides_md and components
    """
    with get_client() as client:
        response = client.get(f"/result/{session_id}")
        if response.status_code != 200:
            detail = response.json().get("detail", "Result not found")
            raise APIError(detail, response.status_code, detail)
        return response.json()


def get_export_url(session_id: str, include_components: bool = False) -> str:
    """Get export URL.

    Args:
        session_id: Session ID
        include_components: Whether to include Vue components as zip

    Returns:
        Export URL
    """
    suffix = "?include_components=true" if include_components else ""
    return f"{API_BASE_URL}/export/{session_id}{suffix}"


def get_llm_settings() -> dict:
    """Get LLM settings.

    Returns:
        LLM settings
    """
    with get_client() as client:
        response = client.get("/settings/llm")
        if response.status_code != 200:
            return {"provider": "openai", "model": "gpt-4o", "temperature": 0.7, "max_tokens": 4096}
        return response.json()


def update_llm_settings(settings: dict) -> dict:
    """Update LLM settings.

    Args:
        settings: New settings

    Returns:
        Updated settings
    """
    with get_client() as client:
        response = client.put("/settings/llm", json=settings)
        if response.status_code != 200:
            detail = response.json().get("detail", "Update failed")
            raise APIError(detail, response.status_code, detail)
        return response.json()


def check_health() -> bool:
    """Check backend health.

    Returns:
        True if healthy
    """
    try:
        with get_client() as client:
            response = client.get("/health")
            return response.status_code == 200
    except Exception:
        return False
