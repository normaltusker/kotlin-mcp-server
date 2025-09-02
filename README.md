# Enterprise Kotlin Android MCP Server

A comprehensive Model Context Protocol (MCP) server that provides AI agents with enterprise-grade access to Kotlin-based Android development projects. This server enables context-aware assistance with advanced security, privacy compliance, AI integration, and comprehensive development tools.

---

## 📋 **Revision History**

### **Version 2.1** *(Current - August 2025)*
**Enhanced Release: Unified Intelligent Server**

#### 🎯 **Latest Improvements**
- **🧠 Intelligent Tool Management**: All 27 tools now use intelligent proxy system with LSP-like capabilities
- **🔄 Server Consolidation**: Unified into single `kotlin_mcp_server.py` with enhanced architecture
- **📁 Clean Architecture**: Archived redundant server versions for cleaner project structure
- **⚡ Enhanced Tool Exposure**: Complete tool suite properly exposed through intelligent management system
- **🛠️ Improved Tool Routing**: Smart delegation between native implementations and intelligent proxies

#### 🔧 **Architectural Changes**
- **Unified Server**: Single `kotlin_mcp_server.py` replaces multiple server versions
- **Intelligent Proxy System**: Tools without full implementations use smart proxies with AI enhancement
- **Clean File Structure**: Legacy servers archived in `archive/legacy-servers/`
- **Enhanced Tool Manager**: Integration with `IntelligentMCPToolManager` for advanced capabilities
- **Complete Tool Coverage**: All 32 tools properly exposed and functional

#### 📊 **Tool Implementation Status**
- **Fully Implemented**: 6 tools (format_code, run_lint, generate_docs, create_compose_component, setup_mvvm_architecture, security_hardening)
- **Legacy Integration**: 3 core tools (create_kotlin_file, gradle_build, analyze_project)
- **Intelligent Proxies**: 23 tools with smart fallback implementations
- **Total Available**: 32 tools with comprehensive Android development coverage

### **Version 2.0** *(August 2025)*
**Major Release: AI-Enhanced Modular Architecture**

#### 🎯 **Key Improvements**
- **🤖 AI Integration**: Transformed from template generator to AI-powered development assistant
- **🏗️ Modular Architecture**: Refactored monolithic structure into 6 specialized modules 
- **🌍 Dynamic Configuration**: Eliminated all hardcoded paths for cross-platform portability
- **⚡ Enhanced Tools**: Expanded from 30 to 31 tools with AI-enhanced implementations
- **🛡️ Security Hardening**: Added configurable audit trails and compliance monitoring
- **📦 Zero-Config Setup**: Intelligent installer with automatic environment detection

#### 🔧 **Technical Changes**
- **Modular Design**: Split into `ai/`, `android/`, `gradle/`, `security/`, `testing/`, `utils/` modules
- **AI-Powered Code Generation**: Leverages calling LLM for production-ready code (no TODOs)
- **Environment Variable Support**: All configurations now use dynamic environment variables
- **Cross-Platform Paths**: Universal `~` notation replaces OS-specific hardcoded paths
- **Enhanced Error Handling**: Comprehensive validation and graceful failure recovery
- **Performance Optimization**: Streamlined tool execution with better resource management

#### 📊 **Migration Impact**
- **Tools**: 30 → 32 tools (107% feature parity + enhancements)
- **File Size**: Optimized modular structure vs. monolithic approach
- **Configuration**: Zero manual path configuration required
- **Compatibility**: Maintains full backward compatibility with existing setups

### **Version 1.0** *(Legacy - Pre-August 2025)*
**Initial Release: Template-Based Code Generator**
- ✅ Basic MCP server with 30 tools
- ✅ Template-based Kotlin/Android code generation
- ✅ Manual configuration with hardcoded paths
- ✅ Monolithic architecture
- ✅ Basic security and compliance features

---

## 🌟 **Enterprise Features Overview**

### 🔒 **Security & Privacy Compliance**
- **GDPR Compliance** - Complete implementation with consent management, data portability, right to erasure
- **HIPAA Compliance** - Healthcare-grade security with audit logging, access controls, encryption
- **Data Encryption** - AES-256 encryption with PBKDF2 key derivation for sensitive data
- **Audit Trails** - Comprehensive logging with compliance flags and security event tracking
- **Privacy by Design** - Built-in privacy protection for all operations

### 🤖 **AI/ML Integration**
- **Local LLM Support** - Ollama, LocalAI, and self-hosted transformers
- **External LLM APIs** - OpenAI GPT-4, Anthropic Claude, custom endpoints
- **AI-Powered Code Analysis** - Security, performance, and complexity analysis
- **Intelligent Code Generation** - Context-aware Kotlin/Android code creation
- **ML Model Integration** - TensorFlow Lite, ONNX, PyTorch Mobile for Android apps

### 📁 **Advanced File Management**
- **Enterprise File Operations** - Backup, restore, sync, encrypt, decrypt with audit trails
- **Real-time Synchronization** - File system watchers with automatic sync
- **Cloud Storage Integration** - AWS S3, Google Cloud, Azure with end-to-end encryption
- **Smart File Classification** - Automatic sensitive data detection and encryption
- **Version Control** - Git-aware operations with conflict resolution

### 🌐 **External API Integration**
- **Comprehensive Auth Support** - API Keys, OAuth 2.0, JWT, Basic Auth
- **Security Features** - Rate limiting, request logging, response validation
- **Real-time Monitoring** - API usage metrics, performance tracking, cost analysis
- **Compliance Validation** - GDPR/HIPAA compliant API handling

### 🏗️ **Advanced Android Development**
- **Architecture Patterns** - MVVM, Clean Architecture, Dependency Injection
- **Modern UI Development** - Jetpack Compose, custom views, complex layouts
- **Database Integration** - Room with encryption, migration handling
- **Network Layer** - Retrofit, GraphQL, WebSocket support
- **Testing Framework** - Comprehensive test generation and execution

---

## 🚀 **Quick Start & Installation**

### ✨ **Upgrade to V2.0 Highlights**

**🤖 AI-Enhanced Development**: Now leverages your AI assistant for production-ready code generation instead of basic templates!

**Before (V1.0):**
- ❌ Template-based code with TODO placeholders
- ❌ Manual path editing in config files
- ❌ Monolithic architecture (single large file)
- ❌ Hardcoded paths and user-specific configurations
- ❌ 30 basic tools with limited AI integration

**After (V2.0):**
- ✅ **AI-Powered Code Generation**: Complete, context-aware implementations
- ✅ **Zero-Configuration Setup**: `python3 install.py` handles everything
- ✅ **Modular Architecture**: Clean, maintainable 6-module structure
- ✅ **Dynamic Configuration**: Cross-platform with environment variables
- ✅ **31 Enhanced Tools**: AI-integrated with intelligent error handling

### 📋 **System Requirements**

- **Python 3.8+** (3.9+ recommended)
- **pip** (Python package manager)
- **Git** (for cloning repository)
- **IDE with MCP support** (VS Code, JetBrains IDEs, Claude Desktop)

### 🔧 **Installation Steps**

#### **1. Clone Repository**
```bash
git clone <your-repo-url>
cd kotlin-mcp-server
```

#### **2. Automated Installation & Configuration**

The project includes an enhanced installation script that handles all configuration automatically:

```bash
# Interactive installation (recommended for first-time users)
python3 install.py

# Non-interactive installation with specific configuration
python3 install.py [install_type] [project_path] [server_name] [use_env_vars]

# Show all available options
python3 install.py --help
```

**Installation Types:**
- `1` - **Portable**: Run directly from project directory
- `2` - **System**: Install command to PATH (`kotlin-android-mcp`)  
- `3` - **Module**: Enable `python -m kotlin_mcp_server`

**Configuration Examples:**

```bash
# Interactive setup (asks for your preferences)
python3 install.py 1

# Portable with your Android project path (replace with actual path)
python3 install.py 1 ~/AndroidStudioProjects/MyApp

# System installation with dynamic environment variables
python3 install.py 2 none my-android-server true

# Module installation with custom server name
python3 install.py 3 /path/to/project kotlin-dev false
```

**What the installer does:**
- ✅ **Installs all Python dependencies** from `requirements.txt`
- ✅ **Creates platform-specific config files** (Claude, VS Code, generic)
- ✅ **Sets up proper file permissions** for scripts
- ✅ **Configures environment variables** based on your choices
- ✅ **Eliminates manual path updates** in configuration files
- ✅ **Provides clear integration instructions** for your setup

#### **3. Manual Installation (Alternative)**

If you prefer manual installation:

```bash
# Install core dependencies
pip install -r requirements.txt

# Optional: Install AI/ML dependencies for advanced features
pip install openai anthropic transformers torch

# Verify installation
python3 -c "import kotlin_mcp_server; print('✅ Installation successful')"
```

**Key Dependencies Installed:**
- **Core MCP:** `python-dotenv`, `pydantic`
- **Security:** `cryptography`, `bcrypt`, `PyJWT`
- **Database:** `aiosqlite`, `sqlalchemy`
- **HTTP Clients:** `aiohttp`, `httpx`
- **File Management:** `aiofiles`, `watchdog`
- **Testing:** `pytest`, `pytest-asyncio`, `coverage`
- **Code Quality:** `black`, `flake8`, `pylint`, `mypy`
- **Security Tools:** `bandit`, `safety`

#### **4. V2.0 Architecture & Tool Enhancements**

**🏗️ Modular Architecture Design**

The V2.0 release introduces a clean, maintainable modular structure:

```
kotlin-mcp-server/
├── kotlin_mcp_server.py      # Main server (32 AI-enhanced tools)
├── ai/
│   ├── llm_integration.py    # AI assistant integration
│   └── code_enhancement.py   # AI-powered code generation
├── android/
│   ├── project_manager.py    # Project structure management  
│   └── manifest_utils.py     # Android manifest operations
├── gradle/
│   ├── build_system.py       # Gradle build automation
│   └── dependency_manager.py # Dependency resolution
├── security/
│   ├── compliance.py         # GDPR/HIPAA compliance
│   └── encryption.py         # Data protection
├── testing/
│   └── test_generator.py     # Automated test creation
└── utils/
    ├── file_operations.py    # Enhanced file management
    └── security.py           # Audit trails & logging
```

**🤖 AI-Enhanced Tool Capabilities**

| Tool Category | V1.0 (Templates) | V2.0 (AI-Enhanced) |
|---------------|-------------------|-------------------|
| **Code Generation** | Basic templates with TODOs | Production-ready, context-aware implementations |
| **Architecture Patterns** | Skeleton code | Complete MVVM, Clean Architecture patterns |
| **UI Components** | Static layouts | Dynamic Jetpack Compose with business logic |
| **Database Operations** | Schema templates | Full Room implementation with migrations |
| **Testing** | Test stubs | Comprehensive test suites with edge cases |
| **Security** | Basic validation | Enterprise-grade security with compliance |

**⚡ Performance & Reliability Improvements**

