#!/usr/bin/env python3
"""
Simplified Pre-commit hook for Kotlin MCP Server
Focuses on essential quality checks for project files only
"""

import shlex
import subprocess
import sys
from pathlib import Path


def run_essential_checks() -> bool:
    """Run essential quality checks before commit"""
    print("🔍 Running essential pre-commit quality checks...")

    failed_checks = []
    project_root = Path(__file__).parent

    # Essential checks that should always pass
    checks = [
        # Python syntax check for main modules
        (
            "python3 -c 'import kotlin_mcp_server; from ai.llm_integration import LLMIntegration; from utils.security import SecurityManager; print(\"✅ Core modules import successfully\")'",
            "Core module imports",
        ),
        # Import sorting check (current directory)
        (
            "python3 -m isort --check-only --profile=black --line-length=100 --skip=.venv .",
            "Import sorting check",
        ),
        # Code formatting check (current directory)
        (
            "python3 -m black --check --line-length=100 --exclude='.venv|__pycache__|htmlcov' .",
            "Code formatting check",
        ),
        # Basic flake8 check (current directory)
        (
            "python3 -m flake8 --max-line-length=100 --extend-ignore=E203,W503,E501,C901 --exclude=__pycache__,.venv,htmlcov .",
            "Code linting check",
        ),
        # Tool modules import test
        (
            "python3 -c 'from tools.gradle_tools import GradleTools; from tools.build_optimization import BuildOptimizationTools; from tools.project_analysis import ProjectAnalysisTools; print(\"✅ Tool modules import successfully\")'",
            "Tool modules import test",
        ),
    ]

    for command, description in checks:
        print(f"\n⚡ {description}...")
        try:
            # Use shlex.split for safer command execution
            command_list = shlex.split(command)

            result = subprocess.run(
                command_list,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=20,
                shell=False,
                check=False,
            )

            if result.returncode == 0:
                print(f"✅ {description} - PASSED")
            else:
                print(f"❌ {description} - FAILED")
                if result.stderr and len(result.stderr) < 500:
                    print(f"Error: {result.stderr}")
                elif result.stdout and len(result.stdout) < 500:
                    print(f"Output: {result.stdout}")
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
    print("🚀 MCP Server Essential Pre-commit Hook")
    print("=" * 50)

    if run_essential_checks():
        print("\n✅ Essential pre-commit checks passed! Commit proceeding...")
        sys.exit(0)
    else:
        print("\n❌ Essential pre-commit checks failed!")
        print("Please fix the issues above before committing.")
        print("Run manual checks:")
        print("  python3 -m isort --profile=black --line-length=100 .")
        print("  python3 -m black --line-length=100 .")
        print(
            "  python3 -m flake8 --max-line-length=100 --extend-ignore=E203,W503,E501,C901 --exclude=__pycache__,.venv,htmlcov ."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
