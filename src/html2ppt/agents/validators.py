"""Vue component validators for Slidev compatibility."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from html2ppt.config.logging import get_logger

logger = get_logger(__name__)


class ValidationSeverity(str, Enum):
    """Severity level for validation issues."""

    ERROR = "error"
    WARNING = "warning"


@dataclass
class ValidationRule:
    """A single validation rule definition."""

    id: str
    pattern: str
    message: str
    severity: ValidationSeverity
    check_root_only: bool = True


@dataclass
class ValidationIssue:
    """A validation issue found in the component."""

    rule_id: str
    message: str
    severity: ValidationSeverity


@dataclass
class ValidationResult:
    """Result of validating a Vue component."""

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Populate errors and warnings lists from issues."""
        for issue in self.issues:
            if issue.severity == ValidationSeverity.ERROR:
                self.errors.append(issue.message)
            else:
                self.warnings.append(issue.message)


# Default validation rules for Slidev compatibility
SLIDEV_VALIDATION_RULES = [
    ValidationRule(
        id="root_height",
        pattern=r"\b(h-full|h-screen|min-h-full|min-h-screen)\b",
        message="根容器缺少高度约束类，建议添加 h-full 或 h-screen 确保组件填满幻灯片高度",
        severity=ValidationSeverity.ERROR,
    ),
    ValidationRule(
        id="root_width",
        pattern=r"\b(w-full|w-screen)\b",
        message="根容器缺少宽度约束类，建议添加 w-full 确保组件填满幻灯片宽度",
        severity=ValidationSeverity.WARNING,
    ),
    ValidationRule(
        id="overflow_control",
        pattern=r"\b(overflow-hidden|overflow-auto|overflow-clip)\b",
        message="根容器缺少overflow控制，建议添加 overflow-hidden 防止内容溢出幻灯片边界",
        severity=ValidationSeverity.ERROR,
    ),
]


def _extract_template_content(vue_code: str) -> Optional[str]:
    """Extract the template content from Vue SFC code.

    Args:
        vue_code: Complete Vue SFC code

    Returns:
        Template content or None if not found
    """
    match = re.search(r"<template[^>]*>([\s\S]*?)</template>", vue_code, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _extract_root_element(template: str) -> Optional[str]:
    """Extract the root element from template content.

    Args:
        template: Template content

    Returns:
        Root element opening tag or None if not found
    """
    # Skip whitespace and comments at the beginning
    template = template.strip()

    # Skip HTML comments
    while template.startswith("<!--"):
        end_comment = template.find("-->")
        if end_comment == -1:
            break
        template = template[end_comment + 3 :].strip()

    # Find the first element opening tag
    match = re.match(r"<([a-zA-Z][a-zA-Z0-9-]*)[^>]*>", template)
    if match:
        return match.group(0)
    return None


def _extract_root_class_attribute(root_element: str) -> str:
    """Extract class attribute value from root element.

    Args:
        root_element: Root element opening tag

    Returns:
        Class attribute value or empty string
    """
    # Handle both static class and :class binding
    # Static class: class="..."
    static_match = re.search(r'\bclass="([^"]*)"', root_element)
    if static_match:
        return static_match.group(1)

    # Single-quoted static class: class='...'
    static_match_single = re.search(r"\bclass='([^']*)'", root_element)
    if static_match_single:
        return static_match_single.group(1)

    return ""


def validate_vue_component(
    vue_code: str,
    rules: list[ValidationRule] | None = None,
) -> ValidationResult:
    """Validate a Vue SFC component for Slidev compatibility.

    Args:
        vue_code: Complete Vue SFC code
        rules: Optional custom validation rules, defaults to SLIDEV_VALIDATION_RULES

    Returns:
        ValidationResult with issues found
    """
    if rules is None:
        rules = SLIDEV_VALIDATION_RULES

    issues: list[ValidationIssue] = []

    # Extract template
    template = _extract_template_content(vue_code)
    if template is None:
        return ValidationResult(
            is_valid=False,
            issues=[
                ValidationIssue(
                    rule_id="no_template",
                    message="Vue组件缺少<template>块",
                    severity=ValidationSeverity.ERROR,
                )
            ],
        )

    # Extract root element
    root_element = _extract_root_element(template)
    if root_element is None:
        return ValidationResult(
            is_valid=False,
            issues=[
                ValidationIssue(
                    rule_id="no_root_element",
                    message="Vue组件模板缺少根元素",
                    severity=ValidationSeverity.ERROR,
                )
            ],
        )

    # Extract class attribute from root element
    root_classes = _extract_root_class_attribute(root_element)

    logger.debug(
        "Validating Vue component",
        root_element=root_element[:100],
        root_classes=root_classes,
    )

    # Apply validation rules
    for rule in rules:
        if rule.check_root_only:
            # Check if pattern exists in root element's classes
            if not re.search(rule.pattern, root_classes):
                issues.append(
                    ValidationIssue(
                        rule_id=rule.id,
                        message=rule.message,
                        severity=rule.severity,
                    )
                )

    # Determine if valid (no errors, warnings are acceptable)
    has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in issues)

    result = ValidationResult(
        is_valid=not has_errors,
        issues=issues,
    )

    logger.info(
        "Vue component validation completed",
        is_valid=result.is_valid,
        error_count=len(result.errors),
        warning_count=len(result.warnings),
    )

    return result


def format_validation_errors_for_prompt(result: ValidationResult) -> str:
    """Format validation errors for inclusion in a fix prompt.

    Args:
        result: ValidationResult from validate_vue_component

    Returns:
        Formatted string describing the issues for LLM
    """
    if result.is_valid and not result.warnings:
        return ""

    lines = ["## 校验问题\n"]
    lines.append("生成的Vue组件存在以下问题需要修复：\n")

    for i, error in enumerate(result.errors, 1):
        lines.append(f"{i}. **错误**: {error}")

    for i, warning in enumerate(result.warnings, len(result.errors) + 1):
        lines.append(f"{i}. **警告**: {warning}")

    lines.append("\n请修复上述问题，确保根容器元素包含必要的类名。")

    return "\n".join(lines)
