"""
Program Runner — loads and executes .ucode programs through BBCSDL.

Usage:
  python -m bridge.program_runner run path/to/program.ucode
  python -m bridge.program_runner serve     # start HTTP/WS adapter server
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from bridge.bbcsdl_bridge import BBCSDLProcess
from bridge.bbcsdl_json_protocol import BBCSDLJsonClient


def load_program(path: Path) -> Optional[str]:
    """Load a .ucode BASIC program from disk."""
    if not path.exists():
        print(f"Error: program not found: {path}")
        return None

    return path.read_text()


def run_program(source: str, bbcsdl_path: str = "./bbcsdl") -> bool:
    """Load and run a BASIC program via BBCSDL."""
    process = BBCSDLProcess()
    try:
        process.start()
    except FileNotFoundError:
        print(f"BBCSDL binary not found at {bbcsdl_path}")
        return False

    client = BBCSDLJsonClient(process)

    # Load program
    resp = client.call("PROGRAM_LOAD", {"source": source}, timeout=10.0)
    if not resp.ok:
        print(f"Failed to load program: {resp.error}")
        process.stop()
        return False

    # Run
    resp = client.call("PROGRAM_RUN", {}, timeout=30.0)
    if not resp.ok:
        print(f"Program error: {resp.error}")
        process.stop()
        return False

    # Capture LENS state
    lens = client.call("LENS_CAPTURE", {}, timeout=5.0)
    if lens.ok:
        print(json.dumps(lens.result, indent=2))

    process.stop()
    return resp.ok


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m bridge.program_runner run <file.ucode>")
        print("       python -m bridge.program_runner serve")
        sys.exit(1)

    command = sys.argv[1]

    if command == "run":
        if len(sys.argv) < 3:
            print("Usage: python -m bridge.program_runner run <file.ucode>")
            sys.exit(1)

        path = Path(sys.argv[2])
        source = load_program(path)
        if source is None:
            sys.exit(1)

        print(f"Running: {path.name}")
        ok = run_program(source)
        if not ok:
            sys.exit(1)

    elif command == "serve":
        from bridge.gridcore_adapter import serve_http
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8671
        print(f"GridcoreAdapter HTTP/WS server on port {port}")
        serve_http(port)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()