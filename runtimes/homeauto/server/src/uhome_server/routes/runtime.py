"""Runtime readiness and environment routes for the standalone uHOME server."""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Any, Callable, Optional

from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from uhome_server.config import (
    get_repo_root,
    get_runtime_settings,
    get_sync_record_contract_path,
    get_sync_record_schema_path,
    get_uhome_network_policy_contract_path,
    get_uhome_network_policy_schema_path,
    load_sync_record_contract,
    load_sync_record_schema,
    load_uhome_network_policy_contract,
    load_uhome_network_policy_schema,
    utc_now_iso_z,
)
from uhome_server.automation_store import get_automation_store
from uhome_server.sync_records import (
    validate_sync_record_envelope,
    validation_error_payload,
)
from uhome_server.sync_store import get_sync_record_store
from uhome_server.uhome_network_policy import (
    uhome_network_policy_validation_error,
    validate_uhome_network_policy_payload,
)
from pydantic import ValidationError
from uhome_server.services.home_assistant_service import get_ha_service
from uhome_server.services.uhome_command_handlers import playback_status
from uhome_server.workspace import get_template_workspace_service
from uhome_server.thin_pages import (
    thin_automation_status_html,
    thin_read_mode_from_path,
    thin_read_mode_html,
)


def _probe(fn: Callable[[], dict[str, Any]], label: str, required: bool = True) -> dict[str, Any]:
    try:
        result = fn()
        payload = result if isinstance(result, dict) else {"result": result}
        return {"ok": True, "required": required, "subsystem": label, **payload}
    except Exception as exc:
        return {"ok": False, "required": required, "subsystem": label, "error": str(exc)}


def _repo_layout_status() -> dict[str, Any]:
    repo_root = get_repo_root()
    expected_paths = {
        "defaults": repo_root / "defaults",
        "library": repo_root / "library",
        "docs": repo_root / "docs",
        "src": repo_root / "src",
    }
    missing = [name for name, path in expected_paths.items() if not path.exists()]
    return {
        "repo_root": str(repo_root),
        "exists": repo_root.exists(),
        "missing_paths": missing,
        "paths": {name: str(path) for name, path in expected_paths.items()},
    }


def _workspace_status() -> dict[str, Any]:
    workspace = get_template_workspace_service(get_repo_root())
    snapshot = workspace.component_snapshot("uhome")
    settings = snapshot.get("settings", {})
    return {
        "workspace_ref": "@memory/workspace/settings",
        "component_id": "uhome",
        "instructions_ref": snapshot.get("instructions_ref"),
        "settings_keys": sorted(settings.keys()),
    }


def _ha_bridge_status() -> dict[str, Any]:
    return get_ha_service().status()


def _jellyfin_status() -> dict[str, Any]:
    status = playback_status({})
    return {
        "jellyfin_configured": status.get("jellyfin_configured", False),
        "jellyfin_url_configured": status.get("jellyfin_url_configured", False),
        "jellyfin_api_key_configured": status.get("jellyfin_api_key_configured", False),
        "jellyfin_reachable": status.get("jellyfin_reachable", False),
        "presentation_mode": status.get("presentation_mode"),
        "preferred_target_client": status.get("preferred_target_client"),
        "issue": status.get("issue"),
        "note": status.get("note"),
    }


def _config_status() -> dict[str, Any]:
    settings = get_runtime_settings(get_repo_root())
    legacy_uhome = settings.config_path.with_name("legacy-uhome.json")
    if settings.config_path.exists():
        active_config_path = settings.config_path
    elif legacy_uhome.exists():
        active_config_path = legacy_uhome
    else:
        active_config_path = settings.legacy_config_path
    return {
        "config_path": str(settings.config_path),
        "legacy_config_path": str(settings.legacy_config_path),
        "active_config_path": str(active_config_path),
        "active_config_exists": active_config_path.exists(),
        "legacy_config_fallback": active_config_path == settings.legacy_config_path,
        "ha_bridge_enabled_env": settings.ha_bridge_enabled,
        "hdhomerun_host": settings.hdhomerun_host,
    }


