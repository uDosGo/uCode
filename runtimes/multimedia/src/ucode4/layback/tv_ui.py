"""TV UI — 10-foot interface theme, screen management, and card-based layouts."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TVTheme(Enum):
    """10-foot UI visual theme."""
    DARK = "dark"
    LIGHT = "light"
    AMBIENT = "ambient"
    GAMING = "gaming"
    CINEMA = "cinema"


class TVScreenType(Enum):
    """Type of TV screen/layout."""
    HOME = "home"
    SEARCH = "search"
    SETTINGS = "settings"
    MEDIA = "media"
    GAME = "game"
    MAP = "map"
    BROWSER = "browser"


@dataclass
class TVCard:
    """A card in the 10-foot UI (movie, app, game, etc.)."""
    card_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    subtitle: str = ""
    image_url: str = ""
    icon: str = ""
    card_type: str = "default"  # "movie", "app", "game", "setting", "custom"
    focusable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "card_id": self.card_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "image_url": self.image_url,
            "icon": self.icon,
            "card_type": self.card_type,
            "focusable": self.focusable,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TVCard":
        return cls(
            card_id=data.get("card_id", str(uuid.uuid4())),
            title=data.get("title", ""),
            subtitle=data.get("subtitle", ""),
            image_url=data.get("image_url", ""),
            icon=data.get("icon", ""),
            card_type=data.get("card_type", "default"),
            focusable=data.get("focusable", True),
            metadata=data.get("metadata", {}),
        )


@dataclass
class TVSection:
    """A horizontal section/row in the TV UI."""
    section_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    cards: List[TVCard] = field(default_factory=list)
    section_type: str = "default"  # "hero", "row", "grid", "list"
    visible: bool = True

    def add_card(self, card: TVCard) -> None:
        self.cards.append(card)

    def remove_card(self, card_id: str) -> bool:
        for i, c in enumerate(self.cards):
            if c.card_id == card_id:
                self.cards.pop(i)
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_id": self.section_id,
            "title": self.title,
            "cards": [c.to_dict() for c in self.cards],
            "section_type": self.section_type,
            "visible": self.visible,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TVSection":
        section = cls(
            section_id=data.get("section_id", str(uuid.uuid4())),
            title=data.get("title", ""),
            section_type=data.get("section_type", "default"),
            visible=data.get("visible", True),
        )
        section.cards = [TVCard.from_dict(c) for c in data.get("cards", [])]
        return section


@dataclass
class TVScreen:
    """A full screen in the 10-foot UI."""
    screen_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    screen_type: TVScreenType = TVScreenType.HOME
    sections: List[TVSection] = field(default_factory=list)
    background: str = ""
    theme: TVTheme = TVTheme.DARK
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_section(self, section: TVSection) -> None:
        self.sections.append(section)

    def remove_section(self, section_id: str) -> bool:
        for i, s in enumerate(self.sections):
            if s.section_id == section_id:
                self.sections.pop(i)
                return True
        return False

    def get_section(self, section_id: str) -> Optional[TVSection]:
        for s in self.sections:
            if s.section_id == section_id:
                return s
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "screen_id": self.screen_id,
            "name": self.name,
            "screen_type": self.screen_type.value,
            "sections": [s.to_dict() for s in self.sections],
            "background": self.background,
            "theme": self.theme.value,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TVScreen":
        screen = cls(
            screen_id=data.get("screen_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            screen_type=TVScreenType(data.get("screen_type", "home")),
            background=data.get("background", ""),
            theme=TVTheme(data.get("theme", "dark")),
            metadata=data.get("metadata", {}),
        )
        screen.sections = [TVSection.from_dict(s) for s in data.get("sections", [])]
        return screen


class TVUI:
    """10-foot TV interface manager — screens, focus, navigation."""

    def __init__(self) -> None:
        self._screens: Dict[str, TVScreen] = {}
        self._active_screen_id: Optional[str] = None
        self._theme: TVTheme = TVTheme.DARK
        self._focus_position: Tuple[int, int] = (0, 0)  # (section_idx, card_idx)
        self._sidebar_visible: bool = False
        self._overlay_visible: bool = False

    @property
    def active_screen(self) -> Optional[TVScreen]:
        if self._active_screen_id:
            return self._screens.get(self._active_screen_id)
        return None

    @property
    def theme(self) -> TVTheme:
        return self._theme

    def set_theme(self, theme: TVTheme) -> None:
        self._theme = theme

    # --- Screen management ---

    def add_screen(self, screen: TVScreen) -> None:
        self._screens[screen.screen_id] = screen
        if self._active_screen_id is None:
            self._active_screen_id = screen.screen_id

    def remove_screen(self, screen_id: str) -> bool:
        if screen_id in self._screens:
            del self._screens[screen_id]
            if self._active_screen_id == screen_id:
                self._active_screen_id = next(iter(self._screens.keys()), None)
            return True
        return False

    def get_screen(self, screen_id: str) -> Optional[TVScreen]:
        return self._screens.get(screen_id)

    def list_screens(self) -> List[TVScreen]:
        return list(self._screens.values())

    def navigate_to_screen(self, screen_id: str) -> bool:
        if screen_id in self._screens:
            self._active_screen_id = screen_id
            self._focus_position = (0, 0)
            return True
        return False

    # --- Focus navigation ---

    @property
    def focus_position(self) -> Tuple[int, int]:
        return self._focus_position

    def move_focus_up(self) -> None:
        section_idx, _ = self._focus_position
        if section_idx > 0:
            self._focus_position = (section_idx - 1, 0)

    def move_focus_down(self) -> None:
        screen = self.active_screen
        if screen and self._focus_position[0] < len(screen.sections) - 1:
            self._focus_position = (self._focus_position[0] + 1, 0)

    def move_focus_left(self) -> None:
        section_idx, card_idx = self._focus_position
        if card_idx > 0:
            self._focus_position = (section_idx, card_idx - 1)

    def move_focus_right(self) -> None:
        screen = self.active_screen
        if screen:
            section_idx, card_idx = self._focus_position
            if section_idx < len(screen.sections):
                section = screen.sections[section_idx]
                if card_idx < len(section.cards) - 1:
                    self._focus_position = (section_idx, card_idx + 1)

    def get_focused_card(self) -> Optional[TVCard]:
        screen = self.active_screen
        if not screen:
            return None
        section_idx, card_idx = self._focus_position
        if section_idx < len(screen.sections):
            section = screen.sections[section_idx]
            if card_idx < len(section.cards):
                return section.cards[card_idx]
        return None

    # --- Sidebar & overlay ---

    def toggle_sidebar(self) -> None:
        self._sidebar_visible = not self._sidebar_visible

    @property
    def sidebar_visible(self) -> bool:
        return self._sidebar_visible

    def show_overlay(self) -> None:
        self._overlay_visible = True

    def hide_overlay(self) -> None:
        self._overlay_visible = False

    @property
    def overlay_visible(self) -> bool:
        return self._overlay_visible

    # --- Serialization ---

    def to_dict(self) -> Dict[str, Any]:
        return {
            "screens": [s.to_dict() for s in self._screens.values()],
            "active_screen_id": self._active_screen_id,
            "theme": self._theme.value,
            "focus_position": list(self._focus_position),
            "sidebar_visible": self._sidebar_visible,
            "overlay_visible": self._overlay_visible,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TVUI":
        ui = cls()
        for sdata in data.get("screens", []):
            screen = TVScreen.from_dict(sdata)
            ui._screens[screen.screen_id] = screen
        ui._active_screen_id = data.get("active_screen_id")
        ui._theme = TVTheme(data.get("theme", "dark"))
        ui._focus_position = tuple(data.get("focus_position", [0, 0]))
        ui._sidebar_visible = data.get("sidebar_visible", False)
        ui._overlay_visible = data.get("overlay_visible", False)
        return ui
