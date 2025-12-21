"""Configuration module for HTML2PPT."""

from html2ppt.config.settings import Settings, get_settings
from html2ppt.config.llm import LLMConfig, LLMProvider

__all__ = ["Settings", "get_settings", "LLMConfig", "LLMProvider"]
