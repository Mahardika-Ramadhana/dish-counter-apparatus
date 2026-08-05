import pytest
import sys
import os

# Masukkan folder src ke dalam Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from detector import ObjectDetector

def test_consolidate_max_count():
    detector = ObjectDetector()
    
    # Simulasi Kamera 1 (Atas) mendeteksi 2 Tahu dan 1 Tempe
    det1 = [
        {'class_name': 'tahu', 'confidence': 0.9, 'bbox': [10,10,20,20]},
        {'class_name': 'tahu', 'confidence': 0.8, 'bbox': [30,30,40,40]},
        {'class_name': 'tempe', 'confidence': 0.9, 'bbox': [50,50,60,60]}
    ]
    
    # Simulasi Kamera 2 (Samping) mendeteksi 1 Tahu dan 2 Tempe (karena sudut pandang berbeda)
    det2 = [
        {'class_name': 'tahu', 'confidence': 0.95, 'bbox': [10,10,20,20]},
        {'class_name': 'tempe', 'confidence': 0.85, 'bbox': [50,50,60,60]},
        {'class_name': 'tempe', 'confidence': 0.88, 'bbox': [70,70,80,80]}
    ]
    
    # Penggabungan Max Count
    result = detector.consolidate_max_count(det1, det2)
    
    tahu_count = sum(1 for d in result if d['class_name'] == 'tahu')
    tempe_count = sum(1 for d in result if d['class_name'] == 'tempe')
    
    # Harus mengambil jumlah maksimum: 2 Tahu (dari kamera 1) dan 2 Tempe (dari kamera 2)
    assert tahu_count == 2
    assert tempe_count == 2

def test_dummy_detection():
    detector = ObjectDetector()
    assert detector.is_dummy == True
    
    # Meskipun tidak ada gambar asli, dummy detection harus mengembalikan list (bisa kosong atau berisi 1 item)
    result = detector.detect(None)
    assert isinstance(result, list)
