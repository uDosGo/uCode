"""Network and storage routes for decentralized uHOME server topologies."""

from __future__ import annotations

from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from uhome_server.cluster.registry import (
    NodeRecord,
    StorageVolumeRecord,
    build_library_index,
    get_node_registry,
    get_storage_registry,
    summarize_topology,
)
from uhome_server.config import get_repo_root, utc_now_iso_z
from uhome_server.services.channel_service import get_channel_service
from uhome_server.services.client_capability_service import get_client_capability_service
from uhome_server.services.uhome_command_handlers import playback_status
from uhome_server.services.uhome_presentation_service import get_uhome_presentation_service

router = APIRouter(prefix="/api/network", tags=["network"])


class NodeUpsertRequest(BaseModel):
    node_id: str
    hostname: str
    role: str = "server"
    status: Literal["online", "degraded", "offline", "unknown"] = "online"
    authority: Literal["primary", "secondary", "observer"] = "secondary"
    capabilities: list[str] = Field(default_factory=list)
    address: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class NodeStatusUpdateRequest(BaseModel):
    status: Literal["online", "degraded", "offline", "unknown"]


class AuthorityUpdateRequest(BaseModel):
    authority: Literal["primary", "secondary", "observer"]


class VolumeStatusUpdateRequest(BaseModel):
    status: Literal["online", "degraded", "offline", "missing"]


class VolumeUpsertRequest(BaseModel):
    volume_id: str
    label: str
    kind: str = "disk"
    status: Literal["online", "degraded", "offline", "missing"] = "online"
    mount_path: Optional[str] = None
    node_id: Optional[str] = None
    capacity_bytes: Optional[int] = None
    free_bytes: Optional[int] = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.get("/nodes")
async def list_nodes():
    nodes = get_node_registry().list_nodes()
    return {"count": len(nodes), "nodes": nodes}


@router.post("/nodes")
async def upsert_node(payload: NodeUpsertRequest):
    record = NodeRecord(**payload.model_dump())
    node = get_node_registry().upsert_node(record)
    return {"success": True, "node": node}


@router.post("/nodes/{node_id}/status")
async def update_node_status(node_id: str, payload: NodeStatusUpdateRequest):
    node = get_node_registry().mark_node_status(node_id, payload.status)
    if node is None:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
    return {"success": True, "node": node}


@router.post("/nodes/{node_id}/authority")
async def update_node_authority(node_id: str, payload: AuthorityUpdateRequest):
    try:
        node = get_node_registry().set_node_authority(node_id, payload.authority)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if node is None:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
    return {"success": True, "node": node}


@router.get("/volumes")
async def list_volumes():
    volumes = get_storage_registry().list_volumes()
    return {"count": len(volumes), "volumes": volumes}


@router.get("/topology")
async def topology_summary():
    nodes = get_node_registry().list_nodes()
    volumes = get_storage_registry().list_volumes()
    return summarize_topology(nodes, volumes)


@router.get("/library-index")
async def library_index():
    nodes = get_node_registry().list_nodes()
    volumes = get_storage_registry().list_volumes()
    return build_library_index(nodes, volumes)


@router.get("/capabilities")
async def network_capabilities():
    nodes = get_node_registry().list_nodes()
    volumes = get_storage_registry().list_volumes()
    topology = summarize_topology(nodes, volumes)
    libraries = build_library_index(nodes, volumes)
    channels = get_channel_service().list_channels()
    playback = playback_status({})
    launcher = get_uhome_presentation_service(repo_root=get_repo_root()).get_status()
    clients = get_client_capability_service(get_repo_root()).profile_summary()

    return {
        "status": topology.get("status", "degraded"),
        "timestamp": utc_now_iso_z(),
        "topology": {
            "status": topology.get("status"),
            "issues": topology.get("issues", []),
            "summary": topology.get("summary", {}),
        },
        "libraries": {
            "count": libraries.get("count", 0),
            "summary": libraries.get("summary", {}),
        },
        "streaming": {
            "channel_count": len(channels),
            "channels": [
                {
                    "channel_id": item.get("channel_id"),
                    "display_name": item.get("display_name"),
                    "media_mode": item.get("media_mode"),
                }
                for item in channels
            ],
            "jellyfin_configured": bool(playback.get("jellyfin_configured", False)),
            "jellyfin_reachable": bool(playback.get("jellyfin_reachable", False)),
            "active_playback_sessions": len(playback.get("active_sessions", [])),
        },
        "launcher": {
            "running": bool(launcher.get("running", False)),
            "active_presentation": launcher.get("active_presentation"),
            "preferred_presentation": launcher.get("preferred_presentation"),
        },
        "clients": clients,
    }


@router.post("/volumes")
async def upsert_volume(payload: VolumeUpsertRequest):
    record = StorageVolumeRecord(**payload.model_dump())
    volume = get_storage_registry().upsert_volume(record)
    return {"success": True, "volume": volume}


@router.post("/volumes/{volume_id}/status")
async def update_volume_status(volume_id: str, payload: VolumeStatusUpdateRequest):
    volume = get_storage_registry().mark_volume_status(volume_id, payload.status)
    if volume is None:
        raise HTTPException(status_code=404, detail=f"Volume not found: {volume_id}")
    return {"success": True, "volume": volume}
