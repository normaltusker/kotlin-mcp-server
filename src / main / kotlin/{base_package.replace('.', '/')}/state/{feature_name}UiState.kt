package {package}.state

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
