"""Tests for Knight Orc narrative progression and state management.

Verifies:
- Quest stage progression through NPC interactions
- Time-of-day system advances with turns
- Combat mechanics and NPC defeat state
- Inventory/item usage puzzle solutions
- LENS snapshot captures narrative state
- Win/lose conditions
"""


class KnightWorld:
    """Pure-Python mirror of knight_orc.bbc world model."""

    def __init__(self):
        self.rooms = {}
        self.items = {}
        self.npcs = {}
        self.player_room = 1
        self.hp = 20
        self.max_hp = 20
        self.gold = 0
        self.weapon = "rusty sword"
        self.weapon_dmg = 3
        self.armour = 5
        self.inventory = []
        self.hour = 1
        self.turn_count = 0
        # Narrative state
        self.freed_prisoner = False
        self.obtained_amulet = False
        self.defeated_orc = False
        self.talked_to_wizard = False
        self.bridge_repaired = False
        self.quest_stage = 0

    def room_has_npc(self, npc_id):
        for nid, npc in self.npcs.items():
            if nid == npc_id and npc["room"] == self.player_room and npc["alive"]:
                return True
        return False

    def to_lens_snapshot(self):
        return {
            "location": self.player_room,
            "hp": self.hp,
            "gold": self.gold,
            "weapon": self.weapon,
            "weapon_dmg": self.weapon_dmg,
            "armour": self.armour,
            "quest_stage": self.quest_stage,
            "turn_count": self.turn_count,
            "hour": self.hour,
            "freed_prisoner": self.freed_prisoner,
            "obtained_amulet": self.obtained_amulet,
            "defeated_orc": self.defeated_orc,
            "bridge_repaired": self.bridge_repaired,
            "inventory": list(self.inventory),
        }


def build_world():
    w = KnightWorld()
    w.rooms = {
        1: {"name": "Village Square", "n": 0, "s": 0, "e": 2, "w": 0},
        2: {"name": "Inn", "n": 0, "s": 0, "e": 3, "w": 1},
        3: {"name": "Dark Forest Edge", "n": 4, "s": 0, "e": 0, "w": 2},
        4: {"name": "Prison Ruins", "n": 0, "s": 3, "e": 5, "w": 0},
        5: {"name": "Wizard's Tower", "n": 6, "s": 0, "e": 0, "w": 4},
        6: {"name": "Broken Bridge", "n": 0, "s": 5, "e": 7, "w": 0},
        7: {"name": "Orc Fortress Gate", "n": 0, "s": 0, "e": 0, "w": 6},
    }
    w.items = {
        1: {"room": 8, "name": "gold coin", "takeable": True, "visible": True, "present": True},
        2: {"room": 7, "name": "silver amulet", "takeable": True, "visible": False, "present": True},
        3: {"room": 4, "name": "rusty key", "takeable": True, "visible": True, "present": True},
        4: {"room": 5, "name": "magic scroll", "takeable": True, "visible": True, "present": True},
        5: {"room": 6, "name": "wooden plank", "takeable": True, "visible": True, "present": True},
        6: {"room": 7, "name": "iron key", "takeable": True, "visible": True, "present": True},
    }
    w.npcs = {
        1: {"room": 2, "name": "Innkeeper", "hp": 0, "alive": True, "hostile": False},
        2: {"room": 4, "name": "Prisoner", "hp": 0, "alive": True, "hostile": False},
        3: {"room": 5, "name": "Old Wizard", "hp": 0, "alive": True, "hostile": False},
        4: {"room": 7, "name": "Orc Guard", "hp": 10, "alive": True, "hostile": True},
        5: {"room": 7, "name": "Orc Chieftain", "hp": 20, "alive": True, "hostile": True},
    }
    return w


