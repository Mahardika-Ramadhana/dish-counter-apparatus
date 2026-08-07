from typing import Any

from dica.core.logger import get_logger
from dica.db.database import Database
from dica.hardware.printer import ReceiptPrinter

logger = get_logger("StateMachine")


class TransactionState:
    IDLE = "IDLE"
    PROCESSING = "PROCESSING"
    VALIDATION = "VALIDATION"
    PAYMENT = "PAYMENT"


class StateMachine:
    def __init__(self, db: Database, printer: ReceiptPrinter):
        self.db = db
        self.printer = printer
        self.state = TransactionState.IDLE
        self.auto_validate = False

        self.current_detections: list[dict[str, Any]] = []
        self.current_total_price: int = 0
        self.current_weight: float = 0.0

        self.validated_items: list[dict[str, Any]] = []
        self.validated_total: int = 0

    def trigger_processing(self) -> bool:
        """Transisi dari IDLE ke PROCESSING. True jika berhasil."""
        if self.state == TransactionState.IDLE:
            self.state = TransactionState.PROCESSING
            logger.info("State berubah ke PROCESSING.")
            return True
        return False

    def finish_processing(self, detections: list[dict[str, Any]], total_price: int):
        """Transisi dari PROCESSING ke VALIDATION atau PAYMENT (jika auto_validate)."""
        self.current_detections = detections
        self.current_total_price = total_price

        if self.auto_validate:
            self.validated_items = detections
            self.validated_total = total_price
            self.state = TransactionState.PAYMENT
            logger.info("Auto-validasi aktif, transaksi lanjut ke PAYMENT.")
        else:
            self.state = TransactionState.VALIDATION
            logger.info("Deteksi selesai. Menunggu validasi kasir di layar Web.")

    def cancel_processing(self):
        """Membatalkan PROCESSING jika terjadi error."""
        if self.state == TransactionState.PROCESSING:
            self.state = TransactionState.IDLE
            logger.warning("Pemrosesan dibatalkan. Kembali ke IDLE.")

    def validate_transaction(self, items: list[dict[str, Any]], total: int):
        """Transisi dari VALIDATION ke PAYMENT."""
        self.validated_items = items
        self.validated_total = total
        self.state = TransactionState.PAYMENT
        logger.info(f"Validasi via Web selesai. Total tagihan: Rp{total}")

    def confirm_payment(self) -> bool:
        """Menyelesaikan pembayaran, mencetak struk, menyimpan ke DB, lalu kembali ke IDLE."""
        if self.state != TransactionState.PAYMENT:
            return False

        logger.info(f"Pembayaran diterima: Rp{self.validated_total}. Menyimpan ke Database...")
        self.db.save_transaction(self.validated_items, self.validated_total)
        self.printer.print_receipt(self.validated_items, self.validated_total)

        self._reset()
        logger.info("Transaksi selesai. Sistem kembali ke mode IDLE.")
        return True

    def _reset(self):
        self.current_detections = []
        self.current_total_price = 0
        self.validated_items = []
        self.validated_total = 0
        self.state = TransactionState.IDLE

    def update_weight(self, weight: float):
        """Update sensor berat terkini."""
        self.current_weight = weight
