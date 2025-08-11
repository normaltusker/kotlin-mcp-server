#!/usr/bin/env python3
"""
Pre-commit hook to ensure code quality before commits
Automatically runs when code is committed to prevent breaking changes
"""

import subprocess
import sys
from pathlib import Path


def run_quick_checks():
    """Run quick quality checks before commit"""
    print("🔍 Running pre-commit quality checks...")

    failed_checks = []
    project_root = Path(__file__).parent

    # Quick lint checks
    main_files = "kotlin_mcp_server.py vscode_bridge.py test_kotlin_mcp_server.py ci_test_runner.py validate_config.py install.py breaking_change_monitor.py"
    checks = [
        # Python syntax check
        (
            f"python3 -m py_compile {main_files}",
            "Python syntax validation",
        ),
        # Import check for main modules
        (
            'python3 -c "import kotlin_mcp_server, vscode_bridge"',
            "Module import validation",
        ),
        # Quick flake8 check (only errors)
        (
            f"python3 -m flake8 --select=E9,F63,F7,F82 {main_files}",
            "Critical syntax errors",
        ),
        # Basic security check
        (
            f"python3 -m bandit -lll {main_files}",
            "High-severity security issues",
        ),
        # isort check for import sorting
        (
            f"python3 -m isort --check-only --diff {main_files}",
            "Import sorting check",
        ),
        # Black check for code formatting
        (
            f"python3 -m black --check --diff {main_files}",
            "Code formatting check",
        ),
    ]

    for command, description in checks:
        print(f"\n⚡ {description}...")
        try:
            # Use shlex.split for safer command execution
            import shlex

            command_list = shlex.split(command)

            # Additional security: validate command executables
            if command_list[0] not in ["python3", "python", "pytest", "black", "flake8"]:
                print(f"❌ {description} - BLOCKED: Unauthorized command: {command_list[0]}")
                failed_checks.append(description)
                continue

            result = subprocess.run(
                command_list,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30,
                shell=False,  # Explicitly disable shell execution
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
        except Exception as e:
            print(f"💥 {description} - ERROR: {e}")
            failed_checks.append(description)

    return len(failed_checks) == 0


def main():
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
