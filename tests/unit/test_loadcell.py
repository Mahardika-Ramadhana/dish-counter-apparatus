import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from dica.hardware.loadcell import LoadCell

def test_loadcell_init_success():
    with patch('dica.hardware.loadcell.HX711_AVAILABLE', True), \
         patch('dica.hardware.loadcell.board'), \
         patch('dica.hardware.loadcell.digitalio'), \
         patch('dica.hardware.loadcell.HX711') as mock_hx, \
         patch('dica.hardware.loadcell.AnalogIn'):
        
        lc = LoadCell()
        lc.init_loadcell()
        assert lc.hx711 is not None

def test_loadcell_init_fail():
    with patch('dica.hardware.loadcell.HX711_AVAILABLE', True), \
         patch('dica.hardware.loadcell.board'), \
         patch('dica.hardware.loadcell.digitalio.DigitalInOut', side_effect=Exception("Hardware Error")):
        lc = LoadCell()
        lc.init_loadcell()
        assert lc.hx711 is None

def test_loadcell_get_weight():
    with patch('dica.hardware.loadcell.HX711_AVAILABLE', True), \
         patch('dica.hardware.loadcell.board'), \
         patch('dica.hardware.loadcell.digitalio'), \
         patch('dica.hardware.loadcell.HX711'), \
         patch('dica.hardware.loadcell.AnalogIn'):
        
        lc = LoadCell()
        lc.init_loadcell()
        
        # Mocking AnalogIn value
        lc.channel_a = MagicMock()
        lc.channel_a.value = 155.5
        lc.offset = 0
        lc.scale = 1.0
        
        weight = lc.read_weight()
        assert weight == 155.5

def test_loadcell_tare():
    with patch('dica.hardware.loadcell.HX711_AVAILABLE', True), \
         patch('dica.hardware.loadcell.board'), \
         patch('dica.hardware.loadcell.digitalio'), \
         patch('dica.hardware.loadcell.HX711'), \
         patch('dica.hardware.loadcell.AnalogIn'):
        
        lc = LoadCell()
        lc.init_loadcell()
        
        lc.channel_a = MagicMock()
        lc.channel_a.value = 10.0
        
        lc.tare()
        assert lc.offset == 10.0

def test_loadcell_init_prod_error(monkeypatch):
    import dica.core.config as config
    import dica.hardware.loadcell as loadcell
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    monkeypatch.setattr(loadcell, 'HX711_AVAILABLE', False)
    lc = LoadCell()
    with pytest.raises(RuntimeError):
        lc.init_loadcell()

def test_loadcell_init_dummy(monkeypatch):
    import dica.hardware.loadcell as loadcell
    monkeypatch.setattr(loadcell, 'HX711_AVAILABLE', False)
    lc = LoadCell()
    lc.init_loadcell()
    assert lc.hx711 is None

def test_loadcell_invalid_pins(monkeypatch):
    import dica.hardware.loadcell as loadcell
    import dica.core.config as config
    monkeypatch.setattr(loadcell, 'HX711_AVAILABLE', True)
    monkeypatch.setattr(config, 'PIN_LOADCELL_DT', '999') # Invalid pin
    with patch('dica.hardware.loadcell.board') as mock_board:
        delattr(mock_board, 'D999')
        lc = LoadCell()
        lc.init_loadcell()
        assert lc.hx711 is None

def test_tare_prod_error(monkeypatch):
    import dica.core.config as config
    import dica.hardware.loadcell as loadcell
    monkeypatch.setattr(config, 'ENVIRONMENT', 'production')
    monkeypatch.setattr(loadcell, 'HX711_AVAILABLE', False)
    lc = LoadCell()
    with pytest.raises(RuntimeError):
        lc.tare()

def test_tare_dummy(monkeypatch):
    import dica.hardware.loadcell as loadcell
    monkeypatch.setattr(loadcell, 'HX711_AVAILABLE', False)
    lc = LoadCell()
    lc.tare()
    assert lc.offset == 0

def test_tare_exception():
    with patch('dica.hardware.loadcell.HX711_AVAILABLE', True), \
         patch('dica.hardware.loadcell.board'), \
         patch('dica.hardware.loadcell.digitalio'), \
         patch('dica.hardware.loadcell.HX711'), \
         patch('dica.hardware.loadcell.AnalogIn'):
        
        lc = LoadCell()
        lc.init_loadcell()
        lc.channel_a = MagicMock()
        # Menggunakan PropertyMock untuk mock attribute .value
        type(lc.channel_a).value = PropertyMock(side_effect=Exception("Read fail"))
        lc.offset = 123.0
        
        lc.tare()
        # Jika gagal total, offset tidak berubah
        assert lc.offset == 123.0

def test_read_weight_dummy(monkeypatch):
    import dica.hardware.loadcell as loadcell
    monkeypatch.setattr(loadcell, 'HX711_AVAILABLE', False)
    lc = LoadCell()
    val = lc.read_weight()
    assert val == 235.0

def test_read_weight_exceptions():
    with patch('dica.hardware.loadcell.HX711_AVAILABLE', True), \
         patch('dica.hardware.loadcell.board'), \
         patch('dica.hardware.loadcell.digitalio'), \
         patch('dica.hardware.loadcell.HX711'), \
         patch('dica.hardware.loadcell.AnalogIn'):
        
        lc = LoadCell()
        lc.init_loadcell()
        
        lc.channel_a = MagicMock()
        type(lc.channel_a).value = PropertyMock(side_effect=Exception("Hardware Fail-Safe"))
        
        # Test total failure fallback
        with patch.object(lc, 'init_loadcell') as mock_init:
            weight = lc.read_weight()
            assert weight == 0.0
            mock_init.assert_called_once()
