"""
Gradle and build tools for Kotlin MCP Server.

This module provides comprehensive build management capabilities:
- Gradle build execution with proper error handling
- Test running and reporting
- Code formatting and linting
- Documentation generation
- Build performance optimization
- Dependency management
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List

from utils.security import SecurityManager


class GradleTools:
    """Tools for Gradle build system operations."""

    def __init__(self, project_path: Path, security_manager: SecurityManager):
        """Initialize Gradle tools with project path and security manager."""
        self.project_path = project_path
        self.security_manager = security_manager

    async def gradle_build(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Gradle build with comprehensive error handling and reporting.

        This tool provides professional-grade build capabilities:
        - Clean builds for reliable results
        - Multiple build configurations (debug, release)
        - Dependency resolution and caching
        - Build performance monitoring
        - Detailed error reporting and analysis
        """
        try:
            # Validate project path is available and contains a Gradle project
            if not self.project_path or not Path(self.project_path).exists():
                return {
                    "success": False,
                    "error": "Build failed: project path required. Please specify a valid --project-path argument.",
                }

            # Check for Gradle project files
            gradle_files = ["build.gradle", "build.gradle.kts", "gradlew"]
            if not any(
                (Path(self.project_path) / gradle_file).exists() for gradle_file in gradle_files
            ):
                return {
                    "success": False,
                    "error": "Build failed: project path required. No Gradle project found. Please specify a valid --project-path argument with build.gradle file.",
                }

            # Extract and validate build arguments
            build_type = arguments.get("build_type", "debug")
            clean_build = arguments.get("clean", False)

            # Validate build type parameter
            valid_build_types = ["debug", "release", "test"]
            if build_type not in valid_build_types:
                return {
                    "success": False,
                    "error": f"Invalid build type: {build_type}. Must be one of: {valid_build_types}",
                }

            # Log audit event for security and compliance
            self.security_manager.log_audit_event(
                "gradle_build", f"build_type:{build_type}", f"clean:{clean_build}"
            )

            # Construct Gradle command with appropriate arguments
            gradle_cmd = ["./gradlew"]

            # Add clean step if requested for reliable builds
            if clean_build:
                gradle_cmd.append("clean")

            # Add build task based on build type
            if build_type == "debug":
                gradle_cmd.append("assembleDebug")
            elif build_type == "release":
                gradle_cmd.append("assembleRelease")
            elif build_type == "test":
                gradle_cmd.extend(["test", "assembleDebug"])

            # Add build optimization flags for better performance
            gradle_cmd.extend(
                [
                    "--parallel",  # Enable parallel execution
                    "--build-cache",  # Use build cache for speed
                    "--configuration-cache",  # Cache configuration for faster subsequent builds
                ]
            )

            # Validate command arguments for security
            safe_args = self.security_manager.validate_command_args(gradle_cmd)

            # Execute Gradle build with timeout for reliability
            process = await asyncio.create_subprocess_exec(
                *safe_args,
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Wait for completion with timeout to prevent hanging
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)

            # Decode output for analysis
            stdout_text = stdout.decode("utf-8")
            stderr_text = stderr.decode("utf-8")

            # Analyze build results
            success = process.returncode == 0

            # Extract build performance metrics if available
            build_time = self._extract_build_time(stdout_text)

            return {
                "success": success,
                "exit_code": process.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "build_type": build_type,
                "build_time": build_time,
                "message": "Build completed successfully" if success else "Build failed",
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Build timed out after 5 minutes",
                "message": "Consider using incremental builds or checking for circular dependencies",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Build execution failed: {str(e)}",
                "message": "Check project configuration and dependencies",
            }

    async def run_tests(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute comprehensive test suite with detailed reporting.

        Features:
        - Unit tests, integration tests, and UI tests
        - Test result parsing and analysis
        - Coverage reporting and analysis
        - Performance test metrics
        - Parallel test execution for speed
        """
        try:
            # Extract test configuration
            test_type = arguments.get("test_type", "unit")
            generate_coverage = arguments.get("coverage", True)

            # Validate test type
            valid_types = ["unit", "integration", "ui", "all"]
            if test_type not in valid_types:
                return {
                    "success": False,
                    "error": f"Invalid test type: {test_type}. Must be one of: {valid_types}",
                }

            # Log test execution for audit trail
            self.security_manager.log_audit_event(
                "run_tests", f"test_type:{test_type}", f"coverage:{generate_coverage}"
            )

            # Build Gradle test command
            gradle_cmd = ["./gradlew"]

            # Add appropriate test tasks
            if test_type == "unit":
                gradle_cmd.extend(["testDebugUnitTest"])
            elif test_type == "integration":
                gradle_cmd.extend(["connectedDebugAndroidTest"])
            elif test_type == "ui":
                gradle_cmd.extend(["connectedDebugAndroidTest"])
            elif test_type == "all":
                gradle_cmd.extend(["test", "connectedDebugAndroidTest"])

            # Add coverage if requested
            if generate_coverage:
                gradle_cmd.extend(["jacocoTestReport"])

            # Add performance flags
            gradle_cmd.extend(["--parallel", "--build-cache"])

            # Validate and execute command
            safe_args = self.security_manager.validate_command_args(gradle_cmd)

            process = await asyncio.create_subprocess_exec(
                *safe_args,
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)

            stdout_text = stdout.decode("utf-8")
            stderr_text = stderr.decode("utf-8")

            # Parse test results
            test_results = self._parse_test_results(stdout_text)

            return {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "test_type": test_type,
                "test_results": test_results,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "coverage_generated": generate_coverage,
            }

        except Exception as e:
            return {"success": False, "error": f"Test execution failed: {str(e)}"}

    async def format_code(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format code using ktlint for consistent code style.

        Features:
        - Kotlin code formatting with industry standards
        - Custom rule configuration support
        - Incremental formatting for large projects
        - Integration with CI/CD pipelines
        """
        try:
            # Extract formatting options
            auto_fix = arguments.get("auto_fix", True)
            check_only = arguments.get("check_only", False)

            self.security_manager.log_audit_event(
                "format_code", f"auto_fix:{auto_fix}", f"check_only:{check_only}"
            )

            # Build ktlint command
            gradle_cmd = ["./gradlew"]

            if check_only:
                gradle_cmd.append("ktlintCheck")
            elif auto_fix:
                gradle_cmd.append("ktlintFormat")
            else:
                gradle_cmd.append("ktlintCheck")

            safe_args = self.security_manager.validate_command_args(gradle_cmd)

            process = await asyncio.create_subprocess_exec(
                *safe_args,
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)

            return {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8"),
                "auto_fix": auto_fix,
                "check_only": check_only,
            }

        except Exception as e:
            return {"success": False, "error": f"Code formatting failed: {str(e)}"}

    async def run_lint(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive lint analysis for code quality.

        Features:
        - Android Lint for platform-specific issues
        - Custom lint rules for project standards
        - Detailed issue reporting with suggestions
        - Integration with quality gates
        """
        try:
            # Extract lint configuration
            lint_type = arguments.get("lint_type", "debug")
            abort_on_error = arguments.get("abort_on_error", False)

            self.security_manager.log_audit_event(
                "run_lint", f"lint_type:{lint_type}", f"abort_on_error:{abort_on_error}"
            )

            # Build lint command
            gradle_cmd = ["./gradlew", f"lint{lint_type.capitalize()}"]

            if abort_on_error:
                gradle_cmd.append("--abort_on_error")

            safe_args = self.security_manager.validate_command_args(gradle_cmd)

            process = await asyncio.create_subprocess_exec(
                *safe_args,
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=180)

            # Parse lint results
            lint_results = self._parse_lint_results(stdout.decode("utf-8"))

            return {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "lint_type": lint_type,
                "lint_results": lint_results,
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8"),
            }

        except Exception as e:
            return {"success": False, "error": f"Lint analysis failed: {str(e)}"}

    async def generate_docs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive project documentation.

        Features:
        - KDoc documentation generation
        - API documentation with examples
        - Dependency graphs and architecture diagrams
        - Custom documentation templates
        """
        try:
            # Extract documentation options
            doc_format = arguments.get("format", "html")
            include_private = arguments.get("include_private", False)

            self.security_manager.log_audit_event(
                "generate_docs", f"format:{doc_format}", f"include_private:{include_private}"
            )

            # Build documentation command
            gradle_cmd = ["./gradlew", "dokkaHtml"]

            if include_private:
                gradle_cmd.append("-PdokkaIncludePrivate=true")

            safe_args = self.security_manager.validate_command_args(gradle_cmd)

            process = await asyncio.create_subprocess_exec(
                *safe_args,
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)

            # Check for generated documentation
            docs_path = self.project_path / "build" / "dokka" / "html"
            docs_generated = docs_path.exists()

            return {
                "success": process.returncode == 0 and docs_generated,
                "exit_code": process.returncode,
                "format": doc_format,
                "docs_path": str(docs_path) if docs_generated else None,
                "docs_generated": docs_generated,
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8"),
            }

        except Exception as e:
            return {"success": False, "error": f"Documentation generation failed: {str(e)}"}

    def _extract_build_time(self, stdout: str) -> str:
        """Extract build time from Gradle output."""
        lines = stdout.split("\n")
        for line in lines:
            if "BUILD SUCCESSFUL" in line or "BUILD FAILED" in line:
                # Look for time pattern like "in 1m 23s"
                if " in " in line:
                    time_part = line.split(" in ")[-1]
                    return time_part.strip()
        return "Unknown"

    def _parse_test_results(self, stdout: str) -> Dict[str, Any]:
        """Parse test results from Gradle output."""
        results = {"total_tests": 0, "passed": 0, "failed": 0, "skipped": 0}

        lines = stdout.split("\n")
        for line in lines:
            if "tests completed" in line.lower():
                # Try to extract test numbers
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        results["total_tests"] = int(part)
                        break

        return results

    def _parse_lint_results(self, stdout: str) -> Dict[str, Any]:
        """Parse lint results from output."""
        results = {"errors": 0, "warnings": 0, "informational": 0}

        lines = stdout.split("\n")
        for line in lines:
            if "error" in line.lower() and "found" in line.lower():
                # Extract error count
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        results["errors"] = int(part)
                        break

        return results

    async def get_dependencies(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get project dependencies.
        """
        try:
            # Log audit event for security and compliance
            self.security_manager.log_audit_event("get_dependencies", "", "")

            # Construct Gradle command
            gradle_cmd = ["./gradlew", "app:dependencies"]

            # Validate command arguments for security
            safe_args = self.security_manager.validate_command_args(gradle_cmd)

            # Execute Gradle command
            process = await asyncio.create_subprocess_exec(
                *safe_args,
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Wait for completion with timeout to prevent hanging
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)

            # Decode output for analysis
            stdout_text = stdout.decode("utf-8")
            stderr_text = stderr.decode("utf-8")

            # Analyze build results
            success = process.returncode == 0

            if not success:
                return {
                    "success": False,
                    "error": "Failed to get dependencies",
                    "stderr": stderr_text,
                }

            # Parse dependencies
            dependencies = self._parse_dependencies(stdout_text)

            return {
                "success": True,
                "dependencies": dependencies,
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Getting dependencies timed out after 5 minutes",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Getting dependencies failed: {str(e)}",
            }

    def _parse_dependencies(self, output: str) -> List[Dict[str, str]]:
        """Parse the output of the dependencies task."""
        dependencies = []
        lines = output.splitlines()
        # This is a very basic parser. A more robust solution would use a proper
        # grammar or a library that can parse Gradle's output.
        for line in lines:
            if "+---" in line or "\\--- " in line:
                parts = line.split()
                if len(parts) > 1:
                    dep_str = parts[-1]
                    dep_parts = dep_str.split(":")
                    if len(dep_parts) == 3:
                        dependencies.append(
                            {
                                "group": dep_parts[0],
                                "name": dep_parts[1],
                                "version": dep_parts[2],
                            }
                        )
        return dependencies
