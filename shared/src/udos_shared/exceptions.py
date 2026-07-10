"""Shared grid exceptions."""


class GridError(Exception):
    """Base exception for grid operations."""
    pass


class GridBoundsError(GridError):
    """Raised when coordinates are out of grid bounds."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        super().__init__(
            f"Coordinate ({x}, {y}) out of bounds "
            f"for grid size {width}x{height}"
        )


class CoordinateError(GridError):
    """Raised for invalid coordinate operations."""
    pass


class GridSizeError(GridError):
    """Raised for invalid grid size/dimension operations."""
    pass