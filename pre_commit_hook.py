#!/usr/bin/env python3
"""
Pre-commit hook to ensure code quality before commits
Automatically runs when code is committed to prevent breaking changes
"""

import shlex
import subprocess
import sys
from pathlib import Path
from typing import List


def run_quick_checks() -> bool:
    """Run quick quality checks before commit"""
    print("🔍 Running pre-commit quality checks...")

    failed_checks = []
    project_root = Path(__file__).parent

    # Dynamically find all Python files in the project
    python_files: List[Path] = []
    for pattern in ["*.py", "**/*.py"]:
        python_files.extend(project_root.glob(pattern))

    # Filter out __pycache__, .venv, htmlcov and other unwanted directories
    python_files_str = [
        str(f.relative_to(project_root))
        for f in python_files
        if not any(
            excluded in str(f)
            for excluded in ["__pycache__", ".git", ".venv", "htmlcov", ".pytest_cache", "archive"]
        )
    ]

    main_files = " ".join(python_files_str)

    checks = [
        # Python syntax check
        (
            f"python3 -m py_compile {main_files}",
            "Python syntax validation",
        ),
        # Import check for main modules
        (
            'python3 -c "import kotlin_mcp_server; from ai.llm_integration import LLMIntegration; from utils.security import SecurityManager"',
            "Module import validation",
        ),
        # Critical flake8 checks (syntax errors and undefined names)
        (
            f"python3 -m flake8 --select=E9,F63,F7,F82 {main_files}",
            "Critical syntax errors",
        ),
        # Basic security check with bandit
        # High-severity security issues
        (
            f"python3 -m bandit -r {main_files} -lll",
            "High-severity security issues",
        ),
        # isort check for import sorting
        (
            f"python3 -m isort --check-only --profile=black --line-length=100 --skip-glob='*.venv*' {main_files}",
            "Import sorting check",
        ),
        # Black check for code formatting
        (
            f"python3 -m black --check --line-length=100 --exclude='.venv|__pycache__|htmlcov' {main_files}",
            "Code formatting check",
        ),
        # Quick test run (only core functionality tests)
        (
            "python3 -m pytest tests/test_server_core.py::TestKotlinMCPServerCore::test_server_initialization --tb=no -q",
            "Core functionality test",
        ),
        # Tool modules import test
        (
            "python3 -c 'from tools.gradle_tools import GradleTools; from tools.build_optimization import BuildOptimizationTools; from tools.project_analysis import ProjectAnalysisTools; print(\"Tool modules import successfully\")'",
            "Tool modules import test",
        ),
        # Tool modules integration test - basic functionality check
        (
            "python3 -c 'from kotlin_mcp_server import KotlinMCPServerV2; server = KotlinMCPServerV2(); print(\"Tool integration test passed\")'",
            "Tool modules integration test",
        ),
    ]

    for command, description in checks:
        print(f"\n⚡ {description}...")
        try:
            # Use shlex.split for safer command execution
            command_list = shlex.split(command)

            # Additional security: validate command executables
            allowed_commands = ["python3", "python", "pytest", "black", "flake8", "isort", "bandit"]
            if command_list[0] not in allowed_commands:
                print(f"❌ {description} - BLOCKED: Unauthorized command: {command_list[0]}")
                failed_checks.append(description)
                continue

            # Use longer timeout for bandit security scan, shorter for others
            timeout_val = 60 if "bandit" in command else 15

            result = subprocess.run(
                command_list,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=timeout_val,
                shell=False,  # Explicitly disable shell execution
                check=False,  # Don't raise exception on non-zero exit
            )

            if result.returncode == 0:
                print(f"✅ {description} - PASSED")
            else:
                print(f"❌ {description} - FAILED")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}")
                failed_checks.append(description)

        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT")
            failed_checks.append(description)
        except (FileNotFoundError, PermissionError, subprocess.SubprocessError) as e:
            print(f"💥 {description} - ERROR: {e}")
            failed_checks.append(description)

    return len(failed_checks) == 0


def main() -> None:
    """Main pre-commit hook"""
    print("🚀 MCP Server Pre-commit Hook")
    print("=" * 50)

    if run_quick_checks():
        print("\n✅ Pre-commit checks passed! Commit proceeding...")
        sys.exit(0)
    else:
        print("\n❌ Pre-commit checks failed!")
        print("Please fix the issues above before committing.")
        print("Run 'python3 ci_test_runner.py' for detailed analysis.")
        sys.exit(1)


if __name__ == "__main__":
    main()
