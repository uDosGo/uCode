#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path("server/api").resolve()))
import router

with tempfile.TemporaryDirectory() as tmpdir:
    root = Path(tmpdir)
    index_path = root / ".media-index.json"
    payload = {
        "root": str(root),
        "count": 3,
        "files": [
            {"path": "movies/matrix.mkv", "size": 111, "mtime_ns": 1},
            {"path": "music/artist/track.flac", "size": 222, "mtime_ns": 2},
            {"path": "tv/show/s01e01.mkv", "size": 333, "mtime_ns": 3},
        ],
        "stats": {},
    }
    index_path.write_text(json.dumps(payload), encoding="utf-8")
    os.environ["UHOME_MEDIA_ROOT"] = str(root)
    os.environ["UHOME_MEDIA_INDEX_PATH"] = str(index_path)

    code, payload = router.route_request("GET", "/api/health")
    assert code == 200 and payload == {"status": "ok"}

    code, payload = router.route_request("GET", "/api/media/browse", "path=%2Fmovies")
    assert code == 200 and payload["path"] == "/movies" and payload["count"] == 1
    assert payload["items"][0]["path"] == "movies/matrix.mkv"

    code, payload = router.route_request("GET", "/api/media/search", "q=matrix")
    assert code == 200 and payload["query"] == "matrix" and payload["count"] == 1
    assert payload["results"][0]["path"] == "movies/matrix.mkv"

    code, payload = router.route_request("POST", "/api/playback/start", "target=living-room&media=movies%2Fmatrix.mkv")
    assert code == 200 and payload["status"] == "started"
    assert payload["target"] == "living-room"
    assert payload["media"] == "movies/matrix.mkv"
    assert payload["now_playing"]["state"] == "playing"
    assert payload["now_playing"]["target"] == "living-room"
    assert payload["now_playing"]["media"] == "movies/matrix.mkv"

    code, payload = router.route_request("GET", "/api/now-playing")
    assert code == 200 and payload["state"] == "playing"
    assert payload["target"] == "living-room"
    assert payload["media"] == "movies/matrix.mkv"

    code, payload = router.route_request("POST", "/api/playback/stop", "target=living-room")
    assert code == 200 and payload["status"] == "stopped" and payload["target"] == "living-room"
    assert payload["now_playing"]["state"] == "idle"
    assert payload["now_playing"]["media"] == ""

    code, payload = router.route_request("GET", "/api/now-playing")
    assert code == 200 and payload["state"] == "idle" and payload["target"] == "living-room"

code, payload = router.route_request("GET", "/api/unknown")
assert code == 404 and payload["error"] == "not found"

code, payload = router.route_request("PUT", "/api/health")
assert code == 405 and payload["error"] == "method not allowed"

print("api router contract test passed")
PY
