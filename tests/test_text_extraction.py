"""Tests for text extraction utilities."""

import pytest

from html2ppt.utils.text_extraction import (
    extract_code_block,
    extract_json,
    extract_json_block,
)


class TestExtractJson:
    """Tests for extract_json function."""

    def test_extract_from_json_code_block(self):
        """Extract JSON from ```json code block."""
        text = '```json\n{"key": "value"}\n```'
        result = extract_json(text)
        assert result == '{"key": "value"}'

    def test_extract_from_generic_code_block(self):
        """Extract JSON from generic ``` code block."""
        text = '```\n{"key": "value"}\n```'
        result = extract_json(text)
        assert result == '{"key": "value"}'

    def test_extract_raw_json_object(self):
        """Extract JSON from raw text containing braces."""
        text = 'Here is the result: {"a": 1, "b": 2}'
        result = extract_json(text)
        assert result == '{"a": 1, "b": 2}'

    def test_extract_nested_json(self):
        """Extract nested JSON object."""
        text = 'Result: {"outer": {"inner": "value"}}'
        result = extract_json(text)
        assert result == '{"outer": {"inner": "value"}}'

    def test_extract_with_extra_text(self):
        """Extract JSON when there's text before and after."""
        text = 'The answer is: {"answer": 42}. That was the result.'
        result = extract_json(text)
        assert result == '{"answer": 42}'

    def test_returns_stripped_text_when_no_json(self):
        """Return stripped text when no JSON found."""
        text = "  plain text without json  "
        result = extract_json(text)
        assert result == "plain text without json"

    def test_json_code_block_with_whitespace(self):
        """Handle whitespace in code block."""
        text = '```json\n  {\n    "formatted": true\n  }\n  ```'
        result = extract_json(text)
        assert '"formatted": true' in result

    def test_prefers_json_block_over_raw(self):
        """Prefer ```json block over raw JSON."""
        text = '```json\n{"from": "block"}\n``` followed by {"from": "raw"}'
        result = extract_json(text)
        assert result == '{"from": "block"}'


class TestExtractJsonBlock:
    """Tests for extract_json_block function."""

    def test_extract_simple_json_object(self):
        """Extract simple JSON object."""
        text = 'Result: {"key": "value"}'
        result = extract_json_block(text)
        assert result == '{"key": "value"}'

    def test_extract_multiline_json(self):
        """Extract multiline JSON object."""
        text = '''Result:
{
    "key": "value",
    "nested": {}
}
Done'''
        result = extract_json_block(text)
        assert '{"key": "value"' in result

    def test_returns_original_when_no_json(self):
        """Return original text when no JSON found."""
        text = "no braces here"
        result = extract_json_block(text)
        assert result == text


class TestExtractCodeBlock:
    """Tests for extract_code_block function."""

    def test_extract_vue_code_block(self):
        """Extract Vue code from ```vue block."""
        text = '```vue\n<template><div>Hello</div></template>\n```'
        result = extract_code_block(text, "vue")
        assert result == "<template><div>Hello</div></template>"

    def test_extract_tsx_code_block(self):
        """Extract TSX code from ```tsx block."""
        text = '```tsx\nconst App = () => <div>Hello</div>;\n```'
        result = extract_code_block(text, "tsx")
        assert result == "const App = () => <div>Hello</div>;"

    def test_extract_markdown_code_block(self):
        """Extract markdown from ```markdown block."""
        text = '```markdown\n# Title\n\nParagraph\n```'
        result = extract_code_block(text, "markdown")
        assert result == "# Title\n\nParagraph"

    def test_extract_generic_code_block_when_language_not_found(self):
        """Fall back to generic block when language not found."""
        text = '```\nsome code\n```'
        result = extract_code_block(text, "python")
        assert result == "some code"

    def test_extract_without_language_specified(self):
        """Extract from any code block when no language specified."""
        text = '```python\ndef hello(): pass\n```'
        result = extract_code_block(text)
        assert result == "python\ndef hello(): pass"

    def test_returns_stripped_text_when_no_code_block(self):
        """Return stripped text when no code block found."""
        text = "  plain text  "
        result = extract_code_block(text)
        assert result == "plain text"

    def test_handles_code_block_with_whitespace(self):
        """Handle whitespace in code block correctly."""
        text = '```vue\n  <template>\n    <div>Indented</div>\n  </template>\n```'
        result = extract_code_block(text, "vue")
        assert "<template>" in result
        assert "Indented" in result

    def test_empty_code_block(self):
        """Handle empty code block."""
        text = "```vue\n```"
        result = extract_code_block(text, "vue")
        assert result == ""
