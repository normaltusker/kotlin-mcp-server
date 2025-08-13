#!/usr/bin/env python3
"""
Setup script for Kotlin Android MCP Server
Handles installation and configuration for different deployment scenarios

This script provides an automated installation and configuration system for the
Kotlin Android MCP Server, supporting multiple deployment modes:
- Portable: Run directly from project directory
- System: Install command to system PATH
- Module: Enable Python module execution

Key Features:
- Interacti    # Step 7: Display results and configuration summary
    print("\n📄 Configuration files created:")
    for config_file in config_files:
        print(f"   📝 {config_file.name}")

    print("\n🎉 Setup complete!")

    # Display configuration summary based on user choices
    print(f"\n📋 Configuration Summary:")
    print(f"   🏷️  Server name: {user_config.get('server_name', 'kotlin-android')}")
    if user_config.get('default_project_path'):
        print(f"   📁 Project path: {user_config['default_project_path']}")
    else:
        print(f"   📁 Project path: {'Dynamic (environment variables)' if user_config.get('use_env_vars') else 'Manual configuration required'}")teractive installation modes
- Automatic configuration file generation for different MCP clients
- Smart environment variable handling
- Cross-platform compatibility
- Zero-manual-configuration setup

Author: MCP Development Team
Version: 2.0.0
License: MIT
"""

import json
import sys
from pathlib import Path


def create_symlink_installation():
    """
    Create a symlink-based installation in user's local bin directory

    This function creates a system-wide installation by:
    1. Creating ~/.local/bin directory if it doesn't exist
    2. Creating a wrapper script that calls the MCP server
    3. Making the wrapper executable and accessible via PATH

    Returns:
        Path: The path to the created symlink/wrapper script

    Raises:
        Exception: If the symlink creation fails due to permissions or other issues
    """
    # Get user's home directory and create local bin path
    home = Path.home()
    local_bin = home / ".local" / "bin"

    # Ensure the local bin directory exists (equivalent to mkdir -p)
    local_bin.mkdir(parents=True, exist_ok=True)

    # Get the absolute path to this script's directory
    script_dir = Path(__file__).parent.absolute()

    # Define the path for our command wrapper
    symlink_path = local_bin / "kotlin-android-mcp"

    # Remove existing symlink if it exists to avoid conflicts
    if symlink_path.exists():
        symlink_path.unlink()

    # Create a bash wrapper script that:
    # - Changes to the MCP server directory
    # - Executes the Python server with all passed arguments
    wrapper_content = f"""#!/bin/bash
cd "{script_dir}"
python3 kotlin_mcp_server.py "$@"
"""

    # Write the wrapper script and make it executable
    symlink_path.write_text(wrapper_content)
    symlink_path.chmod(0o755)  # rwxr-xr-x permissions

    return symlink_path


