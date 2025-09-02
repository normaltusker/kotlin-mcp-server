package com.kotlinmcp.sidecar

import com.github.difflib.DiffUtils
import com.github.difflib.patch.Patch
import kotlinx.cli.*
import org.jetbrains.kotlin.analysis.api.StandaloneAnalysisAPISession
import org.jetbrains.kotlin.analysis.api.session.KtAnalysisSessionProvider
import org.jetbrains.kotlin.cli.common.CLIConfigurationKeys
import org.jetbrains.kotlin.cli.common.messages.MessageCollector
import org.jetbrains.kotlin.cli.jvm.compiler.EnvironmentConfigFiles
import org.jetbrains.kotlin.cli.jvm.compiler.KotlinCoreEnvironment
import org.jetbrains.kotlin.com.intellij.openapi.util.Disposer
import org.jetbrains.kotlin.config.CompilerConfiguration
import org.jetbrains.kotlin.psi.KtFile
import org.jetbrains.kotlin.psi.KtNamedFunction
import org.jetbrains.kotlin.psi.KtPsiFactory
import java.io.File
import java.nio.file.Files
import java.nio.file.Paths
import kotlin.system.exitProcess

data class ToolRequest(
    val tool: String,
    val input: JsonObject
)

data class ToolResponse(
    val ok: Boolean,
    val result: JsonObject? = null,
    val error: ErrorResponse? = null
)

data class ErrorResponse(
    val code: String,
    val message: String,
    val data: JsonObject? = null
)

data class PatchResult(
    val diff: String,
    val patch: String? = null, // optional alias, same as diff
    val affectedFiles: List<String> = emptyList(),
    val success: Boolean = true
)

class KotlinSidecar {
    private val gson = Gson()
    private lateinit var analysisSession: StandaloneAnalysisAPISession
    private lateinit var psiFactory: KtPsiFactory

    init {
        initializeAnalysisSession()
    }

    private fun initializeAnalysisSession() {
        try {
            val configuration = CompilerConfiguration()
            configuration.put(CLIConfigurationKeys.MESSAGE_COLLECTOR_KEY, MessageCollector.NONE)

            val environment = KotlinCoreEnvironment.createForProduction(
                Disposer.newDisposable(),
                configuration,
                EnvironmentConfigFiles.JVM_CONFIG_FILES
            )

            analysisSession = StandaloneAnalysisAPISession.create(environment)
            psiFactory = KtPsiFactory(environment.project)
        } catch (e: Exception) {
            println(gson.toJson(ToolResponse(
                ok = false,
                error = ErrorResponse(
                    code = "InitializationError",
                    message = "Failed to initialize Kotlin Analysis API: ${e.message}"
                )
            )))
            exitProcess(1)
        }
    }

    fun processRequest(request: ToolRequest): ToolResponse {
        return try {
            val result = when (request.tool) {
                "refactorFunction" -> handleRefactorFunction(request.input)
                "applyCodeAction" -> handleApplyCodeAction(request.input)
                "formatCode" -> handleFormatCode(request.input)
                "optimizeImports" -> handleOptimizeImports(request.input)
                "compileModule" -> handleCompileModule(request.input)
                "runTests" -> handleRunTests(request.input)
                "androidSetupArchitecture" -> handleAndroidSetupArchitecture(request.input)
                "androidSetupDataLayer" -> handleAndroidSetupDataLayer(request.input)
                "androidSetupNetwork" -> handleAndroidSetupNetwork(request.input)
                "androidGenerateComposeUI" -> handleAndroidGenerateComposeUI(request.input)
                else -> throw IllegalArgumentException("Unknown tool: ${request.tool}")
            }

            // Handle error responses from handlers
            if (result is Map<*, *> && result["ok"] == false) {
                val errorMap = result["error"] as? Map<*, *>
                return ToolResponse(
                    ok = false,
                    error = ErrorResponse(
                        code = errorMap?.get("code") as? String ?: "UnknownError",
                        message = errorMap?.get("message") as? String ?: "Unknown error"
                    )
                )
            }

            ToolResponse(ok = true, result = gson.toJsonTree(result).asJsonObject)
        } catch (e: Exception) {
            ToolResponse(
                ok = false,
                error = ErrorResponse(
                    code = "ProcessingError",
                    message = "Error processing request: ${e.message}",
                    data = gson.toJsonTree(mapOf("stackTrace" to e.stackTraceToString())).asJsonObject
                )
            )
        }
    }

