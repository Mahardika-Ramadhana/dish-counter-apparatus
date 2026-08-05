import sqlite3
import json
from supabase import create_client, Client
from typing import Dict, Any, List

class CloudSync:
    def __init__(self, db_lokal: str = "transaksi.db", supabase_url: str = "", supabase_key: str = ""):
        self.db_lokal = db_lokal
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        
        # Inisialisasi klien Supabase hanya jika kredensial tersedia
        self.client: Client | None = None
        if self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                print(f"[CloudSync] Gagal inisialisasi Supabase client: {e}")

    def is_configured(self) -> bool:
        """Mengecek apakah kredensial Supabase sudah dikonfigurasi."""
        return self.client is not None

    def sync_unpushed_transactions(self) -> Dict[str, Any]:
        """
        Membaca data dari SQLite lokal dan melakukan upsert ke Supabase Cloud.
        Menggunakan id_lokal sebagai referensi unik di cloud.
        """
        if not self.is_configured():
            return {"status": "error", "message": "Supabase belum dikonfigurasi (URL/Key kosong)"}
            
        try:
            # Ambil semua data transaksi dari SQLite
            conn = sqlite3.connect(self.db_lokal)
            cursor = conn.cursor()
            cursor.execute("SELECT id, items, total_harga, timestamp, status_konfirmasi FROM transaksi")
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return {"status": "success", "message": "Tidak ada transaksi untuk disinkronkan", "count": 0}

            # Format data untuk payload Supabase
            payload = []
            for row in rows:
                payload.append({
                    "id_lokal": row[0],
                    "items": json.loads(row[1]),
                    "total_harga": row[2],
                    "timestamp": row[3],
                    "status_konfirmasi": row[4],
                    "device_id": "DICA-PI-01"
                })

            # Upsert ke tabel transaksi_cloud (menggunakan id_lokal sebagai kunci upsert jika dikonfigurasi di Supabase)
            # Karena ini MVP, kita gunakan insert biasa, error duplicate key akan di-ignore jika id_lokal diset unik
            # Metode terbaik Supabase UPSERT memerlukan parameter on_conflict
            res = self.client.table("transaksi_cloud").upsert(
                payload, on_conflict="id_lokal"
            ).execute()
            
            return {
                "status": "success", 
                "message": f"Berhasil sinkronisasi {len(payload)} transaksi ke Supabase Cloud",
                "count": len(payload)
            }

        except Exception as e:
            return {"status": "error", "message": f"Gagal sinkronisasi: {str(e)}"}
