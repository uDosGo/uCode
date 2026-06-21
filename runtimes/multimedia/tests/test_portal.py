"""Tests for Portal System."""

from ucode4.portal.portal import PortalSystem, Portal


class TestPortal:
    def test_create_portal(self):
        portal = Portal(
            name="Gateway",
            source_world_id="world-1",
            target_world_id="world-2",
        )
        assert portal.name == "Gateway"
        assert portal.source_world_id == "world-1"
        assert portal.target_world_id == "world-2"
        assert portal.bidirectional is True

    def test_portal_roundtrip(self):
        portal = Portal(
            name="Gateway",
            source_world_id="world-1",
            target_world_id="world-2",
            source_position=(10, 0, 10),
            target_position=(-10, 0, -10),
        )
        data = portal.to_dict()
        restored = Portal.from_dict(data)
        assert restored.name == "Gateway"
        assert restored.source_position == (10, 0, 10)


class TestPortalSystem:
    def test_create_portal(self):
        system = PortalSystem()
        portal = system.create_portal(
            name="Gateway",
            source_world_id="world-1",
            target_world_id="world-2",
        )
        assert portal.name == "Gateway"
        assert len(system.list_portals()) == 1

    def test_find_portals_for_world(self):
        system = PortalSystem()
        system.create_portal(name="P1", source_world_id="world-1", target_world_id="world-2")
        system.create_portal(name="P2", source_world_id="world-2", target_world_id="world-3")
        portals = system.find_portals_for_world("world-1")
        assert len(portals) == 1
        assert portals[0].name == "P1"

    def test_traverse(self):
        system = PortalSystem()
        portal = system.create_portal(
            name="Gateway",
            source_world_id="world-1",
            target_world_id="world-2",
        )
        result = system.traverse(portal.portal_id, "world-1")
        assert result is not None
        assert result["target_world_id"] == "world-2"

    def test_traverse_wrong_world(self):
        system = PortalSystem()
        portal = system.create_portal(
            name="Gateway",
            source_world_id="world-1",
            target_world_id="world-2",
        )
        result = system.traverse(portal.portal_id, "world-3")
        assert result is None
