"""Household-safe browsing and status service for living-room clients."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from uhome_server.config import JSONConfigStore, get_repo_root
from uhome_server.library.catalog import get_container_catalog_service
from uhome_server.services.playback_service import get_playback_service
from uhome_server.workspace import get_template_workspace_service

_config = JSONConfigStore()

_DEFAULT_BLOCKED_TERMS = (
    "adult",
    "xxx",
    "porn",
    "nsfw",
    "explicit",
)

_DEFAULT_LIMIT = 24
_MAX_LIMIT = 100


def _blocked_terms() -> list[str]:
    raw = str(_config.get("HOUSEHOLD_BLOCKED_TERMS", "") or "").strip()
    if not raw:
        return list(_DEFAULT_BLOCKED_TERMS)
    custom = [term.strip().lower() for term in raw.split(",") if term.strip()]
    return custom or list(_DEFAULT_BLOCKED_TERMS)


def _contains_blocked_terms(*parts: Optional[str], terms: list[str]) -> bool:
    text = " ".join(str(part or "") for part in parts).lower()
    return any(term in text for term in terms)


class HouseholdService:
    """Service for household-safe browsing and status surfaces."""

    def __init__(self, repo_root: Optional[Path] = None):
        self._repo_root = repo_root or get_repo_root()

    def browse(self, query: str = "", limit: int = _DEFAULT_LIMIT) -> dict[str, Any]:
        """Browse household-safe catalog entries for living-room clients."""
        normalized_query = (query or "").strip().lower()
        bounded_limit = max(1, min(int(limit), _MAX_LIMIT))
        blocked_terms = _blocked_terms()

        entries = get_container_catalog_service(self._repo_root).list_by_kind("library")
        filtered: list[dict[str, Any]] = []
        hidden_count = 0

        for entry in entries:
            route = str((entry.metadata or {}).get("browser_route") or "").strip()
            if not route:
                continue

            title = str(entry.label or "").strip()
            summary = str(entry.summary or "").strip()
            searchable = f"{title} {summary}".lower()

            if normalized_query and normalized_query not in searchable:
                continue

            if _contains_blocked_terms(title, summary, terms=blocked_terms):
                hidden_count += 1
                continue

            filtered.append(
                {
                    "id": entry.entry_id,
                    "title": title,
                    "summary": summary,
                    "browser_route": route,
                    "category": str(entry.category or "container"),
                }
            )

        limited = filtered[:bounded_limit]
        return {
            "safe_mode": "household-default",
            "query": normalized_query or None,
            "count": len(limited),
            "total": len(filtered),
            "hidden_count": hidden_count,
            "items": limited,
        }

    def status(self) -> dict[str, Any]:
        """Return living-room-safe runtime status."""
        blocked_terms = _blocked_terms()
        playback = get_playback_service(self._repo_root).get_status()
        workspace_fields = get_template_workspace_service(self._repo_root).read_fields("settings", "uhome")

        active_sessions = playback.get("active_sessions") or []
        safe_sessions: list[dict[str, Any]] = []
        hidden_count = 0

        for session in active_sessions:
            if not isinstance(session, dict):
                continue
            title = str(session.get("title") or "").strip()
            if _contains_blocked_terms(title, terms=blocked_terms):
                hidden_count += 1
                continue
            safe_sessions.append(
                {
                    "title": title,
                    "media_type": session.get("media_type"),
                    "client": session.get("client"),
                }
            )

        return {
            "safe_mode": "household-default",
            "node_role": str(workspace_fields.get("node_role") or "server"),
            "presentation_mode": playback.get("presentation_mode"),
            "preferred_target_client": playback.get("preferred_target_client"),
            "jellyfin_configured": bool(playback.get("jellyfin_configured", False)),
            "jellyfin_reachable": bool(playback.get("jellyfin_reachable", False)),
            "active_media": safe_sessions,
            "active_media_count": len(safe_sessions),
            "hidden_media_count": hidden_count,
            "note": playback.get("note"),
            "issue": playback.get("issue"),
        }


_service: Optional[HouseholdService] = None


def get_household_service(repo_root: Optional[Path] = None) -> HouseholdService:
    """Get or create the singleton HouseholdService instance."""
    global _service
    if _service is None:
        _service = HouseholdService(repo_root=repo_root)
    return _service
