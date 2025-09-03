#!/usr/bin/env python3
"""
Intelligent Network Tool

Provides intelligent generation of Retrofit interfaces, data models,
and network configuration with LSP-like validation.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class IntelligentNetworkTool(IntelligentToolBase):
    """Setup Retrofit API clients with intelligent capabilities."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Generate Retrofit interfaces, models, and configuration."""

        base_url = arguments.get("base_url", "https://api.example.com")
        endpoints: List[Dict[str, Any]] = arguments.get("endpoints", [])
        package_name = arguments.get("package_name", "com.example.network")
        interceptors: List[str] = arguments.get("interceptors", ["HttpLoggingInterceptor()"])

        project_root = self.project_path
        src_path = project_root / "src" / "main" / "java" / Path(package_name.replace(".", "/"))
        models_path = src_path / "models"
        api_path = src_path / "api"
        di_path = src_path / "di"
        for path in (models_path, api_path, di_path):
            path.mkdir(parents=True, exist_ok=True)

        interface_lines: List[str] = [
            f"package {package_name}.api",
            "",
            "import retrofit2.http.*",
            "",
            "interface ApiService {",
        ]

        for ep in endpoints:
            name = ep.get("name", "endpoint")
            method = ep.get("method", "GET").upper()
            path = ep.get("path", "/")
            request_model = ep.get("request_model")
            response_model = ep.get("response_model", f"{name}Response")

            # Request model
            if isinstance(request_model, dict):
                model_name = request_model.get("name", f"{name}Request")
                fields = request_model.get("fields", [])
                model_code = self._generate_data_class(package_name, model_name, fields)
                (models_path / f"{model_name}.kt").write_text(model_code, encoding="utf-8")

            # Response model
            if isinstance(response_model, dict):
                model_name = response_model.get("name", f"{name}Response")
                fields = response_model.get("fields", [])
                model_code = self._generate_data_class(package_name, model_name, fields)
                (models_path / f"{model_name}.kt").write_text(model_code, encoding="utf-8")
                response_model_name = model_name
            else:
                response_model_name = str(response_model)

            func_code = self._generate_retrofit_function(
                name, method, path, request_model, response_model_name
            )
            interface_lines.extend(["    " + line for line in func_code.split("\n")])

        interface_lines.append("}")
        api_file = api_path / "ApiService.kt"
        api_file.write_text("\n".join(interface_lines), encoding="utf-8")

        network_module = self._generate_network_module(package_name, base_url, interceptors)
        (di_path / "NetworkModule.kt").write_text(network_module, encoding="utf-8")

        analysis = self.analyzer.analyze_file(str(api_file), api_file.read_text(encoding="utf-8"))

        gradle_result = self._ensure_gradle_dependencies(project_root)

        return {
            "api_interface": str(api_file),
            "models_directory": str(models_path),
            "network_module": str(di_path / "NetworkModule.kt"),
            "endpoint_analysis": analysis,
            "gradle_dependencies_added": gradle_result,
        }

    def _generate_data_class(
        self, package_name: str, class_name: str, fields: List[Dict[str, str]]
    ) -> str:
        lines = [f"package {package_name}.models", "", f"data class {class_name}("]
        field_lines = [f"    val {f['name']}: {f.get('type', 'String')}" for f in fields]
        lines.append(",\n".join(field_lines) + "\n)")
        return "\n".join(lines)

    def _generate_retrofit_function(
        self,
        name: str,
        method: str,
        path: str,
        request_model: Optional[Dict[str, Any]],
        response_model: str,
    ) -> str:
        annotation = f'@{method}("{path}")'
        params = []
        if isinstance(request_model, dict):
            model_name = request_model.get("name", "Body")
            params.append(f"@Body {model_name.lower()}: {model_name}")
        param_str = ", ".join(params)
        return f"{annotation}\n    suspend fun {name}({param_str}): {response_model}"

    def _generate_network_module(
        self, package_name: str, base_url: str, interceptors: List[str]
    ) -> str:
        lines = [
            f"package {package_name}.di",
            "",
            "import okhttp3.OkHttpClient",
            "import okhttp3.Interceptor",
            "import retrofit2.Retrofit",
            "import retrofit2.converter.gson.GsonConverterFactory",
            "",
            "object NetworkModule {",
            "    fun provideRetrofit(): Retrofit {",
            "        val client = OkHttpClient.Builder()",
        ]
        for interceptor in interceptors:
            lines.append(f"            .addInterceptor({interceptor})")
        lines.extend(
            [
                "            .build()",
                "",
                "        return Retrofit.Builder()",
                f'            .baseUrl("{base_url}")',
                "            .client(client)",
                "            .addConverterFactory(GsonConverterFactory.create())",
                "            .build()",
                "    }",
                "}",
            ]
        )
        return "\n".join(lines)

    def _ensure_gradle_dependencies(self, project_root: Path) -> Dict[str, Any]:
        gradle_file = project_root / "build.gradle"
        if not gradle_file.exists():
            gradle_file = project_root / "build.gradle.kts"
        if not gradle_file.exists():
            return {"added": False, "reason": "Gradle file not found"}

        content = gradle_file.read_text(encoding="utf-8")
        dependencies = [
            'implementation "com.squareup.retrofit2:retrofit:2.9.0"',
            'implementation "com.squareup.retrofit2:converter-gson:2.9.0"',
            'implementation "com.squareup.okhttp3:logging-interceptor:4.10.0"',
        ]
        modified = False
        for dep in dependencies:
            if dep not in content:
                content = self._add_dependency_line(content, dep)
                modified = True
        if modified:
            gradle_file.write_text(content, encoding="utf-8")
        return {"added": modified, "file": str(gradle_file)}

    def _add_dependency_line(self, content: str, dependency: str) -> str:
        match = re.search(r"dependencies\s*\{", content)
        if not match:
            return content + f"\ndependencies {{\n    {dependency}\n}}\n"
        insert_pos = match.end()
        return content[:insert_pos] + f"\n    {dependency}" + content[insert_pos:]
