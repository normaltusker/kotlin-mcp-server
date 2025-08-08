#!/usr/bin/env python3
"""
Enhanced Kotlin Android MCP Server for Complex App Development
Supports advanced UI development, architecture patterns, and modern Android features
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# Import the base server
from simple_mcp_server import MCPServer

class EnhancedAndroidMCPServer(MCPServer):
    """Enhanced MCP Server with advanced Android development capabilities"""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    async def handle_list_tools(self) -> dict:
        """Enhanced tools list with complex development capabilities"""
        base_tools = await super().handle_list_tools()
        
        enhanced_tools = [
            # UI Development Tools
            {
                "name": "create_compose_component",
                "description": "Create Jetpack Compose UI components",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path for the Compose file"},
                        "component_name": {"type": "string", "description": "Name of the Compose component"},
                        "component_type": {"type": "string", "enum": ["screen", "component", "dialog", "bottom_sheet"], "default": "component"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "uses_state": {"type": "boolean", "description": "Include state management", "default": False},
                        "uses_navigation": {"type": "boolean", "description": "Include navigation", "default": False}
                    },
                    "required": ["file_path", "component_name", "package_name"]
                }
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
                        "view_type": {"type": "string", "enum": ["view", "viewgroup", "compound"], "default": "view"},
                        "has_attributes": {"type": "boolean", "description": "Include custom attributes", "default": False}
                    },
                    "required": ["file_path", "view_name", "package_name"]
                }
            },
            
            # Architecture Tools
            {
                "name": "setup_mvvm_architecture",
                "description": "Set up MVVM architecture pattern with ViewModel and Repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "feature_name": {"type": "string", "description": "Name of the feature/module"},
                        "package_name": {"type": "string", "description": "Base package name"},
                        "include_repository": {"type": "boolean", "description": "Include Repository pattern", "default": True},
                        "include_use_cases": {"type": "boolean", "description": "Include Use Cases (Clean Architecture)", "default": False},
                        "data_source": {"type": "string", "enum": ["network", "database", "both"], "default": "network"}
                    },
                    "required": ["feature_name", "package_name"]
                }
            },
            {
                "name": "setup_dependency_injection",
                "description": "Set up Hilt dependency injection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "module_name": {"type": "string", "description": "Name of the DI module"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "injection_type": {"type": "string", "enum": ["network", "database", "repository", "use_case"], "default": "network"}
                    },
                    "required": ["module_name", "package_name"]
                }
            },
            
            # Database Tools
            {
                "name": "setup_room_database",
                "description": "Set up Room database with entities and DAOs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database_name": {"type": "string", "description": "Name of the database"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "entities": {"type": "array", "items": {"type": "string"}, "description": "List of entity names"},
                        "include_migration": {"type": "boolean", "description": "Include migration setup", "default": False}
                    },
                    "required": ["database_name", "package_name", "entities"]
                }
            },
            
            # Networking Tools
            {
                "name": "setup_retrofit_api",
                "description": "Set up Retrofit API client with endpoints",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "api_name": {"type": "string", "description": "Name of the API service"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "base_url": {"type": "string", "description": "API base URL"},
                        "endpoints": {"type": "array", "items": {"type": "object"}, "description": "API endpoints configuration"},
                        "include_interceptors": {"type": "boolean", "description": "Include logging/auth interceptors", "default": True}
                    },
                    "required": ["api_name", "package_name", "base_url"]
                }
            },
            
            # Advanced Layout Tools
            {
                "name": "create_complex_layout",
                "description": "Create complex layouts with RecyclerView, ViewPager, etc.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "layout_name": {"type": "string", "description": "Layout file name"},
                        "layout_complexity": {"type": "string", "enum": ["recyclerview", "viewpager", "coordinator", "motion"], "default": "recyclerview"},
                        "include_adapter": {"type": "boolean", "description": "Generate adapter code", "default": True},
                        "item_layout": {"type": "string", "description": "Item layout name for lists"}
                    },
                    "required": ["layout_name", "layout_complexity"]
                }
            },
            
            # Testing Tools
            {
                "name": "generate_test_suite",
                "description": "Generate comprehensive test suites",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "class_to_test": {"type": "string", "description": "Class to generate tests for"},
                        "test_type": {"type": "string", "enum": ["unit", "integration", "ui"], "default": "unit"},
                        "include_mockito": {"type": "boolean", "description": "Include Mockito mocks", "default": True},
                        "test_coverage": {"type": "string", "enum": ["basic", "comprehensive"], "default": "basic"}
                    },
                    "required": ["class_to_test"]
                }
            },
            
            # Build Configuration Tools
            {
                "name": "configure_build_variants",
                "description": "Configure build variants and flavors",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "variants": {"type": "array", "items": {"type": "string"}, "description": "Build variant names"},
                        "flavors": {"type": "array", "items": {"type": "string"}, "description": "Product flavor names"},
                        "configuration_type": {"type": "string", "enum": ["development", "staging", "production"], "default": "development"}
                    },
                    "required": ["variants"]
                }
            },
            
            # Modern Android Development Tools
            {
                "name": "setup_navigation_component",
                "description": "Set up Android Navigation Component with destinations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_name": {"type": "string", "description": "Navigation graph name"},
                        "destinations": {"type": "array", "items": {"type": "string"}, "description": "List of destination fragments/activities"},
                        "use_safe_args": {"type": "boolean", "description": "Enable Safe Args plugin", "default": True},
                        "deep_links": {"type": "array", "items": {"type": "string"}, "description": "Deep link patterns"}
                    },
                    "required": ["graph_name", "destinations"]
                }
            },
            {
                "name": "create_work_manager_worker",
                "description": "Create WorkManager worker for background tasks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "worker_name": {"type": "string", "description": "Name of the worker"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "work_type": {"type": "string", "enum": ["one_time", "periodic", "chained"], "default": "one_time"},
                        "constraints": {"type": "array", "items": {"type": "string"}, "description": "Work constraints (network, battery, etc.)"}
                    },
                    "required": ["worker_name", "package_name"]
                }
            },
            {
                "name": "setup_coroutines_flow",
                "description": "Set up Kotlin Coroutines and Flow for async operations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string", "description": "Class name for coroutines implementation"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "flow_type": {"type": "string", "enum": ["state_flow", "shared_flow", "flow"], "default": "state_flow"},
                        "use_viewmodel_scope": {"type": "boolean", "description": "Use viewModelScope", "default": True}
                    },
                    "required": ["class_name", "package_name"]
                }
            },
            {
                "name": "create_firebase_integration",
                "description": "Set up Firebase services integration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "services": {"type": "array", "items": {"type": "string"}, "description": "Firebase services (auth, firestore, analytics, etc.)"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "include_crashlytics": {"type": "boolean", "description": "Include Crashlytics", "default": True}
                    },
                    "required": ["services", "package_name"]
                }
            },
            {
                "name": "setup_data_store",
                "description": "Set up Jetpack DataStore for modern data persistence",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "store_name": {"type": "string", "description": "DataStore name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "store_type": {"type": "string", "enum": ["preferences", "proto"], "default": "preferences"},
                        "keys": {"type": "array", "items": {"type": "string"}, "description": "Data keys to store"}
                    },
                    "required": ["store_name", "package_name"]
                }
            },
            {
                "name": "create_permission_handler",
                "description": "Create runtime permission handling with modern patterns",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "permissions": {"type": "array", "items": {"type": "string"}, "description": "Permissions to handle"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "use_accompanist": {"type": "boolean", "description": "Use Accompanist permissions", "default": True}
                    },
                    "required": ["permissions", "package_name"]
                }
            },
            {
                "name": "setup_biometric_auth",
                "description": "Set up biometric authentication",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "auth_class_name": {"type": "string", "description": "Authentication class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "fallback_to_pin": {"type": "boolean", "description": "Allow PIN fallback", "default": True}
                    },
                    "required": ["auth_class_name", "package_name"]
                }
            },
            {
                "name": "create_notification_system",
                "description": "Create modern notification system with channels",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "notification_class": {"type": "string", "description": "Notification manager class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "channels": {"type": "array", "items": {"type": "string"}, "description": "Notification channel names"},
                        "support_android_13": {"type": "boolean", "description": "Support Android 13+ notification permissions", "default": True}
                    },
                    "required": ["notification_class", "package_name", "channels"]
                }
            },
            {
                "name": "setup_camera_integration",
                "description": "Set up CameraX integration for camera features",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "camera_class": {"type": "string", "description": "Camera handler class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "features": {"type": "array", "items": {"type": "string"}, "description": "Camera features (capture, video, analysis)"},
                        "use_compose": {"type": "boolean", "description": "Create Compose camera UI", "default": True}
                    },
                    "required": ["camera_class", "package_name", "features"]
                }
            },
            {
                "name": "create_media_player",
                "description": "Create media player with ExoPlayer integration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "player_class": {"type": "string", "description": "Media player class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "media_types": {"type": "array", "items": {"type": "string"}, "description": "Supported media types"},
                        "include_ui_controls": {"type": "boolean", "description": "Include player UI controls", "default": True}
                    },
                    "required": ["player_class", "package_name"]
                }
            },
            {
                "name": "setup_security_crypto",
                "description": "Set up Android Security Crypto for data encryption",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "crypto_class": {"type": "string", "description": "Crypto handler class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "encryption_type": {"type": "string", "enum": ["file", "shared_prefs", "custom"], "default": "shared_prefs"}
                    },
                    "required": ["crypto_class", "package_name"]
                }
            },
            {
                "name": "create_accessibility_features",
                "description": "Create accessibility features and content descriptions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "screen_name": {"type": "string", "description": "Screen to make accessible"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "accessibility_services": {"type": "array", "items": {"type": "string"}, "description": "Accessibility services to implement"}
                    },
                    "required": ["screen_name", "package_name"]
                }
            },
            {
                "name": "setup_in_app_updates",
                "description": "Set up Google Play In-App Updates",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "update_class": {"type": "string", "description": "Update manager class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "update_type": {"type": "string", "enum": ["flexible", "immediate", "both"], "default": "flexible"}
                    },
                    "required": ["update_class", "package_name"]
                }
            },
            {
                "name": "create_dynamic_features",
                "description": "Create dynamic feature modules",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "feature_name": {"type": "string", "description": "Dynamic feature module name"},
                        "delivery_type": {"type": "string", "enum": ["on_demand", "conditional", "fast_follow"], "default": "on_demand"},
                        "fusing": {"type": "boolean", "description": "Include in fused APK", "default": False}
                    },
                    "required": ["feature_name"]
                }
            },
            {
                "name": "setup_ml_kit_integration",
                "description": "Set up ML Kit for machine learning features",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ml_features": {"type": "array", "items": {"type": "string"}, "description": "ML features (text_recognition, face_detection, etc.)"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "use_bundled_models": {"type": "boolean", "description": "Use bundled models", "default": True}
                    },
                    "required": ["ml_features", "package_name"]
                }
            },
            
            # File Management Tools
            {
                "name": "create_file_manager",
                "description": "Create comprehensive file manager with storage access",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "manager_name": {"type": "string", "description": "File manager class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "storage_types": {"type": "array", "items": {"type": "string"}, "description": "Storage types (internal, external, scoped, media)"},
                        "file_operations": {"type": "array", "items": {"type": "string"}, "description": "Operations (read, write, delete, copy, move)"},
                        "use_storage_access_framework": {"type": "boolean", "description": "Use SAF for file picking", "default": True}
                    },
                    "required": ["manager_name", "package_name"]
                }
            },
            {
                "name": "setup_document_provider",
                "description": "Set up document provider for file sharing",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "provider_name": {"type": "string", "description": "Document provider name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "supported_formats": {"type": "array", "items": {"type": "string"}, "description": "Supported file formats"},
                        "enable_cloud_sync": {"type": "boolean", "description": "Enable cloud synchronization", "default": False}
                    },
                    "required": ["provider_name", "package_name"]
                }
            },
            {
                "name": "create_media_scanner",
                "description": "Create media scanner for indexing files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "scanner_name": {"type": "string", "description": "Media scanner class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "media_types": {"type": "array", "items": {"type": "string"}, "description": "Media types to scan (images, videos, audio, documents)"},
                        "include_metadata": {"type": "boolean", "description": "Extract metadata", "default": True}
                    },
                    "required": ["scanner_name", "package_name"]
                }
            },
            
            # External API Integration Tools
            {
                "name": "create_api_client",
                "description": "Create comprehensive API client with error handling and caching",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string", "description": "API client class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "base_url": {"type": "string", "description": "API base URL"},
                        "auth_type": {"type": "string", "enum": ["none", "api_key", "bearer_token", "oauth2", "basic"], "default": "none"},
                        "features": {"type": "array", "items": {"type": "string"}, "description": "Features (caching, retry, rate_limiting, offline_support)"},
                        "response_format": {"type": "string", "enum": ["json", "xml", "protobuf"], "default": "json"}
                    },
                    "required": ["client_name", "package_name", "base_url"]
                }
            },
            {
                "name": "setup_graphql_client",
                "description": "Set up GraphQL client with Apollo or custom implementation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string", "description": "GraphQL client name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "graphql_endpoint": {"type": "string", "description": "GraphQL endpoint URL"},
                        "use_apollo": {"type": "boolean", "description": "Use Apollo GraphQL", "default": True},
                        "enable_subscriptions": {"type": "boolean", "description": "Enable real-time subscriptions", "default": False},
                        "schema_file": {"type": "string", "description": "GraphQL schema file path"}
                    },
                    "required": ["client_name", "package_name", "graphql_endpoint"]
                }
            },
            {
                "name": "create_websocket_client",
                "description": "Create WebSocket client for real-time communication",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string", "description": "WebSocket client class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "websocket_url": {"type": "string", "description": "WebSocket server URL"},
                        "protocols": {"type": "array", "items": {"type": "string"}, "description": "WebSocket protocols"},
                        "features": {"type": "array", "items": {"type": "string"}, "description": "Features (auto_reconnect, heartbeat, compression)"},
                        "message_format": {"type": "string", "enum": ["json", "protobuf", "text"], "default": "json"}
                    },
                    "required": ["client_name", "package_name", "websocket_url"]
                }
            },
            {
                "name": "setup_third_party_apis",
                "description": "Set up integration with popular third-party APIs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "api_providers": {"type": "array", "items": {"type": "string"}, "description": "API providers (google_maps, stripe, twilio, aws, etc.)"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "include_sdk": {"type": "boolean", "description": "Include official SDKs where available", "default": True},
                        "custom_endpoints": {"type": "array", "items": {"type": "object"}, "description": "Custom API endpoints"}
                    },
                    "required": ["api_providers", "package_name"]
                }
            },
            {
                "name": "create_api_cache_manager",
                "description": "Create API response caching system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cache_name": {"type": "string", "description": "Cache manager class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "cache_strategies": {"type": "array", "items": {"type": "string"}, "description": "Cache strategies (memory, disk, hybrid)"},
                        "ttl_policies": {"type": "object", "description": "TTL policies for different data types"},
                        "max_cache_size": {"type": "string", "description": "Maximum cache size (e.g., '50MB')"}
                    },
                    "required": ["cache_name", "package_name"]
                }
            },
            {
                "name": "setup_offline_sync",
                "description": "Set up offline synchronization for API data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sync_manager_name": {"type": "string", "description": "Sync manager class name"},
                        "package_name": {"type": "string", "description": "Package name"},
                        "sync_strategies": {"type": "array", "items": {"type": "string"}, "description": "Sync strategies (optimistic, pessimistic, conflict_resolution)"},
                        "data_types": {"type": "array", "items": {"type": "string"}, "description": "Data types to sync"},
                        "conflict_resolution": {"type": "string", "enum": ["server_wins", "client_wins", "merge", "manual"], "default": "server_wins"}
                    },
                    "required": ["sync_manager_name", "package_name"]
                }
            }
        ]
        
        # Combine base tools with enhanced tools
        all_tools = base_tools["tools"] + enhanced_tools
        return {"tools": all_tools}
    
    async def handle_call_tool(self, name: str, arguments: dict) -> dict:
        """Handle enhanced tool calls"""
        
        # Handle base tools first
        base_tools = ["gradle_build", "run_tests", "create_kotlin_file", "create_layout_file", "analyze_project"]
        if name in base_tools:
            return await super().handle_call_tool(name, arguments)
        
        # Handle enhanced tools
        try:
            if name == "create_compose_component":
                return await self._create_compose_component(arguments)
            elif name == "create_custom_view":
                return await self._create_custom_view(arguments)
            elif name == "setup_mvvm_architecture":
                return await self._setup_mvvm_architecture(arguments)
            elif name == "setup_dependency_injection":
                return await self._setup_dependency_injection(arguments)
            elif name == "setup_room_database":
                return await self._setup_room_database(arguments)
            elif name == "setup_retrofit_api":
                return await self._setup_retrofit_api(arguments)
            elif name == "create_complex_layout":
                return await self._create_complex_layout(arguments)
            elif name == "generate_test_suite":
                return await self._generate_test_suite(arguments)
            elif name == "configure_build_variants":
                return await self._configure_build_variants(arguments)
            elif name == "setup_navigation_component":
                return await self._setup_navigation_component(arguments)
            elif name == "create_work_manager_worker":
                return await self._create_work_manager_worker(arguments)
            elif name == "setup_coroutines_flow":
                return await self._setup_coroutines_flow(arguments)
            elif name == "create_firebase_integration":
                return await self._create_firebase_integration(arguments)
            elif name == "setup_data_store":
                return await self._setup_data_store(arguments)
            elif name == "create_permission_handler":
                return await self._create_permission_handler(arguments)
            elif name == "setup_biometric_auth":
                return await self._setup_biometric_auth(arguments)
            elif name == "create_notification_system":
                return await self._create_notification_system(arguments)
            elif name == "setup_camera_integration":
                return await self._setup_camera_integration(arguments)
            elif name == "create_media_player":
                return await self._create_media_player(arguments)
            elif name == "setup_security_crypto":
                return await self._setup_security_crypto(arguments)
            elif name == "create_accessibility_features":
                return await self._create_accessibility_features(arguments)
            elif name == "setup_in_app_updates":
                return await self._setup_in_app_updates(arguments)
            elif name == "create_dynamic_features":
                return await self._create_dynamic_features(arguments)
            elif name == "setup_ml_kit_integration":
                return await self._setup_ml_kit_integration(arguments)
            elif name == "create_file_manager":
                return await self._create_file_manager(arguments)
            elif name == "setup_document_provider":
                return await self._setup_document_provider(arguments)
            elif name == "create_media_scanner":
                return await self._create_media_scanner(arguments)
            elif name == "create_api_client":
                return await self._create_api_client(arguments)
            elif name == "setup_graphql_client":
                return await self._setup_graphql_client(arguments)
            elif name == "create_websocket_client":
                return await self._create_websocket_client(arguments)
            elif name == "setup_third_party_apis":
                return await self._setup_third_party_apis(arguments)
            elif name == "create_api_cache_manager":
                return await self._create_api_cache_manager(arguments)
            elif name == "setup_offline_sync":
                return await self._setup_offline_sync(arguments)
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown enhanced tool: {name}"
                        }
                    ]
                }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing enhanced tool {name}: {str(e)}"
                    }
                ]
            }
    
    async def _create_compose_component(self, arguments: dict) -> dict:
        """Create Jetpack Compose UI component"""
        file_path = arguments["file_path"]
        component_name = arguments["component_name"]
        package_name = arguments["package_name"]
        component_type = arguments.get("component_type", "component")
        uses_state = arguments.get("uses_state", False)
        uses_navigation = arguments.get("uses_navigation", False)
        
        full_path = self.project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate Compose component based on type
        imports = f"package {package_name}\n\n"
        imports += "import androidx.compose.foundation.layout.*\n"
        imports += "import androidx.compose.material3.*\n"
        imports += "import androidx.compose.runtime.*\n"
        imports += "import androidx.compose.ui.Modifier\n"
        imports += "import androidx.compose.ui.tooling.preview.Preview\n"
        imports += "import androidx.compose.ui.unit.dp\n"
        
        if uses_state:
            imports += "import androidx.compose.runtime.getValue\n"
            imports += "import androidx.compose.runtime.setValue\n"
            imports += "import androidx.lifecycle.viewmodel.compose.viewModel\n"
        
        if uses_navigation:
            imports += "import androidx.navigation.NavController\n"
        
        state_code = ""
        if uses_state:
            state_code = """
    var state by remember { mutableStateOf("") }
