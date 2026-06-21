"""Tests for Jellyfin integration and playback status."""

import json
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

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
def jellyfin_sessions_response():
    """Mock Jellyfin /Sessions endpoint response."""
    return [
        {
            "UserName": "alice",
            "Client": "Jellyfin Web",
            "NowPlayingItem": {
                "Name": "Example Movie",
                "Type": "Movie",
                "Id": "abc123",
            },
        },
        {
            "UserName": "bob",
            "Client": "Jellyfin Android",
            "NowPlayingItem": {
                "Name": "Example Show S01E01",
                "Type": "Episode",
                "Id": "def456",
            },
        },
    ]


@pytest.fixture
def mock_urlopen(jellyfin_sessions_response):
    """Mock urllib.request.urlopen for Jellyfin API calls."""

    class MockResponse:
        def __init__(self, data):
            self.data = json.dumps(data).encode()

        def read(self):
            return self.data

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def _urlopen(url, timeout=None):
        if "/Sessions" in url:
            return MockResponse(jellyfin_sessions_response)
        raise ValueError(f"Unexpected URL: {url}")

    return _urlopen


def test_jellyfin_status_configured_and_reachable(tmp_path, monkeypatch, mock_config_store, mock_urlopen):
    """Test Jellyfin status when configured and reachable."""
    from uhome_server.services import playback_service, uhome_command_handlers

    monkeypatch.setattr(uhome_command_handlers, "_config", mock_config_store)
    monkeypatch.setattr(playback_service, "_config", mock_config_store)
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)

    result = uhome_command_handlers.playback_status({})

    assert result["command"] == "uhome.playback.status"
    assert result["jellyfin_configured"] is True
    assert result["jellyfin_url_configured"] is True
    assert result["jellyfin_api_key_configured"] is True
    assert result["jellyfin_reachable"] is True
    assert len(result["active_sessions"]) == 2
    assert result["active_sessions"][0]["user"] == "alice"
    assert result["active_sessions"][0]["title"] == "Example Movie"
    assert result["active_sessions"][1]["user"] == "bob"
    assert result["active_sessions"][1]["title"] == "Example Show S01E01"


def test_jellyfin_status_not_configured(tmp_path, monkeypatch):
    """Test Jellyfin status when URL not configured."""
    from uhome_server.services import uhome_command_handlers

    class EmptyConfig:
        def get(self, key, default=None):
            return default or ""

    monkeypatch.setattr(uhome_command_handlers, "_config", EmptyConfig())

    result = uhome_command_handlers.playback_status({})

    assert result["command"] == "uhome.playback.status"
    assert result["jellyfin_configured"] is False
    assert result["jellyfin_url_configured"] is False
    assert result["jellyfin_api_key_configured"] is False
    assert "note" in result
    assert "JELLYFIN_URL" in result["note"]


def test_jellyfin_status_url_without_api_key(tmp_path, monkeypatch):
    """Test Jellyfin status when URL is configured but API key is missing."""
    from uhome_server.services import playback_service, uhome_command_handlers

    class URLOnlyConfig:
        def get(self, key, default=None):
            if key == "JELLYFIN_URL":
                return "http://localhost:8096"
            if key == "JELLYFIN_API_KEY":
                return ""
            return default or ""

    monkeypatch.setattr(uhome_command_handlers, "_config", URLOnlyConfig())
    monkeypatch.setattr(playback_service, "_config", URLOnlyConfig())

    result = uhome_command_handlers.playback_status({})

    assert result["command"] == "uhome.playback.status"
    assert result["jellyfin_configured"] is False
    assert result["jellyfin_url_configured"] is True
    assert result["jellyfin_api_key_configured"] is False
    assert "JELLYFIN_API_KEY" in result["note"]


def test_jellyfin_status_unreachable(tmp_path, monkeypatch, mock_config_store):
    from uhome_server.services import playback_service, uhome_command_handlers

    monkeypatch.setattr(uhome_command_handlers, "_config", mock_config_store)
    monkeypatch.setattr(playback_service, "_config", mock_config_store)

    def _urlopen_error(url, timeout=None):
        raise OSError("Connection refused")

    monkeypatch.setattr("urllib.request.urlopen", _urlopen_error)

    result = uhome_command_handlers.playback_status({})

    assert result["command"] == "uhome.playback.status"
    assert result["jellyfin_configured"] is True
    assert result["jellyfin_reachable"] is False
    assert "issue" in result


