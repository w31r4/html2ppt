"""Design director agent for generating deck-level design systems."""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from html2ppt.agents.state import DesignSystem
from html2ppt.config.logging import get_logger

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

logger = get_logger(__name__)

# System prompt for design director
DESIGN_DIRECTOR_SYSTEM_PROMPT = """你是一位资深的演示文稿设计总监，负责制定统一的设计系统。

你的设计系统将被用于确保整个演示文稿的视觉一致性。每一页幻灯片都必须遵循你制定的规则。

你需要输出一个 JSON 对象，包含以下字段：
- theme_name: 主题名称（简洁有力，如 "科技蓝" "商务简约"）
- color_palette: 色板（语义化键名映射 CSS 颜色值）
- typography: 字体规范（字体族、字号、字重）
- layout_rules: 布局规则（自然语言描述的列表）
- uno_css_classes: 可复用的 UnoCSS 工具类组合"""


class DesignDirectorAgent:
    """Generate a global design system for the presentation deck.

    This agent analyzes the requirement and outline to produce a consistent
    design system that all Vue slide components must follow.
    """

    def __init__(self, llm: "BaseChatModel") -> None:
        """Initialize the design director agent.

        Args:
            llm: Language model for generating the design system.
        """
        self.llm = llm

    async def generate(
        self,
        requirement: str,
        outline_markdown: str | None = None,
        supplement: str | None = None,
        research_findings: str | None = None,
    ) -> DesignSystem:
        """Generate a design system based on the requirement and outline.

        Args:
            requirement: User's original requirement text.
            outline_markdown: The confirmed outline in markdown format.
            supplement: Optional supplementary requirements.
            research_findings: Optional research context.

        Returns:
            A validated DesignSystem object.

        Raises:
            ValueError: If the LLM response cannot be parsed or validated.
        """
        prompt = self._build_prompt(
            requirement=requirement,
            outline_markdown=outline_markdown,
            supplement=supplement,
            research_findings=research_findings,
        )

        messages = [
            SystemMessage(content=DESIGN_DIRECTOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]

        logger.debug("Generating design system", requirement_length=len(requirement))

        response = await self.llm.ainvoke(messages)
        return self._parse_response(str(response.content))

    def _build_prompt(
        self,
        requirement: str,
        outline_markdown: str | None,
        supplement: str | None,
        research_findings: str | None,
    ) -> str:
        """Build the prompt for design system generation.

        Args:
            requirement: User's requirement text.
            outline_markdown: The presentation outline.
            supplement: Optional supplementary text.
            research_findings: Optional research context.

        Returns:
            Formatted prompt string.
        """
        sections = ["## 需求描述", "", requirement, ""]

        if supplement:
            sections.extend(["## 补充需求", "", supplement, ""])

        if research_findings:
            sections.extend(["## 研究参考", "", research_findings, ""])

        outline_content = outline_markdown.strip() if outline_markdown else "(无大纲)"
        sections.extend(["## 大纲", "", outline_content, ""])

        sections.extend(
            [
                "## 输出要求",
                "",
                "请基于以上内容，制定一套可复用的全局设计系统。",
                "",
                "1. 仅输出 JSON 对象，不要包含 Markdown 代码块或解释文字。",
                "2. JSON 字段必须包含：theme_name, color_palette, typography, layout_rules, uno_css_classes。",
                "3. color_palette 使用语义化键名（如 primary, secondary, accent, background, text）映射 CSS 颜色值。",
                "4. typography 使用语义化键名描述字体族、字号、字重（如 heading_font, body_font, title_size）。",
                "5. layout_rules 使用字符串数组，每条规则用自然语言描述。",
                "6. uno_css_classes 使用字符串数组，列出可复用的 UnoCSS 工具类组合。",
            ]
        )

        return "\n".join(sections)

    def _parse_response(self, content: str) -> DesignSystem:
        """Parse the LLM response into a DesignSystem object.

        Args:
            content: Raw LLM response text.

        Returns:
            Validated DesignSystem object.

        Raises:
            ValueError: If parsing or validation fails.
        """
        raw_json = self._extract_json(content)

        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            logger.warning(
                "Design system JSON parse failed",
                error=str(exc),
                raw_content=content[:500],
            )
            raise ValueError(f"Design system JSON parse failed: {exc}") from exc

        try:
            return DesignSystem.model_validate(payload)
        except ValidationError as exc:
            logger.warning(
                "Design system validation failed",
                error=str(exc),
                payload=payload,
            )
            raise ValueError(f"Design system validation failed: {exc}") from exc

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from text that may contain markdown code blocks.

        Args:
            text: Raw text possibly containing JSON.

        Returns:
            Extracted JSON string.
        """
        # Try to find JSON in markdown code block
        match = re.search(r"```json\s*([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()

        # Try generic code block
        match = re.search(r"```\s*([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()

        # Try to find raw JSON object
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1].strip()

        # Return as-is and let JSON parser handle errors
        return text.strip()
