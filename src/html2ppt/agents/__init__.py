"""Agent modules for HTML2PPT workflow."""

from html2ppt.agents.llm_factory import create_llm, LLMFactory
from html2ppt.agents.prompts import (
    get_outline_prompt,
    get_react_prompt,
    get_slidev_prompt,
)
from html2ppt.agents.state import (
    Outline,
    OutlineSection,
    ReactComponent,
    SlidevSlide,
    WorkflowStage,
    WorkflowState,
    create_initial_state,
)
from html2ppt.agents.workflow import PresentationWorkflow, create_workflow

__all__ = [
    # LLM Factory
    "create_llm",
    "LLMFactory",
    # Prompts
    "get_outline_prompt",
    "get_react_prompt",
    "get_slidev_prompt",
    # State
    "Outline",
    "OutlineSection",
    "ReactComponent",
    "SlidevSlide",
    "WorkflowStage",
    "WorkflowState",
    "create_initial_state",
    # Workflow
    "PresentationWorkflow",
    "create_workflow",
]
