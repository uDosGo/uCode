"""Household-safe browsing and status routes for living-room clients."""

from __future__ import annotations

from typing import Callable, Optional

from fastapi import APIRouter, Depends, Query

from uhome_server.config import get_repo_root, utc_now_iso_z
from uhome_server.services.household_service import get_household_service


def create_household_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    """Create household-safe API routes."""
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/household", tags=["household"])
    service = get_household_service(repo_root=get_repo_root())

    @router.get("/status", dependencies=dependencies)
    async def household_status():
        result = service.status()
        result["timestamp"] = utc_now_iso_z()
        return result

    @router.get("/browse", dependencies=dependencies)
    async def household_browse(
        q: str = Query("", description="Search query for household-safe browsing"),
        limit: int = Query(24, ge=1, le=100, description="Maximum number of items to return"),
    ):
        result = service.browse(query=q, limit=limit)
        result["timestamp"] = utc_now_iso_z()
        return result

    return router
