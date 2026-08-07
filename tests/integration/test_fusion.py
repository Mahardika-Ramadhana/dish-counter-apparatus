import os
import sys

# Setup sys path untuk mengimpor dari root dan src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from dica.core import config


def test_sensor_fusion_weight_subtraction():
    """Menguji logika integrasi berat loadcell dengan deteksi kelas diskrit."""

    # Kasus: Piring berisi 1 Telur (50g) dan 1 Ayam Goreng (80g) dan Nasi
    # Total berat timbangan menunjukkan 310 gram
    current_weight = 310.0

    final_detections = [
        {"class_name": "telur", "confidence": 0.9, "bbox": [0, 0, 0, 0]},
        {"class_name": "ayam_goreng", "confidence": 0.9, "bbox": [0, 0, 0, 0]},
    ]

    # 1. Hitung total berat lauk diskrit
    total_berat_lauk = sum(
        [config.BERAT_RATA_RATA_LAUK.get(d["class_name"], 0) for d in final_detections]
    )
    assert total_berat_lauk == 130.0  # (50g + 80g)

    # 2. Kurangi untuk mendapat estimasi berat Nasi
    berat_nasi = max(0.0, current_weight - total_berat_lauk)
    assert berat_nasi == 180.0

    # 3. Konversi ke porsi nasi (150g = 1 porsi, kelipatan 0.5 terdekat)
    # 180 / 150 = 1.2 -> dibulatkan ke kelipatan 0.5 terdekat = 1.0 porsi
    porsi_nasi = round((berat_nasi / config.BERAT_SATU_PORSI_NASI) * 2) / 2
    assert porsi_nasi == 1.0

    # 4. Kalkulasi harga total
    total_price = sum([config.HARGA.get(d["class_name"], 0) for d in final_detections])
    assert total_price == 13000  # Telur (3000) + Ayam (10000)

    if porsi_nasi > 0:
        total_price += int(porsi_nasi * config.HARGA.get("nasi_porsi", 0))

    assert total_price == 18000  # 13000 + 5000 (1 porsi nasi)
