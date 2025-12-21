"""LLM Factory for multi-backend support."""

from typing import Union

from langchain_core.language_models import BaseChatModel

from html2ppt.config.llm import LLMConfig, LLMProvider
from html2ppt.config.logging import get_logger

logger = get_logger(__name__)


class LLMFactory:
    """Factory for creating LLM instances based on configuration.

    Supports:
    - OpenAI (official and compatible endpoints)
    - Azure OpenAI
    - Google Gemini
    """

    _instances: dict[str, BaseChatModel] = {}

    @classmethod
    def create(cls, config: LLMConfig) -> BaseChatModel:
        """Create an LLM instance based on configuration.

        Args:
            config: LLM configuration

        Returns:
            Configured LangChain chat model

        Raises:
            ValueError: If provider is not supported
        """
        cache_key = cls._get_cache_key(config)

        if cache_key in cls._instances:
            logger.debug("Returning cached LLM instance", provider=config.provider)
            return cls._instances[cache_key]

        logger.info(
            "Creating new LLM instance",
            provider=config.provider,
            model=config.model,
            base_url=config.base_url,
        )

        llm = cls._create_llm(config)
        cls._instances[cache_key] = llm
        return llm

    @classmethod
    def _create_llm(cls, config: LLMConfig) -> BaseChatModel:
        """Internal method to create LLM based on provider."""
        if config.provider == LLMProvider.OPENAI:
            return cls._create_openai(config)
        elif config.provider == LLMProvider.AZURE_OPENAI:
            return cls._create_azure_openai(config)
        elif config.provider == LLMProvider.GEMINI:
            return cls._create_gemini(config)
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")

    @classmethod
    def _create_openai(cls, config: LLMConfig) -> BaseChatModel:
        """Create OpenAI or OpenAI-compatible LLM."""
        from langchain_openai import ChatOpenAI

        kwargs = config.get_openai_kwargs()
        return ChatOpenAI(**kwargs)

    @classmethod
    def _create_azure_openai(cls, config: LLMConfig) -> BaseChatModel:
        """Create Azure OpenAI LLM."""
        from langchain_openai import AzureChatOpenAI

        kwargs = config.get_azure_kwargs()
        return AzureChatOpenAI(**kwargs)

    @classmethod
    def _create_gemini(cls, config: LLMConfig) -> BaseChatModel:
        """Create Google Gemini LLM."""
        from langchain_google_genai import ChatGoogleGenerativeAI

        kwargs = config.get_gemini_kwargs()
        return ChatGoogleGenerativeAI(**kwargs)

    @classmethod
    def _get_cache_key(cls, config: LLMConfig) -> str:
        """Generate cache key for LLM instance."""
        return f"{config.provider}:{config.model}:{config.base_url or 'default'}"

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached LLM instances."""
        cls._instances.clear()
        logger.info("LLM instance cache cleared")


def create_llm(config: LLMConfig) -> BaseChatModel:
    """Convenience function to create LLM instance.

    Args:
        config: LLM configuration

    Returns:
        Configured LangChain chat model
    """
    return LLMFactory.create(config)
