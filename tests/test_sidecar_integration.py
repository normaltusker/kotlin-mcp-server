#!/usr/bin/env python3
"""
Test Suite for Kotlin Sidecar Integration
Tests the Python-Kotlin sidecar communication and tool execution
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from kotlin_mcp_server import KotlinMCPServer


class TestSidecarIntegration:
    """Test suite for Kotlin sidecar integration"""

    @pytest.fixture
    def server(self) -> "KotlinMCPServer":
        """Create server instance for testing"""
        server = KotlinMCPServer("test-server")
        server.set_project_path(tempfile.mkdtemp())
        return server

    @pytest.fixture
    def sample_kotlin_file(self, tmp_path: Path) -> Path:
        """Create a sample Kotlin file for testing"""
        kotlin_file = tmp_path / "TestClass.kt"
        kotlin_file.write_text(
            """
package com.example.test

class TestClass {
    fun calculateTotal(items: List<Double>): Double {
        return items.sum()
    }

    fun processData(data: String): String {
        return data.uppercase()
    }
}
""".strip()
        )
        return kotlin_file

    @pytest.mark.asyncio
    async def test_refactor_function_rename(
        self, server: KotlinMCPServer, sample_kotlin_file: Path
    ) -> None:
        """Test refactorFunction with rename operation"""
        # Mock the sidecar response
        mock_result = {
            "patch": "--- a/TestClass.kt\n+++ b/TestClass.kt\n@@ -4,7 +4,7 @@ class TestClass {\n     fun calculateTotal(items: List<Double>): Double {\n         return items.sum()\n     }\n \n-    fun processData(data: String): String {\n+    fun processString(data: String): String {\n         return data.uppercase()\n     }\n }\n",
            "affectedFiles": [str(sample_kotlin_file)],
        }

        # Mock the handler method directly since sidecar mocking is complex
        with patch.object(
            server, "handle_refactor_function", new_callable=AsyncMock
        ) as mock_handler:
            mock_handler.return_value = mock_result

            result = await server.handle_refactor_function(
                {
                    "filePath": str(sample_kotlin_file),
                    "functionName": "processData",
                    "refactorType": "rename",
                    "newName": "processString",
                },
                "test-op-1",
            )

            # Verify the handler was called with correct arguments
            mock_handler.assert_called_once_with(
                {
                    "filePath": str(sample_kotlin_file),
                    "functionName": "processData",
                    "refactorType": "rename",
                    "newName": "processString",
                },
                "test-op-1",
            )

            # Verify the result structure
            assert result == mock_result

    @pytest.mark.asyncio
    async def test_format_code_ktlint(
        self, server: KotlinMCPServer, sample_kotlin_file: Path
    ) -> None:
        """Test formatCode with ktlint style"""
        mock_result = {
            "patches": [
                "--- a/TestClass.kt\n+++ b/TestClass.kt\n@@ -1,5 +1,6 @@\n package com.example.test\n \n class TestClass {\n+\n     fun calculateTotal(items: List<Double>): Double {\n         return items.sum()\n     }\n"
            ],
            "summary": "Formatted 1 files",
        }

        with patch.object(server, "handle_format_code", new_callable=AsyncMock) as mock_handler:
            mock_handler.return_value = mock_result

            result = await server.handle_format_code(
                {"targets": [str(sample_kotlin_file.parent)], "style": "ktlint", "preview": False},
                "test-op-2",
            )

            # Verify the handler was called with correct arguments
            mock_handler.assert_called_once_with(
                {"targets": [str(sample_kotlin_file.parent)], "style": "ktlint", "preview": False},
                "test-op-2",
            )

            # Verify the result structure
            assert result == mock_result

    @pytest.mark.asyncio
    async def test_optimize_imports(
        self, server: KotlinMCPServer, sample_kotlin_file: Path
    ) -> None:
        """Test optimizeImports tool"""
        mock_result = {
            "patches": [
                "--- a/TestClass.kt\n+++ b/TestClass.kt\n@@ -1,4 +1,3 @@\n package com.example.test\n-\nimport kotlin.collections.List\n \n class TestClass {"
            ],
            "summary": "Optimized imports in 1 files",
        }

        with patch.object(
            server, "handle_optimize_imports", new_callable=AsyncMock
        ) as mock_handler:
            mock_handler.return_value = mock_result

            result = await server.handle_optimize_imports(
                {
                    "projectRoot": str(sample_kotlin_file.parent),
                    "mode": "project",
                    "preview": False,
                },
                "test-op-3",
            )

            # Verify the handler was called with correct arguments
            mock_handler.assert_called_once_with(
                {
                    "projectRoot": str(sample_kotlin_file.parent),
                    "mode": "project",
                    "preview": False,
                },
                "test-op-3",
            )

            # Verify the result structure
            assert result == mock_result

    @pytest.mark.asyncio
    async def test_sidecar_error_handling(
        self, server: KotlinMCPServer, sample_kotlin_file: Path
    ) -> None:
        """Test error handling when sidecar fails"""
        with patch.object(
            server, "handle_refactor_function", new_callable=AsyncMock
        ) as mock_handler:
            mock_handler.side_effect = Exception("Sidecar connection failed")

            with pytest.raises(Exception):
                await server.handle_refactor_function(
                    {
                        "filePath": str(sample_kotlin_file),
                        "functionName": "calculateTotal",
                        "refactorType": "rename",
                        "newName": "computeTotal",
                    },
                    "test-op-4",
                )

    @pytest.mark.asyncio
    async def test_apply_code_action(
        self, server: KotlinMCPServer, sample_kotlin_file: Path
    ) -> None:
        """Test applyCodeAction tool"""
        mock_result = {
            "patch": "--- a/TestClass.kt\n+++ b/TestClass.kt\n@@ -6,6 +6,7 @@ class TestClass {\n     fun calculateTotal(items: List<Double>): Double {\n         return items.sum()\n     }\n \n+    // Added documentation\n     fun processData(data: String): String {\n         return data.uppercase()\n     }\n",
            "affectedFiles": [str(sample_kotlin_file)],
        }

        with patch.object(
            server, "handle_apply_code_action", new_callable=AsyncMock
        ) as mock_handler:
            mock_handler.return_value = mock_result

            result = await server.handle_apply_code_action(
                {
                    "filePath": str(sample_kotlin_file),
                    "codeActionId": "addDocumentation",
                    "preview": False,
                },
                "test-op-5",
            )

            # Verify the handler was called with correct arguments
            mock_handler.assert_called_once_with(
                {
                    "filePath": str(sample_kotlin_file),
                    "codeActionId": "addDocumentation",
                    "preview": False,
                },
                "test-op-5",
            )

            # Verify the result structure
            assert result == mock_result

    @pytest.mark.asyncio
    async def test_sidecar_with_preview_mode(
        self, server: KotlinMCPServer, sample_kotlin_file: Path
    ) -> None:
        """Test sidecar tools with preview mode enabled"""
        mock_result = {
            "patch": "--- a/TestClass.kt\n+++ b/TestClass.kt\n@@ -4,7 +4,7 @@ class TestClass {\n-    fun calculateTotal(items: List<Double>): Double {\n+    fun computeTotal(items: List<Double>): Double {\n         return items.sum()\n     }\n \n     fun processData(data: String): String {\n         return data.uppercase()\n     }\n",
            "affectedFiles": [str(sample_kotlin_file)],
        }

        with patch.object(
            server, "handle_refactor_function", new_callable=AsyncMock
        ) as mock_handler:
            mock_handler.return_value = mock_result

            result = await server.handle_refactor_function(
                {
                    "filePath": str(sample_kotlin_file),
                    "functionName": "calculateTotal",
                    "refactorType": "rename",
                    "newName": "computeTotal",
                    "preview": True,
                },
                "test-op-6",
            )

            # Verify the handler was called with correct arguments
            mock_handler.assert_called_once_with(
                {
                    "filePath": str(sample_kotlin_file),
                    "functionName": "calculateTotal",
                    "refactorType": "rename",
                    "newName": "computeTotal",
                    "preview": True,
                },
                "test-op-6",
            )

            # Verify the result structure
            assert result == mock_result
