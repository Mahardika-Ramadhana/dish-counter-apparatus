# Arsitektur Perangkat Keras DICA (Hardware Architecture)

Dokumen ini menguraikan topologi dan koneksi perangkat keras (hardware) yang digunakan dalam sistem DICA (*Dish Counter Apparatus*).

## Diagram Alur Perangkat Keras

```mermaid
flowchart LR
    %% Komponen Input (Sebelah Kiri)
    LoadCell["Load Cell<br>(Sensor Berat)"]
    HX711["Modul<br>HX711"]
    
    Kamera1["Kamera 1<br>(Sudut Kiri)"]
    Kamera2["Kamera 2<br>(Sudut Kanan)"]

    %% Pusat Pemrosesan (Tengah)
    OrangePi["Orange Pi<br>(Pemroses Utama)"]

    %% Komponen Output (Sebelah Kanan)
    RingLight["Lampu<br>Ring Light"]
    LCD35["Layar LCD 3.5 Inch<br>(Display Harga/QRIS)"]
    
    %% Jaringan (Kanan Bawah)
    Hotspot["Hotspot<br>Lokal"]
    Smartphone["Smartphone<br>Penjual"]

    %% --- Jalur Koneksi ---

    %% Timbangan
    LoadCell -- "Sinyal Analog" --> HX711
    HX711 -- "Kabel Jumper<br>(Pin DT & SCK)" --> OrangePi

    %% Kamera (2 Buah)
    Kamera1 -- "Kabel USB" --> OrangePi
    Kamera2 -- "Kabel USB" --> OrangePi

    %% Output Fisik
    OrangePi -- "Kabel Daya<br>USB 5V" --> RingLight
    OrangePi -- "Pin GPIO / SPI" --> LCD35

    %% Output Jaringan
    OrangePi -. "Sinyal WiFi" .-> Hotspot
    Hotspot -. "Akses IP<br>Dashboard" .-> Smartphone
```

## Deskripsi Komponen

1. **Pemroses Utama:** Menggunakan **Orange Pi** (SBC) yang berperan sebagai otak komputasi untuk mengeksekusi model *Artificial Intelligence* (YOLO/TFLite) secara lokal di *Edge*.
2. **Kamera Ganda:** Dua buah kamera USB yang digunakan untuk meminimalkan *blind spot* atau oklusi (makanan saling menumpuk/menutupi).
3. **Sensor Fisik:** *Load cell* yang dihubungkan melalui modul konverter ADC HX711 untuk memberikan umpan balik (validasi stabilitas piring dan berat).
4. **Display:** Menggunakan layar **LCD 3.5 Inch** via GPIO/SPI untuk menampilkan harga total dan kode QRIS kepada pelanggan dengan ringkas dan elegan, menghilangkan ketergantungan pada monitor besar.
5. **Jaringan:** Alat terkoneksi via WiFi Hotspot ke *Smartphone* penjual untuk memonitor dasbor web lokal.
