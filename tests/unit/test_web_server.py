import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from flask import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from dica.api.web_server import create_app
from dica.core import config


@pytest.fixture
def mock_app():
    # Mocking main.py App object
    app_mock = MagicMock()
    app_mock.transaction_state = "IDLE"
    app_mock.current_total_price = 0
    app_mock.current_detections = [{"class_name": "nasi_porsi", "harga": 5000}]
    app_mock.current_weight = 150.0
    app_mock.auto_validate = False
    app_mock.detector.has_occlusion = False
    return app_mock


@pytest.fixture
def client(mock_app):
    app = create_app(mock_app)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client, mock_app


def test_api_status(client):
    cli, mock_main = client
    response = cli.get("/api/status")
    assert response.status_code == 200
    data = json.loads(response.data)

    assert data["state"] == "IDLE"
    assert data["total_price"] == 0
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "nasi_porsi"
    assert data["weight"] == 150.0


def test_api_validate_valid_data(client):
    cli, mock_main = client
    payload = {"items": [{"name": "nasi_porsi", "price": 5000}, {"name": "telur", "price": 3000}]}
    response = cli.post(
        "/api/validate", json=payload, headers={"Authorization": f"Bearer {config.API_KEY}"}
    )
    assert response.status_code == 200

    # Memastikan fungsi validasi_via_web dipanggil oleh backend
    mock_main.validasi_via_web.assert_called_once()
    args, _ = mock_main.validasi_via_web.call_args
    assert len(args[0]) == 2  # 2 items
    assert args[1] == 8000  # total price


def test_api_validate_invalid_negative_price(client):
    cli, mock_main = client
    payload = {"items": [{"name": "ayam_goreng", "price": -10000}]}
    response = cli.post(
        "/api/validate", json=payload, headers={"Authorization": f"Bearer {config.API_KEY}"}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["status"] == "error"
    assert data["message"] == "Harga tidak valid"


def test_api_confirm_success(client):
    cli, mock_main = client
    mock_main.transaction_state = "PAYMENT"  # Only confirmable during PAYMENT

    response = cli.post("/api/confirm", headers={"Authorization": f"Bearer {config.API_KEY}"})
    assert response.status_code == 200
    mock_main.konfirmasi_pembayaran_via_web.assert_called_once()


def test_api_confirm_fail_not_payment(client):
    cli, mock_main = client
    mock_main.transaction_state = "IDLE"  # Should reject

    response = cli.post("/api/confirm", headers={"Authorization": f"Bearer {config.API_KEY}"})
    # According to current logic, it returns 200 with error JSON
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "error"
    mock_main.konfirmasi_pembayaran_via_web.assert_not_called()


def test_api_tare(client):
    cli, mock_main = client
    response = cli.post("/api/tare", headers={"Authorization": f"Bearer {config.API_KEY}"})
    assert response.status_code == 200
    mock_main.loadcell.tare.assert_called_once()


def test_api_toggle_auto(client):
    cli, mock_main = client
    mock_main.auto_validate = False
    response = cli.post("/api/toggle_auto", headers={"Authorization": f"Bearer {config.API_KEY}"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["auto_validate"] is True
    assert mock_main.auto_validate is True


def test_api_transactions(client):
    cli, mock_main = client
    mock_main.db.get_all_transactions.return_value = [{"id": 1, "total_harga": 5000}]
    response = cli.get("/api/transactions")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]["id"] == 1


def test_api_export_transactions(client):
    cli, mock_main = client
    mock_main.db.get_all_transactions.return_value = [
        {"id": 1, "timestamp": "2023", "items": ["Nasi"], "total_harga": 5000}
    ]
    response = cli.get("/api/export_transactions")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"ID Transaksi" in response.data
    assert b"Nasi" in response.data


def test_api_clear_transactions(client):
    cli, mock_main = client
    response = cli.post(
        "/api/clear_transactions", headers={"Authorization": f"Bearer {config.API_KEY}"}
    )
    assert response.status_code == 200
    mock_main.db.clear_transactions.assert_called_once()


def test_route_pages(client):
    cli, mock_main = client
    assert cli.get("/").status_code == 200
    assert cli.get("/customer").status_code == 200
    assert cli.get("/laporan").status_code == 200


def test_api_qr_code(client):
    cli, mock_main = client
    response = cli.get("/api/qr")
    assert response.status_code == 200
    assert response.mimetype == "image/png"


def test_api_sync_cloud(client):
    cli, mock_main = client
    with patch("dica.api.web_server.CloudSync") as mock_cloud:
        mock_instance = MagicMock()
        mock_instance.sync_unpushed_transactions.return_value = {"status": "success"}
        mock_cloud.return_value = mock_instance

        response = cli.post(
            "/api/sync_cloud", headers={"Authorization": f"Bearer {config.API_KEY}"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
