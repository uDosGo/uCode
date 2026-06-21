"""Gateway configuration and status schemas."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class GatewayConfigSchema:
    gateway_id: str
    name: str
    ha_url: str
    ha_token: str
    ws_enabled: bool = True
    rest_enabled: bool = True
    auto_discovery: bool = True
    discovery_interval: int = 60
    heartbeat_interval: int = 30
    max_connections: int = 100
    tls_enabled: bool = False
    tls_cert_path: str | None = None
    tls_key_path: str | None = None
    allowed_domains: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["ha_token"] = "***REDACTED***"
        return payload


@dataclass
class GatewayStatusSchema:
    status: str
    connected: bool = False
    uptime_seconds: int = 0
    total_devices: int = 0
    available_devices: int = 0
    total_entities: int = 0
    active_connections: int = 0
    last_heartbeat: str | None = None
    error_message: str | None = None
    version: str = "0.1.0"
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
