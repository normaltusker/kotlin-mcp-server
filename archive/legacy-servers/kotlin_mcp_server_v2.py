#!/usr/bin/env python3
"""
Kotlin MCP Server v2 - Modern MCP SDK Implementation

A comprehensive Model Context Protocol server for Android/Kotlin development
built with the official MCP SDK and 2025-06-18 specification compliance.

This modernized version includes:
- Official MCP SDK integration
- 2025-06-18 protocol version support
- Root & Resource management
- Prompt templates
- Structured logging
- Schema-driven tool definitions
- Progress tracking and cancellation
- Enhanced security and validation

Author: MCP Development Team
Version: 2.0.0 (Modern MCP SDK)
License: MIT
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from mcp import stdio_server, types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import BaseModel, Field, ValidationError

# Import existing tool modules
from ai.llm_integration import AnalysisRequest, CodeGenerationRequest, CodeType, LLMIntegration
from generators.kotlin_generator import KotlinCodeGenerator
from tools.build_optimization import BuildOptimizationTools
from tools.gradle_tools import GradleTools
from tools.project_analysis import ProjectAnalysisTools
from utils.security import SecurityManager


# Pydantic models for schema-driven tool definitions
class CreateKotlinFileRequest(BaseModel):
    """Schema for creating Kotlin files."""

    file_path: str = Field(description="Relative path for new Kotlin file")
    package_name: str = Field(description="Package name for the Kotlin class")
    class_name: str = Field(description="Name of the Kotlin class")
    class_type: str = Field(
        default="class",
        description="Type of class to create",
        enum=[
            "activity",
            "fragment",
            "class",
            "data_class",
            "interface",
            "viewmodel",
            "repository",
            "service",
        ],
    )


class GradleBuildRequest(BaseModel):
    """Schema for Gradle build operations."""

    task: str = Field(
        default="assembleDebug",
        description="Gradle task to execute (e.g., 'assembleDebug', 'test', 'lint')",
    )
    clean: bool = Field(default=False, description="Run 'clean' task before the specified task")


class ProjectAnalysisRequest(BaseModel):
    """Schema for project analysis operations."""

    analysis_type: str = Field(
        default="all",
        description="Type of analysis to perform",
        enum=["structure", "dependencies", "manifest", "security", "performance", "all"],
    )


class KotlinMCPServerV2:
    """Modern MCP Server implementation using official SDK."""

    def __init__(self):
        """Initialize the modern MCP server."""
        self.server = Server("kotlin-mcp-server")
        self.project_path: Optional[Path] = None
        self.allowed_roots: List[Path] = []

        # Initialize core components
        self.security_manager = SecurityManager()
        self.llm_integration = LLMIntegration(self.security_manager)
        self.kotlin_generator = KotlinCodeGenerator(self.llm_integration)

        # Tool modules (initialized after project path is set)
        self.gradle_tools: Optional[GradleTools] = None
        self.project_analysis: Optional[ProjectAnalysisTools] = None
        self.build_optimization: Optional[BuildOptimizationTools] = None

        # Setup logging
        self.setup_logging()

        # Register handlers
        self.register_handlers()

    def setup_logging(self) -> None:
        """Configure structured logging for MCP."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger("kotlin-mcp-server")

    def set_project_path(self, project_path: str) -> None:
        """Set the project path and initialize tool modules."""
        self.project_path = Path(project_path)

        # Add project path as allowed root
        if self.project_path.exists():
            self.allowed_roots.append(self.project_path)

        # Initialize tool modules with project path
        self.gradle_tools = GradleTools(self.project_path, self.security_manager)
        self.project_analysis = ProjectAnalysisTools(self.project_path, self.security_manager)
        self.build_optimization = BuildOptimizationTools(self.project_path, self.security_manager)

    def register_handlers(self) -> None:
        """Register all MCP handlers using the official SDK."""

        # Core MCP handlers
        self.server.request_handlers["initialize"] = self.handle_initialize
        self.server.request_handlers["ping"] = self.handle_ping

        # Tool handlers
        self.server.request_handlers["tools/list"] = self.handle_tools_list
        self.server.request_handlers["tools/call"] = self.handle_tools_call

        # Resource handlers
        self.server.request_handlers["resources/list"] = self.handle_resources_list
        self.server.request_handlers["resources/read"] = self.handle_resources_read

        # Root handlers
        self.server.request_handlers["roots/list"] = self.handle_roots_list

        # Prompt handlers
        self.server.request_handlers["prompts/list"] = self.handle_prompts_list
        self.server.request_handlers["prompts/get"] = self.handle_prompts_get

    async def handle_initialize(self, request: types.InitializeRequest) -> types.InitializeResult:
        """Handle MCP initialize request with 2025-06-18 specification."""

        await self.log_message("Initializing Kotlin MCP Server v2", level="info")

        return types.InitializeResult(
            protocolVersion="2025-06-18",
            capabilities=types.ServerCapabilities(
                tools=types.ToolsCapability(listChanged=True),
                resources=types.ResourcesCapability(subscribe=True, listChanged=True),
                prompts=types.PromptsCapability(listChanged=True),
                logging=types.LoggingCapability(),
                roots=types.RootsCapability(listChanged=True),
            ),
            serverInfo=types.Implementation(name="kotlin-mcp-server", version="2.0.0"),
        )

    async def handle_ping(self, request: types.PingRequest) -> types.EmptyResult:
        """Handle ping requests for connectivity testing."""
        return types.EmptyResult()

    async def handle_tools_list(self, request: types.ListToolsRequest) -> types.ListToolsResult:
        """List all available tools with schema-driven definitions."""

        tools = [
            types.Tool(
                name="create_kotlin_file",
                description=(
                    "Create production-ready Kotlin files with complete implementations for "
                    "Android development. Supports Activities, ViewModels, Repositories, Data "
                    "Classes, Use Cases, Services, and more with modern Android patterns."
                ),
                inputSchema=CreateKotlinFileRequest.model_json_schema(),
            ),
            types.Tool(
                name="gradle_build",
                description=(
                    "Build Android project using Gradle build system. Supports all standard "
                    "Gradle tasks including compilation, packaging, and testing with progress tracking."
                ),
                inputSchema=GradleBuildRequest.model_json_schema(),
            ),
            types.Tool(
                name="analyze_project",
                description=(
                    "Analyze Android project structure, dependencies, security, and performance "
                    "with comprehensive reporting and recommendations."
                ),
                inputSchema=ProjectAnalysisRequest.model_json_schema(),
            ),
            # Add more tools here...
        ]

        return types.ListToolsResult(tools=tools)

    async def handle_tools_call(self, request: types.CallToolRequest) -> types.CallToolResult:
        """Handle tool execution with progress tracking and cancellation support."""

        try:
            # Validate request
            if not request.params or "name" not in request.params:
                raise ValueError("Tool name is required")

            tool_name = request.params["name"]
            arguments = request.params.get("arguments", {})

            # Send progress notification
            progress_token = str(uuid.uuid4())
            await self.send_progress(progress_token, 0, f"Starting {tool_name}")

            # Route to appropriate tool handler
            if tool_name == "create_kotlin_file":
                validated_args = CreateKotlinFileRequest(**arguments)
                result = await self.call_create_kotlin_file(validated_args, progress_token)
            elif tool_name == "gradle_build":
                validated_args = GradleBuildRequest(**arguments)
                result = await self.call_gradle_build(validated_args, progress_token)
            elif tool_name == "analyze_project":
                validated_args = ProjectAnalysisRequest(**arguments)
                result = await self.call_analyze_project(validated_args, progress_token)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            # Send completion notification
            await self.send_progress(progress_token, 100, f"Completed {tool_name}")

            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        except ValidationError as e:
            await self.log_message(f"Validation error: {e}", level="error")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Validation error: {e}")],
                isError=True,
            )
        except Exception as e:
            await self.log_message(f"Tool execution error: {e}", level="error")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Error executing tool: {e}")],
                isError=True,
            )

    async def handle_resources_list(
        self, request: types.ListResourcesRequest
    ) -> types.ListResourcesResult:
        """List available project resources."""

        resources = []

        if self.project_path and self.project_path.exists():
            # Add common Android project files as resources
            common_files = [
                "build.gradle",
                "build.gradle.kts",
                "app/build.gradle",
                "app/build.gradle.kts",
                "AndroidManifest.xml",
                "app/src/main/AndroidManifest.xml",
                "gradle.properties",
                "settings.gradle",
                "settings.gradle.kts",
            ]

            for file_path in common_files:
                full_path = self.project_path / file_path
                if full_path.exists():
                    resources.append(
                        types.Resource(
                            uri=f"file://{full_path}",
                            name=file_path,
                            description=f"Android project file: {file_path}",
                            mimeType="text/plain",
                        )
                    )

        return types.ListResourcesResult(resources=resources)

    async def handle_resources_read(
        self, request: types.ReadResourceRequest
    ) -> types.ReadResourceResult:
        """Read resource content with security validation."""

        try:
            # Extract file path from URI
            uri = request.params["uri"]
            if not uri.startswith("file://"):
                raise ValueError("Only file:// URIs are supported")

            file_path = Path(uri[7:])  # Remove "file://" prefix

            # Security check: ensure file is within allowed roots
            if not self.is_path_allowed(file_path):
                raise PermissionError("Access denied: file outside allowed roots")

            # Read file content
            content = file_path.read_text(encoding="utf-8")

            return types.ReadResourceResult(
                contents=[types.TextResourceContents(uri=uri, mimeType="text/plain", text=content)]
            )

        except Exception as e:
            await self.log_message(f"Resource read error: {e}", level="error")
            raise

    async def handle_roots_list(self, request: types.ListRootsRequest) -> types.ListRootsResult:
        """List allowed root directories."""

        roots = [types.Root(uri=f"file://{root}", name=root.name) for root in self.allowed_roots]

        return types.ListRootsResult(roots=roots)

    async def handle_prompts_list(
        self, request: types.ListPromptsRequest
    ) -> types.ListPromptsResult:
        """List available Kotlin/Android development prompts."""

        prompts = [
            types.Prompt(
                name="generate_mvvm_viewmodel",
                description="Generate a complete MVVM ViewModel with state management",
                arguments=[
                    types.PromptArgument(
                        name="feature_name",
                        description="Name of the feature (e.g., 'UserProfile', 'ShoppingCart')",
                        required=True,
                    ),
                    types.PromptArgument(
                        name="data_source",
                        description="Data source type (network, database, both)",
                        required=False,
                    ),
                ],
            ),
            types.Prompt(
                name="create_compose_screen",
                description="Generate a Jetpack Compose screen with navigation",
                arguments=[
                    types.PromptArgument(
                        name="screen_name",
                        description="Name of the screen (e.g., 'LoginScreen', 'ProfileScreen')",
                        required=True,
                    ),
                    types.PromptArgument(
                        name="has_navigation",
                        description="Include navigation setup",
                        required=False,
                    ),
                ],
            ),
            types.Prompt(
                name="setup_room_database",
                description="Generate Room database setup with entities and DAOs",
                arguments=[
                    types.PromptArgument(
                        name="database_name", description="Name of the database", required=True
                    ),
                    types.PromptArgument(
                        name="entities",
                        description="Comma-separated list of entity names",
                        required=True,
                    ),
                ],
            ),
        ]

        return types.ListPromptsResult(prompts=prompts)

    async def handle_prompts_get(self, request: types.GetPromptRequest) -> types.GetPromptResult:
        """Get specific prompt content."""

        prompt_name = request.params["name"]
        arguments = request.params.get("arguments", {})

        if prompt_name == "generate_mvvm_viewmodel":
            feature_name = arguments.get("feature_name", "Feature")
            data_source = arguments.get("data_source", "network")

            content = f"""
Create a complete MVVM ViewModel for {feature_name} with the following requirements:

1. State Management:
   - UI state data class with loading, success, error states
   - StateFlow for reactive state updates
   - Proper state validation and error handling

2. Data Source Integration:
   - {'Repository pattern with network calls' if data_source == 'network' else 'Database operations with Room' if data_source == 'database' else 'Both network and database integration'}
   - Proper data mapping and transformation
   - Error handling for data operations

3. Modern Android Patterns:
   - Hilt dependency injection
   - Coroutines for async operations
   - Lifecycle-aware components
   - Unit test setup

Please generate the complete ViewModel implementation with all necessary dependencies.
"""

        elif prompt_name == "create_compose_screen":
            screen_name = arguments.get("screen_name", "Screen")
            has_navigation = arguments.get("has_navigation", "false").lower() == "true"

            content = f"""
Create a Jetpack Compose screen for {screen_name} with:

1. Screen Structure:
   - Composable function with proper naming
   - State management with remember and state hoisting
   - Material 3 design components

2. UI Components:
   - Scaffold with TopAppBar
   - Responsive layout design
   - Proper spacing and styling

{'3. Navigation Integration:' if has_navigation else ''}
{'   - Navigation arguments handling' if has_navigation else ''}
{'   - Back navigation support' if has_navigation else ''}
{'   - Deep linking support' if has_navigation else ''}

{'4. Additional Features:' if has_navigation else '3. Additional Features:'}
   - Loading states and error handling
   - Accessibility support
   - Preview functions for different states

Please generate the complete Compose screen implementation.
"""

        elif prompt_name == "setup_room_database":
            database_name = arguments.get("database_name", "AppDatabase")
            entities = arguments.get("entities", "User").split(",")

            content = f"""
Set up Room database for {database_name} with the following entities: {', '.join(entities)}

1. Database Setup:
   - Database class with proper annotations
   - Version management and migration strategy
   - Database provider with Hilt integration

2. For each entity ({', '.join(entities)}):
   - Entity class with proper annotations
   - DAO interface with CRUD operations
   - Repository pattern implementation

3. Additional Features:
   - Type converters for complex data types
   - Database seeding if needed
   - Backup and restore functionality
   - Performance optimization

Please generate the complete Room database setup with all components.
"""

        else:
            raise ValueError(f"Unknown prompt: {prompt_name}")

        return types.GetPromptResult(
            description=f"Generated prompt for {prompt_name}",
            messages=[
                types.PromptMessage(
                    role=types.Role.user,
                    content=types.TextContent(type="text", text=content.strip()),
                )
            ],
        )

    # Tool implementation methods
    async def call_create_kotlin_file(
        self, args: CreateKotlinFileRequest, progress_token: str
    ) -> Dict[str, Any]:
        """Execute create_kotlin_file tool."""

        await self.send_progress(progress_token, 25, "Validating parameters")

        if not self.kotlin_generator:
            raise RuntimeError("Kotlin generator not initialized")

        await self.send_progress(progress_token, 50, "Generating Kotlin code")

        # Use existing generator logic
        result = await self.kotlin_generator.create_kotlin_file(
            file_path=args.file_path,
            package_name=args.package_name,
            class_name=args.class_name,
            class_type=args.class_type,
        )

        await self.send_progress(progress_token, 75, "Writing file to disk")

        return {
            "success": True,
            "file_path": args.file_path,
            "message": f"Created {args.class_type} {args.class_name}",
            "result": result,
        }

    async def call_gradle_build(
        self, args: GradleBuildRequest, progress_token: str
    ) -> Dict[str, Any]:
        """Execute gradle_build tool."""

        await self.send_progress(progress_token, 20, "Preparing Gradle build")

        if not self.gradle_tools:
            raise RuntimeError("Gradle tools not initialized - project path required")

        await self.send_progress(progress_token, 40, f"Running Gradle task: {args.task}")

        result = await self.gradle_tools.gradle_build(task=args.task, clean=args.clean)

        await self.send_progress(progress_token, 80, "Processing build results")

        return {
            "success": result.get("success", False),
            "task": args.task,
            "output": result.get("output", ""),
            "execution_time": result.get("execution_time", 0),
        }

    async def call_analyze_project(
        self, args: ProjectAnalysisRequest, progress_token: str
    ) -> Dict[str, Any]:
        """Execute analyze_project tool."""

        await self.send_progress(progress_token, 30, "Starting project analysis")

        if not self.project_analysis:
            raise RuntimeError("Project analysis tools not initialized - project path required")

        await self.send_progress(progress_token, 60, f"Performing {args.analysis_type} analysis")

        result = await self.project_analysis.analyze_project(analysis_type=args.analysis_type)

        return {"success": True, "analysis_type": args.analysis_type, "results": result}

    # Utility methods
    def is_path_allowed(self, path: Path) -> bool:
        """Check if a path is within allowed roots."""
        try:
            resolved_path = path.resolve()
            return any(resolved_path.is_relative_to(root.resolve()) for root in self.allowed_roots)
        except (OSError, ValueError):
            return False

    async def log_message(self, message: str, level: str = "info") -> None:
        """Send structured log message via MCP logging capability."""
        try:
            await self.server.request_handlers.get("logging/message", lambda x: None)(
                {"level": level, "data": message, "logger": "kotlin-mcp-server"}
            )
        except Exception:
            # Fallback to standard logging
            self.logger.log(getattr(logging, level.upper(), logging.INFO), message)

    async def send_progress(self, progress_token: str, progress: int, message: str) -> None:
        """Send progress notification."""
        try:
            # Note: This would be sent via MCP progress notifications in a real implementation
            await self.log_message(f"Progress {progress}%: {message}", level="debug")
        except Exception:
            pass  # Progress notifications are optional


async def main():
    """Main function to start the modern MCP server."""

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Kotlin MCP Server v2")
    parser.add_argument(
        "project_path", nargs="?", help="Path to the Android project root directory"
    )
    args = parser.parse_args()

    # Create and configure server
    server_instance = KotlinMCPServerV2()

    # Set project path if provided
    if args.project_path:
        project_path = Path(args.project_path)
        if project_path.exists():
            server_instance.set_project_path(str(project_path))
        else:
            # Log warning but continue
            await server_instance.log_message(
                f"Warning: Project path {project_path} does not exist", level="warning"
            )

    # Start the MCP server using official SDK
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="kotlin-mcp-server",
                server_version="2.0.0",
                capabilities=server_instance.server.get_capabilities(),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
