package com.yourorg.mcp.schema

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonElement

// Base types
@Serializable
data class FilePath(val value: String) {
    init {
        require(value.isNotBlank()) { "File path cannot be blank" }
    }
}

@Serializable
data class ProjectRoot(val value: String) {
    init {
        require(value.isNotBlank()) { "Project root cannot be blank" }
    }
}

@Serializable
data class RepoRoot(val value: String) {
    init {
        require(value.isNotBlank()) { "Repo root cannot be blank" }
    }
}

@Serializable
data class Uri(val value: String) {
    init {
        require(value.startsWith("http://") || value.startsWith("https://") ||
                value.startsWith("file://")) { "Invalid URI format" }
    }
}

@Serializable
data class Range(
    val startLine: Int,
    val startCol: Int,
    val endLine: Int,
    val endCol: Int
) {
    init {
        require(startLine >= 1 && startCol >= 1 && endLine >= 1 && endCol >= 1) {
            "All range values must be >= 1"
        }
    }
}

@Serializable
data class Patch(val value: String) {
    init {
        require(value.isNotBlank()) { "Patch cannot be blank" }
        require(value.contains("@@")) { "Invalid patch format" }
    }
}

@Serializable
data class Diagnostic(
    val ruleId: String,
    val severity: String,
    val location: DiagnosticLocation,
    val message: String,
    val quickFixId: String? = null
) {
    init {
        require(severity in listOf("info", "warning", "error")) {
            "Severity must be info, warning, or error"
        }
    }
}

@Serializable
data class DiagnosticLocation(
    val filePath: String,
    val line: Int,
    val col: Int? = null
) {
    init {
        require(line >= 1) { "Line must be >= 1" }
    }
}

@Serializable
data class File(
    val path: String,
    val content: String,
    val mode: Int? = null
)

@Serializable
data class Conflict(
    val filePath: String,
    val hunks: List<String>
)

@Serializable
data class Endpoint(
    val name: String,
    val path: String,
    val method: String
) {
    init {
        require(method in listOf("GET", "POST", "PUT", "PATCH", "DELETE")) {
            "Invalid HTTP method"
        }
    }
}

@Serializable
data class DataRef(
    val type: String,
    val value: String
) {
    init {
        require(type in listOf("path", "inline", "uri")) {
            "Type must be path, inline, or uri"
        }
    }
}

@Serializable
data class AuditId(val value: String)

@Serializable
data class SubjectId(val value: String)

@Serializable
data class AuditEvent(
    val id: String,
    val timestamp: String,
    val operation: String,
    val subjectId: String,
    val details: Map<String, JsonElement> = emptyMap(),
    val complianceTags: List<String> = emptyList()
)

@Serializable
data class BackupManifest(
    val id: String,
    val createdAt: String,
    val entries: List<BackupEntry>
)

@Serializable
data class BackupEntry(
    val path: String,
    val hash: String,
    val size: Long
)

@Serializable
data class ClassificationFinding(
    val filePath: String,
    val policy: String,
    val line: Int,
    val snippet: String,
    val confidence: Double
) {
    init {
        require(policy in listOf("PII", "PHI", "Secrets")) {
            "Policy must be PII, PHI, or Secrets"
        }
        require(confidence in 0.0..1.0) { "Confidence must be between 0.0 and 1.0" }
    }
}

@Serializable
data class GitChange(
    val path: String,
    val status: String
) {
    init {
        require(status in listOf("A", "M", "D", "R", "C", "U")) {
            "Invalid git status"
        }
    }
}

@Serializable
data class AheadBehind(
    val ahead: Int,
    val behind: Int
) {
    init {
        require(ahead >= 0 && behind >= 0) {
            "Ahead and behind counts must be >= 0"
        }
    }
}

@Serializable
data class ApiSpec(
    val baseUrl: String,
    val path: String,
    val method: String,
    val headers: Map<String, String> = emptyMap(),
    val auth: AuthSpec? = null,
    val query: Map<String, JsonElement> = emptyMap()
) {
    init {
        require(method in listOf("GET", "POST", "PUT", "PATCH", "DELETE")) {
            "Invalid HTTP method"
        }
    }
}

@Serializable
data class AuthSpec(
    val type: String,
    val tokenRef: DataRef? = null,
    val additionalProperties: Map<String, JsonElement> = emptyMap()
)

@Serializable
data class MetricPoint(
    val ts: String,
    val name: String,
    val value: Double,
    val dimensions: Map<String, String> = emptyMap()
)

@Serializable
data class ComplianceViolation(
    val policy: String,
    val field: String,
    val issue: String,
    val severity: String
) {
    init {
        require(policy in listOf("GDPR", "HIPAA")) {
            "Policy must be GDPR or HIPAA"
        }
        require(severity in listOf("low", "medium", "high")) {
            "Severity must be low, medium, or high"
        }
    }
}

