"""
Unit tests for the uCode BASIC runtime bridge modules.

Tests lens.py, skin.py, and variables.py without requiring
a running BBCSDL process.
"""

import sys
from pathlib import Path

# Ensure runtimes/basic is on the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402
from bridge.lens import (  # noqa: E402
    CellSnapshot,
    LensViewport,
    LensRenderer,
)
from bridge.skin import (  # noqa: E402
    SkinRegistry,
    SkinTheme,
    BBC_PALETTE,
    TELETEXT_PALETTE,
    apply_theme,
    list_themes,
    resolve_colour,
)
from bridge.variables import (  # noqa: E402
    VariableRegister,
    VariableSnapshot,
    VariableManager,
)


class TestCellSnapshot:
    def test_defaults(self):
        cell = CellSnapshot(row=0, col=0)
        assert cell.char == " "
        assert cell.foreground == 7
        assert cell.background == 0
        assert cell.blink is False

    def test_to_dict(self):
        cell = CellSnapshot(row=3, col=5, char="@", foreground=2)
        d = cell.to_dict()
        assert d == {
            "row": 3,
            "col": 5,
            "char": "@",
            "foreground": 2,
            "background": 0,
            "blink": False,
        }


class TestLensViewport:
    def test_default_size(self):
        vp = LensViewport()
        assert vp.cols == 80
        assert vp.rows == 24
        assert len(vp.cells) == 24
        assert len(vp.cells[0]) == 80

    def test_custom_size(self):
        vp = LensViewport(cols=40, rows=10)
        assert vp.cols == 40
        assert vp.rows == 10
        assert len(vp.cells) == 10
        assert len(vp.cells[0]) == 40

    def test_set_cell(self):
        vp = LensViewport(cols=10, rows=5)
        vp.set_cell(2, 3, "@", fg=2, bg=0)
        cell = vp.cells[2][3]
        assert cell.char == "@"
        assert cell.foreground == 2

    def test_set_cell_out_of_bounds(self):
        vp = LensViewport(cols=10, rows=5)
        vp.set_cell(100, 100, "X")  # should not raise
        assert vp.cells[0][0].char == " "  # unchanged

    def test_clear(self):
        vp = LensViewport(cols=5, rows=3)
        vp.set_cell(1, 1, "!")
        vp.clear()
        assert vp.cells[1][1].char == " "

    def test_to_grid(self):
        vp = LensViewport(cols=3, rows=2)
        vp.set_cell(0, 0, "A", fg=7)
        grid = vp.to_grid()
        assert grid["cols"] == 3
        assert grid["rows"] == 2
        assert len(grid["cells"]) == 6


class TestLensRenderer:
    def test_feed_line(self):
        renderer = LensRenderer(cols=10, rows=3)
        renderer.feed_line("ABC")
        assert renderer.viewport.cells[0][0].char == "A"
        assert renderer.viewport.cells[0][1].char == "B"
        assert renderer.viewport.cells[0][2].char == "C"

    def test_feed_with_newline(self):
        renderer = LensRenderer(cols=10, rows=3)
        renderer.feed_line("A\nB")
        assert renderer.viewport.cells[0][0].char == "A"
        assert renderer.viewport.cells[1][0].char == "B"

    def test_set_colours(self):
        renderer = LensRenderer(cols=10, rows=3)
        renderer.set_colours(fg=2, bg=1)
        renderer.feed_line("X")
        fg = renderer.viewport.cells[0][0].foreground
        bg = renderer.viewport.cells[0][0].background
        assert fg == 2
        assert bg == 1

    def test_reset(self):
        renderer = LensRenderer(cols=10, rows=3)
        renderer.feed_line("HELLO")
        renderer.reset()
        assert renderer.viewport.cells[0][0].char == " "
        assert renderer._cursor_row == 0
        assert renderer._cursor_col == 0