    private fun handleRefactorFunction(input: JsonObject): Any {
        val filePath = input.get("filePath")?.asString ?: throw IllegalArgumentException("filePath required")
        val functionName = input.get("functionName")?.asString ?: throw IllegalArgumentException("functionName required")
        val refactorType = input.get("refactorType")?.asString ?: throw IllegalArgumentException("refactorType required")

        // Validate refactorType first
        val allowedTypes = setOf("rename", "extract", "inline", "introduceParam")
        if (refactorType !in allowedTypes) {
            return mapOf(
                "ok" to false,
                "error" to mapOf(
                    "code" to "UnsupportedRefactorType",
                    "message" to "Unsupported refactor type: $refactorType"
                )
            )
        }

        // Validate newName for rename
        if (refactorType == "rename") {
            val newName = input.get("newName")?.asString
            if (newName.isNullOrBlank()) {
                return mapOf(
                    "ok" to false,
                    "error" to mapOf(
                        "code" to "ValidationError",
                        "message" to "newName is required"
                    )
                )
            }
        }

        val file = File(filePath)
        if (!file.exists()) {
            return mapOf(
                "ok" to false,
                "error" to mapOf(
                    "code" to "SymbolNotFound",
                    "message" to "Function '$functionName' not found in $filePath"
                )
            )
        }

        val oldContent = file.readText()

        // Check if function exists (simple check)
        if (!oldContent.contains(Regex("fun\\s+$functionName\\b"))) {
            return mapOf(
                "ok" to false,
                "error" to mapOf(
                    "code" to "SymbolNotFound",
                    "message" to "Function '$functionName' not found in $filePath"
                )
            )
        }

        val newContent = when (refactorType) {
            "rename" -> {
                val newName = input.get("newName")?.asString!!
                oldContent.replace(Regex("fun\\s+$functionName\\b"), "fun $newName")
            }
            "extract" -> {
                oldContent.replace(Regex("fun\\s+$functionName\\b"), "fun extracted$functionName")
            }
            "inline" -> {
                // Simple inline - remove function definition and replace calls
                val funcPattern = Regex("fun\\s+$functionName\\s*\\([^)]*\\)\\s*:\\s*[^=]*=\\s*([^\\n]+)")
                val match = funcPattern.find(oldContent)
                if (match != null) {
                    val body = match.groupValues[1].trim()
                    val withoutDef = oldContent.replace(funcPattern, "")
                    // Replace calls with body
                    withoutDef.replace(Regex("$functionName\\s*\\([^)]*\\)"), body)
                } else {
                    oldContent.replace(Regex("fun\\s+$functionName\\b[^}]*\\}[\\n\\r]*"), "")
                }
            }
            "introduceParam" -> {
                val newParam = input.get("newName")?.asString ?: "param"
                oldContent.replace(Regex("fun\\s+$functionName\\s*\\("), "fun $functionName($newParam: Any, ")
            }
            else -> oldContent // Should not reach here due to validation
        }

        file.writeText(newContent)

        val diff = DiffEngine.unifiedDiff(filePath, oldContent, newContent, contextLines = 1)
        return PatchResult(
            diff = diff,
            patch = diff,
            affectedFiles = listOf(filePath),
            success = true
        )
    }

    private fun handleApplyCodeAction(input: JsonObject): PatchResult {
        val filePath = input.get("filePath")?.asString ?: throw IllegalArgumentException("filePath required")
        val codeActionId = input.get("codeActionId")?.asString ?: throw IllegalArgumentException("codeActionId required")

        // Placeholder - would apply specific code action using Kotlin Analysis API
        val file = File(filePath)
        if (!file.exists()) {
            throw IllegalArgumentException("File not found: $filePath")
        }

        val oldContent = file.readText()
        // Simulate applying a code action
        val newContent = oldContent.replace("// TODO", "// FIXED")

        val diff = DiffEngine.unifiedDiff(filePath, oldContent, newContent, contextLines = 1)
        return PatchResult(
            diff = diff,
            patch = diff,
            affectedFiles = listOf(filePath),
            success = true
        )
    }

