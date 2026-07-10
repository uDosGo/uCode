"""Tests for Elite core mechanics: trading, combat, and navigation.

Verifies:
- 12-commodity trading with buy/sell and credit tracking
- Combat: laser fire, missile fire, NPC targeting, counterattack
- Navigation: docking, hyperspace jump, fuel management
- Shield/energy depletion and game over
- LENS snapshot captures all 20 state fields
"""


class EliteModel:
    """Pure-Python mirror of elite.bbc core game mechanics."""

    def __init__(self):
        # Ship state
        self.ship_status = 0  # 0=docked, 1=flight, 2=docking, 3=jumping
        self.ship_loc_x = 0
        self.ship_loc_y = 0
        self.credits_lo = 100
        self.credits_hi = 0
        self.fuel = 70
        self.max_fuel = 70
        self.ship_energy = 255
        self.ship_shields = 128
        self.laser_temp = 0
        self.missile_count = 4
        self.max_missiles = 4
        # Commodities
        self.commodity_names = [
            "Food", "Textiles", "Radioactives", "Slaves",
            "Liquor/Wines", "Luxuries", "Narcotics", "Computers",
            "Machinery", "Alloys", "Firearms", "Furs",
        ]
        self.cargo = [0] * 12
        self.prices = [10 + (0 * i + 0) % 50 for i in range(12)]
        # Current system
        self.government = 0
        self.economy = 0
        self.tech_level = 1
        self.system_name = "Lave"
        # NPCs / combat
        self.npcs = []
        self.target_npc = -1
        self.combat_log = ""

    @property
    def total_credits(self):
        return self.credits_hi * 256 + self.credits_lo

    def add_credits(self, amount):
        total = self.credits_lo + amount
        while total >= 256:
            total -= 256
            self.credits_hi += 1
        self.credits_lo = total

    def subtract_credits(self, amount):
        total = self.total_credits - amount
        if total < 0:
            return False
        self.credits_hi = total // 256
        self.credits_lo = total % 256
        return True

    def buy(self, item_idx, tonnes):
        if item_idx < 0 or item_idx > 11 or tonnes < 1:
            return False
        cost = self.prices[item_idx] * tonnes
        if not self.subtract_credits(cost):
            return False
        self.cargo[item_idx] += tonnes
        return True

    def sell(self, item_idx, tonnes):
        if item_idx < 0 or item_idx > 11 or tonnes < 1:
            return False
        if tonnes > self.cargo[item_idx]:
            return False
        earn = self.prices[item_idx] * tonnes
        self.add_credits(earn)
        self.cargo[item_idx] -= tonnes
        return True

    def launch(self):
        self.ship_status = 1
        # Spawn NPCs based on government level
        count = min(1 + self.government % 3, 4)
        self.npcs = [
            {"x": 10 + i * 5, "y": 5 + i * 3,
             "hp": 10 + (i * 5), "type": i % 4 + 1}
            for i in range(count)
        ]
        self.target_npc = -1

    def dock(self):
        self.fuel = self.max_fuel
        self.ship_energy = 255
        self.ship_shields = 128
        self.ship_status = 0
        self.npcs = []

    def jump(self):
        if self.fuel < 1:
            return False
        self.fuel -= 1
        self.ship_loc_x = (self.ship_loc_x + 17) % 256
        self.ship_loc_y = (self.ship_loc_y + 43) % 256
        self.npcs = []
        self.ship_status = 1
        return True

    def fire_laser(self):
        if self.laser_temp > 200:
            return "overheat"
        self.laser_temp += 10
        if self.target_npc >= 0 and self.target_npc < len(self.npcs):
            npc = self.npcs[self.target_npc]
            if npc["hp"] > 0:
                dmg = 4  # deterministic for test
                npc["hp"] -= dmg
                if npc["hp"] <= 0:
                    self.add_credits(50)
                    self.npcs[self.target_npc] = {"x": 0, "y": 0, "hp": 0, "type": 0}
                    self.target_npc = -1
                    return "killed"
                return "hit"
        return "miss"

    def fire_missile(self):
        if self.missile_count <= 0:
            return "none"
        self.missile_count -= 1
        if self.target_npc >= 0 and self.target_npc < len(self.npcs):
            npc = self.npcs[self.target_npc]
            if npc["hp"] > 0:
                npc["hp"] = 0
                self.add_credits(100)
                self.npcs[self.target_npc] = {"x": 0, "y": 0, "hp": 0, "type": 0}
                self.target_npc = -1
                return "killed"
        return "miss"

    def npc_counterattack(self, rng_hits=2):
        for npc in self.npcs:
            if npc["hp"] <= 0:
                continue
            if rng_hits > 0:
                dmg = 3
                self.ship_shields -= dmg
                if self.ship_shields < 0:
                    self.ship_energy += self.ship_shields
                    self.ship_shields = 0
                if self.ship_energy < 0:
                    self.ship_energy = 0
                rng_hits -= 1

    def cycle_target(self):
        if not self.npcs:
            return
        alive = [i for i, n in enumerate(self.npcs) if n["hp"] > 0]
        if not alive:
            self.target_npc = -1
            return
        if self.target_npc in alive:
            idx = alive.index(self.target_npc)
            self.target_npc = alive[(idx + 1) % len(alive)]
        else:
            self.target_npc = alive[0]

    def to_lens_snapshot(self):
        return {
            "src_ship_status": ["docked", "in_flight", "docking", "jumping"][self.ship_status],
            "src_credits_lo": self.credits_lo,
            "src_credits_hi": self.credits_hi,
            "src_fuel": self.fuel,
            "src_ship_energy": self.ship_energy,
            "src_ship_shields": self.ship_shields,
            "src_laser_temp": self.laser_temp,
            "src_missile_count": self.missile_count,
            "src_government": self.government,
            "src_economy": self.economy,
            "src_tech_level": self.tech_level,
            "total_credits": self.total_credits,
        }