def test_jellyfin_status_no_active_sessions(tmp_path, monkeypatch, mock_config_store):
    from uhome_server.services import playback_service, uhome_command_handlers

    monkeypatch.setattr(uhome_command_handlers, "_config", mock_config_store)
    monkeypatch.setattr(playback_service, "_config", mock_config_store)

    class MockResponse:
        def read(self):
            return b"[]"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("urllib.request.urlopen", lambda url, timeout=None: MockResponse())

    result = uhome_command_handlers.playback_status({})

    assert result["command"] == "uhome.playback.status"
    assert result["jellyfin_reachable"] is True
    assert len(result["active_sessions"]) == 0


def test_runtime_readiness_includes_jellyfin_check(tmp_path, monkeypatch, mock_config_store, mock_urlopen):
    """Test runtime readiness probe includes Jellyfin health check."""
    from uhome_server.app import create_app

    bootstrap_runtime(tmp_path)
    monkeypatch.setenv("JELLYFIN_URL", "http://localhost:8096")
    monkeypatch.setenv("JELLYFIN_API_KEY", "test_key")

    from uhome_server.services import uhome_command_handlers

    monkeypatch.setattr(uhome_command_handlers, "_config", mock_config_store)
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)
    monkeypatch.setattr("uhome_server.config.get_repo_root", lambda: tmp_path)

    app = create_app()
    client = TestClient(app)
    response = client.get("/api/runtime/ready")

    assert response.status_code == 200
    data = response.json()
    assert "checks" in data
    assert "jellyfin" in data["checks"]

    jellyfin_check = data["checks"]["jellyfin"]
    assert jellyfin_check["ok"] is True
    assert jellyfin_check["jellyfin_configured"] is True


def test_jellyfin_invalid_api_key_handled_gracefully(tmp_path, monkeypatch, mock_config_store):
    from uhome_server.services import playback_service, uhome_command_handlers

    monkeypatch.setattr(uhome_command_handlers, "_config", mock_config_store)
    monkeypatch.setattr(playback_service, "_config", mock_config_store)

    def _urlopen_unauthorized(url, timeout=None):
        from urllib.error import HTTPError

        raise HTTPError(url, 401, "Unauthorized", {}, None)

    monkeypatch.setattr("urllib.request.urlopen", _urlopen_unauthorized)

    result = uhome_command_handlers.playback_status({})

    assert result["command"] == "uhome.playback.status"
    assert result["jellyfin_reachable"] is False
    assert "issue" in result
    assert "401" in result["issue"]


def test_jellyfin_timeout_handled_gracefully(tmp_path, monkeypatch, mock_config_store):
    from uhome_server.services import playback_service, uhome_command_handlers

    monkeypatch.setattr(uhome_command_handlers, "_config", mock_config_store)
    monkeypatch.setattr(playback_service, "_config", mock_config_store)

    def _urlopen_timeout(url, timeout=None):
        from urllib.error import URLError

        raise URLError("timeout")

    monkeypatch.setattr("urllib.request.urlopen", _urlopen_timeout)

    result = uhome_command_handlers.playback_status({})

    assert result["command"] == "uhome.playback.status"
    assert result["jellyfin_reachable"] is False
    assert "issue" in result


def test_jellyfin_malformed_response_handled(tmp_path, monkeypatch, mock_config_store):
    from uhome_server.services import playback_service, uhome_command_handlers

    monkeypatch.setattr(uhome_command_handlers, "_config", mock_config_store)
    monkeypatch.setattr(playback_service, "_config", mock_config_store)

    class BadResponse:
        def read(self):
            return b"not json"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("urllib.request.urlopen", lambda url, timeout=None: BadResponse())

    result = uhome_command_handlers.playback_status({})

    assert result["command"] == "uhome.playback.status"
    assert result["jellyfin_reachable"] is False
    assert "issue" in result
