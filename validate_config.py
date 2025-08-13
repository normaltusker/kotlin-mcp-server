#!/usr/bin/env python3
"""
Configuration Validation Script for Kotlin MCP Server

This script validates your configuration and helps identify common setup issues.
"""

import json
import os
import sys
from pathlib import Path


def validate_path(path, description):
    """Validate a file or directory path"""
    if not path or path.startswith("${") or "your-" in path.lower():
        return False, f"❌ {description}: Contains placeholder - update with actual path"

    path_obj = Path(path)
    if not path_obj.exists():
        return False, f"❌ {description}: Path does not exist: {path}"

    return True, f"✅ {description}: {path}"


def validate_config_file(config_path):
    """Validate an MCP configuration file"""
    if not config_path.exists():
        return False, f"❌ Config file not found: {config_path}"

    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"❌ Invalid JSON in {config_path}: {e}"

    issues = []

    # Check for MCP servers
    if "mcpServers" not in config:
        issues.append("❌ Missing 'mcpServers' section")
    else:
        for server_name, server_config in config["mcpServers"].items():
            # Check cwd path
            cwd = server_config.get("cwd", "")
            if cwd.startswith("${") or "/Users/Niravthakker" in cwd:
                issues.append(f"❌ {server_name}: 'cwd' contains placeholder or hardcoded path")

            # Check command
            command = server_config.get("command", "")
            if not command:
                issues.append(f"❌ {server_name}: Missing 'command'")

            # Check args
            args = server_config.get("args", [])
            if not args:
                issues.append(f"❌ {server_name}: Missing 'args'")

    if issues:
        return False, f"❌ Issues in {config_path}:\n" + "\n".join(
            f"   {issue}" for issue in issues
        )

    return True, f"✅ Config file valid: {config_path}"


def validate_environment():
    """Validate environment variables"""
    required_vars = [
        ("WORKSPACE_PATH", "Android project workspace path"),
        ("MCP_SERVER_DIR", "MCP server directory path"),
    ]

    optional_vars = [
        ("MCP_ENCRYPTION_PASSWORD", "Encryption password"),
        ("OPENAI_API_KEY", "OpenAI API key"),
        ("ANTHROPIC_API_KEY", "Anthropic API key"),
    ]

    issues = []

    # Check required variables
    for var_name, description in required_vars:
        value = os.getenv(var_name)
        if not value:
            issues.append(f"❌ Missing required environment variable: {var_name}")
        elif value.startswith("${") or "your-" in value.lower():
            issues.append(f"❌ {var_name} contains placeholder - update with actual value")
        else:
            valid, message = validate_path(value, f"{var_name} ({description})")
            if not valid:
                issues.append(message)
            else:
                print(message)

    # Check optional variables
    for var_name, description in optional_vars:
        value = os.getenv(var_name)
        if value and not (value.startswith("${") or "your-" in value.lower()):
            print(f"✅ {var_name}: Configured")
        elif value:
            print(f"⚠️  {var_name}: Contains placeholder - update if you want to use {description}")
        else:
            print(f"ℹ️  {var_name}: Not configured (optional)")

    return len(issues) == 0, issues


