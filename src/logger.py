import logging
import os
from datetime import datetime

log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs'))
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = os.path.join(log_dir, f"dishcounter_{datetime.now().strftime('%Y-%m-%d')}.log")

# Konfigurasi logging basic
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler() # Tetap tampil di terminal jika dijalankan secara manual
    ]
)

def get_logger(name: str):
    """Fungsi helper untuk mendapatkan logger terstandarisasi untuk modul."""
    return logging.getLogger(name)
