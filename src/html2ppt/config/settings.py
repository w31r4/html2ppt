"""Application settings with environment variable support."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from html2ppt.config.llm import LLMConfig, LLMProvider


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

    # Storage Settings
    data_dir: Path = Field(
        default=Path("data"),
        description="Data directory for session storage",
    )
    output_dir: Path = Field(
        default=Path("output"),
        description="Output directory for generated files",
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


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: Application settings instance
    """
    return Settings()
