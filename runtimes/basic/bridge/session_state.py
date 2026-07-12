"""
Session State — persistent state for the uCode terminal session.

Holds the shared grid, world registry, program memory, and vault
config so that commands like GRID, WORLD, LOAD, and RUN operate on
real mutable state instead of returning hardcoded strings.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Use shared models when udos_shared is installed; fall back to
# the pure-Python grid models in core_py/grid for development.
try:
    from udos_shared import Grid  # type: ignore
except ImportError:
    # In-repo fallback: add core_py to sys.path
    _core = Path(__file__).resolve().parent.parent / "core_py"
    if str(_core) not in sys.path:
        sys.path.insert(0, str(_core))
    from grid.models import Grid  # type: ignore


@dataclass
class WorldEntry:
    """Metadata about a created world."""
    name: str
    cols: int = 80
    rows: int = 24
    layers: int = 2
    description: str = ""


@dataclass
class SessionState:
    """Mutable session state shared by all dispatch_command calls."""

    # The live grid that GRID GET/SET operate on
    grid: Grid = field(default_factory=lambda: Grid(80, 24))

    # World registry
    worlds: Dict[str, WorldEntry] = field(default_factory=dict)

    # Active world name (if any)
    active_world: Optional[str] = None

    # Program memory — loaded BASIC source lines
    program_lines: Dict[int, str] = field(default_factory=dict)

    # Current program filename (for SAVE)
    program_filename: Optional[str] = None

    # Cached vault config
    vault_cache: Optional[Dict[str, Any]] = None

    # CWD for program discovery
    program_search_paths: List[Path] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Seed the default world so WORLD LIST always has something
        if "default" not in self.worlds:
            self.worlds["default"] = WorldEntry(
                name="default",
                cols=80,
                rows=24,
                layers=2,
                description="Default 80x24 world with 2 layers",
            )
            self.active_world = "default"

        # Default search paths
        if not self.program_search_paths:
            repo_root = Path(__file__).resolve().parents[3]
            programs_dir = repo_root / "programs"
            if programs_dir.exists():
                self.program_search_paths.append(programs_dir)

    # ── Grid helpers ──────────────────────────────────────────

    def grid_set(self, x: int, y: int, char: str) -> str:
        """Set a character on the active grid."""
        cell = self.grid.get(x, y)
        cell.char = char
        cell.data = char
        return f"Set ({x},{y}) to '{char}'"

    def grid_get(self, x: int, y: int) -> str:
        """Get the character at a grid position."""
        cell = self.grid.get(x, y)
        ch = cell.char if cell.char else " "
        return f"  ({x},{y}) = '{ch}'"

    def grid_render(self, region_x: int = 0, region_y: int = 0,
                    region_w: Optional[int] = None,
                    region_h: Optional[int] = None) -> str:
        """Render a region of the grid as ASCII (for terminal output)."""
        w = region_w if region_w is not None else min(self.grid.width, 40)
        h = region_h if region_h is not None else min(self.grid.height, 20)
        lines: List[str] = []
        for y in range(region_y, region_y + h):
            chars: List[str] = []
            for x in range(region_x, region_x + w):
                cell = self.grid.get(x, y)
                chars.append(cell.char if cell.char else " ")
            lines.append("".join(chars))
        return "\n".join(lines)

    # ── World helpers ─────────────────────────────────────────

    def world_create(self, name: str, cols: int = 80, rows: int = 24,
                     layers: int = 2) -> str:
        if name in self.worlds:
            return f"World '{name}' already exists."
        self.worlds[name] = WorldEntry(
            name=name, cols=cols, rows=rows, layers=layers,
            description=f"{cols}x{rows} world with {layers} layer(s)",
        )
        self.active_world = name
        return f"World '{name}' created with {layers} layer(s)."

    def world_list(self) -> str:
        if not self.worlds:
            return "  (no worlds)"
        lines = ["Worlds:"]
        for name, entry in self.worlds.items():
            marker = " *" if name == self.active_world else ""
            lines.append(f"  {name} ({entry.cols}x{entry.rows}, "
                         f"{entry.layers} layer(s)){marker}")
        return "\n".join(lines)

    def world_switch(self, name: str) -> str:
        if name not in self.worlds:
            return f"World '{name}' not found. Use WORLD LIST to see available worlds."
        self.active_world = name
        return f"Switched to world '{name}'."

    # ── Program helpers ───────────────────────────────────────

    def program_load(self, filename: str) -> str:
        """Load a .bbc program from the search paths into memory."""
        fpath = Path(filename)
        if not fpath.is_absolute():
            # Search in program_search_paths
            for base in self.program_search_paths:
                candidate = base / fpath
                if candidate.exists():
                    fpath = candidate
                    break
            else:
                # Also try relative to cwd
                candidate = Path(filename).resolve()
                if candidate.exists():
                    fpath = candidate
                else:
                    return f"Program not found: {filename}"

        try:
            source = fpath.read_text()
        except Exception as exc:
            return f"Error loading program: {exc}"

        self.program_lines.clear()
        self.program_filename = fpath.name
        for line in source.splitlines():
            stripped = line.strip()
            # BBC BASIC lines start with a line number
            parts = stripped.split(maxsplit=1)
            if parts and parts[0].isdigit():
                lineno = int(parts[0])
                self.program_lines[lineno] = stripped

        if not self.program_lines:
            # No line numbers found; store as raw lines
            for i, line in enumerate(source.splitlines(), 1):
                self.program_lines[i] = line

        return f"Loaded '{fpath.name}' ({len(self.program_lines)} lines)"

    def program_list(self, start: Optional[int] = None,
                     end: Optional[int] = None) -> str:
        """Return a formatted listing of the loaded program."""
        if not self.program_lines:
            return "No program loaded."

        sorted_lines = sorted(self.program_lines.items())
        if start is not None and end is not None:
            sorted_lines = [(l, t) for l, t in sorted_lines
                            if start <= l <= end]
        elif start is not None:
            sorted_lines = [(l, t) for l, t in sorted_lines if l >= start]

        if not sorted_lines:
            return "(no lines in range)"

        return "\n".join(f"{lno} {text}" for lno, text in sorted_lines)

    def program_cat(self) -> str:
        """List available programs under the search paths."""
        found: List[str] = []
        for base_dir in self.program_search_paths:
            if not base_dir.exists():
                continue
            for d in sorted(base_dir.iterdir()):
                if not d.is_dir() or d.name.startswith("."):
                    continue
                bbc_file = d / "src" / f"{d.name}.bbc"
                yaml_file = d / "program.yaml"
                if bbc_file.exists():
                    desc = ""
                    if yaml_file.exists():
                        try:
                            import yaml
                            with open(yaml_file) as fh:
                                meta = yaml.safe_load(fh) or {}
                            desc = meta.get("title", "")
                        except Exception:
                            pass
                    found.append(f"  {d.name}" +
                                 (f" — {desc}" if desc else ""))
        if not found:
            return "No programs found."
        return "Available programs:\n" + "\n".join(found)

    def renum(self, start: int = 10, step: int = 10) -> str:
        """Renumber program lines."""
        if not self.program_lines:
            return "No program loaded."

        old_lines = sorted(self.program_lines.items())
        new_lines: Dict[int, str] = {}
        renumber_map: Dict[int, int] = {}

        for i, (old_lineno, text) in enumerate(old_lines):
            new_lineno = start + i * step
            renumber_map[old_lineno] = new_lineno

        for old_lineno, text in old_lines:
            new_lineno = renumber_map[old_lineno]
            # Replace line number in text
            parts = text.split(maxsplit=1)
            if parts and parts[0].isdigit():
                new_text = f"{new_lineno} {parts[1]}" if len(parts) > 1 else str(new_lineno)
            else:
                new_text = text
            new_lines[new_lineno] = new_text

        self.program_lines = new_lines
        return f"Renumbered {len(new_lines)} lines (start={start}, step={step})"


# ── Singleton for the adapter ────────────────────────────────────

# The gridcore_adapter module uses this shared instance so that every
# dispatched command sees the same state.  A real multi-session server
# would scope SessionState per connection.

_default_session: Optional[SessionState] = None


def get_session() -> SessionState:
    """Return the default shared session, creating it on first access."""
    global _default_session
    if _default_session is None:
        _default_session = SessionState()
    return _default_session


def reset_session() -> SessionState:
    """Discard the current session and return a fresh one."""
    global _default_session
    _default_session = SessionState()
    return _default_session