"""Camera Integration Module — Mobile camera capture and processing."""

from __future__ import annotations

import base64
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CameraMode(Enum):
    PHOTO = "photo"
    VIDEO = "video"
    STREAM = "stream"
    QR_SCAN = "qr_scan"
    AR = "ar"


@dataclass
class CameraFrame:
    """A single camera frame."""
    data: str  # base64 encoded image
    width: int
    height: int
    format: str = "jpeg"
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data[:100] + "..." if len(self.data) > 100 else self.data,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class CameraConfig:
    """Camera configuration."""
    mode: CameraMode = CameraMode.PHOTO
    resolution: str = "1920x1080"
    fps: int = 30
    flash: bool = False
    zoom: float = 1.0
    focus_mode: str = "auto"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "resolution": self.resolution,
            "fps": self.fps,
            "flash": self.flash,
            "zoom": self.zoom,
            "focus_mode": self.focus_mode,
        }


class CameraController:
    """Controls mobile camera for AR, QR scanning, and photo capture."""

    def __init__(self) -> None:
        self._config = CameraConfig()
        self._frames: List[CameraFrame] = []
        self._is_active = False

    @property
    def config(self) -> CameraConfig:
        return self._config

    def update_config(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    def capture_frame(self, data: str, width: int, height: int) -> CameraFrame:
        frame = CameraFrame(
            data=data,
            width=width,
            height=height,
            timestamp=time.time(),
        )
        self._frames.append(frame)
        if len(self._frames) > 100:
            self._frames = self._frames[-100:]
        return frame

    def get_latest_frame(self) -> Optional[CameraFrame]:
        return self._frames[-1] if self._frames else None

    def start_stream(self) -> None:
        self._is_active = True

    def stop_stream(self) -> None:
        self._is_active = False

    @property
    def is_active(self) -> bool:
        return self._is_active

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config": self._config.to_dict(),
            "is_active": self._is_active,
            "latest_frame": self.get_latest_frame().to_dict() if self._frames else None,
            "frame_count": len(self._frames),
        }
