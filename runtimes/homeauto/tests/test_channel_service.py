"""Tests for channel service (adapters, sessions, gateway) and REST routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from uhome_server.app import create_app
from uhome_server.config import bootstrap_runtime
from uhome_server.services.channel_service import (
    SessionController,
    get_channel,
    get_channel_service,
    list_channels,
    resolve_gateway_mode,
    GATEWAY_MODE_PROXY_ASSISTED,
    MEDIA_MODE_AUDIO_FIRST,
    MEDIA_MODE_AUDIO_VIDEO,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app_client(tmp_path):
    """Create test client."""
    bootstrap_runtime(tmp_path)
    app = create_app()
    return TestClient(app)


@pytest.fixture
def controller():
    return SessionController()


# ---------------------------------------------------------------------------
# Source adapter tests
# ---------------------------------------------------------------------------


def test_list_channels_returns_both_adapters():
    channels = list_channels()
    ids = {c["channel_id"] for c in channels}
    assert "channel.rewind.mtv" in ids
    assert "channel.rewind.cartoons" in ids


def test_get_channel_mtv_returns_metadata():
    ch = get_channel("channel.rewind.mtv")
    assert ch is not None
    assert ch["display_name"] == "Music TV Rewind"
    assert ch["media_mode"] == MEDIA_MODE_AUDIO_VIDEO
    assert "youtube-embed" in ch["policy_flags"]


def test_get_channel_cartoons_returns_metadata():
    ch = get_channel("channel.rewind.cartoons")
    assert ch is not None
    assert ch["display_name"] == "Cartoon Rewind"
    assert "upstream_url" in ch


def test_get_channel_unknown_returns_none():
    assert get_channel("channel.unknown.xyz") is None


# ---------------------------------------------------------------------------
# Gateway tests
# ---------------------------------------------------------------------------


def test_resolve_gateway_returns_proxy_assisted_by_default():
    result = resolve_gateway_mode("channel.rewind.mtv")
    assert result["gateway_mode"] == GATEWAY_MODE_PROXY_ASSISTED
    assert result["channel_id"] == "channel.rewind.mtv"
    assert "upstream_url" in result


def test_resolve_gateway_respects_audio_first_hint():
    result = resolve_gateway_mode("channel.rewind.mtv", client_hint=MEDIA_MODE_AUDIO_FIRST)
    assert result["media_mode"] == MEDIA_MODE_AUDIO_FIRST


def test_resolve_gateway_unknown_channel_returns_error():
    result = resolve_gateway_mode("channel.unknown.xyz")
    assert "error" in result


# ---------------------------------------------------------------------------
# Session controller tests
# ---------------------------------------------------------------------------


def test_create_session_returns_session_with_id(controller):
    session = controller.create(room="living-room", channel_id="channel.rewind.mtv")
    assert session.session_id
    assert session.room == "living-room"
    assert session.channel_id == "channel.rewind.mtv"
    assert session.state == "active"


def test_join_session_adds_device(controller):
    session = controller.create(room="kitchen", channel_id="channel.rewind.cartoons")
    updated = controller.join(session.session_id, device_id="tablet-01")
    assert updated is not None
    assert "tablet-01" in updated.device_ids


def test_join_unknown_session_returns_none(controller):
    assert controller.join("no-such-id", "device-x") is None


def test_sync_session_returns_session_and_channel(controller):
    session = controller.create(room="bedroom", channel_id="channel.rewind.mtv")
    sync = controller.sync(session.session_id)
    assert sync is not None
    assert "session" in sync
    assert "channel" in sync
    assert sync["channel"]["channel_id"] == "channel.rewind.mtv"


def test_resume_session_sets_state_active(controller):
    session = controller.create(room="lounge", channel_id="channel.rewind.cartoons")
    session.state = "paused"
    resumed = controller.resume(session.session_id)
    assert resumed is not None
    assert resumed.state == "active"


def test_pause_session_sets_state_paused(controller):
    session = controller.create(room="studio", channel_id="channel.rewind.mtv")
    paused = controller.pause(session.session_id)
    assert paused is not None
    assert paused.state == "paused"


def test_move_session_changes_room(controller):
    session = controller.create(room="office", channel_id="channel.rewind.mtv")
    moved = controller.move(session.session_id, target_room="living-room")
    assert moved is not None
    assert moved.room == "living-room"


def test_end_session_removes_from_list(controller):
    session = controller.create(room="guest", channel_id="channel.rewind.cartoons")
    controller.end(session.session_id)
    active = controller.list_sessions()
    assert all(s["session_id"] != session.session_id for s in active)


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------


def test_route_list_channels(app_client):
    resp = app_client.get("/api/channels")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 2
    ids = {c["channel_id"] for c in data["channels"]}
    assert "channel.rewind.mtv" in ids


def test_route_get_channel(app_client):
    resp = app_client.get("/api/channels/channel.rewind.cartoons")
    assert resp.status_code == 200
    assert resp.json()["channel"]["channel_id"] == "channel.rewind.cartoons"


def test_route_get_channel_not_found(app_client):
    resp = app_client.get("/api/channels/channel.unknown.xyz")
    assert resp.status_code == 404


def test_route_get_gateway(app_client):
    resp = app_client.get("/api/channels/channel.rewind.mtv/gateway")
    assert resp.status_code == 200
    data = resp.json()
    assert data["gateway_mode"] == GATEWAY_MODE_PROXY_ASSISTED


def test_route_get_gateway_audio_first(app_client):
    resp = app_client.get("/api/channels/channel.rewind.mtv/gateway?mode=audio-first")
    assert resp.status_code == 200
    assert resp.json()["media_mode"] == MEDIA_MODE_AUDIO_FIRST


def test_route_create_and_get_session(app_client):
    create_resp = app_client.post(
        "/api/channels/sessions",
        json={"room": "living-room", "channel_id": "channel.rewind.mtv"},
    )
    assert create_resp.status_code == 200
    session_id = create_resp.json()["session"]["session_id"]

    get_resp = app_client.get(f"/api/channels/sessions/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["session"]["room"] == "living-room"


def test_route_create_session_unknown_channel(app_client):
    resp = app_client.post(
        "/api/channels/sessions",
        json={"room": "living-room", "channel_id": "channel.unknown.xyz"},
    )
    assert resp.status_code == 404


def test_route_join_session(app_client):
    create_resp = app_client.post(
        "/api/channels/sessions",
        json={"room": "kitchen", "channel_id": "channel.rewind.cartoons"},
    )
    session_id = create_resp.json()["session"]["session_id"]

    join_resp = app_client.post(
        f"/api/channels/sessions/{session_id}/join",
        json={"device_id": "tablet-02"},
    )
    assert join_resp.status_code == 200
    assert "tablet-02" in join_resp.json()["session"]["device_ids"]


def test_route_move_session(app_client):
    create_resp = app_client.post(
        "/api/channels/sessions",
        json={"room": "office", "channel_id": "channel.rewind.mtv"},
    )
    session_id = create_resp.json()["session"]["session_id"]

    move_resp = app_client.post(
        f"/api/channels/sessions/{session_id}/move",
        json={"target_room": "lounge"},
    )
    assert move_resp.status_code == 200
    assert move_resp.json()["session"]["room"] == "lounge"


def test_route_pause_and_resume_session(app_client):
    create_resp = app_client.post(
        "/api/channels/sessions",
        json={"room": "den", "channel_id": "channel.rewind.mtv"},
    )
    session_id = create_resp.json()["session"]["session_id"]

    pause_resp = app_client.post(f"/api/channels/sessions/{session_id}/pause")
    assert pause_resp.status_code == 200
    assert pause_resp.json()["session"]["state"] == "paused"

    resume_resp = app_client.post(f"/api/channels/sessions/{session_id}/resume")
    assert resume_resp.status_code == 200
    assert resume_resp.json()["session"]["state"] == "active"


def test_route_end_session_removes_from_active_list(app_client):
    create_resp = app_client.post(
        "/api/channels/sessions",
        json={"room": "guest", "channel_id": "channel.rewind.cartoons"},
    )
    session_id = create_resp.json()["session"]["session_id"]

    end_resp = app_client.delete(f"/api/channels/sessions/{session_id}")
    assert end_resp.status_code == 200
    assert end_resp.json()["success"] is True

    active_resp = app_client.get("/api/channels/sessions/active")
    active_ids = {item["session_id"] for item in active_resp.json()["sessions"]}
    assert session_id not in active_ids


def test_route_sync_session(app_client):
    create_resp = app_client.post(
        "/api/channels/sessions",
        json={"room": "bedroom", "channel_id": "channel.rewind.cartoons"},
    )
    session_id = create_resp.json()["session"]["session_id"]

    sync_resp = app_client.get(f"/api/channels/sessions/{session_id}/sync")
    assert sync_resp.status_code == 200
    data = sync_resp.json()
    assert "session" in data
    assert "channel" in data
