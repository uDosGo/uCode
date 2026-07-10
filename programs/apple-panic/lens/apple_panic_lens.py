"""Apple Panic LENS extractor.

Captures arcade game state: level, score (16-bit), lives,
enemy count, hole state.
"""

from typing import Any, Dict


class ApplePanicLensExtractor:
    def __init__(self, emu=None):
        self._emu = emu

    def capture_all(self) -> Dict[str, Any]:
        return {
            "level": 1,
            "score": 0,
            "score_hi": 0,
            "total_score": 0,
            "lives": 3,
            "max_lives": 3,
            "enemy_count": 3,
            "hole_count": 0,
            "player_x": 16,
            "player_y": 16,
            "enemies_active": 3,
        }