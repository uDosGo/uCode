"""Eamon LENS extractor.

Captures a minimal runtime snapshot based on the Applesoft-to-BBC research data.
"""


class EamonLensExtractor:
    def __init__(self, emu):
        self._emu = emu

    @property
    def player_hardiness(self) -> int:
        return self._emu.read_uint16(0x0B00)

    @property
    def player_agility(self) -> int:
        return self._emu.read_uint16(0x0B02)

    @property
    def player_charisma(self) -> int:
        return self._emu.read_uint16(0x0B04)

    @property
    def current_room(self) -> int:
        return self._emu.read_byte(0x0B10)

    @property
    def gold(self) -> int:
        return self._emu.read_uint16(0x0B20)

    def capture_all(self) -> dict:
        return {
            "player_hardiness": self.player_hardiness,
            "player_agility": self.player_agility,
            "player_charisma": self.player_charisma,
            "current_room": self.current_room,
            "gold": self.gold,
        }
