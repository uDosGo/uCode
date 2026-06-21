"""Motion Sensor Module — Accelerometer, gyroscope, magnetometer."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MotionReading:
    """A single motion sensor reading."""
    accelerometer: Tuple[float, float, float]  # x, y, z in m/s²
    gyroscope: Tuple[float, float, float]      # x, y, z in rad/s
    magnetometer: Tuple[float, float, float]   # x, y, z in µT
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accelerometer": list(self.accelerometer),
            "gyroscope": list(self.gyroscope),
            "magnetometer": list(self.magnetometer),
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MotionReading":
        return cls(
            accelerometer=tuple(data["accelerometer"]),
            gyroscope=tuple(data["gyroscope"]),
            magnetometer=tuple(data["magnetometer"]),
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class Orientation:
    """Device orientation derived from sensor fusion."""
    pitch: float = 0.0   # radians
    roll: float = 0.0    # radians
    yaw: float = 0.0     # radians
    heading: float = 0.0 # degrees (compass)

    def to_dict(self) -> Dict[str, float]:
        return {
            "pitch": self.pitch,
            "roll": self.roll,
            "yaw": self.yaw,
            "heading": self.heading,
        }


class MotionSensor:
    """Processes accelerometer, gyroscope, and magnetometer data."""

    def __init__(self) -> None:
        self._readings: List[MotionReading] = []
        self._orientation = Orientation()
        self._last_update: float = 0.0

    def add_reading(self, reading: MotionReading) -> None:
        self._readings.append(reading)
        if len(self._readings) > 1000:
            self._readings = self._readings[-1000:]
        self._update_orientation(reading)

    def _update_orientation(self, reading: MotionReading) -> None:
        """Simple complementary filter for orientation estimation."""
        ax, ay, az = reading.accelerometer
        gx, gy, gz = reading.gyroscope
        mx, my, mz = reading.magnetometer

        dt = reading.timestamp - self._last_update if self._last_update else 0.016
        self._last_update = reading.timestamp

        # Accelerometer-based pitch and roll
        accel_pitch = math.atan2(-ax, math.sqrt(ay ** 2 + az ** 2))
        accel_roll = math.atan2(ay, az)

        # Gyroscope integration
        gyro_pitch = self._orientation.pitch + gx * dt
        gyro_roll = self._orientation.roll + gy * dt
        gyro_yaw = self._orientation.yaw + gz * dt

        # Complementary filter (90% gyro, 10% accel for pitch/roll)
        alpha = 0.9
        self._orientation.pitch = alpha * gyro_pitch + (1 - alpha) * accel_pitch
        self._orientation.roll = alpha * gyro_roll + (1 - alpha) * accel_roll
        self._orientation.yaw = gyro_yaw

        # Magnetometer heading
        if mx != 0 or my != 0:
            heading = math.degrees(math.atan2(my, mx))
            self._orientation.heading = (heading + 360) % 360

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    @property
    def latest(self) -> Optional[MotionReading]:
        return self._readings[-1] if self._readings else None

    def get_readings(self, limit: int = 100) -> List[MotionReading]:
        return self._readings[-limit:]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "orientation": self._orientation.to_dict(),
            "latest": self.latest.to_dict() if self.latest else None,
            "readings": [r.to_dict() for r in self._readings[-50:]],
        }
