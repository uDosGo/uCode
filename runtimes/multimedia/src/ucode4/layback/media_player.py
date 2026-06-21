"""Media Player — Playback controls, queue management, and media item handling."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class PlaybackState(Enum):
    """Media playback state."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    BUFFERING = "buffering"
    LOADING = "loading"
    ERROR = "error"


class MediaType(Enum):
    """Type of media content."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    STREAM = "stream"
    LIVE = "live"


class RepeatMode(Enum):
    """Repeat mode for playback."""
    NONE = "none"
    ONE = "one"
    ALL = "all"


@dataclass
class MediaItem:
    """A playable media item."""
    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    artist: str = ""
    album: str = ""
    media_type: MediaType = MediaType.VIDEO
    url: str = ""
    thumbnail_url: str = ""
    duration_seconds: float = 0.0
    current_position: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def progress(self) -> float:
        """Playback progress as 0.0-1.0."""
        if self.duration_seconds > 0:
            return min(1.0, self.current_position / self.duration_seconds)
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "media_type": self.media_type.value,
            "url": self.url,
            "thumbnail_url": self.thumbnail_url,
            "duration_seconds": self.duration_seconds,
            "current_position": self.current_position,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaItem":
        return cls(
            item_id=data.get("item_id", str(uuid.uuid4())),
            title=data.get("title", ""),
            artist=data.get("artist", ""),
            album=data.get("album", ""),
            media_type=MediaType(data.get("media_type", "video")),
            url=data.get("url", ""),
            thumbnail_url=data.get("thumbnail_url", ""),
            duration_seconds=data.get("duration_seconds", 0.0),
            current_position=data.get("current_position", 0.0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class MediaQueue:
    """A queue of media items for sequential playback."""
    queue_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Default Queue"
    items: List[MediaItem] = field(default_factory=list)
    current_index: int = -1
    repeat_mode: RepeatMode = RepeatMode.NONE
    shuffle: bool = False

    @property
    def current_item(self) -> Optional[MediaItem]:
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index]
        return None

    def add_item(self, item: MediaItem) -> None:
        self.items.append(item)

    def add_items(self, items: List[MediaItem]) -> None:
        self.items.extend(items)

    def insert_item(self, index: int, item: MediaItem) -> None:
        self.items.insert(index, item)

    def remove_item(self, item_id: str) -> bool:
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                self.items.pop(i)
                if self.current_index >= i and self.current_index > 0:
                    self.current_index -= 1
                return True
        return False

    def clear(self) -> None:
        self.items.clear()
        self.current_index = -1

    def next(self) -> Optional[MediaItem]:
        if not self.items:
            return None
        if self.current_index < len(self.items) - 1:
            self.current_index += 1
            return self.items[self.current_index]
        elif self.repeat_mode == RepeatMode.ALL:
            self.current_index = 0
            return self.items[0]
        elif self.repeat_mode == RepeatMode.ONE:
            return self.items[self.current_index]
        return None

    def previous(self) -> Optional[MediaItem]:
        if not self.items:
            return None
        if self.current_index > 0:
            self.current_index -= 1
            return self.items[self.current_index]
        elif self.repeat_mode == RepeatMode.ALL:
            self.current_index = len(self.items) - 1
            return self.items[self.current_index]
        return None

    def jump_to(self, index: int) -> Optional[MediaItem]:
        if 0 <= index < len(self.items):
            self.current_index = index
            return self.items[index]
        return None

    @property
    def length(self) -> int:
        return len(self.items)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "queue_id": self.queue_id,
            "name": self.name,
            "items": [i.to_dict() for i in self.items],
            "current_index": self.current_index,
            "repeat_mode": self.repeat_mode.value,
            "shuffle": self.shuffle,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaQueue":
        queue = cls(
            queue_id=data.get("queue_id", str(uuid.uuid4())),
            name=data.get("name", "Default Queue"),
            current_index=data.get("current_index", -1),
            repeat_mode=RepeatMode(data.get("repeat_mode", "none")),
            shuffle=data.get("shuffle", False),
        )
        queue.items = [MediaItem.from_dict(i) for i in data.get("items", [])]
        return queue


class MediaPlayer:
    """Media playback engine with queue management and state tracking."""

    def __init__(self) -> None:
        self._state: PlaybackState = PlaybackState.STOPPED
        self._queue: MediaQueue = MediaQueue()
        self._volume: float = 0.8
        self._muted: bool = False
        self._playback_rate: float = 1.0
        self._state_callbacks: List[Callable[[PlaybackState], None]] = []
        self._position_callbacks: List[Callable[[float], None]] = []
        self._queue_callbacks: List[Callable[[MediaQueue], None]] = []

    @property
    def state(self) -> PlaybackState:
        return self._state

    @property
    def queue(self) -> MediaQueue:
        return self._queue

    @property
    def volume(self) -> float:
        return 0.0 if self._muted else self._volume

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))

    @property
    def muted(self) -> bool:
        return self._muted

    def toggle_mute(self) -> None:
        self._muted = not self._muted

    @property
    def playback_rate(self) -> float:
        return self._playback_rate

    def set_playback_rate(self, rate: float) -> None:
        self._playback_rate = max(0.25, min(4.0, rate))

    # --- Playback controls ---

    def play(self) -> None:
        if self._state == PlaybackState.PAUSED or self._state == PlaybackState.STOPPED:
            self._set_state(PlaybackState.PLAYING)

    def pause(self) -> None:
        if self._state == PlaybackState.PLAYING:
            self._set_state(PlaybackState.PAUSED)

    def toggle_play_pause(self) -> None:
        if self._state == PlaybackState.PLAYING:
            self.pause()
        else:
            self.play()

    def stop(self) -> None:
        self._set_state(PlaybackState.STOPPED)
        if self._queue.current_item:
            self._queue.current_item.current_position = 0.0

    def seek(self, position: float) -> None:
        current = self._queue.current_item
        if current:
            current.current_position = max(0.0, min(position, current.duration_seconds))
            for cb in self._position_callbacks:
                cb(current.current_position)

    def seek_forward(self, seconds: float = 10.0) -> None:
        current = self._queue.current_item
        if current:
            self.seek(current.current_position + seconds)

    def seek_backward(self, seconds: float = 10.0) -> None:
        current = self._queue.current_item
        if current:
            self.seek(current.current_position - seconds)

    def next_track(self) -> None:
        next_item = self._queue.next()
        if next_item:
            self._set_state(PlaybackState.PLAYING)
            for cb in self._queue_callbacks:
                cb(self._queue)

    def previous_track(self) -> None:
        prev_item = self._queue.previous()
        if prev_item:
            self._set_state(PlaybackState.PLAYING)
            for cb in self._queue_callbacks:
                cb(self._queue)

    # --- Queue management ---

    def load_queue(self, queue: MediaQueue) -> None:
        self._queue = queue
        self._set_state(PlaybackState.LOADING)
        for cb in self._queue_callbacks:
            cb(self._queue)

    def play_item(self, item: MediaItem) -> None:
        """Play a specific item immediately."""
        self._queue.add_item(item)
        self._queue.jump_to(len(self._queue.items) - 1)
        self._set_state(PlaybackState.PLAYING)
        for cb in self._queue_callbacks:
            cb(self._queue)

    def add_to_queue(self, item: MediaItem) -> None:
        self._queue.add_item(item)
        for cb in self._queue_callbacks:
            cb(self._queue)

    def clear_queue(self) -> None:
        self._queue.clear()
        self._set_state(PlaybackState.STOPPED)
        for cb in self._queue_callbacks:
            cb(self._queue)

    # --- Callbacks ---

    def on_state_change(self, callback: Callable[[PlaybackState], None]) -> None:
        self._state_callbacks.append(callback)

    def on_position_change(self, callback: Callable[[float], None]) -> None:
        self._position_callbacks.append(callback)

    def on_queue_change(self, callback: Callable[[MediaQueue], None]) -> None:
        self._queue_callbacks.append(callback)

    # --- Internal ---

    def _set_state(self, state: PlaybackState) -> None:
        self._state = state
        for cb in self._state_callbacks:
            cb(state)

    # --- Serialization ---

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self._state.value,
            "queue": self._queue.to_dict(),
            "volume": self._volume,
            "muted": self._muted,
            "playback_rate": self._playback_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaPlayer":
        player = cls()
        player._state = PlaybackState(data.get("state", "stopped"))
        player._queue = MediaQueue.from_dict(data.get("queue", {}))
        player._volume = data.get("volume", 0.8)
        player._muted = data.get("muted", False)
        player._playback_rate = data.get("playback_rate", 1.0)
        return player
