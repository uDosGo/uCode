"""Catalog for git-backed library entries in the standalone uHOME repo."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from uhome_server.config import get_repo_root
from uhome_server.workspace import get_template_workspace_service


@dataclass(frozen=True)
class ContainerExecutionRules:
    execution_model: str
    runtime_owner: str
    callable_from: list[str] = field(default_factory=list)
    library_root: str = "library"
    entry_kind: str = "library"
    standalone_capable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContainerCatalogEntry:
    entry_id: str
    label: str
    summary: str
    path: str
    kind: str
    available: bool = False
    version: str | None = None
    api_prefix: str | None = None
    wrapper_route: str | None = None
    category: str = "container"
    source: str = "library"
    execution: ContainerExecutionRules = field(
        default_factory=lambda: ContainerExecutionRules(
            execution_model="container-library-v1",
            runtime_owner="shared",
            callable_from=["uhome", "thin-kiosk"],
        )
    )
    lens_vars: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["execution"] = self.execution.to_dict()
        return payload


class ContainerCatalogService:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or get_repo_root()
        self.library_root = self.repo_root / "library"

    def list_entries(self) -> list[ContainerCatalogEntry]:
        if not self.library_root.exists():
            return []
        entries: list[ContainerCatalogEntry] = []
        for candidate in sorted(self.library_root.iterdir(), key=lambda path: path.name):
            if not candidate.is_dir():
                continue
            manifest_path = candidate / "container.json"
            if not manifest_path.exists():
                continue
            payload = self._read_json(manifest_path)
            container = payload.get("container", {})
            metadata = payload.get("metadata", {})
            policy = payload.get("policy", {})
            integration = payload.get("integration", {})
            service = payload.get("service", {})
            launch_config = payload.get("launch_config", {})
            entry_id = str(container.get("id") or candidate.name).strip().lower()
            kiosk_exclusive = bool(policy.get("thin_kiosk_only") or policy.get("wizard_only"))
            runtime_owner = (
                "thin-kiosk"
                if kiosk_exclusive
                else str(policy.get("runtime_owner") or "shared").strip().lower()
            )
            resolved_repo_path = self._resolve_repo_path(payload.get("repo_path"), fallback=candidate)
            raw_callable = (
                payload.get("callable_from")
                or metadata.get("callable_from")
                or ["uhome", "thin-kiosk"]
            )
            callable_from = [
                "thin-kiosk" if str(x).strip().lower() == "wizard" else str(x).strip()
                for x in (raw_callable if isinstance(raw_callable, list) else [])
                if isinstance(x, str) and str(x).strip()
            ]
            if not callable_from:
                callable_from = ["uhome", "thin-kiosk"]
            entries.append(
                ContainerCatalogEntry(
                    entry_id=entry_id,
                    label=str(container.get("name") or entry_id).strip(),
                    summary=str(container.get("description") or metadata.get("documentation") or "").strip(),
                    path=str(candidate.relative_to(self.repo_root)),
                    kind="library",
                    available=True,
                    version=self._coerce_optional_str(container.get("version")),
                    api_prefix=self._coerce_optional_str(service.get("browser_route")),
                    wrapper_route=self._coerce_optional_str(integration.get("wrapper_path")),
                    category=str(metadata.get("category") or "container").strip(),
                    execution=ContainerExecutionRules(
                        execution_model=str(policy.get("execution_model") or "container-library-v1").strip(),
                        runtime_owner=runtime_owner,
                        callable_from=callable_from,
                        library_root="library",
                        entry_kind="library",
                        standalone_capable=bool(payload.get("standalone_capable", True)),
                    ),
                    lens_vars={
                        "lens": f"repo-library:{entry_id}",
                        "kind": "library",
                        "runtime_owner": runtime_owner,
                        "path": str(candidate.relative_to(self.repo_root)),
                        "callable_from": callable_from,
                        "workspace_ref": "@memory/workspace/settings",
                    },
                    metadata={
                        "manifest_path": str(manifest_path.relative_to(self.repo_root)),
                        "repo_path": self._coerce_optional_str(payload.get("repo_path")),
                        "resolved_repo_path": str(resolved_repo_path),
                        "license": self._coerce_optional_str(metadata.get("license")),
                        "author": self._coerce_optional_str(metadata.get("maintainer")),
                        "homepage": self._coerce_optional_str(metadata.get("homepage")),
                        "container_type": str(container.get("type") or "local").strip(),
                        "git_source": self._coerce_optional_str(container.get("source")),
                        "git_ref": self._coerce_optional_str(container.get("ref")),
                        "git_cloned": bool(container.get("cloned_at") or (resolved_repo_path / ".git").exists()),
                        "documentation": self._coerce_optional_str(metadata.get("documentation")),
                        "source_url": container.get("source"),
                        "browser_route": service.get("browser_route"),
                        "port": service.get("port"),
                        "health_check_url": self._coerce_optional_str(
                            service.get("health_check_url") or launch_config.get("health_check_url")
                        ),
                        "template_workspace": self._template_workspace_entry(entry_id),
                    },
                )
            )
        return entries

    def list_by_kind(self, kind: str) -> list[ContainerCatalogEntry]:
        return [entry for entry in self.list_entries() if entry.kind == kind.strip().lower()]

    def get_entry(self, entry_id: str) -> ContainerCatalogEntry | None:
        normalized = entry_id.strip().lower()
        for entry in self.list_entries():
            if entry.entry_id == normalized:
                return entry
        return None

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return payload if isinstance(payload, dict) else {}

    def _normalize_string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if isinstance(item, str) and str(item).strip()]

    def _coerce_optional_str(self, value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None

    def _resolve_repo_path(self, value: Any, *, fallback: Path) -> Path:
        if isinstance(value, str) and value.strip():
            candidate = Path(value.strip()).expanduser()
            if not candidate.is_absolute():
                candidate = self.repo_root / candidate
            return candidate
        return fallback

    def _template_workspace_entry(self, component_id: str) -> dict[str, Any]:
        return get_template_workspace_service(self.repo_root).component_contract(component_id)


def get_container_catalog_service(repo_root: Path | None = None) -> ContainerCatalogService:
    return ContainerCatalogService(repo_root=repo_root)
