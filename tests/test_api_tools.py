#!/usr/bin/env python3
"""
Test Suite for API and External Service Tools
Tests external API calls and integration tools
"""

import tempfile

import pytest

from kotlin_mcp_server import KotlinMCPServer


class TestAPITools:
    """Test suite for API and external service tools"""

    @pytest.fixture
    def server(self) -> "KotlinMCPServer":
        """Create server instance for testing"""
        server = KotlinMCPServer("test-server")
        server.set_project_path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_call_external_api(self, server: KotlinMCPServer) -> None:
        """Test external API call tool"""
        result = await server.handle_call_tool(
            "call_external_api", {"api_name": "TestAPI", "method": "GET", "endpoint": "/test"}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_setup_ui_testing(self, server: KotlinMCPServer) -> None:
        """Test UI testing setup"""
        result = await server.handle_call_tool(
            "setup_ui_testing", {"test_framework": "espresso", "include_page_objects": True}
        )
        assert "content" in result
        assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_api_tools_variations(self, server: KotlinMCPServer) -> None:
        """Test API tools with various configurations"""
        test_cases = [
            ("call_external_api", {"api_name": "UserAPI", "method": "POST", "endpoint": "/users"}),
            (
                "call_external_api",
                {"api_name": "ProductAPI", "method": "PUT", "endpoint": "/products/123"},
            ),
            (
                "call_external_api",
                {"api_name": "OrderAPI", "method": "DELETE", "endpoint": "/orders/456"},
            ),
            ("setup_ui_testing", {"test_framework": "androidx", "include_page_objects": False}),
            ("setup_ui_testing", {"test_framework": "robolectric", "include_page_objects": True}),
        ]

        for tool_name, args in test_cases:
            result = await server.handle_call_tool(tool_name, args)
            assert "content" in result
            assert isinstance(result["content"], list)

    @pytest.mark.asyncio
    async def test_api_edge_cases(self, server: KotlinMCPServer) -> None:
        """Test API tools with edge cases"""
        # Test with empty endpoint
        result = await server.handle_call_tool(
            "call_external_api", {"api_name": "TestAPI", "method": "GET", "endpoint": ""}
        )
        assert "content" in result

        # Test with invalid HTTP method
        result = await server.handle_call_tool(
            "call_external_api", {"api_name": "TestAPI", "method": "INVALID", "endpoint": "/test"}
        )
        assert "content" in result

        # Test with empty API name
        result = await server.handle_call_tool(
            "call_external_api", {"api_name": "", "method": "GET", "endpoint": "/test"}
        )
        assert "content" in result
