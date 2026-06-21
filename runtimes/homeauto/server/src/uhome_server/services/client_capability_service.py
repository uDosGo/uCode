"""Client capability registry for local-network uHOME clients."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Optional

from uhome_server.config import get_repo_root, read_json_file, utc_now_iso_z, write_json_file

_CAPABILITY_PROFILES = {"controller", "remote", "touch"}


class ClientCapabilityService:
    """File-backed registry of client capability advertisements."""

    def __init__(self, repo_root: Optional[Path] = None):
        self._repo_root = repo_root or get_repo_root()
        self._state_path = self._repo_root / "memory" / "uhome" / "client_capabilities.json"

    def _load(self) -> dict[str, dict[str, Any]]:
        payload = read_json_file(self._state_path, default={"clients": {}})
        clients = payload.get("clients", {})
        if isinstance(clients, dict):
            return clients
        return {}

    def _save(self, clients: dict[str, dict[str, Any]]) -> None:
        write_json_file(
            self._state_path,
            {
                "updated_at": utc_now_iso_z(),
                "clients": clients,
            },
            indent=2,
        )

    def _recommendations(self, profile: str, capabilities: dict[str, Any]) -> dict[str, Any]:
        ui_mode = "mobile" if profile == "touch" else "tv"
        voice_capable = bool(capabilities.get("voice_capable", False))
        touch_capable = bool(capabilities.get("touch_capable", False))
        keyboard_capable = bool(capabilities.get("keyboard_capable", False))
        network_quality = str(capabilities.get("network_quality") or "unknown")

        return {
            "ui_mode": ui_mode,
            "enable_gestures": touch_capable,
            "enable_voice_search": voice_capable,
            "prefer_text_entry": keyboard_capable,
            "network_quality_hint": network_quality,
            "recommended_handoff_target": "local-display" if ui_mode == "tv" else "living-room-tv",
        }

    def register(self, payload: dict[str, Any]) -> dict[str, Any]:
        client_id = str(payload.get("client_id") or "").strip()
        if not client_id:
            raise ValueError("client_id is required")

        profile = str(payload.get("capability_profile") or "remote").strip().lower()
        if profile not in _CAPABILITY_PROFILES:
            raise ValueError(f"invalid capability_profile {profile!r}")

        capabilities = payload.get("capabilities")
        if not isinstance(capabilities, dict):
            capabilities = {}

        now = utc_now_iso_z()
        clients = self._load()
        existing = clients.get(client_id, {})
        session_token = str(existing.get("session_token") or f"session_{uuid.uuid4().hex[:12]}")
        registered_at = str(existing.get("registered_at") or now)

        record = {
            "client_id": client_id,
            "device_name": str(payload.get("device_name") or "").strip() or client_id,
            "platform": str(payload.get("platform") or "unknown").strip().lower(),
            "os_version": str(payload.get("os_version") or "").strip(),
            "app_version": str(payload.get("app_version") or "").strip(),
            "capability_profile": profile,
            "capabilities": capabilities,
            "registered_at": registered_at,
            "updated_at": now,
            "last_seen": now,
            "session_token": session_token,
        }
        clients[client_id] = record
        self._save(clients)

        return {
            "client_id": client_id,
            "registered_at": registered_at,
            "session_token": session_token,
            "server_recommendations": self._recommendations(profile, capabilities),
            "record": record,
        }

    def list_clients(self) -> list[dict[str, Any]]:
        clients = self._load()
        items = list(clients.values())
        items.sort(key=lambda item: str(item.get("client_id") or ""))
        return items

    def get_client(self, client_id: str) -> Optional[dict[str, Any]]:
        return self._load().get(client_id)

    def update_capabilities(self, client_id: str, capabilities: dict[str, Any]) -> Optional[dict[str, Any]]:
        clients = self._load()
        record = clients.get(client_id)
        if record is None:
            return None

        existing_capabilities = record.get("capabilities")
        merged: dict[str, Any]
        if isinstance(existing_capabilities, dict):
            merged = {**existing_capabilities, **capabilities}
        else:
            merged = dict(capabilities)

        profile = str(record.get("capability_profile") or "remote").strip().lower()
        record["capabilities"] = merged
        record["updated_at"] = utc_now_iso_z()
        record["last_seen"] = record["updated_at"]
        clients[client_id] = record
        self._save(clients)

        return {
            "client_id": client_id,
            "updated_at": record["updated_at"],
            "server_recommendations": self._recommendations(profile, merged),
            "record": record,
        }

    def profile_summary(self) -> dict[str, Any]:
        items = self.list_clients()
        by_profile: dict[str, int] = {"controller": 0, "remote": 0, "touch": 0}
        for item in items:
            profile = str(item.get("capability_profile") or "remote")
            by_profile[profile] = by_profile.get(profile, 0) + 1
        return {
            "count": len(items),
            "profiles": by_profile,
            "clients": [
                {
                    "client_id": item.get("client_id"),
                    "device_name": item.get("device_name"),
                    "platform": item.get("platform"),
                    "capability_profile": item.get("capability_profile"),
                    "last_seen": item.get("last_seen"),
                }
                for item in items
            ],
        }


_service: Optional[ClientCapabilityService] = None
_service_root: Optional[Path] = None


def get_client_capability_service(repo_root: Optional[Path] = None) -> ClientCapabilityService:
    """Get or create singleton ClientCapabilityService."""
    global _service, _service_root
    resolved_root = repo_root or get_repo_root()
    if _service is None or _service_root != resolved_root:
        _service = ClientCapabilityService(repo_root=resolved_root)
        _service_root = resolved_root
    return _service
