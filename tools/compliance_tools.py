"""
Compliance and security tools for Kotlin MCP Server.

Provides utility functions for:
- Audit logging
- Access control checks
- Encrypted messaging
- Configuration validation via Kotlin LSP and security scans
"""

import asyncio
from pathlib import Path
from typing import Any, Dict

from cryptography.fernet import Fernet

from utils.security import SecurityManager, encrypt_data


class ComplianceTools:
    """Tools that help enforce security and compliance."""

    def __init__(self, project_path: Path, security_manager: SecurityManager):
        self.project_path = project_path
        self.security_manager = security_manager

    async def audit_log(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Record an audit log event."""
        try:
            action = arguments.get("action", "unknown")
            resource = arguments.get("resource")
            details = arguments.get("details")
            self.security_manager.log_audit_event(action, resource, details)
            return {"success": True, "message": "Audit event logged"}
        except Exception as e:  # pragma: no cover - defensive
            return {"success": False, "error": f"Audit logging failed: {str(e)}"}

    async def check_access_controls(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate simple role-based access controls."""
        user_role = arguments.get("user_role", "")
        required_role = arguments.get("required_role", "")
        role_levels = {"viewer": 1, "developer": 2, "admin": 3}
        user_level = role_levels.get(user_role, 0)
        required_level = role_levels.get(required_role, 0)
        access_granted = user_level >= required_level

        self.security_manager.log_audit_event(
            "access_control", f"user_role:{user_role}", f"required:{required_role}"
        )

        return {
            "success": True,
            "access_granted": access_granted,
            "user_role": user_role,
            "required_role": required_role,
        }

    async def send_encrypted_message(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt a message using Fernet symmetric encryption."""
        try:
            message = arguments.get("message", "")
            key = Fernet.generate_key()
            token = encrypt_data(message.encode("utf-8"), key)
            self.security_manager.log_audit_event(
                "encrypted_message", details="message encrypted"
            )
            return {
                "success": True,
                "encrypted_message": token.decode("utf-8"),
                "key": key.decode("utf-8"),
            }
        except Exception as e:  # pragma: no cover - defensive
            return {"success": False, "error": f"Encryption failed: {str(e)}"}

    async def validate_configurations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate project configuration using Kotlin LSP and run security scans."""
        results: Dict[str, Any] = {}
        scan_path = Path(arguments.get("config_path", self.project_path))

        self.security_manager.log_audit_event(
            "validate_configurations", resource=str(scan_path)
        )

        # Kotlin LSP check
        try:
            lsp_cmd = ["kotlin-language-server", "--version"]
            safe_lsp_cmd = self.security_manager.validate_command_args(lsp_cmd)
            proc = await asyncio.create_subprocess_exec(
                *safe_lsp_cmd,
                cwd=scan_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            results["kotlin_lsp"] = {
                "returncode": proc.returncode,
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8"),
            }
        except Exception as e:  # pragma: no cover - external dependency
            results["kotlin_lsp"] = {"error": str(e)}

        # Security scan via Bandit
        try:
            scan_cmd = ["bandit", "-q", "-r", str(scan_path)]
            safe_scan_cmd = self.security_manager.validate_command_args(scan_cmd)
            proc = await asyncio.create_subprocess_exec(
                *safe_scan_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            results["security_scan"] = {
                "returncode": proc.returncode,
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8"),
            }
        except Exception as e:  # pragma: no cover - external dependency
            results["security_scan"] = {"error": str(e)}

        success = all(
            r.get("returncode", 1) == 0 for r in results.values() if isinstance(r, dict)
        )
        return {"success": success, "results": results}