- **31 Tools** (vs 30 in V1.0) with enhanced AI integration
- **Error Recovery**: Graceful handling of AI service interruptions
- **Context Awareness**: Tools understand project structure and requirements
- **Resource Optimization**: Efficient memory usage and faster execution
- **Cross-Platform Support**: Universal configuration system

#### **5. IDE Integration Setup**

After installation, the script generates ready-to-use configuration files:

- **`mcp_config_claude.json`** - For Claude Desktop
- **`mcp_config_vscode.json`** - For VS Code and Cursor  
- **`mcp_config.json`** - For other MCP clients

**Integration Instructions:**

🔹 **Claude Desktop**: Copy content from `mcp_config_claude.json` to:
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

🔹 **VS Code/Cursor**: Add to your VS Code `settings.json`:
   ```json
   {
     "mcp.server.configFiles": [
       "/absolute/path/to/mcp_config_vscode.json"
     ]
   }
   ```

🔹 **Other IDEs**: Use `mcp_config.json` with your MCP client

#### **5. Environment Configuration (Advanced)**

For advanced users who need custom environment setup:
Create a `.env` file in the project root (only needed for advanced configurations):

```bash
# Copy the example file and customize
cp .env.example .env

# Edit with your settings
nano .env  # or your preferred editor
```

**Optional Variables:**
```bash
# Security (generate strong password)
MCP_ENCRYPTION_PASSWORD=$(openssl rand -base64 32)
COMPLIANCE_MODE=gdpr,hipaa

# Optional: AI Integration
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**💡 Note**: The installation script automatically configures project paths and server settings, so manual environment configuration is only needed for advanced features like AI integration or custom security settings.

#### **6. Install Required IDE Extensions/Plugins**
See the [Plugin Requirements](#-required-pluginsextensions) section below for IDE-specific extensions.

#### **7. Test Installation**
```bash
# Test the server with your configured setup
# If you used a fixed project path during installation:
python3 kotlin_mcp_server.py

# If you're using dynamic/environment variables:
python3 kotlin_mcp_server.py /path/to/android/project

# For system installation:
kotlin-android-mcp

# For module installation:
python3 -m kotlin_mcp_server

# Validate configuration (optional)
python3 validate_config.py

# Run comprehensive tests (optional)
python test_mcp_comprehensive.py

# Test VS Code bridge server (optional)
python3 vscode_bridge.py &
sleep 2
curl http://localhost:8080/health
# Should return: {"status": "healthy", ...}
kill %1  # Stop background bridge server
```

### ⚡ **Quick Setup Commands**
```bash
# Complete setup with one command (interactive)
python3 install.py

# Quick setup for development environment
make setup-dev

# Quick validation
make dev-check

# Full quality pipeline
make ci

# Test VS Code bridge server (optional)
python3 vscode_bridge.py --test-mode
```

### 🎯 **Installation Summary**

The enhanced installation process has **eliminated the need for manual configuration**:

✅ **Before (Manual)**: Users had to manually edit config files, find paths, update environment variables  
✅ **After (Automated)**: One command creates everything ready-to-use

**Key Improvements:**
- 🚀 **Zero Manual Configuration**: No more path updates or variable editing
- 🎛️ **Interactive & Non-Interactive**: Works in both modes for all users
- 🔧 **Platform-Specific Configs**: Generates optimized files for each IDE/client
- 📋 **Clear Instructions**: Provides exact integration steps for your setup
- ✨ **Smart Defaults**: Handles environment variables intelligently

### 🐳 **Docker Deployment (Optional)**

For containerized deployment, the project includes comprehensive Docker support:

#### **Quick Docker Setup**

```bash
# 1. Validate Docker configuration
python3 validate_docker.py

# 2. Build and run with the setup script
./docker-setup.sh build
./docker-setup.sh start

# 3. Or use Docker Compose directly
docker-compose up -d kotlin-mcp-server
```

#### **Docker Features**

- 🔒 **Security**: Non-root user, minimal attack surface
- 📦 **Optimized**: Multi-stage builds, layer caching
- 🔍 **Health Checks**: Automatic container health monitoring
- 🛠️ **Development**: Volume mounts for live development
- 🚀 **Production**: Daemon mode for production deployment

#### **Available Commands**

```bash
./docker-setup.sh build              # Build the image
./docker-setup.sh start              # Interactive development
./docker-setup.sh daemon [path]      # Production daemon mode
./docker-setup.sh logs               # View container logs
./docker-setup.sh shell              # Open container shell
./docker-setup.sh test               # Run tests in container
./docker-setup.sh clean              # Clean up resources
```

**For detailed Docker setup instructions, see [DOCKER_SETUP.md](DOCKER_SETUP.md)**

---

## 🎯 **Prove-It: Generate Real Android Apps**

**Ready to see the system generate complete, production-ready Android apps?** Follow these steps to witness the full E2E workflow:

### 🚀 **Quick Start: Generate Your First App**

```bash
# 1. Build the Kotlin sidecar (creates fat JAR)
make sidecar

# 2. Generate complete Android app with all features
make e2e

# 3. Your APK appears here:
ls -la e2e/sampleapp/app/build/outputs/apk/debug/app-debug.apk
```

**What you get:**
- ✅ **Complete Gradle project** (Kotlin, Compose, Hilt, MVVM)
- ✅ **Working Android app** with HomeScreen + DetailsScreen
- ✅ **Room database** with entities and DAOs
- ✅ **Retrofit network layer** with API service
- ✅ **Unit tests** that pass (Robolectric + JVM tests)
- ✅ **APK ready to install** on device/emulator

### 🔧 **Available Commands**

```bash
# Build Kotlin sidecar JAR
make sidecar

# Generate complete Android app
make e2e

# Format and optimize code
make fix

# Run detekt static analysis
make detekt

# Run spotless code formatting check
make spotless

# Clean all artifacts
make clean
```

### 📊 **Generated App Features**

The generated `e2e/sampleapp` includes:

**🏗️ Architecture:**
- MVVM pattern with ViewModels
- Hilt dependency injection
- Clean Architecture principles

**🎨 UI/UX:**
- Jetpack Compose screens
- Material3 design
- Navigation between screens

**💾 Data Layer:**
- Room database with entities
- Repository pattern
- Migration skeletons

**🌐 Network:**
- Retrofit API client
- OkHttp interceptors
- Error handling

**🧪 Testing:**
- Unit tests for ViewModels
- DAO tests with Robolectric
- API service tests

**📱 Build:**
- Debug APK generation
- Lint/format checks
- Gradle build optimization

### ⚙️ **Environment Variables**

```bash
# Sidecar configuration
MCP_SIDECAR_CMD=["java", "-jar", "kotlin-sidecar/build/libs/kotlin-sidecar.jar"]

# Performance tuning
MCP_API_TIMEOUT_MS=3000
MCP_RATE_LIMIT_QPS=10

# Build settings
ANDROID_SDK_ROOT=/path/to/android/sdk
JAVA_HOME=/path/to/jdk17
```

### 🔍 **Troubleshooting**

**Gradle build fails:**
```bash
# Ensure Android SDK is installed and ANDROID_SDK_ROOT is set
export ANDROID_SDK_ROOT=/path/to/android/sdk

# Clean and rebuild
make clean && make e2e
```

**Sidecar connection issues:**
```bash
# Check if JAR was built
ls -la kotlin-sidecar/build/libs/kotlin-sidecar.jar

# Test sidecar directly
java -jar kotlin-sidecar/build/libs/kotlin-sidecar.jar
```

**APK not generated:**
```bash
# Check build logs
cd e2e/sampleapp && ./gradlew assembleDebug --info

# Ensure JDK 17 is used
java -version  # Should show Java 17
```

### 📈 **Performance Benchmarks**

The system is optimized for:
- **Sidecar startup**: < 2 seconds
- **Code generation**: < 5 seconds per component
- **Build time**: < 30 seconds for debug APK
- **Test execution**: < 10 seconds for unit tests

### 🎉 **Success Indicators**

When everything works correctly:
- ✅ `kotlin-sidecar.jar` builds successfully
- ✅ `e2e/sampleapp` directory created with full project
- ✅ `./gradlew assembleDebug` completes without errors
- ✅ APK file exists: `app/build/outputs/apk/debug/app-debug.apk`
- ✅ `./gradlew testDebugUnitTest` passes tests
- ✅ No TODO placeholders in generated code
- ✅ All lint/format checks pass

**🎯 The generated app is production-ready and can be opened in Android Studio immediately!**

---

## � **Migration from V1.0 to V2.0**

### **⚡ Quick Migration Steps**

If you have an existing V1.0 installation:

1. **Backup Current Setup**:
   ```bash
   # Backup your existing configuration
   cp mcp_config*.json ~/backup/
   ```

2. **Update to V2.0**:
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Run V2.0 installer
   python3 install.py 1
   ```

3. **Verify Migration**:
   ```bash
   # Test the new modular architecture
   python3 -c "from kotlin_mcp_server import KotlinMCPServer; print('✅ V2.0 Ready!')"
   ```

### **🔍 What's Automatically Migrated**

- ✅ **All 30 original tools** preserved with enhanced AI capabilities
- ✅ **Configuration files** updated with dynamic environment variables
- ✅ **Project paths** converted to cross-platform format
- ✅ **Dependencies** updated to latest versions
- ✅ **Security settings** enhanced with new compliance features

### **⚠️ Migration Notes**

- **Backward Compatibility**: V2.0 maintains full compatibility with V1.0 project structures
- **Enhanced Output**: Code generation now produces complete implementations instead of templates
- **New Environment Variables**: Optional new configuration options (see `.env.example`)
- **Modular Structure**: Internal architecture improved (no user action needed)

---

## 🏗️ **Project Root Resolution Policy**

### **Overview**
All tools in the Kotlin MCP Server have been refactored to work exclusively on the user's project workspace, never on the MCP server's current working directory. This ensures safe, predictable tool behavior and prevents accidental modifications outside your project.

### **Path Resolution Priority**
Tools resolve the project root in this order:

1. **Explicit Input**: `project_root` or `projectRoot` parameter
2. **Environment Variables**: `PROJECT_PATH` or `WORKSPACE_PATH`
3. **IDE Metadata**: Workspace root from MCP client (VS Code, Cursor, etc.)
4. **Fail-Safe**: Tools will error rather than use server CWD

### **Input Synonyms**
Tools accept both camelCase and snake_case parameter names:

```json
// Both formats work identically
{
  "project_root": "/path/to/project",
  "file_path": "src/main.kt",
  "build_tool": "gradle",
  "skip_tests": false
}

{
  "projectRoot": "/path/to/project", 
  "filePath": "src/main.kt",
  "buildTool": "gradle",
  "skipTests": false
}
```

### **IDE Integration Defaults**
When using IDE extensions (VS Code, Cursor), tools automatically detect:

- **Workspace Root**: Active workspace directory
- **Active File**: Currently open file for file-based operations
- **Selection**: Text selection for refactoring operations

### **Security Safeguards**
- **Path Traversal Protection**: All file paths validated to be under project root
- **Server CWD Guard**: Runtime checks prevent accidental server directory operations
- **Audit Logging**: All tool operations logged with project context

### **Example Tool Calls**

