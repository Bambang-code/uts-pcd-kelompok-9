# Panduan Presentasi UTS INF301

Kelompok 9: Bambang Herlambang (5803024019) dan Dustin Pranata Wangsawidjaja (5803024021).

Presentasi memakai **11 slide**: satu sampul, sembilan slide isi (tiga per soal), dan satu penutup. Slide 5–7 membahas soal 2: citra teks, metode `regionprops`, dan hasil 18 karakter. Soal 1 berada pada slide 2–4 dan soal 3 pada slide 8–10.

Alokasi total tetap **20 menit**, termasuk lima menit untuk soal 2 serta dua menit tanya jawab. Tidak ada demo langsung yang dijadwalkan pada susunan ini. Bambang mengerjakan nomor 1 dan 3; Dustin mengerjakan nomor 2.

Berkas presentasi: [presentasi-uts-pcd-kelompok-9-biru.pptx](presentasi-uts-pcd-kelompok-9-biru.pptx).

## Alokasi waktu

| Slide | Pokok bahasan | Mulai | Selesai | Durasi |
| --- | --- | --- | --- | --- |
| 1 | Sampul | 00:00 | 00:45 | 0:45 |
| 2 | Soal 1: selisih dua respons LoG | 00:45 | 02:25 | 1:40 |
| 3 | Soal 1: hasil LoG dan selisihnya | 02:25 | 04:15 | 1:50 |
| 4 | Soal 1: bias DC pada sigma kecil | 04:15 | 06:15 | 2:00 |
| 5 | Soal 2: pemisahan karakter | 06:15 | 07:55 | 1:40 |
| 6 | Soal 2: metode regionprops | 07:55 | 09:35 | 1:40 |
| 7 | Soal 2: hasil segmentasi karakter | 09:35 | 11:15 | 1:40 |
| 8 | Soal 3: segmentasi setiap koin | 11:15 | 13:15 | 2:00 |
| 9 | Soal 3: pengukuran dengan regionprops | 13:15 | 15:15 | 2:00 |
| 10 | Soal 3: hasil penghitungan koin | 15:15 | 17:15 | 2:00 |
| 11 | Penutup dan tanya jawab | 17:15 | 20:00 | 2:45 |
| **Total** | **Termasuk waktu soal 2 dan tanya jawab** | **00:00** | **20:00** | **20:00** |

Pada slide 11, menit **17:15–18:00** digunakan untuk penutup, lalu menit **18:00–20:00** untuk tanya jawab.

## Menggunakan catatan di PowerPoint

Buka berkas PPTX di PowerPoint dan gunakan **Tampilan Penyaji (Presenter View)**. Tampilkan slide kepada audiens, sedangkan catatan pembicara dan pengukur waktu tetap terlihat pada layar penyaji. Catatan setiap slide berisi alur penjelasan, batas klaim, jalur aset, dan sumber yang relevan. Gunakan sebagai petunjuk latihan; jangan membacakan seluruh catatan secara verbatim.

Catat waktu sejak slide pertama. Jika pembahasan melambat, ringkas contoh lisan agar sesi tanya jawab tetap mendapat dua menit. Buka gambar cadangan sebelum sesi jika perlu memperlihatkan hasil lebih rinci.

## Persiapan sebelum presentasi

Pastikan Python 3.10 atau lebih baru tersedia. Buka PowerShell di folder utama repositori dan lakukan persiapan berikut sebelum presentasi:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe soal1/main.py
.\.venv\Scripts\python.exe soal3/main.py
```

Jika lingkungan `.venv` sudah dibuat dan dependensi sudah terpasang, langsung jalankan kedua program. Simpan terminal dalam keadaan siap pada root repositori. Buka gambar cadangan terlebih dahulu dan pastikan semua keluaran lokal dapat dibaca tanpa jaringan.

Untuk memeriksa pengujian sebelum sesi, jalankan:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Pengujian dan eksekusi program dilakukan sebelum sesi. Presentasi memakai gambar hasil yang telah disiapkan.

## Gambar dan berkas cadangan

- [Hasil segmentasi karakter](../../soal2/hasil_karakter/_visualisasi_bbox.png): kotak pembatas dan nomor 18 karakter.
- [Gambar tiap karakter](../../soal2/hasil_karakter/): keluaran PNG individual.

- [Panel LoG](../../soal1/hasil/perbandingan.png): citra grayscale, im1, im2, dan selisihnya.
- [Ringkasan koin](../../soal3/hasil/ringkasan_visual.png): masukan, mask, dan anotasi.
- [Anotasi koin](../../soal3/hasil/anotasi_koin.png): ID dan kelompok setiap objek.
- [Ringkasan numerik koin](../../soal3/hasil/ringkasan.json): total, jumlah kelompok, dan statistik diameter.
- [Metadata LoG](../../soal1/hasil/metadata.json): parameter dan rentang respons asli.
- [Laporan PDF](../pdf/laporan-uts-pcd-kelompok-9.pdf): penjelasan rinci dan hasil.

Jalur pada catatan pembicara dihitung dari root repositori. Tautan dalam panduan ini dihitung dari lokasi panduan di `laporan/ppt/`.

## Penjelasan teknis yang perlu dijaga

- Nomor 2 menghasilkan mask karakter individual dari `region.image`, dengan padding tiga piksel. Jumlah 18 sesuai citra contoh, bukan kemampuan OCR. RANSAC mengurutkan baris berdasarkan centroid.

- Sigma utama nomor 1 adalah **0,1 dan 0,2 piksel**. Pengurangan dilakukan pada respons float64 bertanda sebelum pembuatan PNG. Seluruh respons pada contoh utama bernilai negatif.
- Bias DC pada sigma sangat kecil merupakan akibat sampling kernel. Contoh citra konstan 0,4 menghasilkan im1 = -80, im2 sekitar -19,9962734, dan selisih sekitar -60,0037266. Jangan menafsirkannya sebagai deteksi tepi pada citra konstan.
- `regionprops` mengukur komponen yang telah berlabel. Diameter ekuivalen diperoleh dari luas. Semua anggota calon kelompok harus berada dalam toleransi 8% terhadap median calon kelompok.
- Data koin bersifat sintetis. Empat kelompok dan 25 koin per kelompok merupakan hasil pada contoh, bukan angka yang dipaksakan algoritma. `--expected-count` hanya memberi peringatan.
- Delapan tes terdiri atas tiga tes LoG dan lima tes koin. Pengujian nilai dua tanda menggunakan sigma tambahan 1 dan 2; parameter tugas tidak diganti.
- Tanpa kalibrasi, ukuran tetap dalam piksel dan tidak menentukan nominal uang. Koin bersentuhan, terpotong, bayangan, serta perspektif dapat mengganggu hasil.

## Sumber dan kredit

- [SciPy: gaussian_laplace](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_laplace.html).
- [scikit-image: regionprops](https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.regionprops).
- [scikit-image: threshold_otsu](https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_otsu).
- [Fakultas Teknik UKWMS](https://ft.ukwms.ac.id/), sumber logo; aset lokal pada `laporan/latex/images/logo-ukwms.png`.
- Soal UTS INF301, 8 Oktober 2026, dokumen yang diberikan pengguna.
