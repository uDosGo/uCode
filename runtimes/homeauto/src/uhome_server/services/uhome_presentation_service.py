"""uHOME presentation workflow service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from uhome_server.config import read_json_file, utc_now_iso_z, write_json_file
from uhome_server.workspace import get_template_workspace_service

SUPPORTED_PRESENTATIONS = ("thin-gui", "steam-console")
SUPPORTED_NODE_ROLES = ("server", "tv-node")


class UHomePresentationService:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self._primary_state_dir = self.repo_root / "memory" / "kiosk" / "uhome"
        self._legacy_state_dir = self.repo_root / "memory" / "wizard" / "uhome"
        self._primary_state_dir.mkdir(parents=True, exist_ok=True)

    @property
    def state_path(self) -> Path:
        primary = self._primary_state_dir / "presentation.json"
        legacy = self._legacy_state_dir / "presentation.json"
        if primary.exists():
            return primary
        return legacy if legacy.exists() else primary

    def _read_state(self) -> dict[str, Any]:
        return read_json_file(
            self.state_path,
            default={"active_presentation": None, "updated_at": None, "node_role": "server"},
        )

    def _write_state(self, payload: dict[str, Any]) -> None:
        target = self._primary_state_dir / "presentation.json"
        write_json_file(target, payload, indent=2)

    def _workspace_fields(self) -> dict[str, str]:
        return get_template_workspace_service(self.repo_root).read_fields("settings", "uhome")

    def _preferred_presentation(self) -> tuple[str, str]:
        workspace_value = str(self._workspace_fields().get("presentation_mode") or "").strip().lower()
        if workspace_value in SUPPORTED_PRESENTATIONS:
            return workspace_value, "template_workspace"
        if workspace_value:
            return SUPPORTED_PRESENTATIONS[0], "template_workspace_invalid"
        return SUPPORTED_PRESENTATIONS[0], "default"

    def _node_role(self) -> tuple[str, str]:
        workspace_value = str(self._workspace_fields().get("node_role") or "").strip().lower().replace("_", "-")
        if workspace_value in SUPPORTED_NODE_ROLES:
            return workspace_value, "template_workspace"
        if workspace_value:
            return SUPPORTED_NODE_ROLES[0], "template_workspace_invalid"
        return SUPPORTED_NODE_ROLES[0], "default"

    def get_status(self) -> dict[str, Any]:
        state = self._read_state()
        preferred_presentation, preferred_presentation_source = self._preferred_presentation()
        node_role, node_role_source = self._node_role()
        return {
            "supported_presentations": list(SUPPORTED_PRESENTATIONS),
            "supported_node_roles": list(SUPPORTED_NODE_ROLES),
            "active_presentation": state.get("active_presentation"),
            "running": bool(state.get("active_presentation")),
            "preferred_presentation": preferred_presentation,
            "preferred_presentation_source": preferred_presentation_source,
            "node_role": node_role,
            "node_role_source": node_role_source,
            "state_path": str(self.state_path),
            "updated_at": state.get("updated_at"),
            "session_id": state.get("session_id"),
        }

    def _intent_payload(self, presentation: str | None, node_role: str, action: str) -> dict[str, Any]:
        launcher = presentation or self._preferred_presentation()[0]
        return {
            "intent": {
                "target": "uhome-console",
                "mode": "home",
                "launcher": launcher,
                "workspace": "uhome",
                "profile_id": node_role,
                "auth": {
                    "kiosk_local_session": True,
                    "wizard_mode_active": False,
                    "uhome_role": node_role,
                },
            },
            "action": action,
            "status": "ready" if action == "start" else "stopped",
        }

    def start(self, presentation: str) -> dict[str, Any]:
        normalized = (presentation or "").strip().lower()
        if not normalized:
            normalized, _ = self._preferred_presentation()
        if normalized not in SUPPORTED_PRESENTATIONS:
            raise ValueError(f"Unsupported uHOME presentation: {presentation}")
        node_role, _ = self._node_role()
        payload = {
            "active_presentation": normalized,
            "node_role": node_role,
            "updated_at": utc_now_iso_z(),
            "last_action": "start",
            "thin_gui": self._intent_payload(normalized, node_role, "start"),
        }
        self._write_state(payload)
        return payload

    def stop(self) -> dict[str, Any]:
        node_role, _ = self._node_role()
        payload = {
            "active_presentation": None,
            "node_role": node_role,
            "updated_at": utc_now_iso_z(),
            "last_action": "stop",
            "thin_gui": self._intent_payload(None, node_role, "stop"),
        }
        self._write_state(payload)
        return payload

    def get_console_menu(self) -> dict[str, Any]:
        """Return an action-oriented launcher menu for console clients."""
        status = self.get_status()
        active = status.get("active_presentation")
        running = bool(status.get("running"))
        return {
            "menu_id": "uhome-console-main",
            "title": "uHOME Console",
            "running": running,
            "active_presentation": active,
            "preferred_presentation": status.get("preferred_presentation"),
            "node_role": status.get("node_role"),
            "items": [
                {
                    "id": "start-thin-gui",
                    "label": "Start Thin GUI",
                    "description": "Launch the thin GUI presentation lane.",
                    "enabled": active != "thin-gui",
                    "action": {
                        "method": "POST",
                        "path": "/api/launcher/start",
                        "body": {"presentation": "thin-gui"},
                    },
                },
                {
                    "id": "start-steam-console",
                    "label": "Start Steam Console",
                    "description": "Launch the Steam console presentation lane.",
                    "enabled": active != "steam-console",
                    "action": {
                        "method": "POST",
                        "path": "/api/launcher/start",
                        "body": {"presentation": "steam-console"},
                    },
                },
                {
                    "id": "stop-presentation",
                    "label": "Stop Active Presentation",
                    "description": "Stop any active launcher presentation session.",
                    "enabled": running,
                    "action": {
                        "method": "POST",
                        "path": "/api/launcher/stop",
                        "body": {},
                    },
                },
                {
                    "id": "open-playback-status",
                    "label": "Playback Status",
                    "description": "Inspect Jellyfin and active session state.",
                    "enabled": True,
                    "action": {
                        "method": "GET",
                        "path": "/api/playback/status",
                    },
                },
                {
                    "id": "open-network-capabilities",
                    "label": "Network Capabilities",
                    "description": "Inspect topology and registered client capability profiles.",
                    "enabled": True,
                    "action": {
                        "method": "GET",
                        "path": "/api/network/capabilities",
                    },
                },
            ],
            "metadata": {
                "state_path": status.get("state_path"),
                "updated_at": status.get("updated_at"),
            },
        }


def get_uhome_presentation_service(repo_root: Path) -> UHomePresentationService:
    return UHomePresentationService(repo_root=repo_root)
