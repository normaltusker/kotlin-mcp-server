#!/usr/bin/env python3
"""
Tests for Intelligent Refactoring Tools

This module contains comprehensive tests for the Kotlin refactoring functionality
including rename, extract, inline, and introduce parameter refactorings.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from tools.intelligent_refactoring import (
    IntelligentRefactoringTools,
    KotlinASTParser,
    UnifiedDiffGenerator,
)


class TestKotlinASTParser:
    """Test cases for Kotlin AST parser."""

    def setup_method(self):
        self.parser = KotlinASTParser()

    def test_parse_simple_class(self):
        """Test parsing a simple Kotlin class."""
        kotlin_code = """
class User {
    val name: String = ""
    var age: Int = 0

    fun getDisplayName(): String {
        return name
    }

    fun incrementAge() {
        age += 1
    }
}
""".strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kt", delete=False) as f:
            f.write(kotlin_code)
            temp_file = f.name

        try:
            symbols = self.parser.parse_file(temp_file)

            assert "User" in symbols
            assert symbols["User"]["type"] == "class"
            assert "getDisplayName" in symbols
            assert symbols["getDisplayName"]["type"] == "function"
            assert "incrementAge" in symbols
            assert "name" in symbols
            assert symbols["name"]["type"] == "property"
        finally:
            Path(temp_file).unlink()

    def test_parse_function_with_parameters(self):
        """Test parsing function with parameters."""
        kotlin_code = """
fun calculateTotal(price: Double, tax: Double = 0.0): Double {
    return price + (price * tax)
}
""".strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kt", delete=False) as f:
            f.write(kotlin_code)
            temp_file = f.name

        try:
            symbols = self.parser.parse_file(temp_file)

            assert "calculateTotal" in symbols
            func_info = symbols["calculateTotal"]
            assert func_info["type"] == "function"
            assert len(func_info["parameters"]) == 2
            assert func_info["parameters"][0]["name"] == "price"
            assert func_info["parameters"][0]["type"] == "Double"
            assert func_info["return_type"] == "Double"
        finally:
            Path(temp_file).unlink()


class TestUnifiedDiffGenerator:
    """Test cases for unified diff generation."""

    def test_generate_diff_simple_change(self):
        """Test generating diff for simple change."""
        original = 'fun hello() {\n    println("Hello")\n}'
        modified = 'fun hello() {\n    println("Hello World")\n}'

        diff = UnifiedDiffGenerator.generate_diff(original, modified, "Test.kt")

        assert "@@ -1,3 +1,3 @@" in diff
        assert '-    println("Hello")' in diff
        assert '+    println("Hello World")' in diff

    def test_generate_diff_no_changes(self):
        """Test generating diff when no changes."""
        content = 'fun hello() {\n    println("Hello")\n}'

        diff = UnifiedDiffGenerator.generate_diff(content, content, "Test.kt")

        assert diff == ""


class TestIntelligentRefactoringTools:
    """Test cases for intelligent refactoring tools."""

    def setup_method(self):
        self.project_path = Path(tempfile.mkdtemp())
        self.tools = IntelligentRefactoringTools(str(self.project_path))

    def teardown_method(self):
        # Clean up temp directory
        import shutil

        shutil.rmtree(self.project_path, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_rename_function_success(self):
        """Test successful function rename."""
        kotlin_code = """
class Calculator {
    fun add(a: Int, b: Int): Int {
        return a + b
    }

    fun calculate() {
        val result = add(5, 3)
        println(result)
    }
}
""".strip()

        # Create test file
        test_file = self.project_path / "Calculator.kt"
        test_file.write_text(kotlin_code)

        # Mock ktlint to return modified content
        modified_kotlin_code = """
class Calculator {
    fun sum(a: Int, b: Int): Int {
        return a + b
    }

    fun calculate() {
        val result = sum(5, 3)
        println(result)
    }
}
""".strip()
        with patch.object(self.tools.ktlint, "format_file", return_value=modified_kotlin_code):
            # Mock gradle build to succeed
            with patch.object(
                self.tools.gradle_api, "build_project", return_value={"success": True}
            ):
                result = await self.tools.refactor_function(
                    {
                        "filePath": str(test_file),
                        "functionName": "add",
                        "refactorType": "rename",
                        "newName": "sum",
                        "preview": True,
                    }
                )

                assert result["success"] is True
                assert "diff" in result
                assert "sum" in result["diff"]
                assert result["preview"] is True

    @pytest.mark.asyncio
    async def test_rename_function_missing_new_name(self):
        """Test rename function with missing new name."""
        result = await self.tools.refactor_function(
            {"filePath": "test.kt", "functionName": "testFunc", "refactorType": "rename"}
        )

        assert result["success"] is False
        assert "newName is required" in result["error"]

    @pytest.mark.asyncio
    async def test_extract_function_success(self):
        """Test successful function extraction."""
        kotlin_code = """
