import time
import random
from typing import Optional
import config

try:
    import board
    import digitalio
    from adafruit_hx711.hx711 import HX711
    from adafruit_hx711.analog_in import AnalogIn
    HX711_AVAILABLE = True
except ImportError:
    HX711_AVAILABLE = False
    print("Peringatan: adafruit_hx711 tidak ditemukan. Menggunakan mode dummy.")
except NotImplementedError:
    HX711_AVAILABLE = False
    print("Peringatan: Tidak ada GPIO yang didukung. Menggunakan mode dummy.")

class LoadCell:
    def __init__(self):
        self.hx711: Optional['HX711'] = None
        self.channel_a: Optional['AnalogIn'] = None
        self.offset = 0.0
        self.scale = 1.0 # Nilai kalibrasi, perlu disesuaikan dengan load cell fisik
        
    def init_loadcell(self):
        """Inisialisasi HX711."""
        if not HX711_AVAILABLE:
            print("Mode dummy aktif untuk Load Cell.")
            return

        try:
            # Gunakan getattr untuk pin dinamis dari konfigurasi
            dt_pin = getattr(board, f'D{config.PIN_LOADCELL_DT}', None)
            sck_pin = getattr(board, f'D{config.PIN_LOADCELL_SCK}', None)
            
            if dt_pin and sck_pin:
                data = digitalio.DigitalInOut(dt_pin)
                clock = digitalio.DigitalInOut(sck_pin)
                self.hx711 = HX711(data, clock)
                self.channel_a = AnalogIn(self.hx711, HX711.CHAN_A_GAIN_128)
                print("HX711 berhasil diinisialisasi.")
                self.tare()
            else:
                print(f"Peringatan: Pin D{config.PIN_LOADCELL_DT} atau D{config.PIN_LOADCELL_SCK} tidak valid.")
                
        except Exception as e:
            print(f"Gagal inisialisasi HX711: {e}")

    def tare(self):
        """Kalibrasi nol (piring kosong)."""
        if not HX711_AVAILABLE or self.channel_a is None:
            self.offset = 0
            print("Tare selesai (mode dummy).")
            return

        print("Melakukan tare (kalibrasi nol)...")
        samples = []
        for _ in range(10):
            try:
                samples.append(self.channel_a.value)
            except Exception:
                pass
            time.sleep(0.1)
            
        if samples:
            self.offset = sum(samples) / len(samples)
            print("Tare berhasil.")
        else:
            print("Gagal mengambil sampel untuk tare.")

    def read_weight(self) -> float:
        """Baca berat rata-rata 5 sampel dalam gram."""
        if not HX711_AVAILABLE or self.channel_a is None:
            # Dummy fallback yang statis agar layar tidak bergetar dan angka tidak berubah-ubah
            time.sleep(0.5) # Simulasi jeda baca hardware
            return 235.0

        samples = []
        for _ in range(5):
            try:
                samples.append(self.channel_a.value)
            except Exception as e:
                print(f"[Hardware Fail-Safe] Error baca loadcell: {e}")
            time.sleep(0.1)
            
        if samples:
            avg_val = sum(samples) / len(samples)
            weight = (avg_val - self.offset) / self.scale
            return max(0.0, weight)
        else:
            print("[Hardware Fail-Safe] Kabel timbangan terputus! Mencoba re-inisialisasi HX711...")
            self.init_loadcell()
        
        return 0.0
