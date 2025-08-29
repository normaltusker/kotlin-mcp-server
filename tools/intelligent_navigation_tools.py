#!/usr/bin/env python3
"""Wrappers exposing intelligent navigation and refactoring capabilities."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class IntelligentCodeAnalysisTool(IntelligentToolBase):
    """Analyze Kotlin code using intelligent refactoring engine."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        file_path = arguments.get("file_path") or context.current_file
        analysis_type = arguments.get("analysis_type", "comprehensive")
        if not file_path:
            return {"error": "file_path is required"}
        return await self.refactoring_tools.analyze_code_intelligence(file_path, analysis_type)


class IntelligentRefactoringTool(IntelligentToolBase):
    """Provide or apply intelligent refactorings."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        file_path = arguments.get("file_path") or context.current_file
        if not file_path:
            return {"error": "file_path is required"}

        if arguments.get("apply"):
            action = arguments.get("refactoring_action", {})
            preview_only = arguments.get("preview_only", True)
            return await self.refactoring_tools.perform_intelligent_refactoring(
                file_path, action, preview_only
            )

        intent = arguments.get("refactoring_intent", "")
        selection_start = arguments.get("selection_start") or context.selection_start
        selection_end = arguments.get("selection_end") or context.selection_end
        return await self.refactoring_tools.suggest_intelligent_refactoring(
            file_path, intent, selection_start, selection_end
        )


class IntelligentSymbolIndexTool(IntelligentToolBase):
    """Index project symbols for navigation."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        project_path = arguments.get("project_path") or str(self.project_path)
        return await self.symbol_navigation.index_project(project_path)


class IntelligentGotoDefinitionTool(IntelligentToolBase):
    """Navigate to symbol definitions."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        file_path = arguments.get("file_path") or context.current_file
        line = arguments.get("line") or context.selection_start or 1
        column = arguments.get("column") or 1
        symbol_name = arguments.get("symbol_name")
        if not file_path:
            return {"error": "file_path is required"}
        return await self.symbol_navigation.go_to_definition(file_path, line, column, symbol_name)


class IntelligentFindReferencesTool(IntelligentToolBase):
    """Find references to symbols across the project."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        symbol_name = arguments.get("symbol_name")
        include_declarations = arguments.get("include_declarations", True)
        if not symbol_name:
            return {"error": "symbol_name is required"}
        return await self.symbol_navigation.find_references(symbol_name, include_declarations)


class IntelligentCodeCompletionTool(IntelligentToolBase):
    """Provide intelligent code completions."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        file_path = arguments.get("file_path") or context.current_file
        line = arguments.get("line") or context.selection_start or 1
        column = arguments.get("column") or context.selection_end or 1
        trigger = arguments.get("trigger_character")
        if not file_path:
            return {"error": "file_path is required"}
        return await self.symbol_navigation.intelligent_completion(file_path, line, column, trigger)


class IntelligentSymbolSearchTool(IntelligentToolBase):
    """Search symbols with intelligent filtering."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        query = arguments.get("query")
        symbol_types: Optional[List[str]] = arguments.get("symbol_types")
        fuzzy = arguments.get("fuzzy", True)
        if not query:
            return {"error": "query is required"}
        return await self.symbol_navigation.search_symbols(query, symbol_types, fuzzy)
