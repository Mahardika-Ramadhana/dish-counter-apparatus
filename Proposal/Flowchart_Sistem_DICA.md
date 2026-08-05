# Analisis Fungsional

Berikut adalah diagram alir (*flowchart*) fungsional dari sistem DICA yang telah disesuaikan dengan format desain yang Anda berikan.

### Diagram 1. Alur Kalibrasi Cold Start

```mermaid
flowchart LR
    A((Start)) --> B[State : Sistem Terkunci]
    B --> C[Penjual menghubungkan HP ke Web Dashboard DICA]
    C --> D[Taruh piring kosong di atas timbangan]
    D --> E[Penjual menekan tombol kalibrasi timbangan Tare di HP]
    E --> F[State : Sistem Terbuka]
```

---

### Diagram 2. Alur Transaksi

```mermaid
flowchart TD
    %% Define Nodes
    Start((Start))
    Langkah1[Pelanggan mengambil lauk dan nasi di piring]
    Langkah2[Pelanggan menaruh piring di atas DICA]
    Langkah3[Pelanggan menekan tombol untuk mendeteksi lauk dan menghitung harga]
    Langkah4[State: AI memproses gambar]
    Kondisi1{Apakah ada data lauk ?}
    
    ProsesY1[Deteksi jumlah item secara visual]
    ProsesY2[Masukan harga standar lauk rutin Beli porsi]
    ProsesY3[Kalkulasi bukaan lauk lalu di mix2 dengan berat yang countable lauk dulu]
    ProsesY4[Berat sisa untuk menghitung porsi uncountable nasi / sayur]
    CounterHarga[Counter harga total]
    HitungHarga[Hitung harga lauk dan nasi / sayur]
    
    ProsesT1[Tampilkan Hasil deteksi, harga satuan dan harga total ke penjual dan pembeli]
    ProsesT2[Penjual mengecek hasil deteksi dan validasi bersama pembeli]
    ProsesT3[Lakukan Pembayaran menggunakan QR code]
    Selesai((Selesai))

    %% Define Flows (Main Path)
    Start --> Langkah1 --> Langkah2 --> Langkah3 --> Langkah4 --> Kondisi1
    
    %% Flow if "Ya"
    Kondisi1 -- Y1 --> ProsesY1
    ProsesY1 --> ProsesY2 --> ProsesY3 --> ProsesY4 --> HitungHarga --> CounterHarga
    CounterHarga --> Kondisi1
    
    %% Flow if "Tidak"
    Kondisi1 -- Tidak --> ProsesT1
    ProsesT1 --> ProsesT2 --> ProsesT3 --> Selesai
```
