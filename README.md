# Kotlin Android MCP Server

A Model Context Protocol (MCP) server that provides AI agents with comprehensive access to Kotlin-based Android development projects. This server enables context-aware assistance for Android development through any MCP-compatible AI agent like Claude Desktop, VS Code extensions, and more.

---

## ✨ Features

- 🔄 **Workspace-Aware** – Automatically detects and works with your current Android project
- 📂 **Full Project Context** – AI agents can access your Kotlin files, layouts, Gradle configs, and AndroidManifest.xml
- 🛠️ **Android Development Tools** – Build, test, and generate code directly through AI commands
- 🧠 **Multiple AI Agent Support** – Works with Claude Desktop, VS Code extensions, and other MCP clients
- 🎯 **Template Generation** – Create Activities, Fragments, Layouts with proper Kotlin structure
- 📊 **Project Analysis** – Analyze dependencies, structure, and manifest configuration
- 🏗️ **Complex App Development** – MVVM architecture, Jetpack Compose, Room database, Retrofit API
- 🎨 **Advanced UI Components** – Custom views, complex layouts, Compose components
- 🧪 **Comprehensive Testing** – Unit, integration, and UI test generation
- ⚙️ **Build Configuration** – Multi-variant builds, dependency injection setup

---

## 🚀 Quick Start

### Installation

```bash
# Clone and setup
git clone <your-repo-url>
cd kotlin-mcp-server

# Run the installer
python3 install.py
```

The installer will:
- Install all dependencies
- Create workspace-aware configurations for different AI agents
- Set up the server as a global command (`kotlin-android-mcp`)

### Integration with AI Agents

#### Claude Desktop
1. Copy the configuration from `mcp_config_claude.json`
2. Add it to your Claude Desktop config file:
   ```bash
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
3. Restart Claude Desktop
4. The server will automatically use your current workspace

#### VS Code Extensions
- Use `mcp_config_vscode.json` for VS Code-based integrations
- Start the bridge server: `python3 vscode_bridge.py`

#### Other MCP Clients
- Use `mcp_config.json` with your preferred MCP client
- The server uses workspace environment variables for portability

---

## 🛠️ Available Tools

### Basic Development Tools

### 1. **gradle_build** - Build Android Projects
```
Build your Android project using Gradle
Parameters:
- task: Gradle task to run (default: "assembleDebug")
- clean: Run clean before build (default: false)
```

### 2. **run_tests** - Execute Tests
```
Run Android unit tests or instrumented tests
Parameters:
- test_type: "unit", "instrumented", or "all" (default: "unit")
```

### 3. **create_kotlin_file** - Generate Kotlin Classes
```
Create new Kotlin files with proper templates
Parameters:
- file_path: Relative path for the new file
- package_name: Package name for the class
- class_name: Name of the class
- class_type: "activity", "fragment", "class", "data_class", or "interface"
```

### 4. **create_layout_file** - Generate Android Layouts
```
Create new Android layout XML files
Parameters:
- layout_name: Name of the layout file (without .xml)
- layout_type: "activity", "fragment", "item", or "custom"
```

### 5. **analyze_project** - Project Analysis
```
Analyze Android project structure and configuration
Parameters:
- analysis_type: "structure", "dependencies", "manifest", or "all"
```

---

## 🚀 Enhanced Tools for Complex Development

### UI Development Tools

### 6. **create_compose_component** - Jetpack Compose Components
```
Create modern Jetpack Compose UI components
Parameters:
- file_path: Path for the Compose file
- component_name: Name of the Compose component
- component_type: "screen", "component", "dialog", "bottom_sheet"
- package_name: Package name
- uses_state: Include state management (default: false)
- uses_navigation: Include navigation (default: false)
```

### 7. **create_custom_view** - Custom Android Views
```
Create custom Android View components
Parameters:
- file_path: Path for the custom view
- view_name: Name of the custom view
- package_name: Package name
- view_type: "view", "viewgroup", "compound"
- has_attributes: Include custom attributes (default: false)
```

### 8. **create_complex_layout** - Advanced Layouts
```
Create complex layouts with RecyclerView, ViewPager, etc.
Parameters:
- layout_name: Layout file name
- layout_complexity: "recyclerview", "viewpager", "coordinator", "motion"
- include_adapter: Generate adapter code (default: true)
- item_layout: Item layout name for lists
```

### Architecture Tools

### 9. **setup_mvvm_architecture** - MVVM Pattern
```
Set up MVVM architecture with ViewModel and Repository
Parameters:
- feature_name: Name of the feature/module
- package_name: Base package name
- include_repository: Include Repository pattern (default: true)
- include_use_cases: Include Use Cases/Clean Architecture (default: false)
- data_source: "network", "database", "both"
```

### 10. **setup_dependency_injection** - Hilt DI
```
Set up Hilt dependency injection
Parameters:
- module_name: Name of the DI module
- package_name: Package name
- injection_type: "network", "database", "repository", "use_case"
```

### Data Layer Tools

### 11. **setup_room_database** - Room Database
```
Set up Room database with entities and DAOs
Parameters:
- database_name: Name of the database
- package_name: Package name
- entities: List of entity names
- include_migration: Include migration setup (default: false)
```

### 12. **setup_retrofit_api** - Retrofit Networking
```
Set up Retrofit API client with endpoints
Parameters:
- api_name: Name of the API service
- package_name: Package name
- base_url: API base URL
- endpoints: API endpoints configuration
- include_interceptors: Include logging/auth interceptors (default: true)
```

### Testing Tools

### 13. **generate_test_suite** - Comprehensive Testing
```
Generate comprehensive test suites
Parameters:
- class_to_test: Class to generate tests for
- test_type: "unit", "integration", "ui"
- include_mockito: Include Mockito mocks (default: true)
- test_coverage: "basic", "comprehensive"
```

### Build Configuration Tools

### 14. **configure_build_variants** - Build Variants
```
Configure build variants and flavors
Parameters:
- variants: Build variant names
- flavors: Product flavor names
- configuration_type: "development", "staging", "production"
```

---

## 📂 Resources

The server provides access to your Android project files as MCP resources:

- **Android Configuration Files**: `AndroidManifest.xml`, `build.gradle`, `settings.gradle`
- **Kotlin Source Files**: All `.kt` files in `src/main/java`, `src/main/kotlin`
- **Layout Files**: All XML files in `res/layout/`
- **Test Files**: Kotlin files in test directories

---

## 💡 Usage Examples

Once integrated with an AI agent, you can use natural language commands like:

- *"Analyze my Android project structure"*
- *"Create a new LoginActivity with proper Kotlin structure"*
- *"Build my app in debug mode"*
- *"Run my unit tests and show the results"*
- *"Show me all my layout files"*
- *"Create a new fragment for user profile"*
- *"Generate a data class for User with id, name, and email properties"*

---

## 🔧 Configuration Files

The installer creates multiple configuration files for different use cases:

- **`mcp_config_claude.json`** - For Claude Desktop (uses `${workspaceRoot}`)
- **`mcp_config_vscode.json`** - For VS Code extensions (uses `${workspaceFolder}`)
- **`mcp_config.json`** - Generic configuration (uses `${WORKSPACE_ROOT}`)

### Example Claude Desktop Configuration
```json
{
  "mcpServers": {
    "kotlin-android": {
      "command": "kotlin-android-mcp",
      "args": [],
      "env": {
        "PROJECT_PATH": "${workspaceRoot}"
      }
    }
  }
}
```

---

## 🧪 Testing

Verify your installation works correctly:

```bash
# Run comprehensive tests
python3 comprehensive_test.py

