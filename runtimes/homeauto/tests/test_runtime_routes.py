from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from uhome_server.routes import runtime as runtime_routes


def _client(monkeypatch) -> TestClient:
    monkeypatch.setattr(
        runtime_routes,
        "_repo_layout_status",
        lambda: {
            "repo_root": "/tmp/uhome-server",
            "exists": True,
            "missing_paths": [],
            "paths": {"defaults": "/tmp/uhome-server/defaults"},
        },
    )
    monkeypatch.setattr(
        runtime_routes,
        "_workspace_status",
        lambda: {
            "workspace_ref": "@memory/workspace/settings",
            "component_id": "uhome",
            "instructions_ref": "docs/workspace/instructions/uhome.md",
            "settings_keys": ["node_role", "presentation_mode"],
        },
    )
    monkeypatch.setattr(
        runtime_routes,
        "_config_status",
        lambda: {
            "config_path": "/tmp/uhome-server/memory/config/uhome.json",
            "legacy_config_path": "/tmp/uhome-server/memory/config/wizard.json",
            "active_config_path": "/tmp/uhome-server/memory/config/uhome.json",
            "active_config_exists": True,
            "legacy_config_fallback": False,
            "ha_bridge_enabled_env": False,
            "hdhomerun_host": "",
        },
    )
    monkeypatch.setattr(
        runtime_routes,
        "_ha_bridge_status",
        lambda: {"bridge": "uhome-ha", "enabled": False, "status": "disabled"},
    )
    monkeypatch.setattr(
        runtime_routes,
        "_jellyfin_status",
        lambda: {
            "jellyfin_configured": False,
            "jellyfin_reachable": False,
            "presentation_mode": "thin-gui",
            "preferred_target_client": "living-room",
            "note": "Set JELLYFIN_URL to enable live playback status.",
        },
    )
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    return TestClient(app)