def runtime_readiness_probe() -> dict[str, Any]:
    checks = {
        "repo_layout": _probe(_repo_layout_status, "repo_layout"),
        "config": _probe(_config_status, "config"),
        "workspace": _probe(_workspace_status, "workspace"),
        "ha_bridge": _probe(_ha_bridge_status, "ha_bridge", required=False),
        "jellyfin": _probe(_jellyfin_status, "jellyfin", required=False),
    }
    required_checks = [item for item in checks.values() if item.get("required")]
    optional_checks = [item for item in checks.values() if not item.get("required")]
    required_ok = all(item.get("ok", False) for item in required_checks)
    optional_ok = sum(1 for item in optional_checks if item.get("ok", False))
    return {
        "ok": required_ok,
        "status": "ready" if required_ok else "degraded",
        "timestamp": utc_now_iso_z(),
        "checks": checks,
        "summary": {
            "required_total": len(required_checks),
            "required_healthy": sum(1 for item in required_checks if item.get("ok", False)),
            "optional_total": len(optional_checks),
            "optional_healthy": optional_ok,
        },
    }


def runtime_info() -> dict[str, Any]:
    repo_root = get_repo_root()
    settings = get_runtime_settings(repo_root)
    return {
        "app": "uHOME Server",
        "timestamp": utc_now_iso_z(),
        "python_version": sys.version.split()[0],
        "platform": platform.system().lower(),
        "platform_release": platform.release(),
        "repo_root": str(repo_root),
        "cwd": str(Path.cwd()),
        "settings": settings.to_dict(),
    }


def sync_record_contract_info() -> dict[str, Any]:
    contract_path = get_sync_record_contract_path()
    schema_path = get_sync_record_schema_path()
    contract = load_sync_record_contract()
    schema = load_sync_record_schema()
    return {
        "contract_path": str(contract_path),
        "schema_path": str(schema_path),
        "version": contract.get("version"),
        "owner": contract.get("owner"),
        "schema_title": schema.get("title"),
        "record_types": [record["key"] for record in contract.get("record_types", [])],
        "envelope_collections": contract.get("envelope", {}).get("required_collections", []),
    }


def workflow_automation_contract_info() -> dict[str, Any]:
    base = "uhome_server/contracts"
    return {
        "workflow_state_contract": f"{base}/workflow-state-contract.json",
        "workflow_action_contract": f"{base}/workflow-action-contract.json",
        "automation_job_contract": f"{base}/automation-job-contract.json",
        "automation_result_contract": f"{base}/automation-result-contract.json",
        "workflow_owner": "uHOME-server",
        "automation_fulfillment_owner": "uHOME-server",
        "integration_note": "Standalone uHOME fulfils automation on-box; optional external workflow tools are not required.",
    }


def uhome_network_policy_contract_info() -> dict[str, Any]:
    contract_path = get_uhome_network_policy_contract_path()
    schema_path = get_uhome_network_policy_schema_path()
    contract = load_uhome_network_policy_contract()
    schema = load_uhome_network_policy_schema()
    profiles = contract.get("profiles", {})
    return {
        "contract_path": str(contract_path),
        "schema_path": str(schema_path),
        "version": contract.get("version"),
        "owner": contract.get("owner"),
        "package": contract.get("package"),
        "schema_title": schema.get("title"),
        "profiles": sorted(profiles.keys()),
        "runtime_owners": sorted({str(item.get("runtime_owner")) for item in profiles.values()}),
        "policy_owners": sorted({str(item.get("policy_owner")) for item in profiles.values()}),
        "routes": contract.get("routes", {}),
        "networking_model": contract.get("networking_model"),
        "deployment": contract.get("deployment"),
        "future_integration": contract.get("future_integration"),
    }