# Test specific functionality
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | python3 simple_mcp_server.py /path/to/android/project
```

---

## 🏗️ Architecture

### Core Components

- **`simple_mcp_server.py`** - Main MCP server implementation
- **`install.py`** - Installation and configuration script
- **`vscode_bridge.py`** - HTTP bridge for VS Code integration
- **`comprehensive_test.py`** - Test suite for validation
- **`__main__.py`** - Module entry point (allows `python -m kotlin_android_mcp`)

### Project Structure

The clean project structure after setup:
```
kotlin-mcp-server/
├── 📄 Core Files
│   ├── simple_mcp_server.py     # Main MCP server
│   ├── install.py               # Installation script
│   ├── requirements.txt         # Dependencies
│   └── __main__.py             # Module entry point
│
├── 🔧 Configuration Files
│   ├── mcp_config.json         # Generic MCP configuration
│   ├── mcp_config_claude.json  # Claude Desktop specific
│   └── mcp_config_vscode.json  # VS Code specific
│
├── 🧪 Testing & Integration
│   ├── comprehensive_test.py   # Complete test suite
│   └── vscode_bridge.py        # HTTP bridge for VS Code
│
└── 📚 Documentation
    └── README.md               # This file
```

### Supported Android Project Structure

The server works with standard Android project structures:
```
android-project/
├── app/
│   ├── build.gradle(.kts)
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml
│       │   ├── java/com/example/
│       │   ├── kotlin/com/example/
│       │   └── res/layout/
│       ├── test/
│       └── androidTest/
├── build.gradle(.kts)
└── settings.gradle(.kts)
```

### Alternative Installation Methods

```bash
# Method 1: Direct execution
python3 simple_mcp_server.py /path/to/android/project

# Method 2: Module execution (after installation)
python3 -m kotlin_android_mcp /path/to/android/project

# Method 3: System command (after installation)
kotlin-android-mcp /path/to/android/project
```
