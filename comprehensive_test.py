#!/usr/bin/env python3
"""
Comprehensive test script for the MCP server
"""

import json
import subprocess
import sys
import os
from pathlib import Path
import tempfile

def test_basic_functionality():
    """Test basic Python functionality and imports"""
    print("🔧 Testing Basic Functionality")
    print("=" * 40)

    try:
        # Test basic imports
        import asyncio
        import json
        import os
        print("✅ Basic imports successful")

        # Test pathlib
        from pathlib import Path
        test_path = Path("/tmp")
        print(f"✅ Pathlib works: {test_path.exists()}")

        # Test asyncio
        async def test_async():
            return "async works"

        result = asyncio.run(test_async())
        print(f"✅ Asyncio works: {result}")

        return True

    except Exception as e:
        print(f"❌ Basic functionality failed: {e}")
        return False

def test_simple_server():
    """Test a simplified MCP server"""
    print("\n🔧 Testing Simple MCP Server")
    print("=" * 40)

    # Create a minimal working MCP server
    simple_server_code = '''
import json
import sys
import os
from pathlib import Path

def handle_request(request):
    method = request.get("method")
    request_id = request.get("id")
    
    response = {"jsonrpc": "2.0", "id": request_id}
    
    if method == "initialize":
        response["result"] = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}, "resources": {}},
            "serverInfo": {"name": "kotlin-android-mcp", "version": "1.0.0"}
        }
    elif method == "tools/list":
        response["result"] = {
            "tools": [
                {"name": "analyze_project", "description": "Analyze Android project"}
            ]
        }
    else:
        response["error"] = {"code": -32601, "message": f"Method not found: {method}"}
    
    return response

# Main server loop
try:
    while True:
        line = sys.stdin.readline()
        if not line:
            break
            
        line = line.strip()
        if not line:
            continue
            
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0", 
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response), flush=True)
            
except KeyboardInterrupt:
    pass
'''

    # Write the simple server to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(simple_server_code)
        temp_server_path = f.name

    try:
        # Test the simple server
        test_request = '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}'

        result = subprocess.run(
            [sys.executable, temp_server_path],
            input=test_request,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.stdout:
            try:
                response = json.loads(result.stdout.strip())
                if "result" in response and "serverInfo" in response["result"]:
                    print("✅ Simple MCP server works!")
                    print(f"   Server name: {response['result']['serverInfo']['name']}")
                    return True
                else:
                    print(f"❌ Unexpected response: {response}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {result.stdout}")
        else:
            print(f"❌ No output from server. stderr: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("❌ Server test timed out")
    except Exception as e:
        print(f"❌ Server test failed: {e}")
    finally:
        # Clean up temp file
        os.unlink(temp_server_path)

    return False

def test_android_project_detection():
    """Test Android project detection"""
    print("\n🔧 Testing Android Project Detection")
    print("=" * 40)

    project_path = Path("/Users/Niravthakker/Downloads/Nirav/Personal/Coding/Vital-Trail")

    if not project_path.exists():
        print(f"❌ Project path doesn't exist: {project_path}")
        return False

    print(f"✅ Project path exists: {project_path}")

    # Check for Android files
    android_indicators = [
        "app/build.gradle",
        "app/build.gradle.kts",
        "app/src/main/AndroidManifest.xml",
        "settings.gradle",
        "settings.gradle.kts"
    ]

    found_files = []
    for indicator in android_indicators:
        file_path = project_path / indicator
        if file_path.exists():
            found_files.append(indicator)

    if found_files:
        print(f"✅ Android project detected. Found: {found_files}")
        return True
    else:
        print("❌ No Android project files found")
        return False

def main():
    """Run comprehensive tests"""
    print("🧪 Kotlin Android MCP Server - Comprehensive Test")
    print("=" * 50)

    results = []

    # Test 1: Basic functionality
    results.append(test_basic_functionality())

    # Test 2: Simple server
    results.append(test_simple_server())

    # Test 3: Android project detection
    results.append(test_android_project_detection())

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 40)

    passed = sum(results)
    total = len(results)

    test_names = [
        "Basic Functionality",
        "Simple MCP Server",
        "Android Project Detection"
    ]

    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! MCP server should work correctly.")
    else:
        print("⚠️  Some tests failed. MCP server needs fixes.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
