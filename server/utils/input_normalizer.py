"""
Input normalization utilities for handling camelCase/snake_case synonyms.
"""

from typing import Any


def norm(d: dict, *names: str, default: Any = None, required: bool = False) -> Any:
    """
    Normalize input by checking multiple name variants.

    Args:
        d: Input dictionary
        *names: Names to check in order
        default: Default value if none found
        required: Whether this field is required

    Returns:
        Value from first matching key, default if none found

    Raises:
        ValueError: If required=True and no value found
    """
    for n in names:
        if n in d and d[n] not in (None, "", [], {}):
            return d[n]
    if required:
        raise ValueError(f"{'/'.join(names)} is required")
    return default
