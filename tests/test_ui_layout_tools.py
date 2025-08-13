#!/usr/bin/env python3
"""
Test Suite for UI and Layout Tools
Tests UI component creation and layout tools
"""

import tempfile

import pytest

from kotlin_mcp_server import KotlinMCPServer


class TestUILayoutTools:
    """Test suite for UI and layout tools"""

    @pytest.fixture
    def server(self) -> "KotlinMCPServer":
        """Create server instance for testing"""
        server = KotlinMCPServer("test-server")
        server.set_project_path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_create_compose_component(self, server: KotlinMCPServer) -> None:
        """Test Jetpack Compose component creation"""
        result = await server.handle_call_tool(
            "create_compose_component",
            {"component_name": "UserCard", "component_type": "composable"},
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
    async def test_create_custom_view(self, server: KotlinMCPServer) -> None:
        """Test custom view creation"""
        result = await server.handle_call_tool(
            "create_custom_view", {"view_name": "CustomView", "base_view": "View"}
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
    async def test_ui_layout_variations(self, server: KotlinMCPServer) -> None:
        """Test UI/layout tools with various configurations"""
        test_cases = [
            (
                "create_compose_component",
                {"component_name": "ProductList", "component_type": "screen"},
            ),
            (
                "create_layout_file",
                {"file_path": "fragment_detail.xml", "layout_type": "ConstraintLayout"},
            ),
            (
                "create_custom_view",
                {"view_name": "CircularProgressBar", "base_view": "ProgressBar"},
            ),
            ("create_drawable_resource", {"resource_name": "ic_home", "drawable_type": "bitmap"}),
        ]

        for tool_name, args in test_cases:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result
            assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_compose_component_types(self, server: KotlinMCPServer) -> None:
        """Test different Compose component types"""
        component_types = ["composable", "screen", "dialog", "component"]

        for comp_type in component_types:
            result = await server.handle_call_tool(
                "create_compose_component",
                {"component_name": f"Test{comp_type.capitalize()}", "component_type": comp_type},
            )
            assert "content" in result
            assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_layout_types(self, server: KotlinMCPServer) -> None:
        """Test different layout types"""
        layout_types = ["LinearLayout", "ConstraintLayout", "RelativeLayout", "FrameLayout"]

        for layout_type in layout_types:
            result = await server.handle_call_tool(
                "create_layout_file",
                {"file_path": f"test_{layout_type.lower()}.xml", "layout_type": layout_type},
            )
            assert "content" in result
            assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_drawable_types(self, server: KotlinMCPServer) -> None:
        """Test different drawable types"""
        drawable_types = ["vector", "bitmap", "shape", "selector"]

        for drawable_type in drawable_types:
            result = await server.handle_call_tool(
                "create_drawable_resource",
                {"resource_name": f"test_{drawable_type}", "drawable_type": drawable_type},
            )
            assert "content" in result
            assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_ui_edge_cases(self, server: KotlinMCPServer) -> None:
        """Test UI tools with edge cases"""
        # Test with empty component name
        result = await server.handle_call_tool(
            "create_compose_component", {"component_name": "", "component_type": "composable"}
        )
        assert "content" in result

        # Test with invalid layout type
        result = await server.handle_call_tool(
            "create_layout_file", {"file_path": "test.xml", "layout_type": "InvalidLayout"}
        )
        assert "content" in result
