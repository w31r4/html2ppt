"""LangGraph workflow for presentation generation."""

import asyncio
import re
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from html2ppt.agents.design_director import DesignDirectorAgent
from html2ppt.agents.llm_factory import create_llm
from html2ppt.agents.prompts import get_outline_prompt, get_vue_fix_prompt, get_vue_prompt
from html2ppt.agents.reflection_reviewer import ReflectionReviewer
from html2ppt.agents.research import ResearchAgent
from html2ppt.agents.state import (
    Outline,
    OutlineSection,
    SlidevSlide,
    VueComponent,
    WorkflowStage,
    WorkflowState,
    confirm_outline,
    set_error,
    set_slidev_result,
    update_outline,
)
from html2ppt.agents.validators import (
    format_validation_errors_for_prompt,
    validate_vue_component,
)
from html2ppt.config.llm import LLMConfig
from html2ppt.config.logging import get_logger
from html2ppt.config.reflection import ReflectionConfig

logger = get_logger(__name__)

# Maximum number of validation fix retries
MAX_VALIDATION_RETRIES = 3


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
    """Convert section title to ASCII-only Vue component name.

    Args:
        title: Section title

    Returns:
        PascalCase component name
    """
    # Keep ASCII letters/numbers/spaces only to avoid non-ASCII component names
    cleaned = re.sub(r"[^A-Za-z0-9\s]", "", title)
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

    def __init__(
        self,
        llm_config: LLMConfig,
        reflection_config: ReflectionConfig | None = None,
    ):
        """Initialize workflow with LLM configuration.

        Args:
            llm_config: Configuration for the LLM backend
            reflection_config: Optional reflection reviewer configuration
        """
        self.llm_config = llm_config
        self.llm = create_llm(llm_config)

        self.reflection_config = reflection_config or ReflectionConfig()
        self.reflection_reviewer: ReflectionReviewer | None = None
        if self.reflection_config.enabled:
            evaluator_llm = self.llm
            if self.reflection_config.enable_llm_review:
                evaluator_config = llm_config.model_copy(
                    update={"temperature": self.reflection_config.evaluator_temperature}
                )
                evaluator_llm = create_llm(evaluator_config)

            self.reflection_reviewer = ReflectionReviewer(
                generator_llm=self.llm,
                evaluator_llm=evaluator_llm,
                config=self.reflection_config,
            )

        self.research_agent = ResearchAgent()
        self.design_director = DesignDirectorAgent(self.llm)
        self.graph = self._build_graph()
        self.checkpointer = MemorySaver()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph.

        Returns:
            Configured StateGraph
        """
        graph = StateGraph(WorkflowState)

        # Add nodes
        graph.add_node("research_topic", self._research_topic_node)
        graph.add_node("generate_outline", self._generate_outline_node)
        graph.add_node("human_review", self._human_review_node)
        graph.add_node("design_director", self._design_director_node)
        graph.add_node("generate_vue", self._generate_vue_node)
        graph.add_node("assemble_slidev", self._assemble_slidev_node)

        # Add edges
        graph.add_edge(START, "research_topic")
        graph.add_edge("research_topic", "generate_outline")
        graph.add_edge("generate_outline", "human_review")

        # Conditional edge after human review
        graph.add_conditional_edges(
            "human_review",
            self._route_after_review,
            {
                "regenerate": "research_topic",
                "continue": "design_director",
            },
        )

        # Design director → Vue generation → Assembly
        graph.add_edge("design_director", "generate_vue")
        graph.add_edge("generate_vue", "assemble_slidev")
        graph.add_edge("assemble_slidev", END)

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

    async def _research_topic_node(self, state: WorkflowState) -> dict:
        """Research topic before outline generation.

        This node uses Tavily search to gather real-time information
        about the presentation topic. If Tavily API key is not configured,
        this step is gracefully skipped.

        Args:
            state: Current workflow state

        Returns:
            State update with research findings
        """
        logger.info("Researching topic", session_id=state["session_id"])

        # Build query from requirement and supplement
        query_parts = [state["requirement"]]
        supplement = state.get("supplement")
        if supplement:
            query_parts.append(supplement)
        query = "\n".join(query_parts)

        if not self.research_agent.enabled:
            logger.info(
                "Research skipped: Tavily API key not configured",
                session_id=state["session_id"],
            )
            return {"research_findings": None}

        findings = await self.research_agent.research(query)

        if findings:
            logger.info(
                "Research completed",
                session_id=state["session_id"],
                findings_length=len(findings),
            )
        else:
            logger.info(
                "Research returned no findings",
                session_id=state["session_id"],
            )

        return {"research_findings": findings or None}

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
                research_findings=state.get("research_findings"),
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

        # If supplement was added, regenerate (including research)
        if state.get("supplement"):
            return "regenerate"

        return "continue"

    async def _design_director_node(self, state: WorkflowState) -> dict:
        """Generate global design system after outline confirmation.

        This node creates a unified design system that all Vue slide
        components must follow, ensuring visual consistency across
        the entire presentation.

        Args:
            state: Current workflow state

        Returns:
            State update with design system
        """
        logger.info("Generating design system", session_id=state["session_id"])

        # Get outline markdown for context
        outline_markdown = state.get("outline_markdown")
        outline = state.get("outline")
        if not outline_markdown and outline:
            outline_markdown = outline.raw_markdown

        try:
            design_system = await self.design_director.generate(
                requirement=state["requirement"],
                outline_markdown=outline_markdown or "",
                supplement=state.get("supplement"),
                research_findings=state.get("research_findings"),
            )

            logger.info(
                "Design system generated",
                session_id=state["session_id"],
                theme_name=design_system.theme_name,
            )

            return {"design_system": design_system}

        except Exception as e:
            logger.warning(
                "Design system generation failed, proceeding without design system",
                session_id=state["session_id"],
                error=str(e),
            )
            # Graceful degradation: continue without design system
            return {"design_system": None}

    async def _generate_vue_node(self, state: WorkflowState) -> dict:
        """Generate Vue components for each section.

        Args:
            state: Current workflow state

        Returns:
            State update with generated components
        """
        logger.info(
            "Generating Vue components",
            session_id=state["session_id"],
        )

        state["stage"] = WorkflowStage.VUE_GENERATING

        outline = state.get("outline")
        if not outline:
            # Parse from markdown if not structured
            outline_md = state.get("outline_markdown", "")
            outline = Outline.from_markdown(outline_md)

        # Get design system for visual consistency
        design_system = state.get("design_system")
        design_system_data = design_system.model_dump() if design_system else None

        components: list[VueComponent] = []
        total_sections = len(outline.sections)

        if total_sections == 0:
            return set_error(state, "大纲为空，无法生成组件")

        try:
            semaphore = asyncio.Semaphore(4)
            used_component_names: set[str] = set()
            component_names: list[str] = []
            for index, section in enumerate(outline.sections):
                base_name = _sanitize_component_name(section.title)
                if base_name == "Slide":
                    candidate = f"Slide{index + 1}"
                else:
                    candidate = base_name if base_name.endswith("Slide") else f"{base_name}Slide"

                component_name = candidate
                suffix = 2
                while component_name in used_component_names:
                    component_name = f"{candidate}{suffix}"
                    suffix += 1
                used_component_names.add(component_name)
                component_names.append(component_name)

            async def generate_component(index: int, section: OutlineSection) -> tuple[int, VueComponent]:
                async with semaphore:
                    logger.info(
                        "Generating component",
                        session_id=state["session_id"],
                        section=section.title,
                        progress=f"{index + 1}/{total_sections}",
                    )

                    # Extract visual suggestions and animation effects
                    visual_dict = None
                    if section.visual_suggestions:
                        visual_dict = {
                            "background": section.visual_suggestions.background,
                            "core_image": section.visual_suggestions.core_image,
                            "layout": section.visual_suggestions.layout,
                            "image_url": section.visual_suggestions.image_url,
                        }

                    animation_dict = None
                    if section.animation_effects:
                        animation_dict = {
                            "description": section.animation_effects.description,
                            "elements": section.animation_effects.elements,
                        }

                    prompt = get_vue_prompt(
                        section_title=section.title,
                        section_points=section.points,
                        speaker_notes=section.speaker_notes,
                        visual_suggestions=visual_dict,
                        design_system=design_system_data,
                        animation_effects=animation_dict,
                        raw_content=section.raw_content,
                    )

                    messages = [
                        SystemMessage(
                            content="你是一位专业的Vue前端开发工程师和动画专家，擅长创建美观且富有动感的演示文稿组件。"
                        ),
                        HumanMessage(content=prompt),
                    ]

                    response = await self.llm.ainvoke(messages)
                    code = _extract_code_block(response.content, "vue")

                    # Validation and fix loop
                    retry_count = 0
                    validation_warnings: list[str] = []

                    while retry_count < MAX_VALIDATION_RETRIES:
                        validation_result = validate_vue_component(code)

                        if validation_result.is_valid:
                            logger.info(
                                "Component validation passed",
                                session_id=state["session_id"],
                                section=section.title,
                                retry_count=retry_count,
                            )
                            break

                        retry_count += 1
                        logger.warning(
                            "Component validation failed, attempting fix",
                            session_id=state["session_id"],
                            section=section.title,
                            retry_count=retry_count,
                            errors=validation_result.errors,
                        )

                        if retry_count >= MAX_VALIDATION_RETRIES:
                            # Max retries reached, keep last version with warnings
                            validation_warnings = validation_result.errors + validation_result.warnings
                            logger.warning(
                                "Max validation retries reached, keeping last version with warnings",
                                session_id=state["session_id"],
                                section=section.title,
                                warnings=validation_warnings,
                            )
                            break

                        # Generate fix prompt and retry
                        error_text = format_validation_errors_for_prompt(validation_result)
                        fix_prompt = get_vue_fix_prompt(code, error_text)

                        fix_messages = [
                            SystemMessage(content="你是一位专业的Vue前端开发工程师，擅长修复组件问题。"),
                            HumanMessage(content=fix_prompt),
                        ]

                        fix_response = await self.llm.ainvoke(fix_messages)
                        code = _extract_code_block(fix_response.content, "vue")

                    # Reflection review & (optional) rewrite loop
                    reflection_warnings: list[str] = []
                    reflection_retry_count = 0
                    if self.reflection_reviewer:
                        try:
                            reflection_result = await self.reflection_reviewer.review_and_rewrite(
                                section=section,
                                code=code,
                                design_system=design_system_data,
                                session_id=state["session_id"],
                            )
                            code = reflection_result.code
                            reflection_warnings = reflection_result.warnings
                            reflection_retry_count = reflection_result.retry_count
                        except Exception as exc:
                            logger.warning(
                                "Reflection reviewer failed, continuing without reflection changes",
                                session_id=state["session_id"],
                                section=section.title,
                                error=str(exc),
                            )

                    component = VueComponent(
                        name=component_names[index],
                        code=code,
                        section_title=section.title,
                        validation_warnings=validation_warnings,
                        retry_count=retry_count,
                        reflection_warnings=reflection_warnings,
                        reflection_retry_count=reflection_retry_count,
                    )
                    return index, component

            tasks = [asyncio.create_task(generate_component(i, section)) for i, section in enumerate(outline.sections)]

            results: list[VueComponent | None] = [None] * total_sections
            for task in asyncio.as_completed(tasks):
                index, component = await task
                results[index] = component

            components = [c for c in results if c is not None]

            logger.info(
                "Vue components generated",
                session_id=state["session_id"],
                count=len(components),
            )

            return {
                "vue_components": components,
                "stage": WorkflowStage.VUE_COMPLETED,
                "progress": 0.8,
            }

        except Exception as e:
            logger.error(
                "Vue generation failed",
                session_id=state["session_id"],
                error=str(e),
            )
            return set_error(state, f"Vue组件生成失败: {e!s}")

    async def _assemble_slidev_node(self, state: WorkflowState) -> dict:
        """Assemble Slidev markdown from Vue components.

        Args:
            state: Current workflow state

        Returns:
            State update with Slidev slides
        """
        logger.info(
            "Assembling Slidev markdown",
            session_id=state["session_id"],
        )

        state["stage"] = WorkflowStage.SLIDEV_ASSEMBLING

        components = state.get("vue_components", [])
        if not components:
            return set_error(state, "没有可组装的Vue组件")

        slides: list[SlidevSlide] = []
        outline = state.get("outline")

        try:
            title = outline.title if outline else "Presentation"

            # Assemble each component
            for component in components:
                slide = SlidevSlide(
                    frontmatter={"layout": "default"},
                    content=f"<{component.name} />",
                    component_name=component.name,
                )
                slides.append(slide)

            # Assemble slides.md
            slides_md = self._assemble_slides_md(
                slides,
                global_frontmatter={
                    "theme": "default",
                    "title": title,
                },
            )

            logger.info(
                "Slidev assembly completed",
                session_id=state["session_id"],
                slides_count=len(slides),
            )

            return set_slidev_result(state, slides, slides_md)

        except Exception as e:
            logger.error(
                "Slidev assembly failed",
                session_id=state["session_id"],
                error=str(e),
            )
            return set_error(state, f"Slidev组装失败: {e!s}")

    def _assemble_slides_md(
        self,
        slides: list[SlidevSlide],
        global_frontmatter: dict | None = None,
    ) -> str:
        """Assemble slides into a complete slides.md file.

        Args:
            slides: List of SlidevSlide objects
            global_frontmatter: Optional deck-level frontmatter

        Returns:
            Complete slides.md content
        """
        slide_texts: list[str] = []
        deck_frontmatter = ""

        if global_frontmatter:
            frontmatter_lines = ["---"]
            for key, value in global_frontmatter.items():
                frontmatter_lines.append(f"{key}: {value}")
            frontmatter_lines.append("---")
            deck_frontmatter = "\n".join(frontmatter_lines)

        for i, slide in enumerate(slides):
            # Build frontmatter
            if slide.frontmatter:
                frontmatter_lines = ["---"]
                for key, value in slide.frontmatter.items():
                    frontmatter_lines.append(f"{key}: {value}")
                frontmatter_lines.append("---")
                slide_frontmatter = "\n".join(frontmatter_lines)
            else:
                slide_frontmatter = ""

            # Combine frontmatter and content
            if slide_frontmatter:
                slide_text = f"{slide_frontmatter}\n\n{slide.content}"
            else:
                slide_text = slide.content

            slide_texts.append(slide_text)

        # Join slides with slide separator, keep deck frontmatter at top without a separator
        if deck_frontmatter:
            return deck_frontmatter + "\n\n" + "\n\n---\n\n".join(slide_texts)
        return "\n\n---\n\n".join(slide_texts)


def create_workflow(
    llm_config: LLMConfig,
    *,
    reflection_config: ReflectionConfig | None = None,
) -> PresentationWorkflow:
    """Create a presentation generation workflow.

    Args:
        llm_config: LLM configuration
        reflection_config: Optional reflection reviewer configuration

    Returns:
        Configured PresentationWorkflow instance
    """
    return PresentationWorkflow(llm_config, reflection_config=reflection_config)
