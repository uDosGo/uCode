"""Execute staged uHOME installer artifacts into a target root."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from uhome_server.config import utc_now_iso_z
from uhome_server.installer.linux_assets import render_environment_file, render_service_unit
from uhome_server.installer.service_manifest import StagedServiceManifest


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _sanitize_unit_name(name: str) -> str:
    return name.strip().replace("/", "-")


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _enable_service(unit_path: Path, wants_dir: Path) -> Path:
    wants_dir.mkdir(parents=True, exist_ok=True)
    link_path = wants_dir / unit_path.name
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
    os.symlink(unit_path, link_path)
    return link_path


@dataclass(frozen=True)
class ExecutionResult:
    stage_dir: Path
    target_root: Path
    installed_components: list[str]
    config_paths: list[str]
    environment_paths: list[str]
    service_unit_paths: list[str]
    enabled_service_links: list[str]
    service_manifest_path: Path | None
    receipt_path: Path
    state_path: Path
    rollback_path: Path | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_dir": str(self.stage_dir),
            "target_root": str(self.target_root),
            "installed_components": self.installed_components,
            "config_paths": self.config_paths,
            "environment_paths": self.environment_paths,
            "service_unit_paths": self.service_unit_paths,
            "enabled_service_links": self.enabled_service_links,
            "service_manifest_path": None if self.service_manifest_path is None else str(self.service_manifest_path),
            "receipt_path": str(self.receipt_path),
            "state_path": str(self.state_path),
            "rollback_path": None if self.rollback_path is None else str(self.rollback_path),
        }


def _read_service_manifest(stage_dir: Path) -> StagedServiceManifest:
    manifest_path = stage_dir / "service-manifest.json"
    return StagedServiceManifest.read(manifest_path)


def execute_staged_install(stage_dir: Path, target_root: Path) -> ExecutionResult:
    plan = _read_json(stage_dir / "install-plan.json")
    if not plan.get("ready", False):
        raise ValueError("Staged install plan is not ready.")

    receipt = _read_json(stage_dir / "install-receipt.json")
    config_dir = stage_dir / "config"
    components_dir = stage_dir / "components"
    rollback_source = stage_dir / "rollback" / "rollback.json"

    install_root = target_root / "install-root"
    state_root = target_root / "state"
    config_root = target_root / "config"
    env_root = target_root / "etc" / "uhome"
    services_root = target_root / "systemd" / "system"
    wants_multi_root = target_root / "systemd" / "multi-user.target.wants"
    wants_graphical_root = target_root / "systemd" / "graphical.target.wants"
    bin_root = target_root / "bin"
    receipts_root = target_root / "receipts"
    rollback_root = target_root / "rollback"
    for path in (install_root, state_root, config_root, env_root, services_root, receipts_root, bin_root):
        path.mkdir(parents=True, exist_ok=True)

    installed_components: list[str] = []
    if components_dir.exists():
        for component_dir in sorted(components_dir.iterdir(), key=lambda item: item.name):
            if not component_dir.is_dir():
                continue
            target_component_dir = install_root / component_dir.name
            target_component_dir.mkdir(parents=True, exist_ok=True)
            for artifact in sorted(component_dir.iterdir(), key=lambda item: item.name):
                shutil.copy2(artifact, target_component_dir / artifact.name)
            installed_components.append(component_dir.name)

    config_paths: list[str] = []
    environment_paths: list[str] = []
    service_unit_paths: list[str] = []
    enabled_service_links: list[str] = []
    if config_dir.exists():
        for config_path in sorted(config_dir.glob("*.json")):
            payload = _read_json(config_path)
            target_config = config_root / config_path.name
            _write_json(target_config, payload)
            config_paths.append(str(target_config))

    service_manifest = _read_service_manifest(stage_dir)
    service_names = sorted({record.service_name for record in service_manifest.services})
    for record in sorted(service_manifest.services, key=lambda item: item.service_name):
        asset = record.asset
        env_path = _write_text(
            env_root / f"{_sanitize_unit_name(asset.service_name)}.env",
            render_environment_file(asset.environment),
        )
        environment_paths.append(str(env_path))
        unit_path = _write_text(
            services_root / f"{_sanitize_unit_name(asset.service_name)}.service",
            render_service_unit(asset),
        )
        service_unit_paths.append(str(unit_path))
        wants_root = wants_graphical_root if asset.wanted_by == "graphical.target" else wants_multi_root
        enabled_link = _enable_service(unit_path, wants_root)
        enabled_service_links.append(str(enabled_link))

    _write_text(
        bin_root / "systemctl-apply.sh",
        "\n".join(
            [
                "#!/usr/bin/env sh",
                "set -eu",
                f'SYSTEMD_ROOT="{services_root.parent}"',
                'echo "systemctl daemon-reload"',
                f'echo "systemctl enable {" ".join(sorted(set(service_names)))}"',
                f'echo "systemctl restart {" ".join(sorted(set(service_names)))}"',
                "",
            ]
        ),
    )

    receipt_payload = {
        **receipt,
        "executed_at": utc_now_iso_z(),
        "target_root": str(target_root),
        "installed_components": installed_components,
        "environment_paths": environment_paths,
        "service_unit_paths": service_unit_paths,
        "enabled_service_links": enabled_service_links,
    }
    receipt_path = _write_json(receipts_root / "install-receipt.json", receipt_payload)
    source_service_manifest = stage_dir / "service-manifest.json"
    service_manifest_path = receipts_root / "service-manifest.json"
    shutil.copy2(source_service_manifest, service_manifest_path)

    state_path = _write_json(
        state_root / "install-state.json",
        {
            "executed_at": utc_now_iso_z(),
            "stage_dir": str(stage_dir),
            "target_root": str(target_root),
            "status": "installed",
            "installed_components": installed_components,
            "environment_paths": environment_paths,
            "service_unit_paths": service_unit_paths,
            "enabled_service_links": enabled_service_links,
            "plan_steps": plan.get("steps", []),
        },
    )

    rollback_path = None
    if rollback_source.exists():
        rollback_root.mkdir(parents=True, exist_ok=True)
        rollback_path = rollback_root / "rollback.json"
        shutil.copy2(rollback_source, rollback_path)

    return ExecutionResult(
        stage_dir=stage_dir,
        target_root=target_root,
        installed_components=installed_components,
        config_paths=config_paths,
        environment_paths=environment_paths,
        service_unit_paths=service_unit_paths,
        enabled_service_links=enabled_service_links,
        service_manifest_path=service_manifest_path,
        receipt_path=receipt_path,
        state_path=state_path,
        rollback_path=rollback_path,
    )
