"""Persistence — World state save/load using JSON storage."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ucode4.world.engine import World, WorldEngine


@dataclass
class WorldStore:
    """Configuration for world storage."""

    base_path: str = field(default_factory=lambda: str(Path.home() / ".ucode4" / "worlds"))
    auto_save: bool = True

    def ensure_path(self) -> None:
        os.makedirs(self.base_path, exist_ok=True)

    def world_path(self, world_id: str) -> str:
        return os.path.join(self.base_path, f"{world_id}.json")

    def list_saved_worlds(self) -> List[str]:
        self.ensure_path()
        worlds = []
        for f in os.listdir(self.base_path):
            if f.endswith(".json"):
                worlds.append(f[:-5])
        return worlds


class Persistence:
    """Handles saving and loading world state."""

    def __init__(self, store: Optional[WorldStore] = None) -> None:
        self.store = store or WorldStore()

    def save_world(self, world: World) -> str:
        """Save a world to disk."""
        self.store.ensure_path()
        filepath = self.store.world_path(world.world_id)
        with open(filepath, "w") as f:
            json.dump(world.to_dict(), f, indent=2)
        return filepath

    def load_world(self, world_id: str) -> Optional[World]:
        """Load a world from disk."""
        filepath = self.store.world_path(world_id)
        if not os.path.exists(filepath):
            return None
        with open(filepath) as f:
            data = json.load(f)
        return World.from_dict(data)

    def load_all_worlds(self) -> Dict[str, World]:
        """Load all saved worlds."""
        worlds: Dict[str, World] = {}
        for world_id in self.store.list_saved_worlds():
            world = self.load_world(world_id)
            if world:
                worlds[world_id] = world
        return worlds

    def delete_world(self, world_id: str) -> bool:
        """Delete a saved world."""
        filepath = self.store.world_path(world_id)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def save_engine(self, engine: WorldEngine) -> str:
        """Save all worlds in an engine to disk."""
        self.store.ensure_path()
        filepath = os.path.join(self.store.base_path, "_engine_state.json")
        with open(filepath, "w") as f:
            json.dump(engine.to_dict(), f, indent=2)
        return filepath

    def load_engine(self) -> WorldEngine:
        """Load engine state from disk."""
        filepath = os.path.join(self.store.base_path, "_engine_state.json")
        if not os.path.exists(filepath):
            return WorldEngine()
        with open(filepath) as f:
            data = json.load(f)
        return WorldEngine.from_dict(data)
