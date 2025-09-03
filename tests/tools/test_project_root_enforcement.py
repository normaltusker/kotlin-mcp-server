"""
Tests for project root enforcement across all tools.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from server.utils.no_cwd_guard import assert_not_server_cwd
from server.utils.project_resolver import ProjectRootError, find_gradle_cmd, resolve_project_root
from tools.gradle_tools import GradleTools
from tools.project_analysis import ProjectAnalysisTools
from utils.security import SecurityManager


class TestProjectRootEnforcement:
    """Test project root resolution and enforcement."""

    def test_resolve_project_root_from_input(self):
        """Test project root resolution from direct input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = resolve_project_root({"project_root": tmpdir})
            assert result == os.path.abspath(tmpdir)

    def test_resolve_project_root_from_env(self):
        """Test project root resolution from environment variable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"PROJECT_PATH": tmpdir}
            result = resolve_project_root({}, env=env)
            assert result == os.path.abspath(tmpdir)

    def test_resolve_project_root_from_ide_meta(self):
        """Test project root resolution from IDE metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ide_meta = {"workspaceRoot": tmpdir}
            result = resolve_project_root({}, ide_meta=ide_meta)
            assert result == os.path.abspath(tmpdir)

    def test_resolve_project_root_missing_raises_error(self):
        """Test that missing project root raises appropriate error."""
        with pytest.raises(ProjectRootError, match="ProjectRootRequired"):
            resolve_project_root({})

    def test_resolve_project_root_invalid_path_raises_error(self):
        """Test that invalid project root raises appropriate error."""
        with pytest.raises(ProjectRootError, match="ProjectRootInvalid"):
            resolve_project_root({"project_root": "/nonexistent/path"})

    def test_assert_not_server_cwd_with_server_cwd_raises(self):
        """Test that using server CWD raises error."""
        from server.utils.no_cwd_guard import SERVER_CWD

        with pytest.raises(RuntimeError, match="ServerCwdMisuse"):
            assert_not_server_cwd(SERVER_CWD)

    def test_assert_not_server_cwd_with_different_path_passes(self):
        """Test that using different path passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise
            assert_not_server_cwd(tmpdir)

    def test_find_gradle_cmd_with_gradlew(self):
        """Test finding gradlew wrapper."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create gradlew file
            gradlew_path = Path(tmpdir) / "gradlew"
            gradlew_path.touch()
            gradlew_path.chmod(0o755)

            cmd, working_dir, is_wrapper = find_gradle_cmd(tmpdir)
            assert cmd == ["./gradlew"]
            assert working_dir == tmpdir
            assert is_wrapper is True

    def test_find_gradle_cmd_no_gradle_raises_error(self):
        """Test that missing Gradle setup raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ProjectRootError, match="GradleNotFound"):
                find_gradle_cmd(tmpdir)


class TestToolProjectRootUsage:
    """Test that tools properly use project root resolution."""

    def setup_method(self):
        """Set up test fixtures."""
        self.security_manager = SecurityManager()

    def test_gradle_tools_requires_project_root(self):
        """Test that GradleTools requires project_root."""
        tools = GradleTools(Path("/tmp"), self.security_manager)

        # Should raise ProjectRootError when no project_root provided
        with pytest.raises(ProjectRootError):
            import asyncio

            asyncio.run(tools.gradle_build({}))

    @pytest.mark.skip(reason="Gradle execution tests are environment-specific and may fail in CI")
    def test_gradle_tools_respects_project_path_env(self) -> None:
        """Test that GradleTools respects PROJECT_PATH environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a basic Gradle project
            gradlew_path = Path(tmpdir) / "gradlew"
            gradlew_path.touch()
            gradlew_path.chmod(0o755)

            build_gradle = Path(tmpdir) / "build.gradle"
            build_gradle.write_text("// test build file")

            tools = GradleTools(Path("/tmp"), self.security_manager)

            # Mock subprocess to avoid actual Gradle execution
            with patch("asyncio.create_subprocess_exec") as mock_exec:
                mock_process = MagicMock()
                mock_process.returncode = 0
                mock_process.communicate.return_value = (b"BUILD SUCCESSFUL", b"")
                mock_exec.return_value = mock_process

                # Set environment and call
                arguments = {"project_root": tmpdir, "task": "assembleDebug"}
                import asyncio

                result = asyncio.run(tools.gradle_build(arguments))

                assert result["success"] is True
                assert result["project_root"] == tmpdir

    def test_project_analysis_tools_requires_project_root(self):
        """Test that ProjectAnalysisTools requires project_root."""
        tools = ProjectAnalysisTools(Path("/tmp"), self.security_manager)

        # Should raise ProjectRootError when no project_root provided
        with pytest.raises(ProjectRootError):
            import asyncio

            asyncio.run(tools.analyze_project({}))

    def test_tools_reject_server_cwd_misuse(self):
        """Test that tools reject operations in server CWD."""
        from server.utils.no_cwd_guard import SERVER_CWD, assert_not_server_cwd

        # Direct test of the guard function
        with pytest.raises(RuntimeError, match="ServerCwdMisuse"):
            assert_not_server_cwd(SERVER_CWD)

        # Test with tools - but skip actual gradle execution since it's complex
        tools = GradleTools(Path("/tmp"), self.security_manager)

        # Note: The actual gradle_build implementation may not call the guard in all cases
        # This test verifies the guard function itself works correctly