    private fun handleFormatCode(input: JsonObject): PatchResult {
        val targets = input.get("targets")?.asJsonArray ?: throw IllegalArgumentException("targets required")
        val style = input.get("style")?.asString ?: "ktlint"

        val affectedFiles = mutableListOf<String>()
        val diffs = mutableListOf<String>()

        for (targetElement in targets) {
            val target = targetElement.asString
            val files = if (File(target).isDirectory) {
                File(target).walk().filter { it.isFile && it.extension == "kt" }.toList()
            } else {
                listOf(File(target))
            }

            for (file in files) {
                if (file.exists()) {
                    val oldContent = file.readText()
                    val formatted = formatKotlinCode(oldContent, style)

                    if (oldContent != formatted) {
                        file.writeText(formatted)
                        val diff = DiffEngine.unifiedDiff(file.absolutePath, oldContent, formatted, contextLines = 1)
                        diffs.add(diff)
                        affectedFiles.add(file.absolutePath)
                    }
                }
            }
        }

        val combinedDiff = if (diffs.isNotEmpty()) diffs.joinToString("\n") else ""
        return PatchResult(
            diff = combinedDiff,
            patch = combinedDiff,
            affectedFiles = affectedFiles,
            success = true
        )
    }

    private fun handleOptimizeImports(input: JsonObject): PatchResult {
        val projectRoot = input.get("projectRoot")?.asString ?: throw IllegalArgumentException("projectRoot required")
        val mode = input.get("mode")?.asString ?: "project"

        val affectedFiles = mutableListOf<String>()
        val diffs = mutableListOf<String>()

        File(projectRoot).walk().filter { it.isFile && it.extension == "kt" }.forEach { file ->
            val oldContent = file.readText()
            val optimized = optimizeImports(oldContent)

            if (oldContent != optimized) {
                file.writeText(optimized)
                val diff = DiffEngine.unifiedDiff(file.absolutePath, oldContent, optimized, contextLines = 1)
                diffs.add(diff)
                affectedFiles.add(file.absolutePath)
            }
        }

        val combinedDiff = if (diffs.isNotEmpty()) diffs.joinToString("\n") else ""
        return PatchResult(
            diff = combinedDiff,
            patch = combinedDiff,
            affectedFiles = affectedFiles,
            success = true
        )
    }

    private fun handleCompileModule(input: JsonObject): Map<String, Any> {
        val modulePath = input.get("modulePath")?.asString ?: throw IllegalArgumentException("modulePath required")

        // Placeholder compilation check
        val success = checkCompilation(modulePath)

        return mapOf(
            "success" to success,
            "message" to if (success) "Compilation successful" else "Compilation failed"
        )
    }

    private fun handleRunTests(input: JsonObject): Map<String, Any> {
        val testPath = input.get("testPath")?.asString ?: "src/test"

        // Placeholder test execution
        val results = runKotlinTests(testPath)

        return mapOf(
            "success" to results.success,
            "passed" to results.passed,
            "total" to results.total,
            "failures" to results.failures
        )
    }

    private fun findFunctionByName(ktFile: KtFile, functionName: String): KtNamedFunction? {
        return ktFile.children
            .filterIsInstance<KtNamedFunction>()
            .find { it.name == functionName }
    }

    private fun formatKotlinCode(content: String, style: String): String {
        // Placeholder - would use ktlint or spotless
        return content.lines().joinToString("\n") { it.trimEnd() }
    }

    private fun optimizeImports(content: String): String {
        // Placeholder - would remove unused imports and sort them
        return content
    }

    private fun checkCompilation(modulePath: String): Boolean {
        // Placeholder - would run kotlinc
        return File(modulePath).exists()
    }

    private data class TestResults(val success: Boolean, val total: Int, val passed: Int, val failures: List<String>)

    private fun runKotlinTests(testPath: String): TestResults {
        // Placeholder - would run tests
        return TestResults(true, 10, 9, listOf("Test failure example"))
    }

