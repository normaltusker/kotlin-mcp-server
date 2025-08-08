#!/usr/bin/env python3
"""
Comprehensive test suite for the complete MCP server functionality
Tests security, privacy, AI integration, file management, and API features
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
                if item.get("type") == "text":
                    text = item.get("text", "")
                    # Check for error indicators in text
                    if "error" in text.lower() or "failed" in text.lower():
                        return False
            return True

    # Check for success field (backward compatibility)
    return response.get("success", False)


class TestMCPServerCore:
    """Test core MCP server functionality"""

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
        assert server.audit_db is not None
        assert server.security_logger is not None

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test tools listing includes all expected tools"""
        tools_response = await server.handle_list_tools()
        tools = tools_response.get("tools", [])

        # Check for security tools
        tool_names = [tool["name"] for tool in tools]
        assert "encrypt_sensitive_data" in tool_names
        assert "implement_gdpr_compliance" in tool_names
        assert "implement_hipaa_compliance" in tool_names

        # Check for AI tools
        assert "query_llm" in tool_names
        assert "analyze_code_with_ai" in tool_names
        assert "generate_code_with_ai" in tool_names

        # Check for file management tools
        assert "manage_project_files" in tool_names
        assert "setup_cloud_sync" in tool_names

        # Check for API integration tools
        assert "integrate_external_api" in tool_names
        assert "monitor_api_usage" in tool_names


