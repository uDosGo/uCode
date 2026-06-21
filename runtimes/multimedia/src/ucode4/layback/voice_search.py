"""Voice Search — Voice command recognition, intent parsing, and search integration."""

from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class VoiceIntent(Enum):
    """Recognized voice command intents."""
    PLAY = "play"
    PAUSE = "pause"
    STOP = "stop"
    NEXT = "next"
    PREVIOUS = "previous"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    MUTE = "mute"
    SEARCH = "search"
    NAVIGATE = "navigate"
    OPEN = "open"
    CLOSE = "close"
    HOME = "home"
    BACK = "back"
    SELECT = "select"
    UNKNOWN = "unknown"


@dataclass
class VoiceCommand:
    """A parsed voice command."""
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intent: VoiceIntent = VoiceIntent.UNKNOWN
    confidence: float = 0.0
    raw_text: str = ""
    entities: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "intent": self.intent.value,
            "confidence": self.confidence,
            "raw_text": self.raw_text,
            "entities": self.entities,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoiceCommand":
        return cls(
            command_id=data.get("command_id", str(uuid.uuid4())),
            intent=VoiceIntent(data.get("intent", "unknown")),
            confidence=data.get("confidence", 0.0),
            raw_text=data.get("raw_text", ""),
            entities=data.get("entities", {}),
            timestamp=data.get("timestamp", time.time()),
        )


class VoiceSearch:
    """Voice command recognition and search integration for 10-foot UI."""

    def __init__(self) -> None:
        self._listening: bool = False
        self._commands: List[VoiceCommand] = []
        self._command_callbacks: Dict[VoiceIntent, List[Callable[[VoiceCommand], None]]] = {}
        self._any_command_callbacks: List[Callable[[VoiceCommand], None]] = []
        self._keyword_patterns: Dict[VoiceIntent, List[str]] = {
            VoiceIntent.PLAY: [r"\bplay\b", r"\bstart\b", r"\bresume\b"],
            VoiceIntent.PAUSE: [r"\bpause\b", r"\bhold\b", r"\bstop\b"],
            VoiceIntent.STOP: [r"\bstop\b", r"\bend\b", r"\bquit\b"],
            VoiceIntent.NEXT: [r"\bnext\b", r"\bskip\b", r"\bforward\b"],
            VoiceIntent.PREVIOUS: [r"\bprevious\b", r"\bback\b", r"\brewind\b"],
            VoiceIntent.VOLUME_UP: [r"\bvolume up\b", r"\blouder\b", r"\bturn it up\b"],
            VoiceIntent.VOLUME_DOWN: [r"\bvolume down\b", r"\bquieter\b", r"\bturn it down\b"],
            VoiceIntent.MUTE: [r"\bmute\b", r"\bsilence\b", r"\bsilent\b"],
            VoiceIntent.SEARCH: [r"\bsearch\b", r"\bfind\b", r"\blook for\b"],
            VoiceIntent.NAVIGATE: [r"\bgo to\b", r"\bnavigate\b", r"\bopen\b"],
            VoiceIntent.OPEN: [r"\bopen\b", r"\blaunch\b", r"\bstart\b"],
            VoiceIntent.CLOSE: [r"\bclose\b", r"\bexit\b", r"\bminimize\b"],
            VoiceIntent.HOME: [r"\bhome\b", r"\bmain menu\b", r"\bgo home\b"],
            VoiceIntent.BACK: [r"\bback\b", r"\bgo back\b", r"\breturn\b"],
            VoiceIntent.SELECT: [r"\bselect\b", r"\bchoose\b", r"\bpick\b"],
        }

    @property
    def listening(self) -> bool:
        return self._listening

    def start_listening(self) -> None:
        self._listening = True

    def stop_listening(self) -> None:
        self._listening = False

    def toggle_listening(self) -> None:
        self._listening = not self._listening

    # --- Command processing ---

    def process_text(self, text: str) -> VoiceCommand:
        """Parse raw text into a voice command."""
        text_lower = text.lower().strip()

        best_intent = VoiceIntent.UNKNOWN
        best_confidence = 0.0
        entities: Dict[str, str] = {}

        for intent, patterns in self._keyword_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    confidence = len(match.group()) / max(len(text_lower), 1)
                    confidence = min(1.0, confidence * 3)  # Scale up for short matches
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent

        # Extract search query for SEARCH intent
        if best_intent == VoiceIntent.SEARCH:
            query_match = re.search(
                r"(?:search|find|look for)\s+(.+?)$", text_lower
            )
            if query_match:
                entities["query"] = query_match.group(1).strip()

        # Extract app name for OPEN intent
        if best_intent == VoiceIntent.OPEN:
            app_match = re.search(r"(?:open|launch|start)\s+(.+?)$", text_lower)
            if app_match:
                entities["app"] = app_match.group(1).strip()

        # Extract navigation target for NAVIGATE intent
        if best_intent == VoiceIntent.NAVIGATE:
            nav_match = re.search(r"(?:go to|navigate|open)\s+(.+?)$", text_lower)
            if nav_match:
                entities["target"] = nav_match.group(1).strip()

        command = VoiceCommand(
            intent=best_intent,
            confidence=best_confidence,
            raw_text=text,
            entities=entities,
        )
        self._commands.append(command)
        if len(self._commands) > 100:
            self._commands = self._commands[-100:]

        self._dispatch(command)
        return command

    def process_command(self, command: VoiceCommand) -> None:
        """Process a pre-parsed voice command."""
        self._commands.append(command)
        if len(self._commands) > 100:
            self._commands = self._commands[-100:]
        self._dispatch(command)

    # --- Callbacks ---

    def on_intent(
        self, intent: VoiceIntent, callback: Callable[[VoiceCommand], None]
    ) -> None:
        if intent not in self._command_callbacks:
            self._command_callbacks[intent] = []
        self._command_callbacks[intent].append(callback)

    def on_any_command(self, callback: Callable[[VoiceCommand], None]) -> None:
        self._any_command_callbacks.append(callback)

    # --- History ---

    def get_recent_commands(self, limit: int = 10) -> List[VoiceCommand]:
        return self._commands[-limit:]

    def clear_history(self) -> None:
        self._commands.clear()

    # --- Internal ---

    def _dispatch(self, command: VoiceCommand) -> None:
        for cb in self._any_command_callbacks:
            cb(command)
        if command.intent in self._command_callbacks:
            for cb in self._command_callbacks[command.intent]:
                cb(command)

    # --- Serialization ---

    def to_dict(self) -> Dict[str, Any]:
        return {
            "listening": self._listening,
            "recent_commands": [c.to_dict() for c in self._commands[-20:]],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoiceSearch":
        vs = cls()
        vs._listening = data.get("listening", False)
        vs._commands = [
            VoiceCommand.from_dict(c) for c in data.get("recent_commands", [])
        ]
        return vs
