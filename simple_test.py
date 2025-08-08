#!/usr/bin/env python3
"""
Simplified test suite for MCP server functionality
"""

import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

from ai_integration_server import AIIntegratedMCPServer


def is_mcp_success(response):
    """Helper function to check if MCP response indicates success"""
    if not isinstance(response, dict):
        return False

    # Check for error field - if present, not successful
    if "error" in response:
        return False

    # Check for content field with proper structure
    if "content" in response:
        content = response["content"]
        if isinstance(content, list) and len(content) > 0:
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text", "")
                    # Check for error indicators in text
                    if "error" in text.lower() or "failed" in text.lower():
                        return False
            return True

    # Check for success field (backward compatibility)
    return response.get("success", False)


class TestMCPServerBasic:
    """Test basic MCP server functionality"""

    @pytest_asyncio.fixture
    async def server(self):
        """Create server instance for testing"""
        server = AIIntegratedMCPServer("test-mcp-server")
        # Create temporary project directory
        server.project_path = Path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """Test server initializes correctly"""
        assert server.name == "test-mcp-server"
        assert server.project_path is not None

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test tools listing"""
        tools_response = await server.handle_list_tools()
        tools = tools_response.get("tools", [])
        assert isinstance(tools, list)
        # Should have at least some tools
        assert len(tools) > 0

    @pytest.mark.asyncio
    async def test_gdpr_compliance_implementation(self, server):
        """Test GDPR compliance feature implementation"""
        result = await server.handle_call_tool(
            "implement_gdpr_compliance",
            {
                "package_name": "com.example.app",
                "features": ["consent_management", "data_portability", "right_to_erasure"],
            },
        )
        assert is_mcp_success(result)

    @pytest.mark.asyncio
    async def test_llm_query_local(self, server):
        """Test local LLM integration"""
        result = await server.handle_call_tool(
            "query_llm",
            {
                "prompt": "Generate a Kotlin data class for User",
                "llm_provider": "local",
                "privacy_mode": True,
            },
        )
        assert is_mcp_success(result)

    @pytest.mark.asyncio
    async def test_code_generation_with_ai(self, server):
        """Test AI-powered code generation"""
        result = await server.handle_call_tool(
            "generate_code_with_ai",
            {
                "description": "Create a login screen with validation",
                "code_type": "component",
                "framework": "compose",
                "compliance_requirements": ["gdpr"],
            },
        )
        assert is_mcp_success(result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
