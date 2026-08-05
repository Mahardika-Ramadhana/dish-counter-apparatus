import pytest
import sys
import os
import time
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Jika berjalan di headless server (tidak ada GUI/layar), maka lewati tes ini
if not os.environ.get('DISPLAY'):
    pytest.skip("Melewati tes E2E GUI karena $DISPLAY tidak ditemukan (headless).", allow_module_level=True)

import tkinter as tk
from main import App
from database import Database

@pytest.fixture
def mock_app(monkeypatch):
    """Setup Environment E2E dengan Dependency Mocks untuk hardware fisik."""
    monkeypatch.setattr("camera.CameraManager.init_cameras", MagicMock(return_value=True))
    monkeypatch.setattr("camera.CameraManager.capture_frame", MagicMock(return_value=None))
    
    # Gunakan database temporary agar tidak merusak DB produksi
    db_path = "/tmp/test_e2e_db.sqlite"
    if os.path.exists(db_path):
        os.remove(db_path)
    test_db = Database(db_path)
    test_db.init_db()
    
    root = tk.Tk()
    app = App(root)
    app.db = test_db
    
    yield app
    
    # Cleanup setelah E2E test selesai
    app.running = False
    app.on_closing()
    if os.path.exists(db_path):
        os.remove(db_path)

def test_full_transaction_flow(mock_app, monkeypatch):
    """
    Test End-to-End: 
    Letakkan Piring (Mock Weight) -> Klik Deteksi (GUI) -> 
    Proses AI -> Verifikasi Layar -> Konfirmasi (GUI) -> Masuk DB.
    """
    # 1. Kasir menaruh piring (Simulasi 230 gram = 80g Ayam + 150g Nasi)
    mock_app.current_weight = 230.0 
    
    # Mock AI melihat Ayam Goreng
    mock_app.detector.detect = MagicMock(return_value=[
        {'class_name': 'ayam_goreng', 'confidence': 0.99, 'bbox': [10,10,20,20]}
    ])
    
    import numpy as np
    dummy_frame = np.zeros((10, 10, 3), dtype=np.uint8)
    mock_app.frame_queue.put((dummy_frame, None))
    
    # 2. Kasir menekan tombol "DETEKSI & HITUNG" di GUI
    mock_app.trigger_detection()
    
    # Beri waktu AI thread (di background) untuk memproses maksimal 2 detik
    start = time.time()
    while not mock_app.current_detections and time.time() - start < 2.0:
        time.sleep(0.1)
        
    # 3. Verifikasi apa yang muncul di layar kasir (State)
    assert len(mock_app.current_detections) == 2 # 1 Ayam + 1 Nasi yang digenerate oleh Sensor Fusion
    assert mock_app.current_total_price == 15000 # (Ayam 10k + Nasi 5k)
    
    # Mock messagebox agar tes tidak tersangkut oleh popup
    import tkinter.messagebox
    monkeypatch.setattr(tkinter.messagebox, "showinfo", MagicMock())
    
    # 4. Penjual menekan tombol "KONFIRMASI & BAYAR" via Web
    mock_app.konfirmasi_pembayaran_via_web()
    
    # 5. Verifikasi laporan database keuangan
    history = mock_app.db.get_recent_transactions(1)
    assert len(history) == 1
    assert history[0]['total_harga'] == 15000
