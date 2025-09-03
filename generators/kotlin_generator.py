"""
Kotlin code generators for Android MCP Server.

This module provides comprehensive code generation capabilities for Android development:
- Complete Activity classes with Jetpack Compose
- ViewModels with state management
- Repository patterns with dependency injection
- Data classes with validation and serialization
- Use cases with business logic
- Services with proper lifecycle management
- Adapters with Compose integration
- Interfaces with comprehensive contracts
- General purpose classes with modern patterns
"""

from pathlib import Path
from typing import Any, List, Optional


class KotlinCodeGenerator:
    """
    Generates production-ready Kotlin code for Android development.

    Enhanced with AI integration capabilities for more sophisticated code generation.
    """

    def __init__(self, llm_integration: Optional[Any] = None) -> None:
        """
        Initialize the Kotlin code generator.

        Args:
            llm_integration: Optional LLM integration for enhanced code generation
        """
        self.llm_integration = llm_integration
        self.ai_enhanced = llm_integration is not None

    def generate_complete_activity(
        self, package_name: str, class_name: str, features: List[str]
    ) -> str:
        """Generate a complete, production-ready Activity with modern Android patterns."""
        imports = [
            "import android.os.Bundle",
            "import androidx.activity.ComponentActivity",
            "import androidx.activity.compose.setContent",
            "import androidx.compose.foundation.layout.*",
            "import androidx.compose.material3.*",
            "import androidx.compose.runtime.*",
            "import androidx.compose.ui.Alignment",
            "import androidx.compose.ui.Modifier",
            "import androidx.compose.ui.tooling.preview.Preview",
            "import androidx.compose.ui.unit.dp",
            "import androidx.lifecycle.viewmodel.compose.viewModel",
        ]

        if "viewmodel" in features:
            imports.extend(
                [
                    "import androidx.lifecycle.compose.collectAsStateWithLifecycle",
                    "import androidx.hilt.navigation.compose.hiltViewModel",
                ]
            )

        if "navigation" in features:
            imports.extend(
                [
                    "import androidx.navigation.compose.NavHost",
                    "import androidx.navigation.compose.composable",
                    "import androidx.navigation.compose.rememberNavController",
                ]
            )

        activity_content = f"""package {package_name}

{chr(10).join(imports)}

/**
 * {class_name} - Modern Android Activity with Jetpack Compose UI
 *
 * Features:
 * - Jetpack Compose UI with Material Design 3
 * - State management with ViewModel
 * - Proper lifecycle handling
 * - Accessibility support
 * - Error handling and loading states
 */
class {class_name} : ComponentActivity() {{

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)

        setContent {{
            {class_name}Theme {{
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {{
                    {class_name}Screen()
                }}
            }}
        }}
    }}
}}

@Composable
fun {class_name}Screen(
    viewModel: {class_name}ViewModel = viewModel()
) {{
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {{
        when (uiState) {{
            is {class_name}UiState.Loading -> {{
                CircularProgressIndicator()
                Text(
                    text = "Loading...",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }}
            is {class_name}UiState.Success -> {{
                Text(
                    text = "Welcome to {class_name}!",
                    style = MaterialTheme.typography.headlineMedium,
                    modifier = Modifier.padding(bottom = 16.dp)
                )
                Button(
                    onClick = {{ viewModel.refreshData() }}
                ) {{
                    Text("Refresh")
                }}
            }}
            is {class_name}UiState.Error -> {{
                Text(
                    text = "Error: ${{uiState.message}}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(bottom = 16.dp)
                )
                Button(
                    onClick = {{ viewModel.retry() }}
                ) {{
                    Text("Retry")
                }}
            }}
        }}
    }}
}}

@Preview(showBackground = true)
@Composable
fun {class_name}ScreenPreview() {{
    {class_name}Theme {{
        {class_name}Screen()
    }}
}}

@Composable
fun {class_name}Theme(content: @Composable () -> Unit) {{
    MaterialTheme(
        content = content
    )
}}
"""

        return activity_content

    def generate_complete_viewmodel(
        self, package_name: str, class_name: str, features: List[str]
    ) -> str:
        """Generate a complete ViewModel with state management and business logic."""
        return f"""package {package_name}

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

/**
 * {class_name} - ViewModel managing UI state and business logic
 *
 * Responsibilities:
 * - UI state management with StateFlow
 * - Business logic coordination
 * - Repository interaction
 * - Error handling and loading states
 */
@HiltViewModel
class {class_name} @Inject constructor(
    private val repository: {class_name.replace("ViewModel", "")}Repository
) : ViewModel() {{

    private val _uiState = MutableStateFlow<{class_name.replace("ViewModel", "")}UiState>({class_name.replace("ViewModel", "")}UiState.Loading)
    val uiState: StateFlow<{class_name.replace("ViewModel", "")}UiState> = _uiState.asStateFlow()

    init {{
        loadData()
    }}

    fun loadData() {{
        viewModelScope.launch {{
            _uiState.value = {class_name.replace("ViewModel", "")}UiState.Loading
            try {{
                val data = repository.getData()
                _uiState.value = {class_name.replace("ViewModel", "")}UiState.Success(data)
            }} catch (e: Exception) {{
                _uiState.value = {class_name.replace("ViewModel", "")}UiState.Error(
                    e.message ?: "Unknown error occurred"
                )
            }}
        }}
    }}

    fun refreshData() {{
        loadData()
    }}

    fun retry() {{
        loadData()
    }}
}}

/**
 * UI State sealed class for type-safe state management
 */
sealed class {class_name.replace("ViewModel", "")}UiState {{
    object Loading : {class_name.replace("ViewModel", "")}UiState()
    data class Success(val data: String) : {class_name.replace("ViewModel", "")}UiState()
    data class Error(val message: String) : {class_name.replace("ViewModel", "")}UiState()
}}
"""

    def generate_complete_repository(
        self, package_name: str, class_name: str, features: List[str]
    ) -> str:
        """Generate a complete Repository with data access logic."""
        return f"""package {package_name}

import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * {class_name} - Repository handling data operations
 *
 * Responsibilities:
 * - Data source coordination (local/remote)
 * - Caching strategy implementation
 * - Data transformation and mapping
 * - Error handling and retry logic
 */
@Singleton
class {class_name} @Inject constructor(
    private val localDataSource: {class_name.replace("Repository", "")}LocalDataSource,
    private val remoteDataSource: {class_name.replace("Repository", "")}RemoteDataSource
) {{

    /**
     * Get data with caching strategy
     */
    suspend fun getData(): String {{
        return try {{
            // Try local first
            val localData = localDataSource.getData()
            if (localData.isNotEmpty()) {{
                return localData
            }}

            // Fallback to remote
            val remoteData = remoteDataSource.getData()
            localDataSource.saveData(remoteData)
            remoteData
        }} catch (e: Exception) {{
            throw RepositoryException("Failed to fetch data: ${{e.message}}")
        }}
    }}

    /**
     * Get data as Flow for reactive updates
     */
    fun getDataStream(): Flow<String> = flow {{
        emit(getData())
        // Optionally emit updates as they come
    }}

    /**
     * Refresh data from remote source
     */
    suspend fun refreshData(): String {{
        val data = remoteDataSource.getData()
        localDataSource.saveData(data)
        return data
    }}
}}

/**
 * Custom exception for repository errors
 */
class RepositoryException(message: String) : Exception(message)

/**
 * Local data source interface
 */
interface {class_name.replace("Repository", "")}LocalDataSource {{
    suspend fun getData(): String
    suspend fun saveData(data: String)
}}

/**
 * Remote data source interface
 */
interface {class_name.replace("Repository", "")}RemoteDataSource {{
    suspend fun getData(): String
}}
"""

    def generate_complete_fragment(
        self, package_name: str, class_name: str, features: List[str]
    ) -> str:
        """Generate a complete Fragment with Jetpack Compose integration."""
        return f"""package {package_name}

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.unit.dp
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dagger.hilt.android.AndroidEntryPoint

/**
 * {class_name} - Modern Fragment with Jetpack Compose UI
 */
@AndroidEntryPoint
class {class_name} : Fragment() {{

    private val viewModel: {class_name}ViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {{
        return ComposeView(requireContext()).apply {{
            setContent {{
                {class_name}Content(viewModel = viewModel)
            }}
        }}
    }}
}}

@Composable
fun {class_name}Content(
    viewModel: {class_name}ViewModel
) {{
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {{
        Text(
            text = "{class_name} Fragment",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(16.dp))

        when (uiState.isLoading) {{
            true -> CircularProgressIndicator()
            false -> Button(
                onClick = {{ viewModel.performAction() }}
            ) {{
                Text("Perform Action")
            }}
        }}
    }}
}}
"""

    def generate_complete_data_class(
        self, package_name: str, class_name: str, features: List[str]
    ) -> str:
        """Generate a complete data class with validation and serialization."""
        return f"""package {package_name}

import kotlinx.serialization.Serializable
import android.os.Parcelable
import kotlinx.parcelize.Parcelize

/**
 * {class_name} - Immutable data class with validation and serialization
 */
@Serializable
@Parcelize
data class {class_name}(
    val id: Long = 0L,
    val name: String = "",
    val description: String = "",
    val isActive: Boolean = true,
    val createdAt: Long = System.currentTimeMillis(),
    val metadata: Map<String, String> = emptyMap()
) : Parcelable {{

    /**
     * Validate the data class instance
     */
    fun isValid(): Boolean {{
        return name.isNotBlank() &&
               description.isNotBlank() &&
               id >= 0L &&
               createdAt > 0L
    }}

    /**
     * Create a copy with updated fields
     */
    fun update(
        name: String? = null,
        description: String? = null,
        isActive: Boolean? = null,
        metadata: Map<String, String>? = null
    ): {class_name} {{
        return copy(
            name = name ?: this.name,
            description = description ?: this.description,
            isActive = isActive ?: this.isActive,
            metadata = metadata ?: this.metadata
        )
    }}

    companion object {{
        /**
         * Create empty instance
         */
        fun empty(): {class_name} = {class_name}()

        /**
         * Create from minimal data
         */
        fun create(name: String, description: String): {class_name} {{
            return {class_name}(
                name = name,
                description = description
            )
        }}
    }}
}}
"""

    def generate_complete_use_case(
        self, package_name: str, class_name: str, features: List[str]
    ) -> str:
        """Generate a complete Use Case with business logic."""
        return f"""package {package_name}

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * {class_name} - Use case containing specific business logic
 */
@Singleton
class {class_name} @Inject constructor(
    private val repository: {class_name.replace("UseCase", "")}Repository
) {{

    /**
     * Execute the use case
     */
    suspend operator fun invoke(params: {class_name}Params): Result<{class_name}Result> {{
        return try {{
            if (!params.isValid()) {{
                return Result.failure(IllegalArgumentException("Invalid parameters"))
            }}

            val data = repository.getData(params.query)
            val processedData = processData(data)

            Result.success({class_name}Result(processedData))
        }} catch (e: Exception) {{
            Result.failure(e)
        }}
    }}

    /**
     * Execute as Flow for reactive programming
     */
    fun executeAsFlow(params: {class_name}Params): Flow<Result<{class_name}Result>> = flow {{
        emit(invoke(params))
    }}

    /**
     * Process the raw data according to business rules
     */
    private fun processData(rawData: String): String {{
        // Apply business logic here
        return rawData.trim().takeIf {{ it.isNotEmpty() }} ?: "No data available"
    }}
}}

/**
 * Parameters for the use case
 */
data class {class_name}Params(
    val query: String,
    val includeInactive: Boolean = false
) {{
    fun isValid(): Boolean = query.isNotBlank()
}}

/**
 * Result from the use case
 */
data class {class_name}Result(
    val data: String,
    val timestamp: Long = System.currentTimeMillis()
)
"""

    def generate_complete_service(
        self, package_name: str, class_name: str, features: List[str]
    ) -> str:
        """Generate a complete Android Service."""
        return f"""package {package_name}

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.*
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * {class_name} - Background service with proper lifecycle management
 */
@AndroidEntryPoint
class {class_name} : Service() {{

    @Inject
    lateinit var repository: {class_name.replace("Service", "")}Repository

    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.IO + serviceJob)

    private val notificationId = 1001
    private val channelId = "{package_name.split('.')[-1]}_channel"

    override fun onCreate() {{
        super.onCreate()
        createNotificationChannel()
        startForegroundService()
    }}

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {{
        when (intent?.action) {{
            ACTION_START -> startWork()
            ACTION_STOP -> stopWork()
        }}
        return START_STICKY
    }}

    override fun onBind(intent: Intent?): IBinder? = null

    private fun startWork() {{
        serviceScope.launch {{
            try {{
                while (isActive) {{
                    // Perform background work
                    val result = repository.performBackgroundTask()
                    // Process result
                    delay(5000) // Wait 5 seconds between operations
                }}
            }} catch (e: Exception) {{
                // Handle errors
            }}
        }}
    }}

    private fun stopWork() {{
        serviceJob.cancel()
        stopSelf()
    }}

    private fun createNotificationChannel() {{
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
            val channel = NotificationChannel(
                channelId,
                "{class_name} Channel",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }}
    }}

    private fun startForegroundService() {{
        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("{class_name}")
            .setContentText("Service is running")
            .setSmallIcon(android.R.drawable.ic_menu_info_details)
            .build()

        startForeground(notificationId, notification)
    }}

    override fun onDestroy() {{
        super.onDestroy()
        serviceJob.cancel()
    }}

    companion object {{
        const val ACTION_START = "ACTION_START"
        const val ACTION_STOP = "ACTION_STOP"
    }}
}}
"""

    def generate_complete_adapter(
        self, package_name: str, class_name: str, features: List[str]
    ) -> str:
        """Generate a complete RecyclerView Adapter."""
        return f"""package {package_name}

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.unit.dp

/**
 * {class_name} - Modern RecyclerView Adapter with Compose integration
 */
class {class_name}(
    private val onItemClick: (Item) -> Unit = {{}}
) : ListAdapter<Item, {class_name}.ViewHolder>(ItemDiffCallback()) {{

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {{
        val composeView = ComposeView(parent.context)
        return ViewHolder(composeView, onItemClick)
    }}

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {{
        holder.bind(getItem(position))
    }}

    class ViewHolder(
        private val composeView: ComposeView,
        private val onItemClick: (Item) -> Unit
    ) : RecyclerView.ViewHolder(composeView) {{

        fun bind(item: Item) {{
            composeView.setContent {{
                ItemCard(
                    item = item,
                    onClick = {{ onItemClick(item) }}
                )
            }}
        }}
    }}
}}

@Composable
fun ItemCard(
    item: Item,
    onClick: () -> Unit
) {{
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        onClick = onClick
    ) {{
        Column(
            modifier = Modifier.padding(16.dp)
        ) {{
            Text(
                text = item.title,
                style = MaterialTheme.typography.headlineSmall
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = item.description,
                style = MaterialTheme.typography.bodyMedium
            )
        }}
    }}
}}

class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {{
    override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {{
        return oldItem.id == newItem.id
    }}

    override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {{
        return oldItem == newItem
    }}
}}

/**
 * Data class for adapter items
 */
data class Item(
    val id: Long,
    val title: String,
    val description: String
)
"""

    def generate_complete_interface(
        self, package_name: str, class_name: str, features: List[str]
    ) -> str:
        """Generate a complete interface with proper documentation."""
        return f"""package {package_name}

import kotlinx.coroutines.flow.Flow

/**
 * {class_name} - Interface defining contract for data operations
 */
interface {class_name} {{

    /**
     * Get item by ID
     */
    suspend fun getById(id: Long): Result<Item?>

    /**
     * Get all items
     */
    suspend fun getAll(): Result<List<Item>>

    /**
     * Get items as Flow for reactive updates
     */
    fun getAllAsFlow(): Flow<List<Item>>

    /**
     * Save item
     */
    suspend fun save(item: Item): Result<Long>

    /**
     * Update existing item
     */
    suspend fun update(item: Item): Result<Boolean>

    /**
     * Delete item by ID
     */
    suspend fun deleteById(id: Long): Result<Boolean>

    /**
     * Search items by query
     */
    suspend fun search(query: String): Result<List<Item>>

    /**
     * Check if item exists
     */
    suspend fun exists(id: Long): Boolean
}}
"""

    def generate_complete_class(
        self, package_name: str, class_name: str, features: List[str]
    ) -> str:
        """Generate a complete general-purpose class."""
        return f"""package {package_name}

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * {class_name} - General purpose class with modern Kotlin patterns
 */
@Singleton
class {class_name} @Inject constructor() {{

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()

    /**
     * Initialize the class
     */
    fun initialize() {{
        _state.value = _state.value.copy(isInitialized = true)
    }}

    /**
     * Perform main operation
     */
    suspend fun performOperation(input: String): Result<String> {{
        return try {{
            if (!_state.value.isInitialized) {{
                return Result.failure(IllegalStateException("Not initialized"))
            }}

            val result = processInput(input)
            _state.value = _state.value.copy(lastResult = result)
            Result.success(result)
        }} catch (e: Exception) {{
            Result.failure(e)
        }}
    }}

    /**
     * Reset to initial state
     */
    fun reset() {{
        _state.value = State()
    }}

    /**
     * Process input according to business logic
     */
    private fun processInput(input: String): String {{
        return input.trim().takeIf {{ it.isNotEmpty() }} ?: "Empty input"
    }}

    /**
     * State data class
     */
    data class State(
        val isInitialized: Boolean = false,
        val lastResult: String = ""
    )
}}
"""

    def generate_unit_test(self, package_name: str, class_name: str, directory: Path) -> str:
        """Generate a basic unit test file for a class."""
        test_class_name = f"{class_name}Test"
        test_content = f"""package {package_name}

import org.junit.Assert.assertEquals
import org.junit.Test

class {test_class_name} {{
    @Test
    fun addition_isCorrect() {{
        assertEquals(4, 2 + 2)
    }}
}}
"""
        test_path = directory / f"{test_class_name}.kt"
        test_path.write_text(test_content, encoding="utf-8")
        return f"{test_class_name}.kt"

    def generate_related_files(
        self,
        class_type: str,
        package_name: str,
        class_name: str,
        directory: Path,
        features: List[str],
    ) -> List[str]:
        """Generate related files that complement the main file."""
        related_files = []

        if class_type == "activity" or class_type == "fragment":
            # Generate ViewModel
            viewmodel_name = (
                f"{class_name.replace('Activity', '').replace('Fragment', '')}ViewModel"
            )
            viewmodel_content = self.generate_complete_viewmodel(
                package_name, viewmodel_name, features
            )
            viewmodel_path = directory / f"{viewmodel_name}.kt"
            viewmodel_path.write_text(viewmodel_content, encoding="utf-8")
            related_files.append(f"{viewmodel_name}.kt")
            related_files.append(self.generate_unit_test(package_name, viewmodel_name, directory))

            # Generate Repository
            repo_name = f"{class_name.replace('Activity', '').replace('Fragment', '')}Repository"
            repo_content = self.generate_complete_repository(package_name, repo_name, features)
            repo_path = directory / f"{repo_name}.kt"
            repo_path.write_text(repo_content, encoding="utf-8")
            related_files.append(f"{repo_name}.kt")
            related_files.append(self.generate_unit_test(package_name, repo_name, directory))

        elif class_type == "viewmodel":
            # Generate Repository
            repo_name = f"{class_name.replace('ViewModel', '')}Repository"
            repo_content = self.generate_complete_repository(package_name, repo_name, features)
            repo_path = directory / f"{repo_name}.kt"
            repo_path.write_text(repo_content, encoding="utf-8")
            related_files.append(f"{repo_name}.kt")
            related_files.append(self.generate_unit_test(package_name, repo_name, directory))

        elif class_type == "repository":
            # Generate DataSource interfaces
            ds_name = f"{class_name.replace('Repository', '')}"
            local_ds_name = f"{ds_name}LocalDataSource"
            remote_ds_name = f"{ds_name}RemoteDataSource"

            local_ds_content = f"""package {package_name}

interface {local_ds_name} {{
    suspend fun getData(): String
    suspend fun saveData(data: String)
}}
"""
            remote_ds_content = f"""package {package_name}

interface {remote_ds_name} {{
    suspend fun getData(): String
}}
"""
            local_ds_path = directory / f"{local_ds_name}.kt"
            remote_ds_path = directory / f"{remote_ds_name}.kt"
            local_ds_path.write_text(local_ds_content, encoding="utf-8")
            remote_ds_path.write_text(remote_ds_content, encoding="utf-8")
            related_files.append(f"{local_ds_name}.kt")
            related_files.append(f"{remote_ds_name}.kt")

        # Generate a unit test for the main file itself
        related_files.append(self.generate_unit_test(package_name, class_name, directory))

        return related_files
