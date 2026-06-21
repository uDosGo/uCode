"""Local config, path, and bootstrap helpers for standalone uHOME services."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_code_root() -> Path:
    return get_repo_root().parents[1]


def get_uhome_family_root() -> Path:
    explicit = os.environ.get("UHOME_FAMILY_ROOT") or os.environ.get("UDOS_UHOME_FAMILY_ROOT")
    if explicit:
        return Path(explicit)
    return get_code_root() / "uHOME-family"


def get_sonic_family_root() -> Path:
    return Path(os.environ.get("UDOS_SONIC_FAMILY_ROOT", get_code_root() / "sonic-family"))


def get_workspace_root() -> Path:
    return get_uhome_family_root()


def get_uhome_matter_root(workspace_root: Path | None = None) -> Path:
    root = workspace_root or get_uhome_family_root()
    return root / "uHOME-matter"


def _uhome_bundled_contracts_dir() -> Path:
    return Path(__file__).resolve().parent / "contracts"


def _uhome_network_policy_contracts_dir() -> Path:
    return _uhome_bundled_contracts_dir()


def utc_now_iso_z() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RuntimeSettings:
    repo_root: Path
    memory_root: Path
    config_dir: Path
    config_path: Path
    legacy_config_path: Path
    workspace_settings_dir: Path
    uhome_bank_dir: Path
    jellyfin_url: str
    jellyfin_api_key: str
    hdhomerun_host: str
    ha_bridge_enabled: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_root": str(self.repo_root),
            "memory_root": str(self.memory_root),
            "config_dir": str(self.config_dir),
            "config_path": str(self.config_path),
            "legacy_config_path": str(self.legacy_config_path),
            "workspace_settings_dir": str(self.workspace_settings_dir),
            "uhome_bank_dir": str(self.uhome_bank_dir),
            "jellyfin_url": self.jellyfin_url,
            "jellyfin_api_key_configured": bool(self.jellyfin_api_key),
            "hdhomerun_host": self.hdhomerun_host,
            "ha_bridge_enabled": self.ha_bridge_enabled,
        }


def _env_bool(name: str, default: bool = False) -> bool:
    raw = str(os.environ.get(name, "")).strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def get_runtime_settings(repo_root: Path | None = None) -> RuntimeSettings:
    repo_root = repo_root or get_repo_root()
    memory_root = repo_root / "memory"
    config_dir = memory_root / "config"
    config_path = config_dir / "uhome.json"
    legacy_config_path = config_dir / "wizard.json"
    workspace_settings_dir = memory_root / "workspace" / "settings"
    uhome_bank_dir = memory_root / "bank" / "uhome"
    return RuntimeSettings(
        repo_root=repo_root,
        memory_root=memory_root,
        config_dir=config_dir,
        config_path=config_path,
        legacy_config_path=legacy_config_path,
        workspace_settings_dir=workspace_settings_dir,
        uhome_bank_dir=uhome_bank_dir,
        jellyfin_url=str(os.environ.get("JELLYFIN_URL", "") or "").strip(),
        jellyfin_api_key=str(os.environ.get("JELLYFIN_API_KEY", "") or "").strip(),
        hdhomerun_host=str(os.environ.get("HDHOMERUN_HOST", "") or "").strip(),
        ha_bridge_enabled=_env_bool("HA_BRIDGE_ENABLED", False),
    )


def bootstrap_runtime(repo_root: Path | None = None) -> dict[str, Any]:
    settings = get_runtime_settings(repo_root)
    created_paths: list[str] = []
    for path in (
        settings.memory_root,
        settings.config_dir,
        settings.workspace_settings_dir,
        settings.uhome_bank_dir,
    ):
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created_paths.append(str(path))

    active_config_path = settings.config_path
    if not active_config_path.exists():
        legacy_uhome = settings.config_path.with_name("legacy-uhome.json")
        if legacy_uhome.exists():
            active_config_path = legacy_uhome
        elif settings.legacy_config_path.exists():
            active_config_path = settings.legacy_config_path

    return {
        "ok": True,
        "timestamp": utc_now_iso_z(),
        "created_paths": created_paths,
        "settings": settings.to_dict(),
        "active_config_path": str(active_config_path),
        "active_config_exists": active_config_path.exists(),
        "legacy_config_fallback": active_config_path == settings.legacy_config_path,
    }


class JSONConfigStore:
    def __init__(self, path: Path | None = None):
        settings = get_runtime_settings()
        self.path = path or settings.config_path
        self.legacy_path = self.path.with_name("wizard.json") if path is not None else settings.legacy_config_path

    def _config_candidates(self) -> list[Path]:
        return [self.path, self.path.with_name("legacy-uhome.json"), self.legacy_path]

    def _load(self) -> dict[str, Any]:
        active_path = next((p for p in self._config_candidates() if p.exists()), None)
        if active_path is None:
            return {}
        try:
            return json.loads(active_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def get(self, key: str, default: Any = None) -> Any:
        if key in os.environ:
            return os.environ[key]
        return self._load().get(key, default)

    def set(self, key: str, value: Any) -> None:
        payload = self._load()
        payload[key] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json_file(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return default


def write_json_file(path: Path, payload: dict[str, Any], indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=indent), encoding="utf-8")


def get_sync_record_contract_path(workspace_root: Path | None = None) -> Path:
    _ = workspace_root  # reserved for tests / future overrides
    env_path = os.environ.get("UHOME_SYNC_RECORD_CONTRACT_PATH")
    if env_path:
        return Path(env_path)
    return _uhome_bundled_contracts_dir() / "sync-record-contract.json"


def get_sync_record_schema_path(workspace_root: Path | None = None) -> Path:
    _ = workspace_root
    env_path = os.environ.get("UHOME_SYNC_RECORD_SCHEMA_PATH")
    if env_path:
        return Path(env_path)
    return _uhome_bundled_contracts_dir() / "sync-record-contract.schema.json"


def load_sync_record_contract(workspace_root: Path | None = None) -> dict[str, Any]:
    path = get_sync_record_contract_path(workspace_root)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def load_sync_record_schema(workspace_root: Path | None = None) -> dict[str, Any]:
    path = get_sync_record_schema_path(workspace_root)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def get_home_assistant_bridge_definition_path(workspace_root: Path | None = None) -> Path:
    return get_uhome_matter_root(workspace_root) / "src" / "home-assistant-bridge-definition.json"


def load_home_assistant_bridge_definition(workspace_root: Path | None = None) -> dict[str, Any]:
    path = get_home_assistant_bridge_definition_path(workspace_root)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def get_uhome_network_policy_contract_path() -> Path:
    env_path = os.environ.get("UHOME_NETWORK_POLICY_CONTRACT_PATH")
    if env_path:
        return Path(env_path)
    return _uhome_network_policy_contracts_dir() / "uhome-network-policy-contract.json"


def get_uhome_network_policy_schema_path() -> Path:
    env_path = os.environ.get("UHOME_NETWORK_POLICY_SCHEMA_PATH")
    if env_path:
        return Path(env_path)
    return _uhome_network_policy_contracts_dir() / "uhome-network-policy.schema.json"


def load_uhome_network_policy_contract() -> dict[str, Any]:
    path = get_uhome_network_policy_contract_path()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def load_uhome_network_policy_schema() -> dict[str, Any]:
    path = get_uhome_network_policy_schema_path()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data
