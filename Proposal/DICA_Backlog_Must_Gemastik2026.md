# DICA — Backlog Prioritas MUST (Gemastik 2026)
### Fokus: implementasi nyata ±50% dari purwarupa yang dijanjikan di proposal

Story point: **1, 2, 3, 5, 8, 13** (semakin besar = semakin lama pengerjaannya)
Status: ✅ Sudah dikerjakan · ⬜ Belum dikerjakan

---

## 1. Revisi Narasi Proposal — 21 SP
*(murah waktu, tidak butuh hardware, langsung merespons masukan dosen)*

- ⬜ 1.1 Diagram alur kerja umum end-to-end sebelum breakdown teknis — 3 SP
- ⬜ 1.2 Elaborasi Embedded System (software stack, threading, fault-tolerance) — 5 SP
- ⬜ 1.3 Elaborasi IoT distributif (narasi + diagram arsitektur multi-cabang) — 8 SP
- ⬜ 1.4 Sinkronisasi konsistensi antar-bab (Bab D merefleksikan arsitektur baru) — 5 SP

---

## 2. Computer Vision & AI Pipeline — 26 SP
*(inti nilai teknis produk — ini yang paling dites langsung saat demo)*

- ✅ *(baseline)* Dataset awal, training YOLOv8-Nano-seg, export TFLite, logika deteksi
- ⬜ 2.1 Tambah data occlusion (lauk bertumpuk) — 3 SP
- ⬜ 2.2 Retraining dengan dataset baru — 3 SP
- ⬜ 2.3 Evaluasi mAP/precision/recall per kelas lauk — 2 SP
- ⬜ 2.4 Uji ketahanan model pada occlusion tinggi — 3 SP
- ⬜ 2.5 Re-export & benchmark TFLite versi baru — 2 SP
- ⬜ 2.6 Optimasi waktu inferensi agar transaksi < 5 detik konsisten — 3 SP
- ⬜ 2.7 Kalibrasi ulang konversi piksel → cm² — 2 SP
- ⬜ 2.8 Uji akurasi connected component analysis pada tumpukan — 3 SP
- ⬜ 2.9 Tuning threshold sensor fusion (confidence vs berat) — 3 SP
- ⬜ 2.10 Uji kasus edge sensor fusion (berat vs visual tidak sesuai) — 2 SP (digabung ke SP di atas — total tetap 26)

---

## 3. Embedded System — Bagian Wajib Saja — 9 SP
*(cukup yang menjamin alat stabil saat demo, bukan hardening penuh)*

- ✅ *(baseline)* Auto-boot aplikasi kasir + web server + Hotspot Manager
- ⬜ 3.1 Threading/multiprocessing kamera + load cell + LCD paralel tanpa lag — 5 SP
- ⬜ 3.2 Uji stabilitas koneksi HX711 & load cell (noise, drift) — 2 SP
- ⬜ 3.3 Finalisasi kestabilan auto-boot setelah perubahan software — 2 SP

---

## 4. IoT Distributif — Bukti Konsep Saja — 8 SP
*(ini bagian yang membuktikan 50% implementasi nyata dari ide distributif yang diceritakan di narasi — bukan sistem multi-cabang penuh)*

- ✅ *(baseline)* Web dashboard lokal via hotspot (kalibrasi, validasi, QR, unduh CSV)
- ⬜ 4.1 Skema database cloud (Firebase/Supabase/Neon Postgres) — 3 SP
- ⬜ 4.2 Implementasi sync SQLite lokal → cloud (queue-based, retry saat offline) — 5 SP

> Cukup buktikan **1 device berhasil sync ke cloud secara nyata**. Dashboard analitik multi-cabang, autentikasi per-device, dan deteksi anomali cukup ditulis di proposal sebagai "menuju Babak Final."

---

## 5. Purwarupa Fisik Final — 18 SP
*(mengganti representasi jadi komponen fisik asli — ini penentu skor "implementasi nyata")*

- ✅ *(baseline)* Setup representasi (flash HP, botol minum, laptop)
- ⬜ 5.1 Pasang kamera pada stand sesuai desain 3D — 2 SP
- ⬜ 5.2 Pasang ring light final — 2 SP
- ⬜ 5.3 Pasang LCD 5" TFT sungguhan (ganti representasi laptop) — 3 SP
- ⬜ 5.4 Rakit housing/casing alat — 1 SP
- ⬜ 5.5 Kalibrasi load cell dengan berat referensi asli — 2 SP
- ⬜ 5.6 Kalibrasi kamera dengan jarak & sudut final — 3 SP
- ⬜ 5.7 Uji kestabilan alat di atas meja (guncangan, gesekan) — 2 SP
- ⬜ 5.8 Uji dasar sambungan kabel — 3 SP

---

## 6. Testing & Kesiapan Demo — 23 SP
*(gerbang terakhir — tanpa ini, semua epic di atas tidak terbukti bekerja)*

- ✅ *(baseline)* Integrasi end-to-end pertama (hardware+GUI+dashboard+AI jadi satu siklus)
- ⬜ 6.1 Uji 50-100 transaksi simulasi variasi lauk & porsi — 5 SP
- ⬜ 6.2 Hitung metrik akhir (akurasi, error berat, waktu transaksi) — 3 SP
- ⬜ 6.3 Uji di pencahayaan tidak ideal — 3 SP
- ⬜ 6.4 Uji di permukaan meja tidak rata/stabil — 2 SP
- ⬜ 6.5 Uji dengan gangguan jaringan (hotspot padat pengunjung) — 3 SP
- ⬜ 6.6 Latihan skenario demo end-to-end dengan tim — 3 SP
- ⬜ 6.7 Siapkan skenario cadangan jika sensor gagal (fallback manual) — 2 SP
- ⬜ 6.8 Rekam & edit video showcase sistem bekerja — 2 SP

---

## Ringkasan

| # | Fokus | Story Point |
|---|---|---|
| 1 | Revisi Narasi Proposal | 21 |
| 2 | Computer Vision & AI Pipeline | 26 |
| 3 | Embedded System (wajib saja) | 9 |
| 4 | IoT Distributif (bukti konsep) | 8 |
| 5 | Purwarupa Fisik Final | 18 |
| 6 | Testing & Kesiapan Demo | 23 |
| **Total** | | **105 SP** |

**Urutan pengerjaan yang disarankan:**
1. **Paralel dari sekarang:** #1 (Narasi) + #2 (CV) — dua-duanya tidak saling bergantung
2. **Begitu progres #2 mulai stabil:** #3 (Embedded) + #4 (IoT) bisa jalan bersamaan
3. **Begitu komponen fisik tersedia:** #5 (Purwarupa Fisik)
4. **Paling akhir, setelah semua siap:** #6 (Testing) sebagai validasi menyeluruh sebelum Babak Final

**Definition of Done untuk klaim "50% implementasi nyata":** sebelum submit, pastikan minimal:
- Model CV benar-benar berjalan real-time di Raspberry Pi asli (bukan simulasi laptop)
- Load cell & kamera fisik asli terpasang dan terkalibrasi (bukan representasi botol/laptop)
- Minimal 1 kali sync data lokal → cloud berhasil dibuktikan (bukan cuma didesain di kertas)
- Video/demo langsung menunjukkan siklus transaksi utuh dari piring diletakkan sampai QRIS muncul
