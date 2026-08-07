import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from dica.utils import qris


def test_generate_dynamic_qris():
    # Valid static QRIS format ending in 6304 + 4 chars CRC
    # Format mock: ...010211...5802ID...6304XXXX
    static_qris = "0002010102115204581253033605802ID5914WARTEG BAHARI6007JAKARTA6304A1B2"
    amount = 15000

    dynamic_qris = qris.generate_dynamic_qris(static_qris, amount)

    assert dynamic_qris != static_qris
    # Should change 010211 to 010212
    assert "010212" in dynamic_qris

    # Should insert Tag 54 (amount): 54 + length + amount
    # Length of 15000 is 5, padded to 2 digits is '05'. So "540515000"
    assert "540515000" in dynamic_qris

    # Check it still ends with CRC 4 chars after 6304
    assert "6304" in dynamic_qris
    assert len(dynamic_qris.split("6304")[1]) == 4


def test_generate_dynamic_qris_invalid_format():
    static_qris = "INVALID_QRIS_FORMAT"
    amount = 5000
    dynamic_qris = qris.generate_dynamic_qris(static_qris, amount)

    # If 5802ID is missing, it falls back to return original
    assert dynamic_qris == static_qris
