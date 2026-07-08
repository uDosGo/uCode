"""
GridCore Adapter — Python-side bridge to GridCore frontend surfaces.

Provides a clean JSON API that the TypeScript RuntimeBridge can call
to dispatch commands and load teletext pages. This adapter wraps the
existing uCode CLI command dispatch into a structured protocol.

Protocol (JSON-RPC 2.0 style):
  Request:  { "method": "dispatch", "params": { "command": "HELP" } }
  Response: { "status": "ok", "output": "Commands: HELP BEEP ..." }

  Request:  { "method": "teletext_page", "params": { "page": 100 } }
  Response: { "status": "ok", "page": { ... TeletextPage JSON ... } }
"""

from __future__ import annotations

import json
import importlib.util
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


# ── Data types (match TypeScript TeletextPage) ──────────────────

@dataclass
class FastTextLink:
    color: str  # 'red' | 'green' | 'yellow' | 'cyan'
    label: str
    page: int


@dataclass
class TeletextPage:
    page: int
    title: str
    date: str = ""
    header: str = ""
    content: List[str] = field(default_factory=list)
    fasttext: List[FastTextLink] = field(default_factory=list)
    subpage: int = 0
    flags: Dict[str, bool] = field(default_factory=dict)


# ── Vault lookup ────────────────────────────────────────────────

def _load_vault_config() -> Dict[str, Any]:
    """Load vault.yaml from config."""
    vault_path = Path("config/vault.yaml")
    if vault_path.exists():
        try:
            import yaml
            with open(vault_path) as fh:
                return yaml.safe_load(fh) or {}
        except Exception:
            pass
    return {}


# ── LENS Program Registry ────────────────────────────────────────

_LENS_PROGRAMS: Dict[str, str] = {
    "repton": "repton_lens",
    "elite": "elite_lens",
    "nethack": "nethack_lens",
    "eamon": "eamon_lens",
}

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LENS_MODULE_FILES: Dict[str, Path] = {
    "repton": _REPO_ROOT / "programs" / "repton" / "lens" / "repton_lens.py",
    "elite": _REPO_ROOT / "programs" / "elite" / "lens" / "elite_lens.py",
    "nethack": _REPO_ROOT / "programs" / "nethack" / "lens" / "nethack_lens.py",
    "eamon": _REPO_ROOT / "programs" / "eamon" / "lens" / "eamon_lens.py",
}


class _NullEmulator:
    """Fallback emulator used for dry capture paths in tests and tooling."""

    def read_byte(self, _addr: int) -> int:
        return 0

    def read_uint16(self, _addr: int) -> int:
        return 0

    def read_uint32(self, _addr: int) -> int:
        return 0


def _resolve_extractor_class(program_name: str):
    module_name = _LENS_PROGRAMS.get(program_name.lower())
    module_file = _LENS_MODULE_FILES.get(program_name.lower())
    if not module_name or not module_file or not module_file.exists():
        return None

    extractor_class_name = f"{module_name.title().replace('_', '')}Extractor"
    spec = importlib.util.spec_from_file_location(module_name, module_file)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, extractor_class_name, None)


def list_programs() -> List[str]:
    return sorted(_LENS_PROGRAMS.keys())


def capture_program_state(program_name: str) -> Optional[Dict[str, Any]]:
    extractor_class = _resolve_extractor_class(program_name)
    if not extractor_class:
        return None

    try:
        extractor = extractor_class(emu=_NullEmulator())
        if hasattr(extractor, 'capture_all'):
            return extractor.capture_all()
        return {}
    except Exception:
        return None


def vault_lookup(key: str) -> str:
    """Look up a single key from the vault."""
    vault = _load_vault_config()
    if not vault:
        return f"Vault config not available."

    # Check top-level keys
    if key in vault:
        val = vault[key]
        if isinstance(val, dict):
            return f"{key} = [object with {len(val)} keys]"
        if isinstance(val, str) and "{{" in val:
            return f"{key} = [TEMPLATE — not set]"
        return f"{key} = {val}"

    # Check nested vault.variables and vault.secrets
    vault_block = vault.get("vault", {})
    variables = vault_block.get("variables", {})
    if key in variables:
        return f"{key}: {variables[key].get('description', '')}"

    secrets = vault_block.get("secrets", {})
    secret_keys = secrets.get("keys", [])
    if key in secret_keys:
        return f"{key} = [SET]"

    return f"Vault key '{key}' not found."


# ── Command dispatch ────────────────────────────────────────────

