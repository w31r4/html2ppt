"""Reflection (reviewer) configuration models and helpers."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ReflectionConfig(BaseModel):
    """Configuration for the Reflection Reviewer feature."""

    enabled: bool = Field(default=False, description="Enable reflection review stages")

    # Per-slide review controls
    per_slide_max_rewrites: int = Field(
        default=2,
        ge=0,
        description="Maximum rewrite attempts per slide during reflection review",
    )
    enable_llm_review: bool = Field(
        default=True,
        description="Enable LLM-as-a-judge evaluation during per-slide review",
    )

    # Static (non-rendering) rules
    enable_rule_text_density: bool = Field(default=True, description="Enable text density rule")
    text_char_limit: int = Field(
        default=900,
        ge=0,
        description="Approximate visible text character limit per slide",
    )

    enable_rule_point_density: bool = Field(default=True, description="Enable point density rules")
    max_points_per_slide: int = Field(
        default=8,
        ge=0,
        description="Maximum number of bullet points per slide (approximate)",
    )
    max_chars_per_point: int = Field(
        default=120,
        ge=0,
        description="Maximum approximate characters per bullet point",
    )

    enable_rule_root_container: bool = Field(
        default=True,
        description="Re-enforce existing root container constraints during review",
    )

    # Evaluator call parameters
    evaluator_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for evaluator LLM calls",
    )

    # Global review controls
    enable_global_review: bool = Field(default=False, description="Enable global deck review stage")
    global_max_rewrite_passes: int = Field(
        default=1,
        ge=0,
        description="Maximum number of global rewrite passes",
    )

    # Visual feedback loop controls
    enable_visual_review: bool = Field(
        default=False,
        description="Enable VLM-based visual review using screenshot analysis",
    )
    visual_review_model: str = Field(
        default="gpt-4o",
        description="Model to use for visual review (must support vision)",
    )
    max_visual_retries: int = Field(
        default=2,
        ge=0,
        description="Maximum visual review retry attempts per slide",
    )
    renderer_url: str = Field(
        default="http://browserless:3000",
        description="URL of the Browserless Chrome service",
    )
    vue_preview_url: str = Field(
        default="http://vue-preview:5173",
        description="URL of the Vue preview service for rendering",
    )
    visual_review_timeout_ms: int = Field(
        default=30000,
        ge=1000,
        description="Timeout for visual review operations in milliseconds",
    )


def merge_reflection_config(
    base: ReflectionConfig,
    override: Optional[dict[str, Any]],
) -> tuple[ReflectionConfig, list[str]]:
    """Merge a base config with an override dict.

    Returns:
        (effective_config, overridden_fields)
    """
    if not override:
        return base, []

    model_data = base.model_dump()
    overridden_fields: list[str] = []
    for key, value in override.items():
        if key in model_data:
            model_data[key] = value
            overridden_fields.append(key)

    return ReflectionConfig.model_validate(model_data), overridden_fields
