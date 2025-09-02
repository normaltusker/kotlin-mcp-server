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

        val result = sidecar.processRequest(ToolRequest("refactorFunction", input))

        assertFalse(result.ok)
        assertEquals("ValidationError", result.error?.code)
        assertTrue(result.error?.message?.contains("newName is required") == true)
    }

    @Test
    fun `unsupportedRefactorType_returnsUnsupportedRefactorType`() {
        val input = JsonObject().apply {
            addProperty("filePath", "/tmp/test.kt")
            addProperty("functionName", "testFunc")
            addProperty("refactorType", "unsupported_type")
        }

        val result = sidecar.processRequest(ToolRequest("refactorFunction", input))

        assertFalse(result.ok)
        assertEquals("UnsupportedRefactorType", result.error?.code)
        assertTrue(result.error?.message?.contains("Unsupported refactor type") == true)
    }

    @Test
    fun `functionNotFound_returnsSymbolNotFound`() {
        val input = JsonObject().apply {
            addProperty("filePath", "/tmp/nonexistent.kt")
            addProperty("functionName", "testFunc")
            addProperty("refactorType", "rename")
            addProperty("newName", "newFunc")
        }

        val result = sidecar.processRequest(ToolRequest("refactorFunction", input))

        assertFalse(result.ok)
        assertEquals("SymbolNotFound", result.error?.code)
        assertTrue(result.error?.message?.contains("not found in") == true)
    }
}
