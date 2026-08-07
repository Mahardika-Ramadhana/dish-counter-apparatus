import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from dica.hardware.printer import ReceiptPrinter


def test_printer_init_disabled():
    with patch("dica.hardware.printer.PRINTER_AVAILABLE", False):
        printer = ReceiptPrinter()
        assert printer.init_printer() is False


def test_printer_init_success():
    with (
        patch("dica.hardware.printer.PRINTER_AVAILABLE", True),
        patch("dica.hardware.printer.Usb", create=True),
    ):
        printer = ReceiptPrinter()
        assert printer.init_printer() is True
        assert printer.printer is not None


def test_printer_print_receipt_disabled():
    printer = ReceiptPrinter()
    printer.enabled = False
    assert printer.print_receipt([], 0) is False


def test_printer_print_receipt_success():
    with (
        patch("dica.hardware.printer.PRINTER_AVAILABLE", True),
        patch("dica.hardware.printer.Usb", create=True),
    ):
        printer = ReceiptPrinter()
        printer.init_printer()

        printer.printer = MagicMock()
        items = [{"class_name": "nasi_porsi", "harga": 5000}]
        assert printer.print_receipt(items, 5000) is True
        printer.printer.cut.assert_called_once()
