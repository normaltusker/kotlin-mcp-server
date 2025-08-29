package {package}.model

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
