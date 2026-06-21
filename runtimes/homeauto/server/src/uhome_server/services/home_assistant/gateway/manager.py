"""Home Assistant REST/WebSocket gateway manager."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable

from uhome_server.config import get_logger
from uhome_server.services.home_assistant.schemas.device import DeviceSchema, DeviceStateSchema
from uhome_server.services.home_assistant.schemas.entity import EntitySchema, EntityStateSchema
from uhome_server.services.home_assistant.schemas.gateway import GatewayConfigSchema, GatewayStatusSchema

logger = get_logger("ha-gateway-manager")


class GatewayManager:
    def __init__(self, config: GatewayConfigSchema):
        self.config = config
        self.status = GatewayStatusSchema(status="initializing")
        self.devices: dict[str, DeviceSchema] = {}
        self.device_states: dict[str, DeviceStateSchema] = {}
        self.entities: dict[str, EntitySchema] = {}
        self.entity_states: dict[str, EntityStateSchema] = {}
        self._event_handlers: dict[str, list[Callable]] = {
            "device_discovered": [],
            "state_changed": [],
        }
        self._ha_client = None
        self._discovery_task = None
        self._heartbeat_task = None
        self.start_time = datetime.now()

    async def initialize(self) -> bool:
        try:
            self._ha_client = await self._create_ha_client()
            await self._test_connection()
            self.status.connected = True
            self.status.status = "running"
            if self.config.auto_discovery:
                self._discovery_task = asyncio.create_task(self._discovery_loop())
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            return True
        except Exception as exc:
            logger.error("Failed to initialize gateway: %s", exc)
            self.status.status = "error"
            self.status.error_message = str(exc)
            return False

    async def shutdown(self) -> None:
        if self._discovery_task:
            self._discovery_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._ha_client:
            await self._ha_client.close()
        self.status.connected = False
        self.status.status = "stopped"

    async def discover_devices(self) -> list[DeviceSchema]:
        devices = await self._ha_client.get_devices()
        discovered: list[DeviceSchema] = []
        for device_data in devices:
            device = DeviceSchema(
                id=device_data.get("id"),
                name=device_data.get("name", "Unknown"),
                type=device_data.get("type", "custom"),
                model=device_data.get("model", ""),
                manufacturer=device_data.get("manufacturer", ""),
                hw_version=device_data.get("hw_version"),
                sw_version=device_data.get("sw_version"),
                via_device_id=device_data.get("via_device_id"),
                suggested_area=device_data.get("suggested_area"),
                config_entries=device_data.get("config_entries", []),
                connections=device_data.get("connections", {}),
                identifiers=device_data.get("identifiers", []),
            )
            self.devices[device.id] = device
            self._emit_event("device_discovered", device)
            discovered.append(device)
        self.status.total_devices = len(self.devices)
        return discovered

    async def get_device(self, device_id: str) -> DeviceSchema | None:
        return self.devices.get(device_id)

    async def get_devices(self) -> list[DeviceSchema]:
        return list(self.devices.values())

    async def get_device_state(self, device_id: str) -> DeviceStateSchema | None:
        return self.device_states.get(device_id)

    async def get_entity_state(self, entity_id: str) -> EntityStateSchema | None:
        return self.entity_states.get(entity_id)

    async def call_service(self, domain: str, service: str, entity_ids: list[str], data: dict[str, Any]) -> bool:
        result = await self._ha_client.call_service(domain, service, entity_ids=entity_ids, data=data)
        return result.get("success", False)

    def on_event(self, event_type: str, handler: Callable) -> None:
        if event_type in self._event_handlers:
            self._event_handlers[event_type].append(handler)

    def get_status(self) -> GatewayStatusSchema:
        self.status.uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
        self.status.active_connections = len([state for state in self.device_states.values() if state.is_available])
        self.status.available_devices = self.status.active_connections
        self.status.total_entities = len(self.entities)
        return self.status

    async def _create_ha_client(self):
        return MockHAClient(self.config)

    async def _test_connection(self) -> bool:
        await self._ha_client.get_config()
        return True

    async def _discovery_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self.config.discovery_interval)
                await self.discover_devices()
            except asyncio.CancelledError:
                break

    async def _heartbeat_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                self.status.last_heartbeat = datetime.now().isoformat()
            except asyncio.CancelledError:
                break

    def _emit_event(self, event_type: str, data: Any) -> None:
        for handler in self._event_handlers.get(event_type, []):
            if asyncio.iscoroutinefunction(handler):
                asyncio.create_task(handler(data))
            else:
                handler(data)


class MockHAClient:
    def __init__(self, config: GatewayConfigSchema):
        self.config = config

    async def get_config(self) -> dict[str, Any]:
        return {"location_name": "Home"}

    async def get_devices(self) -> list[dict[str, Any]]:
        return []

    async def call_service(self, domain: str, service: str, entity_ids: list[str], data: dict[str, Any]) -> dict[str, Any]:
        return {"success": True}

    async def close(self) -> None:
        return None