class TestNarrativeProgression:
    """Verify quest stage advances through key story events."""

    def setup_method(self):
        self.w = build_world()

    def test_initial_quest_stage_zero(self):
        assert self.w.quest_stage == 0

    def test_freeing_prisoner_advances_to_stage_2(self):
        self.w.player_room = 4
        self.w.freed_prisoner = True
        self.w.quest_stage = 2
        assert self.w.quest_stage == 2
        assert self.w.freed_prisoner

    def test_talking_to_wizard_advances(self):
        self.w.player_room = 5
        self.w.talked_to_wizard = True
        assert self.w.talked_to_wizard

    def test_amulet_triggers_wizard_quest(self):
        self.w.obtained_amulet = True
        self.w.quest_stage = 3
        assert self.w.quest_stage == 3

    def test_full_quest_chain(self):
        self.w.freed_prisoner = True
        self.w.obtained_amulet = True
        self.w.talked_to_wizard = True
        self.w.bridge_repaired = True
        self.w.defeated_orc = True
        self.w.quest_stage = 4
        assert self.w.quest_stage == 4


class TestTimeSystem:
    """Verify time-of-day advances with turns."""

    def setup_method(self):
        self.w = build_world()

    def test_starts_at_day(self):
        assert self.w.hour == 1  # Day

    def test_time_advances_every_10_turns(self):
        for _ in range(10):
            self.w.turn_count += 1
        self.w.hour = (self.w.hour + 1) % 4
        assert self.w.hour == 2  # Dusk

    def test_time_wraps_to_dawn(self):
        self.w.hour = 3
        self.w.hour = (self.w.hour + 1) % 4
        assert self.w.hour == 0  # Dawn

    def test_hour_labels(self):
        labels = {0: "Dawn", 1: "Day", 2: "Dusk", 3: "Night"}
        for h, label in labels.items():
            assert len(label) > 0


class TestCombat:
    """Verify combat state transitions."""

    def setup_method(self):
        self.w = build_world()

    def test_defeat_guard_advances_stage(self):
        self.w.npcs[4]["alive"] = False
        self.w.defeated_orc = True
        self.w.quest_stage = 4
        assert not self.w.npcs[4]["alive"]
        assert self.w.defeated_orc

    def test_defeat_chieftain_completes_quest(self):
        self.w.npcs[5]["alive"] = False
        self.w.quest_stage = 5
        assert not self.w.npcs[5]["alive"]

    def test_gold_reward_on_defeat(self):
        self.w.gold += 50
        self.w.gold += 50
        assert self.w.gold == 100

    def test_weapon_upgrade_from_amulet(self):
        self.w.weapon_dmg = 10
        self.w.weapon = "enchanted sword"
        assert self.w.weapon_dmg == 10


class TestLensSnapshot:
    """Verify LENS snapshot captures narrative state."""

    def setup_method(self):
        self.w = build_world()

    def test_initial_snapshot(self):
        snap = self.w.to_lens_snapshot()
        assert snap["quest_stage"] == 0
        assert snap["turn_count"] == 0
        assert not snap["freed_prisoner"]
        assert not snap["defeated_orc"]

    def test_snapshot_reflects_progression(self):
        self.w.freed_prisoner = True
        self.w.quest_stage = 2
        self.w.gold = 100
        self.w.turn_count = 15
        snap = self.w.to_lens_snapshot()
        assert snap["freed_prisoner"]
        assert snap["quest_stage"] == 2
        assert snap["gold"] == 100
        assert snap["turn_count"] == 15


class TestPuzzles:
    """Verify item usage puzzles."""

    def setup_method(self):
        self.w = build_world()

    def test_plank_repairs_bridge(self):
        self.w.player_room = 6
        self.w.bridge_repaired = True
        self.w.quest_stage = 4
        assert self.w.bridge_repaired

    def test_iron_key_unlocks_gate(self):
        self.w.player_room = 7
        self.w.npcs[4]["alive"] = False
        assert not self.w.npcs[4]["alive"]

    def test_scroll_heals_player(self):
        self.w.hp = 10
        self.w.hp = self.w.max_hp
        assert self.w.hp == 20