@Serializable
data class SearchMatch(
    val file: String,
    val line: Int,
    val snippet: String
)

@Serializable
data class Todo(
    val ref: String,
    val description: String,
    val suggestedAction: String? = null
)

@Serializable
data class ReleaseNotes(
    val features: List<String>,
    val fixes: List<String>,
    val breaking: List<String>
)

@Serializable
data class TestFailure(
    val name: String,
    val filePath: String,
    val message: String
)

@Serializable
data class Vulnerability(
    val id: String,
    val packageName: String,
    val version: String,
    val severity: String,
    val fixedIn: String? = null
) {
    init {
        require(severity in listOf("low", "medium", "high", "critical")) {
            "Invalid severity level"
        }
    }
}

@Serializable
data class LicenseIssue(
    val packageName: String,
    val license: String,
    val issue: String
)

// Tool Input/Output Data Classes

// refactorFunction
@Serializable
data class RefactorFunctionInput(
    val filePath: String,
    val functionName: String,
    val refactorType: String,
    val newName: String? = null,
    val range: Range? = null,
    val preview: Boolean = false
) {
    init {
        require(refactorType in listOf("rename", "extract", "inline", "introduceParam")) {
            "Invalid refactor type"
        }
        if (refactorType == "rename" || refactorType == "introduceParam") {
            requireNotNull(newName) { "newName is required for $refactorType" }
        }
    }
}

@Serializable
data class RefactorFunctionOutput(
    val patch: String,
    val affectedFiles: List<String>
)

// applyCodeAction
@Serializable
data class ApplyCodeActionInput(
    val filePath: String,
    val codeActionId: String,
    val preview: Boolean = false
)

@Serializable
data class ApplyCodeActionOutput(
    val patch: String
)

// optimizeImports
@Serializable
data class OptimizeImportsInput(
    val projectRoot: String,
    val mode: String,
    val targets: List<String>? = null,
    val preview: Boolean = false
) {
    init {
        require(mode in listOf("file", "module", "project")) {
            "Mode must be file, module, or project"
        }
    }
}

@Serializable
data class OptimizeImportsOutput(
    val patches: List<String>
)

// formatCode
@Serializable
data class FormatCodeInput(
    val targets: List<String>,
    val style: String,
    val preview: Boolean = false
) {
    init {
        require(style in listOf("ktlint", "spotless")) {
            "Style must be ktlint or spotless"
        }
    }
}

@Serializable
data class FormatCodeOutput(
    val patches: List<String>,
    val summary: String
)

// analyzeCodeQuality
@Serializable
data class AnalyzeCodeQualityInput(
    val scope: String,
    val targets: List<String>? = null,
    val ruleset: String,
    val maxFindings: Int? = null
) {
    init {
        require(scope in listOf("file", "module", "project")) {
            "Scope must be file, module, or project"
        }
        require(ruleset in listOf("security", "performance", "complexity", "all")) {
            "Invalid ruleset"
        }
    }
}

@Serializable
data class AnalyzeCodeQualityOutput(
    val diagnostics: List<Diagnostic>
)

// generateTests
@Serializable
data class GenerateTestsInput(
    val filePath: String,
    val classOrFunction: String,
    val framework: String,
    val coverageGoal: Double? = null
) {
    init {
        require(framework in listOf("JUnit5", "MockK")) {
            "Framework must be JUnit5 or MockK"
        }
        coverageGoal?.let {
            require(it in 0.0..100.0) { "Coverage goal must be between 0 and 100" }
        }
    }
}

@Serializable
data class GenerateTestsOutput(
    val files: List<File>,
    val instructions: String
)

// applyPatch
@Serializable
data class ApplyPatchInput(
    val patch: String,
    val allowCreate: Boolean = true
)

@Serializable
data class ApplyPatchOutput(
    val applied: Boolean,
    val conflicts: List<Conflict>? = null
)

// androidGenerateComposeUI
@Serializable
data class AndroidGenerateComposeUIInput(
    val screenName: String,
    val stateModel: Map<String, JsonElement>,
    val navigation: Boolean = true,
    val theme: String? = null
)

@Serializable
data class AndroidGenerateComposeUIOutput(
    val files: List<File>,
    val instructions: String
)

// androidSetupArchitecture
@Serializable
data class AndroidSetupArchitectureInput(
    val pattern: String,
    val di: String,
    val modules: List<String>? = null
) {
    init {
        require(pattern in listOf("MVVM", "Clean")) {
            "Pattern must be MVVM or Clean"
        }
        require(di in listOf("Hilt", "Koin")) {
            "DI must be Hilt or Koin"
        }
    }
}

@Serializable
data class GradleUpdate(
    val file: String,
    val patch: String
)

