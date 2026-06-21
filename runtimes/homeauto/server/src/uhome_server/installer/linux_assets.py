"""Linux deployment assets for staged uHOME installs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class LinuxServiceAsset:
    service_name: str
    description: str
    after: tuple[str, ...]
    wants: tuple[str, ...]
    exec_start: str
    environment: dict[str, str]
    wanted_by: str = "multi-user.target"
    working_directory_var: str = "UHOME_INSTALL_ROOT"
    restart: str = "on-failure"
    health_check: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["after"] = list(self.after)
        payload["wants"] = list(self.wants)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LinuxServiceAsset":
        return cls(
            service_name=str(payload["service_name"]),
            description=str(payload["description"]),
            after=tuple(payload.get("after", [])),
            wants=tuple(payload.get("wants", [])),
            exec_start=str(payload["exec_start"]),
            environment={str(key): str(value) for key, value in dict(payload.get("environment", {})).items()},
            wanted_by=str(payload.get("wanted_by", "multi-user.target")),
            working_directory_var=str(payload.get("working_directory_var", "UHOME_INSTALL_ROOT")),
            restart=str(payload.get("restart", "on-failure")),
            health_check=payload.get("health_check") if isinstance(payload.get("health_check"), dict) else None,
        )


def _default_assets(install_root: str) -> dict[str, LinuxServiceAsset]:
    return {
        "jellyfin": LinuxServiceAsset(
            service_name="jellyfin",
            description="uHOME Jellyfin media service",
            after=("network-online.target",),
            wants=("network-online.target",),
            exec_start="/usr/bin/env sh -lc 'exec jellyfin --datadir \"$UHOME_INSTALL_ROOT/var/jellyfin\"'",
            environment={
                "UHOME_INSTALL_ROOT": install_root,
                "JELLYFIN_DATA_DIR": f"{install_root}/var/jellyfin",
            },
            health_check={
                "kind": "http",
                "target": "http://127.0.0.1:8096/health",
                "command": "curl --fail --silent http://127.0.0.1:8096/health",
            },
        ),
        "comskip": LinuxServiceAsset(
            service_name="comskip",
            description="uHOME Comskip processing worker",
            after=("network-online.target",),
            wants=("network-online.target",),
            exec_start="/usr/bin/env sh -lc 'exec comskip --ini=\"$UHOME_INSTALL_ROOT/etc/comskip.ini\"'",
            environment={
                "UHOME_INSTALL_ROOT": install_root,
                "COMSKIP_INI": f"{install_root}/etc/comskip.ini",
            },
            health_check={
                "kind": "process",
                "target": "comskip",
                "command": "systemctl is-active comskip",
            },
        ),
        "uhome-dvr": LinuxServiceAsset(
            service_name="uhome-dvr",
            description="uHOME DVR orchestration service",
            after=("network-online.target", "jellyfin.service"),
            wants=("network-online.target",),
            exec_start="/usr/bin/env sh -lc 'exec python3 -m uhome_server.app'",
            environment={
                "UHOME_INSTALL_ROOT": install_root,
                "PYTHONPATH": f"{install_root}/src",
                "UHOME_RUNTIME_MODE": "dvr",
            },
            health_check={
                "kind": "http",
                "target": "http://127.0.0.1:8000/api/runtime/ready",
                "command": "curl --fail --silent http://127.0.0.1:8000/api/runtime/ready",
            },
        ),
        "uhome-ha-bridge": LinuxServiceAsset(
            service_name="uhome-ha-bridge",
            description="uHOME Home Assistant bridge",
            after=("network-online.target",),
            wants=("network-online.target",),
            exec_start="/usr/bin/env sh -lc 'exec python3 -m uhome_server.services.home_assistant'",
            environment={
                "UHOME_INSTALL_ROOT": install_root,
                "PYTHONPATH": f"{install_root}/src",
                "HA_BRIDGE_ENABLED": "true",
            },
            health_check={
                "kind": "http",
                "target": "http://127.0.0.1:8123/health",
                "command": "curl --fail --silent http://127.0.0.1:8123/health",
            },
        ),
        "uhome-kiosk": LinuxServiceAsset(
            service_name="uhome-kiosk",
            description="uHOME kiosk launcher session",
            after=("graphical.target", "network-online.target"),
            wants=("graphical.target", "network-online.target"),
            exec_start="/usr/bin/env sh -lc 'exec steam -tenfoot'",
            environment={
                "UHOME_INSTALL_ROOT": install_root,
                "UHOME_PRESENTATION_MODE": "steam-console",
            },
            wanted_by="graphical.target",
            health_check={
                "kind": "process",
                "target": "steam",
                "command": "systemctl is-active uhome-kiosk",
            },
        ),
    }


def service_asset(service_name: str, install_root: str) -> LinuxServiceAsset:
    assets = _default_assets(install_root)
    if service_name in assets:
        return assets[service_name]
    return LinuxServiceAsset(
        service_name=service_name,
        description=f"{service_name} for uHOME",
        after=("network-online.target",),
        wants=("network-online.target",),
        exec_start=f"/usr/bin/env sh -lc 'echo Starting {service_name} from {install_root}; sleep infinity'",
        environment={"UHOME_INSTALL_ROOT": install_root},
    )


def render_service_unit(asset: LinuxServiceAsset) -> str:
    working_directory = asset.environment.get(asset.working_directory_var, "/opt/uhome")
    lines = [
        "[Unit]",
        f"Description={asset.description}",
    ]
    if asset.after:
        lines.append(f"After={' '.join(asset.after)}")
    if asset.wants:
        lines.append(f"Wants={' '.join(asset.wants)}")
    lines.extend(
        [
            "",
            "[Service]",
            "Type=simple",
            f"WorkingDirectory={working_directory}",
            f"EnvironmentFile=/etc/uhome/{asset.service_name}.env",
            f"ExecStart={asset.exec_start}",
            f"Restart={asset.restart}",
            "",
            "[Install]",
            f"WantedBy={asset.wanted_by}",
            "",
        ]
    )
    return "\n".join(lines)


def render_environment_file(payload: dict[str, Any]) -> str:
    lines = []
    for key in sorted(payload):
        value = str(payload[key]).replace("\n", " ").strip()
        lines.append(f'{key}="{value}"')
    return "\n".join(lines) + "\n"
