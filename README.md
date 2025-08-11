# Enterprise Kotlin Android MCP Server

A comprehensive Model Context Protocol (MCP) server that provides AI agents with enterprise-grade access to Kotlin-based Android development projects. This server enables context-aware assistance with advanced security, privacy compliance, AI integration, and comprehensive development tools.

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

#### **2. Install Python Dependencies**
```bash
# Install core dependencies
pip install -r requirements.txt

# Or use the automated installer
python3 install.py
```

#### **3. Install Required IDE Extensions/Plugins**
See the [Plugin Requirements](#-required-pluginsextensions) section below for IDE-specific extensions.

#### **4. Environment Configuration**
Create a `.env` file in the project root:

```bash
# Copy the example file and customize
cp .env.example .env

# Edit with your settings
nano .env  # or your preferred editor
```

**Required Variables to Update:**
```bash
# MUST UPDATE THESE PATHS
WORKSPACE_PATH=/Users/yourusername/AndroidStudioProjects/YourApp
MCP_SERVER_DIR=/Users/yourusername/Documents/kotlin-mcp-server

# Security (generate strong password)
MCP_ENCRYPTION_PASSWORD=$(openssl rand -base64 32)
COMPLIANCE_MODE=gdpr,hipaa

# Optional: AI Integration
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**Find Your Paths:**
```bash
# For MCP_SERVER_DIR
cd /path/to/kotlin-mcp-server && pwd

# For WORKSPACE_PATH  
cd /path/to/your/android/project && pwd
```

#### **5. Configure Your IDE**
Follow the IDE-specific configuration instructions in the [Configuration](#%EF%B8%8F-configuration--plugin-requirements) section.

**⚠️ Important Configuration Steps:**

1. **Update Config Files:** The provided config files contain placeholders that MUST be updated:
   - Replace `${MCP_SERVER_DIR}` with your actual kotlin-mcp-server path
   - Update environment variables with your actual values

2. **Find Your MCP Server Path:**
   ```bash
   cd /path/to/kotlin-mcp-server
   pwd  # Copy this output
   ```

3. **Update Config Files:** See [`CONFIG_TEMPLATE.md`](CONFIG_TEMPLATE.md) for detailed instructions.

#### **6. Test Installation**
```bash
# Validate your configuration first
python3 validate_config.py

# Run basic functionality test
python simple_test.py

# Run comprehensive tests
python test_mcp_comprehensive.py

# Verify server starts correctly
python simple_mcp_server.py /path/to/project

# Test VS Code bridge server (optional)
python3 vscode_bridge.py &
sleep 2
curl http://localhost:8080/health
# Should return: {"status": "healthy", ...}
kill %1  # Stop background bridge server
```

### ⚡ **Quick Setup Commands**
```bash
# One-line setup for development
make setup-dev

# Quick validation
make dev-check

# Full quality pipeline
make ci

# Test VS Code bridge server (optional)
python3 vscode_bridge.py --test-mode
```

---

## 📚 **Comprehensive Usage Guide**

### 🔒 **Security & Privacy Features**

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
      "args": ["/path/to/kotlin-mcp-server/ai_integration_server.py"],
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
   Add to VS Code `settings.json` (`Cmd/Ctrl + Shift + P` → "Preferences: Open Settings (JSON)"):
   ```json
   {
     "mcp.server.configFiles": [
       "${YOUR_MCP_SERVER_PATH}/mcp_config_vscode.json"
     ],
     "python.defaultInterpreterPath": "/usr/bin/python3",
     "python.linting.enabled": true,
     "python.formatting.provider": "black",
     "python.sortImports.path": "isort"
   }
   ```

   **⚠️ Important:** Replace `${YOUR_MCP_SERVER_PATH}` with the actual absolute path.

   **Example:**
   ```json
   {
     "mcp.server.configFiles": [
       "/Users/yourusername/Documents/kotlin-mcp-server/mcp_config_vscode.json"
     ]
   }
   ```

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
   - Go to `File > Settings > Tools > MCP Server`
   - Click `+` to add new server:
     - **Name:** `Kotlin Android MCP Server`
     - **Configuration File:** Select `mcp_config.json`
     - **Environment Variables:**
       - `PROJECT_PATH`: `${PROJECT_DIR}`
       - `PYTHON_PATH`: `/usr/bin/python3`

3. **Android Studio Specific:**
   ```xml
   <!-- Add to .idea/workspace.xml -->
   <component name="MCPServerManager">
     <option name="servers">
       <server name="kotlin-android" configFile="mcp_config.json" autoStart="true"/>
     </option>
   </component>
   ```

#### **Claude Desktop**

1. **Configuration File Location:**
   - **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/claude/claude_desktop_config.json`

2. **Configuration Content:**
   ```json
   {
     "mcpServers": {
       "kotlin-android": {
         "command": "python3",
         "args": ["${YOUR_MCP_SERVER_PATH}/ai_integration_server.py"],
         "env": {
           "WORKSPACE_PATH": "${workspaceRoot}",
           "MCP_ENCRYPTION_PASSWORD": "your-secure-password",
           "COMPLIANCE_MODE": "gdpr,hipaa"
         }
       }
     }
   }
   ```

   **⚠️ Important:** Replace `${YOUR_MCP_SERVER_PATH}` with the actual absolute path to your kotlin-mcp-server directory.

   **Example:**
   ```json
   {
     "mcpServers": {
       "kotlin-android": {
         "command": "python3",
         "args": ["/Users/yourusername/Documents/kotlin-mcp-server/ai_integration_server.py"],
         "env": {
           "WORKSPACE_PATH": "${workspaceRoot}",
           "MCP_ENCRYPTION_PASSWORD": "your-secure-password",
           "COMPLIANCE_MODE": "gdpr,hipaa"
         }
       }
     }
   }
   ```

#### **Cursor IDE**

1. **Install Extensions:**
   - Same extensions as VS Code (Cursor is VS Code-based)
   - Python, Pylint, Black Formatter, isort

2. **Configuration:**
   Use same `settings.json` configuration as VS Code

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
python3 -c "import enhanced_mcp_server; print('Import successful')"

# Check Python path
python3 -c "import sys; print(sys.path)"

# Install in development mode
pip install -e .
```

### **Configuration Issues**

#### **Hardcoded Path Problems**
The config files contain placeholders that MUST be replaced:

```bash
# 1. Find your actual paths
cd /path/to/kotlin-mcp-server && pwd
cd /path/to/android/project && pwd

# 2. Update config files - replace ${MCP_SERVER_DIR} with actual path
# Example: Change this
"cwd": "${MCP_SERVER_DIR}"
# To this (your actual path)
"cwd": "/Users/yourusername/Documents/kotlin-mcp-server"

# 3. Use CONFIG_TEMPLATE.md for detailed instructions
cat CONFIG_TEMPLATE.md
```

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
python3 -m cProfile enhanced_mcp_server.py
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
   python3 simple_mcp_server.py --test
   
   # Test enhanced features
   python3 enhanced_mcp_server.py --test
   
   # Test AI integration
   python3 ai_integration_server.py --test
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
  "current_workspace": "/Users/you/AndroidProject",
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

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Configure environment variables (`.env` file)
- [ ] Install required IDE plugins/extensions
- [ ] Choose your AI agent integration (Claude, VS Code, etc.)
- [ ] Set up your Android project workspace
- [ ] Configure compliance requirements (GDPR/HIPAA)
- [ ] Test basic functionality
- [ ] **Optional**: Test VS Code bridge server (`python3 vscode_bridge.py`)
- [ ] Explore advanced features

**Ready to build enterprise-grade Android applications with AI assistance and full compliance support!** 🎉
