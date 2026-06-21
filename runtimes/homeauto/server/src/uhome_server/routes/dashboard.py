"""Dashboard summary and health routes for the standalone uHOME server."""

from __future__ import annotations

from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends

from uhome_server.cluster.registry import (
    build_library_index,
    get_node_registry,
    get_storage_registry,
    summarize_topology,
)
from uhome_server.config import utc_now_iso_z
from uhome_server.library.catalog import get_container_catalog_service
from uhome_server.services.home_assistant_service import get_ha_service
from uhome_server.services.uhome_presentation_service import get_uhome_presentation_service
from uhome_server.workspace import get_template_workspace_service


def _probe(fn: Callable[[], dict[str, Any]], label: str) -> dict[str, Any]:
    try:
        result = fn()
        if isinstance(result, dict):
            return {"ok": True, **result}
        return {"ok": True, "result": result}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "subsystem": label}


def _ha_status() -> dict[str, Any]:
    return get_ha_service().status()


def _workspace_runtime_status() -> dict[str, Any]:
    workspace = get_template_workspace_service()
    uhome = get_uhome_presentation_service(repo_root=workspace.repo_root)
    uhome_status = uhome.get_status()
    return {
        "workspace_ref": "@memory/workspace/settings",
        "components": {
            "uhome": {
                "template_workspace": workspace.component_contract("uhome"),
                "template_workspace_state": workspace.component_snapshot("uhome"),
                "defaults": {
                    "presentation": {
                        "value": uhome_status.get("preferred_presentation"),
                        "source": uhome_status.get("preferred_presentation_source", "default"),
                    },
                    "node_role": {
                        "value": uhome_status.get("node_role"),
                        "source": uhome_status.get("node_role_source", "default"),
                    },
                },
            }
        },
    }


def _network_status() -> dict[str, Any]:
    nodes = get_node_registry().list_nodes()
    volumes = get_storage_registry().list_volumes()
    online_nodes = [node for node in nodes if node.get("status") == "online"]
    online_volumes = [volume for volume in volumes if volume.get("status") == "online"]
    topology = summarize_topology(nodes, volumes)
    library_index = build_library_index(nodes, volumes)
    return {
        "status": topology["status"],
        "issues": topology["issues"],
        "nodes": {"count": len(nodes), "online": len(online_nodes)},
        "volumes": {"count": len(volumes), "online": len(online_volumes)},
        "library_index": library_index["summary"],
    }


def _library_status() -> dict[str, Any]:
    entries = get_container_catalog_service().list_by_kind("library")
    return {
        "count": len(entries),
        "entries": [entry.to_dict() for entry in entries],
    }


def health_probe() -> dict[str, Any]:
    ha = _probe(_ha_status, "ha_bridge")
    network = _probe(_network_status, "network")
    return {
        "status": "healthy",
        "ok": True,
        "bridge": "uhome-dashboard",
        "timestamp": utc_now_iso_z(),
        "ha_bridge_ready": ha.get("ok", False),
        "network_ready": network.get("ok", False),
    }


def create_dashboard_routes(auth_guard: Optional[Callable] = None) -> APIRouter:
    dependencies = [Depends(auth_guard)] if auth_guard else []
    router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

    @router.get("/health")
    async def dashboard_health():
        return health_probe()

    @router.get("/summary", dependencies=dependencies)
    async def dashboard_summary():
        ha = _probe(_ha_status, "ha_bridge")
        workspace_runtime = _probe(_workspace_runtime_status, "workspace_runtime")
        network = _probe(_network_status, "network")
        library = _probe(_library_status, "library")
        subsystems = {
            "ha_bridge": ha,
            "workspace_runtime": workspace_runtime,
            "network": network,
            "library": library,
        }
        return {
            "ok": all(item.get("ok", False) for item in subsystems.values()),
            "bridge": "uhome-dashboard",
            "timestamp": utc_now_iso_z(),
            "subsystems": subsystems,
            "workspace_runtime": workspace_runtime,
            "summary": {
                "total": len(subsystems),
                "healthy": sum(1 for item in subsystems.values() if item.get("ok")),
                "degraded": sum(1 for item in subsystems.values() if not item.get("ok")),
            },
        }

    return router
