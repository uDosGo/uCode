from __future__ import annotations

from uhome_server.sync_store import SyncRecordStore


def _payload() -> dict:
    return {
        "contract_version": "v2.0.4",
        "contacts": [],
        "activities": [],
        "binders": [],
        "sync_metadata": [],
    }


def test_sync_store_ingest_and_list(tmp_path) -> None:
    store = SyncRecordStore(repo_root=tmp_path)
    item = store.ingest(_payload())
    assert item["contract_version"] == "v2.0.4"

    listing = store.list_envelopes()
    assert listing["count"] == 1
    assert listing["items"][0]["envelope_id"] == item["envelope_id"]


def test_sync_store_returns_latest_payload(tmp_path) -> None:
    store = SyncRecordStore(repo_root=tmp_path)
    store.ingest(_payload())
    latest = store.get_latest()
    assert latest["found"] is True
    assert latest["payload"]["contract_version"] == "v2.0.4"
