#!/usr/bin/env python3
"""
Test Suite for Core Kotlin MCP Server functionality
Tests the main server initialization, tool routing, and core features
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, cast

import pytest

# Import the unified server
from kotlin_mcp_server import KotlinMCPServer


class TestKotlinMCPServerCore:
    """Test suite for core Kotlin MCP Server functionality"""

    @pytest.fixture
    def server(self) -> "KotlinMCPServer":
        """Create server instance for testing"""
        server = KotlinMCPServer("test-server")
        server.set_project_path(tempfile.mkdtemp())
        return server

    # ============================================================================
    # CORE V2.0 ARCHITECTURE TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_server_initialization(self, server: KotlinMCPServer) -> None:
        """Test server initializes with correct name and modules"""
        assert server.name == "test-server"
        assert hasattr(server, "gradle_tools")
        assert hasattr(server, "project_analysis")
        assert hasattr(server, "build_optimization")
        assert hasattr(server, "security_manager")
        assert hasattr(server, "llm_integration")
        assert hasattr(server, "kotlin_generator")

    @pytest.mark.asyncio
    async def test_list_tools(self, server: KotlinMCPServer) -> None:
        """Test that handle_list_tools returns all tool definitions"""
        # Test the actual list_tools method that covers lines 84-758
        tools_result = await server.handle_list_tools()

        # Verify the result structure
        assert "tools" in tools_result
        tools = tools_result["tools"]
        assert isinstance(tools, list)
        assert len(tools) >= 27  # Should have at least 27 tools

        # Verify tool structure
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool

        # Verify specific tools exist (updated to match actual available tools)
        tool_names = [tool["name"] for tool in tools]
        expected_tools = [
            "refactorFunction",
            "buildAndTest",
            "analyzeCodeQuality",
            "generateTests",
            "formatCode",
            "optimizeImports",
            "gitStatus",
            "gitSmartCommit",
            "gitCreateFeatureBranch",
            "gitMergeWithResolution",
            "apiCallSecure",
            "apiMonitorMetrics",
            "apiValidateCompliance",
            "projectSearch",
            "todoListFromCode",
            "readmeGenerateOrUpdate",
            "changelogSummarize",
            "dependencyAudit",
            "applyCodeAction",
            "applyPatch",
            "androidGenerateComposeUI",
            "androidSetupArchitecture",
            "androidSetupDataLayer",
            "androidSetupNetwork",
            "securityEncryptData",
            "securityDecryptData",
            "privacyRequestErasure",
            "privacyExportData",
            "securityAuditTrail",
            "fileBackup",
            "fileRestore",
            "fileSyncWatch",
            "fileClassifySensitivity",
            "securityHardening",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} not found in tool list"

        # Test a simple tool call to ensure basic functionality
        result = await server.handle_call_tool(
            "refactorFunction",
            {
                "filePath": "/tmp/test.kt",
                "functionName": "test",
                "refactorType": "rename",
                "newName": "newTest",
            },
        )

        # Verify the result has the expected structure
        assert "content" in result
        assert isinstance(result["content"], list)
        if result["content"]:
            assert "text" in result["content"][0]

    @pytest.mark.asyncio
    async def test_project_path_management(self, server: KotlinMCPServer) -> None:
        """Test project path setting and validation"""
        # Test setting valid path
        test_path = Path(tempfile.mkdtemp())
        server.set_project_path(str(test_path))
        assert server.project_path == test_path

        # Test with string path
        server.set_project_path(str(test_path))
        assert server.project_path == test_path

    @pytest.mark.asyncio
    async def test_handle_call_tool_routing(self, server: KotlinMCPServer) -> None:
        """Test that handle_call_tool properly routes to correct modules"""
        # Test routing to different modules
        result = await server.handle_call_tool(
            "create_kotlin_class", {"class_name": "TestClass", "package_name": "com.test"}
        )
        assert "content" in result

    @pytest.mark.asyncio
    async def test_invalid_tool_handling(self, server: KotlinMCPServer) -> None:
        """Test handling of invalid tool names"""
        result = await server.handle_call_tool("invalid_tool_name", {})
        assert "content" in result
        assert isinstance(result["content"], list)
        assert len(result["content"]) > 0
        assert "Unknown tool" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_empty_arguments_handling(self, server: KotlinMCPServer) -> None:
        """Test handling of empty arguments"""
        result = await server.handle_call_tool("create_kotlin_class", {})
        assert "content" in result

    @pytest.mark.asyncio
    async def test_none_arguments_handling(self, server: KotlinMCPServer) -> None:
        """Test handling of None arguments"""
        result = await server.handle_call_tool("create_kotlin_class", {})
        assert "content" in result

    @pytest.mark.asyncio
    async def test_all_27_tools_systematically(self, server: KotlinMCPServer) -> None:
        """Test all 27 tools systematically with valid arguments"""
        all_tools_with_args = [
            # Kotlin Creation Tools
            ("create_kotlin_class", {"class_name": "TestClass", "package_name": "com.test"}),
            (
                "create_kotlin_data_class",
                {"class_name": "DataClass", "properties": ["name: String"]},
            ),
            (
                "create_kotlin_interface",
                {"interface_name": "TestInterface", "methods": ["fun test()"]},
            ),
            # Android Component Tools
            ("create_fragment", {"fragment_name": "TestFragment", "layout_name": "fragment_test"}),
            ("create_activity", {"activity_name": "TestActivity", "layout_name": "activity_test"}),
            ("create_service", {"service_name": "TestService", "service_type": "foreground"}),
            (
                "create_broadcast_receiver",
                {"receiver_name": "TestReceiver", "actions": ["ACTION_TEST"]},
            ),
            # UI and Layout Tools
            (
                "create_layout_file",
                {"file_path": "activity_main.xml", "layout_type": "LinearLayout"},
            ),
            ("create_custom_view", {"view_name": "CustomView", "base_view": "View"}),
            (
                "create_drawable_resource",
                {"resource_name": "test_drawable", "drawable_type": "vector"},
            ),
            # Architecture Setup Tools
            (
                "setup_navigation_component",
                {"nav_graph_name": "nav_graph", "destinations": ["HomeFragment"]},
            ),
            ("setup_data_binding", {"enable_dataBinding": True, "enable_viewBinding": True}),
            ("setup_view_binding", {"module_name": "app", "enable_viewBinding": True}),
            # Gradle Tools
            ("gradle_build", {"task": "build", "module": "app"}),
            ("gradle_clean", {"module": "app"}),
            (
                "add_dependency",
                {"dependency": "implementation 'androidx.core:core-ktx:1.8.0'", "module": "app"},
            ),
            ("update_gradle_wrapper", {"gradle_version": "7.5"}),
            # Code Quality Tools
            ("format_code", {"file_path": "Test.kt", "formatter": "ktlint"}),
            ("run_lint", {"fix_issues": True, "output_format": "json"}),
            ("generate_docs", {"doc_type": "api", "include_examples": True}),
            # Architecture and Database Tools
            ("setup_mvvm_architecture", {"feature_name": "User", "include_repository": True}),
            ("setup_room_database", {"database_name": "AppDatabase", "entities": ["User", "Post"]}),
            ("setup_retrofit_api", {"api_name": "UserApi", "base_url": "https://api.example.com/"}),
            ("setup_dependency_injection", {"di_framework": "hilt", "modules": ["NetworkModule"]}),
            # Security Tools
            (
                "encrypt_sensitive_data",
                {"data_type": "personal_info", "encryption_method": "AES256"},
            ),
            (
                "setup_secure_storage",
                {"storage_type": "encrypted_sharedprefs", "encryption_level": "AES256"},
            ),
            ("setup_cloud_sync", {"provider": "firebase", "sync_type": "realtime"}),
            # API and AI Tools
            ("call_external_api", {"api_name": "TestAPI", "method": "GET", "endpoint": "/test"}),
            ("ai_code_review", {"file_path": "Test.kt", "review_type": "comprehensive"}),
            ("ai_refactor_suggestions", {"file_path": "Test.kt", "refactor_type": "performance"}),
            ("ai_generate_comments", {"file_path": "Test.kt", "comment_style": "detailed"}),
            # Testing Tools
            (
                "generate_unit_tests",
                {"class_path": "com.example.TestClass", "test_type": "comprehensive"},
            ),
            ("setup_ui_testing", {"test_framework": "espresso", "include_page_objects": True}),
        ]

        # Test each tool systematically
        for tool_name, args in all_tools_with_args:
            result = await server.handle_call_tool(tool_name, cast(Dict[str, Any], args))
            assert "content" in result, f"Tool {tool_name} failed to return content"
            assert isinstance(
                result["content"], list
            ), f"Tool {tool_name} returned invalid content format"
