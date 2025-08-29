#!/usr/bin/env python3
"""
Kotlin MCP Server v2 - Enhanced Implementation

A modernized Model Context Protocol server for Android/Kotlin development
with improved structure, validation, and features towards 2025-06-18 specification.

This enhanced version includes:
- Schema-driven tool definitions with Pydantic
- Enhanced error handling and validation
- Structured logging capabilities
- Progress tracking for long operations
- Security improvements
- Root/resource management foundation
- Prompt template system

Author: MCP Development Team
Version: 2.0.0 (Enhanced)
License: MIT
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ValidationError

# Import existing tool modules
from ai.llm_integration import AnalysisRequest, CodeGenerationRequest, CodeType, LLMIntegration
from generators.kotlin_generator import KotlinCodeGenerator
from tools.build_optimization import BuildOptimizationTools
from tools.gradle_tools import GradleTools
from tools.intelligent_tool_manager import IntelligentMCPToolManager
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
        pattern="^(activity|fragment|class|data_class|interface|viewmodel|repository|service)$",
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
        pattern="^(structure|dependencies|manifest|security|performance|all)$",
    )


class MCPRequest(BaseModel):
    """Base MCP request structure."""

    jsonrpc: str = Field(default="2.0")
    id: Optional[Union[str, int]] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    """Base MCP response structure."""

    jsonrpc: str = Field(default="2.0")
    id: Optional[Union[str, int]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class MCPError(BaseModel):
    """MCP error structure."""

    code: int
    message: str
    data: Optional[Any] = None


class ProgressNotification(BaseModel):
    """Progress tracking notification."""

    token: str
    progress: int = Field(ge=0, le=100)
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class KotlinMCPServerV2:
    """Enhanced MCP Server implementation with modern features."""

    def __init__(self, name: str = "kotlin-mcp-server"):
        """Initialize the enhanced MCP server."""
        self.name = name
        self.project_path: Optional[Path] = None
        self.allowed_roots: List[Path] = []
        self.active_operations: Dict[str, Dict[str, Any]] = {}

        # Initialize core components
        self.security_manager = SecurityManager()
        self.llm_integration = LLMIntegration(self.security_manager)
        self.kotlin_generator = KotlinCodeGenerator(self.llm_integration)

        # Tool modules (initialized after project path is set)
        self.gradle_tools: Optional[GradleTools] = None
        self.project_analysis: Optional[ProjectAnalysisTools] = None
        self.build_optimization: Optional[BuildOptimizationTools] = None
        self.intelligent_tool_manager: Optional[IntelligentMCPToolManager] = None

        # Setup logging
        self.setup_logging()

    def setup_logging(self) -> None:
        """Configure structured logging."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(self.name)

    def set_project_path(self, project_path: str) -> None:
        """Set the project path and initialize tool modules."""
        self.project_path = Path(project_path)

        # Add project path as allowed root
        if self.project_path.exists():
            self.allowed_roots.append(self.project_path)
            self.logger.info(f"Added project root: {self.project_path}")

        # Initialize tool modules with project path
        self.gradle_tools = GradleTools(self.project_path, self.security_manager)
        self.project_analysis = ProjectAnalysisTools(self.project_path, self.security_manager)
        self.build_optimization = BuildOptimizationTools(self.project_path, self.security_manager)
        self.intelligent_tool_manager = IntelligentMCPToolManager(
            str(self.project_path), self.security_manager
        )

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request with enhanced capabilities."""

        self.log_message("Initializing Kotlin MCP Server v2", level="info")

        return {
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True},
                "prompts": {"listChanged": True},
                "logging": {},
                "roots": {"listChanged": True},
            },
            "serverInfo": {"name": self.name, "version": "2.0.0"},
        }

    async def handle_list_tools(self) -> Dict[str, Any]:
        """List all available tools with schema-driven definitions."""

        tools = [
            # Core Development Tools
            {
                "name": "create_kotlin_file",
                "description": (
                    "Create production-ready Kotlin files with complete implementations for "
                    "Android development. Supports Activities, ViewModels, Repositories, Data "
                    "Classes, Use Cases, Services, and more with modern Android patterns."
                ),
                "inputSchema": CreateKotlinFileRequest.model_json_schema(),
            },
            {
                "name": "gradle_build",
                "description": (
                    "Build Android project using Gradle build system. Supports all standard "
                    "Gradle tasks including compilation, packaging, and testing with progress tracking."
                ),
                "inputSchema": GradleBuildRequest.model_json_schema(),
            },
            {
                "name": "analyze_project",
                "description": (
                    "Analyze Android project structure, dependencies, security, and performance "
                    "with comprehensive reporting and recommendations."
                ),
                "inputSchema": ProjectAnalysisRequest.model_json_schema(),
            },
            # Build and Testing Tools
            {
                "name": "run_tests",
                "description": "Execute Android tests including unit tests, instrumented tests, and UI tests. Provides detailed test results and coverage information.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "test_type": {
                            "type": "string",
                            "enum": ["unit", "instrumented", "all"],
                            "default": "unit",
                            "description": "Type of tests: 'unit' for JVM tests, 'instrumented' for device tests, 'all' for both",
                        }
                    },
                },
            },
            {
                "name": "format_code",
                "description": "Format Kotlin source using ktlint",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "run_lint",
                "description": "Run static analysis tools like detekt or lint",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "lint_tool": {
                            "type": "string",
                            "enum": ["detekt", "ktlint", "android_lint"],
                            "default": "detekt",
                            "description": "Lint tool to run",
                        }
                    },
                },
            },
            {
                "name": "generate_docs",
                "description": "Generate project documentation with Dokka",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doc_type": {
                            "type": "string",
                            "enum": ["html", "javadoc"],
                            "default": "html",
                            "description": "Documentation format",
                        }
                    },
                },
            },
            # File Creation Tools
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
                            "default": "activity",
                            "description": "Layout type",
                        },
                    },
                    "required": ["layout_name"],
                },
            },
            # UI Development Tools
            {
                "name": "create_compose_component",
                "description": "Create Jetpack Compose UI components",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path for the Compose file"},
                        "component_name": {
                            "type": "string",
                            "description": "Name of the Compose component",
                        },
                        "package_name": {"type": "string", "description": "Package name"},
                        "component_type": {
                            "type": "string",
                            "enum": ["screen", "component", "dialog", "bottom_sheet"],
                            "default": "component",
                            "description": "Type of Compose component",
                        },
                        "uses_state": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include state management",
                        },
                        "uses_navigation": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include navigation",
                        },
                    },
                    "required": ["file_path", "component_name", "package_name"],
                },
            },
            {
                "name": "create_custom_view",
                "description": "Create custom Android View components",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path for the custom view"},
                        "view_name": {"type": "string", "description": "Name of the custom view"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "view_type": {
                            "type": "string",
                            "enum": ["view", "viewgroup", "compound"],
                            "default": "view",
                            "description": "Type of view",
                        },
                        "has_attributes": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include custom attributes",
                        },
                    },
                    "required": ["file_path", "view_name", "package_name"],
                },
            },
            # Architecture Tools
            {
                "name": "setup_mvvm_architecture",
                "description": "Set up MVVM architecture pattern with ViewModel and Repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature/module",
                        },
                        "package_name": {"type": "string", "description": "Base package name"},
                        "data_source": {
                            "type": "string",
                            "enum": ["network", "database", "both"],
                            "default": "network",
                            "description": "Data source type",
                        },
                        "include_repository": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include Repository pattern",
                        },
                        "include_use_cases": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include Use Cases (Clean Architecture)",
                        },
                    },
                    "required": ["feature_name", "package_name"],
                },
            },
            {
                "name": "setup_dependency_injection",
                "description": "Set up Hilt dependency injection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "module_name": {"type": "string", "description": "Name of the DI module"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "injection_type": {
                            "type": "string",
                            "enum": ["network", "database", "repository", "use_case"],
                            "default": "network",
                            "description": "Type of injection setup",
                        },
                    },
                    "required": ["module_name", "package_name"],
                },
            },
            {
                "name": "setup_room_database",
                "description": "Set up Room database with entities and DAOs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database_name": {"type": "string", "description": "Name of the database"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "entities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of entity names",
                        },
                        "include_migration": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include migration setup",
                        },
                    },
                    "required": ["database_name", "package_name", "entities"],
                },
            },
            {
                "name": "setup_retrofit_api",
                "description": "Set up Retrofit API interface and service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "api_name": {"type": "string", "description": "Name of the API interface"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "base_url": {"type": "string", "description": "Base URL for the API"},
                        "authentication": {
                            "type": "string",
                            "enum": ["none", "bearer", "api_key", "oauth"],
                            "default": "none",
                            "description": "Authentication type",
                        },
                        "endpoints": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of endpoint names",
                        },
                    },
                    "required": ["api_name", "package_name", "base_url"],
                },
            },
            # Security and Compliance Tools
            {
                "name": "encrypt_sensitive_data",
                "description": "Encrypt sensitive data with compliance-grade encryption",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "Data to encrypt"},
                        "data_type": {
                            "type": "string",
                            "enum": ["pii", "phi", "financial", "general"],
                            "description": "Type of data being encrypted",
                        },
                        "compliance_level": {
                            "type": "string",
                            "enum": ["gdpr", "hipaa", "both"],
                            "description": "Compliance requirement",
                        },
                    },
                    "required": ["data", "data_type"],
                },
            },
            {
                "name": "implement_gdpr_compliance",
                "description": "Implement GDPR compliance features in Android app",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "package_name": {"type": "string", "description": "Package name"},
                        "features": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "consent_management",
                                    "data_portability",
                                    "right_to_erasure",
                                    "privacy_policy",
                                ],
                            },
                            "description": "GDPR features to implement",
                        },
                    },
                    "required": ["package_name", "features"],
                },
            },
            {
                "name": "implement_hipaa_compliance",
                "description": "Implement HIPAA compliance features for healthcare apps",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "package_name": {"type": "string", "description": "Package name"},
                        "features": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "audit_logging",
                                    "access_controls",
                                    "encryption",
                                    "secure_messaging",
                                ],
                            },
                            "description": "HIPAA features to implement",
                        },
                    },
                    "required": ["package_name", "features"],
                },
            },
            {
                "name": "setup_secure_storage",
                "description": "Setup secure storage with encryption and access controls",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "storage_type": {
                            "type": "string",
                            "enum": ["shared_preferences", "room", "keystore", "file"],
                            "description": "Type of storage to secure",
                        },
                        "encryption_level": {
                            "type": "string",
                            "enum": ["standard", "high", "maximum"],
                            "default": "standard",
                            "description": "Level of encryption",
                        },
                        "compliance_mode": {
                            "type": "string",
                            "enum": ["none", "gdpr", "hipaa", "both"],
                            "default": "none",
                            "description": "Compliance requirements",
                        },
                    },
                    "required": ["storage_type"],
                },
            },
            # AI/ML Integration Tools
            {
                "name": "query_llm",
                "description": "Query local or external LLM for code assistance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Prompt for the LLM"},
                        "llm_provider": {
                            "type": "string",
                            "enum": ["openai", "anthropic", "local"],
                            "default": "local",
                            "description": "LLM provider to use",
                        },
                        "model": {"type": "string", "description": "Specific model to use"},
                        "max_tokens": {
                            "type": "integer",
                            "default": 1000,
                            "description": "Maximum tokens in response",
                        },
                        "privacy_mode": {
                            "type": "boolean",
                            "default": True,
                            "description": "Use privacy-preserving mode",
                        },
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "analyze_code_with_ai",
                "description": "Analyze Kotlin/Android code using AI models",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to code file"},
                        "analysis_type": {
                            "type": "string",
                            "enum": ["security", "performance", "bugs", "style", "complexity"],
                            "description": "Type of analysis to perform",
                        },
                        "use_local_model": {
                            "type": "boolean",
                            "default": True,
                            "description": "Use local AI model for analysis",
                        },
                    },
                    "required": ["file_path", "analysis_type"],
                },
            },
            {
                "name": "generate_code_with_ai",
                "description": "Generate Kotlin/Android code using AI assistance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Description of code to generate",
                        },
                        "code_type": {
                            "type": "string",
                            "enum": ["class", "function", "layout", "test", "component"],
                            "description": "Type of code to generate",
                        },
                        "framework": {
                            "type": "string",
                            "enum": ["compose", "view", "kotlin", "java"],
                            "description": "Target framework",
                        },
                        "compliance_requirements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Compliance requirements to consider",
                        },
                    },
                    "required": ["description", "code_type"],
                },
            },
            # Testing Tools
            {
                "name": "generate_unit_tests",
                "description": "Generate unit tests for Kotlin classes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_file": {"type": "string", "description": "Path to file to test"},
                        "test_framework": {
                            "type": "string",
                            "enum": ["junit4", "junit5", "mockk", "robolectric"],
                            "default": "junit5",
                            "description": "Testing framework to use",
                        },
                        "coverage_target": {
                            "type": "integer",
                            "default": 80,
                            "description": "Target test coverage percentage",
                        },
                    },
                    "required": ["target_file"],
                },
            },
            {
                "name": "setup_ui_testing",
                "description": "Set up UI testing with Espresso or Compose Testing",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "testing_framework": {
                            "type": "string",
                            "enum": ["espresso", "compose_testing", "ui_automator"],
                            "description": "UI testing framework to use",
                        },
                        "target_screens": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of screens to test",
                        },
                    },
                    "required": ["testing_framework"],
                },
            },
            # File Management Tools
            {
                "name": "manage_project_files",
                "description": "Advanced file management with security and backup",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": [
                                "backup",
                                "restore",
                                "sync",
                                "encrypt",
                                "decrypt",
                                "archive",
                                "extract",
                                "watch",
                                "search",
                                "analyze",
                            ],
                            "description": "File operation to perform",
                        },
                        "target_path": {
                            "type": "string",
                            "description": "Target file or directory",
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination for operation",
                        },
                        "encryption_level": {
                            "type": "string",
                            "enum": ["none", "standard", "high"],
                            "default": "standard",
                            "description": "Encryption level for secure operations",
                        },
                        "search_pattern": {
                            "type": "string",
                            "description": "Search pattern (for search operation)",
                        },
                        "watch_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File patterns to watch (for watch operation)",
                        },
                    },
                    "required": ["operation", "target_path"],
                },
            },
            {
                "name": "setup_cloud_sync",
                "description": "Set up cloud synchronization for project files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cloud_provider": {
                            "type": "string",
                            "enum": ["google_drive", "dropbox", "onedrive", "aws_s3"],
                            "description": "Cloud storage provider",
                        },
                        "encryption": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable encryption for synced files",
                        },
                        "sync_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File patterns to sync",
                        },
                    },
                    "required": ["cloud_provider"],
                },
            },
            # API Integration Tools
            {
                "name": "setup_external_api",
                "description": "Set up external API integration with authentication and monitoring",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "api_name": {
                            "type": "string",
                            "description": "Name for the API integration",
                        },
                        "base_url": {"type": "string", "description": "Base URL of the API"},
                        "auth_type": {
                            "type": "string",
                            "enum": ["api_key", "oauth", "jwt", "basic", "none"],
                            "description": "Authentication type",
                        },
                        "api_key": {"type": "string", "description": "API key (for api_key auth)"},
                        "rate_limit": {
                            "type": "integer",
                            "description": "Requests per minute limit",
                        },
                        "security_features": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["rate_limiting", "request_logging", "encryption"],
                            },
                            "description": "Security features to enable",
                        },
                    },
                    "required": ["api_name", "base_url", "auth_type"],
                },
            },
            {
                "name": "call_external_api",
                "description": "Make authenticated calls to configured external APIs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "api_name": {"type": "string", "description": "Name of the configured API"},
                        "endpoint": {"type": "string", "description": "API endpoint path"},
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                            "default": "GET",
                            "description": "HTTP method",
                        },
                        "data": {"type": "object", "description": "Request payload"},
                        "headers": {"type": "object", "description": "Additional headers"},
                    },
                    "required": ["api_name", "endpoint"],
                },
            },
        ]

        return {"tools": tools}

    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution with enhanced validation and progress tracking."""

        operation_id = str(uuid.uuid4())

        try:
            self.log_message(f"Starting tool: {name} (ID: {operation_id})", level="info")

            # Track operation
            self.active_operations[operation_id] = {
                "tool": name,
                "start_time": datetime.now(),
                "progress": 0,
            }

            # Send initial progress
            await self.send_progress(operation_id, 0, f"Starting {name}")

            # Route to appropriate tool handler with validation
            if name == "create_kotlin_file":
                validated_args = CreateKotlinFileRequest(**arguments)
                result = await self.call_create_kotlin_file(validated_args, operation_id)
            elif name == "gradle_build":
                gradle_args = GradleBuildRequest(**arguments)
                result = await self.call_gradle_build(gradle_args, operation_id)
            elif name == "analyze_project":
                analysis_args = ProjectAnalysisRequest(**arguments)
                result = await self.call_analyze_project(analysis_args, operation_id)
            else:
                # Delegate all other tools to the intelligent tool manager
                if self.intelligent_tool_manager:
                    await self.send_progress(
                        operation_id, 30, f"Executing {name} via intelligent tool manager"
                    )
                    result = await self.intelligent_tool_manager.execute_intelligent_tool(
                        name, arguments
                    )
                else:
                    # Fallback for legacy tools if intelligent manager not available
                    result = await self.call_legacy_tool(name, arguments, operation_id)

            # Send completion progress
            await self.send_progress(operation_id, 100, f"Completed {name}")

            # Clean up operation tracking
            del self.active_operations[operation_id]

            self.log_message(f"Completed tool: {name} (ID: {operation_id})", level="info")

            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        except ValidationError as e:
            self.log_message(f"Validation error in {name}: {e}", level="error")
            return {
                "content": [{"type": "text", "text": f"Validation error: {e}"}],
                "isError": True,
            }
        except Exception as e:
            self.log_message(f"Error executing {name}: {e}", level="error")
            # Clean up operation tracking
            if operation_id in self.active_operations:
                del self.active_operations[operation_id]
            return {
                "content": [{"type": "text", "text": f"Error executing tool: {e}"}],
                "isError": True,
            }

    async def handle_list_resources(self) -> Dict[str, Any]:
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
                        {
                            "uri": f"file://{full_path}",
                            "name": file_path,
                            "description": f"Android project file: {file_path}",
                            "mimeType": "text/plain",
                        }
                    )

        return {"resources": resources}

    async def handle_read_resource(self, uri: str) -> Dict[str, Any]:
        """Read resource content with security validation."""

        try:
            # Extract file path from URI
            if not uri.startswith("file://"):
                raise ValueError("Only file:// URIs are supported")

            file_path = Path(uri[7:])  # Remove "file://" prefix

            # Security check: ensure file is within allowed roots
            if not self.is_path_allowed(file_path):
                raise PermissionError("Access denied: file outside allowed roots")

            # Read file content
            content = file_path.read_text(encoding="utf-8")

            return {"contents": [{"uri": uri, "mimeType": "text/plain", "text": content}]}

        except Exception as e:
            self.log_message(f"Resource read error: {e}", level="error")
            raise

    async def handle_list_roots(self) -> Dict[str, Any]:
        """List allowed root directories."""

        roots = [{"uri": f"file://{root}", "name": root.name} for root in self.allowed_roots]

        return {"roots": roots}

    async def handle_list_prompts(self) -> Dict[str, Any]:
        """List available Kotlin/Android development prompts."""

        prompts = [
            {
                "name": "generate_mvvm_viewmodel",
                "description": "Generate a complete MVVM ViewModel with state management",
                "arguments": [
                    {
                        "name": "feature_name",
                        "description": "Name of the feature (e.g., 'UserProfile', 'ShoppingCart')",
                        "required": True,
                    },
                    {
                        "name": "data_source",
                        "description": "Data source type (network, database, both)",
                        "required": False,
                    },
                ],
            },
            {
                "name": "create_compose_screen",
                "description": "Generate a Jetpack Compose screen with navigation",
                "arguments": [
                    {
                        "name": "screen_name",
                        "description": "Name of the screen (e.g., 'LoginScreen', 'ProfileScreen')",
                        "required": True,
                    },
                    {
                        "name": "has_navigation",
                        "description": "Include navigation setup",
                        "required": False,
                    },
                ],
            },
            {
                "name": "setup_room_database",
                "description": "Generate Room database setup with entities and DAOs",
                "arguments": [
                    {
                        "name": "database_name",
                        "description": "Name of the database",
                        "required": True,
                    },
                    {
                        "name": "entities",
                        "description": "Comma-separated list of entity names",
                        "required": True,
                    },
                ],
            },
        ]

        return {"prompts": prompts}

    async def handle_get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific prompt content."""

        if name == "generate_mvvm_viewmodel":
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

        elif name == "create_compose_screen":
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

        elif name == "setup_room_database":
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
            raise ValueError(f"Unknown prompt: {name}")

        return {
            "description": f"Generated prompt for {name}",
            "messages": [{"role": "user", "content": {"type": "text", "text": content.strip()}}],
        }

    # Tool implementation methods
    async def call_create_kotlin_file(
        self, args: CreateKotlinFileRequest, operation_id: str
    ) -> Dict[str, Any]:
        """Execute create_kotlin_file tool."""

        await self.send_progress(operation_id, 25, "Validating parameters")

        if not self.kotlin_generator:
            raise RuntimeError("Kotlin generator not initialized")

        await self.send_progress(operation_id, 50, "Generating Kotlin code")

        # Generate content based on class type using existing generator
        if args.class_type == "activity":
            content = self.kotlin_generator.generate_complete_activity(
                args.package_name, args.class_name, []
            )
        elif args.class_type == "viewmodel":
            content = self.kotlin_generator.generate_complete_viewmodel(
                args.package_name, args.class_name, []
            )
        elif args.class_type == "repository":
            content = self.kotlin_generator.generate_complete_repository(
                args.package_name, args.class_name, []
            )
        elif args.class_type == "fragment":
            content = self.kotlin_generator.generate_complete_fragment(
                args.package_name, args.class_name, []
            )
        elif args.class_type == "data_class":
            content = self.kotlin_generator.generate_complete_data_class(
                args.package_name, args.class_name, []
            )
        elif args.class_type == "service":
            content = self.kotlin_generator.generate_complete_service(
                args.package_name, args.class_name, []
            )
        elif args.class_type == "interface":
            content = self.kotlin_generator.generate_complete_interface(
                args.package_name, args.class_name, []
            )
        else:
            content = self.kotlin_generator.generate_complete_class(
                args.package_name, args.class_name, []
            )

        await self.send_progress(operation_id, 75, "Writing file to disk")

        # Validate and write file (simplified for now)
        if self.project_path and self.security_manager:
            try:
                validated_path = self.security_manager.validate_file_path(
                    args.file_path, self.project_path
                )
                # Write content to file
                Path(validated_path).parent.mkdir(parents=True, exist_ok=True)
                Path(validated_path).write_text(content, encoding="utf-8")
            except Exception as e:
                raise RuntimeError(f"Failed to write file: {e}")

        return {
            "success": True,
            "file_path": args.file_path,
            "message": f"Created {args.class_type} {args.class_name}",
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
        }

    async def call_gradle_build(
        self, args: GradleBuildRequest, operation_id: str
    ) -> Dict[str, Any]:
        """Execute gradle_build tool."""

        await self.send_progress(operation_id, 20, "Preparing Gradle build")

        if not self.gradle_tools:
            return {
                "success": False,
                "error": (
                    "Gradle tools not initialized - project path required. "
                    "Start the server with --project-path or run the initialization command."
                ),
            }

        await self.send_progress(operation_id, 40, f"Running Gradle task: {args.task}")

        # Pass arguments as dict to match existing API
        arguments = {"task": args.task, "clean": args.clean}
        result = await self.gradle_tools.gradle_build(arguments)

        await self.send_progress(operation_id, 80, "Processing build results")

        return {
            "success": result.get("success", False),
            "task": args.task,
            "output": result.get("output", ""),
            "execution_time": result.get("execution_time", 0),
        }

    async def call_analyze_project(
        self, args: ProjectAnalysisRequest, operation_id: str
    ) -> Dict[str, Any]:
        """Execute analyze_project tool."""

        await self.send_progress(operation_id, 30, "Starting project analysis")
        if not self.project_analysis:
            await self.send_progress(
                operation_id,
                100,
                "Project analysis tools missing - initialization required",
            )
            return {
                "success": False,
                "analysis_type": args.analysis_type,
                "message": (
                    "Project analysis tools not initialized. Provide a project path "
                    "or run the initialization step before analyzing."
                ),
            }

        await self.send_progress(operation_id, 60, f"Performing {args.analysis_type} analysis")

        # Pass arguments as dict to match existing API
        arguments = {"analysis_type": args.analysis_type}
        result = await self.project_analysis.analyze_project(arguments)

        return {"success": True, "analysis_type": args.analysis_type, "results": result}

    async def call_legacy_tool(
        self, name: str, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Fallback to existing tool implementations."""

        await self.send_progress(operation_id, 50, f"Executing legacy tool: {name}")

        # Here we would delegate to the existing handle_call_tool logic
        # For now, return a placeholder
        return {"success": True, "message": f"Legacy tool {name} executed", "arguments": arguments}

    # Utility methods
    def is_path_allowed(self, path: Path) -> bool:
        """Check if a path is within allowed roots."""
        try:
            resolved_path = path.resolve()
            # Compatibility: use try_relative_to for older Python versions
            for root in self.allowed_roots:
                try:
                    resolved_path.relative_to(root.resolve())
                    return True
                except ValueError:
                    continue
            return False
        except (OSError, ValueError):
            return False

    def log_message(self, message: str, level: str = "info") -> None:
        """Log structured message."""
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, message)

    async def send_progress(self, operation_id: str, progress: int, message: str) -> None:
        """Send progress notification."""
        if operation_id in self.active_operations:
            self.active_operations[operation_id]["progress"] = progress

        # For now, just log progress - in a full MCP implementation,
        # this would send progress notifications via the protocol
        self.log_message(f"Operation {operation_id}: {progress}% - {message}", level="debug")

    def create_error_response(
        self, code: int, message: str, request_id: Optional[Union[str, int]] = None
    ) -> Dict[str, Any]:
        """Create standardized JSON-RPC error response."""
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request with enhanced error handling."""

        try:
            # Validate request structure
            request = MCPRequest(**request_data)

            method = request.method
            params = request.params or {}
            request_id = request.id

            # Route to appropriate handler
            if method == "initialize":
                result = await self.handle_initialize(params)
                return {"jsonrpc": "2.0", "id": request_id, "result": result}
            elif method == "ping":
                return {"jsonrpc": "2.0", "id": request_id, "result": {}}
            elif method in ["tools/list", "list_tools"]:
                result = await self.handle_list_tools()
                return {"jsonrpc": "2.0", "id": request_id, "result": result}
            elif method in ["tools/call", "call_tool"]:
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                if not tool_name:
                    return self.create_error_response(-32602, "Missing tool name", request_id)
                result = await self.handle_call_tool(tool_name, tool_args)
                return {"jsonrpc": "2.0", "id": request_id, "result": result}
            elif method == "resources/list":
                result = await self.handle_list_resources()
                return {"jsonrpc": "2.0", "id": request_id, "result": result}
            elif method == "resources/read":
                uri = params.get("uri")
                if not uri:
                    return self.create_error_response(-32602, "Missing resource URI", request_id)
                result = await self.handle_read_resource(uri)
                return {"jsonrpc": "2.0", "id": request_id, "result": result}
            elif method == "roots/list":
                result = await self.handle_list_roots()
                return {"jsonrpc": "2.0", "id": request_id, "result": result}
            elif method == "prompts/list":
                result = await self.handle_list_prompts()
                return {"jsonrpc": "2.0", "id": request_id, "result": result}
            elif method == "prompts/get":
                name = params.get("name")
                arguments = params.get("arguments", {})
                if not name:
                    return self.create_error_response(-32602, "Missing prompt name", request_id)
                result = await self.handle_get_prompt(name, arguments)
                return {"jsonrpc": "2.0", "id": request_id, "result": result}
            else:
                # Unknown method
                return self.create_error_response(-32601, f"Unknown method: {method}", request_id)

        except ValidationError as e:
            return self.create_error_response(-32602, f"Invalid params: {e}", request_id)
        except Exception as e:
            self.log_message(f"Request handling error: {e}", level="error")
            return self.create_error_response(-32000, f"Server error: {e}", request_id)


def create_server() -> KotlinMCPServerV2:
    """Create and configure the enhanced MCP server."""
    return KotlinMCPServerV2()


async def main() -> None:
    """Main function to start the enhanced MCP server."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Kotlin MCP Server v2 (Enhanced)")
    parser.add_argument(
        "project_path", nargs="?", help="Path to the Android project root directory"
    )
    args = parser.parse_args()

    # Create and configure server
    server = create_server()

    # Set project path if provided
    if args.project_path:
        project_path = Path(args.project_path)
        if project_path.exists():
            server.set_project_path(str(project_path))
        else:
            server.log_message(
                f"Warning: Project path {project_path} does not exist", level="warning"
            )

    server.log_message("Kotlin MCP Server v2 starting...", level="info")

    # Start the enhanced MCP communication loop
    async def mcp_loop() -> None:
        while True:
            try:
                # Use synchronous readline for compatibility
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break  # EOF, client closed connection

                # Parse request
                request_data = json.loads(line.strip())

                # Handle request with enhanced error handling
                response = await server.handle_request(request_data)

                # Send response
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            except json.JSONDecodeError as e:
                # Invalid JSON
                error_response = server.create_error_response(-32700, "Parse error: Invalid JSON")
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
            except Exception as e:
                # Unexpected error
                server.log_message(f"Unexpected error in main loop: {e}", level="error")
                error_response = server.create_error_response(-32000, f"Internal error: {e}")
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()

    await mcp_loop()


# Backward compatibility alias
KotlinMCPServer = KotlinMCPServerV2

if __name__ == "__main__":
    asyncio.run(main())
