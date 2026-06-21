from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from uhome_server.library.catalog import ContainerCatalogService
from uhome_server.routes import containers as container_routes
from uhome_server.routes import library as library_routes


def test_container_catalog_discovers_home_assistant_library_entry():
    service = ContainerCatalogService(Path(__file__).resolve().parents[1])
    entry = service.get_entry("home-assistant")
    assert entry is not None
    assert entry.kind == "library"
    assert entry.metadata["container_type"] == "git"
    assert entry.metadata["browser_route"] == "/ui/home-assistant"
    assert entry.metadata["resolved_repo_path"].endswith("library/containers/home-assistant")


def test_list_available_containers_route(monkeypatch):
    monkeypatch.setattr(
        container_routes,
        "get_launcher",
        lambda: type(
            "_Launcher",
            (),
            {
                "list_available": lambda self: [
                    {
                        "id": "home-assistant",
                        "name": "Home Assistant",
                        "port": 8765,
                        "browser_route": "/ui/home-assistant",
                        "state": "not_cloned",
                        "running": False,
                    }
                ]
            },
        )(),
    )
    app = FastAPI()
    app.include_router(container_routes.router)
    client = TestClient(app)
    response = client.get("/api/containers/list/available")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["containers"][0]["id"] == "home-assistant"


def test_library_clone_route(monkeypatch, tmp_path):
    class _CloneManager:
        def list_repos(self):
            return []

        def clone(self, repo: str, branch: str = "main"):
            path = tmp_path / "library" / "containers" / "home-assistant"
            path.mkdir(parents=True, exist_ok=True)
            return type(
                "_Repo",
                (),
                {
                    "to_dict": lambda self: {
                        "name": "home-assistant",
                        "owner": "home-assistant",
                        "url": repo,
                        "branch": branch,
                        "commit": "deadbeef1234",
                        "cloned_at": "2026-03-07T00:00:00Z",
                        "path": str(path),
                    }
                },
            )()

        def update(self, name: str):
            return True

        def remove(self, name: str):
            return True

    monkeypatch.setattr(library_routes, "get_library_clone_manager", lambda: _CloneManager())
    app = FastAPI()
    app.include_router(library_routes.router)
    client = TestClient(app)
    response = client.post("/api/library/repos/clone?repo=home-assistant/core&branch=master")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["repo"]["name"] == "home-assistant"
