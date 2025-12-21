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


class VisualSuggestion(BaseModel):
    """Visual design suggestions for a slide."""

    background: Optional[str] = Field(None, description="Background color/gradient/image description")
    core_image: Optional[str] = Field(None, description="Core image or illustration description")
    layout: Optional[str] = Field(None, description="Layout arrangement description")
    image_url: Optional[str] = Field(None, description="Optional specific image URL")


class AnimationEffect(BaseModel):
    """Animation effects for slide elements."""

    description: str = Field(..., description="Animation effect description")
    elements: list[str] = Field(default_factory=list, description="Individual animation steps")


class OutlineSection(BaseModel):
    """A section in the presentation outline."""

    title: str = Field(..., description="Section title")
    subtitle: Optional[str] = Field(None, description="Optional subtitle")
    points: list[str] = Field(default_factory=list, description="Bullet points in the section")
    visual_suggestions: Optional[VisualSuggestion] = Field(None, description="Visual design suggestions")
    animation_effects: Optional[AnimationEffect] = Field(None, description="Animation effects")
    speaker_notes: Optional[str] = Field(None, description="Optional speaker notes")
    raw_content: Optional[str] = Field(None, description="Raw markdown content of this section")


class Outline(BaseModel):
    """Structured presentation outline."""

    title: str = Field(..., description="Presentation main title (H1)")
    sections: list[OutlineSection] = Field(default_factory=list, description="Outline sections")
    raw_markdown: str = Field(..., description="Raw markdown representation")

    @classmethod
    def from_markdown(cls, markdown: str) -> "Outline":
        """Parse markdown into structured outline.

        Supports rich format with visual suggestions and animation effects.

        Args:
            markdown: Raw markdown outline text

        Returns:
            Parsed Outline object
        """
        import re

        lines = markdown.strip().split("\n")
        title = ""
        sections: list[OutlineSection] = []

        # Split by page separators (--- or ### Page N:)
        page_pattern = r"(?:^|\n)(?:---\s*\n)?###\s*Page\s*\d+[：:]\s*"
        page_splits = re.split(page_pattern, markdown)

        # Find main title (H1)
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("# ") and not stripped.startswith("## ") and not stripped.startswith("### "):
                title = stripped[2:].strip()
                break

        # Parse each page section
        for page_content in page_splits:
            if not page_content.strip():
                continue

            section = cls._parse_page_section(page_content.strip())
            if section:
                sections.append(section)

        return cls(
            title=title or "Untitled Presentation",
            sections=sections,
            raw_markdown=markdown,
        )

    @classmethod
    def _parse_page_section(cls, content: str) -> Optional["OutlineSection"]:
        """Parse a single page section from markdown.

        Args:
            content: Raw markdown content of one page

        Returns:
            Parsed OutlineSection or None
        """
        import re

        lines = content.split("\n")
        if not lines:
            return None

        # Extract title from first line or **标题** field
        page_title = ""
        subtitle = None
        points: list[str] = []
        visual_suggestions: Optional[VisualSuggestion] = None
        animation_effects: Optional[AnimationEffect] = None
        speaker_notes = None

        # State tracking
        current_block = None  # 'visual', 'animation', 'content', 'notes'
        visual_data: dict = {}
        animation_steps: list[str] = []

        in_speaker_notes = False
        speaker_notes_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines in normal mode
            if not stripped:
                if in_speaker_notes:
                    speaker_notes_lines.append("")
                continue

            # Page title (first line might be the title)
            if not page_title and not stripped.startswith("*") and not stripped.startswith("-"):
                # Check if it's a plain title line
                if not stripped.startswith("**"):
                    page_title = stripped
                    continue

            # Speaker notes block
            if stripped.lower().startswith("<!--") and "speaker" in stripped.lower():
                in_speaker_notes = True
                current_block = "notes"
                continue

            if stripped.endswith("-->") and in_speaker_notes:
                in_speaker_notes = False
                speaker_notes = "\n".join(speaker_notes_lines).strip()
                current_block = None
                continue

            if in_speaker_notes:
                speaker_notes_lines.append(stripped)
                continue

            # Parse structured fields
            if "**标题**" in stripped or "**标题：**" in stripped:
                match = re.search(r"\*\*标题[：:]?\*\*[：:\s]*(.+)", stripped)
                if match:
                    page_title = match.group(1).strip()
                continue

            if "**副标题**" in stripped or "**副标题：**" in stripped:
                match = re.search(r"\*\*副标题[：:]?\*\*[：:\s]*(.+)", stripped)
                if match:
                    subtitle = match.group(1).strip()
                continue

            # Visual suggestions block
            if "**视觉建议**" in stripped:
                current_block = "visual"
                continue

            if current_block == "visual":
                if "**背景**" in stripped:
                    match = re.search(r"\*\*背景[：:]?\*\*[：:\s]*(.+)", stripped)
                    if match:
                        visual_data["background"] = match.group(1).strip()
                elif "**核心图片**" in stripped or "**核心图示**" in stripped:
                    match = re.search(r"\*\*核心图[片示][：:]?\*\*[：:\s]*(.+)", stripped)
                    if match:
                        visual_data["core_image"] = match.group(1).strip()
                elif "**布局**" in stripped:
                    match = re.search(r"\*\*布局[：:]?\*\*[：:\s]*(.+)", stripped)
                    if match:
                        visual_data["layout"] = match.group(1).strip()
                elif "**图片链接**" in stripped:
                    match = re.search(r"\*\*图片链接[：:]?\*\*[：:\s]*(.+)", stripped)
                    if match:
                        visual_data["image_url"] = match.group(1).strip()
                elif stripped.startswith("*   **") or stripped.startswith("- **"):
                    # Still in visual block, sub-item
                    pass
                elif "**动画效果**" in stripped:
                    current_block = "animation"
                elif "**核心内容**" in stripped:
                    current_block = "content"

            # Animation effects block
            if "**动画效果**" in stripped:
                current_block = "animation"
                continue

            if current_block == "animation":
                if stripped.startswith("*") or stripped.startswith("-"):
                    # Remove list marker and add to animation steps
                    step = re.sub(r"^[\*\-]\s*", "", stripped)
                    if step and not step.startswith("**"):
                        animation_steps.append(step)
                elif "**" in stripped and not any(x in stripped for x in ["动画效果", "视觉建议", "核心内容"]):
                    # End of animation block
                    current_block = None

            # Core content block
            if "**核心内容**" in stripped:
                current_block = "content"
                continue

            if current_block == "content":
                if stripped.startswith("*") or stripped.startswith("-"):
                    point = re.sub(r"^[\*\-]\s*", "", stripped)
                    if point:
                        points.append(point)
                elif "**视觉建议**" in stripped:
                    current_block = "visual"
                elif "**动画效果**" in stripped:
                    current_block = "animation"

        # Build visual suggestions if we have data
        if visual_data:
            visual_suggestions = VisualSuggestion(**visual_data)

        # Build animation effects if we have steps
        if animation_steps:
            animation_effects = AnimationEffect(
                description="动画效果",
                elements=animation_steps,
            )

        # Only return section if we have a title
        if not page_title:
            return None

        return OutlineSection(
            title=page_title,
            subtitle=subtitle,
            points=points,
            visual_suggestions=visual_suggestions,
            animation_effects=animation_effects,
            speaker_notes=speaker_notes,
            raw_content=content,
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
