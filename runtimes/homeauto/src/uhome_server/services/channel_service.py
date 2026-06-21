"""Channel service: source adapters, session controller, and local stream gateway.

Implements the uHOME-server local streaming channel ingestion lane (v2.0.7 Round A).

Boundary: uHOME-server owns local delivery orchestration, not channel ownership.
Upstream channels remain the source of truth.  Clients connect to uHOME-server
first — not directly to the public site.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from uhome_server.config import get_logger

_log = get_logger("uhome.channels")

# ---------------------------------------------------------------------------
# Source adapter layer
# ---------------------------------------------------------------------------

MEDIA_MODE_VIDEO = "video"
MEDIA_MODE_AUDIO_VIDEO = "audio-video"
MEDIA_MODE_AUDIO_FIRST = "audio-first"

GATEWAY_MODE_PASSTHROUGH = "passthrough"
GATEWAY_MODE_PROXY_ASSISTED = "proxy-assisted"


@dataclass
class ChannelAdapter:
    """Metadata descriptor for a single upstream channel source."""

    channel_id: str
    display_name: str
    upstream_url: str
    artwork_url: str
    media_mode: str
    policy_flags: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "display_name": self.display_name,
            "upstream_url": self.upstream_url,
            "artwork_url": self.artwork_url,
            "media_mode": self.media_mode,
            "policy_flags": self.policy_flags,
            "notes": self.notes,
        }


# Canonical channel registry — extend here to add new sources.
_CHANNEL_REGISTRY: list[ChannelAdapter] = [
    ChannelAdapter(
        channel_id="channel.rewind.mtv",
        display_name="Music TV Rewind",
        upstream_url="https://www.youtube.com/@MTVClassic/streams",
        artwork_url="",
        media_mode=MEDIA_MODE_AUDIO_VIDEO,
        policy_flags=["ad-free-experience", "no-login-required", "youtube-embed"],
        notes="Always-on music video channel backed by YouTube-hosted embeds.",
    ),
    ChannelAdapter(
        channel_id="channel.rewind.cartoons",
        display_name="Cartoon Rewind",
        upstream_url="https://www.youtube.com/@CartoonNetwork/streams",
        artwork_url="",
        media_mode=MEDIA_MODE_VIDEO,
        policy_flags=["ad-free-experience", "no-login-required", "youtube-embed"],
        notes="Always-on classic cartoon channel backed by YouTube-hosted embeds.",
    ),
]


def list_channels() -> list[dict[str, Any]]:
    """Return metadata for all registered channels."""
    return [a.to_dict() for a in _CHANNEL_REGISTRY]


def get_channel(channel_id: str) -> Optional[dict[str, Any]]:
    """Return metadata for a single channel, or None if not found."""
    for adapter in _CHANNEL_REGISTRY:
        if adapter.channel_id == channel_id:
            return adapter.to_dict()
    return None


# ---------------------------------------------------------------------------
# Session controller
# ---------------------------------------------------------------------------


@dataclass
class ChannelSession:
    """A per-room playback session bound to a channel."""

    session_id: str
    room: str
    channel_id: str
    state: str = "active"  # active | paused | ended
    device_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "room": self.room,
            "channel_id": self.channel_id,
            "state": self.state,
            "device_ids": list(self.device_ids),
        }


class SessionController:
    """In-memory registry of per-room channel sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, ChannelSession] = {}

    def create(self, room: str, channel_id: str, device_id: Optional[str] = None) -> ChannelSession:
        """Create a new session for a room on the given channel."""
        session_id = str(uuid.uuid4())
        devices = [device_id] if device_id else []
        session = ChannelSession(session_id=session_id, room=room, channel_id=channel_id, device_ids=devices)
        self._sessions[session_id] = session
        _log.debug("Created session %s for room=%s channel=%s", session_id, room, channel_id)
        return session

    def join(self, session_id: str, device_id: str) -> Optional[ChannelSession]:
        """Add a device to an existing session."""
        session = self._sessions.get(session_id)
        if session is None or session.state == "ended":
            return None
        if device_id not in session.device_ids:
            session.device_ids.append(device_id)
        return session

    def sync(self, session_id: str) -> Optional[dict[str, Any]]:
        """Return current session state for sync clients."""
        session = self._sessions.get(session_id)
        if session is None:
            return None
        channel = get_channel(session.channel_id)
        return {
            "session": session.to_dict(),
            "channel": channel,
        }

    def resume(self, session_id: str) -> Optional[ChannelSession]:
        """Resume a paused session."""
        session = self._sessions.get(session_id)
        if session is None or session.state == "ended":
            return None
        session.state = "active"
        return session

    def pause(self, session_id: str) -> Optional[ChannelSession]:
        """Pause an active session."""
        session = self._sessions.get(session_id)
        if session is None or session.state == "ended":
            return None
        session.state = "paused"
        return session

    def move(self, session_id: str, target_room: str) -> Optional[ChannelSession]:
        """Move a session to a different room."""
        session = self._sessions.get(session_id)
        if session is None or session.state == "ended":
            return None
        session.room = target_room
        _log.debug("Moved session %s to room=%s", session_id, target_room)
        return session

    def end(self, session_id: str) -> bool:
        """End a session."""
        session = self._sessions.get(session_id)
        if session is None:
            return False
        session.state = "ended"
        return True

    def list_sessions(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self._sessions.values() if s.state != "ended"]

    def get_session(self, session_id: str) -> Optional[dict[str, Any]]:
        session = self._sessions.get(session_id)
        return session.to_dict() if session else None


