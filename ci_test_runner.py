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
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {command}")
        print(f"{'='*60}")

        try:
            # Use shlex.split for safer command execution
            import shlex

            command_list = shlex.split(command)
            result = subprocess.run(
                command_list, cwd=self.project_root, capture_output=True, text=True, timeout=300
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
            ("flake8 *.py", "Flake8 style check"),
            # Black - Code formatting
            ("black --check --diff *.py", "Black formatting check"),
            # isort - Import sorting
            ("isort --check-only --diff *.py", "Import sorting check"),
            # Pylint - Code quality
            ("pylint *.py --output-format=text --reports=yes --score=yes", "Pylint code quality"),
            # MyPy - Type checking
            ("mypy *.py --ignore-missing-imports", "MyPy type checking"),
            # Bandit - Security check
            ("bandit -r *.py -f txt", "Bandit security check"),
        ]

        for command, description in lint_commands:
            self.run_command(command, description)

    def run_unit_tests(self):
        """Run comprehensive unit tests"""
        print("\n" + "=" * 80)
        print("RUNNING UNIT TESTS")
        print("=" * 80)

        test_commands = [
            # Simple tests
            ("python -m pytest simple_test.py -v --tb=short", "Simple MCP tests"),
            # Comprehensive tests
            ("python -m pytest comprehensive_test.py -v --tb=short", "Comprehensive MCP tests"),
            # New comprehensive test suite
            (
                "python -m pytest test_mcp_comprehensive.py -v --tb=short",
                "Full comprehensive test suite",
            ),
            # All tests with coverage
            (
                "python -m pytest test_*.py -v --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=70",
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
                "python -c \"from simple_mcp_server import MCPServer; print('✅ MCPServer import successful')\"",
                "Base MCP Server import",
            ),
            (
                "python -c \"from enhanced_mcp_server import EnhancedAndroidMCPServer; print('✅ Enhanced server import successful')\"",
                "Enhanced MCP Server import",
            ),
            (
                "python -c \"from security_privacy_server import SecurityPrivacyMCPServer; print('✅ Security server import successful')\"",
                "Security MCP Server import",
            ),
            (
                "python -c \"from ai_integration_server import AIIntegratedMCPServer; print('✅ AI server import successful')\"",
                "AI Integration Server import",
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
from ai_integration_server import AIIntegratedMCPServer

async def performance_test():
    server = AIIntegratedMCPServer("perf-test")
    server.project_path = Path(tempfile.mkdtemp())
    
    # Test tool listing speed
    start_time = time.time()
    for _ in range(10):
        await server.handle_list_tools()
    list_time = time.time() - start_time
    
    # Test file creation speed
    start_time = time.time()
    for i in range(5):
        await server.handle_call_tool("create_kotlin_file", {
            "file_path": f"test/Test{i}.kt",
            "class_name": f"Test{i}",
            "package_name": "com.test",
            "class_type": "class"
        })
    create_time = time.time() - start_time
    
    print(f"✅ Tool listing: {list_time:.2f}s for 10 calls")
    print(f"✅ File creation: {create_time:.2f}s for 5 files")
    
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
