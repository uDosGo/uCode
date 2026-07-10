"""Tests for Apple Panic core mechanics: scoring, digging, enemy behavior.

Verifies:
- Dig fills create holes that enemies can fall into
- Killing enemies via fill gives score
- Score overflow at 256 increments high byte
- Enemy count scales with level
- Lives decrement on collision
"""


class ApplePanicModel:
    """Pure-Python mirror of apple_panic.bbc core mechanics."""

    def __init__(self):
        self.grid_w = 32
        self.grid_h = 18
        self.max_lives = 3
        self.max_holes = 3
        self.hole_lifetime = 15
        self.enemy_trap_time = 9
        self.score = 0
        self.score_hi = 0
        self.level = 1
        self.lives = self.max_lives
        self.px = 16
        self.py = 16
        self.pd = 1
        self.platforms = {16: True, 13: True, 10: True, 7: True, 4: True, 1: True}
        self.holes = []
        self.enemy_count = 3
        self.enemies = []

    def add_score(self, points):
        self.score += points
        while self.score >= 256:
            self.score -= 256
            self.score_hi += 1

    def dig(self, dx, dy):
        if len(self.holes) >= self.max_holes:
            return
        self.holes.append({"x": dx, "y": dy, "timer": self.hole_lifetime})

    def fill(self, fx, fy):
        for i, hole in enumerate(self.holes):
            if hole["x"] == fx and hole["y"] == fy:
                self.holes.pop(i)
                self.add_score(200)
                return True
        return False

    def enemy_fall_into_hole(self, ex, ey):
        for hole in self.holes:
            if hole["x"] == ex and hole["y"] == ey:
                self.add_score(100)
                return True
        return False

    def tick_holes(self):
        for hole in list(self.holes):
            hole["timer"] -= 1
            if hole["timer"] <= 0:
                self.holes.remove(hole)

    def player_hit(self):
        self.lives -= 1

    def next_level(self):
        self.level += 1
        self.enemy_count = min(3 + self.level - 1, 7)


class TestScoring:
    """Verify scoring mechanics."""

    def test_initial_score_zero(self):
        m = ApplePanicModel()
        assert m.score == 0
        assert m.score_hi == 0

    def test_fill_kill_gives_200(self):
        m = ApplePanicModel()
        m.dig(10, 16)
        m.fill(10, 16)
        assert m.score == 200

    def test_enemy_trapped_gives_100(self):
        m = ApplePanicModel()
        m.dig(10, 16)
        m.enemy_fall_into_hole(10, 16)
        assert m.score == 100

    def test_score_overflow_to_high_byte(self):
        m = ApplePanicModel()
        m.add_score(200)
        m.add_score(100)
        assert m.score == 44  # (200+100) % 256 = 44
        assert m.score_hi == 1

    def test_cumulative_score_tracking(self):
        m = ApplePanicModel()
        m.add_score(200)
        m.add_score(200)
        m.add_score(100)
        assert m.score == 244  # 500 - 256 = 244
        assert m.score_hi == 1  # 500 // 256


class TestDigMechanics:
    """Verify hole creation and lifetime."""

    def test_max_holes_enforced(self):
        m = ApplePanicModel()
        for i in range(5):
            m.dig(i, 16)
        assert len(m.holes) <= m.max_holes

    def test_hole_lifetime_decreases(self):
        m = ApplePanicModel()
        m.dig(10, 16)
        before = m.holes[0]["timer"]
        m.tick_holes()
        assert m.holes[0]["timer"] == before - 1

    def test_hole_removed_when_lifetime_expires(self):
        m = ApplePanicModel()
        m.holes.append({"x": 5, "y": 13, "timer": 0})
        m.tick_holes()
        assert len(m.holes) == 0

    def test_fill_removes_hole_and_scores(self):
        m = ApplePanicModel()
        m.dig(3, 10)
        assert len(m.holes) == 1
        result = m.fill(3, 10)
        assert result
        assert len(m.holes) == 0
        assert m.score == 200


class TestEnemyBehavior:
    """Verify enemy count scaling and trap mechanics."""

    def test_enemy_count_at_level_1(self):
        m = ApplePanicModel()
        assert m.enemy_count == 3

    def test_enemy_count_scale_with_level(self):
        m = ApplePanicModel()
        m.next_level()
        assert m.enemy_count == 4  # level 2: 3+2-1=4

    def test_enemy_count_capped_at_7(self):
        m = ApplePanicModel()
        m.level = 6
        m.next_level()
        assert m.enemy_count <= 7

    def test_enemy_trap_time(self):
        m = ApplePanicModel()
        assert m.enemy_trap_time == 9


class TestLivesAndGameOver:
    """Verify lives decrement and game-over condition."""

    def test_lives_start_at_3(self):
        m = ApplePanicModel()
        assert m.lives == 3

    def test_player_hit_decrements_lives(self):
        m = ApplePanicModel()
        m.player_hit()
        assert m.lives == 2
        m.player_hit()
        assert m.lives == 1

    def test_game_over_when_lives_zero(self):
        m = ApplePanicModel()
        m.lives = 1
        m.player_hit()
        assert m.lives <= 0


class TestDifficultyProgression:
    """Verify difficulty scales with level."""

    def test_level_starts_at_1(self):
        m = ApplePanicModel()
        assert m.level == 1

    def test_level_advances(self):
        m = ApplePanicModel()
        m.next_level()
        assert m.level == 2

    def test_enemies_increase_with_difficulty(self):
        m = ApplePanicModel()
        initial = m.enemy_count
        m.level = 5
        m.next_level()
        assert m.enemy_count > initial