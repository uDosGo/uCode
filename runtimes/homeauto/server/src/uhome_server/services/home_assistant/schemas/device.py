"""Device schema definitions for the Home Assistant gateway."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DeviceType(str, Enum):
    LIGHT = "light"
    SWITCH = "switch"
    TEMPLATE = "template"
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    CLIMATE = "climate"
    LOCK = "lock"
    COVER = "cover"
    CAMERA = "camera"
    MEDIA_PLAYER = "media_player"
    CUSTOM = "custom"


@dataclass
class DeviceSchema:
    id: str
    name: str
    type: DeviceType | str
    model: str
    manufacturer: str
    hw_version: str | None = None
    sw_version: str | None = None
    via_device_id: str | None = None
    suggested_area: str | None = None
    config_entries: list[str] = field(default_factory=list)
    connections: dict[str, str] = field(default_factory=dict)
    identifiers: list[tuple] = field(default_factory=list)
    disabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DeviceStateSchema:
    device_id: str
    is_available: bool = True
    last_seen: datetime | None = None
    last_updated: datetime | None = None
    state_attributes: dict[str, Any] = field(default_factory=dict)
    connection_status: str = "unknown"
    signal_strength: int | None = None
    battery_level: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.last_seen:
            payload["last_seen"] = self.last_seen.isoformat()
        if self.last_updated:
            payload["last_updated"] = self.last_updated.isoformat()
        return payload
