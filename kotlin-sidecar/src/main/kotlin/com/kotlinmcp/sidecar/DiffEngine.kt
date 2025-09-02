package com.kotlinmcp.sidecar

import com.github.difflib.DiffUtils
import com.github.difflib.UnifiedDiffUtils

object DiffEngine {
    private fun toUnix(s: String): String =
        s.replace("\r\n", "\n").replace("\r", "\n")

    private fun ensureTrailingNewline(s: String): String =
        if (s.isEmpty() || s.endsWith("\n")) s else s + "\n"

    fun unifiedDiff(
        path: String,
        original: String,
        updated: String,
        contextLines: Int = 3
    ): String {
        val orig = ensureTrailingNewline(toUnix(original))
        val upd = ensureTrailingNewline(toUnix(updated))

        val origLines = orig.split('\n')
        val updLines = upd.split('\n')

        val patch = DiffUtils.diff(origLines, updLines)
        val udiff = UnifiedDiffUtils.generateUnifiedDiff(
            "a/$path",
            "b/$path",
            origLines,
            patch,
            contextLines
        )

        // UnifiedDiffUtils returns lines; join with '\n' + final newline
        return udiff.joinToString(separator = "\n", postfix = "\n")
    }
}
