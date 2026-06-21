from __future__ import annotations

class ModuleRegistry:
    def __init__(self) -> None:
        self.modules: dict[str, dict] = {}

    def register(self, name: str, kind: str) -> dict:
        self.modules[name] = {"kind": kind}
        return {"name": name, "kind": kind}

    def list(self) -> dict:
        return {"count": len(self.modules), "modules": self.modules}
