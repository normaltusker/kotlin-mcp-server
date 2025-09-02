#!/usr/bin/env python3
"""
VS Code Parity Check for Kotlin MCP Server

Simulates VS Code's tool filtering to ensure the same tools are visible
in both the server registry and VS Code's "Configure Tools" interface.
"""

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class VSCodeParityChecker:
    def __init__(self) -> None:
        self.main_server_path = PROJECT_ROOT / "kotlin_mcp_server.py"
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)
        print(f"❌ ERROR: {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)
        print(f"⚠️  WARN: {msg}")

    def info(self, msg: str) -> None:
        print(f"ℹ️  {msg}")

    def ok(self, msg: str) -> None:
        print(f"✅ OK: {msg}")

    def get_server_tools(self) -> List[Dict[str, Any]]:
        """Get tools from the server registry"""
        try:
            spec = importlib.util.spec_from_file_location(
                "kotlin_mcp_server", self.main_server_path
            )
            if spec is None or spec.loader is None:
                self.error("Failed to create module spec")
                return []

            server_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(server_module)

            server_class = getattr(server_module, "KotlinMCPServerV2")
            server_instance = server_class()

            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                tools_response = loop.run_until_complete(server_instance.handle_list_tools())
                tools = tools_response.get("tools", [])
                return tools if isinstance(tools, list) else []
            finally:
                loop.close()

        except Exception as e:
            self.error(f"Failed to get server tools: {e}")
            return []

    def simulate_vscode_filtering(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simulate how VS Code filters and validates tools"""
        filtered_tools = []
        seen_names = set()

        for tool in tools:
            tool_name = tool.get("name", "")

            # Skip tools without names
            if not tool_name:
                self.warn("Skipping tool without name")
                continue

            # Skip duplicate names (VS Code dedupe)
            if tool_name in seen_names:
                self.warn(f"Skipping duplicate tool: {tool_name}")
                continue
            seen_names.add(tool_name)

            # VS Code validation checks
            if not self.validate_tool_for_vscode(tool):
                self.warn(f"Skipping invalid tool: {tool_name}")
                continue

            filtered_tools.append(tool)

        return filtered_tools

    def validate_tool_for_vscode(self, tool: Dict[str, Any]) -> bool:
        """Validate tool as VS Code would"""
        tool_name = tool.get("name", "")

        # Check required fields
        if not tool.get("description"):
            self.warn(f"Tool '{tool_name}' missing description")
            return False

        # Check input schema
        input_schema = tool.get("inputSchema", {})
        if not isinstance(input_schema, dict):
            self.warn(f"Tool '{tool_name}' has invalid inputSchema")
            return False

        # Basic schema validation
        if input_schema.get("type") != "object":
            self.warn(f"Tool '{tool_name}' inputSchema should be type 'object'")
            return False

        # Check for empty or malformed schemas
        if not input_schema.get("properties") and input_schema.get("required"):
            self.warn(f"Tool '{tool_name}' has required fields but no properties")
            return False

        return True

    def check_parity(self) -> bool:
        """Main parity check function"""
        self.info("Starting VS Code parity check...")

        # Get server tools
        server_tools = self.get_server_tools()
        if not server_tools:
            self.error("No tools found in server")
            return False

        self.ok(f"Found {len(server_tools)} tools in server registry")

        # Simulate VS Code filtering
        vscode_tools = self.simulate_vscode_filtering(server_tools)

        # Report results
        server_names = {tool.get("name") for tool in server_tools}
        vscode_names = {tool.get("name") for tool in vscode_tools}

        hidden_tools = server_names - vscode_names

        print("\n📊 Parity Check Results:")
        print(f"   Server tools: {len(server_tools)}")
        print(f"   VS Code visible: {len(vscode_tools)}")
        print(f"   Hidden by VS Code: {len(hidden_tools)}")

        if hidden_tools:
            print("\n🔍 Tools hidden by VS Code:")
            for tool_name in sorted(name for name in hidden_tools if name):
                print(f"   • {tool_name}")

        # List tools that would be visible in VS Code
        print("\n📋 Tools visible in VS Code:")
        for i, tool in enumerate(sorted(vscode_tools, key=lambda x: x.get("name", "")), 1):
            name = tool.get("name", "unknown")
            desc = tool.get("description", "No description")[:50]
            print(f"   {i:2d}. {name} - {desc}...")

        # Summary
        if self.errors:
            print("\n🔥 Errors:")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        # Determine success
        is_success = len(server_tools) == len(vscode_tools) and not self.errors

        if is_success:
            self.ok("VS Code parity check PASSED - all tools would be visible")
        else:
            self.error("VS Code parity check FAILED - some tools would be hidden")

        return is_success


def main() -> None:
    parser = argparse.ArgumentParser(description="Check VS Code tool visibility parity")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    _ = parser.parse_args()  # Parse args but don't use them yet

    checker = VSCodeParityChecker()
    success = checker.check_parity()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
