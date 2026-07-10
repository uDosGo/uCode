"""Coordinate system conversion utilities.

Provides conversion functions between different coordinate systems:
Cartesian, Offset (even/odd), Cube, and Axial.
"""

from typing import Tuple

from .models import Coordinate, CoordSystem


def cartesian_to_offset(coord: Coordinate,
                        even_offset: bool = True) -> Coordinate:
    if coord.system in (CoordSystem.OFFSET_EVEN, CoordSystem.OFFSET_ODD):
        return coord
    if coord.system not in (CoordSystem.CARTESIAN,
                            CoordSystem.CARTESIAN_UP):
        raise ValueError(
            f"Cannot convert from {coord.system} to offset")
    system = (CoordSystem.OFFSET_EVEN if even_offset
              else CoordSystem.OFFSET_ODD)
    return Coordinate(coord.x, coord.y, system)


def offset_to_cartesian(coord: Coordinate) -> Coordinate:
    if coord.system not in (CoordSystem.OFFSET_EVEN,
                            CoordSystem.OFFSET_ODD):
        if coord.system in (CoordSystem.CARTESIAN,
                            CoordSystem.CARTESIAN_UP):
            return coord
        raise ValueError(
            f"Cannot convert from {coord.system} to cartesian")
    return Coordinate(coord.x, coord.y, CoordSystem.CARTESIAN_UP)


def cube_to_offset(cube: Coordinate) -> Tuple[Coordinate, Coordinate]:
    if cube.system != CoordSystem.CUBE:
        raise ValueError(f"Expected cube coordinate, got {cube.system}")
    x, y = cube.x, cube.y
    z = cube.z or 0
    even_q = x
    even_r = z + (y + (y & 1)) // 2
    odd_q = x
    odd_r = z + (y - (y & 1)) // 2
    return (
        Coordinate(even_q, even_r, CoordSystem.OFFSET_EVEN),
        Coordinate(odd_q, odd_r, CoordSystem.OFFSET_ODD),
    )


def offset_to_cube(coord: Coordinate) -> Coordinate:
    if coord.system == CoordSystem.CUBE:
        return coord
    if coord.system not in (CoordSystem.OFFSET_EVEN,
                            CoordSystem.OFFSET_ODD):
        raise ValueError(
            f"Expected offset coordinate, got {coord.system}")
    q = coord.x
    r = coord.y
    if coord.system == CoordSystem.OFFSET_EVEN:
        x = q
        z = r - (q + (q & 1)) // 2
        y = -x - z
    else:
        x = q
        z = r - (q - (q & 1)) // 2
        y = -x - z
    return Coordinate(x, y, CoordSystem.CUBE, z)


def axial_to_cube(axial: Coordinate) -> Coordinate:
    if axial.system != CoordSystem.AXIAL:
        raise ValueError(
            f"Expected axial coordinate, got {axial.system}")
    q, r = axial.x, axial.y
    s = -q - r
    return Coordinate(q, r, CoordSystem.CUBE, s)


def cube_to_axial(cube: Coordinate) -> Coordinate:
    if cube.system != CoordSystem.CUBE:
        return Coordinate(cube.x, cube.y, CoordSystem.AXIAL)
    return Coordinate(cube.x, cube.y, CoordSystem.AXIAL)


class CoordinateSystem:
    """Utility class for coordinate system operations."""

    @staticmethod
    def convert(coord: Coordinate, target: CoordSystem) -> Coordinate:
        if coord.system == target:
            return coord

        # Conversion chain: Cube is the universal intermediate
        if coord.system == CoordSystem.CUBE:
            if target == CoordSystem.AXIAL:
                return cube_to_axial(coord)
            elif target in (CoordSystem.OFFSET_EVEN,
                            CoordSystem.OFFSET_ODD):
                result = cube_to_offset(coord)
                return (result[0] if target == CoordSystem.OFFSET_EVEN
                        else result[1])
            else:
                return Coordinate(coord.x, coord.y, target)

        elif coord.system == CoordSystem.AXIAL:
            cube = axial_to_cube(coord)
            return CoordinateSystem.convert(cube, target)

        elif coord.system in (CoordSystem.OFFSET_EVEN,
                              CoordSystem.OFFSET_ODD):
            cube = offset_to_cube(coord)
            return CoordinateSystem.convert(cube, target)

        else:  # Cartesian variants
            if target in (CoordSystem.CARTESIAN,
                          CoordSystem.CARTESIAN_UP):
                if ((coord.system == CoordSystem.CARTESIAN_UP
                     and target == CoordSystem.CARTESIAN)
                    or (coord.system == CoordSystem.CARTESIAN
                        and target == CoordSystem.CARTESIAN_UP)):
                    return Coordinate(coord.x, -coord.y, target)
                return Coordinate(coord.x, coord.y, target)
            cart = Coordinate(coord.x, coord.y,
                              CoordSystem.CARTESIAN_UP)
            return CoordinateSystem.convert(cart, target)

        raise ValueError(
            f"Cannot convert from {coord.system} to {target}")

    @staticmethod
    def distance(a: Coordinate, b: Coordinate) -> float:
        a_cube = CoordinateSystem.convert(a, CoordSystem.CUBE)
        b_cube = CoordinateSystem.convert(b, CoordSystem.CUBE)
        return a_cube.distance_to(b_cube)