**With Explicit Project Root:**
```json
{
  "tool": "buildAndTest",
  "input": {
    "project_root": "/Users/dev/MyAndroidApp",
    "buildTool": "gradle",
    "skipTests": false
  }
}
```

**With Environment Variable:**
```bash
export PROJECT_PATH=/Users/dev/MyAndroidApp
# Tool calls without project_root will use environment
```

**IDE Auto-Detection:**
```json
{
  "tool": "analyzeCodeQuality",
  "input": {
    "scope": "project",
    "ruleset": "all"
  }
}
// Uses active workspace automatically
```

### **Error Handling**
Tools provide clear errors when project root cannot be resolved:

```json
{
  "success": false,
  "error": "ProjectRootRequired: pass `project_root` or set env PROJECT_PATH",
  "error_type": "ProjectRootRequired"
}
```

---

## 📚 **Comprehensive Usage Guide**

### 🛠 **Complete Tool Reference**

The Kotlin MCP Server provides 31 comprehensive tools for Android development, organized by category:

#### **Core Development Tools**

##### 1. `gradle_build` - Build Android Projects
Executes Gradle build tasks for your Android project.

```json
{
  "name": "gradle_build",
  "arguments": {
    "task": "assembleDebug",
    "clean_build": false,
    "parallel": true
  }
}
```
**Parameters:**
- `task` (string): Gradle task to execute (e.g., "assembleDebug", "build", "test")
- `clean_build` (boolean, optional): Whether to clean before building
- `parallel` (boolean, optional): Enable parallel execution

**Usage Examples:**
```bash
# Build debug APK
{"name": "gradle_build", "arguments": {"task": "assembleDebug"}}

# Clean and build release
{"name": "gradle_build", "arguments": {"task": "assembleRelease", "clean_build": true}}

# Run all tests
{"name": "gradle_build", "arguments": {"task": "test"}}
```

##### 2. `run_tests` - Execute Test Suites
Runs unit tests, integration tests, or UI tests with comprehensive reporting.

```json
{
  "name": "run_tests",
  "arguments": {
    "test_type": "unit",
    "test_class": "UserRepositoryTest",
    "generate_report": true
  }
}
```
**Parameters:**
- `test_type` (string): "unit", "integration", "ui", or "all"
- `test_class` (string, optional): Specific test class to run
- `generate_report` (boolean, optional): Generate HTML test report

##### 3. `create_kotlin_file` - Generate Kotlin Files
Creates structured Kotlin files with proper package declaration and imports.

```json
{
  "name": "create_kotlin_file",
  "arguments": {
    "file_path": "src/main/kotlin/com/example/User.kt",
    "class_name": "User",
    "class_type": "data_class",
    "properties": ["id: String", "name: String", "email: String"],
    "package_name": "com.example.model"
  }
}
```
**Parameters:**
- `file_path` (string): Relative path for the new file
- `class_name` (string): Name of the main class
- `class_type` (string): "class", "data_class", "sealed_class", "object", "interface"
- `properties` (array, optional): List of properties for data classes
- `package_name` (string, optional): Package declaration

##### 4. `create_layout_file` - Generate XML Layouts
Creates Android XML layout files with proper structure.

```json
{
  "name": "create_layout_file",
  "arguments": {
    "file_path": "src/main/res/layout/activity_main.xml",
    "layout_type": "activity",
    "root_element": "LinearLayout",
    "include_common_attributes": true
  }
}
```

##### 5. `analyze_project` - Project Analysis
Provides comprehensive analysis of your Android project structure, dependencies, and architecture.

```json
{
  "name": "analyze_project",
  "arguments": {
    "analysis_type": "architecture",
    "include_dependencies": true,
    "check_best_practices": true
  }
}
```
**Analysis Types:**
- `architecture`: Overall project structure and patterns
- `dependencies`: Gradle dependencies and versions
- `security`: Security vulnerabilities and best practices
- `performance`: Performance bottlenecks and optimizations

##### 6. `format_code` - Code Formatting
Formats Kotlin code according to style guidelines.

```json
{
  "name": "format_code",
  "arguments": {
    "file_path": "src/main/kotlin/MainActivity.kt",
    "style_guide": "ktlint"
  }
}
```

##### 7. `run_lint` - Static Code Analysis
Runs lint analysis to detect code issues.

```json
{
  "name": "run_lint",
  "arguments": {
    "lint_tool": "detekt",
    "fail_on_warnings": false,
    "generate_report": true
  }
}
```

##### 8. `generate_docs` - Documentation Generation
Generates project documentation in various formats.

```json
{
  "name": "generate_docs",
  "arguments": {
    "doc_type": "kdoc",
    "output_format": "html",
    "include_private": false
  }
}
```

#### **UI Development Tools**

##### 9. `create_compose_component` - Jetpack Compose Components
Generates Jetpack Compose UI components with best practices.

```json
{
  "name": "create_compose_component",
  "arguments": {
    "component_name": "UserCard",
    "component_type": "composable",
    "file_path": "src/main/kotlin/ui/components/UserCard.kt",
    "parameters": [
      "user: User",
      "onClick: () -> Unit"
    ],
    "include_preview": true,
    "material_design": "material3"
  }
}
```
**Component Types:**
- `composable`: Standard composable function
- `stateful`: Composable with internal state
- `stateless`: Pure UI composable
- `layout`: Layout composable with children

##### 10. `create_custom_view` - Custom Android Views
Creates custom View classes with proper lifecycle management.

```json
{
  "name": "create_custom_view",
  "arguments": {
    "view_name": "CircularProgressView",
    "base_class": "View",
    "file_path": "src/main/kotlin/ui/views/CircularProgressView.kt",
    "custom_attributes": [
      {"name": "progressColor", "type": "color"},
      {"name": "strokeWidth", "type": "dimension"}
    ]
  }
}
```

#### **Architecture & Pattern Tools**

##### 11. `setup_mvvm_architecture` - MVVM Implementation
Sets up complete MVVM architecture with ViewModel, Repository, and UI layers.

```json
{
  "name": "setup_mvvm_architecture",
  "arguments": {
    "feature_name": "UserProfile",
    "package_name": "com.example.userprofile",
    "include_repository": true,
    "include_use_cases": true,
    "state_management": "compose"
  }
}
```
**Generated Files:**
- ViewModel with state management
- Repository with data source abstraction
- Use cases for business logic
- UI composables or fragments
- State classes and sealed classes for events

##### 12. `setup_dependency_injection` - DI Framework Setup
Configures dependency injection using Hilt or Dagger.

```json
{
  "name": "setup_dependency_injection",
  "arguments": {
    "di_framework": "hilt",
    "modules": ["DatabaseModule", "NetworkModule", "RepositoryModule"],
    "application_class": "MyApplication"
  }
}
```

##### 13. `setup_room_database` - Database Setup
Creates Room database implementation with entities, DAOs, and migrations.

```json
{
  "name": "setup_room_database",
  "arguments": {
    "database_name": "AppDatabase",
    "entities": [
      {
        "name": "User",
        "fields": [
          {"name": "id", "type": "String", "primaryKey": true},
          {"name": "name", "type": "String"},
          {"name": "email", "type": "String"}
        ]
      }
    ],
    "version": 1,
    "enable_encryption": true
  }
}
```

##### 14. `setup_retrofit_api` - Network Layer
Sets up Retrofit API interfaces with proper error handling and interceptors.

```json
{
  "name": "setup_retrofit_api",
  "arguments": {
    "base_url": "https://api.example.com/",
    "endpoints": [
      {
        "name": "getUser",
        "method": "GET",
        "path": "users/{id}",
        "response_type": "User"
      }
    ],
    "include_interceptors": ["logging", "auth", "retry"],
    "enable_cache": true
  }
}
```

#### **Security & Compliance Tools**

##### 15. `encrypt_sensitive_data` - Data Encryption
Encrypts sensitive data using industry-standard encryption.

```json
{
  "name": "encrypt_sensitive_data",
  "arguments": {
    "data": "Patient: John Doe, SSN: 123-45-6789",
    "data_type": "phi",
    "compliance_level": "hipaa",
    "encryption_algorithm": "AES-256"
  }
}
```

##### 16. `implement_gdpr_compliance` - GDPR Implementation
Implements complete GDPR compliance framework.

```json
{
  "name": "implement_gdpr_compliance",
  "arguments": {
    "package_name": "com.example.app",
    "features": [
      "consent_management",
      "data_portability",
      "right_to_erasure",
      "privacy_policy",
      "data_breach_notification"
    ],
    "supported_languages": ["en", "de", "fr"],
    "include_ui": true
  }
}
```
**Generated Components:**
- Consent management UI and logic
- Data export functionality
- User data deletion workflows
- Privacy policy templates
- Audit logging system

##### 17. `implement_hipaa_compliance` - HIPAA Implementation
Implements HIPAA-compliant security measures.

```json
{
  "name": "implement_hipaa_compliance",
  "arguments": {
    "package_name": "com.healthcare.app",
    "features": [
      "audit_logging",
      "access_controls",
      "encryption",
      "secure_messaging",
      "risk_assessment"
    ],
    "minimum_password_strength": "high",
    "session_timeout": 900
  }
}
```

##### 18. `setup_secure_storage` - Secure Data Storage
Configures encrypted storage for sensitive data.

```json
{
  "name": "setup_secure_storage",
  "arguments": {
    "storage_type": "room_encrypted",
    "package_name": "com.example.app",
    "data_classification": "restricted",
    "key_management": "android_keystore"
  }
}
```

#### **AI/ML Integration Tools**

##### 19. `query_llm` - Language Model Queries
Queries local or remote language models for code assistance.

```json
{
  "name": "query_llm",
  "arguments": {
    "prompt": "Generate a Kotlin data class for User with validation",
    "llm_provider": "local",
    "model": "codellama",
    "privacy_mode": true,
    "max_tokens": 1000,
    "temperature": 0.2
  }
}
```
**Supported Providers:**
- `local`: Ollama, LocalAI
- `openai`: GPT-4, GPT-3.5
- `anthropic`: Claude models
- `custom`: Custom API endpoints

##### 20. `analyze_code_with_ai` - AI Code Analysis
Uses AI to analyze code for various aspects.

```json
{
  "name": "analyze_code_with_ai",
  "arguments": {
    "file_path": "src/main/kotlin/UserManager.kt",
    "analysis_type": "security",
    "use_local_model": true,
    "detailed_report": true
  }
}
```
**Analysis Types:**
- `security`: Security vulnerabilities and best practices
- `performance`: Performance optimization suggestions
- `bugs`: Potential bug detection
- `style`: Code style improvements
- `complexity`: Code complexity analysis
- `maintainability`: Maintainability assessment

##### 21. `generate_code_with_ai` - AI Code Generation
Generates code using AI based on natural language descriptions.

```json
{
  "name": "generate_code_with_ai",
  "arguments": {
    "description": "Login screen with biometric authentication and error handling",
    "code_type": "compose_screen",
    "framework": "compose",
    "compliance_requirements": ["gdpr"],
    "include_tests": true,
    "style_guide": "material3"
  }
}
```

#### **File Management Tools**

