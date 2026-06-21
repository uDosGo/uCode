from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from uhome_server.cli import contracts_main, installer_main, launcher_main, main
from uhome_server.installer.bundle import (
    BUNDLE_SCHEMA_VERSION,
    UHOMEBundleComponent,
    UHOMEBundleManifest,
    UHOMEHostProfileRef,
    write_bundle_manifest,
)


def _write_probe(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "cpu_cores": 6,
                "ram_gb": 16.0,
                "storage_gb": 512.0,
                "media_storage_gb": 4000.0,
                "has_gigabit": True,
                "has_hdmi": True,
                "tuner_count": 2,
                "has_usb_ports": 4,
                "has_bluetooth": True,
                "game_storage_gb": 0,
                "os_disk_id": "disk-linux-root-test",
                "media_volume_ids": ["media-array-test"],
            }
        ),
        encoding="utf-8",
    )


def _write_bundle(bundle_dir: Path) -> None:
    artifact = bundle_dir / "components" / "jellyfin" / "payload.tar.gz"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(b"uhome-artifact")
    import hashlib

    manifest = UHOMEBundleManifest(
        bundle_id="bundle-001",
        uhome_version="1.0.0",
        sonic_version="1.3.1",
        schema_version=BUNDLE_SCHEMA_VERSION,
        created_at="2026-03-08T00:00:00Z",
        host_profile=UHOMEHostProfileRef(
            profile_id="standalone-linux",
            display_name="Standalone Linux Host",
            boot_mode="standalone",
            target_roles=["media-server"],
        ),
        components=[
            UHOMEBundleComponent(
                component_id="jellyfin",
                display_name="Jellyfin",
                version="10.9.0",
                artifact_path="components/jellyfin/payload.tar.gz",
                sha256=hashlib.sha256(b"uhome-artifact").hexdigest(),
                install_target="/opt/uhome/jellyfin",
            )
        ],
    )
    write_bundle_manifest(bundle_dir, manifest)


def test_launcher_cli_writes_state(tmp_path):
    code = launcher_main(["--repo-root", str(tmp_path), "start", "--presentation", "thin-gui"])
    assert code == 0
    state_path = tmp_path / "memory" / "kiosk" / "uhome" / "presentation.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert payload["active_presentation"] == "thin-gui"


def test_launcher_cli_rejects_invalid_presentation(tmp_path):
    code = launcher_main(["--repo-root", str(tmp_path), "start", "--presentation", "bad-mode"])
    assert code == 2


def test_launcher_cli_menu(tmp_path):
    with patch("uhome_server.cli._write_output") as write_output:
        code = launcher_main(["--repo-root", str(tmp_path), "menu"])

    assert code == 0
    payload = write_output.call_args[0][0]
    assert payload["menu_id"] == "uhome-console-main"
    item_ids = {item["id"] for item in payload["items"]}
    assert "start-thin-gui" in item_ids


def test_installer_preflight_cli(tmp_path):
    probe_path = tmp_path / "probe.json"
    _write_probe(probe_path)
    output_path = tmp_path / "preflight.json"
    code = installer_main(["preflight", "--probe", str(probe_path), "--output", str(output_path)])
    assert code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["passed"] is True


def test_installer_preflight_cli_with_host_profile(tmp_path):
    probe_path = tmp_path / "probe.json"
    _write_probe(probe_path)
    output_path = tmp_path / "preflight.json"
    code = installer_main(
        ["preflight", "--probe", str(probe_path), "--host-profile", "standalone-linux", "--output", str(output_path)]
    )
    assert code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["profile_id"] == "standalone-linux"


