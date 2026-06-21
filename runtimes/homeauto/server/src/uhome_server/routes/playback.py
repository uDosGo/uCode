"""Playback status and handoff routes for living-room clients."""

from __future__ import annotations

from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from uhome_server.config import get_repo_root, utc_now_iso_z
from uhome_server.services.playback_service import get_playback_service


class PlaybackHandoffRequest(BaseModel):
    """Request to hand off playback to a target client."""

    item_id: str = Field(..., description="Media item ID to play")
    target_client: Optional[str] = Field(None, description="Target client name (optional, uses default if not set)")
    params: Optional[dict[str, Any]] = Field(None, description="Additional playback parameters")


def create_playback_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    """Create playback API routes."""
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/playback", tags=["playback"])
    repo_root = get_repo_root()
    playback = get_playback_service(repo_root)

    @router.get("/status")
    async def get_status():
        """Get current playback status including active Jellyfin sessions."""
        result = playback.get_status()
        result["timestamp"] = utc_now_iso_z()
        return result

    @router.post("/handoff", dependencies=dependencies)
    async def handoff(request: PlaybackHandoffRequest):
        """Queue a playback handoff to a target client."""
        result = playback.handoff(
            item_id=request.item_id,
            target_client=request.target_client,
            params=request.params,
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Handoff failed"))
        result["timestamp"] = utc_now_iso_z()
        return result

    @router.get("/queue")
    async def get_queue():
        """Get the current playback queue."""
        queue = playback.get_queue()
        return {
            "queue": queue,
            "count": len(queue),
            "timestamp": utc_now_iso_z(),
        }

    @router.delete("/queue", dependencies=dependencies)
    async def clear_queue():
        """Clear the playback queue."""
        result = playback.clear_queue()
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to clear queue"))
        result["timestamp"] = utc_now_iso_z()
        return result

    return router
