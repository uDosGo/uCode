"""Portal System — Inter-map gateways between dimensions (L700-L799)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Portal:
    """A gateway connecting two locations across dimensions."""

    name: str
    source_world_id: str
    target_world_id: str
    source_position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    target_position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    portal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    bidirectional: bool = True
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "portal_id": self.portal_id,
            "name": self.name,
            "source_world_id": self.source_world_id,
            "target_world_id": self.target_world_id,
            "source_position": list(self.source_position),
            "target_position": list(self.target_position),
            "bidirectional": self.bidirectional,
            "active": self.active,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Portal":
        return cls(
            name=data["name"],
            source_world_id=data["source_world_id"],
            target_world_id=data["target_world_id"],
            source_position=tuple(data.get("source_position", [0, 0, 0])),
            target_position=tuple(data.get("target_position", [0, 0, 0])),
            portal_id=data.get("portal_id", str(uuid.uuid4())),
            bidirectional=data.get("bidirectional", True),
            active=data.get("active", True),
            metadata=data.get("metadata", {}),
        )


class PortalSystem:
    """Manages portals connecting worlds and dimensions."""

    def __init__(self) -> None:
        self._portals: Dict[str, Portal] = {}

    def create_portal(
        self,
        name: str,
        source_world_id: str,
        target_world_id: str,
        source_position: Tuple[float, float, float] = (0, 0, 0),
        target_position: Tuple[float, float, float] = (0, 0, 0),
    ) -> Portal:
        portal = Portal(
            name=name,
            source_world_id=source_world_id,
            target_world_id=target_world_id,
            source_position=source_position,
            target_position=target_position,
        )
        self._portals[portal.portal_id] = portal
        return portal

    def get_portal(self, portal_id: str) -> Optional[Portal]:
        return self._portals.get(portal_id)

    def find_portals_for_world(self, world_id: str) -> List[Portal]:
        return [
            p
            for p in self._portals.values()
            if p.source_world_id == world_id or (p.bidirectional and p.target_world_id == world_id)
        ]

    def list_portals(self) -> List[Portal]:
        return list(self._portals.values())

    def delete_portal(self, portal_id: str) -> bool:
        if portal_id in self._portals:
            del self._portals[portal_id]
            return True
        return False

    def traverse(self, portal_id: str, current_world_id: str) -> Optional[Dict[str, Any]]:
        """Traverse a portal from the current world to the connected world."""
        portal = self._portals.get(portal_id)
        if not portal or not portal.active:
            return None

        if portal.source_world_id == current_world_id:
            return {
                "target_world_id": portal.target_world_id,
                "target_position": portal.target_position,
                "portal_name": portal.name,
            }
        elif portal.bidirectional and portal.target_world_id == current_world_id:
            return {
                "target_world_id": portal.source_world_id,
                "target_position": portal.source_position,
                "portal_name": portal.name,
            }
        return None