def test_bridge_server():
    """Test VS Code bridge server can start and respond"""
    import socket
    import subprocess
    import time

    try:
        import requests

        # Check if bridge server file exists
        script_dir = Path(__file__).parent
        bridge_file = script_dir / "vscode_bridge.py"

        if not bridge_file.exists():
            print("   ❌ vscode_bridge.py: Not found")
            return False

        # Check if port 8080 is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("localhost", 8080))
        sock.close()

        if result == 0:
            print("   ⚠️  Port 8080 already in use - testing existing server")
            try:
                response = requests.get("http://localhost:8080/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        print("   ✅ Bridge server: Running and healthy")
                        return True
                    else:
                        print("   ❌ Bridge server: Unhealthy response")
                        return False
                else:
                    print(f"   ❌ Bridge server: HTTP {response.status_code}")
                    return False
            except Exception as e:
                print(f"   ❌ Bridge server: Health check failed - {e}")
                return False

        # Try to start bridge server temporarily
        print("   🔄 Starting bridge server for testing...")

        # Start bridge server in background
        process = subprocess.Popen(
            [sys.executable, str(bridge_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=script_dir,
        )

        # Wait for server to start
        time.sleep(3)

        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print("   ❌ Bridge server failed to start:")
            print(f"      stdout: {stdout.decode()[:100]}...")
            print(f"      stderr: {stderr.decode()[:100]}...")
            return False

        # Test health endpoint
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("   ✅ Bridge server: Successfully started and healthy")
                    success = True
                else:
                    print("   ❌ Bridge server: Started but unhealthy")
                    success = False
            else:
                print(f"   ❌ Bridge server: HTTP {response.status_code}")
                success = False
        except Exception as e:
            print(f"   ❌ Bridge server: Health check failed - {e}")
            success = False
        finally:
            # Clean up - terminate the test server
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

        return success

    except ImportError:
        print("   ⚠️  requests library not available - skipping bridge server test")
        print("   💡 Install with: pip install requests")
        return True  # Don't fail validation for missing optional dependency
    except Exception as e:
        print(f"   ❌ Bridge server test failed: {e}")
        return False


def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "pydantic",
        "python-dotenv",
        "cryptography",
        "aiosqlite",
        "aiohttp",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}: Installed")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}: Missing")

    if missing:
        print("\n💡 Install missing packages:")
        print(f"   pip install {' '.join(missing)}")

    return len(missing) == 0


def main():
    """Main validation function"""
    try:
        print("🔍 Kotlin MCP Server Configuration Validator")
        print("=" * 50)

        script_dir = Path(__file__).parent

        # Load .env file if it exists
        env_file = script_dir / ".env"
        if env_file.exists():
            print(f"📄 Loading environment from: {env_file}")
            try:
                from dotenv import load_dotenv

                load_dotenv(env_file)
                print("✅ Environment loaded")
            except ImportError:
                print("⚠️  python-dotenv not installed - environment variables may not be loaded")
        else:
            print(f"⚠️  No .env file found at: {env_file}")
            print("💡 Copy .env.example to .env and customize it")

        print("\n🐍 Checking Python Dependencies...")
        deps_ok = check_python_dependencies()

        print("\n🌍 Checking Environment Variables...")
        env_ok, env_issues = validate_environment()
        if env_issues:
            for issue in env_issues:
                print(f"   {issue}")

        print("\n📋 Checking Configuration Files...")
        config_files = [
            script_dir / "mcp_config.json",
            script_dir / "mcp_config_claude.json",
            script_dir / "mcp_config_vscode.json",
        ]

        config_ok = True
        for config_file in config_files:
            valid, message = validate_config_file(config_file)
            print(f"   {message}")
            if not valid:
                config_ok = False

        print("\n📁 Checking Server Files...")
        server_files = [
            script_dir / "kotlin_mcp_server.py",
            script_dir / "vscode_bridge.py",
        ]

        files_ok = True
        for server_file in server_files:
            if server_file.exists():
                print(f"   ✅ {server_file.name}: Found")
            else:
                print(f"   ❌ {server_file.name}: Missing")
                files_ok = False

        print("\n🌉 Testing VS Code Bridge Server...")
        bridge_ok = test_bridge_server()

        print("\n" + "=" * 50)

        # Overall status
        all_ok = deps_ok and env_ok and config_ok and files_ok and bridge_ok

        if all_ok:
            print("🎉 Configuration Validation PASSED!")
            print("\n🚀 Next Steps:")
            print("   1. Test the server: python3 kotlin_mcp_server.py --test")
            print("   2. Configure your IDE using the updated config files")
            print("   3. Start using the MCP server!")
        else:
            print("🚨 Configuration Validation FAILED!")
            print("\n🔧 Fix the issues above and run this validator again:")
            print("   python3 validate_config.py")

        print("\n📚 Resources:")
        print("   • CONFIG_TEMPLATE.md - Detailed configuration guide")
        print("   • .env.example - Example environment file")
        print("   • README.md - Complete setup instructions")

        exit_code = 0 if all_ok else 1
        return exit_code

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Only call sys.exit() if not running under pytest
    if "pytest" not in sys.modules:
        sys.exit(main())
    else:
        main()  # Call main() but don't exit for pytest