##### 22. `manage_project_files` - Advanced File Operations
Performs comprehensive file management operations.

```json
{
  "name": "manage_project_files",
  "arguments": {
    "operation": "backup",
    "include_build_files": false,
    "compression": "zip",
    "encryption": true,
    "backup_location": "/path/to/backup",
    "exclude_patterns": ["*.tmp", "build/", ".gradle/"]
  }
}
```
**Operations:**
- `backup`: Create encrypted backups
- `restore`: Restore from backup
- `sync`: Synchronize with cloud storage
- `encrypt`: Encrypt sensitive files
- `decrypt`: Decrypt files (with proper authorization)
- `organize`: Organize files by type/category

##### 23. `setup_cloud_sync` - Cloud Storage Integration
Configures cloud storage synchronization with encryption.

```json
{
  "name": "setup_cloud_sync",
  "arguments": {
    "cloud_provider": "aws_s3",
    "bucket_name": "my-app-backup",
    "encryption_in_transit": true,
    "encryption_at_rest": true,
    "sync_frequency": "hourly",
    "compliance_mode": "gdpr"
  }
}
```

#### **API Integration Tools**

##### 24. `setup_external_api` - API Configuration
Sets up external API integrations with security and monitoring.

```json
{
  "name": "setup_external_api",
  "arguments": {
    "api_name": "PaymentAPI",
    "base_url": "https://api.payment.com/v1/",
    "auth_type": "oauth2",
    "auth_config": {
      "client_id": "your_client_id",
      "scopes": ["payments", "users"]
    },
    "rate_limiting": {
      "requests_per_minute": 100,
      "burst_limit": 10
    },
    "security_features": ["request_signing", "response_validation"],
    "monitoring": true
  }
}
```

##### 25. `call_external_api` - API Calls
Makes secured API calls with comprehensive monitoring.

```json
{
  "name": "call_external_api",
  "arguments": {
    "api_name": "PaymentAPI",
    "endpoint": "/charges",
    "method": "POST",
    "data": {
      "amount": 1000,
      "currency": "USD",
      "description": "Test payment"
    },
    "headers": {
      "Content-Type": "application/json"
    },
    "timeout": 30,
    "retry_config": {
      "max_retries": 3,
      "backoff_strategy": "exponential"
    }
  }
}
```

#### **Testing Tools**

##### 26. `generate_unit_tests` - Unit Test Generation
Generates comprehensive unit tests for Kotlin classes.

```json
{
  "name": "generate_unit_tests",
  "arguments": {
    "file_path": "src/main/kotlin/UserRepository.kt",
    "test_framework": "junit5",
    "mocking_framework": "mockk",
    "include_edge_cases": true,
    "test_coverage_target": 90
  }
}
```

##### 27. `setup_ui_testing` - UI Test Configuration
Sets up UI testing framework with Espresso or Compose testing.

```json
{
  "name": "setup_ui_testing",
  "arguments": {
    "testing_framework": "compose",
    "include_accessibility_tests": true,
    "include_screenshot_tests": true,
    "test_data_setup": "in_memory_database"
  }
}
```

#### **Git Tools**

##### 28. `gitStatus` - Git Repository Status
Get comprehensive Git repository status including branch, changes, and ahead/behind counts.

```json
{
  "name": "gitStatus",
  "arguments": {}
}
```
**Returns:**
- Current branch name
- List of changed files with status
- Ahead/behind counts relative to remote
- Whether repository has uncommitted changes

##### 29. `gitSmartCommit` - Intelligent Commit Messages
Create conventional commit messages based on code changes analysis.

```json
{
  "name": "gitSmartCommit",
  "arguments": {}
}
```
**Features:**
- Analyzes changed files to determine commit type
- Generates conventional commit message
- Automatically stages changes
- Supports feat, fix, docs, refactor, test types

##### 30. `gitCreateFeatureBranch` - Safe Branch Creation
Create feature branches with validation and naming conventions.

```json
{
  "name": "gitCreateFeatureBranch",
  "arguments": {
    "branchName": "user-authentication"
  }
}
```
**Features:**
- Creates `feature/branch-name` format
- Validates branch name format
- Checks for existing branches
- Switches to new branch automatically

##### 31. `gitMergeWithResolution` - Intelligent Merge
Attempt merge with conflict resolution and advice.

```json
{
  "name": "gitMergeWithResolution",
  "arguments": {
    "targetBranch": "main"
  }
}
```
**Features:**
- Attempts automatic merge
- Provides conflict resolution suggestions
- Returns structured conflict hunks
- Offers merge strategy advice

#### **External API Tools**

##### 32. `apiCallSecure` - Secure API Calls
Make authenticated API calls with monitoring and compliance.

```json
{
  "name": "apiCallSecure",
  "arguments": {
    "apiName": "github",
    "endpoint": "/repos/owner/repo/issues",
    "method": "GET",
    "auth": {
      "type": "bearer",
      "token": "ghp_..."
    }
  }
}
```
**Features:**
- Multiple authentication types (Bearer, API Key, OAuth, Basic)
- Automatic retries with backoff
- Request/response monitoring
- Compliance validation

##### 33. `apiMonitorMetrics` - API Metrics Monitoring
Get real-time API usage metrics and performance data.

```json
{
  "name": "apiMonitorMetrics",
  "arguments": {
    "apiName": "github",
    "windowMinutes": 60
  }
}
```
**Returns:**
- Request count and success rate
- Average latency
- Error counts
- Windowed metrics (1m to 7d)

##### 34. `apiValidateCompliance` - API Compliance Validation
Validate API usage against GDPR/HIPAA compliance rules.

```json
{
  "name": "apiValidateCompliance",
  "arguments": {
    "apiName": "payment-api",
    "complianceType": "gdpr"
  }
}
```
**Validates:**
- Data handling practices
- Privacy policy compliance
- Audit logging requirements
- Provides actionable remediation steps

#### **Quality of Life Development Tools**

##### 35. `projectSearch` - Fast Project Search
Perform fast grep searches across project files with context.

```json
{
  "name": "projectSearch",
  "arguments": {
    "query": "TODO|FIXME",
    "includePattern": "*.kt",
    "maxResults": 50,
    "contextLines": 2
  }
}
```
**Features:**
- Uses ripgrep for speed
- Context lines around matches
- Regex pattern support
- File type filtering

##### 36. `todoListFromCode` - TODO/FIXME Extraction
Parse and organize TODO/FIXME comments from codebase.

```json
{
  "name": "todoListFromCode",
  "arguments": {
    "includePattern": "*.{kt,java,py,js,ts}",
    "maxResults": 100
  }
}
```
**Returns:**
- Organized by priority (FIXME > TODO > XXX > HACK)
- File location and line numbers
- Full comment context
- Summary statistics

##### 37. `readmeGenerateOrUpdate` - README Management
Generate or update README with badges, setup instructions, and tool catalog.

```json
{
  "name": "readmeGenerateOrUpdate",
  "arguments": {
    "forceRegenerate": false
  }
}
```
**Generates:**
- Build status badges
- Setup and usage instructions
- Complete tool catalog
- Environment variable documentation

##### 38. `changelogSummarize` - Changelog Processing
Summarize conventional commits into grouped release notes.

```json
{
  "name": "changelogSummarize",
  "arguments": {
    "changelogPath": "CHANGELOG.md",
    "version": "latest"
  }
}
```
**Groups commits by type:**
- Features
- Bug fixes
- Documentation
- Breaking changes

##### 39. `buildAndTest` - Build and Test Pipeline
Run Gradle/Maven builds and return detailed test results.

```json
{
  "name": "buildAndTest",
  "arguments": {
    "buildTool": "auto",
    "skipTests": false
  }
}
```
**Returns:**
- Build success/failure
- Failing test details
- Build artifacts
- Performance metrics

##### 40. `dependencyAudit` - Dependency Security Audit
Audit Gradle dependencies for vulnerabilities and license compliance.

```json
{
  "name": "dependencyAudit",
  "arguments": {}
}
```
**Checks:**
- OSV vulnerability database
- License compatibility
- Outdated dependencies
- Security advisories

##### 41. `securityHardening` - Security Hardening Management
Manage security hardening features including RBAC, rate limiting, caching, and monitoring.

```json
{
  "name": "securityHardening",
  "arguments": {
    "operation": "get_metrics"
  }
}
```
**Operations:**
- `get_metrics` - Get security metrics and monitoring data
- `assign_role` - Assign user roles (admin, developer, readonly, guest)
- `check_permission` - Check user permissions for operations
- `clear_cache` - Clear the security cache
- `export_telemetry` - Export telemetry data

**Features:**
- Role-Based Access Control (RBAC)
- Sliding window rate limiting
- Circuit breaker pattern
- TTL-based caching
- Comprehensive metrics collection
- Telemetry export capabilities

### 🚀 **Quick Start Tool Examples**

#### **Complete Project Setup Workflow**
Here's a step-by-step workflow to set up a new Android project with enterprise features:

```bash
# 1. Analyze existing project structure
{
  "name": "analyze_project",
  "arguments": {
    "analysis_type": "architecture",
    "include_dependencies": true
  }
}

# 2. Set up MVVM architecture
{
  "name": "setup_mvvm_architecture", 
  "arguments": {
    "feature_name": "UserManagement",
    "package_name": "com.example.users",
    "include_repository": true,
    "state_management": "compose"
  }
}

# 3. Configure dependency injection
{
  "name": "setup_dependency_injection",
  "arguments": {
    "di_framework": "hilt",
    "modules": ["DatabaseModule", "NetworkModule"]
  }
}

# 4. Set up secure database
{
  "name": "setup_room_database",
  "arguments": {
    "database_name": "AppDatabase",
    "entities": [
      {
        "name": "User",
        "fields": [
          {"name": "id", "type": "String", "primaryKey": true},
          {"name": "name", "type": "String"},
          {"name": "email", "type": "String"}
        ]
      }
    ],
    "enable_encryption": true
  }
}

# 5. Implement compliance (if required)
{
  "name": "implement_gdpr_compliance",
  "arguments": {
    "package_name": "com.example.app",
    "features": ["consent_management", "data_portability"],
    "include_ui": true
  }
}

# 6. Generate UI components
{
  "name": "create_compose_component",
  "arguments": {
    "component_name": "UserListScreen",
    "component_type": "stateful",
    "include_preview": true,
    "material_design": "material3"
  }
}

# 7. Set up API integration
{
  "name": "setup_retrofit_api",
  "arguments": {
    "base_url": "https://api.example.com/",
    "endpoints": [
      {
        "name": "getUsers",
        "method": "GET", 
        "path": "users",
        "response_type": "List<User>"
      }
    ],
    "include_interceptors": ["logging", "auth"]
  }
}

# 8. Generate comprehensive tests
{
  "name": "generate_unit_tests",
  "arguments": {
    "file_path": "src/main/kotlin/UserRepository.kt",
    "test_framework": "junit5",
    "include_edge_cases": true
  }
}

# 9. Build and test
{
  "name": "gradle_build",
  "arguments": {
    "task": "assembleDebug",
    "clean_build": true
  }
}

{
  "name": "run_tests",
  "arguments": {
    "test_type": "all",
    "generate_report": true
  }
}
```

