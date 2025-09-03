package com.kotlinmcp.sidecar

import com.google.gson.JsonObject
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class RefactorValidationTest {

    private val sidecar = KotlinSidecar()

    @Test
    fun `rename_missingNewName_returnsValidationError`() {
        val input = JsonObject().apply {
            addProperty("filePath", "/tmp/test.kt")
            addProperty("functionName", "testFunc")
            addProperty("refactorType", "rename")
        }

        val result = sidecar.handleToolRequest(ToolRequest("refactorFunction", input))

        assertFalse(result.ok)
        assertEquals("INVALID_INPUT", result.error?.code)
        assertTrue(result.error?.message?.contains("newName required") == true)
    }

    @Test
    fun `formatCode_missingTargets_returnsValidationError`() {
        val input = JsonObject()

        val result = sidecar.handleToolRequest(ToolRequest("formatCode", input))

        assertFalse(result.ok)
        assertEquals("INVALID_INPUT", result.error?.code)
        assertTrue(result.error?.message?.contains("Missing targets") == true)
    }

    @Test
    fun `buildAndTest_validInput_returnsSuccess`() {
        val input = JsonObject().apply {
            addProperty("buildTool", "gradle")
            addProperty("skipTests", false)
        }

        val result = sidecar.handleToolRequest(ToolRequest("buildAndTest", input))

        assertTrue(result.ok)
        assertEquals("gradle", result.result?.get("buildTool")?.asString)
    }
}
