# Migration Guide: Kotlin MCP Server v1 → v2

## Overview

This guide helps you migrate from the original Kotlin MCP Server to the enhanced v2 implementation with modern MCP SDK patterns and 2025-06-18 specification compliance.

## 🚀 Quick Start

### 1. Update Dependencies

```bash
# Install enhanced requirements
pip install -r requirements.txt

# Key new dependencies:
# - pydantic>=2.0.0 (for schema validation)
# - typing-extensions>=4.8.0 (for enhanced typing)
```

### 2. Update Configuration

**Old v1 config (`mcp_config.json`):**
```json
{
  "mcpServers": {
    "kotlin-android": {
      "command": "python3",
      "args": ["kotlin_mcp_server.py"],
      "cwd": "${MCP_SERVER_DIR}",
      "env": {
        "PROJECT_PATH": "${WORKSPACE_ROOT}"
      }
    }
  }
}
```

**New v2 config (`mcp_config_v2.json`):**
```json
{
  "mcpServers": {
    "kotlin-android-v2": {
      "command": "python3", 
      "args": ["kotlin_mcp_server_v2_enhanced.py"],
      "cwd": "${MCP_SERVER_DIR}",
      "env": {
        "PROJECT_PATH": "${WORKSPACE_ROOT}",
        "PYTHONPATH": "${MCP_SERVER_DIR}"
      },
      "capabilities": [
        "tools", "resources", "prompts", "logging", "roots"
      ]
    }
  }
}
```

### 3. Switch Server Implementation

**Replace this:**
```bash
python3 kotlin_mcp_server.py /path/to/project
```

**With this:**
```bash
python3 kotlin_mcp_server_v2_enhanced.py /path/to/project
```

## 🔄 Feature Comparison

| Feature | v1 | v2 Enhanced | Benefits |
|---------|----|-----------| -------- |
| **Protocol Version** | 2024-11-05 | 2025-06-18 | Latest spec compliance |
| **Tool Validation** | Basic | Pydantic schemas | Auto-validation, better errors |
| **Resource Management** | None | Full support | File access, security |
| **Prompt Templates** | None | Built-in templates | Reusable patterns |
| **Progress Tracking** | None | Real-time updates | Better UX for long operations |
| **Error Handling** | Basic | Enhanced | Standardized JSON-RPC errors |
| **Security** | Basic | Enhanced | Path validation, input sanitization |
| **Logging** | stdout | Structured | Proper log levels, debugging |

## 🛠 Tool Changes

### Enhanced Tool Definitions

**v1 Tools** had basic parameter checking:
```json
{
  "name": "create_kotlin_file",
  "description": "Create Kotlin file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {"type": "string"},
      "class_name": {"type": "string"}
    }
  }
}
```

**v2 Tools** have comprehensive schema validation:
```json
{
  "name": "create_kotlin_file", 
  "description": "Create production-ready Kotlin files...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Relative path for new Kotlin file"
      },
      "class_type": {
        "type": "string",
        "pattern": "^(activity|fragment|class|data_class|interface|viewmodel|repository|service)$",
        "description": "Type of class to create"
      }
    },
    "required": ["file_path", "package_name", "class_name"]
  }
}
```

### New Tools Available

1. **Enhanced Validation**: All tools now have Pydantic schema validation
2. **Progress Tracking**: Long-running operations show progress
3. **Better Error Messages**: Detailed validation errors

## 📋 Step-by-Step Migration

### Step 1: Backup Current Setup

```bash
# Backup your current configuration
cp mcp_config.json mcp_config_backup.json

# Backup any custom modifications
cp kotlin_mcp_server.py kotlin_mcp_server_v1_backup.py
```

### Step 2: Install v2 Server

```bash
# Copy the enhanced server
cp kotlin_mcp_server_v2_enhanced.py your_project/

# Update configuration
cp mcp_config_v2.json your_project/mcp_config.json
```

### Step 3: Test Basic Functionality

```bash
# Test server starts correctly
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | \
  python3 kotlin_mcp_server_v2_enhanced.py /path/to/your/project

# Test tools list
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | \
  python3 kotlin_mcp_server_v2_enhanced.py /path/to/your/project
```

### Step 4: Update Client Integration

If you have custom client code, update it to handle the enhanced responses:

