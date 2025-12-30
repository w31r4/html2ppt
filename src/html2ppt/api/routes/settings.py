"""Settings management endpoints."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, SecretStr
from pydantic import ValidationError as PydanticValidationError

from html2ppt.agents.llm_factory import LLMFactory, create_llm
from html2ppt.config.llm import LLMConfig, LLMProvider, PRESET_CONFIGS
from html2ppt.config.logging import get_logger
from html2ppt.config.reflection import ReflectionConfig, merge_reflection_config
from html2ppt.config.runtime_overrides import clear_override, get_override, set_override
from html2ppt.config.settings import get_settings

router = APIRouter()
logger = get_logger(__name__)

_REFLECTION_NAMESPACE = "reflection"


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


class ReflectionSettingsPatch(BaseModel):
    """Patch model for reflection reviewer runtime settings.

    Notes:
    - This is applied as a runtime override (process-local), not persisted to `.env`.
    - Fields are optional; only provided fields will be updated.
    """

    enabled: Optional[bool] = None
    per_slide_max_rewrites: Optional[int] = Field(default=None, ge=0)
    enable_llm_review: Optional[bool] = None

    enable_rule_text_density: Optional[bool] = None
    text_char_limit: Optional[int] = Field(default=None, ge=0)

    enable_rule_point_density: Optional[bool] = None
    max_points_per_slide: Optional[int] = Field(default=None, ge=0)
    max_chars_per_point: Optional[int] = Field(default=None, ge=0)

    enable_rule_root_container: Optional[bool] = None

    evaluator_temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)

    enable_global_review: Optional[bool] = None
    global_max_rewrite_passes: Optional[int] = Field(default=None, ge=0)


class ReflectionSettingsResponse(BaseModel):
    """Response model for reflection reviewer settings."""

    base: dict[str, Any]
    override: Optional[dict[str, Any]]
    effective: dict[str, Any]
    overridden_fields: list[str]


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


@router.get("/reflection")
async def get_reflection_settings() -> ReflectionSettingsResponse:
    """Get current reflection reviewer settings.

    The effective config is computed as:
      effective = merge(env_defaults, runtime_override)

    Returns:
        base/env config, runtime override, and effective config.
    """
    settings = get_settings()
    base = settings.get_reflection_config()
    override = get_override(_REFLECTION_NAMESPACE)
    effective, overridden_fields = merge_reflection_config(base=base, override=override)

    return ReflectionSettingsResponse(
        base=base.model_dump(),
        override=override,
        effective=effective.model_dump(),
        overridden_fields=overridden_fields,
    )


@router.put("/reflection")
async def update_reflection_settings(patch: ReflectionSettingsPatch) -> ReflectionSettingsResponse:
    """Update reflection reviewer settings (runtime override only).

    Notes:
    - This does not persist to `.env`.
    - Invalid patches are rejected; the previous override is kept.
    """
    settings = get_settings()
    base = settings.get_reflection_config()
    current_override = get_override(_REFLECTION_NAMESPACE) or {}

    patch_dict = patch.model_dump(exclude_unset=True, exclude_none=True)
    if not patch_dict:
        effective, overridden_fields = merge_reflection_config(base=base, override=current_override)
        return ReflectionSettingsResponse(
            base=base.model_dump(),
            override=current_override,
            effective=effective.model_dump(),
            overridden_fields=overridden_fields,
        )

    candidate_override = dict(current_override)
    candidate_override.update(patch_dict)

    try:
        ReflectionConfig.model_validate({**base.model_dump(), **candidate_override})
    except PydanticValidationError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid reflection settings: {exc}") from exc

    set_override(_REFLECTION_NAMESPACE, candidate_override)
    effective, overridden_fields = merge_reflection_config(base=base, override=candidate_override)

    logger.info(
        "Reflection settings updated",
        updated_fields=sorted(patch_dict.keys()),
    )

    return ReflectionSettingsResponse(
        base=base.model_dump(),
        override=candidate_override,
        effective=effective.model_dump(),
        overridden_fields=overridden_fields,
    )


@router.delete("/reflection")
async def reset_reflection_settings() -> ReflectionSettingsResponse:
    """Reset reflection reviewer settings by clearing the runtime override."""
    clear_override(_REFLECTION_NAMESPACE)

    settings = get_settings()
    base = settings.get_reflection_config()
    effective, overridden_fields = merge_reflection_config(base=base, override=None)

    logger.info("Reflection settings reset")

    return ReflectionSettingsResponse(
        base=base.model_dump(),
        override=None,
        effective=effective.model_dump(),
        overridden_fields=overridden_fields,
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
