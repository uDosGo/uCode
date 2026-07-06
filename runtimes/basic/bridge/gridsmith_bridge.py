"""
GridSmith Bridge — Python-side integration with the GridSmith Node CLI.

Provides a thin subprocess wrapper around `gridsmith` that exposes
the full set of GridSmith tools to the uCore Python backend
(gridsmith_api.py).
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class GridSmithResult:
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    stdout: str = ""
    stderr: str = ""


def _run_gridsmith(args: list[str], cwd: Optional[Path] = None) -> GridSmithResult:
    """Execute gridsmith CLI and return structured result."""
    try:
        result = subprocess.run(
            ["gridsmith", *args],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(cwd) if cwd else None,
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            return GridSmithResult(
                success=False,
                error=stderr or f"Exit code {result.returncode}",
                stderr=stderr,
            )

        try:
            data = json.loads(stdout) if stdout else {}
        except json.JSONDecodeError:
            data = {"raw": stdout}

        return GridSmithResult(success=True, data=data, stdout=stdout, stderr=stderr)

    except FileNotFoundError:
        return GridSmithResult(
            success=False,
            error="gridsmith CLI not found. Run: npm link (in agents/gridsmith)",
        )
    except subprocess.TimeoutExpired:
        return GridSmithResult(
            success=False,
            error="gridsmith command timed out after 30s",
        )


def list_tools() -> GridSmithResult:
    """List all available GridSmith tools."""
    return _run_gridsmith(["tools", "list"])


def create_world(
    name: str,
    world_type: str = "earth",
    cols: int = 80,
    rows: int = 24,
    seed: Optional[int] = None,
) -> GridSmithResult:
    """Create a new world."""
    args = [
        "world", "create",
        "--name", name,
        "--type", world_type,
        "--cols", str(cols),
        "--rows", str(rows),
    ]
    if seed is not None:
        args.extend(["--seed", str(seed)])
    return _run_gridsmith(args)


def create_grid(
    grid_id: str,
    cols: int = 80,
    rows: int = 24,
) -> GridSmithResult:
    """Create a named grid."""
    return _run_gridsmith([
        "grid", "create",
        "--grid-id", grid_id,
        "--cols", str(cols),
        "--rows", str(rows),
    ])


def edit_cell(
    grid_id: str,
    x: int,
    y: int,
    char: Optional[str] = None,
    fg: Optional[int] = None,
    bg: Optional[int] = None,
    layer: int = 0,
) -> GridSmithResult:
    """Edit a single cell."""
    args = [
        "cell", "edit",
        "--grid-id", grid_id,
        "--x", str(x),
        "--y", str(y),
        "--layer", str(layer),
    ]
    if char is not None:
        args.extend(["--char", char])
    if fg is not None:
        args.extend(["--fg", str(fg)])
    if bg is not None:
        args.extend(["--bg", str(bg)])
    return _run_gridsmith(args)


def compose_layers(
    grid_id: str,
    layers: Optional[list[int]] = None,
) -> GridSmithResult:
    """Compose layers into a single view."""
    layer_str = ",".join(str(ly) for ly in (layers or [0, 1, 2, 3, 4, 5]))
    return _run_gridsmith([
        "layers", "compose",
        "--grid-id", grid_id,
        "--layers", layer_str,
    ])


def export_uvox(grid_id: str, output_path: str) -> GridSmithResult:
    """Export grid as .uvox artifact."""
    return _run_gridsmith([
        "uvox", "export",
        "--grid-id", grid_id,
        "--output", output_path,
    ])


def find_path(
    grid_id: str,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    layer: int = 0,
) -> GridSmithResult:
    """Find path between two grid points."""
    return _run_gridsmith([
        "path", "find",
        "--grid-id", grid_id,
        "--start-x", str(start_x),
        "--start-y", str(start_y),
        "--end-x", str(end_x),
        "--end-y", str(end_y),
        "--layer", str(layer),
    ])


def convert_latlon_to_ucode(
    lat: float,
    lon: float,
    level: int = 340,
) -> GridSmithResult:
    """Convert latitude/longitude to uCode coordinate."""
    return _run_gridsmith([
        "location", "latlon-to-ucode",
        "--lat", str(lat),
        "--lon", str(lon),
        "--level", str(level),
    ])


def convert_ucode_to_latlon(coord: str) -> GridSmithResult:
    """Convert uCode coordinate to latitude/longitude."""
    return _run_gridsmith([
        "location", "ucode-to-latlon",
        "--coord", coord,
    ])


def import_basic(program: str, world_name: str) -> GridSmithResult:
    """Import a BASIC program as a world."""
    return _run_gridsmith([
        "world", "import-basic",
        "--program", program,
        "--world-name", world_name,
    ])


def import_amos(program: str, world_name: str) -> GridSmithResult:
    """Import an AMOS program as a world."""
    return _run_gridsmith([
        "world", "import-amos",
        "--program", program,
        "--world-name", world_name,
    ])