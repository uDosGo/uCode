"""Camera System — Viewport and camera control for 3D worlds."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Camera:
    """A camera with position, target, and view parameters."""

    name: str
    position: Tuple[float, float, float] = (0.0, 0.0, 10.0)
    target: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    up: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    fov: float = 60.0  # Field of view in degrees
    near: float = 0.1
    far: float = 1000.0
    camera_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def move_to(self, x: float, y: float, z: float) -> None:
        self.position = (x, y, z)

    def look_at(self, x: float, y: float, z: float) -> None:
        self.target = (x, y, z)

    def orbit(self, angle_deg: float, radius: float) -> None:
        """Orbit the camera around its target."""
        angle_rad = math.radians(angle_deg)
        cx, cy, cz = self.target
        self.position = (
            cx + radius * math.cos(angle_rad),
            cy,
            cz + radius * math.sin(angle_rad),
        )

    def zoom(self, factor: float) -> None:
        """Zoom camera toward target by factor (0-1 = zoom in, >1 = zoom out)."""
        cx, cy, cz = self.target
        px, py, pz = self.position
        self.position = (
            cx + (px - cx) * factor,
            cy + (py - cy) * factor,
            cz + (pz - cz) * factor,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "name": self.name,
            "position": list(self.position),
            "target": list(self.target),
            "up": list(self.up),
            "fov": self.fov,
            "near": self.near,
            "far": self.far,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Camera":
        return cls(
            name=data["name"],
            position=tuple(data.get("position", [0, 0, 10])),
            target=tuple(data.get("target", [0, 0, 0])),
            up=tuple(data.get("up", [0, 1, 0])),
            fov=data.get("fov", 60.0),
            near=data.get("near", 0.1),
            far=data.get("far", 1000.0),
            camera_id=data.get("camera_id", str(uuid.uuid4())),
        )


import uuid


class CameraSystem:
    """Manages cameras and viewport configuration."""

    def __init__(self) -> None:
        self._cameras: Dict[str, Camera] = {}
        self._active_camera_id: Optional[str] = None

    def create_camera(self, name: str, **kwargs: Any) -> Camera:
        camera = Camera(name=name, **kwargs)
        self._cameras[camera.camera_id] = camera
        if self._active_camera_id is None:
            self._active_camera_id = camera.camera_id
        return camera

    def get_camera(self, camera_id: str) -> Optional[Camera]:
        return self._cameras.get(camera_id)

    @property
    def active_camera(self) -> Optional[Camera]:
        if self._active_camera_id:
            return self._cameras.get(self._active_camera_id)
        return None

    def set_active(self, camera_id: str) -> bool:
        if camera_id in self._cameras:
            self._active_camera_id = camera_id
            return True
        return False

    def list_cameras(self) -> List[Camera]:
        return list(self._cameras.values())

    def delete_camera(self, camera_id: str) -> bool:
        if camera_id in self._cameras:
            del self._cameras[camera_id]
            if self._active_camera_id == camera_id:
                self._active_camera_id = next(iter(self._cameras), None)
            return True
        return False
