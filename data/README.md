# Data proyek versi wisata

Notebook membaca mobilitas dari Sheets publik yang berasal dari JogjaPulse. Referensi destinasi dikurasi dari artikel Visiting Jogja/Dinas Pariwisata DIY dengan tanggal publikasi sebelum Desember 2021 dan keterangan lokasi kapanewon.

`tourism/destinations.csv`: tujuh kasus, kode wilayah, tanggal dan URL bukti. Kode diperiksa terhadap mobilitas; studi ini bukan inventaris lengkap dan tidak mengklasifikasikan wilayah lain sebagai nonwisata.

`tourism/region_locations.csv`: titik representatif wilayah dari OpenStreetMap/Nominatim saat pengambilan, bukan titik objek wisata atau batas historis. Atribusi © OpenStreetMap contributors, ODbL, https://www.openstreetmap.org/copyright .

Tab Destinasi Terverifikasi (gid 202211) dan Lokasi Wilayah (gid 202212) berada di spreadsheet referensi 1_gXsB8Mg7vkoK0HiGuug1Ei0TJu75jdrVbL6maZkzm4. Tab cuaca lama tidak digunakan versi wisata.

File mentah mobilitas tidak diduplikasi ke ZIP kode karena README sumber belum memberi lisensi redistribusi yang jelas. Pengguna dapat mengunduh dari sumber asli; salinan Sheets yang sudah tersedia dipakai untuk eksekusi. Manifest sumber awal dipertahankan sebagai provenance snapshot.
