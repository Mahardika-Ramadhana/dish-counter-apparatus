import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from dica.hardware.display import HeadlessDisplay, LCD16x2Display, TFTDisplay, get_display


def test_get_display():
    assert isinstance(get_display("HEADLESS"), HeadlessDisplay)
    assert isinstance(get_display("LCD"), LCD16x2Display)
    assert isinstance(get_display("TFT"), TFTDisplay)
    assert isinstance(get_display("unknown"), HeadlessDisplay)


@patch("dica.hardware.display.logger")
def test_headless_display(mock_logger):
    disp = HeadlessDisplay()
    disp.init_display()
    mock_logger.info.assert_called_with("[DISPLAY] Headless mode initialized.")

    disp.show_welcome()
    mock_logger.info.assert_called_with("[DISPLAY] SILAKAN LETAKKAN MAKANAN ANDA")

    disp.show_total(5000)
    mock_logger.info.assert_called_with("[DISPLAY] Total Belanja: Rp5000")

    disp.show_items([1, 2], 5000)
    mock_logger.info.assert_called_with("[DISPLAY] Items: 2 pcs | Total: Rp5000")

    disp.cleanup()


@patch("dica.hardware.display.logger")
def test_lcd_display(mock_logger):
    disp = LCD16x2Display()
    disp.init_display()
    mock_logger.info.assert_called_with("[DISPLAY] Mencoba inisialisasi LCD 16x2 via I2C...")

    disp.show_welcome()
    mock_logger.info.assert_called_with("[LCD] DICA KASIR | Siap Digunakan")

    disp.show_total(5000)
    mock_logger.info.assert_called_with("[LCD] TOTAL: | Rp 5000")

    disp.show_items([1, 2], 5000)
    mock_logger.info.assert_called_with("[LCD] TOTAL: | Rp 5000")

    disp.cleanup()


@patch("dica.hardware.display.logger")
def test_tft_display(mock_logger):
    disp = TFTDisplay()
    disp.init_display()
    mock_logger.info.assert_called_with("[DISPLAY] Inisialisasi Layar TFT Interaktif (GUI)...")

    disp.show_welcome()
    mock_logger.info.assert_called_with("[TFT] Menampilkan UI Selamat Datang")

    disp.show_total(5000)
    mock_logger.info.assert_called_with("[TFT] Menampilkan UI Total: Rp5000")

    disp.show_items([1, 2], 5000)
    mock_logger.info.assert_called_with("[TFT] Menampilkan Daftar Lauk & QR Dinamis. Total: Rp5000")

    disp.cleanup()
