import json
import os

_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "config.json")


def load_json_config():
    # Jika file tidak ada, JANGAN gunakan default! Langsung matikan program dan protes.
    if not os.path.exists(_CONFIG_FILE):
        raise FileNotFoundError(
            f"❌ ERROR: File {_CONFIG_FILE} TIDAK DITEMUKAN! Mesin kasir menolak menyala sebelum daftar harga diisi."
        )

    try:
        with open(_CONFIG_FILE) as f:
            return json.load(f)
    except Exception as e:
        # Jika file ada tapi isinya rusak (salah ketik koma/tanda kutip)
        raise ValueError(
            f"❌ ERROR: Format config.json rusak! Tolong perbaiki penulisan JSON-nya. Detail: {e}"
        )


_json_data = load_json_config()

# Cek apakah bagian 'harga' ada di dalam JSON
if "harga" not in _json_data:
    raise ValueError(
        "❌ ERROR: DAFTAR HARGA KOSONG! Mesin kasir menolak menyala. Tolong isi bagian 'harga' di config.json."
    )
HARGA = _json_data["harga"]

# Cek apakah bagian 'berat_rata_lauk' ada di dalam JSON
if "berat_rata_lauk" not in _json_data:
    raise ValueError(
        "❌ ERROR: DATA BERAT LAUK KOSONG! Tolong isi bagian 'berat_rata_lauk' di config.json."
    )
BERAT_RATA_RATA_LAUK = _json_data["berat_rata_lauk"]

# Cek apakah bagian 'berat_satu_porsi_nasi' ada di dalam JSON
if "berat_satu_porsi_nasi" not in _json_data:
    raise ValueError(
        "❌ ERROR: BERAT PORSI NASI KOSONG! Tolong isi bagian 'berat_satu_porsi_nasi' di config.json."
    )
BERAT_SATU_PORSI_NASI = _json_data["berat_satu_porsi_nasi"]

# Cek apakah bagian 'berat_satu_porsi_sambal' ada di dalam JSON
if "berat_satu_porsi_sambal" not in _json_data:
    raise ValueError(
        "❌ ERROR: BERAT PORSI SAMBAL KOSONG! Sambal adalah barang tak terhitung, tolong isi 'berat_satu_porsi_sambal' di config.json."
    )
BERAT_SATU_PORSI_SAMBAL = _json_data["berat_satu_porsi_sambal"]

ENVIRONMENT = _json_data.get("environment", "development")
DISPLAY_MODE = _json_data.get("display_mode", "HEADLESS")

PIN_LOADCELL_DT = 5
PIN_LOADCELL_SCK = 6
PIN_TOMBOL = 17

CAMERA_IDS = [0, 2]  # 0: Kamera Laptop (Atas), 2: Webcam (Samping)
MODEL_PATH = "../../../models/yolo11n-seg.tflite"
CONFIDENCE_THRESHOLD = 0.5
INPUT_SIZE = (640, 640)

# Kredensial Supabase Cloud Sync
SUPABASE_URL = _json_data.get("supabase_url", "")
SUPABASE_KEY = _json_data.get("supabase_key", "")
API_KEY = _json_data.get("api_key", "gemastik2026_dica_secure")
