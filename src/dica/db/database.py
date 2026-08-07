import sqlite3
import json
import datetime
import threading
from typing import List, Dict, Any


import os

class Database:
    def __init__(self, db_name="data/transaksi.db"):
        self.db_name = db_name
        self.lock = threading.Lock()

    def init_db(self):
        """Buat tabel transaksi (id, items JSON, total_harga, timestamp, status_konfirmasi)."""
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            items TEXT NOT NULL,
            total_harga INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status_konfirmasi TEXT NOT NULL
        )
        ''')

        conn.commit()
        conn.close()
        print("Database berhasil diinisialisasi.")

    def save_transaction(self, items: List[Dict[str, Any]], total: int):
        """Simpan ke SQLite dengan Thread-Safe Lock."""
        item_names = [item['class_name'] for item in items]
        items_json = json.dumps(item_names)

        with self.lock:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO transaksi (items, total_harga, status_konfirmasi) VALUES (?, ?, ?)",
                (items_json, total, "SELESAI")
            )

            conn.commit()
            conn.close()

        print(f"Transaksi disimpan: {item_names} - Rp{total}")

    def get_recent_transactions(self, limit=10):
        """Ambil riwayat."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, items, total_harga, timestamp FROM transaksi ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()

        conn.close()

        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'items': json.loads(row[1]),
                'total_harga': row[2],
                'timestamp': row[3]
            })

        return results

    def get_all_transactions(self):
        """Ambil semua riwayat transaksi untuk diexport."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, items, total_harga, timestamp FROM transaksi ORDER BY timestamp DESC"
        )
        rows = cursor.fetchall()

        conn.close()

        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'items': json.loads(row[1]),
                'total_harga': row[2],
                'timestamp': row[3]
            })

        return results

    def clear_transactions(self):
        """Hapus semua data transaksi dengan Thread-Safe Lock."""
        with self.lock:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transaksi")
            conn.commit()
            conn.close()
