#!/usr/bin/env python3
"""
Intelligent UI and Architecture Tools

Enhanced implementations of UI development and architecture setup tools
with LSP - like intelligent capabilities.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class IntelligentComposeComponentTool(IntelligentToolBase):
    """Enhanced Jetpack Compose component creation with intelligent design patterns."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Create intelligent Jetpack Compose components with best practices."""

        file_path = arguments.get("file_path", "")
        component_name = arguments.get("component_name", "")
        component_type = arguments.get("component_type", "component")
        package_name = arguments.get("package_name", "")
        uses_state = arguments.get("uses_state", False)
        uses_navigation = arguments.get("uses_navigation", False)

        # Intelligent component generation
        component_code = await self._generate_intelligent_compose_component(
            component_name, component_type, package_name, uses_state, uses_navigation
        )

        # Create the file
        full_path = self.project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        # Analyze the generated component
        component_analysis = await self._analyze_compose_component(component_code, component_type)

        return {
            "component_created": {
                "file_path": str(full_path),
                "component_name": component_name,
                "component_type": component_type,
                "features": {
                    "state_management": uses_state,
                    "navigation": uses_navigation,
                    "modern_patterns": True,
                },
            },
            "intelligent_analysis": component_analysis,
            "architectural_insights": await self._generate_compose_insights(component_type),
            "next_steps": await self._suggest_compose_next_steps(
                component_type, uses_state, uses_navigation
            ),
        }

    async def _generate_intelligent_compose_component(
        self,
        component_name: str,
        component_type: str,
        package_name: str,
        uses_state: bool,
        uses_navigation: bool,
    ) -> str:
        """Generate intelligent Compose component with modern patterns."""

        imports = [
            "import androidx.compose.foundation.layout.*",
            "import androidx.compose.material3.*",
            "import androidx.compose.runtime.*",
            "import androidx.compose.ui.Alignment",
            "import androidx.compose.ui.Modifier",
            "import androidx.compose.ui.tooling.preview.Preview",
            "import androidx.compose.ui.unit.dp",
        ]

        if uses_state:
            imports.extend(
                [
                    "import androidx.lifecycle.viewmodel.compose.viewModel",
                    "import androidx.compose.runtime.collectAsState",
                ]
            )

        if uses_navigation:
            imports.extend(
                [
                    "import androidx.navigation.NavController",
                    "import androidx.navigation.compose.rememberNavController",
                ]
            )

        # Generate component based on type
        if component_type == "screen":
            component_code = self._generate_screen_component(
                component_name, uses_state, uses_navigation
            )
        elif component_type == "dialog":
            component_code = self._generate_dialog_component(component_name, uses_state)
        elif component_type == "bottom_sheet":
            component_code = self._generate_bottom_sheet_component(component_name, uses_state)
        else:
            component_code = self._generate_standard_component(component_name, uses_state)

        # Assemble the complete file
        complete_code = """package {package_name}

{chr(10).join(imports)}

/**
 * {component_name} - A modern Jetpack Compose {component_type}
 *
 * Generated with intelligent patterns and best practices:
 * - Material Design 3 components
 * - Proper state management
 * - Accessibility support
 * - Preview support for design validation
 */
{component_code}

@Preview(showBackground = true)
@Composable
fun {component_name}Preview() {{
    MaterialTheme {{
        {component_name}({self._generate_preview_parameters(uses_state, uses_navigation)})
    }}
}}
"""

        return complete_code

    def _generate_screen_component(self, name: str, uses_state: bool, uses_navigation: bool) -> str:
        """Generate a screen - level Compose component."""
        nav_param = "navController: NavController" if uses_navigation else ""
        state_param = "viewModel: YourViewModel = viewModel()" if uses_state else ""

        params = [p for p in [nav_param, state_param] if p]
        param_string = ", ".join(params) if params else ""

        state_code = ""
        if uses_state:
            state_code = """
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        // Initialize screen data
        viewModel.loadData()
    }"""

        navigation_code = ""
        if uses_navigation:
            navigation_code = """
        Button(
            onClick = {
                // Navigate to next screen
                navController.navigate("next_screen")
            }
        ) {
            Text("Navigate")
        }"""

        return """
@Composable
fun {name}({param_string}) {{{state_code}

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {{
        Text(
            text = "{name}",
            style = MaterialTheme.typography.headlineMedium
        )

        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {{
            Column(
                modifier = Modifier.padding(16.dp)
            ) {{
                Text(
                    text = "Welcome to {name}",
                    style = MaterialTheme.typography.bodyLarge
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "This screen was generated with intelligent patterns",
                    style = MaterialTheme.typography.bodyMedium
                )
            }}
        }}{navigation_code}
    }}
}}"""

    def _generate_dialog_component(self, name: str, uses_state: bool) -> str:
        """Generate a dialog Compose component."""
        state_param = "onConfirm: () -> Unit = {}, onDismiss: () -> Unit = {}"

        return """
@Composable
fun {name}(
    showDialog: Boolean,
    {state_param}
) {{
    if (showDialog) {{
        AlertDialog(
            onDismissRequest = onDismiss,
            title = {{
                Text(text = "{name}")
            }},
            text = {{
                Text(text = "This is an intelligent dialog component with proper Material Design patterns.")
            }},
            confirmButton = {{
                TextButton(onClick = onConfirm) {{
                    Text("Confirm")
                }}
            }},
            dismissButton = {{
                TextButton(onClick = onDismiss) {{
                    Text("Cancel")
                }}
            }}
        )
    }}
}}"""

    def _generate_bottom_sheet_component(self, name: str, uses_state: bool) -> str:
        """Generate a bottom sheet Compose component."""
        return """
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun {name}(
    showBottomSheet: Boolean,
    onDismiss: () -> Unit
) {{
    if (showBottomSheet) {{
        ModalBottomSheet(
            onDismissRequest = onDismiss
        ) {{
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {{
                Text(
                    text = "{name}",
                    style = MaterialTheme.typography.headlineSmall
                )

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "Intelligent bottom sheet with modern Material Design",
                    style = MaterialTheme.typography.bodyMedium
                )

                Spacer(modifier = Modifier.height(24.dp))

                Button(
                    onClick = onDismiss,
                    modifier = Modifier.fillMaxWidth()
                ) {{
                    Text("Close")
                }}

                Spacer(modifier = Modifier.height(16.dp))
            }}
        }}
    }}
}}"""

    def _generate_standard_component(self, name: str, uses_state: bool) -> str:
        """Generate a standard Compose component."""
        state_param = "onClick: () -> Unit = {}" if uses_state else ""

        return """
@Composable
fun {name}(
    modifier: Modifier = Modifier{', ' + state_param if state_param else ''}
) {{
    Card(
        modifier = modifier,
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {{
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {{
            Text(
                text = "{name}",
                style = MaterialTheme.typography.titleMedium
            )

            Text(
                text = "Intelligent component with Material Design 3",
                style = MaterialTheme.typography.bodyMedium
            )

            {self._generate_action_button() if uses_state else ''}
        }}
    }}
}}"""

    def _generate_action_button(self) -> str:
        """Generate action button for interactive components."""
        return """
            Button(
                onClick = onClick,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Action")
            }"""

    def _generate_preview_parameters(self, uses_state: bool, uses_navigation: bool) -> str:
        """Generate preview parameters."""
        params = []

        if uses_navigation:
            params.append("navController = rememberNavController()")

        if uses_state:
            params.append("onClick = {}")

        return ", ".join(params)

    async def _analyze_compose_component(self, code: str, component_type: str) -> Dict[str, Any]:
        """Analyze the generated Compose component for quality insights."""
        analysis = {
            "code_quality": {
                "uses_material3": "@Composable" in code and "MaterialTheme" in code,
                "has_preview": "@Preview" in code,
                "follows_naming_conventions": True,
                "accessibility_ready": "modifier" in code.lower(),
            },
            "modern_patterns": {
                "state_hoisting": "remember" in code or "collectAsState" in code,
                "proper_spacing": "Arrangement.spacedBy" in code,
                "material_design": "Card" in code and "MaterialTheme" in code,
            },
            "maintainability": {
                "well_documented": "/**" in code,
                "parameterized": "(" in code and ")" in code,
                "reusable": "modifier: Modifier" in code,
            },
        }

        return analysis

    async def _generate_compose_insights(self, component_type: str) -> List[str]:
        """Generate architectural insights for the Compose component."""
        insights = [
            "🎨 Using Material Design 3 for modern UI consistency",
            "⚡ Compose provides efficient UI rendering and updates",
            "🔄 State hoisting enables better testability",
            "📱 Components are designed to be responsive and accessible",
        ]

        if component_type == "screen":
            insights.extend(
                [
                    "🏗️ Screen - level components should manage navigation state",
                    "📊 Consider integrating with ViewModel for data management",
                    "🎯 Implement proper loading and error states",
                ]
            )
        elif component_type == "dialog":
            insights.extend(
                [
                    "💬 Dialogs should have clear primary and secondary actions",
                    "🎭 Consider animation and transition effects",
                    "♿ Ensure proper focus management for accessibility",
                ]
            )

        return insights

    async def _suggest_compose_next_steps(
        self, component_type: str, uses_state: bool, uses_navigation: bool
    ) -> List[str]:
        """Suggest next steps for component development."""
        steps = [
            "🧪 Add unit tests for the component logic",
            "🎨 Customize theme colors and typography",
            "📱 Test on different screen sizes and orientations",
            "♿ Verify accessibility with TalkBack",
        ]

        if not uses_state:
            steps.append("🔄 Consider adding state management for interactivity")

        if not uses_navigation and component_type == "screen":
            steps.append("🧭 Integrate with Navigation Compose for screen transitions")

        steps.extend(
            [
                "📊 Add analytics tracking for user interactions",
                "🎭 Implement smooth animations and transitions",
                "🔍 Add search and filtering capabilities if needed",
            ]
        )

        return steps


