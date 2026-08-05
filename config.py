import json
import os

_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'data', 'config.json')

def load_json_config():
    if not os.path.exists(_CONFIG_FILE):
        return {}
    try:
        with open(_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

_json_data = load_json_config()

# Baca dari JSON, jika gagal/tidak ada gunakan default bawaan
HARGA = _json_data.get('harga', {
    'nasi_porsi': 5000,
    'telur': 3000,
    'tahu': 2000,
    'tempe': 2000,
    'ayam_goreng': 10000,
    'sambal': 0
})

BERAT_RATA_RATA_LAUK = _json_data.get('berat_rata_lauk', {
    'telur': 50.0,
    'tahu': 30.0,
    'tempe': 30.0,
    'ayam_goreng': 80.0,
    'sambal': 10.0
})

BERAT_SATU_PORSI_NASI = _json_data.get('berat_satu_porsi_nasi', 150.0)

PIN_LOADCELL_DT = 5
PIN_LOADCELL_SCK = 6
PIN_TOMBOL = 17

CAMERA_IDS = [0, 2]  # 0: Kamera Laptop (Atas), 2: Webcam (Samping)
MODEL_PATH = "model.tflite"
CONFIDENCE_THRESHOLD = 0.5
INPUT_SIZE = (640, 640)
