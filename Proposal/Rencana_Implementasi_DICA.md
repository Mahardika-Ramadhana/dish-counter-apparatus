## F. Rencana Implementasi dan Pengembangan Pengerjaan

### Yang telah dikerjakan

*Progres aktual hingga tanggal submit (24 Juli):*

*   **Setup Environment & Pengujian Awal Komponen Hardware:** 
    Sistem berhasil dikonfigurasi menggunakan arsitektur *embedded* Raspberry Pi. Komponen visual (Kamera Webcam) telah terkalibrasi dan siap digunakan. Sistem operasi juga telah dikonfigurasi untuk menjalankan aplikasi kasir dan *Web Server* lokal secara otomatis (Auto-Boot) beserta kapabilitas *Hotspot Manager* agar penjual dapat langsung memantau alat lewat HP tanpa koneksi internet eksternal.
*   **Pengumpulan & Pelabelan Dataset:** 
    Dataset citra lauk dan piring telah dikumpulkan dalam berbagai kondisi pencahayaan. Anotasi dilakukan menggunakan teknik *Semantic Segmentation* (pemetaan piksel) alih-alih *Bounding Box* konvensional, untuk meningkatkan akurasi estimasi area.
*   **Hasil Training Model Awal:** 
    Model *Computer Vision* (YOLOv8-seg) tahap awal telah selesai dilatih dan berhasil diekspor menjadi format TensorFlow Lite (TFLite). Optimasi ini terbukti sangat krusial agar model AI dapat berjalan lancar (*real-time inference*) langsung di atas CPU Raspberry Pi tanpa memerlukan akselerator GPU tambahan.
*   **Implementasi Logika Deteksi AI:** 
    Telah dibangun algoritma cerdas berbasis *Computer Vision*. Sistem AI membaca bentuk *masking* dari hasil *Semantic Segmentation* untuk mengenali jenis makanan sekaligus mengekstraksi luas area pikselnya guna melakukan estimasi porsi secara presisi.
*   **Hasil Integrasi & Pengujian End-to-End:** 
    Seluruh subsistem (Hardware, GUI Layar Sentuh, Web Dashboard Penjual, dan AI) telah terintegrasi penuh menjadi satu siklus transaksi utuh. *Flow* sistem yang diuji mencakup: penguncian layar untuk alur SOP, deteksi harga otomatis, layar validasi nirkabel via HP penjual, hingga pemunculan QRIS dinamis untuk pembayaran pelanggan, beserta penyimpanan riwayat transaksi ke database lokal.

### Yang akan dikerjakan (menuju Babak Final)

*   Integrasi sensor berat digital (Loadcell HX711) ke dalam sistem dan penerapan algoritma *Sensor Fusion* fisik-visual untuk mencapai akurasi estimasi porsi/berat tingkat tinggi melampaui sekadar deteksi kamera.
*   Peningkatan akurasi model melalui penambahan dataset dan *fine-tuning* lanjutan, khususnya untuk mengatasi skenario tumpang tindih (*occlusion*) makanan ekstrem.
*   Implementasi fitur ekspor/pemindahan basis data transaksi lokal langsung ke *smartphone* penjual secara *offline* melalui jaringan *Hotspot* alat. Mekanisme ini dirancang untuk keperluan audit sekaligus otomatis mengosongkan penyimpanan (*storage*) Raspberry Pi.
*   Mekanisme pembaruan model AI dan daftar harga secara jarak jauh (*Over-The-Air / OTA Updates*) dengan validasi dan *rollback* otomatis.
*   Gladi bersih pengujian ketahanan alat pada kondisi yang menyerupai *venue* demo (pencahayaan, stabilitas getaran meja, dsb.), mengingat Babak Final mewajibkan demo langsung secara *live*.
*   Perluasan daftar kelas lauk dan sayur yang dapat dikenali oleh sistem secara otomatis.
