"""Small file-backed workspace service for uHOME settings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from uhome_server.config import get_repo_root


def _normalize_read_keys(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in payload.items():
        normalized[key.replace("-", "_")] = value
    return normalized


class TemplateWorkspaceService:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or get_repo_root()
        self.base_dir = self.repo_root / "memory" / "workspace" / "settings"
        self.defaults_dir = self.repo_root / "defaults" / "workspace" / "settings"

    def _component_path(self, section: str, component_id: str) -> Path:
        return self.base_dir / f"{section}-{component_id}.json"

    def _default_component_path(self, section: str, component_id: str) -> Path:
        return self.defaults_dir / f"{section}-{component_id}.json"

    def _read_json_dict(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return _normalize_read_keys(data)
        except json.JSONDecodeError:
            pass
        return {}

    def read_fields(self, section: str, component_id: str) -> dict[str, Any]:
        defaults = self._read_json_dict(self._default_component_path(section, component_id))
        overrides = self._read_json_dict(self._component_path(section, component_id))
        return {**defaults, **overrides}

    def write_user_field(
        self,
        section: str,
        component_id: str,
        field_name: str,
        value: Any,
    ) -> dict[str, Any]:
        path = self._component_path(section, component_id)
        payload = {}
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(existing, dict):
                    payload = existing
            except json.JSONDecodeError:
                payload = {}
        payload[field_name] = value
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return {"effective_source": "user", "effective_content": json.dumps(payload, indent=2)}

    def component_contract(self, component_id: str) -> dict[str, Any]:
        return {
            "component_id": component_id,
            "workspace_ref": "@memory/workspace/settings",
        }

    def component_snapshot(self, component_id: str) -> dict[str, Any]:
        return {
            "component_id": component_id,
            "settings": self.read_fields("settings", component_id),
            "instructions_ref": f"docs/workspace/instructions/{component_id}.md",
        }


def get_template_workspace_service(
    repo_root: Path | None = None,
) -> TemplateWorkspaceService:
    return TemplateWorkspaceService(repo_root=repo_root)
