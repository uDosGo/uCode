"""Device Registry — MeshCore device registration, status tracking, and discovery."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class DeviceStatus(Enum):
    """Device connection status."""
    OFFLINE = "offline"
    ONLINE = "online"
    SLEEPING = "sleeping"
    ERROR = "error"
    UNKNOWN = "unknown"


class DeviceCapability(Enum):
    """Device hardware capabilities."""
    GPS = "gps"
    CAMERA = "camera"
    MOTION = "motion"
    DISPLAY = "display"
    AUDIO = "audio"
    MESH = "mesh"
    LORA = "lora"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"


@dataclass
class DeviceInfo:
    """Information about a registered device."""
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    device_type: str = "mobile"  # "mobile", "gateway", "sensor", "display", "custom"
    status: DeviceStatus = DeviceStatus.UNKNOWN
    capabilities: List[DeviceCapability] = field(default_factory=list)
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # lat, lon, alt
    last_seen: float = field(default_factory=time.time)
    firmware_version: str = "0.0.0"
    battery_level: float = 100.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type,
            "status": self.status.value,
            "capabilities": [c.value for c in self.capabilities],
            "location": list(self.location),
            "last_seen": self.last_seen,
            "firmware_version": self.firmware_version,
            "battery_level": self.battery_level,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceInfo":
        return cls(
            device_id=data.get("device_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            device_type=data.get("device_type", "mobile"),
            status=DeviceStatus(data.get("status", "unknown")),
            capabilities=[DeviceCapability(c) for c in data.get("capabilities", [])],
            location=tuple(data.get("location", [0.0, 0.0, 0.0])),
            last_seen=data.get("last_seen", time.time()),
            firmware_version=data.get("firmware_version", "0.0.0"),
            battery_level=data.get("battery_level", 100.0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class DeviceGroup:
    """A group of devices for collective management."""
    group_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    device_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "name": self.name,
            "device_ids": self.device_ids,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceGroup":
        return cls(
            group_id=data.get("group_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            device_ids=data.get("device_ids", []),
            metadata=data.get("metadata", {}),
        )


class DeviceRegistry:
    """Registry for managing MeshCore devices and their state."""

    def __init__(self) -> None:
        self._devices: Dict[str, DeviceInfo] = {}
        self._groups: Dict[str, DeviceGroup] = {}

    # --- Device management ---

    def register_device(self, device: DeviceInfo) -> DeviceInfo:
        """Register a new device in the registry."""
        self._devices[device.device_id] = device
        return device

    def unregister_device(self, device_id: str) -> bool:
        """Remove a device from the registry."""
        if device_id in self._devices:
            del self._devices[device_id]
            # Remove from all groups
            for group in self._groups.values():
                if device_id in group.device_ids:
                    group.device_ids.remove(device_id)
            return True
        return False

    def get_device(self, device_id: str) -> Optional[DeviceInfo]:
        return self._devices.get(device_id)

    def list_devices(self, status: Optional[DeviceStatus] = None) -> List[DeviceInfo]:
        if status:
            return [d for d in self._devices.values() if d.status == status]
        return list(self._devices.values())

    def update_device_status(self, device_id: str, status: DeviceStatus) -> bool:
        device = self._devices.get(device_id)
        if not device:
            return False
        device.status = status
        device.last_seen = time.time()
        return True

    def update_device_location(
        self, device_id: str, location: Tuple[float, float, float]
    ) -> bool:
        device = self._devices.get(device_id)
        if not device:
            return False
        device.location = location
        device.last_seen = time.time()
        return True

    def update_device_battery(self, device_id: str, level: float) -> bool:
        device = self._devices.get(device_id)
        if not device:
            return False
        device.battery_level = max(0.0, min(100.0, level))
        device.last_seen = time.time()
        return True

    def get_online_devices(self) -> List[DeviceInfo]:
        return [d for d in self._devices.values() if d.status == DeviceStatus.ONLINE]

    def get_devices_by_capability(self, capability: DeviceCapability) -> List[DeviceInfo]:
        return [
            d for d in self._devices.values()
            if capability in d.capabilities
        ]

    def get_devices_in_radius(
        self,
        center: Tuple[float, float],
        radius_km: float,
    ) -> List[DeviceInfo]:
        """Find devices within a geographic radius."""
        from math import asin, cos, radians, sin, sqrt

        results = []
        lat_c, lon_c = radians(center[0]), radians(center[1])

        for device in self._devices.values():
            lat_d, lon_d = radians(device.location[0]), radians(device.location[1])
            dlat = lat_d - lat_c
            dlon = lon_d - lon_c
            a = sin(dlat / 2) ** 2 + cos(lat_c) * cos(lat_d) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            dist_km = 6371 * c  # Earth radius in km

            if dist_km <= radius_km:
                results.append(device)

        return results

    # --- Group management ---

    def create_group(self, name: str) -> DeviceGroup:
        group = DeviceGroup(name=name)
        self._groups[group.group_id] = group
        return group

    def delete_group(self, group_id: str) -> bool:
        if group_id in self._groups:
            del self._groups[group_id]
            return True
        return False

    def add_device_to_group(self, device_id: str, group_id: str) -> bool:
        group = self._groups.get(group_id)
        if not group or device_id not in self._devices:
            return False
        if device_id not in group.device_ids:
            group.device_ids.append(device_id)
        return True

    def remove_device_from_group(self, device_id: str, group_id: str) -> bool:
        group = self._groups.get(group_id)
        if not group:
            return False
        if device_id in group.device_ids:
            group.device_ids.remove(device_id)
            return True
        return False

    def get_group(self, group_id: str) -> Optional[DeviceGroup]:
        return self._groups.get(group_id)

    def list_groups(self) -> List[DeviceGroup]:
        return list(self._groups.values())

    def get_devices_in_group(self, group_id: str) -> List[DeviceInfo]:
        group = self._groups.get(group_id)
        if not group:
            return []
        return [
            self._devices[did] for did in group.device_ids
            if did in self._devices
        ]

    # --- Serialization ---

    def to_dict(self) -> Dict[str, Any]:
        return {
            "devices": {did: d.to_dict() for did, d in self._devices.items()},
            "groups": {gid: g.to_dict() for gid, g in self._groups.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceRegistry":
        registry = cls()
        for did, ddata in data.get("devices", {}).items():
            registry._devices[did] = DeviceInfo.from_dict(ddata)
        for gid, gdata in data.get("groups", {}).items():
            registry._groups[gid] = DeviceGroup.from_dict(gdata)
        return registry
