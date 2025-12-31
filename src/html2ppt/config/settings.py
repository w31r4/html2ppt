"""Application settings with environment variable support."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from html2ppt.config.llm import LLMConfig, LLMProvider
from html2ppt.config.reflection import ReflectionConfig


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment variables can be set directly or via a .env file.
    All variables are prefixed with HTML2PPT_.

    Example .env file:
        HTML2PPT_LLM_PROVIDER=openai
        HTML2PPT_LLM_API_KEY=sk-xxx
        HTML2PPT_LLM_MODEL=gpt-4o
        HTML2PPT_LLM_BASE_URL=https://api.openai.com/v1
    """

    model_config = SettingsConfigDict(
        env_prefix="HTML2PPT_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = Field(default="HTML2PPT", description="Application name")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="pretty",
        description="Logging output format: pretty or json",
    )

    # Server Settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # LLM Settings (flat structure for env var compatibility)
    llm_provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="LLM provider",
    )
    llm_api_key: str = Field(
        default="",
        description="LLM API key",
    )
    llm_base_url: Optional[str] = Field(
        default=None,
        description="Custom base URL for OpenAI-compatible endpoints",
    )
    llm_model: str = Field(
        default="gpt-4o",
        description="LLM model name",
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM sampling temperature",
    )
    llm_max_tokens: int = Field(
        default=4096,
        gt=0,
        description="Maximum tokens in response",
    )

    # Azure-specific (optional)
    llm_azure_endpoint: Optional[str] = Field(
        default=None,
        description="Azure OpenAI endpoint",
    )
    llm_azure_deployment: Optional[str] = Field(
        default=None,
        description="Azure OpenAI deployment name",
    )
    llm_api_version: str = Field(
        default="2024-02-01",
        description="Azure API version",
    )

    # Research Settings (Tavily)
    tavily_api_key: str = Field(
        default="",
        description="Tavily API key for research agent (optional)",
    )

    # Reflection Settings (Reviewer) - default disabled
    reflection_enabled: bool = Field(
        default=False,
        description="Enable reflection review stages (optional)",
    )
    reflection_per_slide_max_rewrites: int = Field(
        default=2,
        ge=0,
        description="Maximum rewrite attempts per slide during reflection review",
    )
    reflection_enable_llm_review: bool = Field(
        default=True,
        description="Enable LLM-as-a-judge per-slide evaluation",
    )
    reflection_enable_rule_text_density: bool = Field(
        default=True,
        description="Enable per-slide text density rule",
    )
    reflection_text_char_limit: int = Field(
        default=900,
        ge=0,
        description="Approximate visible text character limit per slide",
    )
    reflection_enable_rule_point_density: bool = Field(
        default=True,
        description="Enable per-slide point density rules",
    )
    reflection_max_points_per_slide: int = Field(
        default=8,
        ge=0,
        description="Maximum number of bullet points per slide (approximate)",
    )
    reflection_max_chars_per_point: int = Field(
        default=120,
        ge=0,
        description="Maximum approximate characters per bullet point",
    )
    reflection_enable_rule_root_container: bool = Field(
        default=True,
        description="Re-enforce existing root container constraints during review",
    )
    reflection_evaluator_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for evaluator LLM calls",
    )
    reflection_enable_global_review: bool = Field(
        default=False,
        description="Enable global deck review stage",
    )
    reflection_global_max_rewrite_passes: int = Field(
        default=1,
        ge=0,
        description="Maximum number of global rewrite passes",
    )

    # Pagination Settings (auto split overflow content)
    pagination_enabled: bool = Field(
        default=True,
        description="Enable automatic pagination review before Slidev assembly",
    )
    pagination_max_bullets: int = Field(
        default=6,
        ge=1,
        description="Maximum bullet points per slide before splitting",
    )
    pagination_max_chars: int = Field(
        default=260,
        ge=0,
        description="Approximate max characters per slide before splitting",
    )
    pagination_max_table_rows: int = Field(
        default=8,
        ge=1,
        description="Maximum markdown table rows per slide before splitting",
    )
    pagination_max_passes: int = Field(
        default=2,
        ge=0,
        description="Maximum pagination passes per session",
    )
    pagination_max_splits_per_section: int = Field(
        default=3,
        ge=0,
        description="Maximum extra splits per section (excluding the original)",
    )
    pagination_refiner_enabled: bool = Field(
        default=True,
        description="Enable LLM refiner fallback for pagination",
    )
    pagination_continuation_suffix: str = Field(
        default=" (续)",
        description="Suffix appended to continuation slide titles",
    )

    # Slidev Settings
    slidev_canvas_width: Optional[int] = Field(
        default=None,
        ge=1,
        description="Slidev canvas width (frontmatter canvasWidth)",
    )
    slidev_aspect_ratio: Optional[str] = Field(
        default=None,
        description="Slidev aspect ratio (frontmatter aspectRatio, e.g. 16/9)",
    )

    # Storage Settings
    data_dir: Path = Field(
        default=Path("data"),
        description="Data directory for session storage",
    )
    output_dir: Path = Field(
        default=Path("output"),
        description="Output directory for generated files",
    )
    auto_save_output: bool = Field(
        default=True,
        description="Automatically save slides.md and components after completion",
    )

    def get_llm_config(self) -> LLMConfig:
        """Convert flat settings to LLMConfig object."""
        from pydantic import SecretStr

        return LLMConfig(
            provider=self.llm_provider,
            api_key=SecretStr(self.llm_api_key),
            base_url=self.llm_base_url,
            model=self.llm_model,
            temperature=self.llm_temperature,
            max_tokens=self.llm_max_tokens,
            azure_endpoint=self.llm_azure_endpoint,
            azure_deployment=self.llm_azure_deployment,
            api_version=self.llm_api_version,
        )

    def get_reflection_config(self) -> ReflectionConfig:
        """Convert flat settings to ReflectionConfig object."""
        return ReflectionConfig(
            enabled=self.reflection_enabled,
            per_slide_max_rewrites=self.reflection_per_slide_max_rewrites,
            enable_llm_review=self.reflection_enable_llm_review,
            enable_rule_text_density=self.reflection_enable_rule_text_density,
            text_char_limit=self.reflection_text_char_limit,
            enable_rule_point_density=self.reflection_enable_rule_point_density,
            max_points_per_slide=self.reflection_max_points_per_slide,
            max_chars_per_point=self.reflection_max_chars_per_point,
            enable_rule_root_container=self.reflection_enable_rule_root_container,
            evaluator_temperature=self.reflection_evaluator_temperature,
            enable_global_review=self.reflection_enable_global_review,
            global_max_rewrite_passes=self.reflection_global_max_rewrite_passes,
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: Application settings instance
    """
    return Settings()
