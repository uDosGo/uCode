"""Tests for client capability registration routes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from uhome_server.app import create_app
from uhome_server.config import bootstrap_runtime


@pytest.fixture
def app_client(tmp_path: Path, monkeypatch):
    bootstrap_runtime(tmp_path)
    monkeypatch.setattr("uhome_server.config.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("uhome_server.routes.client.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("uhome_server.services.client_capability_service.get_repo_root", lambda: tmp_path)

    import uhome_server.services.client_capability_service as client_svc

    client_svc._service = None
    app = create_app()
    return TestClient(app)


def test_register_client_returns_session_token_and_recommendations(app_client):
    response = app_client.post(
        "/api/client/register",
        json={
            "client_id": "android-phone-abc123",
            "device_name": "Pixel 7 Pro",
            "platform": "android",
            "os_version": "14",
            "app_version": "1.0.0",
            "capability_profile": "touch",
            "capabilities": {
                "touch_capable": True,
                "voice_capable": True,
                "display_type": "mobile",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["client_id"] == "android-phone-abc123"
    assert body["session_token"].startswith("session_")
    assert body["server_recommendations"]["ui_mode"] == "mobile"
    assert body["server_recommendations"]["enable_gestures"] is True


def test_list_and_get_clients(app_client):
    app_client.post(
        "/api/client/register",
        json={
            "client_id": "living-room-tv",
            "device_name": "Living Room TV",
            "platform": "android-tv",
            "capability_profile": "remote",
            "capabilities": {"voice_capable": True},
        },
    )

    listed = app_client.get("/api/client")
    assert listed.status_code == 200
    data = listed.json()
    assert data["count"] == 1
    assert data["clients"][0]["client_id"] == "living-room-tv"

    fetched = app_client.get("/api/client/living-room-tv")
    assert fetched.status_code == 200
    assert fetched.json()["client"]["capability_profile"] == "remote"


def test_update_client_capabilities_merges_fields(app_client):
    app_client.post(
        "/api/client/register",
        json={
            "client_id": "apple-tv-lounge",
            "device_name": "Apple TV",
            "platform": "tvos",
            "capability_profile": "controller",
            "capabilities": {"voice_capable": False},
        },
    )

    updated = app_client.post(
        "/api/client/apple-tv-lounge/capabilities",
        json={
            "capabilities": {
                "voice_capable": True,
                "network_quality": "ethernet",
            }
        },
    )

    assert updated.status_code == 200
    body = updated.json()
    assert body["record"]["capabilities"]["voice_capable"] is True
    assert body["record"]["capabilities"]["network_quality"] == "ethernet"
    assert body["server_recommendations"]["ui_mode"] == "tv"


def test_register_writes_persistent_registry_file(app_client, tmp_path):
    app_client.post(
        "/api/client/register",
        json={
            "client_id": "bedroom-tablet",
            "device_name": "Bedroom Tablet",
            "platform": "android",
            "capability_profile": "touch",
            "capabilities": {},
        },
    )

    # API data persistence should land under memory/uhome for reboot-safe capability state.
    registry_path = tmp_path / "memory" / "uhome" / "client_capabilities.json"
    assert registry_path.exists()
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    assert "bedroom-tablet" in payload["clients"]


def test_get_missing_client_returns_404(app_client):
    response = app_client.get("/api/client/does-not-exist")
    assert response.status_code == 404
