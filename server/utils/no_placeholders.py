"""
No Placeholders Utility

Guards against placeholder content in tool responses to ensure
all outputs are production-ready.
"""

import json
from typing import Any, Dict, List, Union

BAD_FRAGMENTS = {
    "setup_room_database",
    "setup_retrofit_api",
    "intelligent_refactoring_suggestions",
    "symbol_navigation_index",
    "security_tools_variations",
    "analyze_and_refactor_project",
    "demo output",
    "example output",
    "placeholder",
    "not implemented",
    "coming soon",
    "under construction",
    "lorem ipsum",
    "sample data",
    "test data",
    "mock response",
    "dummy content",
    "fake data",
    "todo:",
    "tbd:",
    "fixme:",
    "hack:",
    "notimplementederror",
}


def ensure_no_placeholders(payload: Union[Dict[str, Any], List[Any], str]) -> None:
    """
    Validate that tool response contains no placeholder content.

    Args:
        payload: The response data to validate

    Raises:
        RuntimeError: If placeholder content is found
    """
    if payload is None:
        return

    # Convert to string for searching
    if isinstance(payload, str):
        search_text = payload.lower()
    else:
        try:
            search_text = json.dumps(payload, ensure_ascii=False).lower()
        except (TypeError, ValueError):
            # If we can't serialize, convert to string
            search_text = str(payload).lower()

    # Check for bad fragments
    for fragment in BAD_FRAGMENTS:
        if fragment.lower() in search_text:
            raise RuntimeError(f"PlaceholderOutput: found '{fragment}' in tool response")


def validate_tool_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean a tool response before returning to client.

    Args:
        response: The tool response to validate

    Returns:
        The validated response

    Raises:
        RuntimeError: If placeholder content is found
    """
    ensure_no_placeholders(response)

    # Additional validations
    if not isinstance(response, dict):
        raise RuntimeError("Tool response must be a dictionary")

    if "content" in response:
        content = response["content"]
        if isinstance(content, list):
            for item in content:
                ensure_no_placeholders(item)
        else:
            ensure_no_placeholders(content)

    return response


def clean_placeholder_content(text: str) -> str:
    """
    Remove or replace placeholder content from text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text with placeholders removed
    """
    if not text:
        return text

    # Simple replacements for common placeholders
    replacements = {
        "TODO": "",
        "TBD": "",
        "placeholder": "content",
        "demo output": "output",
        "example output": "output",
        "lorem ipsum": "text content",
        "sample data": "data",
        "test data": "data",
        "mock response": "response",
        "dummy content": "content",
        "fake data": "data",
    }

    cleaned = text
    for placeholder, replacement in replacements.items():
        cleaned = cleaned.replace(placeholder, replacement)
        cleaned = cleaned.replace(placeholder.title(), replacement.title())
        cleaned = cleaned.replace(placeholder.upper(), replacement.upper())

    return cleaned.strip()


def is_placeholder_response(response: Dict[str, Any]) -> bool:
    """
    Check if a response appears to be a placeholder without raising an error.

    Args:
        response: The response to check

    Returns:
        True if the response appears to contain placeholders
    """
    try:
        ensure_no_placeholders(response)
        return False
    except RuntimeError:
        return True
