"""Scene Manager — Scene composition with sprites, BOBs, and teletext."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SceneObject:
    """An object within a scene (sprite, BOB, text, etc.)."""

    name: str
    object_type: str  # "sprite", "bob", "text", "model", "light"
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    object_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object_id": self.object_id,
            "name": self.name,
            "type": self.object_type,
            "position": list(self.position),
            "rotation": list(self.rotation),
            "scale": list(self.scale),
            "properties": self.properties,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneObject":
        return cls(
            name=data["name"],
            object_type=data["type"],
            position=tuple(data.get("position", [0, 0, 0])),
            rotation=tuple(data.get("rotation", [0, 0, 0])),
            scale=tuple(data.get("scale", [1, 1, 1])),
            object_id=data.get("object_id", str(uuid.uuid4())),
            properties=data.get("properties", {}),
        )


@dataclass
class Scene:
    """A scene within a world, containing objects."""

    name: str
    scene_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objects: List[SceneObject] = field(default_factory=list)
    camera_position: Tuple[float, float, float] = (0.0, 0.0, 10.0)
    lighting: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_object(self, obj: SceneObject) -> None:
        self.objects.append(obj)

    def remove_object(self, object_id: str) -> bool:
        for i, obj in enumerate(self.objects):
            if obj.object_id == object_id:
                self.objects.pop(i)
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "name": self.name,
            "objects": [o.to_dict() for o in self.objects],
            "camera_position": list(self.camera_position),
            "lighting": self.lighting,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        scene = cls(
            name=data["name"],
            scene_id=data.get("scene_id", str(uuid.uuid4())),
            camera_position=tuple(data.get("camera_position", [0, 0, 10])),
            lighting=data.get("lighting", {}),
            metadata=data.get("metadata", {}),
        )
        scene.objects = [SceneObject.from_dict(o) for o in data.get("objects", [])]
        return scene


class SceneManager:
    """Manages scenes and their composition."""

    def __init__(self) -> None:
        self._scenes: Dict[str, Scene] = {}

    def create_scene(self, name: str, world_id: str) -> Scene:
        scene = Scene(name=name, metadata={"world_id": world_id})
        self._scenes[scene.scene_id] = scene
        return scene

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        return self._scenes.get(scene_id)

    def list_scenes(self, world_id: Optional[str] = None) -> List[Scene]:
        if world_id:
            return [
                s for s in self._scenes.values()
                if s.metadata.get("world_id") == world_id
            ]
        return list(self._scenes.values())

    def delete_scene(self, scene_id: str) -> bool:
        if scene_id in self._scenes:
            del self._scenes[scene_id]
            return True
        return False

    def add_object_to_scene(
        self,
        scene_id: str,
        name: str,
        object_type: str,
        position: Tuple[float, float, float] = (0, 0, 0),
    ) -> Optional[SceneObject]:
        scene = self._scenes.get(scene_id)
        if not scene:
            return None
        obj = SceneObject(name=name, object_type=object_type, position=position)
        scene.add_object(obj)
        return obj