@Serializable
data class AndroidSetupArchitectureOutput(
    val files: List<File>,
    val gradleUpdates: List<GradleUpdate>,
    val wiringInstructions: String
)

// androidSetupDataLayer
@Serializable
data class AndroidSetupDataLayerInput(
    val db: String,
    val entities: List<Map<String, JsonElement>>,
    val migrations: Boolean = true,
    val encryption: Boolean = false
) {
    init {
        require(db == "Room") { "Only Room database is supported" }
    }
}

@Serializable
data class AndroidSetupDataLayerOutput(
    val files: List<File>,
    val migrationScripts: List<File>,
    val tests: List<File>
)

// androidSetupNetwork
@Serializable
data class AndroidSetupNetworkInput(
    val style: String,
    val endpoints: List<Endpoint>,
    val auth: String
) {
    init {
        require(style in listOf("Retrofit", "GraphQL", "WebSocket")) {
            "Invalid network style"
        }
        require(auth in listOf("None", "ApiKey", "OAuth2", "JWT")) {
            "Invalid auth type"
        }
    }
}

@Serializable
data class AndroidSetupNetworkOutput(
    val files: List<File>,
    val tests: List<File>
)

// securityEncryptData
@Serializable
data class SecurityEncryptDataInput(
    val dataRef: DataRef,
    val algo: String = "AES-256-GCM",
    val kdf: String = "PBKDF2",
    val context: Map<String, JsonElement> = emptyMap()
) {
    init {
        require(algo == "AES-256-GCM") { "Only AES-256-GCM is supported" }
        require(kdf == "PBKDF2") { "Only PBKDF2 is supported" }
    }
}

@Serializable
data class SecurityEncryptDataOutput(
    val encryptedRef: DataRef,
    val auditId: String
)

// securityDecryptData
@Serializable
data class SecurityDecryptDataInput(
    val dataRef: DataRef,
    val context: Map<String, JsonElement> = emptyMap()
)

@Serializable
data class SecurityDecryptDataOutput(
    val plaintextRef: DataRef,
    val auditId: String
)

// privacyRequestErasure
@Serializable
data class PrivacyRequestErasureInput(
    val subjectId: String,
    val scopes: List<String>
)

@Serializable
data class PrivacyRequestErasureOutput(
    val actions: List<String>,
    val auditId: String
)

// privacyExportData
@Serializable
data class PrivacyExportDataInput(
    val subjectId: String,
    val format: String,
    val fields: List<String>? = null
) {
    init {
        require(format in listOf("JSON", "CSV", "Parquet")) {
            "Invalid export format"
        }
    }
}

@Serializable
data class PrivacyExportDataOutput(
    val exportRef: DataRef,
    val auditId: String
)

// securityAuditTrail
@Serializable
data class AuditFilters(
    val subjectId: String? = null,
    val op: String? = null,
    val dateRange: DateRange? = null,
    val complianceTags: List<String> = emptyList()
)

@Serializable
data class DateRange(
    val from: String,
    val to: String
)

@Serializable
data class SecurityAuditTrailInput(
    val filters: AuditFilters? = null,
    val limit: Int? = null
) {
    init {
        limit?.let { require(it in 1..1000) { "Limit must be between 1 and 1000" } }
    }
}

@Serializable
data class SecurityAuditTrailOutput(
    val events: List<AuditEvent>
)

// fileBackup
@Serializable
data class FileBackupInput(
    val targets: List<String>,
    val dest: String,
    val encrypt: Boolean = false,
    val tag: String? = null
)

@Serializable
data class FileBackupOutput(
    val manifest: BackupManifest,
    val auditId: String
)

// fileRestore
@Serializable
data class FileRestoreInput(
    val manifestRef: DataRef,
    val destRoot: String,
    val decrypt: Boolean = true
)

@Serializable
data class FileRestoreOutput(
    val restored: List<String>,
    val auditId: String
)

// fileSyncWatch
@Serializable
data class FileSyncWatchInput(
    val paths: List<String>,
    val dest: String,
    val includeGlobs: List<String> = emptyList(),
    val excludeGlobs: List<String> = emptyList()
)

@Serializable
data class FileSyncWatchOutput(
    val watchId: String,
    val statusStream: String
)

// fileClassifySensitivity
@Serializable
data class FileClassifySensitivityInput(
    val targets: List<String>,
    val policies: List<String>
) {
    init {
        policies.forEach { policy ->
            require(policy in listOf("PII", "PHI", "Secrets")) {
                "Invalid policy: $policy"
            }
        }
    }
}

@Serializable
data class FileClassifySensitivityOutput(
    val findings: List<ClassificationFinding>,
    val recommendations: List<String>
)

// gitStatus
@Serializable
data class GitStatusInput(
    val repoRoot: String
)

@Serializable
data class GitStatusOutput(
    val branch: String,
    val changes: List<GitChange>,
    val aheadBehind: AheadBehind
)