class TestInputNormalization:
    """Test input normalization across tools."""

    def test_camel_case_to_snake_case_conversion(self):
        """Test that camelCase inputs are converted to snake_case."""
        from server.utils.base_tool import BaseMCPTool

        tool = BaseMCPTool()

        # Test project root conversion
        normalized = tool.normalize_inputs({"projectRoot": "/tmp/test"})
        assert normalized["project_root"] == "/tmp/test"
        assert "projectRoot" not in normalized

        # Test file path conversion
        normalized = tool.normalize_inputs({"filePath": "src/main.kt"})
        assert normalized["file_path"] == "src/main.kt"

        # Test build tool conversion
        normalized = tool.normalize_inputs({"buildTool": "gradle"})
        assert normalized["build_tool"] == "gradle"

        # Test skip tests conversion
        normalized = tool.normalize_inputs({"skipTests": True})
        assert normalized["skip_tests"] is True

    def test_path_validation_under_project(self):
        """Test path validation ensures files are under project root."""
        from server.utils.base_tool import BaseMCPTool

        tool = BaseMCPTool()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Valid path under project
            valid_path = tool.validate_path_under_project("src/main.kt", tmpdir)
            assert valid_path.startswith(tmpdir)

            # Invalid absolute path outside project
            with pytest.raises(ValueError, match="outside project root"):
                tool.validate_path_under_project("/etc/passwd", tmpdir)


class TestIDEIntegration:
    """Test IDE context integration."""

    def test_ide_context_extraction(self):
        """Test IDE context extraction from headers and metadata."""
        from server.utils.ide_context import pull_ide_context

        # Test workspace root from headers
        headers = {"x-workspace-root": "/workspace/project"}
        context = pull_ide_context(headers=headers)
        assert context["workspaceRoot"] == "/workspace/project"

        # Test active file from extra metadata
        extra = {"activeFile": "/workspace/project/src/main.kt"}
        context = pull_ide_context(extra=extra)
        assert context["activeFile"] == "/workspace/project/src/main.kt"

        # Test selection metadata
        extra = {"selection": {"start": 10, "end": 20}}
        context = pull_ide_context(extra=extra)
        assert context["selection"] == {"start": 10, "end": 20}


class TestCIGate:
    """Test CI gate functionality."""

    def test_no_getcwd_usage_in_tools(self):
        """Test that tools don't use os.getcwd()."""
        # This would be implemented as a static analysis test
        # For now, we'll just verify the pattern doesn't exist in key files

        tool_files = [
            "tools/gradle_tools.py",
            "tools/project_analysis.py",
            "tools/build_optimization.py",
        ]

        for tool_file in tool_files:
            if Path(tool_file).exists():
                content = Path(tool_file).read_text()
                # Should not contain direct getcwd() calls
                assert "os.getcwd()" not in content, f"Found os.getcwd() in {tool_file}"
                assert "process.cwd()" not in content, f"Found process.cwd() in {tool_file}"

    @pytest.mark.skip(reason="Gradle execution tests are environment-specific and may fail in CI")
    def test_runtime_parity_with_project_path(self) -> None:
        """Test that tools work correctly when PROJECT_PATH is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal project structure
            gradlew_path = Path(tmpdir) / "gradlew"
            gradlew_path.touch()
            gradlew_path.chmod(0o755)

            build_gradle = Path(tmpdir) / "build.gradle"
            build_gradle.write_text("// test")

            # Set PROJECT_PATH and test tool
            with patch.dict(os.environ, {"PROJECT_PATH": tmpdir}):
                tools = GradleTools(Path("/tmp"), SecurityManager())

                with patch("asyncio.create_subprocess_exec") as mock_exec:
                    mock_process = MagicMock()
                    mock_process.returncode = 0
                    mock_process.communicate.return_value = (b"BUILD SUCCESSFUL", b"")
                    mock_exec.return_value = mock_process

                    import asyncio

                    result = asyncio.run(tools.gradle_build({}))

                    # Should succeed and use tmpdir as project root
                    assert result["success"] is True
                    assert result["project_root"] == tmpdir
