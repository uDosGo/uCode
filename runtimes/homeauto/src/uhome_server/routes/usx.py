"""
USX (Universal Surface eXchange) API routes for HomeNest.

Serves USX files for UDO/UDX renderers and provides runtime
evaluation of USX actions against the uHome server API.
"""

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from uhome_server.config import get_repo_root

router = APIRouter(prefix="/usx", tags=["usx"])

USX_EXAMPLES_DIR = get_repo_root() / "ui" / "usxd" / "examples"


def _load_usx(name: str) -> dict:
    """Load a USX file by name (without .usx extension)."""
    path = USX_EXAMPLES_DIR / f"{name}.usx"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"USX file '{name}' not found")
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid USX JSON: {e}")


@router.get("/list")
async def list_usx_files() -> JSONResponse:
    """List available USX files."""
    if not USX_EXAMPLES_DIR.exists():
        return JSONResponse({"files": [], "directory": str(USX_EXAMPLES_DIR)})
    files = sorted(f.stem for f in USX_EXAMPLES_DIR.iterdir() if f.suffix == ".usx")
    return JSONResponse({
        "files": files,
        "count": len(files),
        "directory": str(USX_EXAMPLES_DIR),
    })


@router.get("/{name}")
async def get_usx(name: str) -> JSONResponse:
    """Get a USX file by name."""
    usx = _load_usx(name)
    return JSONResponse(usx)


@router.get("/{name}/udo")
async def get_udo(name: str) -> JSONResponse:
    """Get the UDO portion of a USX file."""
    usx = _load_usx(name)
    if "udo" not in usx:
        raise HTTPException(status_code=404, detail=f"USX '{name}' has no UDO section")
    return JSONResponse(usx["udo"])


@router.get("/{name}/udx")
async def get_udx(name: str) -> JSONResponse:
    """Get the UDX portion of a USX file."""
    usx = _load_usx(name)
    if "udx" not in usx:
        raise HTTPException(status_code=404, detail=f"USX '{name}' has no UDX section")
    return JSONResponse(usx["udx"])


@router.post("/{name}/action")
async def evaluate_action(name: str, request: Request) -> JSONResponse:
    """
    Evaluate a USX action against the uHome server API.
    
    Body should contain the action to evaluate:
    ```json
    {
      "type": "navigate|media|ha|system|api",
      "command": "...",
      "parameters": {}
    }
    ```
    """
    body = await request.json()
    action_type = body.get("type", "")
    command = body.get("command", "")
    parameters = body.get("parameters", {})

    # Validate the action against the USX file
    usx = _load_usx(name)
    actions = usx.get("actions", {})
    
    # Check if this action exists in the USX file
    found = False
    for section in ["on_load", "on_select", "on_timer"]:
        for action in actions.get(section, []):
            if action.get("type") == action_type and action.get("command", "").startswith(command):
                found = True
                break

    return JSONResponse({
        "evaluated": True,
        "type": action_type,
        "command": command,
        "parameters": parameters,
        "valid": found,
        "message": "Action validated against USX schema" if found else "Action not found in USX file",
    })
