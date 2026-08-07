import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

import dica.utils.wifi_manager as wifi_manager

def test_get_current_ip_hostname_success():
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "192.168.1.10 127.0.0.1"
        mock_run.return_value = mock_result
        
        ip = wifi_manager.get_current_ip()
        assert ip == "192.168.1.10"

def test_get_current_ip_fallback():
    with patch('subprocess.run') as mock_run, \
         patch('dica.utils.wifi_manager.socket.socket') as mock_socket:
        
        mock_result = MagicMock()
        mock_result.stdout = "127.0.0.1"
        mock_run.return_value = mock_result
        
        mock_sock_instance = MagicMock()
        mock_sock_instance.getsockname.return_value = ("10.0.0.5", 12345)
        mock_socket.return_value = mock_sock_instance
        
        ip = wifi_manager.get_current_ip()
        assert ip == "10.0.0.5"

def test_get_current_ip_total_failure():
    with patch('subprocess.run', side_effect=Exception("command failed")), \
         patch('dica.utils.wifi_manager.socket.socket', side_effect=Exception("socket failed")):
        ip = wifi_manager.get_current_ip()
        assert ip == "127.0.0.1"

def test_get_current_ssid_success():
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "no:OtherWifi\nyes:MyWifi\n"
        mock_run.return_value = mock_result
        
        ssid = wifi_manager.get_current_ssid()
        assert ssid == "MyWifi"

def test_get_current_ssid_none():
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "no:OtherWifi\nno:Wifi2\n"
        mock_run.return_value = mock_result
        
        ssid = wifi_manager.get_current_ssid()
        assert ssid == ""

def test_scan_wifi():
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "WifiA:80\nWifiB:60\nWifiA:50\n"
        mock_run.return_value = mock_result
        
        networks = wifi_manager.scan_wifi()
        assert len(networks) == 2
        assert networks[0]['ssid'] == "WifiA"
        assert networks[1]['ssid'] == "WifiB"

def test_scan_wifi_fail():
    with patch('subprocess.run', side_effect=Exception("nmcli missing")):
        networks = wifi_manager.scan_wifi()
        assert len(networks) == 1
        assert "Gagal memindai" in networks[0]['ssid']

def test_connect_wifi_already_connected():
    with patch('dica.utils.wifi_manager.get_current_ssid', return_value="TargetWifi"):
        success, msg = wifi_manager.connect_wifi("TargetWifi", "password123")
        assert success is True
        assert "Sudah terhubung" in msg

def test_connect_wifi_success():
    with patch('dica.utils.wifi_manager.get_current_ssid', return_value="OldWifi"), \
         patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        success, msg = wifi_manager.connect_wifi("TargetWifi", "pass")
        assert success is True
        assert msg == "Berhasil terhubung!"
        mock_run.assert_called_once()

def test_connect_wifi_fail():
    with patch('dica.utils.wifi_manager.get_current_ssid', return_value="OldWifi"), \
         patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Wrong password"
        mock_run.return_value = mock_result
        
        success, msg = wifi_manager.connect_wifi("TargetWifi", "wrongpass")
        assert success is False
        assert msg == "Wrong password"
