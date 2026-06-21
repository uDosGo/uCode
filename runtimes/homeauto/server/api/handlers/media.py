import json
import os
from pathlib import Path
from urllib.parse import parse_qs


def _media_root() -> Path:
    override = os.environ.get("UHOME_MEDIA_ROOT")
    if override:
        return Path(override).expanduser()
    return Path.home() / "media"


def _index_path(root: Path) -> Path:
    override = os.environ.get("UHOME_MEDIA_INDEX_PATH")
    if override:
        return Path(override).expanduser()
    return root / ".media-index.json"


def _load_index() -> dict:
    root = _media_root()
    index_path = _index_path(root)
    if index_path.exists():
        return json.loads(index_path.read_text(encoding="utf-8"))
    return {"root": str(root), "count": 0, "files": [], "stats": {}}


def get_browse(query_string: str) -> dict:
    query = parse_qs(query_string)
    requested = query.get("path", ["/"])[0]
    normalized = requested if requested.startswith("/") else f"/{requested}"
    prefix = normalized.strip("/")
    data = _load_index()
    files = data.get("files", [])
    filtered = files if not prefix else [f for f in files if f["path"].startswith(prefix)]
    items = [{"path": f["path"], "size": f.get("size", 0)} for f in filtered]
    return {"path": normalized, "items": items, "count": len(items)}


def get_search(query_string: str) -> dict:
    query = parse_qs(query_string)
    term = query.get("q", [""])[0].strip()
    data = _load_index()
    files = data.get("files", [])
    if not term:
        return {"query": term, "results": [], "count": 0}
    lowered = term.lower()
    matched = [f for f in files if lowered in f["path"].lower()]
    results = [{"path": f["path"], "size": f.get("size", 0)} for f in matched]
    return {"query": term, "results": results, "count": len(results)}
