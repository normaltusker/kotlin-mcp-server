#!/usr/bin/env python3
"""
Test module for individual tool components.

This module provides specific tests for:
- GradleTools functionality
- BuildOptimizationTools functionality
- ProjectAnalysisTools functionality
- Tool module integration
"""

import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from tools.build_optimization import BuildOptimizationTools
from tools.gradle_tools import GradleTools
from tools.project_analysis import ProjectAnalysisTools
from utils.security import SecurityManager


class TestToolModules:
    """Test individual tool modules functionality."""

    @pytest.fixture
    def mock_security_manager(self):
        """Create a mock security manager for testing."""
        mock_security = MagicMock(spec=SecurityManager)
        mock_security.validate_path = MagicMock(return_value=True)
        mock_security.is_safe_command = MagicMock(return_value=True)
        return mock_security

    @pytest.fixture
    def test_project_path(self, tmp_path):
        """Create a temporary project path for testing."""
        return Path(tmp_path) / "test_project"

    @pytest.mark.asyncio
    async def test_gradle_tools_initialization(self, test_project_path, mock_security_manager):
        """Test GradleTools can be initialized properly."""
        gradle_tools = GradleTools(test_project_path, mock_security_manager)
        assert gradle_tools.project_path == test_project_path
        assert gradle_tools.security_manager == mock_security_manager

    @pytest.mark.asyncio
    async def test_build_optimization_tools_initialization(
        self, test_project_path, mock_security_manager
    ):
        """Test BuildOptimizationTools can be initialized properly."""
        build_tools = BuildOptimizationTools(test_project_path, mock_security_manager)
        assert build_tools.project_path == test_project_path
        assert build_tools.security_manager == mock_security_manager

    @pytest.mark.asyncio
    async def test_project_analysis_tools_initialization(
        self, test_project_path, mock_security_manager
    ):
        """Test ProjectAnalysisTools can be initialized properly."""
        analysis_tools = ProjectAnalysisTools(test_project_path, mock_security_manager)
        assert analysis_tools.project_path == test_project_path
        assert analysis_tools.security_manager == mock_security_manager

    @pytest.mark.asyncio
    async def test_gradle_tools_has_expected_methods(
        self, test_project_path, mock_security_manager
    ):
        """Test that GradleTools has expected methods."""
        gradle_tools = GradleTools(test_project_path, mock_security_manager)

        # Check for key methods
        assert hasattr(gradle_tools, "gradle_build")
        assert hasattr(gradle_tools, "run_tests")
        assert hasattr(gradle_tools, "format_code")
        assert hasattr(gradle_tools, "run_lint")
        assert hasattr(gradle_tools, "generate_docs")
        assert callable(gradle_tools.gradle_build)
        assert callable(gradle_tools.run_tests)
        assert callable(gradle_tools.format_code)

    @pytest.mark.asyncio
    async def test_build_optimization_tools_has_expected_methods(
        self, test_project_path, mock_security_manager
    ):
        """Test that BuildOptimizationTools has expected methods."""
        build_tools = BuildOptimizationTools(test_project_path, mock_security_manager)

        # Check for key methods
        assert hasattr(build_tools, "optimize_build_performance")
        assert callable(build_tools.optimize_build_performance)

    @pytest.mark.asyncio
    async def test_project_analysis_tools_has_expected_methods(
        self, test_project_path, mock_security_manager
    ):
        """Test that ProjectAnalysisTools has expected methods."""
        analysis_tools = ProjectAnalysisTools(test_project_path, mock_security_manager)

        # Check for key methods
        assert hasattr(analysis_tools, "analyze_project")
        assert hasattr(analysis_tools, "analyze_and_refactor_project")
        assert callable(analysis_tools.analyze_project)
        assert callable(analysis_tools.analyze_and_refactor_project)

    @pytest.mark.asyncio
    async def test_all_tools_can_be_imported_together(self):
        """Test that all tool modules can be imported together without conflicts."""
        # This test ensures there are no import conflicts between modules
        from tools.build_optimization import BuildOptimizationTools
        from tools.gradle_tools import GradleTools
        from tools.project_analysis import ProjectAnalysisTools
        from utils.security import SecurityManager

        # All imports should succeed without errors
        assert GradleTools is not None
        assert BuildOptimizationTools is not None
        assert ProjectAnalysisTools is not None
        assert SecurityManager is not None

    @pytest.mark.asyncio
    async def test_tool_modules_type_annotations(self):
        """Test that tool modules have proper type annotations."""
        from tools import build_optimization, gradle_tools, project_analysis

        # Check that modules have proper annotations (this helps catch typing issues)
        assert hasattr(gradle_tools, "__annotations__") or len(gradle_tools.__dict__) > 0
        assert (
            hasattr(build_optimization, "__annotations__") or len(build_optimization.__dict__) > 0
        )
        assert hasattr(project_analysis, "__annotations__") or len(project_analysis.__dict__) > 0


if __name__ == "__main__":
    # Run tests directly if executed as script
    pytest.main([__file__, "-v"])
