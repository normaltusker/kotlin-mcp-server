#!/usr/bin/env python3

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


# Simple MCP server implementation that works with standard MCP clients
class MCPServer:
    def __init__(self, name: str):
        self.name = name
        self.project_path: Optional[Path] = None

    async def handle_initialize(self, params: dict) -> dict:
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "resources": {"subscribe": False, "listChanged": False},
                "tools": {},
                "logging": {},
            },
            "serverInfo": {"name": self.name, "version": "1.0.0"},
        }

    async def handle_list_resources(self) -> dict:
        if not self.project_path:
            return {"resources": []}

        resources = []

        # Add Android config files
        android_files = [
            "app/src/main/AndroidManifest.xml",
            "app/build.gradle.kts",
            "app/build.gradle",
            "build.gradle.kts",
            "build.gradle",
            "gradle.properties",
            "settings.gradle.kts",
            "settings.gradle",
        ]

        for file_path in android_files:
            full_path = self.project_path / file_path
            if full_path.exists():
                resources.append(
                    {
                        "uri": f"file://{full_path}",
                        "name": f"Android Config: {file_path}",
                        "description": f"Android project configuration: {file_path}",
                        "mimeType": "text/plain",
                    }
                )

        # Add Kotlin source files
        kotlin_dirs = ["app/src/main/java", "app/src/main/kotlin"]
        for kotlin_dir in kotlin_dirs:
            kotlin_path = self.project_path / kotlin_dir
            if kotlin_path.exists():
                for kt_file in kotlin_path.rglob("*.kt"):
                    rel_path = kt_file.relative_to(self.project_path)
                    resources.append(
                        {
                            "uri": f"file://{kt_file}",
                            "name": f"Kotlin: {rel_path}",
                            "description": f"Kotlin source: {rel_path}",
                            "mimeType": "text/x-kotlin",
                        }
                    )

        # Add layout files
        layout_dir = self.project_path / "app/src/main/res/layout"
        if layout_dir.exists():
            for layout_file in layout_dir.glob("*.xml"):
                rel_path = layout_file.relative_to(self.project_path)
                resources.append(
                    {
                        "uri": f"file://{layout_file}",
                        "name": f"Layout: {layout_file.name}",
                        "description": f"Android layout: {rel_path}",
                        "mimeType": "application/xml",
                    }
                )

        return {"resources": resources}

    async def handle_read_resource(self, uri: str) -> dict:
        if not uri.startswith("file://"):
            raise ValueError(f"Unsupported URI scheme: {uri}")

        path = Path(uri[7:])  # Remove file:// prefix

        if not path.exists():
            raise FileNotFoundError(f"Resource not found: {path}")

        try:
            content = path.read_text(encoding="utf-8")
            return {"contents": [{"uri": uri, "mimeType": "text/plain", "text": content}]}
        except UnicodeDecodeError:
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/octet-stream",
                        "text": f"Binary file: {path.name}",
                    }
                ]
            }

    async def handle_list_tools(self) -> dict:
        return {
            "tools": [
                {
                    "name": "gradle_build",
                    "description": "Build Android project using Gradle",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Gradle task (e.g. 'assembleDebug', 'test')",
                                "default": "assembleDebug",
                            },
                            "clean": {
                                "type": "boolean",
                                "description": "Run clean before task",
                                "default": False,
                            },
                        },
                    },
                },
                {
                    "name": "run_tests",
                    "description": "Run Android tests",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "test_type": {
                                "type": "string",
                                "enum": ["unit", "instrumented", "all"],
                                "description": "Type of tests to run",
                                "default": "unit",
                            }
                        },
                    },
                },
                {
                    "name": "create_kotlin_file",
                    "description": "Create new Kotlin file with template",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path for new file",
                            },
                            "package_name": {"type": "string", "description": "Package name"},
                            "class_name": {"type": "string", "description": "Class name"},
                            "class_type": {
                                "type": "string",
                                "enum": [
                                    "activity",
                                    "fragment",
                                    "class",
                                    "data_class",
                                    "interface",
                                ],
                                "description": "Type of class",
                                "default": "class",
                            },
                        },
                        "required": ["file_path", "package_name", "class_name"],
                    },
                },
                {
                    "name": "create_layout_file",
                    "description": "Create new Android layout XML",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "layout_name": {
                                "type": "string",
                                "description": "Layout file name (without .xml)",
                            },
                            "layout_type": {
                                "type": "string",
                                "enum": ["activity", "fragment", "item", "custom"],
                                "description": "Layout type",
                                "default": "activity",
                            },
                        },
                        "required": ["layout_name"],
                    },
                },
                {
                    "name": "analyze_project",
                    "description": "Analyze Android project structure",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "analysis_type": {
                                "type": "string",
                                "enum": ["structure", "dependencies", "manifest", "all"],
                                "description": "Analysis type",
                                "default": "all",
                            }
                        },
                    },
                },
            ]
        }

    async def handle_call_tool(self, name: str, arguments: dict) -> dict:
        if not self.project_path:
            return {"content": [{"type": "text", "text": "Error: No project path set"}]}

        try:
            if name == "gradle_build":
                return await self._gradle_build(arguments)
            elif name == "run_tests":
                return await self._run_tests(arguments)
            elif name == "create_kotlin_file":
                return await self._create_kotlin_file(arguments)
            elif name == "create_layout_file":
                return await self._create_layout_file(arguments)
            elif name == "analyze_project":
                return await self._analyze_project(arguments)
            else:
                return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error executing {name}: {str(e)}"}]}

    async def _gradle_build(self, arguments: dict) -> dict:
        task = arguments.get("task", "assembleDebug")
        clean = arguments.get("clean", False)

        commands = []
        if clean:
            commands.append("./gradlew clean")
        commands.append(f"./gradlew {task}")

        output_parts = []
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd.split(), cwd=self.project_path, capture_output=True, text=True, timeout=300
                )

                output = f"Command: {cmd}\nExit code: {result.returncode}\n"
                output += f"Output:\n{result.stdout}\n"
                if result.stderr:
                    output += f"Errors:\n{result.stderr}\n"

                output_parts.append(output)

            except subprocess.TimeoutExpired:
                output_parts.append(f"Command timed out: {cmd}")
            except Exception as e:
                output_parts.append(f"Failed to execute {cmd}: {str(e)}")

        return {"content": [{"type": "text", "text": "\n".join(output_parts)}]}

    async def _run_tests(self, arguments: dict) -> dict:
        test_type = arguments.get("test_type", "unit")

        task_map = {
            "unit": "test",
            "instrumented": "connectedAndroidTest",
            "all": "test connectedAndroidTest",
        }

        task = task_map.get(test_type, "test")

        try:
            result = subprocess.run(
                f"./gradlew {task}".split(),
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600,
            )

            output = f"Running {test_type} tests\n"
            output += f"Command: ./gradlew {task}\n"
            output += f"Exit code: {result.returncode}\n"
            output += f"Output:\n{result.stdout}\n"
            if result.stderr:
                output += f"Errors:\n{result.stderr}\n"

            return {"content": [{"type": "text", "text": output}]}

        except Exception as e:
            return {"content": [{"type": "text", "text": f"Failed to run tests: {str(e)}"}]}

    async def _create_kotlin_file(self, arguments: dict) -> dict:
        file_path = arguments["file_path"]
        package_name = arguments["package_name"]
        class_name = arguments["class_name"]
        class_type = arguments.get("class_type", "class")

        full_path = self.project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        templates = {
            "activity": f"""package {package_name}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class {class_name} : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        // TODO: Set content view
    }}
}}
""",
            "fragment": f"""package {package_name}

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment

class {class_name} : Fragment() {{
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {{
        // TODO: Inflate layout
        return super.onCreateView(inflater, container, savedInstanceState)
    }}
}}
""",
            "data_class": f"""package {package_name}

data class {class_name}(
    // TODO: Add properties
)
""",
            "interface": f"""package {package_name}

interface {class_name} {{
    // TODO: Add methods
}}
""",
            "class": f"""package {package_name}

class {class_name} {{
    // TODO: Add implementation
}}
""",
        }

        content = templates.get(class_type, templates["class"])

        try:
            full_path.write_text(content, encoding="utf-8")
            return {
                "content": [{"type": "text", "text": f"Created Kotlin {class_type}: {file_path}"}]
            }
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Failed to create file: {str(e)}"}]}

    async def _create_layout_file(self, arguments: dict) -> dict:
        layout_name = arguments["layout_name"]
        layout_type = arguments.get("layout_type", "activity")

        layout_path = self.project_path / f"app/src/main/res/layout/{layout_name}.xml"
        layout_path.parent.mkdir(parents=True, exist_ok=True)

        templates = {
            "activity": """<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
""",
            "fragment": """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:text="Fragment content" />

</FrameLayout>
""",
            "item": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:padding="16dp">

    <!-- Item content -->

</LinearLayout>
""",
            "custom": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Custom content -->

</LinearLayout>
""",
        }

        content = templates.get(layout_type, templates["custom"])

        try:
            layout_path.write_text(content, encoding="utf-8")
            return {"content": [{"type": "text", "text": f"Created layout: {layout_name}.xml"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Failed to create layout: {str(e)}"}]}

    async def _analyze_project(self, arguments: dict) -> dict:
        analysis_type = arguments.get("analysis_type", "all")

        results = []

        if analysis_type in ["structure", "all"]:
            structure = self._analyze_structure()
            results.append(f"Project Structure:\n{structure}")

        if analysis_type in ["dependencies", "all"]:
            deps = self._analyze_dependencies()
            results.append(f"Dependencies:\n{deps}")

        if analysis_type in ["manifest", "all"]:
            manifest = self._analyze_manifest()
            results.append(f"Manifest:\n{manifest}")

        return {"content": [{"type": "text", "text": "\n\n".join(results)}]}

    def _analyze_structure(self) -> str:
        important_dirs = [
            "app/src/main/java",
            "app/src/main/kotlin",
            "app/src/main/res",
            "app/src/test",
            "app/src/androidTest",
        ]

        structure = []
        for dir_path in important_dirs:
            full_dir = self.project_path / dir_path
            if full_dir.exists():
                file_count = len(list(full_dir.rglob("*")))
                structure.append(f"✓ {dir_path}: {file_count} files")
            else:
                structure.append(f"✗ {dir_path}: missing")

        return "\n".join(structure)

    def _analyze_dependencies(self) -> str:
        gradle_files = [
            "app/build.gradle",
            "app/build.gradle.kts",
            "build.gradle",
            "build.gradle.kts",
        ]

        deps_info = []
        for gradle_file in gradle_files:
            gradle_path = self.project_path / gradle_file
            if gradle_path.exists():
                try:
                    content = gradle_path.read_text()
                    deps_info.append(f"Found: {gradle_file}")

                    impl_count = content.count("implementation")
                    test_count = content.count("testImplementation")

                    deps_info.append(f"  - implementation: {impl_count}")
                    deps_info.append(f"  - testImplementation: {test_count}")

                except Exception as e:
                    deps_info.append(f"Error reading {gradle_file}: {e}")

        return "\n".join(deps_info) if deps_info else "No Gradle files found"

    def _analyze_manifest(self) -> str:
        manifest_path = self.project_path / "app/src/main/AndroidManifest.xml"

        if not manifest_path.exists():
            return "AndroidManifest.xml not found"

        try:
            content = manifest_path.read_text()

            info = ["AndroidManifest.xml found"]

            if "android:name" in content:
                info.append("✓ Has application name")
            if "activity" in content:
                activity_count = content.count("<activity")
                info.append(f"✓ Activities: {activity_count}")
            if "service" in content:
                service_count = content.count("<service")
                info.append(f"✓ Services: {service_count}")

            return "\n".join(info)

        except Exception as e:
            return f"Error analyzing manifest: {e}"


def main():
    """Main MCP server entry point using stdio transport"""
    server = MCPServer("kotlin-android-mcp")

    # Get project path
    project_path = os.getenv("PROJECT_PATH")
    if len(sys.argv) > 1:
        project_path = sys.argv[1]

    if project_path:
        server.project_path = Path(project_path).resolve()
        if not server.project_path.exists():
            print(f"Warning: Project path does not exist: {server.project_path}", file=sys.stderr)

    print(f"Starting MCP server for project: {server.project_path}", file=sys.stderr)

    # Simple stdio-based MCP server loop with proper error handling
    try:
        while True:
            try:
                # Read JSON-RPC message from stdin
                line = sys.stdin.readline()
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}", file=sys.stderr)
                    continue

                # Handle MCP methods
                method = request.get("method")
                params = request.get("params", {})
                request_id = request.get("id")

                response = {"jsonrpc": "2.0", "id": request_id}

                try:
                    if method == "initialize":
                        response["result"] = asyncio.run(server.handle_initialize(params))
                    elif method == "resources/list":
                        response["result"] = asyncio.run(server.handle_list_resources())
                    elif method == "resources/read":
                        response["result"] = asyncio.run(server.handle_read_resource(params["uri"]))
                    elif method == "tools/list":
                        response["result"] = asyncio.run(server.handle_list_tools())
                    elif method == "tools/call":
                        response["result"] = asyncio.run(
                            server.handle_call_tool(params["name"], params.get("arguments", {}))
                        )
                    else:
                        response["error"] = {
                            "code": -32601,
                            "message": f"Method not found: {method}",
                        }
                except Exception as e:
                    response["error"] = {"code": -32603, "message": str(e)}
                    print(f"Error handling {method}: {e}", file=sys.stderr)

                # Send response to stdout
                print(json.dumps(response), flush=True)

            except EOFError:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Server error: {e}", file=sys.stderr)

    except Exception as e:
        print(f"Fatal server error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
