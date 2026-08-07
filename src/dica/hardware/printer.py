import datetime
import logging

try:
    from escpos.exceptions import USBNotFoundError
    from escpos.printer import Usb

    PRINTER_AVAILABLE = True
except ImportError:
    PRINTER_AVAILABLE = False
except Exception:
    PRINTER_AVAILABLE = False

logger = logging.getLogger("ThermalPrinter")


class ReceiptPrinter:
    def __init__(self, idVendor=0x04B8, idProduct=0x0E28):
        self.printer = None
        self.idVendor = idVendor
        self.idProduct = idProduct
        self.enabled = PRINTER_AVAILABLE

    def init_printer(self):
        if not self.enabled:
            logger.warning("Pustaka python-escpos tidak tersedia. Pencetakan struk dilewati.")
            return False

        try:
            # Sesuaikan idVendor dan idProduct sesuai model printer thermal USB (misal Epson TM-T82)
            self.printer = Usb(self.idVendor, self.idProduct, timeout=0, in_ep=0x81, out_ep=0x03)
            logger.info(
                f"Printer thermal USB terhubung (Vendor: {hex(self.idVendor)}, Product: {hex(self.idProduct)})"
            )
            return True
        except USBNotFoundError:
            logger.error("Printer Thermal USB tidak ditemukan! Periksa koneksi kabel.")
            self.printer = None
            return False
        except Exception as e:
            logger.error(f"Gagal menginisialisasi printer: {e}")
            self.printer = None
            return False

    def print_receipt(self, items, total_price):
        if not self.enabled or self.printer is None:
            # Fallback: log to console if printer offline
            logger.warning("Printer offline. Melewatkan cetak struk.")
            return False

        try:
            self.printer.set(align="center", bold=True, text_type="B")
            self.printer.text("WARTEG DICA MASA DEPAN\n")
            self.printer.set(align="center", bold=False)
            self.printer.text("Jl. Ketintang, Surabaya\n")
            self.printer.text("================================\n")

            self.printer.set(align="left")
            self.printer.text(f"Tanggal: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.printer.text("--------------------------------\n")

            # Group items by name to count quantity
            item_counts = {}
            for item in items:
                name = item["class_name"]
                item_counts[name] = item_counts.get(name, 0) + 1

            for name, qty in item_counts.items():
                price = 0
                for item in items:
                    if item["class_name"] == name:
                        price = item.get("harga", 0)
                        break

                subtotal = qty * price
                self.printer.text(f"{name}\n")
                self.printer.text(f"  {qty} x Rp{price:,} = Rp{subtotal:,}\n".replace(",", "."))

            self.printer.text("--------------------------------\n")
            self.printer.set(align="right", bold=True)
            self.printer.text(f"TOTAL: Rp{total_price:,}\n".replace(",", "."))

            self.printer.set(align="center", bold=False)
            self.printer.text("================================\n")
            self.printer.text("Terima Kasih!\n")
            self.printer.text("Silakan Nikmati Hidangan Anda\n")

            self.printer.cut()
            logger.info("Struk berhasil dicetak.")
            return True

        except Exception as e:
            logger.error(f"Gagal mencetak struk: {e}")
            return False
