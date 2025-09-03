#!/usr/bin/env python3
"""
Intelligent Symbol Navigation and Code Intelligence

This module provides LSP - like intelligent navigation and code understanding
capabilities for Kotlin projects.
"""

import asyncio
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SymbolDefinition:
    name: str
    type: str
    file_path: str
    line: int
    column: int
    signature: str
    documentation: Optional[str] = None
    modifiers: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.modifiers is None:
            self.modifiers = []


@dataclass
class SymbolReference:
    file_path: str
    line: int
    column: int
    context: str
    reference_type: str  # 'usage', 'declaration', 'definition'


@dataclass
class CodeCompletion:
    label: str
    kind: str  # 'function', 'property', 'class', 'keyword', etc.
    detail: str
    documentation: Optional[str]
    insert_text: str
    priority: int = 0


class IntelligentSymbolNavigation:
    """Intelligent symbol navigation with LSP - like capabilities."""

    def __init__(self) -> None:
        self.symbol_index: Dict[str, List[SymbolDefinition]] = {}
        self.project_symbols: Dict[str, SymbolDefinition] = {}
        self.kotlin_stdlib_symbols = self._load_kotlin_stdlib_symbols()

    async def index_project(self, project_path: str) -> Dict[str, Any]:
        """Index all symbols in the project for intelligent navigation."""
        try:
            project_root = Path(project_path)
            if not project_root.exists():
                return {"error": "Project path not found: {project_path}"}

            # Find all Kotlin files
            kotlin_files = list(project_root.rglob("*.kt"))

            indexing_results = {
                "total_files": len(kotlin_files),
                "symbols_indexed": 0,
                "files_processed": [],
                "indexing_errors": [],
            }

            symbols_count = 0
            files_processed_list: List[str] = []
            indexing_errors_list: List[Dict[str, str]] = []

            # Index each file
            for file_path in kotlin_files:
                try:
                    file_symbols = await self._index_file(str(file_path))
                    symbols_count += len(file_symbols)
                    files_processed_list.append(str(file_path))

                    # Update global symbol index
                    for symbol in file_symbols:
                        symbol_key = "{symbol.name}:{symbol.type}"
                        if symbol_key not in self.symbol_index:
                            self.symbol_index[symbol_key] = []
                        self.symbol_index[symbol_key].append(symbol)
                        self.project_symbols[f"{symbol.file_path}:{symbol.line}:{symbol.name}"] = (
                            symbol
                        )

                except Exception as e:
                    indexing_errors_list.append({"file": str(file_path), "error": str(e)})

            indexing_results["symbols_indexed"] = symbols_count
            indexing_results["files_processed"] = files_processed_list
            indexing_results["indexing_errors"] = indexing_errors_list

            return {
                "success": True,
                "indexing_results": indexing_results,
                "capabilities": [
                    "go_to_definition",
                    "find_references",
                    "symbol_search",
                    "intelligent_completion",
                    "hover_information",
                ],
            }

        except Exception as e:
            return {"error": "Project indexing failed: {str(e)}"}

    async def go_to_definition(
        self, file_path: str, line: int, column: int, symbol_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Find the definition of a symbol at the given position."""
        try:
            if not Path(file_path).exists():
                return {"error": "File not found: {file_path}"}

            # If symbol name not provided, extract it from position
            if not symbol_name:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if line <= len(lines):
                        line_content = lines[line - 1]
                        symbol_name = self._extract_symbol_at_position(line_content, column)

            if not symbol_name:
                return {"error": "Could not identify symbol at position"}

            # Search for symbol definition
            definitions = await self._find_symbol_definitions(symbol_name, file_path)

            if not definitions:
                # Try to find in standard library
                stdlib_def = self._find_in_stdlib(symbol_name)
                if stdlib_def:
                    definitions = [stdlib_def]

            return {
                "success": True,
                "symbol_name": symbol_name,
                "definitions": [self._symbol_to_dict(d) for d in definitions],
                "definition_count": len(definitions),
                "search_scope": ["project", "stdlib", "dependencies"],
            }

        except Exception as e:
            return {"error": "Go to definition failed: {str(e)}"}

    async def find_references(
        self, symbol_name: str, include_declarations: bool = True
    ) -> Dict[str, Any]:
        """Find all references to a symbol across the project."""
        try:
            references: List[SymbolReference] = []

            # Search across all indexed files
            for symbol_key, symbol_list in self.symbol_index.items():
                if symbol_name in symbol_key:
                    for symbol in symbol_list:
                        # Find references in the symbol's file
                        file_refs = await self._find_references_in_file(
                            symbol.file_path, symbol_name
                        )
                        references.extend(file_refs)

            # Group references by file
            references_by_file: Dict[str, List[SymbolReference]] = {}
            for ref in references:
                if ref.file_path not in references_by_file:
                    references_by_file[ref.file_path] = []
                references_by_file[ref.file_path].append(ref)

            return {
                "success": True,
                "symbol_name": symbol_name,
                "total_references": len(references),
                "files_with_references": len(references_by_file),
                "references_by_file": {
                    file: [self._reference_to_dict(ref) for ref in refs]
                    for file, refs in references_by_file.items()
                },
                "search_capabilities": [
                    "cross_file_search",
                    "declaration_detection",
                    "usage_analysis",
                    "context_awareness",
                ],
            }

        except Exception as e:
            return {"error": "Find references failed: {str(e)}"}

    async def intelligent_completion(
        self, file_path: str, line: int, column: int, trigger_character: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provide intelligent code completion suggestions."""
        try:
            if not Path(file_path).exists():
                return {"error": "File not found: {file_path}"}

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            if line > len(lines):
                return {"error": "Line number out of range"}

            # Get context around cursor
            current_line = lines[line - 1] if line > 0 else ""
            prefix = current_line[:column]

            completions = []

            # Context - aware completions
            if trigger_character == ".":
                # Member access completion
                completions.extend(await self._get_member_completions(prefix, file_path))
            elif trigger_character == "(":
                # Function parameter completion
                completions.extend(await self._get_parameter_completions(prefix))
            else:
                # General completions
                completions.extend(await self._get_general_completions(prefix, file_path))
                completions.extend(await self._get_keyword_completions(prefix))
                completions.extend(await self._get_symbol_completions(prefix))

            # Sort by priority and relevance
            completions.sort(key=lambda x: (-x.priority, x.label))

            return {
                "success": True,
                "completions": [
                    self._completion_to_dict(c) for c in completions[:50]
                ],  # Limit to 50
                "completion_context": {
                    "trigger": trigger_character,
                    "prefix": prefix,
                    "line_context": current_line,
                },
                "intelligence_features": [
                    "context_awareness",
                    "symbol_resolution",
                    "type_inference",
                    "smart_ranking",
                ],
            }

        except Exception as e:
            return {"error": "Intelligent completion failed: {str(e)}"}

    async def get_hover_information(self, file_path: str, line: int, column: int) -> Dict[str, Any]:
        """Get hover information for symbol at position."""
        try:
            if not Path(file_path).exists():
                return {"error": "File not found: {file_path}"}

            # Extract symbol at position
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if line <= len(lines):
                    line_content = lines[line - 1]
                    symbol_name = self._extract_symbol_at_position(line_content, column)
                else:
                    return {"error": "Line number out of range"}

            if not symbol_name:
                return {"error": "No symbol found at position"}

            # Find symbol information
            symbol_info = await self._get_symbol_information(symbol_name, file_path)

            return {
                "success": True,
                "symbol_name": symbol_name,
                "hover_content": symbol_info,
                "information_types": [
                    "signature",
                    "documentation",
                    "type_information",
                    "usage_examples",
                ],
            }

        except Exception as e:
            return {"error": "Hover information failed: {str(e)}"}

    async def search_symbols(
        self, query: str, symbol_types: Optional[List[str]] = None, fuzzy: bool = True
    ) -> Dict[str, Any]:
        """Search symbols across the project with intelligent filtering."""
        try:
            matching_symbols = []

            for symbol_key, symbol_list in self.symbol_index.items():
                for symbol in symbol_list:
                    # Type filtering
                    if symbol_types and symbol.type not in symbol_types:
                        continue

                    # Name matching
                    if fuzzy:
                        if self._fuzzy_match(query.lower(), symbol.name.lower()):
                            matching_symbols.append(symbol)
                    else:
                        if query.lower() in symbol.name.lower():
                            matching_symbols.append(symbol)

            # Rank by relevance
            matching_symbols.sort(
                key=lambda s: (-self._calculate_relevance_score(query, s.name), s.name)
            )

            return {
                "success": True,
                "query": query,
                "total_matches": len(matching_symbols),
                "symbols": [
                    self._symbol_to_dict(s) for s in matching_symbols[:100]
                ],  # Limit to 100
                "search_features": [
                    "fuzzy_matching",
                    "type_filtering",
                    "relevance_ranking",
                    "scope_awareness",
                ],
            }

        except Exception as e:
            return {"error": "Symbol search failed: {str(e)}"}

    async def _index_file(self, file_path: str) -> List[SymbolDefinition]:
        """Index symbols in a single file."""
        symbols = []

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        # Extract class definitions
        for i, line in enumerate(lines):
            # Class pattern
            class_match = re.search(
                r"^\s*(?:public|private|protected|internal)?\s*(?:abstract|final|open|sealed)?\s*(?:data|enum|annotation)?\s*(class|interface|object)\s+(\w+)",
                line,
            )
            if class_match:
                symbols.append(
                    SymbolDefinition(
                        name=class_match.group(2),
                        type="class",
                        file_path=file_path,
                        line=i + 1,
                        column=class_match.start(2),
                        signature=line.strip(),
                        modifiers=line.split(),
                    )
                )

            # Function pattern
            fun_match = re.search(
                r"^\s*(?:public|private|protected|internal)?\s*(?:override|open|final|abstract|suspend|inline|infix|operator)?\s*fun\s+(\w+)",
                line,
            )
            if fun_match:
                symbols.append(
                    SymbolDefinition(
                        name=fun_match.group(1),
                        type="function",
                        file_path=file_path,
                        line=i + 1,
                        column=fun_match.start(1),
                        signature=line.strip(),
                        modifiers=line.split(),
                    )
                )

            # Property pattern
            prop_match = re.search(
                r"^\s*(?:public|private|protected|internal)?\s*(?:override|open|final|abstract|const|lateinit)?\s*(?:val|var)\s+(\w+)",
                line,
            )
            if prop_match and not fun_match:  # Avoid matching function parameters
                symbols.append(
                    SymbolDefinition(
                        name=prop_match.group(1),
                        type="property",
                        file_path=file_path,
                        line=i + 1,
                        column=prop_match.start(1),
                        signature=line.strip(),
                        modifiers=line.split(),
                    )
                )

        return symbols

    async def _find_symbol_definitions(
        self, symbol_name: str, context_file: str
    ) -> List[SymbolDefinition]:
        """Find definitions of a symbol."""
        definitions = []

        # Search in symbol index
        for symbol_key, symbol_list in self.symbol_index.items():
            if symbol_name in symbol_key:
                for symbol in symbol_list:
                    if symbol.name == symbol_name:
                        definitions.append(symbol)

        return definitions

    async def _find_references_in_file(
        self, file_path: str, symbol_name: str
    ) -> List[SymbolReference]:
        """Find references to a symbol in a specific file."""
        references = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                # Simple pattern matching for symbol usage
                if symbol_name in line:
                    # More sophisticated analysis would check for actual symbol usage vs string occurrences
                    column = line.find(symbol_name)
                    references.append(
                        SymbolReference(
                            file_path=file_path,
                            line=i + 1,
                            column=column,
                            context=line.strip(),
                            reference_type="usage",
                        )
                    )

        except Exception:
            pass  # Skip files that can't be read

        return references

    async def _get_member_completions(self, prefix: str, file_path: str) -> List[CodeCompletion]:
        """Get member access completions."""
        completions = []

        # Extract the object before the dot
        object_match = re.search(r"(\w+)\.$", prefix)
        if object_match:
            object_name = object_match.group(1)

            # Find object type and suggest its members
            # This would involve type inference in a real implementation
            completions.extend(
                [
                    CodeCompletion(
                        "length", "property", "Int", "The length of the string", "length", 10
                    ),
                    CodeCompletion(
                        "isEmpty()", "function", "Boolean", "Returns true if empty", "isEmpty()", 9
                    ),
                    CodeCompletion(
                        "substring()",
                        "function",
                        "String",
                        "Returns substring",
                        "substring(${1:startIndex})",
                        8,
                    ),
                ]
            )

        return completions

    async def _get_parameter_completions(self, prefix: str) -> List[CodeCompletion]:
        """Get function parameter completions."""
        return [CodeCompletion("context", "parameter", "Context", "Android context", "context", 10)]

    async def _get_general_completions(self, prefix: str, file_path: str) -> List[CodeCompletion]:
        """Get general code completions."""
        completions = []

        # Add symbols from current file and project
        for symbol in self.project_symbols.values():
            if symbol.file_path == file_path or self._is_accessible_symbol(symbol, file_path):
                completions.append(
                    CodeCompletion(
                        label=symbol.name,
                        kind=symbol.type,
                        detail=symbol.signature,
                        documentation=symbol.documentation,
                        insert_text=symbol.name,
                        priority=8,
                    )
                )

        return completions

    async def _get_keyword_completions(self, prefix: str) -> List[CodeCompletion]:
        """Get Kotlin keyword completions."""
        keywords = [
            "class",
            "fun",
            "val",
            "var",
            "i",
            "else",
            "when",
            "for",
            "while",
            "try",
            "catch",
            "finally",
            "throw",
            "return",
            "break",
            "continue",
            "object",
            "interface",
            "abstract",
            "override",
            "open",
            "final",
        ]

        return [
            CodeCompletion(kw, "keyword", "Kotlin keyword: {kw}", "Kotlin {kw} keyword", kw, 5)
            for kw in keywords
            if kw.startswith(prefix.split()[-1] if prefix else "")
        ]

    async def _get_symbol_completions(self, prefix: str) -> List[CodeCompletion]:
        """Get symbol - based completions."""
        completions = []

        current_word = prefix.split()[-1] if prefix else ""

        for symbol_key, symbol_list in self.symbol_index.items():
            for symbol in symbol_list:
                if symbol.name.startswith(current_word):
                    completions.append(
                        CodeCompletion(
                            label=symbol.name,
                            kind=symbol.type,
                            detail=symbol.signature,
                            documentation=symbol.documentation,
                            insert_text=symbol.name,
                            priority=7,
                        )
                    )

        return completions

    def _extract_symbol_at_position(self, line: str, column: int) -> Optional[str]:
        """Extract symbol name at given position in line."""
        if column > len(line):
            return None

        # Find word boundaries around the position
        start = column
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
            start -= 1

        end = column
        while end < len(line) and (line[end].isalnum() or line[end] == "_"):
            end += 1

        if start < end:
            return line[start:end]

        return None

    async def _get_symbol_information(self, symbol_name: str, file_path: str) -> Dict[str, Any]:
        """Get comprehensive information about a symbol."""
        info: Dict[str, Any] = {
            "signature": "symbol {symbol_name}",
            "documentation": "Information about {symbol_name}",
            "type": "unknown",
            "modifiers": [],
        }

        # Find symbol in index
        for symbol_key, symbol_list in self.symbol_index.items():
            if symbol_name in symbol_key:
                for symbol in symbol_list:
                    if symbol.name == symbol_name:
                        info.update(
                            {
                                "signature": symbol.signature,
                                "type": symbol.type,
                                "modifiers": symbol.modifiers or [],
                                "file": symbol.file_path,
                                "line": str(symbol.line),
                            }
                        )
                        break

        return info

    def _fuzzy_match(self, query: str, target: str) -> bool:
        """Simple fuzzy matching algorithm."""
        query_idx = 0
        for char in target:
            if query_idx < len(query) and query[query_idx].lower() == char.lower():
                query_idx += 1
        return query_idx == len(query)

    def _calculate_relevance_score(self, query: str, target: str) -> int:
        """Calculate relevance score for search results."""
        score = 0

        if target.lower().startswith(query.lower()):
            score += 10
        elif query.lower() in target.lower():
            score += 5

        # Prefer shorter names
        score += max(0, 20 - len(target))

        return score

    def _is_accessible_symbol(self, symbol: SymbolDefinition, context_file: str) -> bool:
        """Check if symbol is accessible from context file."""
        # Simple implementation - would check visibility modifiers and imports
        return True

    def _find_in_stdlib(self, symbol_name: str) -> Optional[SymbolDefinition]:
        """Find symbol in Kotlin standard library."""
        if symbol_name in self.kotlin_stdlib_symbols:
            return self.kotlin_stdlib_symbols[symbol_name]
        return None

    def _load_kotlin_stdlib_symbols(self) -> Dict[str, SymbolDefinition]:
        """Load common Kotlin standard library symbols."""
        stdlib_symbols = {}

        # Common stdlib functions and classes
        common_symbols = [
            ("String", "class", "kotlin.String"),
            ("Int", "class", "kotlin.Int"),
            ("Boolean", "class", "kotlin.Boolean"),
            ("List", "interface", "kotlin.collections.List"),
            ("Map", "interface", "kotlin.collections.Map"),
            ("println", "function", "kotlin.io.println"),
            ("print", "function", "kotlin.io.print"),
            ("let", "function", "kotlin.let"),
            ("apply", "function", "kotlin.apply"),
            ("also", "function", "kotlin.also"),
            ("run", "function", "kotlin.run"),
        ]

        for name, symbol_type, signature in common_symbols:
            stdlib_symbols[name] = SymbolDefinition(
                name=name,
                type=symbol_type,
                file_path="<stdlib>",
                line=0,
                column=0,
                signature=signature,
                documentation="Kotlin standard library {symbol_type}: {name}",
            )

        return stdlib_symbols

    def _symbol_to_dict(self, symbol: SymbolDefinition) -> Dict[str, Any]:
        """Convert SymbolDefinition to dictionary."""
        return {
            "name": symbol.name,
            "type": symbol.type,
            "file_path": symbol.file_path,
            "line": symbol.line,
            "column": symbol.column,
            "signature": symbol.signature,
            "documentation": symbol.documentation,
            "modifiers": symbol.modifiers,
        }

    def _reference_to_dict(self, reference: SymbolReference) -> Dict[str, Any]:
        """Convert SymbolReference to dictionary."""
        return {
            "file_path": reference.file_path,
            "line": reference.line,
            "column": reference.column,
            "context": reference.context,
            "reference_type": reference.reference_type,
        }

    def _completion_to_dict(self, completion: CodeCompletion) -> Dict[str, Any]:
        """Convert CodeCompletion to dictionary."""
        return {
            "label": completion.label,
            "kind": completion.kind,
            "detail": completion.detail,
            "documentation": completion.documentation,
            "insert_text": completion.insert_text,
            "priority": completion.priority,
        }