def test_installer_check_prereqs_cli(tmp_path):
    workspace_path = tmp_path / "workspace"
    storage_path = tmp_path / "media"
    output_path = tmp_path / "prereqs.json"
    workspace_path.mkdir()
    storage_path.mkdir()

    with patch("uhome_server.cli.collect_host_prerequisites") as collect_host_prerequisites:
        collect_host_prerequisites.return_value.to_dict.return_value = {
            "passed": True,
            "checks": {"platform": {"ok": True}},
            "warnings": [],
        }
        collect_host_prerequisites.return_value.passed = True
        code = installer_main(
            [
                "check-prereqs",
                "--storage-path",
                str(storage_path),
                "--workspace-path",
                str(workspace_path),
                "--output",
                str(output_path),
            ]
        )

    assert code == 0
    collect_host_prerequisites.assert_called_once_with(
        storage_paths=[str(storage_path)],
        workspace_path=str(workspace_path),
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["passed"] is True


def test_installer_plan_cli(tmp_path):
    probe_path = tmp_path / "probe.json"
    bundle_dir = tmp_path / "bundle"
    _write_probe(probe_path)
    _write_bundle(bundle_dir)
    output_path = tmp_path / "plan.json"
    code = installer_main(
        [
            "plan",
            "--bundle-dir",
            str(bundle_dir),
            "--probe",
            str(probe_path),
            "--enable-ha-bridge",
            "--output",
            str(output_path),
        ]
    )
    assert code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["ready"] is True
    assert payload["preflight"]["passed"] is True


def test_installer_verify_bundle_cli_missing_manifest(tmp_path):
    output_path = tmp_path / "verify.json"
    code = installer_main(["verify-bundle", "--bundle-dir", str(tmp_path), "--output", str(output_path)])
    assert code == 1
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["valid"] is False


def test_contracts_sync_record_cli(tmp_path):
    output_path = tmp_path / "sync-record-contract.json"
    code = contracts_main(["sync-record", "--output", str(output_path)])
    assert code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["version"] == "v2.0.4"
    assert payload["owner"] == "uHOME-server"
    assert "canonical_contact" in payload["record_types"]


def test_main_dispatches_contracts_command(tmp_path):
    output_path = tmp_path / "sync-record-contract.json"
    code = main(["contracts", "sync-record", "--output", str(output_path)])
    assert code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["schema_title"] == "uHOME Sync Record Contract"


def test_contracts_validate_sync_record_cli(tmp_path):
    payload = {
        "contract_version": "v2.0.4",
        "contacts": [],
        "activities": [],
        "binders": [],
        "sync_metadata": [],
    }
    input_path = tmp_path / "envelope.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    output_path = tmp_path / "validate.json"
    code = contracts_main(["validate-sync-record", "--input", str(input_path), "--output", str(output_path)])
    assert code == 0
    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["counts"]["contacts"] == 0


def test_contracts_validate_sync_record_cli_rejects_invalid_payload(tmp_path):
    input_path = tmp_path / "bad-envelope.json"
    input_path.write_text(json.dumps({"contract_version": "bad"}), encoding="utf-8")
    output_path = tmp_path / "validate.json"
    code = contracts_main(["validate-sync-record", "--input", str(input_path), "--output", str(output_path)])
    assert code == 1
    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert result["ok"] is False


def test_installer_stage_cli(tmp_path):
    probe_path = tmp_path / "probe.json"
    bundle_dir = tmp_path / "bundle"
    stage_dir = tmp_path / "stage"
    _write_probe(probe_path)
    _write_bundle(bundle_dir)
    output_path = tmp_path / "stage-output.json"
    code = installer_main(
        [
            "stage",
            "--bundle-dir",
            str(bundle_dir),
            "--probe",
            str(probe_path),
            "--stage-dir",
            str(stage_dir),
            "--enable-ha-bridge",
            "--output",
            str(output_path),
        ]
    )
    assert code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["ready"] is True
    assert (stage_dir / "install-plan.json").exists()
    assert (stage_dir / "install-receipt.json").exists()
    assert (stage_dir / "install-state.json").exists()
    assert (stage_dir / "config" / "uhome.json").exists()
    assert (stage_dir / "components" / "jellyfin" / "payload.tar.gz").exists()


def test_installer_execute_stage_cli(tmp_path):
    probe_path = tmp_path / "probe.json"
    bundle_dir = tmp_path / "bundle"
    stage_dir = tmp_path / "stage"
    target_root = tmp_path / "target"
    _write_probe(probe_path)
    _write_bundle(bundle_dir)
    stage_code = installer_main(
        [
            "stage",
            "--bundle-dir",
            str(bundle_dir),
            "--probe",
            str(probe_path),
            "--stage-dir",
            str(stage_dir),
            "--enable-ha-bridge",
        ]
    )
    assert stage_code == 0
    output_path = tmp_path / "execute-output.json"
    code = installer_main(
        [
            "execute-stage",
            "--stage-dir",
            str(stage_dir),
            "--target-root",
            str(target_root),
            "--output",
            str(output_path),
        ]
    )
    assert code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["success"] is True
    assert (target_root / "receipts" / "install-receipt.json").exists()
    assert (target_root / "systemd" / "system" / "jellyfin.service").exists()
    assert (target_root / "etc" / "uhome" / "jellyfin.env").exists()


def test_installer_apply_and_rollback_cli(tmp_path):
    probe_path = tmp_path / "probe.json"
    bundle_dir = tmp_path / "bundle"
    stage_dir = tmp_path / "stage"
    target_root = tmp_path / "target"
    host_root = tmp_path / "host"
    _write_probe(probe_path)
    _write_bundle(bundle_dir)
    assert installer_main(
        ["stage", "--bundle-dir", str(bundle_dir), "--probe", str(probe_path), "--stage-dir", str(stage_dir)]
    ) == 0
    assert installer_main(["execute-stage", "--stage-dir", str(stage_dir), "--target-root", str(target_root)]) == 0

    original_env = host_root / "etc" / "uhome" / "jellyfin.env"
    original_env.parent.mkdir(parents=True, exist_ok=True)
    original_env.write_text('JELLYFIN_DATA_DIR="/srv/original"\n', encoding="utf-8")

    apply_output = tmp_path / "apply-output.json"
    assert installer_main(
        ["apply-target", "--target-root", str(target_root), "--host-root", str(host_root), "--output", str(apply_output)]
    ) == 0
    apply_payload = json.loads(apply_output.read_text(encoding="utf-8"))
    assert apply_payload["success"] is True
    assert (host_root / "etc" / "systemd" / "system" / "jellyfin.service").exists()
    assert Path(apply_payload["result"]["ubuntu_apply_plan_path"]).exists()

    rollback_output = tmp_path / "rollback-output.json"
    assert installer_main(["rollback-target", "--host-root", str(host_root), "--output", str(rollback_output)]) == 0
    rollback_payload = json.loads(rollback_output.read_text(encoding="utf-8"))
    assert rollback_payload["success"] is True
    assert 'JELLYFIN_DATA_DIR="/srv/original"' in original_env.read_text(encoding="utf-8")

    verify_output = tmp_path / "verify-output.json"
    assert installer_main(["apply-target", "--target-root", str(target_root), "--host-root", str(host_root)]) == 0
    verify_code = installer_main(["verify-target", "--host-root", str(host_root), "--output", str(verify_output)])
    assert verify_code == 0
    verify_payload = json.loads(verify_output.read_text(encoding="utf-8"))
    assert verify_payload["success"] is True
    assert verify_payload["result"]["checks"]["service_units"]["ok"] is True
    apply_receipt = json.loads(apply_output.read_text(encoding="utf-8"))
    assert apply_receipt["result"]["upgrade_diff"]["added"] == ["jellyfin"]

    health_output = tmp_path / "health-output.json"

    def _runner(command, shell, text, capture_output):
        del shell, text, capture_output
        return type("_Completed", (), {"returncode": 0, "stdout": f"ok: {command}", "stderr": ""})()

    with patch("uhome_server.installer.health.subprocess.run", side_effect=_runner):
        health_code = installer_main(["health-check-target", "--host-root", str(host_root), "--output", str(health_output)])
    assert health_code == 0
    health_payload = json.loads(health_output.read_text(encoding="utf-8"))
    assert health_payload["success"] is True
    assert any(item["service"] == "jellyfin" for item in health_payload["result"]["checks"])

    live_apply_output = tmp_path / "live-apply-output.json"
    dry_run_code = installer_main(["apply-live", "--host-root", str(host_root), "--output", str(live_apply_output)])
    assert dry_run_code == 0
    dry_run_payload = json.loads(live_apply_output.read_text(encoding="utf-8"))
    assert dry_run_payload["success"] is True
    assert dry_run_payload["result"]["execute"] is False

    with patch("uhome_server.installer.live_apply.subprocess.run", side_effect=_runner):
        live_code = installer_main(
            ["apply-live", "--host-root", str(host_root), "--execute", "--output", str(live_apply_output)]
        )
    assert live_code == 0
    live_payload = json.loads(live_apply_output.read_text(encoding="utf-8"))
    assert live_payload["success"] is True
    assert live_payload["result"]["execute"] is True
