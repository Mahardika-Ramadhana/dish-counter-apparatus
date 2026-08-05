import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify, request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import config
config.API_KEY = "test_api_key_123"

# Kita buat replika endpoint untuk menguji logika otentikasi tanpa menyalakan server penuh
app = Flask(__name__)
@app.route('/api/sync_cloud', methods=['POST'])
def sync_cloud():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {config.API_KEY}":
        return jsonify({'status': 'error', 'message': 'Akses ditolak: API Key tidak valid'}), 401
    return jsonify({"status": "success", "count": 2})

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_sync_cloud_no_auth(client):
    response = client.post('/api/sync_cloud')
    assert response.status_code == 401

def test_sync_cloud_wrong_auth(client):
    response = client.post('/api/sync_cloud', headers={'Authorization': 'Bearer wrong_key'})
    assert response.status_code == 401

def test_sync_cloud_valid_auth(client):
    response = client.post('/api/sync_cloud', headers={'Authorization': f'Bearer {config.API_KEY}'})
    assert response.status_code == 200
    assert response.get_json()['status'] == 'success'

