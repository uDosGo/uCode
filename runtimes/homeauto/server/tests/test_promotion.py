from __future__ import annotations

import json
from pathlib import Path

from uhome_server.installer.executor import execute_staged_install
from uhome_server.installer.health import run_promoted_health_checks
from uhome_server.installer.promotion import promote_target_root, rollback_promoted_target, verify_promoted_target
from uhome_server.installer.staging import stage_install_artifacts
from uhome_server.installer.bundle import (
    BUNDLE_SCHEMA_VERSION,
    UHOMEBundleComponent,
    UHOMEBundleManifest,
    UHOMEHostProfileRef,
    write_bundle_manifest,
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
        "os_disk_id": "disk-linux-root-promo",
        "media_volume_ids": ["media-array-promo"],
    }


def _bundle(bundle_dir: Path) -> None:
    import hashlib

    artifact = bundle_dir / "components" / "jellyfin" / "payload.tar.gz"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(b"promotion-payload")
    manifest = UHOMEBundleManifest(
        bundle_id="bundle-promotion-001",
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
        rollback_token="rb-promotion-001",
        components=[
            UHOMEBundleComponent(
                component_id="jellyfin",
                display_name="Jellyfin",
                version="10.9.0",
                artifact_path="components/jellyfin/payload.tar.gz",
                sha256=hashlib.sha256(b"promotion-payload").hexdigest(),
                install_target="/opt/uhome/jellyfin",
            )
        ],
    )
    write_bundle_manifest(bundle_dir, manifest)


def test_promote_and_rollback_target_root(tmp_path):
    bundle_dir = tmp_path / "bundle"
    stage_dir = tmp_path / "stage"
    target_root = tmp_path / "target"
    host_root = tmp_path / "host"
    _bundle(bundle_dir)
    stage_install_artifacts(bundle_dir, stage_dir, _probe(), UHOMEInstallOptions(enable_ha_bridge=True))
    execute_staged_install(stage_dir, target_root)

    original_host_env = host_root / "etc" / "uhome" / "jellyfin.env"
    original_host_env.parent.mkdir(parents=True, exist_ok=True)
    original_host_env.write_text('JELLYFIN_DATA_DIR="/srv/old"\n', encoding="utf-8")

    promotion = promote_target_root(target_root, host_root)
    assert (host_root / "etc" / "uhome" / "jellyfin.env").exists()
    assert (host_root / "etc" / "systemd" / "system" / "jellyfin.service").exists()
    assert promotion.receipt_path.exists()
    assert promotion.mode == "first_apply"
    assert promotion.upgrade_diff["added"] == ["jellyfin"]
    assert promotion.command_plan_path.exists()
    assert promotion.ubuntu_apply_plan_path.exists()
    assert promotion.health_check_plan_path.exists()
    assert promotion.verification_path.exists()

    promoted_env = (host_root / "etc" / "uhome" / "jellyfin.env").read_text(encoding="utf-8")
    assert "/opt/uhome/var/jellyfin" in promoted_env
    verification = verify_promoted_target(host_root)
    assert verification.ok is True
    assert verification.checks["host_profile_present"]["ok"] is True
    assert verification.checks["rollback_evidence_present"]["ok"] is True
    assert verification.checks["storage_identity_evidence_present"]["ok"] is True
    command_plan = promotion.command_plan_path.read_text(encoding="utf-8")
    assert "systemctl daemon-reload" in command_plan
    assert "systemctl enable" in command_plan
    ubuntu_apply_plan = promotion.ubuntu_apply_plan_path.read_text(encoding="utf-8")
    assert "sudo rsync -a --delete" in ubuntu_apply_plan
    assert "sudo systemctl daemon-reload" in ubuntu_apply_plan
    health_plan = json.loads(promotion.health_check_plan_path.read_text(encoding="utf-8"))
    checks_by_service = {item["service"]: item["health_check"] for item in health_plan["checks"]}
    assert checks_by_service["jellyfin"]["kind"] == "http"
    promotion_receipt = json.loads(promotion.receipt_path.read_text(encoding="utf-8"))
    assert promotion_receipt["reinstall_context"]["current_host_profile_id"] == "standalone-linux"
    assert promotion_receipt["reinstall_context"]["rollback_supported"] is True
    assert promotion_receipt["reinstall_context"]["storage_identity_complete"] is True

    rollback = rollback_promoted_target(host_root)
    restored_env = (host_root / "etc" / "uhome" / "jellyfin.env").read_text(encoding="utf-8")
    assert 'JELLYFIN_DATA_DIR="/srv/old"' in restored_env
    assert rollback.state_path.exists()


def test_promote_target_root_requires_existing_target(tmp_path):
    try:
        promote_target_root(tmp_path / "missing-target", tmp_path / "host")
    except ValueError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("Expected promote_target_root to reject missing target root")


def test_promote_target_root_detects_reapply(tmp_path):
    bundle_dir = tmp_path / "bundle"
    stage_dir = tmp_path / "stage"
    target_root = tmp_path / "target"
    host_root = tmp_path / "host"
    _bundle(bundle_dir)
    stage_install_artifacts(bundle_dir, stage_dir, _probe(), UHOMEInstallOptions(enable_ha_bridge=True))
    execute_staged_install(stage_dir, target_root)
    first = promote_target_root(target_root, host_root)
    second = promote_target_root(target_root, host_root)
    assert first.mode == "first_apply"
    assert second.mode == "reapply"
    assert second.upgrade_diff["unchanged"] == ["jellyfin"]


def test_run_promoted_health_checks(tmp_path):
    bundle_dir = tmp_path / "bundle"
    stage_dir = tmp_path / "stage"
    target_root = tmp_path / "target"
    host_root = tmp_path / "host"
    _bundle(bundle_dir)
    stage_install_artifacts(bundle_dir, stage_dir, _probe(), UHOMEInstallOptions(enable_ha_bridge=True))
    execute_staged_install(stage_dir, target_root)
    promote_target_root(target_root, host_root)

    def _runner(command, shell, text, capture_output):
        del shell, text, capture_output
        service = "jellyfin" if "8096" in command else "other"
        return type(
            "_Completed",
            (),
            {
                "returncode": 0,
                "stdout": f"{service} ok",
                "stderr": "",
            },
        )()

    result = run_promoted_health_checks(host_root, runner=_runner)
    assert result.ok is True
    assert result.report_path.exists()
    assert any(item["service"] == "jellyfin" for item in result.checks)
