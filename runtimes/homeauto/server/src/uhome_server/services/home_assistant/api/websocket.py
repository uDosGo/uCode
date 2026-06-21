"""WebSocket gateway for Home Assistant real-time updates."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket

from uhome_server.config import get_logger, utc_now_iso_z
from uhome_server.services.home_assistant.gateway.manager import GatewayManager

logger = get_logger("ha-websocket-gateway")


class WebSocketManager:
    def __init__(self, gateway: GatewayManager):
        self.gateway = gateway
        self.active_connections: set[WebSocket] = set()
        self.subscriptions: dict[str, set[WebSocket]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        await self._send_message(
            websocket,
            {
                "type": "welcome",
                "gateway_id": self.gateway.config.gateway_id,
                "version": self.gateway.get_status().version,
                "connected": self.gateway.get_status().connected,
            },
        )

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        for subscribers in self.subscriptions.values():
            subscribers.discard(websocket)

    async def handle_message(self, websocket: WebSocket, message: str) -> bool:
        import json

        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            await self._send_error(websocket, "Invalid JSON")
            return False
        msg_type = data.get("type")
        if msg_type == "subscribe":
            topics = data.get("topics", [])
            for topic in topics:
                self.subscriptions.setdefault(topic, set()).add(websocket)
            await self._send_message(websocket, {"type": "subscribed", "topics": topics, "timestamp": utc_now_iso_z()})
            return True
        if msg_type == "ping":
            await self._send_message(websocket, {"type": "pong"})
            return True
        await self._send_error(websocket, f"Unknown message type: {msg_type}")
        return False

    async def broadcast_state_change(self, device_id: str, state: dict[str, Any]) -> None:
        await self._broadcast_to_all({"type": "state_changed", "device_id": device_id, "state": state})

    async def broadcast_discovery(self, devices: list[dict[str, Any]]) -> None:
        await self._broadcast_to_all({"type": "discovery", "devices": devices, "count": len(devices)})

    async def _send_message(self, websocket: WebSocket, message: dict[str, Any]) -> bool:
        try:
            await websocket.send_json(message)
            return True
        except Exception:
            self.disconnect(websocket)
            return False

    async def _send_error(self, websocket: WebSocket, error: str) -> None:
        await self._send_message(websocket, {"type": "error", "message": error, "timestamp": utc_now_iso_z()})

    async def _broadcast_to_all(self, message: dict[str, Any]) -> None:
        disconnected = set()
        for websocket in self.active_connections:
            if not await self._send_message(websocket, message):
                disconnected.add(websocket)
        for websocket in disconnected:
            self.disconnect(websocket)
