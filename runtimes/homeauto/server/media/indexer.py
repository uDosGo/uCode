#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from scanner import scan


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_index(index_path: Path) -> dict[str, Any]:
    if not index_path.exists():
        return {}
    return json.loads(index_path.read_text(encoding="utf-8"))


def build_index(media_root: Path, previous_index: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    previous_index = previous_index or {}
    previous_files = {f["path"]: f for f in previous_index.get("files", [])}
    scanned_files = scan(media_root)
    scanned_map = {f["path"]: f for f in scanned_files}

    added = [path for path in scanned_map if path not in previous_files]
    removed = [path for path in previous_files if path not in scanned_map]
    changed = []
    unchanged = []
    for path, record in scanned_map.items():
        old = previous_files.get(path)
        if old is None:
            continue
        if old.get("size") != record["size"] or old.get("mtime_ns") != record["mtime_ns"]:
            changed.append(path)
        else:
            unchanged.append(path)

    return {
        "root": str(media_root),
        "generated_at": _iso_now(),
        "count": len(scanned_files),
        "files": scanned_files,
        "stats": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "unchanged": len(unchanged),
        },
    }


def write_index(media_root: Path, index_path: Path) -> dict[str, Any]:
    previous = _load_index(index_path)
    index = build_index(media_root, previous)
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return index


if __name__ == "__main__":
    root = Path.home() / "media"
    output = root / ".media-index.json"
    result = write_index(root, output)
    print(f"Wrote {output}")
    print(
        "Stats:"
        f" +{result['stats']['added']}"
        f" ~{result['stats']['changed']}"
        f" -{result['stats']['removed']}"
    )
