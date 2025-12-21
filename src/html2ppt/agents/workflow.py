"""LangGraph workflow for presentation generation."""

import re
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from html2ppt.agents.llm_factory import create_llm
from html2ppt.agents.prompts import get_outline_prompt, get_react_prompt, get_slidev_prompt
from html2ppt.agents.state import (
    Outline,
    ReactComponent,
    SlidevSlide,
    WorkflowStage,
    WorkflowState,
    add_react_component,
    confirm_outline,
    set_error,
    set_react_completed,
    set_slidev_result,
    update_outline,
)
from html2ppt.config.llm import LLMConfig
from html2ppt.config.logging import get_logger

logger = get_logger(__name__)


def _extract_code_block(text: str, language: str = "") -> str:
    """Extract code from markdown code block.

    Args:
        text: Text potentially containing code block
        language: Expected language marker (tsx, markdown, etc.)

    Returns:
        Extracted code or original text if no code block found
    """
    # Try to extract code block with specific language
    pattern = rf"```{language}\s*([\s\S]*?)```"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()

    # Try generic code block
    pattern = r"```\s*([\s\S]*?)```"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()

    return text.strip()


def _sanitize_component_name(title: str) -> str:
    """Convert section title to valid React component name.

    Args:
        title: Section title

    Returns:
        PascalCase component name
    """
    # Remove Chinese characters and special chars, keep alphanumeric
    cleaned = re.sub(r"[^\w\s]", "", title)
    # Split on whitespace and capitalize each word
    words = cleaned.split()
    # Convert to PascalCase
    pascal = "".join(word.capitalize() for word in words)
    # Ensure it starts with a letter
    if pascal and not pascal[0].isalpha():
        pascal = "Slide" + pascal
    return pascal or "Slide"