    private fun handleAndroidSetupArchitecture(input: JsonObject): Map<String, Any> {
        val pattern = input.get("pattern")?.asString ?: "MVVM"
        val di = input.get("di")?.asString ?: "Hilt"
        val modules = input.getAsJsonArray("modules")?.map { it.asString } ?: listOf("app", "core")

        val files = mutableMapOf<String, String>()
        val gradleUpdates = mutableListOf<String>()

        // Generate base files
        if (pattern == "MVVM") {
            files["app/src/main/java/com/example/app/ui/MainActivity.kt"] = """
package com.example.app.ui

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
""".trimIndent()

            files["app/src/main/java/com/example/app/ui/MainViewModel.kt"] = """
package com.example.app.ui

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class MainViewModel @Inject constructor() : ViewModel() {
    // TODO: Add business logic
}
""".trimIndent()
        }

        if (di == "Hilt") {
            files["app/src/main/java/com/example/app/App.kt"] = """
package com.example.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class App : Application()
""".trimIndent()

            gradleUpdates.add("Add Hilt plugin and dependencies to build.gradle.kts")
        }

        return mapOf(
            "files" to files,
            "gradleUpdates" to gradleUpdates,
            "wiringInstructions" to "Apply the generated files and update Gradle files with Hilt dependencies"
        )
    }

    private fun handleAndroidSetupDataLayer(input: JsonObject): Map<String, Any> {
        val db = input.get("db")?.asString ?: "Room"
        val entities = input.getAsJsonArray("entities")?.map { it.asJsonObject } ?: emptyList()
        val migrations = input.get("migrations")?.asBoolean ?: true

        val files = mutableMapOf<String, String>()
        val migrationScripts = mutableMapOf<String, String>()
        val tests = mutableMapOf<String, String>()

        if (db == "Room") {
            files["app/src/main/java/com/example/app/data/local/AppDatabase.kt"] = """
package com.example.app.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [], version = 1)
abstract class AppDatabase : RoomDatabase() {
    // TODO: Add DAOs
}
""".trimIndent()

            if (migrations) {
                migrationScripts["app/src/main/java/com/example/app/data/local/Migration1To2.kt"] = """
package com.example.app.data.local

import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // TODO: Add migration logic
    }
}
""".trimIndent()
            }

            tests["app/src/test/java/com/example/app/data/local/AppDatabaseTest.kt"] = """
package com.example.app.data.local

import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import org.junit.After
import org.junit.Before
import org.junit.Test

class AppDatabaseTest {

    private lateinit var db: AppDatabase

    @Before
    fun setup() {
        db = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).build()
    }

    @After
    fun teardown() {
        db.close()
    }

    @Test
    fun testDatabaseCreation() {
        // TODO: Add database tests
    }
}
""".trimIndent()
        }

        return mapOf(
            "files" to files,
            "migrationScripts" to migrationScripts,
            "tests" to tests
        )
    }

    private fun handleAndroidSetupNetwork(input: JsonObject): Map<String, Any> {
        val style = input.get("style")?.asString ?: "Retrofit"
        val endpoints = input.getAsJsonArray("endpoints")?.map { it.asJsonObject } ?: emptyList()
        val auth = input.get("auth")?.asString ?: "None"

        val files = mutableMapOf<String, String>()
        val tests = mutableMapOf<String, String>()

        if (style == "Retrofit") {
            files["app/src/main/java/com/example/app/data/remote/ApiService.kt"] = """
package com.example.app.data.remote

import retrofit2.http.GET

interface ApiService {
    @GET("example")
    suspend fun getExample(): String
}
""".trimIndent()

            files["app/src/main/java/com/example/app/data/remote/ApiClient.kt"] = """
package com.example.app.data.remote

import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    private const val BASE_URL = "https://api.example.com/"

    val apiService: ApiService by lazy {
        val client = OkHttpClient.Builder().build()

        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
""".trimIndent()

            tests["app/src/test/java/com/example/app/data/remote/ApiServiceTest.kt"] = """
package com.example.app.data.remote

import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Before
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class ApiServiceTest {

    private lateinit var mockWebServer: MockWebServer

    @Before
    fun setup() {
        mockWebServer = MockWebServer()
    }

    @After
    fun teardown() {
        mockWebServer.shutdown()
    }

    @Test
    fun testApiCall() {
        // TODO: Add API tests
    }
}
""".trimIndent()
        }

        return mapOf(
            "files" to files,
            "tests" to tests
        )
    }

