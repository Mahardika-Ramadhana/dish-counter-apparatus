import os
import sys
from unittest.mock import MagicMock, patch

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from dica.hardware.camera import CameraManager


def test_camera_init_success():
    with patch("dica.hardware.camera.cv2.VideoCapture") as mock_cap:
        # Mock that both cameras open successfully
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_cap.return_value = mock_instance

        manager = CameraManager()
        assert manager.init_cameras() is True
        assert len(manager.cameras) == 2  # According to config.CAMERA_IDS which is usually [0, 1]


def test_camera_init_fail():
    with patch("dica.hardware.camera.cv2.VideoCapture") as mock_cap:
        # Mock that camera fails to open
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = False
        mock_cap.return_value = mock_instance

        manager = CameraManager()
        assert manager.init_cameras() is False
        assert len(manager.cameras) == 0


def test_capture_frame_success():
    with patch("dica.hardware.camera.cv2.VideoCapture") as mock_cap:
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True

        # Mock read() returning a dummy numpy array
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_instance.read.return_value = (True, dummy_frame)

        mock_cap.return_value = mock_instance

        manager = CameraManager()
        manager.init_cameras()

        # Test taking frame from cam_id 0
        frame = manager.capture_frame(0)

        assert frame is not None
        assert frame.shape == (480, 640, 3)


def test_capture_frame_read_fail():
    with patch("dica.hardware.camera.cv2.VideoCapture") as mock_cap:
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (False, None)

        mock_cap.return_value = mock_instance

        manager = CameraManager()
        manager.init_cameras()

        # Failsafe will trigger, so it will attempt to reconnect. We mock the second connect as failing too.
        frame = manager.capture_frame(0)
        assert frame is None
