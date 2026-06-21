"""Playback service for media status and handoff coordination."""

from __future__ import annotations

import json
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from uhome_server.config import JSONConfigStore, get_logger, get_repo_root
from uhome_server.workspace import get_template_workspace_service

_log = get_logger("uhome.playback")
_config = JSONConfigStore()

_DEFAULT_TARGET_CLIENT = "default"
_DEFAULT_PRESENTATION_MODE = "auto"
_PRESENTATION_MODES = {"auto", "kiosk", "desktop"}


def _playback_queue_path() -> Path:
    return get_repo_root() / "memory" / "bank" / "uhome" / "playback_queue.json"


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    return []


def _save_json_list(path: Path, payload: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _jellyfin_base_url() -> str:
    return str(_config.get("JELLYFIN_URL", "") or "").strip()


def _jellyfin_api_key() -> str:
    return str(_config.get("JELLYFIN_API_KEY", "") or "").strip()


def _uhome_workspace_fields() -> dict[str, str]:
    workspace = get_template_workspace_service()
    return workspace.read_fields("settings", "uhome")


def _workspace_choice(
    workspace_fields: dict[str, str],
    field_name: str,
    default: str,
    valid_values: Optional[set[str]] = None,
) -> tuple[str, str]:
    raw_value = str(workspace_fields.get(field_name, "") or "").strip()
    if not raw_value:
        return default, "default"
    value = raw_value.lower() if valid_values is not None else raw_value
    if valid_values is not None and value not in valid_values:
        return default, "template_workspace_invalid"
    return value, "template_workspace"


class PlaybackService:
    """Service for tracking media playback status and coordinating handoff."""

    def __init__(self, repo_root: Optional[Path] = None):
        self._repo_root = repo_root or get_repo_root()

    def get_status(self) -> dict[str, Any]:
        """Get current playback status including active Jellyfin sessions."""
        workspace_fields = _uhome_workspace_fields()
        presentation_mode, presentation_mode_source = _workspace_choice(
            workspace_fields, "presentation_mode", _DEFAULT_PRESENTATION_MODE, valid_values=_PRESENTATION_MODES
        )
        preferred_target_client, preferred_target_client_source = _workspace_choice(
            workspace_fields, "preferred_target_client", _DEFAULT_TARGET_CLIENT
        )
        base_url = _jellyfin_base_url()
        api_key = _jellyfin_api_key()
        jellyfin_url_configured = bool(base_url)
        jellyfin_api_key_configured = bool(api_key)
        jellyfin_configured = jellyfin_url_configured and jellyfin_api_key_configured
        result: dict[str, Any] = {
            "jellyfin_configured": jellyfin_configured,
            "jellyfin_url_configured": jellyfin_url_configured,
            "jellyfin_api_key_configured": jellyfin_api_key_configured,
            "active_sessions": [],
            "presentation_mode": presentation_mode,
            "presentation_mode_source": presentation_mode_source,
            "preferred_target_client": preferred_target_client,
            "preferred_target_client_source": preferred_target_client_source,
        }
        if not jellyfin_configured:
            if not jellyfin_url_configured and not jellyfin_api_key_configured:
                result["note"] = "Set JELLYFIN_URL and JELLYFIN_API_KEY to enable live playback status."
            elif not jellyfin_url_configured:
                result["note"] = "Set JELLYFIN_URL to enable live playback status."
            else:
                result["note"] = "Set JELLYFIN_API_KEY to enable live playback status."
            return result

        try:
            url = f"{base_url.rstrip('/')}/Sessions?api_key={api_key}"
            with urllib.request.urlopen(url, timeout=3) as resp:
                sessions = json.loads(resp.read())
            active = [session for session in sessions if session.get("NowPlayingItem")]
            result["active_sessions"] = [
                {
                    "user": session.get("UserName"),
                    "title": session.get("NowPlayingItem", {}).get("Name"),
                    "media_type": session.get("NowPlayingItem", {}).get("Type"),
                    "client": session.get("Client"),
                }
                for session in active
            ]
            result["jellyfin_reachable"] = True
        except Exception as exc:
            result["jellyfin_reachable"] = False
            result["issue"] = str(exc)
        return result

    def handoff(
        self, item_id: str, target_client: Optional[str] = None, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Queue a playback handoff to a target client."""
        if not item_id or not item_id.strip():
            return {"success": False, "error": "item_id is required"}

        workspace_fields = _uhome_workspace_fields()
        default_target, default_target_source = _workspace_choice(
            workspace_fields, "preferred_target_client", _DEFAULT_TARGET_CLIENT
        )
        requested_target = (target_client or "").strip()
        use_default_target = not requested_target or requested_target.lower() == "default"
        resolved_target = default_target if use_default_target else requested_target

        try:
            queue = _load_json_list(_playback_queue_path())
            queue.append(
                {
                    "id": str(uuid.uuid4())[:8],
                    "item_id": item_id.strip(),
                    "target_client": resolved_target,
                    "queued_at": datetime.now(timezone.utc).isoformat(),
                    "params": params or {},
                }
            )
            _save_json_list(_playback_queue_path(), queue)
            return {
                "success": True,
                "item_id": item_id.strip(),
                "target_client": resolved_target,
                "source": default_target_source if use_default_target else "request",
            }
        except Exception as exc:
            _log.error(f"Playback handoff failed: {exc}")
            return {"success": False, "error": str(exc)}

    def get_queue(self) -> list[dict[str, Any]]:
        """Get the current playback queue."""
        return _load_json_list(_playback_queue_path())

    def clear_queue(self) -> dict[str, Any]:
        """Clear the playback queue."""
        try:
            _save_json_list(_playback_queue_path(), [])
            return {"success": True, "cleared": True}
        except Exception as exc:
            _log.error(f"Failed to clear queue: {exc}")
            return {"success": False, "error": str(exc)}


_service: Optional[PlaybackService] = None


def get_playback_service(repo_root: Optional[Path] = None) -> PlaybackService:
    """Get or create the singleton PlaybackService instance."""
    global _service
    if _service is None:
        _service = PlaybackService(repo_root)
    return _service