def get_user_configuration():
    """
    Collect user configuration either from command line or interactive prompts

    This function handles:
    1. Command line argument parsing for non-interactive usage
    2. Interactive prompts with input validation
    3. Default value handling for missing parameters
    4. Input sanitization for security

    Returns:
        dict: User configuration containing project settings and preferences
    """
    # Check if running in non-interactive mode (command line arguments provided)
    if len(sys.argv) > 2:
        # Non-interactive mode - extract configuration from command line
        return parse_command_line_config()

    # Interactive mode - prompt user for configuration with validation
    print("\n📋 Configuration Setup:")
    print("You can press Enter to use default values or provide custom settings.")

    # Get project path with validation
    while True:
        try:
            default_project_path = input(
                "📁 Default Android project path (or leave empty for dynamic): "
            ).strip()
            # Basic path validation and sanitization
            if default_project_path:
                # Remove dangerous characters and validate path format
                if any(char in default_project_path for char in ["|", "&", ";", "$", "`"]):
                    print("❌ Invalid characters in path. Please use a standard file path.")
                    continue
                # Convert to absolute path and validate
                validated_path = str(Path(default_project_path).expanduser().resolve())
                default_project_path = validated_path
            break
        except (OSError, ValueError) as e:
            print(f"❌ Invalid path: {e}. Please try again.")
            continue

    # Get server name with validation
    while True:
        server_name = input("🏷️  MCP Server name [kotlin-android]: ").strip()
        if not server_name:
            server_name = "kotlin-android"  # Default value
        # Validate server name (alphanumeric, hyphens, underscores only)
        if not server_name.replace("-", "").replace("_", "").isalnum():
            print("❌ Server name must contain only letters, numbers, hyphens, and underscores.")
            continue
        break

    # Get environment variable preference with validation
    while True:
        env_input = (
            input("🌐 Use environment variables for dynamic project paths? [y/N]: ").strip().lower()
        )
        if env_input in ["", "n", "no"]:
            use_env_vars = False
            break
        elif env_input in ["y", "yes"]:
            use_env_vars = True
            break
        else:
            print("❌ Please enter 'y' for yes or 'n' for no (or press Enter for default).")
            continue

    return {
        "default_project_path": default_project_path or None,
        "server_name": server_name,
        "use_env_vars": use_env_vars,
    }


def parse_command_line_config():
    """
    Parse configuration from command line arguments for non-interactive setup

    Command line argument format:
    python install.py [install_type] [project_path] [server_name] [use_env_vars]

    Arguments:
    - install_type: 1=Portable, 2=System, 3=Module (handled by main())
    - project_path: Path to Android project, or 'none' for dynamic configuration
    - server_name: MCP server identifier (default: kotlin-android)
    - use_env_vars: 'true'/'false' for environment variable usage

    Returns:
        dict: Configuration dictionary with parsed values and defaults

    Example:
        python install.py 1 /path/to/project my-server true
        -> Portable installation with fixed path, custom name, env vars enabled
    """
    # Initialize configuration with sensible defaults
    config = {
        "default_project_path": None,  # No fixed path by default
        "server_name": "kotlin-android",  # Standard server name
        "use_env_vars": True,  # Enable environment variables by default
    }

    # Parse arguments: python install.py [install_type] [project_path] [server_name] [use_env_vars]
    # sys.argv[0] = script name, sys.argv[1] = install_type, sys.argv[2] onwards = our config

    if len(sys.argv) > 2:
        # Parse project path - 'none' means dynamic configuration
        config["default_project_path"] = sys.argv[2] if sys.argv[2] != "none" else None

    if len(sys.argv) > 3:
        # Parse custom server name
        config["server_name"] = sys.argv[3]

    if len(sys.argv) > 4:
        # Parse environment variable preference - accept various true/false formats
        config["use_env_vars"] = sys.argv[4].lower() in ["true", "yes", "1", "y"]

    # Display parsed configuration for user confirmation
    print("📋 Using command-line configuration:")
    print(f"   🏷️  Server name: {config['server_name']}")
    print(f"   📁 Project path: {config['default_project_path'] or 'Dynamic'}")
    print(f"   🌐 Environment variables: {'Yes' if config['use_env_vars'] else 'No'}")

    return config


