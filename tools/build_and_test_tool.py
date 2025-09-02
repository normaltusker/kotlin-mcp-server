"""
Enhanced build and test tool with project root enforcement.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from server.utils.base_tool import BaseMCPTool
from server.utils.project_resolver import ProjectRootError, find_gradle_cmd
from utils.security import SecurityManager


class BuildAndTestTool(BaseMCPTool):
    """Build and test tool with robust project root resolution."""

    def __init__(self, security_manager: Optional[SecurityManager] = None):
        """Initialize build and test tool."""
        super().__init__(security_manager)

    async def build_and_test(
        self, arguments: Dict[str, Any], ide_context: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Build and test a project with comprehensive reporting.

        Args:
            arguments: Tool arguments including project_root, build_tool, skip_tests
            ide_context: IDE metadata for workspace resolution

        Returns:
            Dictionary with build/test results, artifacts, and test summaries
        """
        try:
            # Normalize inputs and resolve project root
            arguments = self.normalize_inputs(arguments)
            project_root = self.resolve_project_root(arguments, ide_context)

            # Extract build configuration
            build_tool = arguments.get("build_tool", "auto")
            skip_tests = arguments.get("skip_tests", False)
            variant = arguments.get("variant", "debug")

            if self.security_manager:
                self.security_manager.log_audit_event(
                    "build_and_test",
                    f"build_tool:{build_tool}",
                    f"skip_tests:{skip_tests}",
                    f"variant:{variant}",
                    f"project_root:{project_root}",
                )

            # Auto-detect build tool if needed
            if build_tool == "auto":
                build_tool = self._detect_build_tool(project_root)

            # Execute build and test based on tool
            if build_tool == "gradle":
                return await self._gradle_build_and_test(project_root, variant, skip_tests)
            elif build_tool == "maven":
                return await self._maven_build_and_test(project_root, variant, skip_tests)
            else:
                raise ValueError(f"Unsupported build tool: {build_tool}")

        except ProjectRootError as e:
            return {
                "success": False,
                "error": f"Project root resolution failed: {str(e)}",
                "error_type": "ProjectRootRequired",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Build and test failed: {str(e)}",
                "error_type": "BuildTestFailed",
            }

    def _detect_build_tool(self, project_root: str) -> str:
        """Detect the build tool used by the project."""
        project_path = Path(project_root)

        # Check for Gradle files
        gradle_files = ["build.gradle", "build.gradle.kts", "gradlew", "gradle.properties"]
        if any((project_path / file).exists() for file in gradle_files):
            return "gradle"

        # Check for Maven files
        maven_files = ["pom.xml", "mvnw"]
        if any((project_path / file).exists() for file in maven_files):
            return "maven"

        # Default to gradle for Android projects
        if (project_path / "app" / "src" / "main" / "AndroidManifest.xml").exists():
            return "gradle"

        raise ValueError("Could not detect build tool. Please specify build_tool parameter.")

    async def _gradle_build_and_test(
        self, project_root: str, variant: str, skip_tests: bool
    ) -> Dict[str, Any]:
        """Execute Gradle build and test."""
        try:
            # Find Gradle command
            gradle_cmd, working_dir, is_wrapper = find_gradle_cmd(project_root)

            # Build command
            build_cmd = gradle_cmd.copy()

            # Add build tasks
            if variant == "debug":
                build_cmd.extend(["assembleDebug"])
            elif variant == "release":
                build_cmd.extend(["assembleRelease"])
            else:
                build_cmd.extend([f"assemble{variant.capitalize()}"])

            # Add test tasks if not skipped
            if not skip_tests:
                build_cmd.extend(["test", f"test{variant.capitalize()}UnitTest"])

            # Add build optimization flags
            build_cmd.extend(["--parallel", "--build-cache", "--configuration-cache"])

            # Validate command for security
            if self.security_manager:
                safe_cmd = self.security_manager.validate_command_args(build_cmd)
            else:
                safe_cmd = build_cmd

            # Execute build
            process = await asyncio.create_subprocess_exec(
                *safe_cmd,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)

            stdout_text = stdout.decode("utf-8")
            stderr_text = stderr.decode("utf-8")

            # Parse results
            build_success = process.returncode == 0
            build_time = self._extract_build_time(stdout_text)
            test_results = self._parse_test_results(stdout_text) if not skip_tests else None
            artifacts = self._find_artifacts(working_dir, variant)

            return {
                "success": build_success,
                "exit_code": process.returncode,
                "build_tool": "gradle",
                "variant": variant,
                "build_time": build_time,
                "test_results": test_results,
                "artifacts": artifacts,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "project_root": project_root,
                "working_dir": working_dir,
                "is_wrapper": is_wrapper,
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Build timed out after 10 minutes",
                "error_type": "BuildTimeout",
                "project_root": project_root,
            }

    async def _maven_build_and_test(
        self, project_root: str, variant: str, skip_tests: bool
    ) -> Dict[str, Any]:
        """Execute Maven build and test."""
        try:
            # Find Maven command
            maven_cmd = self._find_maven_cmd(project_root)

            # Build command
            build_cmd = maven_cmd.copy()
            build_cmd.extend(["clean", "compile"])

            if not skip_tests:
                build_cmd.append("test")

            # Add variant-specific profile
            if variant != "debug":
                build_cmd.extend(["-P", variant])

            # Validate command for security
            if self.security_manager:
                safe_cmd = self.security_manager.validate_command_args(build_cmd)
            else:
                safe_cmd = build_cmd

            # Execute build
            process = await asyncio.create_subprocess_exec(
                *safe_cmd,
                cwd=project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)

            stdout_text = stdout.decode("utf-8")
            stderr_text = stderr.decode("utf-8")

            # Parse results
            build_success = process.returncode == 0
            build_time = self._extract_maven_build_time(stdout_text)
            test_results = self._parse_maven_test_results(stdout_text) if not skip_tests else None
            artifacts = self._find_maven_artifacts(project_root, variant)

            return {
                "success": build_success,
                "exit_code": process.returncode,
                "build_tool": "maven",
                "variant": variant,
                "build_time": build_time,
                "test_results": test_results,
                "artifacts": artifacts,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "project_root": project_root,
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Build timed out after 10 minutes",
                "error_type": "BuildTimeout",
                "project_root": project_root,
            }

    def _find_maven_cmd(self, project_root: str) -> List[str]:
        """Find Maven command (wrapper or system)."""
        # Check for Maven wrapper
        mvnw = Path(project_root) / "mvnw"
        if mvnw.exists():
            mvnw.chmod(0o755)
            return ["./mvnw"]

        # Check for system Maven
        import shutil

        if shutil.which("mvn"):
            return ["mvn"]

        raise ProjectRootError("Maven not found: no mvnw wrapper and no system mvn on PATH")

    def _extract_build_time(self, stdout: str) -> Optional[str]:
        """Extract build time from Gradle output."""
        lines = stdout.split("\n")
        for line in lines:
            if "BUILD SUCCESSFUL" in line or "BUILD FAILED" in line:
                if " in " in line:
                    time_part = line.split(" in ")[-1]
                    return time_part.strip()
        return None

    def _extract_maven_build_time(self, stdout: str) -> Optional[str]:
        """Extract build time from Maven output."""
        lines = stdout.split("\n")
        for line in lines:
            if "Total time:" in line:
                return line.split("Total time:")[-1].strip()
        return None

    def _parse_test_results(self, stdout: str) -> Dict[str, Any]:
        """Parse test results from Gradle output."""
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "test_files": [],
        }

        lines = stdout.split("\n")
        for line in lines:
            if "tests completed" in line.lower():
                # Extract test numbers
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        results["total_tests"] = int(part)
                        break

        return results

    def _parse_maven_test_results(self, stdout: str) -> Dict[str, Any]:
        """Parse test results from Maven output."""
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "test_files": [],
        }

        lines = stdout.split("\n")
        for line in lines:
            if "Tests run:" in line:
                # Parse Maven test summary line
                if "Failures:" in line and "Errors:" in line:
                    parts = line.split(",")
                    for part in parts:
                        part = part.strip()
                        if part.startswith("Tests run:"):
                            results["total_tests"] = int(part.split(":")[1].strip())
                        elif part.startswith("Failures:"):
                            results["failed"] = int(part.split(":")[1].strip())

        return results

    def _find_artifacts(self, project_root: str, variant: str) -> List[Dict[str, Any]]:
        """Find build artifacts."""
        artifacts = []
        build_dir = Path(project_root) / "app" / "build" / "outputs"

        if build_dir.exists():
            # Find APK files
            apk_dir = build_dir / "apk" / variant
            if apk_dir.exists():
                for apk_file in apk_dir.glob("*.apk"):
                    artifacts.append(
                        {
                            "type": "apk",
                            "path": str(apk_file),
                            "size": apk_file.stat().st_size,
                            "variant": variant,
                        }
                    )

            # Find AAB files
            aab_dir = build_dir / "bundle" / variant
            if aab_dir.exists():
                for aab_file in aab_dir.glob("*.aab"):
                    artifacts.append(
                        {
                            "type": "aab",
                            "path": str(aab_file),
                            "size": aab_file.stat().st_size,
                            "variant": variant,
                        }
                    )

        return artifacts

    def _find_maven_artifacts(self, project_root: str, variant: str) -> List[Dict[str, Any]]:
        """Find Maven build artifacts."""
        artifacts = []
        target_dir = Path(project_root) / "target"

        if target_dir.exists():
            for jar_file in target_dir.glob("*.jar"):
                artifacts.append(
                    {
                        "type": "jar",
                        "path": str(jar_file),
                        "size": jar_file.stat().st_size,
                        "variant": variant,
                    }
                )

        return artifacts
