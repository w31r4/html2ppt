"""Research agent for gathering topical context via Tavily.

This module provides a ResearchAgent that uses Tavily search to gather
real-time information about presentation topics before outline generation.
"""

from __future__ import annotations

import os
from typing import Any

from html2ppt.config.logging import get_logger
from html2ppt.config.settings import get_settings

logger = get_logger(__name__)


class ResearchAgent:
    """Fetch and format research findings for outline generation.

    The ResearchAgent uses Tavily search API to gather current information
    about a given topic. If no API key is configured, the research step
    is gracefully skipped.
    """

    def __init__(self, api_key: str | None = None, max_results: int = 5) -> None:
        """Initialize the research agent.

        Args:
            api_key: Tavily API key. If None, uses settings.tavily_api_key.
            max_results: Maximum number of search results to fetch.
        """
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.tavily_api_key
        self.max_results = max_results
        self._tool: Any = None

    @property
    def enabled(self) -> bool:
        """Return True when Tavily API key is configured."""
        return bool(self.api_key)

    def _get_tool(self) -> Any:
        """Lazily initialize and return the Tavily search tool.

        Returns:
            TavilySearchResults tool instance.

        Raises:
            ImportError: If langchain-community is not installed.
        """
        if self._tool is None:
            # Set API key in environment for Tavily tool
            if self.api_key:
                os.environ["TAVILY_API_KEY"] = self.api_key

            try:
                from langchain_community.tools.tavily_search import TavilySearchResults
            except ImportError as e:
                logger.error(
                    "langchain-community not installed",
                    error=str(e),
                )
                raise ImportError(
                    "langchain-community is required for research agent. "
                    "Install with: pip install langchain-community"
                ) from e

            self._tool = TavilySearchResults(max_results=self.max_results)

        return self._tool

    async def research(self, query: str) -> str:
        """Run Tavily search and return a formatted summary.

        Args:
            query: Search query describing the presentation topic.

        Returns:
            Formatted research findings as a string, or empty string if
            research is disabled, fails, or returns no results.
        """
        cleaned_query = query.strip()
        if not cleaned_query:
            logger.debug("Research skipped: empty query")
            return ""

        if not self.enabled:
            logger.info("Research skipped: Tavily API key not configured")
            return ""

        try:
            tool = self._get_tool()
            results = await tool.ainvoke({"query": cleaned_query})
            return self._format_results(results)
        except ImportError:
            # Already logged in _get_tool
            return ""
        except Exception as exc:
            logger.warning(
                "Research failed, continuing without findings",
                error=str(exc),
            )
            return ""

    def _format_results(self, results: Any) -> str:
        """Format Tavily search results into a readable summary.

        Args:
            results: Raw results from Tavily search.

        Returns:
            Formatted string with research findings.
        """
        if not results:
            return ""

        # Handle string results directly
        if isinstance(results, str):
            return results.strip()

        # Handle dict with nested results
        if isinstance(results, dict):
            results = results.get("results") or results.get("data") or results.get("items") or results

        # Handle list of result items
        if isinstance(results, list):
            lines: list[str] = []
            for item in results:
                if not isinstance(item, dict):
                    continue

                title = str(item.get("title") or item.get("name") or "").strip()
                snippet = str(item.get("content") or item.get("snippet") or item.get("summary") or "").strip()
                url = str(item.get("url") or item.get("link") or "").strip()

                if not title and not snippet:
                    continue

                # Build formatted line
                if title and snippet:
                    line = f"- **{title}**: {snippet}"
                elif title:
                    line = f"- **{title}**"
                else:
                    line = f"- {snippet}"

                if url:
                    line = f"{line} ([来源]({url}))"

                lines.append(line)

            return "\n".join(lines).strip()

        # Fallback for unknown format
        return str(results).strip()
