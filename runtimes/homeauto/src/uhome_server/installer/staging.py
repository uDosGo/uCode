"""Materialize staged installer artifacts for standalone uHOME installs."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from uhome_server.config import utc_now_iso_z
from uhome_server.installer.bundle import (
    UHOMEBundleManifest,
    UHOMERollbackRecord,
    read_bundle_manifest,
    read_rollback_record,
    write_rollback_record,
)
from uhome_server.installer.linux_assets import LinuxServiceAsset, service_asset
from uhome_server.installer.plan import UHOMEInstallOptions, UHOMEInstallPlan, build_uhome_install_plan
from uhome_server.installer.service_manifest import StagedServiceManifest, StagedServiceRecord


@dataclass(frozen=True)
class UHOMEStagedArtifacts:
    stage_dir: Path
    plan_path: Path
    service_manifest_path: Path
    receipt_path: Path
    state_path: Path
    copied_artifacts: list[str]
    config_paths: list[str]
    rollback_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_dir": str(self.stage_dir),
            "plan_path": str(self.plan_path),
            "service_manifest_path": str(self.service_manifest_path),
            "receipt_path": str(self.receipt_path),
            "state_path": str(self.state_path),
            "copied_artifacts": self.copied_artifacts,
            "config_paths": self.config_paths,
            "rollback_path": None if self.rollback_path is None else str(self.rollback_path),
        }


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def _copy_bundle_artifacts(manifest: UHOMEBundleManifest, bundle_dir: Path, stage_dir: Path) -> list[str]:
    copied: list[str] = []
    for component in manifest.components:
        source = bundle_dir / component.artifact_path
        target = stage_dir / "components" / component.component_id / Path(component.artifact_path).name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(str(target))
    return copied


def _write_config_artifacts(stage_dir: Path, manifest: UHOMEBundleManifest, opts: UHOMEInstallOptions) -> list[str]:
    config_dir = stage_dir / "config"
    config_paths = [
        _write_json(
            config_dir / "uhome.json",
            {
                "install_root": opts.install_root,
                "uhome_version": manifest.uhome_version,
                "sonic_version": manifest.sonic_version,
                "enable_ha_bridge": opts.enable_ha_bridge,
                "enable_autologin_kiosk": opts.enable_autologin_kiosk,
                "kiosk_user": opts.kiosk_user,
            },
        ),
        _write_json(
            config_dir / "jellyfin.json",
            {
                "install_root": opts.install_root,
                "service_name": "jellyfin",
                "component_id": "jellyfin",
            },
        ),
        _write_json(
            config_dir / "comskip.json",
            {
                "install_root": opts.install_root,
                "service_name": "comskip",
                "component_id": "comskip",
            },
        ),
        _write_json(
            config_dir / "uhome-dvr.json",
            {
                "install_root": opts.install_root,
                "service_name": "uhome-dvr",
                "component_id": "udos_uhome",
            },
        ),
    ]
    if opts.enable_ha_bridge:
        config_paths.append(
            _write_json(
                config_dir / "home-assistant-bridge.json",
                {
                    "install_root": opts.install_root,
                    "service_name": "uhome-ha-bridge",
                    "enabled": True,
                },
            )
        )
    if opts.enable_autologin_kiosk:
        config_paths.append(
            _write_json(
                config_dir / "uhome-kiosk.json",
                {
                    "install_root": opts.install_root,
                    "service_name": "uhome-kiosk",
                    "component_id": "udos_uhome",
                    "kiosk_user": opts.kiosk_user,
                },
            )
        )
    return [str(path) for path in config_paths]


def _write_service_manifest(stage_dir: Path, config_paths: list[str]) -> Path:
    services: list[StagedServiceRecord] = []
    for config_path_str in sorted(config_paths):
        payload = _read_json(Path(config_path_str))
        service_name = str(payload.get("service_name") or "").strip()
        if not service_name:
            continue
        asset = service_asset(service_name, str(payload.get("install_root", "/opt/uhome")))
        merged_environment = {**asset.environment}
        for key, value in payload.items():
            if key in {"service_name", "component_id"}:
                continue
            merged_environment[key.upper()] = value
        merged_asset = replace(asset, environment=merged_environment)
        services.append(
            StagedServiceRecord(
                service_name=service_name,
                asset=merged_asset,
                source_config=Path(config_path_str).name,
            )
        )
    manifest = StagedServiceManifest(services=services)
    return manifest.write(stage_dir / "service-manifest.json")


def _storage_identity_evidence(probe: dict[str, Any], host_profile_id: str | None) -> dict[str, Any]:
    return {
        "host_profile_id": host_profile_id,
        "os_disk_id": probe.get("os_disk_id"),
        "windows_disk_id": probe.get("windows_disk_id"),
        "media_volume_ids": list(probe.get("media_volume_ids", []))
        if isinstance(probe.get("media_volume_ids"), list)
        else [],
        "game_storage_gb": probe.get("game_storage_gb"),
        "complete": bool(probe.get("os_disk_id"))
        and (
            not host_profile_id == "dual-boot-steam-node" or bool(probe.get("windows_disk_id"))
        )
        and isinstance(probe.get("media_volume_ids"), list)
        and bool(probe.get("media_volume_ids")),
    }


def _write_install_receipt(
    stage_dir: Path,
    manifest: UHOMEBundleManifest,
    plan: UHOMEInstallPlan,
    opts: UHOMEInstallOptions,
    probe: dict[str, Any],
    rollback: UHOMERollbackRecord | None,
) -> Path:
    return _write_json(
        stage_dir / "install-receipt.json",
        {
            "generated_at": utc_now_iso_z(),
            "bundle_id": manifest.bundle_id,
            "uhome_version": manifest.uhome_version,
            "sonic_version": manifest.sonic_version,
            "install_root": opts.install_root,
            "dry_run": opts.dry_run,
            "ready": plan.ready,
            "host_profile_id": plan.host_profile_id,
            "host_profile": None
            if manifest.host_profile is None
            else {
                "profile_id": manifest.host_profile.profile_id,
                "display_name": manifest.host_profile.display_name,
                "boot_mode": manifest.host_profile.boot_mode,
                "target_roles": list(manifest.host_profile.target_roles),
                "notes": manifest.host_profile.notes,
            },
            "preflight": {
                "profile_id": plan.preflight_result.profile_id,
                "profile_label": plan.preflight_result.profile_label,
                "issues": list(plan.preflight_result.issues),
                "warnings": list(plan.preflight_result.warnings),
                "capability_checks": dict(plan.preflight_result.capability_checks),
            },
            "rollback_evidence": {
                "rollback_supported": rollback is not None or bool(manifest.rollback_token),
                "rollback_token": rollback.rollback_token if rollback is not None else manifest.rollback_token,
                "snapshot_paths": [] if rollback is None else list(rollback.snapshot_paths),
            },
            "storage_identity_evidence": _storage_identity_evidence(probe, plan.host_profile_id),
            "component_ids": [component.component_id for component in manifest.components],
            "components": [
                {
                    "component_id": component.component_id,
                    "version": component.version,
                    "install_target": component.install_target,
                    "artifact_path": component.artifact_path,
                }
                for component in manifest.components
            ],
        },
    )


def _write_install_state(stage_dir: Path, plan: UHOMEInstallPlan) -> Path:
    return _write_json(
        stage_dir / "install-state.json",
        {
            "generated_at": utc_now_iso_z(),
            "ready": plan.ready,
            "bundle_dir": plan.bundle_dir,
            "host_profile_id": plan.host_profile_id,
            "steps": [
                {
                    "phase": step.phase.value,
                    "action": step.action,
                    "blocking": step.blocking,
                    "status": "staged",
                }
                for step in plan.steps
            ],
        },
    )


def _stage_rollback(stage_dir: Path, bundle_dir: Path, manifest: UHOMEBundleManifest) -> Path | None:
    rollback = read_rollback_record(bundle_dir)
    if rollback is None and manifest.rollback_token:
        rollback = UHOMERollbackRecord(rollback_token=manifest.rollback_token)
    if rollback is None:
        return None
    return write_rollback_record(stage_dir, rollback)


def stage_install_artifacts(
    bundle_dir: Path,
    stage_dir: Path,
    probe: dict[str, Any],
    opts: UHOMEInstallOptions | None = None,
) -> tuple[UHOMEInstallPlan, UHOMEStagedArtifacts]:
    opts = opts or UHOMEInstallOptions()
    rollback = read_rollback_record(bundle_dir)
    plan = build_uhome_install_plan(bundle_dir, probe, opts, rollback=rollback)
    if not plan.ready:
        raise ValueError("Install plan is not ready; staging requires passing preflight and a valid bundle.")

    manifest = read_bundle_manifest(bundle_dir)
    if manifest is None:
        raise ValueError("Bundle manifest missing; cannot stage installer artifacts.")

    stage_dir.mkdir(parents=True, exist_ok=True)
    plan_path = _write_json(stage_dir / "install-plan.json", plan.to_dict())
    copied_artifacts = _copy_bundle_artifacts(manifest, bundle_dir, stage_dir)
    config_paths = _write_config_artifacts(stage_dir, manifest, opts)
    service_manifest_path = _write_service_manifest(stage_dir, config_paths)
    receipt_path = _write_install_receipt(stage_dir, manifest, plan, opts, probe, rollback)
    state_path = _write_install_state(stage_dir, plan)
    rollback_path = _stage_rollback(stage_dir, bundle_dir, manifest)
    return plan, UHOMEStagedArtifacts(
        stage_dir=stage_dir,
        plan_path=plan_path,
        service_manifest_path=service_manifest_path,
        receipt_path=receipt_path,
        state_path=state_path,
        copied_artifacts=copied_artifacts,
        config_paths=config_paths,
        rollback_path=rollback_path,
    )
