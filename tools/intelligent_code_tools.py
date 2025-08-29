#!/usr/bin/env python3
"""
Intelligent Code Analysis and Formatting Tools

Enhanced implementations of code analysis, formatting, and linting tools
with LSP - like intelligent capabilities.
"""

import asyncio
import json
import subprocess
from typing import Any, Dict, List, Optional

from tools.intelligent_base import (
    IntelligentToolBase,
    IntelligentToolContext,
    IntelligentToolResult,
)


class IntelligentFormattingTool(IntelligentToolBase):
    """Enhanced code formatting with intelligent analysis and suggestions."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Execute intelligent code formatting with comprehensive analysis."""

        # Pre - format analysis
        pre_format_analysis = await self._analyze_formatting_needs()

        # Execute ktlint formatting
        try:
            result = subprocess.run(
                ["./gradlew", "ktlintFormat"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Post - format analysis
            post_format_analysis = await self._analyze_formatting_results(result)

            # Generate intelligent insights
            formatting_insights = await self._generate_formatting_insights(
                pre_format_analysis, post_format_analysis
            )

            return {
                "formatting_result": {
                    "exit_code": result.returncode,
                    "output": result.stdout,
                    "errors": result.stderr,
                    "success": result.returncode == 0,
                },
                "pre_format_analysis": pre_format_analysis,
                "post_format_analysis": post_format_analysis,
                "formatting_insights": formatting_insights,
                "recommendations": await self._generate_formatting_recommendations(
                    formatting_insights
                ),
            }

        except subprocess.TimeoutExpired:
            return {"error": "Formatting timed out - project may be too large"}
        except Exception as e:
            return {"error": "Formatting failed: {str(e)}"}

    async def _analyze_formatting_needs(self) -> Dict[str, Any]:
        """Analyze code formatting needs across the project."""
        kotlin_files = list(self.project_path.rglob("*.kt"))

        files_needing_formatting: List[Dict[str, Any]] = []
        common_issues: List[str] = []

        analysis = {
            "total_files": len(kotlin_files),
            "files_needing_formatting": files_needing_formatting,
            "common_issues": common_issues,
            "style_violations": {},
        }

        # Check common formatting issues
        style_violations = {
            "long_lines": 0,
            "inconsistent_indentation": 0,
            "missing_spaces": 0,
            "trailing_whitespace": 0,
        }

        for file_path in kotlin_files[:20]:  # Limit to first 20 files for performance
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                file_issues = []

                # Check for long lines
                long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 120]
                if long_lines:
                    style_violations["long_lines"] += len(long_lines)
                    file_issues.append("Long lines: {len(long_lines)}")

                # Check for trailing whitespace
                trailing_ws = [i for i, line in enumerate(lines, 1) if line.rstrip() != line]
                if trailing_ws:
                    style_violations["trailing_whitespace"] += len(trailing_ws)
                    file_issues.append("Trailing whitespace: {len(trailing_ws)}")

                # Check for inconsistent indentation
                indent_sizes = set()
                for line in lines:
                    if line.strip():
                        leading_spaces = len(line) - len(line.lstrip(" "))
                        if leading_spaces > 0:
                            indent_sizes.add(leading_spaces % 4)

                if len(indent_sizes) > 1:
                    style_violations["inconsistent_indentation"] += 1
                    file_issues.append("Inconsistent indentation")

                if file_issues:
                    analysis["files_needing_formatting"].append(
                        {
                            "file": str(file_path.relative_to(self.project_path)),
                            "issues": file_issues,
                        }
                    )

            except Exception:
                continue  # Skip files that can't be read

        analysis["style_violations"] = style_violations
        return analysis

    async def _analyze_formatting_results(
        self, result: subprocess.CompletedProcess
    ) -> Dict[str, Any]:
        """Analyze the results of formatting operation."""
        analysis = {
            "success": result.returncode == 0,
            "files_formatted": [],
            "errors_encountered": [],
            "warnings": [],
        }

        # Parse ktlint output for formatted files
        import re

        if result.stdout:
            # Look for patterns indicating formatted files
            formatted_pattern = r"(.+\.kt).*formatted"
            matches = re.findall(formatted_pattern, result.stdout, re.IGNORECASE)
            analysis["files_formatted"] = matches

        # Parse errors
        if result.stderr:
            error_lines = result.stderr.split("\n")
            analysis["errors_encountered"] = [line for line in error_lines if line.strip()]

        return analysis

    async def _generate_formatting_insights(
        self, pre_analysis: Dict[str, Any], post_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate intelligent insights about formatting."""
        insights = {
            "formatting_impact": {
                "files_improved": len(post_analysis.get("files_formatted", [])),
                "total_violations_found": sum(pre_analysis.get("style_violations", {}).values()),
                "most_common_issue": self._find_most_common_issue(
                    pre_analysis.get("style_violations", {})
                ),
            },
            "code_quality_improvement": {
                "readability": "improved" if post_analysis.get("success") else "unchanged",
                "consistency": (
                    "improved" if len(post_analysis.get("files_formatted", [])) > 0 else "unchanged"
                ),
                "maintainability": "improved",
            },
            "team_benefits": [
                "Consistent code style across team",
                "Reduced code review time on style issues",
                "Better IDE integration and autocompletion",
            ],
        }

        return insights

    def _find_most_common_issue(self, violations: Dict[str, int]) -> str:
        """Find the most common formatting issue."""
        if not violations:
            return "none"

        max_count = max(violations.values())
        for issue, count in violations.items():
            if count == max_count:
                return issue.replace("_", " ").title()

        return "unknown"

    async def _generate_formatting_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on formatting insights."""
        recommendations = []

        impact = insights.get("formatting_impact", {})
        violations = impact.get("total_violations_found", 0)

        if violations > 50:
            recommendations.append(
                "Consider setting up pre - commit hooks to prevent formatting issues"
            )

        if impact.get("most_common_issue") == "Long Lines":
            recommendations.append("Configure IDE to show line length guide at 120 characters")

        recommendations.extend(
            [
                "Set up automatic formatting on save in your IDE",
                "Add ktlint to your CI / CD pipeline",
                "Consider using detekt for additional code quality checks",
            ]
        )

        return recommendations


class IntelligentLintTool(IntelligentToolBase):
    """Enhanced linting with intelligent issue analysis and fix suggestions."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Execute intelligent linting with comprehensive analysis."""
        lint_tool = arguments.get("lint_tool", "detekt")

        # Pre - lint analysis
        pre_lint_analysis = await self._analyze_code_quality()

        # Execute linting
        task_map = {"detekt": "detekt", "ktlint": "ktlintCheck", "android_lint": "lint"}

        task = task_map.get(lint_tool, "detekt")

        try:
            result = subprocess.run(
                ["./gradlew", task],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600,
            )

            # Analyze lint results
            lint_analysis = await self._analyze_lint_results(result, lint_tool)

            # Generate intelligent recommendations
            recommendations = await self._generate_lint_recommendations(lint_analysis)

            return {
                "lint_result": {
                    "tool": lint_tool,
                    "exit_code": result.returncode,
                    "output": result.stdout,
                    "errors": result.stderr,
                },
                "pre_lint_analysis": pre_lint_analysis,
                "lint_analysis": lint_analysis,
                "intelligent_recommendations": recommendations,
                "priority_fixes": await self._identify_priority_fixes(lint_analysis),
            }

        except subprocess.TimeoutExpired:
            return {"error": "Linting timed out - consider reducing scope or optimizing rules"}
        except Exception as e:
            return {"error": "Linting failed: {str(e)}"}

    async def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze overall code quality before linting."""
        kotlin_files = list(self.project_path.rglob("*.kt"))

        analysis = {
            "total_files": len(kotlin_files),
            "total_lines": 0,
            "complexity_hotspots": [],
            "potential_issues": {
                "null_safety": 0,
                "unused_imports": 0,
                "long_methods": 0,
                "complex_classes": 0,
            },
        }

        for file_path in kotlin_files[:15]:  # Limit for performance
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                analysis["total_lines"] += len(lines)

                # Check for potential issues
                if "!!" in content:
                    analysis["potential_issues"]["null_safety"] += content.count("!!")

                import_lines = [line for line in lines if line.strip().startswith("import")]
                analysis["potential_issues"]["unused_imports"] += len(import_lines)

                # Check for long methods (simplified)
                method_lines = 0
                in_method = False
                brace_count = 0

                for line in lines:
                    if "fun " in line and "{" in line:
                        in_method = True
                        method_lines = 1
                        brace_count = line.count("{") - line.count("}")
                    elif in_method:
                        method_lines += 1
                        brace_count += line.count("{") - line.count("}")
                        if brace_count == 0:
                            if method_lines > 30:
                                analysis["potential_issues"]["long_methods"] += 1
                            in_method = False
                            method_lines = 0

            except Exception:
                continue

        return analysis

    async def _analyze_lint_results(
        self, result: subprocess.CompletedProcess, tool: str
    ) -> Dict[str, Any]:
        """Analyze lint results with intelligent categorization."""
        analysis = {
            "tool_used": tool,
            "success": result.returncode == 0,
            "issues_found": [],
            "issue_categories": {},
            "severity_breakdown": {"error": 0, "warning": 0, "info": 0},
            "fixable_issues": [],
        }

        if result.stdout:
            issues = self._parse_lint_output(result.stdout, tool)
            analysis["issues_found"] = issues

            # Categorize issues
            categories = {}
            for issue in issues:
                category = issue.get("category", "other")
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1

                # Count by severity
                severity = issue.get("severity", "info")
                if severity in analysis["severity_breakdown"]:
                    analysis["severity_breakdown"][severity] += 1

                # Check if fixable
                if issue.get("auto_fixable", False):
                    analysis["fixable_issues"].append(issue)

            analysis["issue_categories"] = categories

        return analysis

    def _parse_lint_output(self, output: str, tool: str) -> List[Dict[str, Any]]:
        """Parse lint tool output into structured issues."""
        issues = []

        if tool == "detekt":
            issues = self._parse_detekt_output(output)
        elif tool == "ktlint":
            issues = self._parse_ktlint_output(output)
        elif tool == "android_lint":
            issues = self._parse_android_lint_output(output)

        return issues

    def _parse_detekt_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse detekt output."""
        issues = []
        import re

        # Simplified parsing - in real implementation would be more sophisticated
        pattern = r"(.+):(\d+):(\d+): (.+): (.+)"
        for match in re.finditer(pattern, output):
            issues.append(
                {
                    "file": match.group(1),
                    "line": int(match.group(2)),
                    "column": int(match.group(3)),
                    "severity": match.group(4).lower(),
                    "message": match.group(5),
                    "category": "code_quality",
                    "auto_fixable": False,
                }
            )

        return issues

    def _parse_ktlint_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse ktlint output."""
        issues = []
        import re

        pattern = r"(.+):(\d+):(\d+): (.+)"
        for match in re.finditer(pattern, output):
            issues.append(
                {
                    "file": match.group(1),
                    "line": int(match.group(2)),
                    "column": int(match.group(3)),
                    "message": match.group(4),
                    "severity": "warning",
                    "category": "formatting",
                    "auto_fixable": True,
                }
            )

        return issues

    def _parse_android_lint_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse Android lint output."""
        issues = []
        # Simplified implementation
        if "errors" in output.lower():
            issues.append(
                {
                    "file": "multiple",
                    "line": 0,
                    "column": 0,
                    "message": "Android lint found issues",
                    "severity": "warning",
                    "category": "android_specific",
                    "auto_fixable": False,
                }
            )

        return issues

    async def _generate_lint_recommendations(self, lint_analysis: Dict[str, Any]) -> List[str]:
        """Generate intelligent recommendations based on lint results."""
        recommendations = []

        issues_found = lint_analysis.get("issues_found", [])
        severity_breakdown = lint_analysis.get("severity_breakdown", {})

        if severity_breakdown.get("error", 0) > 0:
            recommendations.append("Address critical errors before proceeding with deployment")

        if severity_breakdown.get("warning", 0) > 10:
            recommendations.append("Consider fixing warnings to improve code quality")

        # Category - specific recommendations
        categories = lint_analysis.get("issue_categories", {})
        if categories.get("formatting", 0) > 5:
            recommendations.append("Run ktlintFormat to fix formatting issues automatically")

        if categories.get("code_quality", 0) > 3:
            recommendations.append(
                "Review code quality issues for potential refactoring opportunities"
            )

        # Tool - specific recommendations
        tool = lint_analysis.get("tool_used", "")
        if tool == "detekt" and len(issues_found) > 0:
            recommendations.append(
                "Consider configuring detekt rules to match your team's standards"
            )

        return recommendations

    async def _identify_priority_fixes(self, lint_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify high - priority issues that should be fixed first."""
        priority_fixes = []

        issues = lint_analysis.get("issues_found", [])

        # Prioritize by severity and category
        error_issues = [issue for issue in issues if issue.get("severity") == "error"]
        security_issues = [
            issue for issue in issues if "security" in issue.get("message", "").lower()
        ]
        performance_issues = [
            issue for issue in issues if "performance" in issue.get("message", "").lower()
        ]

        priority_fixes.extend(error_issues[:5])  # Top 5 errors
        priority_fixes.extend(security_issues[:3])  # Top 3 security issues
        priority_fixes.extend(performance_issues[:3])  # Top 3 performance issues

        return priority_fixes


class IntelligentDocumentationTool(IntelligentToolBase):
    """Enhanced documentation generation with intelligent content analysis."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Execute intelligent documentation generation."""
        doc_type = arguments.get("doc_type", "html")

        # Pre - documentation analysis
        doc_analysis = await self._analyze_documentation_needs()

        # Execute documentation generation
        task_map = {"html": "dokkaHtml", "javadoc": "dokkaJavadoc"}

        task = task_map.get(doc_type, "dokkaHtml")

        try:
            result = subprocess.run(
                ["./gradlew", task],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600,
            )

            # Analyze generated documentation
            post_doc_analysis = await self._analyze_generated_docs(result, doc_type)

            return {
                "documentation_result": {
                    "type": doc_type,
                    "exit_code": result.returncode,
                    "output": result.stdout,
                    "errors": result.stderr,
                    "success": result.returncode == 0,
                },
                "documentation_analysis": doc_analysis,
                "generation_analysis": post_doc_analysis,
                "improvement_suggestions": await self._suggest_documentation_improvements(
                    doc_analysis
                ),
            }

        except subprocess.TimeoutExpired:
            return {"error": "Documentation generation timed out"}
        except Exception as e:
            return {"error": "Documentation generation failed: {str(e)}"}

    async def _analyze_documentation_needs(self) -> Dict[str, Any]:
        """Analyze project documentation coverage and quality."""
        kotlin_files = list(self.project_path.rglob("*.kt"))

        analysis = {
            "total_files": len(kotlin_files),
            "documented_classes": 0,
            "documented_methods": 0,
            "undocumented_public_apis": [],
            "documentation_quality": {
                "has_kdoc": 0,
                "has_examples": 0,
                "has_param_docs": 0,
                "has_return_docs": 0,
            },
        }

        for file_path in kotlin_files[:10]:  # Limit for performance
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                # Analyze KDoc coverage
                in_kdoc = False
                current_kdoc = []

                for i, line in enumerate(lines):
                    stripped = line.strip()

                    # Track KDoc blocks
                    if stripped.startswith("/**"):
                        in_kdoc = True
                        current_kdoc = [stripped]
                    elif in_kdoc:
                        current_kdoc.append(stripped)
                        if stripped.endswith("*/"):
                            in_kdoc = False
                            # Check KDoc quality
                            kdoc_text = " ".join(current_kdoc)
                            if "@param" in kdoc_text:
                                analysis["documentation_quality"]["has_param_docs"] += 1
                            if "@return" in kdoc_text:
                                analysis["documentation_quality"]["has_return_docs"] += 1
                            if "example" in kdoc_text.lower():
                                analysis["documentation_quality"]["has_examples"] += 1
                            current_kdoc = []

                    # Check for class and function declarations
                    if "class " in stripped and "public" in stripped:
                        if i > 0 and "/**" in lines[i - 1]:
                            analysis["documented_classes"] += 1
                        else:
                            analysis["undocumented_public_apis"].append(
                                "{file_path.name}:{i + 1} - Class needs documentation"
                            )

                    if "fun " in stripped and "public" in stripped:
                        if i > 0 and "/**" in lines[i - 1]:
                            analysis["documented_methods"] += 1
                        else:
                            analysis["undocumented_public_apis"].append(
                                "{file_path.name}:{i + 1} - Function needs documentation"
                            )

            except Exception:
                continue

        return analysis

    async def _analyze_generated_docs(
        self, result: subprocess.CompletedProcess, doc_type: str
    ) -> Dict[str, Any]:
        """Analyze the generated documentation."""
        analysis = {
            "generation_successful": result.returncode == 0,
            "doc_type": doc_type,
            "output_size": len(result.stdout) if result.stdout else 0,
            "warnings": [],
            "generated_files": [],
        }

        # Look for documentation output directory
        docs_dir = None
        if doc_type == "html":
            docs_dir = self.project_path / "build" / "dokka" / "html"
        elif doc_type == "javadoc":
            docs_dir = self.project_path / "build" / "dokka" / "javadoc"

        if docs_dir and docs_dir.exists():
            html_files = list(docs_dir.rglob("*.html"))
            analysis["generated_files"] = [str(f.relative_to(docs_dir)) for f in html_files[:10]]

        # Parse warnings from output
        if result.stdout:
            warning_lines = [
                line for line in result.stdout.split("\n") if "warning" in line.lower()
            ]
            analysis["warnings"] = warning_lines[:5]  # Limit warnings

        return analysis

    async def _suggest_documentation_improvements(self, doc_analysis: Dict[str, Any]) -> List[str]:
        """Suggest improvements for documentation."""
        suggestions = []

        undocumented = len(doc_analysis.get("undocumented_public_apis", []))
        if undocumented > 0:
            suggestions.append("Add KDoc comments to {undocumented} undocumented public APIs")

        quality = doc_analysis.get("documentation_quality", {})
        if quality.get("has_examples", 0) < 3:
            suggestions.append("Add more code examples to improve documentation usability")

        if quality.get("has_param_docs", 0) < quality.get("has_return_docs", 0):
            suggestions.append("Document parameters for better API understanding")

        suggestions.extend(
            [
                "Consider adding architectural decision records (ADRs)",
                "Include setup and getting started guides",
                "Add diagrams for complex workflows",
                "Set up automated documentation deployment",
            ]
        )

        return suggestions
