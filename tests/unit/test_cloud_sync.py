import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from dica.db.cloud_sync import CloudSync


def test_cloud_sync_initialization():
    """Test inisialisasi CloudSync dengan dummy creds."""
    sync = CloudSync("dummy.db", "http://dummy.supabase.co", "dummy_key")
    assert sync.db_lokal == "dummy.db"
    assert sync.client is not None


@patch("sqlite3.connect")
@patch("dica.db.cloud_sync.create_client")
def test_sync_unpushed_transactions(mock_create_client, mock_sqlite_connect):
    """Test fungsi sinkronisasi (mencegah data leakage, menggunakan mock)"""
    # Mock Supabase client
    mock_supabase_instance = MagicMock()
    mock_create_client.return_value = mock_supabase_instance

    # Mock SQLite DB
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_sqlite_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Return 2 transaksi dummy (belum disinkron)
    # Row format: (id, items(json), total_harga, timestamp, status_konfirmasi)
    mock_cursor.fetchall.return_value = [
        (1, '["ayam","nasi"]', 15000, "2026-08-05 10:00:00", "SELESAI"),
        (2, '["tahu"]', 2000, "2026-08-05 10:05:00", "SELESAI"),
    ]

    sync = CloudSync("dummy.db", "http://dummy.supabase.co", "dummy_key")

    # Panggil fungsi sync
    result = sync.sync_unpushed_transactions()

    assert result["status"] == "success"
    assert result["count"] == 2

    # Pastikan data diupsert ke Supabase dengan struktur yang benar
    # payload arg of upsert
    call_args = mock_supabase_instance.table().upsert.call_args[0][0]
    assert len(call_args) == 2
    assert call_args[0]["id_lokal"] == 1
    assert call_args[0]["items"] == ["ayam", "nasi"]
    assert call_args[1]["total_harga"] == 2000
