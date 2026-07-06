"""
SKIN — colour/character theming for BBCSDL LENS output.

Maps standard BBC BASIC colour indices and character glyphs to
named palettes and tile sets, enabling theme-switching in the
viewport without modifying the underlying BASIC program.
"""

from dataclasses import dataclass

# BBC Micro default palette (8 colours)
BBC_PALETTE = {
    0: "#000000",  # black
    1: "#FF0000",  # red
    2: "#00FF00",  # green
    3: "#FFFF00",  # yellow
    4: "#0000FF",  # blue
    5: "#FF00FF",  # magenta
    6: "#00FFFF",  # cyan
    7: "#FFFFFF",  # white
}

# Teletext-compatible extended palette
TELETEXT_PALETTE = {
    0: "#000000",
    1: "#FF0000",
    2: "#00FF00",
    3: "#FFFF00",
    4: "#0000FF",
    5: "#FF00FF",
    6: "#00FFFF",
    7: "#FFFFFF",
    8: "#000000",  # flashing black
    9: "#FF0000",  # flashing red
    10: "#00FF00",
    11: "#FFFF00",
    12: "#0000FF",
    13: "#FF00FF",
    14: "#00FFFF",
    15: "#FFFFFF",
}


@dataclass
class SkinTheme:
    name: str
    palette: dict[int, str]
    description: str = ""


DEFAULT_THEMES = {
    "bbc": SkinTheme(
        name="bbc",
        palette=BBC_PALETTE,
        description="Classic BBC Micro 8-colour palette.",
    ),
    "teletext": SkinTheme(
        name="teletext",
        palette=TELETEXT_PALETTE,
        description="Teletext-style 16-colour display.",
    ),
    "inverse": SkinTheme(
        name="inverse",
        palette={i: "#000000" for i in range(16)},
        description="All-black monochrome (skeleton mode).",
    ),
}


class SkinRegistry:
    """
    Registry of named SKIN themes with lookup and application helpers.
    """

    def __init__(self):
        self._themes: dict[str, SkinTheme] = dict(DEFAULT_THEMES)

    def register(self, theme: SkinTheme) -> None:
        self._themes[theme.name] = theme

    def get(self, name: str) -> SkinTheme:
        if name in self._themes:
            return self._themes[name]
        return self._themes["bbc"]

    def list_names(self) -> list[str]:
        return sorted(self._themes.keys())

    def resolve_colour(self, theme_name: str, index: int) -> str:
        theme = self.get(theme_name)
        return theme.palette.get(index, "#000000")


# Module-level singleton for convenience
_skin = SkinRegistry()


def apply_theme(name: str) -> SkinTheme:
    return _skin.get(name)


def list_themes() -> list[str]:
    return _skin.list_names()


def resolve_colour(theme_name: str, colour_index: int) -> str:
    return _skin.resolve_colour(theme_name, colour_index)