// gitSmartCommit
@Serializable
data class GitSmartCommitInput(
    val repoRoot: String,
    val intent: String,
    val messageHint: String? = null,
    val include: List<String>? = null
) {
    init {
        require(intent in listOf("refactor", "fix", "feat", "chore", "docs")) {
            "Invalid intent"
        }
    }
}

@Serializable
data class GitSmartCommitOutput(
    val commitId: String,
    val summary: String
)

// gitCreateFeatureBranch
@Serializable
data class GitCreateFeatureBranchInput(
    val repoRoot: String,
    val name: String,
    val from: String? = null
)

@Serializable
data class GitCreateFeatureBranchOutput(
    val branch: String,
    val tip: String
)

// gitMergeWithResolution
@Serializable
data class GitMergeWithResolutionInput(
    val repoRoot: String,
    val source: String,
    val target: String,
    val strategy: String? = null
) {
    init {
        strategy?.let {
            require(it in listOf("recursive", "ours", "theirs", "ort")) {
                "Invalid merge strategy"
            }
        }
    }
}

@Serializable
data class GitMergeWithResolutionOutput(
    val merged: Boolean,
    val conflicts: List<Conflict>? = null,
    val instructions: String? = null
)

// apiCallSecure
@Serializable
data class ApiCallSecureInput(
    val spec: ApiSpec,
    val body: JsonElement? = null,
    val schema: JsonElement? = null,
    val rateLimitKey: String? = null
)

@Serializable
data class ApiCallSecureOutput(
    val response: JsonElement,
    val latencyMs: Long,
    val costEst: Double? = null
)

// apiMonitorMetrics
@Serializable
data class ApiMonitorMetricsInput(
    val serviceId: String,
    val window: String,
    val dimensions: List<String> = emptyList()
) {
    init {
        require(window.matches(Regex("^(1m|5m|15m|1h|24h|7d)$"))) {
            "Invalid window format"
        }
    }
}

@Serializable
data class ApiMonitorMetricsOutput(
    val metrics: List<MetricPoint>,
    val alerts: List<String> = emptyList()
)

// apiValidateCompliance
@Serializable
data class ApiValidateComplianceInput(
    val payloadRef: DataRef,
    val policies: List<String>
) {
    init {
        policies.forEach { policy ->
            require(policy in listOf("GDPR", "HIPAA")) {
                "Invalid policy: $policy"
            }
        }
    }
}

@Serializable
data class ApiValidateComplianceOutput(
    val violations: List<ComplianceViolation>,
    val suggestedRemediations: List<String>
)

// projectSearch
@Serializable
data class ProjectSearchInput(
    val query: String,
    val paths: List<String>? = null,
    val regex: Boolean = false,
    val contextLines: Int = 2
) {
    init {
        require(contextLines in 0..20) { "Context lines must be between 0 and 20" }
    }
}

@Serializable
data class ProjectSearchOutput(
    val matches: List<SearchMatch>
)

// todoListFromCode
@Serializable
data class TodoListFromCodeInput(
    val scope: String,
    val targets: List<String>? = null
) {
    init {
        require(scope in listOf("file", "module", "project")) {
            "Scope must be file, module, or project"
        }
    }
}

@Serializable
data class TodoListFromCodeOutput(
    val todos: List<Todo>
)

// readmeGenerateOrUpdate
@Serializable
data class ReadmeGenerateOrUpdateInput(
    val projectRoot: String,
    val sections: List<String>? = null
)

@Serializable
data class ReadmeGenerateOrUpdateOutput(
    val file: File,
    val patch: String
)

// changelogSummarize
@Serializable
data class ChangelogSummarizeInput(
    val repoRoot: String,
    val sinceTag: String,
    val until: String? = null
)

@Serializable
data class ChangelogSummarizeOutput(
    val notes: ReleaseNotes,
    val nextVersionHint: String
)

// buildAndTest
@Serializable
data class BuildAndTestInput(
    val command: String,
    val targets: List<String>? = null,
    val profile: String? = null
) {
    init {
        require(command in listOf("gradle", "maven")) {
            "Command must be gradle or maven"
        }
    }
}

@Serializable
data class BuildAndTestOutput(
    val status: String,
    val summary: String,
    val failingTests: List<TestFailure>? = null,
    val artifacts: List<File>? = null
) {
    init {
        require(status in listOf("passed", "failed")) {
            "Status must be passed or failed"
        }
    }
}

// dependencyAudit
@Serializable
data class DependencyAuditInput(
    val projectRoot: String,
    val includeLicenses: Boolean = true,
    val allowList: List<String> = emptyList()
)

@Serializable
data class DependencyAuditOutput(
    val vulns: List<Vulnerability>,
    val licenseIssues: List<LicenseIssue> = emptyList(),
    val upgradeAdvice: List<String>
)
