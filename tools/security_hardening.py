#!/usr/bin/env python3
"""
Security hardening tools for MCP server.

This module provides comprehensive security hardening including:
- Role-Based Access Control (RBAC)
- Rate limiting with sliding window
- Circuit breaker pattern for resilience
- Caching layer with TTL
- Observability with metrics and telemetry
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union
from urllib.parse import urlparse

import aiohttp
from aiohttp import web

from config import Config
from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class UserRole(Enum):
    """User roles for RBAC system."""

    ADMIN = "admin"
    DEVELOPER = "developer"
    READONLY = "readonly"
    GUEST = "guest"


class Permission(Enum):
    """Permissions for tool access."""

    # File operations
    FILE_READ = "file:read"
    FILE_WRITE = "file:write"
    FILE_DELETE = "file:delete"

    # Git operations
    GIT_READ = "git:read"
    GIT_WRITE = "git:write"

    # API operations
    API_READ = "api:read"
    API_WRITE = "api:write"

    # Build operations
    BUILD_EXECUTE = "build:execute"

    # Security operations
    SECURITY_ENCRYPT = "security:encrypt"
    SECURITY_DECRYPT = "security:decrypt"

    # Admin operations
    ADMIN_CONFIG = "admin:config"
    ADMIN_AUDIT = "admin:audit"


@dataclass
class RBACPolicy:
    """RBAC policy definition."""

    role: UserRole
    permissions: Set[Permission] = field(default_factory=set)
    resource_patterns: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    requests_per_window: int
    window_seconds: int
    burst_limit: Optional[int] = None


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int
    recovery_timeout: float
    expected_exception: Tuple[Type[Exception], ...] = (Exception,)


@dataclass
class CacheEntry:
    """Cache entry with TTL."""

    data: Any
    timestamp: float
    ttl: float

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() - self.timestamp > self.ttl


class MetricsCollector:
    """Collect and export metrics."""

    def __init__(self) -> None:
        self.counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.histograms: Dict[str, Dict[str, List[Tuple[float, float]]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.start_time = time.time()

    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        key = json.dumps(labels or {}, sort_keys=True)
        self.counters[name][key] += 1

    def record_histogram(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a histogram value."""
        key = json.dumps(labels or {}, sort_keys=True)
        self.histograms[name][key].append((time.time(), value))

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {"counters": dict(self.counters), "histograms": dict(self.histograms)}


class TelemetryExporter:
    """Export telemetry data."""

    def __init__(self, endpoint: Optional[str] = None) -> None:
        self.endpoint = endpoint or Config.get_str("TELEMETRY_ENDPOINT", "")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "TelemetryExporter":
        if self.endpoint:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.session:
            await self.session.close()

    async def export(self, metrics: Dict[str, Any]) -> None:
        """Export metrics to telemetry endpoint."""
        if not self.session or not self.endpoint:
            return

        try:
            await self.session.post(
                self.endpoint,
                json={
                    "timestamp": datetime.now().isoformat(),
                    "metrics": metrics,
                    "service": "kotlin-mcp-server",
                },
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            logging.warning(f"Failed to export telemetry: {e}")


class RBACManager:
    """Role-Based Access Control manager."""

    def __init__(self) -> None:
        self.policies: Dict[UserRole, RBACPolicy] = {}
        self.user_roles: Dict[str, UserRole] = {}
        self._load_default_policies()

    def _load_default_policies(self) -> None:
        """Load default RBAC policies."""
        # Admin policy
        self.policies[UserRole.ADMIN] = RBACPolicy(
            role=UserRole.ADMIN, permissions=set(Permission), resource_patterns=["*"]
        )

        # Developer policy
        self.policies[UserRole.DEVELOPER] = RBACPolicy(
            role=UserRole.DEVELOPER,
            permissions={
                Permission.FILE_READ,
                Permission.FILE_WRITE,
                Permission.GIT_READ,
                Permission.GIT_WRITE,
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.BUILD_EXECUTE,
                Permission.SECURITY_ENCRYPT,
                Permission.SECURITY_DECRYPT,
            },
            resource_patterns=["src/**", "tests/**", "*.kt", "*.java", "*.gradle"],
        )

        # Read-only policy
        self.policies[UserRole.READONLY] = RBACPolicy(
            role=UserRole.READONLY,
            permissions={Permission.FILE_READ, Permission.GIT_READ, Permission.API_READ},
            resource_patterns=["**"],
        )

        # Guest policy
        self.policies[UserRole.GUEST] = RBACPolicy(
            role=UserRole.GUEST,
            permissions={Permission.FILE_READ},
            resource_patterns=["README.md", "docs/**"],
        )

    def assign_role(self, user_id: str, role: UserRole) -> None:
        """Assign role to user."""
        self.user_roles[user_id] = role

    def check_permission(self, user_id: str, permission: Permission, resource: str = "") -> bool:
        """Check if user has permission for resource."""
        role = self.user_roles.get(user_id, UserRole.GUEST)
        policy = self.policies.get(role)

        if not policy:
            return False

        # Check permission
        if permission not in policy.permissions:
            return False

        # Check resource pattern
        if resource and policy.resource_patterns != ["*"]:
            if not any(
                self._matches_pattern(resource, pattern) for pattern in policy.resource_patterns
            ):
                return False

        return True

    def _matches_pattern(self, resource: str, pattern: str) -> bool:
        """Check if resource matches pattern (simple glob matching)."""
        # Simple implementation - could be enhanced with fnmatch
        if pattern == "*":
            return True
        if pattern.endswith("/**"):
            prefix = pattern[:-3]
            return resource.startswith(prefix)
        return resource == pattern


class SlidingWindowRateLimiter:
    """Sliding window rate limiter."""

    def __init__(self, config: RateLimitConfig):
        self.requests_per_window = config.requests_per_window
        self.window_seconds = config.window_seconds
        self.burst_limit = config.burst_limit or config.requests_per_window * 2
        self.requests: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.burst_limit))

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit."""
        now = time.time()
        request_times = self.requests[key]

        # Remove old requests outside the window
        while request_times and now - request_times[0] > self.window_seconds:
            request_times.popleft()

        # Check if under limit
        if len(request_times) >= self.requests_per_window:
            return False

        # Add current request
        request_times.append(now)
        return True

    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests in current window."""
        now = time.time()
        request_times = self.requests[key]

        # Clean old requests
        while request_times and now - request_times[0] > self.window_seconds:
            request_times.popleft()

        return max(0, self.requests_per_window - len(request_times))


