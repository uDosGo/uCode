"""REST API endpoints for the standalone Home Assistant gateway."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from uhome_server.config import get_logger, utc_now_iso_z
from uhome_server.services.home_assistant.gateway.manager import GatewayManager
from uhome_server.services.home_assistant.schemas.device import DeviceType

logger = get_logger("ha-rest-api")
router = APIRouter(prefix="/api/ha", tags=["home-assistant-gateway"])
_gateway_manager: GatewayManager | None = None


class ServiceCallRequest(BaseModel):
    domain: str
    service: str
    entity_ids: list[str]
    data: dict[str, Any] = Field(default_factory=dict)


def set_gateway_manager(manager: GatewayManager) -> None:
    global _gateway_manager
    _gateway_manager = manager


def get_gateway_manager() -> GatewayManager:
    if _gateway_manager is None:
        raise RuntimeError("Gateway manager not initialized")
    return _gateway_manager


@router.get("/status")
async def get_gateway_status() -> dict[str, Any]:
    manager = get_gateway_manager()
    status = manager.get_status()
    return {"success": True, "data": status.to_dict()}


@router.get("/health")
async def health_check() -> dict[str, Any]:
    manager = get_gateway_manager()
    status = manager.get_status()
    return {"healthy": status.connected, "status": status.status, "timestamp": utc_now_iso_z()}


@router.get("/discover")
async def discover_devices() -> dict[str, Any]:
    devices = await get_gateway_manager().discover_devices()
    return {"success": True, "data": {"devices": [device.to_dict() for device in devices], "count": len(devices)}}


@router.get("/devices")
async def list_devices(type_filter: DeviceType | None = Query(None), manufacturer: str | None = Query(None)) -> dict[str, Any]:
    devices = await get_gateway_manager().get_devices()
    if type_filter:
        devices = [device for device in devices if device.type == type_filter]
    if manufacturer:
        devices = [device for device in devices if device.manufacturer == manufacturer]
    return {"success": True, "data": {"devices": [device.to_dict() for device in devices], "count": len(devices)}}


@router.get("/devices/{device_id}")
async def get_device(device_id: str) -> dict[str, Any]:
    manager = get_gateway_manager()
    device = await manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    state = await manager.get_device_state(device_id)
    return {"success": True, "data": {"device": device.to_dict(), "state": state.to_dict() if state else None}}


@router.get("/entities")
async def list_entities(domain: str | None = Query(None), device_id: str | None = Query(None)) -> dict[str, Any]:
    entities = list(get_gateway_manager().entities.values())
    if domain:
        entities = [entity for entity in entities if entity.domain == domain]
    if device_id:
        entities = [entity for entity in entities if entity.device_id == device_id]
    return {"success": True, "data": {"entities": [entity.to_dict() for entity in entities], "count": len(entities)}}


@router.post("/services/{domain}/{service}")
async def call_service(domain: str, service: str, payload: ServiceCallRequest) -> dict[str, Any]:
    success = await get_gateway_manager().call_service(domain, service, payload.entity_ids, payload.data)
    return {"success": success, "data": {"domain": domain, "service": service}}
