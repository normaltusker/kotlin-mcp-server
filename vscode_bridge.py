#!/usr/bin/env python3
"""
VS Code Extension Bridge for MCP Server
This creates a simple HTTP API that VS Code extensions can call
"""

import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer


class MCPBridgeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)

        try:
            request_data = json.loads(post_data)
            tool_name = request_data.get("tool")
            arguments = request_data.get("arguments", {})

            # Get project path from request or use VS Code workspace
            project_path = request_data.get("project_path")
            if not project_path:
                # Try to get from VS Code workspace environment
                project_path = os.getenv("VSCODE_WORKSPACE_FOLDER")
            if not project_path:
                # Fallback to current working directory
                project_path = os.getcwd()

            # Call the MCP server
            result = self.call_mcp_tool(tool_name, arguments, project_path)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            response = {"result": result, "project_path": project_path}
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())

    def do_GET(self):
        """Health check and project info endpoint"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            # Return current workspace info
            workspace_info = {
                "status": "healthy",
                "current_workspace": os.getenv("VSCODE_WORKSPACE_FOLDER", os.getcwd()),
                "available_tools": [
                    "gradle_build",
                    "run_tests",
                    "create_kotlin_file",
                    "create_layout_file",
                    "analyze_project",
                ],
            }

            self.wfile.write(json.dumps(workspace_info).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def call_mcp_tool(self, tool_name, arguments, project_path):
        """Call the MCP server tool via command line with security validation"""

        # Validate project_path to prevent command injection
        try:
            from pathlib import Path

            validated_path = Path(project_path).resolve()

            # Basic security checks
            if not validated_path.exists():
                return {"error": f"Project path does not exist: {project_path}"}

            if not validated_path.is_dir():
                return {"error": f"Project path is not a directory: {project_path}"}

            # Convert back to string for subprocess
            safe_project_path = str(validated_path)

        except (OSError, ValueError) as e:
            return {"error": f"Invalid project path: {e}"}

        # Validate tool_name to prevent injection
        if not tool_name.replace("_", "").replace("-", "").isalnum():
            return {"error": f"Invalid tool name: {tool_name}"}

        cmd = ["kotlin-android-mcp", safe_project_path]

        # Create a mock JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        try:
            # Set environment variable for the subprocess
            env = os.environ.copy()
            env["PROJECT_PATH"] = safe_project_path

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                shell=False,  # Explicitly disable shell execution
            )

            stdout, stderr = process.communicate(json.dumps(request), timeout=30)

            if process.returncode == 0:
                response = json.loads(stdout)
                return response.get("result", {})
            else:
                return {"error": stderr}

        except subprocess.TimeoutExpired:
            process.kill()
            return {"error": "Command timeout"}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {e}"}
        except Exception as e:
            return {"error": str(e)}


def start_bridge_server(port=8080):
    """Start the HTTP bridge server"""
    host = os.getenv("MCP_BRIDGE_HOST", "localhost")
    port = int(os.getenv("MCP_BRIDGE_PORT", port))

    server_address = (host, port)
    httpd = HTTPServer(server_address, MCPBridgeHandler)

    print(f"🌐 MCP Bridge Server running on http://{host}:{port}")
    print("📁 Workspace-aware Android MCP bridge for VS Code")
    print(f"🔍 Health check: http://{host}:{port}/health")
    print("\n📋 Usage in VS Code extension:")
    print(f"   POST http://{host}:{port}/ with JSON: {{tool: 'tool_name', arguments: {{...}}}}")
    print("   The bridge will automatically use the current VS Code workspace")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Bridge server stopped")


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_bridge_server(port)
