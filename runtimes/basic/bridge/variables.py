"""
Variable Manager — register, snapshot, and restore BASIC variable state.

Provides a way to capture the runtime state of BBC BASIC variables
(primarily those surfaced via LENS/SKIN hooks) so that sessions can
be serialised and restored.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class VariableRegister:
    name: str
    value: Any
    type_tag: str = "string"
    locked: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "type": self.type_tag,
            "locked": self.locked,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VariableRegister":
        return cls(
            name=data["name"],
            value=data["value"],
            type_tag=data.get("type", "string"),
            locked=data.get("locked", False),
        )


@dataclass
class VariableSnapshot:
    registers: dict[str, VariableRegister] = field(default_factory=dict)
    timestamp: str = ""

    def set(
        self, name: str, value: Any, type_tag: str = "string", locked: bool = False
    ) -> None:
        self.registers[name] = VariableRegister(
            name=name, value=value, type_tag=type_tag, locked=locked
        )

    def get(self, name: str) -> Optional[VariableRegister]:
        return self.registers.get(name)

    def delete(self, name: str) -> bool:
        if name in self.registers and not self.registers[name].locked:
            del self.registers[name]
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "registers": {
                k: r.to_dict() for k, r in self.registers.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VariableSnapshot":
        instance = cls(timestamp=data.get("timestamp", ""))
        for name, reg in data.get("registers", {}).items():
            instance.registers[name] = VariableRegister.from_dict(reg)
        return instance

    def save(self, path: Path) -> None:
        """Persist snapshot to a JSON file."""
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "VariableSnapshot":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)


class VariableManager:
    """
    Session-level variable manager — holds active registers, supports
    snapshots, diffing, and restore operations.
    """

    def __init__(self):
        self._active = VariableSnapshot()

    def register(
        self, name: str, value: Any, type_tag: str = "string", locked: bool = False
    ) -> None:
        self._active.set(name, value, type_tag, locked)

    def resolve(self, name: str) -> Optional[Any]:
        reg = self._active.get(name)
        return reg.value if reg else None

    def unregister(self, name: str) -> bool:
        return self._active.delete(name)

    def snapshot(self) -> VariableSnapshot:
        """Return a copy of the current register state."""
        import datetime
        snap = VariableSnapshot(
            registers=dict(self._active.registers),
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        )
        return snap

    def restore(self, snap: VariableSnapshot) -> None:
        """Overwrite active registers from a saved snapshot."""
        self._active = VariableSnapshot(
            registers=dict(snap.registers),
            timestamp=snap.timestamp,
        )

    def list_names(self) -> list[str]:
        return sorted(self._active.registers.keys())