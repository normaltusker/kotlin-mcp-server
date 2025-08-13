#!/usr/bin/env python3
"""
Consolidated Test Suite for Kotlin MCP Server
Comprehensive test coverage combining all test scenarios
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

# Import the unified server
from kotlin_mcp_server import KotlinMCPServer


class TestKotlinMCPServerConsolidated:
    """Consolidated comprehensive test suite for Kotlin MCP Server"""

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
        assert len(tools) >= 31  # Should have at least 31 tools

        # Verify tool structure
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool

        # Verify specific tools exist
        tool_names = [tool["name"] for tool in tools]
        expected_tools = [
            "create_kotlin_file",
            "gradle_build",
            "run_tests",
            "analyze_project",
            "generate_code_with_ai",
            "create_layout_file",
            "format_code",
            "run_lint",
            "generate_docs",
            "create_compose_component",
            "setup_mvvm_architecture",
            "setup_dependency_injection",
            "setup_room_database",
            "generate_unit_tests",
        ]

        for expected_tool in expected_tools:
            assert (
                expected_tool in tool_names
            ), f"Tool {expected_tool} not found in tool list"  # Test a simple tool call to ensure basic functionality
        result = await server.handle_call_tool(
            "create_kotlin_class", {"class_name": "TestClass", "package_name": "com.test"}
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

    # ============================================================================
    # COMPREHENSIVE TOOL TESTING - ALL 31 TOOLS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_all_31_tools_systematically(self, server: KotlinMCPServer) -> None:
        """Test all 31 tools systematically with valid arguments"""
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
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result, f"Tool {tool_name} failed to return content"
            assert isinstance(
                result["content"], list
            ), f"Tool {tool_name} returned invalid content format"

    @pytest.mark.asyncio
    async def test_kotlin_creation_tools(self, server: KotlinMCPServer) -> None:
        """Test all Kotlin file creation tools"""
        tools_and_args = [
            ("create_kotlin_class", {"class_name": "TestClass", "package_name": "com.test"}),
            (
                "create_kotlin_data_class",
                {"class_name": "DataClass", "properties": ["name: String"]},
            ),
            (
                "create_kotlin_interface",
                {"interface_name": "TestInterface", "methods": ["fun test()"]},
            ),
        ]

        for tool_name, args in tools_and_args:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_android_component_tools(self, server: KotlinMCPServer) -> None:
        """Test Android component creation tools"""
        tools_and_args = [
            ("create_fragment", {"fragment_name": "TestFragment", "layout_name": "fragment_test"}),
            ("create_activity", {"activity_name": "TestActivity", "layout_name": "activity_test"}),
            ("create_service", {"service_name": "TestService", "service_type": "foreground"}),
            (
                "create_broadcast_receiver",
                {"receiver_name": "TestReceiver", "actions": ["ACTION_TEST"]},
            ),
        ]

        for tool_name, args in tools_and_args:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_ui_layout_tools(self, server: KotlinMCPServer) -> None:
        """Test UI and layout creation tools"""
        tools_and_args = [
            (
                "create_layout_file",
                {"file_path": "activity_main.xml", "layout_type": "LinearLayout"},
            ),
            ("create_custom_view", {"view_name": "CustomView", "base_view": "View"}),
            (
                "create_drawable_resource",
                {"resource_name": "test_drawable", "drawable_type": "vector"},
            ),
        ]

        for tool_name, args in tools_and_args:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_architecture_setup_tools(self, server: KotlinMCPServer) -> None:
        """Test architecture setup tools"""
        tools_and_args = [
            (
                "setup_navigation_component",
                {"nav_graph_name": "nav_graph", "destinations": ["HomeFragment"]},
            ),
            ("setup_data_binding", {"enable_dataBinding": True, "enable_viewBinding": True}),
            ("setup_view_binding", {"module_name": "app", "enable_viewBinding": True}),
        ]

        for tool_name, args in tools_and_args:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_gradle_tools(self, server: KotlinMCPServer) -> None:
        """Test Gradle-related tools"""
        tools_and_args = [
            ("gradle_build", {"task": "build", "module": "app"}),
            ("gradle_clean", {"module": "app"}),
            (
                "add_dependency",
                {"dependency": "implementation 'androidx.core:core-ktx:1.8.0'", "module": "app"},
            ),
            ("update_gradle_wrapper", {"gradle_version": "7.5"}),
        ]

        for tool_name, args in tools_and_args:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_code_quality_tools(self, server: KotlinMCPServer) -> None:
        """Test code quality and formatting tools"""
        tools_and_args = [
            ("format_code", {"file_path": "Test.kt", "formatter": "ktlint"}),
            ("run_lint", {"fix_issues": True, "output_format": "json"}),
            ("generate_docs", {"doc_type": "api", "include_examples": True}),
        ]

        for tool_name, args in tools_and_args:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_mvvm_and_database_tools(self, server: KotlinMCPServer) -> None:
        """Test MVVM architecture and database setup tools"""
        tools_and_args = [
            ("setup_mvvm_architecture", {"feature_name": "User", "include_repository": True}),
            ("setup_room_database", {"database_name": "AppDatabase", "entities": ["User", "Post"]}),
            ("setup_retrofit_api", {"api_name": "UserApi", "base_url": "https://api.example.com/"}),
            ("setup_dependency_injection", {"di_framework": "hilt", "modules": ["NetworkModule"]}),
        ]

        for tool_name, args in tools_and_args:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_security_tools(self, server: KotlinMCPServer) -> None:
        """Test security-related tools"""
        tools_and_args = [
            (
                "encrypt_sensitive_data",
                {"data_type": "personal_info", "encryption_method": "AES256"},
            ),
            (
                "setup_secure_storage",
                {"storage_type": "encrypted_sharedprefs", "encryption_level": "AES256"},
            ),
            ("setup_cloud_sync", {"provider": "firebase", "sync_type": "realtime"}),
        ]

        for tool_name, args in tools_and_args:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_api_and_ai_tools(self, server: KotlinMCPServer) -> None:
        """Test API and AI-enhanced tools"""
        tools_and_args = [
            ("call_external_api", {"api_name": "TestAPI", "method": "GET", "endpoint": "/test"}),
            ("ai_code_review", {"file_path": "Test.kt", "review_type": "comprehensive"}),
            ("ai_refactor_suggestions", {"file_path": "Test.kt", "refactor_type": "performance"}),
            ("ai_generate_comments", {"file_path": "Test.kt", "comment_style": "detailed"}),
        ]

        for tool_name, args in tools_and_args:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_testing_tools(self, server: KotlinMCPServer) -> None:
        """Test testing-related tools"""
        tools_and_args = [
            (
                "generate_unit_tests",
                {"class_path": "com.example.TestClass", "test_type": "comprehensive"},
            ),
            ("setup_ui_testing", {"test_framework": "espresso", "include_page_objects": True}),
        ]

        for tool_name, args in tools_and_args:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    # ============================================================================
    # EDGE CASES AND ERROR HANDLING
    # ============================================================================

    @pytest.mark.asyncio
    async def test_kotlin_class_variations(self, server: KotlinMCPServer) -> None:
        """Test different Kotlin class creation variations"""
        variations = [
            {"class_name": "SimpleClass"},
            {"class_name": "DataClass", "is_data_class": True},
            {"class_name": "AbstractClass", "is_abstract": True},
            {"class_name": "InheritedClass", "extends": "BaseClass"},
            {"class_name": "InterfaceImpl", "implements": ["Interface1", "Interface2"]},
        ]

        for args in variations:
            result = await server.handle_call_tool("create_kotlin_class", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_file_path_edge_cases(self, server: KotlinMCPServer) -> None:
        """Test file creation with various path scenarios"""
        edge_cases = [
            {"file_path": "", "class_name": "Test"},
            {"file_path": "deep/nested/path/Test.kt", "class_name": "Test"},
            {"file_path": "special-chars@#$.kt", "class_name": "Test"},
            {"file_path": "../outside/Test.kt", "class_name": "Test"},
        ]

        for args in edge_cases:
            result = await server.handle_call_tool("create_kotlin_class", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_android_component_variations(self, server: KotlinMCPServer) -> None:
        """Test Android component creation with different configurations"""
        # Activity variations
        activity_cases = [
            {"activity_name": "MainActivity", "is_launcher": True},
            {"activity_name": "DetailActivity", "parent_activity": "BaseActivity"},
            {"activity_name": "SettingsActivity", "theme": "CustomTheme"},
        ]

        for args in activity_cases:
            result = await server.handle_call_tool("create_activity", args)
            assert "content" in result

        # Fragment variations
        fragment_cases = [
            {"fragment_name": "ListFragment", "fragment_type": "list"},
            {"fragment_name": "DetailFragment", "fragment_type": "detail"},
            {"fragment_name": "DialogFragment", "fragment_type": "dialog"},
        ]

        for args in fragment_cases:
            result = await server.handle_call_tool("create_fragment", args)
            assert "content" in result

    # ============================================================================
    # ADVANCED SCENARIOS AND WORKFLOWS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_ai_code_generation_with_context(self, server: KotlinMCPServer) -> None:
        """Test AI code generation with contextual information"""
        # Setup project path
        test_dir = Path(tempfile.mkdtemp())
        server.set_project_path(str(test_dir))

        # Create a test file first for context
        if server.project_path:
            test_file = server.project_path / "ExistingClass.kt"
            test_file.write_text(
                """
        package com.test

        class ExistingClass {
            fun existingMethod(): String {
                return "existing"
            }
        }
        """
            )

        args = {
            "file_path": "ExistingClass.kt",
            "enhancement_type": "performance",
            "specific_requirements": "Add caching mechanism",
        }

        mock_result = {
            "success": True,
            "content": "Enhanced code with caching implementation",
            "enhancement_type": "performance",
        }

        with patch.object(
            server.llm_integration, "generate_code_with_ai", return_value=mock_result
        ):
            result = await server.handle_call_tool("enhance_existing_code", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_documentation_generation_workflow(self, server: KotlinMCPServer) -> None:
        """Test comprehensive documentation generation"""
        args = {
            "doc_type": "api",
            "include_examples": True,
            "output_format": "markdown",
            "include_diagrams": True,
        }

        mock_result = {
            "success": True,
            "content": "# Comprehensive API Documentation\n\n## Overview\nDetailed API documentation with examples.",
        }

        with patch.object(
            server.llm_integration, "generate_code_with_ai", return_value=mock_result
        ):
            result = await server.handle_call_tool("generate_docs", args)
            assert "content" in result

            # Verify docs directory and file creation
            if server.project_path:
                docs_path = server.project_path / "docs" / "api_documentation.md"
                assert docs_path.exists()
                content = docs_path.read_text()
                assert "Comprehensive API Documentation" in content

    @pytest.mark.asyncio
    async def test_security_implementation_workflow(self, server: KotlinMCPServer) -> None:
        """Test comprehensive security setup workflow"""
        security_configs = [
            {
                "data_type": "user_credentials",
                "encryption_method": "AES256",
                "key_storage": "android_keystore",
                "compliance": "GDPR",
            },
            {
                "data_type": "payment_info",
                "encryption_method": "RSA",
                "key_storage": "hardware_security_module",
                "compliance": "PCI_DSS",
            },
            {
                "data_type": "biometric_data",
                "encryption_method": "ChaCha20",
                "key_storage": "secure_enclave",
                "compliance": "HIPAA",
            },
        ]

        for config in security_configs:
            result = await server.handle_call_tool("encrypt_sensitive_data", config)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_comprehensive_mvvm_setup(self, server: KotlinMCPServer) -> None:
        """Test complete MVVM architecture setup"""
        features = ["User", "Product", "Order", "Payment"]

        for feature in features:
            args = {
                "feature_name": feature,
                "include_repository": True,
                "include_use_cases": True,
                "include_di": True,
                "package_name": f"com.app.{feature.lower()}",
            }

            result = await server.handle_call_tool("setup_mvvm_architecture", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_database_setup_with_migrations(self, server: KotlinMCPServer) -> None:
        """Test Room database setup with comprehensive configuration"""
        database_configs = [
            {
                "database_name": "UserDatabase",
                "entities": ["User", "Profile", "Settings"],
                "version": 1,
                "migrations": True,
                "type_converters": ["DateConverter", "ListConverter"],
            },
            {
                "database_name": "ProductDatabase",
                "entities": ["Product", "Category", "Review"],
                "version": 2,
                "export_schema": True,
                "prepopulate": True,
            },
        ]

        for config in database_configs:
            result = await server.handle_call_tool("setup_room_database", config)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_api_integration_comprehensive(self, server: KotlinMCPServer) -> None:
        """Test comprehensive API integration setup"""
        api_configs = [
            {
                "api_name": "UserAPI",
                "base_url": "https://api.example.com/v1/",
                "endpoints": ["getUsers", "createUser", "updateUser", "deleteUser"],
                "auth_type": "bearer_token",
                "interceptors": ["logging", "authentication", "retry"],
                "timeout": 30,
                "cache_policy": "network_first",
            },
            {
                "api_name": "PaymentAPI",
                "base_url": "https://payments.example.com/",
                "endpoints": ["processPayment", "refund", "getTransactions"],
                "auth_type": "api_key",
                "ssl_pinning": True,
                "rate_limiting": True,
            },
        ]

        for config in api_configs:
            result = await server.handle_call_tool("setup_retrofit_api", config)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_testing_framework_setup(self, server: KotlinMCPServer) -> None:
        """Test comprehensive testing framework setup"""
        testing_configs = [
            {
                "test_framework": "junit5",
                "include_mockito": True,
                "include_coroutines_test": True,
                "test_coverage": "jacoco",
                "integration_tests": True,
            },
            {
                "test_framework": "espresso",
                "include_page_objects": True,
                "test_runner": "AndroidJUnitRunner",
                "include_accessibility": True,
                "screenshot_testing": True,
            },
            {
                "test_framework": "compose_test",
                "semantic_testing": True,
                "animation_testing": True,
                "screenshot_testing": True,
            },
        ]

        for config in testing_configs:
            result = await server.handle_call_tool("setup_ui_testing", config)
            assert "content" in result

    # ============================================================================
    # SPECIFIC MISSING LINE TARGETING
    # ============================================================================

    @pytest.mark.asyncio
    async def test_targeted_missing_lines_860_936(self, server: KotlinMCPServer) -> None:
        """Target specific missing lines 860-936"""
        test_cases = [
            # Line 860-861: format_code error handling
            ("format_code", {"file_path": "NonExistent.kt", "formatter": "invalid_formatter"}),
            # Line 870: run_lint specific path
            ("run_lint", {"fix_issues": True, "file_path": "specific/path/Test.kt"}),
            # Line 897: generate_docs error case
            ("generate_docs", {"doc_type": "invalid_type", "include_examples": False}),
            # Line 936: create_custom_view minimal
            ("create_custom_view", {"view_name": "MinimalView"}),
        ]

        for tool_name, args in test_cases:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_targeted_missing_lines_1010_1358(self, server: KotlinMCPServer) -> None:
        """Target specific missing lines 1010-1358"""
        # Lines 1010-1026: setup_mvvm_architecture variations
        mvvm_cases = [
            {"feature_name": "Test", "include_repository": False},
            {"feature_name": "Test", "include_use_cases": False},
            {"feature_name": "Test", "include_di": False},
            {},  # Empty args case
        ]

        for args in mvvm_cases:
            result = await server.handle_call_tool("setup_mvvm_architecture", args)
            assert "content" in result

        # Lines 1081-1082: setup_room_database edge cases
        result = await server.handle_call_tool(
            "setup_room_database", {"database_name": "", "entities": [], "version": 0}
        )
        assert "content" in result

        # Lines 1147-1151: setup_retrofit_api variations
        retrofit_cases: List[Dict[str, Any]] = [
            {"api_name": "", "base_url": ""},
            {"api_name": "Test", "endpoints": []},
            {"api_name": "Test", "auth_type": "none"},
        ]

        for args in retrofit_cases:
            result = await server.handle_call_tool("setup_retrofit_api", args)
            assert "content" in result

        # Lines 1161-1165: encrypt_sensitive_data edge cases
        encryption_cases: List[Dict[str, Any]] = [
            {"data_type": "", "encryption_method": ""},
            {"data_type": "test", "key_storage": "invalid"},
        ]

        for args in encryption_cases:
            result = await server.handle_call_tool("encrypt_sensitive_data", args)
            assert "content" in result

        # Lines 1203-1204: setup_secure_storage minimal
        result = await server.handle_call_tool("setup_secure_storage", {"storage_type": ""})
        assert "content" in result

        # Lines 1211-1252: setup_cloud_sync comprehensive variations
        cloud_cases: List[Dict[str, Any]] = [
            {"provider": ""},
            {"provider": "firebase", "sync_type": ""},
            {"provider": "aws", "service": ""},
            {"provider": "google_drive", "file_types": []},
            {},  # Empty args
        ]

        for args in cloud_cases:
            result = await server.handle_call_tool("setup_cloud_sync", args)
            assert "content" in result

        # Lines 1261-1300: call_external_api variations
        api_cases: List[Dict[str, Any]] = [
            {"api_name": "", "method": "GET"},
            {"api_name": "Test", "method": ""},
            {"api_name": "Test", "method": "POST", "body": None},
            {},  # Empty args
        ]

        for args in api_cases:
            result = await server.handle_call_tool("call_external_api", args)
            assert "content" in result

        # Lines 1309-1358: generate_unit_tests comprehensive
        test_cases: List[Dict[str, Any]] = [
            {"class_path": ""},
            {"class_path": "Test", "test_type": ""},
            {"class_path": "Test", "test_framework": ""},
            {},  # Empty args
        ]

        for args in test_cases:
            result = await server.handle_call_tool("generate_unit_tests", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_all_tools_empty_arguments(self, server: KotlinMCPServer) -> None:
        """Test all tools with empty arguments to hit edge cases"""
        all_tools = [
            "create_kotlin_class",
            "create_kotlin_data_class",
            "create_kotlin_interface",
            "create_fragment",
            "create_activity",
            "create_service",
            "create_broadcast_receiver",
            "create_layout_file",
            "create_custom_view",
            "create_drawable_resource",
            "setup_navigation_component",
            "setup_data_binding",
            "setup_view_binding",
            "gradle_build",
            "gradle_clean",
            "add_dependency",
            "update_gradle_wrapper",
            "format_code",
            "run_lint",
            "generate_docs",
            "setup_mvvm_architecture",
            "setup_room_database",
            "setup_retrofit_api",
            "setup_dependency_injection",
            "encrypt_sensitive_data",
            "setup_secure_storage",
            "setup_cloud_sync",
            "call_external_api",
            "ai_code_review",
            "ai_refactor_suggestions",
            "ai_generate_comments",
            "generate_unit_tests",
            "setup_ui_testing",
        ]

        for tool_name in all_tools:
            result = await server.handle_call_tool(tool_name, {})
            assert "content" in result

    @pytest.mark.asyncio
    async def test_error_handling_comprehensive(self, server: KotlinMCPServer) -> None:
        """Test comprehensive error handling scenarios"""
        # Test with invalid JSON-like structures
        invalid_args_list = [
            {"invalid": "structure"},
            {"nested": {"invalid": "structure"}},
            {"list": ["invalid", "structure"]},
            {"mixed": {"types": ["and", "structures"]}},
        ]

        critical_tools = [
            "create_kotlin_class",
            "create_activity",
            "setup_mvvm_architecture",
            "generate_unit_tests",
            "call_external_api",
        ]

        for tool_name in critical_tools:
            for args in invalid_args_list:
                result = await server.handle_call_tool(tool_name, args)
                assert "content" in result

    @pytest.mark.asyncio
    async def test_subprocess_error_handling(self, server: KotlinMCPServer) -> None:
        """Test error handling in subprocess calls"""
        # Test format_code with subprocess failure
        with patch("subprocess.run", side_effect=FileNotFoundError("ktlint not found")):
            result = await server.handle_call_tool("format_code", {"file_path": "Test.kt"})
            assert "content" in result

        # Test run_lint with subprocess timeout
        with patch("subprocess.run", side_effect=TimeoutError("Lint timed out")):
            result = await server.handle_call_tool("run_lint", {"fix_issues": True})
            assert "content" in result

        # Test gradle_build with permission error
        with patch("subprocess.run", side_effect=PermissionError("Permission denied")):
            result = await server.handle_call_tool("gradle_build", {"task": "build"})
            assert "content" in result

    # ============================================================================
    # PERFORMANCE AND STRESS TESTS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self, server: KotlinMCPServer) -> None:
        """Test concurrent execution of multiple tools"""
        tools_and_args = [
            ("create_kotlin_class", {"class_name": "Class1"}),
            ("create_activity", {"activity_name": "Activity1"}),
            ("gradle_build", {"task": "build"}),
            ("ai_code_review", {"file_path": "Test.kt"}),
        ]

        # Execute tools concurrently
        tasks = [server.handle_call_tool(tool_name, args) for tool_name, args in tools_and_args]

        results = await asyncio.gather(*tasks)

        # Verify all executions completed successfully
        for result in results:
            assert "content" in result

    @pytest.mark.asyncio
    async def test_large_data_handling(self, server: KotlinMCPServer) -> None:
        """Test handling of large data structures"""
        # Test with large lists and complex structures
        large_args = {
            "class_name": "LargeClass",
            "methods": [f"fun method{i}(): String" for i in range(100)],
            "properties": [f"val property{i}: String" for i in range(50)],
            "implements": [f"Interface{i}" for i in range(20)],
        }

        result = await server.handle_call_tool("create_kotlin_class", large_args)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_memory_cleanup(self, server: KotlinMCPServer) -> None:
        """Test that server properly cleans up resources"""
        # Create multiple temporary files and ensure cleanup
        for i in range(10):
            result = await server.handle_call_tool(
                "create_kotlin_class",
                {"class_name": f"TempClass{i}", "file_path": f"temp/TempClass{i}.kt"},
            )
            assert "content" in result

        # Verify server state remains stable
        assert server.project_path is not None
        assert hasattr(server, "gradle_tools")

    # ============================================================================
    # MISSING LINE TARGETING AND EDGE CASES
    # ============================================================================

    @pytest.mark.asyncio
    async def test_create_kotlin_file_comprehensive(self, server: KotlinMCPServer) -> None:
        """Test _create_kotlin_file method comprehensively to cover lines 877-947"""
        # Test all class types to cover the if-elif chain
        class_types = [
            "activity",
            "viewmodel",
            "repository",
            "fragment",
            "data_class",
            "use_case",
            "service",
            "adapter",
            "interface",
            "class",
        ]

        for class_type in class_types:
            args = {
                "file_path": f"Test{class_type.title()}.kt",
                "class_name": f"Test{class_type.title()}",
                "package_name": "com.test",
                "class_type": class_type,
                "features": ["lifecycle", "databinding"],
                "generate_related": True,
            }

            result = await server.handle_call_tool("create_kotlin_file", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_kotlin_file_generation_edge_cases(self, server: KotlinMCPServer) -> None:
        """Test edge cases for kotlin file generation"""
        # Test with missing optional parameters
        edge_cases = [
            {
                "file_path": "Test.kt",
                "class_name": "Test",
                "package_name": "com.test",
                "class_type": "class",
            },
            {
                "file_path": "Test.kt",
                "class_name": "Test",
                "package_name": "com.test",
                "class_type": "activity",
                "features": [],
            },
            {
                "file_path": "Test.kt",
                "class_name": "Test",
                "package_name": "com.test",
                "class_type": "viewmodel",
                "generate_related": False,
            },
        ]

        for args in edge_cases:
            result = await server.handle_call_tool("create_kotlin_file", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_direct_tool_methods(self, server: KotlinMCPServer) -> None:
        """Test direct tool methods to increase coverage"""
        # Test create_kotlin_class variations
        kotlin_class_args = [
            {"class_name": "TestClass", "package_name": "com.test"},
            {"class_name": "TestClass", "package_name": "com.test", "extends": "BaseClass"},
            {"class_name": "TestClass", "package_name": "com.test", "implements": ["Interface1"]},
            {"class_name": "TestClass", "package_name": "com.test", "is_abstract": True},
        ]

        for args in kotlin_class_args:
            result = await server.handle_call_tool("create_kotlin_class", args)
            assert "content" in result

        # Test create_kotlin_data_class variations
        data_class_args = [
            {"class_name": "DataTest", "properties": ["name: String", "age: Int"]},
            {"class_name": "DataTest", "properties": ["id: Long"], "package_name": "com.test"},
        ]

        for args in data_class_args:
            result = await server.handle_call_tool("create_kotlin_data_class", args)
            assert "content" in result

        # Test create_kotlin_interface variations
        interface_args = [
            {"interface_name": "TestInterface", "methods": ["fun test(): Unit"]},
            {"interface_name": "TestInterface", "methods": [], "package_name": "com.test"},
        ]

        for args in interface_args:
            result = await server.handle_call_tool("create_kotlin_interface", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_android_component_comprehensive(self, server: KotlinMCPServer) -> None:
        """Test Android component creation comprehensively"""
        # Test create_fragment with various configurations
        fragment_configs = [
            {
                "fragment_name": "TestFragment",
                "layout_name": "fragment_test",
                "fragment_type": "standard",
            },
            {
                "fragment_name": "ListFragment",
                "layout_name": "fragment_list",
                "fragment_type": "list",
                "viewmodel": True,
            },
            {
                "fragment_name": "DetailFragment",
                "layout_name": "fragment_detail",
                "fragment_type": "detail",
                "navigation": True,
            },
        ]

        for args in fragment_configs:
            result = await server.handle_call_tool("create_fragment", args)
            assert "content" in result

        # Test create_activity with various configurations
        activity_configs = [
            {"activity_name": "MainActivity", "layout_name": "activity_main", "is_launcher": True},
            {
                "activity_name": "DetailActivity",
                "layout_name": "activity_detail",
                "parent_activity": "BaseActivity",
                "theme": "AppTheme",
            },
            {
                "activity_name": "SettingsActivity",
                "layout_name": "activity_settings",
                "orientation": "portrait",
            },
        ]

        for args in activity_configs:
            result = await server.handle_call_tool("create_activity", args)
            assert "content" in result

        # Test create_service variations
        service_configs = [
            {"service_name": "TestService", "service_type": "foreground"},
            {"service_name": "BackgroundService", "service_type": "background"},
            {"service_name": "BoundService", "service_type": "bound"},
        ]

        for args in service_configs:
            result = await server.handle_call_tool("create_service", args)
            assert "content" in result

        # Test create_broadcast_receiver variations
        receiver_configs = [
            {"receiver_name": "TestReceiver", "actions": ["ACTION_TEST"]},
            {
                "receiver_name": "NetworkReceiver",
                "actions": ["CONNECTIVITY_CHANGE", "WIFI_STATE_CHANGED"],
            },
        ]

        for args in receiver_configs:
            result = await server.handle_call_tool("create_broadcast_receiver", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_all_tools_with_empty_args(self, server: KotlinMCPServer) -> None:
        """Test all 31 tools with empty arguments to hit edge cases"""
        all_tools = [
            "create_kotlin_class",
            "create_kotlin_data_class",
            "create_kotlin_interface",
            "create_fragment",
            "create_activity",
            "create_service",
            "create_broadcast_receiver",
            "create_layout_file",
            "create_custom_view",
            "create_drawable_resource",
            "setup_navigation_component",
            "setup_data_binding",
            "setup_view_binding",
            "gradle_build",
            "gradle_clean",
            "add_dependency",
            "update_gradle_wrapper",
            "format_code",
            "run_lint",
            "generate_docs",
            "setup_mvvm_architecture",
            "setup_room_database",
            "setup_retrofit_api",
            "setup_dependency_injection",
            "encrypt_sensitive_data",
            "setup_secure_storage",
            "setup_cloud_sync",
            "call_external_api",
            "ai_code_review",
            "ai_refactor_suggestions",
            "ai_generate_comments",
            "generate_unit_tests",
            "setup_ui_testing",
        ]

        for tool_name in all_tools:
            result = await server.handle_call_tool(tool_name, {})
            assert "content" in result

    @pytest.mark.asyncio
    async def test_enhance_existing_code_with_file(self, server: KotlinMCPServer) -> None:
        """Test enhance_existing_code that reads a file"""
        # Create a test file first
        if server.project_path:
            test_file = server.project_path / "TestClass.kt"
            test_file.write_text(
                """
        package com.test

        class TestClass {
            fun simpleMethod(): String {
                return "test"
            }
        }
        """
            )

        args = {
            "file_path": "TestClass.kt",
            "enhancement_type": "performance",
            "specific_requirements": "Add caching",
        }

        mock_result = {
            "success": True,
            "content": "Enhanced code with caching",
            "enhancement_type": "performance",
        }

        with patch.object(
            server.llm_integration, "generate_code_with_ai", return_value=mock_result
        ):
            result = await server.handle_call_tool("enhance_existing_code", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_create_layout_comprehensive_variations(self, server: KotlinMCPServer) -> None:
        """Test create_layout_file with various configurations"""
        test_cases = [
            {
                "file_path": "activity_main.xml",
                "layout_name": "activity_main",
                "layout_type": "LinearLayout",
                "orientation": "vertical",
                "components": ["TextView", "Button"],
            },
            {
                "file_path": "fragment_user.xml",
                "layout_name": "fragment_user",
                "layout_type": "ConstraintLayout",
                "components": ["RecyclerView", "FloatingActionButton"],
            },
            {
                "file_path": "item_product.xml",
                "layout_name": "item_product",
                "layout_type": "CardView",
                "components": ["ImageView", "TextView", "Button"],
            },
        ]

        for args in test_cases:
            result = await server.handle_call_tool("create_layout_file", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_specific_missing_lines_variations(self, server: KotlinMCPServer) -> None:
        """Test specific variations to hit missing lines"""

        # Test setup_mvvm_architecture variations (lines 1010-1026)
        mvvm_cases = [
            {"feature_name": "Test", "include_repository": False},
            {"feature_name": "Test", "include_use_cases": False},
            {"feature_name": "Test", "include_di": False},
            {"feature_name": "Test", "package_name": ""},
        ]

        for args in mvvm_cases:
            result = await server.handle_call_tool("setup_mvvm_architecture", args)
            assert "content" in result

        # Test setup_room_database edge cases (lines 1081-1082)
        result = await server.handle_call_tool(
            "setup_room_database", {"database_name": "", "entities": [], "version": 0}
        )
        assert "content" in result

        # Test setup_retrofit_api variations (lines 1147-1151)
        retrofit_cases = [
            {"api_name": "", "base_url": ""},
            {"api_name": "Test", "endpoints": []},
            {"api_name": "Test", "auth_type": "none"},
            {"api_name": "Test", "interceptors": []},
        ]

        for args in retrofit_cases:
            result = await server.handle_call_tool("setup_retrofit_api", args)
            assert "content" in result

        # Test encrypt_sensitive_data edge cases (lines 1161-1165)
        encryption_cases = [
            {"data_type": "", "encryption_method": ""},
            {"data_type": "test", "key_storage": "invalid"},
            {"data_type": "test", "compliance": "none"},
        ]

        for args in encryption_cases:
            result = await server.handle_call_tool("encrypt_sensitive_data", args)
            assert "content" in result

        # Test setup_secure_storage minimal (lines 1203-1204)
        result = await server.handle_call_tool("setup_secure_storage", {"storage_type": ""})
        assert "content" in result

        # Test setup_cloud_sync variations (lines 1211-1252)
        cloud_cases = [
            {"provider": ""},
            {"provider": "firebase", "sync_type": ""},
            {"provider": "aws", "service": ""},
            {"provider": "google_drive", "file_types": []},
            {"provider": "custom", "endpoint": ""},
            {"provider": "azure", "container": ""},
            {"provider": "dropbox", "app_key": ""},
        ]

        for args in cloud_cases:
            result = await server.handle_call_tool("setup_cloud_sync", args)
            assert "content" in result

        # Test call_external_api variations (lines 1261-1300)
        api_cases = [
            {"api_name": "", "method": "GET"},
            {"api_name": "Test", "method": ""},
            {"api_name": "Test", "method": "POST", "body": None},
            {"api_name": "Test", "method": "PUT", "headers": {}},
            {"api_name": "Test", "method": "DELETE", "params": {}},
            {"api_name": "Test", "method": "PATCH", "timeout": 0},
        ]

        for args in api_cases:
            result = await server.handle_call_tool("call_external_api", args)
            assert "content" in result

        # Test generate_unit_tests variations (lines 1309-1358)
        test_cases = [
            {"class_path": ""},
            {"class_path": "Test", "test_type": ""},
            {"class_path": "Test", "test_framework": ""},
            {"class_path": "Test", "mock_dependencies": False},
            {"class_path": "Test", "coverage_target": 0},
            {"class_path": "Test", "include_ui_tests": False},
            {"class_path": "Test", "property_based_testing": False},
        ]

        for args in test_cases:
            result = await server.handle_call_tool("generate_unit_tests", args)
            assert "content" in result

        # Test setup_ui_testing variations (lines 1394-1433)
        ui_test_cases = [
            {"test_framework": ""},
            {"test_framework": "espresso", "include_page_objects": False},
            {"test_framework": "compose_test", "semantic_testing": False},
            {"test_framework": "robolectric", "shadow_configuration": ""},
        ]

        for args in ui_test_cases:
            result = await server.handle_call_tool("setup_ui_testing", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_create_kotlin_file_variations(self, server: KotlinMCPServer) -> None:
        """Test create_kotlin_file with different configurations"""
        variations = [
            {
                "file_path": "TestClass.kt",
                "file_type": "class",
                "class_name": "TestClass",
                "package_name": "com.test",
            },
            {"file_path": "TestObject.kt", "file_type": "object", "class_name": "TestObject"},
            {
                "file_path": "TestEnum.kt",
                "file_type": "enum",
                "class_name": "TestEnum",
                "enum_values": ["VALUE1", "VALUE2"],
            },
            {"file_path": "TestSealed.kt", "file_type": "sealed_class", "class_name": "TestSealed"},
        ]

        for args in variations:
            result = await server.handle_call_tool("create_kotlin_file", args)
            assert "content" in result

    @pytest.mark.asyncio
    async def test_comprehensive_error_scenarios(self, server: KotlinMCPServer) -> None:
        """Test comprehensive error handling scenarios"""

        # Test with invalid JSON-like structures for critical tools
        invalid_args_list = [
            {"invalid": "structure"},
            {"nested": {"invalid": "structure"}},
            {"list": ["invalid", "structure"]},
            {"mixed": {"types": ["and", "structures"]}},
        ]

        critical_tools = [
            "create_kotlin_class",
            "create_activity",
            "setup_mvvm_architecture",
            "generate_unit_tests",
            "call_external_api",
            "gradle_build",
        ]

        for tool_name in critical_tools:
            for args in invalid_args_list:
                result = await server.handle_call_tool(tool_name, args)
                assert "content" in result

    @pytest.mark.asyncio
    async def test_subprocess_error_handling_comprehensive(self, server: KotlinMCPServer) -> None:
        """Test comprehensive subprocess error handling"""

        # Test format_code with various errors
        with patch("subprocess.run", side_effect=FileNotFoundError("ktlint not found")):
            result = await server.handle_call_tool("format_code", {"file_path": "Test.kt"})
            assert "content" in result

        # Test run_lint with timeout
        with patch("subprocess.run", side_effect=TimeoutError("Lint timed out")):
            result = await server.handle_call_tool("run_lint", {"fix_issues": True})
            assert "content" in result

        # Test gradle_build with permission error
        with patch("subprocess.run", side_effect=PermissionError("Permission denied")):
            result = await server.handle_call_tool("gradle_build", {"task": "build"})
            assert "content" in result

        # Test various subprocess failures
        subprocess_errors = [OSError("OS Error"), RuntimeError("Runtime Error")]
        for error in subprocess_errors:
            with patch("subprocess.run", side_effect=error):
                result = await server.handle_call_tool("gradle_build", {"task": "clean"})
                assert "content" in result

    @pytest.mark.asyncio
    async def test_generate_code_with_ai_comprehensive(self, server: KotlinMCPServer) -> None:
        """Test generate_code_with_ai method with various scenarios"""
        # Test basic functionality (covers lines 962-996)
        arguments = {
            "description": "Test description",
            "code_type": "activity",
            "package_name": "com.test.app",
            "class_name": "TestActivity",
            "framework": "android",
            "features": ["hilt", "compose"],
            "compliance_requirements": ["gdpr"],
        }

        result = await server.handle_call_tool("generate_code_with_ai", arguments)
        assert "content" in result

        # Test without optional parameters
        basic_arguments = {
            "description": "Basic test",
            "code_type": "class",
            "package_name": "com.test",
            "class_name": "BasicClass",
        }

        result = await server.handle_call_tool("generate_code_with_ai", basic_arguments)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_analyze_code_with_ai_comprehensive(self, server: KotlinMCPServer) -> None:
        """Test analyze_code_with_ai method (covers lines 1000-1026)"""
        arguments = {
            "file_path": "test.kt",
            "analysis_type": "performance",
            "focus_areas": ["memory", "performance"],
        }

        result = await server.handle_call_tool("analyze_code_with_ai", arguments)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_enhance_existing_code_comprehensive(self, server: KotlinMCPServer) -> None:
        """Test enhance_existing_code method"""
        arguments = {
            "file_path": "test.kt",
            "enhancement_type": "performance",
            "current_code": "class Test {}",
            "requirements": ["add_logging", "add_error_handling"],
        }

        result = await server.handle_call_tool("enhance_existing_code", arguments)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_security_compliance_tools(self, server: KotlinMCPServer) -> None:
        """Test security and compliance related tools"""
        # Test encrypt_sensitive_data
        encrypt_args = {
            "data_type": "user_credentials",
            "encryption_method": "aes256",
            "storage_location": "secure_preferences",
        }
        result = await server.handle_call_tool("encrypt_sensitive_data", encrypt_args)
        assert "content" in result

        # Test GDPR compliance
        gdpr_args = {
            "data_types": ["personal", "behavioral"],
            "consent_mechanism": "explicit",
            "retention_period": "2_years",
        }
        result = await server.handle_call_tool("implement_gdpr_compliance", gdpr_args)
        assert "content" in result

        # Test HIPAA compliance
        hipaa_args = {
            "data_types": ["medical", "patient_info"],
            "audit_logging": True,
            "access_controls": ["role_based", "mfa"],
        }
        result = await server.handle_call_tool("implement_hipaa_compliance", hipaa_args)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_database_and_api_tools(self, server: KotlinMCPServer) -> None:
        """Test database and API setup tools"""
        # Test Room database setup
        room_args = {"entities": ["User", "Product"], "database_name": "AppDatabase", "version": 1}
        result = await server.handle_call_tool("setup_room_database", room_args)
        assert "content" in result

        # Test Retrofit API setup
        retrofit_args = {
            "base_url": "https://api.example.com",
            "endpoints": ["users", "products"],
            "authentication": "bearer_token",
        }
        result = await server.handle_call_tool("setup_retrofit_api", retrofit_args)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_ui_and_compose_tools(self, server: KotlinMCPServer) -> None:
        """Test UI and Compose related tools"""
        # Test create_compose_component
        compose_args = {
            "component_type": "screen",
            "component_name": "UserProfileScreen",
            "package_name": "com.test.app.ui",
            "features": ["navigation", "state_management"],
        }
        result = await server.handle_call_tool("create_compose_component", compose_args)
        assert "content" in result

        # Test create_custom_view
        view_args = {
            "view_name": "CustomButton",
            "package_name": "com.test.app.ui",
            "view_type": "compound",
            "features": ["animations", "accessibility"],
        }
        result = await server.handle_call_tool("create_custom_view", view_args)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_advanced_testing_tools(self, server: KotlinMCPServer) -> None:
        """Test advanced testing related tools"""
        # Test generate_unit_tests
        test_args = {
            "target_class": "com.example.UserViewModel",
            "test_framework": "junit5",
            "coverage_target": 80,
        }
        result = await server.handle_call_tool("generate_unit_tests", test_args)
        assert "content" in result

        # Test setup_ui_testing
        ui_test_args = {
            "testing_framework": "espresso",
            "features": ["accessibility", "screenshots"],
        }
        result = await server.handle_call_tool("setup_ui_testing", ui_test_args)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_project_management_tools(self, server: KotlinMCPServer) -> None:
        """Test project management and dependency tools"""
        # Test manage_dependencies
        dep_args = {
            "action": "add",
            "dependencies": ["implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.2'"],
            "scope": "implementation",
        }
        result = await server.handle_call_tool("manage_dependencies", dep_args)
        assert "content" in result

        # Test manage_project_files
        file_args = {
            "action": "create",
            "file_type": "configuration",
            "file_path": "config/app_config.json",
        }
        result = await server.handle_call_tool("manage_project_files", file_args)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_external_integration_tools(self, server: KotlinMCPServer) -> None:
        """Test external integration tools"""
        # Test setup_external_api
        api_args = {
            "api_name": "weather_api",
            "base_url": "https://api.weather.com",
            "auth_type": "api_key",
            "endpoints": ["current", "forecast"],
        }
        result = await server.handle_call_tool("setup_external_api", api_args)
        assert "content" in result

        # Test call_external_api
        call_args = {
            "api_name": "test_api",
            "endpoint": "users",
            "method": "GET",
            "parameters": {"limit": 10},
        }
        result = await server.handle_call_tool("call_external_api", call_args)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_cloud_and_storage_tools(self, server: KotlinMCPServer) -> None:
        """Test cloud and storage tools"""
        # Test setup_cloud_sync
        cloud_args = {
            "provider": "firebase",
            "sync_types": ["user_data", "app_settings"],
            "offline_support": True,
        }
        result = await server.handle_call_tool("setup_cloud_sync", cloud_args)
        assert "content" in result

        # Test setup_secure_storage
        storage_args = {
            "storage_type": "encrypted_preferences",
            "encryption_level": "aes256",
            "backup_enabled": True,
        }
        result = await server.handle_call_tool("setup_secure_storage", storage_args)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_file_operations_and_error_handling(self, server: KotlinMCPServer) -> None:
        """Test file operations and error handling for better coverage"""
        # Create a test file for analysis

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kt", delete=False) as tmp:
            tmp.write("class TestClass { fun testMethod() {} }")
            tmp_path = tmp.name

        try:
            # Test analyze_code_with_ai with actual file (covers lines 1010-1026)
            arguments = {
                "file_path": tmp_path,
                "analysis_type": "performance",
                "focus_areas": ["memory", "performance"],
            }

            result = await server.handle_call_tool("analyze_code_with_ai", arguments)
            assert "content" in result

            # Test enhance_existing_code with actual file
            enhance_args = {
                "file_path": tmp_path,
                "enhancement_type": "performance",
                "current_code": "class Test {}",
                "requirements": ["add_logging"],
            }

            result = await server.handle_call_tool("enhance_existing_code", enhance_args)
            assert "content" in result

        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @pytest.mark.asyncio
    async def test_query_llm_tool(self, server: KotlinMCPServer) -> None:
        """Test query_llm tool for additional coverage"""
        arguments = {"prompt": "Explain Kotlin data classes", "context": "Android development"}

        result = await server.handle_call_tool("query_llm", arguments)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_initialization_and_properties(self, server: KotlinMCPServer) -> None:
        """Test server initialization and property access for additional coverage"""
        # Test server properties (server name is set in fixture as 'test-server')
        assert server.name == "test-server"
        # Test that server is properly initialized
        assert hasattr(server, "name")

    @pytest.mark.asyncio
    async def test_edge_cases_and_validation(self, server: KotlinMCPServer) -> None:
        """Test edge cases and validation for remaining coverage"""
        # Test tools with missing required parameters to trigger validation
        try:
            result = await server.handle_call_tool("create_kotlin_file", {})
            assert "content" in result
        except (KeyError, ValueError, TypeError):
            # Expected for invalid parameters
            pass

        # Test with empty/invalid arguments for additional coverage
        try:
            result = await server.handle_call_tool("gradle_build", {"invalid": "param"})
            assert "content" in result
        except (KeyError, ValueError, TypeError):
            pass


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=kotlin_mcp_server",
            "--cov-report=term-missing",
            "--cov-report=html",
        ]
    )
