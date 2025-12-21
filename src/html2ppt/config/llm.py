"""LLM configuration schema with multi-backend support."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, SecretStr, model_validator


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    GEMINI = "gemini"


class LLMConfig(BaseModel):
    """Configuration for LLM backend.

    Supports:
    - OpenAI official API
    - OpenAI-compatible endpoints (vLLM, Ollama, OpenRouter, etc.)
    - Azure OpenAI
    - Google Gemini
    """

    provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="LLM provider type",
    )

    # API Configuration
    api_key: SecretStr = Field(
        description="API key for the LLM provider",
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Custom base URL for OpenAI-compatible endpoints. "
        "Examples: http://localhost:8000/v1 (vLLM), "
        "http://localhost:11434/v1 (Ollama), "
        "https://api.openrouter.ai/api/v1 (OpenRouter)",
    )

    # Azure-specific
    azure_endpoint: Optional[str] = Field(
        default=None,
        description="Azure OpenAI endpoint URL",
    )
    azure_deployment: Optional[str] = Field(
        default=None,
        description="Azure OpenAI deployment name",
    )
    api_version: Optional[str] = Field(
        default="2024-02-01",
        description="Azure OpenAI API version",
    )

    # Model Configuration
    model: str = Field(
        default="gpt-4o",
        description="Model name to use",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )
    max_tokens: Optional[int] = Field(
        default=4096,
        gt=0,
        description="Maximum tokens in response",
    )

    # Request Configuration
    timeout: int = Field(
        default=120,
        gt=0,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum number of retries on failure",
    )

    @model_validator(mode="after")
    def validate_provider_config(self) -> "LLMConfig":
        """Validate provider-specific configuration."""
        if self.provider == LLMProvider.AZURE_OPENAI:
            if not self.azure_endpoint:
                raise ValueError("azure_endpoint is required for Azure OpenAI provider")
            if not self.azure_deployment:
                raise ValueError("azure_deployment is required for Azure OpenAI provider")
        return self

    def get_openai_kwargs(self) -> dict:
        """Get kwargs for ChatOpenAI initialization."""
        kwargs = {
            "api_key": self.api_key.get_secret_value(),
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return kwargs

    def get_azure_kwargs(self) -> dict:
        """Get kwargs for AzureChatOpenAI initialization."""
        return {
            "api_key": self.api_key.get_secret_value(),
            "azure_endpoint": self.azure_endpoint,
            "azure_deployment": self.azure_deployment,
            "api_version": self.api_version,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }

    def get_gemini_kwargs(self) -> dict:
        """Get kwargs for ChatGoogleGenerativeAI initialization."""
        return {
            "google_api_key": self.api_key.get_secret_value(),
            "model": self.model,
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }

    class Config:
        """Pydantic model configuration."""

        use_enum_values = True


# Preset configurations for common providers
PRESET_CONFIGS = {
    "openai": {
        "provider": LLMProvider.OPENAI,
        "model": "gpt-4o",
    },
    "openai-mini": {
        "provider": LLMProvider.OPENAI,
        "model": "gpt-4o-mini",
    },
    "gemini": {
        "provider": LLMProvider.GEMINI,
        "model": "gemini-2.0-flash-exp",
    },
    "gemini-pro": {
        "provider": LLMProvider.GEMINI,
        "model": "gemini-1.5-pro",
    },
    "ollama": {
        "provider": LLMProvider.OPENAI,
        "base_url": "http://localhost:11434/v1",
        "model": "llama3.2",
    },
    "vllm": {
        "provider": LLMProvider.OPENAI,
        "base_url": "http://localhost:8000/v1",
        "model": "default",
    },
}
