#!/usr/bin/env python3
import time
from pathlib import Path

from indexer import write_index


def watch(root: Path, interval: int = 5, index_name: str = ".media-index.json") -> None:
    index_path = root / index_name
    print(f"Watching {root} every {interval}s")
    while True:
        result = write_index(root, index_path)
        print(
            f"indexed files={result['count']}"
            f" +{result['stats']['added']}"
            f" ~{result['stats']['changed']}"
            f" -{result['stats']['removed']}"
        )
        time.sleep(interval)


if __name__ == "__main__":
    watch(Path.home() / "media")
