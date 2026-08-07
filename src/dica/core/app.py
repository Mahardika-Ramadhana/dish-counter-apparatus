import queue
import threading
import time

import numpy as np

from dica.ai.detector import ObjectDetector
from dica.api.web_server import start_web_server
from dica.core import config
from dica.core.logger import get_logger
from dica.core.state_machine import StateMachine
from dica.db.database import Database
from dica.hardware.camera import CameraManager
from dica.hardware.loadcell import LoadCell
from dica.hardware.printer import ReceiptPrinter

logger = get_logger("MainAppHeadless")

try:
    from gpiozero import Button

    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logger.warning("gpiozero tidak ditemukan. Tombol fisik GPIO tidak aktif.")
except Exception as e:
    GPIO_AVAILABLE = False
    logger.error(f"Peringatan GPIO: {e}")


class App:
    def __init__(self):
        logger.info("Menginisialisasi sistem DICA (HEADLESS MODE)...")
        self.db = Database()
        self.db.init_db()

        self.camera_manager = CameraManager()
        self.camera_manager.init_cameras()

        self.loadcell = LoadCell()
        self.loadcell.init_loadcell()

        self.printer = ReceiptPrinter()
        self.printer.init_printer()

        self.detector = ObjectDetector()
        self.detector.load_model()

        self.sm = StateMachine(self.db, self.printer)

        self.btn_fisik = None
        if GPIO_AVAILABLE:
            try:
                self.btn_fisik = Button(config.PIN_TOMBOL, pull_up=True)
                self.btn_fisik.when_pressed = self.trigger_detection
                logger.info("Tombol fisik GPIO berhasil diinisialisasi.")
            except Exception as e:
                logger.error(f"Gagal inisialisasi tombol GPIO: {e}")

        self.last_raw_frame_bgr = None
        self.last_drawn_frame_bgr = None

        self.running = True
        self.frame_queue = queue.Queue(maxsize=1)
        self.snapshot_event = threading.Event()

        logger.info("Memulai pemrosesan paralel (Threading) dengan CPU Core Pinning...")
        self.cam_thread = threading.Thread(target=self.camera_task, name="CamThread", daemon=True)
        self.ai_thread = threading.Thread(target=self.ai_task, name="AIThread", daemon=True)
        self.sensor_thread = threading.Thread(
            target=self.sensor_task, name="SensorThread", daemon=True
        )

        self.cam_thread.start()
        self.ai_thread.start()
        self.sensor_thread.start()

        # Mulai Web Server Penjual
        logger.info("Memulai Web Server Penjual di background (Core 0)...")
        # Flask berjalan di thread utama/web_thread (akan kita pin ke Core 0 di dalam fungsinya atau biarkan default OS)
        try:
            import os

            os.sched_setaffinity(0, {0})
            logger.info("Main Process (Flask Web Server) dipin ke Core 0")
        except (AttributeError, OSError) as e:
            logger.warning(f"CPU Pinning Core 0 gagal (Bukan Linux/Root): {e}")

        self.web_thread = threading.Thread(target=start_web_server, args=(self,), daemon=True)
        self.web_thread.start()

    @property
    def transaction_state(self):
        return self.sm.state

    @transaction_state.setter
    def transaction_state(self, val):
        self.sm.state = val

    @property
    def current_detections(self):
        return self.sm.current_detections

    @property
    def current_total_price(self):
        return self.sm.current_total_price

    @property
    def current_weight(self):
        return self.sm.current_weight

    @property
    def validated_items(self):
        return self.sm.validated_items

    @property
    def validated_total(self):
        return self.sm.validated_total

    @property
    def auto_validate(self):
        return self.sm.auto_validate

    @auto_validate.setter
    def auto_validate(self, val):
        self.sm.auto_validate = val

    def camera_task(self):
        try:
            import os

            os.sched_setaffinity(0, {1})
            logger.info("Camera Worker dipin ke Core 1")
        except (AttributeError, OSError):
            pass

        while self.running:
            if not self.snapshot_event.wait(timeout=0.1):
                continue

            self.snapshot_event.clear()
            logger.info("Snapshot event dipicu. Mengambil frame statis (Discrete dual-frame)...")

            # Flush buffer OpenCV untuk mendapatkan gambar paling baru
            for _ in range(4):
                self.camera_manager.capture_frame(config.CAMERA_IDS[0])
            frame_atas = self.camera_manager.capture_frame(config.CAMERA_IDS[0])

            frame_samping = None
            if len(config.CAMERA_IDS) > 1:
                for _ in range(4):
                    self.camera_manager.capture_frame(config.CAMERA_IDS[1])
                frame_samping = self.camera_manager.capture_frame(config.CAMERA_IDS[1])

            if frame_atas is not None:
                self.last_raw_frame_bgr = frame_atas.copy()

                if not self.frame_queue.empty():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                self.frame_queue.put((frame_atas, frame_samping))
            else:
                logger.error("Gagal mengambil snapshot dari kamera utama!")
                if self.transaction_state == "PROCESSING":
                    self.transaction_state = "IDLE"

    def trigger_detection(self):
        if self.sm.trigger_processing():
            logger.info("Deteksi dipicu (via Tombol/Web). Memicu Snapshot...")
            self.snapshot_event.set()

    def ai_task(self):
        try:
            import os

            os.sched_setaffinity(0, {3})
            logger.info("AI Inference Worker dipin ke Core 3")
        except (AttributeError, OSError):
            pass

        while self.running:
            try:
                # Blokir thread hingga frame tersedia di antrean
                frames = self.frame_queue.get(timeout=0.1)
                frame_atas, frame_samping = frames

                logger.info("YOLOv8 mulai memproses frame (Snapshot mode)...")
                det_atas = self.detector.detect(frame_atas)
                atas_annotated = self.detector.last_annotated_frame

                det_samping = (
                    self.detector.detect(frame_samping) if frame_samping is not None else []
                )
                # samping_annotated = self.detector.last_annotated_frame

                final_detections = self.detector.consolidate_max_count(det_atas, det_samping)
                total_price = sum([config.HARGA.get(d["class_name"], 0) for d in final_detections])

                for d in final_detections:
                    d["harga"] = config.HARGA.get(d["class_name"], 0)

                self.sm.finish_processing(final_detections, total_price)

                if atas_annotated is not None:
                    self.last_drawn_frame_bgr = atas_annotated
                else:
                    self.last_drawn_frame_bgr = (
                        frame_atas.copy()
                        if frame_atas is not None
                        else np.zeros((480, 640, 3), dtype=np.uint8)
                    )

            except queue.Empty:
                pass  # Lanjutkan menunggu
            except Exception as e:
                logger.error(f"Error saat inferensi AI: {e}")
                self.sm.cancel_processing()

    def sensor_task(self):
        try:
            import os

            os.sched_setaffinity(0, {2})
            logger.info("Sensor Loadcell Worker dipin ke Core 2")
        except (AttributeError, OSError):
            pass

        while self.running:
            try:
                weight = self.loadcell.read_weight()
                self.sm.update_weight(weight)
            except Exception as e:
                logger.error(f"Error membaca Loadcell: {e}")
                time.sleep(1)
            # Sensor timbangan cukup dibaca 2x sedetik untuk hemat CPU
            time.sleep(0.5)

    def validasi_via_web(self, validated_items, validated_total):
        self.sm.validate_transaction(validated_items, validated_total)

    def konfirmasi_pembayaran_via_web(self):
        if self.sm.confirm_payment():
            self.last_drawn_frame_bgr = None

    def stop(self):
        logger.info("Sinyal berhenti diterima. Mematikan aplikasi Headless...")
        self.running = False
        time.sleep(0.5)
        self.camera_manager.release_all()
        if self.btn_fisik:
            self.btn_fisik.close()


if __name__ == "__main__":
    app = App()
    try:
        logger.info("=== MESIN KASIR DICA BERJALAN DI BACKGROUND ===")
        logger.info("Buka browser di HP/Laptop dan ketik: http://[IP_ORANGE_PI]:5000")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        app.stop()