**v1 Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "message": "File created"
  }
}
```

**v2 Response:**
```json
{
  "jsonrpc": "2.0", 
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"success\": true, \"file_path\": \"Test.kt\", \"message\": \"Created class Test\"}"
    }]
  }
}
```

### Step 5: Leverage New Features

#### Use Enhanced Error Handling
```python
# v2 provides detailed validation errors
try:
    result = call_tool("create_kotlin_file", {
        "file_path": "Test.kt",
        "class_type": "invalid_type"  # Will be caught by validation
    })
except ValidationError as e:
    print(f"Validation failed: {e}")
```

#### Use Resource Management
```bash
# List available project resources
echo '{"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}' | \
  python3 kotlin_mcp_server_v2_enhanced.py /path/to/project

# Read specific resource
echo '{"jsonrpc": "2.0", "id": 4, "method": "resources/read", "params": {"uri": "file:///path/to/build.gradle"}}' | \
  python3 kotlin_mcp_server_v2_enhanced.py /path/to/project
```

#### Use Prompt Templates
```bash
# List available prompts
echo '{"jsonrpc": "2.0", "id": 5, "method": "prompts/list", "params": {}}' | \
  python3 kotlin_mcp_server_v2_enhanced.py /path/to/project

# Get specific prompt
echo '{"jsonrpc": "2.0", "id": 6, "method": "prompts/get", "params": {"name": "generate_mvvm_viewmodel", "arguments": {"feature_name": "UserProfile"}}}' | \
  python3 kotlin_mcp_server_v2_enhanced.py /path/to/project
```

## ⚠️ Breaking Changes

### 1. Response Format Changes

**v1**: Direct result object
```json
{"success": true, "message": "Done"}
```

**v2**: MCP-compliant content format
```json
{
  "content": [{
    "type": "text", 
    "text": "{\"success\": true, \"message\": \"Done\"}"
  }]
}
```

### 2. Error Response Format

**v1**: Custom error format
```json
{"success": false, "error": "Something failed"}
```

**v2**: JSON-RPC standard errors
```json
{
  "error": {
    "code": -32602,
    "message": "Invalid params: Something failed"
  }
}
```

### 3. Tool Parameter Validation

**v1**: Runtime validation (loose)
**v2**: Schema validation (strict)

Parameters are now validated against Pydantic schemas, so invalid inputs will be rejected before execution.

## 🚨 Troubleshooting

### Common Issues

#### 1. "Import mcp.server could not be resolved"
The built-in `mcp` package may not have the expected server modules. The v2 implementation uses a compatible approach that works with available packages.

#### 2. Validation Errors
```bash
# Check your tool parameters match the new schemas
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | \
  python3 kotlin_mcp_server_v2_enhanced.py /path/to/project
```

#### 3. Path Permission Errors
v2 has enhanced security - ensure your project path is properly set:
```bash
python3 kotlin_mcp_server_v2_enhanced.py /full/path/to/android/project
```

#### 4. Missing Dependencies
```bash
pip install pydantic typing-extensions
```

### Rollback Plan

If you need to rollback to v1:

```bash
# Restore original files
cp kotlin_mcp_server_v1_backup.py kotlin_mcp_server.py
cp mcp_config_backup.json mcp_config.json

# Use original startup
python3 kotlin_mcp_server.py /path/to/project
```

## 🎯 Next Steps

After successful migration:

1. **Explore New Features**: Try the resource management and prompt templates
2. **Update Documentation**: Update any internal docs to reflect new capabilities
3. **Performance Testing**: Verify performance with your typical workloads
4. **Security Review**: Review the enhanced security features
5. **Team Training**: Train team members on new capabilities

## 📞 Support

If you encounter issues during migration:

1. Check the demo script: `python3 demo_enhanced_server.py`
2. Review the comprehensive test suite in `tests/test_mcp_server_v2_enhanced.py`
3. Consult the modernization summary: `MCP_V2_MODERNIZATION_SUMMARY.md`

## 🎉 Benefits After Migration

- ✅ **Future-Proof**: 2025-06-18 MCP specification compliance
- ✅ **Better Validation**: Automatic schema validation prevents errors
- ✅ **Enhanced Security**: Path validation and input sanitization
- ✅ **Improved UX**: Progress tracking and better error messages
- ✅ **More Capable**: Resource management, prompt templates, structured logging
- ✅ **Maintainable**: Clean architecture, comprehensive testing, documentation

The enhanced v2 server provides a solid foundation for current and future Android development workflows!
