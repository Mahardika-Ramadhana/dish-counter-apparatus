import time

from dica.core import config

try:
    import board
    import digitalio
    from adafruit_hx711.analog_in import AnalogIn
    from adafruit_hx711.hx711 import HX711

    HX711_AVAILABLE = True
except ImportError:
    HX711_AVAILABLE = False
    print("Peringatan: adafruit_hx711 tidak ditemukan. Menggunakan mode dummy.")
except NotImplementedError:
    HX711_AVAILABLE = False
    print("Peringatan: Tidak ada GPIO yang didukung. Menggunakan mode dummy.")


class LoadCell:
    def __init__(self):
        self.hx711: HX711 | None = None
        self.channel_a: AnalogIn | None = None
        self.offset = 0.0
        self.scale = 1.0  # Nilai kalibrasi, perlu disesuaikan dengan load cell fisik

    def init_loadcell(self):
        """Inisialisasi HX711."""
        if not HX711_AVAILABLE:
            if getattr(config, "ENVIRONMENT", "development") == "production":
                raise RuntimeError(
                    "❌ BENCANA: Mode Produksi menyala tapi Library adafruit_hx711 / Kabel Timbangan tidak ditemukan! Segera perbaiki hardware!"
                )
            print("Mode dummy aktif untuk Load Cell.")
            return

        try:
            # Gunakan getattr untuk pin dinamis dari konfigurasi
            dt_pin = getattr(board, f"D{config.PIN_LOADCELL_DT}", None)
            sck_pin = getattr(board, f"D{config.PIN_LOADCELL_SCK}", None)

            if dt_pin and sck_pin:
                data = digitalio.DigitalInOut(dt_pin)
                clock = digitalio.DigitalInOut(sck_pin)
                clock.direction = digitalio.Direction.OUTPUT
                self.hx711 = HX711(data, clock)
                self.channel_a = AnalogIn(self.hx711, HX711.CHAN_A_GAIN_128)
                print("HX711 berhasil diinisialisasi.")
                self.tare()
            else:
                print(
                    f"Peringatan: Pin D{config.PIN_LOADCELL_DT} atau D{config.PIN_LOADCELL_SCK} tidak valid."
                )

        except Exception as e:
            print(f"Gagal inisialisasi HX711: {e}")

    def tare(self):
        """Kalibrasi nol (piring kosong) dengan filter noise."""
        if not HX711_AVAILABLE or self.channel_a is None:
            if getattr(config, "ENVIRONMENT", "development") == "production":
                raise RuntimeError(
                    "❌ BENCANA: Gagal melakukan Tare! Mode Produksi menyala tapi hardware timbangan tidak berfungsi!"
                )
            self.offset = 0
            print("Tare selesai (mode dummy).")
            return

        print("Melakukan tare (kalibrasi nol)...")
        samples = []
        for _ in range(15):
            try:
                samples.append(self.channel_a.value)
            except Exception:
                pass
            time.sleep(0.05)

        if samples:
            samples.sort()
            # Buang outlier (nilai ekstrem) jika sampel cukup
            if len(samples) > 4:
                valid_samples = samples[2:-2]
            else:
                valid_samples = samples
            self.offset = sum(valid_samples) / len(valid_samples)
            print("Tare berhasil.")
        else:
            print("Gagal mengambil sampel untuk tare.")

    def read_weight(self) -> float:
        """Baca berat dalam gram dengan median filter dan deadband."""
        if not HX711_AVAILABLE or self.channel_a is None:
            # Dummy fallback yang statis agar layar tidak bergetar dan angka tidak berubah-ubah
            time.sleep(0.5)  # Simulasi jeda baca hardware
            return 235.0

        samples = []
        for _ in range(10):
            try:
                samples.append(self.channel_a.value)
            except Exception as e:
                print(f"[Hardware Fail-Safe] Error baca loadcell: {e}")
            time.sleep(0.05)

        if samples:
            samples.sort()
            # Buang outlier noise listrik
            if len(samples) > 4:
                valid_samples = samples[2:-2]
            else:
                valid_samples = samples
                
            avg_val = sum(valid_samples) / len(valid_samples)
            
            # Jika user belum mengubah scale, gunakan estimasi rata-rata loadcell 5kg (420.0)
            # karena default 1.0 akan membuat noise 10 terbaca 10 gram.
            effective_scale = self.scale if self.scale != 1.0 else 420.0
            
            weight = (avg_val - self.offset) / effective_scale
            
            # Deadband: Abaikan fluktuasi di bawah 5 gram (anggap piring kosong)
            if abs(weight) < 5.0:
                return 0.0
                
            return abs(weight)
        else:
            print("[Hardware Fail-Safe] Kabel timbangan terputus! Mencoba re-inisialisasi HX711...")
            self.init_loadcell()

        return 0.0
