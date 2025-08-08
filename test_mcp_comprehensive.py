#!/usr/bin/env python3
"""
Comprehensive Unit Test Suite for MCP Server
Tests all functionality and ensures no breaking changes after enhancements
"""

import asyncio
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio

from ai_integration_server import AIIntegratedMCPServer
from enhanced_mcp_server import EnhancedAndroidMCPServer
from security_privacy_server import SecurityPrivacyMCPServer

# Import all server classes
from simple_mcp_server import MCPServer
from vscode_bridge import MCPBridgeHandler


def is_mcp_success(result: dict) -> bool:
    """Check if an MCP response indicates success (no error messages)"""
    if not result or "content" not in result:
        return False

    content = result["content"]
    if not content or not isinstance(content, list):
        return False

    # Check if any content contains explicit error messages
    for item in content:
        if isinstance(item, dict) and "text" in item:
            text = item["text"].lower()
            # Look for explicit error indicators
            if any(
                error_phrase in text
                for error_phrase in [
                    "error executing",
                    "failed to",
                    "unknown tool:",
                    "unknown enhanced tool:",
                    "error:",
                    "attributeerror:",
                    "exception:",
                    "traceback",
                ]
            ):
                return False

    return True


class TestMCPServerBase:
    """Test base MCP server functionality"""

    @pytest_asyncio.fixture
    async def base_server(self):
        """Create base server instance for testing"""
        server = MCPServer("test-base-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_base_server_initialization(self, base_server):
        """Test base server initializes correctly"""
        assert base_server.name == "test-base-server"
        assert base_server.project_path is not None
        assert base_server.project_path.exists()

    @pytest.mark.asyncio
    async def test_base_tools_listing(self, base_server):
        """Test base tools are listed correctly"""
        tools_response = await base_server.handle_list_tools()
        tools = tools_response.get("tools", [])

        # Check basic tools exist
        tool_names = [tool["name"] for tool in tools]
        expected_tools = [
            "gradle_build",
            "run_tests",
            "create_kotlin_file",
            "create_layout_file",
            "analyze_project",
        ]

        for tool in expected_tools:
            assert tool in tool_names, f"Missing basic tool: {tool}"

    @pytest.mark.asyncio
    async def test_gradle_build_tool(self, base_server):
        """Test gradle build functionality"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "BUILD SUCCESSFUL"

            result = await base_server.handle_call_tool(
                "gradle_build", {"task": "assembleDebug", "clean": True}
            )

            assert is_mcp_success(result)
            # Check that BUILD SUCCESSFUL appears in the response content
            content_text = ""
            if "content" in result and result["content"]:
                for item in result["content"]:
                    if "text" in item:
                        content_text += item["text"]
            assert "BUILD SUCCESSFUL" in content_text

    @pytest.mark.asyncio
    async def test_kotlin_file_creation(self, base_server):
        """Test Kotlin file creation"""
        result = await base_server.handle_call_tool(
            "create_kotlin_file",
            {
                "file_path": "src/main/kotlin/test/TestClass.kt",
                "class_name": "TestClass",
                "package_name": "com.test.app",
                "class_type": "data",
            },
        )

        assert is_mcp_success(result)
        expected_file = base_server.project_path / "src/main/kotlin/test/TestClass.kt"
        assert expected_file.exists()

    @pytest.mark.asyncio
    async def test_layout_file_creation(self, base_server):
        """Test layout file creation"""
        result = await base_server.handle_call_tool(
            "create_layout_file",
            {
                "layout_name": "test_layout",
                "layout_type": "activity",
            },
        )

        assert is_mcp_success(result)
        expected_file = base_server.project_path / "app/src/main/res/layout/test_layout.xml"
        assert expected_file.exists()


class TestEnhancedMCPServer:
    """Test enhanced MCP server functionality"""

    @pytest_asyncio.fixture
    async def enhanced_server(self):
        """Create enhanced server instance for testing"""
        server = EnhancedAndroidMCPServer("test-enhanced-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_enhanced_server_initialization(self, enhanced_server):
        """Test enhanced server initializes correctly"""
        assert enhanced_server.name == "test-enhanced-server"
        assert enhanced_server.project_path is not None

    @pytest.mark.asyncio
    async def test_enhanced_tools_listing(self, enhanced_server):
        """Test enhanced tools are listed correctly"""
        tools_response = await enhanced_server.handle_list_tools()
        tools = tools_response.get("tools", [])

        # Check enhanced tools exist
        tool_names = [tool["name"] for tool in tools]
        enhanced_tools = [
            "create_compose_component",
            "create_custom_view",
            "setup_mvvm_architecture",
            "setup_dependency_injection",
            "setup_room_database",
            "setup_retrofit_api",
            "setup_navigation_component",
            "create_work_manager_worker",
            "setup_coroutines_flow",
            "create_firebase_integration",
            "setup_data_store",
            "create_permission_handler",
            "setup_biometric_auth",
            "create_notification_system",
            "setup_camera_integration",
            "create_media_player",
            "setup_security_crypto",
            "create_accessibility_features",
        ]

        for tool in enhanced_tools:
            assert tool in tool_names, f"Missing enhanced tool: {tool}"

    @pytest.mark.asyncio
    async def test_compose_component_creation(self, enhanced_server):
        """Test Jetpack Compose component creation"""
        result = await enhanced_server.handle_call_tool(
            "create_compose_component",
            {
                "file_path": "src/main/kotlin/ui/TestScreen.kt",
                "component_name": "TestScreen",
                "component_type": "screen",
                "package_name": "com.test.app.ui",
                "uses_state": True,
                "uses_navigation": True,
            },
        )

        assert is_mcp_success(result)
        expected_file = enhanced_server.project_path / "src/main/kotlin/ui/TestScreen.kt"
        assert expected_file.exists()

    @pytest.mark.asyncio
    async def test_mvvm_architecture_setup(self, enhanced_server):
        """Test MVVM architecture setup"""
        result = await enhanced_server.handle_call_tool(
            "setup_mvvm_architecture",
            {
                "feature_name": "user",
                "package_name": "com.test.app",
                "include_repository": True,
                "include_use_cases": True,
                "data_source": "both",
            },
        )

        assert is_mcp_success(result)
        # Check if ViewModel, Repository, and UseCase files are created
        base_path = enhanced_server.project_path / "src/main/kotlin/com/test/app/user"
        assert (base_path / "UserViewModel.kt").exists()
        assert (base_path / "UserRepository.kt").exists()
        assert (base_path / "UserUseCase.kt").exists()

    @pytest.mark.asyncio
    async def test_room_database_setup(self, enhanced_server):
        """Test Room database setup"""
        result = await enhanced_server.handle_call_tool(
            "setup_room_database",
            {
                "database_name": "AppDatabase",
                "package_name": "com.test.app.data",
                "entities": ["User", "Product"],
                "include_migration": True,
            },
        )

        assert is_mcp_success(result)
        # Check if database files are created
        base_path = enhanced_server.project_path / "src/main/kotlin/com/test/app/data"
        assert (base_path / "AppDatabase.kt").exists()
        assert (base_path / "entities" / "User.kt").exists()
        assert (base_path / "dao" / "UserDao.kt").exists()

    @pytest.mark.asyncio
    async def test_retrofit_api_setup(self, enhanced_server):
        """Test Retrofit API setup"""
        result = await enhanced_server.handle_call_tool(
            "setup_retrofit_api",
            {
                "api_name": "UserApi",
                "package_name": "com.test.app.network",
                "base_url": "https://api.example.com",
                "endpoints": [
                    {"method": "GET", "path": "/users", "name": "getUsers"},
                    {"method": "POST", "path": "/users", "name": "createUser"},
                ],
                "include_interceptors": True,
            },
        )

        assert is_mcp_success(result)
        base_path = enhanced_server.project_path / "src/main/kotlin/com/test/app/network"
        assert (base_path / "UserApi.kt").exists()


class TestSecurityPrivacyServer:
    """Test security and privacy functionality"""

    @pytest_asyncio.fixture
    async def security_server(self):
        """Create security server instance for testing"""
        server = SecurityPrivacyMCPServer("test-security-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_security_server_initialization(self, security_server):
        """Test security server initializes correctly"""
        assert security_server.name == "test-security-server"
        assert security_server.audit_db is not None
        assert security_server.security_logger is not None

    @pytest.mark.asyncio
    async def test_gdpr_compliance_implementation(self, security_server):
        """Test GDPR compliance implementation"""
        result = await security_server.handle_call_tool(
            "implement_gdpr_compliance",
            {
                "package_name": "com.test.app",
                "features": ["consent_management", "data_portability", "right_to_erasure"],
            },
        )

        assert is_mcp_success(result)
        assert result.get("compliance_standard") == "GDPR"
        assert len(result.get("implemented_features", [])) == 3

    @pytest.mark.asyncio
    async def test_hipaa_compliance_implementation(self, security_server):
        """Test HIPAA compliance implementation"""
        result = await security_server.handle_call_tool(
            "implement_hipaa_compliance",
            {
                "package_name": "com.healthcare.app",
                "features": ["audit_logging", "access_controls", "encryption"],
            },
        )

        assert is_mcp_success(result)
        assert result.get("compliance_standard") == "HIPAA"
        assert len(result.get("implemented_features", [])) == 3

    @pytest.mark.asyncio
    async def test_data_encryption(self, security_server):
        """Test data encryption functionality"""
        test_data = "sensitive user data"
        result = await security_server.handle_call_tool(
            "encrypt_sensitive_data",
            {"data": test_data, "encryption_type": "aes256", "key_source": "generated"},
        )

        assert is_mcp_success(result)
        assert result.get("encrypted_data") != test_data
        assert result.get("encryption_method") == "aes256"

    @pytest.mark.asyncio
    async def test_audit_logging(self, security_server):
        """Test audit logging functionality"""
        # Perform an action that should be logged
        await security_server.handle_call_tool(
            "implement_gdpr_compliance",
            {"package_name": "com.test.app", "features": ["consent_management"]},
        )

        # Check if audit entry was created
        cursor = security_server.audit_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        count = cursor.fetchone()[0]

        assert count > 0, "Audit log should contain entries"


class TestAIIntegrationServer:
    """Test AI integration functionality"""

    @pytest_asyncio.fixture
    async def ai_server(self):
        """Create AI server instance for testing"""
        server = AIIntegratedMCPServer("test-ai-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_ai_server_initialization(self, ai_server):
        """Test AI server initializes correctly"""
        assert ai_server.name == "test-ai-server"
        assert hasattr(ai_server, "llm_clients")
        assert hasattr(ai_server, "local_models")
        assert hasattr(ai_server, "api_clients")

    @pytest.mark.asyncio
    async def test_local_llm_query(self, ai_server):
        """Test local LLM query functionality"""
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"response": "Generated Kotlin code"}
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            result = await ai_server.handle_call_tool(
                "query_llm",
                {
                    "prompt": "Generate a Kotlin data class for User",
                    "llm_provider": "local",
                    "privacy_mode": True,
                },
            )

            assert is_mcp_success(result)
            assert "response" in result

    @pytest.mark.asyncio
    async def test_code_generation_with_ai(self, ai_server):
        """Test AI-powered code generation"""
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"response": "Generated Compose component"}
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            result = await ai_server.handle_call_tool(
                "generate_code_with_ai",
                {
                    "description": "Create a login screen with validation",
                    "code_type": "component",
                    "framework": "compose",
                    "compliance_requirements": ["gdpr"],
                },
            )

            assert is_mcp_success(result)

    @pytest.mark.asyncio
    async def test_code_analysis_with_ai(self, ai_server):
        """Test AI-powered code analysis"""
        test_code = """
        class UserActivity : AppCompatActivity() {
            override fun onCreate(savedInstanceState: Bundle?) {
                super.onCreate(savedInstanceState)
                setContentView(R.layout.activity_user)
            }
        }
        """

        result = await ai_server.handle_call_tool(
            "analyze_code_with_ai",
            {"code": test_code, "analysis_type": "security", "language": "kotlin"},
        )

        assert is_mcp_success(result)

    @pytest.mark.asyncio
    async def test_external_api_integration(self, ai_server):
        """Test external API integration"""
        result = await ai_server.handle_call_tool(
            "integrate_external_api",
            {
                "api_name": "weather_api",
                "api_url": "https://api.openweathermap.org/data/2.5",
                "auth_method": "api_key",
                "endpoints": ["/weather", "/forecast"],
                "package_name": "com.test.app.api",
            },
        )

        assert is_mcp_success(result)


class TestFileAndAPIManagement:
    """Test file management and API functionality"""

    @pytest_asyncio.fixture
    async def full_server(self):
        """Create full server instance for testing"""
        server = AIIntegratedMCPServer("test-full-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_project_file_management(self, full_server):
        """Test project file management"""
        result = await full_server.handle_call_tool(
            "manage_project_files",
            {
                "operation": "backup",
                "target_path": "src/",
                "backup_location": "backup/",
                "include_patterns": ["*.kt", "*.xml"],
                "exclude_patterns": ["*.tmp"],
            },
        )

        assert is_mcp_success(result)

    @pytest.mark.asyncio
    async def test_cloud_sync_setup(self, full_server):
        """Test cloud sync setup"""
        result = await full_server.handle_call_tool(
            "setup_cloud_sync",
            {
                "provider": "google_drive",
                "sync_folders": ["src/", "res/"],
                "sync_frequency": "daily",
                "encryption": True,
            },
        )

        assert is_mcp_success(result)

    @pytest.mark.asyncio
    async def test_api_usage_monitoring(self, full_server):
        """Test API usage monitoring"""
        result = await full_server.handle_call_tool(
            "monitor_api_usage",
            {
                "api_endpoints": ["/users", "/products"],
                "metrics": ["requests_per_hour", "error_rate", "response_time"],
                "alert_thresholds": {"error_rate": 5.0, "response_time": 1000},
            },
        )

        assert is_mcp_success(result)


class TestToolIntegrity:
    """Test tool integrity and schema validation"""

    @pytest_asyncio.fixture
    async def all_servers(self):
        """Create all server types for testing"""
        return {
            "base": MCPServer("test-base"),
            "enhanced": EnhancedAndroidMCPServer("test-enhanced"),
            "security": SecurityPrivacyMCPServer("test-security"),
            "ai": AIIntegratedMCPServer("test-ai"),
        }

    @pytest.mark.asyncio
    async def test_tool_schema_integrity(self, all_servers):
        """Test all tools have proper schemas"""
        for server_name, server in all_servers.items():
            server.project_path = Path(tempfile.mkdtemp())
            tools_response = await server.handle_list_tools()
            tools = tools_response.get("tools", [])

            for tool in tools:
                # Check required fields
                assert "name" in tool, f"Tool missing name in {server_name}"
                assert "description" in tool, f"Tool missing description in {server_name}"
                assert "inputSchema" in tool, f"Tool missing inputSchema in {server_name}"

                # Check schema structure
                schema = tool["inputSchema"]
                assert "type" in schema, f"Schema missing type for {tool['name']} in {server_name}"
                assert (
                    schema["type"] == "object"
                ), f"Schema type not object for {tool['name']} in {server_name}"

    @pytest.mark.asyncio
    async def test_tool_name_uniqueness(self, all_servers):
        """Test tool names are unique within each server"""
        for server_name, server in all_servers.items():
            server.project_path = Path(tempfile.mkdtemp())
            tools_response = await server.handle_list_tools()
            tools = tools_response.get("tools", [])

            tool_names = [tool["name"] for tool in tools]
            unique_names = set(tool_names)

            assert len(tool_names) == len(unique_names), f"Duplicate tool names in {server_name}"

    @pytest.mark.asyncio
    async def test_error_handling(self, all_servers):
        """Test error handling for invalid tool calls"""
        for server_name, server in all_servers.items():
            server.project_path = Path(tempfile.mkdtemp())

            # Test invalid tool name
            result = await server.handle_call_tool("invalid_tool_name", {})
            assert not is_mcp_success(result)
            assert "error" in result or "message" in result

    @pytest.mark.asyncio
    async def test_required_parameters(self, all_servers):
        """Test tools properly validate required parameters"""
        for server_name, server in all_servers.items():
            server.project_path = Path(tempfile.mkdtemp())
            tools_response = await server.handle_list_tools()
            tools = tools_response.get("tools", [])

            for tool in tools:
                schema = tool["inputSchema"]
                if "required" in schema and schema["required"]:
                    # Test calling tool without required parameters
                    result = await server.handle_call_tool(tool["name"], {})
                    # Should either fail gracefully or handle missing params
                    assert isinstance(result, dict), f"Tool {tool['name']} should return dict"


class TestPerformanceAndStability:
    """Test performance and stability"""

    @pytest_asyncio.fixture
    async def stress_server(self):
        """Create server for stress testing"""
        server = AIIntegratedMCPServer("test-stress-server")
        server.project_path = Path(tempfile.mkdtemp())
        return server

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, stress_server):
        """Test concurrent tool execution"""
        # Create multiple concurrent tool calls
        tasks = []
        for i in range(10):
            task = stress_server.handle_call_tool(
                "create_kotlin_file",
                {
                    "file_path": f"src/main/kotlin/Test{i}.kt",
                    "class_name": f"Test{i}",
                    "package_name": "com.test.app",
                    "class_type": "class",
                },
            )
            tasks.append(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check all succeeded
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), f"Task {i} failed with exception: {result}"
            assert is_mcp_success(result), f"Task {i} failed: {result}"

    @pytest.mark.asyncio
    async def test_memory_usage(self, stress_server):
        """Test memory usage doesn't grow excessively"""
        try:
            import gc

            import psutil

            process = psutil.Process()
            initial_memory = process.memory_info().rss

            # Perform many operations
            for i in range(50):
                await stress_server.handle_call_tool(
                    "create_kotlin_file",
                    {
                        "file_path": f"src/main/kotlin/MemTest{i}.kt",
                        "class_name": f"MemTest{i}",
                        "package_name": "com.test.app",
                        "class_type": "class",
                    },
                )

                if i % 10 == 0:
                    gc.collect()  # Force garbage collection

            final_memory = process.memory_info().rss
            memory_growth = final_memory - initial_memory

            # Memory shouldn't grow by more than 100MB
            assert (
                memory_growth < 100 * 1024 * 1024
            ), f"Memory grew by {memory_growth / 1024 / 1024:.2f}MB"

        except ImportError:
            # Skip memory test if psutil is not available
            pytest.skip("psutil not available for memory testing")


class TestVSCodeBridgeServer:
    """Test VS Code Bridge Server HTTP API functionality"""

    @pytest.fixture(scope="class")
    def bridge_server_port(self):
        """Get an available port for testing"""
        import socket

        sock = socket.socket()
        sock.bind(("", 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    @pytest.fixture(scope="class")
    def bridge_server_thread(self, bridge_server_port):
        """Start bridge server in a separate thread for testing"""
        import os
        from http.server import HTTPServer

        # Set test environment variables
        os.environ["MCP_BRIDGE_HOST"] = "localhost"
        os.environ["MCP_BRIDGE_PORT"] = str(bridge_server_port)
        os.environ["VSCODE_WORKSPACE_FOLDER"] = str(Path(tempfile.mkdtemp()))

        # Create server
        server_address = ("localhost", bridge_server_port)
        httpd = HTTPServer(server_address, MCPBridgeHandler)

        # Start server in thread
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        # Wait for server to start
        time.sleep(0.5)

        yield {
            "port": bridge_server_port,
            "base_url": f"http://localhost:{bridge_server_port}",
            "httpd": httpd,
        }

        # Cleanup
        httpd.shutdown()
        httpd.server_close()

    def test_bridge_server_health_check(self, bridge_server_thread):
        """Test bridge server health endpoint"""
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not available")

        base_url = bridge_server_thread["base_url"]

        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "current_workspace" in data
        assert "available_tools" in data
        assert isinstance(data["available_tools"], list)

        # Check expected tools are listed
        expected_tools = ["gradle_build", "run_tests", "create_kotlin_file", "analyze_project"]
        for tool in expected_tools:
            assert tool in data["available_tools"]

    def test_bridge_server_404_for_unknown_paths(self, bridge_server_thread):
        """Test bridge server returns 404 for unknown paths"""
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not available")

        base_url = bridge_server_thread["base_url"]

        # Test unknown endpoint
        response = requests.get(f"{base_url}/unknown", timeout=5)
        assert response.status_code == 404

    def test_bridge_server_tool_execution(self, bridge_server_thread):
        """Test bridge server tool execution via POST"""
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not available")

        base_url = bridge_server_thread["base_url"]

        # Test valid tool call
        tool_request = {"tool": "list_tools", "arguments": {}}

        response = requests.post(
            base_url, json=tool_request, headers={"Content-Type": "application/json"}, timeout=10
        )

        assert response.status_code == 200

        # Response should be JSON
        data = response.json()
        assert isinstance(data, dict)

        # Should contain tools list or success indicator
        # (Exact response format depends on MCP implementation)
        assert "tools" in data or "content" in data or "result" in data

    def test_bridge_server_invalid_tool(self, bridge_server_thread):
        """Test bridge server handles invalid tool gracefully"""
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not available")

        base_url = bridge_server_thread["base_url"]

        # Test invalid tool call
        tool_request = {"tool": "nonexistent_tool", "arguments": {}}

        response = requests.post(
            base_url, json=tool_request, headers={"Content-Type": "application/json"}, timeout=10
        )

        assert response.status_code == 200

        # Should return error in response
        data = response.json()
        assert isinstance(data, dict)
        assert "result" in data
        result = data["result"]
        assert "error" in result

    def test_bridge_server_malformed_request(self, bridge_server_thread):
        """Test bridge server handles malformed requests"""
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not available")

        base_url = bridge_server_thread["base_url"]

        # Test malformed JSON
        response = requests.post(
            base_url, data="invalid json", headers={"Content-Type": "application/json"}, timeout=5
        )

        assert response.status_code == 500

        # Should return error in response
        data = response.json()
        assert isinstance(data, dict)
        assert "error" in data

    def test_bridge_server_missing_arguments(self, bridge_server_thread):
        """Test bridge server handles missing arguments"""
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not available")

        base_url = bridge_server_thread["base_url"]

        # Test request without required fields
        incomplete_request = {
            "arguments": {}
            # Missing 'tool' field
        }

        response = requests.post(
            base_url,
            json=incomplete_request,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )

        assert response.status_code == 200

        # Should return error in response
        data = response.json()
        assert isinstance(data, dict)
        assert "result" in data
        result = data["result"]
        assert "error" in result

    def test_bridge_server_cors_headers(self, bridge_server_thread):
        """Test bridge server includes CORS headers"""
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not available")

        base_url = bridge_server_thread["base_url"]

        # Test OPTIONS request
        response = requests.options(base_url, timeout=5)
        assert response.status_code == 200

        # Should include CORS headers
        headers = response.headers
        assert "Access-Control-Allow-Origin" in headers
        assert "Access-Control-Allow-Methods" in headers
        assert "Access-Control-Allow-Headers" in headers

    def test_bridge_server_workspace_detection(self, bridge_server_thread):
        """Test bridge server detects workspace correctly"""
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not available")

        base_url = bridge_server_thread["base_url"]

        # Get health check to see workspace info
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200

        data = response.json()
        workspace = data.get("current_workspace")

        # Should have workspace path
        assert workspace is not None
        assert isinstance(workspace, str)
        assert len(workspace) > 0

    @pytest.mark.asyncio
    async def test_bridge_server_concurrent_requests(self, bridge_server_thread):
        """Test bridge server handles concurrent requests"""
        try:
            import asyncio

            import aiohttp
        except ImportError:
            pytest.skip("aiohttp library not available")

        base_url = bridge_server_thread["base_url"]

        async def make_request(session, request_id):
            """Make a single request"""
            try:
                async with session.get(f"{base_url}/health") as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data["status"] == "healthy"
                    return request_id
            except Exception as e:
                pytest.fail(f"Request {request_id} failed: {e}")

        # Make multiple concurrent requests
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session, i) for i in range(5)]
            results = await asyncio.gather(*tasks)

            # All requests should succeed
            assert len(results) == 5
            assert all(isinstance(r, int) for r in results)


if __name__ == "__main__":
    # Run with coverage
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80",
        ]
    )