def uhome_network_policy_validation_result(payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    try:
        validated = validate_uhome_network_policy_payload(payload)
    except ValidationError as exc:
        return uhome_network_policy_validation_error(exc), 400
    except ValueError as exc:
        return uhome_network_policy_validation_error(exc), 400
    return (
        {
            "ok": True,
            "contract_version": validated["contract_version"],
            "profile_id": validated["profile_id"],
            "runtime_owner": validated["runtime_owner"],
            "policy_owner": validated["policy_owner"],
            "consumer_repos": validated["consumer_repos"],
        },
        200,
    )


def sync_record_validation_result(payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    try:
        envelope = validate_sync_record_envelope(payload)
    except ValidationError as exc:
        return validation_error_payload(exc), 400
    return (
        {
            "ok": True,
            "contract_version": envelope.contract_version,
            "counts": {
                "contacts": len(envelope.contacts),
                "activities": len(envelope.activities),
                "binders": len(envelope.binders),
                "sync_metadata": len(envelope.sync_metadata),
            },
        },
        200,
    )


def create_runtime_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/runtime", tags=["runtime"])

    @router.get("/ready")
    async def readiness():
        return runtime_readiness_probe()

    @router.get("/info", dependencies=dependencies)
    async def info(request: Request):
        payload = runtime_info()
        bootstrap = getattr(request.app.state, "bootstrap", None)
        if isinstance(bootstrap, dict):
            payload["bootstrap"] = bootstrap
        return payload

    @router.get("/contracts/sync-record", dependencies=dependencies)
    async def sync_record_contract():
        return sync_record_contract_info()

    @router.get("/contracts/workflow-automation", dependencies=dependencies)
    async def workflow_automation_contract():
        return workflow_automation_contract_info()

    @router.get("/contracts/uhome-network-policy", dependencies=dependencies)
    async def uhome_network_policy_contract():
        return uhome_network_policy_contract_info()

    @router.get("/contracts/uhome-network-policy/schema", dependencies=dependencies)
    async def uhome_network_policy_schema():
        return load_uhome_network_policy_schema()

    @router.post("/contracts/uhome-network-policy/validate", dependencies=dependencies)
    async def validate_uhome_network_policy(payload: dict[str, Any] = Body(...)):
        body, status_code = uhome_network_policy_validation_result(payload)
        return JSONResponse(content=body, status_code=status_code)

    @router.get("/automation/status", dependencies=dependencies)
    async def automation_status():
        return get_automation_store().status()

    @router.get("/automation/jobs", dependencies=dependencies)
    async def automation_jobs():
        return get_automation_store().list_jobs()

    @router.post("/automation/jobs", dependencies=dependencies)
    async def queue_automation_job(payload: dict[str, Any] = Body(...)):
        return get_automation_store().queue_job(payload)

    @router.post("/automation/jobs/{job_id}/cancel", dependencies=dependencies)
    async def cancel_automation_job(job_id: str):
        return get_automation_store().cancel_job(job_id)

    @router.get("/automation/results", dependencies=dependencies)
    async def automation_results():
        return get_automation_store().list_results()

    @router.post("/automation/results", dependencies=dependencies)
    async def record_automation_result(payload: dict[str, Any] = Body(...)):
        return get_automation_store().record_result(payload)

    @router.post("/automation/results/{job_id}/retry", dependencies=dependencies)
    async def retry_automation_job(job_id: str):
        return get_automation_store().retry_job(job_id)

    @router.post("/automation/process-next", dependencies=dependencies)
    async def process_next_automation_job(payload: dict[str, Any] = Body(default={})):
        return get_automation_store().process_next_job(payload)

    @router.get("/thin/automation", response_class=HTMLResponse)
    async def thin_automation():
        return HTMLResponse(thin_automation_status_html())

    @router.get("/thin/read", response_class=HTMLResponse)
    async def thin_read():
        return HTMLResponse(thin_read_mode_html())

    @router.get("/thin/browse", response_class=HTMLResponse)
    async def thin_browse(rel: str = Query(..., min_length=1, description="Path under repo docs/, e.g. pathway/README.md")):
        docs_root = get_repo_root() / "docs"
        raw = rel.replace("\\", "/").lstrip("/")
        if ".." in raw.split("/"):
            return HTMLResponse("Invalid path", status_code=400)
        target = (docs_root / raw).resolve()
        try:
            target.relative_to(docs_root.resolve())
        except ValueError:
            return HTMLResponse("Forbidden", status_code=403)
        page, status_code = thin_read_mode_from_path(target)
        return HTMLResponse(page, status_code=status_code)

    @router.post("/sync-records/validate", dependencies=dependencies)
    async def validate_sync_records(payload: dict[str, Any] = Body(...)):
        body, status_code = sync_record_validation_result(payload)
        return JSONResponse(content=body, status_code=status_code)

    @router.post("/sync-records/ingest", dependencies=dependencies)
    async def ingest_sync_records(payload: dict[str, Any] = Body(...)):
        try:
            metadata = get_sync_record_store().ingest(payload)
        except ValidationError as exc:
            return JSONResponse(content=validation_error_payload(exc), status_code=400)
        return {
            "ok": True,
            "ingested": metadata,
        }

    @router.get("/sync-records/latest", dependencies=dependencies)
    async def latest_sync_records():
        return get_sync_record_store().get_latest()

    @router.get("/sync-records", dependencies=dependencies)
    async def list_sync_records():
        return get_sync_record_store().list_envelopes()

    return router
