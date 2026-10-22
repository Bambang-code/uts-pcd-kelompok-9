# UTS INF301 Pengolahan Citra Digital – Soal 2
**Memecah Karakter pada Gambar Teks dengan `regionprops`**

Program `soal2_segmentasi_karakter.py` memecah gambar teks menjadi karakter-karakter individual dan menyimpan tiap karakter sebagai gambar terpisah.

## Cara Menjalankan
```bash
pip install scikit-image numpy matplotlib
python soal2_segmentasi_karakter.py
```
Gambar soal disimpan sebagai `teks.png` (atau ubah `INPUT_PATH` di kode). Hasil ada di folder `hasil_karakter/`: `karakter_01.png` sampai `karakter_18.png`, dan `_visualisasi_bbox.png` (gambar dengan kotak dan nomor tiap karakter).

## Penjelasan Metode (CPMK112)
Karakter pada gambar berwarna putih di latar hitam dan tidak saling bersentuhan, sehingga tiap karakter adalah satu kelompok piksel putih yang saling terhubung (*connected component*). Langkahnya:

1. **Grayscale.** Citra diubah menjadi satu kanal intensitas per piksel.
2. **Thresholding Otsu.** Citra diubah menjadi biner (karakter = 1, latar = 0). Nilai ambang dipilih otomatis oleh Otsu, yaitu nilai yang memisahkan dua kelompok piksel (karakter dan latar) sejelas mungkin, jadi tidak perlu dicoba manual.
3. **Hapus noise.** Bintik yang sangat kecil dibuang.
4. **Pelabelan.** `measure.label` memberi nomor yang sama pada piksel yang saling terhubung, sehingga satu karakter = satu label. Dipakai 8-connectivity supaya goresan diagonal pada huruf yang miring tidak terputus.
5. **`regionprops`.** Fungsi ini memberi properti tiap region: `bbox` (kotak pembatas), `image` (mask karakter yang sudah terpotong), dan `centroid` (titik pusat). Mask `image` disimpan sebagai gambar karakter, sehingga huruf tetangga yang masuk ke dalam kotak huruf miring tidak ikut tersalin.
6. **Saring region.** Region yang lebih besar dari setengah ukuran gambar dibuang karena tidak mungkin satu karakter.
7. **Urutkan.** Karakter dikelompokkan ke tiap baris teks (garis miring) dengan RANSAC pada titik centroid, baris diurutkan dari atas ke bawah, lalu tiap baris dari kiri ke kanan.
8. **Simpan.** Tiap mask disimpan sebagai `karakter_XX.png`.

## Hasil
Terdeteksi **18 karakter** sesuai teks pada soal (ZEUS = 4, TWINPEAK = 8, ACOSTA = 6), tiap karakter terpisah dan bernomor sesuai urutan baca.

## Refleksi
- **Border ikut terdeteksi.** Awalnya terdeteksi 19 objek, karena garis tepi gambar menjadi satu objek besar. Diperbaiki dengan menyaring region berdasarkan ukuran bounding box.
- **Urutan nomor acak.** Mengurutkan berdasarkan baris centroid tidak cocok untuk teks miring. Diperbaiki dengan mengelompokkan karakter ke tiap baris teks dulu (RANSAC), baru diurutkan.
- **Asumsi.** Karakter terang pada latar gelap seragam, tidak bersentuhan, dan disimpan sebagai mask biner dengan orientasi aslinya.
- **Keterbatasan.** Karakter yang bersentuhan akan tergabung; huruf dengan lebih dari satu bagian (seperti "i") terdeteksi sebagai dua objek; pengurutan mengasumsikan baris teks kira-kira lurus dan tidak vertikal.