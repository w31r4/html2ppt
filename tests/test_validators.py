"""Unit tests for Vue component validators."""

import pytest

from html2ppt.agents.validators import (
    ValidationResult,
    ValidationSeverity,
    _extract_root_class_attribute,
    _extract_root_element,
    _extract_template_content,
    format_validation_errors_for_prompt,
    validate_vue_component,
)


class TestExtractTemplateContent:
    """Tests for _extract_template_content function."""

    def test_extract_simple_template(self):
        code = """<template>
  <div class="container">Hello</div>
</template>"""
        result = _extract_template_content(code)
        assert result is not None
        assert "<div" in result
        assert "Hello" in result

    def test_extract_template_with_script(self):
        code = """<template>
  <div>Content</div>
</template>

<script setup>
const x = 1
</script>"""
        result = _extract_template_content(code)
        assert result is not None
        assert "<div>" in result
        assert "script" not in result

    def test_no_template_returns_none(self):
        code = """<script setup>
const x = 1
</script>"""
        result = _extract_template_content(code)
        assert result is None


class TestExtractRootElement:
    """Tests for _extract_root_element function."""

    def test_extract_div_root(self):
        template = '<div class="h-full w-full">Content</div>'
        result = _extract_root_element(template)
        assert result == '<div class="h-full w-full">'

    def test_skip_comments(self):
        template = """<!-- comment -->
<div class="container">Content</div>"""
        result = _extract_root_element(template)
        assert result == '<div class="container">'

    def test_extract_with_whitespace(self):
        template = """
  <section class="slide">
    Content
  </section>
"""
        result = _extract_root_element(template)
        assert result == '<section class="slide">'

    def test_no_element_returns_none(self):
        template = "Just text, no HTML"
        result = _extract_root_element(template)
        assert result is None


class TestExtractRootClassAttribute:
    """Tests for _extract_root_class_attribute function."""

    def test_extract_double_quoted_class(self):
        element = '<div class="h-full w-full overflow-hidden">'
        result = _extract_root_class_attribute(element)
        assert result == "h-full w-full overflow-hidden"

    def test_extract_single_quoted_class(self):
        element = "<div class='h-full w-full'>"
        result = _extract_root_class_attribute(element)
        assert result == "h-full w-full"

    def test_no_class_returns_empty(self):
        element = "<div id='root'>"
        result = _extract_root_class_attribute(element)
        assert result == ""


class TestValidateVueComponent:
    """Tests for validate_vue_component function."""

    def test_valid_component_passes(self):
        code = """<template>
  <div class="h-full w-full overflow-hidden flex items-center justify-center">
    <h1>Hello World</h1>
  </div>
</template>"""
        result = validate_vue_component(code)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_missing_height_class_fails(self):
        code = """<template>
  <div class="w-full overflow-hidden flex items-center">
    <h1>Hello World</h1>
  </div>
</template>"""
        result = validate_vue_component(code)
        assert result.is_valid is False
        assert len(result.errors) >= 1
        assert any("高度约束" in e for e in result.errors)

    def test_missing_overflow_class_fails(self):
        code = """<template>
  <div class="h-full w-full flex items-center">
    <h1>Hello World</h1>
  </div>
</template>"""
        result = validate_vue_component(code)
        assert result.is_valid is False
        assert any("overflow" in e for e in result.errors)

    def test_missing_width_class_is_warning(self):
        code = """<template>
  <div class="h-full overflow-hidden flex items-center">
    <h1>Hello World</h1>
  </div>
</template>"""
        result = validate_vue_component(code)
        # Width is a warning, not error, so should still be valid
        assert result.is_valid is True
        assert len(result.warnings) >= 1
        assert any("宽度约束" in w for w in result.warnings)

    def test_h_screen_accepted(self):
        code = """<template>
  <div class="h-screen w-full overflow-hidden">
    <h1>Hello World</h1>
  </div>
</template>"""
        result = validate_vue_component(code)
        assert result.is_valid is True

    def test_min_h_full_accepted(self):
        code = """<template>
  <div class="min-h-full w-full overflow-hidden">
    <h1>Hello World</h1>
  </div>
</template>"""
        result = validate_vue_component(code)
        assert result.is_valid is True

    def test_overflow_auto_accepted(self):
        code = """<template>
  <div class="h-full w-full overflow-auto">
    <h1>Hello World</h1>
  </div>
</template>"""
        result = validate_vue_component(code)
        assert result.is_valid is True

    def test_no_template_fails(self):
        code = """<script setup>
const x = 1
</script>"""
        result = validate_vue_component(code)
        assert result.is_valid is False
        assert any("template" in e.lower() for e in result.errors)

    def test_empty_template_fails(self):
        code = """<template>
</template>"""
        result = validate_vue_component(code)
        assert result.is_valid is False


class TestFormatValidationErrorsForPrompt:
    """Tests for format_validation_errors_for_prompt function."""

    def test_format_errors_and_warnings(self):
        result = ValidationResult(
            is_valid=False,
            issues=[],
            errors=["错误1", "错误2"],
            warnings=["警告1"],
        )
        formatted = format_validation_errors_for_prompt(result)
        assert "校验问题" in formatted
        assert "错误1" in formatted
        assert "错误2" in formatted
        assert "警告1" in formatted

    def test_valid_result_returns_empty(self):
        result = ValidationResult(is_valid=True, issues=[])
        formatted = format_validation_errors_for_prompt(result)
        assert formatted == ""
