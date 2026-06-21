"""Gamepad — D-pad navigation, button mapping, and event handling for 10-foot UI."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class GamepadButton(Enum):
    """Standard gamepad buttons."""
    DPAD_UP = "dpad_up"
    DPAD_DOWN = "dpad_down"
    DPAD_LEFT = "dpad_left"
    DPAD_RIGHT = "dpad_right"
    A = "a"
    B = "b"
    X = "x"
    Y = "y"
    START = "start"
    SELECT = "select"
    HOME = "home"
    L1 = "l1"
    R1 = "r1"
    L2 = "l2"
    R2 = "r2"
    L3 = "l3"
    R3 = "r3"


class GamepadAxis(Enum):
    """Analog stick axes."""
    LEFT_X = "left_x"
    LEFT_Y = "left_y"
    RIGHT_X = "right_x"
    RIGHT_Y = "right_y"


class ButtonAction(Enum):
    """Button press action type."""
    PRESS = "press"
    RELEASE = "release"
    HOLD = "hold"


@dataclass
class GamepadEvent:
    """A gamepad input event."""
    button: Optional[GamepadButton] = None
    axis: Optional[GamepadAxis] = None
    action: ButtonAction = ButtonAction.PRESS
    value: float = 0.0  # 1.0 for press, axis value for analog
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "button": self.button.value if self.button else None,
            "axis": self.axis.value if self.axis else None,
            "action": self.action.value,
            "value": self.value,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GamepadEvent":
        return cls(
            button=GamepadButton(data["button"]) if data.get("button") else None,
            axis=GamepadAxis(data["axis"]) if data.get("axis") else None,
            action=ButtonAction(data.get("action", "press")),
            value=data.get("value", 0.0),
            timestamp=data.get("timestamp", time.time()),
        )


class Gamepad:
    """Gamepad input handler with button mapping and event callbacks."""

    def __init__(self) -> None:
        self._button_callbacks: Dict[GamepadButton, List[Callable[[GamepadEvent], None]]] = {}
        self._axis_callbacks: Dict[GamepadAxis, List[Callable[[GamepadEvent], None]]] = {}
        self._any_callbacks: List[Callable[[GamepadEvent], None]] = []
        self._pressed_buttons: Dict[GamepadButton, float] = {}  # button -> press start time
        self._axis_values: Dict[GamepadAxis, float] = {
            axis: 0.0 for axis in GamepadAxis
        }
        self._deadzone: float = 0.15
        self._connected: bool = False
        self._player_index: int = 0

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False
        self._pressed_buttons.clear()

    @property
    def deadzone(self) -> float:
        return self._deadzone

    def set_deadzone(self, value: float) -> None:
        self._deadzone = max(0.0, min(1.0, value))

    # --- Button handling ---

    def on_button(self, button: GamepadButton, callback: Callable[[GamepadEvent], None]) -> None:
        if button not in self._button_callbacks:
            self._button_callbacks[button] = []
        self._button_callbacks[button].append(callback)

    def on_any_button(self, callback: Callable[[GamepadEvent], None]) -> None:
        self._any_callbacks.append(callback)

    def press_button(self, button: GamepadButton) -> None:
        """Simulate a button press."""
        if not self._connected:
            return
        event = GamepadEvent(button=button, action=ButtonAction.PRESS, value=1.0)
        self._pressed_buttons[button] = time.time()
        self._dispatch(event)

    def release_button(self, button: GamepadButton) -> None:
        """Simulate a button release."""
        if not self._connected:
            return
        event = GamepadEvent(button=button, action=ButtonAction.RELEASE, value=0.0)
        self._pressed_buttons.pop(button, None)
        self._dispatch(event)

    def is_pressed(self, button: GamepadButton) -> bool:
        return button in self._pressed_buttons

    def get_pressed_duration(self, button: GamepadButton) -> float:
        """Get how long a button has been held (seconds)."""
        start = self._pressed_buttons.get(button)
        if start:
            return time.time() - start
        return 0.0

    # --- Axis handling ---

    def on_axis(self, axis: GamepadAxis, callback: Callable[[GamepadEvent], None]) -> None:
        if axis not in self._axis_callbacks:
            self._axis_callbacks[axis] = []
        self._axis_callbacks[axis].append(callback)

    def set_axis(self, axis: GamepadAxis, value: float) -> None:
        """Set an analog axis value."""
        if not self._connected:
            return
        # Apply deadzone
        if abs(value) < self._deadzone:
            value = 0.0
        self._axis_values[axis] = value
        event = GamepadEvent(axis=axis, action=ButtonAction.PRESS, value=value)
        self._dispatch(event)

    def get_axis(self, axis: GamepadAxis) -> float:
        return self._axis_values.get(axis, 0.0)

    # --- Navigation helpers ---

    def navigate_up(self) -> None:
        self.press_button(GamepadButton.DPAD_UP)
        self.release_button(GamepadButton.DPAD_UP)

    def navigate_down(self) -> None:
        self.press_button(GamepadButton.DPAD_DOWN)
        self.release_button(GamepadButton.DPAD_DOWN)

    def navigate_left(self) -> None:
        self.press_button(GamepadButton.DPAD_LEFT)
        self.release_button(GamepadButton.DPAD_LEFT)

    def navigate_right(self) -> None:
        self.press_button(GamepadButton.DPAD_RIGHT)
        self.release_button(GamepadButton.DPAD_RIGHT)

    def confirm(self) -> None:
        self.press_button(GamepadButton.A)
        self.release_button(GamepadButton.A)

    def back(self) -> None:
        self.press_button(GamepadButton.B)
        self.release_button(GamepadButton.B)

    def menu(self) -> None:
        self.press_button(GamepadButton.START)
        self.release_button(GamepadButton.START)

    # --- Internal ---

    def _dispatch(self, event: GamepadEvent) -> None:
        for cb in self._any_callbacks:
            cb(event)
        if event.button and event.button in self._button_callbacks:
            for cb in self._button_callbacks[event.button]:
                cb(event)
        if event.axis and event.axis in self._axis_callbacks:
            for cb in self._axis_callbacks[event.axis]:
                cb(event)

    # --- Serialization ---

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connected": self._connected,
            "player_index": self._player_index,
            "deadzone": self._deadzone,
            "pressed_buttons": [b.value for b in self._pressed_buttons.keys()],
            "axis_values": {a.value: v for a, v in self._axis_values.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Gamepad":
        gp = cls()
        gp._connected = data.get("connected", False)
        gp._player_index = data.get("player_index", 0)
        gp._deadzone = data.get("deadzone", 0.15)
        gp._axis_values = {
            GamepadAxis(k): v for k, v in data.get("axis_values", {}).items()
        }
        return gp
