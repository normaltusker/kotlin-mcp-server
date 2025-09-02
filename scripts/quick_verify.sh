#!/bin/bash
# Quick verification script to ensure tool count parity

echo "🔧 Kotlin MCP Server - Tool Count Verification"
echo "=============================================="

# Get server tool count
echo "📊 Checking server tool count..."
SERVER_COUNT=$(python3 kotlin_mcp_server.py --list-tools 2>/dev/null | grep "Available tools" | grep -o '[0-9]\+' || echo "0")
echo "   Server reports: $SERVER_COUNT tools"

# Check VS Code parity  
echo "📱 Checking VS Code parity..."
PARITY_RESULT=$(python3 scripts/vscode_parity_check.py 2>/dev/null | grep "VS Code visible:" | grep -o '[0-9]\+' || echo "0")
echo "   VS Code would show: $PARITY_RESULT tools"

# Results
echo
if [ "$SERVER_COUNT" = "$PARITY_RESULT" ] && [ "$SERVER_COUNT" -gt 0 ]; then
    echo "✅ SUCCESS: Tool count parity achieved ($SERVER_COUNT = $PARITY_RESULT)"
    echo "🎉 VS Code will show the same number of tools as the server!"
    exit 0
else
    echo "❌ FAILED: Tool count mismatch ($SERVER_COUNT ≠ $PARITY_RESULT)"
    echo "🔍 Run 'make verify-tools' for detailed analysis"
    exit 1
fi
