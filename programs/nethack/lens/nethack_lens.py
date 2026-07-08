"""NetHack LENS extractor.

Captures a minimal runtime state snapshot aligned with the research notes.
"""


class NethackLensExtractor:
    def __init__(self, emu):
        self._emu = emu

    @property
    def player_hp(self) -> int:
        return self._emu.read_byte(0x0A00)

    @property
    def player_level(self) -> int:
        return self._emu.read_byte(0x0A01)

    @property
    def dungeon_level(self) -> int:
        return self._emu.read_byte(0x0A02)

    @property
    def turn_count(self) -> int:
        return self._emu.read_uint16(0x0A10)

    @property
    def inventory_count(self) -> int:
        return self._emu.read_byte(0x0A20)

    def capture_all(self) -> dict:
        return {
            "player_hp": self.player_hp,
            "player_level": self.player_level,
            "dungeon_level": self.dungeon_level,
            "turn_count": self.turn_count,
            "inventory_count": self.inventory_count,
        }
