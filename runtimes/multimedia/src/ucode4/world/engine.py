"""World Engine — Core 3D world creation and management."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Dimension:
    """A 3D dimension/world with spatial bounds."""

    name: str
    band: int  # Layer band (400-499 for dimensions, 700-799 for portals)
    width: float = 100.0
    height: float = 100.0
    depth: float = 100.0
    world_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def bounds(self) -> Dict[str, float]:
        return {"width": self.width, "height": self.height, "depth": self.depth}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "name": self.name,
            "band": self.band,
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dimension":
        return cls(
            name=data["name"],
            band=data["band"],
            width=data.get("width", 100.0),
            height=data.get("height", 100.0),
            depth=data.get("depth", 100.0),
            world_id=data.get("world_id", str(uuid.uuid4())),
            metadata=data.get("metadata", {}),
        )


@dataclass
class World:
    """A complete 3D world with scenes, objects, and state."""

    name: str
    dimension: Dimension
    world_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scenes: List[Dict[str, Any]] = field(default_factory=list)
    objects: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_scene(self, scene: Dict[str, Any]) -> None:
        self.scenes.append(scene)

    def add_object(self, obj: Dict[str, Any]) -> None:
        self.objects.append(obj)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "name": self.name,
            "dimension": self.dimension.to_dict(),
            "scenes": self.scenes,
            "objects": self.objects,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "World":
        world = cls(
            name=data["name"],
            dimension=Dimension.from_dict(data["dimension"]),
            world_id=data.get("world_id", str(uuid.uuid4())),
            metadata=data.get("metadata", {}),
        )
        world.scenes = data.get("scenes", [])
        world.objects = data.get("objects", [])
        return world


class WorldEngine:
    """Engine for creating, managing, and navigating 3D worlds."""

    def __init__(self) -> None:
        self._worlds: Dict[str, World] = {}

    def create_world(
        self,
        name: str,
        band: int = 400,
        width: float = 100.0,
        height: float = 100.0,
        depth: float = 100.0,
    ) -> World:
        """Create a new 3D world."""
        dimension = Dimension(
            name=f"{name}_dimension",
            band=band,
            width=width,
            height=height,
            depth=depth,
        )
        world = World(name=name, dimension=dimension)
        self._worlds[world.world_id] = world
        return world

    def get_world(self, world_id: str) -> Optional[World]:
        return self._worlds.get(world_id)

    def list_worlds(self) -> List[World]:
        return list(self._worlds.values())

    def delete_world(self, world_id: str) -> bool:
        if world_id in self._worlds:
            del self._worlds[world_id]
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worlds": {wid: w.to_dict() for wid, w in self._worlds.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldEngine":
        engine = cls()
        for wid, wdata in data.get("worlds", {}).items():
            engine._worlds[wid] = World.from_dict(wdata)
        return engine
