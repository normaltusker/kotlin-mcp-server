#!/usr/bin/env python3
"""
Pre-commit hook to ensure code quality before commits
Automatically runs when code is committed to prevent breaking changes
"""

import os
import subprocess
import sys
from pathlib import Path


def run_quick_checks():
    """Run quick quality checks before commit"""
    print("🔍 Running pre-commit quality checks...")

    failed_checks = []
    project_root = Path(__file__).parent

    # Quick lint checks
    checks = [
        # Python syntax check
        (
            "python -m py_compile simple_mcp_server.py enhanced_mcp_server.py security_privacy_server.py ai_integration_server.py",
            "Python syntax validation",
        ),
        # Import check
        (
            'python -c "import simple_mcp_server, enhanced_mcp_server, security_privacy_server, ai_integration_server"',
            "Module import validation",
        ),
        # Quick flake8 check (only errors)
        (
            "flake8 --select=E9,F63,F7,F82 simple_mcp_server.py enhanced_mcp_server.py security_privacy_server.py ai_integration_server.py",
            "Critical syntax errors",
        ),
        # Basic security check
        (
            "bandit -ll simple_mcp_server.py enhanced_mcp_server.py security_privacy_server.py ai_integration_server.py",
            "High-severity security issues",
        ),
    ]

    for command, description in checks:
        print(f"\n⚡ {description}...")
        try:
            # Use shlex.split for safer command execution
            import shlex

            command_list = shlex.split(command)
            result = subprocess.run(
                command_list, cwd=project_root, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                print(f"✅ {description} - PASSED")
            else:
                print(f"❌ {description} - FAILED")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}")
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
        print("Run 'python ci_test_runner.py' for detailed analysis.")
        sys.exit(1)


if __name__ == "__main__":
    main()
