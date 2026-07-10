"""Tests for udos_shared grid models and coordinate conversions.

These tests run against the shared interface and must pass from both
ucode1 and ucode2 contexts.
"""

import udos_shared as us


class TestCoordinate:
    def test_create_cartesian(self):
        c = us.Coordinate(5, 10)
        assert c.x == 5
        assert c.y == 10
        assert c.system == us.CoordSystem.CARTESIAN

    def test_create_cube(self):
        c = us.Coordinate(1, -2, us.CoordSystem.CUBE, 1)
        assert c.x == 1
        assert c.y == -2
        assert c.z == 1

    def test_from_tuple(self):
        c = us.Coordinate.from_tuple((3, 7))
        assert c.to_tuple() == (3, 7)

    def test_equality(self):
        a = us.Coordinate(1, 2)
        b = us.Coordinate(1, 2)
        c = us.Coordinate(2, 1)
        assert a == b
        assert a != c

    def test_hashable(self):
        s = {us.Coordinate(0, 0), us.Coordinate(1, 1)}
        assert len(s) == 2

    def test_addition(self):
        a = us.Coordinate(1, 2)
        b = us.Coordinate(3, 4)
        result = a + b
        assert result.x == 4
        assert result.y == 6

    def test_distance_euclidean(self):
        a = us.Coordinate(0, 0)
        b = us.Coordinate(3, 4)
        assert a.distance_to(b) == 5.0

    def test_distance_cube(self):
        a = us.Coordinate(0, 0, us.CoordSystem.CUBE, 0)
        b = us.Coordinate(1, -1, us.CoordSystem.CUBE, 0)
        assert a.distance_to(b) == 1.0


class TestGrid:
    def test_create_grid(self):
        g = us.Grid[str](width=5, height=3)
        assert g.width == 5
        assert g.height == 3
        assert len(g) == 15

    def test_get_cell(self):
        g = us.Grid[str](width=4, height=4)
        cell = g.get(2, 2)
        assert cell.x == 2
        assert cell.y == 2
        assert cell.is_empty()

    def test_set_data(self):
        g = us.Grid[str](width=3, height=2)
        g.set_data(1, 0, "hello")
        assert g.get(1, 0).data == "hello"

    def test_bounds_error(self):
        g = us.Grid[str](width=3, height=2)
        try:
            g.get(100, 100)
            assert False, "Should have raised GridBoundsError"
        except us.GridBoundsError as e:
            assert str(e) is not None

    def test_get_safe_out_of_bounds(self):
        g = us.Grid[str](width=3, height=2)
        assert g.get_safe(100, 100) is None

    def test_size(self):
        g = us.Grid[str](width=7, height=9)
        s = g.size()
        assert s.width == 7
        assert s.height == 9
        assert s.area() == 63


class TestCoordinateConversions:
    def test_cartesian_to_offset_identity(self):
        c = us.Coordinate(3, 4, us.CoordSystem.CARTESIAN)
        result = us.cartesian_to_offset(c)
        assert result.system == us.CoordSystem.OFFSET_EVEN

    def test_axial_to_cube(self):
        a = us.Coordinate(2, -3, us.CoordSystem.AXIAL)
        cube = us.axial_to_cube(a)
        assert cube.system == us.CoordSystem.CUBE
        assert cube.x == 2
        assert cube.y == -3
        assert cube.z == 1

    def test_cube_to_axial_roundtrip(self):
        orig = us.Coordinate(2, -3, us.CoordSystem.CUBE, 1)
        axial = us.cube_to_axial(orig)
        assert axial.system == us.CoordSystem.AXIAL

    def test_coordinate_system_convert_cube_to_axial(self):
        cube = us.Coordinate(3, -1, us.CoordSystem.CUBE, -2)
        result = us.CoordinateSystem.convert(cube, us.CoordSystem.AXIAL)
        assert result.system == us.CoordSystem.AXIAL


class TestGridCell:
    def test_create_cell(self):
        cell = us.GridCell[str](data="test", x=1, y=2,
                                fg_color="red", bold=True)
        assert cell.data == "test"
        assert cell.x == 1
        assert cell.y == 2
        assert cell.fg_color == "red"
        assert cell.bold is True

    def test_is_empty_when_no_data(self):
        cell = us.GridCell[int]()
        assert cell.is_empty()

    def test_to_dict(self):
        cell = us.GridCell[str](data="value", x=3, y=4, char="X")
        d = cell.to_dict()
        assert d["data"] == "value"
        assert d["x"] == 3
        assert d["char"] == "X"


class TestGridRegion:
    def test_create_region(self):
        r = us.GridRegion(2, 3, 4, 5)
        assert r.x == 2
        assert r.width == 4
        assert r.height == 5
        assert r.area == 20

    def test_contains(self):
        r = us.GridRegion(0, 0, 10, 10)
        assert r.contains_xy(5, 5)
        assert not r.contains_xy(15, 5)

    def test_iterate(self):
        r = us.GridRegion(0, 0, 2, 2)
        coords = r.iterate()
        assert len(coords) == 4