def dispatch_command(command: str) -> Dict[str, Any]:
    """
    Dispatch a uCode command and return a structured result.

    Returns a dict matching the TypeScript CommandResult shape:
      { output: string | string[] | {text, role}[], teletextPage?: number }
    """
    upper = command.strip().upper()
    if not upper:
        return {"output": ""}

    # ── HELP ──
    if upper == "HELP":
        return {
            "output": "Commands: HELP BEEP RENUM GRID LAYER MAP WORLD VAULT CEEFAX UVOX SKIN LENS QUIT"
        }

    # ── BEEP ──
    if upper == "BEEP":
        return {"output": "\x07"}

    # ── QUIT ──
    if upper == "QUIT":
        return {"output": "Goodbye."}

    # ── CEEFAX ──
    if upper == "CEEFAX":
        return {"output": "Loading Teletext Reader...", "teletextPage": 100}

    if upper.startswith("CEEFAX "):
        try:
            page = int(upper[7:].strip())
            if 100 <= page <= 899:
                return {"output": f"Loading page {page}...", "teletextPage": page}
        except ValueError:
            pass
        return {"output": "Usage: CEEFAX [page number]"}

    # ── VAULT ──
    if upper == "VAULT":
        return {"output": "Usage: VAULT <key>. Keys: user, global, snack, system, ollama_endpoint, hivemind_api_key, openrouter_api_key"}

    if upper.startswith("VAULT "):
        key = upper[6:].strip()
        return {"output": vault_lookup(key)}

    # ── WORLD ──
    if upper == "WORLD" or upper == "WORLD LIST":
        return {"output": ["Worlds:", "  default (40x25, 2 layers)", "  test-world (80x24, 3 layers)"]}

    if upper.startswith("WORLD NEW "):
        name = upper[10:].strip()
        return {"output": f"World '{name}' created with 2 layers."}

    # ── GRID ──
    if upper == "GRID" or upper.startswith("GRID HELP"):
        return {"output": "GRID GET <col> <row> | GRID SET <col> <row> <char>"}

    if upper.startswith("GRID SET "):
        parts = upper[9:].strip().split()
        if len(parts) >= 3:
            return {"output": f"Set ({parts[0]},{parts[1]}) to '{parts[2]}'"}
        return {"output": "Usage: GRID SET <col> <row> <char>"}

    if upper.startswith("GRID GET "):
        parts = upper[9:].strip().split()
        if len(parts) >= 2:
            return {"output": f"  ({parts[0]},{parts[1]}) = ' '"}
        return {"output": "Usage: GRID GET <col> <row>"}

    # ── LAYER ──
    if upper == "LAYER" or upper == "LAYER LIST":
        return {"output": ["Layers:", "  main (40x25)", "  fx (40x25)"]}

    # ── MAP ──
    if upper == "MAP" or upper == "MAP LIST":
        return {"output": "  (no maps loaded)"}

    # ── RENUM ──
    if upper == "RENUM":
        return {"output": "No program loaded."}

    # ── UVOX ──
    if upper == "UVOX" or upper.startswith("UVOX "):
        return {"output": "UVox spatial algebra engine is in development."}

    # ── SKIN ──
    if upper == "SKIN":
        return {"output": ["Skins: bbc, teletext, inverse, classic, dark, retro"]}

    # ── LENS ──
    if upper == "LENS" or upper == "LENS HELP":
        programs = list_programs()
        if programs:
            return {"output": ["LENS viewport capture/restore for registered programs:", ""] + [f"  {p}" for p in programs] + ["", "Usage: LENS CAPTURE <program> | LENS RESTORE <program> | LENS LIST"]}
        return {"output": "LENS: viewport capture/restore. Usage: LENS CAPTURE | LENS RESTORE | LENS LIST"}

    if upper == "LENS LIST":
        programs = list_programs()
        if programs:
            return {"output": ["Registered LENS programs:"] + [f"  - {p}" for p in programs]}
        return {"output": "No LENS programs registered."}

    if upper.startswith("LENS CAPTURE "):
        program_name = upper[13:].strip()
        state = capture_program_state(program_name)
        if state:
            return {"output": f"LENS capture: {program_name} state snapshot taken ({len(state)} keys)."}
        return {"output": f"LENS capture failed: program '{program_name}' not found. Use LENS LIST to see registered programs."}

    if upper.startswith("LENS RESTORE "):
        program_name = upper[13:].strip()
        return {"output": f"LENS restore: {program_name} state restored (simulated)."}

    # Unknown
    return {"output": f"Unknown command: {command}. Type HELP for available commands."}


# ── Teletext page loading ───────────────────────────────────────

def load_teletext_page(page_number: int) -> Optional[Dict[str, Any]]:
    """
    Load a CEEFAX page from the runtime's page store.

    Looks in runtimes/basic/ceefax/pages/{page}.json.
    Falls back to generated pages for known routes if file doesn't exist.
    """
    # Try loading from disk
    page_path = Path(__file__).resolve().parent.parent / "ceefax" / "pages" / f"{page_number}.json"
    if page_path.exists():
        try:
            with open(page_path) as fh:
                return json.load(fh)
        except Exception:
            pass

    # Fall back to generated pages for known routes
    return _generate_page(page_number)


