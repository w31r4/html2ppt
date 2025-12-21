"""LangGraph workflow state definitions."""

from enum import Enum
from typing import Annotated, Optional, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class WorkflowStage(str, Enum):
    """Current stage in the workflow."""

    INITIAL = "initial"
    OUTLINE_GENERATED = "outline_generated"
    OUTLINE_CONFIRMED = "outline_confirmed"
    REACT_GENERATING = "react_generating"
    REACT_COMPLETED = "react_completed"
    SLIDEV_CONVERTING = "slidev_converting"
    COMPLETED = "completed"
    ERROR = "error"


class OutlineSection(BaseModel):
    """A section in the presentation outline."""

    title: str = Field(..., description="Section title (H2)")
    points: list[str] = Field(default_factory=list, description="Bullet points in the section")
    speaker_notes: Optional[str] = Field(None, description="Optional speaker notes")


class Outline(BaseModel):
    """Structured presentation outline."""

    title: str = Field(..., description="Presentation main title (H1)")
    sections: list[OutlineSection] = Field(default_factory=list, description="Outline sections")
    raw_markdown: str = Field(..., description="Raw markdown representation")

    @classmethod
    def from_markdown(cls, markdown: str) -> "Outline":
        """Parse markdown into structured outline.

        Args:
            markdown: Raw markdown outline text

        Returns:
            Parsed Outline object
        """
        lines = markdown.strip().split("\n")
        title = ""
        sections: list[OutlineSection] = []
        current_section: Optional[OutlineSection] = None
        in_speaker_notes = False
        speaker_notes_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                if in_speaker_notes:
                    speaker_notes_lines.append("")
                continue

            # Main title (H1)
            if stripped.startswith("# ") and not stripped.startswith("## "):
                title = stripped[2:].strip()
                continue

            # Section title (H2)
            if stripped.startswith("## "):
                # Save previous section
                if current_section is not None:
                    if speaker_notes_lines:
                        current_section.speaker_notes = "\n".join(speaker_notes_lines).strip()
                    sections.append(current_section)

                current_section = OutlineSection(
                    title=stripped[3:].strip(),
                    points=[],
                )
                in_speaker_notes = False
                speaker_notes_lines = []
                continue

            # Speaker notes block
            if stripped.lower().startswith("<!--") and "speaker" in stripped.lower():
                in_speaker_notes = True
                continue

            if stripped.endswith("-->") and in_speaker_notes:
                in_speaker_notes = False
                continue

            if in_speaker_notes:
                speaker_notes_lines.append(stripped)
                continue

            # Bullet points
            if stripped.startswith("- ") or stripped.startswith("* "):
                if current_section is not None:
                    current_section.points.append(stripped[2:].strip())

        # Save last section
        if current_section is not None:
            if speaker_notes_lines:
                current_section.speaker_notes = "\n".join(speaker_notes_lines).strip()
            sections.append(current_section)

        return cls(
            title=title or "Untitled Presentation",
            sections=sections,
            raw_markdown=markdown,
        )

    def to_markdown(self) -> str:
        """Convert outline back to markdown.

        Returns:
            Markdown string representation
        """
        lines = [f"# {self.title}", ""]

        for section in self.sections:
            lines.append(f"## {section.title}")
            for point in section.points:
                lines.append(f"- {point}")

            if section.speaker_notes:
                lines.append("")
                lines.append("<!-- speaker notes")
                lines.append(section.speaker_notes)
                lines.append("-->")

            lines.append("")

        return "\n".join(lines)


class ReactComponent(BaseModel):
    """A generated React component for a slide."""

    name: str = Field(..., description="Component name")
    code: str = Field(..., description="React component code (TSX)")
    section_title: str = Field(..., description="Original section title")


class SlidevSlide(BaseModel):
    """A single Slidev slide."""

    frontmatter: dict = Field(default_factory=dict, description="Slide frontmatter")
    content: str = Field(..., description="Markdown content")


