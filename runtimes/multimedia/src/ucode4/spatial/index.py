"""Spatial Index — Spatial query and neighbour resolution for 3D worlds."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SpatialQuery:
    """A spatial query for finding objects within bounds."""

    center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    radius: float = 10.0
    object_type: Optional[str] = None
    max_results: int = 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "center": list(self.center),
            "radius": self.radius,
            "object_type": self.object_type,
            "max_results": self.max_results,
        }


@dataclass
class SpatialEntity:
    """An entity with a spatial position."""

    entity_id: str
    position: Tuple[float, float, float]
    entity_type: str = "object"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def distance_to(self, other: SpatialEntity) -> float:
        return math.sqrt(
            (self.position[0] - other.position[0]) ** 2
            + (self.position[1] - other.position[1]) ** 2
            + (self.position[2] - other.position[2]) ** 2
        )

    def distance_to_point(self, point: Tuple[float, float, float]) -> float:
        return math.sqrt(
            (self.position[0] - point[0]) ** 2
            + (self.position[1] - point[1]) ** 2
            + (self.position[2] - point[2]) ** 2
        )


class SpatialIndex:
    """Spatial index for efficient neighbour queries."""

    def __init__(self) -> None:
        self._entities: Dict[str, SpatialEntity] = {}

    def add_entity(
        self,
        entity_id: str,
        position: Tuple[float, float, float],
        entity_type: str = "object",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SpatialEntity:
        entity = SpatialEntity(
            entity_id=entity_id,
            position=position,
            entity_type=entity_type,
            metadata=metadata or {},
        )
        self._entities[entity_id] = entity
        return entity

    def remove_entity(self, entity_id: str) -> bool:
        if entity_id in self._entities:
            del self._entities[entity_id]
            return True
        return False

    def update_position(self, entity_id: str, position: Tuple[float, float, float]) -> bool:
        entity = self._entities.get(entity_id)
        if entity:
            entity.position = position
            return True
        return False

    def query(self, query: SpatialQuery) -> List[SpatialEntity]:
        """Find entities within radius of center point."""
        results = []
        for entity in self._entities.values():
            if query.object_type and entity.entity_type != query.object_type:
                continue
            dist = entity.distance_to_point(query.center)
            if dist <= query.radius:
                results.append((dist, entity))

        results.sort(key=lambda x: x[0])
        return [e for _, e in results[: query.max_results]]

    def find_nearest(
        self,
        position: Tuple[float, float, float],
        entity_type: Optional[str] = None,
    ) -> Optional[SpatialEntity]:
        """Find the nearest entity to a position."""
        nearest: Optional[Tuple[float, SpatialEntity]] = None
        for entity in self._entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            dist = entity.distance_to_point(position)
            if nearest is None or dist < nearest[0]:
                nearest = (dist, entity)
        return nearest[1] if nearest else None

    def entities_in_bounds(
        self,
        min_pos: Tuple[float, float, float],
        max_pos: Tuple[float, float, float],
    ) -> List[SpatialEntity]:
        """Find entities within axis-aligned bounding box."""
        results = []
        for entity in self._entities.values():
            x, y, z = entity.position
            if (
                min_pos[0] <= x <= max_pos[0]
                and min_pos[1] <= y <= max_pos[1]
                and min_pos[2] <= z <= max_pos[2]
            ):
                results.append(entity)
        return results

    @property
    def count(self) -> int:
        return len(self._entities)

    def clear(self) -> None:
        self._entities.clear()
