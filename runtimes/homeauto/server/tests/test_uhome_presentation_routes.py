from fastapi import FastAPI
from fastapi.testclient import TestClient

from uhome_server.routes import platform as platform_routes


class _UHomeSvc:
    active_presentation = None
    preferred_presentation = "thin-gui"
    node_role = "server"

    def get_status(self):
        return {
            "supported_presentations": ["thin-gui", "steam-console"],
            "supported_node_roles": ["server", "tv-node"],
            "active_presentation": self.active_presentation,
            "running": self.active_presentation is not None,
            "preferred_presentation": self.preferred_presentation,
            "preferred_presentation_source": "template_workspace",
            "node_role": self.node_role,
            "node_role_source": "template_workspace",
        }

    def start(self, presentation):
        presentation = presentation or self.preferred_presentation
        if presentation not in {"thin-gui", "steam-console"}:
            raise ValueError("Unsupported uHOME presentation")
        self.active_presentation = presentation
        return {"active_presentation": presentation, "node_role": self.node_role, "last_action": "start"}

    def stop(self):
        self.active_presentation = None
        return {"active_presentation": None, "node_role": self.node_role, "last_action": "stop"}


def _client(monkeypatch):
    monkeypatch.setattr(platform_routes, "get_uhome_presentation_service", lambda repo_root=None: _UHomeSvc())
    monkeypatch.setattr(
        platform_routes,
        "get_template_workspace_service",
        lambda repo_root=None: type(
            "_Svc",
            (),
            {
                "component_contract": lambda self, component_id: {"component_id": component_id, "workspace_ref": "@memory/workspace/settings"},
                "component_snapshot": lambda self, component_id: {"component_id": component_id, "settings": {}},
            },
        )(),
    )
    app = FastAPI()
    app.include_router(platform_routes.create_platform_routes(auth_guard=None))
    return TestClient(app)


def test_uhome_presentation_routes(monkeypatch):
    client = _client(monkeypatch)
    status = client.get("/api/platform/uhome/status")
    assert status.status_code == 200
    assert status.json()["presentation"]["preferred_presentation"] == "thin-gui"

    start = client.post("/api/platform/uhome/presentation/start", json={"presentation": ""})
    assert start.status_code == 200
    assert start.json()["state"]["active_presentation"] == "thin-gui"

    invalid = client.post("/api/platform/uhome/presentation/start", json={"presentation": "bad"})
    assert invalid.status_code == 400

    stop = client.post("/api/platform/uhome/presentation/stop")
    assert stop.status_code == 200
    assert stop.json()["state"]["active_presentation"] is None