# ---------------------------------------------------------------------------
# Local stream gateway
# ---------------------------------------------------------------------------


def resolve_gateway_mode(channel_id: str, client_hint: Optional[str] = None) -> dict[str, Any]:
    """Return the gateway mode and endpoint descriptor for a channel.

    Baseline for v2.0.7 Round A: web-passthrough and proxy-assisted only.
    Transcoded relay is out of scope.
    """
    channel = get_channel(channel_id)
    if channel is None:
        return {"error": f"Unknown channel: {channel_id}"}

    # Client hint may request audio-first; otherwise follow channel default.
    effective_mode = client_hint if client_hint in (MEDIA_MODE_AUDIO_FIRST, MEDIA_MODE_VIDEO, MEDIA_MODE_AUDIO_VIDEO) else channel["media_mode"]

    # Gateway mode selection: proxy-assisted for all known channels in v2.0.7 baseline.
    gateway_mode = GATEWAY_MODE_PROXY_ASSISTED

    return {
        "channel_id": channel_id,
        "gateway_mode": gateway_mode,
        "media_mode": effective_mode,
        "upstream_url": channel["upstream_url"],
        "policy_flags": channel["policy_flags"],
    }


# ---------------------------------------------------------------------------
# Public service facade
# ---------------------------------------------------------------------------

_controller = SessionController()


def get_channel_service() -> _ChannelService:
    return _ChannelService(_controller)


class _ChannelService:
    """Combines adapter registry, session controller, and gateway into one service."""

    def __init__(self, controller: SessionController) -> None:
        self._ctrl = controller

    # --- channel list ----------------------------------------------------------

    def list_channels(self) -> list[dict[str, Any]]:
        return list_channels()

    def get_channel(self, channel_id: str) -> Optional[dict[str, Any]]:
        return get_channel(channel_id)

    # --- gateway ---------------------------------------------------------------

    def resolve_gateway(self, channel_id: str, client_hint: Optional[str] = None) -> dict[str, Any]:
        return resolve_gateway_mode(channel_id, client_hint)

    # --- session lifecycle -----------------------------------------------------

    def create_session(self, room: str, channel_id: str, device_id: Optional[str] = None) -> Optional[dict[str, Any]]:
        if get_channel(channel_id) is None:
            return None
        return self._ctrl.create(room, channel_id, device_id).to_dict()

    def join_session(self, session_id: str, device_id: str) -> Optional[dict[str, Any]]:
        session = self._ctrl.join(session_id, device_id)
        return session.to_dict() if session else None

    def sync_session(self, session_id: str) -> Optional[dict[str, Any]]:
        return self._ctrl.sync(session_id)

    def resume_session(self, session_id: str) -> Optional[dict[str, Any]]:
        session = self._ctrl.resume(session_id)
        return session.to_dict() if session else None

    def pause_session(self, session_id: str) -> Optional[dict[str, Any]]:
        session = self._ctrl.pause(session_id)
        return session.to_dict() if session else None

    def end_session(self, session_id: str) -> bool:
        return self._ctrl.end(session_id)

    def move_session(self, session_id: str, target_room: str) -> Optional[dict[str, Any]]:
        session = self._ctrl.move(session_id, target_room)
        return session.to_dict() if session else None

    def list_sessions(self) -> list[dict[str, Any]]:
        return self._ctrl.list_sessions()

    def get_session(self, session_id: str) -> Optional[dict[str, Any]]:
        return self._ctrl.get_session(session_id)
