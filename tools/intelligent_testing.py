#!/usr/bin/env python3
"""Intelligent test execution tools using Gradle.

This module provides an intelligent implementation of the ``run_tests`` tool.
It executes Gradle tests by category (unit, integration, ui), streams logs in
real-time and returns structured results including any failed tests with their
source locations.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class IntelligentTestingTool(IntelligentToolBase):
    """Run Gradle tests with structured result parsing."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Execute Gradle tests and capture results.

        Args:
            context: Tool execution context (unused).
            arguments: Should contain ``test_type`` selecting which tests to run.
        """

        test_type = arguments.get("test_type", "unit")
        task_map = {
            "unit": "test",
            "integration": "integrationTest",
            "ui": "uiTest",
            "all": "test",
        }
        gradle_task = task_map.get(test_type, "test")

        # Log audit event if security manager is available
        if self.security_manager:
            self.security_manager.log_audit_event(
                "run_tests", f"test_type:{test_type}", gradle_task
            )

        cmd = ["./gradlew", gradle_task, "--console=plain"]
        if self.security_manager:
            try:
                cmd = self.security_manager.validate_command_args(cmd)
            except Exception as exc:  # pragma: no cover - defensive
                return {
                    "success": False,
                    "error": f"Invalid command arguments: {exc}",
                    "test_type": test_type,
                }

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Gradle wrapper not found",
                "test_type": test_type,
                "failed_tests": [],
                "logs": [],
            }
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "success": False,
                "error": f"Failed to start Gradle: {exc}",
                "test_type": test_type,
                "failed_tests": [],
                "logs": [],
            }

        logs: List[str] = []
        failed_tests: List[Dict[str, Any]] = []

        failure_line = re.compile(r"([^ >]+) > ([^ ]+) FAILED")
        location_line = re.compile(r"\s+at (.*):(\d+)")

        async def stream_reader(stream: asyncio.StreamReader) -> None:
            while True:
                line_bytes = await stream.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").rstrip()
                logs.append(line)
                match = failure_line.search(line)
                if match:
                    failed_tests.append(
                        {
                            "class": match.group(1).strip(),
                            "test": match.group(2).strip(),
                            "file": None,
                            "line": None,
                        }
                    )
                    continue
                match = location_line.search(line)
                if match and failed_tests:
                    failed_tests[-1]["file"] = match.group(1)
                    failed_tests[-1]["line"] = int(match.group(2))

        stdout_task = asyncio.create_task(stream_reader(process.stdout))
        stderr_task = asyncio.create_task(stream_reader(process.stderr))
        await asyncio.gather(stdout_task, stderr_task)

        exit_code = await process.wait()
        success = exit_code == 0

        return {
            "success": success,
            "exit_code": exit_code,
            "test_type": test_type,
            "failed_tests": failed_tests,
            "logs": logs,
        }
