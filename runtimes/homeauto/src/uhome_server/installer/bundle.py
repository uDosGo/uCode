"""uHOME bundle artifact contract."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

BUNDLE_MANIFEST_FILENAME = "uhome-bundle.json"
ROLLBACK_FILENAME = "rollback.json"
BUNDLE_SCHEMA_VERSION = "1.0"
UHOME_COMPONENT_IDS = ["jellyfin", "comskip", "hdhomerun_config", "udos_uhome"]


@dataclass
class UHOMEHostProfileRef:
    profile_id: str
    display_name: str
    boot_mode: str
    target_roles: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class UHOMEBundleComponent:
    component_id: str
    display_name: str
    version: str
    artifact_path: str
    sha256: str
    install_target: str
    optional: bool = False


@dataclass
class UHOMERollbackRecord:
    rollback_token: str
    snapshot_paths: list[str] = field(default_factory=list)
    pre_install_hashes: dict[str, str] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UHOMERollbackRecord":
        return cls(
            rollback_token=data["rollback_token"],
            snapshot_paths=data.get("snapshot_paths", []),
            pre_install_hashes=data.get("pre_install_hashes", {}),
            notes=data.get("notes", ""),
        )


@dataclass
class UHOMEBundleManifest:
    bundle_id: str
    uhome_version: str
    sonic_version: str
    schema_version: str
    created_at: str
    host_profile: UHOMEHostProfileRef | None = None
    components: list[UHOMEBundleComponent] = field(default_factory=list)
    rollback_token: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UHOMEBundleManifest":
        components = [UHOMEBundleComponent(**component) for component in data.get("components", [])]
        host_profile_data = data.get("host_profile")
        return cls(
            bundle_id=data["bundle_id"],
            uhome_version=data["uhome_version"],
            sonic_version=data["sonic_version"],
            schema_version=data.get("schema_version", BUNDLE_SCHEMA_VERSION),
            created_at=data["created_at"],
            host_profile=None if not isinstance(host_profile_data, dict) else UHOMEHostProfileRef(**host_profile_data),
            components=components,
            rollback_token=data.get("rollback_token", ""),
            notes=data.get("notes", ""),
        )


def compute_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checksum(path: Path, expected: str) -> bool:
    return path.exists() and compute_checksum(path) == expected


def write_bundle_manifest(bundle_dir: Path, manifest: UHOMEBundleManifest) -> Path:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    out = bundle_dir / BUNDLE_MANIFEST_FILENAME
    out.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
    return out


def read_bundle_manifest(bundle_dir: Path) -> UHOMEBundleManifest | None:
    path = bundle_dir / BUNDLE_MANIFEST_FILENAME
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return UHOMEBundleManifest.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return None


def write_rollback_record(bundle_dir: Path, record: UHOMERollbackRecord) -> Path:
    rollback_dir = bundle_dir / "rollback"
    rollback_dir.mkdir(parents=True, exist_ok=True)
    out = rollback_dir / ROLLBACK_FILENAME
    out.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
    return out


def read_rollback_record(bundle_dir: Path) -> UHOMERollbackRecord | None:
    path = bundle_dir / "rollback" / ROLLBACK_FILENAME
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return UHOMERollbackRecord.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return None


@dataclass
class BundleVerifyResult:
    valid: bool
    missing: list[str] = field(default_factory=list)
    corrupt: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def verify_bundle(manifest: UHOMEBundleManifest, bundle_dir: Path) -> BundleVerifyResult:
    missing: list[str] = []
    corrupt: list[str] = []
    warnings: list[str] = []
    if manifest.host_profile is None:
        warnings.append("Bundle manifest does not declare a host_profile; default profile resolution will be used.")
    for component in manifest.components:
        artifact = bundle_dir / component.artifact_path
        if not artifact.exists():
            if component.optional:
                warnings.append(
                    f"Optional component '{component.component_id}' artifact not found: {component.artifact_path}"
                )
            else:
                missing.append(component.component_id)
            continue
        if component.sha256 and not verify_checksum(artifact, component.sha256):
            corrupt.append(component.component_id)
    return BundleVerifyResult(valid=(not missing and not corrupt), missing=missing, corrupt=corrupt, warnings=warnings)
