"""
BBCSDL Bridge — spawn and manage the BBC BASIC runtime process.

Provides a subprocess-based IPC bridge to bbcsdl, supporting:
  - stdin/stdout pipe communication
  - program upload and execution
  - LENS/SKIN hook dispatch
  - variable register snapshots
"""

import os
import subprocess
import threading
from pathlib import Path
from typing import Callable, Optional

BBCOUT_CHUNK_SIZE = 4096


def _find_bbcsdl() -> Path:
    """Locate the bbcsdl binary relative to this package or via env."""
    candidate = os.environ.get("BBCOUT_BBCOUT_PATH", "")
    if candidate and Path(candidate).exists():
        return Path(candidate)

    # Check adjacent bbcsdl engine package
    pkg_root = Path(__file__).resolve().parent.parent / "bbcsdl"
    for name in ("bbcsdl", "bbcsdl.exe"):
        binary = pkg_root / name
        if binary.exists():
            return binary

    raise FileNotFoundError(
        "Cannot locate bbcsdl binary. Set BBCOUT_BBCOUT_PATH or "
        "ensure runtimes/basic/bbcsdl/ contains the engine."
    )


class BBCSDLProcess:
    """
    Manage a single bbcsdl subprocess with line-oriented output dispatch.
    """

    def __init__(self, binary_path: Optional[Path] = None):
        self._bin = binary_path or _find_bbcsdl()
        self._proc: Optional[subprocess.Popen] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._running = False
        self._on_line: Optional[Callable[[str], None]] = None

    @property
    def running(self) -> bool:
        return self._running and self._proc is not None and self._proc.poll() is None

    def start(self, on_line: Optional[Callable[[str], None]] = None) -> None:
        """Launch the bbcsdl engine in non-interactive mode."""
        if self.running:
            return

        self._on_line = on_line
        self._proc = subprocess.Popen(
            [str(self._bin), "-headless"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self._running = True
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

    def stop(self) -> None:
        """Terminate the bbcsdl process cleanly."""
        self._running = False
        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                self._proc.kill()
            self._proc = None

    def send(self, line: str) -> None:
        """Write a line into bbcsdl stdin."""
        if self._proc and self._proc.stdin:
            self._proc.stdin.write(line + "\n")
            self._proc.stdin.flush()

    def send_program(self, source: str) -> None:
        """Feed a multi-line BASIC program into the engine."""
        for line in source.splitlines():
            self.send(line)
        self.send("RUN")

    def _read_loop(self) -> None:
        """Drain stdout and dispatch each line."""
        while self._running and self._proc and self._proc.stdout:
            line = self._proc.stdout.readline()
            if not line:
                self._running = False
                break
            stripped = line.rstrip("\n\r")
            if self._on_line:
                self._on_line(stripped)