"""
Centralized Tool Registry for Kotlin MCP Server

Single source of truth for all exposed MCP tools.
Each tool must have a valid schema and working handler.
"""

from typing import Any, Dict, List

# Tool definitions with complete schemas
TOOL_REGISTRY: List[Dict[str, Any]] = [
    # Core Development Tools
    {
        "name": "refactorFunction",
        "description": "Refactor Kotlin functions with AST-aware transformations including rename, extract, inline, and parameter introduction.",
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
                "range": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "object",
                            "properties": {
                                "line": {"type": "integer"},
                                "column": {"type": "integer"},
                            },
                        },
                        "end": {
                            "type": "object",
                            "properties": {
                                "line": {"type": "integer"},
                                "column": {"type": "integer"},
                            },
                        },
                    },
                },
                "preview": {"type": "boolean", "default": False},
            },
        },
        "handler": "handle_refactor_function",
    },
    {
        "name": "applyCodeAction",
        "description": "Apply IDE code actions like quick fixes and suggestions",
        "inputSchema": {
            "type": "object",
            "required": ["filePath", "codeActionId"],
            "properties": {
                "filePath": {"type": "string", "minLength": 1},
                "codeActionId": {"type": "string", "minLength": 1},
                "preview": {"type": "boolean", "default": False},
            },
        },
        "handler": "handle_apply_code_action",
    },
    {
        "name": "optimizeImports",
        "description": "Optimize and organize Kotlin imports across files",
        "inputSchema": {
            "type": "object",
            "required": ["mode"],
            "properties": {
                "projectRoot": {"type": "string"},
                "mode": {"type": "string", "enum": ["file", "module", "project"]},
                "targets": {"type": "array", "items": {"type": "string"}},
                "preview": {"type": "boolean", "default": False},
            },
        },
        "handler": "handle_optimize_imports",
    },
    {
        "name": "formatCode",
        "description": "Format Kotlin code using ktlint or spotless with configurable style rules",
        "inputSchema": {
            "type": "object",
            "required": ["targets", "style"],
            "properties": {
                "targets": {"type": "array", "items": {"type": "string"}},
                "style": {"type": "string", "enum": ["ktlint", "spotless"]},
                "preview": {"type": "boolean", "default": False},
            },
        },
        "handler": "handle_format_code",
    },
    {
        "name": "analyzeCodeQuality",
        "description": "Analyze code quality with security, performance, complexity, or comprehensive rules",
        "inputSchema": {
            "type": "object",
            "required": ["scope", "ruleset"],
            "properties": {
                "scope": {"type": "string", "enum": ["file", "module", "project"]},
                "targets": {"type": "array", "items": {"type": "string"}},
                "ruleset": {
                    "type": "string",
                    "enum": ["security", "performance", "complexity", "all"],
                },
                "maxFindings": {"type": "integer", "minimum": 1},
            },
        },
        "handler": "handle_analyze_code_quality",
    },
    {
        "name": "generateTests",
        "description": "Generate comprehensive unit tests with chosen framework and coverage goals",
        "inputSchema": {
            "type": "object",
            "required": ["filePath", "classOrFunction", "framework"],
            "properties": {
                "filePath": {"type": "string", "minLength": 1},
                "classOrFunction": {"type": "string", "minLength": 1},
                "framework": {"type": "string", "enum": ["JUnit5", "MockK"]},
                "coverageGoal": {"type": "number", "minimum": 0, "maximum": 100},
            },
        },
        "handler": "handle_generate_tests",
    },
    {
        "name": "applyPatch",
        "description": "Apply unified diff patches to files with conflict resolution",
        "inputSchema": {
            "type": "object",
            "required": ["patch"],
            "properties": {
                "patch": {"type": "string", "minLength": 1},
                "allowCreate": {"type": "boolean", "default": True},
            },
        },
        "handler": "handle_apply_patch",
    },
    # Android Development Tools
    {
        "name": "androidGenerateComposeUI",
        "description": "Generate complete Jetpack Compose UI components with state management",
        "inputSchema": {
            "type": "object",
            "required": ["screenName"],
            "properties": {
                "screenName": {"type": "string", "minLength": 1},
                "stateModel": {"type": "object"},
                "navigation": {"type": "boolean", "default": True},
                "theme": {"type": "string"},
            },
        },
        "handler": "handle_android_generate_compose_ui",
    },
    {
        "name": "androidSetupArchitecture",
        "description": "Set up complete MVVM or Clean Architecture with dependency injection",
        "inputSchema": {
            "type": "object",
            "required": ["pattern", "di"],
            "properties": {
                "pattern": {"type": "string", "enum": ["MVVM", "Clean"]},
                "di": {"type": "string", "enum": ["Hilt", "Koin"]},
                "modules": {"type": "array", "items": {"type": "string"}},
            },
        },
        "handler": "handle_android_setup_architecture",
    },
    {
        "name": "androidSetupDataLayer",
        "description": "Configure Room database with entities, DAOs, and migrations",
        "inputSchema": {
            "type": "object",
            "required": ["db", "entities"],
            "properties": {
                "db": {"type": "string", "enum": ["Room"]},
                "entities": {"type": "array", "items": {"type": "object"}},
                "migrations": {"type": "boolean", "default": True},
                "encryption": {"type": "boolean", "default": False},
            },
        },
        "handler": "handle_android_setup_data_layer",
    },
    {
        "name": "androidSetupNetwork",
        "description": "Configure networking with Retrofit, GraphQL, or WebSocket support",
        "inputSchema": {
            "type": "object",
            "required": ["style", "endpoints"],
            "properties": {
                "style": {"type": "string", "enum": ["Retrofit", "GraphQL", "WebSocket"]},
                "endpoints": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "method": {"type": "string"},
                            "description": {"type": "string"},
                        },
                    },
                },
                "auth": {"type": "string", "enum": ["None", "ApiKey", "OAuth2", "JWT"]},
            },
        },
        "handler": "handle_android_setup_network",
    },
    # Security and Compliance Tools
    {
        "name": "securityEncryptData",
        "description": "Encrypt sensitive data using AES-256-GCM with proper key derivation",
        "inputSchema": {
            "type": "object",
            "required": ["dataRef"],
            "properties": {
                "dataRef": {"type": "string", "minLength": 1},
                "algo": {"type": "string", "enum": ["AES-256-GCM"], "default": "AES-256-GCM"},
                "kdf": {"type": "string", "enum": ["PBKDF2"], "default": "PBKDF2"},
                "context": {"type": "object"},
            },
        },
        "handler": "handle_security_encrypt_data",
    },
    {
        "name": "securityDecryptData",
        "description": "Decrypt data with audit logging",
        "inputSchema": {
            "type": "object",
            "required": ["dataRef"],
            "properties": {
                "dataRef": {"type": "string", "minLength": 1},
                "context": {"type": "object"},
            },
        },
        "handler": "handle_security_decrypt_data",
    },
    {
        "name": "privacyRequestErasure",
        "description": "Handle GDPR data erasure requests with comprehensive scope coverage",
        "inputSchema": {
            "type": "object",
            "required": ["subjectId", "scopes"],
            "properties": {
                "subjectId": {"type": "string", "minLength": 1},
                "scopes": {"type": "array", "items": {"type": "string"}},
            },
        },
        "handler": "handle_privacy_request_erasure",
    },
    {
        "name": "privacyExportData",
        "description": "Export user data in GDPR-compliant formats",
        "inputSchema": {
            "type": "object",
            "required": ["subjectId", "format"],
            "properties": {
                "subjectId": {"type": "string", "minLength": 1},
                "format": {"type": "string", "enum": ["JSON", "CSV", "Parquet"]},
                "fields": {"type": "array", "items": {"type": "string"}},
            },
        },
        "handler": "handle_privacy_export_data",
    },
    {
        "name": "securityAuditTrail",
        "description": "Query and analyze security audit logs with filtering",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filters": {"type": "object"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 1000},
            },
        },
        "handler": "handle_security_audit_trail",
    },
    # File Management Tools
    {
        "name": "fileBackup",
        "description": "Create encrypted backups of project files with versioning",
        "inputSchema": {
            "type": "object",
            "required": ["targets", "dest"],
            "properties": {
                "targets": {"type": "array", "items": {"type": "string"}},
                "dest": {"type": "string", "minLength": 1},
                "encrypt": {"type": "boolean", "default": False},
                "tag": {"type": "string"},
            },
        },
        "handler": "handle_file_backup",
    },
    {
        "name": "fileRestore",
        "description": "Restore files from backup with integrity verification",
        "inputSchema": {
            "type": "object",
            "required": ["manifestRef", "destRoot"],
            "properties": {
                "manifestRef": {"type": "string", "minLength": 1},
                "destRoot": {"type": "string", "minLength": 1},
                "decrypt": {"type": "boolean", "default": True},
            },
        },
        "handler": "handle_file_restore",
    },
    {
        "name": "fileSyncWatch",
        "description": "Set up real-time file synchronization with change monitoring",
        "inputSchema": {
            "type": "object",
            "required": ["paths", "dest"],
            "properties": {
                "paths": {"type": "array", "items": {"type": "string"}},
                "dest": {"type": "string", "minLength": 1},
                "includeGlobs": {"type": "array", "items": {"type": "string"}},
                "excludeGlobs": {"type": "array", "items": {"type": "string"}},
            },
        },
        "handler": "handle_file_sync_watch",
    },
    {
        "name": "fileClassifySensitivity",
        "description": "Classify files by sensitivity level using pattern matching and ML",
        "inputSchema": {
            "type": "object",
            "required": ["targets", "policies"],
            "properties": {
                "targets": {"type": "array", "items": {"type": "string"}},
                "policies": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["PII", "PHI", "Secrets"]},
                },
            },
        },
        "handler": "handle_file_classify_sensitivity",
    },
    {
        "name": "securityHardening",
        "description": "Apply security hardening measures with role-based access control",
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
                },
                "user_id": {"type": "string"},
                "role": {"type": "string", "enum": ["admin", "developer", "readonly", "guest"]},
                "permission": {"type": "string"},
                "resource": {"type": "string"},
            },
        },
        "handler": "handle_security_hardening",
    },
    # Git Integration Tools
    {
        "name": "gitStatus",
        "description": "Get comprehensive git repository status with change analysis",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repository": {"type": "string"},
                "detailed": {"type": "boolean", "default": False},
            },
        },
        "handler": "handle_git_status",
    },
    {
        "name": "gitSmartCommit",
        "description": "Create intelligent commits with auto-generated messages and staging",
        "inputSchema": {
            "type": "object",
            "required": ["files"],
            "properties": {
                "files": {"type": "array", "items": {"type": "string"}},
                "message": {"type": "string"},
                "autoGenerate": {"type": "boolean", "default": True},
            },
        },
        "handler": "handle_git_smart_commit",
    },
    {
        "name": "gitCreateFeatureBranch",
        "description": "Create feature branches with proper naming and setup",
        "inputSchema": {
            "type": "object",
            "required": ["featureName"],
            "properties": {
                "featureName": {"type": "string", "minLength": 1},
                "baseBranch": {"type": "string", "default": "main"},
                "setupTracking": {"type": "boolean", "default": True},
            },
        },
        "handler": "handle_git_create_feature_branch",
    },
    {
        "name": "gitMergeWithResolution",
        "description": "Merge branches with intelligent conflict resolution",
        "inputSchema": {
            "type": "object",
            "required": ["sourceBranch", "targetBranch"],
            "properties": {
                "sourceBranch": {"type": "string", "minLength": 1},
                "targetBranch": {"type": "string", "minLength": 1},
                "strategy": {"type": "string", "enum": ["auto", "manual", "ours", "theirs"]},
                "deleteSource": {"type": "boolean", "default": False},
            },
        },
        "handler": "handle_git_merge_with_resolution",
    },
    # API and External Integration Tools
    {
        "name": "apiCallSecure",
        "description": "Make secure API calls with authentication, retries, and monitoring",
        "inputSchema": {
            "type": "object",
            "required": ["apiName", "endpoint"],
            "properties": {
                "apiName": {"type": "string", "minLength": 1},
                "endpoint": {"type": "string", "minLength": 1},
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "default": "GET",
                },
                "data": {"type": "object"},
                "headers": {"type": "object"},
                "auth": {"type": "object"},
            },
        },
        "handler": "handle_api_call_secure",
    },
    {
        "name": "apiMonitorMetrics",
        "description": "Get API monitoring metrics with windowed counters",
        "inputSchema": {
            "type": "object",
            "properties": {
                "apiName": {"type": "string"},
                "windowMinutes": {"type": "integer", "default": 60},
            },
        },
        "handler": "handle_api_monitor_metrics",
    },
    {
        "name": "apiValidateCompliance",
        "description": "Validate API compliance with GDPR/HIPAA rules and provide remediations",
        "inputSchema": {
            "type": "object",
            "required": ["apiName"],
            "properties": {
                "apiName": {"type": "string", "minLength": 1},
                "complianceType": {"type": "string", "enum": ["gdpr", "hipaa"], "default": "gdpr"},
            },
        },
        "handler": "handle_api_validate_compliance",
    },
    # Project Management Tools
    {
        "name": "projectSearch",
        "description": "Advanced project-wide search with pattern matching and filtering",
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "minLength": 1},
                "fileTypes": {"type": "array", "items": {"type": "string"}},
                "caseSensitive": {"type": "boolean", "default": False},
                "regex": {"type": "boolean", "default": False},
            },
        },
        "handler": "handle_project_search",
    },
    {
        "name": "todoListFromCode",
        "description": "Extract and organize task comments from codebase with prioritization",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paths": {"type": "array", "items": {"type": "string"}},
                "priority": {"type": "string", "enum": ["all", "high", "medium", "low"]},
            },
        },
        "handler": "handle_todo_list_from_code",
    },
    {
        "name": "readmeGenerateOrUpdate",
        "description": "Generate or update README with project analysis and documentation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["markdown", "rst", "txt"],
                    "default": "markdown",
                },
                "sections": {"type": "array", "items": {"type": "string"}},
                "autoGenerate": {"type": "boolean", "default": True},
            },
        },
        "handler": "handle_readme_generate_or_update",
    },
    {
        "name": "changelogSummarize",
        "description": "Generate changelog summaries from git history and commit analysis",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fromTag": {"type": "string"},
                "toTag": {"type": "string"},
                "format": {
                    "type": "string",
                    "enum": ["markdown", "json", "text"],
                    "default": "markdown",
                },
            },
        },
        "handler": "handle_changelog_summarize",
    },
    # Build and Test Tools
    {
        "name": "buildAndTest",
        "description": "Run Gradle/Maven build and return failing tests with artifacts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "buildTool": {
                    "type": "string",
                    "enum": ["auto", "gradle", "maven"],
                    "default": "auto",
                },
                "skipTests": {"type": "boolean", "default": False},
            },
        },
        "handler": "handle_build_and_test",
    },
    {
        "name": "dependencyAudit",
        "description": "Audit project dependencies for security vulnerabilities and license compliance",
        "inputSchema": {
            "type": "object",
            "properties": {
                "checkSecurity": {"type": "boolean", "default": True},
                "checkLicenses": {"type": "boolean", "default": True},
                "checkOutdated": {"type": "boolean", "default": True},
            },
        },
        "handler": "handle_dependency_audit",
    },
]


def get_tool_by_name(name: str) -> Dict[str, Any] | None:
    """Get a tool definition by name"""
    for tool in TOOL_REGISTRY:
        if tool["name"] == name:
            return tool
    return None


def get_all_tool_names() -> List[str]:
    """Get list of all registered tool names"""
    return [tool["name"] for tool in TOOL_REGISTRY]


def validate_registry() -> List[str]:
    """Validate the registry for common issues"""
    errors = []
    names = set()

    for tool in TOOL_REGISTRY:
        # Check required fields
        if "name" not in tool:
            errors.append("Tool missing 'name' field")
            continue

        name = tool["name"]

        # Check for duplicates
        if name in names:
            errors.append(f"Duplicate tool name: {name}")
        names.add(name)

        # Check required fields
        required_fields = ["description", "inputSchema", "handler"]
        for field in required_fields:
            if field not in tool:
                errors.append(f"Tool '{name}' missing field: {field}")

        # Validate schema structure
        schema = tool.get("inputSchema", {})
        if not isinstance(schema, dict):
            errors.append(f"Tool '{name}' has invalid inputSchema")
        elif schema.get("type") != "object":
            errors.append(f"Tool '{name}' inputSchema should be type 'object'")

    return errors