"""
        
        nav_param = ", navController: NavController" if uses_navigation else ""
        
        templates = {
            "screen": f'''{imports}

@Composable
fun {component_name}Screen({nav_param.lstrip(", ")}) {{{state_code}
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {{
        Text(
            text = "{component_name} Screen",
            style = MaterialTheme.typography.headlineMedium
        )
        
        // TODO: Add your screen content here
    }}
}}

@Preview(showBackground = true)
@Composable
fun {component_name}ScreenPreview() {{
    MaterialTheme {{
        {component_name}Screen()
    }}
}}
''',
            "component": f'''{imports}

@Composable
fun {component_name}({nav_param.lstrip(", ")}) {{{state_code}
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {{
        Column(
            modifier = Modifier.padding(16.dp)
        ) {{
            Text(
                text = "{component_name}",
                style = MaterialTheme.typography.titleMedium
            )
            
            // TODO: Add your component content here
        }}
    }}
}}

@Preview(showBackground = true)
@Composable
fun {component_name}Preview() {{
    MaterialTheme {{
        {component_name}()
    }}
}}
'''
        }
        
        content = templates.get(component_type, templates["component"])
        
        try:
            full_path.write_text(content, encoding='utf-8')
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Created Jetpack Compose {component_type}: {file_path}"
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Failed to create Compose component: {str(e)}"
                    }
                ]
            }
    
    async def _setup_mvvm_architecture(self, arguments: dict) -> dict:
        """Set up MVVM architecture pattern"""
        feature_name = arguments["feature_name"]
        package_name = arguments["package_name"]
        include_repository = arguments.get("include_repository", True)
        include_use_cases = arguments.get("include_use_cases", False)
        data_source = arguments.get("data_source", "network")
        
        created_files = []
        
        # Create ViewModel
        viewmodel_path = self.project_path / f"app/src/main/java/{package_name.replace('.', '/')}/ui/{feature_name.lower()}/{feature_name}ViewModel.kt"
        viewmodel_path.parent.mkdir(parents=True, exist_ok=True)
        
        viewmodel_content = f'''package {package_name}.ui.{feature_name.lower()}

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class {feature_name}ViewModel @Inject constructor(
    private val repository: {feature_name}Repository
) : ViewModel() {{
    
    private val _uiState = MutableStateFlow({feature_name}UiState())
    val uiState: StateFlow<{feature_name}UiState> = _uiState.asStateFlow()
    
    fun load{feature_name}Data() {{
        viewModelScope.launch {{
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {{
                val data = repository.get{feature_name}Data()
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    data = data
                )
            }} catch (e: Exception) {{
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }}
        }}
    }}
}}

data class {feature_name}UiState(
    val isLoading: Boolean = false,
    val data: List<Any> = emptyList(),
    val error: String? = null
)
'''
        
        viewmodel_path.write_text(viewmodel_content, encoding='utf-8')
        created_files.append(f"ViewModel: {viewmodel_path.name}")
        
        # Create Repository if requested
        if include_repository:
            repo_path = self.project_path / f"app/src/main/java/{package_name.replace('.', '/')}/data/repository/{feature_name}Repository.kt"
            repo_path.parent.mkdir(parents=True, exist_ok=True)
            
            repo_content = f'''package {package_name}.data.repository

import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class {feature_name}Repository @Inject constructor(
    private val remoteDataSource: {feature_name}RemoteDataSource,
    private val localDataSource: {feature_name}LocalDataSource
) {{
    
    suspend fun get{feature_name}Data(): List<Any> {{
        return try {{
            val remoteData = remoteDataSource.fetch{feature_name}Data()
            localDataSource.cache{feature_name}Data(remoteData)
            remoteData
        }} catch (e: Exception) {{
            localDataSource.getCached{feature_name}Data()
        }}
    }}
}}
'''
            
            repo_path.write_text(repo_content, encoding='utf-8')
            created_files.append(f"Repository: {repo_path.name}")
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Created MVVM architecture for {feature_name}:\\n" + "\\n".join(created_files)
                }
            ]
        }
    
    # Modern Android Development Methods
    async def _setup_navigation_component(self, arguments: dict) -> dict:
        """Set up Android Navigation Component"""
        graph_name = arguments["graph_name"]
        destinations = arguments["destinations"]
        use_safe_args = arguments.get("use_safe_args", True)
        deep_links = arguments.get("deep_links", [])
        
        # Create navigation graph XML
        nav_path = self.project_path / f"app/src/main/res/navigation/{graph_name}.xml"
        nav_path.parent.mkdir(parents=True, exist_ok=True)
        
        nav_content = f'''<?xml version="1.0" encoding="utf-8"?>
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/{graph_name}"
    app:startDestination="@id/{destinations[0] if destinations else 'homeFragment'}">

'''
        
        for dest in destinations:
            nav_content += f'''    <fragment
        android:id="@+id/{dest}Fragment"
        android:name="com.example.{dest}Fragment"
        android:label="{dest}"
        tools:layout="@layout/fragment_{dest.lower()}" />
        
'''
        
        nav_content += "</navigation>"
        nav_path.write_text(nav_content, encoding='utf-8')
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Created Navigation Component graph: {graph_name}.xml with {len(destinations)} destinations"
                }
            ]
        }
    
    async def _create_work_manager_worker(self, arguments: dict) -> dict:
        """Create WorkManager worker"""
        worker_name = arguments["worker_name"]
        package_name = arguments["package_name"]
        work_type = arguments.get("work_type", "one_time")
        constraints = arguments.get("constraints", [])
        
        worker_path = self.project_path / f"app/src/main/java/{package_name.replace('.', '/')}/worker/{worker_name}Worker.kt"
        worker_path.parent.mkdir(parents=True, exist_ok=True)
        
        constraints_code = ""
        if constraints:
            constraints_code = f"""
        val constraints = Constraints.Builder()
            {chr(10).join([f'.setRequiredNetworkType(NetworkType.CONNECTED)' if 'network' in constraints else '',
                          f'.setRequiresBatteryNotLow(true)' if 'battery' in constraints else '',
                          f'.setRequiresCharging(true)' if 'charging' in constraints else ''])}
            .build()
