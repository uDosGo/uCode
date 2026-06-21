from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from uhome_server.routes.household import create_household_routes


@dataclass
class _Entry:
    entry_id: str
    label: str
    summary: str
    category: str = "container"
    metadata: dict[str, Any] = field(default_factory=dict)


class _Catalog:
    def __init__(self, entries: list[_Entry]):
        self._entries = entries

    def list_by_kind(self, kind: str) -> list[_Entry]:
        return list(self._entries) if kind == "library" else []


class _Playback:
    def __init__(self, status_payload: dict[str, Any]):
        self._status_payload = status_payload

    def get_status(self) -> dict[str, Any]:
        return dict(self._status_payload)


@pytest.fixture
def household_client(tmp_path: Path, monkeypatch) -> TestClient:
    import uhome_server.routes.household as household_routes
    import uhome_server.services.household_service as household_service

    household_service._service = None
    monkeypatch.setattr(household_routes, "get_repo_root", lambda: tmp_path)
    monkeypatch.setattr(household_service, "get_repo_root", lambda: tmp_path)

    app = FastAPI()
    app.include_router(create_household_routes())
    return TestClient(app)


def test_household_browse_filters_blocked_terms(household_client: TestClient, monkeypatch):
    import uhome_server.services.household_service as household_service

    entries = [
        _Entry(
            entry_id="movies",
            label="Family Movies",
            summary="Safe evening picks",
            metadata={"browser_route": "/ui/movies"},
        ),
        _Entry(
            entry_id="late-night",
            label="Adult Picks",
            summary="Not for kids",
            metadata={"browser_route": "/ui/late-night"},
        ),
    ]

    monkeypatch.setattr(household_service, "get_container_catalog_service", lambda repo_root=None: _Catalog(entries))

    response = household_client.get("/api/household/browse")
    assert response.status_code == 200
    body = response.json()

    assert body["safe_mode"] == "household-default"
    assert body["count"] == 1
    assert body["hidden_count"] == 1
    assert body["items"][0]["id"] == "movies"
    assert body["items"][0]["browser_route"] == "/ui/movies"


def test_household_browse_query_and_limit(household_client: TestClient, monkeypatch):
    import uhome_server.services.household_service as household_service

    entries = [
        _Entry(
            entry_id="ha-core",
            label="Home Assistant Core",
            summary="Primary household automation",
            metadata={"browser_route": "/ui/home-assistant"},
        ),
        _Entry(
            entry_id="ha-dashboard",
            label="Home Dashboards",
            summary="Living-room tiles",
            metadata={"browser_route": "/ui/dashboards"},
        ),
        _Entry(
            entry_id="media",
            label="Media Shelf",
            summary="Movies and shows",
            metadata={"browser_route": "/ui/media"},
        ),
    ]

    monkeypatch.setattr(household_service, "get_container_catalog_service", lambda repo_root=None: _Catalog(entries))

    response = household_client.get("/api/household/browse?q=home&limit=1")
    assert response.status_code == 200
    body = response.json()

    assert body["query"] == "home"
    assert body["count"] == 1
    assert body["total"] == 2
    assert len(body["items"]) == 1


def test_household_status_filters_session_titles(household_client: TestClient, monkeypatch):
    import uhome_server.services.household_service as household_service

    playback_payload = {
        "jellyfin_configured": True,
        "jellyfin_reachable": True,
        "presentation_mode": "kiosk",
        "preferred_target_client": "living-room",
        "active_sessions": [
            {
                "user": "alice",
                "title": "Family Movie Night",
                "media_type": "Movie",
                "client": "Jellyfin TV",
            },
            {
                "user": "bob",
                "title": "Explicit Content Preview",
                "media_type": "Movie",
                "client": "Jellyfin Web",
            },
        ],
    }

    class _Workspace:
        def read_fields(self, section: str, component_id: str) -> dict[str, str]:
            return {"node_role": "tv-node"}

    monkeypatch.setattr(household_service, "get_playback_service", lambda repo_root=None: _Playback(playback_payload))
    monkeypatch.setattr(household_service, "get_template_workspace_service", lambda repo_root=None: _Workspace())

    response = household_client.get("/api/household/status")
    assert response.status_code == 200
    body = response.json()

    assert body["safe_mode"] == "household-default"
    assert body["node_role"] == "tv-node"
    assert body["jellyfin_configured"] is True
    assert body["active_media_count"] == 1
    assert body["hidden_media_count"] == 1
    assert body["active_media"][0]["title"] == "Family Movie Night"
    assert "user" not in body["active_media"][0]


def test_household_status_handles_unconfigured_jellyfin(household_client: TestClient, monkeypatch):
    import uhome_server.services.household_service as household_service

    playback_payload = {
        "jellyfin_configured": False,
        "jellyfin_reachable": False,
        "presentation_mode": "auto",
        "preferred_target_client": "default",
        "active_sessions": [],
        "note": "Set JELLYFIN_URL to enable live playback status.",
    }

    class _Workspace:
        def read_fields(self, section: str, component_id: str) -> dict[str, str]:
            return {"node_role": "server"}

    monkeypatch.setattr(household_service, "get_playback_service", lambda repo_root=None: _Playback(playback_payload))
    monkeypatch.setattr(household_service, "get_template_workspace_service", lambda repo_root=None: _Workspace())

    response = household_client.get("/api/household/status")
    assert response.status_code == 200
    body = response.json()

    assert body["jellyfin_configured"] is False
    assert body["jellyfin_reachable"] is False
    assert body["active_media_count"] == 0
    assert "JELLYFIN_URL" in body["note"]
