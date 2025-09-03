package com.yourorg.mcp.schema

import com.networknt.schema.JsonSchema
import com.networknt.schema.JsonSchemaFactory
import com.networknt.schema.SpecVersion
import com.networknt.schema.ValidationMessage
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.encodeToJsonElement

// Custom exceptions
class ValidationException(
    val code: String,
    val details: String,
    val errors: List<ValidationMessage> = emptyList()
) : Exception("$code: $details")

class SchemaMissingException(toolName: String) :
    Exception("Schema not found for tool: $toolName")

// JSON Schema factory with strict mode
private val jsonSchemaFactory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V202012)

// JSON configuration with strict mode
private val json = Json {
    encodeDefaults = true
    explicitNulls = false
    ignoreUnknownKeys = false
    isLenient = false
    allowStructuredMapKeys = true
    prettyPrint = false
    useArrayPolymorphism = false
}

// Schema storage - in production, this would be loaded from the schema file
private val toolSchemas = mutableMapOf<String, Pair<JsonSchema, JsonSchema>>()

// Initialize schemas (this would be done at startup)
fun initializeSchemas(schemaJson: String) {
    // Parse the main schema file and extract tool schemas
    // This is a simplified implementation - in production you'd parse the full schema
    val schemaMap = mapOf(
        "refactorFunction" to createToolSchema(
            """
            {
              "type": "object",
              "required": ["filePath", "functionName", "refactorType"],
              "properties": {
                "filePath": {"type": "string", "minLength": 1},
                "functionName": {"type": "string", "minLength": 1},
                "refactorType": {"type": "string", "enum": ["rename", "extract", "inline", "introduceParam"]},
                "newName": {"type": "string"},
                "preview": {"type": "boolean", "default": false}
              }
            }
            """,
            """
            {
              "type": "object",
              "required": ["patch", "affectedFiles"],
              "properties": {
                "patch": {"type": "string", "minLength": 1},
                "affectedFiles": {"type": "array", "items": {"type": "string", "minLength": 1}}
              }
            }
            """
        ),
        // Add other tool schemas here...
    )

    toolSchemas.putAll(schemaMap)
}

private fun createToolSchema(inputSchema: String, outputSchema: String): Pair<JsonSchema, JsonSchema> {
    val inputJsonSchema = jsonSchemaFactory.getSchema(inputSchema)
    val outputJsonSchema = jsonSchemaFactory.getSchema(outputSchema)
    return Pair(inputJsonSchema, outputJsonSchema)
}

// Validation functions
fun validateInput(toolName: String, jsonElement: JsonElement): Unit {
    val schemas = toolSchemas[toolName] ?: throw SchemaMissingException(toolName)
    val inputSchema = schemas.first

    val errors = inputSchema.validate(jsonElement)
    if (errors.isNotEmpty()) {
        throw ValidationException(
            code = "ValidationError",
            details = "Input validation failed for $toolName",
            errors = errors
        )
    }
}

fun validateOutput(toolName: String, jsonElement: JsonElement): Unit {
    val schemas = toolSchemas[toolName] ?: throw SchemaMissingException(toolName)
    val outputSchema = schemas.second

    val errors = outputSchema.validate(jsonElement)
    if (errors.isNotEmpty()) {
        throw ValidationException(
            code = "InternalOutputInvalid",
            details = "Output validation failed for $toolName",
            errors = errors
        )
    }
}

// Convenience functions for data classes
inline fun <reified T> validateInput(toolName: String, data: T): Unit {
    val jsonElement = json.encodeToJsonElement(data)
    validateInput(toolName, jsonElement)
}

inline fun <reified T> validateOutput(toolName: String, data: T): Unit {
    val jsonElement = json.encodeToJsonElement(data)
    validateOutput(toolName, jsonElement)
}

// Utility functions
fun getAvailableTools(): Set<String> = toolSchemas.keys

fun hasTool(toolName: String): Boolean = toolSchemas.containsKey(toolName)

// Schema loading from file (production implementation)
fun loadSchemasFromFile(schemaFilePath: String) {
    // Implementation would parse the JSON schema file and populate toolSchemas
    // For now, this is a placeholder
}
