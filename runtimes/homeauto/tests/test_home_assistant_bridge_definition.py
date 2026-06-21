from __future__ import annotations

from uhome_server.config import load_home_assistant_bridge_definition
from uhome_server.services.home_assistant_service import HomeAssistantService


def test_bridge_definition_is_loaded_from_uhome_matter():
    definition = load_home_assistant_bridge_definition()
    assert definition["extension"] == "uHOME-matter"
    assert definition["runtime_owner"] == "uHOME-server"
    assert "uhome.playback.status" in definition["command_allowlist"]
    assert "uhome.launcher.menu" in definition["command_allowlist"]


def test_home_assistant_service_uses_shared_bridge_definition():
    service = HomeAssistantService()
    status = service.status()
    discover = service.discover()
    capabilities = service.execute_command("system.capabilities", {})

    assert status["bridge"] == "uhome-ha"
    assert status["command_allowlist_size"] == len(capabilities["result"]["allowlist"])
    assert discover["entity_count"] == len(discover["entities"])
    assert any(entity["id"] == "uhome.playback" for entity in discover["entities"])
    assert any(entity["id"] == "uhome.launcher" for entity in discover["entities"])