class PresentationWorkflow:
    """LangGraph workflow for generating presentations."""

    def __init__(self, llm_config: LLMConfig):
        """Initialize workflow with LLM configuration.

        Args:
            llm_config: Configuration for the LLM backend
        """
        self.llm = create_llm(llm_config)
        self.graph = self._build_graph()
        self.checkpointer = MemorySaver()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph.

        Returns:
            Configured StateGraph
        """
        graph = StateGraph(WorkflowState)

        # Add nodes
        graph.add_node("generate_outline", self._generate_outline_node)
        graph.add_node("human_review", self._human_review_node)
        graph.add_node("generate_react", self._generate_react_node)
        graph.add_node("convert_slidev", self._convert_slidev_node)

        # Add edges
        graph.add_edge(START, "generate_outline")
        graph.add_edge("generate_outline", "human_review")

        # Conditional edge after human review
        graph.add_conditional_edges(
            "human_review",
            self._route_after_review,
            {
                "regenerate": "generate_outline",
                "continue": "generate_react",
            },
        )

        graph.add_edge("generate_react", "convert_slidev")
        graph.add_edge("convert_slidev", END)

        return graph

    def compile(self):
        """Compile the graph with checkpointer.

        Returns:
            Compiled graph ready for execution
        """
        return self.graph.compile(
            checkpointer=self.checkpointer,
            interrupt_before=["human_review"],  # Pause before human review
        )

    async def _generate_outline_node(self, state: WorkflowState) -> dict:
        """Generate outline from requirements.

        Args:
            state: Current workflow state

        Returns:
            State update with generated outline
        """
        logger.info("Generating outline", session_id=state["session_id"])

        try:
            prompt = get_outline_prompt(
                requirement=state["requirement"],
                supplement=state.get("supplement"),
            )

            messages = [
                SystemMessage(content="你是一位专业的演示文稿设计师，擅长将需求转换为清晰的演示大纲。"),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            outline_markdown = response.content

            logger.info(
                "Outline generated",
                session_id=state["session_id"],
                length=len(outline_markdown),
            )

            return update_outline(state, outline_markdown)

        except Exception as e:
            logger.error(
                "Outline generation failed",
                session_id=state["session_id"],
                error=str(e),
            )
            return set_error(state, f"大纲生成失败: {e!s}")

    async def _human_review_node(self, state: WorkflowState) -> dict:
        """Human review placeholder node.

        This node is interrupted before execution to allow human review.
        When resumed, it checks if outline was confirmed.

        Args:
            state: Current workflow state

        Returns:
            State update (potentially with confirmed status)
        """
        # This node is reached after human has reviewed
        # The state should already be updated by the API
        if state.get("stage") == WorkflowStage.OUTLINE_CONFIRMED:
            logger.info("Outline confirmed", session_id=state["session_id"])
            return confirm_outline(state)

        # If not confirmed, just pass through (will regenerate if routed there)
        return {}

    def _route_after_review(self, state: WorkflowState) -> Literal["regenerate", "continue"]:
        """Route after human review.

        Args:
            state: Current workflow state

        Returns:
            Next node to execute
        """
        if state.get("stage") == WorkflowStage.OUTLINE_CONFIRMED:
            return "continue"

        # If supplement was added, regenerate
        if state.get("supplement"):
            return "regenerate"

        return "continue"

    async def _generate_react_node(self, state: WorkflowState) -> dict:
        """Generate React components for each section.

        Args:
            state: Current workflow state

        Returns:
            State update with generated components
        """
        logger.info(
            "Generating React components",
            session_id=state["session_id"],
        )

        outline = state.get("outline")
        if not outline:
            # Parse from markdown if not structured
            outline_md = state.get("outline_markdown", "")
            outline = Outline.from_markdown(outline_md)

        components: list[ReactComponent] = []
        total_sections = len(outline.sections)

        try:
            for i, section in enumerate(outline.sections):
                logger.info(
                    "Generating component",
                    session_id=state["session_id"],
                    section=section.title,
                    progress=f"{i + 1}/{total_sections}",
                )

                prompt = get_react_prompt(
                    section_title=section.title,
                    section_points=section.points,
                    speaker_notes=section.speaker_notes,
                )

                messages = [
                    SystemMessage(content="你是一位专业的React前端开发工程师，擅长创建美观的演示文稿组件。"),
                    HumanMessage(content=prompt),
                ]

                response = await self.llm.ainvoke(messages)
                code = _extract_code_block(response.content, "tsx")

                component_name = _sanitize_component_name(section.title)
                component = ReactComponent(
                    name=f"{component_name}Slide",
                    code=code,
                    section_title=section.title,
                )
                components.append(component)

            logger.info(
                "React components generated",
                session_id=state["session_id"],
                count=len(components),
            )

            return {
                "react_components": components,
                "stage": WorkflowStage.REACT_COMPLETED,
                "progress": 0.8,
            }

        except Exception as e:
            logger.error(
                "React generation failed",
                session_id=state["session_id"],
                error=str(e),
            )
            return set_error(state, f"React组件生成失败: {e!s}")

    async def _convert_slidev_node(self, state: WorkflowState) -> dict:
        """Convert React components to Slidev format.

        Args:
            state: Current workflow state

        Returns:
            State update with Slidev slides
        """
        logger.info(
            "Converting to Slidev",
            session_id=state["session_id"],
        )

        components = state.get("react_components", [])
        if not components:
            return set_error(state, "没有可转换的React组件")

        slides: list[SlidevSlide] = []
        outline = state.get("outline")

        try:
            # Generate title slide
            title = outline.title if outline else "Presentation"
            title_slide = SlidevSlide(
                frontmatter={
                    "theme": "default",
                    "title": title,
                    "layout": "cover",
                },
                content=f"# {title}\n\n演示文稿",
            )
            slides.append(title_slide)

            # Convert each component
            for component in components:
                prompt = get_slidev_prompt(component.code)

                messages = [
                    SystemMessage(content="你是Slidev格式专家，擅长将React组件转换为Slidev Markdown。"),
                    HumanMessage(content=prompt),
                ]

                response = await self.llm.ainvoke(messages)
                slide_content = response.content.strip()

                # Remove markdown code block if present
                slide_content = _extract_code_block(slide_content, "markdown")
                if slide_content.startswith("```"):
                    slide_content = slide_content.split("\n", 1)[1] if "\n" in slide_content else ""
                if slide_content.endswith("```"):
                    slide_content = slide_content.rsplit("```", 1)[0]

                slide = SlidevSlide(
                    frontmatter={"layout": "default"},
                    content=slide_content.strip(),
                )
                slides.append(slide)

            # Assemble slides.md
            slides_md = self._assemble_slides_md(slides)

            logger.info(
                "Slidev conversion completed",
                session_id=state["session_id"],
                slides_count=len(slides),
            )

            return set_slidev_result(state, slides, slides_md)

        except Exception as e:
            logger.error(
                "Slidev conversion failed",
                session_id=state["session_id"],
                error=str(e),
            )
            return set_error(state, f"Slidev转换失败: {e!s}")

    def _assemble_slides_md(self, slides: list[SlidevSlide]) -> str:
        """Assemble slides into a complete slides.md file.

        Args:
            slides: List of SlidevSlide objects

        Returns:
            Complete slides.md content
        """
        parts = []

        for i, slide in enumerate(slides):
            # Build frontmatter
            if slide.frontmatter:
                frontmatter_lines = ["---"]
                for key, value in slide.frontmatter.items():
                    frontmatter_lines.append(f"{key}: {value}")
                frontmatter_lines.append("---")
                frontmatter = "\n".join(frontmatter_lines)
            else:
                frontmatter = ""

            # Combine frontmatter and content
            if frontmatter:
                slide_text = f"{frontmatter}\n\n{slide.content}"
            else:
                slide_text = slide.content

            parts.append(slide_text)

        # Join with slide separator
        return "\n\n---\n\n".join(parts)


def create_workflow(llm_config: LLMConfig) -> PresentationWorkflow:
    """Create a presentation generation workflow.

    Args:
        llm_config: LLM configuration

    Returns:
        Configured PresentationWorkflow instance
    """
    return PresentationWorkflow(llm_config)
