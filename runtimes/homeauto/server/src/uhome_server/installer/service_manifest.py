"""Typed service-manifest contract for staged uHOME installer flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from uhome_server.installer.linux_assets import LinuxServiceAsset


@dataclass(frozen=True)
class StagedServiceRecord:
    service_name: str
    asset: LinuxServiceAsset
    source_config: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "service_name": self.service_name,
            "asset": self.asset.to_dict(),
            "source_config": self.source_config,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StagedServiceRecord":
        service_name = str(payload.get("service_name") or "").strip()
        asset_payload = payload.get("asset")
        if not service_name:
            raise ValueError("service_name is required in staged service record")
        if not isinstance(asset_payload, dict):
            raise ValueError(f"asset is required for staged service record '{service_name}'")
        return cls(
            service_name=service_name,
            asset=LinuxServiceAsset.from_dict(asset_payload),
            source_config=str(payload.get("source_config") or ""),
        )


@dataclass(frozen=True)
class StagedServiceManifest:
    services: list[StagedServiceRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"services": [service.to_dict() for service in self.services]}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StagedServiceManifest":
        services_payload = payload.get("services", [])
        if not isinstance(services_payload, list):
            raise ValueError("services must be a list in staged service manifest")
        return cls(
            services=[
                StagedServiceRecord.from_dict(item)
                for item in services_payload
                if isinstance(item, dict)
            ]
        )

    @classmethod
    def read(cls, path: Path) -> "StagedServiceManifest":
        import json

        if not path.exists():
            raise ValueError(f"Service manifest does not exist: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Expected JSON object in {path}")
        return cls.from_dict(payload)

    def write(self, path: Path) -> Path:
        import json

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
        return path