def update_config_file(config_file, installation_type, script_dir=None, user_config=None):
    """
    Update configuration file based on installation type and user preferences

    This function generates platform-specific MCP configuration files:
    - mcp_config.json: Generic configuration for any MCP client
    - mcp_config_claude.json: Optimized for Claude Desktop with ${workspaceRoot}
    - mcp_config_vscode.json: Optimized for VS Code with ${workspaceFolder}

    Args:
        config_file (Path): Base path for configuration files
        installation_type (str): 'portable', 'installable', or 'module'
        script_dir (Path, optional): Directory containing the MCP server script
        user_config (dict, optional): User preferences from get_user_configuration()

    Returns:
        tuple: (list of created config files, user configuration dict)

    Installation Types:
    - portable: Run directly from project directory with absolute paths
    - installable: Use system command (kotlin-android-mcp)
    - module: Use Python module execution (python -m kotlin_mcp_server)
    """

    # Use provided user configuration or empty dict as fallback
    if user_config is None:
        user_config = {}

    # Determine working directory for the MCP server
    # For portable/module: use absolute script directory
    # For installable: use environment variable placeholder
    if script_dir is None:
        cwd_path = "${MCP_SERVER_DIR}"
        server_script_path = "kotlin_mcp_server.py"
    else:
        cwd_path = str(script_dir)
        server_script_path = str(script_dir / "kotlin_mcp_server.py")

    # Define command configurations for different installation types
    configs = {
        "portable": {
            "command": "python3",  # Use system Python
            "args": [server_script_path],  # Execute server script with absolute path
            "cwd": cwd_path,  # Set working directory
        },
        "installable": {
            "command": "kotlin-android-mcp",  # Use installed system command
            "args": [],  # No additional arguments needed
        },
        "module": {
            "command": "python3",  # Use system Python
            "args": ["-m", "kotlin_mcp_server"],  # Execute as Python module
            "cwd": cwd_path,  # Set working directory
        },
    }

    # Get the appropriate configuration for the installation type
    config = configs.get(installation_type, configs["portable"])

    # Extract user preferences with defaults
    server_name = user_config.get("server_name", "kotlin-android")
    default_project_path = user_config.get("default_project_path")
    use_env_vars = user_config.get("use_env_vars", True)

    # Configure environment variables based on user preferences
    env_config = {}

    if default_project_path:
        # User provided a specific project path - use it directly
        # This creates a fixed configuration for a single project
        env_config["PROJECT_PATH"] = default_project_path

    elif use_env_vars:
        # Use environment variables for dynamic project paths
        # This allows the server to work with different projects
        env_config["PROJECT_PATH"] = "${WORKSPACE_ROOT}"

    else:
        # No project path specified and env vars disabled
        # User will need to manually configure this later
        env_config["PROJECT_PATH"] = "/path/to/android/project"

    # Create base MCP configuration with user's server name
    mcp_config = {"mcpServers": {server_name: {**config, "env": env_config}}}

    # Create platform-specific environment configurations
    # Start with copies of the base environment config
    claude_env = env_config.copy()
    vscode_env = env_config.copy()

    # Override environment variables for platform-specific behavior
    # Only when using dynamic configuration (env vars enabled, no fixed path)
    if use_env_vars and not default_project_path:
        # Claude Desktop uses ${workspaceRoot} variable
        claude_env["PROJECT_PATH"] = "${workspaceRoot}"

        # VS Code uses ${workspaceFolder} variable (standard VS Code variable)
        vscode_env["PROJECT_PATH"] = "${workspaceFolder}"

    # Create multiple config files optimized for different MCP clients
    configs_to_create = {
        # Generic configuration - works with any MCP client
        "mcp_config.json": mcp_config,
        # Claude Desktop optimized configuration
        "mcp_config_claude.json": {"mcpServers": {server_name: {**config, "env": claude_env}}},
        # VS Code optimized configuration
        "mcp_config_vscode.json": {"mcpServers": {server_name: {**config, "env": vscode_env}}},
    }

    # Write all configuration files to disk
    created_files = []
    for filename, config_content in configs_to_create.items():
        config_path = Path(config_file).parent / filename

        # Write JSON with proper formatting (2-space indentation)
        with open(config_path, "w") as f:
            json.dump(config_content, f, indent=2)
        created_files.append(config_path)

    return created_files, user_config


