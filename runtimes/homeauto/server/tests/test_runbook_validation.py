from __future__ import annotations

from types import SimpleNamespace

from uhome_server.cluster.registry import (
    NodeRecord,
    NodeRegistry,
    StorageRegistry,
    StorageVolumeRecord,
    build_library_index,
    summarize_topology,
)
from uhome_server.routes import health as health_routes


def _mock_health_settings(monkeypatch) -> None:
    monkeypatch.setattr(
        health_routes,
        "get_runtime_settings",
        lambda: SimpleNamespace(
            config_dir=SimpleNamespace(exists=lambda: True),
            workspace_settings_dir=SimpleNamespace(exists=lambda: True),
            jellyfin_url="",
            jellyfin_api_key="",
        ),
    )


def test_storage_runbook_validation_missing_volume_then_recovery(monkeypatch, tmp_path):
    nodes = NodeRegistry(repo_root=tmp_path)
    volumes = StorageRegistry(repo_root=tmp_path)
    _mock_health_settings(monkeypatch)
    monkeypatch.setattr(health_routes, "get_node_registry", lambda: nodes)
    monkeypatch.setattr(health_routes, "get_storage_registry", lambda: volumes)

    nodes.upsert_node(NodeRecord(node_id="node-a", hostname="uhome-a.local", authority="primary", status="online"))
    volumes.upsert_volume(
        StorageVolumeRecord(
            volume_id="vol-a",
            label="Main Media",
            node_id="node-a",
            status="online",
            mount_path="/media/library-a",
            metadata={"library_keys": ["family-media"]},
        )
    )
    volumes.upsert_volume(
        StorageVolumeRecord(
            volume_id="vol-b",
            label="Secondary Media",
            node_id="node-a",
            status="online",
            mount_path="/media/library-b",
            metadata={"library_keys": ["family-media"]},
        )
    )

    missing = volumes.mark_volume_status("vol-b", "missing")
    assert missing is not None
    assert missing["recovery_state"] == "missing"

    storage_status, storage_issues = health_routes._check_storage_health()
    assert storage_status == "degraded"
    assert "1 volume(s) offline" in storage_issues

    degraded_topology = summarize_topology(nodes.list_nodes(), volumes.list_volumes())
    assert degraded_topology["status"] == "degraded"
    assert "offline_volumes_present" in degraded_topology["issues"]

    degraded_library = build_library_index(nodes.list_nodes(), volumes.list_volumes())
    assert degraded_library["libraries"][0]["status"] == "degraded"
    assert "partial_volume_availability" in degraded_library["libraries"][0]["issues"]

    returned = volumes.mark_volume_status("vol-b", "online")
    assert returned is not None
    assert returned["recovery_state"] == "returned"

    recovered_topology = summarize_topology(nodes.list_nodes(), volumes.list_volumes())
    assert recovered_topology["status"] == "degraded"
    assert "returned_volumes_present" in recovered_topology["issues"]
    assert recovered_topology["summary"]["offline_volume_count"] == 0

    storage_status, storage_issues = health_routes._check_storage_health()
    assert storage_status == "healthy"
    assert storage_issues == []


def test_offline_node_runbook_validation_primary_failover(monkeypatch, tmp_path):
    nodes = NodeRegistry(repo_root=tmp_path)
    volumes = StorageRegistry(repo_root=tmp_path)
    _mock_health_settings(monkeypatch)
    monkeypatch.setattr(health_routes, "get_node_registry", lambda: nodes)
    monkeypatch.setattr(health_routes, "get_storage_registry", lambda: volumes)

    nodes.upsert_node(NodeRecord(node_id="node-a", hostname="uhome-a.local", authority="primary", status="online"))
    nodes.upsert_node(NodeRecord(node_id="node-b", hostname="uhome-b.local", authority="secondary", status="online"))
    volumes.upsert_volume(
        StorageVolumeRecord(
            volume_id="vol-a",
            label="Main Media",
            node_id="node-b",
            status="online",
            mount_path="/media/library",
            metadata={"library_keys": ["family-media"]},
        )
    )

    offline = nodes.mark_node_status("node-a", "offline")
    assert offline is not None
    assert offline["status"] == "offline"

    node_status, node_issues = health_routes._check_nodes_health()
    assert node_status == "critical"
    assert "Primary authority node is offline" in node_issues

    promoted = nodes.set_node_authority("node-b", "primary")
    assert promoted is not None
    assert promoted["authority"] == "primary"

    post_failover_nodes = {item["node_id"]: item for item in nodes.list_nodes()}
    assert post_failover_nodes["node-a"]["authority"] == "secondary"
    assert post_failover_nodes["node-b"]["authority"] == "primary"

    node_status, node_issues = health_routes._check_nodes_health()
    assert node_status == "degraded"
    assert "1 node(s) offline" in node_issues

    topology = summarize_topology(nodes.list_nodes(), volumes.list_volumes())
    assert topology["status"] == "degraded"
    assert topology["summary"]["active_primary_node_count"] == 1
    assert "offline_nodes_present" in topology["issues"]

    library_index = build_library_index(nodes.list_nodes(), volumes.list_volumes())
    assert library_index["libraries"][0]["status"] == "healthy"
