"""Quality of Life development tools for enhanced productivity."""

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import Config
from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext
from utils.security import SecurityManager


class IntelligentQoLDevTool(IntelligentToolBase):
    """Quality of Life development tools."""

    def __init__(self, project_path: str, security_manager: Optional[Any] = None):
        super().__init__(project_path, security_manager)
        self.project_path = Path(project_path)

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        operation = arguments.get("operation", "search")

        if operation == "search":
            return await self._project_search(arguments)
        elif operation == "todo_list":
            return await self._todo_list_from_code(arguments)
        elif operation == "readme_update":
            return await self._readme_generate_or_update(arguments)
        elif operation == "changelog_summarize":
            return await self._changelog_summarize(arguments)
        elif operation == "build_and_test":
            return await self._build_and_test(arguments)
        elif operation == "dependency_audit":
            return await self._dependency_audit(arguments)
        else:
            return {"success": False, "error": f"Unknown QoL operation: {operation}"}

    async def _project_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Fast grep search with context."""
        query = arguments.get("query")
        include_pattern = arguments.get("include_pattern", "*")
        max_results = arguments.get("max_results", 50)
        context_lines = arguments.get("context_lines", 2)

        if not query:
            return {"success": False, "error": "Query is required"}

        try:
            # Use ripgrep if available, fallback to grep
            results = []
            if await self._has_ripgrep():
                results = await self._search_with_ripgrep(
                    query, include_pattern, max_results, context_lines
                )
            else:
                results = await self._search_with_grep(
                    query, include_pattern, max_results, context_lines
                )

            return {
                "success": True,
                "query": query,
                "results": results,
                "total_matches": len(results),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _has_ripgrep(self) -> bool:
        """Check if ripgrep is available."""
        try:
            process = await asyncio.create_subprocess_exec(
                "rg", "--version", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.wait()
            return process.returncode == 0
        except FileNotFoundError:
            return False

    async def _search_with_ripgrep(
        self, query: str, pattern: str, max_results: int, context: int
    ) -> List[Dict[str, Any]]:
        """Search using ripgrep."""
        cmd = ["rg", "--json", "-C", str(context), "--max-count", str(max_results)]
        if pattern != "*":
            cmd.extend(["-g", pattern])
        cmd.append(query)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.project_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()

        results = []
        for line in stdout.decode().split("\n"):
            if line.strip():
                try:
                    data = json.loads(line)
                    if data.get("type") == "match":
                        results.append(
                            {
                                "file": data["data"]["path"]["text"],
                                "line_number": data["data"]["line_number"],
                                "content": data["data"]["lines"]["text"].rstrip(),
                                "context_before": [
                                    ctx["text"].rstrip()
                                    for ctx in data["data"]
                                    .get("lines", {})
                                    .get("context_before", [])
                                ],
                                "context_after": [
                                    ctx["text"].rstrip()
                                    for ctx in data["data"]
                                    .get("lines", {})
                                    .get("context_after", [])
                                ],
                            }
                        )
                except json.JSONDecodeError:
                    continue

        return results

    async def _search_with_grep(
        self, query: str, pattern: str, max_results: int, context: int
    ) -> List[Dict[str, Any]]:
        """Search using grep."""
        cmd = ["grep", "-r", "-n", "-C", str(context), "--include", pattern, query, "."]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.project_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()

        results = []
        current_result: Optional[Dict[str, Any]] = None

        for line in stdout.decode().split("\n"):
            if line.strip():
                if ":" in line and not line.startswith(" "):
                    # New match
                    if current_result:
                        results.append(current_result)
                    parts = line.split(":", 2)
                    current_result = {
                        "file": parts[0],
                        "line_number": int(parts[1]),
                        "content": parts[2],
                        "context_before": [],
                        "context_after": [],
                    }
                elif current_result and line.startswith("-"):
                    current_result["context_before"].append(line[1:])
                elif current_result and line.startswith("+"):
                    current_result["context_after"].append(line[1:])

        if current_result:
            results.append(current_result)

        return results[:max_results]

    async def _todo_list_from_code(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Parse TODO/FIXME/@Deprecated from code."""
        include_pattern = arguments.get("include_pattern", "*.{kt,java,py,js,ts}")
        max_results = arguments.get("max_results", 100)

        try:
            todos = []
            patterns = [
                r"TODO[:\s]*(.+)",
                r"FIXME[:\s]*(.+)",
                r"@Deprecated[:\s]*(.+)",
                r"XXX[:\s]*(.+)",
                r"HACK[:\s]*(.+)",
            ]

            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    if self._matches_pattern(file, include_pattern):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                for line_num, line in enumerate(f, 1):
                                    for pattern in patterns:
                                        match = re.search(pattern, line, re.IGNORECASE)
                                        if match:
                                            todos.append(
                                                {
                                                    "file": str(
                                                        file_path.relative_to(self.project_path)
                                                    ),
                                                    "line": line_num,
                                                    "type": pattern.split(":")[0].upper(),
                                                    "content": match.group(1).strip(),
                                                    "full_line": line.strip(),
                                                }
                                            )
                        except Exception:
                            continue

            # Sort by type priority
            priority_order = {"FIXME": 0, "TODO": 1, "XXX": 2, "HACK": 3, "@DEPRECATED": 4}
            todos.sort(key=lambda x: (priority_order.get(str(x["type"]), 5), x["file"], x["line"]))

            return {
                "success": True,
                "todos": todos[:max_results],
                "total_count": len(todos),
                "summary": self._summarize_todos(todos),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches glob pattern."""
        import fnmatch

        return fnmatch.fnmatch(filename, pattern)

    def _summarize_todos(self, todos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize todos by type."""
        summary: Dict[str, int] = {}
        for todo in todos:
            todo_type = todo["type"]
            summary[todo_type] = summary.get(todo_type, 0) + 1
        return summary

    async def _readme_generate_or_update(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update README with badges, setup/run/test, tool catalog."""
        readme_path = self.project_path / "README.md"
        force_regenerate = arguments.get("force_regenerate", False)

        try:
            if readme_path.exists() and not force_regenerate:
                # Update existing
                content = readme_path.read_text()
                updated_content = self._update_readme_content(content)
            else:
                # Generate new
                updated_content = self._generate_readme_content()

            readme_path.write_text(updated_content)

            return {
                "success": True,
                "action": "updated" if readme_path.exists() else "generated",
                "path": str(readme_path),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _update_readme_content(self, content: str) -> str:
        """Update existing README content."""
        # Add badges if missing
        if "![Build Status]" not in content:
            badges = self._generate_badges()
            content = badges + "\n\n" + content

        # Ensure sections exist
        required_sections = ["Setup", "Usage", "Development", "Tools"]
        for section in required_sections:
            if f"## {section}" not in content:
                content += f"\n\n## {section}\n\n{self._generate_section_content(section)}"

        return content

    def _generate_readme_content(self) -> str:
        """Generate new README content."""
        return f"""# Kotlin MCP Server

{self._generate_badges()}

Intelligent MCP server for Kotlin development with AI-powered tools.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m kotlin_mcp_server
```

## Development

### Building

```bash
./gradlew build
```

### Testing

```bash
./gradlew test
```

## Tools

{self._generate_tool_catalog()}

## Environment Variables

{self._generate_env_vars_docs()}
"""

    def _generate_badges(self) -> str:
        """Generate status badges."""
        return """[![Build Status](https://github.com/normaltusker/kotlin-mcp-server/workflows/CI/badge.svg)](https://github.com/normaltusker/kotlin-mcp-server/actions)
[![Coverage](https://codecov.io/gh/normaltusker/kotlin-mcp-server/branch/main/graph/badge.svg)](https://codecov.io/gh/normaltusker/kotlin-mcp-server)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)"""

    def _generate_section_content(self, section: str) -> str:
        """Generate content for a section."""
        if section == "Setup":
            return """### Prerequisites

- Python 3.8+
- Java 17+
- Gradle 7+

### Installation

```bash
git clone https://github.com/normaltusker/kotlin-mcp-server.git
cd kotlin-mcp-server
pip install -r requirements.txt
```"""
        elif section == "Usage":
            return """### Starting the Server

```bash
python -m kotlin_mcp_server
```

### Configuration

See environment variables section below."""
        elif section == "Development":
            return """### Running Tests

```bash
pytest
```

### Code Quality

```bash
./gradlew ktlintCheck
./gradlew detekt
```"""
        elif section == "Tools":
            return self._generate_tool_catalog()
        else:
            return "TBD"

    def _generate_tool_catalog(self) -> str:
        """Generate tool catalog for README."""
        return """### Available Tools

- **Git Tools**: Status, smart commits, branch management
- **External API**: Secure API calls with monitoring
- **Code Analysis**: Quality metrics and refactoring
- **File Management**: Backup, sync, classification
- **Security**: Compliance and audit tools

See [full documentation](docs/) for details."""

    def _generate_env_vars_docs(self) -> str:
        """Generate environment variables documentation."""
        return """### Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_MAX_RETRIES` | 5 | Maximum API retry attempts |
| `MCP_API_TIMEOUT_MS` | 3000 | API timeout in milliseconds |
| `MCP_RATE_LIMIT_QPS` | 10 | Rate limit queries per second |
| `MCP_AUDIT_DB_PATH` | ./audit.db | Audit database path |
| `MCP_SIDECAR_CMD` | java -jar kotlin-sidecar.jar | Kotlin sidecar command |
| `MCP_LOG_LEVEL` | INFO | Logging level |
| `MCP_ENABLE_TELEMETRY` | false | Enable telemetry |

See [configuration docs](docs/configuration.md) for details."""

    async def _changelog_summarize(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize conventional commits to grouped release notes."""
        changelog_path = arguments.get("changelog_path", "CHANGELOG.md")
        version = arguments.get("version", "latest")

        try:
            if not (self.project_path / changelog_path).exists():
                return {"success": False, "error": "CHANGELOG.md not found"}

            content = (self.project_path / changelog_path).read_text()
            summary = self._parse_changelog(content, version)

            return {"success": True, "version": version, "summary": summary}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_changelog(self, content: str, version: str) -> Dict[str, Any]:
        """Parse changelog and group by conventional commit types."""
        lines = content.split("\n")
        sections: Dict[str, Dict[str, List[str]]] = {}
        current_version = None

        for line in lines:
            # Version header
            version_match = re.match(r"^## \[?(\d+\.\d+\.\d+)", line)
            if version_match:
                current_version = version_match.group(1)
                if version != "latest" and current_version != version:
                    continue
                sections[current_version] = {"features": [], "fixes": [], "docs": [], "other": []}

            # Commit entries
            if current_version and current_version in sections:
                commit_match = re.match(r"^- (\w+): (.+)", line)
                if commit_match:
                    commit_type, message = commit_match.groups()
                    if commit_type == "feat":
                        sections[current_version]["features"].append(message)
                    elif commit_type == "fix":
                        sections[current_version]["fixes"].append(message)
                    elif commit_type == "docs":
                        sections[current_version]["docs"].append(message)
                    else:
                        sections[current_version]["other"].append(message)

        return sections

    async def _build_and_test(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Run Gradle/Maven build and return failing tests + artifacts."""
        build_tool = arguments.get("build_tool", "auto")  # auto, gradle, maven
        skip_tests = arguments.get("skip_tests", False)

        try:
            if build_tool == "auto":
                build_tool = (
                    "gradle" if (self.project_path / "build.gradle.kts").exists() else "maven"
                )

            if build_tool == "gradle":
                return await self._run_gradle_build(skip_tests)
            elif build_tool == "maven":
                return await self._run_maven_build(skip_tests)
            else:
                return {"success": False, "error": f"Unsupported build tool: {build_tool}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _run_gradle_build(self, skip_tests: bool) -> Dict[str, Any]:
        """Run Gradle build."""
        cmd = ["./gradlew", "build"]
        if skip_tests:
            cmd.append("-x")
            cmd.append("test")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.project_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        # Parse test results
        test_results = self._parse_gradle_test_output(stdout.decode() + stderr.decode())

        return {
            "success": process.returncode == 0,
            "build_tool": "gradle",
            "test_results": test_results,
            "output": stdout.decode(),
            "errors": stderr.decode(),
        }

    async def _run_maven_build(self, skip_tests: bool) -> Dict[str, Any]:
        """Run Maven build."""
        cmd = ["mvn", "clean", "compile"]
        if not skip_tests:
            cmd.append("test")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.project_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        # Parse test results
        test_results = self._parse_maven_test_output(stdout.decode() + stderr.decode())

        return {
            "success": process.returncode == 0,
            "build_tool": "maven",
            "test_results": test_results,
            "output": stdout.decode(),
            "errors": stderr.decode(),
        }

    def _parse_gradle_test_output(self, output: str) -> Dict[str, Any]:
        """Parse Gradle test output."""
        # Simple parsing - in real implementation, use proper test report parsing
        failed_tests = []
        lines = output.split("\n")
        for i, line in enumerate(lines):
            if "FAILED" in line and i > 0:
                test_name = lines[i - 1].strip()
                failed_tests.append({"test": test_name, "error": line.strip()})

        return {
            "total_tests": 0,  # Would need to parse from output
            "failed_tests": failed_tests,
            "passed_tests": 0,
        }

    def _parse_maven_test_output(self, output: str) -> Dict[str, Any]:
        """Parse Maven test output."""
        # Similar to Gradle
        failed_tests = []
        lines = output.split("\n")
        for line in lines:
            if "FAILED" in line:
                failed_tests.append({"test": line.strip(), "error": ""})

        return {"total_tests": 0, "failed_tests": failed_tests, "passed_tests": 0}

    async def _dependency_audit(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Audit Gradle deps for OSV + license scan."""
        try:
            # Run Gradle dependencies task
            process = await asyncio.create_subprocess_exec(
                "./gradlew",
                "dependencies",
                "--configuration",
                "runtimeClasspath",
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return {"success": False, "error": stderr.decode()}

            dependencies = self._parse_gradle_dependencies(stdout.decode())

            # Check for vulnerabilities (placeholder - would integrate with OSV)
            vulnerabilities = await self._check_vulnerabilities(dependencies)

            # Check licenses (placeholder)
            license_issues = await self._check_licenses(dependencies)

            return {
                "success": True,
                "dependencies": dependencies,
                "vulnerabilities": vulnerabilities,
                "license_issues": license_issues,
                "audit_summary": {
                    "total_deps": len(dependencies),
                    "vulnerable_deps": len(vulnerabilities),
                    "license_issues": len(license_issues),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_gradle_dependencies(self, output: str) -> List[Dict[str, str]]:
        """Parse Gradle dependencies output."""
        dependencies = []
        lines = output.split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith(("+", "\\", "|")) and "->" in line:
                parts = line.split(" -> ")
                if len(parts) == 2:
                    dep_name = parts[0].strip()
                    version = parts[1].strip()
                    dependencies.append({"name": dep_name, "version": version})
        return dependencies

    async def _check_vulnerabilities(
        self, dependencies: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Check for vulnerabilities using OSV."""
        # Placeholder - would integrate with OSV API
        vulnerabilities = []
        for dep in dependencies:
            # Simulate vulnerability check
            if "old" in dep["version"].lower():
                vulnerabilities.append(
                    {
                        "dependency": dep["name"],
                        "version": dep["version"],
                        "severity": "HIGH",
                        "description": "Known vulnerability in old version",
                    }
                )
        return vulnerabilities

    async def _check_licenses(self, dependencies: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Check dependency licenses."""
        # Placeholder - would check license compatibility
        license_issues = []
        for dep in dependencies:
            # Simulate license check
            if "proprietary" in dep["name"].lower():
                license_issues.append(
                    {
                        "dependency": dep["name"],
                        "issue": "Proprietary license may not be compatible",
                    }
                )
        return license_issues
