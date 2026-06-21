"""Cloud Map — Geo-spatial map data, tile management, and layer composition."""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TileFormat(Enum):
    """Map tile image format."""
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"
    SVG = "svg"


class MapProjection(Enum):
    """Map projection type."""
    MERCATOR = "mercator"
    EQUIRECTANGULAR = "equirectangular"
    GNOMONIC = "gnomonic"


@dataclass
class GeoBounds:
    """Geographic bounding box."""
    north: float  # max latitude
    south: float  # min latitude
    east: float   # max longitude
    west: float   # min longitude

    def contains(self, lat: float, lon: float) -> bool:
        return (
            self.south <= lat <= self.north
            and self.west <= lon <= self.east
        )

    def center(self) -> Tuple[float, float]:
        return (
            (self.north + self.south) / 2,
            (self.east + self.west) / 2,
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "north": self.north,
            "south": self.south,
            "east": self.east,
            "west": self.west,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "GeoBounds":
        return cls(
            north=data["north"],
            south=data["south"],
            east=data["east"],
            west=data["west"],
        )


@dataclass
class MapTile:
    """A single map tile at a zoom level."""
    x: int
    y: int
    zoom: int
    format: TileFormat = TileFormat.PNG
    data: Optional[str] = None  # base64 encoded tile image
    bounds: Optional[GeoBounds] = None
    timestamp: float = field(default_factory=time.time)

    def tile_coords_to_latlon(self) -> Tuple[float, float]:
        """Convert tile coordinates to latitude/longitude (NW corner)."""
        n = 2.0 ** self.zoom
        lon = self.x / n * 360.0 - 180.0
        lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * self.y / n))))
        return lat, lon

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "zoom": self.zoom,
            "format": self.format.value,
            "data": self.data[:100] + "..." if self.data and len(self.data) > 100 else self.data,
            "bounds": self.bounds.to_dict() if self.bounds else None,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MapTile":
        return cls(
            x=data["x"],
            y=data["y"],
            zoom=data["zoom"],
            format=TileFormat(data.get("format", "png")),
            data=data.get("data"),
            bounds=GeoBounds.from_dict(data["bounds"]) if data.get("bounds") else None,
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class MapLayer:
    """A composable map layer (satellite, terrain, heatmap, etc.)."""
    name: str
    layer_type: str  # "base", "overlay", "heatmap", "traffic", "custom"
    visible: bool = True
    opacity: float = 1.0
    tiles: List[MapTile] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.layer_type,
            "visible": self.visible,
            "opacity": self.opacity,
            "tiles": [t.to_dict() for t in self.tiles],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MapLayer":
        layer = cls(
            name=data["name"],
            layer_type=data["type"],
            visible=data.get("visible", True),
            opacity=data.get("opacity", 1.0),
            metadata=data.get("metadata", {}),
        )
        layer.tiles = [MapTile.from_dict(t) for t in data.get("tiles", [])]
        return layer


class CloudMap:
    """Cloud-based geo-spatial map with tile management and layer composition."""

    def __init__(self, map_id: str, name: str) -> None:
        self.map_id = map_id
        self.name = name
        self._layers: Dict[str, MapLayer] = {}
        self._bounds: Optional[GeoBounds] = None
        self._center: Tuple[float, float] = (0.0, 0.0)
        self._zoom: int = 10
        self._projection: MapProjection = MapProjection.MERCATOR
        self._created: float = time.time()
        self._updated: float = time.time()

    @property
    def center(self) -> Tuple[float, float]:
        return self._center

    def set_center(self, lat: float, lon: float) -> None:
        self._center = (lat, lon)
        self._updated = time.time()

    @property
    def zoom(self) -> int:
        return self._zoom

    def set_zoom(self, zoom: int) -> None:
        self._zoom = max(0, min(zoom, 22))
        self._updated = time.time()

    @property
    def bounds(self) -> Optional[GeoBounds]:
        return self._bounds

    def set_bounds(self, bounds: GeoBounds) -> None:
        self._bounds = bounds
        self._updated = time.time()

    def add_layer(self, layer: MapLayer) -> None:
        self._layers[layer.name] = layer
        self._updated = time.time()

    def remove_layer(self, name: str) -> bool:
        if name in self._layers:
            del self._layers[name]
            self._updated = time.time()
            return True
        return False

    def get_layer(self, name: str) -> Optional[MapLayer]:
        return self._layers.get(name)

    def list_layers(self) -> List[MapLayer]:
        return list(self._layers.values())

    def add_tile(self, layer_name: str, tile: MapTile) -> bool:
        layer = self._layers.get(layer_name)
        if not layer:
            return False
        layer.tiles.append(tile)
        self._updated = time.time()
        return True

    def get_tiles_at_zoom(self, zoom: int) -> List[MapTile]:
        """Get all tiles at a specific zoom level across all layers."""
        tiles = []
        for layer in self._layers.values():
            for tile in layer.tiles:
                if tile.zoom == zoom:
                    tiles.append(tile)
        return tiles

    def latlon_to_tile(self, lat: float, lon: float, zoom: int) -> MapTile:
        """Convert lat/lon to tile coordinates."""
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.log(math.tan(math.radians(lat)) + 1.0 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n)
        return MapTile(x=x, y=y, zoom=zoom)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "map_id": self.map_id,
            "name": self.name,
            "center": list(self._center),
            "zoom": self._zoom,
            "projection": self._projection.value,
            "bounds": self._bounds.to_dict() if self._bounds else None,
            "layers": [l.to_dict() for l in self._layers.values()],
            "created": self._created,
            "updated": self._updated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CloudMap":
        cm = cls(
            map_id=data["map_id"],
            name=data["name"],
        )
        cm._center = tuple(data.get("center", [0.0, 0.0]))
        cm._zoom = data.get("zoom", 10)
        cm._projection = MapProjection(data.get("projection", "mercator"))
        cm._bounds = GeoBounds.from_dict(data["bounds"]) if data.get("bounds") else None
        cm._created = data.get("created", time.time())
        cm._updated = data.get("updated", time.time())
        for layer_data in data.get("layers", []):
            layer = MapLayer.from_dict(layer_data)
            cm._layers[layer.name] = layer
        return cm
