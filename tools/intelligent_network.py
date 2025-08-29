#!/usr/bin/env python3
"""
Intelligent Network Tool

Provides an HTTP client with retry logic, timeout handling, authentication
support, and response validation. Returns structured responses with basic
telemetry so callers can understand request behavior.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


@dataclass
class NetworkTelemetry:
    """Telemetry information for HTTP requests."""

    request_duration: float
    retries_attempted: int
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_duration": round(self.request_duration, 3),
            "retries_attempted": self.retries_attempted,
            "timestamp": self.timestamp,
        }


class IntelligentNetworkTool(IntelligentToolBase):
    """Advanced HTTP client with retry, timeout and response validation."""

    DEFAULT_BASE_URLS = {
        "TestAPI": "https://httpbin.org",
        "UserAPI": "https://httpbin.org",
        "ProductAPI": "https://httpbin.org",
        "OrderAPI": "https://httpbin.org",
    }

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        api_name = arguments.get("api_name", "")
        endpoint = arguments.get("endpoint", "")
        method = arguments.get("method", "GET").upper()
        data = arguments.get("data")
        headers = arguments.get("headers") or {}
        params = arguments.get("params") or {}
        timeout = arguments.get("timeout", 10.0)
        retries = int(arguments.get("retries", 3))
        auth_config = arguments.get("auth") or {}
        base_url = arguments.get("base_url") or self.DEFAULT_BASE_URLS.get(api_name, "https://httpbin.org")

        if not api_name or not endpoint:
            return {
                "success": False,
                "error": "api_name and endpoint are required",
            }

        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        auth: Optional[httpx.Auth] = None
        auth_type = auth_config.get("type")
        if auth_type == "basic":
            auth = httpx.BasicAuth(auth_config.get("username", ""), auth_config.get("password", ""))
        elif auth_type == "bearer":
            token = auth_config.get("token", "")
            if token:
                headers.setdefault("Authorization", f"Bearer {token}")

        telemetry = NetworkTelemetry(request_duration=0.0, retries_attempted=0, timestamp=time.time())
        last_error: Optional[str] = None
        start_time = time.monotonic()

        for attempt in range(1, retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.request(
                        method,
                        url,
                        params=params,
                        json=data if method in {"POST", "PUT", "PATCH", "DELETE"} else None,
                        headers=headers,
                        auth=auth,
                    )
                telemetry.request_duration = time.monotonic() - start_time
                telemetry.retries_attempted = attempt - 1

                success = 200 <= response.status_code < 300
                parsed: Any
                try:
                    parsed = response.json()
                except Exception:
                    parsed = response.text

                result = {
                    "success": success,
                    "status_code": response.status_code,
                    "url": url,
                    "method": method,
                    "data": parsed,
                    "headers": dict(response.headers),
                    "telemetry": telemetry.to_dict(),
                }

                if not success:
                    result["error"] = f"Unexpected status code: {response.status_code}"
                return result

            except httpx.RequestError as exc:
                last_error = str(exc)
                telemetry.retries_attempted = attempt
                await asyncio.sleep(min(2 ** attempt, 5))
                continue

        telemetry.request_duration = time.monotonic() - start_time
        return {
            "success": False,
            "error": f"Request failed: {last_error}",
            "url": url,
            "method": method,
            "telemetry": telemetry.to_dict(),
        }