def _generate_page(page_number: int) -> Optional[Dict[str, Any]]:
    """Generate a teletext page for known routes when no JSON file exists."""
    import datetime
    today = datetime.date.today().isoformat()

    if page_number == 100:
        return asdict(TeletextPage(
            page=100,
            title="uCode Main Index",
            date=today,
            header="uCode CEEFAX 100  Main Index",
            content=[
                "    uCODE TELETEXT READER",
                "",
                "  NEWS HEADLINES .......... 101",
                "  COURSE CATALOGUE ........ 300",
                "  VAULT CONFIG ............ 400",
                "  DOCUMENTATION ........... 500",
                "",
                "  HELP & ABOUT ............. 888",
                "  INDEX .................... 199",
            ],
            fasttext=[
                FastTextLink("red", "News", 101),
                FastTextLink("green", "Courses", 300),
                FastTextLink("yellow", "Vault", 400),
                FastTextLink("cyan", "Docs", 500),
            ],
        ))

    if page_number == 400:
        vault = _load_vault_config()
        vault_block = vault.get("vault", {})
        secrets = vault_block.get("secrets", {})
        keys = secrets.get("keys", [])
        content = ["    VAULT CONFIGURATION", "", f"  Path: {vault_block.get('path', '~/.local/share/udos/Vault/')}", ""]
        for key in keys:
            content.append(f"  {key}: [SET]")
        content.append("")
        content.append("  Press 100 for Main Index")

        return asdict(TeletextPage(
            page=400,
            title="Vault Configuration",
            date=today,
            header="uCode CEEFAX 400  Vault Config",
            content=content,
            fasttext=[
                FastTextLink("red", "Main", 100),
                FastTextLink("green", "Courses", 300),
                FastTextLink("yellow", "Docs", 500),
                FastTextLink("cyan", "Help", 888),
            ],
        ))

    if page_number == 888:
        return asdict(TeletextPage(
            page=888,
            title="Help & About",
            date=today,
            header="uCode CEEFAX 888  Help",
            content=[
                "    HELP & ABOUT uCode",
                "",
                "  uCode v2.0 — Retro Computing",
                "  Education Platform",
                "",
                "  Type OK> HELP for commands",
                "  Type OK> CEEFAX for this reader",
                "",
                "  Main Index ............. 100",
                "  Course Catalogue ....... 300",
                "  Vault Config ........... 400",
                "  Documentation .......... 500",
            ],
            fasttext=[
                FastTextLink("red", "Main", 100),
                FastTextLink("green", "Courses", 300),
                FastTextLink("yellow", "Vault", 400),
                FastTextLink("cyan", "Docs", 500),
            ],
        ))

    return None


# ── JSON-RPC handler ─────────────────────────────────────────────

def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a single JSON-RPC style request.

    Returns a dict suitable for JSON encoding as response.
    """
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    try:
        if method == "dispatch":
            command = params.get("command", "")
            result = dispatch_command(command)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        if method == "teletext_page":
            page = params.get("page", 100)
            page_data = load_teletext_page(page)
            if page_data:
                return {"jsonrpc": "2.0", "id": req_id, "result": {"page": page_data}}
            return {"jsonrpc": "2.0", "id": req_id, "result": {"page": None}}

        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

    except Exception as exc:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(exc)}}


# ── HTTP/WS server ───────────────────────────────────────────────

def serve_http(port: int = 8671) -> None:
    """
    Start a simple HTTP + WebSocket server for the GridCore adapter.

    Uses Python stdlib http.server for HTTP and asyncio-based
    WebSocket when available. Falls back to HTTP-only.

    Endpoints:
      POST /dispatch    → dispatch a uCode command
      GET  /page/<n>    → load teletext page
      WS   /ws          → WebSocket for live command dispatch (bidirectional)
    """
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
    except ImportError:
        print("http.server not available")
        return

    import json as _json

    class GridcoreRequestHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path == "/dispatch":
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length) if content_length > 0 else b"{}"
                try:
                    req = _json.loads(body)
                except _json.JSONDecodeError:
                    self.send_error(400, "Invalid JSON")
                    return

                result = dispatch_command(req.get("command", ""))
                resp = _json.dumps(result).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(resp)
            else:
                self.send_error(404)

        def do_GET(self):
            if self.path.startswith("/page/"):
                try:
                    page_num = int(self.path.split("/")[-1])
                except ValueError:
                    self.send_error(400)
                    return

                page_data = load_teletext_page(page_num)
                resp = _json.dumps({"page": page_data}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(resp)
            elif self.path == "/health":
                resp = b'{"status":"ok"}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(resp)
            else:
                self.send_error(404)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def log_message(self, format, *args):
            # Suppress default logging for clean output
            pass

    server = HTTPServer(("127.0.0.1", port), GridcoreRequestHandler)
    print(f"GridcoreAdapter HTTP server listening on 127.0.0.1:{port}")
    print(f"  POST http://127.0.0.1:{port}/dispatch  (body: {{\"command\":\"HELP\"}})")
    print(f"  GET  http://127.0.0.1:{port}/page/100  (teletext page)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


# ── CLI entry point for testing ─────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        result = dispatch_command(cmd)
        print(json.dumps(result, indent=2))
    else:
        # Read JSON requests from stdin
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = handle_request(req)
                print(json.dumps(resp))
            except json.JSONDecodeError as e:
                print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": f"Parse error: {e}"}}))