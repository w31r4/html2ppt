"""Session manager for workflow execution."""

import asyncio
from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from html2ppt.agents.state import (
    Outline,
    WorkflowStage,
    WorkflowState,
    create_initial_state,
)
from html2ppt.agents.workflow import PresentationWorkflow, create_workflow
from html2ppt.config.llm import LLMConfig
from html2ppt.config.logging import get_logger
from html2ppt.config.settings import get_settings

logger = get_logger(__name__)


@dataclass
class Session:
    """Represents an active presentation generation session."""

    session_id: str
    state: WorkflowState
    workflow: Optional[PresentationWorkflow] = None
    thread_config: dict = field(default_factory=dict)
    started: bool = False  # Track if workflow has been started


class SessionManager:
    """Manages presentation generation sessions."""

    _instance: Optional["SessionManager"] = None
    _sessions: dict[str, Session] = {}

    def __new__(cls) -> "SessionManager":
        """Singleton pattern for session manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._sessions = {}
        return cls._instance

    def get_llm_config(self) -> LLMConfig:
        """Get current LLM configuration.

        Returns:
            LLMConfig from settings
        """
        settings = get_settings()
        return settings.get_llm_config()

    async def create_session(
        self,
        requirement: str,
        supplement: Optional[str] = None,
    ) -> Session:
        """Create a new session and generate initial outline.

        Args:
            requirement: User requirement text
            supplement: Optional additional requirements

        Returns:
            Created session with generated outline
        """
        session_id = str(uuid4())

        # Create initial state
        state = create_initial_state(
            session_id=session_id,
            requirement=requirement,
            supplement=supplement,
        )

        # Create workflow
        llm_config = self.get_llm_config()
        workflow = create_workflow(llm_config)

        # Create thread config for checkpointing
        thread_config = {"configurable": {"thread_id": session_id}}

        session = Session(
            session_id=session_id,
            state=state,
            workflow=workflow,
            thread_config=thread_config,
        )

        self._sessions[session_id] = session

        logger.info("Session created", session_id=session_id)

        # Start workflow execution (will pause at human_review)
        await self._run_until_interrupt(session)

        return session

    async def _run_until_interrupt(self, session: Session) -> None:
        """Run workflow until it reaches an interrupt point.

        Args:
            session: Session to run
        """
        if not session.workflow:
            return

        compiled = session.workflow.compile()

        try:
            # Determine input: initial state for first run, None for resume
            input_data = None if session.started else session.state
            session.started = True

            # Run the graph
            async for event in compiled.astream(
                input_data,
                session.thread_config,
                stream_mode="updates",
            ):
                # Update session state with latest
                for node_name, updates in event.items():
                    if isinstance(updates, dict):
                        session.state.update(updates)

                logger.debug(
                    "Workflow update",
                    session_id=session.session_id,
                    update_data=str(event),
                )

        except Exception as e:
            logger.error(
                "Workflow execution error",
                session_id=session.session_id,
                error=str(e),
            )
            session.state["error"] = str(e)
            session.state["stage"] = WorkflowStage.ERROR

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session if found, None otherwise
        """
        return self._sessions.get(session_id)

    def get_outline(self, session_id: str) -> Optional[str]:
        """Get outline markdown for a session.

        Args:
            session_id: Session ID

        Returns:
            Outline markdown if available
        """
        session = self.get_session(session_id)
        if session:
            return session.state.get("outline_markdown")
        return None

    def get_status(self, session_id: str) -> Optional[dict]:
        """Get session status.

        Args:
            session_id: Session ID

        Returns:
            Status dict with stage, progress, and error info
        """
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": session_id,
            "stage": (
                session.state.get("stage", WorkflowStage.INITIAL).value
                if hasattr(session.state.get("stage", WorkflowStage.INITIAL), "value")
                else str(session.state.get("stage", WorkflowStage.INITIAL))
            ),
            "progress": session.state.get("progress", 0.0),
            "error": session.state.get("error"),
        }

    async def update_outline(
        self,
        session_id: str,
        outline_markdown: str,
    ) -> bool:
        """Update outline for a session.

        Args:
            session_id: Session ID
            outline_markdown: New outline markdown

        Returns:
            True if updated successfully
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Preserve history
        history = list(session.state.get("outline_history", []))
        if session.state.get("outline_markdown"):
            history.append(session.state["outline_markdown"])

        # Update state
        session.state["outline_markdown"] = outline_markdown
        session.state["outline"] = Outline.from_markdown(outline_markdown)
        session.state["outline_history"] = history

        logger.info("Outline updated", session_id=session_id)

        return True

    async def confirm_outline(self, session_id: str, run_background: bool = True) -> bool:
        """Confirm outline and continue workflow.

        Args:
            session_id: Session ID
            run_background: If True, start workflow in background (don't wait)

        Returns:
            True if confirmed successfully
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Mark outline as confirmed
        session.state["stage"] = WorkflowStage.OUTLINE_CONFIRMED

        logger.info("Outline confirmed", session_id=session_id)

        if run_background:
            # Start workflow in background task
            import asyncio

            asyncio.create_task(self._run_until_interrupt(session))
        else:
            # Resume workflow synchronously (for testing)
            await self._run_until_interrupt(session)

        return True

    async def add_supplement(
        self,
        session_id: str,
        supplement: str,
    ) -> bool:
        """Add supplement requirements and regenerate outline.

        Args:
            session_id: Session ID
            supplement: Additional requirements

        Returns:
            True if regeneration started
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Update supplement
        session.state["supplement"] = supplement
        session.state["stage"] = WorkflowStage.INITIAL

        logger.info("Supplement added, regenerating", session_id=session_id)

        # Resume workflow (will regenerate outline)
        await self._run_until_interrupt(session)

        return True

    def get_result(self, session_id: str) -> Optional[dict]:
        """Get generation result.

        Args:
            session_id: Session ID

        Returns:
            Result dict with slides_md and components if completed
        """
        session = self.get_session(session_id)
        if not session:
            return None

        stage = session.state.get("stage")
        if stage != WorkflowStage.COMPLETED:
            return None

        return {
            "slides_md": session.state.get("slides_md"),
            "components": [
                {
                    "name": c.name,
                    "code": c.code,
                    "section_title": c.section_title,
                }
                for c in session.state.get("react_components", [])
            ],
            "slides": [
                {
                    "frontmatter": s.frontmatter,
                    "content": s.content,
                }
                for s in session.state.get("slidev_slides", [])
            ],
        }

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info("Session deleted", session_id=session_id)
            return True
        return False

    def list_sessions(self) -> list[dict]:
        """List all active sessions.

        Returns:
            List of session status dicts
        """
        return [self.get_status(session_id) for session_id in self._sessions if self.get_status(session_id) is not None]


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance.

    Returns:
        SessionManager singleton
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
