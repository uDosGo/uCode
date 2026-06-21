"""File-backed registries for decentralized uHOME nodes and storage volumes."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from uhome_server.config import get_repo_root, read_json_file, utc_now_iso_z, write_json_file

NODE_AUTHORITIES = ("primary", "secondary", "observer")
NODE_STATUSES = ("online", "degraded", "offline", "unknown")
VOLUME_STATUSES = ("online", "degraded", "offline", "missing")
VOLUME_RECOVERY_STATES = ("steady", "missing", "returned")


def _require_allowed(value: str, allowed: tuple[str, ...], field_name: str) -> None:
    if value not in allowed:
        choices = ", ".join(allowed)
        raise ValueError(f"Invalid {field_name}: {value}. Expected one of: {choices}")


@dataclass
class NodeRecord:
    node_id: str
    hostname: str
    role: str = "server"
    status: str = "online"
    authority: str = "secondary"
    capabilities: list[str] = field(default_factory=list)
    address: str | None = None
    last_seen: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_allowed(self.authority, NODE_AUTHORITIES, "authority")
        _require_allowed(self.status, NODE_STATUSES, "status")

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "hostname": self.hostname,
            "role": self.role,
            "status": self.status,
            "authority": self.authority,
            "capabilities": list(self.capabilities),
            "address": self.address,
            "last_seen": self.last_seen,
            "metadata": dict(self.metadata),
        }


@dataclass
class StorageVolumeRecord:
    volume_id: str
    label: str
    kind: str = "disk"
    status: str = "online"
    mount_path: str | None = None
    node_id: str | None = None
    capacity_bytes: int | None = None
    free_bytes: int | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    last_seen: str | None = None
    recovery_state: str = "steady"
    transitioned_at: str | None = None

    def __post_init__(self) -> None:
        _require_allowed(self.status, VOLUME_STATUSES, "status")
        _require_allowed(self.recovery_state, VOLUME_RECOVERY_STATES, "recovery_state")

    def to_dict(self) -> dict[str, Any]:
        return {
            "volume_id": self.volume_id,
            "label": self.label,
            "kind": self.kind,
            "status": self.status,
            "mount_path": self.mount_path,
            "node_id": self.node_id,
            "capacity_bytes": self.capacity_bytes,
            "free_bytes": self.free_bytes,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
            "last_seen": self.last_seen,
            "recovery_state": self.recovery_state,
            "transitioned_at": self.transitioned_at,
        }


class _BaseRegistry:
    key: str

    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or get_repo_root()
        self.state_path = self.repo_root / "memory" / "uhome" / f"{self.key}.json"

    def _load(self) -> list[dict[str, Any]]:
        payload = read_json_file(self.state_path, default={"items": []})
        items = payload.get("items", [])
        return items if isinstance(items, list) else []

    def _save(self, items: list[dict[str, Any]]) -> None:
        write_json_file(self.state_path, {"updated_at": utc_now_iso_z(), "items": items}, indent=2)


def _volume_recovery_state(previous_status: str | None, next_status: str) -> str:
    online_like = {"online", "degraded"}
    offline_like = {"offline", "missing"}
    if previous_status in offline_like and next_status in online_like:
        return "returned"
    if previous_status in online_like and next_status in offline_like:
        return "missing"
    if next_status in offline_like:
        return "missing"
    return "steady"


class NodeRegistry(_BaseRegistry):
    key = "nodes"

    def list_nodes(self) -> list[dict[str, Any]]:
        return self._load()

    def upsert_node(self, record: NodeRecord) -> dict[str, Any]:
        items = self._load()
        payload = record.to_dict()
        payload["last_seen"] = payload["last_seen"] or utc_now_iso_z()
        updated = False
        for index, item in enumerate(items):
            if item.get("node_id") == record.node_id:
                items[index] = payload
                updated = True
                break
        if not updated:
            items.append(payload)
        self._save(items)
        return payload

    def mark_node_status(self, node_id: str, status: str) -> dict[str, Any] | None:
        _require_allowed(status, NODE_STATUSES, "status")
        items = self._load()
        for item in items:
            if item.get("node_id") == node_id:
                item["status"] = status
                item["last_seen"] = utc_now_iso_z()
                self._save(items)
                return item
        return None

    def set_node_authority(self, node_id: str, authority: str) -> dict[str, Any] | None:
        _require_allowed(authority, NODE_AUTHORITIES, "authority")
        items = self._load()
        target: dict[str, Any] | None = None
        for item in items:
            if item.get("node_id") == node_id:
                target = item
                break
        if target is None:
            return None

        if authority == "primary":
            if target.get("status") not in {"online", "degraded"}:
                raise ValueError("Only online or degraded nodes can become primary")
            for item in items:
                if item.get("node_id") != node_id and item.get("authority") == "primary":
                    item["authority"] = "secondary"
                    item["last_seen"] = utc_now_iso_z()
        elif target.get("authority") == "primary":
            has_other_active_primary = any(
                item.get("node_id") != node_id
                and item.get("authority") == "primary"
                and item.get("status") in {"online", "degraded"}
                for item in items
            )
            if not has_other_active_primary:
                raise ValueError("Cannot demote the active primary without promoting a replacement")

        target["authority"] = authority
        target["last_seen"] = utc_now_iso_z()
        self._save(items)
        return target


class StorageRegistry(_BaseRegistry):
    key = "volumes"

    def list_volumes(self) -> list[dict[str, Any]]:
        return self._load()

    def upsert_volume(self, record: StorageVolumeRecord) -> dict[str, Any]:
        items = self._load()
        payload = record.to_dict()
        payload["last_seen"] = payload["last_seen"] or utc_now_iso_z()
        updated = False
        for index, item in enumerate(items):
            if item.get("volume_id") == record.volume_id:
                previous_status = str(item.get("status") or "")
                payload["recovery_state"] = _volume_recovery_state(previous_status, payload["status"])
                payload["transitioned_at"] = (
                    utc_now_iso_z()
                    if previous_status != payload["status"]
                    else item.get("transitioned_at")
                )
                items[index] = payload
                updated = True
                break
        if not updated:
            payload["recovery_state"] = _volume_recovery_state(None, payload["status"])
            payload["transitioned_at"] = payload["last_seen"]
            items.append(payload)
        self._save(items)
        return payload

    def mark_volume_status(self, volume_id: str, status: str) -> dict[str, Any] | None:
        _require_allowed(status, VOLUME_STATUSES, "status")
        items = self._load()
        for item in items:
            if item.get("volume_id") == volume_id:
                previous_status = str(item.get("status") or "")
                item["status"] = status
                item["last_seen"] = utc_now_iso_z()
                item["recovery_state"] = _volume_recovery_state(previous_status, status)
                if previous_status != status:
                    item["transitioned_at"] = item["last_seen"]
                self._save(items)
                return item
        return None


def get_node_registry(repo_root: Path | None = None) -> NodeRegistry:
    return NodeRegistry(repo_root=repo_root)


def get_storage_registry(repo_root: Path | None = None) -> StorageRegistry:
    return StorageRegistry(repo_root=repo_root)


def summarize_topology(nodes: list[dict[str, Any]], volumes: list[dict[str, Any]]) -> dict[str, Any]:
    online_nodes = [item for item in nodes if item.get("status") == "online"]
    degraded_nodes = [item for item in nodes if item.get("status") == "degraded"]
    offline_nodes = [item for item in nodes if item.get("status") == "offline"]
    primary_nodes = [item for item in nodes if item.get("authority") == "primary"]
    online_primary_nodes = [
        item for item in primary_nodes if item.get("status") in {"online", "degraded"}
    ]
    degraded_volumes = [item for item in volumes if item.get("status") == "degraded"]
    offline_volumes = [item for item in volumes if item.get("status") in {"offline", "missing"}]
    returned_volumes = [item for item in volumes if item.get("recovery_state") == "returned"]
    missing_volumes = [item for item in volumes if item.get("recovery_state") == "missing"]
    issues: list[str] = []

    if not nodes:
        issues.append("no_nodes_registered")
    if not online_primary_nodes and nodes:
        issues.append("no_active_primary")
    if len(online_primary_nodes) > 1:
        issues.append("multiple_active_primaries")
    if degraded_nodes:
        issues.append("degraded_nodes_present")
    if offline_nodes:
        issues.append("offline_nodes_present")
    if degraded_volumes:
        issues.append("degraded_volumes_present")
    if offline_volumes:
        issues.append("offline_volumes_present")
    if returned_volumes:
        issues.append("returned_volumes_present")

    node_ids = {item.get("node_id") for item in nodes if item.get("node_id")}
    unavailable_node_ids = {
        item.get("node_id")
        for item in nodes
        if item.get("node_id") and item.get("status") in {"offline", "unknown"}
    }
    detached_volumes = [
        item
        for item in volumes
        if item.get("node_id") and item.get("node_id") not in node_ids
    ]
    volumes_on_unavailable_nodes = [
        item
        for item in volumes
        if item.get("node_id") and item.get("node_id") in unavailable_node_ids
    ]
    if detached_volumes:
        issues.append("detached_volumes_present")
    if volumes_on_unavailable_nodes:
        issues.append("volumes_on_unavailable_nodes")

    if nodes and not online_nodes and not degraded_nodes:
        topology_status = "offline"
    elif issues:
        topology_status = "degraded"
    else:
        topology_status = "healthy"

    return {
        "status": topology_status,
        "issues": issues,
        "summary": {
            "node_count": len(nodes),
            "volume_count": len(volumes),
            "online_node_count": len(online_nodes),
            "degraded_node_count": len(degraded_nodes),
            "offline_node_count": len(offline_nodes),
            "primary_node_count": len(primary_nodes),
            "active_primary_node_count": len(online_primary_nodes),
            "degraded_volume_count": len(degraded_volumes),
            "offline_volume_count": len(offline_volumes),
            "missing_volume_count": len(missing_volumes),
            "returned_volume_count": len(returned_volumes),
            "detached_volume_count": len(detached_volumes),
            "unavailable_host_volume_count": len(volumes_on_unavailable_nodes),
        },
        "active_primary_nodes": [
            {
                "node_id": item.get("node_id"),
                "hostname": item.get("hostname"),
                "status": item.get("status"),
            }
            for item in online_primary_nodes
        ],
        "nodes": nodes,
        "volumes": volumes,
    }


def _volume_library_keys(volume: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    metadata = volume.get("metadata")
    if isinstance(metadata, dict):
        raw = metadata.get("library_keys")
        if isinstance(raw, str) and raw.strip():
            keys.append(raw.strip())
        elif isinstance(raw, list):
            keys.extend(str(item).strip() for item in raw if str(item).strip())
    for tag in volume.get("tags", []):
        if isinstance(tag, str) and tag.startswith("library:"):
            value = tag.split(":", 1)[1].strip()
            if value:
                keys.append(value)
    return sorted(set(keys))


def build_library_index(nodes: list[dict[str, Any]], volumes: list[dict[str, Any]]) -> dict[str, Any]:
    node_map = {
        item.get("node_id"): item
        for item in nodes
        if isinstance(item, dict) and item.get("node_id")
    }
    libraries: dict[str, dict[str, Any]] = {}
    for volume in volumes:
        keys = _volume_library_keys(volume)
        if not keys:
            continue
        node = node_map.get(volume.get("node_id"))
        node_status = node.get("status") if isinstance(node, dict) else None
        node_available = node is None or node_status in {"online", "degraded"}
        volume_available = volume.get("status") in {"online", "degraded"} and node_available
        for key in keys:
            entry = libraries.setdefault(
                key,
                {
                    "library_key": key,
                    "status": "healthy",
                    "issues": [],
                    "volume_count": 0,
                    "available_volume_count": 0,
                    "offline_volume_count": 0,
                    "returned_volume_count": 0,
                    "paths": [],
                    "volumes": [],
                },
            )
            entry["volume_count"] += 1
            if volume_available:
                entry["available_volume_count"] += 1
            else:
                entry["offline_volume_count"] += 1
            if volume.get("recovery_state") == "returned":
                entry["returned_volume_count"] += 1
            if volume.get("mount_path"):
                entry["paths"].append(volume["mount_path"])
            entry["volumes"].append(
                {
                    "volume_id": volume.get("volume_id"),
                    "label": volume.get("label"),
                    "status": volume.get("status"),
                    "recovery_state": volume.get("recovery_state", "steady"),
                    "node_id": volume.get("node_id"),
                    "node_status": node_status,
                    "mount_path": volume.get("mount_path"),
                }
            )

    entries = sorted(libraries.values(), key=lambda item: item["library_key"])
    for entry in entries:
        entry["paths"] = sorted(set(entry["paths"]))
        if entry["available_volume_count"] == 0:
            entry["status"] = "offline"
            entry["issues"].append("no_available_volumes")
        elif entry["offline_volume_count"] > 0 or entry["returned_volume_count"] > 0:
            entry["status"] = "degraded"
            if entry["offline_volume_count"] > 0:
                entry["issues"].append("partial_volume_availability")
            if entry["returned_volume_count"] > 0:
                entry["issues"].append("returned_volumes_present")

    return {
        "count": len(entries),
        "libraries": entries,
        "summary": {
            "healthy": sum(1 for item in entries if item["status"] == "healthy"),
            "degraded": sum(1 for item in entries if item["status"] == "degraded"),
            "offline": sum(1 for item in entries if item["status"] == "offline"),
        },
    }
