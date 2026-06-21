"""File-backed storage for validated sync-record envelopes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from uhome_server.config import get_repo_root, read_json_file, utc_now_iso_z, write_json_file
from uhome_server.sync_records import SyncRecordEnvelope, validate_sync_record_envelope


class SyncRecordStore:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or get_repo_root()
        self.base_dir = self.repo_root / "memory" / "bank" / "uhome" / "sync-records"
        self.index_path = self.base_dir / "index.json"

    def _read_index(self) -> Dict[str, Any]:
        return read_json_file(self.index_path, default={"updated_at": None, "items": []})

    def _write_index(self, items: list[dict[str, Any]]) -> None:
        write_json_file(
            self.index_path,
            {
                "updated_at": utc_now_iso_z(),
                "items": items,
            },
            indent=2,
        )

    def ingest(self, payload: dict[str, Any]) -> dict[str, Any]:
        envelope = validate_sync_record_envelope(payload)
        received_at = utc_now_iso_z()
        envelope_id = f"sync-envelope:{received_at.replace(':', '').replace('-', '')}"
        path = self.base_dir / f"{envelope_id}.json"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        write_json_file(path, envelope.model_dump(mode="json"), indent=2)

        index = self._read_index()
        items = [
            {
                "envelope_id": envelope_id,
                "path": str(path),
                "received_at": received_at,
                "contract_version": envelope.contract_version,
                "counts": {
                    "contacts": len(envelope.contacts),
                    "activities": len(envelope.activities),
                    "binders": len(envelope.binders),
                    "sync_metadata": len(envelope.sync_metadata),
                },
            }
        ]
        items.extend(index.get("items", []))
        self._write_index(items)
        return items[0]

    def list_envelopes(self) -> dict[str, Any]:
        index = self._read_index()
        return {
            "updated_at": index.get("updated_at"),
            "count": len(index.get("items", [])),
            "items": index.get("items", []),
        }

    def get_latest(self) -> dict[str, Any]:
        index = self._read_index()
        items = index.get("items", [])
        if not items:
            return {"found": False}
        latest = items[0]
        payload = read_json_file(Path(latest["path"]), default={})
        return {
            "found": True,
            "metadata": latest,
            "payload": payload,
        }


_store: Optional[SyncRecordStore] = None


def get_sync_record_store(repo_root: Optional[Path] = None) -> SyncRecordStore:
    global _store
    if _store is None:
        _store = SyncRecordStore(repo_root=repo_root)
    return _store
