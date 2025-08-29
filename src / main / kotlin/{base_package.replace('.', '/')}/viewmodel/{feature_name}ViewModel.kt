package {package}.viewmodel

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
