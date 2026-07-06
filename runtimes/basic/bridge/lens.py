"""
LENS — viewport-mapping layer for BBCSDL output.

Translates raw BBCSDL text-mode output into a structured cell grid
suitable for consumption by GridCore viewport widgets.
"""

from dataclasses import dataclass, field


@dataclass
class CellSnapshot:
    row: int
    col: int
    char: str = " "
    foreground: int = 7   # default white
    background: int = 0   # default black
    blink: bool = False

    def to_dict(self) -> dict:
        return {
            "row": self.row,
            "col": self.col,
            "char": self.char,
            "foreground": self.foreground,
            "background": self.background,
            "blink": self.blink,
        }


@dataclass
class LensViewport:
    cols: int = 80
    rows: int = 24
    cells: list[list[CellSnapshot]] = field(default_factory=list)

    def __post_init__(self):
        if not self.cells:
            self.cells = [
                [CellSnapshot(row=r, col=c) for c in range(self.cols)]
                for r in range(self.rows)
            ]

    def set_cell(
        self,
        row: int,
        col: int,
        char: str,
        fg: int = 7,
        bg: int = 0,
        blink: bool = False,
    ) -> None:
        """Update a single cell in the viewport grid."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.cells[row][col] = CellSnapshot(
                row=row, col=col, char=char, foreground=fg,
                background=bg, blink=blink,
            )

    def clear(self):
        """Reset all cells to blank."""
        for row in range(self.rows):
            for col in range(self.cols):
                self.cells[row][col] = CellSnapshot(row=row, col=col)

    def to_grid(self) -> dict:
        """Export viewport as a grid-format dict."""
        return {
            "cols": self.cols,
            "rows": self.rows,
            "cells": [
                cell.to_dict()
                for row in self.cells
                for cell in row
            ],
        }


class LensRenderer:
    """
    High-level renderer: accept BBCSDL output lines and drive a
    LensViewport, optionally applying SKIN theme transformations.
    """

    def __init__(self, cols: int = 80, rows: int = 24):
        self.viewport = LensViewport(cols=cols, rows=rows)
        self._cursor_row = 0
        self._cursor_col = 0
        self._current_fg = 7
        self._current_bg = 0

    def feed_line(self, line: str) -> None:
        """Render a single line of BBCSDL text output."""
        for char in line:
            if char == "\n":
                self._cursor_row += 1
                self._cursor_col = 0
                continue

            if self._cursor_row < self.viewport.rows:
                self.viewport.set_cell(
                    row=self._cursor_row,
                    col=self._cursor_col,
                    char=char,
                    fg=self._current_fg,
                    bg=self._current_bg,
                )
                self._cursor_col += 1

                if self._cursor_col >= self.viewport.cols:
                    self._cursor_col = 0
                    self._cursor_row += 1

    def set_colours(self, fg: int, bg: int) -> None:
        """Set foreground/background colours for subsequent writes."""
        self._current_fg = fg
        self._current_bg = bg

    def reset(self) -> None:
        """Clear viewport and reset cursor."""
        self.viewport.clear()
        self._cursor_row = 0
        self._cursor_col = 0