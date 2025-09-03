#!/usr/bin/env python3
"""
Integration tests for the enhanced Kotlin MCP Server v2.

Tests the modernized server implementation with 2025-06-18 specification compliance,
including schema validation, progress tracking, resource management, and error handling.
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kotlin_mcp_server import (
    CreateKotlinFileRequest,
    GradleBuildRequest,
    KotlinMCPServerV2,
    ProjectAnalysisRequest,
)


class TestKotlinMCPServerV2(unittest.TestCase):
    """Test cases for the enhanced MCP server."""

    def setUp(self):
        """Set up test environment."""
        self.server = KotlinMCPServerV2()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.server.set_project_path(str(self.temp_dir))

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_server_initialization(self):
        """Test server initialization with proper capabilities."""
        params = {}
        result = await self.server.handle_initialize(params)

        self.assertEqual(result["protocolVersion"], "2025-06-18")
        self.assertIn("capabilities", result)
        self.assertIn("tools", result["capabilities"])
        self.assertIn("resources", result["capabilities"])
        self.assertIn("prompts", result["capabilities"])
        self.assertIn("logging", result["capabilities"])
        self.assertIn("roots", result["capabilities"])
        self.assertEqual(result["serverInfo"]["name"], "kotlin-mcp-server")
        self.assertEqual(result["serverInfo"]["version"], "2.0.0")

    async def test_tools_list(self):
        """Test tools listing with schema-driven definitions."""
        result = await self.server.handle_list_tools()

        self.assertIn("tools", result)
        tools = result["tools"]
        self.assertGreater(len(tools), 0)

        # Check for key tools
        tool_names = [tool["name"] for tool in tools]
        self.assertIn("create_kotlin_file", tool_names)
        self.assertIn("gradle_build", tool_names)
        self.assertIn("analyze_project", tool_names)

        # Verify schema structure
        for tool in tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)
            self.assertIn("type", tool["inputSchema"])
            self.assertEqual(tool["inputSchema"]["type"], "object")

    async def test_pydantic_validation(self):
        """Test Pydantic schema validation for tool arguments."""
        # Valid request
        valid_args = {
            "file_path": "src/main/java/com/example/MainActivity.kt",
            "package_name": "com.example",
            "class_name": "MainActivity",
            "class_type": "activity",
        }
        request = CreateKotlinFileRequest(**valid_args)
        self.assertEqual(request.file_path, valid_args["file_path"])
        self.assertEqual(request.class_type, "activity")

        # Invalid class_type should raise validation error
        invalid_args = valid_args.copy()
        invalid_args["class_type"] = "invalid_type"

        with self.assertRaises(Exception):  # Pydantic validation error
            CreateKotlinFileRequest(**invalid_args)

    async def test_resource_management(self):
        """Test resource listing and reading capabilities."""
        # Create test files
        test_file = self.temp_dir / "build.gradle"
        test_content = "apply plugin: 'com.android.application'"
        test_file.write_text(test_content)

        # Test resource listing
        result = await self.server.handle_list_resources()
        self.assertIn("resources", result)

        # Test resource reading
        uri = f"file://{test_file}"
        result = await self.server.handle_read_resource(uri)
        self.assertIn("contents", result)
        self.assertEqual(result["contents"][0]["text"], test_content)

    async def test_security_validation(self):
        """Test security path validation."""
        # Valid path within project
        valid_path = self.temp_dir / "src" / "main" / "Test.kt"
        self.assertTrue(self.server.is_path_allowed(valid_path))

        # Invalid path outside project
        invalid_path = Path("/etc/passwd")
        self.assertFalse(self.server.is_path_allowed(invalid_path))

    async def test_prompt_templates(self):
        """Test prompt template system."""
        result = await self.server.handle_list_prompts()
        self.assertIn("prompts", result)

        prompts = result["prompts"]
        prompt_names = [p["name"] for p in prompts]
        self.assertIn("generate_mvvm_viewmodel", prompt_names)
        self.assertIn("create_compose_screen", prompt_names)
        self.assertIn("setup_room_database", prompt_names)

        # Test getting specific prompt
        prompt_result = await self.server.handle_get_prompt(
            "generate_mvvm_viewmodel", {"feature_name": "UserProfile", "data_source": "network"}
        )
        self.assertIn("description", prompt_result)
        self.assertIn("messages", prompt_result)
        self.assertIn("UserProfile", prompt_result["messages"][0]["content"]["text"])

    async def test_error_handling(self):
        """Test enhanced error handling."""
        # Test invalid method
        request_data = {"jsonrpc": "2.0", "id": 1, "method": "invalid_method", "params": {}}
        response = await self.server.handle_request(request_data)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)

        # Test missing parameters
        request_data = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {},  # Missing name
        }
        response = await self.server.handle_request(request_data)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32602)

    async def test_analyze_project_with_automatic_initialization(self) -> None:
        """call_analyze_project should work correctly with automatic initialization."""
        server = KotlinMCPServerV2()  # Should auto-initialize with current directory
        args = ProjectAnalysisRequest(analysis_type="structure")
        result = await server.call_analyze_project(args, "op-test")
        # Should succeed since tools are always initialized now
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis_type"], "structure")

    async def test_progress_tracking(self):
        """Test progress tracking functionality."""
        # Mock the progress sending
        progress_messages = []

        async def mock_send_progress(operation_id, progress, message):
            progress_messages.append((operation_id, progress, message))

        self.server.send_progress = mock_send_progress

        # Call a tool that should track progress
        args = CreateKotlinFileRequest(
            file_path="Test.kt", package_name="com.test", class_name="Test", class_type="class"
        )

        with patch.object(self.server, "kotlin_generator") as mock_generator:
            mock_generator.generate_complete_class.return_value = "class Test {}"
            await self.server.call_create_kotlin_file(args, "test-op-1")

        # Verify progress was tracked
        self.assertGreater(len(progress_messages), 0)
        progress_values = [msg[1] for msg in progress_messages]
        self.assertIn(0, progress_values)  # Should start at 0

    async def test_create_kotlin_file_with_automatic_initialization(self) -> None:
        """Test that create_kotlin_file works correctly with automatic initialization."""

        args = CreateKotlinFileRequest(
            file_path="TestFile.kt",
            package_name="com.test",
            class_name="TestFile",
            class_type="class",
        )

        result = await self.server.call_create_kotlin_file(args, "op-test")

        # Should succeed since kotlin_generator is always initialized now
        self.assertTrue(result["success"])
        self.assertEqual(result["class_name"], "TestFile")
        self.assertIn("package com.test", result["content"])

    async def test_mcp_request_response_cycle(self):
        """Test complete MCP request/response cycle."""
        # Test initialize
        init_request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        response = await self.server.handle_request(init_request)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 1)
        self.assertIn("result", response)

        # Test tools list
        tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        response = await self.server.handle_request(tools_request)
        self.assertEqual(response["id"], 2)
        self.assertIn("result", response)
        self.assertIn("tools", response["result"])


class TestSchemaGeneration(unittest.TestCase):
    """Test Pydantic schema generation for tools."""

    def test_create_kotlin_file_schema(self):
        """Test CreateKotlinFileRequest schema generation."""
        schema = CreateKotlinFileRequest.model_json_schema()

        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertIn("file_path", schema["properties"])
        self.assertIn("package_name", schema["properties"])
        self.assertIn("class_name", schema["properties"])
        self.assertIn("class_type", schema["properties"])

        # Test enum validation for class_type
        class_type_property = schema["properties"]["class_type"]
        self.assertIn("pattern", class_type_property)

    def test_gradle_build_schema(self):
        """Test GradleBuildRequest schema generation."""
        schema = GradleBuildRequest.model_json_schema()

        self.assertEqual(schema["type"], "object")
        self.assertIn("task", schema["properties"])
        self.assertIn("clean", schema["properties"])
        self.assertEqual(schema["properties"]["clean"]["type"], "boolean")


async def run_async_tests():
    """Run all async tests."""
    suite = unittest.TestSuite()

    # Add test cases
    test_cases = [
        TestKotlinMCPServerV2("test_server_initialization"),
        TestKotlinMCPServerV2("test_tools_list"),
        TestKotlinMCPServerV2("test_pydantic_validation"),
        TestKotlinMCPServerV2("test_resource_management"),
        TestKotlinMCPServerV2("test_security_validation"),
        TestKotlinMCPServerV2("test_prompt_templates"),
        TestKotlinMCPServerV2("test_error_handling"),
        TestKotlinMCPServerV2("test_progress_tracking"),
        TestKotlinMCPServerV2("test_mcp_request_response_cycle"),
    ]

    for test_case in test_cases:
        try:
            test_case.setUp()
            await getattr(test_case, test_case._testMethodName)()
            test_case.tearDown()
            print(f"✓ {test_case._testMethodName}")
        except Exception as e:
            print(f"✗ {test_case._testMethodName}: {e}")
            test_case.tearDown()


def main():
    """Main test runner."""
    print("Running Kotlin MCP Server v2 Enhanced Tests")
    print("=" * 50)

    # Run sync tests
    print("\nRunning schema tests...")
    unittest.main(
        module="__main__", argv=[""], testRunner=unittest.TextTestRunner(verbosity=0), exit=False
    )

    # Run async tests
    print("\nRunning async integration tests...")
    asyncio.run(run_async_tests())

    print("\nTest suite completed!")


if __name__ == "__main__":
    main()
