from __future__ import annotations

import hashlib
from pathlib import Path

from uhome_server.installer.bundle import (
    BUNDLE_MANIFEST_FILENAME,
    BUNDLE_SCHEMA_VERSION,
    UHOMEBundleComponent,
    UHOMEBundleManifest,
    UHOMEHostProfileRef,
    UHOMERollbackRecord,
    compute_checksum,
    read_bundle_manifest,
    read_rollback_record,
    verify_bundle,
    verify_checksum,
    write_bundle_manifest,
    write_rollback_record,
)
from uhome_server.installer.plan import UHOMEInstallOptions, build_uhome_install_plan
from uhome_server.installer.preflight import get_host_profile, preflight_check


def _write_artifact(bundle_dir: Path, rel_path: str, content: bytes = b"fake-payload") -> str:
    artifact = bundle_dir / rel_path
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def _minimal_component(bundle_dir: Path, component_id: str = "jellyfin") -> UHOMEBundleComponent:
    rel = f"components/{component_id}/payload.tar.gz"
    sha = _write_artifact(bundle_dir, rel)
    return UHOMEBundleComponent(
        component_id=component_id,
        display_name=component_id.capitalize(),
        version="1.0.0",
        artifact_path=rel,
        sha256=sha,
        install_target=f"/opt/uhome/{component_id}",
    )


def _minimal_manifest(bundle_dir: Path) -> UHOMEBundleManifest:
    return UHOMEBundleManifest(
        bundle_id="test-bundle-001",
        uhome_version="1.0.0",
        sonic_version="1.3.1",
        schema_version=BUNDLE_SCHEMA_VERSION,
        created_at="2026-02-23T00:00:00Z",
        host_profile=UHOMEHostProfileRef(
            profile_id="standalone-linux",
            display_name="Standalone Linux Host",
            boot_mode="standalone",
            target_roles=["media-server"],
        ),
        components=[_minimal_component(bundle_dir)],
    )


def _passing_probe() -> dict:
    return {
        "cpu_cores": 6,
        "ram_gb": 16.0,
        "storage_gb": 512.0,
        "media_storage_gb": 4000.0,
        "has_gigabit": True,
        "has_hdmi": True,
        "tuner_count": 2,
        "has_usb_ports": 4,
        "has_bluetooth": True,
        "storage_ready": True,
        "dvr_ready": True,
        "os_disk_id": "disk-linux-root-test",
        "media_volume_ids": ["media-array-test"],
    }


def _failing_probe() -> dict:
    return {"cpu_cores": 2, "ram_gb": 4.0, "storage_gb": 128.0, "media_storage_gb": 500.0, "has_gigabit": False, "has_hdmi": False, "tuner_count": 0}


def test_compute_checksum(tmp_path):
    path = tmp_path / "artifact.bin"
    content = b"hello uHOME"
    path.write_bytes(content)
    assert compute_checksum(path) == hashlib.sha256(content).hexdigest()


def test_verify_checksum_passes(tmp_path):
    path = tmp_path / "artifact.bin"
    content = b"correct content"
    path.write_bytes(content)
    assert verify_checksum(path, hashlib.sha256(content).hexdigest()) is True


def test_write_and_read_bundle_manifest(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    out = write_bundle_manifest(tmp_path, manifest)
    assert out.name == BUNDLE_MANIFEST_FILENAME
    loaded = read_bundle_manifest(tmp_path)
    assert loaded is not None
    assert loaded.bundle_id == manifest.bundle_id
    assert loaded.host_profile is not None
    assert loaded.host_profile.profile_id == "standalone-linux"


def test_write_and_read_rollback_record(tmp_path):
    record = UHOMERollbackRecord(rollback_token="tok-abc123", snapshot_paths=["/opt/uhome/jellyfin"])
    write_rollback_record(tmp_path, record)
    loaded = read_rollback_record(tmp_path)
    assert loaded is not None
    assert loaded.rollback_token == "tok-abc123"


def test_verify_bundle_missing_artifact(tmp_path):
    manifest = UHOMEBundleManifest(
        bundle_id="b2",
        uhome_version="1.0.0",
        sonic_version="1.3.1",
        schema_version=BUNDLE_SCHEMA_VERSION,
        created_at="2026-02-23T00:00:00Z",
        components=[
            UHOMEBundleComponent(
                component_id="comskip",
                display_name="Comskip",
                version="0.81.0",
                artifact_path="components/comskip/comskip.tar.gz",
                sha256="abc123",
                install_target="/opt/uhome/comskip",
            )
        ],
    )
    result = verify_bundle(manifest, tmp_path)
    assert result.valid is False
    assert "comskip" in result.missing


def test_install_plan_ready(tmp_path):
    manifest = _minimal_manifest(tmp_path)
    write_bundle_manifest(tmp_path, manifest)
    plan = build_uhome_install_plan(tmp_path, _passing_probe(), UHOMEInstallOptions(enable_autologin_kiosk=False))
    assert plan.ready is True
    assert plan.verify_result is not None
    assert plan.host_profile_id == "standalone-linux"


def test_install_plan_blocked_by_preflight(tmp_path):
    plan = build_uhome_install_plan(tmp_path, _failing_probe())
    assert plan.ready is False
    assert plan.verify_result is None


def test_dual_boot_profile_requires_dual_boot_capabilities():
    probe = _passing_probe()
    result = preflight_check(probe, host_profile=get_host_profile("dual-boot-steam-node"))
    assert result.passed is False
    assert any("supports_windows_dual_boot" in issue for issue in result.issues)
