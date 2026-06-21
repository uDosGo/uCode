"""Device discovery and management for Home Assistant integration."""

from __future__ import annotations

import asyncio
from typing import Any

from uhome_server.config import get_logger

logger = get_logger("ha-device-manager")


class DeviceRegistry:
    def __init__(self):
        self.devices: dict[str, dict[str, Any]] = {}
        self.device_aliases: dict[str, str] = {}

    def register_device(self, device_id: str, device_info: dict[str, Any]) -> bool:
        try:
            self.devices[device_id] = device_info
            for alias in device_info.get("aliases", []):
                self.device_aliases[alias] = device_id
            return True
        except Exception as exc:
            logger.error("Device registration failed: %s", exc)
            return False

    def get_device(self, device_id_or_alias: str) -> dict[str, Any] | None:
        if device_id_or_alias in self.devices:
            return self.devices[device_id_or_alias]
        if device_id_or_alias in self.device_aliases:
            return self.devices.get(self.device_aliases[device_id_or_alias])
        return None


class DiscoveryService:
    def __init__(self, registry: DeviceRegistry):
        self.registry = registry

    async def discover_all(self) -> list[dict[str, Any]]:
        results = await asyncio.gather(
            self._udp_discovery(),
            self._mdns_discovery(),
            self._upnp_discovery(),
            self._ha_api_discovery(),
        )
        discovered: list[dict[str, Any]] = []
        for result in results:
            if isinstance(result, list):
                discovered.extend(result)
        return discovered

    async def _udp_discovery(self) -> list[dict[str, Any]]:
        return []

    async def _mdns_discovery(self) -> list[dict[str, Any]]:
        return []

    async def _upnp_discovery(self) -> list[dict[str, Any]]:
        return []

    async def _ha_api_discovery(self) -> list[dict[str, Any]]:
        return []


class DeviceController:
    def __init__(self, registry: DeviceRegistry):
        self.registry = registry

    async def turn_on_device(self, device_id: str, **kwargs) -> bool:
        return self.registry.get_device(device_id) is not None

    async def turn_off_device(self, device_id: str, **kwargs) -> bool:
        return self.registry.get_device(device_id) is not None


class DeviceMonitor:
    def __init__(self, registry: DeviceRegistry):
        self.registry = registry
        self.device_health: dict[str, dict[str, Any]] = {}

    async def check_device_health(self, device_id: str) -> dict[str, Any]:
        if not self.registry.get_device(device_id):
            return {"healthy": False, "reason": "Device not found"}
        health = {"healthy": True, "response_time_ms": 0, "signal_strength": -50, "last_seen": None}
        self.device_health[device_id] = health
        return health
