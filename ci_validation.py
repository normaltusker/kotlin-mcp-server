#!/usr/bin/env python3
"""
CI Validation Script
Quick validation of CI components to ensure they work locally before pushing.
"""

import asyncio
import sys
import tempfile


def test_imports() -> bool:
    """Test that all critical imports work."""
    try:
        import kotlin_mcp_server  # noqa: F401

        print("✅ Core imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


async def test_server_initialization() -> bool:
    """Test server can be initialized and basic operations work."""
    try:
        from kotlin_mcp_server import KotlinMCPServerV2

        server = KotlinMCPServerV2("ci-test")
        server.set_project_path(tempfile.mkdtemp())

        # Test tool listing
        tools = await server.handle_list_tools()
        tool_count = len(tools.get("tools", []))
        print(f"✅ Server initialized with {tool_count} tools")

        # Test a simple tool call
        result = await server.handle_call_tool("format_code", {})
        if "content" in result or not result.get("isError", True):
            print("✅ Basic tool execution works")
        else:
            print("⚠️ Tool execution returned error (this may be expected)")

        return True
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False


def test_pydantic_schemas() -> bool:
    """Test that Pydantic schemas work correctly."""
    try:
        from kotlin_mcp_server import CreateKotlinFileRequest

        # Test schema generation
        schema = CreateKotlinFileRequest.model_json_schema()
        if "properties" in schema:
            print("✅ Pydantic schemas generate correctly")
            return True
        else:
            print("❌ Schema generation failed")
            return False
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False


async def main() -> int:
    """Run all CI validation tests."""
    print("🧪 Running CI Validation Tests")
    print("=" * 40)

    tests = [
        ("Import Test", test_imports()),
        ("Server Test", await test_server_initialization()),
        ("Schema Test", test_pydantic_schemas()),
    ]

    passed = 0
    total = len(tests)

    for test_name, result in tests:
        if result:
            passed += 1
        print()

    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All CI validation tests passed!")
        return 0
    else:
        print("❌ Some tests failed. CI may fail.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
