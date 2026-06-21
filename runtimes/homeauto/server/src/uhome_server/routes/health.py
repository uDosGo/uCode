"""Health and readiness endpoints for monitoring and observability."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from uhome_server.cluster.registry import get_node_registry, get_storage_registry
from uhome_server.config import get_runtime_settings

router = APIRouter(prefix="/api", tags=["health"])


def _check_nodes_health() -> tuple[str, list[str]]:
    """Check node registry health.
    
    Returns:
        Tuple of (status, issues) where status is "healthy", "degraded", or "critical"
    """
    try:
        registry = get_node_registry()
        nodes = registry.list_nodes()
        
        if not nodes:
            return "degraded", ["No nodes registered"]
        
        primary_nodes = [n for n in nodes if n.get("authority") == "primary"]
        online_primaries = [n for n in primary_nodes if n.get("status") == "online"]
        
        if not primary_nodes:
            return "critical", ["No primary authority node registered"]
        
        if not online_primaries:
            return "critical", ["Primary authority node is offline"]
        
        degraded_nodes = [n for n in nodes if n.get("status") == "degraded"]
        offline_nodes = [n for n in nodes if n.get("status") == "offline"]
        
        issues = []
        if degraded_nodes:
            issues.append(f"{len(degraded_nodes)} node(s) degraded")
        if offline_nodes:
            issues.append(f"{len(offline_nodes)} node(s) offline")
        
        if offline_nodes or degraded_nodes:
            return "degraded", issues
        
        return "healthy", []
    except Exception as e:
        return "critical", [f"Node registry error: {str(e)}"]


def _check_storage_health() -> tuple[str, list[str]]:
    """Check storage registry health.
    
    Returns:
        Tuple of (status, issues) where status is "healthy", "degraded", or "critical"
    """
    try:
        registry = get_storage_registry()
        volumes = registry.list_volumes()
        
        if not volumes:
            return "degraded", ["No storage volumes registered"]
        
        online_volumes = [v for v in volumes if v.get("status") == "online"]
        degraded_volumes = [v for v in volumes if v.get("status") == "degraded"]
        offline_volumes = [v for v in volumes if v.get("status") in {"offline", "missing"}]
        
        issues = []
        if not online_volumes and not degraded_volumes:
            return "critical", ["All storage volumes offline"]
        
        if degraded_volumes:
            issues.append(f"{len(degraded_volumes)} volume(s) degraded")
        if offline_volumes:
            issues.append(f"{len(offline_volumes)} volume(s) offline")
        
        if offline_volumes:
            return "degraded", issues
        if degraded_volumes:
            return "degraded", issues
        
        return "healthy", []
    except Exception as e:
        return "critical", [f"Storage registry error: {str(e)}"]


def _check_configuration_health() -> tuple[str, list[str]]:
    """Check runtime configuration health.
    
    Returns:
        Tuple of (status, issues) where status is "healthy", "degraded", or "critical"
    """
    try:
        settings = get_runtime_settings()
        issues = []
        
        # Check critical paths exist
        if not settings.config_dir.exists():
            issues.append("Config directory missing")
        if not settings.workspace_settings_dir.exists():
            issues.append("Workspace settings directory missing")
        
        # Check optional integrations
        if settings.jellyfin_url and not settings.jellyfin_api_key:
            issues.append("Jellyfin URL configured but API key missing")
        
        if issues:
            if any("missing" in issue.lower() for issue in issues):
                return "critical", issues
            return "degraded", issues
        
        return "healthy", []
    except Exception as e:
        return "critical", [f"Configuration error: {str(e)}"]


@router.get("/health")
def health_check() -> dict[str, Any]:
    """Overall system health check.
    
    Returns health status and detailed component status.
    
    Status levels:
    - healthy: All components operating normally
    - degraded: Some components offline/degraded but service continues
    - critical: Core functionality impaired, immediate attention required
    """
    nodes_status, nodes_issues = _check_nodes_health()
    storage_status, storage_issues = _check_storage_health()
    config_status, config_issues = _check_configuration_health()
    
    # Determine overall status (most severe component status wins)
    status_priority = {"critical": 3, "degraded": 2, "healthy": 1}
    component_statuses = [nodes_status, storage_status, config_status]
    overall_status = max(component_statuses, key=lambda s: status_priority[s])
    
    all_issues = nodes_issues + storage_issues + config_issues
    
    response: dict[str, Any] = {
        "status": overall_status,
        "timestamp": _utc_now_iso(),
        "components": {
            "nodes": {
                "status": nodes_status,
                "issues": nodes_issues,
            },
            "storage": {
                "status": storage_status,
                "issues": storage_issues,
            },
            "configuration": {
                "status": config_status,
                "issues": config_issues,
            },
        },
    }
    
    if all_issues:
        response["issues"] = all_issues
    
    return response


@router.get("/ready")
def readiness_check() -> dict[str, Any]:
    """Readiness check for load balancers and orchestrators.
    
    Returns simple ready/not-ready status. More lenient than health check.
    A server is ready if it can serve requests, even in degraded mode.
    """
    try:
        # Check if we can access registries (basic sanity check)
        node_registry = get_node_registry()
        storage_registry = get_storage_registry()
        nodes = node_registry.list_nodes()
        volumes = storage_registry.list_volumes()
        
        # Ready if we have at least one online or degraded node
        has_active_node = any(
            n.get("status") in {"online", "degraded"} for n in nodes
        )
        
        # Ready if we have at least one online or degraded volume
        has_active_storage = any(
            v.get("status") in {"online", "degraded"} for v in volumes
        )
        
        ready = has_active_node and has_active_storage
        
        return {
            "ready": ready,
            "timestamp": _utc_now_iso(),
        }
    except Exception as e:
        # If we can't even check registries, we're not ready
        return {
            "ready": False,
            "timestamp": _utc_now_iso(),
            "error": str(e),
        }


@router.get("/debug/registries")
def debug_registries() -> dict[str, Any]:
    """Debug endpoint exposing full registry state.
    
    Useful for troubleshooting and runbook procedures.
    """
    try:
        node_registry = get_node_registry()
        storage_registry = get_storage_registry()
        
        nodes = node_registry.list_nodes()
        volumes = storage_registry.list_volumes()
        
        return {
            "timestamp": _utc_now_iso(),
            "nodes": {
                "count": len(nodes),
                "items": nodes,
            },
            "volumes": {
                "count": len(volumes),
                "items": volumes,
            },
        }
    except Exception as e:
        return {
            "timestamp": _utc_now_iso(),
            "error": str(e),
            "nodes": {"count": 0, "items": []},
            "volumes": {"count": 0, "items": []},
        }


def _utc_now_iso() -> str:
    """Get current UTC timestamp in ISO format."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
