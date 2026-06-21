"""First-class REST API routes for launcher/session management."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from uhome_server.config import get_repo_root
from uhome_server.services.uhome_presentation_service import (
    get_uhome_presentation_service,
)


class LauncherStartRequest(BaseModel):
    """Request to start a launcher presentation session."""

    presentation: Optional[str] = None
    """Presentation mode (thin-gui, steam-console). Uses default if not specified."""


class LauncherResponse(BaseModel):
    """Response for launcher operations."""

    status: str
    """Status of the launcher operation (e.g., 'started', 'stopped')."""

    active_presentation: Optional[str] = None
    """Currently active presentation, if any."""

    session_id: Optional[str] = None
    """Session ID for tracking, if available."""


def create_launcher_routes(auth_guard=None) -> APIRouter:
    """Create first-class launcher/session REST API routes."""
    del auth_guard  # Reserved for future authentication
    router = APIRouter(prefix="/api/launcher", tags=["launcher"])
    repo_root = get_repo_root()
    presentation_svc = get_uhome_presentation_service(repo_root=repo_root)

    @router.get("/status")
    async def get_launcher_status():
        """
        Get current launcher session status.

        Returns:
            Current launcher state including active presentation,
            supported modes, node role, and session metadata.
        """
        return presentation_svc.get_status()

    @router.get("/menu")
    async def get_launcher_menu():
        """Get a console-friendly action menu for launcher and stream controls."""
        return presentation_svc.get_console_menu()

    @router.post("/start")
    async def start_launcher_session(payload: LauncherStartRequest):
        """
        Start a new launcher presentation session.

        Args:
            payload: Request containing optional presentation mode.

        Returns:
            Session state including active presentation and configuration.

        Raises:
            HTTPException (400): If the requested presentation is invalid.
        """
        try:
            state = presentation_svc.start(payload.presentation or "")
            return {
                "status": "started",
                "active_presentation": state.get("active_presentation"),
                "node_role": state.get("node_role"),
                "updated_at": state.get("updated_at"),
                "session_id": state.get("session_id"),
            }
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/stop")
    async def stop_launcher_session():
        """
        Stop the currently running launcher session.

        Returns:
            Updated session state with active presentation set to None.
        """
        state = presentation_svc.stop()
        return {
            "status": "stopped",
            "active_presentation": state.get("active_presentation"),
            "node_role": state.get("node_role"),
            "updated_at": state.get("updated_at"),
        }

    return router
