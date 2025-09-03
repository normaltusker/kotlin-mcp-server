# sidecar_client.py
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import time
from typing import Any, Dict, Optional, Tuple

# --- env config with sane defaults (no config.yaml) ---
MCP_SIDECAR_CMD = json.loads(os.getenv("MCP_SIDECAR_CMD", '["java","-jar","kotlin-sidecar.jar"]'))
MCP_API_TIMEOUT_MS = int(os.getenv("MCP_API_TIMEOUT_MS", "3000"))
MCP_MAX_RETRIES = int(os.getenv("MCP_MAX_RETRIES", "5"))
MCP_SIDECAR_STARTUP_TIMEOUT_MS = int(os.getenv("MCP_SIDECAR_STARTUP_TIMEOUT_MS", "6000"))


# optional: circuit breaker signals from your hardening module (stubbed)
class CircuitOpen(Exception):
    """Circuit breaker is open."""

    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_time_s: int = 10):
        self.failure_threshold = failure_threshold
        self.reset_time_s = reset_time_s
        self.failures = 0
        self.open_until = 0.0

    def allow(self) -> None:
        now = time.time()
        if now < self.open_until:
            raise CircuitOpen("sidecar circuit open")
        # half-open allowed if elapsed

    def success(self) -> None:
        self.failures = 0
        self.open_until = 0.0

    def failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.open_until = time.time() + self.reset_time_s


_circuit = CircuitBreaker()


class _SidecarProcess:
    def __init__(self, cmd: list[str]):
        self.cmd = cmd
        self.proc: Optional[subprocess.Popen] = None
        self.stdout_q: "queue.Queue[str]" = queue.Queue()
        self._stdout_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self.proc and self.proc.poll() is None:
            return
        self.proc = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # line-oriented JSON (NDJSON)
            bufsize=1,  # line buffered
        )
        self._stdout_thread = threading.Thread(target=self._pump_stdout, daemon=True)
        self._stdout_thread.start()

    def _pump_stdout(self) -> None:
        assert self.proc and self.proc.stdout
        for line in self.proc.stdout:
            self.stdout_q.put(line.rstrip("\n"))

    def request(self, payload: Dict[str, Any], timeout_ms: int) -> Dict[str, Any]:
        if not self.proc or self.proc.poll() is not None:
            self.start()
        assert self.proc and self.proc.stdin
        line = json.dumps(payload, separators=(",", ":"))
        # write request
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()
        # read response
        deadline = time.time() + timeout_ms / 1000.0
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError("sidecar response timed out")
            try:
                resp_line = self.stdout_q.get(timeout=remaining)
                if not resp_line:
                    continue
                obj = json.loads(resp_line)
                return obj
            except queue.Empty:
                raise TimeoutError("sidecar response timed out")

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
            except Exception:
                pass
        self.proc = None


# singleton-ish sidecar
_sidecar = _SidecarProcess(MCP_SIDECAR_CMD)


def call_sidecar(
    tool: str, tool_input: Dict[str, Any], *, timeout_ms: Optional[int] = None
) -> Dict[str, Any]:
    """
    Send a single JSON request to the sidecar and return the JSON response.
    Contract (NDJSON):
      REQ: {"tool": "<name>", "input": { ... }}
      RES: {"ok": true, "result": {...}}  OR  {"ok": false, "error": {"code": "...", "message": "...", "data": {...}}}
    """
    payload = {"tool": tool, "input": tool_input}
    timeout = timeout_ms or MCP_API_TIMEOUT_MS

    # startup (best-effort)
    try:
        _sidecar.start()
    except Exception as e:
        raise RuntimeError(f"failed to start sidecar: {e}") from e

    # retry with exponential backoff + circuit breaker
    backoff = 0.1
    for attempt in range(1, MCP_MAX_RETRIES + 1):
        try:
            _circuit.allow()
            resp = _sidecar.request(payload, timeout_ms=timeout)
            if not isinstance(resp, dict) or "ok" not in resp:
                raise RuntimeError(f"malformed sidecar response: {resp}")

            if resp.get("ok") is True:
                _circuit.success()
                return resp["result"]

            # error from sidecar (semantic)
            err = resp.get("error", {})
            code = err.get("code", "SidecarError")
            msg = err.get("message", "unknown error")
            data = err.get("data")
            # do not retry on validation errors; retry on transient categories
            if code in {"ValidationError", "BadRequest", "UnsupportedTool"}:
                _circuit.success()
                raise RuntimeError(f"{code}: {msg}", data)
            # transient → fallthrough to retry
            raise RuntimeError(f"{code}: {msg}")

        except (TimeoutError, BrokenPipeError, RuntimeError) as e:
            # decide retryability
            retryable = isinstance(e, TimeoutError) or "EPIPE" in str(e) or "SidecarError" in str(e)
            if not retryable or attempt == MCP_MAX_RETRIES:
                _circuit.failure()
                raise
            _circuit.failure()
            time.sleep(backoff)
            backoff = min(backoff * 2, 2.0)  # cap backoff
            # if process died, try restart
            if _sidecar.proc and _sidecar.proc.poll() is not None:
                _sidecar.start()


def shutdown_sidecar() -> None:
    _sidecar.stop()


# --- handy helpers for MCP tools that need diffs from sidecar ---


def sidecar_refactor_function(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Expects schema-conformant input for `refactorFunction`.
    Returns: {"diff": "...", "success": true, "affectedFiles": ["..."], "diagnostics": [...]}
    """
    result = call_sidecar("refactorFunction", input_payload)
    # Adapt sidecar result to expected format
    return {
        "diff": result.get("diff") or result.get("patch") or "",
        "success": result.get("success", True),
        "affectedFiles": result.get("affectedFiles", []),
        "diagnostics": result.get("diagnostics", []),
    }


def sidecar_apply_code_action(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = call_sidecar("applyCodeAction", input_payload)
    return {
        "diff": result.get("diff") or result.get("patch") or "",
        "success": result.get("success", True),
        "affectedFiles": result.get("affectedFiles", []),
        "diagnostics": result.get("diagnostics", []),
    }


def sidecar_format_code(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = call_sidecar("formatCode", input_payload)
    return {
        "diff": result.get("diff") or result.get("patch") or "",
        "success": result.get("success", True),
        "affectedFiles": result.get("affectedFiles", []),
        "diagnostics": result.get("diagnostics", []),
    }


def sidecar_optimize_imports(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = call_sidecar("optimizeImports", input_payload)
    return {
        "diff": result.get("diff") or result.get("patch") or "",
        "success": result.get("success", True),
        "affectedFiles": result.get("affectedFiles", []),
        "diagnostics": result.get("diagnostics", []),
    }
