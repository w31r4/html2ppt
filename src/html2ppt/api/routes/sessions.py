"""Session management endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from html2ppt.agents.session_manager import get_session_manager
from html2ppt.agents.state import WorkflowStage
from html2ppt.config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class RequirementInput(BaseModel):
    """Input model for requirement submission."""

    content: str = Field(..., min_length=1, max_length=10000, description="Requirement text")
    supplement: Optional[str] = Field(None, description="Additional requirements to merge")


class OutlineUpdate(BaseModel):
    """Input model for outline update."""

    outline: str = Field(..., min_length=1, description="Updated outline markdown")


class SupplementInput(BaseModel):
    """Input model for adding supplement."""

    content: str = Field(..., min_length=1, max_length=5000, description="Supplement text")


class OutlineResponse(BaseModel):
    """Response model for outline."""

    session_id: str
    outline: str
    status: str  # draft, confirmed, generating, completed, error


class SessionStatus(BaseModel):
    """Session status model."""

    session_id: str
    status: str
    stage: str
    progress: float
    error: Optional[str] = None


class GenerationResult(BaseModel):
    """Generation result model."""

    session_id: str
    slides_md: str
    components: list[dict]
    slides: list[dict]


@router.post("/requirements", response_model=OutlineResponse)
async def submit_requirements(req: RequirementInput) -> OutlineResponse:
    """Submit requirements and generate outline.

    Args:
        req: Requirement input

    Returns:
        Generated outline with session ID
    """
    logger.info("Submitting requirements", content_length=len(req.content))

    manager = get_session_manager()

    try:
        session = await manager.create_session(
            requirement=req.content,
            supplement=req.supplement,
        )

        outline = session.state.get("outline_markdown", "")
        stage = session.state.get("stage", WorkflowStage.INITIAL)

        # Map stage to status
        status_map = {
            WorkflowStage.INITIAL: "generating",
            WorkflowStage.OUTLINE_GENERATED: "draft",
            WorkflowStage.OUTLINE_CONFIRMED: "confirmed",
            WorkflowStage.REACT_GENERATING: "generating",
            WorkflowStage.REACT_COMPLETED: "generating",
            WorkflowStage.SLIDEV_CONVERTING: "generating",
            WorkflowStage.COMPLETED: "completed",
            WorkflowStage.ERROR: "error",
        }

        return OutlineResponse(
            session_id=session.session_id,
            outline=outline or "",
            status=status_map.get(stage, "draft"),
        )

    except Exception as e:
        logger.error("Failed to create session", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate outline: {e!s}")


@router.get("/outline/{session_id}", response_model=OutlineResponse)
async def get_outline(session_id: str) -> OutlineResponse:
    """Get outline for a session.

    Args:
        session_id: Session ID

    Returns:
        Current outline
    """
    manager = get_session_manager()
    session = manager.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    outline = session.state.get("outline_markdown", "")
    stage = session.state.get("stage", WorkflowStage.INITIAL)

    status_map = {
        WorkflowStage.INITIAL: "generating",
        WorkflowStage.OUTLINE_GENERATED: "draft",
        WorkflowStage.OUTLINE_CONFIRMED: "confirmed",
        WorkflowStage.REACT_GENERATING: "generating",
        WorkflowStage.REACT_COMPLETED: "generating",
        WorkflowStage.SLIDEV_CONVERTING: "generating",
        WorkflowStage.COMPLETED: "completed",
        WorkflowStage.ERROR: "error",
    }

    return OutlineResponse(
        session_id=session_id,
        outline=outline or "",
        status=status_map.get(stage, "draft"),
    )


@router.put("/outline/{session_id}", response_model=OutlineResponse)
async def update_outline(session_id: str, data: OutlineUpdate) -> OutlineResponse:
    """Update outline content.

    Args:
        session_id: Session ID
        data: New outline content

    Returns:
        Updated outline
    """
    manager = get_session_manager()

    success = await manager.update_outline(session_id, data.outline)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return OutlineResponse(
        session_id=session_id,
        outline=data.outline,
        status="draft",
    )


@router.post("/outline/{session_id}/supplement", response_model=OutlineResponse)
async def add_supplement(session_id: str, data: SupplementInput) -> OutlineResponse:
    """Add supplement and regenerate outline.

    Args:
        session_id: Session ID
        data: Supplement content

    Returns:
        Regenerated outline
    """
    manager = get_session_manager()

    success = await manager.add_supplement(session_id, data.content)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    session = manager.get_session(session_id)
    outline = session.state.get("outline_markdown", "") if session else ""

    return OutlineResponse(
        session_id=session_id,
        outline=outline,
        status="draft",
    )


@router.post("/outline/{session_id}/confirm", response_model=SessionStatus)
async def confirm_outline(
    session_id: str,
    background_tasks: BackgroundTasks,
) -> SessionStatus:
    """Confirm outline and start generation.

    Args:
        session_id: Session ID
        background_tasks: FastAPI background tasks

    Returns:
        Session status
    """
    manager = get_session_manager()

    # Confirm in background to return quickly
    success = await manager.confirm_outline(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    status = manager.get_status(session_id)
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionStatus(
        session_id=session_id,
        status="generating",
        stage=status.get("stage", "outline_confirmed"),
        progress=status.get("progress", 0.0),
        error=status.get("error"),
    )


@router.get("/generation/{session_id}/status", response_model=SessionStatus)
async def get_generation_status(session_id: str) -> SessionStatus:
    """Get generation status.

    Args:
        session_id: Session ID

    Returns:
        Current generation status
    """
    manager = get_session_manager()
    status = manager.get_status(session_id)

    if not status:
        raise HTTPException(status_code=404, detail="Session not found")

    # Map internal stage to user-friendly status
    stage = status.get("stage", "initial")
    status_map = {
        "initial": "pending",
        "outline_generated": "outline_ready",
        "outline_confirmed": "generating",
        "react_generating": "generating",
        "react_completed": "converting",
        "slidev_converting": "converting",
        "completed": "completed",
        "error": "error",
    }

    return SessionStatus(
        session_id=session_id,
        status=status_map.get(stage, "pending"),
        stage=stage,
        progress=status.get("progress", 0.0),
        error=status.get("error"),
    )


@router.get("/result/{session_id}", response_model=GenerationResult)
async def get_result(session_id: str) -> GenerationResult:
    """Get generation result.

    Args:
        session_id: Session ID

    Returns:
        Generated slides.md content and components
    """
    manager = get_session_manager()
    result = manager.get_result(session_id)

    if not result:
        # Check if session exists but not completed
        status = manager.get_status(session_id)
        if status:
            raise HTTPException(
                status_code=400,
                detail=f"Generation not completed. Current stage: {status.get('stage')}",
            )
        raise HTTPException(status_code=404, detail="Session not found")

    return GenerationResult(
        session_id=session_id,
        slides_md=result.get("slides_md", ""),
        components=result.get("components", []),
        slides=result.get("slides", []),
    )


@router.get("/export/{session_id}")
async def export_slides(session_id: str) -> PlainTextResponse:
    """Export slides.md file.

    Args:
        session_id: Session ID

    Returns:
        slides.md content as downloadable file
    """
    manager = get_session_manager()
    result = manager.get_result(session_id)

    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    slides_md = result.get("slides_md", "")

    return PlainTextResponse(
        content=slides_md,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=slides-{session_id[:8]}.md"},
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> dict:
    """Delete a session.

    Args:
        session_id: Session ID

    Returns:
        Deletion confirmation
    """
    manager = get_session_manager()
    success = manager.delete_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Session deleted", "session_id": session_id}


@router.get("/sessions")
async def list_sessions() -> list[SessionStatus]:
    """List all active sessions.

    Returns:
        List of session statuses
    """
    manager = get_session_manager()
    sessions = manager.list_sessions()

    return [
        SessionStatus(
            session_id=s["session_id"],
            status=s.get("stage", "unknown"),
            stage=s.get("stage", "unknown"),
            progress=s.get("progress", 0.0),
            error=s.get("error"),
        )
        for s in sessions
    ]
