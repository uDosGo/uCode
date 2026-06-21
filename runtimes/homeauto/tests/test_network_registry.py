from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from uhome_server.routes import network as network_routes
from uhome_server.cluster.registry import (
    NodeRecord,
    NodeRegistry,
    StorageRegistry,
    StorageVolumeRecord,
    build_library_index,
    summarize_topology,
)


def _client(monkeypatch):
    node_store = {}
    volume_store = {}

    class _Nodes:
        def list_nodes(self):
            return list(node_store.values())

        def upsert_node(self, record):
            payload = record.to_dict()
            node_store[payload["node_id"]] = payload
            return payload

        def mark_node_status(self, node_id, status):
            item = node_store.get(node_id)
            if item is None:
                return None
            item["status"] = status
            return item

        def set_node_authority(self, node_id, authority):
            item = node_store.get(node_id)
            if item is None:
                return None
            if authority == "primary" and item.get("status") not in {"online", "degraded"}:
                raise ValueError("Only online or degraded nodes can become primary")
            if authority == "primary":
                for candidate in node_store.values():
                    if candidate["node_id"] != node_id and candidate.get("authority") == "primary":
                        candidate["authority"] = "secondary"
            elif item.get("authority") == "primary":
                has_other_active_primary = any(
                    candidate["node_id"] != node_id
                    and candidate.get("authority") == "primary"
                    and candidate.get("status") in {"online", "degraded"}
                    for candidate in node_store.values()
                )
                if not has_other_active_primary:
                    raise ValueError("Cannot demote the active primary without promoting a replacement")
            item["authority"] = authority
            return item

    class _Volumes:
        def list_volumes(self):
            return list(volume_store.values())

        def upsert_volume(self, record):
            payload = record.to_dict()
            volume_store[payload["volume_id"]] = payload
            return payload

        def mark_volume_status(self, volume_id, status):
            item = volume_store.get(volume_id)
            if item is None:
                return None
            item["status"] = status
            return item

    monkeypatch.setattr(network_routes, "get_node_registry", lambda: _Nodes())
    monkeypatch.setattr(network_routes, "get_storage_registry", lambda: _Volumes())
    app = FastAPI()
    app.include_router(network_routes.router)
    return TestClient(app)


def test_upsert_and_list_nodes(monkeypatch):
    client = _client(monkeypatch)
    response = client.post(
        "/api/network/nodes",
        json={
            "node_id": "node-a",
            "hostname": "uhome-a.local",
            "authority": "primary",
            "capabilities": ["ingest", "playback"],
        },
    )
    assert response.status_code == 200
    listed = client.get("/api/network/nodes")
    assert listed.status_code == 200
    body = listed.json()
    assert body["count"] == 1
    assert body["nodes"][0]["node_id"] == "node-a"


def test_update_node_status(monkeypatch):
    client = _client(monkeypatch)
    client.post("/api/network/nodes", json={"node_id": "node-a", "hostname": "uhome-a.local"})
    response = client.post("/api/network/nodes/node-a/status", json={"status": "offline"})
    assert response.status_code == 200
    assert response.json()["node"]["status"] == "offline"


def test_handoff_primary_authority(monkeypatch):
    client = _client(monkeypatch)
    client.post(
        "/api/network/nodes",
        json={"node_id": "node-a", "hostname": "uhome-a.local", "authority": "primary", "status": "online"},
    )
    client.post(
        "/api/network/nodes",
        json={"node_id": "node-b", "hostname": "uhome-b.local", "authority": "secondary", "status": "online"},
    )
    response = client.post("/api/network/nodes/node-b/authority", json={"authority": "primary"})
    assert response.status_code == 200
    listed = client.get("/api/network/nodes").json()["nodes"]
    nodes_by_id = {item["node_id"]: item for item in listed}
    assert nodes_by_id["node-b"]["authority"] == "primary"
    assert nodes_by_id["node-a"]["authority"] == "secondary"


def test_reject_promoting_offline_primary(monkeypatch):
    client = _client(monkeypatch)
    client.post(
        "/api/network/nodes",
        json={"node_id": "node-a", "hostname": "uhome-a.local", "authority": "secondary", "status": "offline"},
    )
    response = client.post("/api/network/nodes/node-a/authority", json={"authority": "primary"})
    assert response.status_code == 400
    assert "Only online or degraded nodes can become primary" in response.json()["detail"]


def test_reject_invalid_volume_status_request(monkeypatch):
    client = _client(monkeypatch)
    response = client.post("/api/network/volumes/missing/status", json={"status": "unknown"})
    assert response.status_code == 422


