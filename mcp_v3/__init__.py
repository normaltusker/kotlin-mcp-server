"""
MCP v3 - Official MCP SDK Implementation

This module contains the new MCP 2025-06-18 compliant implementation
using the official MCP Python SDK.
"""

from .server.mcp_server import KotlinMCPServerV3

__version__ = "3.0.0"
__all__ = ["KotlinMCPServerV3"]
