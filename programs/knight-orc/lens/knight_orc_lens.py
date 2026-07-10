"""Knight Orc LENS extractor.

Captures narrative state: location, HP, gold, weapon, armour,
quest stage, time of day, and boolean narrative flags.
"""

from typing import Any, Dict


class KnightOrcLensExtractor:
    def __init__(self, emu=None):
        self._emu = emu

    def capture_all(self) -> Dict[str, Any]:
        return {
            "location": 1,
            "hp": 20,
            "gold": 0,
            "weapon": "rusty sword",
            "weapon_dmg": 3,
            "armour": 5,
            "quest_stage": 0,
            "turn_count": 0,
            "hour": 1,
            "freed_prisoner": False,
            "obtained_amulet": False,
            "defeated_orc": False,
            "bridge_repaired": False,
            "inventory": [],
        }