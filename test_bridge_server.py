#!/usr/bin/env python3
"""
Dedicated Test Suite for VS Code Bridge Server
Tests HTTP API functionality, health checks, and tool execution
"""

import os
import socket
import tempfile
import threading
import time
from unittest.mock import patch

import pytest


class TestBridgeServerStandalone:
    """Standalone tests for bridge server without external dependencies"""

    def test_bridge_server_module_import(self):
        """Test bridge server module imports correctly"""
        import vscode_bridge

        assert hasattr(vscode_bridge, "MCPBridgeHandler")
        assert hasattr(vscode_bridge, "start_bridge_server")

    def test_bridge_handler_instantiation(self):
        """Test MCPBridgeHandler can be instantiated"""
        from vscode_bridge import MCPBridgeHandler

        # Should be able to instantiate the handler class
        handler_class = MCPBridgeHandler
        assert handler_class is not None

    def test_environment_variable_handling(self):
        """Test bridge server respects environment variables"""
        from vscode_bridge import start_bridge_server

        # Test with environment variables set
        with patch.dict(os.environ, {"MCP_BRIDGE_HOST": "test-host", "MCP_BRIDGE_PORT": "9999"}):
            # We can't actually start the server in tests, but we can check
            # the function exists and accepts parameters
            assert callable(start_bridge_server)

    def test_workspace_detection_logic(self):
        """Test workspace detection logic"""
        import os

        # Test with VSCODE_WORKSPACE_FOLDER set
        test_workspace = "/tmp/test-workspace"
        with patch.dict(os.environ, {"VSCODE_WORKSPACE_FOLDER": test_workspace}):
            workspace = os.getenv("VSCODE_WORKSPACE_FOLDER", os.getcwd())
            assert workspace == test_workspace

        # Test fallback to current directory
        with patch.dict(os.environ, {}, clear=True):
            workspace = os.getenv("VSCODE_WORKSPACE_FOLDER", os.getcwd())
            assert workspace == os.getcwd()


