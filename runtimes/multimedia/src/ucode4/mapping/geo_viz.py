"""Geo Viz — Geo-spatial map visualization, heatmaps, and real-time device tracking."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class MapStyle(Enum):
    """Visual map style."""
    STREET = "street"
    SATELLITE = "satellite"
    TERRAIN = "terrain"
    DARK = "dark"
    LIGHT = "light"
    OUTDOORS = "outdoors"


@dataclass
class MapMarker:
    """A point marker on the map."""
    marker_id: str
    latitude: float
    longitude: float
    label: str = ""
    icon: str = "default"
    color: str = "#FF0000"
    size: int = 12
    device_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "marker_id": self.marker_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "label": self.label,
            "icon": self.icon,
            "color": self.color,
            "size": self.size,
            "device_id": self.device_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MapMarker":
        return cls(
            marker_id=data["marker_id"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            label=data.get("label", ""),
            icon=data.get("icon", "default"),
            color=data.get("color", "#FF0000"),
            size=data.get("size", 12),
            device_id=data.get("device_id"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class HeatmapPoint:
    """A weighted point for heatmap rendering."""
    latitude: float
    longitude: float
    weight: float = 1.0
    radius: int = 20

    def to_dict(self) -> Dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "weight": self.weight,
            "radius": self.radius,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HeatmapPoint":
        return cls(
            latitude=data["latitude"],
            longitude=data["longitude"],
            weight=data.get("weight", 1.0),
            radius=data.get("radius", 20),
        )


@dataclass
class GeoPath:
    """A path/route on the map."""
    path_id: str
    points: List[Tuple[float, float]] = field(default_factory=list)
    color: str = "#3388FF"
    width: int = 3
    opacity: float = 0.8
    label: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_point(self, lat: float, lon: float) -> None:
        self.points.append((lat, lon))

    def distance_km(self) -> float:
        """Calculate total path distance in km."""
        if len(self.points) < 2:
            return 0.0
        total = 0.0
        for i in range(1, len(self.points)):
            lat1, lon1 = math.radians(self.points[i - 1][0]), math.radians(self.points[i - 1][1])
            lat2, lon2 = math.radians(self.points[i][0]), math.radians(self.points[i][1])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            total += 6371 * c
        return total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path_id": self.path_id,
            "points": [[p[0], p[1]] for p in self.points],
            "color": self.color,
            "width": self.width,
            "opacity": self.opacity,
            "label": self.label,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeoPath":
        path = cls(
            path_id=data["path_id"],
            color=data.get("color", "#3388FF"),
            width=data.get("width", 3),
            opacity=data.get("opacity", 0.8),
            label=data.get("label", ""),
            metadata=data.get("metadata", {}),
        )
        path.points = [(p[0], p[1]) for p in data.get("points", [])]
        return path


class GeoViz:
    """Geo-spatial visualization engine for maps, markers, heatmaps, and tracking."""

    def __init__(self, map_id: str) -> None:
        self.map_id = map_id
        self._style: MapStyle = MapStyle.STREET
        self._markers: Dict[str, MapMarker] = {}
        self._heatmap_points: List[HeatmapPoint] = []
        self._paths: Dict[str, GeoPath] = {}
        self._center: Tuple[float, float] = (0.0, 0.0)
        self._zoom: int = 10
        self._pitch: float = 0.0
        self._bearing: float = 0.0

    @property
    def style(self) -> MapStyle:
        return self._style

    def set_style(self, style: MapStyle) -> None:
        self._style = style

    @property
    def center(self) -> Tuple[float, float]:
        return self._center

    def set_center(self, lat: float, lon: float) -> None:
        self._center = (lat, lon)

    @property
    def zoom(self) -> int:
        return self._zoom

    def set_zoom(self, zoom: int) -> None:
        self._zoom = max(0, min(22, zoom))

    def fly_to(self, lat: float, lon: float, zoom: int) -> None:
        """Animate camera to a location (simulated)."""
        self._center = (lat, lon)
        self._zoom = zoom

    # --- Markers ---

    def add_marker(self, marker: MapMarker) -> None:
        self._markers[marker.marker_id] = marker

    def remove_marker(self, marker_id: str) -> bool:
        if marker_id in self._markers:
            del self._markers[marker_id]
            return True
        return False

    def get_marker(self, marker_id: str) -> Optional[MapMarker]:
        return self._markers.get(marker_id)

    def list_markers(self) -> List[MapMarker]:
        return list(self._markers.values())

    def get_markers_by_device(self, device_id: str) -> List[MapMarker]:
        return [
            m for m in self._markers.values()
            if m.device_id == device_id
        ]

    # --- Heatmap ---

    def add_heatmap_point(self, point: HeatmapPoint) -> None:
        self._heatmap_points.append(point)

    def add_heatmap_points(self, points: List[HeatmapPoint]) -> None:
        self._heatmap_points.extend(points)

    def clear_heatmap(self) -> None:
        self._heatmap_points.clear()

    def get_heatmap_data(self) -> List[HeatmapPoint]:
        return self._heatmap_points

    def generate_heatmap_from_device_positions(
        self, positions: List[Tuple[float, float, float]]
    ) -> None:
        """Generate heatmap points from device positions with weights."""
        self._heatmap_points = [
            HeatmapPoint(latitude=lat, longitude=lon, weight=weight)
            for lat, lon, weight in positions
        ]

    # --- Paths ---

    def add_path(self, path: GeoPath) -> None:
        self._paths[path.path_id] = path

    def remove_path(self, path_id: str) -> bool:
        if path_id in self._paths:
            del self._paths[path_id]
            return True
        return False

    def get_path(self, path_id: str) -> Optional[GeoPath]:
        return self._paths.get(path_id)

    def list_paths(self) -> List[GeoPath]:
        return list(self._paths.values())

    # --- Real-time tracking ---

    def update_device_marker(
        self,
        device_id: str,
        lat: float,
        lon: float,
        label: str = "",
    ) -> MapMarker:
        """Update or create a marker for a tracked device."""
        existing = self.get_markers_by_device(device_id)
        if existing:
            marker = existing[0]
            marker.latitude = lat
            marker.longitude = lon
            return marker
        marker = MapMarker(
            marker_id=f"device_{device_id}",
            latitude=lat,
            longitude=lon,
            label=label or device_id[:8],
            device_id=device_id,
        )
        self.add_marker(marker)
        return marker

    def trace_device_path(
        self,
        device_id: str,
        path_id: str,
        lat: float,
        lon: float,
    ) -> GeoPath:
        """Add a point to a device's tracking path."""
        path = self._paths.get(path_id)
        if not path:
            path = GeoPath(
                path_id=path_id,
                label=f"Device {device_id[:8]} path",
                metadata={"device_id": device_id},
            )
            self.add_path(path)
        path.add_point(lat, lon)
        return path

    # --- Serialization ---

    def to_dict(self) -> Dict[str, Any]:
        return {
            "map_id": self.map_id,
            "style": self._style.value,
            "center": list(self._center),
            "zoom": self._zoom,
            "pitch": self._pitch,
            "bearing": self._bearing,
            "markers": [m.to_dict() for m in self._markers.values()],
            "heatmap": [p.to_dict() for p in self._heatmap_points],
            "paths": [p.to_dict() for p in self._paths.values()],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeoViz":
        viz = cls(map_id=data["map_id"])
        viz._style = MapStyle(data.get("style", "street"))
        viz._center = tuple(data.get("center", [0.0, 0.0]))
        viz._zoom = data.get("zoom", 10)
        viz._pitch = data.get("pitch", 0.0)
        viz._bearing = data.get("bearing", 0.0)
        for mdata in data.get("markers", []):
            marker = MapMarker.from_dict(mdata)
            viz._markers[marker.marker_id] = marker
        viz._heatmap_points = [HeatmapPoint.from_dict(p) for p in data.get("heatmap", [])]
        for pdata in data.get("paths", []):
            path = GeoPath.from_dict(pdata)
            viz._paths[path.path_id] = path
        return viz
