#!/usr/bin/env python3
"""
AI-assisted Kotlin code generation utilities.

This module provides a high level API for turning natural language
specifications into Kotlin source files.  Generated code is inserted into
an Android/Kotlin project using LSP-like behaviour and is optionally
accompanied by unit tests.  The goal is not to be perfect but to provide
reasonable defaults so tests can exercise the integration points.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from ai.llm_integration import CodeGenerationRequest, CodeType, LLMIntegration
from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


@dataclass
class KotlinCodeSpec:
    """Specification for generating Kotlin code."""

    description: str
    package_name: str
    class_name: str
    code_type: CodeType = CodeType.CUSTOM
    generate_tests: bool = False
    test_package: Optional[str] = None
    test_framework: str = "junit"


class KotlinCodeGenerator:
    """Generate Kotlin code and insert it into the project."""

    def __init__(self, project_path: Path, llm: Optional[LLMIntegration] = None):
        self.project_path = Path(project_path)
        self.llm = llm or LLMIntegration()

    async def generate_and_insert(self, spec: KotlinCodeSpec) -> Dict[str, Any]:
        """Generate Kotlin source (and optional tests) then write them to disk."""
        request = CodeGenerationRequest(
            description=spec.description,
            code_type=spec.code_type,
            package_name=spec.package_name,
            class_name=spec.class_name,
            framework="android",
        )
        result = await self.llm.generate_code_with_ai(request)
        if not result.get("success"):
            raise RuntimeError(result.get("error", "generation failed"))

        code = result.get("generated_code", "")
        kotlin_path = self._write_kotlin_file(spec, code)

        test_path = None
        test_code = None
        if spec.generate_tests:
            test_request = CodeGenerationRequest(
                description=f"Unit tests for {spec.class_name}",
                code_type=CodeType.TEST,
                package_name=spec.test_package or spec.package_name,
                class_name=f"{spec.class_name}Test",
                framework=spec.test_framework,
            )
            test_result = await self.llm.generate_code_with_ai(test_request)
            if test_result.get("success"):
                test_code = test_result.get("generated_code", "")
                test_path = self._write_test_file(spec, test_code)

        await self._format_file(kotlin_path)
        if test_path:
            await self._format_file(test_path)

        return {
            "kotlin_file": str(kotlin_path),
            "test_file": str(test_path) if test_path else None,
            "generated_code": code,
            "generated_test": test_code,
        }

    def _write_kotlin_file(self, spec: KotlinCodeSpec, code: str) -> Path:
        rel_path = Path("src") / "main" / "kotlin" / spec.package_name.replace(".", "/")
        file_path = self.project_path / rel_path / f"{spec.class_name}.kt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(code.strip() + "\n", encoding="utf-8")
        return file_path

    def _write_test_file(self, spec: KotlinCodeSpec, code: str) -> Path:
        rel_path = Path("src") / "test" / "kotlin" / (spec.test_package or spec.package_name).replace(".", "/")
        file_path = self.project_path / rel_path / f"{spec.class_name}Test.kt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(code.strip() + "\n", encoding="utf-8")
        return file_path

    async def _format_file(self, path: Path) -> None:
        """Best-effort formatting: ensure newline termination."""
        try:
            text = path.read_text(encoding="utf-8")
            path.write_text(text.rstrip() + "\n", encoding="utf-8")
        except Exception:
            # Formatting is a best-effort operation; ignore failures.
            pass


class IntelligentCodeGenerationTool(IntelligentToolBase):
    """Tool wrapper exposing KotlinCodeGenerator through the MCP interface."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        description = arguments.get("description") or arguments.get("prompt", "")
        package_name = arguments.get("package_name", "com.example.generated")
        class_name = arguments.get("class_name", "GeneratedClass")
        code_type_str = arguments.get("code_type", "custom")
        generate_tests = bool(arguments.get("generate_tests", False))

        code_type = CodeType.CUSTOM
        if code_type_str in CodeType._value2member_map_:
            code_type = CodeType(code_type_str)

        spec = KotlinCodeSpec(
            description=description,
            package_name=package_name,
            class_name=class_name,
            code_type=code_type,
            generate_tests=generate_tests,
        )

        generator = KotlinCodeGenerator(self.project_path, self.llm_integration)
        result = await generator.generate_and_insert(spec)

        return {
            "success": True,
            "kotlin_file": result["kotlin_file"],
            "test_file": result["test_file"],
        }
