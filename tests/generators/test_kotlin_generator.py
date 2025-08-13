#!/usr/bin/env python3
"""
Test Suite for Kotlin Code Generator Module
Tests Kotlin code generation functionality
"""

import tempfile

import pytest

from kotlin_mcp_server import KotlinMCPServer


class TestKotlinGenerator:
    """Test suite for Kotlin code generator functionality"""

    @pytest.fixture
    def server(self) -> "KotlinMCPServer":
        """Create server instance for testing"""
        server = KotlinMCPServer("test-server")
        server.set_project_path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_create_kotlin_class(self, server: KotlinMCPServer) -> None:
        """Test Kotlin class creation"""
        result = await server.handle_call_tool(
            "create_kotlin_class", {"class_name": "TestClass", "package_name": "com.test"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_create_kotlin_data_class(self, server: KotlinMCPServer) -> None:
        """Test Kotlin data class creation"""
        result = await server.handle_call_tool(
            "create_kotlin_data_class",
            {"class_name": "DataClass", "properties": ["name: String", "age: Int"]},
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_create_kotlin_interface(self, server: KotlinMCPServer) -> None:
        """Test Kotlin interface creation"""
        result = await server.handle_call_tool(
            "create_kotlin_interface",
            {
                "interface_name": "TestInterface",
                "methods": ["fun test()", "fun validate(): Boolean"],
            },
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_create_fragment(self, server: KotlinMCPServer) -> None:
        """Test Android Fragment creation"""
        result = await server.handle_call_tool(
            "create_fragment", {"fragment_name": "TestFragment", "layout_name": "fragment_test"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_create_activity(self, server: KotlinMCPServer) -> None:
        """Test Android Activity creation"""
        result = await server.handle_call_tool(
            "create_activity", {"activity_name": "TestActivity", "layout_name": "activity_test"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_create_service(self, server: KotlinMCPServer) -> None:
        """Test Android Service creation"""
        result = await server.handle_call_tool(
            "create_service", {"service_name": "TestService", "service_type": "foreground"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_create_broadcast_receiver(self, server: KotlinMCPServer) -> None:
        """Test Android BroadcastReceiver creation"""
        result = await server.handle_call_tool(
            "create_broadcast_receiver",
            {"receiver_name": "TestReceiver", "actions": ["ACTION_TEST", "ACTION_CUSTOM"]},
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_create_custom_view(self, server: KotlinMCPServer) -> None:
        """Test custom view creation"""
        result = await server.handle_call_tool(
            "create_custom_view", {"view_name": "CustomView", "base_view": "View"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_create_layout_file(self, server: KotlinMCPServer) -> None:
        """Test layout file creation"""
        result = await server.handle_call_tool(
            "create_layout_file", {"file_path": "activity_main.xml", "layout_type": "LinearLayout"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_create_drawable_resource(self, server: KotlinMCPServer) -> None:
        """Test drawable resource creation"""
        result = await server.handle_call_tool(
            "create_drawable_resource",
            {"resource_name": "test_drawable", "drawable_type": "vector"},
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_kotlin_class_variations(self, server: KotlinMCPServer) -> None:
        """Test Kotlin class creation with various configurations"""
        test_cases = [
            (
                "create_kotlin_class",
                {"class_name": "UserController", "package_name": "com.example.controller"},
            ),
            (
                "create_kotlin_data_class",
                {"class_name": "User", "properties": ["id: Long", "email: String"]},
            ),
            (
                "create_kotlin_interface",
                {
                    "interface_name": "Repository",
                    "methods": ["suspend fun save()", "fun findAll(): List<T>"],
                },
            ),
            ("create_fragment", {"fragment_name": "HomeFragment", "layout_name": "fragment_home"}),
            ("create_activity", {"activity_name": "MainActivity", "layout_name": "activity_main"}),
        ]

        for tool_name, args in test_cases:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result
            assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_android_component_variations(self, server: KotlinMCPServer) -> None:
        """Test Android component creation with different configurations"""
        test_cases = [
            ("create_service", {"service_name": "BackgroundService", "service_type": "background"}),
            (
                "create_broadcast_receiver",
                {"receiver_name": "NetworkReceiver", "actions": ["CONNECTIVITY_CHANGE"]},
            ),
            ("create_custom_view", {"view_name": "CircularImageView", "base_view": "ImageView"}),
            (
                "create_layout_file",
                {"file_path": "fragment_detail.xml", "layout_type": "ConstraintLayout"},
            ),
            ("create_drawable_resource", {"resource_name": "ic_home", "drawable_type": "bitmap"}),
        ]

        for tool_name, args in test_cases:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result
            assert isinstance(result["content"], list)
