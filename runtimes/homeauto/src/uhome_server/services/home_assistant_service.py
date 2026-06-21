"""Standalone Home Assistant bridge service."""

from __future__ import annotations

from typing import Any

from uhome_server.config import JSONConfigStore, load_home_assistant_bridge_definition


class HomeAssistantService:
    """uHOME server ↔ Home Assistant bridge service."""

    def __init__(self, config: JSONConfigStore | None = None):
        self.config = config or JSONConfigStore()
        self.definition = load_home_assistant_bridge_definition()

    def _bridge_name(self) -> str:
        return str(self.definition.get("bridge", "uhome-ha"))

    def _bridge_version(self) -> str:
        return str(self.definition.get("version", "0.1.0"))

    def _command_allowlist(self) -> set[str]:
        allowlist = self.definition.get("command_allowlist", [])
        return {item for item in allowlist if isinstance(item, str)}

    def _entities(self) -> list[dict[str, Any]]:
        entities = self.definition.get("entities", [])
        return [item for item in entities if isinstance(item, dict)]

    def is_enabled(self) -> bool:
        return bool(self.config.get("ha_bridge_enabled", False))

    def status(self) -> dict[str, Any]:
        enabled = self.is_enabled()
        return {
            "bridge": self._bridge_name(),
            "version": self._bridge_version(),
            "status": "ok" if enabled else "disabled",
            "enabled": enabled,
            "command_allowlist_size": len(self._command_allowlist()),
        }

    def discover(self) -> dict[str, Any]:
        entities = self._entities()
        return {
            "bridge": self._bridge_name(),
            "version": self._bridge_version(),
            "entity_count": len(entities),
            "entities": entities,
        }

    def execute_command(self, command: str, params: dict[str, Any]) -> dict[str, Any]:
        command_allowlist = self._command_allowlist()
        if command not in command_allowlist:
            raise ValueError(f"Command not in allowlist: {command!r}")

        if command == "system.info":
            return {"command": "system.info", "result": {"bridge_version": self._bridge_version()}}
        if command == "system.capabilities":
            return {"command": "system.capabilities", "result": {"allowlist": sorted(command_allowlist)}}
        if command.startswith("uhome."):
            from uhome_server.services.uhome_command_handlers import dispatch

            try:
                return dispatch(command, params)
            except KeyError:
                return {
                    "command": command,
                    "status": "unimplemented",
                    "note": f"Handler for {command!r} not yet wired.",
                    "params": params,
                }
        raise ValueError(f"Unhandled allowlisted command: {command!r}")


def get_ha_service() -> HomeAssistantService:
    return HomeAssistantService()
