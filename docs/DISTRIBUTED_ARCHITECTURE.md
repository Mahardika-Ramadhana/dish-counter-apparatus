# Arsitektur Terdistribusi DICA (Edge-to-Cloud)

Dokumen ini menjelaskan topologi Komputasi Terdistribusi *Edge-to-Cloud* yang diimplementasikan pada sistem DICA (*Dish Counter Apparatus*).

## Diagram Alur

```mermaid
flowchart BT
    %% Lapisan Edge di bagian bawah
    subgraph LapisanEdge ["Lapisan Edge (Banyak Cabang UMKM / Edge Nodes)"]
        direction LR
        Cabang1["DICA Cabang Jakarta<br>(Inferensi AI & DB Lokal)"]
        Cabang2["DICA Cabang Surabaya<br>(Inferensi AI & DB Lokal)"]
        Cabang3["DICA Cabang Bandung<br>(Inferensi AI & DB Lokal)"]
        CabangN["DICA Cabang ke-N...<br>(Inferensi AI & DB Lokal)"]
    end

    %% Jaringan Transmisi di tengah
    Internet(("Jaringan Internet<br>(Pengiriman Payload JSON Ringan)"))

    %% Panah mengarah ke atas dari Cabang ke Internet
    Cabang1 -->|Sinkronisasi| Internet
    Cabang2 -->|Sinkronisasi| Internet
    Cabang3 -->|Sinkronisasi| Internet
    CabangN -->|Sinkronisasi| Internet

    %% Lapisan Cloud di atas Internet
    subgraph LapisanCloud ["Lapisan Cloud (Centralized Server)"]
        Supabase[("Supabase<br>(Pangkalan Data Utama)")]
        QRIS["Payment Gateway API<br>(Verifikasi Pembayaran Nasional)"]
        Supabase <--> QRIS
    end

    %% Panah mengarah ke atas dari Internet ke Cloud
    Internet ==>|Agregasi Ribuan Transaksi| Supabase

    %% Akses Pemilik di posisi paling atas
    subgraph AksesPemilik ["Akses Pemilik Waralaba (Franchise Owner)"]
        Dashboard["Dasbor Analitik Web<br>(Pantau Performa Seluruh Cabang)"]
        Mobile["Aplikasi Mobile<br>(Notifikasi Stok Lauk Real-Time)"]
    end

    %% Panah mengarah ke atas dari Cloud ke Akses Pemilik
    Supabase ==>|Distribusi Big Data| Dashboard
    Supabase -.->|Push Notification| Mobile
```

## Cara Kerja Implementasi Terdistribusi (Manajemen Skalabilitas Multi-Cabang)

Untuk memastikan DICA siap diimplementasikan secara komersial dalam skala besar tanpa menyebabkan kelebihan beban (*bottleneck*) pada jaringan internet UMKM, sistem ini dibangun menggunakan topologi Komputasi Terdistribusi *Edge-to-Cloud*. Melalui arsitektur ini, beban kerja sistem dipisahkan ke dalam dua lapisan utama:

1. **Lapisan *Edge* (Perangkat Lokal di Cabang):** Bertanggung jawab secara eksklusif atas beban komputasi berat (*Heavy Compute*) seperti akuisisi citra statis (pengambilan foto), pra-pemrosesan piksel, inferensi AI (TFLite/YOLO), dan kendali aktuator (printer/timbangan). Setiap mesin DICA beroperasi secara otonom di lokasi masing-masing cabang.
2. **Lapisan *Cloud* (Server Pusat/Supabase):** Bertanggung jawab atas beban analitik ringan (*Light Compute*), agregasi data penjualan dari seluruh cabang, manajemen autentikasi QRIS, dan penyajian *Dashboard* pemantauan untuk pemilik usaha.

Dengan pemisahan logika terdistribusi ini, latensi deteksi di meja kasir dapat ditekan hingga di bawah 1 detik tanpa menyumbat *bandwidth* internet warteg. Hal ini dikarenakan setelah transaksi selesai, mesin *Edge* hanya mengirimkan *payload* data transaksi berukuran kilobyte (berupa *string* JSON hasil rekap inferensi), bukan mengunggah *file* foto beresolusi tinggi ke server.

Keunggulan utama dari implementasi desentralisasi ini adalah kemampuannya menampung ratusan mesin DICA di bawah satu ekosistem pangkalan data terpusat (*Centralized Cloud Database*). Seluruh data transaksi dari berbagai cabang geografis (misalnya: Cabang A di Surabaya, Cabang B di Malang) akan diagregasi secara *real-time*. Hasilnya, pemilik usaha waralaba dapat memantau performa penjualan, ketersediaan lauk, dan pola konsumsi pelanggan dari seluruh cabangnya melalui satu antarmuka dasbor analitik tunggal. Topologi ini tidak hanya menciptakan ekosistem perangkat cerdas yang efisien, tetapi juga memberikan landasan *Big Data* yang krusial untuk pemantauan ekonomi dan ketahanan pangan tingkat akar rumput.
