#!/usr/bin/env python3
"""Intelligent build and project tools that leverage existing utilities."""

from pathlib import Path
from typing import Any, Dict

from tools.build_optimization import BuildOptimizationTools
from tools.gradle_tools import GradleTools
from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext
from tools.project_analysis import ProjectAnalysisTools


class IntelligentGradleBuildTool(IntelligentToolBase):
    """Run Gradle builds with intelligent context."""

    def __init__(self, project_path: str, security_manager: Any | None = None) -> None:
        super().__init__(project_path, security_manager)
        self.gradle_tools = GradleTools(Path(project_path), security_manager)

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        return await self.gradle_tools.gradle_build(arguments)


class IntelligentProjectAnalysisTool(IntelligentToolBase):
    """Analyze project structure and configuration."""

    def __init__(self, project_path: str, security_manager: Any | None = None) -> None:
        super().__init__(project_path, security_manager)
        self.project_tools = ProjectAnalysisTools(Path(project_path), security_manager)

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        return await self.project_tools.analyze_project(arguments)


class IntelligentProjectRefactorTool(IntelligentToolBase):
    """Analyze and refactor an entire project."""

    def __init__(self, project_path: str, security_manager: Any | None = None) -> None:
        super().__init__(project_path, security_manager)
        self.project_tools = ProjectAnalysisTools(Path(project_path), security_manager)

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        return await self.project_tools.analyze_and_refactor_project(arguments)


class IntelligentBuildOptimizationTool(IntelligentToolBase):
    """Optimize build performance and configuration."""

    def __init__(self, project_path: str, security_manager: Any | None = None) -> None:
        super().__init__(project_path, security_manager)
        self.optimization_tools = BuildOptimizationTools(Path(project_path), security_manager)

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        return await self.optimization_tools.optimize_build_performance(arguments)
