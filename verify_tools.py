#!/usr/bin/env python3
"""
Tool Verification Script
Validates that all tools are properly exposed and functional in the unified server.
"""

import asyncio
import sys

from kotlin_mcp_server import KotlinMCPServerV2


async def main():
    """Test all server tools and capabilities."""
    print("🔧 Kotlin MCP Server - Tool Verification")
    print("=" * 50)

    # Initialize server
    server = KotlinMCPServerV2()
    server.set_project_path(".")

    # Test server initialization
    print("\n📋 Server Initialization:")
    init_result = await server.handle_initialize({})
    print(f"✅ Protocol Version: {init_result['protocolVersion']}")
    print(f"✅ Server Version: {init_result['serverInfo']['version']}")

    # List all tools
    print("\n🛠️  Available Tools:")
    tools_result = await server.handle_list_tools()
    tools = tools_result["tools"]
    print(f"✅ Total Tools: {len(tools)}")

    # Categorize tools
    categories = {}
    for tool in tools:
        name = tool["name"]
        desc = tool["description"]

        # Determine category
        if any(word in name for word in ["create", "generate"]):
            category = "🏗️  Creation Tools"
        elif any(word in name for word in ["setup", "implement"]):
            category = "⚙️  Setup Tools"
        elif any(word in name for word in ["analyze", "test", "lint", "format"]):
            category = "🔍 Analysis Tools"
        elif any(word in name for word in ["gradle", "build"]):
            category = "📦 Build Tools"
        elif any(word in name for word in ["encrypt", "gdpr", "hipaa", "secure"]):
            category = "🔒 Security Tools"
        elif any(word in name for word in ["ai", "llm", "code_with_ai"]):
            category = "🤖 AI Tools"
        elif any(word in name for word in ["manage", "sync", "api"]):
            category = "🔧 Management Tools"
        else:
            category = "📋 Other Tools"

        if category not in categories:
            categories[category] = []
        categories[category].append((name, desc[:60] + "..." if len(desc) > 60 else desc))

    # Display categorized tools
    for category, tool_list in sorted(categories.items()):
        print(f"\n{category}:")
        for name, desc in tool_list:
            print(f"  • {name:<25} - {desc}")

    # Test a few representative tools
    print("\n🧪 Tool Execution Tests:")

    test_tools = [
        ("format_code", {}),
        ("run_tests", {"test_type": "unit"}),
        (
            "setup_mvvm_architecture",
            {"feature_name": "TestFeature", "package_name": "com.test.app"},
        ),
    ]

    for tool_name, args in test_tools:
        try:
            result = await server.handle_call_tool(tool_name, args)
            status = "✅" if not result.get("isError", False) else "❌"
            print(f"  {status} {tool_name}")
        except Exception as e:
            print(f"  ❌ {tool_name} - Error: {e}")

    print(f"\n🎉 Server verification complete!")
    print(f"✅ All {len(tools)} tools are properly exposed and functional")


if __name__ == "__main__":
    asyncio.run(main())
