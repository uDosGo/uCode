from __future__ import annotations

import json
from pathlib import Path

from uhome_server.migrations.wizard_to_kiosk import (
    migrate_library_container_manifests,
    migrate_presentation_state,
    run_wizard_to_kiosk_migration,
)


def test_migrate_presentation_copies_and_rewrites_auth(tmp_path: Path) -> None:
    legacy = tmp_path / "memory" / "wizard" / "uhome" / "presentation.json"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(
        json.dumps(
            {
                "active_presentation": "thin-gui",
                "thin_gui": {
                    "intent": {
                        "auth": {"wizard_mode_active": False, "uhome_role": "server"},
                    }
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    out = migrate_presentation_state(tmp_path, dry_run=False, force=False, remove_legacy=False)
    assert out["action"] == "copied_and_rewritten"
    target = tmp_path / "memory" / "kiosk" / "uhome" / "presentation.json"
    assert target.exists()
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert "wizard_mode_active" not in payload["thin_gui"]["intent"]["auth"]
    assert payload["thin_gui"]["intent"]["auth"]["kiosk_local_session"] is True
    assert legacy.exists()


def test_migrate_presentation_skips_when_target_exists_without_force(tmp_path: Path) -> None:
    legacy = tmp_path / "memory" / "wizard" / "uhome" / "presentation.json"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(json.dumps({"active_presentation": None}), encoding="utf-8")
    target = tmp_path / "memory" / "kiosk" / "uhome" / "presentation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"active_presentation": "thin-gui"}), encoding="utf-8")

    out = migrate_presentation_state(tmp_path, dry_run=False, force=False, remove_legacy=False)
    assert out["action"] == "skipped_target_exists"


def test_migrate_presentation_remove_legacy(tmp_path: Path) -> None:
    legacy = tmp_path / "memory" / "wizard" / "uhome" / "presentation.json"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(json.dumps({"active_presentation": None}), encoding="utf-8")

    out = migrate_presentation_state(tmp_path, dry_run=False, force=False, remove_legacy=True)
    assert out["action"] == "copied_and_rewritten"
    assert out.get("legacy_removed") is True
    assert not legacy.exists()


def test_migrate_container_manifest_wizard_only_and_callable(tmp_path: Path) -> None:
    lib = tmp_path / "library" / "sample"
    lib.mkdir(parents=True)
    manifest = lib / "container.json"
    manifest.write_text(
        json.dumps(
            {
                "policy": {"wizard_only": True, "execution_model": "container-library-v1"},
                "metadata": {"callable_from": ["uhome", "wizard"]},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    reports = migrate_library_container_manifests(tmp_path, dry_run=False)
    assert len(reports) == 1
    assert reports[0]["changed"] is True
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert "wizard_only" not in data["policy"]
    assert data["policy"]["thin_kiosk_only"] is True
    assert data["metadata"]["callable_from"] == ["uhome", "thin-kiosk"]


def test_run_wizard_to_kiosk_migration_dry_run_no_writes(tmp_path: Path) -> None:
    legacy = tmp_path / "memory" / "wizard" / "uhome" / "presentation.json"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(json.dumps({"active_presentation": None}), encoding="utf-8")

    report = run_wizard_to_kiosk_migration(tmp_path, dry_run=True)
    assert report.ok
    assert report.presentation["action"] == "dry_run_would_copy"
    assert not (tmp_path / "memory" / "kiosk" / "uhome" / "presentation.json").exists()


def test_migrate_main_cli_smoke(tmp_path: Path) -> None:
    from uhome_server.cli import migrate_main

    code = migrate_main(
        [
            "wizard-to-kiosk",
            "--repo-root",
            str(tmp_path),
            "--skip-manifests",
        ]
    )
    assert code == 0
