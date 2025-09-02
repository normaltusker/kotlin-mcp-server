#!/usr/bin/env python3
"""
Placeholder Output Guard

Prevents tools from returning placeholder/stub content by detecting common
placeholder patterns and raising errors when found.

Author: MCP Development Team
Version: 1.0.0
License: MIT
"""

import json
from typing import Any, Dict, List, Optional


def reject_placeholders(output: Dict[str, Any]) -> None:
    """
    Guard against placeholder outputs by scanning for common placeholder patterns.

    Args:
        output: Tool output dictionary to validate

    Raises:
        RuntimeError: When placeholder content is detected
    """
    serialized = json.dumps(output, ensure_ascii=False)

    # Known placeholder patterns that should never appear in production outputs
    bad_fragments = [
        "setup_room_database",
        "setup_retrofit_api",
        "intelligent_refactoring_suggestions",
        "symbol_navigation_index",
        "security_tools_variations",
        "analyze_and_refactor_project",
        "analyze_code",  # as a bare list entry
        "TODO",
        "TBD",
        "placeholder",
        "stub",
        "demo output",
        "sample output",
        "example output",
        "NotImplemented",
        "✓",  # Check mark emoji
        "❌",  # Cross mark emoji
        "⚠",  # Warning emoji
        "\u2705",  # Unicode check mark
        "\u274c",  # Unicode cross mark
        "\u26a0",  # Unicode warning sign
    ]

    # Check for any bad fragments in the serialized output
    found_fragments = [fragment for fragment in bad_fragments if fragment in serialized]

    if found_fragments:
        raise RuntimeError(
            f"PlaceholderOutput: tool returned placeholder content containing: {', '.join(found_fragments)}. "
            "Tools must return structured findings from real analyzers, not placeholder content."
        )


def validate_structured_output(
    output: Dict[str, Any], required_fields: Optional[List[str]] = None
) -> None:
    """
    Validate that output has proper structured format.

    Args:
        output: Tool output dictionary
        required_fields: List of fields that must be present

    Raises:
        RuntimeError: When output is not properly structured
    """
    if not isinstance(output, dict):
        raise RuntimeError("Tool output must be a dictionary")

    # Check for required structure fields
    if required_fields:
        missing_fields = [field for field in required_fields if field not in output]
        if missing_fields:
            raise RuntimeError(f"Tool output missing required fields: {', '.join(missing_fields)}")

    # Ensure no placeholder patterns
    reject_placeholders(output)


def ensure_typed_findings(output: Dict[str, Any]) -> None:
    """
    Ensure analysis tools return typed findings, not prose or emoji strings.

    Args:
        output: Tool output dictionary

    Raises:
        RuntimeError: When findings are not properly typed
    """
    # Check for emoji-based "reports" that should be structured
    serialized = json.dumps(output, ensure_ascii=False)

    emoji_patterns = ["✓", "❌", "🟢", "🔴", "⚠️"]
    found_emojis = [emoji for emoji in emoji_patterns if emoji in serialized]

    if found_emojis and "findings" not in output and "reports" not in output:
        raise RuntimeError(
            f"Tool output contains emoji patterns ({', '.join(found_emojis)}) "
            "but lacks structured 'findings' or 'reports' fields. "
            "Analysis tools must return typed JSON objects, not formatted strings."
        )

    # Check for "No_Gradle" type fake status strings
    if "No_Gradle" in serialized:
        raise RuntimeError(
            "Tool output contains 'No_Gradle' placeholder. "
            "Use proper Gradle detection and return typed error objects."
        )


def validate_compliance_output(output: Dict[str, Any]) -> None:
    """
    Validate compliance tool outputs have required structure.

    Args:
        output: Compliance tool output

    Raises:
        RuntimeError: When compliance output is invalid
    """
    validate_structured_output(output, ["ok"])

    if output.get("ok"):
        # Successful compliance check should have violations array and remediations
        if "violations" not in output:
            raise RuntimeError("Compliance output missing 'violations' field")
        if "suggestedRemediations" not in output:
            raise RuntimeError("Compliance output missing 'suggestedRemediations' field")
    else:
        # Failed compliance check should have error object
        if "error" not in output:
            raise RuntimeError("Failed compliance output missing 'error' field")


def validate_analysis_output(output: Dict[str, Any]) -> None:
    """
    Validate code analysis outputs have required structure.

    Args:
        output: Analysis tool output

    Raises:
        RuntimeError: When analysis output is invalid
    """
    validate_structured_output(output, ["ok"])

    if output.get("ok"):
        # Successful analysis should have findings and counts
        if "findings" not in output:
            raise RuntimeError("Analysis output missing 'findings' field")
        if "counts" not in output:
            raise RuntimeError("Analysis output missing 'counts' field")

        # Ensure findings are structured objects, not strings
        findings = output.get("findings", [])
        if findings and isinstance(findings[0], str):
            raise RuntimeError(
                "Analysis findings must be objects with id/severity/file/line/message, not strings"
            )


def validate_quality_output(output: Dict[str, Any]) -> None:
    """
    Validate code quality outputs have required structure.

    Args:
        output: Quality tool output

    Raises:
        RuntimeError: When quality output is invalid
    """
    validate_structured_output(output, ["ok"])

    if output.get("ok"):
        # Successful quality check should have reports object
        if "reports" not in output:
            raise RuntimeError("Quality output missing 'reports' field")
        if "project" not in output:
            raise RuntimeError("Quality output missing 'project' field")
    else:
        # Failed quality check should have error with code
        if "error" not in output or "code" not in output.get("error", {}):
            raise RuntimeError("Failed quality output missing structured 'error' with 'code' field")
