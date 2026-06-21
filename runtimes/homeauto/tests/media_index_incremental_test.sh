#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path("server/media").resolve()))
from indexer import write_index

with tempfile.TemporaryDirectory() as tmpdir:
    root = Path(tmpdir)
    (root / "movies").mkdir()
    (root / "movies" / "a.txt").write_text("one", encoding="utf-8")
    index_path = root / ".media-index.json"

    first = write_index(root, index_path)
    assert first["count"] == 1
    assert first["stats"]["added"] == 1
    assert first["stats"]["changed"] == 0
    assert first["stats"]["removed"] == 0

    time.sleep(0.01)
    (root / "movies" / "a.txt").write_text("one-updated", encoding="utf-8")
    (root / "music").mkdir()
    (root / "music" / "b.txt").write_text("two", encoding="utf-8")
    second = write_index(root, index_path)
    assert second["count"] == 2
    assert second["stats"]["added"] == 1
    assert second["stats"]["changed"] == 1
    assert second["stats"]["removed"] == 0

    (root / "movies" / "a.txt").unlink()
    third = write_index(root, index_path)
    assert third["count"] == 1
    assert third["stats"]["added"] == 0
    assert third["stats"]["changed"] == 0
    assert third["stats"]["removed"] == 1

print("media index incremental test passed")
PY
