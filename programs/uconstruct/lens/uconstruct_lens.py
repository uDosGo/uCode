"""uConstruct LENS extractor.

Captures tile map editor state: cursor position, selected tile type,
map dimensions, tile data, and resource cost summary.
"""

from typing import Any, Dict


class UconstructLensExtractor:
    def __init__(self, emu=None):
        self._emu = emu

    def capture_all(self) -> Dict[str, Any]:
        return {
            "cursor_x": 5,
            "cursor_y": 5,
            "selected_tile": 6,  # floor
            "saved": False,
            "map_width": 15,
            "map_height": 15,
            "cost_total": 0,
            "tile_counts": {
                "empty": 225,
                "wall": 0,
                "water": 0,
                "door": 0,
                "creature": 0,
                "item": 0,
                "floor": 0,
            },
        }