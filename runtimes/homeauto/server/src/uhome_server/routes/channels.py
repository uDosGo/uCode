"""Channel API routes — local streaming channel list, gateway, and session lifecycle."""

from __future__ import annotations

from typing import Any, Callable, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from uhome_server.config import utc_now_iso_z
from uhome_server.services.channel_service import get_channel_service


class CreateSessionRequest(BaseModel):
    room: str = Field(..., description="Room name for this playback session")
    channel_id: str = Field(..., description="Channel to tune to")
    device_id: Optional[str] = Field(None, description="Initiating device ID (optional)")


class JoinSessionRequest(BaseModel):
    device_id: str = Field(..., description="Device joining the session")


class MoveSessionRequest(BaseModel):
    target_room: str = Field(..., description="Room to move the session to")


def create_channel_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    """Create channel API routes."""
    dependencies = []
    router = APIRouter(prefix="/api/channels", tags=["channels"])
    svc = get_channel_service()

    @router.get("")
    async def list_channels() -> dict[str, Any]:
        """List all registered channel sources."""
        return {
            "channels": svc.list_channels(),
            "count": len(svc.list_channels()),
            "timestamp": utc_now_iso_z(),
        }

    @router.get("/{channel_id}")
    async def get_channel(channel_id: str) -> dict[str, Any]:
        """Get metadata for a single channel."""
        channel = svc.get_channel(channel_id)
        if channel is None:
            raise HTTPException(status_code=404, detail=f"Channel not found: {channel_id}")
        return {"channel": channel, "timestamp": utc_now_iso_z()}

    @router.get("/{channel_id}/gateway")
    async def get_gateway(channel_id: str, mode: Optional[str] = None) -> dict[str, Any]:
        """Resolve the gateway mode and endpoint for a channel.

        Pass ?mode=audio-first for audio-priority clients (phones in background, etc).
        """
        result = svc.resolve_gateway(channel_id, client_hint=mode)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        result["timestamp"] = utc_now_iso_z()
        return result

    @router.get("/sessions/active")
    async def list_sessions() -> dict[str, Any]:
        """List all active channel sessions."""
        sessions = svc.list_sessions()
        return {"sessions": sessions, "count": len(sessions), "timestamp": utc_now_iso_z()}

    @router.post("/sessions")
    async def create_session(request: CreateSessionRequest) -> dict[str, Any]:
        """Create a new channel session for a room."""
        session = svc.create_session(request.room, request.channel_id, request.device_id)
        if session is None:
            raise HTTPException(status_code=404, detail=f"Unknown channel: {request.channel_id}")
        return {"session": session, "timestamp": utc_now_iso_z()}

    @router.get("/sessions/{session_id}")
    async def get_session(session_id: str) -> dict[str, Any]:
        """Get current state of a session."""
        session = svc.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
        return {"session": session, "timestamp": utc_now_iso_z()}

    @router.get("/sessions/{session_id}/sync")
    async def sync_session(session_id: str) -> dict[str, Any]:
        """Return session + channel state for sync clients."""
        result = svc.sync_session(session_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
        result["timestamp"] = utc_now_iso_z()
        return result

    @router.post("/sessions/{session_id}/join")
    async def join_session(session_id: str, request: JoinSessionRequest) -> dict[str, Any]:
        """Add a device to an existing session."""
        session = svc.join_session(session_id, request.device_id)
        if session is None:
            raise HTTPException(status_code=404, detail=f"Session not found or ended: {session_id}")
        return {"session": session, "timestamp": utc_now_iso_z()}

    @router.post("/sessions/{session_id}/resume")
    async def resume_session(session_id: str) -> dict[str, Any]:
        """Resume a paused session."""
        session = svc.resume_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail=f"Session not found or ended: {session_id}")
        return {"session": session, "timestamp": utc_now_iso_z()}

    @router.post("/sessions/{session_id}/pause")
    async def pause_session(session_id: str) -> dict[str, Any]:
        """Pause an active session."""
        session = svc.pause_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail=f"Session not found or ended: {session_id}")
        return {"session": session, "timestamp": utc_now_iso_z()}

    @router.post("/sessions/{session_id}/move")
    async def move_session(session_id: str, request: MoveSessionRequest) -> dict[str, Any]:
        """Move a session to a different room."""
        session = svc.move_session(session_id, request.target_room)
        if session is None:
            raise HTTPException(status_code=404, detail=f"Session not found or ended: {session_id}")
        return {"session": session, "timestamp": utc_now_iso_z()}

    @router.delete("/sessions/{session_id}")
    async def end_session(session_id: str) -> dict[str, Any]:
        """End a session and remove it from active listings."""
        ended = svc.end_session(session_id)
        if not ended:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
        return {"success": True, "session_id": session_id, "timestamp": utc_now_iso_z()}

    return router
