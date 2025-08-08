#!/usr/bin/env python3
"""
Kotlin Android MCP Server - Installable Module
This allows the server to be run as: python -m kotlin_android_mcp
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import and run the server
from simple_mcp_server import main

if __name__ == "__main__":
    main()
