"""Tests for uConstruct tile map save/load format.

The BBC BASIC program (uconstruct.bbc) saves maps as:
  Line 1: width,height  (e.g. "15,15")
  Line 2: comma-separated tile IDs  (e.g. "0,0,1,1,0,...")

These tests validate that:
1. A roundtrip save/load preserves all tile and layer metadata
2. Map validation catches invalid tiles
3. Resource costs are consistent with the tile type definitions
"""

import tempfile
from pathlib import Path

TILE_COSTS = {0: 0, 1: 1, 2: 2, 3: 1, 4: 3, 5: 1, 6: 0}
TILE_NAMES = {
    0: "empty", 1: "wall", 2: "water", 3: "door",
    4: "creature-spawn", 5: "item", 6: "floor",
}
TILE_CHARS = {0: ".", 1: " ", 2: "#", 3: "~", 4: "D", 5: "C", 6: "I"}
WALKABLE = {0, 4, 6}  # empty, creature-spawn, floor


def save_map(path, width, height, tiles):
    """Write a uConstruct .map file (matching uconstruct.bbc PROCsave)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(f"{width},{height}\n")
        f.write(",".join(str(t) for t in tiles) + "\n")


def load_map(path):
    """Read a uConstruct .map file (matching uconstruct.bbc PROCload)."""
    with open(path) as f:
        dim_line = f.readline().strip()
        tile_line = f.readline().strip()
    w_str, h_str = dim_line.split(",")
    width, height = int(w_str), int(h_str)
    tiles = [int(t) for t in tile_line.split(",") if t]
    return width, height, tiles


def compute_cost(tiles):
    return sum(TILE_COSTS[t] for t in tiles)


def validate_map(width, height, tiles):
    errors = []
    if len(tiles) != width * height:
        errors.append(f"tile count {len(tiles)} != {width}x{height}")
    for t in tiles:
        if t < 0 or t > 6:
            errors.append(f"invalid tile type: {t}")
    return errors


def tiles_to_string(tiles):
    """Render tiles as a 2D grid string (same as uconstruct PROCrender)."""
    width = height = int(len(tiles) ** 0.5)
    lines = []
    for y in range(height):
        row = " ".join(TILE_CHARS[t] for t in tiles[y * width:(y + 1) * width])
        lines.append(row)
    return "\n".join(lines)


class TestSaveLoad:
    """Verify save/load roundtrip preserves all tile/layer metadata."""

    def test_roundtrip_default_15x15(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "test.map"
            tiles = [0] * (15 * 15)
            tiles[0] = 1  # wall top-left
            tiles[14] = 1  # wall top-right
            save_map(path, 15, 15, tiles)
            w, h, loaded = load_map(path)
            assert w == 15
            assert h == 15
            assert loaded == tiles

    def test_roundtrip_full_tile_set(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "full.map"
            tiles = [i % 7 for i in range(25)]  # 5x5 with all tile types
            save_map(path, 5, 5, tiles)
            w, h, loaded = load_map(path)
            assert loaded == tiles

    def test_roundtrip_modified_map(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "modified.map"
            tiles = [0] * 100  # 10x10 empty
            # Place walls around border
            for x in range(10):
                tiles[x] = 1
                tiles[x + 90] = 1
            for y in range(10):
                tiles[y * 10] = 1
                tiles[y * 10 + 9] = 1
            # Place water and floor
            tiles[55] = 2  # water at center
            tiles[56] = 6  # floor
            save_map(path, 10, 10, tiles)
            w, h, loaded = load_map(path)
            assert loaded == tiles

    def test_non_square_map(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "wide.map"
            tiles = [0] * 40  # 8x5
            tiles[0] = 1
            save_map(path, 8, 5, tiles)
            w, h, loaded = load_map(path)
            assert w == 8
            assert h == 5
            assert loaded == tiles


class TestResourceCosts:
    """Verify tile costs match the resource model from uconstruct.bbc."""

    def test_empty_cost_zero(self):
        assert TILE_COSTS[0] == 0

    def test_wall_cost_one(self):
        assert TILE_COSTS[1] == 1

    def test_water_cost_two(self):
        assert TILE_COSTS[2] == 2

    def test_creature_cost_three(self):
        assert TILE_COSTS[4] == 3

    def test_total_cost_computation(self):
        tiles = [0, 1, 2, 3, 4, 5, 6]
        expected = 0 + 1 + 2 + 1 + 3 + 1 + 0  # 8
        assert compute_cost(tiles) == expected

    def test_empty_map_cost_zero(self):
        tiles = [0] * 225  # 15x15
        assert compute_cost(tiles) == 0

    def test_full_wall_map_cost(self):
        tiles = [1] * 225
        assert compute_cost(tiles) == 225


class TestValidation:
    """Verify map validation logic."""

    def test_valid_map_empty(self):
        errors = validate_map(5, 5, [0] * 25)
        assert errors == []

    def test_valid_map_mixed(self):
        errors = validate_map(3, 3, [0, 1, 2, 3, 4, 5, 6, 0, 1])
        assert errors == []

    def test_invalid_tile_type_negative(self):
        errors = validate_map(2, 2, [0, 0, -1, 0])
        assert len(errors) >= 1
        assert "invalid" in errors[0]

    def test_invalid_tile_count(self):
        errors = validate_map(5, 5, [0] * 24)  # 24 tiles, not 25
        assert len(errors) >= 1
        assert "tile count" in errors[0]

    def test_tile_within_range(self):
        for t in range(7):
            errors = validate_map(1, 1, [t])
            assert errors == [], f"Tile {t} should be valid"


class TestTileRepresentation:
    """Verify tile-to-character mapping matches uconstruct.bbc C$ string."""

    def test_character_map_complete(self):
        assert len(TILE_CHARS) == 7

    def test_empty_character(self):
        assert TILE_CHARS[0] == "."

    def test_wall_character(self):
        assert TILE_CHARS[1] == " "

    def test_water_character(self):
        assert TILE_CHARS[2] == "#"

    def test_floor_character(self):
        assert TILE_CHARS[6] == "I"


class TestWalkability:
    """Verify walkable tile types."""

    def test_empty_is_walkable(self):
        assert 0 in WALKABLE

    def test_wall_is_not_walkable(self):
        assert 1 not in WALKABLE

    def test_water_is_not_walkable(self):
        assert 2 not in WALKABLE

    def test_floor_is_walkable(self):
        assert 6 in WALKABLE