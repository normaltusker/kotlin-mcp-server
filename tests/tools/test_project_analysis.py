#!/usr/bin/env python3
"""
Test Suite for Project Analysis Tools Module
Tests project analysis and build optimization functionality
"""

import tempfile

import pytest

from kotlin_mcp_server import KotlinMCPServer


class TestProjectAnalysisTools:
    """Test suite for project analysis tools functionality"""

    @pytest.fixture
    def server(self) -> "KotlinMCPServer":
        """Create server instance for testing"""
        server = KotlinMCPServer("test-server")
        server.set_project_path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_analyze_project(self, server: KotlinMCPServer) -> None:
        """Test project analysis tool"""
        result = await server.handle_call_tool("analyze_project", {"include_metrics": True})
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_run_tests(self, server: KotlinMCPServer) -> None:
        """Test running tests"""
        result = await server.handle_call_tool("run_tests", {"test_type": "unit"})
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_format_code(self, server: KotlinMCPServer) -> None:
        """Test code formatting"""
        result = await server.handle_call_tool(
            "format_code", {"file_path": "Test.kt", "formatter": "ktlint"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_run_lint(self, server: KotlinMCPServer) -> None:
        """Test linting"""
        result = await server.handle_call_tool(
            "run_lint", {"fix_issues": True, "output_format": "json"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_generate_docs(self, server: KotlinMCPServer) -> None:
        """Test documentation generation"""
        result = await server.handle_call_tool(
            "generate_docs", {"doc_type": "api", "include_examples": True}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_project_analysis_variations(self, server: KotlinMCPServer) -> None:
        """Test project analysis tools with various configurations"""
        test_cases = [
            ("analyze_project", {"include_metrics": False}),
            ("run_tests", {"test_type": "integration"}),
            ("format_code", {"file_path": "MainActivity.kt", "formatter": "detekt"}),
            ("run_lint", {"fix_issues": False, "output_format": "xml"}),
            ("generate_docs", {"doc_type": "user", "include_examples": False}),
        ]

        for tool_name, args in test_cases:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result
            assert isinstance(result["content"], list)
