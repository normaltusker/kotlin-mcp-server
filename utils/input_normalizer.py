#!/usr/bin/env python3
"""
Input Normalizer Utility

Provides robust input field normalization supporting multiple naming conventions
(snake_case, camelCase) with clear error messages for missing required fields.

Author: MCP Development Team
Version: 1.0.0
License: MIT
"""

from typing import Any, Dict, List


def norm(d: Dict[str, Any], *names: str, default: Any = None, required: bool = False) -> Any:
    """
    Normalize input field access supporting multiple field name conventions.

    Args:
        d: Input dictionary
        *names: Field name variants to check (snake_case, camelCase, etc.)
        default: Default value if no field found
        required: If True, raises ValueError when no field found

    Returns:
        Field value or default

    Raises:
        ValueError: When required=True and no valid field found
    """
    for name in names:
        if name in d and d[name] not in (None, "", [], {}):
            return d[name]

    if required:
        field_options = "/".join(names)
        raise ValueError(f"{field_options} is required")

    return default


def normalize_api_input(inp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize API validation inputs to handle various field name conventions.

    Args:
        inp: Raw input dictionary

    Returns:
        Normalized input dictionary with standardized field names

    Raises:
        ValueError: When required fields are missing
    """
    normalized = {}

    # Required fields
    normalized["endpoint"] = norm(inp, "endpoint", "path", required=True)

    # Optional fields with defaults
    normalized["api_name"] = norm(inp, "api_name", "apiName", default="unknown")
    normalized["method"] = norm(inp, "method", default="GET")

    # Handle policies/compliance type
    policies = norm(inp, "policies", "policy", "complianceType", default=["gdpr"])
    if isinstance(policies, str):
        policies = [policies]
    normalized["policies"] = policies

    # Handle payload references
    normalized["payload_ref"] = norm(inp, "payloadRef", "payload", default=None)
    normalized["openapi_ref"] = norm(inp, "openapiRef", "openapi", default=None)

    return normalized


def normalize_project_input(inp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize project analysis inputs.

    Args:
        inp: Raw input dictionary

    Returns:
        Normalized input dictionary
    """
    normalized = {}

    # Project root handling
    normalized["project_root"] = norm(inp, "project_root", "projectRoot", default=None)
    normalized["file_path"] = norm(inp, "file_path", "filePath", default=None)

    # Analysis parameters
    normalized["analysis_type"] = norm(inp, "analysis_type", "analysisType", default="all")
    normalized["max_findings"] = norm(inp, "max_findings", "maxFindings", default=100)

    # Scope and ruleset
    normalized["scope"] = norm(inp, "scope", default="project")
    normalized["ruleset"] = norm(inp, "ruleset", "ruleSet", default="all")

    return normalized


class ValidationError(Exception):
    """Raised when input validation fails with clear error message."""


def validate_required_fields(normalized: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that all required fields are present and valid.

    Args:
        normalized: Normalized input dictionary
        required_fields: List of required field names

    Raises:
        ValidationError: When required fields are missing or invalid
    """
    missing_fields = []

    for field in required_fields:
        if field not in normalized or normalized[field] in (None, "", [], {}):
            missing_fields.append(field)

    if missing_fields:
        if len(missing_fields) == 1:
            raise ValidationError(f"Required field missing: {missing_fields[0]}")
        else:
            raise ValidationError(f"Required fields missing: {', '.join(missing_fields)}")
