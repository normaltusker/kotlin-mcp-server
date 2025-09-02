"""Intelligent build and project tools that leverage existing utilities."""

import asyncio
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.build_optimization import BuildOptimizationTools
from tools.gradle_tools import GradleTools
from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext
from tools.project_analysis import ProjectAnalysisTools
from utils.security import SecurityManager


class IntelligentGradleBuildTool(IntelligentToolBase):
    """Run Gradle builds with intelligent context."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None) -> None:
        super().__init__(project_path, security_manager)
        self.gradle_tools = GradleTools(Path(project_path), security_manager or SecurityManager())

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        return await self.gradle_tools.gradle_build(arguments)


class IntelligentProjectAnalysisTool(IntelligentToolBase):
    """Analyze project structure and configuration."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None) -> None:
        super().__init__(project_path, security_manager)
        self.project_tools = ProjectAnalysisTools(
            Path(project_path), security_manager or SecurityManager()
        )

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        return await self.project_tools.analyze_project(arguments)


class IntelligentProjectRefactorTool(IntelligentToolBase):
    """Analyze and refactor an entire project."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None) -> None:
        super().__init__(project_path, security_manager)
        self.project_tools = ProjectAnalysisTools(
            Path(project_path), security_manager or SecurityManager()
        )

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        return await self.project_tools.analyze_and_refactor_project(arguments)


class IntelligentBuildOptimizationTool(IntelligentToolBase):
    """Optimize build performance and configuration."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None) -> None:
        super().__init__(project_path, security_manager)
        self.optimization_tools = BuildOptimizationTools(
            Path(project_path), security_manager or SecurityManager()
        )

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        return await self.optimization_tools.optimize_build_performance(arguments)


