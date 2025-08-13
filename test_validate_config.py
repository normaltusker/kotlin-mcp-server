import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
from pathlib import Path
import sys
import socket
import subprocess
import time
import requests
import builtins
import importlib # Import importlib
import io # Import io

original_import = builtins.__import__

# Add the parent directory to the sys.path to allow imports from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import validate_config here, but we will reload it later
import validate_config

class TestValidateConfig(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = Path("test_temp_dir")
        self.test_dir.mkdir(exist_ok=True)
        (self.test_dir / "test_file.txt").touch()

    def tearDown(self):
        # Clean up the temporary directory
        (self.test_dir / "test_file.txt").unlink()
        self.test_dir.rmdir()

    @patch('validate_config.Path')
    def test_validate_path_valid(self, mock_path_class):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        valid, message = validate_config.validate_path(str(self.test_dir), "Test Directory")
        self.assertTrue(valid)
        self.assertIn("✅", message)

    @patch('validate_config.Path')
    def test_validate_path_invalid_placeholder(self, mock_path_class):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = False
        valid, message = validate_config.validate_path("${PLACEHOLDER}", "Test Placeholder")
        self.assertFalse(valid)
        self.assertIn("❌", message)
        self.assertIn("placeholder", message)

    @patch('validate_config.Path')
    def test_validate_path_not_exists(self, mock_path_class):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = False
        valid, message = validate_config.validate_path("non_existent_dir", "Non Existent Directory")
        self.assertFalse(valid)
        self.assertIn("❌", message)
        self.assertIn("does not exist", message)

    @patch('validate_config.Path')
    def test_validate_path_hardcoded_your(self, mock_path_class):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        valid, message = validate_config.validate_path("/path/to/your-project", "Hardcoded Your Path")
        self.assertFalse(valid)
        self.assertIn("❌ Hardcoded Your Path: Contains placeholder", message)

    @patch('pathlib.Path.exists', return_value=False)
    def test_validate_config_file_not_found(self, mock_exists):
        config_path = Path("non_existent_config.json")
        valid, message = validate_config.validate_config_file(config_path)
        self.assertFalse(valid)
        self.assertIn("❌ Config file not found", message)

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', side_effect=json.JSONDecodeError("Expecting value", "doc", 0))
    def test_validate_config_file_invalid_json(self, mock_open, mock_exists):
        config_path = Path("invalid_config.json")
        valid, message = validate_config.validate_config_file(config_path)
        self.assertFalse(valid)
        self.assertIn("❌ Invalid JSON", message)

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open(read_data='{"someOtherKey": "value"}'))
    def test_validate_config_file_missing_mcp_servers(self, mock_exists):
        config_path = Path("config_missing_mcp.json")
        valid, message = validate_config.validate_config_file(config_path)
        self.assertFalse(valid)
        self.assertIn("❌ Missing 'mcpServers' section", message)

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open(read_data='{"mcpServers": {"server1": {"cwd": "${PLACEHOLDER}", "command": "cmd", "args": ["arg"]}}}'))
    def test_validate_config_file_cwd_placeholder(self, mock_exists):
        config_path = Path("config_cwd_placeholder.json")
        valid, message = validate_config.validate_config_file(config_path)
        self.assertFalse(valid)
        self.assertIn("❌ server1: 'cwd' contains placeholder or hardcoded path", message) # Updated assertion

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open(read_data='{"mcpServers": {"server1": {"cwd": "/Users/Niravthakker/project", "command": "cmd", "args": ["arg"]}}}'))
    def test_validate_config_file_cwd_hardcoded_user(self, mock_exists):
        config_path = Path("config_cwd_hardcoded_user.json")
        valid, message = validate_config.validate_config_file(config_path)
        self.assertFalse(valid)
        self.assertIn("❌ server1: 'cwd' contains placeholder or hardcoded path", message)

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open(read_data='{"mcpServers": {"server1": {"cwd": "/path", "args": ["arg"]}}}'))
    def test_validate_config_file_missing_command(self, mock_exists):
        config_path = Path("config_missing_command.json")
        valid, message = validate_config.validate_config_file(config_path)
        self.assertFalse(valid)
        self.assertIn("❌ server1: Missing 'command'", message)

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open(read_data='{"mcpServers": {"server1": {"cwd": "/path", "command": "cmd"}}}'))
    def test_validate_config_file_missing_args(self, mock_exists):
        config_path = Path("config_missing_args.json")
        valid, message = validate_config.validate_config_file(config_path)
        self.assertFalse(valid)
        self.assertIn("❌ server1: Missing 'args'", message)

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open(read_data='{"mcpServers": {"server1": {"cwd": "/path", "command": "cmd", "args": ["arg"]}}}'))
    def test_validate_config_file_valid(self, mock_exists):
        config_path = Path("valid_config.json")
        valid, message = validate_config.validate_config_file(config_path)
        self.assertTrue(valid)
        self.assertIn("✅ Config file valid", message)

    @patch('os.getenv')
    @patch('validate_config.Path')
    @patch('builtins.print')
    def test_validate_environment_missing_required(self, mock_print, mock_path_class, mock_getenv):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        mock_getenv.side_effect = lambda x: None if x == "WORKSPACE_PATH" else "/some/path"
        valid, issues = validate_config.validate_environment()
        self.assertFalse(valid)
        self.assertIn("❌ Missing required environment variable: WORKSPACE_PATH", issues)

    @patch('os.getenv')
    @patch('validate_config.Path')
    @patch('builtins.print')
    def test_validate_environment_required_placeholder(self, mock_print, mock_path_class, mock_getenv):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        mock_getenv.side_effect = lambda x: "${PLACEHOLDER}" if x == "WORKSPACE_PATH" else "/some/path"
        valid, issues = validate_config.validate_environment()
        self.assertFalse(valid)
        self.assertIn("❌ {var_name} contains placeholder - update with actual value".format(var_name="WORKSPACE_PATH"), issues) # Updated assertion

    @patch('os.getenv')
    @patch('validate_config.Path')
    @patch('builtins.print')
    def test_validate_environment_required_path_not_exists(self, mock_print, mock_path_class, mock_getenv):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = False
        mock_getenv.side_effect = lambda x: "/non/existent/path" if x == "WORKSPACE_PATH" else "/some/path"
        valid, issues = validate_config.validate_environment()
        self.assertFalse(valid)
        self.assertIn("❌ WORKSPACE_PATH (Android project workspace path): Path does not exist: /non/existent/path", issues)

    @patch('os.getenv')
    @patch('validate_config.Path')
    @patch('builtins.print')
    def test_validate_environment_required_path_valid(self, mock_print, mock_path_class, mock_getenv):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        mock_getenv.side_effect = {
            "WORKSPACE_PATH": "/valid/workspace",
            "MCP_SERVER_DIR": "/valid/server/dir",
            "MCP_ENCRYPTION_PASSWORD": None, # Optional, not configured
            "OPENAI_API_KEY": "your-openai-key", # Optional, placeholder
            "ANTHROPIC_API_KEY": "configured-key" # Optional, configured
        }.get
        valid, issues = validate_config.validate_environment()
        self.assertTrue(valid)
        self.assertEqual(len(issues), 0)
        mock_print.assert_any_call("✅ WORKSPACE_PATH (Android project workspace path): /valid/workspace")
        mock_print.assert_any_call("✅ MCP_SERVER_DIR (MCP server directory path): /valid/server/dir")
        mock_print.assert_any_call("ℹ️  MCP_ENCRYPTION_PASSWORD: Not configured (optional)")
        mock_print.assert_any_call("⚠️  OPENAI_API_KEY: Contains placeholder - update if you want to use OpenAI API key")
        mock_print.assert_any_call("✅ ANTHROPIC_API_KEY: Configured")

    @patch('builtins.print')
    @patch('sys.modules')
    def test_check_python_dependencies_all_installed(self, mock_sys_modules, mock_print):
        # Simulate all packages being installed
        mock_sys_modules.__contains__.side_effect = lambda key: key in ["pydantic", "python_dotenv", "cryptography", "aiosqlite", "aiohttp"]
        mock_sys_modules.__getitem__.side_effect = lambda key: MagicMock() # Return a mock module object

        result = validate_config.check_python_dependencies()
        self.assertTrue(result)
        mock_print.assert_any_call("✅ pydantic: Installed")
        mock_print.assert_any_call("✅ python-dotenv: Installed")
        mock_print.assert_any_call("✅ cryptography: Installed")
        mock_print.assert_any_call("✅ aiosqlite: Installed")
        mock_print.assert_any_call("✅ aiohttp: Installed")

    @patch('builtins.print')
    @patch('sys.modules')
    def test_check_python_dependencies_some_missing(self, mock_sys_modules, mock_print):
        # Simulate 'pydantic' and 'cryptography' missing
        mock_sys_modules.__contains__.side_effect = lambda key: key not in ["pydantic", "cryptography"]
        mock_sys_modules.__getitem__.side_effect = lambda key: MagicMock() # Return a mock module object

        result = validate_config.check_python_dependencies()
        self.assertFalse(result)
        mock_print.assert_any_call("❌ pydantic: Missing")
        mock_print.assert_any_call("✅ python-dotenv: Installed")
        mock_print.assert_any_call("❌ cryptography: Missing")
        mock_print.assert_any_call("   pip install pydantic cryptography")

    @patch('builtins.print')
    @patch('requests.get')
    @patch('time.sleep')
    @patch('subprocess.Popen')
    @patch('os.getenv', side_effect=lambda x, y=None: "8080" if x == "MCP_BRIDGE_PORT" else "localhost")
    @patch('socket.socket')
    @patch('validate_config.Path') # Patch validate_config.Path directly
    def test_bridge_server_file_not_found(self, mock_validate_config_path, mock_socket, mock_getenv, mock_popen, mock_sleep, mock_requests_get, mock_print):
        # Configure the mock validate_config.Path to return a mock object when instantiated
        mock_script_dir = MagicMock()
        mock_bridge_file = MagicMock()

        mock_validate_config_path.return_value = mock_script_dir
        mock_script_dir.parent = mock_script_dir # For Path(__file__).parent

        # Configure the mock for script_dir / "vscode_bridge.py"
        mock_script_dir.__truediv__.return_value = mock_bridge_file
        mock_bridge_file.exists.return_value = False

        result = validate_config.test_bridge_server()
        self.assertFalse(result)
        mock_print.assert_any_call("   ❌ vscode_bridge.py: Not found")

    @patch('builtins.print')
    @patch('requests.get')
    @patch('os.getenv', side_effect=lambda x, y=None: "8080" if x == "MCP_BRIDGE_PORT" else "localhost")
    @patch('socket.socket')
    @patch('validate_config.Path')
    def test_bridge_server_port_in_use_healthy(self, mock_path_class, mock_socket, mock_getenv, mock_requests_get, mock_print):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        # Mock socket to simulate port in use
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 0  # Port in use

        # Mock requests.get for healthy response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_requests_get.return_value = mock_response

        result = validate_config.test_bridge_server()
        self.assertTrue(result)
        mock_print.assert_any_call("   ✅ Bridge server: Running and healthy")

    @patch('builtins.print')
    @patch('requests.get')
    @patch('os.getenv', side_effect=lambda x, y=None: "8080" if x == "MCP_BRIDGE_PORT" else "localhost")
    @patch('socket.socket')
    @patch('validate_config.Path')
    def test_bridge_server_port_in_use_unhealthy(self, mock_path_class, mock_socket, mock_getenv, mock_requests_get, mock_print):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        # Mock socket to simulate port in use
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 0  # Port in use

        # Mock requests.get for unhealthy response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "unhealthy"}
        mock_requests_get.return_value = mock_response

        result = validate_config.test_bridge_server()
        self.assertFalse(result)
        mock_print.assert_any_call("   ❌ Bridge server: Unhealthy response")

    @patch('builtins.print')
    @patch('requests.get', side_effect=requests.exceptions.ConnectionError("Connection refused"))
    @patch('time.sleep')
    @patch('subprocess.Popen')
    @patch('os.getenv', side_effect=lambda x, y=None: "8080" if x == "MCP_BRIDGE_PORT" else "localhost")
    @patch('socket.socket')
    @patch('validate_config.Path')
    def test_bridge_server_starts_health_check_fails(self, mock_path_class, mock_socket, mock_getenv, mock_popen, mock_sleep, mock_requests_get, mock_print):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        # Mock socket to simulate port not in use
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 1  # Port not in use

        # Mock subprocess.Popen to simulate process running
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process still running
        mock_popen.return_value = mock_process

        result = validate_config.test_bridge_server()
        self.assertFalse(result)
        mock_print.assert_any_call("   ❌ Bridge server: Health check failed - Connection refused")

    @patch('builtins.print')
    @patch('requests.get')
    @patch('time.sleep')
    @patch('subprocess.Popen')
    @patch('os.getenv', side_effect=lambda x, y=None: "8080" if x == "MCP_BRIDGE_PORT" else "localhost")
    @patch('socket.socket')
    @patch('validate_config.Path')
    def test_bridge_server_starts_successfully(self, mock_path_class, mock_socket, mock_getenv, mock_popen, mock_sleep, mock_requests_get, mock_print):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        # Mock socket to simulate port not in use
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 1  # Port not in use

        # Mock subprocess.Popen to simulate process running
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process still running
        mock_popen.return_value = mock_process

        # Mock requests.get for healthy response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_requests_get.return_value = mock_response

        result = validate_config.test_bridge_server()
        self.assertTrue(result)
        mock_print.assert_any_call("   🔄 Starting bridge server for testing...")
        mock_print.assert_any_call("   ✅ Bridge server: Successfully started and healthy")
        mock_process.terminate.assert_called_once()

    @patch('builtins.print')
    @patch('requests.get')
    @patch('time.sleep')
    @patch('subprocess.Popen')
    @patch('os.getenv', side_effect=lambda x, y=None: "8080" if x == "MCP_BRIDGE_PORT" else "localhost")
    @patch('socket.socket')
    @patch('validate_config.Path')
    def test_bridge_server_fails_to_start(self, mock_path_class, mock_socket, mock_getenv, mock_popen, mock_sleep, mock_requests_get, mock_print):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        # Mock socket to simulate port not in use
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 1  # Port not in use

        # Mock subprocess.Popen to simulate process failing to start
        mock_process = MagicMock()
        mock_process.poll.return_value = 1  # Process exited immediately
        mock_process.communicate.return_value = (b"stdout output", b"stderr output")
        mock_popen.return_value = mock_process

        result = validate_config.test_bridge_server()
        self.assertFalse(result)
        mock_print.assert_any_call("   ❌ Bridge server failed to start:")
        mock_print.assert_any_call("      stdout: stdout output...")
        mock_print.assert_any_call("      stderr: stderr output...")

    @patch('builtins.print')
    @patch('builtins.__import__')
    def test_bridge_server_requests_not_available(self, mock_import, mock_print):
        def custom_import_side_effect(name, globals=None, locals=None, fromlist=(), level=0):
            if name == 'requests':
                raise ImportError
            # Call the original __import__ for other modules
            return original_import(name, globals, locals, fromlist, level)

        mock_import.side_effect = custom_import_side_effect
        result = validate_config.test_bridge_server()
        self.assertTrue(result)
        mock_print.assert_any_call("   ⚠️  requests library not available - skipping bridge server test")

    @patch('os.getenv')
    @patch('pathlib.Path.exists')
    @patch('json.load')
    @patch('builtins.open')
    @patch('validate_config.check_python_dependencies')
    @patch('validate_config.validate_environment')
    @patch('validate_config.validate_config_file')
    @patch('validate_config.test_bridge_server')
    @patch('sys.modules', {})
    @patch('dotenv.load_dotenv')
    @patch('validate_config.__name__', new='not_main') # Patch __name__
    def test_main_all_validations_pass(self, mock_load_dotenv, mock_test_bridge_server, mock_validate_config_file, mock_validate_environment, mock_check_python_dependencies, mock_open, mock_json_load, mock_path_exists, mock_getenv):
        # Mock all checks to pass
        mock_check_python_dependencies.return_value = True
        mock_validate_environment.return_value = (True, [])
        mock_validate_config_file.return_value = (True, "✅ Config file valid")
        mock_test_bridge_server.return_value = True

        # Mock Path.exists for all file checks
        mock_path_exists.return_value = True

        # Mock os.getenv for environment variables
        mock_getenv.side_effect = lambda x: "/mock/path" # Return a dummy path for all env vars

        # Mock json.load for config files
        mock_json_load.return_value = {"mcpServers": {"server1": {"cwd": "/tmp", "command": "cmd", "args": ["a"]}}}

        # Mock load_dotenv
        mock_load_dotenv.return_value = True

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with patch('validate_config.sys.exit', side_effect=SystemExit) as mock_exit: # Patch sys.exit in validate_config module
                try:
                    validate_config.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 0)
                self.assertIn("🎉 Configuration Validation PASSED!", mock_stdout.getvalue())

    @patch('validate_config.check_python_dependencies', return_value=False)
    @patch('validate_config.validate_environment', return_value=(True, []))
    @patch('validate_config.validate_config_file', return_value=(True, "✅ Config file valid: mock_config.json"))
    @patch('validate_config.test_bridge_server', return_value=True)
    @patch('validate_config.Path') # Patch the Path class
    @patch('builtins.__import__') # For dotenv import
    def test_main_deps_fail(self, mock_import, mock_path_class, mock_test_bridge_server, mock_validate_config_file, mock_validate_environment, mock_check_python_dependencies):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.side_effect = lambda: True
        mock_dotenv = MagicMock()
        mock_import.return_value = mock_dotenv

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with patch('sys.exit', side_effect=SystemExit) as mock_exit:
                try:
                    validate_config.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 1)
                self.assertIn("🚨 Configuration Validation FAILED!", mock_stdout.getvalue())

    @patch('validate_config.check_python_dependencies', return_value=True)
    @patch('validate_config.validate_environment', return_value=(False, ["env issue"]))
    @patch('validate_config.validate_config_file', return_value=(True, "✅ Config file valid: mock_config.json"))
    @patch('validate_config.test_bridge_server', return_value=True)
    @patch('validate_config.Path') # Patch the Path class
    @patch('builtins.__import__') # For dotenv import
    def test_main_env_fail(self, mock_import, mock_path_class, mock_test_bridge_server, mock_validate_config_file, mock_validate_environment, mock_check_python_dependencies):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.side_effect = lambda: True
        mock_dotenv = MagicMock()
        mock_import.return_value = mock_dotenv

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with patch('sys.exit', side_effect=SystemExit) as mock_exit:
                try:
                    validate_config.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 1)
                self.assertIn("🚨 Configuration Validation FAILED!", mock_stdout.getvalue())

    @patch('validate_config.check_python_dependencies', return_value=True)
    @patch('validate_config.validate_environment', return_value=(True, []))
    @patch('validate_config.validate_config_file', return_value=(False, "❌ Config file invalid: mock_config.json"))
    @patch('validate_config.test_bridge_server', return_value=True)
    @patch('validate_config.Path') # Patch the Path class
    @patch('builtins.__import__') # For dotenv import
    def test_main_config_fail(self, mock_import, mock_path_class, mock_test_bridge_server, mock_validate_config_file, mock_validate_environment, mock_check_python_dependencies):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.side_effect = lambda: True
        mock_dotenv = MagicMock()
        mock_import.return_value = mock_dotenv

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with patch('sys.exit', side_effect=SystemExit) as mock_exit:
                try:
                    validate_config.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 1)
                self.assertIn("🚨 Configuration Validation FAILED!", mock_stdout.getvalue())

    @patch('validate_config.check_python_dependencies', return_value=True)
    @patch('validate_config.validate_environment', return_value=(True, []))
    @patch('validate_config.validate_config_file', return_value=(True, "✅ Config file valid: mock_config.json"))
    @patch('validate_config.test_bridge_server', return_value=True)
    @patch('validate_config.Path') # Patch the Path class
    @patch('builtins.__import__') # For dotenv import
    def test_main_bridge_fail(self, mock_import, mock_path_class, mock_test_bridge_server, mock_validate_config_file, mock_validate_environment, mock_check_python_dependencies):
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.side_effect = lambda: True
        mock_dotenv = MagicMock()
        mock_import.return_value = mock_dotenv

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with patch('sys.exit', side_effect=SystemExit) as mock_exit:
                try:
                    validate_config.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 1)
                self.assertIn("🚨 Configuration Validation FAILED!", mock_stdout.getvalue())

    @patch('validate_config.check_python_dependencies', return_value=True)
    @patch('validate_config.validate_environment', return_value=(True, []))
    @patch('validate_config.validate_config_file', return_value=(True, "✅ Config file valid: mock_config.json"))
    @patch('validate_config.test_bridge_server', return_value=True)
    @patch('validate_config.Path') # Patch the Path class
    @patch('builtins.__import__') # For dotenv import
    def test_main_server_file_missing(self, mock_import, mock_path_class, mock_test_bridge_server, mock_validate_config_file, mock_validate_environment, mock_check_python_dependencies):
        # Configure the mocked Path.exists() for instances
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        # Simulate kotlin_mcp_server.py missing
        mock_path_instance.exists.side_effect = lambda: False if "kotlin_mcp_server.py" in str(mock_path_instance) else True
        mock_dotenv = MagicMock()
        mock_import.return_value = mock_dotenv

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with patch('sys.exit', side_effect=SystemExit) as mock_exit:
                try:
                    validate_config.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 1)
                self.assertIn("🚨 Configuration Validation FAILED!", mock_stdout.getvalue())

    @patch('validate_config.check_python_dependencies', return_value=True)
    @patch('validate_config.validate_environment', return_value=(True, []))
    @patch('validate_config.validate_config_file', return_value=(True, "✅ Config file valid: mock_config.json"))
    @patch('validate_config.test_bridge_server', return_value=True)
    @patch('validate_config.Path') # Patch the Path class
    def test_main_no_env_file(self, mock_path_class, mock_test_bridge_server, mock_validate_config_file, mock_validate_environment, mock_check_python_dependencies):
        # Configure the mocked Path.exists() for instances
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        # Simulate no .env file
        mock_path_instance.exists.side_effect = lambda: False if ".env" in str(mock_path_instance) else True

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with patch('sys.exit', side_effect=SystemExit) as mock_exit:
                try:
                    validate_config.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 0)
                self.assertIn("⚠️  No .env file found at: test_temp_dir/validate_config.py", mock_stdout.getvalue()) # Path will be relative to test file

    @patch('validate_config.check_python_dependencies', return_value=True)
    @patch('validate_config.validate_environment', return_value=(True, []))
    @patch('validate_config.validate_config_file', return_value=(True, "✅ Config file valid: mock_config.json"))
    @patch('validate_config.test_bridge_server', return_value=True)
    @patch('validate_config.Path') # Patch the Path class
    @patch('builtins.__import__', side_effect=ImportError) # Simulate python-dotenv not installed
    def test_main_dotenv_not_installed(self, mock_import, mock_path_class, mock_test_bridge_server, mock_validate_config_file, mock_validate_environment, mock_check_python_dependencies):
        # Configure the mocked Path.exists() for instances
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        # Simulate .env file exists but python-dotenv not installed
        mock_path_instance.exists.side_effect = lambda: True # All paths exist

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with patch('sys.exit', side_effect=SystemExit) as mock_exit:
                try:
                    validate_config.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 0)
                self.assertIn("⚠️  python-dotenv not installed - environment variables may not be loaded", mock_stdout.getvalue())

    @patch('validate_config.check_python_dependencies', side_effect=Exception("Simulated error"))
    def test_main_exception_handling(self, mock_check_python_dependencies):
        with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            with patch('sys.exit', side_effect=SystemExit) as mock_exit:
                try:
                    validate_config.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 1)
                self.assertIn("An unexpected error occurred: Simulated error", mock_stderr.getvalue())

if __name__ == '__main__':
    unittest.main()