#### **AI-Powered Development Examples**

```bash
# Generate a complete login feature using AI
{
  "name": "generate_code_with_ai",
  "arguments": {
    "description": "Complete login feature with email/password, biometric authentication, remember me option, forgot password flow, and proper error handling",
    "code_type": "feature",
    "framework": "compose",
    "compliance_requirements": ["gdpr"],
    "include_tests": true
  }
}

# Analyze existing code for security issues
{
  "name": "analyze_code_with_ai",
  "arguments": {
    "file_path": "src/main/kotlin/AuthManager.kt",
    "analysis_type": "security",
    "detailed_report": true
  }
}

# Get AI assistance for complex implementation
{
  "name": "query_llm",
  "arguments": {
    "prompt": "How do I implement secure biometric authentication in Android with fallback to PIN? Include error handling for different biometric states.",
    "llm_provider": "local",
    "privacy_mode": true
  }
}
```

### 🛠️ **Tool Usage Best Practices**

#### **File Path Conventions**
Always use relative paths from your project root:
```bash
# ✅ Correct
"file_path": "src/main/kotlin/com/example/User.kt"

# ❌ Incorrect  
"file_path": "/absolute/path/to/User.kt"
```

#### **Package Naming**
Follow Android package naming conventions:
```bash
# ✅ Correct
"package_name": "com.company.app.feature.user"

# ❌ Incorrect
"package_name": "User.Package"
```

#### **Security Best Practices**
- Always use encryption for sensitive data
- Implement proper compliance features from the start
- Use secure storage for API keys and secrets
- Enable audit logging for compliance requirements

#### **Performance Optimization**
- Use `parallel: true` for Gradle builds when possible
- Generate tests incrementally rather than all at once
- Use local LLM providers for privacy-sensitive code analysis
- Enable caching for API setups

#### **Error Handling**
All tools provide comprehensive error information:
```json
{
  "success": false,
  "error": "File already exists",
  "details": {
    "file_path": "src/main/kotlin/User.kt",
    "suggestion": "Use a different file name or set overwrite: true"
  }
}
```

### 📊 **Tool Response Formats**

#### **Success Response**
```json
{
  "success": true,
  "result": {
    "files_created": ["User.kt", "UserTest.kt"],
    "lines_of_code": 125,
    "compilation_status": "success"
  },
  "metadata": {
    "execution_time": "2.3s",
    "tools_used": ["kotlin_compiler", "test_generator"]
  }
}
```

#### **Error Response**
```json
{
  "success": false,
  "error": "Compilation failed",
  "details": {
    "error_type": "compilation_error",
    "line_number": 23,
    "message": "Unresolved reference: undefinedVariable",
    "suggestions": [
      "Check variable declaration",
      "Verify imports"
    ]
  }
}
```

### �🔒 **Security & Privacy Features**

#### GDPR Compliance Implementation
```json
{
  "name": "implement_gdpr_compliance",
  "arguments": {
    "package_name": "com.example.app",
    "features": [
      "consent_management",
      "data_portability", 
      "right_to_erasure",
      "privacy_policy"
    ]
  }
}
```

**Generated Features:**
- Consent management UI components
- Data export functionality 
- User data deletion workflows
- Privacy policy templates
- Legal basis tracking

#### HIPAA Compliance Implementation
```json
{
  "name": "implement_hipaa_compliance",
  "arguments": {
    "package_name": "com.healthcare.app",
    "features": [
      "audit_logging",
      "access_controls",
      "encryption",
      "secure_messaging"
    ]
  }
}
```

**Generated Features:**
- Comprehensive audit logging system
- Role-based access control framework
- PHI encryption utilities
- Secure messaging infrastructure
- Risk assessment tools

#### Data Encryption
```json
{
  "name": "encrypt_sensitive_data",
  "arguments": {
    "data": "Patient: John Doe, SSN: 123-45-6789",
    "data_type": "phi",
    "compliance_level": "hipaa"
  }
}
```

#### Secure Storage Setup
```json
{
  "name": "setup_secure_storage",
  "arguments": {
    "storage_type": "room_encrypted",
    "package_name": "com.example.app",
    "data_classification": "restricted"
  }
}
```

### 🤖 **AI Integration Features**

#### Local LLM Queries
```json
{
  "name": "query_llm", 
  "arguments": {
    "prompt": "Generate a Kotlin data class for User with validation",
    "llm_provider": "local",
    "privacy_mode": true,
    "max_tokens": 1000
  }
}
```

#### AI-Powered Code Analysis
```json
{
  "name": "analyze_code_with_ai",
  "arguments": {
    "file_path": "src/main/UserManager.kt",
    "analysis_type": "security",
    "use_local_model": true
  }
}
```

**Analysis Types:**
- `security` - Vulnerability and security best practices
- `performance` - Performance optimization suggestions
- `bugs` - Potential bug detection
- `style` - Code style and formatting improvements
- `complexity` - Code complexity analysis

#### AI Code Generation
```json
{
  "name": "generate_code_with_ai",
  "arguments": {
    "description": "Login screen with biometric authentication",
    "code_type": "component",
    "framework": "compose",
    "compliance_requirements": ["gdpr", "hipaa"]
  }
}
```

**Code Types:**
- `class` - Kotlin classes with methods
- `function` - Standalone functions
- `layout` - XML layout files
- `test` - Unit and integration tests
- `component` - Jetpack Compose components

### 📁 **File Management Operations**

#### Advanced Backup
```json
{
  "name": "manage_project_files",
  "arguments": {
    "operation": "backup",
    "target_path": "./src",
    "destination": "./backups",
    "encryption_level": "high"
  }
}
```

#### Real-time Synchronization
```json
{
  "name": "manage_project_files",
  "arguments": {
    "operation": "sync",
    "target_path": "./src",
    "destination": "./remote-sync",
    "sync_strategy": "real_time"
  }
}
```

#### Cloud Storage Sync
```json
{
  "name": "setup_cloud_sync",
  "arguments": {
    "cloud_provider": "aws",
    "sync_strategy": "scheduled",
    "encryption_in_transit": true,
    "compliance_mode": "gdpr"
  }
}
```

**Supported Operations:**
- `backup` - Create encrypted backups with manifests
- `restore` - Restore from backup with integrity checking
- `sync` - Two-way synchronization with conflict resolution
- `encrypt` - Encrypt sensitive files in place
- `decrypt` - Decrypt files with proper authorization
- `archive` - Create compressed archives
- `extract` - Extract archives with validation
- `search` - Content-based file discovery
- `analyze` - File structure and usage analysis

### 🌐 **External API Integration**

#### API Integration Setup
```json
{
  "name": "integrate_external_api",
  "arguments": {
    "api_name": "HealthRecordsAPI",
    "base_url": "https://api.healthrecords.com",
    "auth_type": "oauth",
    "security_features": [
      "rate_limiting",
      "request_logging", 
      "response_validation"
    ],
    "compliance_requirements": ["hipaa"]
  }
}
```

#### API Usage Monitoring
```json
{
  "name": "monitor_api_usage",
  "arguments": {
    "api_name": "HealthRecordsAPI",
    "metrics": [
      "latency",
      "error_rate",
      "usage_volume",
      "cost"
    ],
    "alert_thresholds": {
      "error_rate": 5.0,
      "latency_ms": 2000
    }
  }
}
```

**Authentication Types:**
- `none` - No authentication required
- `api_key` - API key in header or query
- `oauth` - OAuth 2.0 flow
- `jwt` - JSON Web Token
- `basic` - Basic HTTP authentication

### 🏗️ **Advanced Android Development**

#### MVVM Architecture Setup
```json
{
  "name": "setup_mvvm_architecture",
  "arguments": {
    "feature_name": "UserProfile",
    "package_name": "com.example.app",
    "include_repository": true,
    "include_use_cases": true,
    "data_source": "both"
  }
}
```

#### Jetpack Compose Components
```json
{
  "name": "create_compose_component",
  "arguments": {
    "file_path": "ui/components/LoginForm.kt",
    "component_name": "LoginForm",
    "component_type": "component",
    "package_name": "com.example.ui",
    "uses_state": true,
    "uses_navigation": false
  }
}
```

#### Room Database Setup
```json
{
  "name": "setup_room_database",
  "arguments": {
    "database_name": "AppDatabase",
    "package_name": "com.example.data",
    "entities": ["User", "Profile", "Settings"],
    "include_migration": true
  }
}
```

#### Retrofit API Client
```json
{
  "name": "setup_retrofit_api",
  "arguments": {
    "api_name": "UserApiService",
    "package_name": "com.example.network",
    "base_url": "https://api.example.com",
    "endpoints": [
      {
        "method": "GET",
        "path": "/users/{id}",
        "name": "getUser"
      }
    ],
    "include_interceptors": true
  }
}
```

#### Dependency Injection (Hilt)
```json
{
  "name": "setup_dependency_injection",
  "arguments": {
    "module_name": "NetworkModule",
    "package_name": "com.example.di",
    "injection_type": "network"
  }
}
```

#### ML Model Integration
```json
{
  "name": "integrate_ml_model",
  "arguments": {
    "model_type": "tflite",
    "model_path": "assets/model.tflite",
    "use_case": "image_classification",
    "privacy_preserving": true
  }
}
```

### 🛠️ **Tool-Specific Troubleshooting**

#### **Gradle Build Issues**
```bash
# Tool: gradle_build
# Common solutions:

# 1. Clear Gradle cache
{
  "name": "gradle_build",
  "arguments": {
    "task": "clean",
    "clean_build": true
  }
}

# 2. Check Java version
echo $JAVA_HOME
java -version

# 3. Fix permission issues (macOS/Linux)
chmod +x gradlew

# 4. Enable verbose output for debugging
{
  "name": "gradle_build",
  "arguments": {
    "task": "assembleDebug",
    "gradle_args": ["--debug", "--stacktrace"]
  }
}
```

#### **AI Integration Issues**
```bash
# Tool: query_llm, analyze_code_with_ai, generate_code_with_ai

# Local LLM not responding
curl http://localhost:11434/api/generate -d '{"model":"codellama","prompt":"test"}'

# API key issues
python3 -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"

# Privacy mode for sensitive code
{
  "name": "query_llm",
  "arguments": {
    "prompt": "Your prompt here",
    "llm_provider": "local",  # Force local processing
    "privacy_mode": true      # No external API calls
  }
}
```

#### **File Creation Issues**
```bash
# Tool: create_kotlin_file, create_layout_file, create_compose_component

# Permission denied
sudo chown -R $(whoami):$(whoami) src/

# File already exists
{
  "name": "create_kotlin_file",
  "arguments": {
    "file_path": "src/main/kotlin/User.kt",
    "overwrite": true  # Force overwrite
  }
}

# Invalid package structure
# Ensure your file path matches package structure:
# File: src/main/kotlin/com/example/User.kt
# Package: com.example
```