def test_upsert_and_list_volumes(monkeypatch):
    client = _client(monkeypatch)
    response = client.post(
        "/api/network/volumes",
        json={
            "volume_id": "vol-1",
            "label": "Media Array A",
            "kind": "partition",
            "node_id": "node-a",
            "mount_path": "/srv/media-a",
            "tags": ["movies", "archive"],
        },
    )
    assert response.status_code == 200
    listed = client.get("/api/network/volumes")
    assert listed.status_code == 200
    body = listed.json()
    assert body["count"] == 1
    assert body["volumes"][0]["volume_id"] == "vol-1"


def test_update_volume_status_404(monkeypatch):
    client = _client(monkeypatch)
    response = client.post("/api/network/volumes/missing/status", json={"status": "offline"})
    assert response.status_code == 404


def test_topology_summary_reports_degraded_offline_storage(monkeypatch):
    client = _client(monkeypatch)
    client.post(
        "/api/network/nodes",
        json={
            "node_id": "node-a",
            "hostname": "uhome-a.local",
            "authority": "primary",
            "status": "online",
        },
    )
    client.post(
        "/api/network/volumes",
        json={
            "volume_id": "vol-1",
            "label": "Media A",
            "node_id": "node-a",
            "status": "offline",
        },
    )
    response = client.get("/api/network/topology")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert "offline_volumes_present" in body["issues"]
    assert body["summary"]["active_primary_node_count"] == 1


def test_library_index_reports_partial_availability(monkeypatch):
    client = _client(monkeypatch)
    client.post(
        "/api/network/nodes",
        json={"node_id": "node-a", "hostname": "uhome-a.local", "authority": "primary", "status": "online"},
    )
    client.post(
        "/api/network/volumes",
        json={
            "volume_id": "vol-1",
            "label": "Media A",
            "node_id": "node-a",
            "status": "online",
            "mount_path": "/srv/media-a",
            "metadata": {"library_keys": ["family-media"]},
        },
    )
    client.post(
        "/api/network/volumes",
        json={
            "volume_id": "vol-2",
            "label": "Media B",
            "node_id": "node-a",
            "status": "offline",
            "mount_path": "/srv/media-b",
            "metadata": {"library_keys": ["family-media"]},
        },
    )
    response = client.get("/api/network/library-index")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["libraries"][0]["library_key"] == "family-media"
    assert body["libraries"][0]["status"] == "degraded"
    assert body["libraries"][0]["available_volume_count"] == 1
    assert body["libraries"][0]["offline_volume_count"] == 1


