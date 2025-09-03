#!/usr/bin/env python3
"""
Intelligent Base Classes for LSP - like Tool Enhancement

This module provides base classes and utilities that enhance all MCP tools
with intelligent, LSP - like capabilities for Kotlin development.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import our existing intelligence modules
from ai.intelligent_analysis import CodeIssue, KotlinAnalyzer, RefactoringType
from ai.llm_integration import CodeGenerationRequest, CodeType, LLMIntegration
from tools.intelligent_navigation import IntelligentSymbolNavigation
from tools.intelligent_refactoring import IntelligentRefactoringTools


@dataclass
class IntelligentToolContext:
    """Context information for intelligent tool execution."""

    project_path: str
    tool_name: str
    current_file: Optional[str] = None
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    user_intent: Optional[str] = None
    project_symbols: Optional[Dict[str, Any]] = None
    project_analysis: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IntelligentToolResult:
    """Enhanced result from intelligent tool execution."""

    success: bool
    primary_result: Any
    intelligence_insights: Optional[Dict[str, Any]] = None
    refactoring_suggestions: Optional[List[Dict[str, Any]]] = None
    code_issues: Optional[List[Dict[str, Any]]] = None
    symbol_information: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    related_files: Optional[List[str]] = None
    impact_analysis: Optional[Dict[str, Any]] = None

    def to_mcp_response(self) -> Dict[str, Any]:
        """Convert to MCP response format."""
        content = []

        # Primary result
        if isinstance(self.primary_result, str):
            content.append({"type": "text", "text": self.primary_result})
        else:
            content.append({"type": "text", "text": json.dumps(self.primary_result, indent=2)})

        # Add intelligence insights if available
        if self.intelligence_insights:
            content.append(
                {
                    "type": "text",
                    "text": f"\n🧠 **Intelligence Insights:**\n{json.dumps(self.intelligence_insights, indent = 2)}",
                }
            )

        # Add refactoring suggestions
        if self.refactoring_suggestions:
            content.append(
                {
                    "type": "text",
                    "text": f"\n🔧 **Refactoring Suggestions:**\n{json.dumps(self.refactoring_suggestions, indent = 2)}",
                }
            )

        # Add code issues
        if self.code_issues:
            content.append(
                {
                    "type": "text",
                    "text": f"\n⚠️ **Code Quality Issues:**\n{json.dumps(self.code_issues, indent = 2)}",
                }
            )

        # Add symbol information
        if self.symbol_information:
            content.append(
                {
                    "type": "text",
                    "text": f"\n📋 **Symbol Analysis:**\n{json.dumps(self.symbol_information, indent = 2)}",
                }
            )

        return {"content": content}


class IntelligentToolBase(ABC):
    """
    Base class for all intelligent MCP tools.

    Provides LSP - like capabilities including:
    - Semantic code analysis
    - Symbol resolution and navigation
    - Intelligent refactoring suggestions
    - Context - aware code completion
    - Impact analysis and safety checks
    """

    def __init__(self, project_path: str, security_manager: Optional[Any] = None):
        self.project_path = Path(project_path)
        self.security_manager = security_manager

        # Initialize intelligent components
        self.analyzer = KotlinAnalyzer()
        self.llm_integration = LLMIntegration(security_manager)
        self.symbol_navigation = IntelligentSymbolNavigation()
        self.refactoring_tools = IntelligentRefactoringTools(project_path, security_manager)

        # Cache for project - wide analysis
        self._project_symbols: Optional[Dict[str, Any]] = None
        self._project_analysis: Optional[Dict[str, Any]] = None

    async def execute_with_intelligence(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> IntelligentToolResult:
        """
        Execute the tool with full intelligence capabilities.

        This method:
        1. Performs semantic analysis of relevant code
        2. Executes the core tool functionality
        3. Provides intelligent insights and suggestions
        4. Analyzes impact and safety considerations
        """
        try:
            # Ensure project symbols are indexed
            await self._ensure_project_indexed()

            # Perform pre - execution analysis
            pre_analysis = await self._analyze_context(context)

            # Execute the core tool functionality
            core_result = await self._execute_core_functionality(context, arguments)

            # Perform post - execution analysis and enhancement
            intelligence_insights = await self._generate_intelligence_insights(
                context, arguments, core_result, pre_analysis
            )

            # Generate refactoring suggestions
            refactoring_suggestions = await self._generate_refactoring_suggestions(
                context, pre_analysis
            )

            # Analyze impact of the changes
            impact_analysis = await self._analyze_impact(context, core_result)

            return IntelligentToolResult(
                success=True,
                primary_result=core_result,
                intelligence_insights=intelligence_insights,
                refactoring_suggestions=refactoring_suggestions,
                code_issues=pre_analysis.get("code_issues", []),
                symbol_information=pre_analysis.get("symbols", {}),
                impact_analysis=impact_analysis,
                related_files=pre_analysis.get("related_files", []),
            )

        except Exception as e:
            return IntelligentToolResult(
                success=False,
                primary_result=f"Tool execution failed: {str(e)}",
                intelligence_insights={"error": str(e)},
            )

    @abstractmethod
    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Execute the core functionality of the specific tool."""
        pass

    async def _ensure_project_indexed(self) -> None:
        """Ensure project symbols are indexed for intelligent operations."""
        if self._project_symbols is None:
            index_result = await self.symbol_navigation.index_project(str(self.project_path))
            self._project_symbols = index_result

    async def _analyze_context(self, context: IntelligentToolContext) -> Dict[str, Any]:
        """Analyze the current context for intelligent insights."""
        analysis: Dict[str, Any] = {
            "symbols": {},
            "code_issues": [],
            "related_files": [],
            "complexity_metrics": {},
        }

        if context.current_file and Path(context.current_file).exists():
            # Analyze the current file
            with open(context.current_file, "r", encoding="utf-8") as f:
                content = f.read()

            file_analysis = self.analyzer.analyze_file(context.current_file, content)
            analysis.update(file_analysis)

            # Find related files based on imports and usage
            related_files = await self._find_related_files(context.current_file, content)
            analysis["related_files"] = related_files

        return analysis

    async def _generate_intelligence_insights(
        self,
        context: IntelligentToolContext,
        arguments: Dict[str, Any],
        core_result: Any,
        pre_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate intelligent insights about the tool execution."""
        insights = {
            "execution_context": {
                "tool_purpose": self.__class__.__name__,
                "project_context": str(self.project_path),
                "affected_files": pre_analysis.get("related_files", []),
            },
            "code_quality_assessment": {
                "issues_found": len(pre_analysis.get("code_issues", [])),
                "symbols_analyzed": len(pre_analysis.get("symbols", [])),
                "complexity_score": pre_analysis.get("complexity_metrics", {}).get(
                    "total_complexity", 0
                ),
            },
            "recommendations": await self._generate_recommendations(context, pre_analysis),
        }

        return insights

    async def _generate_refactoring_suggestions(
        self, context: IntelligentToolContext, analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate context - aware refactoring suggestions."""
        suggestions = []

        if context.current_file:
            refactoring_result = await self.refactoring_tools.suggest_intelligent_refactoring(
                context.current_file,
                context.user_intent or "improve code quality",
                context.selection_start,
                context.selection_end,
            )

            if refactoring_result.get("success"):
                suggestions = refactoring_result.get("suggestions", [])

        return suggestions

    async def _analyze_impact(self, context: IntelligentToolContext, result: Any) -> Dict[str, Any]:
        """Analyze the impact of the tool execution."""
        impact = {
            "files_modified": [],
            "symbols_affected": [],
            "breaking_changes_risk": "low",
            "test_impact": "minimal",
            "build_impact": "none",
            "recommendations": [],
        }

        # This is a base implementation - specific tools can override
        if context.current_file:
            impact["files_modified"] = [context.current_file]

        return impact

    async def _find_related_files(self, current_file: str, content: str) -> List[str]:
        """Find files related to the current file through imports and usage."""
        related = []

        # Find imports
        import_pattern = r"import\s+([a - zA - Z0 - 9_.]+)"
        imports = []
        for match in __import__("re").finditer(import_pattern, content):
            imports.append(match.group(1))

        # Convert imports to potential file paths
        for import_path in imports:
            # Convert package.Class to potential file paths
            file_path = import_path.replace(".", "/") + ".kt"
            potential_file = self.project_path / "src" / "main" / "kotlin" / file_path
            if potential_file.exists():
                related.append(str(potential_file))

        return related

    async def _generate_recommendations(
        self, context: IntelligentToolContext, analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate intelligent recommendations based on analysis."""
        recommendations = []

        # Code quality recommendations
        issues = analysis.get("code_issues", [])
        if issues:
            high_priority = [issue for issue in issues if issue.get("severity") == "error"]
            if high_priority:
                recommendations.append(
                    "Address {len(high_priority)} critical code issues before proceeding"
                )

        # Performance recommendations
        complexity = analysis.get("complexity_metrics", {}).get("total_complexity", 0)
        if complexity > 50:  # Arbitrary threshold
            recommendations.append("Consider refactoring to reduce code complexity")

        # Architecture recommendations
        symbols = analysis.get("symbols", [])
        class_count = len([s for s in symbols if s.get("type") == "class"])
        if class_count > 10:  # Large file
            recommendations.append("Consider splitting this file into smaller, focused classes")

        return recommendations


class IntelligentBuildTool(IntelligentToolBase):
    """Enhanced build tool with intelligent analysis."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Execute Gradle build with intelligent analysis."""
        task = arguments.get("task", "assembleDebug")
        clean = arguments.get("clean", False)

        # Pre - build analysis
        build_analysis = await self._analyze_build_configuration()

        # Execute build
        import subprocess

        try:
            if clean:
                clean_result = subprocess.run(
                    ["./gradlew", "clean"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

            build_result = subprocess.run(
                ["./gradlew", task],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600,
            )

            return {
                "build_result": {
                    "task": task,
                    "exit_code": build_result.returncode,
                    "output": build_result.stdout,
                    "errors": build_result.stderr,
                },
                "build_analysis": build_analysis,
                "performance_metrics": await self._analyze_build_performance(),
            }

        except subprocess.TimeoutExpired:
            return {"error": "Build timed out - consider build optimization"}
        except Exception as e:
            return {"error": "Build failed: {str(e)}"}

    async def _analyze_build_configuration(self) -> Dict[str, Any]:
        """Analyze build configuration for optimization opportunities."""
        build_gradle = self.project_path / "build.gradle.kts"
        if not build_gradle.exists():
            build_gradle = self.project_path / "build.gradle"

        if not build_gradle.exists():
            return {"error": "No build.gradle file found"}

        with open(build_gradle, "r") as f:
            content = f.read()

        optimization_opportunities: List[str] = []
        analysis = {
            "kotlin_version": self._extract_kotlin_version(content),
            "dependencies_count": len(
                __import__("re").findall(r"implementation|api|compile", content)
            ),
            "build_features": self._analyze_build_features(content),
            "optimization_opportunities": optimization_opportunities,
        }

        # Check for optimization opportunities
        if "buildCache" not in content:
            optimization_opportunities.append("Enable build cache for faster incremental builds")

        if "parallel" not in content:
            optimization_opportunities.append("Enable parallel execution")

        return analysis

    def _extract_kotlin_version(self, content: str) -> Optional[str]:
        """Extract Kotlin version from build file."""
        import re

        match = re.search(r'kotlin_version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        return None

    def _analyze_build_features(self, content: str) -> List[str]:
        """Analyze enabled build features."""
        features = []
        feature_patterns = [
            (r"dataBinding\s*{\s * enabled\s*=\s * true", "DataBinding"),
            (r"viewBinding\s*{\s * enabled\s*=\s * true", "ViewBinding"),
            (r"compose\s * true", "Jetpack Compose"),
            (r"buildConfig\s * true", "BuildConfig"),
        ]

        for pattern, feature in feature_patterns:
            if __import__("re").search(pattern, content):
                features.append(feature)

        return features

    async def _analyze_build_performance(self) -> Dict[str, Any]:
        """Analyze build performance metrics."""
        # This would integrate with Gradle build scans in a real implementation
        return {
            "estimated_build_time": "30 - 60 seconds",
            "optimization_potential": "medium",
            "bottlenecks": ["annotation processing", "resource compilation"],
        }


class IntelligentTestTool(IntelligentToolBase):
    """Enhanced test tool with intelligent test analysis."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Execute tests with intelligent analysis."""
        test_type = arguments.get("test_type", "unit")

        # Pre - test analysis
        test_analysis = await self._analyze_test_coverage()

        # Execute tests
        import subprocess

        task_map = {
            "unit": "test",
            "instrumented": "connectedAndroidTest",
            "all": "test connectedAndroidTest",
        }

        task = task_map.get(test_type, "test")

        try:
            result = subprocess.run(
                ["./gradlew"] + task.split(),
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=900,
            )

            return {
                "test_result": {
                    "test_type": test_type,
                    "exit_code": result.returncode,
                    "output": result.stdout,
                    "errors": result.stderr,
                },
                "test_analysis": test_analysis,
                "coverage_report": await self._generate_coverage_insights(result.stdout),
            }

        except Exception as e:
            return {"error": "Test execution failed: {str(e)}"}

    async def _analyze_test_coverage(self) -> Dict[str, Any]:
        """Analyze test coverage and identify gaps."""
        test_dirs = [
            self.project_path / "src" / "test" / "kotlin",
            self.project_path / "src" / "androidTest" / "kotlin",
        ]

        test_files = []
        for test_dir in test_dirs:
            if test_dir.exists():
                test_files.extend(list(test_dir.rglob("*.kt")))

        source_files = list((self.project_path / "src" / "main" / "kotlin").rglob("*.kt"))

        return {
            "total_test_files": len(test_files),
            "total_source_files": len(source_files),
            "estimated_coverage": "{min(100, (len(test_files) / max(len(source_files), 1)) * 100):.1f}%",
            "missing_tests": await self._identify_missing_tests(source_files, test_files),
        }

    async def _identify_missing_tests(
        self, source_files: List[Path], test_files: List[Path]
    ) -> List[str]:
        """Identify source files without corresponding tests."""
        test_names = {f.stem.replace("Test", "").replace("Spec", "") for f in test_files}
        source_names = {f.stem for f in source_files}

        missing = []
        for source_name in source_names:
            if source_name not in test_names and not source_name.endswith(
                "Activity"
            ):  # Skip activities for now
                missing.append(source_name)

        return missing[:10]  # Limit to first 10

    async def _generate_coverage_insights(self, test_output: str) -> Dict[str, Any]:
        """Generate insights from test output."""
        performance_issues: List[str] = []
        insights = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "performance_issues": performance_issues,
        }

        # Parse test output for basic metrics
        import re

        test_pattern = r"(\d+) tests? completed"
        match = re.search(test_pattern, test_output)
        if match:
            insights["tests_run"] = int(match.group(1))

        # Look for performance issues
        if "SLOW" in test_output or "timeout" in test_output.lower():
            performance_issues.append("Some tests are running slowly")

        return insights
