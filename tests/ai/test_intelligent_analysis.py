#!/usr/bin/env python3
"""Tests for AST and LLM based code analysis."""

import json
import tempfile
from pathlib import Path

import pytest

from kotlin_mcp_server import KotlinMCPServerV2


@pytest.fixture
def server() -> "KotlinMCPServerV2":
    server = KotlinMCPServerV2("test-server")
    tmp = Path(tempfile.mkdtemp())
    server.set_project_path(str(tmp))
    return server


@pytest.mark.asyncio
async def test_analyze_code_with_ai_detects_eval(server: KotlinMCPServerV2) -> None:
    """Ensure AST analysis surfaces security issues with line numbers."""
    code = "def bad(x):\n    eval(x)\n"
    target = server.project_path / "bad.py"
    target.write_text(code)

    result = await server.handle_call_tool(
        "analyze_code_with_ai",
        {"file_path": str(target), "analysis_type": "security"},
    )

    assert "content" in result
    outer = json.loads(result["content"][0]["text"])
    payload = json.loads(outer["content"][0]["text"])
    issues = payload.get("ast_findings", [])
    assert any(f["issue"] == "use_of_eval" for f in issues)
