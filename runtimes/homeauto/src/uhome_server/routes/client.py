"""Client capability registration routes."""

from __future__ import annotations

from typing import Any, Callable, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from uhome_server.config import get_repo_root, utc_now_iso_z
from uhome_server.services.client_capability_service import get_client_capability_service


class ClientRegisterRequest(BaseModel):
    client_id: str = Field(..., description="Stable unique client identifier")
    device_name: str = Field(..., description="Friendly device name")
    platform: str = Field(..., description="Client platform, e.g. android, ios, tvos")
    os_version: str = Field(default="", description="Client OS version")
    app_version: str = Field(default="", description="Client app version")
    capability_profile: Literal["controller", "remote", "touch"] = Field(
        ..., description="Base capability profile"
    )
    capabilities: dict[str, Any] = Field(default_factory=dict, description="Extended capability map")


class ClientCapabilitiesUpdateRequest(BaseModel):
    capabilities: dict[str, Any] = Field(default_factory=dict, description="Partial capability updates")


def create_client_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/client", tags=["client"])
    svc = get_client_capability_service(get_repo_root())

    @router.post("/register")
    async def register_client(payload: ClientRegisterRequest) -> dict[str, Any]:
        try:
            result = svc.register(payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        result["timestamp"] = utc_now_iso_z()
        return result

    @router.get("")
    async def list_clients() -> dict[str, Any]:
        clients = svc.list_clients()
        return {
            "count": len(clients),
            "clients": clients,
            "timestamp": utc_now_iso_z(),
        }

    @router.get("/{client_id}")
    async def get_client(client_id: str) -> dict[str, Any]:
        client = svc.get_client(client_id)
        if client is None:
            raise HTTPException(status_code=404, detail=f"Client not found: {client_id}")
        return {
            "client": client,
            "timestamp": utc_now_iso_z(),
        }

    @router.post("/{client_id}/capabilities", dependencies=dependencies)
    async def update_client_capabilities(client_id: str, payload: ClientCapabilitiesUpdateRequest) -> dict[str, Any]:
        result = svc.update_capabilities(client_id, payload.capabilities)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Client not found: {client_id}")
        result["timestamp"] = utc_now_iso_z()
        return result

    return router
