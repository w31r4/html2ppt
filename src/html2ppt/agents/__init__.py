"""Agent modules for HTML2PPT workflow."""

from html2ppt.agents.llm_factory import create_llm, LLMFactory
from html2ppt.agents.prompts import (
    get_outline_prompt,
    get_vue_prompt,
)
from html2ppt.agents.state import (
    Outline,
    OutlineSection,
    VueComponent,
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
    "get_vue_prompt",
    # State
    "Outline",
    "OutlineSection",
    "VueComponent",
    "SlidevSlide",
    "WorkflowStage",
    "WorkflowState",
    "create_initial_state",
    # Workflow
    "PresentationWorkflow",
    "create_workflow",
]