class WorkflowState(TypedDict):
    """LangGraph workflow state.

    This state flows through all nodes in the workflow.
    """

    # Session management
    session_id: str

    # Input
    requirement: str
    supplement: Optional[str]

    # Workflow tracking
    stage: WorkflowStage
    error: Optional[str]
    progress: float  # 0.0 to 1.0

    # Outline generation
    outline_markdown: Optional[str]
    outline: Optional[Outline]
    outline_history: list[str]  # Previous versions for undo

    # React generation
    react_components: list[ReactComponent]
    current_generating_index: int

    # Slidev conversion
    slidev_slides: list[SlidevSlide]
    slides_md: Optional[str]

    # Messages for LangGraph (optional, for agent interactions)
    messages: Annotated[list, add_messages]


def create_initial_state(
    session_id: str,
    requirement: str,
    supplement: Optional[str] = None,
) -> WorkflowState:
    """Create initial workflow state.

    Args:
        session_id: Unique session identifier
        requirement: User requirement text
        supplement: Optional additional requirements

    Returns:
        Initial WorkflowState
    """
    return WorkflowState(
        session_id=session_id,
        requirement=requirement,
        supplement=supplement,
        stage=WorkflowStage.INITIAL,
        error=None,
        progress=0.0,
        outline_markdown=None,
        outline=None,
        outline_history=[],
        react_components=[],
        current_generating_index=0,
        slidev_slides=[],
        slides_md=None,
        messages=[],
    )


# State update helpers
def update_outline(
    state: WorkflowState,
    outline_markdown: str,
) -> dict:
    """Create state update with new outline.

    Args:
        state: Current state
        outline_markdown: New outline markdown

    Returns:
        State update dict
    """
    outline = Outline.from_markdown(outline_markdown)

    # Preserve history
    history = list(state.get("outline_history", []))
    if state.get("outline_markdown"):
        history.append(state["outline_markdown"])

    return {
        "outline_markdown": outline_markdown,
        "outline": outline,
        "outline_history": history,
        "stage": WorkflowStage.OUTLINE_GENERATED,
    }


def confirm_outline(state: WorkflowState) -> dict:
    """Mark outline as confirmed.

    Args:
        state: Current state

    Returns:
        State update dict
    """
    return {
        "stage": WorkflowStage.OUTLINE_CONFIRMED,
    }


def add_react_component(
    state: WorkflowState,
    component: ReactComponent,
) -> dict:
    """Add a generated React component.

    Args:
        state: Current state
        component: New React component

    Returns:
        State update dict
    """
    components = list(state.get("react_components", []))
    components.append(component)

    total_sections = len(state.get("outline", Outline(title="", sections=[], raw_markdown="")).sections)
    progress = len(components) / max(total_sections, 1)

    return {
        "react_components": components,
        "current_generating_index": len(components),
        "progress": min(progress * 0.8, 0.8),  # Reserve 20% for Slidev conversion
        "stage": WorkflowStage.REACT_GENERATING,
    }


def set_react_completed(state: WorkflowState) -> dict:
    """Mark React generation as completed.

    Args:
        state: Current state

    Returns:
        State update dict
    """
    return {
        "stage": WorkflowStage.REACT_COMPLETED,
        "progress": 0.8,
    }


def set_slidev_result(
    state: WorkflowState,
    slides: list[SlidevSlide],
    slides_md: str,
) -> dict:
    """Set Slidev conversion result.

    Args:
        state: Current state
        slides: List of Slidev slides
        slides_md: Complete slides.md content

    Returns:
        State update dict
    """
    return {
        "slidev_slides": slides,
        "slides_md": slides_md,
        "stage": WorkflowStage.COMPLETED,
        "progress": 1.0,
    }


def set_error(state: WorkflowState, error: str) -> dict:
    """Set error state.

    Args:
        state: Current state
        error: Error message

    Returns:
        State update dict
    """
    return {
        "error": error,
        "stage": WorkflowStage.ERROR,
    }
