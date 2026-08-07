import cv2
from typing import List, Optional
import dica.core.config as config


class CameraManager:
    def __init__(self):
        self.cameras = {}

    def init_cameras(self) -> bool:
        """Buka dua webcam pakai OpenCV VideoCapture."""
        success = True
        for cam_id in config.CAMERA_IDS:
            cap = cv2.VideoCapture(cam_id)
            if cap.isOpened():
                self.cameras[cam_id] = cap
                print(f"Kamera {cam_id} berhasil diinisialisasi.")
            else:
                print(f"Peringatan: Gagal membuka kamera {cam_id}.")
                success = False
        return success

    def capture_frame(self, cam_id: int):
        """Ambil frame dari camera_id tertentu dengan fail-safe auto-reconnect."""
        if cam_id in self.cameras:
            ret, frame = self.cameras[cam_id].read()
            if ret:
                return frame
            else:
                # Fail-safe: Kamera mungkin terputus, coba reconnect
                print(
                    f"[Hardware Fail-Safe] Kamera {cam_id} terputus! Mencoba auto-reconnect...")
                self.cameras[cam_id].release()
                import time
                time.sleep(1)  # Beri waktu OS mendeteksi ulang USB
                new_cap = cv2.VideoCapture(cam_id)
                if new_cap.isOpened():
                    self.cameras[cam_id] = new_cap
                    print(
                        f"[Hardware Fail-Safe] Kamera {cam_id} berhasil tersambung kembali.")
                else:
                    print(
                        f"[Hardware Fail-Safe] Gagal menyambung ulang kamera {cam_id}.")
        return None

    def get_frame_for_display(self, cam_id: int = 0):
        """Ambil frame untuk preview GUI."""
        frame = self.capture_frame(cam_id)
        if frame is not None:
            # Convert BGR (OpenCV) to RGB (Tkinter/Pillow)
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def release_all(self):
        """Lepas semua kamera."""
        for cap in self.cameras.values():
            cap.release()
