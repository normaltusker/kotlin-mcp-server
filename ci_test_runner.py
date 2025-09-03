#!/usr/bin/env python3
"""
Continuous Integration Test Runner
Runs comprehensive tests and lint checks to ensure code quality
"""

import shlex
import subprocess
import sys
from pathlib import Path


class CITestRunner:
    """Continuous Integration test runner"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.failed_checks = []

    def run_command(self, command, description):
        """Run a command and report results"""
        print(f"\n{'=' * 60}")
        print(f"Running: {description}")
        print(f"Command: {command}")
        print(f"{'=' * 60}")

        try:
            command_list = shlex.split(command)

            # Security: validate command executables
            allowed_commands = [
                "python3",
                "python",
                "pytest",
                "black",
                "flake8",
                "pip",
                "coverage",
                "isort",
                "pylint",
                "mypy",
                "bandit",
            ]
            if command_list[0] not in allowed_commands:
                print(f"❌ {description} - BLOCKED: Unauthorized command: {command_list[0]}")
                self.failed_checks.append(f"{description} (blocked)")
                return False

            result = subprocess.run(
                command_list,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,
                shell=False,
            )

            if result.returncode == 0:
                print(f"✅ {description} - PASSED")
                if result.stdout:
                    print("Output:", result.stdout[:500])
                return True
            else:
                print(f"❌ {description} - FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                self.failed_checks.append(description)
                return False

        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT")
            self.failed_checks.append(f"{description} (timeout)")
            return False
        except Exception as e:
            print(f"❌ {description} - ERROR: {e}")
            self.failed_checks.append(f"{description} (error)")
            return False

    def check_dependencies(self):
        """Check required dependencies"""
        print("🔍 Checking dependencies...")

        required_packages = [
            "pytest",
            "pytest_asyncio",
            "pytest_cov",
            "flake8",
            "black",
            "isort",
            "psutil",
        ]

        missing = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} - available")
            except ImportError:
                print(f"❌ {package} - missing")
                missing.append(package)

        if missing:
            print(f"❌ Missing packages: {missing}")
            return False
        return True

    def run_tests(self):
        """Run the test suite"""
        print("\n🧪 Running Test Suite")

        test_commands = [
            ("python3 -m pytest tests/ -v --tb=short", "Core test suite"),
            ("python3 -m pytest tests/test_server_core.py -v", "Server core tests"),
            ("python3 -m pytest tests/ai/ -v", "AI integration tests"),
            ("python3 -m pytest tests/tools/ -v", "Tools tests"),
        ]

        all_passed = True
        for command, description in test_commands:
            if not self.run_command(command, description):
                all_passed = False

        return all_passed

    def run_quality_checks(self):
        """Run code quality checks"""
        print("\n🔍 Running Code Quality Checks")

        quality_commands = [
            (
                "python3 -m black --check --diff . --exclude htmlcov --exclude __pycache__ --exclude .git --exclude archive",
                "Black formatting check",
            ),
            (
                "python3 -m isort --check-only --diff . --skip htmlcov --skip __pycache__ --skip archive",
                "Import sorting check",
            ),
            (
                "python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=htmlcov,__pycache__,.git,archive",
                "Flake8 linting",
            ),
        ]

        all_passed = True
        for command, description in quality_commands:
            if not self.run_command(command, description):
                all_passed = False

        return all_passed

    def run_server_validation(self):
        """Run server validation"""
        print("\n🖥️ Running Server Validation")

        validation_script = """
import asyncio
import tempfile
from kotlin_mcp_server import KotlinMCPServer

async def validate():
    try:
        print("🔍 Testing server initialization...")
        server = KotlinMCPServer("ci-test")
        server.set_project_path(tempfile.mkdtemp())

        print("🔍 Testing tool listing...")
        tools = await server.handle_list_tools()
        tool_count = len(tools.get("tools", []))
        print(f"✅ Server has {tool_count} tools")

        print("🔍 Testing tool execution...")
        result = await server.handle_call_tool("create_kotlin_file", {
            "file_path": "test/TestClass.kt",
            "package_name": "com.test",
            "class_name": "TestClass",
            "class_type": "class"
        })
        assert "content" in result
        print("✅ Tool execution successful")

        print("🎉 Server validation completed successfully")

    except Exception as e:
        print(f"❌ Server validation failed: {e}")
        raise

asyncio.run(validate())
"""

        try:
            result = subprocess.run(
                [sys.executable, "-c", validation_script],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                print("✅ Server validation - PASSED")
                print(result.stdout)
                return True
            else:
                print("❌ Server validation - FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                self.failed_checks.append("Server validation")
                return False

        except Exception as e:
            print(f"❌ Server validation - ERROR: {e}")
            self.failed_checks.append("Server validation (error)")
            return False

    def run_all(self):
        """Run all CI checks"""
        print("🚀 Starting CI Test Runner")
        print(f"Project root: {self.project_root}")

        all_passed = True

        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependency check failed")
            return False

        # Run quality checks
        if not self.run_quality_checks():
            all_passed = False

        # Run tests
        if not self.run_tests():
            all_passed = False

        # Run server validation
        if not self.run_server_validation():
            all_passed = False

        # Final report
        print(f"\n{'=' * 60}")
        print("CI TEST RUNNER SUMMARY")
        print(f"{'=' * 60}")

        if all_passed:
            print("🎉 ALL CHECKS PASSED!")
            return True
        else:
            print(f"❌ {len(self.failed_checks)} CHECKS FAILED:")
            for check in self.failed_checks:
                print(f"  - {check}")
            return False


def main():
    """Main entry point"""
    runner = CITestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
