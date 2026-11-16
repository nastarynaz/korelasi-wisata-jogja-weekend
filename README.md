# Ritme Wisata Jogja

**Apakah kawasan wisata Jogja lebih aktif saat akhir pekan?** Studi kasus kapanewon yang memiliki destinasi terdokumentasi sebelum Desember 2021.

| Anggota | NIM |
|---|---|
| Muhammad Khoirunas | 24/533373/TK/59083 |
| Aulia Nur Fajri Tri Anggoro | 24/535054/TK/59327 |
| Muhammad Farrel Alghazy | 24/540589/TK/60022 |
| Wangsit Nursyahada | 24/545092/TK/60594 |
| Naufal Dzaky | 24/543697/TK/60431 |

## Menjalankan

[Buka Colab](https://colab.research.google.com/drive/1DvzX-nuuoy03t1u9p99IQd4ZRJotZYlm). Notebook mandiri membaca Sheets publik tanpa login. Setiap bagian menampilkan kode, penjelasan, dan hasil; sepuluh grafik tersimpan langsung dalam notebook. Tidak ada unduhan ZIP otomatis.

Lokal: pasang `requirements-tourism.txt` pada lingkungan Python, lalu jalankan `./run_all.sh`. Kode analisis yang terlihat pada notebook dibangun oleh `src/build_tourism_notebook.py`; skrip executor menjalankan notebook dan menyalin hasil ke `outputs/tourism/`.

## Dua sumber utama

1. [JogjaPulse / UGM](https://zenodo.org/records/23157460), device presence per kapanewon dan jam.
2. [Visiting Jogja / Dinas Pariwisata DIY](https://visitingjogja.jogjaprov.go.id/), referensi lokasi dan tanggal keberadaan destinasi. Tujuh baris kurasi beserta URL bukti tersedia di `data/tourism/destinations.csv` dan tab **Destinasi Terverifikasi** pada Sheets referensi.

Peta titik menggunakan lokasi representatif administratif OpenStreetMap, bukan titik destinasi atau batas historis. Atribusi © OpenStreetMap contributors, ODbL: https://www.openstreetmap.org/copyright . Referensi koordinat tersedia di `data/tourism/region_locations.csv`.

## Metode dan temuan

Periode: 1 Desember 2021–15 Februari 2022. Desember dan Januari–15 Februari dipisah untuk menangani perubahan sampel sumber. Seleksi coverage minimal 90% per periode, seluruh 10 jam 08–17 terbit, serta minimal empat hari akhir pekan dan sepuluh hari kerja lengkap pada kedua periode.

Ukuran aktivitas adalah rata-rata hitungan perangkat per jam dalam jendela siang. Rasio akhir pekan dihitung terhadap rerata hari kerja pada wilayah dan periode yang sama; hitungan tidak dijumlahkan menjadi perangkat unik harian.

Tujuh kasus terdokumentasi, enam layak dibandingkan. Tanjungsari dikeluarkan karena cakupan rendah. Kokap dan Kretek positif pada kedua periode. Cangkringan, Dlingo, Pakem, dan Prambanan berubah arah. Lihat `REPORT.md` untuk angka dan batas interpretasi.

Sampel kasus bukan inventaris wisata lengkap; wilayah lain tidak dilabeli sebagai wilayah tanpa wisata. Kehadiran regional mencakup penduduk dan aktivitas lain, bukan jumlah pengunjung objek wisata. Hasil deskriptif tidak membuktikan efek wisata atau signifikansi statistik.

## Keluaran dan pengumpulan

Repositori kode: https://github.com/nastarynaz/korelasi-wisata-jogja-weekend

[Video presentasi wisata (5 menit)](https://drive.google.com/file/d/1XIyzRdP1U1JO56rYKm0XG1Uy4fkXMfe_/view) · [Gambar PNG](https://drive.google.com/drive/folders/1xkrpjVKA4pQHVMM6g1TeFhgpD2EhtKNj)


- `COLAB_RUN.ipynb`: notebook beserta sepuluh grafik hasil eksekusi.
- `outputs/tourism/figures/`: PNG/PDF; `outputs/tourism/tables/`: tabel sumber hasil.
- `data/tourism/`: kurasi referensi serta pemetaan wilayah.
- `presentation/scenes_en.json`: naskah Inggris versi wisata.
- `presentation/ritme-jogja-final.mp4`: video versi wisata, tepat 5 menit, narasi Inggris sintetis dan kredit lima anggota.

Kode tersedia di repositori GitHub ini; video belum dikumpulkan ke eLOK. Tugas meminta video lima menit, unggah kode GitHub, video eLOK sebelum minggu ke-13, serta presentasi minggu 13–14. Tanggal kalender mengikuti kelas. Berkas analisis cuaca terdahulu merupakan arsip, bukan temuan proyek versi ini.
