"""Text extraction utilities for parsing LLM responses.

This module provides functions for extracting structured content (JSON, code blocks)
from LLM responses that may contain markdown formatting or extra text.
"""

import re


def extract_json(text: str) -> str:
    """Extract JSON from text that may contain markdown code blocks.

    Attempts extraction in the following order:
    1. JSON markdown code block (```json ... ```)
    2. Generic markdown code block (``` ... ```)
    3. Raw JSON object by finding outermost braces

    Args:
        text: Raw text possibly containing JSON.

    Returns:
        Extracted JSON string, or the original text stripped if no JSON found.

    Examples:
        >>> extract_json('```json\\n{"key": "value"}\\n```')
        '{"key": "value"}'
        >>> extract_json('Here is the result: {"a": 1}')
        '{"a": 1}'
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

    return text.strip()


def extract_json_block(text: str) -> str:
    """Extract JSON block using a simpler regex pattern.

    This is a simpler variant that just finds the first JSON object.

    Args:
        text: Text potentially containing a JSON object.

    Returns:
        The JSON object string, or original text if not found.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    return match.group(0) if match else text


def extract_code_block(text: str, language: str = "") -> str:
    """Extract code from markdown code block.

    Args:
        text: Text potentially containing code block.
        language: Expected language marker (tsx, markdown, vue, etc.).
                  If empty, will first try to find any code block.

    Returns:
        Extracted code or original text if no code block found.

    Examples:
        >>> extract_code_block('```vue\\n<template>...</template>\\n```', 'vue')
        '<template>...</template>'
        >>> extract_code_block('```\\nsome code\\n```')
        'some code'
    """
    # Try to extract code block with specific language
    if language:
        pattern = rf"```{language}\s*([\s\S]*?)```"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    # Try generic code block
    match = re.search(r"```\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()

    return text.strip()
