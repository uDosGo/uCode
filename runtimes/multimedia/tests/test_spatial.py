"""Tests for Spatial Index."""

from ucode4.spatial.index import SpatialIndex, SpatialQuery, SpatialEntity


class TestSpatialEntity:
    def test_distance_to(self):
        e1 = SpatialEntity(entity_id="1", position=(0, 0, 0))
        e2 = SpatialEntity(entity_id="2", position=(3, 4, 0))
        assert e1.distance_to(e2) == 5.0

    def test_distance_to_point(self):
        e = SpatialEntity(entity_id="1", position=(0, 0, 0))
        assert e.distance_to_point((3, 4, 0)) == 5.0


class TestSpatialIndex:
    def test_add_entity(self):
        idx = SpatialIndex()
        entity = idx.add_entity("player", (0, 0, 0), "character")
        assert entity.entity_id == "player"
        assert idx.count == 1

    def test_query_radius(self):
        idx = SpatialIndex()
        idx.add_entity("e1", (0, 0, 0), "item")
        idx.add_entity("e2", (5, 0, 0), "item")
        idx.add_entity("e3", (20, 0, 0), "item")

        query = SpatialQuery(center=(0, 0, 0), radius=10)
        results = idx.query(query)
        assert len(results) == 2  # e1 and e2

    def test_find_nearest(self):
        idx = SpatialIndex()
        idx.add_entity("e1", (0, 0, 0), "item")
        idx.add_entity("e2", (5, 0, 0), "item")
        idx.add_entity("e3", (20, 0, 0), "item")

        nearest = idx.find_nearest((1, 0, 0))
        assert nearest is not None
        assert nearest.entity_id == "e1"

    def test_entities_in_bounds(self):
        idx = SpatialIndex()
        idx.add_entity("e1", (0, 0, 0))
        idx.add_entity("e2", (5, 5, 5))
        idx.add_entity("e3", (20, 20, 20))

        results = idx.entities_in_bounds((-1, -1, -1), (10, 10, 10))
        assert len(results) == 2

    def test_update_position(self):
        idx = SpatialIndex()
        idx.add_entity("player", (0, 0, 0))
        assert idx.update_position("player", (10, 10, 10)) is True
        nearest = idx.find_nearest((10, 10, 10))
        assert nearest is not None
        assert nearest.position == (10, 10, 10)

    def test_clear(self):
        idx = SpatialIndex()
        idx.add_entity("e1", (0, 0, 0))
        idx.add_entity("e2", (5, 5, 5))
        assert idx.count == 2
        idx.clear()
        assert idx.count == 0
