#!/usr/bin/env python3
"""
Kotlin Android MCP Server - Installable Module
This allows the server to be run as: python -m kotlin_android_mcp
"""

import sys
from pathlib import Path

# Import and run the server
from kotlin_mcp_server import main

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    main()
