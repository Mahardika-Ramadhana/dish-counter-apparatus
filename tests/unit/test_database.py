import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from database import Database

@pytest.fixture
def db():
    # Gunakan file temporary agar koneksi terpisah (karena sqlite3.connect(':memory:') membuat DB baru tiap dipanggil)
    db_path = "/tmp/test_db.sqlite"
    if os.path.exists(db_path):
        os.remove(db_path)
    test_db = Database(db_path)
    test_db.init_db()
    yield test_db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_save_and_get_transaction(db):
    detections = [
        {'class_name': 'ayam_goreng', 'confidence': 0.9, 'bbox': [0,0,0,0]},
        {'class_name': 'nasi (1.0 porsi)', 'confidence': 1.0, 'bbox': [0,0,0,0]}
    ]
    
    # Simpan transaksi 15.000 (Ayam 10k + Nasi 5k)
    db.save_transaction(detections, 15000)
    
    # Ambil 5 transaksi terakhir
    recent = db.get_recent_transactions(5)
    
    # Validasi
    assert len(recent) == 1
    assert recent[0]['total_harga'] == 15000
    assert 'ayam_goreng' in recent[0]['items']
    assert 'nasi (1.0 porsi)' in recent[0]['items']
    
def test_empty_database(db):
    recent = db.get_recent_transactions(10)
    assert isinstance(recent, list)
    assert len(recent) == 0