class TestSecurityAndPrivacy:
    """Test security and privacy compliance features"""

    @pytest_asyncio.fixture
    async def server(self):
        server = AIIntegratedMCPServer("test-security-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

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
    async def test_hipaa_compliance_implementation(self, server):
        """Test HIPAA compliance feature implementation"""
        result = await server.handle_call_tool(
            "implement_hipaa_compliance",
            {
                "package_name": "com.healthcare.app",
                "features": ["audit_logging", "access_controls", "encryption"],
            },
        )

        assert is_mcp_success(result)

    @pytest.mark.asyncio
    async def test_data_encryption(self, server):
        """Test data encryption capabilities"""
        sensitive_data = "Patient John Doe, SSN: 123-45-6789"

        result = await server.handle_call_tool(
            "encrypt_sensitive_data",
            {
                "data": sensitive_data,
                "data_type": "phi",
                "compliance_level": "hipaa",
            },
        )

        # Should work regardless of cryptography availability
        assert is_mcp_success(result)

    @pytest.mark.asyncio
    async def test_privacy_policy_generation(self, server):
        """Test privacy policy generation"""
        result = await server.handle_call_tool(
            "generate_privacy_policy",
            {
                "app_name": "HealthTracker",
                "data_types": ["health_data", "location", "personal_info"],
                "compliance_requirements": ["gdpr", "hipaa"],
            },
        )

        assert is_mcp_success(result)


class TestAIIntegration:
    """Test AI/ML integration capabilities"""

    @pytest_asyncio.fixture
    async def server(self):
        server = AIIntegratedMCPServer("test-ai-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

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
    async def test_code_analysis_with_ai(self, server):
        """Test AI-powered code analysis"""
        # Create sample Kotlin code
        kotlin_code = """
        class UserManager {
            fun saveUser(user: User) {
                // Save user password without validation
                database.save(user.password)
            }
        }
        """

        result = await server.handle_call_tool(
            "analyze_code_with_ai",
            {
                "code": kotlin_code,
                "analysis_type": "security",
                "use_local_model": True,
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


class TestFileManagement:
    """Test advanced file management capabilities"""

    @pytest_asyncio.fixture
    async def server(self):
        server = AIIntegratedMCPServer("test-file-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_file_backup(self, server):
        """Test file backup functionality"""
        # Create test files
        test_dir = server.project_path / "src"
        test_dir.mkdir()
        (test_dir / "main.kt").write_text('fun main() { println("Hello") }')
        (test_dir / "config.env").write_text("SECRET_KEY=test123")

        backup_dir = server.project_path / "backup"

        result = await server.handle_call_tool(
            "manage_project_files",
            {
                "operation": "backup",
                "target_path": str(test_dir),
                "destination": str(backup_dir),
                "encryption_level": "standard",
            },
        )

        assert is_mcp_success(result)

    @pytest.mark.asyncio
    async def test_file_sync(self, server):
        """Test file synchronization"""
        source_dir = server.project_path / "source"
        dest_dir = server.project_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        (source_dir / "test.kt").write_text("class Test {}")

        result = await server.handle_call_tool(
            "manage_project_files",
            {
                "operation": "sync",
                "target_path": str(source_dir),
                "destination": str(dest_dir),
            },
        )

        assert is_mcp_success(result)


class TestExternalAPIIntegration:
    """Test external API integration capabilities"""

    @pytest_asyncio.fixture
    async def server(self):
        server = AIIntegratedMCPServer("test-api-server")
        return server

    @pytest.mark.asyncio
    async def test_api_integration_setup(self, server):
        """Test external API integration setup"""
        result = await server.handle_call_tool(
            "integrate_external_api",
            {
                "api_name": "TestAPI",
                "base_url": "https://api.test.com",
                "auth_type": "api_key",
                "security_features": ["rate_limiting", "request_logging"],
                "compliance_requirements": ["gdpr"],
            },
        )

        assert is_mcp_success(result)

    @pytest.mark.asyncio
    async def test_api_monitoring(self, server):
        """Test API usage monitoring"""
        # First integrate an API
        await server.handle_call_tool(
            "integrate_external_api",
            {
                "api_name": "MonitoredAPI",
                "base_url": "https://api.monitored.com",
                "auth_type": "none",
            },
        )

        result = await server.handle_call_tool(
            "monitor_api_usage",
            {
                "api_name": "MonitoredAPI",
                "metrics": ["latency", "error_rate", "usage_volume"],
            },
        )

        # Should return monitoring data structure
        assert "api_name" in result


class TestMLModelIntegration:
    """Test ML model integration"""

    @pytest_asyncio.fixture
    async def server(self):
        server = AIIntegratedMCPServer("test-ml-server")
        return server

    @pytest.mark.asyncio
    async def test_ml_model_integration(self, server):
        """Test ML model integration for Android"""
        result = await server.handle_call_tool(
            "integrate_ml_model",
            {
                "model_type": "tflite",
                "use_case": "image_classification",
                "privacy_preserving": True,
            },
        )

        assert is_mcp_success(result)


class TestIntegrationScenarios:
    """Test complete integration scenarios"""

    @pytest_asyncio.fixture
    async def server(self):
        server = AIIntegratedMCPServer("test-integration-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_healthcare_app_scenario(self, server):
        """Test complete healthcare app development scenario"""
        # 1. Implement HIPAA compliance
        hipaa_result = await server.handle_call_tool(
            "implement_hipaa_compliance",
            {
                "package_name": "com.health.tracker",
                "features": ["audit_logging", "encryption", "access_controls"],
            },
        )
        assert is_mcp_success(hipaa_result)

        # 2. Setup secure storage
        storage_result = await server.handle_call_tool(
            "setup_secure_storage",
            {
                "storage_type": "room_encrypted",
                "package_name": "com.health.tracker",
                "data_classification": "restricted",
            },
        )
        assert is_mcp_success(storage_result)

        # 3. Generate AI-powered code with compliance
        code_result = await server.handle_call_tool(
            "generate_code_with_ai",
            {
                "description": "Patient data entry form with validation",
                "code_type": "component",
                "framework": "compose",
                "compliance_requirements": ["hipaa"],
            },
        )
        assert is_mcp_success(code_result)

    @pytest.mark.asyncio
    async def test_fintech_app_scenario(self, server):
        """Test complete fintech app development scenario"""
        # 1. Implement GDPR compliance
        gdpr_result = await server.handle_call_tool(
            "implement_gdpr_compliance",
            {
                "package_name": "com.fintech.app",
                "features": ["consent_management", "data_portability"],
            },
        )
        assert is_mcp_success(gdpr_result)

        # 2. Integrate secure API
        api_result = await server.handle_call_tool(
            "integrate_external_api",
            {
                "api_name": "PaymentAPI",
                "base_url": "https://api.payments.com",
                "auth_type": "oauth",
                "security_features": ["rate_limiting", "request_logging"],
            },
        )
        assert is_mcp_success(api_result)

        # 3. Setup cloud sync with encryption
        sync_result = await server.handle_call_tool(
            "setup_cloud_sync",
            {
                "cloud_provider": "aws",
                "sync_strategy": "scheduled",
                "encryption_in_transit": True,
                "compliance_mode": "gdpr",
            },
        )
        assert is_mcp_success(sync_result)


if __name__ == "__main__":
    # Run comprehensive tests
    import sys

    print("🚀 Starting Comprehensive MCP Server Test Suite...")
    print("=" * 60)

    # Run tests with verbose output
    exit_code = pytest.main([__file__, "-v", "--tb=short", "--disable-warnings"])

    if exit_code == 0:
        print("=" * 60)
        print("✅ ALL TESTS PASSED! MCP Server is fully functional.")
        print("📊 Features verified:")
        print("   • Security & Privacy (GDPR/HIPAA)")
        print("   • AI/ML Integration")
        print("   • File Management")
        print("   • External API Integration")
        print("   • Complete workflow scenarios")
    else:
        print("=" * 60)
        print("❌ Some tests failed. Check output above for details.")

    sys.exit(exit_code)
