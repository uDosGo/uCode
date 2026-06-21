"""uHOME install-plan builder."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from uhome_server.installer.bundle import (
    BundleVerifyResult,
    UHOMEBundleManifest,
    UHOMERollbackRecord,
    read_bundle_manifest,
    verify_bundle,
)
from uhome_server.installer.preflight import (
    DEFAULT_PROFILE,
    get_host_profile,
    UHOMEHardwareProfile,
    UHOMEPreflightResult,
    preflight_check,
)


class InstallPhase(str, Enum):
    PREFLIGHT = "preflight"
    VERIFY = "verify"
    STAGE = "stage"
    CONFIGURE = "configure"
    ENABLE = "enable"
    FINALIZE = "finalize"


@dataclass
class UHOMEInstallStep:
    phase: InstallPhase
    action: str
    description: str
    params: dict[str, Any] = field(default_factory=dict)
    blocking: bool = True


@dataclass
class UHOMEInstallPlan:
    bundle_dir: str
    dry_run: bool
    preflight_result: UHOMEPreflightResult
    verify_result: BundleVerifyResult | None
    host_profile_id: str | None = None
    steps: list[UHOMEInstallStep] = field(default_factory=list)
    ready: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_dir": self.bundle_dir,
            "dry_run": self.dry_run,
            "ready": self.ready,
            "host_profile_id": self.host_profile_id,
            "preflight": self.preflight_result.to_dict(),
            "verify": None
            if self.verify_result is None
            else {
                "valid": self.verify_result.valid,
                "missing": self.verify_result.missing,
                "corrupt": self.verify_result.corrupt,
                "warnings": self.verify_result.warnings,
            },
            "steps": [
                {
                    "phase": step.phase.value,
                    "action": step.action,
                    "description": step.description,
                    "params": step.params,
                    "blocking": step.blocking,
                }
                for step in self.steps
            ],
        }


@dataclass
class UHOMEInstallOptions:
    install_root: str = "/opt/uhome"
    enable_autologin_kiosk: bool = True
    kiosk_user: str = "uhome"
    enable_ha_bridge: bool = False
    dry_run: bool = False


def _preflight_steps(result: UHOMEPreflightResult) -> list[UHOMEInstallStep]:
    return [
        UHOMEInstallStep(
            phase=InstallPhase.PREFLIGHT,
            action="hardware_preflight",
            description="Validate target hardware against uHOME minimum profile.",
            params={"passed": result.passed, "issues": result.issues, "warnings": result.warnings},
        )
    ]


def _verify_steps(manifest: UHOMEBundleManifest, result: BundleVerifyResult) -> list[UHOMEInstallStep]:
    host_profile_id = manifest.host_profile.profile_id if manifest.host_profile is not None else None
    return [
        UHOMEInstallStep(
            phase=InstallPhase.VERIFY,
            action="verify_bundle_checksums",
            description=f"Verify SHA-256 checksums for {len(manifest.components)} bundle component(s).",
            params={
                "valid": result.valid,
                "missing": result.missing,
                "corrupt": result.corrupt,
                "component_count": len(manifest.components),
                "host_profile_id": host_profile_id,
            },
        )
    ]


def _stage_steps(manifest: UHOMEBundleManifest, bundle_dir: Path) -> list[UHOMEInstallStep]:
    return [
        UHOMEInstallStep(
            phase=InstallPhase.STAGE,
            action="stage_component",
            description=f"Stage {component.display_name} v{component.version} -> {component.install_target}",
            params={
                "component_id": component.component_id,
                "source": str(bundle_dir / component.artifact_path),
                "target": component.install_target,
                "sha256": component.sha256,
            },
            blocking=not component.optional,
        )
        for component in manifest.components
    ]


def _configure_steps(manifest: UHOMEBundleManifest, opts: UHOMEInstallOptions) -> list[UHOMEInstallStep]:
    host_profile_id = manifest.host_profile.profile_id if manifest.host_profile is not None else None
    steps = [
        UHOMEInstallStep(
            phase=InstallPhase.CONFIGURE,
            action="write_uhome_config",
            description="Write uHOME service configuration files.",
            params={
                "install_root": opts.install_root,
                "uhome_version": manifest.uhome_version,
                "ha_bridge_enabled": opts.enable_ha_bridge,
                "host_profile_id": host_profile_id,
            },
        ),
        UHOMEInstallStep(
            phase=InstallPhase.CONFIGURE,
            action="write_jellyfin_config",
            description="Write Jellyfin media server initial configuration.",
            params={"install_root": opts.install_root, "host_profile_id": host_profile_id},
        ),
        UHOMEInstallStep(
            phase=InstallPhase.CONFIGURE,
            action="write_comskip_config",
            description="Write Comskip ad-detection configuration.",
            params={"install_root": opts.install_root, "host_profile_id": host_profile_id},
        ),
    ]
    if opts.enable_ha_bridge:
        steps.append(
            UHOMEInstallStep(
                phase=InstallPhase.CONFIGURE,
                action="write_ha_bridge_config",
                description="Write Home Assistant bridge configuration.",
                params={"install_root": opts.install_root, "host_profile_id": host_profile_id},
            )
        )
    return steps


def _enable_steps(opts: UHOMEInstallOptions, manifest: UHOMEBundleManifest) -> list[UHOMEInstallStep]:
    host_profile_id = manifest.host_profile.profile_id if manifest.host_profile is not None else None
    steps = [
        UHOMEInstallStep(
            phase=InstallPhase.ENABLE,
            action="enable_jellyfin_service",
            description="Enable and start jellyfin.service via systemd.",
            params={"service": "jellyfin", "host_profile_id": host_profile_id},
        ),
        UHOMEInstallStep(
            phase=InstallPhase.ENABLE,
            action="enable_uhome_dvr_service",
            description="Enable uhome-dvr.service for recording integration.",
            params={"service": "uhome-dvr", "host_profile_id": host_profile_id},
        ),
    ]
    if host_profile_id == "dual-boot-steam-node":
        steps.append(
            UHOMEInstallStep(
                phase=InstallPhase.ENABLE,
                action="enable_steam_console_mode",
                description="Prepare dual-boot Steam console launch and host integration.",
                params={"service": "uhome-steam-console", "host_profile_id": host_profile_id},
            )
        )
    if opts.enable_autologin_kiosk:
        steps.append(
            UHOMEInstallStep(
                phase=InstallPhase.ENABLE,
                action="enable_kiosk_autologin",
                description=f"Configure autologin for user '{opts.kiosk_user}' and enable uhome-kiosk.service.",
                params={"kiosk_user": opts.kiosk_user, "service": "uhome-kiosk", "host_profile_id": host_profile_id},
            )
        )
    return steps


def _finalize_steps(manifest: UHOMEBundleManifest, rollback: UHOMERollbackRecord | None) -> list[UHOMEInstallStep]:
    steps = [
        UHOMEInstallStep(
            phase=InstallPhase.FINALIZE,
            action="write_install_receipt",
            description="Record install receipt with bundle and component versions.",
            params={"bundle_id": manifest.bundle_id, "uhome_version": manifest.uhome_version, "sonic_version": manifest.sonic_version},
        )
    ]
    if rollback:
        steps.append(
            UHOMEInstallStep(
                phase=InstallPhase.FINALIZE,
                action="commit_rollback_token",
                description="Persist rollback token so a failed install can be reversed.",
                params={"rollback_token": rollback.rollback_token},
            )
        )
    return steps


def build_uhome_install_plan(
    bundle_dir: Path,
    probe: dict[str, Any],
    opts: UHOMEInstallOptions | None = None,
    profile: UHOMEHardwareProfile = DEFAULT_PROFILE,
    rollback: UHOMERollbackRecord | None = None,
) -> UHOMEInstallPlan:
    opts = opts or UHOMEInstallOptions()
    manifest = read_bundle_manifest(bundle_dir)
    host_profile = None if manifest is None or manifest.host_profile is None else get_host_profile(manifest.host_profile.profile_id)
    preflight_result = preflight_check(probe, profile=profile, host_profile=host_profile)
    steps: list[UHOMEInstallStep] = []
    steps.extend(_preflight_steps(preflight_result))
    if not preflight_result.passed:
        return UHOMEInstallPlan(
            bundle_dir=str(bundle_dir),
            dry_run=opts.dry_run,
            preflight_result=preflight_result,
            verify_result=None,
            host_profile_id=None if manifest is None or manifest.host_profile is None else manifest.host_profile.profile_id,
            steps=steps,
            ready=False,
        )

    if manifest is None:
        steps.append(
            UHOMEInstallStep(
                phase=InstallPhase.VERIFY,
                action="read_bundle_manifest",
                description="Read bundle manifest.",
                params={"path": str(bundle_dir / "uhome-bundle.json")},
            )
        )
        return UHOMEInstallPlan(
            bundle_dir=str(bundle_dir),
            dry_run=opts.dry_run,
            preflight_result=preflight_result,
            verify_result=BundleVerifyResult(valid=False, missing=["uhome-bundle.json"]),
            host_profile_id=None,
            steps=steps,
            ready=False,
        )

    verify_result = verify_bundle(manifest, bundle_dir)
    steps.extend(_verify_steps(manifest, verify_result))
    if not verify_result.valid:
        return UHOMEInstallPlan(
            bundle_dir=str(bundle_dir),
            dry_run=opts.dry_run,
            preflight_result=preflight_result,
            verify_result=verify_result,
            host_profile_id=manifest.host_profile.profile_id if manifest.host_profile is not None else None,
            steps=steps,
            ready=False,
        )

    steps.extend(_stage_steps(manifest, bundle_dir))
    steps.extend(_configure_steps(manifest, opts))
    steps.extend(_enable_steps(opts, manifest))
    steps.extend(_finalize_steps(manifest, rollback))
    return UHOMEInstallPlan(
        bundle_dir=str(bundle_dir),
        dry_run=opts.dry_run,
        preflight_result=preflight_result,
        verify_result=verify_result,
        host_profile_id=manifest.host_profile.profile_id if manifest.host_profile is not None else None,
        steps=steps,
        ready=True,
    )