def main():
    """
    Main installation function - orchestrates the entire setup process

    This function handles:
    1. Command line argument parsing and help display
    2. User configuration collection (interactive or non-interactive)
    3. Python environment validation and dependency installation
    4. File permission setup for executable scripts
    5. Installation type selection and execution
    6. Configuration file generation
    7. User guidance and testing instructions

    Installation Flow:
    1. Parse command line arguments or show help
    2. Get user configuration (project path, server name, env vars)
    3. Validate Python installation and install dependencies
    4. Set up file permissions for scripts
    5. Execute chosen installation type (portable/system/module)
    6. Generate platform-specific configuration files
    7. Display integration instructions and testing commands

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Get absolute path to the script directory for all operations
    script_dir = Path(__file__).parent.absolute()

    # Display main header
    print("🔧 Kotlin Android MCP Server Setup")
    print("=" * 40)

    # Handle help requests before any other processing
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print("\n📋 Usage:")
        print("  python install.py [install_type] [project_path] [server_name] [use_env_vars]")
        print("\n📋 Arguments:")
        print("  install_type   : 1=Portable, 2=System, 3=Module")
        print("  project_path   : Path to Android project (or 'none' for dynamic)")
        print("  server_name    : MCP server identifier (default: kotlin-android)")
        print("  use_env_vars   : true/false for environment variable usage")
        print("\n📋 Examples:")
        print("  python install.py 1                                    # Interactive portable")
        print("  python install.py 1 /path/to/project                   # Portable with fixed path")
        print("  python install.py 2 none my-server true               # System with env vars")
        print("  python install.py 3 /home/user/app kotlin-dev false   # Module with fixed path")
        return 0

    # Step 1: Get user configuration (interactive or from command line)
    user_config = get_user_configuration()

    # Step 2: Validate Python installation
    try:
        import subprocess

        # Check Python version and display it to user
        # Use list format to prevent command injection
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True,
            shell=False,  # Explicitly disable shell execution
            timeout=10,  # Add timeout for safety
        )
        print(f"✅ Python: {result.stdout.strip()}")
    except subprocess.TimeoutExpired:
        print("❌ Python version check timed out")
        return 1
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return 1

    # Step 3: Install Python dependencies from requirements.txt
    print("\n📦 Installing dependencies...")
    try:
        # Use the same Python executable that's running this script
        # Install dependencies in the script's directory context
        # Use list format to prevent command injection
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,  # Raise exception on non-zero exit code
            cwd=script_dir,  # Run from script directory
            shell=False,  # Explicitly disable shell execution
            timeout=300,  # 5-minute timeout for package installation
        )
        print("✅ Dependencies installed")
    except subprocess.TimeoutExpired:
        print("❌ Dependency installation timed out")
        return 1
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return 1

    # Step 4: Make scripts executable (Unix-like systems) with secure permissions
    # Set executable permissions for main server script and helper scripts
    scripts = ["kotlin_mcp_server.py", "servers/mcp-process/mcp-gradle-wrapper.sh"]
    for script in scripts:
        script_path = script_dir / script
        if script_path.exists():
            try:
                # Set secure permissions: rwxr-xr-x (755)
                # Owner: read, write, execute
                # Group and others: read, execute only
                script_path.chmod(0o755)
                print(f"✅ Set executable permissions for {script}")
            except OSError as e:
                print(f"⚠️  Warning: Could not set permissions for {script}: {e}")
        else:
            print(f"⚠️  Warning: Script not found: {script}")

    # Step 5: Installation type selection
    print("\n🔧 Choose installation type:")
    print("1. Portable (run from this directory)")
    print("2. System installation (add to PATH)")
    print("3. Python module (importable)")

    # Get installation choice from command line or default to portable
    if len(sys.argv) > 1 and sys.argv[1] in ["1", "2", "3"]:
        choice = sys.argv[1]
    else:
        choice = "1"  # Default to portable installation

    # Step 6: Execute the chosen installation type
    if choice == "1":
        # Portable installation - run directly from project directory
        config_files, user_config = update_config_file(
            script_dir / "mcp_config.json", "portable", script_dir, user_config
        )
        print("✅ Portable configuration created")
        print(f"📁 Server directory: {script_dir}")

    elif choice == "2":
        # System installation - add command to PATH
        try:
            # Create wrapper script in ~/.local/bin
            symlink_path = create_symlink_installation()

            # Generate configuration for system command
            config_files, user_config = update_config_file(
                script_dir / "mcp_config.json",
                "installable",
                None,  # No cwd needed for system command
                user_config,
            )
            print(f"✅ System installation created: {symlink_path}")
            print("🔧 Command 'kotlin-android-mcp' is now available")
        except Exception as e:
            print(f"❌ System installation failed: {e}")
            return 1

    elif choice == "3":
        # Python module installation - enable module execution
        config_files, user_config = update_config_file(
            script_dir / "mcp_config.json", "module", script_dir, user_config
        )
        print("✅ Module configuration created")
        print("🔧 Can be run with: python -m kotlin_mcp_server")

    else:
        print("❌ Invalid choice")
        return 1

    print("\n📄 Configuration files created:")
    for config_file in config_files:
        print(f"   📝 {config_file.name}")

    print("\n🎉 Setup complete!")

    # Display configuration summary
    print("\n📋 Configuration Summary:")
    print(f"   🏷️  Server name: {user_config.get('server_name', 'kotlin-android')}")
    if user_config.get("default_project_path"):
        print(f"   � Project path: {user_config['default_project_path']}")
    else:
        print(
            f"   📁 Project path: {'Dynamic (environment variables)' if user_config.get('use_env_vars') else 'Manual configuration required'}"
        )

    # Step 8: Provide integration instructions based on configuration
    print("\n📋 Integration Instructions:")

    if user_config.get("default_project_path"):
        print("\n🔹 Fixed Project Path Configuration:")
        print(f"   Your server is configured to work with: {user_config['default_project_path']}")
        print("   All configuration files use this path directly.")
    elif user_config.get("use_env_vars"):
        print("\n🔹 Dynamic Project Path Configuration:")
        print("   Your server uses environment variables for project paths.")
    else:
        print("\n🔹 Manual Configuration Required:")
        print("   Update PROJECT_PATH in configuration files to your project path.")

    # Platform-specific integration instructions
    print("\n🔹 Claude Desktop:")
    print("   Copy content from 'mcp_config_claude.json' to:")
    print("   ~/Library/Application Support/Claude/claude_desktop_config.json")

    print("\n🔹 VS Code:")
    print("   Use 'mcp_config_vscode.json' for VS Code extensions")

    print("\n🔹 Other MCP Clients:")
    print("   Use 'mcp_config.json' for generic MCP client integration")

    # Step 9: Provide testing instructions based on installation type
    print("\n🧪 Test the server:")
    if choice == "2":
        # System installation testing
        if user_config.get("default_project_path"):
            print("   kotlin-android-mcp")
        else:
            print("   kotlin-android-mcp /path/to/android/project")
    else:
        # Portable or module installation testing
        print(f"   cd {script_dir}")
        if user_config.get("default_project_path"):
            print("   python3 kotlin_mcp_server.py")
        else:
            print("   python3 kotlin_mcp_server.py /path/to/android/project")

    # Step 10: Display additional tips based on configuration choices
    if user_config.get("use_env_vars") and not user_config.get("default_project_path"):
        print("\n⚠️  Environment Variables:")
        print("   - ${workspaceFolder}: Standard VS Code variable (automatically resolved)")
        print("   - ${workspaceRoot}: Claude Desktop variable (may need manual setup)")
        print("   - ${WORKSPACE_ROOT}: Generic variable (set manually or via shell)")
        print("\n💡 Pro Tip:")
        print("   The server uses workspace/project context automatically!")
        print("   Environment variables will be resolved by your MCP client.")
    elif user_config.get("default_project_path"):
        print("\n💡 Pro Tip:")
        print(f"   Your server is pre-configured for: {user_config['default_project_path']}")
        print("   No additional configuration needed!")
    else:
        print("\n⚠️  Manual Configuration:")
        print("   Remember to update PROJECT_PATH in your configuration files")
        print("   to point to your actual Android project directory.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
