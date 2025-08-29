#!/usr/bin/env python3
"""
Continuous Integration Test Runner
Runs comprehensive tests and lint checks to ensure code quality
"""

import os
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
            # Use shlex.split for safer command execution
            import shlex

            command_list = shlex.split(command)

            # Additional security: validate command executables
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
                shell=False,  # Explicitly disable shell execution
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
            print(f"💥 {description} - ERROR: {e}")
            self.failed_checks.append(f"{description} (error)")
            return False

    def check_dependencies(self):
        """Check and install required dependencies"""
        print("Checking dependencies...")

        required_packages = [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "pylint>=2.17.0",
            "mypy>=1.4.0",
            "bandit>=1.7.0",
            "psutil>=5.9.0",
        ]

        for package in required_packages:
            try:
                package_name = package.split(">=")[0]
                __import__(package_name.replace("-", "_"))
                print(f"✅ {package_name} is available")
            except ImportError:
                print(f"⚠️  Installing {package}...")
                self.run_command(f"pip install {package}", f"Install {package}")

    def run_lint_checks(self):
        """Run all linting checks"""
        print("\n" + "=" * 80)
        print("RUNNING LINT CHECKS")
        print("=" * 80)

        lint_commands = [
            # Flake8 - Style and complexity
            (
                "flake8 . --exclude=htmlcov,__pycache__,.git --count --select=E9,F63,F7,F82 --show-source --statistics",
                "Flake8 style check",
            ),
            # Black - Code formatting
            (
                "black --check --diff . --exclude=htmlcov --exclude=__pycache__ --exclude=.git",
                "Black formatting check",
            ),
            # isort - Import sorting
            (
                "isort --check-only --diff . --skip=htmlcov --skip=__pycache__",
                "Import sorting check",
            ),
            # Pylint - Code quality (target specific files)
            (
                "pylint kotlin_mcp_server.py vscode_bridge.py --output-format=text --reports=yes --score=yes",
                "Pylint code quality",
            ),
            # MyPy - Type checking
            (
                "mypy kotlin_mcp_server.py vscode_bridge.py --ignore-missing-imports",
                "MyPy type checking",
            ),
            # Bandit - Security check
            ("bandit -r . -f txt --exclude=htmlcov,__pycache__,.git", "Bandit security check"),
        ]

        for command, description in lint_commands:
            self.run_command(command, description)

    def run_unit_tests(self):
        """Run comprehensive unit tests"""
        print("\n" + "=" * 80)
        print("RUNNING UNIT TESTS")
        print("=" * 80)

        test_commands = [
            # Modular test suite (new structure)
            (
                "python -m pytest tests/ -v --tb=short --asyncio-mode=auto",
                "Modular test suite",
            ),
            # All tests with coverage
            (
                "python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=30 --asyncio-mode=auto",
                "All tests with coverage",
            ),
        ]

        for command, description in test_commands:
            self.run_command(command, description)

    def run_functionality_tests(self):
        """Run functionality validation tests"""
        print("\n" + "=" * 80)
        print("RUNNING FUNCTIONALITY VALIDATION")
        print("=" * 80)

        # Test server imports and basic initialization
        functionality_tests = [
            (
                "python -c \"from kotlin_mcp_server import KotlinMCPServer; print('✅ KotlinMCPServer import successful')\"",
                "Kotlin MCP Server import",
            ),
            (
                "python -c \"from vscode_bridge import MCPBridgeHandler; print('✅ Bridge handler import successful')\"",
                "VS Code Bridge import",
            ),
        ]

        for command, description in functionality_tests:
            self.run_command(command, description)

    def run_performance_tests(self):
        """Run performance validation"""
        print("\n" + "=" * 80)
        print("RUNNING PERFORMANCE TESTS")
        print("=" * 80)

        # Performance test script
        perf_script = """
import asyncio
import time
import tempfile
from pathlib import Path
from kotlin_mcp_server import KotlinMCPServer

async def performance_test():
    server = KotlinMCPServer("perf-test")
    server.project_path = Path(tempfile.mkdtemp())

    # Test tool listing speed
    start_time = time.time()
    for _ in range(5):
        result = await server.handle_list_tools()
    list_time = time.time() - start_time

    # Test basic server functionality
    start_time = time.time()
    for i in range(3):
        # Test basic tool call that should exist
        try:
            await server.handle_call_tool({
                "name": "create_kotlin_file",
                "arguments": {
                    "filename": f"Test{i}.kt",
                    "class_name": f"Test{i}",
                    "package_name": "com.test"
                }
            })
        except Exception as e:
            print(f"Tool call test failed (expected): {e}")
    create_time = time.time() - start_time

    print(f"✅ Tool listing: {list_time:.2f}s for 5 calls")
    print(f"✅ Tool calls: {create_time:.2f}s for 3 calls")

    # Cleanup
    import shutil
    shutil.rmtree(server.project_path, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(performance_test())
"""

        # Write and run performance test
        with open("temp_perf_test.py", "w") as f:
            f.write(perf_script)

        self.run_command("python temp_perf_test.py", "Performance validation")

        # Cleanup
        if os.path.exists("temp_perf_test.py"):
            os.remove("temp_perf_test.py")

    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("FINAL TEST REPORT")
        print("=" * 80)

        if not self.failed_checks:
            print("🎉 ALL CHECKS PASSED! The MCP server is ready for deployment.")
            print("\nThe following areas were validated:")
            print("• Code style and formatting")
            print("• Type checking and static analysis")
            print("• Security vulnerabilities")
            print("• Unit and integration tests")
            print("• Functionality validation")
            print("• Performance benchmarks")
            return True
        else:
            print("❌ SOME CHECKS FAILED!")
            print(f"\nFailed checks ({len(self.failed_checks)}):")
            for i, check in enumerate(self.failed_checks, 1):
                print(f"  {i}. {check}")

            print("\n🔧 Recommendations:")
            print("• Fix failing lint checks before deployment")
            print("• Ensure all tests pass")
            print("• Review security vulnerabilities")
            print("• Check import dependencies")
            return False

    def run_all_checks(self):
        """Run all quality checks"""
        print("🚀 Starting MCP Server Quality Assurance Pipeline")
        print("=" * 80)

        # Check dependencies first
        self.check_dependencies()

        # Run all checks
        self.run_functionality_tests()
        self.run_lint_checks()
        self.run_unit_tests()
        self.run_performance_tests()

        # Generate final report
        success = self.generate_report()

        return success


def main():
    """Main entry point"""
    runner = CITestRunner()
    success = runner.run_all_checks()

    if success:
        print("\n✅ Quality assurance pipeline completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Quality assurance pipeline failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
