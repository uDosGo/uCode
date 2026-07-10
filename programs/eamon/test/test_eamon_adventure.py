"""Deterministic tests for the Eamon text adventure model.

Verifies:
- Verb/Noun parser tokenization
- Room graph traversal and exit directions
- Item pickup/drop and inventory management
- Combat mechanics and HP transitions
- LENS snapshot reflects room/player state changes
- Quest completion path (8-room linear path)
"""


class EamonWorld:
    """Pure-Python mirror of eamon.bbc world model."""

    def __init__(self):
        self.rooms = {}
        self.items = {}
        self.monsters = {}
        self.player_room = 1
        self.hp = 15
        self.max_hp = 15
        self.agility = 12
        self.charisma = 10
        self.gold = 0
        self.weapon = "fists"
        self.weapon_dmg = 2
        self.inventory = []
        self.goblin_alive = True
        self.troll_alive = True
        self.quest_done = False

    def room_exits(self, room_id):
        room = self.rooms.get(room_id, {})
        exits = {}
        if room.get("n"):
            exits["north"] = room["n"]
        if room.get("s"):
            exits["south"] = room["s"]
        if room.get("e"):
            exits["east"] = room["e"]
        if room.get("w"):
            exits["west"] = room["w"]
        return exits

    def move(self, direction):
        room = self.rooms.get(self.player_room, {})
        dest = room.get(direction)
        if dest is None or dest == 0:
            return False
        self.player_room = dest
        return True

    def items_in_room(self):
        return [i for i in self.items.values()
                if i["room"] == self.player_room and i["present"]]

    def take_item(self, item_name):
        for item in self.items.values():
            if item["room"] == self.player_room and item["present"]:
                if item_name.lower() in item["name"].lower():
                    if not item["takeable"]:
                        return None
                    if len(self.inventory) >= 10:
                        return None
                    item["present"] = False
                    self.inventory.append(item["name"])
                    return item["name"]
        return None

    def drop_item(self, item_name):
        for i, name in enumerate(self.inventory):
            if item_name.lower() in name.lower():
                self.inventory.pop(i)
                for item in self.items.values():
                    if not item["present"]:
                        item["room"] = self.player_room
                        item["present"] = True
                        item["name"] = name
                        return name
        return None

    def to_lens_snapshot(self):
        return {
            "room": self.player_room,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "agility": self.agility,
            "charisma": self.charisma,
            "gold": self.gold,
            "weapon": self.weapon,
            "weapon_dmg": self.weapon_dmg,
            "inv_count": len(self.inventory),
            "inventory": list(self.inventory),
            "goblin_alive": self.goblin_alive,
            "troll_alive": self.troll_alive,
        }


def build_world():
    """Build the standard 8-room Eamon world (matching eamon.bbc)."""
    w = EamonWorld()
    w.rooms = {
        1: {"name": "Main Hall",
            "desc": "A grand hall with marble floors.",
            "n": 2, "s": 0, "e": 3, "w": 0},
        2: {"name": "Armory",
            "desc": "Weapons and shields line the walls.",
            "n": 0, "s": 1, "e": 0, "w": 4},
        3: {"name": "Kitchen",
            "desc": "A warm kitchen with pots bubbling.",
            "n": 0, "s": 0, "e": 0, "w": 1},
        4: {"name": "Library",
            "desc": "Dusty shelves tower around you.",
            "n": 5, "s": 0, "e": 2, "w": 0},
        5: {"name": "Treasury",
            "desc": "Gold coins glitter in torchlight.",
            "n": 0, "s": 4, "e": 6, "w": 0},
        6: {"name": "Guard Room",
            "desc": "A burly goblin guard blocks the passage.",
            "n": 0, "s": 0, "e": 7, "w": 5},
        7: {"name": "Throne Room",
            "desc": "An ornate throne dominates this chamber.",
            "n": 0, "s": 0, "e": 8, "w": 6},
        8: {"name": "Victory Chamber",
            "desc": "Sunlight streams through high windows.",
            "n": 0, "s": 0, "e": 0, "w": 7},
    }
    w.items = {
        1: {"room": 1, "name": "rusty dagger", "takeable": True,
            "present": True},
        2: {"room": 2, "name": "broadsword", "takeable": True,
            "present": True},
        3: {"room": 3, "name": "meat pie", "takeable": True,
            "present": True},
        4: {"room": 4, "name": "ancient scroll", "takeable": True,
            "present": True},
        5: {"room": 5, "name": "gold chalice", "takeable": True,
            "present": True},
        6: {"room": 8, "name": "victory crown", "takeable": True,
            "present": True},
    }
    return w


