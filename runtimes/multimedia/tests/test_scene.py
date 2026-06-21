"""Tests for Scene Manager."""

from ucode4.scene.manager import SceneManager, Scene, SceneObject


class TestSceneObject:
    def test_create_object(self):
        obj = SceneObject(name="Cube", object_type="model")
        assert obj.name == "Cube"
        assert obj.object_type == "model"
        assert obj.position == (0, 0, 0)

    def test_object_roundtrip(self):
        obj = SceneObject(name="Cube", object_type="model", position=(1, 2, 3))
        data = obj.to_dict()
        restored = SceneObject.from_dict(data)
        assert restored.name == "Cube"
        assert restored.object_type == "model"
        assert restored.position == (1, 2, 3)


class TestScene:
    def test_create_scene(self):
        scene = Scene(name="MainScene")
        assert scene.name == "MainScene"
        assert len(scene.objects) == 0

    def test_add_remove_object(self):
        scene = Scene(name="MainScene")
        obj = SceneObject(name="Cube", object_type="model")
        scene.add_object(obj)
        assert len(scene.objects) == 1
        assert scene.remove_object(obj.object_id) is True
        assert len(scene.objects) == 0

    def test_scene_roundtrip(self):
        scene = Scene(name="MainScene")
        scene.add_object(SceneObject(name="Cube", object_type="model"))
        data = scene.to_dict()
        restored = Scene.from_dict(data)
        assert restored.name == "MainScene"
        assert len(restored.objects) == 1


class TestSceneManager:
    def test_create_scene(self):
        mgr = SceneManager()
        scene = mgr.create_scene(name="TestScene", world_id="world-1")
        assert scene.name == "TestScene"
        assert scene.metadata.get("world_id") == "world-1"

    def test_get_scene(self):
        mgr = SceneManager()
        scene = mgr.create_scene(name="TestScene", world_id="world-1")
        retrieved = mgr.get_scene(scene.scene_id)
        assert retrieved is not None
        assert retrieved.name == "TestScene"

    def test_list_scenes_by_world(self):
        mgr = SceneManager()
        mgr.create_scene(name="Scene1", world_id="world-1")
        mgr.create_scene(name="Scene2", world_id="world-1")
        mgr.create_scene(name="Scene3", world_id="world-2")
        assert len(mgr.list_scenes("world-1")) == 2
        assert len(mgr.list_scenes("world-2")) == 1

    def test_add_object_to_scene(self):
        mgr = SceneManager()
        scene = mgr.create_scene(name="TestScene", world_id="world-1")
        obj = mgr.add_object_to_scene(scene.scene_id, "Cube", "model", (1, 2, 3))
        assert obj is not None
        assert obj.name == "Cube"
        assert obj.position == (1, 2, 3)