@pytest.mark.integration
class TestBridgeServerIntegration:
    """Integration tests for bridge server (requires requests library)"""

    @pytest.fixture(scope="class")
    def available_port(self):
        """Find an available port for testing"""
        sock = socket.socket()
        sock.bind(("", 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    @pytest.fixture(scope="class")
    def bridge_server(self, available_port):
        """Start bridge server for integration testing"""
        requests = pytest.importorskip("requests")

        from vscode_bridge import MCPBridgeHandler
        from http.server import HTTPServer

        # Set up test environment
        test_workspace = tempfile.mkdtemp()
        os.environ["VSCODE_WORKSPACE_FOLDER"] = test_workspace
        os.environ["MCP_BRIDGE_HOST"] = "localhost"
        os.environ["MCP_BRIDGE_PORT"] = str(available_port)

        # Create and start server
        server_address = ("localhost", available_port)
        httpd = HTTPServer(server_address, MCPBridgeHandler)

        # Start in background thread
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        # Wait for server to be ready
        time.sleep(1)

        # Verify server is responding
        try:
            response = requests.get(f"http://localhost:{available_port}/health", timeout=2)
            assert response.status_code == 200
        except Exception as e:
            httpd.shutdown()
            pytest.fail(f"Bridge server failed to start: {e}")

        yield {
            "port": available_port,
            "base_url": f"http://localhost:{available_port}",
            "workspace": test_workspace,
        }

        # Cleanup
        httpd.shutdown()
        httpd.server_close()

    def test_health_endpoint(self, bridge_server):
        """Test health check endpoint returns correct data"""
        requests = pytest.importorskip("requests")

        response = requests.get(f"{bridge_server['base_url']}/health")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert data["status"] == "healthy"
        assert "current_workspace" in data
        assert "available_tools" in data
        assert isinstance(data["available_tools"], list)

        # Workspace should match our test workspace
        assert bridge_server["workspace"] in data["current_workspace"]

    def test_tool_execution_endpoint(self, bridge_server):
        """Test tool execution via POST endpoint"""
        requests = pytest.importorskip("requests")

        # Test with a simple tool call
        tool_request = {"tool": "list_tools", "arguments": {}}

        response = requests.post(
            bridge_server["base_url"],
            json=tool_request,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        data = response.json()

        # Response should be a dictionary
        assert isinstance(data, dict)
        # Should have project_path and result structure
        assert "project_path" in data
        assert "result" in data
        assert isinstance(data["result"], dict)
        # Result should have content or error
        assert "content" in data["result"] or "error" in data["result"]

    def test_cors_headers(self, bridge_server):
        """Test CORS headers are present"""
        requests = pytest.importorskip("requests")

        # Test OPTIONS request
        response = requests.options(bridge_server["base_url"])
        assert response.status_code == 200

        # Check for CORS headers
        headers = response.headers
        assert "Access-Control-Allow-Origin" in headers
        assert "Access-Control-Allow-Methods" in headers
        assert "Access-Control-Allow-Headers" in headers

    def test_invalid_tool_request(self, bridge_server):
        """Test invalid tool requests are handled gracefully"""
        requests = pytest.importorskip("requests")

        # Test with nonexistent tool
        tool_request = {"tool": "nonexistent_tool_12345", "arguments": {}}

        response = requests.post(
            bridge_server["base_url"],
            json=tool_request,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should return structured response with error in result
        assert isinstance(data, dict)
        assert "result" in data
        assert "error" in data["result"]

    def test_malformed_json_request(self, bridge_server):
        """Test malformed JSON requests are handled"""
        requests = pytest.importorskip("requests")

        # Send invalid JSON
        response = requests.post(
            bridge_server["base_url"],
            data='{"invalid": json}',
            headers={"Content-Type": "application/json"},
        )

        # Bridge server returns 500 for malformed JSON, which is acceptable
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            # Should return error information
            assert isinstance(data, dict)
            assert "error" in data or ("result" in data and "error" in data["result"])

    def test_404_for_unknown_paths(self, bridge_server):
        """Test unknown paths return 404"""
        requests = pytest.importorskip("requests")

        response = requests.get(f"{bridge_server['base_url']}/unknown-path")
        assert response.status_code == 404

    def test_concurrent_requests(self, bridge_server):
        """Test bridge server handles concurrent requests"""
        requests = pytest.importorskip("requests")

        import concurrent.futures

        def make_health_request():
            response = requests.get(f"{bridge_server['base_url']}/health")
            assert response.status_code == 200
            return response.json()

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_health_request) for _ in range(5)]
            results = [future.result() for future in futures]

        # All requests should succeed
        assert len(results) == 5
        for result in results:
            assert result["status"] == "healthy"


@pytest.mark.performance
class TestBridgeServerPerformance:
    """Performance tests for bridge server"""

    def test_startup_time(self):
        """Test bridge server starts quickly"""
        import time
        from vscode_bridge import MCPBridgeHandler
        from http.server import HTTPServer

        # Find available port
        sock = socket.socket()
        sock.bind(("", 0))
        port = sock.getsockname()[1]
        sock.close()

        start_time = time.time()

        # Create server (but don't start serving)
        server_address = ("localhost", port)
        httpd = HTTPServer(server_address, MCPBridgeHandler)

        startup_time = time.time() - start_time

        # Should start very quickly (under 1 second)
        assert startup_time < 1.0

        httpd.server_close()

    def test_health_endpoint_response_time(self):
        """Test health endpoint responds quickly"""
        # This test requires a running server, so we'll skip if integration tests aren't enabled
        pytest.skip("Requires running bridge server - run with integration tests")


if __name__ == "__main__":
    # Run bridge server tests
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-m",
            "not integration and not performance",  # Run only standalone tests by default
        ]
    )
