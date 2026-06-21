"""Tests for first-class launcher/session REST API routes."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from uhome_server.app import create_app
from uhome_server.config import bootstrap_runtime


@pytest.fixture
def launcher_test_workspace(tmp_path: Path):
    """Set up a test workspace for launcher tests."""
    bootstrap_runtime(tmp_path)
    return tmp_path


@pytest.fixture
def launcher_api_client(launcher_test_workspace: Path, monkeypatch):
    """FastAPI test client with mocked repo_root."""
    monkeypatch.setattr("uhome_server.config.get_repo_root", lambda: launcher_test_workspace)
    monkeypatch.setattr("uhome_server.routes.launcher.get_repo_root", lambda: launcher_test_workspace)
    app = create_app()
    return TestClient(app)


def test_launcher_status_initial_state(launcher_api_client):
    """Test launcher status endpoint returns expected initial state."""
    response = launcher_api_client.get("/api/launcher/status")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify expected fields are present
    assert "supported_presentations" in data
    assert "supported_node_roles" in data
    assert "active_presentation" in data
    assert "running" in data
    assert "preferred_presentation" in data
    assert "node_role" in data
    
    # Initial state should not be running
    assert data["running"] is False
    assert data["active_presentation"] is None
    
    # Should have default preferred presentation
    assert data["preferred_presentation"] in ("thin-gui", "steam-console")
    assert data["node_role"] in ("server", "tv-node")


def test_launcher_menu_returns_actions(launcher_api_client):
    """Test launcher menu endpoint returns console action items."""
    response = launcher_api_client.get("/api/launcher/menu")

    assert response.status_code == 200
    data = response.json()
    assert data["menu_id"] == "uhome-console-main"
    item_ids = {item["id"] for item in data["items"]}
    assert "start-thin-gui" in item_ids
    assert "start-steam-console" in item_ids
    assert "open-network-capabilities" in item_ids


def test_launcher_start_default_presentation(launcher_api_client):
    """Test starting launcher with default presentation."""
    response = launcher_api_client.post(
        "/api/launcher/start",
        json={"presentation": None}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "started"
    assert data["active_presentation"] in ("thin-gui", "steam-console")
    assert "updated_at" in data
    assert "node_role" in data
    
    # Verify status reflects the started session
    status_response = launcher_api_client.get("/api/launcher/status")
    status_data = status_response.json()
    assert status_data["running"] is True
    assert status_data["active_presentation"] == data["active_presentation"]


def test_launcher_start_explicit_presentation(launcher_api_client):
    """Test starting launcher with explicit presentation mode."""
    response = launcher_api_client.post(
        "/api/launcher/start",
        json={"presentation": "thin-gui"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "started"
    assert data["active_presentation"] == "thin-gui"


def test_launcher_start_invalid_presentation(launcher_api_client):
    """Test starting launcher with invalid presentation returns 400."""
    response = launcher_api_client.post(
        "/api/launcher/start",
        json={"presentation": "invalid-mode"}
    )
    
    assert response.status_code == 400
    assert "detail" in response.json()


def test_launcher_stop_session(launcher_api_client):
    """Test stopping a running launcher session."""
    # Start a session first
    launcher_api_client.post(
        "/api/launcher/start",
        json={"presentation": "thin-gui"}
    )
    
    # Stop the session
    response = launcher_api_client.post("/api/launcher/stop")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "stopped"
    assert data["active_presentation"] is None
    
    # Verify status reflects stopped state
    status_response = launcher_api_client.get("/api/launcher/status")
    status_data = status_response.json()
    assert status_data["running"] is False
    assert status_data["active_presentation"] is None


def test_launcher_session_persistence(launcher_api_client, launcher_test_workspace: Path):
    """Test that launcher session state persists across requests."""
    # Start session
    start_response = launcher_api_client.post(
        "/api/launcher/start",
        json={"presentation": "steam-console"}
    )
    start_data = start_response.json()
    
    # Verify state file was created
    state_path = launcher_test_workspace / "memory" / "kiosk" / "uhome" / "presentation.json"
    assert state_path.exists()
    
    # Verify state file content
    state_content = json.loads(state_path.read_text())
    assert state_content["active_presentation"] == "steam-console"
    assert state_content["last_action"] == "start"
    
    # Get status in another request
    status_response = launcher_api_client.get("/api/launcher/status")
    status_data = status_response.json()
    assert status_data["active_presentation"] == "steam-console"
    assert status_data["running"] is True


def test_launcher_restart_changes_presentation(launcher_api_client):
    """Test restarting launcher with a different presentation mode."""
    # Start with thin-gui
    launcher_api_client.post(
        "/api/launcher/start",
        json={"presentation": "thin-gui"}
    )
    
    # Start with steam-console (implicit restart)
    response = launcher_api_client.post(
        "/api/launcher/start",
        json={"presentation": "steam-console"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["active_presentation"] == "steam-console"
    
    # Verify status shows new presentation
    status_response = launcher_api_client.get("/api/launcher/status")
    status_data = status_response.json()
    assert status_data["active_presentation"] == "steam-console"


def test_launcher_empty_body_uses_default(launcher_api_client):
    """Test that empty request body uses default presentation."""
    response = launcher_api_client.post(
        "/api/launcher/start",
        json={}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
    assert data["active_presentation"] in ("thin-gui", "steam-console")
