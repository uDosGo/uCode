from __future__ import annotations

import json
from pathlib import Path

from uhome_server.config import JSONConfigStore, bootstrap_runtime, get_runtime_settings


def test_runtime_settings_paths(monkeypatch, tmp_path):
    monkeypatch.setenv("JELLYFIN_URL", "http://jellyfin.local:8096")
    monkeypatch.setenv("HA_BRIDGE_ENABLED", "true")
    settings = get_runtime_settings(tmp_path)
    assert settings.config_path == tmp_path / "memory" / "config" / "uhome.json"
    assert settings.legacy_config_path == tmp_path / "memory" / "config" / "wizard.json"
    assert settings.ha_bridge_enabled is True
    assert settings.jellyfin_url == "http://jellyfin.local:8096"


def test_bootstrap_runtime_creates_expected_paths(tmp_path):
    report = bootstrap_runtime(tmp_path)
    assert report["ok"] is True
    assert (tmp_path / "memory" / "config").exists()
    assert (tmp_path / "memory" / "workspace" / "settings").exists()
    assert (tmp_path / "memory" / "bank" / "uhome").exists()
    assert report["legacy_config_fallback"] is False


def test_json_config_store_uses_wizard_fallback(tmp_path):
    legacy_path = tmp_path / "memory" / "config" / "wizard.json"
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text(json.dumps({"ha_bridge_enabled": True}), encoding="utf-8")
    store = JSONConfigStore(path=tmp_path / "memory" / "config" / "uhome.json")
    assert store.get("ha_bridge_enabled", False) is True


def test_json_config_store_prefers_legacy_uhome_over_wizard(tmp_path):
    base = tmp_path / "memory" / "config"
    base.mkdir(parents=True, exist_ok=True)
    (base / "legacy-uhome.json").write_text(json.dumps({"ha_bridge_enabled": True}), encoding="utf-8")
    (base / "wizard.json").write_text(json.dumps({"ha_bridge_enabled": False}), encoding="utf-8")
    store = JSONConfigStore(path=base / "uhome.json")
    assert store.get("ha_bridge_enabled", False) is True


def test_json_config_store_writes_canonical_path(tmp_path):
    config_path = tmp_path / "memory" / "config" / "uhome.json"
    store = JSONConfigStore(path=config_path)
    store.set("JELLYFIN_URL", "http://localhost:8096")
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    assert payload["JELLYFIN_URL"] == "http://localhost:8096"
