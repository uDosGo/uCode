"""
BBCSDL JSON Protocol — structured command/response overlay on BBCSDL process.

Wraps BBCSDLProcess with a JSON-RPC 2.0 protocol over stdin/stdout,
replacing raw line dispatch with typed commands and responses.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from bridge.bbcsdl_bridge import BBCSDLProcess


@dataclass
class BBCSDLJsonResponse:
    """Structured response from BBCSDL engine via JSON protocol."""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None

    @property
    def ok(self) -> bool:
        return self.error is None


class BBCSDLJsonClient:
    """
    JSON-RPC client for the BBCSDL engine.

    Commands:
      - GRID_SET {col, row, char, fg?, bg?}   → set a cell
      - GRID_GET {col, row}                    → get a cell
      - GRID_DUMP {}                           → dump full grid
      - PROGRAM_LOAD {source}                  → load BASIC program
      - PROGRAM_RUN {}                         → run loaded program
      - PROGRAM_STOP {}                        → stop running program
      - DIRECT {line}                          → pass-through to BBC BASIC direct mode
      - LENS_CAPTURE {}                        → capture current display state
      - SKIN_APPLY {theme}                     → apply a skin theme
      - STATUS {}                              → engine status
    """

    def __init__(self, process: BBCSDLProcess):
        self._process = process
        self._pending: Dict[str, BBCSDLJsonResponse] = {}
        self._lock = threading.Lock()
        self._response_ready = threading.Condition(self._lock)
        self._next_id = 0

        # Hook into the process output stream
        self._process._on_line = self._handle_line

    def _next_request_id(self) -> str:
        with self._lock:
            self._next_id += 1
            return str(self._next_id)

    def _handle_line(self, line: str) -> None:
        """Parse JSON-RPC response lines from BBCSDL stdout."""
        if not line.startswith("{"):
            # Non-JSON output (e.g. program output) — store as raw
            return

        try:
            msg = json.loads(line)
            if "jsonrpc" not in msg or "id" not in msg:
                return

            req_id = str(msg["id"])
            resp = BBCSDLJsonResponse(
                jsonrpc=msg.get("jsonrpc", "2.0"),
                id=req_id,
                result=msg.get("result", {}),
                error=msg.get("error"),
            )
            with self._lock:
                self._pending[req_id] = resp
                self._response_ready.notify_all()
        except json.JSONDecodeError:
            pass

    def call(self, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> BBCSDLJsonResponse:
        """Send a JSON-RPC request and wait for response."""
        req_id = self._next_request_id()
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }
        payload = json.dumps(request)

        # Send
        if not self._process.running:
            return BBCSDLJsonResponse(
                id=req_id,
                error={"code": -32000, "message": "BBCSDL process not running"},
            )

        self._process.send(payload)

        # Wait for response
        deadline = time.time() + timeout
        with self._lock:
            while time.time() < deadline:
                if req_id in self._pending:
                    return self._pending.pop(req_id)
                self._response_ready.wait(timeout=0.1)

        return BBCSDLJsonResponse(
            id=req_id,
            error={"code": -32001, "message": f"Timeout waiting for response to {method}"},
        )

    def call_async(self, method: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Send a JSON-RPC request without waiting (fire-and-forget). Returns request ID."""
        req_id = self._next_request_id()
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }
        payload = json.dumps(request)

        if self._process.running:
            self._process.send(payload)

        return req_id

    # ── Convenience methods ─────────────────────────────────────

    def grid_set(self, col: int, row: int, char: str, fg: int = 7, bg: int = 0, layer: int = 0) -> BBCSDLJsonResponse:
        return self.call("GRID_SET", {"col": col, "row": row, "char": char, "fg": fg, "bg": bg, "layer": layer})

    def grid_get(self, col: int, row: int, layer: int = 0) -> BBCSDLJsonResponse:
        return self.call("GRID_GET", {"col": col, "row": row, "layer": layer})

    def grid_dump(self) -> BBCSDLJsonResponse:
        return self.call("GRID_DUMP", {})

    def program_load(self, source: str) -> BBCSDLJsonResponse:
        return self.call("PROGRAM_LOAD", {"source": source})

    def program_run(self) -> BBCSDLJsonResponse:
        return self.call("PROGRAM_RUN", {})

    def program_stop(self) -> BBCSDLJsonResponse:
        return self.call("PROGRAM_STOP", {})

    def direct(self, line: str) -> BBCSDLJsonResponse:
        return self.call("DIRECT", {"line": line})

    def lens_capture(self) -> BBCSDLJsonResponse:
        return self.call("LENS_CAPTURE", {})

    def skin_apply(self, theme: str) -> BBCSDLJsonResponse:
        return self.call("SKIN_APPLY", {"theme": theme})

    def status(self) -> BBCSDLJsonResponse:
        return self.call("STATUS", {})


# ── Self-test ───────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("BBCSDL JSON Protocol self-test")
    print("===============================")

    # Start process (mock mode — no real BBCSDL binary needed for protocol test)
    process = BBCSDLProcess()
    try:
        process.start()
    except FileNotFoundError:
        print("[SKIP] BBCSDL binary not found — testing protocol layer only")
        sys.exit(0)

    client = BBCSDLJsonClient(process)

    # Status check
    resp = client.status()
    print(f"STATUS: ok={resp.ok}")

    # Grid operations
    resp = client.grid_set(10, 10, "X")
    print(f"GRID_SET(10,10,X): ok={resp.ok}")

    resp = client.grid_get(10, 10)
    print(f"GRID_GET(10,10): ok={resp.ok}, result={resp.result}")

    # Program load
    program = '10 PRINT "Hello uCode"\n20 END\n'
    resp = client.program_load(program)
    print(f"PROGRAM_LOAD: ok={resp.ok}")

    # Direct mode
    resp = client.direct("PRINT 42")
    print(f"DIRECT: ok={resp.ok}")

    process.stop()
    print("Done.")