class CircuitBreaker:
    """Circuit breaker implementation."""

    class State(Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"

    def __init__(self, config: CircuitBreakerConfig) -> None:
        self.failure_threshold = config.failure_threshold
        self.recovery_timeout = config.recovery_timeout
        self.expected_exception = config.expected_exception
        self.state = self.State.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None

    def __call__(self, func: Any) -> Any:
        """Decorator to apply circuit breaker to function."""

        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if self.state == self.State.OPEN:
                if self._should_attempt_reset():
                    self.state = self.State.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self) -> None:
        """Handle successful call."""
        if self.state == self.State.HALF_OPEN:
            self.state = self.State.CLOSED
            self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = self.State.OPEN


class TTLCache:
    """Time-To-Live cache implementation."""

    def __init__(self, default_ttl: float = 300.0) -> None:  # 5 minutes default
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        entry = self.cache.get(key)
        if entry and not entry.is_expired():
            return entry.data
        elif entry:
            del self.cache[key]  # Remove expired entry
        return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache with TTL."""
        ttl = ttl or self.default_ttl
        self.cache[key] = CacheEntry(data=value, timestamp=time.time(), ttl=ttl)

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        self.cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

    def cleanup_expired(self) -> None:
        """Remove expired entries."""
        expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
        for key in expired_keys:
            del self.cache[key]


class SecurityHardeningManager:
    """Main security hardening manager."""

    def __init__(self):
        self.rbac = RBACManager()
        self.rate_limiter = SlidingWindowRateLimiter(
            RateLimitConfig(
                requests_per_window=Config.get_int("RATE_LIMIT_REQUESTS", 100),
                window_seconds=Config.get_int("RATE_LIMIT_WINDOW", 60),
                burst_limit=Config.get_int("RATE_LIMIT_BURST", 200),
            )
        )
        self.circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=Config.get_int("CIRCUIT_BREAKER_THRESHOLD", 5),
                recovery_timeout=Config.get_float("CIRCUIT_BREAKER_TIMEOUT", 60.0),
            )
        )
        self.cache = TTLCache(default_ttl=Config.get_float("CACHE_DEFAULT_TTL", 300.0))
        self.metrics = MetricsCollector()
        self.telemetry = TelemetryExporter()

    async def check_access(
        self, user_id: str, tool_name: str, permission: Permission, resource: str = ""
    ) -> bool:
        """Check if user has access to perform operation."""
        # Record access attempt
        self.metrics.increment_counter(
            "access_attempts",
            {"user_id": user_id, "tool": tool_name, "permission": permission.value},
        )

        # Check rate limit
        if not self.rate_limiter.is_allowed(user_id):
            self.metrics.increment_counter("rate_limit_exceeded", {"user_id": user_id})
            return False

        # Check RBAC
        allowed = self.rbac.check_permission(user_id, permission, resource)
        if not allowed:
            self.metrics.increment_counter(
                "access_denied", {"user_id": user_id, "tool": tool_name, "reason": "rbac"}
            )

        return allowed

    def get_cache_key(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Generate cache key from tool name and arguments."""
        key_data = {"tool": tool_name, **args}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    async def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result if available."""
        return self.cache.get(cache_key)

    async def cache_result(self, cache_key: str, result: Any, ttl: Optional[float] = None):
        """Cache result with TTL."""
        self.cache.set(cache_key, result, ttl)

    async def execute_with_hardening(
        self,
        user_id: str,
        tool_name: str,
        permission: Permission,
        resource: str,
        operation_func,
        *args,
        **kwargs,
    ) -> Any:
        """Execute operation with full hardening applied."""
        start_time = time.time()

        try:
            # Check access
            if not await self.check_access(user_id, tool_name, permission, resource):
                raise PermissionError(f"Access denied for user {user_id}")

            # Check cache for read operations
            cache_key = None
            if permission in [Permission.FILE_READ, Permission.GIT_READ, Permission.API_READ]:
                cache_key = self.get_cache_key(tool_name, kwargs)
                cached_result = await self.get_cached_result(cache_key)
                if cached_result is not None:
                    self.metrics.increment_counter("cache_hit", {"tool": tool_name})
                    return cached_result
                self.metrics.increment_counter("cache_miss", {"tool": tool_name})

            # Execute with circuit breaker
            @self.circuit_breaker
            async def execute():
                return await operation_func(*args, **kwargs)

            result = await execute()

            # Cache result for read operations
            if cache_key and result is not None:
                await self.cache_result(cache_key, result)

            # Record success metrics
            execution_time = time.time() - start_time
            self.metrics.record_histogram(
                "operation_duration", execution_time, {"tool": tool_name, "status": "success"}
            )
            self.metrics.increment_counter("operations_completed", {"tool": tool_name})

            return result

        except Exception as e:
            # Record failure metrics
            execution_time = time.time() - start_time
            self.metrics.record_histogram(
                "operation_duration",
                execution_time,
                {"tool": tool_name, "status": "error", "error_type": type(e).__name__},
            )
            self.metrics.increment_counter("operations_failed", {"tool": tool_name})
            raise e

    async def export_telemetry(self):
        """Export collected metrics via telemetry."""
        async with self.telemetry:
            await self.telemetry.export(self.metrics.get_metrics())

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for monitoring."""
        metrics_data = self.metrics.get_metrics()
        return {
            "uptime_seconds": time.time() - self.metrics.start_time,
            "total_operations": sum(
                sum(counts.values())
                for counts in metrics_data["counters"].get("operations_completed", {}).values()
            ),
            "total_failures": sum(
                sum(counts.values())
                for counts in metrics_data["counters"].get("operations_failed", {}).values()
            ),
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "rate_limit_exceeded": sum(
                sum(counts.values())
                for counts in metrics_data["counters"].get("rate_limit_exceeded", {}).values()
            ),
        }

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        metrics_data = self.metrics.get_metrics()
        hits = sum(
            sum(counts.values())
            for counts in metrics_data["counters"].get("cache_hit", {}).values()
        )
        misses = sum(
            sum(counts.values())
            for counts in metrics_data["counters"].get("cache_miss", {}).values()
        )
        total = hits + misses
        return hits / total if total > 0 else 0.0


