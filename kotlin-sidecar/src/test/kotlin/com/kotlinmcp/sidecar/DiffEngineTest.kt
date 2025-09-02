package com.kotlinmcp.sidecar

import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class DiffEngineTest {

    @Test
    fun `unifiedDiff_simpleChange_hasHunkHeaderAndNewlines`() {
        val original = "fun hello() {\n    println(\"Hello\")\n}"
        val modified = "fun hello() {\n    println(\"Hello World\")\n}"

        val diff = DiffEngine.unifiedDiff("Test.kt", original, modified, contextLines = 1)

        assertTrue(diff.contains("--- a/Test.kt"))
        assertTrue(diff.contains("+++ b/Test.kt"))
        assertTrue(diff.contains("@@"))
        assertTrue(diff.endsWith("\n"))
    }

    @Test
    fun `unifiedDiff_preservesExpectedHunkRange_onTwoLineChange`() {
        val original = "fun hello() {\n    println(\"Hello\")\n}"
        val modified = "fun hello() {\n    println(\"Hello World\")\n}"

        val diff = DiffEngine.unifiedDiff("Test.kt", original, modified, contextLines = 1)

        assertTrue(diff.contains("@@ -1,3 +1,3 @@"))
    }

    @Test
    fun `unifiedDiff_noChanges_returnsEmptyDiff`() {
        val content = "fun hello() {\n    println(\"Hello\")\n}"

        val diff = DiffEngine.unifiedDiff("Test.kt", content, content, contextLines = 1)

        // Should return a diff with headers but no hunks
        assertTrue(diff.contains("--- a/Test.kt"))
        assertTrue(diff.contains("+++ b/Test.kt"))
        assertTrue(diff.endsWith("\n"))
    }
}
