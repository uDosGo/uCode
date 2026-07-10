"""Grid core models — shared between ucode1 and ucode2 runtimes.

These are the canonical data structures for grid operations,
extracted from core_py/grid/models.py with versioned interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union
from enum import Enum

T = TypeVar("T")


class CoordSystem(Enum):
    """Coordinate system types."""
    CARTESIAN = "cartesian"
    CARTESIAN_UP = "cartesian_up"
    OFFSET_EVEN = "offset_even"
    OFFSET_ODD = "offset_odd"
    CUBE = "cube"
    AXIAL = "axial"


@dataclass
class Coordinate:
    """Represents a coordinate in a grid.

    Supports multiple coordinate systems via conversion methods.
    """

    x: int
    y: int
    system: CoordSystem = CoordSystem.CARTESIAN
    z: Optional[int] = None  # For cube coordinates

    def __post_init__(self):
        if self.system == CoordSystem.CUBE and self.z is None:
            self.z = 0

    @classmethod
    def from_tuple(cls, coords: Tuple[int, int],
                   system: CoordSystem = CoordSystem.CARTESIAN) -> Coordinate:
        return cls(coords[0], coords[1], system)

    @classmethod
    def from_cube(cls, x: int, y: int, z: int) -> Coordinate:
        return cls(x, y, CoordSystem.CUBE, z)

    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def __add__(self, other: Coordinate) -> Coordinate:
        return Coordinate(self.x + other.x, self.y + other.y, self.system)

    def __sub__(self, other: Coordinate) -> Coordinate:
        return Coordinate(self.x - other.x, self.y - other.y, self.system)

    def __mul__(self, scalar: int) -> Coordinate:
        return Coordinate(self.x * scalar, self.y * scalar, self.system)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Coordinate):
            return False
        return (self.x == other.x and self.y == other.y
                and self.system == other.system)

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.system))

    def __repr__(self) -> str:
        return f"Coordinate({self.x}, {self.y}, system={self.system.value})"

    def distance_to(self, other: Coordinate) -> float:
        if self.system == CoordSystem.CUBE or other.system == CoordSystem.CUBE:
            dx = self.x - other.x
            dy = self.y - other.y
            dz = (self.z or 0) - (other.z or 0)
            return (abs(dx) + abs(dy) + abs(dz)) / 2
        else:
            dx = self.x - other.x
            dy = self.y - other.y
            return (dx**2 + dy**2) ** 0.5


@dataclass
class GridSize:
    width: int
    height: int

    @classmethod
    def from_tuple(cls, size: Tuple[int, int]) -> GridSize:
        return cls(size[0], size[1])

    def to_tuple(self) -> Tuple[int, int]:
        return (self.width, self.height)

    def area(self) -> int:
        return self.width * self.height

    def __repr__(self) -> str:
        return f"GridSize({self.width}, {self.height})"


@dataclass
class GridCell(Generic[T]):
    data: Optional[T] = None
    x: int = 0
    y: int = 0
    fg_color: Optional[str] = None
    bg_color: Optional[str] = None
    char: Optional[str] = None
    bold: bool = False
    underline: bool = False
    blink: bool = False
    cell_type: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return self.data is None and self.char is None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data,
            "x": self.x,
            "y": self.y,
            "fg_color": self.fg_color,
            "bg_color": self.bg_color,
            "char": self.char,
            "bold": self.bold,
            "underline": self.underline,
            "blink": self.blink,
            "cell_type": self.cell_type,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        data_repr = repr(self.data) if self.data is not None else "None"
        return f"GridCell({data_repr}, {self.x}, {self.y})"


@dataclass
class GridRegion:
    x: int
    y: int
    width: int
    height: int

    @property
    def size(self) -> GridSize:
        return GridSize(self.width, self.height)

    @property
    def area(self) -> int:
        return self.width * self.height

    def contains(self, coord: Coordinate) -> bool:
        return (self.x <= coord.x < self.x + self.width
                and self.y <= coord.y < self.y + self.height)

    def contains_xy(self, x: int, y: int) -> bool:
        return (self.x <= x < self.x + self.width
                and self.y <= y < self.y + self.height)

    def iterate(self) -> List[Coordinate]:
        return [Coordinate(x, y)
                for y in range(self.y, self.y + self.height)
                for x in range(self.x, self.x + self.width)]

    def __repr__(self) -> str:
        return f"GridRegion({self.x}, {self.y}, {self.width}x{self.height})"


@dataclass
class Grid(Generic[T]):
    width: int
    height: int
    cells: List[List[GridCell[T]]] = field(default_factory=list)
    default_cell: Optional[GridCell[T]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.cells:
            self.cells = [
                [self._create_default_cell(x, y) for x in range(self.width)]
                for y in range(self.height)
            ]

    def _create_default_cell(self, x: int, y: int) -> GridCell[T]:
        if self.default_cell:
            return GridCell(
                data=self.default_cell.data, x=x, y=y,
                fg_color=self.default_cell.fg_color,
                bg_color=self.default_cell.bg_color,
                char=self.default_cell.char,
            )
        return GridCell(x=x, y=y)

    def get(self, x: int, y: int) -> GridCell[T]:
        from .exceptions import GridBoundsError
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise GridBoundsError(x, y, self.width, self.height)
        return self.cells[y][x]

    def get_safe(self, x: int, y: int,
                 default: Optional[GridCell[T]] = None) -> Optional[GridCell[T]]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return default

    def set(self, x: int, y: int, cell: GridCell[T]) -> None:
        from .exceptions import GridBoundsError
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise GridBoundsError(x, y, self.width, self.height)
        self.cells[y][x] = cell
        self.cells[y][x].x = x
        self.cells[y][x].y = y

    def set_data(self, x: int, y: int, data: T) -> None:
        cell = self.get(x, y)
        cell.data = data

    def size(self) -> GridSize:
        return GridSize(self.width, self.height)

    def __repr__(self) -> str:
        return f"Grid({self.width}x{self.height}, cells={self.width * self.height})"

    def __len__(self) -> int:
        return self.width * self.height