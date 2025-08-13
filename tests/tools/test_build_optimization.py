#!/usr/bin/env python3
"""
Test Suite for Build Optimization Tools Module
Tests build optimization and performance tools
"""

import tempfile

import pytest

from kotlin_mcp_server import KotlinMCPServer


class TestBuildOptimizationTools:
    """Test suite for build optimization tools functionality"""

    @pytest.fixture
    def server(self) -> "KotlinMCPServer":
        """Create server instance for testing"""
        server = KotlinMCPServer("test-server")
        server.set_project_path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_setup_mvvm_architecture(self, server: KotlinMCPServer) -> None:
        """Test MVVM architecture setup"""
        result = await server.handle_call_tool(
            "setup_mvvm_architecture", {"feature_name": "User", "include_repository": True}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_setup_room_database(self, server: KotlinMCPServer) -> None:
        """Test Room database setup"""
        result = await server.handle_call_tool(
            "setup_room_database", {"database_name": "AppDatabase", "entities": ["User", "Post"]}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_setup_retrofit_api(self, server: KotlinMCPServer) -> None:
        """Test Retrofit API setup"""
        result = await server.handle_call_tool(
            "setup_retrofit_api", {"api_name": "UserApi", "base_url": "https://api.example.com/"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_setup_dependency_injection(self, server: KotlinMCPServer) -> None:
        """Test dependency injection setup"""
        result = await server.handle_call_tool(
            "setup_dependency_injection", {"di_framework": "hilt", "modules": ["NetworkModule"]}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_setup_navigation_component(self, server: KotlinMCPServer) -> None:
        """Test Navigation Component setup"""
        result = await server.handle_call_tool(
            "setup_navigation_component",
            {"nav_graph_name": "nav_graph", "destinations": ["HomeFragment"]},
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_setup_data_binding(self, server: KotlinMCPServer) -> None:
        """Test data binding setup"""
        result = await server.handle_call_tool(
            "setup_data_binding", {"enable_dataBinding": True, "enable_viewBinding": True}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_setup_view_binding(self, server: KotlinMCPServer) -> None:
        """Test view binding setup"""
        result = await server.handle_call_tool(
            "setup_view_binding", {"module_name": "app", "enable_viewBinding": True}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_optimization_tools_variations(self, server: KotlinMCPServer) -> None:
        """Test build optimization tools with various configurations"""
        test_cases = [
            ("setup_mvvm_architecture", {"feature_name": "Product", "include_repository": False}),
            ("setup_room_database", {"database_name": "UserDatabase", "entities": ["Profile"]}),
            (
                "setup_retrofit_api",
                {"api_name": "ProductApi", "base_url": "https://store.api.com/"},
            ),
            (
                "setup_dependency_injection",
                {"di_framework": "dagger", "modules": ["DatabaseModule"]},
            ),
        ]

        for tool_name, args in test_cases:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result
            assert isinstance(result["content"], list)