fun processData() {
    val data = listOf(1, 2, 3, 4, 5)
    val filtered = data.filter { it > 2 }
    val mapped = filtered.map { it * 2 }
    println(mapped)
}
""".strip()

        # Create test file
        test_file = self.project_path / "Processor.kt"
        test_file.write_text(kotlin_code)

        # Mock ktlint and gradle
        with patch.object(self.tools.ktlint, "format_file", return_value=kotlin_code):
            with patch.object(
                self.tools.gradle_api, "build_project", return_value={"success": True}
            ):
                result = await self.tools.refactor_function(
                    {
                        "filePath": str(test_file),
                        "functionName": "processData",
                        "refactorType": "extract",
                        "newName": "transformData",
                        "range": {"start": {"line": 2}, "end": {"line": 4}},
                        "preview": True,
                    }
                )

                assert result["success"] is True
                assert "diff" in result

    @pytest.mark.asyncio
    async def test_inline_function_success(self):
        """Test successful function inlining."""
        kotlin_code = """
fun getMessage(): String {
    return "Hello World"
}

fun displayMessage() {
    val message = getMessage()
    println(message)
}
""".strip()

        # Create test file
        test_file = self.project_path / "Message.kt"
        test_file.write_text(kotlin_code)

        # Mock ktlint and gradle
        with patch.object(self.tools.ktlint, "format_file", return_value=kotlin_code):
            with patch.object(
                self.tools.gradle_api, "build_project", return_value={"success": True}
            ):
                result = await self.tools.refactor_function(
                    {
                        "filePath": str(test_file),
                        "functionName": "getMessage",
                        "refactorType": "inline",
                        "preview": True,
                    }
                )

                assert result["success"] is True
                assert "diff" in result

    @pytest.mark.asyncio
    async def test_introduce_parameter_success(self):
        """Test successful parameter introduction."""
        kotlin_code = """
fun greet(): String {
    return "Hello User"
}
""".strip()

        # Create test file
        test_file = self.project_path / "Greeter.kt"
        test_file.write_text(kotlin_code)

        # Mock ktlint and gradle
        with patch.object(self.tools.ktlint, "format_file", return_value=kotlin_code):
            with patch.object(
                self.tools.gradle_api, "build_project", return_value={"success": True}
            ):
                result = await self.tools.refactor_function(
                    {
                        "filePath": str(test_file),
                        "functionName": "greet",
                        "refactorType": "introduceParam",
                        "paramName": "name",
                        "paramType": "String",
                        "preview": True,
                    }
                )

                assert result["success"] is True
                assert "diff" in result

    @pytest.mark.asyncio
    async def test_compilation_failure_handling(self):
        """Test handling of compilation failures."""
        kotlin_code = "fun test() { invalid_syntax }"

        # Create test file
        test_file = self.project_path / "Invalid.kt"
        test_file.write_text(kotlin_code)

        # Mock ktlint to succeed but gradle to fail
        with patch.object(self.tools.ktlint, "format_file", return_value=kotlin_code):
            with patch.object(
                self.tools.gradle_api,
                "build_project",
                return_value={"success": False, "error": "Compilation failed: syntax error"},
            ):
                result = await self.tools.refactor_function(
                    {
                        "filePath": str(test_file),
                        "functionName": "test",
                        "refactorType": "rename",
                        "newName": "testRenamed",
                        "preview": True,
                    }
                )

                assert result["success"] is False
                assert "compilation errors" in result["error"].lower()

    def test_file_not_found(self):
        """Test handling of non-existent files."""
        result = asyncio.run(
            self.tools.refactor_function(
                {
                    "filePath": "nonexistent.kt",
                    "functionName": "test",
                    "refactorType": "rename",
                    "newName": "test2",
                }
            )
        )

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_unsupported_refactor_type(self):
        """Test handling of unsupported refactor types."""
        result = asyncio.run(
            self.tools.refactor_function(
                {"filePath": "test.kt", "functionName": "test", "refactorType": "unsupported_type"}
            )
        )

        assert result["success"] is False
        assert "Unsupported refactor type" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__])
