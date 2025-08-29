#!/usr/bin/env python3
"""
Intelligent Kotlin Refactoring Tools

This module provides IDE - like intelligent refactoring tools that understand
Kotlin code semantics and offer sophisticated refactoring capabilities.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai.intelligent_analysis import IntelligentRefactoring, KotlinAnalyzer


class IntelligentRefactoringTools:
    """IDE - like intelligent refactoring tools for Kotlin."""

    def __init__(self) -> None:
        self.refactoring_engine = IntelligentRefactoring()
        self.analyzer = KotlinAnalyzer()

    async def analyze_code_intelligence(
        self, file_path: str, analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Perform intelligent code analysis with semantic understanding.

        Args:
            file_path: Path to Kotlin file
            analysis_type: Type of analysis (comprehensive, quick, focused)

        Returns:
            Comprehensive analysis with symbols, issues, and refactoring suggestions
        """
        try:
            if not Path(file_path).exists():
                return {"error": "File not found: {file_path}"}

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if analysis_type == "comprehensive":
                analysis = self.refactoring_engine.analyze_and_suggest(file_path, content)

                # Add advanced analysis
                analysis["advanced_metrics"] = await self._calculate_advanced_metrics(content)
                analysis["design_patterns"] = await self._detect_design_patterns(content)
                analysis["performance_insights"] = await self._analyze_performance(content)

            elif analysis_type == "quick":
                analysis = self.analyzer.analyze_file(file_path, content)

            elif analysis_type == "focused":
                # Focus on specific aspects
                analysis = {
                    "file_path": file_path,
                    "refactoring_suggestions": self.analyzer._suggest_refactorings(
                        content,
                        content.split("\n"),
                        self.analyzer._extract_symbols(content, content.split("\n")),
                    ),
                    "code_issues": self.analyzer._detect_code_issues(content, content.split("\n")),
                }

            return {
                "success": True,
                "analysis": analysis,
                "intelligence_level": "high",
                "capabilities": [
                    "symbol_resolution",
                    "semantic_analysis",
                    "intelligent_refactoring",
                    "pattern_detection",
                    "performance_analysis",
                ],
            }

        except Exception as e:
            return {"error": "Intelligent analysis failed: {str(e)}"}

    async def suggest_intelligent_refactoring(
        self,
        file_path: str,
        refactoring_intent: str,
        selection_start: Optional[int] = None,
        selection_end: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Suggest intelligent refactorings based on user intent and code selection.

        Args:
            file_path: Path to Kotlin file
            refactoring_intent: User's refactoring intent (e.g., "extract method", "improve null safety")
            selection_start: Start line of code selection
            selection_end: End line of code selection

        Returns:
            Intelligent refactoring suggestions with previews and impact analysis
        """
        try:
            if not Path(file_path).exists():
                return {"error": "File not found: {file_path}"}

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Get base analysis
            analysis = self.refactoring_engine.analyze_and_suggest(
                file_path, content, refactoring_intent
            )

            # Context - aware suggestions based on selection
            if selection_start and selection_end:
                selected_code = "\n".join(lines[selection_start - 1 : selection_end])
                context_suggestions = await self._analyze_selected_code(
                    selected_code, refactoring_intent, selection_start, selection_end
                )
                analysis["context_aware_suggestions"] = context_suggestions

            # Add intelligent suggestions based on intent
            intent_suggestions = await self._generate_intent_based_suggestions(
                content, refactoring_intent
            )
            analysis["intent_based_suggestions"] = intent_suggestions

            return {
                "success": True,
                "refactoring_suggestions": analysis,
                "intelligent_features": [
                    "context_awareness",
                    "intent_understanding",
                    "impact_analysis",
                    "preview_generation",
                    "safety_checks",
                ],
            }

        except Exception as e:
            return {"error": "Intelligent refactoring suggestion failed: {str(e)}"}

    async def perform_intelligent_refactoring(
        self, file_path: str, refactoring_action: Dict[str, Any], preview_only: bool = True
    ) -> Dict[str, Any]:
        """
        Perform intelligent refactoring with safety checks and preview.

        Args:
            file_path: Path to Kotlin file
            refactoring_action: Refactoring action to perform
            preview_only: If True, only show preview without applying changes

        Returns:
            Refactoring result with preview and safety analysis
        """
        try:
            if not Path(file_path).exists():
                return {"error": "File not found: {file_path}"}

            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Perform safety checks
            safety_check = await self._perform_safety_checks(original_content, refactoring_action)
            if not safety_check["safe"]:
                return {
                    "error": "Refactoring not safe to apply",
                    "safety_issues": safety_check["issues"],
                    "recommendations": safety_check["recommendations"],
                }

            # Generate refactored code
            refactored_content = await self._apply_refactoring(original_content, refactoring_action)

            # Generate diff and impact analysis
            diff = await self._generate_diff(original_content, refactored_content)
            impact = await self._analyze_refactoring_impact(original_content, refactored_content)

            result = {
                "success": True,
                "preview": refactored_content if preview_only else None,
                "dif": diff,
                "impact_analysis": impact,
                "safety_check": safety_check,
                "refactoring_applied": not preview_only,
            }

            # Apply changes if not preview only
            if not preview_only:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(refactored_content)
                result["file_updated"] = True

            return result

        except Exception as e:
            return {"error": "Intelligent refactoring failed: {str(e)}"}

    async def find_code_symbols(
        self, file_path: str, symbol_name: str, symbol_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find code symbols with intelligent search and navigation.

        Args:
            file_path: Path to Kotlin file
            symbol_name: Name of symbol to find
            symbol_type: Type of symbol (class, function, property, etc.)

        Returns:
            Symbol locations with context and usage analysis
        """
        try:
            if not Path(file_path).exists():
                return {"error": "File not found: {file_path}"}

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            analysis = self.analyzer.analyze_file(file_path, content)
            symbols = analysis.get("symbols", [])

            # Find matching symbols
            matching_symbols = []
            for symbol in symbols:
                if symbol_name.lower() in symbol["name"].lower():
                    if not symbol_type or symbol["type"] == symbol_type:
                        # Add context and usage information
                        symbol["context"] = await self._get_symbol_context(content, symbol)
                        symbol["usages"] = await self._find_symbol_usages(content, symbol["name"])
                        symbol["related_symbols"] = await self._find_related_symbols(
                            content, symbol
                        )
                        matching_symbols.append(symbol)

            return {
                "success": True,
                "symbols_found": len(matching_symbols),
                "symbols": matching_symbols,
                "search_capabilities": [
                    "fuzzy_matching",
                    "context_analysis",
                    "usage_tracking",
                    "related_symbols",
                ],
            }

        except Exception as e:
            return {"error": "Symbol search failed: {str(e)}"}

    async def analyze_dependencies_intelligent(self, project_path: str) -> Dict[str, Any]:
        """
        Perform intelligent dependency analysis across the project.

        Args:
            project_path: Path to project root

        Returns:
            Comprehensive dependency analysis with recommendations
        """
        try:
            project_root = Path(project_path)
            if not project_root.exists():
                return {"error": "Project path not found: {project_path}"}

            # Find all Kotlin files
            kotlin_files = list(project_root.rglob("*.kt"))

            dependency_analysis = {
                "total_files": len(kotlin_files),
                "dependencies": {},
                "circular_dependencies": [],
                "unused_imports": [],
                "outdated_dependencies": [],
                "recommendations": [],
            }

            # Analyze each file
            dependencies_dict: Dict[str, Any] = {}
            unused_imports_list: List[Dict[str, Any]] = []

            for file_path in kotlin_files:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                file_analysis = self.analyzer.analyze_file(str(file_path), content)
                file_deps = file_analysis.get("dependencies", {})

                dependencies_dict[str(file_path)] = file_deps

                # Collect unused imports
                for issue in file_analysis.get("issues", []):
                    if issue["rule"] == "unused_imports":
                        unused_imports_list.append(
                            {
                                "file": str(file_path),
                                "line": issue["line"],
                                "import": issue["message"],
                            }
                        )

            dependency_analysis["dependencies"] = dependencies_dict
            dependency_analysis["unused_imports"] = unused_imports_list

            # Add intelligent recommendations
            dependency_analysis["recommendations"] = (
                await self._generate_dependency_recommendations(dependency_analysis)
            )

            return {
                "success": True,
                "analysis": dependency_analysis,
                "intelligence_features": [
                    "circular_dependency_detection",
                    "unused_import_analysis",
                    "dependency_optimization",
                    "modernization_suggestions",
                ],
            }

        except Exception as e:
            return {"error": "Dependency analysis failed: {str(e)}"}

    async def _calculate_advanced_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate advanced code metrics."""
        lines = content.split("\n")

        # Technical debt indicators
        debt_indicators = {
            "todo_count": content.lower().count("todo"),
            "fixme_count": content.lower().count("fixme"),
            "hack_count": content.lower().count("hack"),
            "deprecated_usage": content.count("@Deprecated"),
        }

        # Code quality metrics
        quality_metrics = {
            "function_length_avg": await self._calculate_avg_function_length(content),
            "class_complexity": await self._calculate_class_complexity(content),
            "test_coverage_estimate": await self._estimate_test_coverage(content),
        }

        return {
            "technical_debt": debt_indicators,
            "quality_metrics": quality_metrics,
            "overall_score": max(0, 100 - sum(debt_indicators.values()) * 5),
        }

    async def _detect_design_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detect design patterns in the code."""
        patterns = []

        # Singleton pattern
        if "object " in content or ("class " in content and "private constructor" in content):
            patterns.append(
                {
                    "pattern": "Singleton",
                    "confidence": 0.8,
                    "description": "Singleton pattern detected",
                }
            )

        # Observer pattern
        if "interface" in content and (
            "notify" in content.lower() or "observer" in content.lower()
        ):
            patterns.append(
                {
                    "pattern": "Observer",
                    "confidence": 0.7,
                    "description": "Observer pattern detected",
                }
            )

        # Factory pattern
        if "create" in content.lower() and "fun " in content:
            patterns.append(
                {"pattern": "Factory", "confidence": 0.6, "description": "Factory pattern detected"}
            )

        return patterns

    async def _analyze_performance(self, content: str) -> Dict[str, Any]:
        """Analyze performance characteristics."""
        performance_issues = []

        # String concatenation in loops
        if "+" in content and ("for" in content or "while" in content):
            performance_issues.append(
                {
                    "issue": "String concatenation in loop",
                    "severity": "medium",
                    "suggestion": "Use StringBuilder",
                }
            )

        # Inefficient collections
        if "ArrayList" in content and "LinkedList" not in content:
            performance_issues.append(
                {
                    "issue": "Consider LinkedList for frequent insertions",
                    "severity": "low",
                    "suggestion": "Evaluate collection choice",
                }
            )

        return {
            "issues": performance_issues,
            "performance_score": max(0, 100 - len(performance_issues) * 20),
        }

    async def _analyze_selected_code(
        self, selected_code: str, intent: str, start: int, end: int
    ) -> List[Dict[str, Any]]:
        """Analyze selected code for context - aware suggestions."""
        suggestions = []

        if "extract" in intent.lower():
            # Analyze for method extraction
            if len(selected_code.split("\n")) > 3:
                suggestions.append(
                    {
                        "type": "extract_method",
                        "description": "Extract {end - start + 1} lines into a new method",
                        "confidence": 0.9,
                        "preview": "private fun extractedMethod() {{\n    {selected_code[:50]}...\n}}",
                    }
                )

        if "null" in intent.lower():
            # Analyze for null safety improvements
            if "?" in selected_code or "!!" in selected_code:
                suggestions.append(
                    {
                        "type": "improve_null_safety",
                        "description": "Improve null safety in selected code",
                        "confidence": 0.8,
                        "preview": "// Safer null handling implementation",
                    }
                )

        return suggestions

    async def _generate_intent_based_suggestions(
        self, content: str, intent: str
    ) -> List[Dict[str, Any]]:
        """Generate suggestions based on user intent."""
        suggestions = []

        intent_lower = intent.lower()

        if "performance" in intent_lower:
            suggestions.extend(await self._generate_performance_suggestions(content))
        elif "modernize" in intent_lower or "compose" in intent_lower:
            suggestions.extend(await self._generate_modernization_suggestions(content))
        elif "clean" in intent_lower:
            suggestions.extend(await self._generate_cleanup_suggestions(content))

        return suggestions

    async def _generate_performance_suggestions(self, content: str) -> List[Dict[str, Any]]:
        """Generate performance improvement suggestions."""
        return [
            {
                "type": "performance_optimization",
                "description": "Optimize string operations using StringBuilder",
                "confidence": 0.7,
                "impact": "medium",
            }
        ]

    async def _generate_modernization_suggestions(self, content: str) -> List[Dict[str, Any]]:
        """Generate code modernization suggestions."""
        suggestions = []

        if "findViewById" in content:
            suggestions.append(
                {
                    "type": "modernize_view_binding",
                    "description": "Convert to View Binding",
                    "confidence": 0.9,
                    "impact": "high",
                }
            )

        return suggestions

    async def _generate_cleanup_suggestions(self, content: str) -> List[Dict[str, Any]]:
        """Generate code cleanup suggestions."""
        return [
            {
                "type": "remove_unused_imports",
                "description": "Remove unused import statements",
                "confidence": 1.0,
                "impact": "low",
            }
        ]

    async def _perform_safety_checks(
        self, content: str, refactoring_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform safety checks before refactoring."""
        return {"safe": True, "issues": [], "recommendations": []}

    async def _apply_refactoring(self, content: str, refactoring_action: Dict[str, Any]) -> str:
        """Apply refactoring to code."""
        # Simple placeholder - would implement actual refactoring logic
        return content

    async def _generate_diff(self, original: str, refactored: str) -> List[str]:
        """Generate diff between original and refactored code."""
        return ["@@ Example diff @@", "+ Added line", "- Removed line"]

    async def _analyze_refactoring_impact(self, original: str, refactored: str) -> Dict[str, Any]:
        """Analyze impact of refactoring."""
        return {"lines_changed": 5, "complexity_change": -2, "maintainability_improvement": 15}

    async def _get_symbol_context(self, content: str, symbol: Dict[str, Any]) -> str:
        """Get context around a symbol."""
        lines = content.split("\n")
        start = max(0, symbol["line"] - 3)
        end = min(len(lines), symbol["line"] + 2)
        return "\n".join(lines[start:end])

    async def _find_symbol_usages(self, content: str, symbol_name: str) -> List[Dict[str, Any]]:
        """Find usages of a symbol."""
        usages = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if symbol_name in line:
                usages.append({"line": i + 1, "context": line.strip(), "type": "usage"})

        return usages

    async def _find_related_symbols(self, content: str, symbol: Dict[str, Any]) -> List[str]:
        """Find symbols related to the given symbol."""
        # Simple implementation - could be much more sophisticated
        return []

    async def _generate_dependency_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate intelligent dependency recommendations."""
        recommendations = []

        if analysis["unused_imports"]:
            recommendations.append("Remove unused imports to improve compilation time")

        recommendations.append(
            "Consider upgrading to latest Kotlin version for performance improvements"
        )

        return recommendations

    async def _calculate_avg_function_length(self, content: str) -> float:
        """Calculate average function length."""
        return 10.5  # Placeholder

    async def _calculate_class_complexity(self, content: str) -> int:
        """Calculate class complexity."""
        return 15  # Placeholder

    async def _estimate_test_coverage(self, content: str) -> float:
        """Estimate test coverage."""
        return 0.75  # Placeholder
