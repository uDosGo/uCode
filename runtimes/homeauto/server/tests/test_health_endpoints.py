"""Tests for health and readiness endpoints."""

from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from uhome_server.cluster.registry import NodeRecord, StorageVolumeRecord
from uhome_server.routes import health as health_routes


def _client(monkeypatch):
    """Create test client with mocked registries."""
    node_store = {}
    volume_store = {}

    class _Nodes:
        def list_nodes(self):
            return list(node_store.values())

        def upsert_node(self, record):
            payload = record.to_dict()
            node_store[payload["node_id"]] = payload
            return payload

    class _Volumes:
        def list_volumes(self):
            return list(volume_store.values())

        def upsert_volume(self, record):
            payload = record.to_dict()
            volume_store[payload["volume_id"]] = payload
            return payload

    # Mock runtime settings to avoid filesystem checks
    mock_settings = Mock()
    mock_settings.config_dir = Mock()
    mock_settings.config_dir.exists = Mock(return_value=True)
    mock_settings.workspace_settings_dir = Mock()
    mock_settings.workspace_settings_dir.exists = Mock(return_value=True)
    mock_settings.jellyfin_url = None
    mock_settings.jellyfin_api_key = None

    monkeypatch.setattr(
        "uhome_server.routes.health.get_node_registry",
        lambda: _Nodes(),
    )
    monkeypatch.setattr(
        "uhome_server.routes.health.get_storage_registry",
        lambda: _Volumes(),
    )
    monkeypatch.setattr(
        "uhome_server.routes.health.get_runtime_settings",
        lambda: mock_settings,
    )

    app = FastAPI()
    app.include_router(health_routes.router)
    return TestClient(app), node_store, volume_store


def test_health_check_healthy(monkeypatch):
    """Test health check returns healthy when all components OK."""
    client, node_store, volume_store = _client(monkeypatch)

    # Setup healthy state
    node = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="primary",
        status="online",
    )
    node_store[node.node_id] = node.to_dict()

    volume = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="online",
    )
    volume_store[volume.volume_id] = volume.to_dict()

    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["components"]["nodes"]["status"] == "healthy"
    assert data["components"]["storage"]["status"] == "healthy"
    assert data["components"]["configuration"]["status"] == "healthy"
    assert data["components"]["nodes"]["issues"] == []
    assert data["components"]["storage"]["issues"] == []


def test_health_check_degraded_offline_node(monkeypatch):
    """Test health check returns degraded when secondary node offline."""
    client, node_store, volume_store = _client(monkeypatch)

    # Primary online, secondary offline
    primary = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="primary",
        status="online",
    )
    node_store[primary.node_id] = primary.to_dict()

    secondary = NodeRecord(
        node_id="node2",
        hostname="server2",
        authority="secondary",
        status="offline",
    )
    node_store[secondary.node_id] = secondary.to_dict()

    volume = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="online",
    )
    volume_store[volume.volume_id] = volume.to_dict()

    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "degraded"
    assert data["components"]["nodes"]["status"] == "degraded"
    assert "1 node(s) offline" in data["components"]["nodes"]["issues"]


def test_health_check_degraded_storage(monkeypatch):
    """Test health check returns degraded when storage has issues."""
    client, node_store, volume_store = _client(monkeypatch)

    node = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="primary",
        status="online",
    )
    node_store[node.node_id] = node.to_dict()

    # Some volumes offline
    vol1 = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="online",
    )
    volume_store[vol1.volume_id] = vol1.to_dict()

    vol2 = StorageVolumeRecord(
        volume_id="vol2",
        label="Backup Storage",
        status="offline",
    )
    volume_store[vol2.volume_id] = vol2.to_dict()

    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "degraded"
    assert data["components"]["storage"]["status"] == "degraded"
    assert "1 volume(s) offline" in data["components"]["storage"]["issues"]


def test_health_check_critical_no_primary(monkeypatch):
    """Test health check returns critical when no primary node."""
    client, node_store, volume_store = _client(monkeypatch)

    # Only secondary nodes
    secondary = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="secondary",
        status="online",
    )
    node_store[secondary.node_id] = secondary.to_dict()

    volume = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="online",
    )
    volume_store[volume.volume_id] = volume.to_dict()

    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "critical"
    assert data["components"]["nodes"]["status"] == "critical"
    assert "No primary authority node" in str(data["components"]["nodes"]["issues"])


