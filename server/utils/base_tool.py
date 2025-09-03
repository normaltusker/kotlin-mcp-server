"""
Base class for MCP tools with project root enforcement.
"""

import os
from typing import Any, Dict, Optional

from server.utils.no_cwd_guard import assert_not_server_cwd
from server.utils.project_resolver import ProjectRootError, resolve_project_root


class BaseMCPTool:
    """Base class for all MCP tools with project root enforcement."""

    def __init__(self, security_manager: Optional[Any] = None):
        """Initialize base tool."""
        self.security_manager = security_manager

    def resolve_project_root(
        self, arguments: Dict[str, Any], ide_context: Optional[dict] = None
    ) -> str:
        """
        Resolve project root from arguments with IDE fallback.

        Args:
            arguments: Tool arguments
            ide_context: IDE metadata from MCP client

        Returns:
            Absolute project root path

        Raises:
            ProjectRootError: If project root cannot be resolved
        """
        try:
            project_root = resolve_project_root(arguments, ide_meta=ide_context)
            assert_not_server_cwd(project_root)
            return project_root
        except ProjectRootError as exc:
            # Re-raise with helpful context
            raise ProjectRootError(
                f"Tool {self.__class__.__name__} requires project_root. "
                "Pass project_root parameter or set PROJECT_PATH environment variable."
            ) from exc

    def validate_path_under_project(self, file_path: str, project_root: str) -> str:
        """
        Validate that a file path is under the project root.

        Args:
            file_path: File path to validate
            project_root: Project root directory

        Returns:
            Absolute path under project root

        Raises:
            ValueError: If path is outside project root
        """
        if os.path.isabs(file_path):
            abs_path = file_path
        else:
            abs_path = os.path.join(project_root, file_path)

        abs_path = os.path.abspath(abs_path)
        abs_project_root = os.path.abspath(project_root)

        # Check if path is under project root
        try:
            os.path.relpath(abs_path, abs_project_root)
        except ValueError as exc:
            # Happens on Windows when paths are on different drives
            raise ValueError(f"Path {file_path} is outside project root {project_root}") from exc

        if not abs_path.startswith(abs_project_root + os.sep) and abs_path != abs_project_root:
            raise ValueError(f"Path {file_path} is outside project root {project_root}")

        return abs_path

    def normalize_inputs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize input arguments with camelCase/snake_case synonyms.

        Args:
            arguments: Raw input arguments

        Returns:
            Normalized arguments with standard keys
        """
        # Standard normalization for common parameters
        normalized = dict(arguments)

        # Project root
        if "project_root" not in normalized and "projectRoot" in normalized:
            normalized["project_root"] = normalized.pop("projectRoot")

        # File path
        if "file_path" not in normalized and "filePath" in normalized:
            normalized["file_path"] = normalized.pop("filePath")

        # Build tool
        if "build_tool" not in normalized and "buildTool" in normalized:
            normalized["build_tool"] = normalized.pop("buildTool")

        # Skip tests
        if "skip_tests" not in normalized and "skipTests" in normalized:
            normalized["skip_tests"] = normalized.pop("skipTests")

        # Max findings
        if "max_findings" not in normalized and "maxFindings" in normalized:
            normalized["max_findings"] = normalized.pop("maxFindings")

        return normalized