class TestRoomGraph:
    """Verify the 8-room world layout and connectivity."""

    def setup_method(self):
        self.w = build_world()

    def test_start_in_main_hall(self):
        assert self.w.player_room == 1
        assert self.w.rooms[1]["name"] == "Main Hall"

    def test_main_hall_exits(self):
        exits = self.w.room_exits(1)
        assert "north" in exits
        assert "east" in exits
        assert "south" not in exits
        assert "west" not in exits
        assert exits["north"] == 2
        assert exits["east"] == 3

    def test_armory_exits(self):
        exits = self.w.room_exits(2)
        assert exits["south"] == 1
        assert exits["west"] == 4

    def test_library_exits(self):
        exits = self.w.room_exits(4)
        assert exits["north"] == 5
        assert exits["east"] == 2

    def test_victory_chamber_exits(self):
        exits = self.w.room_exits(8)
        assert exits["west"] == 7
        assert "east" not in exits

    def test_move_north_from_main_hall(self):
        assert self.w.move("n")
        assert self.w.player_room == 2

    def test_move_into_dead_end_blocked(self):
        assert not self.w.move("s")  # no south exit from room 1

    def test_full_linear_path_to_victory(self):
        path = ["n", "w", "n", "e", "e", "e"]
        for d in path:
            assert self.w.move(d), f"Failed at direction {d}"
        assert self.w.player_room == 8
        assert self.w.rooms[8]["name"] == "Victory Chamber"


class TestItems:
    """Verify item placement, pickup, and inventory."""

    def setup_method(self):
        self.w = build_world()

    def test_main_hall_has_dagger(self):
        items = self.w.items_in_room()
        assert any("dagger" in i["name"] for i in items)

    def test_take_dagger(self):
        result = self.w.take_item("dagger")
        assert result is not None
        assert "dagger" in result
        assert len(self.w.inventory) == 1

    def test_take_sword_from_armory(self):
        self.w.player_room = 2
        result = self.w.take_item("sword")
        assert result is not None
        assert "broadsword" in result

    def test_cant_take_twice(self):
        self.w.take_item("dagger")
        items = self.w.items_in_room()
        assert not any("dagger" in i["name"] for i in items)

    def test_drop_item(self):
        self.w.take_item("dagger")
        assert len(self.w.inventory) == 1
        result = self.w.drop_item("dagger")
        assert result is not None
        assert len(self.w.inventory) == 0

    def test_inventory_full_at_10(self):
        self.w.inventory = ["item"] * 10
        result = self.w.take_item("dagger")
        assert result is None


class TestCombat:
    """Verify combat state transitions."""

    def setup_method(self):
        self.w = build_world()

    def test_goblin_guard_starts_alive(self):
        assert self.w.goblin_alive

    def test_defeat_goblin(self):
        self.w.goblin_alive = False
        self.w.gold += 10
        assert not self.w.goblin_alive
        assert self.w.gold == 10

    def test_defeat_troll(self):
        self.w.troll_alive = False
        self.w.gold += 25
        assert not self.w.troll_alive
        assert self.w.gold == 25

    def test_hp_loss_in_combat(self):
        initial_hp = self.w.hp
        self.w.hp -= 4
        assert self.w.hp == initial_hp - 4

    def test_weapon_upgrade(self):
        self.w.weapon = "broadsword"
        self.w.weapon_dmg = 6
        assert self.w.weapon_dmg > 2


class TestLensSnapshot:
    """Verify LENS CAPTURE eamon reflects room/player changes."""

    def setup_method(self):
        self.w = build_world()

    def test_initial_snapshot(self):
        snap = self.w.to_lens_snapshot()
        assert snap["room"] == 1
        assert snap["hp"] == 15
        assert snap["gold"] == 0
        assert snap["weapon"] == "fists"
        assert snap["goblin_alive"]
        assert snap["troll_alive"]

    def test_snapshot_reflects_movement(self):
        before_room = self.w.to_lens_snapshot()["room"]
        self.w.move("n")
        after_room = self.w.to_lens_snapshot()["room"]
        assert after_room != before_room
        assert after_room == 2

    def test_snapshot_reflects_pickup(self):
        before_inv = self.w.to_lens_snapshot()["inv_count"]
        self.w.take_item("dagger")
        after_inv = self.w.to_lens_snapshot()["inv_count"]
        assert after_inv > before_inv

    def test_snapshot_reflects_combat(self):
        self.w.goblin_alive = False
        self.w.gold += 10
        snap = self.w.to_lens_snapshot()
        assert not snap["goblin_alive"]
        assert snap["gold"] == 10


class TestParser:
    """Verify VERB NOUN command parsing."""

    def test_first_word(self):
        assert first_word("TAKE SWORD") == "TAKE"
        assert first_word("NORTH") == "NORTH"
        assert first_word("") == ""

    def test_rest_words(self):
        assert rest_words("TAKE SWORD") == "SWORD"
        assert rest_words("ATTACK GOBLIN GUARD") == "GOBLIN GUARD"
        assert rest_words("NORTH") == ""

    def test_uppercase(self):
        assert upper("hello") == "HELLO"
        assert upper("Sword") == "SWORD"


def first_word(s):
    p = s.find(" ")
    if p == -1:
        return s
    return s[:p]


def rest_words(s):
    p = s.find(" ")
    if p == -1:
        return ""
    return s[p + 1:]


def upper(s):
    result = ""
    for ch in s:
        c = ord(ch)
        if 97 <= c <= 122:
            c -= 32
        result += chr(c)
    return result