# Configuration Template for Kotlin MCP Server

## How to Configure

1. **Copy the appropriate config file:**
   - For Claude Desktop: Copy `mcp_config_claude.json` → `claude_desktop_config.json`
   - For VS Code: Copy `mcp_config_vscode.json` and reference in settings.json
   - For General use: Copy `mcp_config.json`

2. **Replace placeholders:**

### Required Replacements

#### `${MCP_SERVER_DIR}`
Replace with the absolute path to your kotlin-mcp-server directory:

**Examples:**
- macOS: `/Users/yourusername/Documents/kotlin-mcp-server`
- Linux: `/home/yourusername/kotlin-mcp-server`
- Windows: `C:\\Users\\yourusername\\kotlin-mcp-server`

**How to find your path:**
```bash
cd /path/to/kotlin-mcp-server
pwd
```

#### Workspace Variables (IDE-specific)
- `${workspaceRoot}` - Used by Claude Desktop
- `${workspaceFolder}` - Used by VS Code
- `${WORKSPACE_ROOT}` - General environment variable

These are automatically resolved by the respective IDEs.

## Configuration Examples

### Claude Desktop (macOS)
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "kotlin-android": {
      "command": "python3",
      "args": ["kotlin_mcp_server.py"],
      "cwd": "/Users/yourusername/Documents/kotlin-mcp-server",
      "env": {
        "PROJECT_PATH": "${workspaceRoot}",
        "WORKSPACE_PATH": "${workspaceRoot}"
      }
    }
  }
}
```

### VS Code
Location: User or Workspace `settings.json`

```json
{
  "mcp.server.configFiles": [
    "/Users/yourusername/Documents/kotlin-mcp-server/mcp_config_vscode.json"
  ]
}
```

And update the `mcp_config_vscode.json` with your actual path:
```json
{
  "mcpServers": {
    "kotlin-android": {
      "command": "python3",
      "args": ["kotlin_mcp_server.py"],
      "cwd": "/Users/yourusername/Documents/kotlin-mcp-server",
      "env": {
        "PROJECT_PATH": "${workspaceFolder}",
        "WORKSPACE_PATH": "${workspaceFolder}"
      }
    }
  }
}
```

### JetBrains IDEs
Configure through IDE settings and point to your updated `mcp_config.json` file.

## Environment Variables

You can also use environment variables to make configs more portable:

```bash
# Set in your shell profile (.bashrc, .zshrc, etc.)
export MCP_SERVER_DIR="/path/to/kotlin-mcp-server"
export MCP_WORKSPACE_DIR="/path/to/your/android/project"
```

Then use in config:
```json
{
  "mcpServers": {
    "kotlin-android": {
      "command": "python3",
      "args": ["kotlin_mcp_server.py"],
      "cwd": "$MCP_SERVER_DIR",
      "env": {
        "PROJECT_PATH": "$MCP_WORKSPACE_DIR"
      }
    }
  }
}
```

## Configuration Validation

Test your configuration:

```bash
# Test server starts correctly
cd /your/kotlin-mcp-server/path
python3 kotlin_mcp_server.py --test

# Test with specific project path
PROJECT_PATH="/path/to/android/project" python3 kotlin_mcp_server.py --test
```

## Troubleshooting

### Common Issues

1. **Path not found errors:**
   - Verify `cwd` path exists and contains `kotlin_mcp_server.py`
   - Use absolute paths, not relative paths
   - Check file permissions

2. **Permission denied:**
   ```bash
   chmod +x kotlin_mcp_server.py
   ```

3. **Python not found:**
   - Use full path to Python: `/usr/bin/python3` or `/usr/local/bin/python3`
   - Check with: `which python3`

4. **Environment variables not resolved:**
   - Some IDEs may not support shell variable expansion
   - Use absolute paths in those cases
