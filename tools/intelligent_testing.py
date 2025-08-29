#!/usr/bin/env python3
"""
Intelligent Testing Tools

This module provides LSP-like intelligent test generation capabilities
for Kotlin projects. It uses project context and LLM suggestions to
produce JUnit or Compose tests, inserts them into the project, and
validates compilation via Gradle.
"""

import subprocess
from pathlib import Path
from typing import Any, Dict

from ai.llm_integration import CodeGenerationRequest, CodeType
from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class IntelligentTestGenerationTool(IntelligentToolBase):
    """Generate Kotlin test code using project context and LLM guidance."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Generate and insert tests, then validate compilation."""

        target_file = arguments.get("target_file")
        test_type = arguments.get("test_type", "junit")
        class_name = arguments.get("class_name", "Generated")
        package_name = arguments.get("package_name", "com.example")

        source_content = ""
        if target_file:
            src_path = self.project_path / target_file
            if src_path.exists():
                source_content = src_path.read_text(encoding="utf-8")

        # Provide limited project context for better generation
        project_files = [
            str(p.relative_to(self.project_path))
            for p in self.project_path.rglob("*.kt")
        ][:20]
        self.llm_integration.set_project_context({"files": project_files})

        request = CodeGenerationRequest(
            description=f"Generate {test_type} tests for {class_name}",
            code_type=CodeType.TEST,
            package_name=package_name,
            class_name=f"{class_name}Test",
            framework="compose" if test_type.lower() == "compose" else "junit",
            context={"source_file": target_file, "source_content": source_content},
        )

        generation = await self.llm_integration.generate_code_with_ai(request)
        test_code = generation.get("generated_code", "")

        test_dir = (
            self.project_path
            / "src"
            / "test"
            / "kotlin"
            / package_name.replace(".", "/")
        )
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / f"{class_name}Test.kt"
        test_file.write_text(test_code, encoding="utf-8")

        compilation = await self._validate_compilation()

        return {
            "test_file": str(test_file),
            "generation": generation,
            "compilation": compilation,
        }

    async def _validate_compilation(self) -> Dict[str, Any]:
        """Attempt to compile tests using Gradle to ensure validity."""
        try:
            result = subprocess.run(
                ["./gradlew", "testClasses"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Gradle wrapper not found",
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Compilation timed out",
            }
