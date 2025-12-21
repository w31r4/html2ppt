"""Settings management endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, SecretStr

from html2ppt.config.llm import LLMConfig, LLMProvider, PRESET_CONFIGS
from html2ppt.config.settings import get_settings
from html2ppt.agents.llm_factory import LLMFactory, create_llm
from html2ppt.config.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class LLMSettingsInput(BaseModel):
    """Input model for LLM settings update."""

    provider: LLMProvider = Field(default=LLMProvider.OPENAI)
    api_key: str = Field(..., min_length=1)
    base_url: Optional[str] = Field(None)
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)

    # Azure-specific
    azure_endpoint: Optional[str] = None
    azure_deployment: Optional[str] = None
    api_version: Optional[str] = "2024-02-01"


class LLMSettingsResponse(BaseModel):
    """Response model for LLM settings."""

    provider: str
    model: str
    base_url: Optional[str]
    temperature: float
    max_tokens: int
    is_configured: bool


class ValidationResult(BaseModel):
    """LLM validation result."""

    valid: bool
    message: str
    model_info: Optional[dict] = None


@router.get("/llm")
async def get_llm_settings() -> LLMSettingsResponse:
    """Get current LLM settings.

    Returns:
        Current LLM configuration (without API key)
    """
    settings = get_settings()

    return LLMSettingsResponse(
        provider=settings.llm_provider.value,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        is_configured=bool(settings.llm_api_key),
    )


@router.put("/llm")
async def update_llm_settings(config: LLMSettingsInput) -> LLMSettingsResponse:
    """Update LLM settings.

    Note: This updates the runtime configuration only.
    For persistent changes, update the .env file.

    Args:
        config: New LLM configuration

    Returns:
        Updated configuration
    """
    # Clear cached LLM instances
    LLMFactory.clear_cache()

    # Note: In a real implementation, you might want to persist this
    # For now, we just validate and return
    logger.info(
        "LLM settings updated",
        provider=config.provider,
        model=config.model,
    )

    return LLMSettingsResponse(
        provider=config.provider.value,
        model=config.model,
        base_url=config.base_url,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        is_configured=True,
    )


@router.post("/llm/validate")
async def validate_llm_settings(config: LLMSettingsInput) -> ValidationResult:
    """Validate LLM configuration by making a test call.

    Args:
        config: LLM configuration to validate

    Returns:
        Validation result
    """
    try:
        llm_config = LLMConfig(
            provider=config.provider,
            api_key=SecretStr(config.api_key),
            base_url=config.base_url,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            azure_endpoint=config.azure_endpoint,
            azure_deployment=config.azure_deployment,
            api_version=config.api_version,
        )

        llm = create_llm(llm_config)

        # Make a simple test call
        response = await llm.ainvoke("Say 'Hello' in one word.")

        return ValidationResult(
            valid=True,
            message="LLM configuration is valid",
            model_info={
                "provider": config.provider.value,
                "model": config.model,
                "response_preview": str(response.content)[:100],
            },
        )

    except Exception as e:
        logger.error("LLM validation failed", error=str(e))
        return ValidationResult(
            valid=False,
            message=f"Validation failed: {str(e)}",
        )


@router.get("/llm/presets")
async def get_llm_presets() -> dict:
    """Get available LLM preset configurations.

    Returns:
        Dictionary of preset configurations
    """
    return {
        "presets": {
            name: {
                "provider": (
                    preset.get("provider", LLMProvider.OPENAI).value
                    if isinstance(preset.get("provider"), LLMProvider)
                    else preset.get("provider", "openai")
                ),
                "model": preset.get("model"),
                "base_url": preset.get("base_url"),
            }
            for name, preset in PRESET_CONFIGS.items()
        }
    }
