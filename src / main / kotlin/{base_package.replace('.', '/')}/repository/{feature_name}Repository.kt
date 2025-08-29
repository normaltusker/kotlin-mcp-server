package {package}.repository

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
