"""
IDE context adapter for extracting workspace and active file information.
"""

from typing import Optional


def pull_ide_context(headers: Optional[dict] = None, extra: Optional[dict] = None) -> dict:
    """
    Extract IDE context from MCP client headers and metadata.

    Args:
        headers: HTTP-style headers from MCP client
        extra: Additional metadata from MCP client

    Returns:
        Dictionary with IDE context information
    """
    # MCP clients often pass metadata; stub for now (Copilot: wire where available)
    return {
        "workspaceRoot": (extra or {}).get("workspaceRoot")
        or (headers or {}).get("x-workspace-root"),
        "activeFile": (extra or {}).get("activeFile") or (headers or {}).get("x-active-file"),
        "selection": (extra or {}).get("selection") or None,
    }
