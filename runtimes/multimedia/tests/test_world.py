"""Tests for World Engine."""

from ucode4.world.engine import WorldEngine, World, Dimension


class TestDimension:
    def test_create_dimension(self):
        dim = Dimension(name="test", band=400)
        assert dim.name == "test"
        assert dim.band == 400
        assert dim.bounds == {"width": 100.0, "height": 100.0, "depth": 100.0}

    def test_dimension_roundtrip(self):
        dim = Dimension(name="test", band=400, width=50, height=30, depth=20)
        data = dim.to_dict()
        restored = Dimension.from_dict(data)
        assert restored.name == "test"
        assert restored.band == 400
        assert restored.width == 50
        assert restored.height == 30
        assert restored.depth == 20


class TestWorld:
    def test_create_world(self):
        dim = Dimension(name="test_dim", band=400)
        world = World(name="MyWorld", dimension=dim)
        assert world.name == "MyWorld"
        assert world.dimension.band == 400
        assert len(world.scenes) == 0
        assert len(world.objects) == 0

    def test_add_scene_and_object(self):
        dim = Dimension(name="test_dim", band=400)
        world = World(name="MyWorld", dimension=dim)
        world.add_scene({"name": "Scene1", "objects": []})
        world.add_object({"name": "Cube", "type": "model"})
        assert len(world.scenes) == 1
        assert len(world.objects) == 1

    def test_world_roundtrip(self):
        dim = Dimension(name="test_dim", band=400)
        world = World(name="MyWorld", dimension=dim)
        world.add_scene({"name": "Scene1"})
        data = world.to_dict()
        restored = World.from_dict(data)
        assert restored.name == "MyWorld"
        assert restored.dimension.band == 400
        assert len(restored.scenes) == 1


class TestWorldEngine:
    def test_create_world(self):
        engine = WorldEngine()
        world = engine.create_world(name="TestWorld", band=400)
        assert world.name == "TestWorld"
        assert world.world_id in [w.world_id for w in engine.list_worlds()]

    def test_get_world(self):
        engine = WorldEngine()
        world = engine.create_world(name="TestWorld")
        retrieved = engine.get_world(world.world_id)
        assert retrieved is not None
        assert retrieved.name == "TestWorld"

    def test_delete_world(self):
        engine = WorldEngine()
        world = engine.create_world(name="TestWorld")
        assert engine.delete_world(world.world_id) is True
        assert engine.get_world(world.world_id) is None

    def test_list_worlds(self):
        engine = WorldEngine()
        assert len(engine.list_worlds()) == 0
        engine.create_world(name="World1")
        engine.create_world(name="World2")
        assert len(engine.list_worlds()) == 2

    def test_engine_roundtrip(self):
        engine = WorldEngine()
        engine.create_world(name="World1", band=400)
        engine.create_world(name="World2", band=500)
        data = engine.to_dict()
        restored = WorldEngine.from_dict(data)
        assert len(restored.list_worlds()) == 2
