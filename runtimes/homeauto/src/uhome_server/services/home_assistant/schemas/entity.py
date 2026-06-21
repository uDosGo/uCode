"""Entity schema definitions for the Home Assistant gateway."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EntitySchema:
    entity_id: str
    device_id: str
    domain: str
    name: str
    unique_id: str
    platform: str
    icon: str | None = None
    entity_category: str | None = None
    has_entity_name: bool = False
    enabled_by_default: bool = True
    disabled: bool = False
    state_class: str | None = None
    unit_of_measurement: str | None = None
    suggested_display_precision: int | None = None
    capabilities: dict[str, Any] = field(default_factory=dict)
    options: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EntityStateSchema:
    entity_id: str
    state: str
    attributes: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
    last_changed: str | None = None
    last_updated: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