#### **Security Tool Issues**
```bash
# Tool: encrypt_sensitive_data, implement_gdpr_compliance

# Cryptography not available
pip install cryptography>=41.0.0

# Test encryption
python3 -c "from cryptography.fernet import Fernet; print('✅ Encryption available')"

# GDPR compliance setup
{
  "name": "implement_gdpr_compliance",
  "arguments": {
    "package_name": "com.example.app",
    "features": ["consent_management"],  # Start with basic features
    "dry_run": true  # Test mode first
  }
}
```

#### **Database Setup Issues**
```bash
# Tool: setup_room_database, setup_secure_storage

# Check Android Room version compatibility
grep "room_version" build.gradle

# Test database creation
{
  "name": "setup_room_database",
  "arguments": {
    "database_name": "TestDB",
    "entities": [{"name": "TestEntity", "fields": [{"name": "id", "type": "String", "primaryKey": true}]}],
    "validate_only": true  # Check schema without creating files
  }
}
```

#### **Network/API Issues**
```bash
# Tool: setup_retrofit_api, call_external_api

# Test network connectivity
curl -I https://api.example.com/

# Verify SSL certificates
openssl s_client -connect api.example.com:443

# Debug API calls
{
  "name": "call_external_api",
  "arguments": {
    "api_name": "TestAPI",
    "endpoint": "/health",
    "method": "GET",
    "debug_mode": true,  # Enable detailed logging
    "timeout": 10        # Shorter timeout for testing
  }
}
```

### 🧪 **Testing & Quality Assurance**

#### Comprehensive Test Generation
```json
{
  "name": "generate_test_suite",
  "arguments": {
    "class_to_test": "UserRepository",
    "test_type": "unit",
    "include_mockito": true,
    "test_coverage": "comprehensive"
  }
}
```

**Test Types:**
- `unit` - Unit tests with mocking
- `integration` - Integration tests with real dependencies
- `ui` - UI tests with Espresso

---

## 🏥 **Industry-Specific Examples**

### Healthcare Application
```bash
# 1. Implement HIPAA compliance
{
  "name": "implement_hipaa_compliance",
  "arguments": {
    "package_name": "com.health.tracker",
    "features": ["audit_logging", "encryption", "access_controls"]
  }
}

# 2. Setup secure storage for PHI
{
  "name": "setup_secure_storage", 
  "arguments": {
    "storage_type": "room_encrypted",
    "data_classification": "restricted"
  }
}

# 3. Generate patient form with AI
{
  "name": "generate_code_with_ai",
  "arguments": {
    "description": "Patient intake form with validation",
    "compliance_requirements": ["hipaa"]
  }
}
```

### Financial Application
```bash
# 1. Implement GDPR compliance
{
  "name": "implement_gdpr_compliance",
  "arguments": {
    "features": ["consent_management", "data_portability"]
  }
}

# 2. Setup secure API integration
{
  "name": "integrate_external_api",
  "arguments": {
    "api_name": "PaymentAPI",
    "auth_type": "oauth",
    "security_features": ["rate_limiting", "request_logging"]
  }
}

# 3. Enable cloud backup with encryption
{
  "name": "setup_cloud_sync",
  "arguments": {
    "cloud_provider": "aws",
    "encryption_in_transit": true,
    "compliance_mode": "gdpr"
  }
}
```

---

## 🔧 **Configuration & Deployment**

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up -d

# Or build manually
docker build -t kotlin-mcp-server .
docker run -p 8000:8000 -v $(pwd):/workspace kotlin-mcp-server
```

### AI Agent Integration

#### Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "kotlin-android": {
      "command": "python",
      "args": ["/path/to/kotlin-mcp-server/kotlin_mcp_server.py"],
      "env": {
        "WORKSPACE_PATH": "/path/to/your/android/project"
      }
    }
  }
}
```

#### VS Code Extension
Use the configuration from `mcp_config_vscode.json`

---

## ⚙️ **Configuration & Plugin Requirements**

This section provides detailed instructions on configuring the MCP server for different IDEs and the required plugins.

### 🔌 **Required Plugins/Extensions**

#### **VS Code Extensions**
```bash
# Install required VS Code extensions
code --install-extension ms-python.python
code --install-extension ms-python.pylint
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort
code --install-extension ms-python.mypy-type-checker
code --install-extension ms-toolsai.jupyter
```

**Manual Installation via VS Code Marketplace:**
- **Python** (ms-python.python) - Core Python support
- **Pylint** (ms-python.pylint) - Code linting
- **Black Formatter** (ms-python.black-formatter) - Code formatting
- **isort** (ms-python.isort) - Import sorting
- **Jupyter** (ms-toolsai.jupyter) - Notebook support (optional)
- **MCP for VS Code** - Model Context Protocol support (if available)

#### **JetBrains IDEs (IntelliJ IDEA, Android Studio)**
**Required Plugins:**
- **Python Plugin** - For Python script execution
- **MCP Plugin** - Model Context Protocol support (check JetBrains marketplace)
- **Kotlin Plugin** - Built-in for Android Studio, install for IntelliJ
- **Android Plugin** - Built-in for Android Studio

#### **Claude Desktop Integration**
No additional plugins required - uses built-in MCP support.

### 🛠️ **IDE Configuration**

#### **Visual Studio Code**

1. **Install Python Extension Pack:**
   ```bash
   code --install-extension ms-python.python
   ```

2. **Configure MCP Server:**
   The installation script generates `mcp_config_vscode.json` with the correct paths. Simply add to VS Code `settings.json` (`Cmd/Ctrl + Shift + P` → "Preferences: Open Settings (JSON)"):
   ```json
   {
     "mcp.server.configFiles": [
       "/absolute/path/to/your/kotlin-mcp-server/mcp_config_vscode.json"
     ],
     "python.defaultInterpreterPath": "/usr/bin/python3",
     "python.linting.enabled": true,
     "python.formatting.provider": "black",
     "python.sortImports.path": "isort"
   }
   ```

   **💡 Pro Tip:** The installation script provides the exact path you need to use.

3. **Workspace Settings (.vscode/settings.json):**
   ```json
   {
     "python.pythonPath": "python3",
     "mcp.server.autoStart": true,
     "mcp.server.logLevel": "info"
   }
   ```

#### **JetBrains IDEs (IntelliJ IDEA, Android Studio)**

1. **Install Required Plugins:**
   - Go to `File > Settings > Plugins` (Windows/Linux) or `IntelliJ IDEA > Preferences > Plugins` (Mac)
   - Search and install "MCP" plugin from marketplace
   - Install "Python" plugin if not already available

2. **Configure MCP Server:**
   The installation script generates `mcp_config.json` with proper configuration. In your IDE:
   - Go to `File > Settings > Tools > MCP Server`
   - Click `+` to add new server:
     - **Name:** Your custom server name (as configured during installation)
     - **Configuration File:** Select the generated `mcp_config.json`
     - **Auto Start:** Enable

3. **Android Studio Specific:**
   ```xml
   <!-- Add to .idea/workspace.xml -->
   <component name="MCPServerManager">
     <option name="servers">
       <server name="your-server-name" configFile="mcp_config.json" autoStart="true"/>
     </option>
   </component>
   ```

   **💡 Note:** Replace `your-server-name` with the server name you chose during installation.

#### **Claude Desktop**

1. **Configuration File Location:**
   - **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/claude/claude_desktop_config.json`

2. **Configuration Content:**
   Simply copy the content from the generated `mcp_config_claude.json` file to your Claude Desktop configuration file. The installation script has already configured all paths and settings correctly.

   **Example of generated configuration:**
   ```json
   {
     "mcpServers": {
       "your-server-name": {
         "command": "python3",
         "args": ["kotlin_mcp_server.py"],
         "cwd": "/absolute/path/to/kotlin-mcp-server",
         "env": {
           "PROJECT_PATH": "${workspaceRoot}"
         }
       }
     }
   }
   ```

   **✅ Ready to Use:** No manual path updates needed - everything is pre-configured!

#### **Cursor IDE**

1. **Install Extensions:**
   - Same extensions as VS Code (Cursor is VS Code-based)
   - Python, Pylint, Black Formatter, isort

2. **Configuration:**
   Use the same `mcp_config_vscode.json` configuration as VS Code. Add to Cursor's `settings.json`:
   ```json
   {
     "mcp.server.configFiles": [
       "/absolute/path/to/your/kotlin-mcp-server/mcp_config_vscode.json"
     ]
   }
   ```

#### **VS Code Bridge Server (Alternative Integration)**

For VS Code extensions that need HTTP API access to MCP tools, the project includes a bridge server.

**1. Start the Bridge Server:**
```bash
# Default port (8080)
python3 vscode_bridge.py

# Custom port
python3 vscode_bridge.py 8081

# With environment configuration
MCP_BRIDGE_HOST=0.0.0.0 MCP_BRIDGE_PORT=8080 python3 vscode_bridge.py
```

**2. Health Check:**
```bash
# Test server is running
curl http://localhost:8080/health

# Expected response:
{
  "status": "healthy",
  "current_workspace": "/path/to/current/workspace",
  "available_tools": [
    "gradle_build",
    "run_tests", 
    "create_kotlin_file",
    "create_layout_file",
    "analyze_project"
  ]
}
```

**3. Using the Bridge API:**
```bash
# Call MCP tools via HTTP
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "create_kotlin_file",
    "arguments": {
      "file_path": "src/main/MyClass.kt",
      "content": "class MyClass { }"
    }
  }'
```

**4. VS Code Extension Integration:**
```javascript
// In your VS Code extension
const response = await fetch('http://localhost:8080/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tool: 'analyze_project',
    arguments: { analysis_type: 'architecture' }
  })
});

const result = await response.json();
```

**5. Configuration:**
```bash
# Environment variables for bridge server
MCP_BRIDGE_HOST=localhost     # Server host
MCP_BRIDGE_PORT=8080          # Server port
VSCODE_WORKSPACE_FOLDER=/path # Override workspace detection
```

#### **Other IDEs**

For IDEs with MCP support:
- **Vim/Neovim:** Use coc-mcp or similar MCP plugins
- **Emacs:** Install mcp-mode package
- **Sublime Text:** Install MCP package via Package Control

---

## �️ **Troubleshooting**

### **Common Installation Issues**

#### **Python Version Compatibility**
```bash
# Check Python version (must be 3.8+)
python3 --version

# If using older Python, install newer version
# macOS with Homebrew:
brew install python@3.11

# Ubuntu/Debian:
sudo apt update && sudo apt install python3.11
```

#### **Dependency Installation Errors**
```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Install with verbose output for debugging
pip install -r requirements.txt -v

# Use alternative index if needed
pip install -r requirements.txt -i https://pypi.org/simple/
```

#### **Import Errors**
```bash
# Verify installation
python3 -c "import kotlin_mcp_server; print('Import successful')"

# Check Python path
python3 -c "import sys; print(sys.path)"

# Install in development mode
pip install -e .
```

### **Configuration Issues**

#### **Using the New Installer (Recommended)**
Most configuration issues are now resolved automatically:

```bash
# Regenerate configuration with the enhanced installer
python3 install.py

