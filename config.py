"""Configuration management using environment variables with sane defaults."""

import os
from typing import Any, Dict, List, Optional


class Config:
    """Configuration manager for MCP server."""

    # Default values
    DEFAULTS = {
        "MCP_MAX_RETRIES": 5,
        "MCP_API_TIMEOUT_MS": 3000,
        "MCP_RATE_LIMIT_QPS": 10,
        "MCP_AUDIT_DB_PATH": "./audit.db",
        "MCP_SIDECAR_CMD": ["java", "-jar", "kotlin-sidecar/build/libs/kotlin-sidecar.jar"],
        "MCP_LOG_LEVEL": "INFO",
        "MCP_ENABLE_TELEMETRY": False,
        "MCP_CACHE_SIZE_MB": 100,
        "MCP_CIRCUIT_BREAKER_THRESHOLD": 5,
        "MCP_CIRCUIT_BREAKER_TIMEOUT_MS": 60000,
        # Hardening configuration
        "RATE_LIMIT_REQUESTS": 100,
        "RATE_LIMIT_WINDOW": 60,
        "RATE_LIMIT_BURST": 200,
        "CIRCUIT_BREAKER_THRESHOLD": 5,
        "CIRCUIT_BREAKER_TIMEOUT": 60.0,
        "CACHE_DEFAULT_TTL": 300.0,
        "TELEMETRY_ENDPOINT": "",
        "SECURITY_AUDIT_LOG_PATH": "./mcp_security.log",
        "SECURITY_ENCRYPTION_KEY": "default-key-change-in-production",
    }

    @staticmethod
    def get_str(key: str, default: Optional[str] = None) -> str:
        """Get string value from environment or default."""
        value = os.getenv(key)
        if value is not None:
            return value
        if default is not None:
            return default
        default_val = Config.DEFAULTS.get(key, "")
        return str(default_val) if default_val is not None else ""

    @staticmethod
    def get_int(key: str, default: Optional[int] = None) -> int:
        """Get integer value from environment or default."""
        value = os.getenv(key)
        if value is not None:
            try:
                return int(value)
            except ValueError:
                pass
        if default is not None:
            return default
        default_val = Config.DEFAULTS.get(key, 0)
        return int(default_val) if isinstance(default_val, (int, str)) else 0

    @staticmethod
    def get_bool(key: str, default: Optional[bool] = None) -> bool:
        """Get boolean value from environment or default."""
        value = os.getenv(key)
        if value is not None:
            return value.lower() in ("true", "1", "yes", "on")
        if default is not None:
            return default
        return bool(Config.DEFAULTS.get(key, False))

    @staticmethod
    def get_list(key: str, default: Optional[List[str]] = None, separator: str = ",") -> List[str]:
        """Get list value from environment or default."""
        value = os.getenv(key)
        if value is not None:
            return [item.strip() for item in value.split(separator)]
        if default is not None:
            return default
        default_value = Config.DEFAULTS.get(key, [])
        return default_value if isinstance(default_value, list) else []

    @staticmethod
    def get_duration(key: str, default: Optional[int] = None) -> int:
        """Get duration in milliseconds from environment or default."""
        value = os.getenv(key)
        if value is not None:
            # Support formats like 5s, 3000ms, 3m
            if value.endswith("ms"):
                return int(value[:-2])
            elif value.endswith("s"):
                return int(value[:-1]) * 1000
            elif value.endswith("m"):
                return int(value[:-1]) * 60000
            else:
                try:
                    return int(value)
                except ValueError:
                    pass
        if default is not None:
            return default
        default_val = Config.DEFAULTS.get(key, 0)
        return int(default_val) if isinstance(default_val, (int, str)) else 0

    @classmethod
    def get_sidecar_cmd(cls) -> List[str]:
        """Get sidecar command as list."""
        cmd_str = cls.get_str("MCP_SIDECAR_CMD")
        if cmd_str:
            # If it's a single string, split by space
            return cmd_str.split()
        default_val = cls.DEFAULTS.get("MCP_SIDECAR_CMD", [])
        return list(default_val) if isinstance(default_val, list) else []

    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all configuration values."""
        config: Dict[str, Any] = {}
        for key in cls.DEFAULTS.keys():
            if (
                key.endswith("_MS")
                or key.endswith("_TIMEOUT")
                or key in ["RATE_LIMIT_WINDOW", "CIRCUIT_BREAKER_THRESHOLD"]
            ):
                config[key] = cls.get_duration(key) if key.endswith("_MS") else cls.get_int(key)
            elif key in [
                "MCP_MAX_RETRIES",
                "MCP_RATE_LIMIT_QPS",
                "MCP_CACHE_SIZE_MB",
                "RATE_LIMIT_REQUESTS",
                "RATE_LIMIT_BURST",
            ]:
                config[key] = cls.get_int(key)
            elif key in ["MCP_ENABLE_TELEMETRY"]:
                config[key] = cls.get_bool(key)
            elif key == "MCP_SIDECAR_CMD":
                config[key] = cls.get_sidecar_cmd()
            elif key in ["CACHE_DEFAULT_TTL", "CIRCUIT_BREAKER_TIMEOUT"]:
                config[key] = cls.get_float(key)
            else:
                config[key] = cls.get_str(key)
        return config

    @staticmethod
    def get_float(key: str, default: Optional[float] = None) -> float:
        """Get float value from environment or default."""
        value = os.getenv(key)
        if value is not None:
            try:
                return float(value)
            except ValueError:
                pass
        if default is not None:
            return default
        default_val = Config.DEFAULTS.get(key, 0.0)
        return float(default_val) if isinstance(default_val, (int, float, str)) else 0.0


# Convenience constants
MCP_MAX_RETRIES = Config.get_int("MCP_MAX_RETRIES")
MCP_API_TIMEOUT_MS = Config.get_duration("MCP_API_TIMEOUT_MS")
MCP_RATE_LIMIT_QPS = Config.get_int("MCP_RATE_LIMIT_QPS")
MCP_AUDIT_DB_PATH = Config.get_str("MCP_AUDIT_DB_PATH")
MCP_SIDECAR_CMD = Config.get_sidecar_cmd()
MCP_LOG_LEVEL = Config.get_str("MCP_LOG_LEVEL")
MCP_ENABLE_TELEMETRY = Config.get_bool("MCP_ENABLE_TELEMETRY")
MCP_CACHE_SIZE_MB = Config.get_int("MCP_CACHE_SIZE_MB")
MCP_CIRCUIT_BREAKER_THRESHOLD = Config.get_int("MCP_CIRCUIT_BREAKER_THRESHOLD")
MCP_CIRCUIT_BREAKER_TIMEOUT_MS = Config.get_duration("MCP_CIRCUIT_BREAKER_TIMEOUT_MS")
