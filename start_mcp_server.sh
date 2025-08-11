#!/bin/bash
# MCP Server Launcher Script for IntelliJ Integration
# This script ensures proper environment setup and absolute path resolution

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up environment
export GPG_TTY=$(tty)
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Change to script directory to ensure relative imports work
cd "${SCRIPT_DIR}"

# Launch the MCP server with absolute path
exec python3 "${SCRIPT_DIR}/kotlin_mcp_server.py" "$@"
