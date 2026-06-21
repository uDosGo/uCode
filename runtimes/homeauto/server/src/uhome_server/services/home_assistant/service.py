"""Main Home Assistant gateway service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from uhome_server.config import get_logger
from uhome_server.services.home_assistant.api.rest import router as rest_router, set_gateway_manager
from uhome_server.services.home_assistant.api.websocket import WebSocketManager
from uhome_server.services.home_assistant.devices import DeviceController, DeviceMonitor, DeviceRegistry, DiscoveryService
from uhome_server.services.home_assistant.gateway.manager import GatewayManager
from uhome_server.services.home_assistant.schemas.gateway import GatewayConfigSchema

logger = get_logger("ha-service")


class HomeAssistantService:
    def __init__(self, config: Optional[GatewayConfigSchema] = None):
        self.config = config or self._default_config()
        self.gateway_manager: Optional[GatewayManager] = None
        self.device_registry: Optional[DeviceRegistry] = None
        self.discovery_service: Optional[DiscoveryService] = None
        self.device_controller: Optional[DeviceController] = None
        self.device_monitor: Optional[DeviceMonitor] = None
        self.ws_manager: Optional[WebSocketManager] = None
        self.app = self._create_app()

    def _default_config(self) -> GatewayConfigSchema:
        return GatewayConfigSchema(
            gateway_id="uhome-ha-main",
            name="uHOME Home Assistant Gateway",
            ha_url="http://localhost:8123",
            ha_token="mock-token",
            ws_enabled=True,
            rest_enabled=True,
            auto_discovery=True,
        )

    def _create_app(self) -> FastAPI:
        @asynccontextmanager
        async def lifespan(_app: FastAPI):
            await self.startup()
            yield
            await self.shutdown()

        app = FastAPI(
            title="uHOME Home Assistant Gateway",
            description="REST/WebSocket gateway for Home Assistant",
            version="0.1.0",
            lifespan=lifespan,
        )
        app.include_router(rest_router)

        @app.websocket("/ws/ha")
        async def websocket_endpoint(websocket: WebSocket):
            await self.ws_manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    await self.ws_manager.handle_message(websocket, data)
            except WebSocketDisconnect:
                self.ws_manager.disconnect(websocket)
            except Exception as exc:
                logger.error("WebSocket error: %s", exc)
                self.ws_manager.disconnect(websocket)

        @app.get("/health")
        async def health():
            return {"status": "ok", "service": "home-assistant"}

        return app

    async def startup(self) -> None:
        self.device_registry = DeviceRegistry()
        self.discovery_service = DiscoveryService(self.device_registry)
        self.device_controller = DeviceController(self.device_registry)
        self.device_monitor = DeviceMonitor(self.device_registry)
        self.gateway_manager = GatewayManager(self.config)
        if not await self.gateway_manager.initialize():
            raise RuntimeError("Failed to initialize gateway manager")
        set_gateway_manager(self.gateway_manager)
        self.ws_manager = WebSocketManager(self.gateway_manager)
        self.gateway_manager.on_event("device_discovered", self._on_device_discovered)
        self.gateway_manager.on_event("state_changed", self._on_state_changed)

    async def shutdown(self) -> None:
        if self.gateway_manager:
            await self.gateway_manager.shutdown()

    async def _on_device_discovered(self, device) -> None:
        self.device_registry.register_device(device.id, device.to_dict())
        if self.ws_manager:
            await self.ws_manager.broadcast_discovery([device.to_dict()])

    async def _on_state_changed(self, state_data) -> None:
        if self.ws_manager and isinstance(state_data, dict):
            await self.ws_manager.broadcast_state_change(state_data.get("device_id", "unknown"), state_data)