# For specific setup types:
python3 install.py 1 /your/android/project my-server false
python3 install.py --help  # See all options
```

#### **Legacy Manual Configuration Issues** 
If you're still using manual configuration from older versions:

```bash
# 1. Update to the new installer (recommended)
python3 install.py

# 2. Or manually find your actual paths (legacy method)
cd /path/to/kotlin-mcp-server && pwd
cd /path/to/android/project && pwd

# 3. Update config files - replace ${MCP_SERVER_DIR} with actual path
# Example: Change this
"cwd": "${MCP_SERVER_DIR}"
# To this (your actual path)  
"cwd": "~/Documents/kotlin-mcp-server"
```

**💡 Pro Tip**: The new installer eliminates these manual steps entirely!

#### **Environment Variable Issues**
```bash
# Check if variables are set
env | grep MCP
env | grep WORKSPACE

# Load environment file manually if needed
source .env

# Test variable expansion
echo $MCP_SERVER_DIR
echo $WORKSPACE_PATH
```

#### **MCP Server Not Starting**
1. **Check configuration file paths** in your IDE settings
2. **Verify Python interpreter** path in IDE settings
3. **Ensure environment variables** are set correctly
4. **Check logs** for specific error messages

#### **IDE Plugin Issues**
```bash
# VS Code: Reset extension
code --uninstall-extension ms-python.python
code --install-extension ms-python.python

# JetBrains: Clear caches
File > Invalidate Caches and Restart
```

#### **VS Code Bridge Server Issues**
```bash
# Test bridge server is running
curl http://localhost:8080/health

# Check if port is in use
netstat -an | grep 8080
lsof -i :8080

# Start bridge server with debug
MCP_BRIDGE_HOST=0.0.0.0 MCP_BRIDGE_PORT=8080 python3 vscode_bridge.py

# Test specific tool call
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{"tool": "list_tools", "arguments": {}}'

# Common fixes:
# 1. Check firewall settings for port 8080
# 2. Ensure python3 vscode_bridge.py is running
# 3. Verify VSCODE_WORKSPACE_FOLDER environment variable
# 4. Check bridge server logs for errors
```

#### **Permission Errors**
```bash
# macOS/Linux: Fix permissions
chmod +x *.py
chmod 755 servers/mcp-process/

# Windows: Run as administrator or check file permissions
```

### **Runtime Issues**

#### **AI Integration Failures**
```bash
# Test local LLM connection
curl http://localhost:11434/api/generate -d '{"model":"llama2","prompt":"test"}'

# Verify API keys are set
python3 -c "import os; print('OpenAI key:', os.getenv('OPENAI_API_KEY', 'Not set'))"
```

#### **File Operation Errors**
```bash
# Check disk space
df -h

# Verify write permissions
touch test_file.txt && rm test_file.txt

# Check workspace path
ls -la "${WORKSPACE_PATH}"
```

#### **Security/Compliance Errors**
```bash
# Test encryption setup
python3 -c "from cryptography.fernet import Fernet; print('Encryption available')"

# Verify compliance mode
python3 -c "import os; print('Compliance:', os.getenv('COMPLIANCE_MODE', 'None'))"
```

### **Known Issues & Fixes**

#### **GitHub Actions Build Failures**
If you encounter CI/CD issues:

1. **Configuration Files:** Ensure `.flake8` exists (not in `pyproject.toml`)
2. **GitHub Actions:** Update to latest versions:
   - `actions/checkout@v4`
   - `actions/setup-python@v4`
   - `actions/cache@v4`
3. **Code Formatting:** Run `make format` to fix style issues

#### **Deprecated Dependencies**
```bash
# Update all dependencies
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
pip audit

# Update Python tools
pip install --upgrade black isort flake8 pylint mypy
```

### **Performance Issues**

#### **Slow Server Response**
```bash
# Enable performance monitoring
export LOG_LEVEL=DEBUG

# Run performance tests
make perf

# Profile server startup
python3 -m cProfile kotlin_mcp_server.py
```

#### **Memory Usage**
```bash
# Monitor memory usage
python3 -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"

# Run memory-efficient mode
export MCP_LOW_MEMORY_MODE=true
```

### **Getting Help**

1. **Check Logs:** Look in `mcp_security.log` for detailed error information
2. **Run Diagnostics:** Use `python3 comprehensive_test.py --verbose`
3. **Validate Configuration:** Run `python3 breaking_change_monitor.py`
4. **Test Individual Components:**
   ```bash
   # Test core server
   python3 kotlin_mcp_server.py --test
   
   # Test enhanced features
   python3 kotlin_mcp_server.py --test
   
   # Test AI integration
   python3 kotlin_mcp_server.py --test
   ```

5. **Contact Support:** Include logs, system info, and error messages when reporting issues

---

## 🌉 **VS Code Bridge Server**

The VS Code Bridge Server provides HTTP API access to MCP tools for VS Code extensions and other applications that can't directly use the MCP protocol.

### **When to Use the Bridge Server**

- **VS Code Extensions**: When building custom VS Code extensions that need MCP functionality
- **HTTP Clients**: When integrating with tools that only support HTTP APIs
- **Remote Access**: When you need to access MCP tools from another machine
- **Testing**: For easy testing of MCP tools using curl or Postman
- **Web Applications**: For web-based interfaces to MCP functionality

### **Bridge Server Features**

#### **Workspace Detection**
- Automatically detects current VS Code workspace
- Uses `VSCODE_WORKSPACE_FOLDER` environment variable
- Falls back to current working directory

#### **Available Endpoints**

**Health Check:**
```bash
GET /health
# Returns: server status, workspace info, available tools
```

**Tool Execution:**
```bash
POST /
Content-Type: application/json

{
  "tool": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

#### **Supported Tools via Bridge**
- `gradle_build` - Build Android project
- `run_tests` - Execute tests
- `create_kotlin_file` - Create Kotlin source files
- `create_layout_file` - Create Android layout files
- `analyze_project` - Project structure analysis
- All other MCP tools (see full list via `/health`)

### **Configuration**

#### **Environment Variables**
```bash
# Bridge server configuration
MCP_BRIDGE_HOST=localhost          # Server host (default: localhost)
MCP_BRIDGE_PORT=8080              # Server port (default: 8080)

# Workspace configuration  
VSCODE_WORKSPACE_FOLDER=/path/to/project   # Override workspace detection
PROJECT_PATH=/path/to/project              # Fallback project path
```

#### **Security Considerations**
```bash
# For remote access (use with caution)
MCP_BRIDGE_HOST=0.0.0.0           # Allow external connections

# For local development only (recommended)
MCP_BRIDGE_HOST=127.0.0.1         # Local connections only
```

### **Usage Examples**

#### **Start Bridge Server**
```bash
# Basic startup
python3 vscode_bridge.py

# With custom configuration
MCP_BRIDGE_HOST=localhost MCP_BRIDGE_PORT=8081 python3 vscode_bridge.py

# Background mode
python3 vscode_bridge.py &
```

#### **Health Check**
```bash
curl http://localhost:8080/health

# Response:
{
  "status": "healthy",
  "current_workspace": "~/AndroidProject",
  "available_tools": ["gradle_build", "run_tests", ...]
}
```

#### **Create Kotlin File**
```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "create_kotlin_file",
    "arguments": {
      "file_path": "src/main/kotlin/MainActivity.kt",
      "package_name": "com.example.app",
      "class_name": "MainActivity"
    }
  }'
```

#### **Run Gradle Build**
```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "gradle_build",
    "arguments": {
      "task": "assembleDebug",
      "clean_first": true
    }
  }'
```

#### **Format Kotlin Code**
```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "format_code",
    "arguments": {}
  }'
```

#### **Run Static Analysis**
```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "run_lint",
    "arguments": { "lint_tool": "detekt" }
  }'
```

#### **Generate Documentation**
```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "generate_docs",
    "arguments": { "doc_type": "html" }
  }'
```

### **VS Code Extension Integration**

#### **TypeScript/JavaScript Example**
```typescript
interface MCPRequest {
  tool: string;
  arguments: Record<string, any>;
}

interface MCPResponse {
  success?: boolean;
  result?: any;
  error?: string;
}

class MCPBridgeClient {
  private baseUrl: string;

  constructor(host = 'localhost', port = 8080) {
    this.baseUrl = `http://${host}:${port}`;
  }

  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }

  async callTool(tool: string, arguments: Record<string, any>): Promise<MCPResponse> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool, arguments })
    });
    return response.json();
  }

  async createKotlinFile(filePath: string, className: string): Promise<MCPResponse> {
    return this.callTool('create_kotlin_file', {
      file_path: filePath,
      class_name: className
    });
  }

  async buildProject(task = 'assembleDebug'): Promise<MCPResponse> {
    return this.callTool('gradle_build', { task });
  }
}

// Usage in VS Code extension
const mcpClient = new MCPBridgeClient();

// In extension activation
const health = await mcpClient.healthCheck();
console.log('MCP Bridge Status:', health.status);

// Create new Kotlin file
const result = await mcpClient.createKotlinFile(
  'src/main/kotlin/NewClass.kt',
  'NewClass'
);
```

### **Troubleshooting Bridge Server**

#### **Common Issues**
```bash
# Port already in use
netstat -tulpn | grep 8080
# Kill process using port: sudo kill -9 <PID>

# Permission denied
sudo ufw allow 8080  # Ubuntu
sudo firewall-cmd --add-port=8080/tcp  # CentOS

# Connection refused
# Check if server is running:
ps aux | grep vscode_bridge.py

# Test with verbose curl:
curl -v http://localhost:8080/health
```

#### **Debug Mode**
```bash
# Enable debug logging
DEBUG=true python3 vscode_bridge.py

# Check server logs
tail -f /tmp/mcp-bridge.log
```

### **Performance Notes**

- **Lightweight**: Minimal HTTP server with low memory footprint
- **Workspace-aware**: Automatically uses current VS Code workspace
- **Error handling**: Graceful error responses with details
- **CORS support**: Includes CORS headers for web applications

---

## 🧪 **Testing & Quality Assurance**

This project includes a comprehensive testing and quality assurance system. For detailed testing information, see [`TESTING_GUIDE.md`](TESTING_GUIDE.md).

### **Quick Testing Commands**
```bash
# Run all tests
make test

# Run tests with coverage
make coverage

# Run quality checks
make lint

# Full CI pipeline
make ci