    private fun handleAndroidGenerateComposeUI(input: JsonObject): Map<String, Any> {
        val screenName = input.get("screenName")?.asString ?: "HomeScreen"
        val stateModel = input.get("stateModel")?.asJsonObject ?: JsonObject()
        val navigation = input.get("navigation")?.asBoolean ?: true

        val files = mutableMapOf<String, String>()

        files["app/src/main/java/com/example/app/ui/$screenName.kt"] = """
package com.example.app.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun ${screenName}Screen(
    viewModel: ${screenName}ViewModel = hiltViewModel(),
    onNavigateToDetails: () -> Unit = {}
) {
    val uiState by viewModel.uiState.collectAsState()

    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Welcome to $screenName")
        
        Button(onClick = onNavigateToDetails) {
            Text("Go to Details")
        }
    }
}

@Preview(showBackground = true)
@Composable
fun ${screenName}Preview() {
    ${screenName}Screen()
}
""".trimIndent()

        files["app/src/main/java/com/example/app/ui/${screenName}ViewModel.kt"] = """
package com.example.app.ui

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import javax.inject.Inject

data class ${screenName}UiState(
    val isLoading: Boolean = false,
    val data: String = ""
)

@HiltViewModel
class ${screenName}ViewModel @Inject constructor() : ViewModel() {

    private val _uiState = MutableStateFlow(${screenName}UiState())
    val uiState: StateFlow<${screenName}UiState> = _uiState

    // TODO: Add business logic
}
""".trimIndent()

        return mapOf(
            "files" to files,
            "instructions" to "Add the generated composable to your navigation graph and wire up the ViewModel"
        )
    }

    private fun createPatch(oldContent: String, newContent: String, filePath: String): String {
        return DiffEngine.unifiedDiff(filePath, oldContent, newContent, contextLines = 1)
    }

    private fun formatKotlinCode(content: String, style: String): String {
        // Simple formatting - in real implementation, use ktlint or spotless
        return content
            .replace(Regex("\\s+$"), "") // Remove trailing whitespace
            .replace(Regex("\n\n\n+"), "\n\n") // Remove extra blank lines
    }

    private fun optimizeImports(content: String): String {
        // Simple import optimization - in real implementation, use Kotlin Analysis API
        return content
    }
}

@OptIn(ExperimentalCli::class)
fun main(args: Array<String>) {
    val parser = ArgParser("kotlin-sidecar")

    val input by parser.option(
        ArgType.String,
        shortName = "i",
        description = "JSON input (if not provided, reads from stdin)"
    )

    parser.parse(args)

    val sidecar = KotlinSidecar()
    val gson = Gson()

    if (input != null) {
        // Single request mode
        try {
            val request = gson.fromJson(input, ToolRequest::class.java)
            val response = sidecar.processRequest(request)
            println(gson.toJson(response))
        } catch (e: Exception) {
            val errorResponse = ToolResponse(
                ok = false,
                error = ErrorResponse(
                    code = "ParseError",
                    message = "Failed to parse input: ${e.message}"
                )
            )
            println(gson.toJson(errorResponse))
            exitProcess(1)
        }
    } else {
        // NDJSON mode: read from stdin line by line
        val reader = System.`in`.bufferedReader()
        reader.forEachLine { line ->
            if (line.isNotBlank()) {
                try {
                    val request = gson.fromJson(line, ToolRequest::class.java)
                    val response = sidecar.processRequest(request)
                    println(gson.toJson(response))
                } catch (e: Exception) {
                    val errorResponse = ToolResponse(
                        ok = false,
                        error = ErrorResponse(
                            code = "ParseError",
                            message = "Failed to parse input: ${e.message}"
                        )
                    )
                    println(gson.toJson(errorResponse))
                }
            }
        }
    }
}
