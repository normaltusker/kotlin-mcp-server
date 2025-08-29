#!/usr/bin/env python3
"""
Intelligent Architecture Tools for Dependency Injection

This module provides intelligent project refactoring to set up dependency
injection. It can generate DI modules, inject required annotations, and modify
the Application class using Kotlin LSP style refactoring. Both Hilt and
standard Dagger are supported and selected via arguments.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any, Dict

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class IntelligentDependencyInjectionTool(IntelligentToolBase):
    """Set up dependency injection with Kotlin-aware refactoring."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        di_type = arguments.get("di_type", "hilt").lower()
        module_name = arguments.get("module_name", "AppModule")
        package_name = arguments.get("package_name", "com.example.app")
        application_file = arguments.get("application_file")
        module_path = arguments.get(
            "module_path",
            f"app/src/main/java/{package_name.replace('.', '/')}/{module_name}.kt",
        )

        module_info = await self._generate_module(
            module_path, module_name, package_name, di_type
        )
        app_info: Dict[str, Any] = {}
        if application_file:
            app_info = await self._modify_application_class(application_file, di_type)

        return {
            "success": True,
            "di_type": di_type,
            "module": module_info,
            "application_changes": app_info,
        }

    async def _generate_module(
        self, module_path: str, module_name: str, package_name: str, di_type: str
    ) -> Dict[str, Any]:
        path = self.project_path / module_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if di_type == "hilt":
            imports = [
                "import dagger.Module",
                "import dagger.hilt.InstallIn",
                "import dagger.hilt.components.SingletonComponent",
            ]
            body = (
                f"@Module\n@InstallIn(SingletonComponent::class)\nobject {module_name} {{}}\n"
            )
        else:
            imports = [
                "import dagger.Module",
                "import dagger.Provides",
                "import javax.inject.Singleton",
            ]
            body = f"@Module\nobject {module_name} {{}}\n"

        content = (
            f"package {package_name}\n\n"
            + "\n".join(imports)
            + "\n\n"
            + body
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return {"file_path": str(path), "created": True}

    async def _modify_application_class(
        self, application_file: str, di_type: str
    ) -> Dict[str, Any]:
        path = self.project_path / application_file
        if not path.exists():
            return {"file_path": str(path), "modified": False, "reason": "not found"}

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if di_type == "hilt":
            new_content = await self._inject_hilt_annotation(content)
        else:
            new_content = await self._inject_dagger_initialization(content)

        applied = await self._apply_with_lsp(path, new_content)
        if not applied:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

        return {"file_path": str(path), "modified": True, "lsp_applied": applied}

    async def _inject_hilt_annotation(self, content: str) -> str:
        lines = content.splitlines()
        if "@HiltAndroidApp" not in content:
            for idx, line in enumerate(lines):
                if line.startswith("package"):
                    lines.insert(idx + 1, "import dagger.hilt.android.HiltAndroidApp")
                    break
            for idx, line in enumerate(lines):
                if line.strip().startswith("class "):
                    lines.insert(idx, "@HiltAndroidApp")
                    break
        return "\n".join(lines) + "\n"

    async def _inject_dagger_initialization(self, content: str) -> str:
        lines = content.splitlines()
        if "DaggerAppComponent" not in content:
            for idx, line in enumerate(lines):
                if line.startswith("package"):
                    lines.insert(idx + 1, "import javax.inject.Singleton")
                    lines.insert(idx + 1, "import dagger.Component")
                    break
            for idx, line in enumerate(lines):
                if line.strip().startswith("override fun onCreate"):
                    indent = " " * (len(line) - len(line.lstrip()))
                    for j in range(idx + 1, len(lines)):
                        if "super.onCreate" in lines[j]:
                            lines.insert(j + 1, f"{indent}DaggerAppComponent.create().inject(this)")
                            break
        return "\n".join(lines) + "\n"

    async def _apply_with_lsp(self, file_path: Path, new_content: str) -> bool:
        """Attempt to apply edits using Kotlin LSP; fall back to direct write."""
        edit = {
            "textDocument": {"uri": str(file_path)},
            "edits": [
                {
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 10_000, "character": 0},
                    },
                    "newText": new_content,
                }
            ],
        }
        try:
            proc = await asyncio.create_subprocess_exec(
                "kotlin-language-server",
                "--apply-edits",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate(json.dumps(edit).encode("utf-8"))
            return proc.returncode == 0
        except Exception:
            return False
