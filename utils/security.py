"""
Security and logging utilities for Kotlin MCP Server.

This module provides comprehensive security features including:
- Audit logging and security monitoring
- SQLite database for audit trails
- Path validation and sanitization
- Command argument validation
- Compliance monitoring (GDPR, HIPAA, SOC2)
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import bcrypt
from cryptography.fernet import Fernet


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Encrypts data using Fernet symmetric encryption."""
    f = Fernet(key)
    return f.encrypt(data)


def decrypt_data(token: bytes, key: bytes) -> bytes:
    """Decrypts data using Fernet symmetric encryption."""
    f = Fernet(key)
    return f.decrypt(token)


def hash_password(password: str) -> bytes:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def check_password(password: str, hashed: bytes) -> bool:
    """Checks a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


class SecurityManager:
    """Manages security logging and audit database for the MCP server."""

    def __init__(self) -> None:
        """Initialize security manager with logging and audit database."""
        self.security_logger: Optional[logging.Logger] = None
        self.audit_db: Optional[sqlite3.Connection] = None
        self._setup_security_logging()
        self._setup_audit_database()

    def _setup_security_logging(self) -> None:
        """
        Configure comprehensive security and audit logging system.

        Sets up dedicated loggers for:
        - Security events (authentication, authorization)
        - Audit trails (tool usage, data access)
        - Error tracking (security violations, failures)
        - Compliance monitoring (GDPR, HIPAA requirements)
        """
        try:
            # Create dedicated security logger with INFO level for audit trails
            security_logger = logging.getLogger("mcp_security")
            security_logger.setLevel(logging.INFO)

            # Configure file handler for persistent audit logs
            log_file = "mcp_security.log"
            handler = logging.FileHandler(log_file)

            # Use detailed format including timestamps for audit requirements
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            security_logger.addHandler(handler)

            self.security_logger = security_logger

        except (FileNotFoundError, PermissionError, OSError) as e:
            # Graceful degradation: continue without security logging if setup fails
            print(f"Warning: Could not setup security logging: {e}", file=sys.stderr)
            self.security_logger = None

    def _setup_audit_database(self) -> None:
        """
        Initialize SQLite database for comprehensive audit trails and compliance monitoring.

        Creates tables for:
        - audit_log: General activity tracking (tool calls, actions, results)
        - data_access_log: Data access patterns for compliance (GDPR, HIPAA)

        The database supports:
        - User activity tracking
        - Data retention policy enforcement
        - Compliance reporting
        - Security incident investigation
        """
        try:
            # Create persistent SQLite database with thread safety disabled
            # (MCP server runs single-threaded async, so this is safe)
            audit_db_path = os.getenv("MCP_AUDIT_DB_PATH", "mcp_audit.db")
            self.audit_db = sqlite3.connect(audit_db_path, check_same_thread=False)

            # Create main audit log table for general activity tracking
            self.audit_db.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,           -- ISO format timestamp
                    user_id TEXT,                      -- User identifier (if available)
                    action TEXT NOT NULL,              -- Action performed (tool_call, etc.)
                    resource TEXT,                     -- Resource accessed or modified
                    details TEXT,                      -- JSON details of the operation
                    ip_address TEXT,                   -- Client IP for security tracking
                    result TEXT                        -- Success/failure/error details
                )
            """
            )

            # Create data access log for compliance monitoring (GDPR, HIPAA)
            self.audit_db.execute(
                """
                CREATE TABLE IF NOT EXISTS data_access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,           -- When data was accessed
                    data_type TEXT NOT NULL,           -- Type of data (personal, medical, etc.)
                    access_type TEXT NOT NULL,         -- Read, write, delete, export
                    user_id TEXT,                      -- Who accessed the data
                    retention_date TEXT,               -- When data should be deleted
                    compliance_flags TEXT              -- JSON flags for compliance requirements
                )
            """
            )

            # Commit table creation to ensure schema is persisted
            self.audit_db.commit()

        except (OSError, PermissionError, RuntimeError) as e:
            # Graceful degradation: continue without audit database if setup fails
            print(f"Warning: Could not setup audit database: {e}", file=sys.stderr)
            self.audit_db = None

    def log_audit_event(
        self,
        action: str,
        resource: Optional[str] = None,
        details: Optional[str] = None,
        user_id: str = "system",
    ) -> None:
        """
        Log audit events for security monitoring and compliance reporting.

        This method creates audit trails required for:
        - Security incident investigation
        - Compliance reporting (GDPR, HIPAA, SOC2)
        - User activity monitoring
        - Data access tracking

        Args:
            action (str): Action performed (e.g., 'tool_call', 'data_access', 'file_read')
            resource (str, optional): Resource accessed or modified
            details (str, optional): Additional details about the operation
            user_id (str): User identifier (defaults to 'system' for server actions)
        """
        if self.audit_db and self.security_logger:
            try:
                # Use UTC timestamp for consistent audit trails across timezones
                timestamp = datetime.now(timezone.utc).isoformat()

                # Insert audit record with all available information
                self.audit_db.execute(
                    """
                    INSERT INTO audit_log (timestamp, user_id, action, resource, details, ip_address, result)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        timestamp,
                        user_id,
                        action,
                        resource,
                        details,
                        os.getenv("MCP_CLIENT_HOST", "localhost"),
                        "success",
                    ),
                )

                # Immediately commit to ensure audit record persistence
                self.audit_db.commit()

                # Also log to security log file for immediate monitoring
                if self.security_logger:
                    self.security_logger.info(
                        "AUDIT: %s - User: %s - Resource: %s", action, user_id, resource
                    )

            except (PermissionError, OSError) as e:
                # Even audit logging failure should not break server operation
                print(f"Warning: Could not log audit event: {e}", file=sys.stderr)

    def validate_file_path(self, file_path: str, base_path: Path) -> Path:
        """
        Validate and sanitize file paths to prevent path traversal attacks.

        Args:
            file_path (str): User-provided file path
            base_path (Path): Base directory to restrict access to

        Returns:
            Path: Validated and resolved path

        Raises:
            ValueError: If path contains dangerous patterns or escapes base directory
        """
        # Normalize path and resolve any symbolic links
        try:
            # Convert to Path object and resolve
            path = Path(file_path)

            # Check for dangerous path components
            for part in path.parts:
                if part in ["..", ".", ""]:
                    continue
                if part.startswith(".") and len(part) > 1:
                    # Allow hidden files but log access
                    self.log_audit_event("file_access", f"hidden_file:{part}")

            # Resolve relative to base path
            if path.is_absolute():
                resolved_path = path.resolve()
            else:
                resolved_path = (base_path / path).resolve()

            # Ensure the resolved path is within the base directory
            try:
                resolved_path.relative_to(base_path.resolve())
            except ValueError as exc:
                raise ValueError(
                    f"Path traversal detected: {file_path} escapes base directory"
                ) from exc

            return resolved_path

        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid file path: {file_path} - {str(e)}") from e

    def validate_command_args(self, command_args: list) -> list:
        """
        Validate and sanitize command arguments to prevent injection attacks.

        Args:
            command_args (list): List of command arguments

        Returns:
            list: Sanitized command arguments

        Raises:
            ValueError: If dangerous command patterns are detected
        """
        if not isinstance(command_args, list):
            raise ValueError("Command arguments must be a list")

        # Dangerous patterns to check for
        dangerous_patterns = [
            ";",
            "&",
            "|",
            "`",
            "$",
            "$(",
            "&&",
            "||",
            ">>",
            ">",
            "<",
            "rm",
            "del",
            "format",
            "fdisk",
            "mkfs",
        ]

        sanitized_args = []
        for arg in command_args:
            if not isinstance(arg, str):
                arg = str(arg)

            # Check for dangerous patterns
            for pattern in dangerous_patterns:
                if pattern in arg.lower():
                    self.log_audit_event("security_violation", f"dangerous_command_arg:{arg}")
                    raise ValueError(f"Potentially dangerous command argument: {arg}")

            sanitized_args.append(arg)

        return sanitized_args

    def close(self) -> None:
        """Close database connections and cleanup resources."""
        if self.audit_db:
            self.audit_db.close()