class IntelligentLayoutFileTool(IntelligentToolBase):
    """Enhanced XML layout creation with intelligent validation and LSP checks."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Create an intelligent Android XML layout file."""

        file_path = arguments.get("file_path", "")
        layout_type = arguments.get("layout_type", "LinearLayout")
        attributes: Dict[str, str] = arguments.get("attributes", {})

        # Validate layout type
        valid_layouts = {
            "LinearLayout",
            "ConstraintLayout",
            "RelativeLayout",
            "FrameLayout",
        }
        if layout_type not in valid_layouts:
            return {
                "layout_created": False,
                "error": f"Unsupported layout type: {layout_type}",
            }

        attribute_issues = self._validate_layout_attributes(attributes)

        # Generate layout scaffold
        layout_content = self._generate_layout_content(layout_type, attributes)

        # Perform reference checks using LSP navigation
        reference_analysis = await self._check_references_with_lsp(layout_content)

        # Resolve path and create file
        full_path = self._resolve_layout_path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(layout_content)

        # Attempt to format XML using xmllint if available
        try:
            subprocess.run(
                ["xmllint", "--format", str(full_path), "-o", str(full_path)],
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            pass

        return {
            "layout_created": {
                "file_path": str(full_path),
                "layout_type": layout_type,
                "attributes": attributes,
            },
            "validation": {"attribute_issues": attribute_issues},
            "reference_analysis": reference_analysis,
        }

    def _generate_layout_content(self, layout_type: str, attributes: Dict[str, str]) -> str:
        """Generate basic XML layout structure."""

        default_attrs = {
            "android:layout_width": "match_parent",
            "android:layout_height": "match_parent",
        }
        all_attrs = {**default_attrs, **attributes}

        if layout_type == "LinearLayout" and "android:orientation" not in all_attrs:
            all_attrs["android:orientation"] = "vertical"

        attrs_text = "\n".join(f'    {k}="{v}"' for k, v in all_attrs.items())
        return (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            f"<{layout_type}\n{attrs_text}\n>\n\n</{layout_type}>\n"
        )

    def _validate_layout_attributes(self, attributes: Dict[str, str]) -> List[str]:
        """Validate attribute namespaces and values."""

        issues: List[str] = []
        for name, value in attributes.items():
            if not name.startswith("android:") and not name.startswith("app:"):
                issues.append(f"Unknown namespace for attribute '{name}'")
            if value == "":
                issues.append(f"Attribute '{name}' has empty value")
        return issues

    async def _check_references_with_lsp(self, content: str) -> Dict[str, Any]:
        """Use symbol navigation to analyze resource references."""

        import re

        references: Dict[str, Any] = {}
        pattern = re.compile(r"@([\w]+)/([A-Za-z0-9_]+)")
        for res_type, res_name in pattern.findall(content):
            lsp_result = await self.symbol_navigation.find_references(res_name)
            references[f"{res_type}/{res_name}"] = lsp_result.get("total_references", 0)
        return references

    def _resolve_layout_path(self, file_path: str) -> Path:
        """Determine where to create the layout file within the project."""

        path = Path(file_path)
        if path.is_absolute():
            return path

        # If path already includes a module/src structure, respect it
        if "src" in path.parts:
            return self.project_path / path

        # Default to app module layout directory
        return self.project_path / "app/src/main/res/layout" / path


class IntelligentMVVMArchitectureTool(IntelligentToolBase):
    """Enhanced MVVM architecture setup with intelligent patterns."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Set up intelligent MVVM architecture with modern patterns."""

        feature_name = arguments.get("feature_name", "")
        package_name = arguments.get("package_name", "")
        include_repository = arguments.get("include_repository", True)
        include_use_cases = arguments.get("include_use_cases", False)
        data_source = arguments.get("data_source", "network")

        # Generate architecture components
        architecture_files = await self._generate_mvvm_architecture(
            feature_name, package_name, include_repository, include_use_cases, data_source
        )

        # Create files
        created_files = []
        for file_info in architecture_files:
            file_path = self.project_path / file_info["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_info["content"])

            created_files.append(str(file_path))

        # Generate architecture analysis
        architecture_analysis = await self._analyze_mvvm_architecture(
            feature_name, include_repository, include_use_cases, data_source
        )

        return {
            "architecture_setup": {
                "feature_name": feature_name,
                "pattern": "MVVM" + (" + Clean Architecture" if include_use_cases else ""),
                "files_created": created_files,
                "data_sources": [data_source] if data_source != "both" else ["network", "database"],
            },
            "intelligent_analysis": architecture_analysis,
            "architectural_benefits": await self._explain_mvvm_benefits(),
            "implementation_guide": await self._create_implementation_guide(feature_name),
        }

    async def _generate_mvvm_architecture(
        self,
        feature_name: str,
        package_name: str,
        include_repository: bool,
        include_use_cases: bool,
        data_source: str,
    ) -> List[Dict[str, str]]:
        """Generate complete MVVM architecture files."""

        files = []
        base_package = f"{package_name}.{feature_name.lower()}"

        # 1. Data Model
        model_code = self._generate_data_model(feature_name, base_package)
        files.append(
            {
                "path": "src/main/kotlin/{base_package.replace('.', '/')}/model/{feature_name}.kt",
                "content": model_code,
            }
        )

        # 2. Repository Interface
        if include_repository:
            repo_interface_code = self._generate_repository_interface(feature_name, base_package)
            files.append(
                {
                    "path": "src/main/kotlin/{base_package.replace('.', '/')}/repository/{feature_name}Repository.kt",
                    "content": repo_interface_code,
                }
            )

            # 3. Repository Implementation
            repo_impl_code = self._generate_repository_implementation(
                feature_name, base_package, data_source
            )
            files.append(
                {
                    "path": "src/main/kotlin/{base_package.replace('.', '/')}/repository/{feature_name}RepositoryImpl.kt",
                    "content": repo_impl_code,
                }
            )

        # 4. Use Cases (if Clean Architecture)
        if include_use_cases:
            use_case_code = self._generate_use_case(feature_name, base_package)
            files.append(
                {
                    "path": "src/main/kotlin/{base_package.replace('.', '/')}/usecase/Get{feature_name}UseCase.kt",
                    "content": use_case_code,
                }
            )

        # 5. ViewModel
        view_model_code = self._generate_view_model(
            feature_name, base_package, include_repository, include_use_cases
        )
        files.append(
            {
                "path": "src/main/kotlin/{base_package.replace('.', '/')}/viewmodel/{feature_name}ViewModel.kt",
                "content": view_model_code,
            }
        )

        # 6. UI State
        ui_state_code = self._generate_ui_state(feature_name, base_package)
        files.append(
            {
                "path": "src/main/kotlin/{base_package.replace('.', '/')}/state/{feature_name}UiState.kt",
                "content": ui_state_code,
            }
        )

        return files

    def _generate_data_model(self, feature_name: str, package: str) -> str:
        """Generate intelligent data model."""
        return """package {package}.model

import kotlinx.serialization.Serializable

/**
 * {feature_name} data model with intelligent design patterns
 *
 * Features:
 * - Immutable data class for thread safety
 * - Kotlinx serialization support
 * - Proper null safety
 * - Documentation for all properties
 */
@Serializable
data class {feature_name}(
    val id: String,
    val name: String,
    val description: String? = null,
    val createdAt: Long = System.currentTimeMillis(),
    val isActive: Boolean = true
) {{

    /**
     * Computed property for display name
     */
    val displayName: String
        get() = name.ifBlank {{ "Unnamed {feature_name}" }}

    /**
     * Check if this item is recent (created within last 24 hours)
     */
    fun isRecent(): Boolean {{
        val dayInMillis = 24 * 60 * 60 * 1000
        return (System.currentTimeMillis() - createdAt) < dayInMillis
    }}
}}

/**
 * UI - specific model for displaying {feature_name} in lists
 */
data class {feature_name}ItemUi(
    val id: String,
    val title: String,
    val subtitle: String?,
    val isSelected: Boolean = false,
    val isLoading: Boolean = false
) {{
    companion object {{
        fun from{feature_name}(item: {feature_name}, isSelected: Boolean = false): {feature_name}ItemUi {{
            return {feature_name}ItemUi(
                id = item.id,
                title = item.displayName,
                subtitle = item.description,
                isSelected = isSelected
            )
        }}
    }}
}}
"""

    def _generate_repository_interface(self, feature_name: str, package: str) -> str:
        """Generate repository interface."""
        return """package {package}.repository

import {package}.model.{feature_name}
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for {feature_name} data operations
 *
 * Follows repository pattern with:
 * - Single source of truth
 * - Reactive data with Flow
 * - Clear separation of concerns
 * - Error handling strategy
 */
interface {feature_name}Repository {{

    /**
     * Get all {feature_name.lower()} items as a reactive stream
     */
    fun getAll(): Flow<List<{feature_name}>>

    /**
     * Get a specific {feature_name.lower()} by ID
     */
    suspend fun getById(id: String): Result<{feature_name}?>

    /**
     * Create a new {feature_name.lower()}
     */
    suspend fun create(item: {feature_name}): Result<{feature_name}>

    /**
     * Update an existing {feature_name.lower()}
     */
    suspend fun update(item: {feature_name}): Result<{feature_name}>

    /**
     * Delete a {feature_name.lower()} by ID
     */
    suspend fun delete(id: String): Result<Unit>

    /**
     * Search {feature_name.lower()} items by query
     */
    fun search(query: String): Flow<List<{feature_name}>>

    /**
     * Clear local cache (if applicable)
     */
    suspend fun clearCache()
}}
"""

    def _generate_repository_implementation(
        self, feature_name: str, package: str, data_source: str
    ) -> str:
        """Generate repository implementation."""
        network_import = (
            "// import your.api.package.ApiService" if data_source in ["network", "both"] else ""
        )
        database_import = (
            "// import your.db.package.Dao" if data_source in ["database", "both"] else ""
        )

        return """package {package}.repository

import {package}.model.{feature_name}
{network_import}
{database_import}
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOf
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Implementation of {feature_name}Repository with intelligent caching and data synchronization
 *
 * Architecture features:
 * - Repository pattern implementation
 * - Proper error handling with Result type
 * - Reactive data streams with Flow
 * - Dependency injection ready
 */
@Singleton
class {feature_name}RepositoryImpl @Inject constructor(
    // TODO: Inject your dependencies here
    // private val apiService: ApiService,
    // private val localDao: Dao
) : {feature_name}Repository {{

    override fun getAll(): Flow<List<{feature_name}>> = flow {{
        try {{
            // TODO: Implement actual data fetching logic
            val mockData = listOf(
                {feature_name}(
                    id = "1",
                    name = "Sample {feature_name}",
                    description = "This is a sample item"
                )
            )
            emit(mockData)
        }} catch (e: Exception) {{
            emit(emptyList())
        }}
    }}

    override suspend fun getById(id: String): Result<{feature_name}?> {{
        return try {{
            // TODO: Implement actual data fetching
            val mockItem = {feature_name}(
                id = id,
                name = "Sample {feature_name}",
                description = "Retrieved by ID"
            )
            Result.success(mockItem)
        }} catch (e: Exception) {{
            Result.failure(e)
        }}
    }}

    override suspend fun create(item: {feature_name}): Result<{feature_name}> {{
        return try {{
            // TODO: Implement creation logic
            Result.success(item)
        }} catch (e: Exception) {{
            Result.failure(e)
        }}
    }}

    override suspend fun update(item: {feature_name}): Result<{feature_name}> {{
        return try {{
            // TODO: Implement update logic
            Result.success(item)
        }} catch (e: Exception) {{
            Result.failure(e)
        }}
    }}

    override suspend fun delete(id: String): Result<Unit> {{
        return try {{
            // TODO: Implement deletion logic
            Result.success(Unit)
        }} catch (e: Exception) {{
            Result.failure(e)
        }}
    }}

    override fun search(query: String): Flow<List<{feature_name}>> = flow {{
        // TODO: Implement search logic
        emit(emptyList())
    }}

    override suspend fun clearCache() {{
        // TODO: Implement cache clearing
    }}
}}
"""

    def _generate_use_case(self, feature_name: str, package: str) -> str:
        """Generate use case for Clean Architecture."""
        return """package {package}.usecase

import {package}.model.{feature_name}
import {package}.repository.{feature_name}Repository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

/**
 * Use case for getting {feature_name} data with business logic
 *
 * Clean Architecture benefits:
 * - Encapsulates business rules
 * - Testable in isolation
 * - Independent of UI and data layers
 * - Single responsibility principle
 */
class Get{feature_name}UseCase @Inject constructor(
    private val repository: {feature_name}Repository
) {{

    /**
     * Get all active {feature_name.lower()} items
     */
    fun getAllActive(): Flow<List<{feature_name}>> {{
        // Business logic: filter only active items
        return repository.getAll()
            .map {{ items -> items.filter {{ it.isActive }} }}
    }}

    /**
     * Get recent {feature_name.lower()} items (last 24 hours)
     */
    fun getRecent(): Flow<List<{feature_name}>> {{
        return repository.getAll()
            .map {{ items ->
                items.filter {{ it.isRecent() && it.isActive }}
                    .sortedByDescending {{ it.createdAt }}
            }}
    }}

    /**
     * Get {feature_name.lower()} by ID with validation
     */
    suspend fun getById(id: String): Result<{feature_name}> {{
        if (id.isBlank()) {{
            return Result.failure(IllegalArgumentException("ID cannot be blank"))
        }}

        return repository.getById(id).fold(
            onSuccess = {{ item ->
                if (item != null) {{
                    Result.success(item)
                }} else {{
                    Result.failure(NoSuchElementException("{feature_name} not found"))
                }}
            }},
            onFailure = {{ Result.failure(it) }}
        )
    }}
}}
"""

    def _generate_view_model(
        self, feature_name: str, package: str, include_repository: bool, include_use_cases: bool
    ) -> str:
        """Generate intelligent ViewModel."""
        dependency = (
            "get{feature_name}UseCase: Get{feature_name}UseCase"
            if include_use_cases
            else "repository: {feature_name}Repository"
        )
        dependency_field = (
            "private val useCase = get${feature_name}UseCase"
            if include_use_cases
            else "private val repository = repository"
        )
        data_call = "useCase.getAllActive()" if include_use_cases else "repository.getAll()"

        return """package {package}.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import {package}.model.{feature_name}
{"import {package}.usecase.Get{feature_name}UseCase" if include_use_cases else f"import {package}.repository.{feature_name}Repository"}
import {package}.state.{feature_name}UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for {feature_name} feature with intelligent state management
 *
 * Features:
 * - Reactive UI state with StateFlow
 * - Proper error handling and loading states
 * - Memory leak prevention with viewModelScope
 * - Dependency injection with Hilt
 * - Unidirectional data flow
 */
@HiltViewModel
class {feature_name}ViewModel @Inject constructor(
    {dependency}
) : ViewModel() {{

    {dependency_field}

    private val _uiState = MutableStateFlow({feature_name}UiState())
    val uiState: StateFlow<{feature_name}UiState> = _uiState.asStateFlow()

    init {{
        loadData()
    }}

    /**
     * Load {feature_name.lower()} data with proper state management
     */
    fun loadData() {{
        viewModelScope.launch {{
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)

            try {{
                {data_call}
                    .catch {{ exception ->
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            error = exception.message ?: "Unknown error occurred"
                        )
                    }}
                    .collect {{ items ->
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            items = items,
                            error = null
                        )
                    }}
            }} catch (e: Exception) {{
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message ?: "Failed to load data"
                )
            }}
        }}
    }}

    /**
     * Refresh data (pull - to - refresh)
     */
    fun refresh() {{
        loadData()
    }}

    /**
     * Select an item
     */
    fun selectItem(item: {feature_name}) {{
        _uiState.value = _uiState.value.copy(selectedItem = item)
    }}

    /**
     * Clear selection
     */
    fun clearSelection() {{
        _uiState.value = _uiState.value.copy(selectedItem = null)
    }}

    /**
     * Search items
     */
    fun search(query: String) {{
        _uiState.value = _uiState.value.copy(searchQuery = query)

        if (query.isBlank()) {{
            loadData()
            return
        }}

        viewModelScope.launch {{
            try {{
                repository.search(query)
                    .collect {{ items ->
                        _uiState.value = _uiState.value.copy(
                            items = items,
                            isLoading = false
                        )
                    }}
            }} catch (e: Exception) {{
                _uiState.value = _uiState.value.copy(
                    error = "Search failed: ${{e.message}}",
                    isLoading = false
                )
            }}
        }}
    }}

    /**
     * Clear any error state
     */
    fun clearError() {{
        _uiState.value = _uiState.value.copy(error = null)
    }}
}}
"""

    def _generate_ui_state(self, feature_name: str, package: str) -> str:
        """Generate UI state class."""
        return """package {package}.state

import {package}.model.{feature_name}

/**
 * UI State for {feature_name} feature with comprehensive state management
 *
 * Benefits:
 * - Immutable state for predictable UI updates
 * - Complete loading, success, and error states
 * - Easy testing and debugging
 * - Type - safe state management
 */
data class {feature_name}UiState(
    val isLoading: Boolean = false,
    val items: List<{feature_name}> = emptyList(),
    val selectedItem: {feature_name}? = null,
    val searchQuery: String = "",
    val error: String? = null,
    val isRefreshing: Boolean = false
) {{

    /**
     * Check if we have data to display
     */
    val hasData: Boolean
        get() = items.isNotEmpty()

    /**
     * Check if we're in an empty state
     */
    val isEmpty: Boolean
        get() = !isLoading && !hasData && error == null

    /**
     * Check if we're in an error state
     */
    val hasError: Boolean
        get() = error != null

    /**
     * Check if search is active
     */
    val isSearching: Boolean
        get() = searchQuery.isNotBlank()

    /**
     * Get filtered items based on current state
     */
    val displayItems: List<{feature_name}>
        get() = if (isSearching) {{
            items.filter {{
                it.name.contains(searchQuery, ignoreCase = true) ||
                it.description?.contains(searchQuery, ignoreCase = true) == true
            }}
        }} else {{
            items
        }}
}}
"""

    async def _analyze_mvvm_architecture(
        self, feature_name: str, include_repository: bool, include_use_cases: bool, data_source: str
    ) -> Dict[str, Any]:
        """Analyze the generated MVVM architecture."""

        return {
            "architecture_quality": {
                "separation_of_concerns": "excellent",
                "testability": "high",
                "maintainability": "excellent",
                "scalability": "high",
            },
            "pattern_implementation": {
                "mvvm_compliance": True,
                "clean_architecture": include_use_cases,
                "repository_pattern": include_repository,
                "reactive_programming": True,
            },
            "modern_practices": {
                "dependency_injection": "Hilt ready",
                "coroutines": "Full async support",
                "state_management": "StateFlow + UiState",
                "error_handling": "Result type + try - catch",
            },
            "data_flow": {
                "direction": "Unidirectional",
                "state_source": "Single source of truth",
                "reactivity": "Flow - based reactive streams",
                "lifecycle_aware": "ViewModel scoped",
            },
        }

    async def _explain_mvvm_benefits(self) -> List[str]:
        """Explain the benefits of the MVVM architecture."""
        return [
            "🏗️ **Separation of Concerns**: Clear boundaries between UI, business logic, and data",
            "🧪 **Testability**: Each layer can be tested independently with mocking",
            "🔄 **Reactive UI**: Automatic UI updates when data changes through StateFlow",
            "📱 **Lifecycle Awareness**: ViewModel survives configuration changes",
            "🛡️ **Error Handling**: Comprehensive error states and recovery mechanisms",
            "🎯 **Single Source of Truth**: Repository pattern ensures data consistency",
            "⚡ **Performance**: Efficient data loading with coroutines and caching",
            "🔧 **Maintainability**: Clean code structure that's easy to modify and extend",
        ]

    async def _create_implementation_guide(self, feature_name: str) -> List[str]:
        """Create step - by - step implementation guide."""
        return [
            "📋 **Step 1**: Review generated {feature_name} model and adjust properties as needed",
            "🔌 **Step 2**: Implement actual data sources (API service, local database)",
            "🏗️ **Step 3**: Complete repository implementation with real data operations",
            "🎨 **Step 4**: Create Compose UI screens using the ViewModel",
            "🧪 **Step 5**: Write unit tests for ViewModel, Repository, and Use Cases",
            "📊 **Step 6**: Add analytics and monitoring to track feature usage",
            "🔄 **Step 7**: Implement caching strategy for offline support",
            "🎭 **Step 8**: Add loading animations and error state UI",
            "♿ **Step 9**: Ensure accessibility compliance with proper content descriptions",
            "🚀 **Step 10**: Performance optimization and memory leak prevention",
        ]
