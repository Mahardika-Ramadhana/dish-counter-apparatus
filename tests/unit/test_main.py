import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from dica.core.app import App

@pytest.fixture
def app_instance():
    with patch('dica.core.app.ObjectDetector'), \
         patch('dica.core.app.CameraManager'), \
         patch('dica.core.app.LoadCell'), \
         patch('dica.core.app.ReceiptPrinter'), \
         patch('dica.core.app.Database'), \
         patch('dica.core.app.start_web_server'):
        
        # Instantiate App without actually starting infinite loops or web server
        # because the loops are started in __init__ we must patch Thread
        with patch('dica.core.app.threading.Thread'):
            app = App()
            return app

def test_validasi_via_web(app_instance):
    items = [{'class_name': 'nasi_porsi', 'harga': 5000}]
    total = 5000
    
    app_instance.validasi_via_web(items, total)
    assert app_instance.transaction_state == 'PAYMENT'
    assert app_instance.validated_items == items
    assert app_instance.validated_total == total

def test_konfirmasi_pembayaran_via_web(app_instance):
    app_instance.transaction_state = 'PAYMENT'
    app_instance.sm.validated_items = [{'class_name': 'nasi_porsi', 'harga': 5000}]
    app_instance.sm.validated_total = 5000
    
    app_instance.konfirmasi_pembayaran_via_web()
    
    assert app_instance.transaction_state == 'IDLE'
    assert len(app_instance.current_detections) == 0
    assert app_instance.current_total_price == 0
    
    # Check if database and printer were called
    app_instance.db.save_transaction.assert_called_once()
    app_instance.printer.print_receipt.assert_called_once()

def test_trigger_detection(app_instance):
    app_instance.transaction_state = 'IDLE'
    app_instance.trigger_detection()
    assert app_instance.transaction_state == 'PROCESSING'
    assert app_instance.snapshot_event.is_set() is True

def test_stop(app_instance):
    app_instance.btn_fisik = MagicMock()
    app_instance.stop()
    assert app_instance.running is False
    app_instance.camera_manager.release_all.assert_called_once()
    app_instance.btn_fisik.close.assert_called_once()

def test_sensor_task_loop(app_instance):
    # Simulasi 1 iterasi loop dengan mengganti running menjadi False setelah 1 panggilan loadcell.read_weight
    def mock_read_weight():
        app_instance.running = False
        return 123.4
    
    app_instance.loadcell.read_weight.side_effect = mock_read_weight
    app_instance.sensor_task()
    assert app_instance.current_weight == 123.4

def test_ai_task_loop(app_instance):
    import numpy as np
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    def mock_queue_get(timeout):
        app_instance.running = False
        return (dummy_frame, None)
    
    app_instance.frame_queue.get = MagicMock(side_effect=mock_queue_get)
    app_instance.detector.detect.return_value = [{'class_name': 'nasi_porsi', 'harga': 5000}]
    app_instance.detector.consolidate_max_count.return_value = [{'class_name': 'nasi_porsi', 'harga': 5000}]
    
    app_instance.ai_task()
    assert app_instance.transaction_state == 'VALIDATION'
    assert app_instance.current_total_price == 5000

def test_camera_task_loop(app_instance):
    def mock_wait(timeout):
        app_instance.running = False
        return True
    
    app_instance.snapshot_event.wait = MagicMock(side_effect=mock_wait)
    import numpy as np
    app_instance.camera_manager.capture_frame.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
    
    app_instance.camera_task()
    
    # Should put frames in queue
    assert not app_instance.frame_queue.empty()

