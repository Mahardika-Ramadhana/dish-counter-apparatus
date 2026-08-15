import time
import board
import digitalio
from adafruit_hx711.analog_in import AnalogIn
from adafruit_hx711.hx711 import HX711

print("=== PROGRAM KALIBRASI TIMBANGAN (HX711) ===")
print("Menghubungkan ke sensor...")

try:
    data = digitalio.DigitalInOut(board.D5)
    data.direction = digitalio.Direction.INPUT
    clock = digitalio.DigitalInOut(board.D6)
    clock.direction = digitalio.Direction.OUTPUT
    hx711 = HX711(data, clock)
    channel_a = AnalogIn(hx711, HX711.CHAN_A_GAIN_128)
except Exception as e:
    print(f"Gagal akses sensor: {e}")
    print("Pastikan Anda sudah mematikan sistem kasir dengan: sudo systemctl stop dica")
    exit(1)

def get_average(samples=20):
    vals = []
    for _ in range(samples):
        vals.append(channel_a.value)
        time.sleep(0.1)
    return sum(vals) / len(vals)

print("\n[LANGKAH 1] KOSONGKAN TIMBANGAN")
input("Pastikan TIDAK ADA BENDA APAPUN di atas timbangan, lalu tekan ENTER...")
print("Mencari titik nol (Tare)...")
offset = get_average(20)
print(f"Titik nol berhasil didapat: {offset}")

print("\n[LANGKAH 2] LETAKKAN BENDA (KALIBRASI BERAT)")
print("Siapkan benda yang Anda TAHU PASTI beratnya.")
print("Contoh: Botol air mineral tanggung (600 gram), atau HP (misal 185 gram).")
berat_asli_str = input("Ketikkan BERAT BENDA TERSEBUT (dalam satuan Gram): ")

try:
    berat_asli = float(berat_asli_str)
except:
    print("Masukkan harus berupa angka! Program berhenti.")
    exit(1)

input(f"Letakkan benda seberat {berat_asli}g tersebut di ATAS TIMBANGAN, lalu tekan ENTER...")
print("Sedang mengukur berat referensi...")
val_beban = get_average(20)
print(f"Nilai Raw dengan beban: {val_beban}")

scale = (val_beban - offset) / berat_asli
print(f"\n=== HASIL KALIBRASI ===")
print(f"Nilai Scale Baru: {scale}")

print("\nMenyimpan nilai kalibrasi secara permanen ke dalam file loadcell.py...")
try:
    with open("src/dica/hardware/loadcell.py", "r") as f:
        code = f.read()
    
    import re
    # Ganti self.scale = ... menjadi nilai baru
    code = re.sub(r"self\.scale\s*=\s*[0-9\.\-]+\s*#.*?kalibrasi", f"self.scale = {scale}  # Nilai kalibrasi otomatis", code)
    
    with open("src/dica/hardware/loadcell.py", "w") as f:
        f.write(code)
    print("[SUCCESS] Timbangan berhasil dikalibrasi!")
except Exception as e:
    print(f"Gagal menyimpan ke file: {e}")

print("\nSelesai! Anda bisa menyalakan mesin kasirnya kembali dengan: sudo systemctl start dica")
