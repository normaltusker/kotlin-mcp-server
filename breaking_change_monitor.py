#!/usr/bin/env python3
"""
Breaking Change Monitor
Monitors MCP server functionality to detect breaking changes after code enhancements
"""

import asyncio
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class BreakingChangeMonitor:
    """Monitor for breaking changes in MCP server functionality"""

    def __init__(self):
        self.baseline_file = Path("mcp_baseline.json")
        self.current_results: Dict[str, Any] = {}
        self.baseline_results: Optional[Dict[str, Any]] = None

    def load_baseline(self) -> bool:
        """Load baseline functionality snapshot"""
        if self.baseline_file.exists():
            try:
                with open(self.baseline_file, "r") as f:
                    self.baseline_results = json.load(f)
                print(f"✅ Loaded baseline from {self.baseline_file}")
                return True
            except Exception as e:
                print(f"⚠️  Could not load baseline: {e}")
                return False
        else:
            print(f"ℹ️  No baseline file found at {self.baseline_file}")
            return False

    def save_baseline(self):
        """Save current functionality as baseline"""
        try:
            with open(self.baseline_file, "w") as f:
                json.dump(self.current_results, f, indent=2)
            print(f"✅ Saved baseline to {self.baseline_file}")
        except Exception as e:
            print(f"❌ Could not save baseline: {e}")

    async def capture_server_functionality(self, server_class, server_name: str) -> Dict[str, Any]:
        """Capture current server functionality"""
        print(f"📊 Capturing {server_name} functionality...")

        try:
            # Initialize server
            server = server_class(f"monitor-{server_name}")
            server.project_path = Path(tempfile.mkdtemp())

            functionality = {
                "server_name": server_name,
                "timestamp": time.time(),
                "tools": [],
                "basic_operations": {},
                "performance_metrics": {},
            }

            # Capture tool list
            start_time = time.time()
            tools_response = await server.handle_list_tools()
            list_duration = time.time() - start_time

            tools = tools_response.get("tools", [])
            functionality["tools"] = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "has_schema": "inputSchema" in tool,
                    "required_params": tool.get("inputSchema", {}).get("required", []),
                }
                for tool in tools
            ]

            functionality["performance_metrics"]["tool_list_time"] = list_duration
            functionality["performance_metrics"]["tool_count"] = len(tools)

            # Test basic operations
            basic_tests = [
                (
                    "create_kotlin_file",
                    {
                        "file_path": "test/MonitorTest.kt",
                        "class_name": "MonitorTest",
                        "package_name": "com.test.monitor",
                        "class_type": "class",
                    },
                ),
                (
                    "create_layout_file",
                    {
                        "file_path": "res/layout/monitor_layout.xml",
                        "layout_type": "linear",
                        "components": ["button"],
                    },
                ),
            ]

            for tool_name, args in basic_tests:
                if tool_name in [tool["name"] for tool in tools]:
                    try:
                        start_time = time.time()
                        result = await server.handle_call_tool(tool_name, args)
                        duration = time.time() - start_time

                        functionality["basic_operations"][tool_name] = {
                            "success": result.get("success", False),
                            "duration": duration,
                            "has_error": "error" in result,
                        }
                    except Exception as e:
                        functionality["basic_operations"][tool_name] = {
                            "success": False,
                            "duration": 0,
                            "error": str(e),
                        }

            # Cleanup
            import shutil

            shutil.rmtree(server.project_path, ignore_errors=True)

            return functionality

        except Exception as e:
            print(f"❌ Error capturing {server_name} functionality: {e}")
            return {
                "server_name": server_name,
                "timestamp": time.time(),
                "error": str(e),
                "tools": [],
                "basic_operations": {},
                "performance_metrics": {},
            }

    async def monitor_all_servers(self) -> Dict[str, Any]:
        """Monitor all MCP server types"""
        print("🔍 Monitoring all MCP servers...")

        servers_to_test = [
            ("simple_mcp_server", "MCPServer", "Base"),
            ("enhanced_mcp_server", "EnhancedAndroidMCPServer", "Enhanced"),
            ("security_privacy_server", "SecurityPrivacyMCPServer", "Security"),
            ("ai_integration_server", "AIIntegratedMCPServer", "AI"),
        ]

        all_results = {"monitoring_timestamp": time.time(), "servers": {}}

        for module_name, class_name, display_name in servers_to_test:
            try:
                # Import server class
                module = __import__(module_name)
                server_class = getattr(module, class_name)

                # Capture functionality
                functionality = await self.capture_server_functionality(server_class, display_name)
                all_results["servers"][display_name] = functionality

            except Exception as e:
                print(f"❌ Failed to test {display_name} server: {e}")
                all_results["servers"][display_name] = {
                    "server_name": display_name,
                    "error": str(e),
                    "timestamp": time.time(),
                }

        return all_results

    def compare_functionality(self) -> List[str]:
        """Compare current functionality with baseline"""
        if not self.baseline_results:
            return ["No baseline available for comparison"]

        issues = []

        for server_name in self.baseline_results.get("servers", {}):
            baseline_server = self.baseline_results["servers"][server_name]
            current_server = self.current_results["servers"].get(server_name, {})

            if not current_server:
                issues.append(f"❌ {server_name} server is missing")
                continue

            if "error" in current_server:
                issues.append(f"❌ {server_name} server has errors: {current_server['error']}")
                continue

            # Compare tool counts
            baseline_tools = len(baseline_server.get("tools", []))
            current_tools = len(current_server.get("tools", []))

            if current_tools < baseline_tools:
                issues.append(
                    f"❌ {server_name}: Tool count decreased from {baseline_tools} to {current_tools}"
                )

            # Compare tool names
            baseline_tool_names = {tool["name"] for tool in baseline_server.get("tools", [])}
            current_tool_names = {tool["name"] for tool in current_server.get("tools", [])}

            missing_tools = baseline_tool_names - current_tool_names
            if missing_tools:
                issues.append(f"❌ {server_name}: Missing tools: {', '.join(missing_tools)}")

            # Compare basic operations
            baseline_ops = baseline_server.get("basic_operations", {})
            current_ops = current_server.get("basic_operations", {})

            for op_name, baseline_result in baseline_ops.items():
                if op_name not in current_ops:
                    issues.append(f"❌ {server_name}: Operation '{op_name}' is missing")
                    continue

                current_result = current_ops[op_name]

                if baseline_result.get("success") and not current_result.get("success"):
                    issues.append(
                        f"❌ {server_name}: Operation '{op_name}' was working but now fails"
                    )

                # Performance regression check (50% slowdown threshold)
                baseline_duration = baseline_result.get("duration", 0)
                current_duration = current_result.get("duration", 0)

                if baseline_duration > 0 and current_duration > baseline_duration * 1.5:
                    issues.append(
                        f"⚠️  {server_name}: Operation '{op_name}' is 50%+ slower ({current_duration:.3f}s vs {baseline_duration:.3f}s)"
                    )

        return issues

    def generate_report(self, issues: List[str]) -> bool:
        """Generate monitoring report"""
        print("\n" + "=" * 80)
        print("BREAKING CHANGE MONITORING REPORT")
        print("=" * 80)

        if not issues:
            print("🎉 NO BREAKING CHANGES DETECTED!")
            print("\nAll MCP server functionality is preserved:")

            for server_name, server_data in self.current_results["servers"].items():
                if "error" not in server_data:
                    tool_count = len(server_data.get("tools", []))
                    print(f"  ✅ {server_name}: {tool_count} tools available")

            return True
        else:
            print("🚨 BREAKING CHANGES DETECTED!")
            print(f"\nFound {len(issues)} issues:")

            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")

            print("\n🔧 Recommendations:")
            print("  • Review recent code changes")
            print("  • Check if tools were intentionally removed/modified")
            print("  • Run full test suite to identify specific failures")
            print("  • Consider reverting breaking changes")

            return False

    async def run_monitoring(self, update_baseline: bool = False) -> bool:
        """Run complete monitoring pipeline"""
        print("🚀 Starting MCP Server Breaking Change Monitor")
        print("=" * 60)

        # Capture current functionality
        self.current_results = await self.monitor_all_servers()

        if update_baseline:
            self.save_baseline()
            print("✅ Baseline updated successfully!")
            return True

        # Load and compare with baseline
        if not self.load_baseline():
            print("ℹ️  No baseline available. Creating initial baseline...")
            self.save_baseline()
            print("✅ Initial baseline created. Run again to detect changes.")
            return True

        # Compare functionality
        issues = self.compare_functionality()

        # Generate report
        success = self.generate_report(issues)

        # Save current results for future comparison
        self.save_baseline()

        return success


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor MCP server for breaking changes")
    parser.add_argument(
        "--update-baseline", action="store_true", help="Update the baseline instead of comparing"
    )

    args = parser.parse_args()

    monitor = BreakingChangeMonitor()
    success = await monitor.run_monitoring(update_baseline=args.update_baseline)

    if success:
        print("\n✅ Monitoring completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Breaking changes detected!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
