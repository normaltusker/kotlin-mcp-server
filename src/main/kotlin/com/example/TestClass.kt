package com.example

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * TestClass - General purpose class with modern Kotlin patterns
 */
@Singleton
class TestClass @Inject constructor() {

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()

    /**
     * Initialize the class
     */
    fun initialize() {
        _state.value = _state.value.copy(isInitialized = true)
    }

    /**
     * Perform main operation
     */
    suspend fun performOperation(input: String): Result<String> {
        return try {
            if (!_state.value.isInitialized) {
                return Result.failure(IllegalStateException("Not initialized"))
            }

            val result = processInput(input)
            _state.value = _state.value.copy(lastResult = result)
            Result.success(result)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Reset to initial state
     */
    fun reset() {
        _state.value = State()
    }

    /**
     * Process input according to business logic
     */
    private fun processInput(input: String): String {
        return input.trim().takeIf { it.isNotEmpty() } ?: "Empty input"
    }

    /**
     * State data class
     */
    data class State(
        val isInitialized: Boolean = false,
        val lastResult: String = ""
    )
}
