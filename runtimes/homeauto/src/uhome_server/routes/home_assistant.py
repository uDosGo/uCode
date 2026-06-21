"""Home Assistant bridge routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from uhome_server.config import get_repo_root
from uhome_server.services.home_assistant_service import get_ha_service
from uhome_server.workspace import get_template_workspace_service


class HACommandRequest(BaseModel):
    command: str
    params: dict[str, Any] = Field(default_factory=dict)


def create_ha_routes(auth_guard=None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/ha", tags=["home-assistant"])

    @router.get("/status")
    async def ha_status():
        workspace = get_template_workspace_service(get_repo_root())
        return {
            **get_ha_service().status(),
            "template_workspace": workspace.component_contract("uhome"),
            "template_workspace_state": workspace.component_snapshot("uhome"),
        }

    @router.get("/discover", dependencies=dependencies)
    async def ha_discover():
        svc = get_ha_service()
        if not svc.is_enabled():
            raise HTTPException(status_code=503, detail="Home Assistant bridge is disabled.")
        workspace = get_template_workspace_service(get_repo_root())
        return {
            **svc.discover(),
            "template_workspace": workspace.component_contract("uhome"),
            "template_workspace_state": workspace.component_snapshot("uhome"),
        }

    @router.post("/command", dependencies=dependencies)
    async def ha_command(payload: HACommandRequest):
        svc = get_ha_service()
        if not svc.is_enabled():
            raise HTTPException(status_code=503, detail="Home Assistant bridge is disabled.")
        try:
            result = svc.execute_command(payload.command, payload.params)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"success": True, "result": result}

    return router
