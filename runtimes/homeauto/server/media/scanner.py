#!/usr/bin/env python3
import os
from pathlib import Path


def _to_record(root: Path, file_path: Path) -> dict:
    stat = file_path.stat()
    return {
        "path": file_path.relative_to(root).as_posix(),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def scan(root: Path) -> list[dict]:
    if not root.exists():
        return []
    # Skip hidden index files and hidden directories.
    files = []
    for current_root, dirs, filenames in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in filenames:
            if name.startswith("."):
                continue
            file_path = Path(current_root) / name
            if file_path.is_file():
                files.append(_to_record(root, file_path))
    files.sort(key=lambda item: item["path"])
    return files


if __name__ == "__main__":
    media_root = Path.home() / "media"
    print(f"Found {len(scan(media_root))} files in {media_root}")
