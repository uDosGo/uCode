"""Tests for playback service and REST API routes."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from uhome_server.app import create_app
from uhome_server.config import bootstrap_runtime


@pytest.fixture
def mock_config_store():
    """Mock config store with Jellyfin settings."""
    store = {
        "JELLYFIN_URL": "http://localhost:8096",
        "JELLYFIN_API_KEY": "test_api_key",
    }

    class MockConfigStore:
        def get(self, key, default=None):
            return store.get(key, default)

        def set(self, key, value):
            store[key] = value

    return MockConfigStore()


@pytest.fixture
def mock_workspace():
    """Mock workspace service."""

    class MockWorkspace:
        def read_fields(self, section, component_id):
            return {
                "presentation_mode": "kiosk",
                "preferred_target_client": "living-room-tv",
            }

    return MockWorkspace()


@pytest.fixture
def jellyfin_sessions():
    """Mock Jellyfin sessions response."""
    return [
        {
            "UserName": "alice",
            "Client": "Jellyfin Web",
            "NowPlayingItem": {
                "Name": "Test Movie",
                "Type": "Movie",
                "Id": "movie123",
            },
        }
    ]


@pytest.fixture
def app_client(tmp_path, monkeypatch):
    """Create test client with mocked dependencies."""
    bootstrap_runtime(tmp_path)
    monkeypatch.setattr("uhome_server.config.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("uhome_server.services.playback_service.get_repo_root", lambda: tmp_path)
    app = create_app()
    return TestClient(app)


def test_playback_status_route(app_client, monkeypatch, mock_config_store, mock_workspace, jellyfin_sessions):
    """Test GET /api/playback/status."""
    from uhome_server.services import playback_service

    monkeypatch.setattr(playback_service, "_config", mock_config_store)
    monkeypatch.setattr(playback_service, "get_template_workspace_service", lambda: mock_workspace)

    class MockResponse:
        def read(self):
            return json.dumps(jellyfin_sessions).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("urllib.request.urlopen", lambda url, timeout=None: MockResponse())

    response = app_client.get("/api/playback/status")

    assert response.status_code == 200
    data = response.json()
    assert data["jellyfin_configured"] is True
    assert data["jellyfin_url_configured"] is True
    assert data["jellyfin_api_key_configured"] is True
    assert data["jellyfin_reachable"] is True
    assert len(data["active_sessions"]) == 1
    assert data["active_sessions"][0]["title"] == "Test Movie"
    assert data["presentation_mode"] == "kiosk"
    assert data["preferred_target_client"] == "living-room-tv"
    assert "timestamp" in data


def test_playback_status_not_configured(app_client, monkeypatch):
    """Test playback status when Jellyfin not configured."""
    from uhome_server.services import playback_service

    class EmptyConfig:
        def get(self, key, default=None):
            return default or ""

    monkeypatch.setattr(playback_service, "_config", EmptyConfig())

    response = app_client.get("/api/playback/status")

    assert response.status_code == 200
    data = response.json()
    assert data["jellyfin_configured"] is False
    assert data["jellyfin_url_configured"] is False
    assert data["jellyfin_api_key_configured"] is False
    assert "note" in data


def test_playback_status_url_without_api_key_is_not_configured(app_client, monkeypatch):
    """Test playback status reports missing API key when only URL is set."""
    from uhome_server.services import playback_service

    class URLOnlyConfig:
        def get(self, key, default=None):
            if key == "JELLYFIN_URL":
                return "http://localhost:8096"
            if key == "JELLYFIN_API_KEY":
                return ""
            return default

    monkeypatch.setattr(playback_service, "_config", URLOnlyConfig())

    response = app_client.get("/api/playback/status")

    assert response.status_code == 200
    data = response.json()
    assert data["jellyfin_configured"] is False
    assert data["jellyfin_url_configured"] is True
    assert data["jellyfin_api_key_configured"] is False
    assert "JELLYFIN_API_KEY" in data["note"]


def test_playback_handoff_route(app_client, tmp_path, monkeypatch, mock_workspace):
    """Test POST /api/playback/handoff."""
    from uhome_server.services import playback_service

    monkeypatch.setattr(playback_service, "get_template_workspace_service", lambda: mock_workspace)

    response = app_client.post(
        "/api/playback/handoff",
        json={"item_id": "movie123", "target_client": "tv-client"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["item_id"] == "movie123"
    assert data["target_client"] == "tv-client"
    assert data["source"] == "request"
    assert "timestamp" in data

    # Verify queue was updated
    queue_file = tmp_path / "memory" / "bank" / "uhome" / "playback_queue.json"
    assert queue_file.exists()
    queue = json.loads(queue_file.read_text())
    assert len(queue) == 1
    assert queue[0]["item_id"] == "movie123"
    assert queue[0]["target_client"] == "tv-client"


def test_playback_handoff_uses_default_target(app_client, tmp_path, monkeypatch, mock_workspace):
    """Test playback handoff uses default target when not specified."""
    from uhome_server.services import playback_service

    monkeypatch.setattr(playback_service, "get_template_workspace_service", lambda: mock_workspace)

    response = app_client.post(
        "/api/playback/handoff",
        json={"item_id": "movie456"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["target_client"] == "living-room-tv"
    assert data["source"] == "template_workspace"


def test_playback_handoff_requires_item_id(app_client):
    """Test playback handoff requires item_id."""
    response = app_client.post(
        "/api/playback/handoff",
        json={"target_client": "tv"},
    )

    assert response.status_code == 422  # Validation error from Pydantic


def test_playback_handoff_empty_item_id(app_client):
    """Test playback handoff rejects empty item_id."""
    response = app_client.post(
        "/api/playback/handoff",
        json={"item_id": ""},
    )

    assert response.status_code == 400
    assert "item_id is required" in response.json()["detail"]


def test_playback_get_queue(app_client, tmp_path, monkeypatch, mock_workspace):
    """Test GET /api/playback/queue."""
    from uhome_server.services import playback_service

    monkeypatch.setattr(playback_service, "get_template_workspace_service", lambda: mock_workspace)

    # Add items to queue
    app_client.post("/api/playback/handoff", json={"item_id": "item1"})
    app_client.post("/api/playback/handoff", json={"item_id": "item2"})

    response = app_client.get("/api/playback/queue")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["queue"]) == 2
    assert data["queue"][0]["item_id"] == "item1"
    assert data["queue"][1]["item_id"] == "item2"
    assert "timestamp" in data


def test_playback_clear_queue(app_client, tmp_path, monkeypatch, mock_workspace):
    """Test DELETE /api/playback/queue."""
    from uhome_server.services import playback_service

    monkeypatch.setattr(playback_service, "get_template_workspace_service", lambda: mock_workspace)

    # Add items to queue
    app_client.post("/api/playback/handoff", json={"item_id": "item1"})
    app_client.post("/api/playback/handoff", json={"item_id": "item2"})

    # Clear queue
    response = app_client.delete("/api/playback/queue")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["cleared"] is True

    # Verify queue is empty
    queue_response = app_client.get("/api/playback/queue")
    assert queue_response.json()["count"] == 0


def test_playback_handoff_with_extra_params(app_client, tmp_path, monkeypatch, mock_workspace):
    """Test playback handoff with additional parameters."""
    from uhome_server.services import playback_service

    monkeypatch.setattr(playback_service, "get_template_workspace_service", lambda: mock_workspace)

    response = app_client.post(
        "/api/playback/handoff",
        json={
            "item_id": "movie789",
            "target_client": "bedroom-tv",
            "params": {"start_position": 120, "audio_track": "en"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify params were stored
    queue_file = tmp_path / "memory" / "bank" / "uhome" / "playback_queue.json"
    queue = json.loads(queue_file.read_text())
    assert queue[0]["params"]["start_position"] == 120
    assert queue[0]["params"]["audio_track"] == "en"
