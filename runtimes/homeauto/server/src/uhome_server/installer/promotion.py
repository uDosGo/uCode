"""Promote executed uHOME install assets onto a host-style filesystem layout."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from uhome_server.config import utc_now_iso_z
from uhome_server.installer.service_manifest import StagedServiceManifest


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _copy_tree(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination, symlinks=True)


@dataclass(frozen=True)
class PromotionResult:
    target_root: Path
    host_root: Path
    snapshot_root: Path
    promoted_paths: list[str]
    mode: str
    upgrade_diff: dict[str, Any]
    command_plan_path: Path
    ubuntu_apply_plan_path: Path
    health_check_plan_path: Path
    verification_path: Path
    receipt_path: Path
    state_path: Path

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_root": str(self.target_root),
            "host_root": str(self.host_root),
            "snapshot_root": str(self.snapshot_root),
            "promoted_paths": self.promoted_paths,
            "mode": self.mode,
            "upgrade_diff": self.upgrade_diff,
            "command_plan_path": str(self.command_plan_path),
            "ubuntu_apply_plan_path": str(self.ubuntu_apply_plan_path),
            "health_check_plan_path": str(self.health_check_plan_path),
            "verification_path": str(self.verification_path),
            "receipt_path": str(self.receipt_path),
            "state_path": str(self.state_path),
        }


@dataclass(frozen=True)
class RollbackResult:
    host_root: Path
    snapshot_root: Path
    restored_paths: list[str]
    state_path: Path

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_root": str(self.host_root),
            "snapshot_root": str(self.snapshot_root),
            "restored_paths": self.restored_paths,
            "state_path": str(self.state_path),
        }


@dataclass(frozen=True)
class VerificationResult:
    host_root: Path
    ok: bool
    checks: dict[str, Any]
    report_path: Path

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_root": str(self.host_root),
            "ok": self.ok,
            "checks": self.checks,
            "report_path": str(self.report_path),
        }


_PROMOTION_MAPPINGS: tuple[tuple[str, str], ...] = (
    ("install-root", "opt/uhome"),
    ("config", "opt/uhome/config"),
    ("etc/uhome", "etc/uhome"),
    ("systemd/system", "etc/systemd/system"),
    ("systemd/multi-user.target.wants", "etc/systemd/system/multi-user.target.wants"),
    ("systemd/graphical.target.wants", "etc/systemd/system/graphical.target.wants"),
    ("bin", "opt/uhome/bin"),
    ("receipts", "var/lib/uhome/receipts"),
    ("state", "var/lib/uhome/state"),
    ("rollback", "var/lib/uhome/rollback"),
)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def _service_names_from_target(target_root: Path) -> list[str]:
    system_root = target_root / "systemd" / "system"
    if not system_root.exists():
        return []
    return sorted(path.stem for path in system_root.glob("*.service"))


def _write_command_plan(host_root: Path, service_names: list[str]) -> Path:
    plan_path = host_root / "var" / "lib" / "uhome" / "systemctl-plan.sh"
    commands = [
        "#!/usr/bin/env sh",
        "set -eu",
        "systemctl daemon-reload",
    ]
    if service_names:
        joined = " ".join(service_names)
        commands.extend(
            [
                f"systemctl enable {joined}",
                f"systemctl restart {joined}",
                f"systemctl status {joined} --no-pager",
            ]
        )
    else:
        commands.append('echo "No uHOME services discovered to enable."')
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text("\n".join(commands) + "\n", encoding="utf-8")
    return plan_path


def _write_ubuntu_apply_plan(host_root: Path, service_names: list[str]) -> Path:
    plan_path = host_root / "var" / "lib" / "uhome" / "ubuntu-apply-plan.sh"
    commands = [
        "#!/usr/bin/env sh",
        "set -eu",
        f'HOST_ROOT="{host_root}"',
        'sudo mkdir -p /opt/uhome /etc/uhome /etc/systemd/system /var/lib/uhome',
        'sudo rsync -a --delete "$HOST_ROOT/opt/uhome/" "/opt/uhome/"',
        'sudo rsync -a --delete "$HOST_ROOT/etc/uhome/" "/etc/uhome/"',
        'sudo rsync -a --delete "$HOST_ROOT/etc/systemd/system/" "/etc/systemd/system/"',
        'sudo rsync -a --delete "$HOST_ROOT/var/lib/uhome/" "/var/lib/uhome/"',
        "sudo systemctl daemon-reload",
    ]
    if service_names:
        joined = " ".join(service_names)
        commands.extend(
            [
                f"sudo systemctl enable {joined}",
                f"sudo systemctl restart {joined}",
                f"sudo systemctl status {joined} --no-pager",
            ]
        )
    else:
        commands.append('echo "No uHOME services discovered to enable."')
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text("\n".join(commands) + "\n", encoding="utf-8")
    return plan_path


def _component_versions(payload: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(payload, dict):
        return {}
    components = payload.get("components", [])
    if not isinstance(components, list):
        return {}
    result: dict[str, str] = {}
    for item in components:
        if not isinstance(item, dict):
            continue
        component_id = str(item.get("component_id") or "").strip()
        version = str(item.get("version") or "").strip()
        if component_id:
            result[component_id] = version
    return result


def _compute_upgrade_diff(previous_receipt: dict[str, Any] | None, install_receipt: dict[str, Any]) -> dict[str, Any]:
    previous_versions = _component_versions(previous_receipt.get("install_receipt") if isinstance(previous_receipt, dict) else None)
    current_versions = _component_versions(install_receipt)
    added = sorted(component for component in current_versions if component not in previous_versions)
    removed = sorted(component for component in previous_versions if component not in current_versions)
    changed = sorted(
        component
        for component in current_versions
        if component in previous_versions and current_versions[component] != previous_versions[component]
    )
    unchanged = sorted(
        component
        for component in current_versions
        if component in previous_versions and current_versions[component] == previous_versions[component]
    )
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
        "previous_versions": previous_versions,
        "current_versions": current_versions,
    }


def _compute_reinstall_context(previous_receipt: dict[str, Any] | None, install_receipt: dict[str, Any]) -> dict[str, Any]:
    previous_install = previous_receipt.get("install_receipt") if isinstance(previous_receipt, dict) else None
    previous_bundle_id = None if not isinstance(previous_install, dict) else previous_install.get("bundle_id")
    previous_host_profile_id = None if not isinstance(previous_install, dict) else previous_install.get("host_profile_id")
    current_bundle_id = install_receipt.get("bundle_id")
    current_host_profile_id = install_receipt.get("host_profile_id")
    rollback_evidence = install_receipt.get("rollback_evidence", {})
    storage_identity_evidence = install_receipt.get("storage_identity_evidence", {})
    return {
        "previous_bundle_id": previous_bundle_id,
        "current_bundle_id": current_bundle_id,
        "same_bundle_id": previous_bundle_id == current_bundle_id if previous_bundle_id is not None else False,
        "previous_host_profile_id": previous_host_profile_id,
        "current_host_profile_id": current_host_profile_id,
        "same_host_profile_id": previous_host_profile_id == current_host_profile_id if previous_host_profile_id is not None else False,
        "rollback_supported": bool(isinstance(rollback_evidence, dict) and rollback_evidence.get("rollback_supported")),
        "storage_identity_complete": bool(
            isinstance(storage_identity_evidence, dict) and storage_identity_evidence.get("complete")
        ),
    }


def _read_service_manifest(path: Path) -> StagedServiceManifest:
    return StagedServiceManifest.read(path)


def _service_names_from_manifest(manifest: StagedServiceManifest) -> list[str]:
    return sorted({service.service_name for service in manifest.services})


def _write_health_check_plan(host_root: Path, manifest: StagedServiceManifest) -> Path:
    checks = []
    for service in manifest.services:
        checks.append(
            {
                "service": service.service_name,
                "health_check": service.asset.health_check,
            }
        )
    return _write_json(
        host_root / "var" / "lib" / "uhome" / "health-check-plan.json",
        {
            "generated_at": utc_now_iso_z(),
            "service_count": len(checks),
            "checks": checks,
        },
    )


def verify_promoted_target(host_root: Path) -> VerificationResult:
    service_root = host_root / "etc" / "systemd" / "system"
    env_root = host_root / "etc" / "uhome"
    receipt_root = host_root / "var" / "lib" / "uhome" / "receipts"
    state_root = host_root / "var" / "lib" / "uhome" / "state"
    install_receipt = _read_json(receipt_root / "install-receipt.json") if (receipt_root / "install-receipt.json").exists() else {}
    service_units = sorted(path.name for path in service_root.glob("*.service")) if service_root.exists() else []
    env_files = sorted(path.name for path in env_root.glob("*.env")) if env_root.exists() else []
    checks = {
        "service_units": {"ok": bool(service_units), "count": len(service_units), "items": service_units},
        "environment_files": {"ok": bool(env_files), "count": len(env_files), "items": env_files},
        "receipt_present": {"ok": (receipt_root / "install-receipt.json").exists()},
        "state_present": {"ok": (state_root / "install-state.json").exists()},
        "host_profile_present": {"ok": bool(install_receipt.get("host_profile_id"))},
        "rollback_evidence_present": {
            "ok": bool(isinstance(install_receipt.get("rollback_evidence"), dict)),
        },
        "storage_identity_evidence_present": {
            "ok": bool(isinstance(install_receipt.get("storage_identity_evidence"), dict) and install_receipt.get("storage_identity_evidence", {}).get("complete")),
        },
    }
    ok = all(item.get("ok", False) for item in checks.values())
    report_path = _write_json(
        host_root / "var" / "lib" / "uhome" / "verification-report.json",
        {
            "verified_at": utc_now_iso_z(),
            "host_root": str(host_root),
            "ok": ok,
            "checks": checks,
        },
    )
    return VerificationResult(host_root=host_root, ok=ok, checks=checks, report_path=report_path)


def promote_target_root(target_root: Path, host_root: Path) -> PromotionResult:
    if not target_root.exists():
        raise ValueError(f"Target root does not exist: {target_root}")
    snapshot_root = host_root / "var" / "lib" / "uhome" / "snapshots" / "latest"
    snapshot_root.mkdir(parents=True, exist_ok=True)
    prior_receipt_path = host_root / "var" / "lib" / "uhome" / "promotion-receipt.json"
    prior_receipt = _read_json(prior_receipt_path) if prior_receipt_path.exists() else None
    mode = "reapply" if prior_receipt is not None else "first_apply"

    promoted_paths: list[str] = []
    for source_rel, dest_rel in _PROMOTION_MAPPINGS:
        source = target_root / source_rel
        if not source.exists():
            continue
        destination = host_root / dest_rel
        snapshot = snapshot_root / dest_rel
        if destination.exists():
            if snapshot.exists():
                shutil.rmtree(snapshot)
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            if destination.is_dir():
                shutil.copytree(destination, snapshot, symlinks=True)
            else:
                shutil.copy2(destination, snapshot)
        if source.is_dir():
            _copy_tree(source, destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        promoted_paths.append(str(destination))

    service_manifest = _read_service_manifest(target_root / "receipts" / "service-manifest.json")
    service_names = _service_names_from_manifest(service_manifest)
    target_install_receipt = target_root / "receipts" / "install-receipt.json"
    target_install_state = target_root / "state" / "install-state.json"
    install_receipt = _read_json(target_install_receipt) if target_install_receipt.exists() else {}
    install_state = _read_json(target_install_state) if target_install_state.exists() else {}
    upgrade_diff = _compute_upgrade_diff(prior_receipt, install_receipt)
    reinstall_context = _compute_reinstall_context(prior_receipt, install_receipt)
    command_plan_path = _write_command_plan(host_root, service_names)
    ubuntu_apply_plan_path = _write_ubuntu_apply_plan(host_root, service_names)
    health_check_plan_path = _write_health_check_plan(host_root, service_manifest)
    verification = verify_promoted_target(host_root)

    receipt_path = _write_json(
        host_root / "var" / "lib" / "uhome" / "promotion-receipt.json",
        {
            "promoted_at": utc_now_iso_z(),
            "mode": mode,
            "target_root": str(target_root),
            "host_root": str(host_root),
            "snapshot_root": str(snapshot_root),
            "promoted_paths": promoted_paths,
            "previous_receipt": prior_receipt,
            "service_names": service_names,
            "upgrade_diff": upgrade_diff,
            "reinstall_context": reinstall_context,
            "command_plan_path": str(command_plan_path),
            "ubuntu_apply_plan_path": str(ubuntu_apply_plan_path),
            "health_check_plan_path": str(health_check_plan_path),
            "verification_path": str(verification.report_path),
            "install_receipt": install_receipt,
            "install_state": install_state,
        },
    )
    state_path = _write_json(
        host_root / "var" / "lib" / "uhome" / "promotion-state.json",
        {
            "status": "applied",
            "applied_at": utc_now_iso_z(),
            "mode": mode,
            "target_root": str(target_root),
            "snapshot_root": str(snapshot_root),
            "promoted_paths": promoted_paths,
            "service_names": service_names,
            "upgrade_diff": upgrade_diff,
            "reinstall_context": reinstall_context,
            "verification_ok": verification.ok,
        },
    )
    return PromotionResult(
        target_root=target_root,
        host_root=host_root,
        snapshot_root=snapshot_root,
        promoted_paths=promoted_paths,
        mode=mode,
        upgrade_diff=upgrade_diff,
        command_plan_path=command_plan_path,
        ubuntu_apply_plan_path=ubuntu_apply_plan_path,
        health_check_plan_path=health_check_plan_path,
        verification_path=verification.report_path,
        receipt_path=receipt_path,
        state_path=state_path,
    )


def rollback_promoted_target(host_root: Path) -> RollbackResult:
    snapshot_root = host_root / "var" / "lib" / "uhome" / "snapshots" / "latest"
    if not snapshot_root.exists():
        raise ValueError(f"Snapshot root does not exist: {snapshot_root}")

    restored_paths: list[str] = []
    for _, dest_rel in _PROMOTION_MAPPINGS:
        snapshot = snapshot_root / dest_rel
        destination = host_root / dest_rel
        if not snapshot.exists():
            continue
        if destination.exists():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        if snapshot.is_dir():
            _copy_tree(snapshot, destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(snapshot, destination)
        restored_paths.append(str(destination))

    state_path = _write_json(
        host_root / "var" / "lib" / "uhome" / "promotion-state.json",
        {
            "status": "rolled_back",
            "rolled_back_at": utc_now_iso_z(),
            "snapshot_root": str(snapshot_root),
            "restored_paths": restored_paths,
        },
    )
    return RollbackResult(
        host_root=host_root,
        snapshot_root=snapshot_root,
        restored_paths=restored_paths,
        state_path=state_path,
    )
