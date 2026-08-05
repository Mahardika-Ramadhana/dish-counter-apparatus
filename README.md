# Dish Counter Apparatus
Sistem Kasir Otomatis berbasis Computer Vision dan Sensor Fusion untuk UMKM Prasmanan.

## Prasyarat
Sistem ini dirancang untuk berjalan pada OS Linux modern seperti **Raspberry Pi OS (Bookworm/Trixie) 64-bit**.

### Instalasi Sistem Dasar & UV
Pastikan sistem Raspberry Pi Anda memiliki `git` dan manajer paket super cepat `uv`:
```bash
sudo apt update && sudo apt install git -y
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

## Instalasi Project (Sangat Cepat dengan UV)

1. **Kloning Kode:**
```bash
git clone https://github.com/Mahardika-Ramadhana/dish-counter-apparatus.git
cd dish-counter-apparatus
```

2. **Buat Virtual Environment & Install Semua Library Otomatis:**
Dengan `uv`, pembuatan ruang isolasi dan instalasi puluhan pustaka AI (termasuk OpenCV dan AI Edge LiteRT) akan selesai dalam hitungan detik.
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Cara Menjalankan Aplikasi
Setiap kali Anda ingin menyalakan mesin kasir cerdas ini, pastikan Anda berada di folder proyek, mengaktifkan `venv`, dan menggunakan perintah `run.sh` agar semua konfigurasi terbaca dengan sempurna:

```bash
cd ~/dish-counter-apparatus
source .venv/bin/activate
./run.sh
```

## Setup Perangkat Keras (Hardware)
1. **Webcam USB:** Pastikan dicolokkan ke *port* USB. Jika gagal mendeteksi kamera, periksa apakah file `/dev/video0` muncul di sistem.
2. **Modul HX711 (Timbangan):** 
   - Pin `DT` sambungkan ke GPIO Pin 5.
   - Pin `SCK` sambungkan ke GPIO Pin 6.
   - Sambungkan VCC ke 5V/3.3V dan GND ke Ground.

## Troubleshooting
- **Tidak Tampil Layar Penuh (Pop-up salah ukuran):** Sistem antarmuka dikalibrasi ketat untuk layar *touchscreen* berukuran 5-inch (resolusi 800x480). Jika dijalankan di monitor besar, GUI akan menempati batas 800x480 di pojok kiri atas.
- **Kamera Gelap / Crash:** Coba tutup aplikasi lain yang mungkin sedang memakai kamera, atau cabut-colok kabel USB kamera.
- **Timbangan Menunjukkan Angka Negatif/Ngawur:** Pastikan sel beban (*load cell*) dipasang dengan tanda panah menghadap ke bawah, lalu kalibrasi ulang nilainya di dalam modul kode kalibrasi.