def test_network_capabilities_combines_streaming_launcher_and_client_profiles(monkeypatch):
    client = _client(monkeypatch)

    class _Channels:
        def list_channels(self):
            return [
                {
                    "channel_id": "channel.rewind.mtv",
                    "display_name": "Music TV Rewind",
                    "media_mode": "audio-video",
                }
            ]

    class _Clients:
        def profile_summary(self):
            return {
                "count": 2,
                "profiles": {"controller": 1, "remote": 1, "touch": 0},
                "clients": [
                    {
                        "client_id": "living-room-tv",
                        "device_name": "Living Room TV",
                        "platform": "android-tv",
                        "capability_profile": "remote",
                        "last_seen": "2026-03-17T00:00:00Z",
                    }
                ],
            }

    class _Launcher:
        def get_status(self):
            return {
                "running": True,
                "active_presentation": "steam-console",
                "preferred_presentation": "steam-console",
            }

    monkeypatch.setattr(network_routes, "get_repo_root", lambda: Path("/tmp/uhome-server"))
    monkeypatch.setattr(network_routes, "get_channel_service", lambda: _Channels())
    monkeypatch.setattr(network_routes, "get_client_capability_service", lambda repo_root=None: _Clients())
    monkeypatch.setattr(network_routes, "get_uhome_presentation_service", lambda repo_root=None: _Launcher())
    monkeypatch.setattr(
        network_routes,
        "playback_status",
        lambda params: {
            "jellyfin_configured": True,
            "jellyfin_reachable": True,
            "active_sessions": [{"title": "Example Movie"}],
        },
    )

    response = client.get("/api/network/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["streaming"]["channel_count"] == 1
    assert body["streaming"]["jellyfin_reachable"] is True
    assert body["streaming"]["active_playback_sessions"] == 1
    assert body["launcher"]["active_presentation"] == "steam-console"
    assert body["clients"]["profiles"]["remote"] == 1


def test_registry_persists_and_summarizes_topology(tmp_path):
    nodes = NodeRegistry(repo_root=tmp_path)
    volumes = StorageRegistry(repo_root=tmp_path)
    nodes.upsert_node(
        NodeRecord(
            node_id="node-a",
            hostname="uhome-a.local",
            authority="primary",
            status="online",
            capabilities=["ingest", "playback"],
        )
    )
    nodes.upsert_node(
        NodeRecord(
            node_id="node-b",
            hostname="uhome-b.local",
            authority="secondary",
            status="offline",
            capabilities=["storage"],
        )
    )
    volumes.upsert_volume(
        StorageVolumeRecord(
            volume_id="vol-1",
            label="Media A",
            node_id="node-b",
            status="online",
            mount_path="/srv/media-a",
        )
    )
    reloaded_nodes = NodeRegistry(repo_root=tmp_path).list_nodes()
    reloaded_volumes = StorageRegistry(repo_root=tmp_path).list_volumes()
    summary = summarize_topology(reloaded_nodes, reloaded_volumes)
    assert summary["status"] == "degraded"
    assert "offline_nodes_present" in summary["issues"]
    assert "volumes_on_unavailable_nodes" in summary["issues"]
    assert summary["summary"]["node_count"] == 2
    assert summary["summary"]["volume_count"] == 1


def test_volume_recovery_and_library_index(tmp_path):
    nodes = NodeRegistry(repo_root=tmp_path)
    volumes = StorageRegistry(repo_root=tmp_path)
    nodes.upsert_node(NodeRecord(node_id="node-a", hostname="uhome-a.local", authority="primary", status="online"))
    volumes.upsert_volume(
        StorageVolumeRecord(
            volume_id="vol-1",
            label="Media A",
            node_id="node-a",
            status="online",
            mount_path="/srv/media-a",
            metadata={"library_keys": ["family-media"]},
        )
    )
    missing = volumes.mark_volume_status("vol-1", "missing")
    assert missing is not None
    assert missing["recovery_state"] == "missing"
    returned = volumes.mark_volume_status("vol-1", "online")
    assert returned is not None
    assert returned["recovery_state"] == "returned"

    summary = summarize_topology(nodes.list_nodes(), volumes.list_volumes())
    assert "returned_volumes_present" in summary["issues"]

    library_index = build_library_index(nodes.list_nodes(), volumes.list_volumes())
    assert library_index["libraries"][0]["status"] == "degraded"
    assert "returned_volumes_present" in library_index["libraries"][0]["issues"]


def test_registry_rejects_invalid_status_values(tmp_path):
    nodes = NodeRegistry(repo_root=tmp_path)
    try:
        nodes.upsert_node(NodeRecord(node_id="node-a", hostname="uhome-a.local", status="broken"))
    except ValueError as exc:
        assert "Invalid status" in str(exc)
    else:
        raise AssertionError("Expected invalid node status to be rejected")

    volumes = StorageRegistry(repo_root=tmp_path)
    try:
        volumes.upsert_volume(StorageVolumeRecord(volume_id="vol-1", label="Media A", status="ghost"))
    except ValueError as exc:
        assert "Invalid status" in str(exc)
    else:
        raise AssertionError("Expected invalid volume status to be rejected")


def test_library_index_can_stay_healthy_with_multiple_online_volumes(tmp_path):
    nodes = NodeRegistry(repo_root=tmp_path)
    volumes = StorageRegistry(repo_root=tmp_path)
    nodes.upsert_node(NodeRecord(node_id="node-a", hostname="uhome-a.local", authority="primary", status="online"))
    volumes.upsert_volume(
        StorageVolumeRecord(
            volume_id="vol-1",
            label="Media A",
            node_id="node-a",
            status="online",
            mount_path="/srv/media-a",
            metadata={"library_keys": ["family-media"]},
        )
    )
    volumes.upsert_volume(
        StorageVolumeRecord(
            volume_id="vol-2",
            label="Media B",
            node_id="node-a",
            status="online",
            mount_path="/srv/media-b",
            metadata={"library_keys": ["family-media"]},
        )
    )
    library_index = build_library_index(nodes.list_nodes(), volumes.list_volumes())
    assert library_index["summary"]["healthy"] == 1
    assert library_index["libraries"][0]["status"] == "healthy"


def test_registry_primary_handoff_demotes_previous_primary(tmp_path):
    nodes = NodeRegistry(repo_root=tmp_path)
    nodes.upsert_node(NodeRecord(node_id="node-a", hostname="uhome-a.local", authority="primary", status="online"))
    nodes.upsert_node(NodeRecord(node_id="node-b", hostname="uhome-b.local", authority="secondary", status="online"))
    promoted = nodes.set_node_authority("node-b", "primary")
    assert promoted is not None
    listed = {item["node_id"]: item for item in nodes.list_nodes()}
    assert listed["node-b"]["authority"] == "primary"
    assert listed["node-a"]["authority"] == "secondary"


def test_registry_rejects_demoting_last_active_primary(tmp_path):
    nodes = NodeRegistry(repo_root=tmp_path)
    nodes.upsert_node(NodeRecord(node_id="node-a", hostname="uhome-a.local", authority="primary", status="online"))
    try:
        nodes.set_node_authority("node-a", "secondary")
    except ValueError as exc:
        assert "Cannot demote the active primary" in str(exc)
    else:
        raise AssertionError("Expected last active primary demotion to be rejected")