# Global hardening manager instance
hardening_manager = SecurityHardeningManager()


class HardeningTool(IntelligentToolBase):
    """Tool for managing security hardening features."""

    def __init__(self, project_path: str):
        super().__init__(project_path)
        self.name = "security_hardening"
        self.description = (
            "Manage security hardening features including RBAC, rate limiting, and monitoring"
        )

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        """Execute the core functionality of the hardening tool."""
        operation = arguments.get("operation")

        if operation == "get_metrics":
            return {
                "metrics": hardening_manager.get_metrics_summary(),
                "timestamp": datetime.now().isoformat(),
            }

        elif operation == "assign_role":
            user_id = arguments.get("user_id")
            role_name = arguments.get("role")
            if not isinstance(user_id, str) or not isinstance(role_name, str):
                return {"status": "error", "message": "user_id and role must be strings"}
            try:
                role = UserRole(role_name)
                hardening_manager.rbac.assign_role(user_id, role)
                return {"status": "success", "user_id": user_id, "role": role_name}
            except ValueError as e:
                return {"status": "error", "message": f"Invalid role: {role_name}"}

        elif operation == "check_permission":
            user_id = arguments.get("user_id")
            permission_name = arguments.get("permission")
            resource = arguments.get("resource", "")
            if not isinstance(user_id, str) or not isinstance(permission_name, str):
                return {"status": "error", "message": "user_id and permission must be strings"}
            try:
                permission = Permission(permission_name)
                allowed = hardening_manager.rbac.check_permission(user_id, permission, resource)
                return {
                    "user_id": user_id,
                    "permission": permission_name,
                    "resource": resource,
                    "allowed": allowed,
                }
            except ValueError as e:
                return {"status": "error", "message": f"Invalid permission: {permission_name}"}

        elif operation == "clear_cache":
            hardening_manager.cache.clear()
            return {"status": "success", "message": "Cache cleared"}

        elif operation == "export_telemetry":
            await hardening_manager.export_telemetry()
            return {"status": "success", "message": "Telemetry exported"}

        else:
            return {
                "status": "error",
                "message": f"Unknown operation: {operation}",
                "available_operations": [
                    "get_metrics",
                    "assign_role",
                    "check_permission",
                    "clear_cache",
                    "export_telemetry",
                ],
            }


# Export the hardening manager for use by other modules
__all__ = ["hardening_manager", "HardeningTool", "UserRole", "Permission"]
