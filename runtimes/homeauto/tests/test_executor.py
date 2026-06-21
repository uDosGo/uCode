from __future__ import annotations

import json
from pathlib import Path

from uhome_server.installer.executor import execute_staged_install
from uhome_server.installer.staging import stage_install_artifacts
from uhome_server.installer.plan import UHOMEInstallOptions
from uhome_server.installer.bundle import (
    BUNDLE_SCHEMA_VERSION,
    UHOMEBundleComponent,
    UHOMEBundleManifest,
    UHOMEHostProfileRef,
    write_bundle_manifest,
)


def _probe() -> dict:
    return {
        "cpu_cores": 6,
        "ram_gb": 16.0,
        "storage_gb": 512.0,
        "media_storage_gb": 4000.0,
        "storage_ready": True,
        "dvr_ready": True,
        "has_gigabit": True,
        "has_hdmi": True,
        "tuner_count": 2,
        "has_usb_ports": 4,
        "has_bluetooth": True,
        "os_disk_id": "disk-linux-root-exec",
        "media_volume_ids": ["media-array-exec"],
    }


def _bundle(bundle_dir: Path) -> None:
    import hashlib

    artifact = bundle_dir / "components" / "jellyfin" / "payload.tar.gz"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(b"execute-payload")
    manifest = UHOMEBundleManifest(
        bundle_id="bundle-exec-001",
        uhome_version="1.0.0",
        sonic_version="1.3.1",
        schema_version=BUNDLE_SCHEMA_VERSION,
        created_at="2026-03-08T00:00:00Z",
        host_profile=UHOMEHostProfileRef(
            profile_id="standalone-linux",
            display_name="Standalone Linux Host",
            boot_mode="standalone",
            target_roles=["media-server", "dvr", "launcher"],
        ),
        components=[
            UHOMEBundleComponent(
                component_id="jellyfin",
                display_name="Jellyfin",
                version="10.9.0",
                artifact_path="components/jellyfin/payload.tar.gz",
                sha256=hashlib.sha256(b"execute-payload").hexdigest(),
                install_target="/opt/uhome/jellyfin",
            )
        ],
        rollback_token="rb-exec-001",
    )
    write_bundle_manifest(bundle_dir, manifest)


def test_execute_staged_install_writes_target_outputs(tmp_path):
    bundle_dir = tmp_path / "bundle"
    stage_dir = tmp_path / "stage"
    target_root = tmp_path / "target"
    _bundle(bundle_dir)
    stage_install_artifacts(bundle_dir, stage_dir, _probe(), UHOMEInstallOptions(enable_ha_bridge=True))
    result = execute_staged_install(stage_dir, target_root)
    assert "jellyfin" in result.installed_components
    assert (target_root / "install-root" / "jellyfin" / "payload.tar.gz").exists()
    assert (target_root / "config" / "jellyfin.json").exists()
    assert (target_root / "etc" / "uhome" / "jellyfin.env").exists()
    assert (target_root / "systemd" / "system" / "jellyfin.service").exists()
    assert (target_root / "systemd" / "multi-user.target.wants" / "jellyfin.service").exists()
    unit_text = (target_root / "systemd" / "system" / "jellyfin.service").read_text(encoding="utf-8")
    assert "EnvironmentFile=/etc/uhome/jellyfin.env" in unit_text
    assert "ExecStart=/usr/bin/env sh -lc 'exec jellyfin" in unit_text
    assert (target_root / "receipts" / "install-receipt.json").exists()
    assert (target_root / "receipts" / "service-manifest.json").exists()
    assert (target_root / "bin" / "systemctl-apply.sh").exists()
    receipt = json.loads((target_root / "receipts" / "install-receipt.json").read_text(encoding="utf-8"))
    assert receipt["host_profile_id"] == "standalone-linux"
    assert receipt["rollback_evidence"]["rollback_supported"] is True
    state = json.loads((target_root / "state" / "install-state.json").read_text(encoding="utf-8"))
    assert state["status"] == "installed"


def test_execute_staged_install_rejects_unready_stage(tmp_path):
    stage_dir = tmp_path / "stage"
    stage_dir.mkdir(parents=True, exist_ok=True)
    (stage_dir / "install-plan.json").write_text(json.dumps({"ready": False}), encoding="utf-8")
    (stage_dir / "install-receipt.json").write_text(json.dumps({"install_root": "/opt/uhome"}), encoding="utf-8")
    try:
        execute_staged_install(stage_dir, tmp_path / "target")
    except ValueError as exc:
        assert "not ready" in str(exc)
    else:
        raise AssertionError("Expected execute_staged_install to reject an unready stage")


def test_execute_staged_install_requires_service_manifest(tmp_path):
    stage_dir = tmp_path / "stage"
    target_root = tmp_path / "target"
    stage_dir.mkdir(parents=True, exist_ok=True)
    (stage_dir / "install-plan.json").write_text(json.dumps({"ready": True}), encoding="utf-8")
    (stage_dir / "install-receipt.json").write_text(json.dumps({"install_root": "/opt/uhome"}), encoding="utf-8")
    (stage_dir / "config").mkdir(parents=True, exist_ok=True)
    try:
        execute_staged_install(stage_dir, target_root)
    except ValueError as exc:
        assert "Service manifest does not exist" in str(exc)
    else:
        raise AssertionError("Expected execute_staged_install to require a staged service manifest")
