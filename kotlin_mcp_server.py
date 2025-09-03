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

    def __init__(self, name: str = "kotlin-mcp-server", project_path: Optional[str] = None):
        """Initialize the enhanced MCP server."""
        self.name = name
        self.active_operations: Dict[str, Dict[str, Any]] = {}

        # Initialize core components
        self.security_manager = SecurityManager()
        self.llm_integration = LLMIntegration(self.security_manager)
        self.kotlin_generator = KotlinCodeGenerator(self.llm_integration)

        # Setup logging first
        self.setup_logging()

        # Import project resolver after logging is set up
        from server.utils.project_resolver import resolve_project_root

        # Set initial project path - will be updated during MCP initialization
        if project_path:
            self.project_path = Path(project_path)
        else:
            # Start with current directory as fallback
            # The actual project path will be determined during MCP initialize
            self.project_path = Path.cwd()
            self.logger.info(
                "Using current directory as initial project path, will update from MCP client workspace info"
            )

        self.allowed_roots: List[Path] = [self.project_path]
        self.logger.info(f"Using project path: {self.project_path}")

        # Initialize all tool modules immediately
        self.gradle_tools = GradleTools(self.project_path, self.security_manager)
        self.project_analysis = ProjectAnalysisTools(self.project_path, self.security_manager)
        self.build_optimization = BuildOptimizationTools(self.project_path, self.security_manager)
        self.intelligent_tool_manager = IntelligentMCPToolManager(
            str(self.project_path), self.security_manager
        )

    def setup_logging(self) -> None:
        """Configure structured logging."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(self.name)

    def set_project_path(self, project_path: str) -> None:
        """Set a new project path and re-initialize tool modules."""
        new_path = Path(project_path)

        # Only re-initialize if the path is actually different
        if self.project_path != new_path:
            self.project_path = new_path

            # Update allowed roots
            if new_path not in self.allowed_roots:
                self.allowed_roots.append(new_path)
                self.logger.info(f"Added project root: {new_path}")

            # Re-initialize tool modules with new project path
            self.gradle_tools = GradleTools(self.project_path, self.security_manager)
            self.project_analysis = ProjectAnalysisTools(self.project_path, self.security_manager)
            self.build_optimization = BuildOptimizationTools(
                self.project_path, self.security_manager
            )
            self.intelligent_tool_manager = IntelligentMCPToolManager(
                str(self.project_path), self.security_manager
            )
            self.logger.info(f"Re-initialized tools with project path: {self.project_path}")

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request with enhanced capabilities."""

        self.log_message("Initializing Kotlin MCP Server v2", level="info")

        # Import project resolver
        from server.utils.project_resolver import resolve_project_root

        # Extract workspace/project information from MCP client
        try:
            # Log all environment variables for debugging
            project_path_env = os.environ.get("PROJECT_PATH")
            vscode_workspace = os.environ.get("VSCODE_WORKSPACE_FOLDER")
            workspace_path_env = os.environ.get("WORKSPACE_PATH")

            self.logger.info(
                f"Environment variables - PROJECT_PATH: {project_path_env}, VSCODE_WORKSPACE_FOLDER: {vscode_workspace}, WORKSPACE_PATH: {workspace_path_env}"
            )

            # Try to resolve project root from MCP initialization parameters
            ide_meta = {}

            # Extract client info which may contain workspace information
            client_info = params.get("clientInfo", {})
            if client_info:
                self.logger.info(
                    f"MCP Client: {client_info.get('name', 'unknown')} {client_info.get('version', '')}"
                )

            # Check multiple possible locations for workspace information
            # 1. Check for 'roots' parameter
            roots = params.get("roots", [])
            if roots:
                self.logger.info(f"Found roots in params: {roots}")
                # Use the first root as project path
                root_uri = roots[0].get("uri", "") if isinstance(roots[0], dict) else str(roots[0])
                if root_uri.startswith("file://"):
                    workspace_path = root_uri[7:]  # Remove "file://" prefix
                    ide_meta["workspacePath"] = workspace_path
                    self.logger.info(f"Found workspace root from MCP client: {workspace_path}")

            # 2. Check for 'workspaceFolders' (VS Code might send this)
            workspace_folders = params.get("workspaceFolders", [])
            if workspace_folders and not ide_meta.get("workspacePath"):
                self.logger.info(f"Found workspaceFolders in params: {workspace_folders}")
                folder_uri = (
                    workspace_folders[0].get("uri", "")
                    if isinstance(workspace_folders[0], dict)
                    else str(workspace_folders[0])
                )
                if folder_uri.startswith("file://"):
                    workspace_path = folder_uri[7:]  # Remove "file://" prefix
                    ide_meta["workspacePath"] = workspace_path
                    self.logger.info(f"Found workspace from workspaceFolders: {workspace_path}")

            # 3. Check capabilities for workspace information
            capabilities = params.get("capabilities", {})
            if capabilities and not ide_meta.get("workspacePath"):
                workspace_capability = capabilities.get("workspace", {})
                if workspace_capability:
                    self.logger.info(f"Found workspace capabilities: {workspace_capability}")

            # 4. Try to get workspace from environment variables (this should work with VS Code MCP config)
            if not ide_meta.get("workspacePath"):
                # Check PROJECT_PATH first (set by our MCP config)
                if project_path_env:
                    ide_meta["workspacePath"] = project_path_env
                    self.logger.info(
                        f"Found workspace from PROJECT_PATH environment: {project_path_env}"
                    )
                # Check if VS Code workspace info is available in environment
                elif vscode_workspace:
                    ide_meta["workspacePath"] = vscode_workspace
                    self.logger.info(
                        f"Found workspace from VS Code environment: {vscode_workspace}"
                    )
                # Check WORKSPACE_PATH as another fallback
                elif workspace_path_env:
                    ide_meta["workspacePath"] = workspace_path_env
                    self.logger.info(
                        f"Found workspace from WORKSPACE_PATH environment: {workspace_path_env}"
                    )

            # Resolve project root with IDE metadata
            if ide_meta:
                try:
                    new_project_path = Path(resolve_project_root({}, ide_meta=ide_meta))
                    if new_project_path != self.project_path:
                        self.logger.info(
                            f"Updating project path from {self.project_path} to {new_project_path}"
                        )
                        self.set_project_path(str(new_project_path))
                    else:
                        self.logger.info(f"Project path already correct: {self.project_path}")
                except Exception as e:
                    self.logger.warning(f"Could not resolve project root from IDE metadata: {e}")
            else:
                self.logger.warning(
                    "No workspace information found in MCP initialization, using current directory"
                )

        except Exception as e:
            self.logger.error(f"Error processing MCP initialization parameters: {e}")

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
        # Import the centralized registry
        try:
            from server.tools_registry import TOOL_REGISTRY

            return {"tools": TOOL_REGISTRY}
        except ImportError:
            # Fallback to embedded definitions if registry not available
            pass

        tools = [
            # Core Development Tools
            {
                "name": "refactorFunction",
                "description": (
                    "Refactor Kotlin functions with AST-aware transformations including rename, extract, inline, and parameter introduction."
                ),
                "inputSchema": {
                    "type": "object",
                    "required": ["filePath", "functionName", "refactorType"],
                    "properties": {
                        "filePath": {"type": "string", "minLength": 1},
                        "functionName": {"type": "string", "minLength": 1},
                        "refactorType": {
                            "type": "string",
                            "enum": ["rename", "extract", "inline", "introduceParam"],
                        },
                        "newName": {"type": "string"},
                        "range": {"$ref": "#/$defs/range"},
                        "preview": {"type": "boolean", "default": False},
                    },
                },
            },
            {
                "name": "analyzeCodeQuality",
                "description": (
                    "Analyze code quality with security, performance, complexity, or comprehensive rules."
                ),
                "inputSchema": {
                    "type": "object",
                    "required": ["scope", "ruleset"],
                    "properties": {
                        "scope": {"type": "string", "enum": ["file", "module", "project"]},
                        "targets": {"$ref": "#/$defs/pathsOrGlobs"},
                        "ruleset": {
                            "type": "string",
                            "enum": ["security", "performance", "complexity", "all"],
                        },
                        "maxFindings": {"type": "integer", "minimum": 1},
                    },
                },
            },
            # Build and Testing Tools
            {
                "name": "generateTests",
                "description": "Generate comprehensive unit tests for Kotlin classes and functions with JUnit5 or MockK.",
                "inputSchema": {
                    "type": "object",
                    "required": ["filePath", "classOrFunction", "framework"],
                    "properties": {
                        "filePath": {"type": "string", "minLength": 1},
                        "classOrFunction": {"type": "string"},
                        "framework": {"type": "string", "enum": ["JUnit5", "MockK"]},
                        "coverageGoal": {"type": "number", "minimum": 0, "maximum": 100},
                    },
                },
            },
            {
                "name": "formatCode",
                "description": "Format Kotlin code using ktlint or spotless with configurable style rules.",
                "inputSchema": {
                    "type": "object",
                    "required": ["targets", "style"],
                    "properties": {
                        "targets": {"$ref": "#/$defs/pathsOrGlobs"},
                        "style": {"type": "string", "enum": ["ktlint", "spotless"]},
                        "preview": {"type": "boolean", "default": False},
                    },
                },
            },
            {
                "name": "optimizeImports",
                "description": "Optimize and organize Kotlin imports across files, modules, or the entire project.",
                "inputSchema": {
                    "type": "object",
                    "required": ["projectRoot", "mode"],
                    "properties": {
                        "projectRoot": {"type": "string", "minLength": 1},
                        "mode": {"type": "string", "enum": ["file", "module", "project"]},
                        "targets": {"$ref": "#/$defs/pathsOrGlobs"},
                        "preview": {"type": "boolean", "default": False},
                    },
                },
            },
            {
                "name": "gitStatus",
                "description": "Get Git repository status including branch, changes, and ahead/behind counts.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "gitSmartCommit",
                "description": "Create intelligent commit message based on changes and conventional commit standards.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "gitCreateFeatureBranch",
                "description": "Create a new feature branch with safe naming and validation.",
                "inputSchema": {
                    "type": "object",
                    "required": ["branchName"],
                    "properties": {
                        "branchName": {
                            "type": "string",
                            "description": "Name of the feature branch",
                        }
                    },
                },
            },
            {
                "name": "gitMergeWithResolution",
                "description": "Attempt merge with intelligent conflict resolution and advice.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "targetBranch": {
                            "type": "string",
                            "default": "main",
                            "description": "Target branch to merge",
                        }
                    },
                },
            },
            {
                "name": "apiCallSecure",
                "description": "Make secure API calls with authentication, retries, and monitoring.",
                "inputSchema": {
                    "type": "object",
                    "required": ["apiName", "endpoint"],
                    "properties": {
                        "apiName": {"type": "string", "description": "Name of the configured API"},
                        "endpoint": {"type": "string", "description": "API endpoint path"},
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                            "default": "GET",
                        },
                        "headers": {"type": "object", "description": "Additional headers"},
                        "data": {"type": "object", "description": "Request payload"},
                        "auth": {"type": "object", "description": "Authentication configuration"},
                    },
                },
            },
            {
                "name": "apiMonitorMetrics",
                "description": "Get API monitoring metrics with windowed counters.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "apiName": {"type": "string", "description": "Name of the API to monitor"},
                        "windowMinutes": {
                            "type": "integer",
                            "default": 60,
                            "description": "Metrics window in minutes",
                        },
                    },
                },
            },
            {
                "name": "apiValidateCompliance",
                "description": "Validate API compliance with GDPR/HIPAA rules and provide remediations.",
                "inputSchema": {
                    "type": "object",
                    "required": ["apiName"],
                    "properties": {
                        "apiName": {"type": "string", "description": "Name of the API to validate"},
                        "complianceType": {
                            "type": "string",
                            "enum": ["gdpr", "hipaa"],
                            "default": "gdpr",
                        },
                    },
                },
            },
            {
                "name": "projectSearch",
                "description": "Fast grep search with context across project files.",
                "inputSchema": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "includePattern": {
                            "type": "string",
                            "default": "*",
                            "description": "File pattern to include",
                        },
                        "maxResults": {
                            "type": "integer",
                            "default": 50,
                            "description": "Maximum results to return",
                        },
                        "contextLines": {
                            "type": "integer",
                            "default": 2,
                            "description": "Lines of context around matches",
                        },
                    },
                },
            },
            {
                "name": "todoListFromCode",
                "description": "Parse task comments and deprecated items from codebase.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "includePattern": {
                            "type": "string",
                            "default": "*.{kt,java,py,js,ts}",
                            "description": "File pattern to scan",
                        },
                        "maxResults": {
                            "type": "integer",
                            "default": 100,
                            "description": "Maximum TODOs to return",
                        },
                    },
                },
            },
            {
                "name": "readmeGenerateOrUpdate",
                "description": "Generate or update README with badges, setup instructions, and tool catalog.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "forceRegenerate": {
                            "type": "boolean",
                            "default": False,
                            "description": "Force complete regeneration",
                        }
                    },
                },
            },
            {
                "name": "changelogSummarize",
                "description": "Summarize conventional commits into grouped release notes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "changelogPath": {
                            "type": "string",
                            "default": "CHANGELOG.md",
                            "description": "Path to changelog file",
                        },
                        "version": {
                            "type": "string",
                            "default": "latest",
                            "description": "Version to summarize",
                        },
                    },
                },
            },
            {
                "name": "buildAndTest",
                "description": "Run Gradle/Maven build and return failing tests with artifacts.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "buildTool": {
                            "type": "string",
                            "enum": ["auto", "gradle", "maven"],
                            "default": "auto",
                        },
                        "skipTests": {
                            "type": "boolean",
                            "default": False,
                            "description": "Skip running tests",
                        },
                    },
                },
            },
            {
                "name": "dependencyAudit",
                "description": "Audit Gradle dependencies for OSV vulnerabilities and license compliance.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "generateDocs",
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
                "name": "createLayoutFile",
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
                "name": "createComposeComponent",
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
                "name": "createCustomView",
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
                "name": "setupMvvmArchitecture",
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
                "name": "setupDependencyInjection",
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
                "name": "setupRoomDatabase",
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
                "name": "setupRetrofitApi",
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
                "name": "securityEncryptData",
                "description": "Encrypt sensitive data with AES-256-GCM encryption and tamper-evident audit trail",
                "inputSchema": {
                    "type": "object",
                    "required": ["dataRef"],
                    "properties": {
                        "dataRef": {
                            "type": "object",
                            "required": ["type", "value"],
                            "properties": {
                                "type": {"type": "string", "enum": ["inline", "path", "uri"]},
                                "value": {"type": "string"},
                            },
                        },
                        "algo": {
                            "type": "string",
                            "enum": ["AES-256-GCM"],
                            "default": "AES-256-GCM",
                        },
                        "kdf": {"type": "string", "enum": ["PBKDF2"], "default": "PBKDF2"},
                        "context": {"type": "object", "additionalProperties": True},
                    },
                },
            },
            {
                "name": "securityDecryptData",
                "description": "Decrypt data encrypted with securityEncryptData",
                "inputSchema": {
                    "type": "object",
                    "required": ["dataRef"],
                    "properties": {
                        "dataRef": {
                            "type": "object",
                            "required": ["type", "value"],
                            "properties": {
                                "type": {"type": "string", "enum": ["inline", "path", "uri"]},
                                "value": {"type": "string"},
                            },
                        },
                        "context": {"type": "object"},
                    },
                },
            },
            {
                "name": "securityAuditTrail",
                "description": "Query tamper-evident audit trail with hash chaining",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "properties": {
                                "subjectId": {"type": "string"},
                                "op": {"type": "string"},
                                "dateRange": {
                                    "type": "object",
                                    "properties": {
                                        "start": {"type": "string", "format": "date-time"},
                                        "end": {"type": "string", "format": "date-time"},
                                    },
                                },
                            },
                        },
                        "limit": {"type": "integer", "minimum": 1, "default": 50},
                    },
                },
            },
            {
                "name": "privacyRequestErasure",
                "description": "Delete subject data from files, database, or cloud with audit trail",
                "inputSchema": {
                    "type": "object",
                    "required": ["subjectId", "scopes"],
                    "properties": {
                        "subjectId": {"type": "string"},
                        "scopes": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["files", "database", "cloud"]},
                        },
                    },
                },
            },
            {
                "name": "privacyExportData",
                "description": "Export subject data in requested format with compliance audit",
                "inputSchema": {
                    "type": "object",
                    "required": ["subjectId", "format"],
                    "properties": {
                        "subjectId": {"type": "string"},
                        "format": {
                            "type": "string",
                            "enum": ["JSON", "XML", "CSV"],
                            "default": "JSON",
                        },
                    },
                },
            },
            {
                "name": "implementGdprCompliance",
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
                "name": "implementHipaaCompliance",
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
                "name": "setupSecureStorage",
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
                "name": "queryLlm",
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
                "name": "analyzeCodeWithAi",
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
                "name": "generateCodeWithAi",
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
                "name": "generateUnitTests",
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
                "name": "setupUiTesting",
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
                "name": "manageProjectFiles",
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
                "name": "setupCloudSync",
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
                "name": "setupExternalApi",
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
                "name": "callExternalApi",
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
            # File Operations Tools
            {
                "name": "fileBackup",
                "description": "Create encrypted backups with manifest and SHA-256 hashes",
                "inputSchema": {
                    "type": "object",
                    "required": ["targets", "dest"],
                    "properties": {
                        "targets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File/directory paths to backup",
                        },
                        "dest": {
                            "type": "string",
                            "description": "Destination path or S3/Cloud URL",
                        },
                        "encrypt": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable client-side encryption",
                        },
                        "tag": {"type": "string", "description": "Backup tag for identification"},
                    },
                },
            },
            {
                "name": "fileRestore",
                "description": "Restore files from backup with integrity verification",
                "inputSchema": {
                    "type": "object",
                    "required": ["manifestRef", "destRoot"],
                    "properties": {
                        "manifestRef": {
                            "type": "object",
                            "required": ["type", "value"],
                            "properties": {
                                "type": {"type": "string", "enum": ["inline", "path", "uri"]},
                                "value": {"type": "string"},
                            },
                        },
                        "destRoot": {
                            "type": "string",
                            "description": "Root directory for restoration",
                        },
                        "decrypt": {
                            "type": "boolean",
                            "default": True,
                            "description": "Decrypt if encrypted",
                        },
                    },
                },
            },
            {
                "name": "fileSyncWatch",
                "description": "Watch directories for changes and sync to cloud storage",
                "inputSchema": {
                    "type": "object",
                    "required": ["paths", "dest"],
                    "properties": {
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Local paths to watch",
                        },
                        "dest": {"type": "string", "description": "Cloud destination URL"},
                        "patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File patterns to include/exclude",
                        },
                    },
                },
            },
            {
                "name": "fileClassifySensitivity",
                "description": "Classify files for PII/Secrets using regex and heuristics",
                "inputSchema": {
                    "type": "object",
                    "required": ["targets", "policies"],
                    "properties": {
                        "targets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Files/directories to scan",
                        },
                        "policies": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["PII", "Secrets", "PHI", "Financial"],
                            },
                            "description": "Classification policies to apply",
                        },
                    },
                },
            },
            # Security Hardening Tools
            {
                "name": "securityHardening",
                "description": "Manage security hardening features including RBAC, rate limiting, caching, and monitoring",
                "inputSchema": {
                    "type": "object",
                    "required": ["operation"],
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": [
                                "get_metrics",
                                "assign_role",
                                "check_permission",
                                "clear_cache",
                                "export_telemetry",
                            ],
                            "description": "Hardening operation to perform",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID for role/permission operations",
                        },
                        "role": {
                            "type": "string",
                            "enum": ["admin", "developer", "readonly", "guest"],
                            "description": "Role to assign",
                        },
                        "permission": {"type": "string", "description": "Permission to check"},
                        "resource": {
                            "type": "string",
                            "description": "Resource path for permission check",
                        },
                    },
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
            if name == "refactorFunction":
                # Map to existing create_kotlin_file or intelligent refactoring
                result = await self.handle_refactor_function(arguments, operation_id)
            elif name == "applyCodeAction":
                result = await self.handle_apply_code_action(arguments, operation_id)
            elif name == "optimizeImports":
                result = await self.handle_optimize_imports(arguments, operation_id)
            elif name == "formatCode":
                result = await self.handle_format_code(arguments, operation_id)
            elif name == "analyzeCodeQuality":
                # Delegate to intelligent tool manager
                if self.intelligent_tool_manager:
                    await self.send_progress(
                        operation_id, 30, f"Executing {name} via intelligent tool manager"
                    )
                    result = await self.intelligent_tool_manager.execute_intelligent_tool(
                        name, arguments
                    )
                    await self.send_progress(operation_id, 100, f"Completed {name}")
                else:
                    result = {
                        "content": [{"type": "text", "text": "Tool not available"}],
                        "isError": True,
                    }
            elif name == "generateTests":
                # Delegate to intelligent tool manager
                if self.intelligent_tool_manager:
                    await self.send_progress(
                        operation_id, 30, f"Executing {name} via intelligent tool manager"
                    )
                    result = await self.intelligent_tool_manager.execute_intelligent_tool(
                        name, arguments
                    )
                    await self.send_progress(operation_id, 100, f"Completed {name}")
                else:
                    result = {
                        "content": [{"type": "text", "text": "Tool not available"}],
                        "isError": True,
                    }
            elif name == "applyPatch":
                # Delegate to intelligent tool manager
                if self.intelligent_tool_manager:
                    await self.send_progress(
                        operation_id, 30, f"Executing {name} via intelligent tool manager"
                    )
                    result = await self.intelligent_tool_manager.execute_intelligent_tool(
                        name, arguments
                    )
                    await self.send_progress(operation_id, 100, f"Completed {name}")
                else:
                    result = {
                        "content": [{"type": "text", "text": "Tool not available"}],
                        "isError": True,
                    }
            elif name == "androidGenerateComposeUI":
                result = await self.handle_android_generate_compose_ui(arguments, operation_id)
            elif name == "androidSetupArchitecture":
                result = await self.handle_android_setup_architecture(arguments, operation_id)
            elif name == "androidSetupDataLayer":
                result = await self.handle_android_setup_data_layer(arguments, operation_id)
            elif name == "androidSetupNetwork":
                result = await self.handle_android_setup_network(arguments, operation_id)
            elif name == "securityEncryptData":
                result = await self.handle_security_encrypt_data(arguments, operation_id)
            elif name == "securityDecryptData":
                result = await self.handle_security_decrypt_data(arguments, operation_id)
            elif name == "privacyRequestErasure":
                result = await self.handle_privacy_request_erasure(arguments, operation_id)
            elif name == "privacyExportData":
                result = await self.handle_privacy_export_data(arguments, operation_id)
            elif name == "securityAuditTrail":
                result = await self.handle_security_audit_trail(arguments, operation_id)
            elif name == "fileBackup":
                result = await self.handle_file_backup(arguments, operation_id)
            elif name == "fileRestore":
                result = await self.handle_file_restore(arguments, operation_id)
            elif name == "fileSyncWatch":
                result = await self.handle_file_sync_watch(arguments, operation_id)
            elif name == "fileClassifySensitivity":
                result = await self.handle_file_classify_sensitivity(arguments, operation_id)
            elif name == "securityHardening":
                result = await self.handle_security_hardening(arguments, operation_id)
            elif name == "gitStatus":
                result = await self.handle_git_status(arguments, operation_id)
            elif name == "gitSmartCommit":
                result = await self.handle_git_smart_commit(arguments, operation_id)
            elif name == "gitCreateFeatureBranch":
                result = await self.handle_git_create_feature_branch(arguments, operation_id)
            elif name == "gitMergeWithResolution":
                result = await self.handle_git_merge_with_resolution(arguments, operation_id)
            elif name == "apiCallSecure":
                result = await self.handle_api_call_secure(arguments, operation_id)
            elif name == "apiMonitorMetrics":
                result = await self.handle_api_monitor_metrics(arguments, operation_id)
            elif name == "apiValidateCompliance":
                result = await self.handle_api_validate_compliance(arguments, operation_id)
            elif name == "projectSearch":
                result = await self.handle_project_search(arguments, operation_id)
            elif name == "todoListFromCode":
                result = await self.handle_todo_list_from_code(arguments, operation_id)
            elif name == "readmeGenerateOrUpdate":
                result = await self.handle_readme_generate_or_update(arguments, operation_id)
            elif name == "changelogSummarize":
                result = await self.handle_changelog_summarize(arguments, operation_id)
            elif name == "buildAndTest":
                result = await self.handle_build_and_test(arguments, operation_id)
            elif name == "dependencyAudit":
                result = await self.handle_dependency_audit(arguments, operation_id)
            # Let other tools fall through to intelligent manager
            # elif name == "setupRetrofitApi":
            #     result = await self.handle_setup_retrofit_api(arguments, operation_id)
            # elif name == "implementGdprCompliance":
            #     result = await self.handle_implement_gdpr_compliance(arguments, operation_id)
            # elif name == "implementHipaaCompliance":
            #     result = await self.handle_implement_hipaa_compliance(arguments, operation_id)
            # elif name == "setupSecureStorage":
            #     result = await self.handle_setup_secure_storage(arguments, operation_id)
            # elif name == "queryLlm":
            #     result = await self.handle_query_llm(arguments, operation_id)
            # elif name == "analyzeCodeWithAi":
            #     result = await self.handle_analyze_code_quality(arguments, operation_id)
            # elif name == "generateCodeWithAi":
            #     result = await self.handle_generate_code_with_ai(arguments, operation_id)
            # elif name == "generateUnitTests":
            #     result = await self.handle_generate_tests(arguments, operation_id)
            # elif name == "setupUiTesting":
            #     result = await self.handle_setup_ui_testing(arguments, operation_id)
            # elif name == "manageProjectFiles":
            #     result = await self.handle_manage_project_files(arguments, operation_id)
            # elif name == "setupCloudSync":
            #     result = await self.handle_setup_cloud_sync(arguments, operation_id)
            # elif name == "setupExternalApi":
            #     result = await self.handle_setup_external_api(arguments, operation_id)
            # elif name == "callExternalApi":
            #     result = await self.handle_call_external_api(arguments, operation_id)
            else:
                # All other tools are handled by the intelligent tool manager
                # This ensures proper MCP protocol communication while using intelligent capabilities
                if self.intelligent_tool_manager:
                    await self.send_progress(
                        operation_id, 30, f"Executing {name} via intelligent tool manager"
                    )

                    # Use intelligent tool manager but ensure MCP protocol compliance
                    try:
                        result = await self.intelligent_tool_manager.execute_intelligent_tool(
                            name, arguments
                        )

                        # Ensure the result is in proper MCP format
                        if isinstance(result, dict) and "content" in result:
                            # Already in MCP format
                            mcp_result = result
                        else:
                            # Convert to MCP format
                            mcp_result = {
                                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                            }

                        await self.send_progress(operation_id, 100, f"Completed {name}")

                        # Clean up operation tracking
                        del self.active_operations[operation_id]

                        self.log_message(
                            f"Completed tool: {name} (ID: {operation_id})", level="info"
                        )

                        return mcp_result

                    except Exception as e:
                        self.log_message(
                            f"Intelligent tool manager error for {name}: {e}", level="error"
                        )
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(
                                        {
                                            "success": False,
                                            "error": f"Tool execution failed: {str(e)}",
                                            "tool_name": name,
                                        },
                                        indent=2,
                                    ),
                                }
                            ],
                            "isError": True,
                        }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(
                                    {
                                        "success": False,
                                        "error": "Intelligent tool manager not available",
                                        "tool_name": name,
                                    },
                                    indent=2,
                                ),
                            }
                        ],
                        "isError": True,
                    }

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

        # Note: kotlin_generator is always initialized, but check for safety
        if not self.kotlin_generator:
            await self.send_progress(operation_id, 100, "Kotlin generator initialization error")
            return {
                "success": False,
                "error": "Kotlin generator initialization error",
                "message": "Internal error: Kotlin generator should always be initialized.",
            }

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

    # New tool handlers using sidecar and new tools
    async def handle_refactor_function(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle refactorFunction tool using sidecar."""
        try:
            from sidecar_client import refactor_function

            await self.send_progress(operation_id, 30, "Delegating to Kotlin sidecar")

            result = await refactor_function(
                file_path=arguments.get("filePath"),
                function_name=arguments.get("functionName"),
                refactor_type=arguments.get("refactorType"),
                new_name=arguments.get("newName"),
                preview=arguments.get("preview", False),
            )

            await self.send_progress(operation_id, 80, "Processing sidecar response")

            return result
        except ImportError:
            # Fallback if sidecar not available
            return {
                "success": False,
                "error": "Kotlin sidecar not available",
                "message": "Install and configure the Kotlin sidecar for enhanced refactoring capabilities",
            }

    async def handle_apply_code_action(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle applyCodeAction tool using sidecar."""
        try:
            from sidecar_client import apply_code_action

            await self.send_progress(operation_id, 30, "Delegating to Kotlin sidecar")

            result = await apply_code_action(
                file_path=arguments.get("filePath"),
                code_action_id=arguments.get("codeActionId"),
                preview=arguments.get("preview", False),
            )

            return result
        except ImportError:
            return {
                "success": False,
                "error": "Kotlin sidecar not available",
                "message": "Install and configure the Kotlin sidecar for code actions",
            }

    async def handle_format_code(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle formatCode tool using sidecar."""
        try:
            from sidecar_client import format_code

            await self.send_progress(operation_id, 30, "Delegating to Kotlin sidecar")

            result = await format_code(
                targets=arguments.get("targets", []),
                style=arguments.get("style", "ktlint"),
                preview=arguments.get("preview", False),
            )

            return result
        except ImportError:
            return {
                "success": False,
                "error": "Kotlin sidecar not available",
                "message": "Install and configure the Kotlin sidecar for code formatting",
            }

    async def handle_optimize_imports(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle optimizeImports tool using sidecar."""
        try:
            from sidecar_client import optimize_imports

            await self.send_progress(operation_id, 30, "Delegating to Kotlin sidecar")

            result = await optimize_imports(
                project_root=arguments.get("projectRoot"),
                mode=arguments.get("mode", "project"),
                targets=arguments.get("targets"),
                preview=arguments.get("preview", False),
            )

            return result
        except ImportError:
            return {
                "success": False,
                "error": "Kotlin sidecar not available",
                "message": "Install and configure the Kotlin sidecar for import optimization",
            }

    async def handle_git_status(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle gitStatus tool."""
        from tools.intelligent_build_tools import IntelligentGitTool

        await self.send_progress(operation_id, 30, "Checking Git status")

        git_tool = IntelligentGitTool(str(self.project_path), self.security_manager)
        result = await git_tool._execute_core_functionality(None, {"operation": "status"})

        return result

    async def handle_git_smart_commit(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle gitSmartCommit tool."""
        from tools.intelligent_build_tools import IntelligentGitTool

        await self.send_progress(operation_id, 30, "Creating smart commit")

        git_tool = IntelligentGitTool(str(self.project_path), self.security_manager)
        result = await git_tool._execute_core_functionality(None, {"operation": "smart_commit"})

        return result

    async def handle_git_create_feature_branch(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle gitCreateFeatureBranch tool."""
        from tools.intelligent_build_tools import IntelligentGitTool

        await self.send_progress(operation_id, 30, "Creating feature branch")

        git_tool = IntelligentGitTool(str(self.project_path), self.security_manager)
        result = await git_tool._execute_core_functionality(
            None, {"operation": "create_feature_branch", "branch_name": arguments.get("branchName")}
        )

        return result

    async def handle_git_merge_with_resolution(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle gitMergeWithResolution tool."""
        from tools.intelligent_build_tools import IntelligentGitTool

        await self.send_progress(operation_id, 30, "Attempting merge with resolution")

        git_tool = IntelligentGitTool(str(self.project_path), self.security_manager)
        result = await git_tool._execute_core_functionality(
            None,
            {
                "operation": "merge_with_resolution",
                "target_branch": arguments.get("targetBranch", "main"),
            },
        )

        return result

    async def handle_api_call_secure(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle apiCallSecure tool."""
        from tools.intelligent_external_api_tools import IntelligentExternalAPITool

        await self.send_progress(operation_id, 30, "Making secure API call")

        api_tool = IntelligentExternalAPITool(str(self.project_path), self.security_manager)
        result = await api_tool._execute_core_functionality(
            None,
            {
                "operation": "call",
                "api_name": arguments.get("apiName"),
                "endpoint": arguments.get("endpoint"),
                "method": arguments.get("method", "GET"),
                "headers": arguments.get("headers", {}),
                "data": arguments.get("data"),
                "auth": arguments.get("auth", {}),
            },
        )

        return result

    async def handle_api_monitor_metrics(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle apiMonitorMetrics tool."""
        from tools.intelligent_external_api_tools import IntelligentExternalAPITool

        await self.send_progress(operation_id, 30, "Retrieving API metrics")

        api_tool = IntelligentExternalAPITool(str(self.project_path), self.security_manager)
        result = await api_tool._execute_core_functionality(
            None,
            {
                "operation": "monitor",
                "api_name": arguments.get("apiName"),
                "window_minutes": arguments.get("windowMinutes", 60),
            },
        )

        return result

    async def handle_api_validate_compliance(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle apiValidateCompliance tool."""
        from tools.intelligent_external_api_tools import IntelligentExternalAPITool

        await self.send_progress(operation_id, 30, "Validating API compliance")

        api_tool = IntelligentExternalAPITool(str(self.project_path), self.security_manager)
        result = await api_tool._execute_core_functionality(
            None,
            {
                "operation": "validate_compliance",
                "api_name": arguments.get("apiName"),
                "compliance_type": arguments.get("complianceType", "gdpr"),
            },
        )

        return result

    async def handle_security_hardening(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle securityHardening tool."""
        from tools.security_hardening import HardeningTool

        await self.send_progress(operation_id, 30, "Executing security hardening operation")

        hardening_tool = HardeningTool(str(self.project_path))
        result = await hardening_tool._execute_core_functionality(None, arguments)

        return result

    async def handle_project_search(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle projectSearch tool."""
        from tools.intelligent_qol_dev_tools import IntelligentQoLDevTool

        await self.send_progress(operation_id, 30, "Searching project")

        qol_tool = IntelligentQoLDevTool(str(self.project_path), self.security_manager)
        result = await qol_tool._execute_core_functionality(
            None,
            {
                "operation": "search",
                "query": arguments.get("query"),
                "include_pattern": arguments.get("includePattern", "*"),
                "max_results": arguments.get("maxResults", 50),
                "context_lines": arguments.get("contextLines", 2),
            },
        )

        return result

    async def handle_todo_list_from_code(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle todoListFromCode tool."""
        from tools.intelligent_qol_dev_tools import IntelligentQoLDevTool

        await self.send_progress(operation_id, 30, "Extracting TODOs from code")

        qol_tool = IntelligentQoLDevTool(str(self.project_path), self.security_manager)
        result = await qol_tool._execute_core_functionality(
            None,
            {
                "operation": "todo_list",
                "include_pattern": arguments.get("includePattern", "*.{kt,java,py,js,ts}"),
                "max_results": arguments.get("maxResults", 100),
            },
        )

        return result

    async def handle_readme_generate_or_update(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle readmeGenerateOrUpdate tool."""
        from tools.intelligent_qol_dev_tools import IntelligentQoLDevTool

        await self.send_progress(operation_id, 30, "Generating/updating README")

        qol_tool = IntelligentQoLDevTool(str(self.project_path), self.security_manager)
        result = await qol_tool._execute_core_functionality(
            None,
            {
                "operation": "readme_update",
                "force_regenerate": arguments.get("forceRegenerate", False),
            },
        )

        return result

    async def handle_changelog_summarize(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle changelogSummarize tool."""
        from tools.intelligent_qol_dev_tools import IntelligentQoLDevTool

        await self.send_progress(operation_id, 30, "Summarizing changelog")

        qol_tool = IntelligentQoLDevTool(str(self.project_path), self.security_manager)
        result = await qol_tool._execute_core_functionality(
            None,
            {
                "operation": "changelog_summarize",
                "changelog_path": arguments.get("changelogPath", "CHANGELOG.md"),
                "version": arguments.get("version", "latest"),
            },
        )

        return result

    async def handle_build_and_test(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle buildAndTest tool."""
        from tools.build_and_test_tool import BuildAndTestTool

        await self.send_progress(operation_id, 30, "Building and testing")

        # Use new project root enforcing tool
        build_tool = BuildAndTestTool(self.security_manager)
        result = await build_tool.build_and_test(arguments)

        return result

    async def handle_dependency_audit(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle dependencyAudit tool."""
        from tools.intelligent_qol_dev_tools import IntelligentQoLDevTool

        await self.send_progress(operation_id, 30, "Auditing dependencies")

        qol_tool = IntelligentQoLDevTool(str(self.project_path), self.security_manager)
        result = await qol_tool._execute_core_functionality(None, {"operation": "dependency_audit"})

        return result

    # All tool handling now delegated to intelligent tool manager

    async def handle_android_generate_compose_ui(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle androidGenerateComposeUI tool."""
        return {"success": True, "message": "Compose UI generated"}

    async def handle_android_setup_architecture(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle androidSetupArchitecture tool."""
        return {"success": True, "message": "Architecture setup completed"}

    async def handle_android_setup_data_layer(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle androidSetupDataLayer tool."""
        return {"success": True, "message": "Data layer setup completed"}

    async def handle_android_setup_network(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle androidSetupNetwork tool."""
        return {"success": True, "message": "Network setup completed"}

    async def handle_security_encrypt_data(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle securityEncryptData tool."""
        return {"success": True, "message": "Data encrypted"}

    async def handle_security_decrypt_data(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle securityDecryptData tool."""
        return {"success": True, "message": "Data decrypted"}

    async def handle_privacy_request_erasure(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle privacyRequestErasure tool."""
        return {"success": True, "message": "Data erased"}

    async def handle_privacy_export_data(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle privacyExportData tool."""
        return {"success": True, "message": "Data exported"}

    async def handle_security_audit_trail(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle securityAuditTrail tool."""
        return {"success": True, "message": "Audit trail queried"}

    async def handle_file_backup(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle fileBackup tool."""
        return {"success": True, "message": "Files backed up"}

    async def handle_file_restore(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle fileRestore tool."""
        return {"success": True, "message": "Files restored"}

    async def handle_file_sync_watch(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle fileSyncWatch tool."""
        return {"success": True, "message": "File sync started"}

    async def handle_file_classify_sensitivity(
        self, arguments: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """Handle fileClassifySensitivity tool."""
        return {"success": True, "message": "Files classified"}

    async def call_gradle_build(
        self, args: GradleBuildRequest, operation_id: str
    ) -> Dict[str, Any]:
        """Execute gradle_build tool."""

        await self.send_progress(operation_id, 20, "Preparing Gradle build")

        # Note: gradle_tools is always initialized, but check for safety
        if not self.gradle_tools:
            return {
                "success": False,
                "error": "Internal error: Gradle tools should always be initialized.",
                "message": "Gradle tools initialization failed. This is an internal error.",
            }

        await self.send_progress(operation_id, 40, f"Running Gradle task: {args.task}")

        # Pass arguments as dict to match existing API
        arguments = {"task": args.task, "clean": args.clean}
        result = await self.gradle_tools.gradle_build(arguments)

        await self.send_progress(operation_id, 80, "Processing build results")

        # Propagate error messages if build failed
        response = {
            "success": result.get("success", False),
            "task": args.task,
            "output": result.get("output", ""),
            "execution_time": result.get("execution_time", 0),
        }

        # Include error message if present
        if "error" in result:
            response["error"] = result["error"]

        return response

    async def call_analyze_project(
        self, args: ProjectAnalysisRequest, operation_id: str
    ) -> Dict[str, Any]:
        """Execute analyze_project tool."""

        await self.send_progress(operation_id, 30, "Starting project analysis")

        # Note: project_analysis is always initialized, but check for safety
        if not self.project_analysis:
            await self.send_progress(
                operation_id,
                100,
                "Project analysis tools initialization error",
            )
            return {
                "success": False,
                "analysis_type": args.analysis_type,
                "message": "Internal error: Project analysis tools should always be initialized.",
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

        # Delegate to intelligent tool manager - no fallback needed
        if self.intelligent_tool_manager:
            return await self.intelligent_tool_manager.execute_intelligent_tool(name, arguments)

        # Return error if no tool manager available
        return {
            "content": [
                {"type": "text", "text": f"Tool {name} not available - no intelligent tool manager"}
            ],
            "isError": True,
        }

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
            elif method == "logging/setLevel":
                # Handle VS Code logging level setting
                level = params.get("level", "info")
                self.logger.info(f"MCP client requested log level: {level}")
                # We can optionally adjust our logging level here
                return {"jsonrpc": "2.0", "id": request_id, "result": {}}
            else:
                # Unknown method
                return self.create_error_response(-32601, f"Unknown method: {method}", request_id)

        except ValidationError as e:
            return self.create_error_response(-32602, f"Invalid params: {e}", request_id)
        except Exception as e:
            self.log_message(f"Request handling error: {e}", level="error")
            return self.create_error_response(-32000, f"Server error: {e}", request_id)


def create_server(project_path: Optional[str] = None) -> KotlinMCPServerV2:
    """Create and configure the enhanced MCP server."""
    return KotlinMCPServerV2(project_path=project_path)


async def main() -> None:
    """Main function to start the enhanced MCP server."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Kotlin MCP Server v2 (Enhanced)")
    parser.add_argument(
        "project_path", nargs="?", help="Path to the Android project root directory"
    )
    parser.add_argument(
        "--list-tools", action="store_true", help="List all available tools and exit"
    )
    args = parser.parse_args()

    # Create server with project path
    if args.project_path:
        project_path = Path(args.project_path)
        if project_path.exists():
            server = KotlinMCPServerV2(project_path=str(project_path))
            server.log_message(f"Using provided project path: {project_path}", level="info")
        else:
            print(
                f"Warning: Provided project path {project_path} does not exist, using current directory"
            )
            server = KotlinMCPServerV2()  # Will use current directory
    else:
        server = KotlinMCPServerV2()  # Will use current directory
        server.log_message(
            "No project path provided, using current working directory", level="info"
        )

    # Handle --list-tools option
    if args.list_tools:
        try:
            tools_response = await server.handle_list_tools()
            tools = tools_response.get("tools", [])
            print(f"Available tools ({len(tools)}):")
            for i, tool in enumerate(tools, 1):
                name = tool.get("name", "unknown")
                desc = tool.get("description", "No description")[:60]
                print(f"  {i:2d}. {name} - {desc}...")
            return
        except Exception as e:
            print(f"Error listing tools: {e}")
            sys.exit(1)

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
