"""Tests for Camera System."""

from ucode4.camera.system import CameraSystem, Camera


class TestCamera:
    def test_create_camera(self):
        cam = Camera(name="MainCam", position=(0, 0, 10))
        assert cam.name == "MainCam"
        assert cam.position == (0, 0, 10)

    def test_move_to(self):
        cam = Camera(name="MainCam")
        cam.move_to(5, 10, 15)
        assert cam.position == (5, 10, 15)

    def test_look_at(self):
        cam = Camera(name="MainCam")
        cam.look_at(1, 2, 3)
        assert cam.target == (1, 2, 3)

    def test_zoom(self):
        cam = Camera(name="MainCam", position=(0, 0, 10))
        cam.zoom(0.5)
        assert cam.position[2] == 5.0  # zoomed in toward target

    def test_camera_roundtrip(self):
        cam = Camera(name="MainCam", position=(1, 2, 3), fov=90)
        data = cam.to_dict()
        restored = Camera.from_dict(data)
        assert restored.name == "MainCam"
        assert restored.position == (1, 2, 3)
        assert restored.fov == 90


class TestCameraSystem:
    def test_create_camera(self):
        system = CameraSystem()
        cam = system.create_camera(name="MainCam")
        assert cam.name == "MainCam"
        assert system.active_camera is not None

    def test_set_active(self):
        system = CameraSystem()
        cam1 = system.create_camera(name="Cam1")
        cam2 = system.create_camera(name="Cam2")
        assert system.set_active(cam2.camera_id) is True
        assert system.active_camera is not None
        assert system.active_camera.name == "Cam2"

    def test_delete_camera(self):
        system = CameraSystem()
        cam = system.create_camera(name="MainCam")
        assert system.delete_camera(cam.camera_id) is True
        assert system.get_camera(cam.camera_id) is None