# Check for breaking changes
python breaking_change_monitor.py
```

### **Quality Metrics**
- **Test Coverage:** 80% minimum
- **Performance:** < 5s tool listing, < 2s file operations
- **Security:** Zero high-severity vulnerabilities
- **Code Quality:** Pylint score 8.0+/10.0

---

## �📊 **Monitoring & Analytics**

The server provides comprehensive monitoring:

- **Security Events** - Real-time security monitoring and alerts
- **API Usage** - Request/response metrics, error rates, costs
- **File Operations** - Backup status, sync health, storage usage
- **Compliance Status** - GDPR/HIPAA compliance reporting
- **Performance Metrics** - Response times, throughput, resource usage

---

## 🛡️ **Security Best Practices**

1. **Environment Variables** - Store sensitive data in `.env` files
2. **Encryption Keys** - Use strong, unique encryption passwords
3. **API Keys** - Rotate API keys regularly
4. **Audit Logs** - Review security logs periodically
5. **Access Controls** - Implement least privilege principles
6. **Data Classification** - Properly classify and handle sensitive data

---

## 📄 **License & Compliance**

This MCP server is designed to help you build compliant applications:

- **GDPR Ready** - Full Article 25 "Privacy by Design" implementation
- **HIPAA Compatible** - Meets Technical Safeguards requirements  
- **SOC 2 Type II** - Security controls framework
- **ISO 27001** - Information security management standards

---

## 🤝 **Contributing**

We welcome contributions! Please see our contributing guidelines for:

- Code style and standards
- Security review process
- Testing requirements
- Documentation standards

---

## 🆘 **Support & Resources**

- **Documentation** - Complete API documentation in `/docs`
- **Examples** - Industry-specific examples in `/examples`
- **Issues** - Report bugs and feature requests
- **Security** - Report security issues privately

---

## 🚀 **Getting Started Checklist**

### **Installation & Setup**
- [ ] Install Python 3.8+ and pip
- [ ] Clone repository: `git clone <repo-url>`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure environment variables in `.env` file
- [ ] Install required IDE plugins/extensions
- [ ] Validate installation: `python3 validate_config.py`

### **Basic Tool Testing**
- [ ] Test project analysis: `{"name": "analyze_project", "arguments": {"analysis_type": "architecture"}}`
- [ ] Test file creation: `{"name": "create_kotlin_file", "arguments": {"file_path": "Test.kt", "class_name": "Test"}}`
- [ ] Test build: `{"name": "gradle_build", "arguments": {"task": "assembleDebug"}}`
- [ ] Test AI integration: `{"name": "query_llm", "arguments": {"prompt": "Hello world", "llm_provider": "local"}}`

### **Advanced Features**
- [ ] Set up MVVM architecture: `setup_mvvm_architecture`
- [ ] Configure dependency injection: `setup_dependency_injection`
- [ ] Implement security features: `encrypt_sensitive_data`
- [ ] Set up compliance (if needed): `implement_gdpr_compliance` or `implement_hipaa_compliance`
- [ ] Configure cloud sync: `setup_cloud_sync`
- [ ] Set up external APIs: `setup_external_api`

### **Testing & Quality**
- [ ] Generate unit tests: `generate_unit_tests`
- [ ] Run comprehensive tests: `run_tests`
- [ ] Perform code analysis: `analyze_code_with_ai`
- [ ] Run lint checks: `run_lint`
- [ ] Generate documentation: `generate_docs`

### **Optional Integrations**
- [ ] Test VS Code bridge server: `python3 vscode_bridge.py`
- [ ] Configure Claude Desktop integration
- [ ] Set up cloud storage backup
- [ ] Enable AI code generation features

**🎉 Ready to build enterprise-grade Android applications with 31 AI-enhanced tools at your disposal!**

### 📚 **Next Steps**

1. **Explore the Tools:** Start with basic tools like `analyze_project` and `create_kotlin_file`
2. **Set Up Architecture:** Use `setup_mvvm_architecture` for clean code structure
3. **Add Security:** Implement `encrypt_sensitive_data` and compliance features
4. **Generate Code:** Leverage AI tools for rapid development
5. **Test Everything:** Use `generate_unit_tests` and `run_tests` for quality assurance

### 🆘 **Getting Help**

- **Tool Reference:** Each tool has detailed parameter documentation above
- **Examples:** Industry-specific examples in the README
- **Troubleshooting:** Comprehensive troubleshooting section included
- **Best Practices:** Follow the tool usage guidelines for optimal results

---

## 📄 **Version Information**

**Current Version:** `V2.0` - AI-Enhanced Modular Architecture  
**Release Date:** August 2025  
**Compatibility:** Backward compatible with V1.0 projects  
**Next Release:** V2.1 planned for minor enhancements and bug fixes

**Release Notes:**
- 🤖 AI-powered code generation with production-ready implementations
- 🏗️ Modular architecture for better maintainability  
- 🌍 Dynamic configuration system for cross-platform compatibility
- ⚡ Enhanced performance and reliability improvements
- 🛡️ Advanced security and compliance features

For detailed version history, see the **Revision History** section at the top of this document.

---

## 🔧 Kotlin Sidecar Setup

The Kotlin sidecar provides AST-aware code analysis and refactoring capabilities using the Kotlin Analysis API.

### Building the Sidecar

```bash
# Navigate to the sidecar directory
cd kotlin-sidecar

# Build with Gradle (requires Java 17+)
./gradlew build

# Or use gradle wrapper if available
gradle build
```

### Running the Sidecar

```bash
# Run the sidecar directly
./gradlew runSidecar

# Or run the built JAR
java -jar build/libs/kotlin-sidecar-1.0.0.jar
```

### Sidecar Protocol

The sidecar communicates via NDJSON over stdin/stdout:

**Request Format:**
```json
{"tool": "refactorFunction", "input": {"filePath": "...", "functionName": "..."}}
```

**Response Format:**
```json
{"ok": true, "result": {"patch": "...", "affectedFiles": ["..."]}}
```

**Error Format:**
```json
{"ok": false, "error": {"code": "ValidationError", "message": "..."}}
```

---

## ⚙️ Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SIDECAR_CMD` | `["java","-jar","kotlin-sidecar.jar"]` | Command to start Kotlin sidecar |
| `MCP_MAX_RETRIES` | `5` | Maximum API retry attempts |
| `MCP_API_TIMEOUT_MS` | `3000` | API timeout in milliseconds |
| `MCP_RATE_LIMIT_QPS` | `10` | Rate limit queries per second |
| `MCP_AUDIT_DB_PATH` | `./mcp_audit.db` | Audit database path |
| `MCP_LOG_LEVEL` | `INFO` | Logging level |
| `MCP_ENABLE_TELEMETRY` | `false` | Enable telemetry collection |
| `MCP_CIRCUIT_BREAKER_THRESHOLD` | `5` | Circuit breaker failure threshold |
| `MCP_CIRCUIT_BREAKER_TIMEOUT_MS` | `60000` | Circuit breaker reset timeout |

### Security & Compliance

| Variable | Description |
|----------|-------------|
| `MCP_ENCRYPTION_KEY` | AES-256 encryption key for sensitive data |
| `MCP_AUDIT_RETENTION_DAYS` | Days to retain audit logs |
| `MCP_GDPR_MODE` | Enable GDPR compliance features |
| `MCP_HIPAA_MODE` | Enable HIPAA compliance features |

### AI/ML Configuration

| Variable | Description |
|----------|-------------|
| `MCP_LLM_PROVIDER` | LLM provider (openai, anthropic, local) |
| `MCP_LLM_API_KEY` | API key for external LLM providers |
| `MCP_LOCAL_LLM_ENDPOINT` | Endpoint for local LLM server |
| `MCP_AI_MODEL` | Specific AI model to use |

### File Management

| Variable | Description |
|----------|-------------|
| `MCP_BACKUP_RETENTION_DAYS` | Days to retain file backups |
| `MCP_MAX_BACKUP_SIZE_MB` | Maximum backup size in MB |
| `MCP_SYNC_INTERVAL_SECONDS` | File sync interval |
| `MCP_ENCRYPTED_EXTENSIONS` | File extensions to auto-encrypt |

---

## 📚 Tool Catalog & Examples

### Core Development Tools

#### `refactorFunction`
Refactor Kotlin functions with AST-aware transformations.

```json
{
  "name": "refactorFunction",
  "arguments": {
    "filePath": "/app/src/main/kotlin/MyClass.kt",
    "functionName": "calculateTotal",
    "refactorType": "rename",
    "newName": "computeTotal",
    "preview": false
  }
}
```

#### `formatCode`
Format Kotlin code using ktlint or spotless.

```json
{
  "name": "formatCode",
  "arguments": {
    "targets": ["src/main/kotlin"],
    "style": "ktlint",
    "preview": false
  }
}
```

#### `optimizeImports`
Optimize and organize Kotlin imports.

```json
{
  "name": "optimizeImports",
  "arguments": {
    "projectRoot": "/app",
    "mode": "project",
    "preview": false
  }
}
```

### Git Tools

#### `gitStatus`
Get Git repository status.

```json
{
  "name": "gitStatus",
  "arguments": {}
}
```

#### `gitSmartCommit`
Create intelligent commit message.

```json
{
  "name": "gitSmartCommit",
  "arguments": {}
}
```

#### `gitCreateFeatureBranch`
Create a new feature branch.

```json
{
  "name": "gitCreateFeatureBranch",
  "arguments": {
    "branchName": "user-authentication"
  }
}
```

### API Tools

#### `apiCallSecure`
Make secure API calls with authentication.

```json
{
  "name": "apiCallSecure",
  "arguments": {
    "apiName": "github",
    "endpoint": "/repos/owner/repo/issues",
    "method": "GET",
    "auth": {
      "type": "bearer",
      "token": "ghp_..."
    }
  }
}
```

#### `apiMonitorMetrics`
Get API monitoring metrics.

```json
{
  "name": "apiMonitorMetrics",
  "arguments": {
    "apiName": "github",
    "windowMinutes": 60
  }
}
```

### Quality of Life Tools

#### `projectSearch`
Fast grep search with context.

```json
{
  "name": "projectSearch",
  "arguments": {
    "query": "TODO|FIXME",
    "includePattern": "*.{kt,java}",
    "maxResults": 50,
    "contextLines": 2
  }
}
```

#### `todoListFromCode`
Parse TODO/FIXME comments.

```json
{
  "name": "todoListFromCode",
  "arguments": {
    "includePattern": "*.{kt,java,py}",
    "maxResults": 100
  }
}
```

#### `readmeGenerateOrUpdate`
Generate or update README.

```json
{
  "name": "readmeGenerateOrUpdate",
  "arguments": {
    "forceRegenerate": false
  }
}
```

#### `buildAndTest`
Run build and return test results.

```json
{
  "name": "buildAndTest",
  "arguments": {
    "buildTool": "auto",
    "skipTests": false
  }
}
```

#### `dependencyAudit`
Audit dependencies for vulnerabilities.

```json
{
  "name": "dependencyAudit",
  "arguments": {}
}
```

---

## 🔒 Security & RBAC

### Role-Based Access Control

The server implements comprehensive RBAC with the following roles:

- **admin**: Full access to all tools and configurations
- **developer**: Access to development tools (refactor, format, build)
- **analyst**: Read-only access to analysis and monitoring tools
- **auditor**: Access to audit trails and compliance reports

### Rate Limiting

Configurable rate limiting protects against abuse:

- **Global QPS Limit**: `MCP_RATE_LIMIT_QPS` (default: 10)
- **Per-User Limits**: Configurable per role
- **Burst Handling**: Token bucket algorithm for smooth traffic

### Telemetry

Optional telemetry collection for usage analytics:

- **Enable**: Set `MCP_ENABLE_TELEMETRY=true`
- **Data Collected**: Tool usage statistics, performance metrics
- **Privacy**: No sensitive data or code content collected
- **Opt-out**: Disabled by default
