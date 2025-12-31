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
from html2ppt.config.reflection import ReflectionConfig, merge_reflection_config
from html2ppt.config.runtime_overrides import get_override
from html2ppt.config.settings import get_settings

logger = get_logger(__name__)

_REFLECTION_NAMESPACE = "reflection"
_LLM_NAMESPACE = "llm"


@dataclass
class Session:
    """Represents an active presentation generation session."""

    session_id: str
    state: WorkflowState
    workflow: Optional[PresentationWorkflow] = None
    thread_config: dict = field(default_factory=dict)
    started: bool = False  # Track if workflow has been started
    output_saved: bool = False


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
        from pydantic import SecretStr

        settings = get_settings()
        override = get_override(_LLM_NAMESPACE) or {}

        provider = override.get("provider", settings.llm_provider)
        api_key = override.get("api_key") or settings.llm_api_key
        if isinstance(api_key, SecretStr):
            api_key = api_key.get_secret_value()

        return LLMConfig(
            provider=provider,
            api_key=SecretStr(api_key),
            base_url=override.get("base_url", settings.llm_base_url),
            model=override.get("model", settings.llm_model),
            temperature=override.get("temperature", settings.llm_temperature),
            max_tokens=override.get("max_tokens", settings.llm_max_tokens),
            azure_endpoint=override.get("azure_endpoint", settings.llm_azure_endpoint),
            azure_deployment=override.get("azure_deployment", settings.llm_azure_deployment),
            api_version=override.get("api_version", settings.llm_api_version),
        )

    def get_reflection_config(self) -> ReflectionConfig:
        """Get effective reflection configuration (env defaults + runtime override)."""
        settings = get_settings()
        base = settings.get_reflection_config()
        override = get_override(_REFLECTION_NAMESPACE)
        effective, _overridden = merge_reflection_config(base=base, override=override)
        return effective

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
        reflection_config = self.get_reflection_config()
        workflow = create_workflow(llm_config, reflection_config=reflection_config)

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

                self._maybe_save_output(session)

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

    def _maybe_save_output(self, session: Session) -> None:
        settings = get_settings()
        if not settings.auto_save_output or session.output_saved:
            return

        stage = session.state.get("stage")
        if stage != WorkflowStage.COMPLETED and str(stage) != WorkflowStage.COMPLETED.value:
            return

        slides_md = session.state.get("slides_md")
        if not slides_md:
            logger.warning(
                "Auto-save skipped: slides.md missing",
                session_id=session.session_id,
            )
            return

        output_dir = settings.output_dir / session.session_id
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "slides.md").write_text(slides_md, encoding="utf-8")

            components = session.state.get("vue_components", [])
            if components:
                components_dir = output_dir / "components"
                components_dir.mkdir(parents=True, exist_ok=True)
                for index, component in enumerate(components, start=1):
                    fallback = f"Component{index}"
                    name = self._sanitize_filename(component.name, fallback)
                    (components_dir / f"{name}.vue").write_text(component.code, encoding="utf-8")

            session.output_saved = True
            logger.info(
                "Auto-saved output",
                session_id=session.session_id,
                output_dir=str(output_dir),
            )
        except Exception as exc:
            logger.error(
                "Auto-save failed",
                session_id=session.session_id,
                error=str(exc),
            )

    @staticmethod
    def _sanitize_filename(name: str, fallback: str) -> str:
        cleaned = name.strip() or fallback
        cleaned = cleaned.replace("/", "_").replace("\\", "_")
        return cleaned

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
        session.state["pagination_passes"] = 0
        session.state["pagination_warnings"] = []
        session.state["pagination_needs_regen"] = False

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
        stage_value = stage.value if hasattr(stage, "value") else str(stage)
        if stage_value != WorkflowStage.COMPLETED.value:
            return None

        return {
            "slides_md": session.state.get("slides_md"),
            "components": [
                {
                    "name": c.name,
                    "code": c.code,
                    "section_title": c.section_title,
                }
                for c in session.state.get("vue_components", [])
            ],
            "slides": [
                {
                    "frontmatter": s.frontmatter,
                    "content": s.content,
                    "component_name": s.component_name,
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
