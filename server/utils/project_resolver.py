"""
Project and workspace resolution utilities.
"""

import os
import shutil
from typing import Dict, Optional, Tuple


class ProjectRootError(Exception):
    """Raised when project root cannot be resolved or is invalid."""


def resolve_project_root(
    inp: dict, env: Optional[Dict[str, str]] = None, ide_meta: Optional[dict] = None
) -> str:
    """
    Resolve project root from input, environment, or IDE metadata.

    Priority order:
    1. Explicit input (project_root or projectRoot)
    2. Environment variables (PROJECT_PATH or WORKSPACE_PATH)
    3. IDE metadata (projectRoot, workspaceRoot, workspacePath)

    Args:
        inp: Input dictionary with potential project_root
        env: Environment variables (defaults to os.environ)
        ide_meta: IDE metadata from MCP client

    Returns:
        Absolute path to project root

    Raises:
        ProjectRootError: If no valid project root found
    """
    env_dict: Dict[str, str] = env or dict(os.environ)

    # 1) Explicit input
    pr = inp.get("project_root") or inp.get("projectRoot")

    # 2) Environment variables
    pr = pr or env_dict.get("PROJECT_PATH") or env_dict.get("WORKSPACE_PATH")

    # 3) IDE metadata (MCP client may pass this in resource metadata)
    if not pr and ide_meta:
        pr = (
            ide_meta.get("projectRoot")
            or ide_meta.get("workspaceRoot")
            or ide_meta.get("workspacePath")
        )

    if not pr:
        raise ProjectRootError(
            "ProjectRootRequired: pass `project_root` or set env PROJECT_PATH; "
            "IDE workspace will be used if available."
        )

    pr = os.path.abspath(pr)
    if not (os.path.isdir(pr) and os.path.exists(pr)):
        raise ProjectRootError(f"ProjectRootInvalid: {pr} not found or not a directory")

    return pr


def find_gradle_cmd(project_root: str) -> Tuple[list, str, bool]:
    """
    Find Gradle command and working directory.

    Args:
        project_root: Project root directory

    Returns:
        Tuple of (command_list, working_dir, is_wrapper)

    Raises:
        ProjectRootError: If no Gradle setup found
    """
    # Search for wrapper upward from project_root
    cur = project_root
    while True:
        gw = os.path.join(cur, "gradlew")
        gw_bat = os.path.join(cur, "gradlew.bat")

        if os.path.isfile(gw) or os.path.isfile(gw_bat):
            if os.path.isfile(gw):
                try:
                    os.chmod(gw, 0o755)
                except OSError:
                    pass
                return ["./gradlew"], cur, True
            return ["gradlew.bat"], cur, True

        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent

    # No wrapper—fallback if settings present and system gradle exists
    settings = ("settings.gradle", "settings.gradle.kts")
    if any(os.path.exists(os.path.join(project_root, s)) for s in settings):
        if shutil.which("gradle"):
            return ["gradle"], project_root, False

    raise ProjectRootError("GradleNotFound: no gradle wrapper and no system gradle on PATH")
