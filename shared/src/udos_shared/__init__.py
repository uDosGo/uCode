"""uDos Shared — Common grid-core models and coordinate system utilities.

This package provides the canonical interfaces used by ucode1 (BASIC runtime)
and ucode2 (ProseUI/AMOS runtime).  Versioned to allow independent evolution.
"""

from .models import (
    Coordinate,
    CoordSystem,
    Grid,
    GridCell,
    GridRegion,
    GridSize,
)
from .coords import (
    CoordinateSystem,
    axial_to_cube,
    cartesian_to_offset,
    cube_to_axial,
    cube_to_offset,
    offset_to_cartesian,
    offset_to_cube,
)
from .exceptions import (
    CoordinateError,
    GridBoundsError,
    GridError,
    GridSizeError,
)

__version__ = "0.1.0"

__all__ = [
    # Models
    "Coordinate",
    "CoordSystem",
    "Grid",
    "GridCell",
    "GridRegion",
    "GridSize",
    # Coordinate systems
    "CoordinateSystem",
    "cartesian_to_offset",
    "offset_to_cartesian",
    "cube_to_offset",
    "offset_to_cube",
    "axial_to_cube",
    "cube_to_axial",
    # Exceptions
    "GridError",
    "GridBoundsError",
    "CoordinateError",
    "GridSizeError",
]