"""
        
        worker_content = f'''package {package_name}.worker

import android.content.Context
import androidx.work.*
import androidx.hilt.work.HiltWorker
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import java.util.concurrent.TimeUnit

@HiltWorker
class {worker_name}Worker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted workerParams: WorkerParameters
) : CoroutineWorker(context, workerParams) {{

    override suspend fun doWork(): Result {{
        return try {{
            // TODO: Implement your background work here
            
            Result.success()
        }} catch (e: Exception) {{
            Result.failure()
        }}
    }}
    
    companion object {{
        fun start{work_type.replace('_', '').title()}Work(context: Context) {{{constraints_code}
            val workRequest = {
                'OneTimeWorkRequestBuilder' if work_type == 'one_time' else 
                'PeriodicWorkRequestBuilder' if work_type == 'periodic' else 
                'OneTimeWorkRequestBuilder'
            }<{worker_name}Worker>(){
                f'''
                .setConstraints(constraints)''' if constraints else ''
            }{
                f'''
                .setRepeatInterval(15, TimeUnit.MINUTES)''' if work_type == 'periodic' else ''
            }
                .build()
                
            WorkManager.getInstance(context).enqueue(workRequest)
        }}
    }}
}}
'''
        
        worker_path.write_text(worker_content, encoding='utf-8')
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Created WorkManager worker: {worker_name}Worker.kt"
                }
            ]
        }
    
    async def _setup_coroutines_flow(self, arguments: dict) -> dict:
        """Set up Kotlin Coroutines and Flow"""
        class_name = arguments["class_name"]
        package_name = arguments["package_name"]
        flow_type = arguments.get("flow_type", "state_flow")
        use_viewmodel_scope = arguments.get("use_viewmodel_scope", True)
        
        flow_path = self.project_path / f"app/src/main/java/{package_name.replace('.', '/')}/flow/{class_name}.kt"
        flow_path.parent.mkdir(parents=True, exist_ok=True)
        
        imports = f"package {package_name}.flow\n\n"
        imports += "import kotlinx.coroutines.*\n"
        imports += "import kotlinx.coroutines.flow.*\n"
        
        if use_viewmodel_scope:
            imports += "import androidx.lifecycle.ViewModel\n"
            imports += "import androidx.lifecycle.viewModelScope\n"
            imports += "import dagger.hilt.android.lifecycle.HiltViewModel\n"
            imports += "import javax.inject.Inject\n"
        
        flow_implementations = {
            "state_flow": f'''
    private val _dataFlow = MutableStateFlow<String>("")
    val dataFlow: StateFlow<String> = _dataFlow.asStateFlow()
    
    fun updateData(newData: String) {{
        _dataFlow.value = newData
    }}
''',
            "shared_flow": f'''
    private val _eventFlow = MutableSharedFlow<String>()
    val eventFlow: SharedFlow<String> = _eventFlow.asSharedFlow()
    
    fun emitEvent(event: String) {{
        viewModelScope.launch {{
            _eventFlow.emit(event)
        }}
    }}
''',
            "flow": f'''
    fun getDataFlow(): Flow<String> = flow {{
        // TODO: Implement your data emission logic
        emit("Sample data")
        delay(1000)
        emit("Updated data")
    }}
'''
        }
        
        class_declaration = f"@HiltViewModel\nclass {class_name} @Inject constructor() : ViewModel()" if use_viewmodel_scope else f"class {class_name}"
        
        flow_content = f'''{imports}

{class_declaration} {{
{flow_implementations.get(flow_type, flow_implementations["state_flow"])}
}}
'''
        
        flow_path.write_text(flow_content, encoding='utf-8')
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Created Coroutines/Flow implementation: {class_name}.kt with {flow_type}"
                }
            ]
        }
    
    async def _create_firebase_integration(self, arguments: dict) -> dict:
        """Create Firebase services integration"""
        services = arguments["services"]
        package_name = arguments["package_name"]
        include_crashlytics = arguments.get("include_crashlytics", True)
        
        firebase_path = self.project_path / f"app/src/main/java/{package_name.replace('.', '/')}/firebase/FirebaseManager.kt"
        firebase_path.parent.mkdir(parents=True, exist_ok=True)
        
        imports = f"package {package_name}.firebase\n\n"
        
        service_imports = {
            "auth": "import com.google.firebase.auth.FirebaseAuth\n",
            "firestore": "import com.google.firebase.firestore.FirebaseFirestore\n",
            "analytics": "import com.google.firebase.analytics.FirebaseAnalytics\n",
            "storage": "import com.google.firebase.storage.FirebaseStorage\n",
            "messaging": "import com.google.firebase.messaging.FirebaseMessaging\n"
        }
        
        for service in services:
            if service in service_imports:
                imports += service_imports[service]
        
        if include_crashlytics:
            imports += "import com.google.firebase.crashlytics.FirebaseCrashlytics\n"
        
        imports += "import javax.inject.Inject\nimport javax.inject.Singleton\n"
        
        service_properties = ""
        service_methods = ""
        
        for service in services:
            if service == "auth":
                service_properties += "    private val auth = FirebaseAuth.getInstance()\n"
                service_methods += '''
    fun signInWithEmail(email: String, password: String, callback: (Boolean) -> Unit) {
        auth.signInWithEmailAndPassword(email, password)
            .addOnCompleteListener { task ->
                callback(task.isSuccessful)
            }
    }
'''
            elif service == "firestore":
                service_properties += "    private val firestore = FirebaseFirestore.getInstance()\n"
                service_methods += '''
    fun saveToFirestore(collection: String, data: Map<String, Any>, callback: (Boolean) -> Unit) {
        firestore.collection(collection)
            .add(data)
            .addOnSuccessListener { callback(true) }
            .addOnFailureListener { callback(false) }
    }
'''
        
        firebase_content = f'''{imports}

@Singleton
class FirebaseManager @Inject constructor() {{
{service_properties}
{service_methods}
}}
'''
        
        firebase_path.write_text(firebase_content, encoding='utf-8')
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Created Firebase integration with services: {', '.join(services)}"
                }
            ]
        }
    
    async def _setup_data_store(self, arguments: dict) -> dict:
        """Set up Jetpack DataStore"""
        store_name = arguments["store_name"]
        package_name = arguments["package_name"]
        store_type = arguments.get("store_type", "preferences")
        keys = arguments.get("keys", [])
        
        datastore_path = self.project_path / f"app/src/main/java/{package_name.replace('.', '/')}/datastore/{store_name}DataStore.kt"
        datastore_path.parent.mkdir(parents=True, exist_ok=True)
        
        if store_type == "preferences":
            datastore_content = f'''package {package_name}.datastore

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.{store_name.lower()}DataStore: DataStore<Preferences> by preferencesDataStore(name = "{store_name.lower()}")

@Singleton
class {store_name}DataStore @Inject constructor(private val context: Context) {{
    
    companion object {{
        {chr(10).join([f'val {key.upper()}_KEY = stringPreferencesKey("{key}")' for key in keys])}
    }}
    
    {chr(10).join([f'''
    suspend fun save{key.title()}(value: String) {{
        context.{store_name.lower()}DataStore.edit {{ preferences ->
            preferences[{key.upper()}_KEY] = value
        }}
    }}
    
    fun get{key.title()}(): Flow<String> {{
        return context.{store_name.lower()}DataStore.data.map {{ preferences ->
            preferences[{key.upper()}_KEY] ?: ""
        }}
    }}''' for key in keys])}
}}
'''
        else:  # proto datastore
            datastore_content = f'''package {package_name}.datastore

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.dataStore
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

// TODO: Define your proto schema and implement serializer

@Singleton
class {store_name}DataStore @Inject constructor(private val context: Context) {{
    
    // TODO: Implement proto DataStore methods
    
}}
'''
        
        datastore_path.write_text(datastore_content, encoding='utf-8')
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Created {store_type} DataStore: {store_name}DataStore.kt"
                }
            ]
        }
    
    # Placeholder implementations for remaining methods
    async def _create_permission_handler(self, arguments: dict) -> dict:
        return {"content": [{"type": "text", "text": "Permission handler created (implementation needed)"}]}
    
    async def _setup_biometric_auth(self, arguments: dict) -> dict:
        return {"content": [{"type": "text", "text": "Biometric auth setup created (implementation needed)"}]}
    
    async def _create_notification_system(self, arguments: dict) -> dict:
        return {"content": [{"type": "text", "text": "Notification system created (implementation needed)"}]}
    
    async def _setup_camera_integration(self, arguments: dict) -> dict:
        return {"content": [{"type": "text", "text": "Camera integration setup created (implementation needed)"}]}
    
    async def _create_media_player(self, arguments: dict) -> dict:
        return {"content": [{"type": "text", "text": "Media player created
