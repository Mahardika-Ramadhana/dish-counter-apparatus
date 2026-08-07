from abc import ABC, abstractmethod

from dica.core.logger import get_logger

logger = get_logger("DisplayManager")


class BaseDisplay(ABC):
    @abstractmethod
    def init_display(self):
        pass

    @abstractmethod
    def show_welcome(self):
        pass

    @abstractmethod
    def show_total(self, total: int):
        pass

    @abstractmethod
    def show_items(self, items: list, total: int):
        pass

    @abstractmethod
    def cleanup(self):
        pass


class HeadlessDisplay(BaseDisplay):
    """Opsi A: Tanpa layar khusus. Hanya menampilkan log sistem."""

    def init_display(self):
        logger.info("[DISPLAY] Headless mode initialized.")

    def show_welcome(self):
        logger.info("[DISPLAY] SILAKAN LETAKKAN MAKANAN ANDA")

    def show_total(self, total: int):
        logger.info(f"[DISPLAY] Total Belanja: Rp{total}")

    def show_items(self, items: list, total: int):
        logger.info(f"[DISPLAY] Items: {len(items)} pcs | Total: Rp{total}")

    def cleanup(self):
        pass


class LCD16x2Display(BaseDisplay):
    """Opsi C: Layar LCD 16x2 via I2C."""

    def __init__(self):
        self.lcd = None

    def init_display(self):
        logger.info("[DISPLAY] Mencoba inisialisasi LCD 16x2 via I2C...")
        try:
            # Placeholder untuk smbus / RPLCD
            pass
        except Exception as e:
            logger.error(f"[DISPLAY] Gagal inisiasi LCD: {e}")

    def show_welcome(self):
        logger.info("[LCD] DICA KASIR | Siap Digunakan")
        # if self.lcd: self.lcd.write_string("DICA KASIR\nSiap Digunakan")

    def show_total(self, total: int):
        logger.info(f"[LCD] TOTAL: | Rp {total}")
        # if self.lcd: self.lcd.write_string(f"TOTAL:\nRp {total}")

    def show_items(self, items: list, total: int):
        self.show_total(total)

    def cleanup(self):
        pass


class TFTDisplay(BaseDisplay):
    """Opsi B: Layar TFT Interaktif (PyGame/Tkinter)."""

    def init_display(self):
        logger.info("[DISPLAY] Inisialisasi Layar TFT Interaktif (GUI)...")
        # Placeholder untuk PyGame init

    def show_welcome(self):
        logger.info("[TFT] Menampilkan UI Selamat Datang")

    def show_total(self, total: int):
        logger.info(f"[TFT] Menampilkan UI Total: Rp{total}")

    def show_items(self, items: list, total: int):
        logger.info(f"[TFT] Menampilkan Daftar Lauk & QR Dinamis. Total: Rp{total}")

    def cleanup(self):
        pass


def get_display(mode: str) -> BaseDisplay:
    if mode.upper() == "LCD":
        return LCD16x2Display()
    elif mode.upper() == "TFT":
        return TFTDisplay()
    else:
        return HeadlessDisplay()
