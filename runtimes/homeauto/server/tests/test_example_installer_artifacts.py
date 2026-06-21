from __future__ import annotations

import json
from pathlib import Path

from uhome_server.config import get_repo_root
from uhome_server.installer.bundle import read_bundle_manifest, verify_bundle
from uhome_server.installer.executor import execute_staged_install
from uhome_server.installer.plan import build_uhome_install_plan
from uhome_server.installer.promotion import promote_target_root, rollback_promoted_target
from uhome_server.installer.staging import stage_install_artifacts


def test_example_standalone_bundle_verifies():
    bundle_dir = get_repo_root() / "examples" / "installer" / "bundles" / "standalone"
    manifest = read_bundle_manifest(bundle_dir)
    assert manifest is not None
    result = verify_bundle(manifest, bundle_dir)
    assert result.valid is True
    assert manifest.host_profile is not None
    assert manifest.host_profile.profile_id == "standalone-linux"


def test_example_dual_boot_bundle_verifies():
    bundle_dir = get_repo_root() / "examples" / "installer" / "bundles" / "dual-boot"
    manifest = read_bundle_manifest(bundle_dir)
    assert manifest is not None
    result = verify_bundle(manifest, bundle_dir)
    assert result.valid is True
    assert manifest.host_profile is not None
    assert manifest.host_profile.profile_id == "dual-boot-steam-node"


def test_example_dual_boot_bundle_builds_dual_boot_plan():
    repo_root = get_repo_root()
    bundle_dir = repo_root / "examples" / "installer" / "bundles" / "dual-boot"
    probe_path = repo_root / "examples" / "installer" / "probes" / "dual-boot-steam-node.json"
    plan = build_uhome_install_plan(bundle_dir, json.loads(probe_path.read_text(encoding="utf-8")))
    assert plan.ready is True
    assert plan.host_profile_id == "dual-boot-steam-node"
    assert any(step.action == "enable_steam_console_mode" for step in plan.steps)


def test_example_standalone_flow_records_reinstall_context(tmp_path):
    repo_root = get_repo_root()
    bundle_dir = repo_root / "examples" / "installer" / "bundles" / "standalone"
    probe = json.loads((repo_root / "examples" / "installer" / "probes" / "standalone-linux.json").read_text(encoding="utf-8"))
    stage_dir = tmp_path / "stage"
    target_root = tmp_path / "target"
    host_root = tmp_path / "host"

    plan, staged = stage_install_artifacts(bundle_dir, stage_dir, probe)
    assert plan.ready is True
    receipt = json.loads(staged.receipt_path.read_text(encoding="utf-8"))
    assert receipt["storage_identity_evidence"]["complete"] is True

    execute_staged_install(stage_dir, target_root)
    first = promote_target_root(target_root, host_root)
    first_receipt = json.loads(first.receipt_path.read_text(encoding="utf-8"))
    assert first_receipt["reinstall_context"]["current_host_profile_id"] == "standalone-linux"
    assert first_receipt["reinstall_context"]["rollback_supported"] is True
    assert first_receipt["reinstall_context"]["storage_identity_complete"] is True

    second = promote_target_root(target_root, host_root)
    second_receipt = json.loads(second.receipt_path.read_text(encoding="utf-8"))
    assert second_receipt["reinstall_context"]["same_bundle_id"] is True
    assert second_receipt["reinstall_context"]["same_host_profile_id"] is True

    rollback = rollback_promoted_target(host_root)
    assert rollback.state_path.exists()


def test_example_dual_boot_flow_records_profile_evidence(tmp_path):
    repo_root = get_repo_root()
    bundle_dir = repo_root / "examples" / "installer" / "bundles" / "dual-boot"
    probe = json.loads((repo_root / "examples" / "installer" / "probes" / "dual-boot-steam-node.json").read_text(encoding="utf-8"))
    stage_dir = tmp_path / "stage"
    plan, staged = stage_install_artifacts(bundle_dir, stage_dir, probe)
    assert plan.ready is True
    assert plan.host_profile_id == "dual-boot-steam-node"
    receipt = json.loads(staged.receipt_path.read_text(encoding="utf-8"))
    assert receipt["host_profile"]["boot_mode"] == "dual-boot"
    assert receipt["preflight"]["capability_checks"]["dual_boot_disk_layout_present"]["passed"] is True
    assert receipt["storage_identity_evidence"]["windows_disk_id"] == "disk-windows-root-002"