def test_health_check_critical_primary_offline(monkeypatch):
    """Test health check returns critical when primary node offline."""
    client, node_store, volume_store = _client(monkeypatch)

    primary = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="primary",
        status="offline",
    )
    node_store[primary.node_id] = primary.to_dict()

    volume = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="online",
    )
    volume_store[volume.volume_id] = volume.to_dict()

    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "critical"
    assert data["components"]["nodes"]["status"] == "critical"
    assert "Primary authority node is offline" in str(data["components"]["nodes"]["issues"])


def test_health_check_critical_all_storage_offline(monkeypatch):
    """Test health check returns critical when all storage offline."""
    client, node_store, volume_store = _client(monkeypatch)

    node = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="primary",
        status="online",
    )
    node_store[node.node_id] = node.to_dict()

    volume = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="offline",
    )
    volume_store[volume.volume_id] = volume.to_dict()

    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "critical"
    assert data["components"]["storage"]["status"] == "critical"
    assert "All storage volumes offline" in str(data["components"]["storage"]["issues"])


def test_readiness_check_ready(monkeypatch):
    """Test readiness check returns ready when system can serve requests."""
    client, node_store, volume_store = _client(monkeypatch)

    node = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="primary",
        status="online",
    )
    node_store[node.node_id] = node.to_dict()

    volume = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="online",
    )
    volume_store[volume.volume_id] = volume.to_dict()

    response = client.get("/api/ready")
    assert response.status_code == 200

    data = response.json()
    assert data["ready"] is True
    assert "timestamp" in data


def test_readiness_check_ready_when_degraded(monkeypatch):
    """Test readiness check returns ready even when degraded (can still serve)."""
    client, node_store, volume_store = _client(monkeypatch)

    # Degraded node should still be ready
    node = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="primary",
        status="degraded",
    )
    node_store[node.node_id] = node.to_dict()

    volume = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="degraded",
    )
    volume_store[volume.volume_id] = volume.to_dict()

    response = client.get("/api/ready")
    assert response.status_code == 200

    data = response.json()
    assert data["ready"] is True


def test_readiness_check_not_ready_no_active_node(monkeypatch):
    """Test readiness check returns not ready when no active nodes."""
    client, node_store, volume_store = _client(monkeypatch)

    # All nodes offline
    node = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="primary",
        status="offline",
    )
    node_store[node.node_id] = node.to_dict()

    volume = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="online",
    )
    volume_store[volume.volume_id] = volume.to_dict()

    response = client.get("/api/ready")
    assert response.status_code == 200

    data = response.json()
    assert data["ready"] is False


def test_readiness_check_not_ready_no_active_storage(monkeypatch):
    """Test readiness check returns not ready when no active storage."""
    client, node_store, volume_store = _client(monkeypatch)

    node = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="primary",
        status="online",
    )
    node_store[node.node_id] = node.to_dict()

    # All storage offline
    volume = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="offline",
    )
    volume_store[volume.volume_id] = volume.to_dict()

    response = client.get("/api/ready")
    assert response.status_code == 200

    data = response.json()
    assert data["ready"] is False


def test_debug_registries(monkeypatch):
    """Test debug endpoint returns full registry state."""
    client, node_store, volume_store = _client(monkeypatch)

    node = NodeRecord(
        node_id="node1",
        hostname="server1",
        authority="primary",
        status="online",
    )
    node_store[node.node_id] = node.to_dict()

    volume = StorageVolumeRecord(
        volume_id="vol1",
        label="Main Storage",
        status="online",
    )
    volume_store[volume.volume_id] = volume.to_dict()

    response = client.get("/api/debug/registries")
    assert response.status_code == 200

    data = response.json()
    assert "timestamp" in data
    assert data["nodes"]["count"] == 1
    assert data["volumes"]["count"] == 1
    assert len(data["nodes"]["items"]) == 1
    assert len(data["volumes"]["items"]) == 1
    assert data["nodes"]["items"][0]["node_id"] == "node1"
    assert data["volumes"]["items"][0]["volume_id"] == "vol1"


def test_debug_registries_empty(monkeypatch):
    """Test debug endpoint handles empty registries."""
    client, node_store, volume_store = _client(monkeypatch)

    response = client.get("/api/debug/registries")
    assert response.status_code == 200

    data = response.json()
    assert data["nodes"]["count"] == 0
    assert data["volumes"]["count"] == 0
    assert data["nodes"]["items"] == []
    assert data["volumes"]["items"] == []