class TestSkin:
    def test_bbc_palette_has_8_colours(self):
        assert len(BBC_PALETTE) == 8
        assert BBC_PALETTE[0] == "#000000"
        assert BBC_PALETTE[7] == "#FFFFFF"

    def test_teletext_palette_has_16_colours(self):
        assert len(TELETEXT_PALETTE) == 16

    def test_default_themes(self):
        names = list_themes()
        assert "bbc" in names
        assert "teletext" in names
        assert "inverse" in names

    def test_apply_theme(self):
        theme = apply_theme("teletext")
        assert theme.name == "teletext"

    def test_apply_unknown_falls_back_to_bbc(self):
        theme = apply_theme("nonexistent")
        assert theme.name == "bbc"

    def test_resolve_colour(self):
        assert resolve_colour("bbc", 7) == "#FFFFFF"
        assert resolve_colour("bbc", 99) == "#000000"

    def test_register_custom_theme(self):
        registry = SkinRegistry()
        custom = SkinTheme(
            name="pastel", palette={0: "#FFE0E0", 1: "#E0FFE0"}
        )
        registry.register(custom)
        assert "pastel" in registry.list_names()

    def test_inverse_theme_all_black(self):
        theme = apply_theme("inverse")
        for i in range(16):
            assert theme.palette[i] == "#000000"


class TestVariableRegister:
    def test_defaults(self):
        reg = VariableRegister(name="score", value=100)
        assert reg.name == "score"
        assert reg.value == 100
        assert reg.type_tag == "string"
        assert reg.locked is False

    def test_to_dict(self):
        reg = VariableRegister(name="hp", value=42, type_tag="integer")
        d = reg.to_dict()
        assert d == {
            "name": "hp",
            "value": 42,
            "type": "integer",
            "locked": False,
        }

    def test_from_dict(self):
        reg = VariableRegister.from_dict({
            "name": "name",
            "value": "Alice",
            "type": "string",
            "locked": True,
        })
        assert reg.name == "name"
        assert reg.value == "Alice"
        assert reg.locked is True

    def test_round_trip(self):
        reg = VariableRegister(
            name="x", value=3.14, type_tag="float", locked=False
        )
        data = reg.to_dict()
        restored = VariableRegister.from_dict(data)
        assert restored.name == "x"
        assert restored.value == 3.14
        assert restored.type_tag == "float"


class TestVariableSnapshot:
    def test_set_and_get(self):
        snap = VariableSnapshot()
        snap.set("health", 100, "integer")
        reg = snap.get("health")
        assert reg is not None
        assert reg.value == 100

    def test_get_missing(self):
        snap = VariableSnapshot()
        assert snap.get("nonexistent") is None

    def test_delete(self):
        snap = VariableSnapshot()
        snap.set("temp", 0)
        assert snap.delete("temp") is True
        assert snap.get("temp") is None

    def test_cannot_delete_locked(self):
        snap = VariableSnapshot()
        snap.set("readonly", "secret", locked=True)
        assert snap.delete("readonly") is False
        assert snap.get("readonly") is not None

    def test_to_dict(self):
        snap = VariableSnapshot()
        snap.set("a", 1)
        snap.set("b", 2)
        d = snap.to_dict()
        assert "registers" in d
        assert len(d["registers"]) == 2

    def test_from_dict(self):
        data = {
            "timestamp": "2026-01-01T00:00:00Z",
            "registers": {
                "x": {
                    "name": "x",
                    "value": "hello",
                    "type": "string",
                    "locked": False,
                }
            },
        }
        snap = VariableSnapshot.from_dict(data)
        assert snap.timestamp == "2026-01-01T00:00:00Z"
        assert snap.get("x") is not None

    def test_save_and_load(self, tmp_path):
        snap = VariableSnapshot()
        snap.set("score", 999)
        path = tmp_path / "snapshot.json"
        snap.save(path)

        loaded = VariableSnapshot.load(path)
        reg = loaded.get("score")
        assert reg is not None
        assert reg.value == 999


class TestVariableManager:
    def test_register_and_resolve(self):
        mgr = VariableManager()
        mgr.register("level", 5, "integer")
        assert mgr.resolve("level") == 5

    def test_resolve_missing(self):
        mgr = VariableManager()
        assert mgr.resolve("ghost") is None

    def test_unregister(self):
        mgr = VariableManager()
        mgr.register("temp", "gone")
        assert mgr.unregister("temp") is True
        assert mgr.resolve("temp") is None

    def test_snapshot_and_restore(self):
        mgr = VariableManager()
        mgr.register("a", 1)
        mgr.register("b", 2)
        snap = mgr.snapshot()

        mgr.register("c", 3)
        mgr.restore(snap)

        assert mgr.resolve("a") == 1
        assert mgr.resolve("b") == 2
        assert mgr.resolve("c") is None

    def test_list_names(self):
        mgr = VariableManager()
        mgr.register("one", 1)
        mgr.register("two", 2)
        assert mgr.list_names() == ["one", "two"]