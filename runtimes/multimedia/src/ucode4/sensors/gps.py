"""GPS Location Tracking Module."""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class GPSLocation:
    """A GPS coordinate with timestamp."""
    latitude: float
    longitude: float
    altitude: float = 0.0
    accuracy: float = 0.0
    speed: float = 0.0
    heading: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "accuracy": self.accuracy,
            "speed": self.speed,
            "heading": self.heading,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GPSLocation":
        return cls(
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data.get("altitude", 0.0),
            accuracy=data.get("accuracy", 0.0),
            speed=data.get("speed", 0.0),
            heading=data.get("heading", 0.0),
            timestamp=data.get("timestamp", time.time()),
        )

    def distance_to(self, other: "GPSLocation") -> float:
        """Haversine distance in meters."""
        R = 6371000  # Earth radius in meters
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c


class GPSTracker:
    """Tracks GPS location history and provides location-based services."""

    def __init__(self) -> None:
        self._locations: List[GPSLocation] = []
        self._current: Optional[GPSLocation] = None

    @property
    def current(self) -> Optional[GPSLocation]:
        return self._current

    def update(self, location: GPSLocation) -> None:
        self._current = location
        self._locations.append(location)
        # Keep last 1000 points
        if len(self._locations) > 1000:
            self._locations = self._locations[-1000:]

    def get_history(self, limit: int = 100) -> List[GPSLocation]:
        return self._locations[-limit:]

    def get_track(self) -> List[Tuple[float, float]]:
        return [(loc.latitude, loc.longitude) for loc in self._locations]

    def total_distance(self) -> float:
        if len(self._locations) < 2:
            return 0.0
        total = 0.0
        for i in range(1, len(self._locations)):
            total += self._locations[i - 1].distance_to(self._locations[i])
        return total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current": self._current.to_dict() if self._current else None,
            "history": [loc.to_dict() for loc in self._locations[-100:]],
            "total_distance": self.total_distance(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GPSTracker":
        tracker = cls()
        if data.get("current"):
            tracker._current = GPSLocation.from_dict(data["current"])
        tracker._locations = [GPSLocation.from_dict(loc) for loc in data.get("history", [])]
        return tracker
