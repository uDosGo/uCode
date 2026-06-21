from __future__ import annotations

import hashlib
import json
from pathlib import Path

from uhome_server.installer.staging import stage_install_artifacts
from uhome_server.installer.bundle import (
    BUNDLE_SCHEMA_VERSION,
    UHOMEBundleComponent,
    UHOMEBundleManifest,
    UHOMEHostProfileRef,
    write_bundle_manifest,
    write_rollback_record,
    UHOMERollbackRecord,
)
from uhome_server.installer.plan import UHOMEInstallOptions


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
        "os_disk_id": "disk-linux-root-stage",
        "media_volume_ids": ["media-array-stage"],
    }


def _bundle(bundle_dir: Path) -> None:
    artifact = bundle_dir / "components" / "jellyfin" / "payload.tar.gz"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(b"staged-payload")
    manifest = UHOMEBundleManifest(
        bundle_id="bundle-stage-001",
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
                sha256=hashlib.sha256(b"staged-payload").hexdigest(),
                install_target="/opt/uhome/jellyfin",
            )
        ],
        rollback_token="rb-stage-001",
    )
    write_bundle_manifest(bundle_dir, manifest)


def test_stage_install_artifacts_writes_expected_outputs(tmp_path):
    bundle_dir = tmp_path / "bundle"
    stage_dir = tmp_path / "stage"
    _bundle(bundle_dir)
    write_rollback_record(bundle_dir, UHOMERollbackRecord(rollback_token="rb-stage-001"))
    plan, staged = stage_install_artifacts(
        bundle_dir,
        stage_dir,
        _probe(),
        UHOMEInstallOptions(enable_ha_bridge=True),
    )
    assert plan.ready is True
    assert staged.plan_path.exists()
    assert staged.service_manifest_path.exists()
    assert staged.receipt_path.exists()
    assert staged.state_path.exists()
    assert staged.rollback_path is not None
    assert (stage_dir / "components" / "jellyfin" / "payload.tar.gz").exists()
    assert (stage_dir / "config" / "home-assistant-bridge.json").exists()
    assert (stage_dir / "rollback" / "rollback.json").exists()
    receipt = json.loads(staged.receipt_path.read_text(encoding="utf-8"))
    assert receipt["bundle_id"] == "bundle-stage-001"
    assert receipt["host_profile_id"] == "standalone-linux"
    assert receipt["rollback_evidence"]["rollback_supported"] is True
    assert receipt["storage_identity_evidence"]["complete"] is True
    assert receipt["preflight"]["capability_checks"]["storage_ready"]["passed"] is True


def test_stage_install_artifacts_rejects_unready_plan(tmp_path):
    bundle_dir = tmp_path / "bundle"
    stage_dir = tmp_path / "stage"
    _bundle(bundle_dir)
    failing_probe = {"cpu_cores": 2, "ram_gb": 4.0, "storage_gb": 128.0, "media_storage_gb": 500.0}
    try:
        stage_install_artifacts(bundle_dir, stage_dir, failing_probe)
    except ValueError as exc:
        assert "not ready" in str(exc)
    else:
        raise AssertionError("Expected staging to fail for an unready plan")
