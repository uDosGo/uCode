#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path("server/media").resolve()))
from indexer import write_index
from scanner import scan

with tempfile.TemporaryDirectory() as tmpdir:
    root = Path(tmpdir)
    (root / "movies").mkdir()
    (root / "movies" / "sample.mkv").write_text("x", encoding="utf-8")
    files = scan(root)
    assert len(files) == 1
    index = write_index(root, root / ".media-index.json")
    assert index["count"] == 1
PY

echo "media scan test passed"
