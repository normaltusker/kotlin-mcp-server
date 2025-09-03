#!/usr/bin/env python3
"""
Intelligent Kotlin Code Analysis Engine

This module provides LSP - like intelligent analysis and refactoring capabilities
for Kotlin code, including:
- Semantic code analysis
- Intelligent refactoring suggestions
- Symbol resolution and navigation
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class SymbolType(Enum):
    CLASS = "class"
    FUNCTION = "function"
    PROPERTY = "property"
    VARIABLE = "variable"
    PARAMETER = "parameter"
    IMPORT = "import"


class RefactoringType(Enum):
    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    RENAME_SYMBOL = "rename_symbol"
    INLINE_FUNCTION = "inline_function"
    MOVE_CLASS = "move_class"
    EXTRACT_INTERFACE = "extract_interface"
    CONVERT_TO_DATA_CLASS = "convert_to_data_class"
    ADD_NULL_SAFETY = "add_null_safety"
    OPTIMIZE_IMPORTS = "optimize_imports"
    CONVERT_TO_COMPOSE = "convert_to_compose"


@dataclass
class CodeSymbol:
    name: str
    type: SymbolType
    line: int
    column: int
    end_line: int
    end_column: int
    scope: str
    modifiers: List[str]
    return_type: Optional[str] = None
    parameters: Optional[List[str]] = None
    usages: Optional[List[Tuple[int, int]]] = None

    def __post_init__(self) -> None:
        if self.parameters is None:
            self.parameters = []
        if self.usages is None:
            self.usages = []


@dataclass
class RefactoringAction:
    type: RefactoringType
    description: str
    confidence: float
    start_line: int
    end_line: int
    code_to_extract: str
    suggested_name: str
    parameters: List[str]
    return_type: Optional[str]
    preview: str
    impact_analysis: Dict[str, Any]


@dataclass
class CodeIssue:
    severity: str  # error, warning, info
    message: str
    line: int
    column: int
    rule: str
    fix_suggestion: Optional[str] = None
    auto_fixable: bool = False


class KotlinAnalyzer:
    """Advanced Kotlin code analyzer with LSP - like capabilities."""

    def __init__(self) -> None:
        self.symbols: Dict[str, List[CodeSymbol]] = {}
        self.kotlin_keywords = {
            "abstract",
            "actual",
            "annotation",
            "as",
            "break",
            "by",
            "catch",
            "class",
            "companion",
            "const",
            "constructor",
            "continue",
            "crossinline",
            "data",
            "delegate",
            "do",
            "dynamic",
            "else",
            "enum",
            "expect",
            "external",
            "false",
            "field",
            "file",
            "final",
            "finally",
            "for",
            "fun",
            "get",
            "i",
            "import",
            "in",
            "infix",
            "init",
            "inline",
            "inner",
            "interface",
            "internal",
            "is",
            "lateinit",
            "noinline",
            "null",
            "object",
            "open",
            "operator",
            "out",
            "override",
            "package",
            "param",
            "private",
            "property",
            "protected",
            "public",
            "receiver",
            "reified",
            "return",
            "sealed",
            "set",
            "setparam",
            "super",
            "suspend",
            "tailrec",
            "this",
            "throw",
            "true",
            "try",
            "typealias",
            "typeo",
            "val",
            "var",
            "vararg",
            "when",
            "where",
            "while",
        }

    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of a Kotlin file."""
        try:
            lines = content.split("\n")

            # Extract symbols
            symbols = self._extract_symbols(content, lines)

            # Detect code issues
            issues = self._detect_code_issues(content, lines)

            # Find refactoring opportunities
            refactoring_suggestions = self._suggest_refactorings(content, lines, symbols)

            # Calculate complexity metrics
            complexity = self._calculate_complexity(content, lines)

            # Analyze dependencies
            dependencies = self._analyze_dependencies(content)

            return {
                "file_path": file_path,
                "symbols": [self._symbol_to_dict(s) for s in symbols],
                "issues": [self._issue_to_dict(i) for i in issues],
                "refactoring_suggestions": [
                    self._refactoring_to_dict(r) for r in refactoring_suggestions
                ],
                "complexity_metrics": complexity,
                "dependencies": dependencies,
                "analysis_summary": {
                    "total_lines": len(lines),
                    "code_lines": len(
                        [
                            line
                            for line in lines
                            if line.strip() and not line.strip().startswith("//")
                        ]
                    ),
                    "comment_lines": len([line for line in lines if line.strip().startswith("//")]),
                    "symbol_count": len(symbols),
                    "issue_count": len(issues),
                    "refactoring_opportunities": len(refactoring_suggestions),
                },
            }
        except Exception as e:
            return {"error": "Analysis failed: {str(e)}"}

    def _extract_symbols(self, content: str, lines: List[str]) -> List[CodeSymbol]:
        """Extract code symbols (classes, functions, properties, etc.)."""
        symbols = []

        # Pattern for class declarations
        class_pattern = r"^\s*((?:public|private|protected|internal)?\s*(?:abstract|final|open|sealed)?\s*(?:data|enum|annotation)?\s * class|interface|object)\s+(\w+)"

        # Pattern for function declarations
        function_pattern = r"^\s*((?:public|private|protected|internal)?\s*(?:override|open|final|abstract|suspend|inline|infix|operator)?\s * fun)\s+(\w+)\s*\("

        # Pattern for property declarations
        property_pattern = r"^\s*((?:public|private|protected|internal)?\s*(?:override|open|final|abstract|const|lateinit)?\s*(?:val|var))\s+(\w+)"

        for i, line in enumerate(lines):
            # Extract classes
            class_match = re.search(class_pattern, line)
            if class_match:
                modifiers = class_match.group(1).split()
                name = class_match.group(2)
                symbols.append(
                    CodeSymbol(
                        name=name,
                        type=SymbolType.CLASS,
                        line=i + 1,
                        column=class_match.start(2),
                        end_line=i + 1,
                        end_column=class_match.end(2),
                        scope="file",
                        modifiers=modifiers,
                    )
                )

            # Extract functions
            function_match = re.search(function_pattern, line)
            if function_match:
                modifiers = function_match.group(1).split()
                name = function_match.group(2)

                # Extract parameters
                param_start = line.find("(", function_match.end())
                param_end = line.find(")", param_start)
                if param_start != -1 and param_end != -1:
                    param_str = line[param_start + 1 : param_end]
                    parameters = [
                        p.strip().split(":")[0].strip() for p in param_str.split(",") if p.strip()
                    ]
                else:
                    parameters = []

                # Extract return type
                return_type = None
                colon_pos = line.find(":", param_end if param_end != -1 else function_match.end())
                if colon_pos != -1:
                    brace_pos = line.find("{", colon_pos)
                    eq_pos = line.find("=", colon_pos)
                    end_pos = min(p for p in [brace_pos, eq_pos, len(line)] if p != -1)
                    return_type = line[colon_pos + 1 : end_pos].strip()

                symbols.append(
                    CodeSymbol(
                        name=name,
                        type=SymbolType.FUNCTION,
                        line=i + 1,
                        column=function_match.start(2),
                        end_line=i + 1,
                        end_column=function_match.end(2),
                        scope="class" if any("class" in l for l in lines[:i]) else "file",
                        modifiers=modifiers,
                        parameters=parameters,
                        return_type=return_type,
                    )
                )

            # Extract properties
            property_match = re.search(property_pattern, line)
            if property_match and not function_match:  # Avoid matching function parameters
                modifiers = property_match.group(1).split()
                name = property_match.group(2)
                symbols.append(
                    CodeSymbol(
                        name=name,
                        type=SymbolType.PROPERTY,
                        line=i + 1,
                        column=property_match.start(2),
                        end_line=i + 1,
                        end_column=property_match.end(2),
                        scope="class" if any("class" in l for l in lines[:i]) else "file",
                        modifiers=modifiers,
                    )
                )

        return symbols

    def _detect_code_issues(self, content: str, lines: List[str]) -> List[CodeIssue]:
        """Detect code quality issues and potential bugs."""
        issues = []

        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()

            # Long lines
            if len(line) > 120:
                issues.append(
                    CodeIssue(
                        severity="warning",
                        message="Line too long (>120 characters)",
                        line=line_num,
                        column=120,
                        rule="line_length",
                        fix_suggestion="Consider breaking this line into multiple lines",
                        auto_fixable=False,
                    )
                )

            # Non - null assertion operator
            if "!!" in line:
                issues.append(
                    CodeIssue(
                        severity="warning",
                        message="Non - null assertion operator (!!) can cause NullPointerException",
                        line=line_num,
                        column=line.find("!!"),
                        rule="null_safety",
                        fix_suggestion="Consider using safe call operator (?.) or proper null check",
                        auto_fixable=False,
                    )
                )

            # Hardcoded strings
            if re.search(r'["\'][^"\']{20,}["\']', line) and "R.string" not in line:
                issues.append(
                    CodeIssue(
                        severity="info",
                        message="Long hardcoded string should be extracted to resources",
                        line=line_num,
                        column=0,
                        rule="hardcoded_strings",
                        fix_suggestion="Extract to strings.xml resource file",
                        auto_fixable=False,
                    )
                )

            # Unused imports (simplified detection)
            if stripped.startswith("import ") and not stripped.startswith("import android."):
                import_name = stripped.split(".")[-1]
                if import_name not in content:
                    issues.append(
                        CodeIssue(
                            severity="info",
                            message="Unused import",
                            line=line_num,
                            column=0,
                            rule="unused_imports",
                            fix_suggestion="Remove unused import",
                            auto_fixable=True,
                        )
                    )

            # Missing override annotation
            if (
                re.search(r"fun\s+(?:equals|hashCode|toString)\s*\(", line)
                and "@Override" not in lines[i - 1]
                if i > 0
                else False
            ):
                issues.append(
                    CodeIssue(
                        severity="warning",
                        message="Missing @Override annotation",
                        line=line_num,
                        column=0,
                        rule="missing_override",
                        fix_suggestion="Add @Override annotation",
                        auto_fixable=True,
                    )
                )

            # Deprecated findViewById usage
            if "findViewById" in line and "kotlin - android - extensions" not in content:
                issues.append(
                    CodeIssue(
                        severity="warning",
                        message="findViewById is deprecated, use View Binding instead",
                        line=line_num,
                        column=line.find("findViewById"),
                        rule="deprecated_findviewbyid",
                        fix_suggestion="Convert to View Binding or Data Binding",
                        auto_fixable=False,
                    )
                )

            # Inefficient string concatenation
            if "+" in line and ('"' in line or "'" in line) and "StringBuilder" not in line:
                string_concat = re.search(r'["\'][^"\']*["\']\s*\+', line)
                if string_concat:
                    issues.append(
                        CodeIssue(
                            severity="info",
                            message="Consider using string templates instead of concatenation",
                            line=line_num,
                            column=string_concat.start(),
                            rule="string_concatenation",
                            fix_suggestion='Use string templates: "text $variable"',
                            auto_fixable=True,
                        )
                    )

        return issues

    def _suggest_refactorings(
        self, content: str, lines: List[str], symbols: List[CodeSymbol]
    ) -> List[RefactoringAction]:
        """Suggest intelligent refactoring actions."""
        suggestions = []

        # Find long methods that should be extracted
        for symbol in symbols:
            if symbol.type == SymbolType.FUNCTION:
                method_lines = self._get_method_lines(lines, symbol.line - 1)
                if len(method_lines) > 20:  # Long method
                    # Analyze method for extraction opportunities
                    code_blocks = self._find_extractable_blocks(method_lines)
                    for block in code_blocks:
                        suggestions.append(
                            RefactoringAction(
                                type=RefactoringType.EXTRACT_METHOD,
                                description="Extract code block from {symbol.name} into separate method",
                                confidence=0.8,
                                start_line=symbol.line + block["start"],
                                end_line=symbol.line + block["end"],
                                code_to_extract="\n".join(
                                    method_lines[block["start"] : block["end"]]
                                ),
                                suggested_name="extracted{block['start']}",
                                parameters=block.get("variables", []),
                                return_type=block.get("return_type"),
                                preview=f"private fun extracted{block['start']}(): {block.get('return_type', 'Unit')} {{\n    // extracted code\n}}",
                                impact_analysis={
                                    "complexity_reduction": len(method_lines)
                                    - block["end"]
                                    + block["start"]
                                },
                            )
                        )

        # Find classes that could be data classes
        for symbol in symbols:
            if symbol.type == SymbolType.CLASS and "data" not in symbol.modifiers:
                class_lines = self._get_class_lines(lines, symbol.line - 1)
                if self._is_data_class_candidate(class_lines):
                    suggestions.append(
                        RefactoringAction(
                            type=RefactoringType.CONVERT_TO_DATA_CLASS,
                            description="Convert {symbol.name} to data class",
                            confidence=0.9,
                            start_line=symbol.line,
                            end_line=symbol.line,
                            code_to_extract="",
                            suggested_name=symbol.name,
                            parameters=[],
                            return_type=None,
                            preview=f"data class {symbol.name}(...)",
                            impact_analysis={
                                "auto_generated_methods": ["equals", "hashCode", "toString", "copy"]
                            },
                        )
                    )

        # Find null safety improvements
        nullable_patterns = re.finditer(r"(\w+)\?\.\w+", content)
        for match in nullable_patterns:
            line_num = content[: match.start()].count("\n") + 1
            suggestions.append(
                RefactoringAction(
                    type=RefactoringType.ADD_NULL_SAFETY,
                    description="Add proper null safety check",
                    confidence=0.7,
                    start_line=line_num,
                    end_line=line_num,
                    code_to_extract=match.group(),
                    suggested_name="",
                    parameters=[],
                    return_type=None,
                    preview=f"{match.group(1)}?.let {{ /* safe operation */ }}",
                    impact_analysis={"null_safety_improvement": True},
                )
            )

        # Find Android View to Compose conversion opportunities
        if "findViewById" in content or "xml" in content.lower():
            suggestions.append(
                RefactoringAction(
                    type=RefactoringType.CONVERT_TO_COMPOSE,
                    description="Convert XML layouts to Jetpack Compose",
                    confidence=0.6,
                    start_line=1,
                    end_line=len(lines),
                    code_to_extract="",
                    suggested_name="",
                    parameters=[],
                    return_type=None,
                    preview="@Composable\nfun YourComponent() {\n    // Compose UI\n}",
                    impact_analysis={"modernization": True, "performance_improvement": True},
                )
            )

        return suggestions

    def _calculate_complexity(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """Calculate code complexity metrics."""
        # Cyclomatic complexity (simplified)
        complexity_keywords = ["i", "when", "while", "for", "catch", "&&", "||", "?:"]
        cyclomatic_complexity = 1  # Base complexity

        for keyword in complexity_keywords:
            cyclomatic_complexity += content.count(keyword)

        # Halstead metrics (simplified)
        operators = len(re.findall(r"[+\\\-*/=<>!&|%^]", content))
        operands = len(re.findall(r"\b\w+\b", content))

        # Maintainability index (simplified)
        lines_of_code = len([line for line in lines if line.strip()])
        comment_ratio = len([line for line in lines if line.strip().startswith("//")]) / max(
            lines_of_code, 1
        )

        return {
            "cyclomatic_complexity": cyclomatic_complexity,
            "lines_of_code": lines_of_code,
            "comment_ratio": comment_ratio,
            "halstead_operators": operators,
            "halstead_operands": operands,
            "maintainability_score": max(0, 100 - cyclomatic_complexity * 2 + comment_ratio * 10),
        }

    def _analyze_dependencies(self, content: str) -> Dict[str, Any]:
        """Analyze imports and dependencies."""
        import_lines = [
            line.strip() for line in content.split("\n") if line.strip().startswith("import")
        ]

        android_imports = [imp for imp in import_lines if "android" in imp]
        kotlin_imports = [imp for imp in import_lines if "kotlin" in imp]
        third_party_imports = [
            imp for imp in import_lines if not any(x in imp for x in ["android", "kotlin", "java."])
        ]

        return {
            "total_imports": len(import_lines),
            "android_imports": len(android_imports),
            "kotlin_imports": len(kotlin_imports),
            "third_party_imports": len(third_party_imports),
            "import_list": import_lines,
            "dependency_analysis": {
                "heavy_dependencies": [
                    imp
                    for imp in third_party_imports
                    if any(heavy in imp for heavy in ["retrofit", "dagger", "rxjava"])
                ],
                "compose_usage": any("compose" in imp.lower() for imp in import_lines),
                "coroutines_usage": any("coroutines" in imp.lower() for imp in import_lines),
            },
        }

    def _get_method_lines(self, lines: List[str], start_line: int) -> List[str]:
        """Extract lines belonging to a method."""
        method_lines = []
        brace_count = 0
        in_method = False

        for i in range(start_line, len(lines)):
            line = lines[i].strip()
            if "{" in line:
                in_method = True
                brace_count += line.count("{")
            if in_method:
                method_lines.append(lines[i])
                brace_count += line.count("{") - line.count("}")
                if brace_count <= 0:
                    break

        return method_lines

    def _get_class_lines(self, lines: List[str], start_line: int) -> List[str]:
        """Extract lines belonging to a class."""
        return self._get_method_lines(lines, start_line)  # Same logic for now

    def _find_extractable_blocks(self, method_lines: List[str]) -> List[Dict[str, Any]]:
        """Find code blocks that can be extracted into separate methods."""
        blocks = []
        current_block = {"start": 0, "variables": [], "return_type": "Unit"}

        for i, line in enumerate(method_lines):
            # Simple heuristic: consecutive lines doing similar operations
            if i > 0 and i % 5 == 0:  # Every 5 lines could be a block
                current_block["end"] = i
                blocks.append(current_block.copy())
                current_block = {"start": i, "variables": [], "return_type": "Unit"}

        return blocks[:3]  # Limit suggestions

    def _is_data_class_candidate(self, class_lines: List[str]) -> bool:
        """Check if a class is a good candidate for conversion to data class."""
        class_content = "\n".join(class_lines)

        # Has properties but no complex methods
        has_properties = any(re.search(r"val|var", line) for line in class_lines)
        has_simple_methods = class_content.count("fun") <= 2
        no_inheritance = "extends" not in class_content and "override" not in class_content

        return has_properties and has_simple_methods and no_inheritance

    def _symbol_to_dict(self, symbol: CodeSymbol) -> Dict[str, Any]:
        """Convert CodeSymbol to dictionary."""
        return {
            "name": symbol.name,
            "type": symbol.type.value,
            "line": symbol.line,
            "column": symbol.column,
            "end_line": symbol.end_line,
            "end_column": symbol.end_column,
            "scope": symbol.scope,
            "modifiers": symbol.modifiers,
            "return_type": symbol.return_type,
            "parameters": symbol.parameters,
            "usages": symbol.usages,
        }

    def _issue_to_dict(self, issue: CodeIssue) -> Dict[str, Any]:
        """Convert CodeIssue to dictionary."""
        return {
            "severity": issue.severity,
            "message": issue.message,
            "line": issue.line,
            "column": issue.column,
            "rule": issue.rule,
            "fix_suggestion": issue.fix_suggestion,
            "auto_fixable": issue.auto_fixable,
        }

    def _refactoring_to_dict(self, refactoring: RefactoringAction) -> Dict[str, Any]:
        """Convert RefactoringAction to dictionary."""
        return {
            "type": refactoring.type.value,
            "description": refactoring.description,
            "confidence": refactoring.confidence,
            "start_line": refactoring.start_line,
            "end_line": refactoring.end_line,
            "code_to_extract": refactoring.code_to_extract,
            "suggested_name": refactoring.suggested_name,
            "parameters": refactoring.parameters,
            "return_type": refactoring.return_type,
            "preview": refactoring.preview,
            "impact_analysis": refactoring.impact_analysis,
        }


class IntelligentRefactoring:
    """Intelligent refactoring engine with context awareness."""

    def __init__(self, project_path: str = "", security_manager: Any = None) -> None:
        self.project_path = project_path
        self.security_manager = security_manager
        self.analyzer = KotlinAnalyzer()

    def analyze_and_suggest(
        self, file_path: str, content: str, refactoring_request: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze code and provide intelligent refactoring suggestions."""
        analysis = self.analyzer.analyze_file(file_path, content)

        if refactoring_request:
            # Filter suggestions based on request
            filtered_suggestions = self._filter_suggestions(
                analysis.get("refactoring_suggestions", []), refactoring_request
            )
            analysis["targeted_suggestions"] = filtered_suggestions

        return analysis

    def _filter_suggestions(self, suggestions: List[Dict], request: str) -> List[Dict]:
        """Filter refactoring suggestions based on user request."""
        request_lower = request.lower()

        if "extract" in request_lower:
            return [s for s in suggestions if "extract" in s["type"]]
        elif "data class" in request_lower:
            return [s for s in suggestions if "data_class" in s["type"]]
        elif "compose" in request_lower:
            return [s for s in suggestions if "compose" in s["type"]]
        elif "null" in request_lower:
            return [s for s in suggestions if "null" in s["type"]]

        return suggestions