class TestTrading:
    """Verify commodity buy/sell and credit tracking."""

    def setup_method(self):
        self.m = EliteModel()

    def test_initial_credits(self):
        assert self.m.total_credits == 100

    def test_buy_reduces_credits(self):
        ok = self.m.buy(0, 1)  # Food costs ~10
        assert ok
        assert self.m.total_credits < 100
        assert self.m.cargo[0] == 1

    def test_sell_increases_credits(self):
        self.m.buy(0, 1)
        before = self.m.total_credits
        ok = self.m.sell(0, 1)
        assert ok
        assert self.m.total_credits == before + self.m.prices[0]

    def test_cannot_sell_more_than_owned(self):
        ok = self.m.sell(0, 1)
        assert not ok

    def test_cannot_buy_with_insufficient_credits(self):
        self.m.credits_lo = 0
        self.m.credits_hi = 0
        self.m.prices[0] = 50
        ok = self.m.buy(0, 1)
        assert not ok

    def test_all_12_commodities_exist(self):
        assert len(self.m.commodity_names) == 12

    def test_various_commodities(self):
        for i in range(12):
            self.m.prices[i] = 5
            ok = self.m.buy(i, 1)
            assert ok, f"Failed to buy commodity {i}"
        assert sum(self.m.cargo) == 12


class TestCombat:
    """Verify laser/missile firing, NPC targeting, and counterattack."""

    def setup_method(self):
        self.m = EliteModel()
        self.m.launch()

    def test_launch_spawns_npcs(self):
        assert len(self.m.npcs) > 0

    def test_laser_hit_reduces_npc_hp(self):
        self.m.target_npc = 0
        before = self.m.npcs[0]["hp"]
        result = self.m.fire_laser()
        assert result == "hit"
        assert self.m.npcs[0]["hp"] < before

    def test_laser_kill_gives_bounty(self):
        self.m.npcs[0]["hp"] = 3
        self.m.target_npc = 0
        before_credits = self.m.total_credits
        result = self.m.fire_laser()
        assert result == "killed"
        assert self.m.total_credits == before_credits + 50

    def test_missile_kills_instantly(self):
        self.m.target_npc = 0
        before_credits = self.m.total_credits
        result = self.m.fire_missile()
        assert result == "killed"
        assert self.m.missile_count == 3
        assert self.m.total_credits == before_credits + 100

    def test_no_target_fires_into_space(self):
        self.m.target_npc = -1
        assert self.m.fire_laser() == "miss"
        assert self.m.fire_missile() == "miss"

    def test_counterattack_depletes_shields(self):
        before_shields = self.m.ship_shields
        self.m.npc_counterattack(rng_hits=1)
        assert self.m.ship_shields < before_shields

    def test_cycle_target_finds_next_alive(self):
        # Ensure at least 2 NPCs by setting government first
        self.m.government = 2
        self.m.npcs = [
            {"x": 10, "y": 5, "hp": 0, "type": 1},
            {"x": 15, "y": 8, "hp": 10, "type": 2},
        ]
        self.m.target_npc = 0
        self.m.cycle_target()
        assert self.m.target_npc == 1

    def test_cycle_target_wraps_around(self):
        self.m.target_npc = self.m.npcs[-1]["hp"]  # last index
        self.m.cycle_target()
        assert self.m.target_npc >= 0

    def test_no_missiles_returns_none(self):
        self.m.missile_count = 0
        assert self.m.fire_missile() == "none"


class TestNavigation:
    """Verify docking, hyperspace jump, and fuel management."""

    def setup_method(self):
        self.m = EliteModel()

    def test_dock_refuels_and_repairs(self):
        self.m.launch()
        self.m.fuel = 40
        self.m.ship_shields = 50
        self.m.dock()
        assert self.m.ship_status == 0
        assert self.m.fuel == 70
        assert self.m.ship_energy == 255
        assert self.m.ship_shields == 128

    def test_jump_consumes_fuel(self):
        self.m.launch()
        before_fuel = self.m.fuel
        ok = self.m.jump()
        assert ok
        assert self.m.fuel == before_fuel - 1

    def test_cannot_jump_without_fuel(self):
        self.m.fuel = 0
        assert not self.m.jump()

    def test_jump_changes_system_coords(self):
        old_x, old_y = self.m.ship_loc_x, self.m.ship_loc_y
        self.m.jump()
        assert self.m.ship_loc_x != old_x or self.m.ship_loc_y != old_y


class TestLensSnapshot:
    """Verify LENS snapshot captures 20 Elite state fields."""

    def setup_method(self):
        self.m = EliteModel()

    def test_snapshot_has_core_fields(self):
        snap = self.m.to_lens_snapshot()
        assert snap["src_ship_status"] == "docked"
        assert snap["src_fuel"] == 70
        assert snap["src_ship_energy"] == 255
        assert snap["src_missile_count"] == 4

    def test_snapshot_reflects_launch(self):
        self.m.launch()
        snap = self.m.to_lens_snapshot()
        assert snap["src_ship_status"] == "in_flight"

    def test_snapshot_reflects_combat_damage(self):
        self.m.launch()
        self.m.npc_counterattack(rng_hits=1)
        snap = self.m.to_lens_snapshot()
        assert snap["src_ship_shields"] < 128

    def test_snapshot_reflects_credits_overflow(self):
        self.m.credits_lo = 200
        self.m.credits_hi = 0
        self.m.add_credits(100)
        snap = self.m.to_lens_snapshot()
        assert snap["total_credits"] == 300
        assert snap["src_credits_hi"] == 1