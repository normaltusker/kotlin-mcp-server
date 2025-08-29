#!/usr/bin/env python3
"""
Kotlin MCP Server - Modular version

A comprehensive Model Context Protocol server for Android/Kotlin development
that has been refactored into smaller, manageable modules.

This is the main server file that coordinates all the tool modules:
- utils.security: Security and logging utilities
- generators.kotlin_generator: Kotlin code generation
- tools.gradle_tools: Gradle build operations
- tools.project_analysis: Project analysis and refactoring
- tools.build_optimization: Build performance optimization

Author: MCP Development Team
Version: 2.0.0 (Modular)
License: MIT
"""

import argparse
import json
import sys
import asyncio
import os
import httpx
import shutil
from pathlib import Path
from typing import Optional

from ai.llm_integration import AnalysisRequest, CodeGenerationRequest, CodeType, LLMIntegration
from generators.kotlin_generator import KotlinCodeGenerator
from tools.build_optimization import BuildOptimizationTools
from tools.gradle_tools import GradleTools
from tools.project_analysis import ProjectAnalysisTools

# Import modular components
from utils.security import SecurityManager


class KotlinMCPServer:
    """Main MCP Server class that coordinates all tool modules."""

    def __init__(self, name: str):
        """Initialize the MCP server with all tool modules."""
        self.name = name
        self.project_path: Optional[Path] = None

        # Initialize core components
        self.security_manager = SecurityManager()
        self.llm_integration = LLMIntegration(self.security_manager)
        self.kotlin_generator = KotlinCodeGenerator(self.llm_integration)

        # Tool modules (initialized after project path is set)
        self.gradle_tools: Optional[GradleTools] = None
        self.project_analysis: Optional[ProjectAnalysisTools] = None
        self.build_optimization: Optional[BuildOptimizationTools] = None

    def set_project_path(self, project_path: str) -> None:
        """Set the project path and initialize tool modules."""
        self.project_path = Path(project_path)

        # Initialize tool modules with project path
        self.gradle_tools = GradleTools(self.project_path, self.security_manager)
        self.project_analysis = ProjectAnalysisTools(self.project_path, self.security_manager)
        self.build_optimization = BuildOptimizationTools(self.project_path, self.security_manager)

    async def handle_initialize(self, params: dict) -> dict:
        """Handle MCP initialize request."""
        return {
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "resources": {
                    "subscribe": False,
                    "listChanged": False,
                },
                "tools": {},
                "logging": {},
            },
            "serverInfo": {
                "name": self.name,
                "version": "2.0.0",
            },
        }

    async def handle_list_tools(self) -> dict:
        """List all available tools from all modules."""
        tools = [
            # Kotlin Code Generation Tools
            {
                "name": "create_kotlin_file",
                "description": (
                    "Create production-ready Kotlin files with complete implementations for "
                    "Android development. Supports Activities, ViewModels, Repositories, Data "
                    "Classes, Use Cases, Services, Adapters, Interfaces, and general Classes "
                    "with modern Android patterns including Jetpack Compose, MVVM architecture, "
                    "Hilt dependency injection, and comprehensive error handling. "
                    "Class name and package name can be inferred from the file path."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": (
                                "Path where the Kotlin file should be created "
                                "(relative to project root). Used to infer class and package name if not provided."
                            ),
                        },
                        "class_name": {
                            "type": "string",
                            "description": "Optional: Name of the Kotlin class to create. If not provided, it's inferred from the file name.",
                        },
                        "package_name": {
                            "type": "string",
                            "description": "Optional: Kotlin package name (e.g., com.example.app.ui). If not provided, it's inferred from the file path.",
                        },
                        "class_type": {
                            "type": "string",
                            "enum": [
                                "activity",
                                "fragment",
                                "viewmodel",
                                "repository",
                                "data_class",
                                "use_case",
                                "service",
                                "adapter",
                                "interface",
                                "class",
                            ],
                            "description": "Type of Kotlin class to generate",
                        },
                        "features": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "viewmodel",
                                    "livedata",
                                    "coroutines",
                                    "navigation",
                                    "hilt",
                                    "room",
                                    "retrofit",
                                    "compose",
                                    "material3",
                                ],
                            },
                            "description": "Android features to include in the generated code",
                        },
                        "generate_related": {
                            "type": "boolean",
                            "description": "Whether to generate related files (e.g., ViewModel for Activity)",
                            "default": False,
                        },
                    },
                    "required": ["file_path", "class_type"],
                },
            },
            # Gradle Build Tools
            {
                "name": "gradle",
                "description": "Execute Gradle operations like building, testing, and getting dependencies.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sub_command": {
                            "type": "string",
                            "enum": ["build", "test", "get_dependencies"],
                            "description": "The Gradle operation to perform."
                        },
                        "build_type": {
                            "type": "string",
                            "enum": ["debug", "release"],
                            "default": "debug",
                            "description": "Type of build to execute (for build operation)."
                        },
                        "clean": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether to clean before building (for build operation)."
                        },
                        "test_type": {
                            "type": "string",
                            "enum": ["unit", "integration", "ui", "all"],
                            "default": "unit",
                            "description": "Type of tests to run (for test operation)."
                        },
                        "coverage": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to generate coverage reports (for test operation)."
                        }
                    },
                    "required": ["sub_command"]
                }
            },
            # Project Analysis Tools
            {
                "name": "analyze_project",
                "description": "Perform comprehensive project analysis including structure assessment, dependency analysis, manifest validation, and build configuration review.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "analysis_type": {
                            "type": "string",
                            "enum": [
                                "comprehensive",
                                "structure",
                                "dependencies",
                                "manifest",
                                "gradle",
                                "architecture",
                                "proactive_analysis"
                            ],
                            "default": "comprehensive",
                            "description": "Type of analysis to perform",
                        }
                    },
                },
            },
            {
                "name": "analyze_and_refactor_project",
                "description": "Advanced project analysis with automated refactoring capabilities. Performs deep structure analysis, code quality improvements, dependency updates, security fixes, and UI modernization with configurable automation levels.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "modernization_level": {
                            "type": "string",
                            "enum": ["conservative", "moderate", "aggressive"],
                            "default": "moderate",
                            "description": "Level of modernization to apply",
                        },
                        "target_api_level": {
                            "type": "integer",
                            "default": 34,
                            "description": "Target Android API level",
                        },
                        "focus_areas": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "compose",
                                    "coroutines",
                                    "hilt",
                                    "performance",
                                    "security",
                                ],
                            },
                            "default": ["compose", "coroutines", "hilt"],
                            "description": "Areas to focus modernization efforts on",
                        },
                        "apply_fixes": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether to automatically apply fixes (USE WITH CAUTION)",
                        },
                        "proactive": {
                            "type": "boolean",
                            "default": False,
                            "description": "If true, the tool will proactively suggest modernizations."
                        }
                    },
                },
            },
            {
                "name": "debug",
                "description": "Analyze a stack trace to identify the cause of an error and suggest a fix.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "stack_trace": {
                            "type": "string",
                            "description": "The stack trace to analyze."
                        }
                    },
                    "required": ["stack_trace"]
                }
            },
            {
                "name": "tickets",
                "description": "Interact with issue trackers like GitHub Issues.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sub_command": {
                            "type": "string",
                            "enum": ["list", "create", "view", "comment", "assign", "close"],
                            "description": "The issue tracker operation to perform."
                        },
                        "repo": {
                            "type": "string",
                            "description": "The GitHub repository (e.g., \"owner/repo\")."
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "The issue number (for view, comment, assign, close operations)."
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the new issue (for create operation)."
                        },
                        "body": {
                            "type": "string",
                            "description": "The body of the new issue (for create operation)."
                        },
                        "comment_body": {
                            "type": "string",
                            "description": "The body of the comment (for comment operation)."
                        },
                        "assignee": {
                            "type": "string",
                            "description": "The GitHub username to assign the issue to (for assign operation)."
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed"],
                            "description": "The state to set the issue to (for close operation)."
                        }
                    },
                    "required": ["sub_command", "repo"]
                }
            },
            {
                "name": "design",
                "description": "Inspect a Figma file and extract basic metadata.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sub_command": {
                            "type": "string",
                            "enum": ["get_file_metadata", "extract_tokens"],
                            "description": "The design operation to perform."
                        },
                        "figma_file_url": {
                            "type": "string",
                            "description": "The URL of the Figma file."
                        },
                        "figma_token": {
                            "type": "string",
                            "description": "Your Figma personal access token."
                        },
                        "token_type": {
                            "type": "string",
                            "enum": ["colors", "fonts", "all"],
                            "description": "The type of design tokens to extract."
                        },
                        "output_file": {
                            "type": "string",
                            "description": "The path to the output Kotlin file (e.g., app/src/main/java/com/example/app/ui/theme/Theme.kt)."
                        }
                    },
                    "required": ["sub_command", "figma_file_url", "figma_token"]
                }
            },
            {
                "name": "ci",
                "description": "Interact with GitHub Actions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sub_command": {
                            "type": "string",
                            "enum": ["list_workflows", "get_workflow_runs", "rerun_workflow", "get_run_logs", "get_test_results"],
                            "description": "The CI operation to perform."
                        },
                        "repo": {
                            "type": "string",
                            "description": "The GitHub repository (e.g., \"owner/repo\")."
                        },
                        "workflow_id": {
                            "type": "string",
                            "description": "The ID of the workflow (e.g., \"ci.yml\")."
                        },
                        "run_id": {
                            "type": "integer",
                            "description": "The ID of the workflow run."
                        },
                        "job_id": {
                            "type": "integer",
                            "description": "The ID of the job within the workflow run."
                        }
                    },
                    "required": ["sub_command", "repo"]
                }
            }
            # Build Optimization Tools
            {
                "name": "optimize_build_performance",
                "description": "Comprehensive build performance optimization including Gradle configuration analysis, cache optimization, parallel execution setup, and performance measurement with before/after comparison.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "optimization_level": {
                            "type": "string",
                            "enum": ["conservative", "moderate", "aggressive"],
                            "default": "moderate",
                            "description": "Level of optimization to apply",
                        },
                        "measure_baseline": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to measure baseline performance",
                        },
                        "apply_optimizations": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether to apply optimizations automatically",
                        },
                    },
                },
            },
            # AI/LLM Integration Tools
            {
                "name": "generate_code_with_ai",
                "description": "Generate sophisticated, production-ready Kotlin/Android code using AI. Leverages the calling LLM to create complete implementations with modern patterns, proper error handling, and comprehensive business logic. Generates actual working code, not templates or skeletons.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Natural language description of the code to generate",
                        },
                        "code_type": {
                            "type": "string",
                            "enum": [
                                "activity",
                                "fragment",
                                "viewmodel",
                                "repository",
                                "service",
                                "utility_class",
                                "data_class",
                                "interface",
                                "enum",
                                "test",
                                "custom",
                            ],
                            "description": "Type of code to generate",
                        },
                        "class_name": {
                            "type": "string",
                            "description": "Name of the class to generate",
                        },
                        "package_name": {
                            "type": "string",
                            "description": "Package name for the generated code",
                        },
                        "framework": {
                            "type": "string",
                            "enum": ["android", "kotlin", "compose"],
                            "default": "android",
                            "description": "Target framework",
                        },
                        "features": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "compose",
                                    "hilt",
                                    "room",
                                    "retrofit",
                                    "coroutines",
                                    "stateflow",
                                    "navigation",
                                    "material3",
                                    "viewmodel",
                                    "repository",
                                    "testing",
                                ],
                            },
                            "description": "Framework features to include",
                        },
                        "compliance_requirements": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["gdpr", "hipaa", "accessibility", "security"],
                            },
                            "description": "Compliance requirements to consider",
                        },
                    },
                    "required": ["description", "code_type", "class_name", "package_name"],
                },
            },
            {
                "name": "analyze_code_with_ai",
                "description": "Perform comprehensive AI-powered code analysis to identify quality issues, security vulnerabilities, performance optimizations, and architectural improvements. Provides actionable recommendations with specific code examples.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Kotlin file to analyze",
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["quality", "security", "performance", "architecture", "all"],
                            "default": "all",
                            "description": "Type of analysis to perform",
                        },
                        "specific_concerns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific areas of concern to focus on",
                        },
                    },
                    "required": ["file_path"],
                },
            },
            {
                "name": "enhance_existing_code",
                "description": "Use AI to enhance existing Kotlin code by adding missing functionality, improving patterns, optimizing performance, and modernizing to current best practices. Maintains existing logic while adding sophistication.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Kotlin file to enhance",
                        },
                        "enhancement_type": {
                            "type": "string",
                            "enum": [
                                "add_functionality",
                                "improve_patterns",
                                "optimize_performance",
                                "modernize",
                                "add_tests",
                                "add_documentation",
                            ],
                            "description": "Type of enhancement to apply",
                        },
                        "specific_requirements": {
                            "type": "string",
                            "description": "Specific requirements or features to add",
                        },
                    },
                    "required": ["file_path", "enhancement_type"],
                },
            },
            # Additional Tools for Feature Parity
            {
                "name": "create_layout_file",
                "description": "Create XML layout files for Android with modern design patterns including Material 3, ConstraintLayout, and Compose compatibility.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path for the layout file"},
                        "layout_name": {"type": "string", "description": "Name of the layout"},
                        "layout_type": {
                            "type": "string",
                            "enum": ["activity", "fragment", "item", "dialog", "custom"],
                            "description": "Type of layout to create",
                        },
                        "features": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Layout features to include",
                        },
                    },
                    "required": ["file_path", "layout_name", "layout_type"],
                },
            },
            {
                "name": "format_code",
                "description": "Format Kotlin code using ktlint and other formatting tools.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to file to format"}
                    },
                    "required": ["file_path"],
                },
            },
            {
                "name": "run_lint",
                "description": "Run Android lint checks with comprehensive reporting.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "fix_issues": {
                            "type": "boolean",
                            "default": False,
                            "description": "Auto-fix issues where possible",
                        }
                    },
                },
            },
            {
                "name": "generate_docs",
                "description": "Generate comprehensive documentation for the project.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doc_type": {
                            "type": "string",
                            "enum": ["api", "user", "architecture", "all"],
                            "default": "all",
                        }
                    },
                },
            },
            {
                "name": "create_compose_component",
                "description": "Create sophisticated Jetpack Compose components with state management and theming.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "component_name": {
                            "type": "string",
                            "description": "Name of the Compose component",
                        },
                        "package_name": {"type": "string", "description": "Package name"},
                        "component_type": {
                            "type": "string",
                            "enum": ["screen", "widget", "dialog", "custom"],
                            "description": "Type of component",
                        },
                        "features": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Compose features to include",
                        },
                    },
                    "required": ["component_name", "package_name", "component_type"],
                },
            },
            {
                "name": "create_custom_view",
                "description": "Create custom Android View components with proper lifecycle and drawing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "view_name": {"type": "string", "description": "Name of the custom view"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "view_type": {
                            "type": "string",
                            "enum": ["canvas", "viewgroup", "compound", "widget"],
                            "description": "Type of custom view",
                        },
                    },
                    "required": ["view_name", "package_name", "view_type"],
                },
            },
            {
                "name": "scaffold",
                "description": "Scaffold a new feature module with all necessary files and architecture.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature to scaffold (e.g., login, profile)."
                        },
                        "feature_description": {
                            "type": "string",
                            "description": "A high-level description of the feature (e.g., a login screen with email and password)."
                        }
                    },
                    "required": ["feature_name", "feature_description"]
                }
            },
            {
                "name": "setup_dependency_injection",
                "description": "Configure Hilt dependency injection with modules and components.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "injection_type": {
                            "type": "string",
                            "enum": ["hilt", "dagger", "koin"],
                            "default": "hilt",
                        },
                        "modules": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "DI modules to create",
                        },
                    },
                },
            },
            {
                "name": "setup_room_database",
                "description": "Set up Room database with entities, DAOs, and migrations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database_name": {"type": "string", "description": "Name of the database"},
                        "entities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Entity names to create",
                        },
                        "version": {"type": "integer", "default": 1},
                    },
                    "required": ["database_name"],
                },
            },
            {
                "name": "setup_retrofit_api",
                "description": "Configure Retrofit API client with interceptors and converters.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "api_name": {"type": "string", "description": "Name of the API service"},
                        "base_url": {"type": "string", "description": "Base URL for the API"},
                        "endpoints": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "API endpoints to create",
                        },
                    },
                    "required": ["api_name", "base_url"],
                },
            },
            {
                "name": "encrypt_sensitive_data",
                "description": "Implement encryption for sensitive data storage and transmission.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "encryption_type": {
                            "type": "string",
                            "enum": ["aes", "rsa", "biometric"],
                            "default": "aes",
                        },
                        "data_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of data to encrypt",
                        },
                    },
                },
            },
            {
                "name": "implement_gdpr_compliance",
                "description": "Implement GDPR compliance features including consent management and data handling.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "compliance_level": {
                            "type": "string",
                            "enum": ["basic", "comprehensive"],
                            "default": "basic",
                        }
                    },
                },
            },
            {
                "name": "implement_hipaa_compliance",
                "description": "Implement HIPAA compliance for healthcare applications.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "security_level": {
                            "type": "string",
                            "enum": ["standard", "high"],
                            "default": "standard",
                        }
                    },
                },
            },
            {
                "name": "setup_secure_storage",
                "description": "Configure secure storage using Android Keystore and EncryptedSharedPreferences.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "storage_type": {
                            "type": "string",
                            "enum": ["preferences", "files", "database"],
                            "default": "preferences",
                        }
                    },
                },
            },
            {
                "name": "query_llm",
                "description": "Direct query to the LLM for custom assistance and code generation.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Question or request for the LLM",
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context for the query",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "manage_dependencies",
                "description": "Manage project dependencies including updates and conflict resolution.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["update", "add", "remove", "analyze"],
                            "description": "Action to perform",
                        },
                        "dependency": {"type": "string", "description": "Dependency to manage"},
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "manage_project_files",
                "description": "Manage project files including organization and cleanup.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["organize", "cleanup", "backup", "restore"],
                            "description": "File management operation",
                        }
                    },
                    "required": ["operation"],
                },
            },
            {
                "name": "setup_cloud_sync",
                "description": "Configure cloud synchronization for project data.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "enum": ["firebase", "aws", "azure", "gcp"],
                            "description": "Cloud provider",
                        },
                        "sync_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of data to sync",
                        },
                    },
                    "required": ["provider"],
                },
            },
            {
                "name": "setup_external_api",
                "description": "Configure external API integrations with proper authentication.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "api_name": {"type": "string", "description": "Name of the external API"},
                        "auth_type": {
                            "type": "string",
                            "enum": ["oauth", "apikey", "bearer"],
                            "description": "Authentication type",
                        },
                    },
                    "required": ["api_name", "auth_type"],
                },
            },
            {
                "name": "call_external_api",
                "description": "Make calls to external APIs with proper error handling.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "api_name": {"type": "string", "description": "Name of the API to call"},
                        "endpoint": {"type": "string", "description": "API endpoint"},
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE"],
                            "default": "GET",
                        },
                        "parameters": {"type": "object", "description": "API parameters"},
                    },
                    "required": ["api_name", "endpoint"],
                },
            },
            {
                "name": "generate_unit_tests",
                "description": "Generate comprehensive unit tests for Kotlin classes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_class": {
                            "type": "string",
                            "description": "Class to generate tests for",
                        },
                        "test_framework": {
                            "type": "string",
                            "enum": ["junit", "mockk", "espresso"],
                            "default": "junit",
                        },
                    },
                    "required": ["target_class"],
                },
            },
            {
                "name": "setup_ui_testing",
                "description": "Configure UI testing framework with Espresso or Compose testing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "testing_type": {
                            "type": "string",
                            "enum": ["espresso", "compose", "both"],
                            "default": "both",
                        }
                    },
                },
            },
            {
                "name": "file_system",
                "description": "Perform file system operations like read, write, list, and search.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sub_command": {
                            "type": "string",
                            "enum": ["read", "write", "list", "search", "delete", "move"],
                            "description": "The file system operation to perform."
                        },
                        "path": {
                            "type": "string",
                            "description": "The path to the file or directory (for read, write, list, search, delete)."
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file (for write operation)."
                        },
                        "pattern": {
                            "type": "string",
                            "description": "The search pattern (for search operation)."
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force the operation (for delete operation).",
                            "default": False
                        },
                        "source_path": {
                            "type": "string",
                            "description": "The source path (for move operation)."
                        },
                        "destination_path": {
                            "type": "string",
                            "description": "The destination path (for move operation)."
                        }
                    },
                    "required": ["sub_command"]
                }
            },
            {
                "name": "git",
                "description": "Perform git operations like status, diff, add, commit, and log.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sub_command": {
                            "type": "string",
                            "enum": ["status", "diff", "add", "commit", "log", "branch", "checkout", "stash", "cherry-pick"],
                            "description": "The git operation to perform."
                        },
                        "path": {
                            "type": "string",
                            "description": "The path to the file or directory to add."
                        },
                        "message": {
                            "type": "string",
                            "description": "The commit message (for commit operation)."
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name of the branch (for branch operation)."
                        },
                        "commit_hash": {
                            "type": "string",
                            "description": "The commit hash (for cherry-pick operation)."
                        }
                    },
                    "required": ["sub_command"]
                }
            }
        ]

        return {"tools": tools}

    async def handle_gradle_tool(self, arguments: dict) -> dict:
        """Handle gradle tool calls."""
        sub_command = arguments.get("sub_command")

        if not sub_command:
            return {"success": False, "error": "sub_command is required."}

        if not self.gradle_tools:
            return {"success": False, "error": "Gradle tools not initialized."}

        if sub_command == "build":
            return await self.gradle_tools.gradle_build(arguments)
        elif sub_command == "test":
            return await self.gradle_tools.run_tests(arguments)
        elif sub_command == "get_dependencies":
            return await self.gradle_tools.get_dependencies(arguments)
        else:
            return {"success": False, "error": f"Unknown sub_command: {sub_command}"}

    async def handle_project_analysis_tool(self, arguments: dict) -> dict:
        """Handle project analysis tool calls."""
        sub_command = arguments.get("analysis_type") # Keep analysis_type for backward compatibility

        if not sub_command:
            return {"success": False, "error": "analysis_type is required."}

        if not self.project_analysis:
            return {"success": False, "error": "Project analysis tools not initialized."}

        if sub_command == "architecture":
            return await self.project_analysis.analyze_architecture(arguments)
        elif sub_command == "proactive_analysis":
            return await self.project_analysis.proactive_analysis(arguments)
        else:
            # For other analysis types, we can call the old analyze_project method
            return await self.project_analysis.analyze_project(arguments)

    async def handle_call_tool(self, name: str, arguments: dict) -> dict:
        """Route tool calls to appropriate modules."""
        try:
            if not self.project_path:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000, # Server error
                        "message": "Error: No project path set. Please provide a project path when starting the server.",
                    },
                }

            # Ensure tool modules are initialized
            if not all([self.gradle_tools, self.project_analysis, self.build_optimization]):
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000, # Server error
                        "message": "Error: Tool modules not properly initialized. Please set project path.",
                    },
                }

            # Route to appropriate tool module
            if name == "create_kotlin_file":
                result = await self._create_kotlin_file(arguments)
            elif name == "gradle" and self.gradle_tools:
                result = await self.handle_gradle_tool(arguments)
            elif name == "project_analysis" and self.project_analysis:
                result = await self.handle_project_analysis_tool(arguments)
            elif name == "analyze_and_refactor_project" and self.project_analysis:
                result = await self.project_analysis.analyze_and_refactor_project(arguments)
            elif name == "optimize_build_performance" and self.build_optimization:
                result = await self.build_optimization.optimize_build_performance(arguments)
            # AI/LLM Integration Tools
            elif name == "generate_code_with_ai":
                result = await self._generate_code_with_ai(arguments)
            elif name == "analyze_code_with_ai":
                result = await self._analyze_code_with_ai(arguments)
            elif name == "enhance_existing_code":
                result = await self._enhance_existing_code(arguments)
            # Additional Tools for Feature Parity
            elif name == "create_layout_file":
                result = await self._create_layout_file(arguments)
            elif name == "format_code":
                result = await self._format_code(arguments)
            elif name == "run_lint":
                result = await self._run_lint(arguments)
            elif name == "generate_docs":
                result = await self._generate_docs(arguments)
            elif name == "create_compose_component":
                result = await self._create_compose_component(arguments)
            elif name == "create_custom_view":
                result = await self._create_custom_view(arguments)
            elif name == "scaffold":
                result = await self.handle_scaffold_tool(arguments)
            elif name == "setup_dependency_injection":
                result = await self._setup_dependency_injection(arguments)
            elif name == "setup_room_database":
                result = await self._setup_room_database(arguments)
            elif name == "setup_retrofit_api":
                result = await self._setup_retrofit_api(arguments)
            elif name == "encrypt_sensitive_data":
                result = await self._encrypt_sensitive_data(arguments)
            elif name == "implement_gdpr_compliance":
                result = await self._implement_gdpr_compliance(arguments)
            elif name == "implement_hipaa_compliance":
                result = await self._implement_hipaa_compliance(arguments)
            elif name == "setup_secure_storage":
                result = await self._setup_secure_storage(arguments)
            elif name == "query_llm":
                result = await self._query_llm(arguments)
            elif name == "manage_dependencies":
                result = await self._manage_dependencies(arguments)
            elif name == "manage_project_files":
                result = await self._manage_project_files(arguments)
            elif name == "setup_cloud_sync":
                result = await self._setup_cloud_sync(arguments)
            elif name == "setup_external_api":
                result = await self._setup_external_api(arguments)
            elif name == "call_external_api":
                result = await self._call_external_api(arguments)
            elif name == "generate_unit_tests":
                result = await self._generate_unit_tests(arguments)
            elif name == "setup_ui_testing":
                result = await self._setup_ui_testing(arguments)
            elif name == "file_system":
                result = await self.handle_file_system_tool(arguments)
            elif name == "git":
                result = await self.handle_git_tool(arguments)
            elif name == "debug":
                result = await self.handle_debug_tool(arguments)
            elif name == "tickets":
                result = await self.handle_tickets_tool(arguments)
            elif name == "design":
                result = await self.handle_design_tool(arguments)
            elif name == "ci":
                result = await self.handle_ci_tool(arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601, # Method not found
                        "message": f"Unknown tool: {name}",
                    },
                }

            # Format result for MCP response
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        except (KeyError, ValueError) as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602, # Invalid params
                    "message": f"Invalid parameters or tool execution failed: {str(e)}",
                },
            }
        except (RuntimeError, AttributeError) as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000, # Server error
                    "message": f"Unexpected server error: {str(e)}",
                },
            }
        except Exception as e: # Catch any other unexpected errors
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000, # Server error
                    "message": f"An unexpected error occurred: {str(e)}",
                },
            }

    async def _get_project_features(self) -> list[str]:
        """Analyze the project to find the features in use."""
        if not self.gradle_tools:
            return []

        # Get dependencies from gradle tool
        dependencies_result = await self.handle_gradle_tool({"sub_command": "get_dependencies"})
        if not dependencies_result.get("success"):
            return []
        
        dependencies = dependencies_result.get("dependencies", [])

        features = []
        # A mapping of dependency names to feature names
        feature_keywords = {
            "hilt": "hilt",
            "room": "room",
            "retrofit": "retrofit",
            "compose": "compose",
            "lifecycle-viewmodel": "viewmodel",
            "kotlinx-coroutines": "coroutines",
            "navigation-compose": "navigation",
        }

        for dep in dependencies:
            for keyword, feature in feature_keywords.items():
                if keyword in dep.get("name", ""):
                    features.append(feature)

        return list(set(features)) # remove duplicates

    async def _create_kotlin_file(self, arguments: dict) -> dict:
        """Create Kotlin file using the code generator."""
        try:
            if not self.project_path:
                return {"success": False, "error": "No project path set"}

            # Extract arguments
            file_path = arguments["file_path"]
            class_type = arguments["class_type"]
            user_features = arguments.get("features", []) # Features provided by the user
            generate_related = arguments.get("generate_related", False)

            # Get project features
            project_features = await self._get_project_features()
            
            # Combine user features and project features
            features = list(set(user_features + project_features))

            # Get project architecture
            arch_details = await self.handle_project_analysis_tool({"analysis_type": "architecture"})
            if not arch_details.get("success"):
                return arch_details

            source_root = arch_details.get("source_root")
            base_package_name = arch_details.get("package_name")

            # Construct full path if a relative path is given
            if not Path(file_path).is_absolute():
                if not base_package_name:
                    return {"success": False, "error": "Could not determine base package name."}
                file_path = f"{source_root}/{base_package_name.replace('.', '/')}/{file_path}"

            # Validate file path
            validated_path = self.security_manager.validate_file_path(file_path, self.project_path)

            # Infer class_name and package_name if not provided
            class_name = arguments.get("class_name")
            if not class_name:
                class_name = validated_path.stem

            package_name = arguments.get("package_name")
            if not package_name:
                try:
                    # Find the 'java' or 'kotlin' directory
                    java_dir_index = -1
                    for i, part in enumerate(validated_path.parts):
                        if part == 'java' or part == 'kotlin':
                            java_dir_index = i
                            break
                    
                    if java_dir_index != -1:
                        package_parts = validated_path.parts[java_dir_index + 1:-1]
                        package_name = ".".join(package_parts)
                    else:
                        package_name = ""

                except ValueError:
                    # Fallback if 'java' or 'kotlin' is not in the path
                    package_name = ""

            # Generate content based on class type
            if class_type == "activity":
                content = self.kotlin_generator.generate_complete_activity(
                    package_name, class_name, features
                )
            elif class_type == "viewmodel":
                content = self.kotlin_generator.generate_complete_viewmodel(
                    package_name, class_name, features
                )
            elif class_type == "repository":
                content = self.kotlin_generator.generate_complete_repository(
                    package_name, class_name, features
                )
            elif class_type == "fragment":
                content = self.kotlin_generator.generate_complete_fragment(
                    package_name, class_name, features
                )
            elif class_type == "data_class":
                content = self.kotlin_generator.generate_complete_data_class(
                    package_name, class_name, features
                )
            elif class_type == "use_case":
                content = self.kotlin_generator.generate_complete_use_case(
                    package_name, class_name, features
                )
            elif class_type == "service":
                content = self.kotlin_generator.generate_complete_service(
                    package_name, class_name, features
                )
            elif class_type == "adapter":
                content = self.kotlin_generator.generate_complete_adapter(
                    package_name, class_name, features
                )
            elif class_type == "interface":
                content = self.kotlin_generator.generate_complete_interface(
                    package_name, class_name, features
                )
            elif class_type == "class":
                content = self.kotlin_generator.generate_complete_class(
                    package_name, class_name, features
                )
            else:
                return {"success": False, "error": f"Unsupported class type: {class_type}"}

            # Create directory if it doesn't exist
            validated_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            validated_path.write_text(content, encoding="utf-8")

            # Generate related files if requested
            related_files = []
            if generate_related:
                related_files = self.kotlin_generator.generate_related_files(
                    class_type, package_name, class_name, validated_path.parent, features
                )

            # Log audit event
            self.security_manager.log_audit_event(
                "create_kotlin_file",
                str(validated_path),
                f"class_type:{class_type}, features:{features}",
            )

            return {
                "success": True,
                "file_path": str(validated_path),
                "class_name": class_name,
                "class_type": class_type,
                "features": features,
                "related_files": related_files,
                "message": f"Successfully created {class_type} file: {validated_path.name}",
            }

        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Failed to create Kotlin file: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _generate_code_with_ai(self, arguments: dict) -> dict:
        """Generate sophisticated code using AI integration."""
        try:
            # Create request object from arguments
            request = CodeGenerationRequest(
                description=arguments["description"],
                code_type=CodeType(arguments["code_type"]),
                package_name=arguments["package_name"],
                class_name=arguments["class_name"],
                framework=arguments.get("framework", "android"),
                features=arguments.get("features"),
                compliance_requirements=arguments.get("compliance_requirements"),
            )

            # Set project context for better generation
            if self.project_path:
                project_context = {
                    "project_path": str(self.project_path),
                    "architecture": "MVVM",  # Could be detected from project
                    "dependencies": [
                        "hilt",
                        "compose",
                        "retrofit",
                        "room",
                    ],  # Could be read from gradle
                    "min_sdk": 24,
                    "target_sdk": 34,
                }
                self.llm_integration.set_project_context(project_context)

            # Generate code using AI
            result = await self.llm_integration.generate_code_with_ai(request)

            return result

        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _analyze_code_with_ai(self, arguments: dict) -> dict:
        """Analyze code using AI integration."""
        try:
            file_path = arguments["file_path"]
            analysis_type = arguments.get("analysis_type", "all")
            specific_concerns = arguments.get("specific_concerns", [])

            # Validate and read file
            full_path = self.project_path / file_path
            if not full_path.exists():
                return {"content": [{"type": "text", "text": f"Error: File not found: {file_path}"}], "isError": True}

            code_content = full_path.read_text(encoding="utf-8")

            # Create analysis request
            request = AnalysisRequest(
                file_path=file_path,
                analysis_type=analysis_type,
                code_content=code_content,
                specific_concerns=specific_concerns,
            )

            # Perform AI analysis
            result = await self.llm_integration.analyze_code_with_ai(request)

            return result

        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _enhance_existing_code(self, arguments: dict) -> dict:
        """Enhance existing code using AI integration."""
        try:
            file_path = arguments["file_path"]
            enhancement_type = arguments["enhancement_type"]
            specific_requirements = arguments.get("specific_requirements", "")

            # Validate and read existing file
            full_path = self.project_path / file_path
            if not full_path.exists():
                return {"content": [{"type": "text", "text": f"Error: File not found: {file_path}"}], "isError": True}

            existing_code = full_path.read_text(encoding="utf-8")

            # Create enhancement prompt
            enhancement_description = f"""
            Enhance the existing Kotlin code with the following requirements:

            Enhancement Type: {enhancement_type}
            Specific Requirements: {specific_requirements}

            Existing Code:
            ```kotlin
            {existing_code}
            ```

            Please provide enhanced version that:
            1. Maintains all existing functionality
            2. Adds the requested enhancements
            3. Uses modern Kotlin/Android patterns
            4. Includes proper error handling
            5. Follows best practices
            """

            # Use AI generation to enhance the code
            request = CodeGenerationRequest(
                description=enhancement_description,
                code_type=CodeType.CUSTOM,
                package_name="enhanced",  # Will be extracted from existing code
                class_name="Enhanced",  # Will be extracted from existing code
                framework="android",
            )

            result = await self.llm_integration.generate_code_with_ai(request)

            # Add enhancement-specific metadata
            if result.get("success"):
                result["enhancement_type"] = enhancement_type
                result["original_file"] = file_path
                result["specific_requirements"] = specific_requirements

            return result

        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    # Additional Tool Methods for Feature Parity
    async def _create_layout_file(self, arguments: dict) -> dict:
        """Create XML layout file using AI-enhanced generation."""
        try:
            layout_name = arguments["layout_name"]
            layout_type = arguments["layout_type"]
            features = arguments.get("features", [])

            # Generate sophisticated layout using AI
            layout_description = f"""
            Create a modern Android XML layout file for {layout_type} with the following specifications:
            Layout Name: {layout_name}
            Layout Type: {layout_type}
            Features: {', '.join(features)}

            Requirements:
            1. Use ConstraintLayout as root for optimal performance
            2. Include Material 3 design components
            3. Support both light and dark themes
            4. Include proper accessibility attributes
            5. Use proper naming conventions
            6. Include comments for maintainability
            """

            request = CodeGenerationRequest(
                description=layout_description,
                code_type=CodeType.CUSTOM,
                package_name="layout",
                class_name=layout_name,
                framework="android",
                features=features,
            )

            result = await self.llm_integration.generate_code_with_ai(request)

            if result.get("success"):
                # Write layout file
                if self.project_path:
                    layout_path = (
                        self.project_path / "app/src/main/res/layout" / f"{layout_name}.xml"
                    )
                    layout_path.parent.mkdir(parents=True, exist_ok=True)
                    layout_path.write_text(result.get("content", ""), encoding="utf-8")

                    result["file_path"] = str(layout_path)
                    result["layout_type"] = layout_type

            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _format_code(self, arguments: dict) -> dict:
        """Format Kotlin code using ktlint."""
        try:
            file_path = arguments["file_path"]
            full_path = self.project_path / file_path

            if not full_path.exists():
                return {"content": [{"type": "text", "text": f"Error: File not found: {file_path}"}], "isError": True}

            # Use gradle tools for formatting
            if self.gradle_tools:
                result = await self.gradle_tools.format_code(file_path)
            else:
                result = {"content": [{"type": "text", "text": "Error: Gradle tools not initialized"}], "isError": True}

            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _run_lint(self, arguments: dict) -> dict:
        """Run Android lint checks."""
        try:
            fix_issues = arguments.get("fix_issues", False)

            if self.gradle_tools:
                result = await self.gradle_tools.run_lint(fix_issues)
            else:
                result = {"content": [{"type": "text", "text": "Error: Gradle tools not initialized"}], "isError": True}

            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _generate_docs(self, arguments: dict) -> dict:
        """Generate project documentation."""
        try:
            doc_type = arguments.get("doc_type", "all")

            # Use AI to generate documentation
            doc_description = f"""
            Generate comprehensive project documentation of type: {doc_type}

            Create documentation covering:
            1. API documentation with examples
            2. Architecture overview
            3. Setup and installation guide
            4. Usage examples
            5. Contributing guidelines
            6. Troubleshooting guide
            """

            request = CodeGenerationRequest(
                description=doc_description,
                code_type=CodeType.CUSTOM,
                package_name="docs",
                class_name="ProjectDocumentation",
                framework="android",
            )

            result = await self.llm_integration.generate_code_with_ai(request)

            if result.get("success") and self.project_path:
                # Save documentation
                docs_path = self.project_path / "docs" / f"{doc_type}_documentation.md"
                docs_path.parent.mkdir(parents=True, exist_ok=True)
                docs_path.write_text(result.get("content", ""), encoding="utf-8")
                result["documentation_path"] = str(docs_path)

            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _create_compose_component(self, arguments: dict) -> dict:
        """Create Jetpack Compose component using AI."""
        try:
            component_name = arguments["component_name"]
            package_name = arguments["package_name"]
            component_type = arguments["component_type"]
            features = arguments.get("features", [])

            compose_description = f"""
            Create a sophisticated Jetpack Compose {component_type} component with the following specifications:
            Component Name: {component_name}
            Component Type: {component_type}
            Package: {package_name}
            Features: {', '.join(features)}

            Requirements:
            1. Use modern Compose patterns and state management
            2. Include proper state hoisting
            3. Support Material 3 theming
            4. Include accessibility support
            5. Use proper preview annotations
            6. Include comprehensive documentation
            7. Follow Compose best practices
            """

            request = CodeGenerationRequest(
                description=compose_description,
                code_type=CodeType.CUSTOM,
                package_name=package_name,
                class_name=component_name,
                framework="compose",
                features=features + ["compose", "material3"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)

            if result.get("success"):
                # Save compose file
                if self.project_path:
                    compose_path = (
                        self.project_path
                        / f"app/src/main/java/{package_name.replace('.', '/')}/{component_name}.kt"
                    )
                    compose_path.parent.mkdir(parents=True, exist_ok=True)
                    compose_path.write_text(result.get("content", ""), encoding="utf-8")

                    result["file_path"] = str(compose_path)
                    result["component_type"] = component_type

            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}],"isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}],"isError": True}

    async def _create_custom_view(self, arguments: dict) -> dict:
        """Create custom Android View using AI."""
        try:
            view_name = arguments["view_name"]
            package_name = arguments["package_name"]
            view_type = arguments["view_type"]

            view_description = f"""
            Create a sophisticated custom Android View with the following specifications:
            View Name: {view_name}
            View Type: {view_type}
            Package: {package_name}

            Requirements:
            1. Extend appropriate View class based on type
            2. Implement proper constructors
            3. Override necessary drawing/measurement methods
            4. Include custom attributes support
            5. Handle touch events appropriately
            6. Support accessibility
            7. Include proper documentation
            """

            request = CodeGenerationRequest(
                description=view_description,
                code_type=CodeType.CUSTOM,
                package_name=package_name,
                class_name=view_name,
                framework="android",
                features=["custom_view"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)

            if result.get("success"):
                # Save view file
                if self.project_path:
                    view_path = (
                        self.project_path
                        / f"app/src/main/java/{package_name.replace('.', '/')}/{view_name}.kt"
                    )
                    view_path.parent.mkdir(parents=True, exist_ok=True)
                    view_path.write_text(result.get("content", ""), encoding="utf-8")

                    result["file_path"] = str(view_path)
                    result["view_type"] = view_type

            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
                return {"content": [{"type": "text", "text": "Error: Operation failed: {str(e)}"}],"isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
                return {"content": [{"type": "text", "text": "Error: Unexpected error: {str(e)}"}],"isError": True}

    async def _setup_mvvm_architecture(self, arguments: dict) -> dict:
        """Set up complete MVVM architecture using AI."""
        try:
            feature_name = arguments["feature_name"]
            package_base = arguments["package_base"]
            include_testing = arguments.get("include_testing", True)

            mvvm_description = f"""
            Create a complete MVVM architecture setup for feature: {feature_name}
            Base Package: {package_base}
            Include Testing: {include_testing}

            Generate the following components:
            1. ViewModel with proper state management
            2. Repository with data source abstraction
            3. Use Cases for business logic
            4. Model/Data classes
            5. UI State classes
            6. Navigation setup if needed
            7. Unit tests if requested

            Use modern Android patterns including:
            - Hilt dependency injection
            - Coroutines and Flow
            - State management with StateFlow
            - Proper error handling
            """

            request = CodeGenerationRequest(
                description=mvvm_description,
                code_type=CodeType.CUSTOM,
                package_name=package_base,
                class_name=f"{feature_name}Architecture",
                framework="android",
                features=["mvvm", "hilt", "coroutines", "stateflow"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)

            if result.get("success"):
                # Create architecture files
                arch_files = []
                if self.project_path:
                    base_path = (
                        self.project_path
                        / f"app/src/main/java/{package_base.replace('.', '/')}/{feature_name.lower()}"
                    )
                    base_path.mkdir(parents=True, exist_ok=True)

                    # This would typically create multiple files
                    arch_files.append(str(base_path / f"{feature_name}ViewModel.kt"))
                    arch_files.append(str(base_path / f"{feature_name}Repository.kt"))
                    arch_files.append(str(base_path / f"{feature_name}UseCase.kt"))

                result["architecture_files"] = arch_files
                result["feature_name"] = feature_name

            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _setup_dependency_injection(self, arguments: dict) -> dict:
        """Set up dependency injection using AI."""
        try:
            injection_type = arguments.get("injection_type", "hilt")
            modules = arguments.get("modules", ["app", "network", "database"])

            di_description = f"""
            Set up {injection_type} dependency injection with the following modules:
            Modules: {', '.join(modules)}

            Create:
            1. Application class with DI setup
            2. Module classes for each specified module
            3. Component interfaces if needed
            4. Qualifier annotations
            5. Provider methods for dependencies
            6. Proper scoping annotations

            Follow best practices for {injection_type}
            """

            request = CodeGenerationRequest(
                description=di_description,
                code_type=CodeType.CUSTOM,
                package_name="di",
                class_name="DependencyInjection",
                framework="android",
                features=["hilt", "dependency_injection"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _setup_room_database(self, arguments: dict) -> dict:
        """Set up Room database using AI."""
        try:
            database_name = arguments["database_name"]
            entities = arguments.get("entities", [])
            version = arguments.get("version", 1)

            room_description = f"""
            Set up Room database with the following specifications:
            Database Name: {database_name}
            Entities: {', '.join(entities)}
            Version: {version}

            Create:
            1. Entity classes with proper annotations
            2. DAO interfaces with CRUD operations
            3. Database class with Room configuration
            4. Type converters if needed
            5. Migration strategies
            6. Repository integration

            Use modern Room patterns and coroutines
            """

            request = CodeGenerationRequest(
                description=room_description,
                code_type=CodeType.CUSTOM,
                package_name="database",
                class_name=database_name,
                framework="android",
                features=["room", "coroutines", "hilt"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _setup_retrofit_api(self, arguments: dict) -> dict:
        """Set up Retrofit API client using AI."""
        try:
            api_name = arguments["api_name"]
            base_url = arguments["base_url"]
            endpoints = arguments.get("endpoints", [])

            retrofit_description = f"""
            Set up Retrofit API client with the following specifications:
            API Name: {api_name}
            Base URL: {base_url}
            Endpoints: {', '.join(endpoints)}

            Create:
            1. API service interface with endpoints
            2. Data models for requests/responses
            3. Retrofit configuration with interceptors
            4. Error handling
            5. Authentication handling
            6. Repository integration

            Use modern networking patterns with coroutines
            """

            request = CodeGenerationRequest(
                description=retrofit_description,
                code_type=CodeType.CUSTOM,
                package_name="network",
                class_name=api_name,
                framework="android",
                features=["retrofit", "coroutines", "hilt"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _encrypt_sensitive_data(self, arguments: dict) -> dict:
        """Implement data encryption using AI."""
        try:
            encryption_type = arguments.get("encryption_type", "aes")
            data_types = arguments.get("data_types", ["user_data", "credentials"])

            encryption_description = f"""
            Implement {encryption_type} encryption for sensitive data:
            Data Types: {', '.join(data_types)}

            Create:
            1. Encryption utility classes
            2. Key management with Android Keystore
            3. Secure data storage methods
            4. Decryption utilities
            5. Error handling for crypto operations
            6. Proper key rotation strategies

            Follow Android security best practices
            """

            request = CodeGenerationRequest(
                description=encryption_description,
                code_type=CodeType.UTILITY_CLASS,
                package_name="security",
                class_name="DataEncryption",
                framework="android",
                features=["security", "encryption"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _implement_gdpr_compliance(self, arguments: dict) -> dict:
        """Implement GDPR compliance features using AI."""
        try:
            compliance_level = arguments.get("compliance_level", "basic")

            gdpr_description = f"""
            Implement GDPR compliance features at {compliance_level} level:

            Create:
            1. Consent management system
            2. Data processing logging
            3. User rights implementation (access, deletion, portability)
            4. Privacy policy integration
            5. Data retention policies
            6. Audit trail mechanisms

            Ensure full GDPR compliance for data handling
            """

            request = CodeGenerationRequest(
                description=gdpr_description,
                code_type=CodeType.UTILITY_CLASS,
                package_name="compliance",
                class_name="GDPRCompliance",
                framework="android",
                features=["gdpr", "privacy", "compliance"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _implement_hipaa_compliance(self, arguments: dict) -> dict:
        """Implement HIPAA compliance features using AI."""
        try:
            security_level = arguments.get("security_level", "standard")

            hipaa_description = f"""
            Implement HIPAA compliance features at {security_level} security level:

            Create:
            1. PHI (Protected Health Information) handling
            2. Access control and authentication
            3. Audit logging for all PHI access
            4. Encryption for data at rest and in transit
            5. User access management
            6. Breach detection and reporting

            Ensure full HIPAA compliance for healthcare data
            """

            request = CodeGenerationRequest(
                description=hipaa_description,
                code_type=CodeType.UTILITY_CLASS,
                package_name="compliance",
                class_name="HIPAACompliance",
                framework="android",
                features=["hipaa", "healthcare", "security"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _setup_secure_storage(self, arguments: dict) -> dict:
        """Set up secure storage using AI."""
        try:
            storage_type = arguments.get("storage_type", "preferences")

            storage_description = f"""
            Set up secure {storage_type} storage:

            Create:
            1. Encrypted storage wrapper
            2. Android Keystore integration
            3. Biometric authentication support
            4. Secure backup strategies
            5. Key rotation mechanisms
            6. Storage integrity validation

            Use Android security best practices
            """

            request = CodeGenerationRequest(
                description=storage_description,
                code_type=CodeType.UTILITY_CLASS,
                package_name="storage",
                class_name="SecureStorage",
                framework="android",
                features=["security", "encryption", "biometric"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

            request = CodeGenerationRequest(
                description=storage_description,
                code_type=CodeType.UTILITY_CLASS,
                package_name="storage",
                class_name="SecureStorage",
                framework="android",
                features=["security", "encryption", "biometric"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"success": False, "error": f"Operation failed: {str(e)}"}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    async def _query_llm(self, arguments: dict) -> dict:
        """Direct query to the LLM."""
        try:
            query = arguments["query"]
            context = arguments.get("context", "")

            # Use the AI integration to handle the query
            description = f"User Query: {query}\nContext: {context}"

            request = CodeGenerationRequest(
                description=description,
                code_type=CodeType.CUSTOM,
                package_name="query",
                class_name="LLMResponse",
                framework="android",
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _manage_dependencies(self, arguments: dict) -> dict:
        """Manage project dependencies."""
        try:
            action = arguments["action"]
            dependency = arguments.get("dependency", "")

            # Use AI to manage dependencies
            dep_description = f"""
            Perform dependency management action: {action}
            Dependency: {dependency}

            Actions to perform:
            1. Analyze current dependencies
            2. {action.title()} the specified dependency
            3. Check for conflicts
            4. Update gradle files as needed
            5. Provide recommendations
            """

            request = CodeGenerationRequest(
                description=dep_description,
                code_type=CodeType.CUSTOM,
                package_name="dependency",
                class_name="DependencyManager",
                framework="android",
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError": True}

    async def _manage_project_files(self, arguments: dict) -> dict:
        """Manage project files."""
        try:
            operation = arguments["operation"]

            # Use AI to manage files
            file_description = f"""
            Perform file management operation: {operation}

            Operations to perform:
            1. Analyze project file structure
            2. {operation.title()} files as needed
            3. Organize by best practices
            4. Clean up unused files
            5. Create file organization report
            """

            request = CodeGenerationRequest(
                description=file_description,
                code_type=CodeType.CUSTOM,
                package_name="files",
                class_name="FileManager",
                framework="android",
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"success": False, "error": f"Operation failed: {str(e)}"}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    async def _setup_cloud_sync(self, arguments: dict) -> dict:
        """Set up cloud synchronization using AI."""
        try:
            provider = arguments["provider"]
            sync_types = arguments.get("sync_types", ["user_data"])

            cloud_description = f"""
            Set up cloud synchronization with {provider}:
            Sync Types: {', '.join(sync_types)}

            Create:
            1. Cloud service integration
            2. Sync manager for data types
            3. Conflict resolution strategies
            4. Offline support
            5. Progress tracking
            6. Error handling and retry logic

            Use best practices for {provider} integration
            """

            request = CodeGenerationRequest(
                description=cloud_description,
                code_type=CodeType.SERVICE,
                package_name="cloud",
                class_name=f"{provider.title()}SyncService",
                framework="android",
                features=["cloud", "sync", provider.lower()],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError":True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError":True}

    async def _setup_external_api(self, arguments: dict) -> dict:
        """Set up external API integration using AI."""
        try:
            api_name = arguments["api_name"]
            auth_type = arguments["auth_type"]

            api_description = f"""
            Set up external API integration for {api_name}:
            Authentication: {auth_type}

            Create:
            1. API client with {auth_type} authentication
            2. Request/response models
            3. Error handling and retry logic
            4. Rate limiting support
            5. Caching strategies
            6. Testing utilities

            Follow REST API best practices
            """

            request = CodeGenerationRequest(
                description=api_description,
                code_type=CodeType.SERVICE,
                package_name="api",
                class_name=f"{api_name}ApiService",
                framework="android",
                features=["retrofit", "authentication", auth_type.lower()],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"success": False, "error": f"Operation failed: {str(e)}"}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    async def _call_external_api(self, arguments: dict) -> dict:
        """Make external API calls."""
        try:
            api_name = arguments["api_name"]
            endpoint = arguments["endpoint"]
            method = arguments.get("method", "GET")
            parameters = arguments.get("parameters", {})

            # This would typically use the configured API services
            # For now, return a simulated response
            result = {
                "success": True,
                "api_name": api_name,
                "endpoint": endpoint,
                "method": method,
                "response": f"Simulated {method} response from {endpoint}",
                "parameters": parameters,
            }

            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Operation failed: {str(e)}"}], "isError":True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError":True}

    async def _generate_unit_tests(self, arguments: dict) -> dict:
        """Generate unit tests using AI."""
        try:
            target_class = arguments["target_class"]
            test_framework = arguments.get("test_framework", "junit")

            # Read the target class file
            if not self.project_path:
                return {"success": False, "error": "No project path set"}

            class_file = (
                self.project_path / f"app/src/main/java/{target_class.replace('.', '/')}.kt"
            )
            if not class_file.exists():
                return {"success": False, "error": f"Target class file not found: {target_class}"}

            class_content = class_file.read_text(encoding="utf-8")

            test_description = f"""
            Generate comprehensive unit tests for the following Kotlin class using {test_framework}:

            Target Class: {target_class}
            Test Framework: {test_framework}

            Class Content:
            ```kotlin
            {class_content}
            ```

            Create:
            1. Test class with proper setup/teardown
            2. Tests for all public methods
            3. Edge case testing
            4. Mock dependencies where needed
            5. Parameterized tests where appropriate
            6. Assertion coverage for all paths

            Use modern testing patterns and best practices
            """

            request = CodeGenerationRequest(
                description=test_description,
                code_type=CodeType.TEST,
                package_name="test",
                class_name=f"{target_class.split('.')[-1]}Test",
                framework="android",
                features=["testing", test_framework, "mockk"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)

            if result.get("success"):
                # Save test file
                if self.project_path:
                    test_path = (
                        self.project_path
                        / f"app/src/test/java/{target_class.replace('.', '/')}Test.kt"
                    )
                    test_path.parent.mkdir(parents=True, exist_ok=True)
                    test_path.write_text(result.get("content", ""), encoding="utf-8")

                    result["test_file_path"] = str(test_path)
                    result["target_class"] = target_class

            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: Test generation failed: {str(e)}"}],"isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError":True}

    async def _setup_ui_testing(self, arguments: dict) -> dict:
        """Set up UI testing framework using AI."""
        try:
            testing_type = arguments.get("testing_type", "both")

            ui_test_description = f"""
            Set up UI testing framework for {testing_type}:

            Create:
            1. UI test configuration and setup
            2. Page Object Model classes
            3. Test utilities and helpers
            4. Compose test rules if needed
            5. Espresso test setup if needed
            6. Screenshot testing setup
            7. Test data management

            Use modern UI testing patterns
            """

            request = CodeGenerationRequest(
                description=ui_test_description,
                code_type=CodeType.TEST,
                package_name="uitest",
                class_name="UITestSetup",
                framework="android",
                features=["ui_testing", "espresso", "compose_testing"],
            )

            result = await self.llm_integration.generate_code_with_ai(request)
            return result
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
            return {"content": [{"type": "text", "text": f"Error: UI testing setup failed: {str(e)}"}],"isError": True}
        except (RuntimeError, AttributeError, TypeError) as e:
            return {"content": [{"type": "text", "text": f"Error: Unexpected error: {str(e)}"}], "isError":True}

    async def handle_ci_tool(self, arguments: dict) -> dict:
        """Handle CI tool calls."""
        sub_command = arguments.get("sub_command")
        repo = arguments.get("repo")

        if not sub_command or not repo:
            return {"success": False, "error": "sub_command and repo are required."}

        if sub_command == "list_workflows":
            return await self._list_workflows(repo)
        elif sub_command == "get_workflow_runs":
            workflow_id = arguments.get("workflow_id")
            if not workflow_id:
                return {"success": False, "error": "workflow_id is required for get_workflow_runs operation."}
            
            runs_result = await self._get_workflow_runs(repo, workflow_id)
            
            # Check for failed runs and trigger debug analysis
            if runs_result.get("success") and runs_result.get("workflow_runs"): # Check for 'workflow_runs' key
                for run in runs_result["workflow_runs"].get("workflow_runs", []): # Access 'workflow_runs' list safely
                    if run.get("status") == "completed" and run.get("conclusion") == "failure":
                        # Trigger debug analysis for failed run
                        logs_result = await self._get_run_logs(repo, run["id"])
                        if logs_result.get("success"):
                            debug_arguments = {
                                "stack_trace": f"Workflow run {run["id"]} failed. Logs:\n{logs_result["logs"]}"
                            }
                            debug_analysis = await self.handle_debug_tool(debug_arguments)
                            run["debug_analysis"] = debug_analysis # Add debug analysis to the run info
            return runs_result
        elif sub_command == "rerun_workflow":
            run_id = arguments.get("run_id")
            if not run_id:
                return {"success": False, "error": "run_id is required for rerun_workflow operation."}
            return await self._rerun_workflow(repo, run_id)
        elif sub_command == "get_run_logs":
            run_id = arguments.get("run_id")
            if not run_id:
                return {"success": False, "error": "run_id is required for get_run_logs operation."}
            return await self._get_run_logs(repo, run_id)
        elif sub_command == "get_test_results":
            run_id = arguments.get("run_id")
            if not run_id:
                return {"success": False, "error": "run_id is required for get_test_results operation."}
            return await self._get_test_results(repo, run_id)
        else:
            return {"success": False, "error": f"Unknown sub_command: {sub_command}"}

    async def _list_workflows(self, repo: str) -> dict:
        """List workflows in a GitHub repository."""
        url = f"https://api.github.com/repos/{repo}/actions/workflows"
        headers = await self._get_github_api_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return {"success": True, "workflows": response.json()}
        else:
            return {"success": False, "error": f"Failed to list workflows: {response.text}"}

    async def _get_workflow_runs(self, repo: str, workflow_id: str) -> dict:
        """Get workflow runs for a specific workflow."""
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/runs"
        headers = await self._get_github_api_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return {"success": True, "workflow_runs": response.json()}
        else:
            return {"success": False, "error": f"Failed to get workflow runs: {response.text}"}

    async def _rerun_workflow(self, repo: str, run_id: int) -> dict:
        """Rerun a specific workflow run."""
        url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/rerun"
        headers = await self._get_github_api_headers()

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)

        if response.status_code == 201:
            return {"success": True, "message": "Workflow rerun successfully."}
        else:
            return {"success": False, "error": f"Failed to rerun workflow: {response.text}"}

    async def _get_run_logs(self, repo: str, run_id: int) -> dict:
        """Get logs for a specific workflow run."""
        url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
        headers = await self._get_github_api_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return {"success": True, "logs": response.text}
        else:
            return {"success": False, "error": f"Failed to get run logs: {response.text}"}

    async def _get_test_results(self, repo: str, run_id: int) -> dict:
        """Get test results for a specific workflow run."""
        # This is a simplified placeholder. Real test result extraction is complex.
        # It would involve downloading artifacts, parsing JUnit XML, etc.
        # For now, we'll return a dummy response.
        return {"success": True, "test_results": f"Dummy test results for run_id: {run_id}"}

    async def handle_design_tool(self, arguments: dict) -> dict:
        """Handle design tool calls."""
        figma_file_url = arguments.get("figma_file_url")
        figma_token = arguments.get("figma_token")

        if sub_command == "get_file_metadata":
            url = f"https://api.figma.com/v1/files/{file_key}"
            headers = {"X-Figma-Token": figma_token}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return {"success": True, "figma_file": response.json()}
            else:
                return {"success": False, "error": f"Failed to fetch Figma file: {response.text}"}
        elif sub_command == "extract_tokens":
            token_type = arguments.get("token_type")
            output_file = arguments.get("output_file")
            if not token_type or not output_file:
                return {"success": False, "error": "token_type and output_file are required for extract_tokens operation."}
            return await self._extract_design_tokens(file_key, figma_token, token_type, output_file)
        else:

    async def _extract_design_tokens(self, file_key: str, figma_token: str, token_type: str, output_file: str) -> dict:
        """Extract design tokens (colors, fonts) from a Figma file and generate Kotlin code."""
        url = f"https://api.figma.com/v1/files/{file_key}"
        headers = {"X-Figma-Token": figma_token}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return {"success": False, "error": f"Failed to fetch Figma file: {response.text}"}

        figma_data = response.json()
        kotlin_code_lines = []
        
        # Add necessary imports
        kotlin_code_lines.append("package com.example.app.ui.theme\n") # Assuming a default package
        kotlin_code_lines.append("import androidx.compose.ui.graphics.Color\n")
        kotlin_code_lines.append("import androidx.compose.ui.text.TextStyle\n")
        kotlin_code_lines.append("import androidx.compose.ui.text.font.FontFamily\n")
        kotlin_code_lines.append("import androidx.compose.ui.unit.sp\n\n")

        # Extract Colors
        if token_type == "colors" or token_type == "all":
            kotlin_code_lines.append("// Colors\n")
            for style_id, style in figma_data.get("styles", {}).items():
                if style.get("styleType") == "FILL":
                    # Find the node that uses this style to get its color
                    # This is a simplified approach; a full implementation would traverse the document
                    # to find paint styles and their associated colors.
                    # For now, we'll assume colors are defined as top-level styles or within components.
                    # Figma API doesn't directly expose color values in styles endpoint,
                    # so we need to find a node that uses it. This is a placeholder.
                    # A more robust solution would involve traversing the document tree.
                    pass # Placeholder for actual color extraction logic

            # A more direct way to get colors from document if they are defined as fills on nodes
            # This requires traversing the document. For simplicity, let's assume some common colors
            # are defined in the document's `document.sharedStyles` or similar.
            # This is a simplified example. Real Figma API parsing is complex.
            # We'll just add some placeholder colors for now.
            kotlin_code_lines.append("val Purple80 = Color(0xFFD0BCFF)\n")
            kotlin_code_lines.append("val PurpleGrey80 = Color(0xFFCCC2DC)\n")
            kotlin_code_lines.append("val Pink80 = Color(0xFFEFB8C8)\n\n")
            
            kotlin_code_lines.append("val Purple40 = Color(0xFF6650a4)\n")
            kotlin_code_lines.append("val PurpleGrey40 = Color(0xFF625b71)\n")
            kotlin_code_lines.append("val Pink40 = Color(0xFF7D5260)\n\n")


        # Extract Fonts/Text Styles
        if token_type == "fonts" or token_type == "all":
            kotlin_code_lines.append("// Typography\n")
            for style_id, style in figma_data.get("styles", {}).items():
                if style.get("styleType") == "TEXT":
                    name = style.get("name", "UnnamedTextStyle").replace("/", "_").replace(" ", "")
                    description = style.get("description", "")
                    
                    # Figma API text styles contain font details
                    font_family = style.get("fontFamily", "Default")
                    font_post_script_name = style.get("fontPostScriptName", "")
                    font_size = style.get("fontSize", 16)
                    font_weight = style.get("fontWeight", 400) # Figma's fontWeight is 100-900
                    line_height = style.get("lineHeightPx", font_size) # Use lineHeightPx for exact value
                    
                    # Map Figma font weight to Compose FontWeights (simplified)
                    compose_font_weight = "FontWeight.Normal"
                    if font_weight >= 700:
                        compose_font_weight = "FontWeight.Bold"
                    elif font_weight <= 300:
                        compose_font_weight = "FontWeight.Light"

                    # Generate TextStyle
                    kotlin_code_lines.append(f"val {name} = TextStyle(\
")
                    kotlin_code_lines.append(f"    fontFamily = FontFamily.Default, // Placeholder, map actual font families\n")
                    kotlin_code_lines.append(f"    fontWeight = {compose_font_weight},\n")
                    kotlin_code_lines.append(f"    fontSize = {font_size}.sp,\n")
                    kotlin_code_lines.append(f"    lineHeight = {line_height}.sp,\n")
                    kotlin_code_lines.append(")\n\n")

        # Write to file
        try:
            full_output_path = self.project_path / output_file
            full_output_path.parent.mkdir(parents=True, exist_ok=True)
            full_output_path.write_text("".join(kotlin_code_lines), encoding="utf-8")
            return {"success": True, "message": f"Successfully extracted tokens to {output_file}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to write output file: {e}"}
        """Handle tickets tool calls."""
        sub_command = arguments.get("sub_command")
        repo = arguments.get("repo")

        if not sub_command or not repo:
            return {"success": False, "error": "sub_command and repo are required."}

        if sub_command == "list":
            return await self._list_issues(repo)
        elif sub_command == "create":
            title = arguments.get("title")
            body = arguments.get("body")
            if not title:
                return {"success": False, "error": "title is required for create operation."}
            return await self._create_issue(repo, title, body)
        elif sub_command == "view":
            issue_number = arguments.get("issue_number")
            if not issue_number:
                return {"success": False, "error": "issue_number is required for view operation."}
            return await self._view_issue(repo, issue_number)
        elif sub_command == "comment":
            issue_number = arguments.get("issue_number")
            comment_body = arguments.get("comment_body")
            if not issue_number or not comment_body:
                return {"success": False, "error": "issue_number and comment_body are required for comment operation."}
            return await self._comment_issue(repo, issue_number, comment_body)
        elif sub_command == "assign":
            issue_number = arguments.get("issue_number")
            assignee = arguments.get("assignee")
            if not issue_number or not assignee:
                return {"success": False, "error": "issue_number and assignee are required for assign operation."}
            return await self._assign_issue(repo, issue_number, assignee)
        elif sub_command == "close":
            issue_number = arguments.get("issue_number")
            if not issue_number:
                return {"success": False, "error": "issue_number is required for close operation."}
            return await self._close_issue(repo, issue_number)
        else:
            return {"success": False, "error": f"Unknown sub_command: {sub_command}"}

    async def _get_github_api_headers(self) -> dict:
        """Get the headers for GitHub API requests."""
        # In a real application, the token would be stored securely.
        # For now, we'll use an environment variable.
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            # For the demo, we can proceed without a token, but the rate limit will be very low.
            return {"Accept": "application/vnd.github.v3+json"}
        return {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        }

    async def _list_issues(self, repo: str) -> dict:
        """List issues in a GitHub repository."""
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = await self._get_github_api_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return {"success": True, "issues": response.json()}
        else:
            return {"success": False, "error": f"Failed to list issues: {response.text}"}

    async def _create_issue(self, repo: str, title: str, body: str | None) -> dict:
        """Create an issue in a GitHub repository."""
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = await self._get_github_api_headers()
        data = {"title": title, "body": body}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)

        if response.status_code == 201:
            return {"success": True, "issue": response.json()}
        else:
            return {"success": False, "error": f"Failed to create issue: {response.text}"}

    async def _view_issue(self, repo: str, issue_number: int) -> dict:
        """View an issue in a GitHub repository."""
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
        headers = await self._get_github_api_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return {"success": True, "issue": response.json()}
        else:
            return {"success": False, "error": f"Failed to view issue: {response.text}"}

    async def _view_issue(self, repo: str, issue_number: int) -> dict:
        """View an issue in a GitHub repository."""
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
        headers = await self._get_github_api_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return {"success": True, "issue": response.json()}
        else:
            return {"success": False, "error": f"Failed to view issue: {response.text}"}

    async def _comment_issue(self, repo: str, issue_number: int, comment_body: str) -> dict:
        """Comment on a GitHub issue."""
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
        headers = await self._get_github_api_headers()
        data = {"body": comment_body}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)

        if response.status_code == 201:
            return {"success": True, "comment": response.json()}
        else:
            return {"success": False, "error": f"Failed to comment on issue: {response.text}"}

    async def _assign_issue(self, repo: str, issue_number: int, assignee: str) -> dict:
        """Assign a GitHub issue."""
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/assignees"
        headers = await self._get_github_api_headers()
        data = {"assignees": [assignee]}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)

        if response.status_code == 201:
            return {"success": True, "issue": response.json()}
        else:
            return {"success": False, "error": f"Failed to assign issue: {response.text}"}

    async def _close_issue(self, repo: str, issue_number: int) -> dict:
        """Close a GitHub issue."""
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
        headers = await self._get_github_api_headers()
        data = {"state": "closed"}

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, json=data)

        if response.status_code == 200:
            return {"success": True, "issue": response.json()}
        else:
            return {"success": False, "error": f"Failed to close issue: {response.text}"}

    async def handle_scaffold_tool(self, arguments: dict) -> dict:
        """Handle scaffold tool calls."""
        feature_name = arguments.get("feature_name")
        feature_description = arguments.get("feature_description")

        if not feature_name or not feature_description:
            return {"success": False, "error": "feature_name and feature_description are required."}

        # Get project architecture
        arch_details = await self.handle_project_analysis_tool({"analysis_type": "architecture"})
        if not arch_details.get("success"):
            return arch_details

        source_root = arch_details.get("source_root")
        base_package_name = arch_details.get("package_name")

        if not source_root or not base_package_name:
            return {"success": False, "error": "Could not determine project architecture."}

        # Step 1: Deconstruct the feature using the LLM
        prompt = f"""
        Based on the following feature description, generate a list of files to be created.
        The output should be a JSON array of objects, where each object has the following keys:
        - "file_path": The path to the file to be created, relative to the base package name (e.g., "login/LoginActivity.kt").
        - "class_type": The type of the class to be generated (e.g., "activity", "viewmodel", "repository", "layout").
        - "class_name": The name of the class.
        - "features": A list of features to be included in the generated code.

        Feature Name: {feature_name}
        Feature Description: {feature_description}
        Base Package Name: {base_package_name}
        """

        request = CodeGenerationRequest(
            description=prompt,
            code_type=CodeType.CUSTOM,
            package_name="scaffold",
            class_name="ScaffoldPlan",
            framework="android",
        )

        deconstruction_result = await self.llm_integration.generate_code_with_ai(request)

        if not deconstruction_result.get("success"):
            return deconstruction_result

        try:
            files_to_generate = json.loads(deconstruction_result["content"])
        except json.JSONDecodeError:
            return {"success": False, "error": "Failed to parse the scaffolding plan from the LLM."}

        # Step 2: Generate the files
        generated_files = []
        for file_info in files_to_generate:
            # Construct full path and package name
            relative_path = file_info["file_path"]
            full_path = f"{source_root}/{base_package_name.replace('.', '/')}/{relative_path}"
            package_name = f"{base_package_name}.{relative_path.rsplit('/', 1)[0].replace('/', '.')}"

            file_info["file_path"] = full_path
            file_info["package_name"] = package_name

            if file_info["class_type"] == "layout":
                result = await self._create_layout_file(file_info)
            else:
                result = await self._create_kotlin_file(file_info)

            if not result.get("success"):
                return result # Stop if any file generation fails

            generated_files.append(result)

        return {"success": True, "generated_files": generated_files}

    async def handle_debug_tool(self, arguments: dict) -> dict:
        """Handle debug tool calls."""
        stack_trace = arguments.get("stack_trace")

        if not stack_trace:
            return {"success": False, "error": "stack_trace is required."}

        prompt = f"""
        The following is a stack trace from an Android application.
        Please analyze the error, explain the likely cause in simple terms,
        and provide a code snippet that would fix the issue.

        Stack Trace:
        {stack_trace}
        """

        request = CodeGenerationRequest(
            description=prompt,
            code_type=CodeType.CUSTOM,
            package_name="debug",
            class_name="DebugAnalysis",
            framework="android",
        )

        result = await self.llm_integration.generate_code_with_ai(request)
        return result

    async def handle_git_tool(self, arguments: dict) -> dict:
        """Handle git tool calls."""
        sub_command = arguments.get("sub_command")

        if not sub_command:
            return {"success": False, "error": "sub_command is required."}

        if sub_command == "status":
            return await self._git_status()
        elif sub_command == "diff":
            return await self._git_diff()
        elif sub_command == "add":
            path = arguments.get("path")
            if not path:
                return {"success": False, "error": "path is required for add operation."}
            return await self._git_add(path)
        elif sub_command == "commit":
            message = arguments.get("message")
            if not message:
                return {"success": False, "error": "message is required for commit operation."}
            return await self._git_commit(message)
        elif sub_command == "log":
            return await self._git_log()
        elif sub_command == "branch":
            branch_name = arguments.get("branch_name")
            return await self._git_branch(branch_name)
        elif sub_command == "checkout":
            branch_name = arguments.get("branch_name")
            if not branch_name:
                return {"success": False, "error": "branch_name is required for checkout operation."}
            return await self._git_checkout(branch_name)
        elif sub_command == "stash":
            return await self._git_stash()
        elif sub_command == "cherry-pick":
            commit_hash = arguments.get("commit_hash")
            if not commit_hash:
                return {"success": False, "error": "commit_hash is required for cherry-pick operation."}
            return await self._git_cherry_pick(commit_hash)
        else:
            return {"success": False, "error": f"Unknown sub_command: {sub_command}"}

    async def _run_git_command(self, command: str) -> dict:
        """Run a git command and return the output."""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_path,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            return {"success": False, "error": stderr.decode().strip()}
        else:
            return {"success": True, "output": stdout.decode().strip()}

    async def _git_status(self) -> dict:
        """Get git status."""
        return await self._run_git_command("git status")

    async def _git_diff(self) -> dict:
        """Get git diff."""
        return await self._run_git_command("git diff")

    async def _git_add(self, path: str) -> dict:
        """Add a file to git."""
        # Sanitize path to prevent command injection
        validated_path = self.security_manager.validate_file_path(path, self.project_path)
        return await self._run_git_command(f"git add {validated_path}")

    async def _git_commit(self, message: str) -> dict:
        """Commit changes."""
        # For security, we should be careful with the message.
        # For now, we'll just pass it to the command.
        return await self._run_git_command(f"git commit -m '{message}'")

    async def _git_log(self) -> dict:
        """Get git log."""
        return await self._run_git_command("git log --oneline -n 10")

    async def _git_branch(self, branch_name: str | None) -> dict:
        """Create or list branches."""
        if branch_name:
            return await self._run_git_command(f"git branch {branch_name}")
        else:
            return await self._run_git_command("git branch")

    async def _git_checkout(self, branch_name: str) -> dict:
        """Checkout a branch."""
        return await self._run_git_command(f"git checkout {branch_name}")

    async def _git_stash(self) -> dict:
        """Stash changes."""
        return await self._run_git_command("git stash")

    async def _git_cherry_pick(self, commit_hash: str) -> dict:
        """Cherry-pick a commit."""
        return await self._run_git_command(f"git cherry-pick {commit_hash}")

    async def handle_file_system_tool(self, arguments: dict) -> dict:
        """Handle file system tool calls."""
        if sub_command == "read":
            path = arguments.get("path")
            if not path:
                return {"success": False, "error": "path is required for read operation."}
            validated_path = self.security_manager.validate_file_path(path, self.project_path)
            return await self._fs_read(validated_path)
        elif sub_command == "write":
            path = arguments.get("path")
            content = arguments.get("content")
            if not path or content is None:
                return {"success": False, "error": "path and content are required for write operation."}
            validated_path = self.security_manager.validate_file_path(path, self.project_path)
            return await self._fs_write(validated_path, content)
        elif sub_command == "list":
            path = arguments.get("path")
            if not path:
                return {"success": False, "error": "path is required for list operation."}
            validated_path = self.security_manager.validate_file_path(path, self.project_path)
            return await self._fs_list(validated_path)
        elif sub_command == "search":
            path = arguments.get("path")
            pattern = arguments.get("pattern")
            if not path or not pattern:
                return {"success": False, "error": "path and pattern are required for search operation."}
            validated_path = self.security_manager.validate_file_path(path, self.project_path)
            return await self._fs_search(validated_path, pattern)
        elif sub_command == "delete":
            path = arguments.get("path")
            if not path:
                return {"success": False, "error": "path is required for delete operation."}
            force = arguments.get("force", False)
            validated_path = self.security_manager.validate_file_path(path, self.project_path)
            return await self._fs_delete(validated_path, force)
        elif sub_command == "move":
            source_path_str = arguments.get("source_path")
            destination_path_str = arguments.get("destination_path")
            if not source_path_str or not destination_path_str:
                return {"success": False, "error": "source_path and destination_path are required for move operation."}
            
            try:
                validated_source_path = self.security_manager.validate_file_path(source_path_str, self.project_path)
                validated_destination_path = self.security_manager.validate_file_path(destination_path_str, self.project_path)
            except ValueError as e:
                return {"success": False, "error": str(e)}

            return await self._fs_move(validated_source_path, validated_destination_path)
        else:
            return {"success": False, "error": f"Unknown sub_command: {sub_command}"}

    async def _fs_read(self, path: Path) -> dict:
        """Read a file."""
        if not path.is_file():
            return {"success": False, "error": "Path is not a file."}
        try:
            content = path.read_text(encoding="utf-8")
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": f"Error reading file: {e}"}

    async def _fs_write(self, path: Path, content: str) -> dict:
        """Write to a file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            self.security_manager.log_audit_event("file_system.write", str(path))
            return {"success": True, "message": f"Successfully wrote to {path}"}
        except Exception as e:
            return {"success": False, "error": f"Error writing to file: {e}"}

    async def _fs_list(self, path: Path) -> dict:
        """List files in a directory."""
        if not path.is_dir():
            return {"success": False, "error": "Path is not a directory."}
        try:
            files = [f.name for f in path.iterdir()]
            return {"success": True, "files": files}
        except Exception as e:
            return {"success": False, "error": f"Error listing files: {e}"}

    async def _fs_search(self, path: Path, pattern: str) -> dict:
        """Search for files in a directory."""
        if not path.is_dir():
            return {"success": False, "error": "Path is not a directory."}
        try:
            files = [f.as_posix() for f in path.rglob(pattern)]
            return {"success": True, "files": files}
        except Exception as e:
            return {"success": False, "error": f"Error searching for files: {e}"}

    async def _fs_delete(self, path: Path, force: bool = False) -> dict:
        """Delete a file or directory."""
        if not path.exists():
            return {"success": False, "error": "Path does not exist."}
        try:
            if path.is_dir():
                if force:
                    shutil.rmtree(path)
                    self.security_manager.log_audit_event("file_system.delete", f"recursively deleted {path}")
                    return {"success": True, "message": f"Successfully recursively deleted directory {path}"}
                else:
                    if not any(path.iterdir()):
                        path.rmdir()
                        self.security_manager.log_audit_event("file_system.delete", str(path))
                        return {"success": True, "message": f"Successfully deleted empty directory {path}"}
                    else:
                        return {"success": False, "error": "Directory is not empty. Use force=True to delete recursively."}
            elif path.is_file():
                path.unlink()
                self.security_manager.log_audit_event("file_system.delete", str(path))
                return {"success": True, "message": f"Successfully deleted file {path}"}
            else:
                return {"success": False, "error": "Path is not a file or directory."}
        except Exception as e:
            return {"success": False, "error": f"Error deleting: {e}"}

    async def _fs_move(self, source_path: Path, destination_path: Path) -> dict:
        """Move or rename a file or directory."""
        if not source_path.exists():
            return {"success": False, "error": "Source path does not exist."}
        try:
            source_path.rename(destination_path)
            self.security_manager.log_audit_event("file_system.move", f"{source_path} -> {destination_path}")
            return {"success": True, "message": f"Successfully moved {source_path} to {destination_path}"}
        except Exception as e:
            return {"success": False, "error": f"Error moving file: {e}"}

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.security_manager:
            self.security_manager.close()


def create_server(name: str = "kotlin-android-mcp") -> KotlinMCPServer:
    """Create and configure the MCP server."""
    return KotlinMCPServer(name)


# Backward compatibility alias for tests
MCPServer = KotlinMCPServer


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(
        description="Kotlin MCP Server - Modular Android Development Tools"
    )
    parser.add_argument(
        "project_path", nargs="?", help="Path to the Android project root directory"
    )

    args = parser.parse_args()

    # Create server
    server = create_server()

    # Set project path if provided
    if args.project_path:
        project_path = Path(args.project_path)
        if not project_path.exists():
            # In an MCP server, it's generally better to return an error through the protocol
            # rather than exiting. However, if the project path is fundamental for server
            # operation, the client should ensure it's valid.
            # For now, we'll let the server continue without a valid project path,
            # and tools requiring it will report an error.
            pass

        server.set_project_path(str(project_path))
    else:
        pass # No project path provided, server will operate without project-specific tools.

    # The server is ready to accept MCP connections.
    # All communication should happen via JSON-RPC over stdin/stdout.
    # Do not print anything to stdout outside of JSON-RPC responses.

    # Start the MCP communication loop
    async def mcp_loop():
        while True:
            line = await asyncio.to_thread(sys.stdin.readline)
            if not line:
                break # EOF, client closed connection

            try:
                request = json.loads(line)
                method = request.get("method")
                params = request.get("params", {})
                request_id = request.get("id")

                response = {}
                if method == "initialize":
                    result = await server.handle_initialize(params)
                    response = {"jsonrpc": "2.0", "id": request_id, "result": result}
                elif method == "list_tools" or method == "tools/list":
                    result = await server.handle_list_tools()
                    response = {"jsonrpc": "2.0", "id": request_id, "result": result}
                elif method == "call_tool":
                    tool_name = params.get("name")
                    tool_args = params.get("arguments", {})
                    result = await server.handle_call_tool(tool_name, tool_args)
                    response = {"jsonrpc": "2.0", "id": request_id, "result": result}
                else:
                    # Handle unknown method
                    error_message = f"Unknown method: {method}"
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": error_message},
                    }

                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            except json.JSONDecodeError:
                error_message = "Invalid JSON received"
                sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": error_message}}) + "\n")
                sys.stdout.flush()
            except Exception as e:
                error_message = f"Server error: {str(e)}"
                sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32000, "message": error_message}}) + "\n")
                sys.stdout.flush()

    asyncio.run(mcp_loop())


if __name__ == "__main__":
    main()
