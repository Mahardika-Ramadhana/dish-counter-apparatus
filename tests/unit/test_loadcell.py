import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from loadcell import LoadCell

@patch('loadcell.HX711_AVAILABLE', False)
def test_loadcell_dummy_mode():
    """Test pembacaan dalam mode dummy (fail-safe atau no-hardware)"""
    lc = LoadCell()
    lc.init_loadcell()
    
    # Harusnya return nilai dummy statis 235.0
    weight = lc.read_weight()
    assert weight == 235.0

import loadcell

def test_loadcell_hardware_failsafe():
    """Test auto-reconnect fail-safe saat kabel putus (raise Exception)"""
    # Force hardware mode for this test
    original_hx711 = loadcell.HX711_AVAILABLE
    loadcell.HX711_AVAILABLE = True
    try:
        lc = loadcell.LoadCell()
        
        class MockChannel:
            @property
            def value(self):
                raise Exception("Kabel Putus")
                
        lc.channel_a = MockChannel()
        
        # Pastikan inisialisasi ulang dipanggil saat gagal terus
        with patch.object(lc, 'init_loadcell') as mock_init, patch('loadcell.time.sleep', return_value=None):
            weight = lc.read_weight()
            
            # Karena 5 sampel error semua, harusnya memanggil init_loadcell
            mock_init.assert_called_once()
            assert weight == 0.0
    finally:
        loadcell.HX711_AVAILABLE = original_hx711

from unittest.mock import PropertyMock
