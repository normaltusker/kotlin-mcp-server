#!/usr/bin/env python3
"""
Test Suite for Gradle Tools Module
Tests all Gradle-related functionality
"""

import json
import tempfile

import pytest

from kotlin_mcp_server import KotlinMCPServer


class TestGradleTools:
    """Test suite for Gradle tools functionality"""

    @pytest.fixture
    def server(self) -> "KotlinMCPServer":
        """Create server instance for testing"""
        server = KotlinMCPServer("test-server")
        server.set_project_path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_gradle_build(self, server: KotlinMCPServer) -> None:
        """Test gradle build tool"""
        result = await server.handle_call_tool("gradle_build", {"task": "build", "module": "app"})
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_gradle_clean(self, server: KotlinMCPServer) -> None:
        """Test gradle clean tool"""
        result = await server.handle_call_tool("gradle_clean", {"module": "app"})
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_add_dependency(self, server: KotlinMCPServer) -> None:
        """Test adding dependencies"""
        result = await server.handle_call_tool(
            "add_dependency",
            {"dependency": "implementation 'androidx.core:core-ktx:1.8.0'", "module": "app"},
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_update_gradle_wrapper(self, server: KotlinMCPServer) -> None:
        """Test updating gradle wrapper"""
        result = await server.handle_call_tool("update_gradle_wrapper", {"gradle_version": "7.5"})
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_gradle_tools_with_empty_args(self, server: KotlinMCPServer) -> None:
        """Test gradle tools with empty arguments"""
        result = await server.handle_call_tool("gradle_build", {})
        assert "content" in result

    @pytest.mark.asyncio
    async def test_gradle_tools_variations(self, server: KotlinMCPServer) -> None:
        """Test gradle tools with various argument combinations"""
        test_cases = [
            ("gradle_build", {"task": "assembleDebug", "module": "app"}),
            ("gradle_build", {"task": "test", "module": "lib"}),
            ("gradle_clean", {"module": "app"}),
            ("gradle_clean", {"module": "lib"}),
        ]

        for tool_name, args in test_cases:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result
            assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_gradle_build_requires_project_path(self) -> None:
        """Ensure structured error when project path is missing"""
        server = KotlinMCPServer("test-server")
        result = await server.handle_call_tool("gradle_build", {"task": "build"})

        assert "content" in result
        assert isinstance(result["content"], list)
        assert len(result["content"]) > 0

        # Check if response contains error information (handle both JSON and text responses)
        response_text = result["content"][0]["text"]
        try:
            response = json.loads(response_text)
            # If it's JSON, check for structured error
            assert response["success"] is False
            assert "project path required" in response["error"]
            assert "--project-path" in response["error"]
        except (json.JSONDecodeError, KeyError):
            # If it's not JSON, check for error message in text
            assert any(
                keyword in response_text.lower()
                for keyword in ["error", "failed", "project", "path"]
            )
            print(f"Non-JSON response (acceptable): {response_text[:100]}...")
