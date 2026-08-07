import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from dica.db.database import Database


@pytest.fixture
def db():
    db_path = "/tmp/test_dica.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    test_db = Database(db_path)
    test_db.init_db()
    yield test_db
    if os.path.exists(db_path):
        os.remove(db_path)


def test_database_init(db):
    conn = sqlite3.connect(db.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transaksi'")
    assert cursor.fetchone() is not None
    conn.close()


def test_save_and_get_transaction(db):
    items = [{"class_name": "nasi_porsi"}, {"class_name": "ayam_goreng"}]
    total = 15000
    db.save_transaction(items, total)

    transactions = db.get_recent_transactions(10)
    assert len(transactions) == 1
    assert transactions[0]["total_harga"] == 15000
    assert "nasi_porsi" in transactions[0]["items"]
    assert "ayam_goreng" in transactions[0]["items"]


def test_clear_transactions(db):
    db.save_transaction([{"class_name": "nasi_porsi"}], 5000)
    assert len(db.get_all_transactions()) == 1

    db.clear_transactions()
    assert len(db.get_all_transactions()) == 0
