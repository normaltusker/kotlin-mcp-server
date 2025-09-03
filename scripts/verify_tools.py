#!/usr/bin/env python3
"""
Tool Verification Script for Kotlin MCP Server

Validates tool registry against schema, detects duplicates, placeholders,
and import errors. Ensures VS Code sees the same tools as the server.
"""

import argparse
import importlib.util
import inspect
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Try to import jsonschema, but don't fail if not available
try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Known placeholder/stub fragments that indicate incomplete tools
BAD_FRAGMENTS = {
    "setup_room_database",
    "setup_retrofit_api",
    "intelligent_refactoring_suggestions",
    "symbol_navigation_index",
    "security_tools_variations",
    "analyze_and_refactor_project",
    "demo output",
    "example output",
    "placeholder",
    "not implemented",
    "coming soon",
    "under construction",
    "lorem ipsum",
    "sample data",
    "test data",
    "mock response",
    "dummy content",
    "fake data",
    "todo:",
    "tbd:",
    "fixme:",
    "hack:",
    "notimplementederror",
}


class ToolVerifier:
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.schema_path = PROJECT_ROOT / "schema" / "mcp-tools.schema.json"
        self.main_server_path = PROJECT_ROOT / "kotlin_mcp_server.py"

        # Load schema
        try:
            with open(self.schema_path) as f:
                self.schema = json.load(f)
        except Exception as e:
            self.error(f"Failed to load schema: {e}")
            self.schema = {}

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
        """Extract tools from the main server file"""
        try:
            # Import the server module
            spec = importlib.util.spec_from_file_location(
                "kotlin_mcp_server", self.main_server_path
            )
            if spec is None or spec.loader is None:
                self.error("Failed to create module spec")
                return []

            server_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(server_module)

            # Create an instance and get tools
            server_class = getattr(server_module, "KotlinMCPServerV2")
            server_instance = server_class()

            # Call handle_list_tools to get the tools
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
            self.error(f"Failed to import server tools: {e}")
            return []

    def validate_tool_schema(self, tool: Dict[str, Any]) -> bool:
        """Validate a single tool against the schema"""
        tool_name = tool.get("name", "unknown")

        # Check if tool has required fields
        required_fields = ["name", "description", "inputSchema"]
        missing_fields = [field for field in required_fields if field not in tool]

        if missing_fields:
            self.error(f"Tool '{tool_name}' missing required fields: {missing_fields}")
            return False

        # Validate input schema structure
        input_schema = tool.get("inputSchema", {})
        if not isinstance(input_schema, dict):
            self.error(f"Tool '{tool_name}' has invalid inputSchema type")
            return False

        # Check if input schema has proper structure
        if input_schema.get("type") != "object":
            self.warn(f"Tool '{tool_name}' inputSchema should have type 'object'")

        if "properties" not in input_schema:
            self.warn(f"Tool '{tool_name}' inputSchema missing 'properties'")

        # Validate against main schema if tool is defined there
        if tool_name in self.schema.get("properties", {}):
            try:
                tool_schema = self.schema["properties"][tool_name]
                input_def = tool_schema.get("properties", {}).get("input", {})

                # Compare schemas (basic validation)
                if input_def and input_schema:
                    schema_props = input_def.get("properties", {})
                    tool_props = input_schema.get("properties", {})

                    # Check for property mismatches
                    schema_keys = set(schema_props.keys())
                    tool_keys = set(tool_props.keys())

                    missing_in_tool = schema_keys - tool_keys
                    extra_in_tool = tool_keys - schema_keys

                    if missing_in_tool:
                        self.warn(
                            f"Tool '{tool_name}' missing schema properties: {missing_in_tool}"
                        )
                    if extra_in_tool:
                        self.warn(f"Tool '{tool_name}' has extra properties: {extra_in_tool}")

            except Exception as e:
                self.warn(f"Schema validation failed for '{tool_name}': {e}")

        return True

    def check_for_placeholders(self, tool: Dict[str, Any]) -> bool:
        """Check if tool contains placeholder content"""
        tool_name = tool.get("name", "unknown")
        tool_str = json.dumps(tool, ensure_ascii=False).lower()

        found_placeholders = []
        for fragment in BAD_FRAGMENTS:
            if fragment.lower() in tool_str:
                found_placeholders.append(fragment)

        if found_placeholders:
            self.error(f"Tool '{tool_name}' contains placeholder fragments: {found_placeholders}")
            return False

        return True

    def check_handler_imports(self, tool: Dict[str, Any]) -> bool:
        """Check if tool handler can be imported and called"""
        tool_name = tool.get("name", "unknown")

        # For now, we check if the tool is properly handled in the main server
        # by looking for its handler method
        try:
            with open(self.main_server_path, "r") as f:
                server_content = f.read()

            # Look for tool handler patterns
            handler_patterns = [
                f'elif name == "{tool_name}":',
                f'if name == "{tool_name}":',
                f"handle_{tool_name.lower()}",
                f'"{tool_name}":',
            ]

            found_handler = any(pattern in server_content for pattern in handler_patterns)

            if not found_handler:
                self.warn(f"Tool '{tool_name}' may not have a handler implementation")
                return False

        except Exception as e:
            self.warn(f"Failed to check handler for '{tool_name}': {e}")
            return False

        return True

    def detect_duplicates(self, tools: List[Dict[str, Any]]) -> Set[str]:
        """Detect duplicate tool names"""
        names = [tool.get("name", "") for tool in tools]
        seen = set()
        duplicates = set()

        for name in names:
            if name in seen:
                duplicates.add(name)
            seen.add(name)

        if duplicates:
            self.error(f"Duplicate tool names found: {duplicates}")

        return duplicates

    def run_server_list_tools(self) -> List[str]:
        """Run the server with --list-tools flag to get dynamic tool list"""
        try:
            cmd = [sys.executable, str(self.main_server_path), "--list-tools"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                self.warn(f"Server --list-tools failed: {result.stderr}")
                return []

            # Parse the output to extract tool names
            output_lines = result.stdout.strip().split("\n")
            tool_names = []

            for line in output_lines:
                line = line.strip()
                if line and not line.startswith("INFO") and not line.startswith("DEBUG"):
                    # Try to extract tool name from various formats
                    if ":" in line:
                        parts = line.split(":")
                        potential_name = parts[0].strip()
                        if potential_name and " " not in potential_name:
                            tool_names.append(potential_name)
                    elif line and " " not in line and len(line) < 50:
                        tool_names.append(line)

            return tool_names

        except Exception as e:
            self.warn(f"Failed to run server --list-tools: {e}")
            return []

    def verify(self, print_tools: bool = False) -> bool:
        """Main verification function"""
        self.info("Starting tool verification...")

        # Get tools from server
        tools = self.get_server_tools()
        if not tools:
            self.error("No tools found in server")
            return False

        self.ok(f"{len(tools)} tools registered in server")

        if print_tools:
            print("\n📋 Registered Tools:")
            for i, tool in enumerate(tools, 1):
                name = tool.get("name", "unknown")
                desc = tool.get("description", "No description")[:60]
                print(f"{i:2d}. {name} - {desc}...")

        # Check for duplicates
        duplicates = self.detect_duplicates(tools)
        if not duplicates:
            self.ok("No duplicate tool names")

        # Validate schemas
        schema_valid = True
        for tool in tools:
            if not self.validate_tool_schema(tool):
                schema_valid = False

        if schema_valid:
            self.ok("All tool schemas are valid")

        # Check for placeholders
        placeholder_free = True
        for tool in tools:
            if not self.check_for_placeholders(tool):
                placeholder_free = False

        if placeholder_free:
            self.ok("No placeholder content found")

        # Check handler imports
        handlers_valid = True
        for tool in tools:
            if not self.check_handler_imports(tool):
                handlers_valid = False

        # Compare with dynamic tool list
        dynamic_tools = self.run_server_list_tools()
        if dynamic_tools:
            static_names = {tool.get("name") for tool in tools}
            dynamic_names = set(dynamic_tools)

            missing_in_dynamic = static_names - dynamic_names
            extra_in_dynamic = dynamic_names - static_names

            if missing_in_dynamic:
                self.warn(f"Tools in registry but not in --list-tools: {missing_in_dynamic}")
            if extra_in_dynamic:
                self.warn(f"Tools in --list-tools but not in registry: {extra_in_dynamic}")

            if not missing_in_dynamic and not extra_in_dynamic:
                self.ok("Static and dynamic tool lists match")

        # Summary
        print(f"\n📊 Verification Summary:")
        print(f"   Tools found: {len(tools)}")
        print(f"   Errors: {len(self.errors)}")
        print(f"   Warnings: {len(self.warnings)}")

        if self.errors:
            print(f"\n🔥 Errors:")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        # Return success status
        has_critical_issues = bool(self.errors)
        if self.strict_mode:
            has_critical_issues = has_critical_issues or bool(self.warnings)

        if has_critical_issues:
            print(f"\n❌ Verification FAILED")
            return False
        else:
            print(f"\n✅ Verification PASSED")
            return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify MCP tool registry")
    parser.add_argument("--print", action="store_true", help="Print list of all tools")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()

    verifier = ToolVerifier(strict_mode=args.strict)
    success = verifier.verify(print_tools=args.print)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
