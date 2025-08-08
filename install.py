#!/usr/bin/env python3
"""
Setup script for Kotlin Android MCP Server
Handles installation and configuration for different deployment scenarios
"""

import os
import sys
import json
import shutil
from pathlib import Path

def create_symlink_installation():
    """Create a symlink-based installation in user's local bin"""
    home = Path.home()
    local_bin = home / ".local" / "bin"
    local_bin.mkdir(parents=True, exist_ok=True)

    script_dir = Path(__file__).parent.absolute()
    server_script = script_dir / "simple_mcp_server.py"

    symlink_path = local_bin / "kotlin-android-mcp"

    if symlink_path.exists():
        symlink_path.unlink()

    # Create a wrapper script
    wrapper_content = f"""#!/bin/bash
cd "{script_dir}"
python3 simple_mcp_server.py "$@"
"""

    symlink_path.write_text(wrapper_content)
    symlink_path.chmod(0o755)

    return symlink_path

def update_config_file(config_file, installation_type, script_dir=None):
    """Update configuration file based on installation type"""

    configs = {
        "portable": {
            "command": "python3",
            "args": ["simple_mcp_server.py"],
            "cwd": str(script_dir) if script_dir else "."
        },
        "installable": {
            "command": "kotlin-android-mcp",
            "args": []
        },
        "module": {
            "command": "python3",
            "args": ["-m", "kotlin_android_mcp"],
            "cwd": str(script_dir) if script_dir else "."
        }
    }

    config = configs.get(installation_type, configs["portable"])

    # Don't set PROJECT_PATH at install time - let it be dynamic
    mcp_config = {
        "mcpServers": {
            "kotlin-android": {
                **config,
                "env": {
                    "PROJECT_PATH": "${WORKSPACE_ROOT}"
                }
            }
        }
    }

    # Create multiple config examples
    configs_to_create = {
        "mcp_config.json": mcp_config,
        "mcp_config_claude.json": {
            "mcpServers": {
                "kotlin-android": {
                    **config,
                    "env": {
                        "PROJECT_PATH": "${workspaceRoot}"
                    }
                }
            }
        },
        "mcp_config_vscode.json": {
            "mcpServers": {
                "kotlin-android": {
                    **config,
                    "env": {
                        "PROJECT_PATH": "${workspaceFolder}"
                    }
                }
            }
        }
    }

    created_files = []
    for filename, config_content in configs_to_create.items():
        config_path = Path(config_file).parent / filename
        with open(config_path, 'w') as f:
            json.dump(config_content, f, indent=2)
        created_files.append(config_path)

    return created_files

def main():
    script_dir = Path(__file__).parent.absolute()

    print("🔧 Kotlin Android MCP Server Setup")
    print("=" * 40)

    # Check Python
    try:
        import subprocess
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return 1

    # Install dependencies
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True, cwd=script_dir)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return 1

    # Make scripts executable
    scripts = ["simple_mcp_server.py", "mcp_server.py", "servers/mcp-process/mcp-gradle-wrapper.sh"]
    for script in scripts:
        script_path = script_dir / script
        if script_path.exists():
            script_path.chmod(0o755)

    print("\n🔧 Choose installation type:")
    print("1. Portable (run from this directory)")
    print("2. System installation (add to PATH)")
    print("3. Python module (importable)")

    choice = input("Enter choice (1-3) [1]: ").strip() or "1"

    if choice == "1":
        # Portable installation
        config_files = update_config_file(script_dir / "mcp_config.json", "portable", script_dir)
        print(f"✅ Portable configuration created")
        print(f"📁 Server directory: {script_dir}")

    elif choice == "2":
        # System installation
        try:
            symlink_path = create_symlink_installation()
            config_files = update_config_file(script_dir / "mcp_config.json", "installable")
            print(f"✅ System installation created: {symlink_path}")
            print("🔧 Command 'kotlin-android-mcp' is now available")
        except Exception as e:
            print(f"❌ System installation failed: {e}")
            return 1

    elif choice == "3":
        # Python module installation
        config_files = update_config_file(script_dir / "mcp_config.json", "module", script_dir)
        print(f"✅ Module configuration created")
        print("🔧 Can be run with: python -m kotlin_android_mcp")

    else:
        print("❌ Invalid choice")
        return 1

    print("\n📄 Configuration files created:")
    for config_file in config_files:
        print(f"   📝 {config_file.name}")

    print("\n🎉 Setup complete!")
    print("\n📋 Integration Instructions:")
    print("\n🔹 Claude Desktop:")
    print("   Copy content from 'mcp_config_claude.json' to:")
    print("   ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("   The server will automatically use your current workspace/project")

    print("\n🔹 VS Code:")
    print("   Use 'mcp_config_vscode.json' for VS Code extensions")
    print("   The ${workspaceFolder} variable will be resolved automatically")

    print("\n🔹 Other MCP Clients:")
    print("   Use 'mcp_config.json' with ${WORKSPACE_ROOT} placeholder")
    print("   Update PROJECT_PATH environment variable as needed")

    print(f"\n🧪 Test the server:")
    if choice == "2":
        print("   kotlin-android-mcp /path/to/android/project")
    else:
        print(f"   cd {script_dir}")
        print("   python3 simple_mcp_server.py /path/to/android/project")

    print("\n💡 Pro Tip:")
    print("   The server now uses workspace/project context automatically!")
    print("   No need to hardcode project paths in the configuration.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
