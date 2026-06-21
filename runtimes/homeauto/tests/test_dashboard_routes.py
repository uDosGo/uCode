from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from uhome_server.routes.dashboard import create_dashboard_routes


def _client(monkeypatch) -> TestClient:
    import uhome_server.routes.dashboard as mod

    monkeypatch.setattr(mod, "_ha_status", lambda: {"enabled": True, "status": "ok"})
    monkeypatch.setattr(
        mod,
        "_workspace_runtime_status",
        lambda: {
            "workspace_ref": "@memory/workspace/settings",
            "components": {
                "uhome": {
                    "defaults": {
                        "presentation": {"value": "thin-gui", "source": "template_workspace"},
                        "node_role": {"value": "server", "source": "template_workspace"},
                    }
                }
            },
        },
    )
    monkeypatch.setattr(
        mod,
        "_network_status",
        lambda: {
            "status": "degraded",
            "issues": ["offline_volumes_present"],
            "nodes": {"count": 2, "online": 1},
            "volumes": {"count": 4, "online": 3},
            "library_index": {"healthy": 1, "degraded": 1, "offline": 0},
        },
    )
    monkeypatch.setattr(
        mod,
        "_library_status",
        lambda: {"count": 1, "entries": [{"entry_id": "home-assistant", "kind": "library"}]},
    )

    app = FastAPI()
    app.include_router(create_dashboard_routes())
    return TestClient(app)


def test_dashboard_health(monkeypatch):
    client = _client(monkeypatch)
    response = client.get("/api/dashboard/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["bridge"] == "uhome-dashboard"
    assert body["ha_bridge_ready"] is True


def test_dashboard_summary_shape(monkeypatch):
    client = _client(monkeypatch)
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert set(body["subsystems"].keys()) == {"ha_bridge", "workspace_runtime", "network", "library"}
    assert body["workspace_runtime"]["components"]["uhome"]["defaults"]["presentation"]["value"] == "thin-gui"
    assert body["subsystems"]["network"]["nodes"]["count"] == 2
    assert body["subsystems"]["network"]["status"] == "degraded"


def test_dashboard_summary_degraded(monkeypatch):
    import uhome_server.routes.dashboard as mod

    monkeypatch.setattr(mod, "_ha_status", lambda: (_ for _ in ()).throw(RuntimeError("bridge down")))
    monkeypatch.setattr(mod, "_workspace_runtime_status", lambda: {"workspace_ref": "@memory/workspace/settings"})
    monkeypatch.setattr(
        mod,
        "_network_status",
        lambda: {
            "status": "offline",
            "issues": ["no_nodes_registered"],
            "nodes": {"count": 0, "online": 0},
            "volumes": {"count": 0, "online": 0},
            "library_index": {"healthy": 0, "degraded": 0, "offline": 0},
        },
    )
    monkeypatch.setattr(mod, "_library_status", lambda: {"count": 0, "entries": []})

    app = FastAPI()
    app.include_router(create_dashboard_routes())
    client = TestClient(app)
    body = client.get("/api/dashboard/summary").json()
    assert body["ok"] is False
    assert body["subsystems"]["ha_bridge"]["ok"] is False
