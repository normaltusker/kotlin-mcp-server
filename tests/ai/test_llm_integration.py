#!/usr/bin/env python3
"""
Test Suite for AI / LLM Integration Module
Tests AI - powered code generation and analysis tools
"""

import tempfile
from pathlib import Path

import pytest

from kotlin_mcp_server import KotlinMCPServerV2


class TestLLMIntegration:
    """Test suite for AI / LLM integration functionality"""

    @pytest.fixture
    def server(self) -> "KotlinMCPServerV2":
        """Create server instance for testing"""
        server = KotlinMCPServerV2("test-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_generate_code_with_ai(self, server: KotlinMCPServerV2) -> None:
        """Test AI code generation"""
        result = await server.handle_call_tool(
            "generate_code_with_ai",
            {"prompt": "Create a user login function", "code_type": "function"},
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_ai_code_review(self, server: KotlinMCPServerV2) -> None:
        """Test AI code review"""
        result = await server.handle_call_tool(
            "ai_code_review", {"file_path": "Test.kt", "review_type": "comprehensive"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_ai_refactor_suggestions(self, server: KotlinMCPServerV2) -> None:
        """Test AI refactoring suggestions"""
        result = await server.handle_call_tool(
            "ai_refactor_suggestions", {"file_path": "Test.kt", "refactor_type": "performance"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_ai_generate_comments(self, server: KotlinMCPServerV2) -> None:
        """Test AI comment generation"""
        result = await server.handle_call_tool(
            "ai_generate_comments", {"file_path": "Test.kt", "comment_style": "detailed"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_generate_unit_tests(self, server: KotlinMCPServerV2) -> None:
        """Test AI unit test generation"""
        result = await server.handle_call_tool(
            "generate_unit_tests",
            {"class_path": "com.example.TestClass", "test_type": "comprehensive"},
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_ai_tools_variations(self, server: KotlinMCPServerV2) -> None:
        """Test AI tools with various configurations"""
        test_cases = [
            (
                "generate_code_with_ai",
                {"prompt": "Create a data validation function", "code_type": "class"},
            ),
            ("ai_code_review", {"file_path": "MainActivity.kt", "review_type": "security"}),
            (
                "ai_refactor_suggestions",
                {"file_path": "UserRepository.kt", "refactor_type": "readability"},
            ),
            ("ai_generate_comments", {"file_path": "ApiService.kt", "comment_style": "concise"}),
            (
                "generate_unit_tests",
                {"class_path": "com.example.UserService", "test_type": "basic"},
            ),
        ]

        for tool_name, args in test_cases:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result
            assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_ai_code_generation_edge_cases(self, server: KotlinMCPServerV2) -> None:
        """Test AI code generation with edge cases"""
        # Test with empty prompt
        result = await server.handle_call_tool(
            "generate_code_with_ai", {"prompt": "", "code_type": "function"}
        )
        assert "content" in result

        # Test with very long prompt
        long_prompt = "Create a function that " + "handles complex business logic " * 50
        result = await server.handle_call_tool(
            "generate_code_with_ai", {"prompt": long_prompt, "code_type": "function"}
        )
        assert "content" in result

    @pytest.mark.asyncio
    async def test_ai_file_analysis_edge_cases(self, server: KotlinMCPServerV2) -> None:
        """Test AI file analysis with edge cases"""
        # Test with non - existent file
        result = await server.handle_call_tool(
            "ai_code_review", {"file_path": "NonExistent.kt", "review_type": "comprehensive"}
        )
        assert "content" in result

        # Test with empty file path
        result = await server.handle_call_tool(
            "ai_refactor_suggestions", {"file_path": "", "refactor_type": "performance"}
        )
        assert "content" in result
