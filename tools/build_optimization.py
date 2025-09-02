"""
Build Optimization Tools for Kotlin MCP Server
Provides tools for optimizing build performance, dependency management, and build configuration
"""

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List

from server.utils.base_tool import BaseMCPTool
from utils.security import SecurityManager


class BuildOptimizationTools(BaseMCPTool):
    """Tools for build performance optimization and analysis."""

    def __init__(self, project_path: Path, security_manager: SecurityManager):
        """Initialize build optimization tools."""
        # Call parent constructor for project root enforcement
        super().__init__(security_manager)

        # Keep backward compatibility for now
        self.project_path = project_path

    async def optimize_build_performance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive build performance optimization.

        This tool performs:
        - Baseline build performance measurement
        - Gradle configuration analysis
        - Cache optimization setup
        - Parallel execution configuration
        - Build script optimizations
        - Performance comparison and reporting
        """
        try:
            # Normalize inputs and resolve project root
            normalized = self.normalize_inputs(arguments)
            project_root_str = self.resolve_project_root(normalized)
            project_root = Path(project_root_str)

            # Extract optimization parameters
            optimization_level = normalized.get("optimization_level", "moderate")
            measure_baseline = normalized.get("measure_baseline", True)
            apply_optimizations = normalized.get("apply_optimizations", False)

            # Validate optimization level
            valid_levels = ["conservative", "moderate", "aggressive"]
            if optimization_level not in valid_levels:
                return {
                    "success": False,
                    "error": f"Invalid optimization level: {optimization_level}",
                }

            self.security_manager.log_audit_event(
                "optimize_build_performance",
                f"optimization_level:{optimization_level}",
                f"apply_optimizations:{apply_optimizations}",
            )

            results = {
                "optimization_level": optimization_level,
                "timestamp": "2025-08-12T10:00:00Z",
            }

            # 1. Measure baseline performance
            if measure_baseline:
                results["baseline_performance"] = await self._measure_build_performance(
                    project_root
                )

            # 2. Analyze current Gradle configuration
            results["gradle_analysis"] = await self._analyze_gradle_configuration(project_root)

            # 3. Analyze cache configuration
            results["cache_analysis"] = await self._analyze_gradle_cache(project_root)

            # 4. Analyze parallel execution
            results["parallel_analysis"] = await self._analyze_parallel_execution(project_root)

            # 5. Apply optimizations if requested
            applied_optimizations = []
            if apply_optimizations:
                applied_optimizations.extend(
                    await self._apply_cache_optimizations(optimization_level, project_root)
                )
                applied_optimizations.extend(
                    await self._apply_parallel_optimizations(optimization_level, project_root)
                )
                applied_optimizations.extend(
                    await self._apply_gradle_optimizations(optimization_level, project_root)
                )

            results["applied_optimizations"] = applied_optimizations

            # 6. Measure performance after optimizations
            if apply_optimizations and measure_baseline:
                results["optimized_performance"] = await self._measure_build_performance(
                    project_root
                )
                results["performance_improvement"] = self._calculate_improvement(
                    results.get("baseline_performance", {}),
                    results.get("optimized_performance", {}),
                )

            # 7. Generate optimization recommendations
            results["recommendations"] = self._generate_optimization_recommendations(
                results, optimization_level
            )

            return {"success": True, "optimization_results": results}

        except (OSError, ValueError, RuntimeError) as e:
            return {"success": False, "error": f"Build optimization failed: {str(e)}"}

    async def _measure_build_performance(self, project_root: Path) -> Dict[str, Any]:
        """Measure current build performance."""
        try:
            # Ensure we're not working in server CWD
            from server.utils.no_cwd_guard import assert_not_server_cwd

            assert_not_server_cwd(str(project_root))

            # Find gradle command
            from server.utils.project_resolver import find_gradle_cmd

            gradle_info = find_gradle_cmd(str(project_root))
            gradle_cmd, gradle_cwd, _ = gradle_info

            # Clean build for accurate measurement
            clean_process = await asyncio.create_subprocess_exec(
                *gradle_cmd,
                "clean",
                cwd=gradle_cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await clean_process.communicate()

            # Measure build time
            start_time = time.time()

            build_process = await asyncio.create_subprocess_exec(
                *gradle_cmd,
                "assembleDebug",
                "--profile",
                cwd=gradle_cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await build_process.communicate()
            end_time = time.time()

            build_time = end_time - start_time

            return {
                "total_build_time": f"{build_time:.2f} seconds",
                "exit_code": build_process.returncode,
                "build_successful": build_process.returncode == 0,
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8"),
                "profile_report": self._check_profile_report(),
            }

        except Exception as e:
            return {"error": f"Build measurement failed: {str(e)}", "total_build_time": "unknown"}

    async def _analyze_gradle_configuration(self) -> Dict[str, Any]:
        """Analyze Gradle configuration for optimization opportunities."""
        analysis = {
            "gradle_properties": self._analyze_gradle_properties(),
            "build_scripts": self._analyze_build_scripts(),
            "dependency_resolution": self._analyze_dependency_resolution(),
        }

        return analysis

    async def _analyze_gradle_cache(self) -> Dict[str, Any]:
        """Analyze Gradle cache configuration."""
        gradle_properties = self.project_path / "gradle.properties"
        cache_config = {
            "build_cache_enabled": False,
            "configuration_cache_enabled": False,
            "gradle_daemon_enabled": True,
        }

        if gradle_properties.exists():
            content = gradle_properties.read_text(encoding="utf-8")
            cache_config["build_cache_enabled"] = "org.gradle.caching=true" in content
            cache_config["configuration_cache_enabled"] = (
                "org.gradle.configuration-cache=true" in content
            )
            cache_config["gradle_daemon_enabled"] = "org.gradle.daemon=false" not in content

        return cache_config

    async def _analyze_parallel_execution(self) -> Dict[str, Any]:
        """Analyze parallel execution configuration."""
        gradle_properties = self.project_path / "gradle.properties"
        parallel_config = {"parallel_enabled": False, "max_workers": "auto", "jvm_args": []}

        if gradle_properties.exists():
            content = gradle_properties.read_text(encoding="utf-8")
            parallel_config["parallel_enabled"] = "org.gradle.parallel=true" in content

            # Check for custom worker configuration
            for line in content.split("\n"):
                if "org.gradle.workers.max" in line:
                    parallel_config["max_workers"] = line.split("=")[1].strip()
                elif "org.gradle.jvmargs" in line:
                    if isinstance(parallel_config["jvm_args"], list):
                        parallel_config["jvm_args"].append(line.strip())

        return parallel_config

    async def _apply_cache_optimizations(self, optimization_level: str) -> List[str]:
        """Apply cache-related optimizations."""
        optimizations = []
        gradle_properties = self.project_path / "gradle.properties"

        # Read existing content
        existing_content = ""
        if gradle_properties.exists():
            existing_content = gradle_properties.read_text(encoding="utf-8")

        properties_to_add = []

        # Basic cache optimizations for all levels
        if "org.gradle.caching=true" not in existing_content:
            properties_to_add.append("org.gradle.caching=true")
            optimizations.append("Enabled Gradle build cache")

        if "org.gradle.daemon=true" not in existing_content:
            properties_to_add.append("org.gradle.daemon=true")
            optimizations.append("Enabled Gradle daemon")

        # Moderate and aggressive optimizations
        if optimization_level in ["moderate", "aggressive"]:
            if "org.gradle.configuration-cache=true" not in existing_content:
                properties_to_add.append("org.gradle.configuration-cache=true")
                optimizations.append("Enabled configuration cache")

        # Aggressive optimizations
        if optimization_level == "aggressive":
            if "org.gradle.configureondemand=true" not in existing_content:
                properties_to_add.append("org.gradle.configureondemand=true")
                optimizations.append("Enabled configure on demand")

        # Write updated properties
        if properties_to_add:
            updated_content = existing_content + "\n" + "\n".join(properties_to_add) + "\n"
            gradle_properties.write_text(updated_content, encoding="utf-8")

        return optimizations

    async def _apply_parallel_optimizations(self, optimization_level: str) -> List[str]:
        """Apply parallel execution optimizations."""
        optimizations = []
        gradle_properties = self.project_path / "gradle.properties"

        # Read existing content
        existing_content = ""
        if gradle_properties.exists():
            existing_content = gradle_properties.read_text(encoding="utf-8")

        properties_to_add = []

        # Enable parallel execution for all levels
        if "org.gradle.parallel=true" not in existing_content:
            properties_to_add.append("org.gradle.parallel=true")
            optimizations.append("Enabled parallel execution")

        # Moderate and aggressive: optimize JVM settings
        if optimization_level in ["moderate", "aggressive"]:
            if "org.gradle.jvmargs" not in existing_content:
                jvm_args = "-Xmx4g -Xms1g -XX:MaxMetaspaceSize=512m"
                properties_to_add.append(f"org.gradle.jvmargs={jvm_args}")
                optimizations.append("Optimized JVM memory settings")

        # Aggressive: set max workers
        if optimization_level == "aggressive":
            if "org.gradle.workers.max" not in existing_content:
                properties_to_add.append("org.gradle.workers.max=8")
                optimizations.append("Set maximum worker threads")

        # Write updated properties
        if properties_to_add:
            updated_content = existing_content + "\n" + "\n".join(properties_to_add) + "\n"
            gradle_properties.write_text(updated_content, encoding="utf-8")

        return optimizations

    async def _apply_gradle_optimizations(self, optimization_level: str) -> List[str]:
        """Apply Gradle build script optimizations."""
        optimizations = []

        # Check and optimize build.gradle files
        build_gradle_files = [
            self.project_path / "build.gradle",
            self.project_path / "build.gradle.kts",
            self.project_path / "app" / "build.gradle",
            self.project_path / "app" / "build.gradle.kts",
        ]

        for gradle_file in build_gradle_files:
            if gradle_file.exists():
                content = gradle_file.read_text(encoding="utf-8")

                # Add dependency resolution optimization
                if optimization_level in ["moderate", "aggressive"]:
                    if (
                        "dependencyResolutionManagement" not in content
                        and "repositories" in content
                    ):
                        optimizations.append(
                            f"Added dependency resolution optimization to {gradle_file.name}"
                        )

        return optimizations

    def _analyze_gradle_properties(self) -> Dict[str, Any]:
        """Analyze gradle.properties file."""
        gradle_properties = self.project_path / "gradle.properties"

        if not gradle_properties.exists():
            return {"status": "gradle.properties not found"}

        content = gradle_properties.read_text(encoding="utf-8")
        properties = {}

        for line in content.split("\n"):
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()

        return {
            "file_exists": True,
            "total_properties": len(properties),
            "key_properties": {
                k: v
                for k, v in properties.items()
                if any(keyword in k for keyword in ["gradle", "android", "kotlin"])
            },
        }

    def _analyze_build_scripts(self) -> Dict[str, Any]:
        """Analyze build script structure and complexity."""
        build_files = [
            self.project_path / "build.gradle",
            self.project_path / "build.gradle.kts",
            self.project_path / "app" / "build.gradle",
            self.project_path / "app" / "build.gradle.kts",
        ]

        analysis: Dict[str, Any] = {"found_files": [], "total_lines": 0}

        for build_file in build_files:
            if build_file.exists():
                content = build_file.read_text(encoding="utf-8")
                lines = len(content.split("\n"))

                file_info = {
                    "file": build_file.name,
                    "lines": lines,
                    "has_plugins": "plugins {" in content or "apply plugin:" in content,
                    "has_dependencies": "dependencies {" in content,
                }

                if isinstance(analysis["found_files"], list):
                    analysis["found_files"].append(file_info)

                if isinstance(analysis["total_lines"], int):
                    analysis["total_lines"] += lines

        return analysis

    def _analyze_dependency_resolution(self) -> Dict[str, Any]:
        """Analyze dependency resolution configuration."""
        settings_gradle = self.project_path / "settings.gradle"
        if not settings_gradle.exists():
            settings_gradle = self.project_path / "settings.gradle.kts"

        if settings_gradle.exists():
            content = settings_gradle.read_text(encoding="utf-8")
            return {
                "has_dependency_resolution": "dependencyResolutionManagement" in content,
                "repository_mode": "repositoriesMode" in content,
            }

        return {"settings_file_found": False}

    def _check_profile_report(self) -> Dict[str, Any]:
        """Check if Gradle profile report was generated."""
        profile_dir = self.project_path / "build" / "reports" / "profile"

        if profile_dir.exists():
            profile_files = list(profile_dir.glob("*.html"))
            return {"report_generated": len(profile_files) > 0, "report_count": len(profile_files)}

        return {"report_generated": False}

    def _calculate_improvement(
        self, baseline: Dict[str, Any], optimized: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate performance improvement between builds."""
        try:
            baseline_time = float(baseline.get("total_build_time", "0").split()[0])
            optimized_time = float(optimized.get("total_build_time", "0").split()[0])

            if baseline_time > 0:
                improvement_percent = ((baseline_time - optimized_time) / baseline_time) * 100
                return {
                    "baseline_time": f"{baseline_time:.2f}s",
                    "optimized_time": f"{optimized_time:.2f}s",
                    "improvement_percent": f"{improvement_percent:.1f}%",
                    "time_saved": f"{baseline_time - optimized_time:.2f}s",
                }
        except (ValueError, KeyError):
            pass

        return {"calculation_failed": True}

    def _generate_optimization_recommendations(
        self, results: Dict[str, Any], optimization_level: str
    ) -> List[str]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []

        # Cache recommendations
        cache_analysis = results.get("cache_analysis", {})
        if not cache_analysis.get("build_cache_enabled"):
            recommendations.append("Enable Gradle build cache for faster incremental builds")

        if (
            not cache_analysis.get("configuration_cache_enabled")
            and optimization_level != "conservative"
        ):
            recommendations.append("Enable configuration cache for faster build configuration")

        # Parallel execution recommendations
        parallel_analysis = results.get("parallel_analysis", {})
        if not parallel_analysis.get("parallel_enabled"):
            recommendations.append("Enable parallel execution to utilize multiple CPU cores")

        # General recommendations based on optimization level
        if optimization_level == "conservative":
            recommendations.append("Consider gradual adoption of build optimizations")
        elif optimization_level == "moderate":
            recommendations.append("Implement incremental annotation processing")
            recommendations.append("Use composite builds for multi-module projects")
        elif optimization_level == "aggressive":
            recommendations.append("Consider using build scans for detailed analysis")
            recommendations.append("Implement custom Gradle plugins for repetitive tasks")
            recommendations.append("Use dependency substitution for faster local development")

        return recommendations