def test_runtime_readiness_reports_required_health(monkeypatch):
    client = _client(monkeypatch)
    response = client.get("/api/runtime/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["status"] == "ready"
    assert body["checks"]["repo_layout"]["ok"] is True
    assert body["checks"]["config"]["ok"] is True
    assert body["checks"]["ha_bridge"]["required"] is False


def test_runtime_readiness_degrades_when_required_check_fails(monkeypatch):
    monkeypatch.setattr(
        runtime_routes,
        "_repo_layout_status",
        lambda: (_ for _ in ()).throw(RuntimeError("repo layout missing")),
    )
    monkeypatch.setattr(runtime_routes, "_config_status", lambda: {"active_config_exists": False})
    monkeypatch.setattr(runtime_routes, "_workspace_status", lambda: {"workspace_ref": "@memory/workspace/settings"})
    monkeypatch.setattr(runtime_routes, "_ha_bridge_status", lambda: {"enabled": True, "status": "ok"})
    monkeypatch.setattr(runtime_routes, "_jellyfin_status", lambda: {"jellyfin_configured": True, "jellyfin_reachable": True})
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    client = TestClient(app)
    body = client.get("/api/runtime/ready").json()
    assert body["ok"] is False
    assert body["status"] == "degraded"
    assert body["checks"]["repo_layout"]["error"] == "repo layout missing"


def test_runtime_info_shape(monkeypatch):
    client = _client(monkeypatch)
    response = client.get("/api/runtime/info")
    assert response.status_code == 200
    body = response.json()
    assert body["app"] == "uHOME Server"
    assert "python_version" in body
    assert "platform" in body
    assert "settings" in body


def test_sync_record_contract_route_reports_bundled_contract(monkeypatch):
    client = _client(monkeypatch)
    response = client.get("/api/runtime/contracts/sync-record")
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "v2.0.4"
    assert body["owner"] == "uHOME-server"
    assert "binder_project" in body["record_types"]
    assert "sync-record-contract.json" in body["contract_path"]


def test_sync_record_validation_route_accepts_valid_envelope(monkeypatch):
    monkeypatch.setattr(
        runtime_routes,
        "sync_record_validation_result",
        lambda payload: (
            {
                "ok": True,
                "contract_version": payload["contract_version"],
                "counts": {
                    "contacts": len(payload["contacts"]),
                    "activities": len(payload["activities"]),
                    "binders": len(payload["binders"]),
                    "sync_metadata": len(payload["sync_metadata"]),
                },
            },
            200,
        ),
    )
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    client = TestClient(app)
    response = client.post(
        "/api/runtime/sync-records/validate",
        json={
            "contract_version": "v2.0.4",
            "contacts": [],
            "activities": [],
            "binders": [],
            "sync_metadata": [],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["counts"]["contacts"] == 0


def test_sync_record_validation_route_rejects_invalid_envelope(monkeypatch):
    monkeypatch.setattr(
        runtime_routes,
        "sync_record_validation_result",
        lambda payload: (
            {
                "ok": False,
                "error": "sync-record-validation-failed",
                "issues": [{"loc": ["contract_version"], "msg": "invalid"}],
            },
            400,
        ),
    )
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    client = TestClient(app)
    response = client.post(
        "/api/runtime/sync-records/validate",
        json={"contract_version": "bad"},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
    assert body["error"] == "sync-record-validation-failed"


def test_workflow_automation_contract_route_reports_uhome_bundle(monkeypatch):
    client = _client(monkeypatch)
    response = client.get("/api/runtime/contracts/workflow-automation")
    assert response.status_code == 200
    body = response.json()
    assert body["workflow_owner"] == "uHOME-server"
    assert body["automation_fulfillment_owner"] == "uHOME-server"
    assert body["automation_job_contract"].startswith("uhome_server/contracts/")
    assert "integration_note" in body


def test_uhome_network_policy_contract_route_reports_uhome_bundle(monkeypatch):
    monkeypatch.setattr(
        runtime_routes,
        "uhome_network_policy_contract_info",
        lambda: {
            "contract_path": "/tmp/uhome-network-policy-contract.json",
            "schema_path": "/tmp/uhome-network-policy.schema.json",
            "version": "v2.0.4",
            "owner": "uHOME-server",
            "package": "uhome-network-policy-contract",
            "schema_title": "UHomeNetworkPolicy",
            "profiles": ["beacon", "crypt", "home", "lan", "tomb"],
            "runtime_owners": ["uHOME-server"],
            "policy_owners": ["uHOME-server"],
            "routes": {"contract": {"path": "/api/runtime/contracts/uhome-network-policy"}},
            "networking_model": "regular-lan",
            "deployment": {"default_profile": "lan"},
            "future_integration": "ubuntu later",
        },
    )
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    client = TestClient(app)
    response = client.get("/api/runtime/contracts/uhome-network-policy")
    assert response.status_code == 200
    body = response.json()
    assert body["owner"] == "uHOME-server"
    assert "lan" in body["profiles"]
    assert body["runtime_owners"] == ["uHOME-server"]


def test_uhome_network_policy_validation_route_accepts_and_rejects_payloads(monkeypatch):
    monkeypatch.setattr(
        runtime_routes,
        "uhome_network_policy_validation_result",
        lambda payload: (
            {
                "ok": payload["profile_id"] == "beacon",
                "contract_version": payload.get("contract_version", "v2.0.4"),
                "profile_id": payload.get("profile_id"),
                "runtime_owner": "uHOME-server",
                "policy_owner": "uHOME-server",
                "consumer_repos": payload.get("consumer_repos", []),
                "error": None if payload["profile_id"] == "beacon" else "uhome-network-policy-validation-failed",
            },
            200 if payload["profile_id"] == "beacon" else 400,
        ),
    )
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    client = TestClient(app)

    valid = client.post(
        "/api/runtime/contracts/uhome-network-policy/validate",
        json={
            "contract_version": "v2.0.4",
            "profile_id": "beacon",
            "consumer_repos": ["uHOME-server"],
        },
    )
    assert valid.status_code == 200
    assert valid.json()["ok"] is True

    invalid = client.post(
        "/api/runtime/contracts/uhome-network-policy/validate",
        json={
            "contract_version": "v2.0.4",
            "profile_id": "tomb",
            "consumer_repos": ["uHOME-server"],
        },
    )
    assert invalid.status_code == 400
    assert invalid.json()["error"] == "uhome-network-policy-validation-failed"


def test_uhome_network_policy_schema_route_returns_bundled_schema():
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    client = TestClient(app)
    response = client.get("/api/runtime/contracts/uhome-network-policy/schema")
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "UHomeNetworkPolicy"
    assert "lan" in body["properties"]["profile_id"]["enum"]


def test_uhome_network_policy_lan_payload_validates_end_to_end():
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    client = TestClient(app)
    payload = {
        "contract_version": "v2.0.4",
        "profile_id": "lan",
        "network_scope": "private",
        "visibility": "visible",
        "auth_mode": "password-protected",
        "vault_access": "local-only",
        "internet_sharing": "disabled",
        "runtime_owner": "uHOME-server",
        "policy_owner": "uHOME-server",
        "consumer_repos": ["uHOME-server"],
        "secret_refs": [],
    }
    response = client.post("/api/runtime/contracts/uhome-network-policy/validate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["profile_id"] == "lan"


def test_automation_routes_queue_and_record_results(monkeypatch):
    class _Store:
        def status(self):
            return {
                "contract_version": "v2.0.4",
                "owner": "uHOME-server",
                "queued_jobs": 0,
                "recorded_results": 0,
            }

        def list_jobs(self):
            return {"contract_version": "v2.0.4", "updated_at": None, "items": []}

        def queue_job(self, payload):
            return {
                "contract_version": "v2.0.4",
                "job_id": payload["job_id"],
                "requested_capability": payload["requested_capability"],
                "origin_surface": payload["origin_surface"],
                "workflow_id": payload["policy_flags"]["workflow_id"],
            }

        def cancel_job(self, job_id):
            return {"contract_version": "v2.0.4", "status": "cancelled", "job_id": job_id}

        def list_results(self):
            return {"contract_version": "v2.0.4", "updated_at": None, "items": []}

        def record_result(self, payload):
            return {
                "contract_version": "v2.0.4",
                "job_id": payload["job_id"],
                "status": payload["status"],
                "suggested_workflow_action": payload["suggested_workflow_action"],
            }

        def retry_job(self, job_id):
            return {"contract_version": "v2.0.4", "status": "queued", "retried_from": job_id}

        def process_next_job(self, payload):
            return {
                "contract_version": "v2.0.4",
                "status": "processed",
                "job": {"job_id": "job:test"},
                "result": {"job_id": "job:test", "status": payload.get("status", "completed")},
            }

    monkeypatch.setattr(runtime_routes, "get_automation_store", lambda: _Store())
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    client = TestClient(app)

    status = client.get("/api/runtime/automation/status")
    assert status.status_code == 200
    assert status.json()["owner"] == "uHOME-server"

    queued = client.post(
        "/api/runtime/automation/jobs",
        json={
            "job_id": "job:test",
            "requested_capability": "render-export",
            "payload_ref": "memory://render/export",
            "origin_surface": "uHOME-kiosk",
            "policy_flags": {"workflow_id": "mission-beta", "step_id": "step-4"},
            "queued_at": "2026-03-15T00:00:00Z",
        },
    )
    assert queued.status_code == 200
    assert queued.json()["job_id"] == "job:test"
    assert queued.json()["workflow_id"] == "mission-beta"

    cancelled = client.post("/api/runtime/automation/jobs/job:test/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    recorded = client.post(
        "/api/runtime/automation/results",
        json={
            "job_id": "job:test",
            "status": "completed",
            "output_refs": [],
            "event_refs": [],
            "completed_at": "2026-03-15T00:10:00Z",
            "suggested_workflow_action": "advance",
        },
    )
    assert recorded.status_code == 200
    assert recorded.json()["status"] == "completed"

    retried = client.post("/api/runtime/automation/results/job:test/retry")
    assert retried.status_code == 200
    assert retried.json()["status"] == "queued"

    processed = client.post(
        "/api/runtime/automation/process-next",
        json={"status": "completed"},
    )
    assert processed.status_code == 200
    assert processed.json()["status"] == "processed"


def test_thin_automation_route_serves_html(monkeypatch):
    class _Store:
        def status(self):
            return {"queued_jobs": 1, "recorded_results": 1}

        def list_jobs(self):
            return {"items": [{"job_id": "job:test"}]}

        def list_results(self):
            return {"items": [{"job_id": "job:test", "status": "completed"}]}

    monkeypatch.setattr(runtime_routes, "get_automation_store", lambda: _Store())
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    client = TestClient(app)
    response = client.get("/api/runtime/thin/automation")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Automation Status" in response.text
    assert "/static/thin/prose.css" in response.text
    assert "/api/runtime/thin/read" in response.text


def test_thin_read_route_uses_prose_shell():
    from uhome_server.app import app as full_app

    client = TestClient(full_app)
    response = client.get("/api/runtime/thin/read")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "prose" in response.text
    assert "/static/thin/prose.css" in response.text


def test_thin_browse_docs_under_pathway():
    from uhome_server.app import app as full_app

    client = TestClient(full_app)
    response = client.get("/api/runtime/thin/browse", params={"rel": "pathway/README.md"})
    assert response.status_code == 200
    assert "prose" in response.text


def test_sync_record_ingest_and_latest_routes(monkeypatch):
    class _Store:
        def ingest(self, payload):
            return {
                "envelope_id": "sync-envelope:test",
                "path": "/tmp/envelope.json",
                "received_at": "2026-03-15T00:00:00Z",
                "contract_version": payload["contract_version"],
                "counts": {"contacts": 0, "activities": 0, "binders": 0, "sync_metadata": 0},
            }

        def get_latest(self):
            return {
                "found": True,
                "metadata": {"envelope_id": "sync-envelope:test"},
                "payload": {
                    "contract_version": "v2.0.4",
                    "contacts": [],
                    "activities": [],
                    "binders": [],
                    "sync_metadata": [],
                },
            }

        def list_envelopes(self):
            return {
                "updated_at": "2026-03-15T00:00:00Z",
                "count": 1,
                "items": [{"envelope_id": "sync-envelope:test"}],
            }

    monkeypatch.setattr(runtime_routes, "get_sync_record_store", lambda: _Store())
    app = FastAPI()
    app.include_router(runtime_routes.create_runtime_routes())
    client = TestClient(app)

    ingest = client.post(
        "/api/runtime/sync-records/ingest",
        json={
            "contract_version": "v2.0.4",
            "contacts": [],
            "activities": [],
            "binders": [],
            "sync_metadata": [],
        },
    )
    assert ingest.status_code == 200
    assert ingest.json()["ok"] is True

    latest = client.get("/api/runtime/sync-records/latest")
    assert latest.status_code == 200
    assert latest.json()["found"] is True

    listing = client.get("/api/runtime/sync-records")
    assert listing.status_code == 200
    assert listing.json()["count"] == 1