class IntelligentGitTool(IntelligentToolBase):
    """Git operations with intelligent commit messages and conflict resolution."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None) -> None:
        super().__init__(project_path, security_manager)
        self.project_path = Path(project_path)

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        operation = arguments.get("operation", "status")

        if operation == "status":
            return await self._git_status()
        elif operation == "smart_commit":
            return await self._git_smart_commit(arguments)
        elif operation == "create_feature_branch":
            return await self._git_create_feature_branch(arguments)
        elif operation == "merge_with_resolution":
            return await self._git_merge_with_resolution(arguments)
        else:
            return {"success": False, "error": f"Unknown Git operation: {operation}"}

    async def _git_status(self) -> Dict[str, Any]:
        """Get Git repository status."""
        try:
            # Get status
            process = await asyncio.create_subprocess_exec(
                "git",
                "status",
                "--porcelain",
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return {"success": False, "error": stderr.decode()}

            # Parse status
            changes = []
            for line in stdout.decode().split("\n"):
                if line.strip():
                    status = line[:2]
                    file_path = line[3:]
                    changes.append({"status": status, "file": file_path})

            # Get branch info
            process = await asyncio.create_subprocess_exec(
                "git",
                "branch",
                "--show-current",
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            current_branch = stdout.decode().strip() if process.returncode == 0 else "unknown"

            # Get ahead/behind info
            ahead_behind = await self._get_ahead_behind(current_branch)

            return {
                "success": True,
                "current_branch": current_branch,
                "changes": changes,
                "has_changes": len(changes) > 0,
                "ahead_behind": ahead_behind,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _git_smart_commit(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create intelligent commit message based on changes."""
        try:
            # Get diff
            process = await asyncio.create_subprocess_exec(
                "git", "diff", "--cached", cwd=self.project_path, stdout=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return {"success": False, "error": "No staged changes"}

            diff_content = stdout.decode()

            # Analyze diff to determine commit type
            commit_type = self._analyze_commit_type(diff_content)
            commit_message = self._generate_commit_message(diff_content, commit_type)

            # Stage all changes if none staged
            await asyncio.create_subprocess_exec("git", "add", ".", cwd=self.project_path)

            # Commit
            process = await asyncio.create_subprocess_exec(
                "git",
                "commit",
                "-m",
                commit_message,
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "commit_message": commit_message,
                "commit_type": commit_type,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_commit_type(self, diff: str) -> str:
        """Analyze diff to determine conventional commit type."""
        if "test" in diff.lower() or "spec" in diff.lower():
            return "test"
        elif "fix" in diff.lower() or "bug" in diff.lower():
            return "fix"
        elif "feat" in diff.lower() or "feature" in diff.lower():
            return "feat"
        elif "docs" in diff.lower() or "readme" in diff.lower():
            return "docs"
        elif "refactor" in diff.lower():
            return "refactor"
        else:
            return "chore"

    def _generate_commit_message(self, diff: str, commit_type: str) -> str:
        """Generate intelligent commit message."""
        # Extract meaningful changes
        lines = diff.split("\n")
        changes = []

        for line in lines:
            if line.startswith("+") and not line.startswith("+++"):
                changes.append(line[1:].strip())
            elif line.startswith("-") and not line.startswith("---"):
                changes.append(f"Removed: {line[1:].strip()}")

        # Create concise message
        if changes:
            summary = changes[0][:50] + "..." if len(changes[0]) > 50 else changes[0]
            return f"{commit_type}: {summary}"
        else:
            return f"{commit_type}: Update files"

    async def _git_create_feature_branch(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new feature branch."""
        branch_name = arguments.get("branch_name")
        if not branch_name:
            return {"success": False, "error": "Branch name is required"}

        try:
            # Create and switch to new branch
            process = await asyncio.create_subprocess_exec(
                "git",
                "checkout",
                "-b",
                f"feature/{branch_name}",
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "branch_name": f"feature/{branch_name}",
                "error": stderr.decode() if process.returncode != 0 else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _git_merge_with_resolution(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Merge branch with intelligent conflict resolution."""
        target_branch = arguments.get("target_branch", "main")

        try:
            # Attempt merge
            process = await asyncio.create_subprocess_exec(
                "git",
                "merge",
                target_branch,
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {"success": True, "merged": True}

            # Check for conflicts
            conflict_process = await asyncio.create_subprocess_exec(
                "git", "status", cwd=self.project_path, stdout=asyncio.subprocess.PIPE
            )
            conflict_stdout, _ = await conflict_process.communicate()

            if "conflict" in conflict_stdout.decode().lower():
                # Get conflict hunks
                conflicts = await self._get_conflicts()
                return {
                    "success": False,
                    "has_conflicts": True,
                    "conflicts": conflicts,
                    "resolution_suggestions": self._suggest_resolution(conflicts),
                }

            return {"success": False, "error": stderr.decode()}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_conflicts(self) -> List[Dict[str, Any]]:
        """Get conflict information."""
        try:
            process = await asyncio.create_subprocess_exec(
                "git", "diff", cwd=self.project_path, stdout=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()

            # Parse conflicts from diff
            conflicts: List[Dict[str, Any]] = []
            lines = stdout.decode().split("\n")
            current_file = None
            current_conflict = None

            for line in lines:
                if line.startswith("+++ b/"):
                    current_file = line[6:]
                elif line.startswith("@@"):
                    if current_conflict:
                        conflicts.append(current_conflict)
                    current_conflict = {
                        "file": current_file,
                        "hunk": line,
                        "ours": [],
                        "theirs": [],
                    }
                elif current_conflict is not None and line.startswith("+"):
                    current_conflict["theirs"].append(line[1:])
                elif current_conflict is not None and line.startswith("-"):
                    current_conflict["ours"].append(line[1:])

            if current_conflict:
                conflicts.append(current_conflict)

            return conflicts

        except Exception:
            return []

    def _suggest_resolution(self, conflicts: List[Dict[str, Any]]) -> List[str]:
        """Suggest conflict resolution strategies."""
        suggestions = []
        for conflict in conflicts:
            if "test" in conflict["file"].lower():
                suggestions.append(f"Keep both test changes in {conflict['file']}")
            elif "gradle" in conflict["file"].lower():
                suggestions.append(f"Review dependency conflicts in {conflict['file']}")
            else:
                suggestions.append(f"Manual review needed for {conflict['file']}")

        return suggestions

    async def _get_ahead_behind(self, current_branch: str) -> Dict[str, int]:
        """Get ahead/behind counts relative to remote."""
        try:
            # Get remote tracking branch
            process = await asyncio.create_subprocess_exec(
                "git",
                "rev-parse",
                "--abbrev-ref",
                f"{current_branch}@{{upstream}}",
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return {"ahead": 0, "behind": 0}

            upstream = stdout.decode().strip()

            # Get ahead count
            process = await asyncio.create_subprocess_exec(
                "git",
                "rev-list",
                "--count",
                f"{upstream}..{current_branch}",
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()
            ahead = int(stdout.decode().strip()) if process.returncode == 0 else 0

            # Get behind count
            process = await asyncio.create_subprocess_exec(
                "git",
                "rev-list",
                "--count",
                f"{current_branch}..{upstream}",
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()
            behind = int(stdout.decode().strip()) if process.returncode == 0 else 0

            return {"ahead": ahead, "behind": behind}

        except Exception:
            return {"ahead": 0, "behind": 0}
