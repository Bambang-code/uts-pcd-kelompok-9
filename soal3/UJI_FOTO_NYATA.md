# Uji tambahan pada foto koin nyata

Foto asli: `data/koin_nyata_scikit.png`, salinan tanpa perubahan dari
`skimage.data.coins()` (303 x 384 piksel). Foto ini berisi 24 koin menurut
pemeriksaan visual, sehingga merupakan uji tambahan, bukan pengganti data
100 koin pada tugas.

Sumber: [scikit-image: coins](https://scikit-image.org/docs/stable/api/skimage.data.html#skimage.data.coins).
Dokumentasi menyebut foto koin Yunani dari Pompeii, berasal dari koleksi
Brooklyn Museum, tanpa pembatasan hak cipta yang diketahui. Dokumentasi
juga menjelaskan bahwa tingkat keabuan latar dan koin bertumpang tindih,
sehingga segmentasi sederhana tidak mencukupi.

## Menjalankan dari folder utama repositori

```powershell
.\.venv\Scripts\python.exe soal3/main.py --input soal3/data/koin_nyata_scikit.png --output-dir soal3/hasil_foto_nyata --expected-count 24
```

`--expected-count 24` hanya memeriksa jumlah dan memberikan peringatan;
parameter ini tidak mengubah hasil segmentasi atau memaksakan jumlah objek.

## Hasil metode bawaan Otsu (sebelum pengembangan)

- Program menghasilkan 24 region, tetapi segmentasinya **belum sepenuhnya benar**.
- Region di kiri atas menggabungkan koin dengan area latar yang terang.
  Diameter ekuivalennya sekitar 109,62 piksel, jauh melebihi ukuran koin
  tersebut pada foto.
- Kesamaan jumlah region dengan jumlah koin tidak cukup untuk menyatakan
  deteksi benar. Mask dan lokasi setiap region juga harus diperiksa.
- Enam kelompok yang dihasilkan merupakan kelompok dari region hasil
  segmentasi. Hasil itu belum tervalidasi sebagai enam ukuran koin fisik.
- Foto ini memperlihatkan keterbatasan Otsu global pada pencahayaan latar
  yang tidak seragam. Metode Otsu tetap menjadi metode bawaan.

Periksa `hasil_foto_nyata/ringkasan_visual.png`, `mask_koin.png`,
`anotasi_koin.png`, serta `ringkasan.json` untuk bukti hasil.

Uji ini tidak menyatakan bahwa program telah berhasil pada semua foto
nyata atau telah diuji pada foto 100 koin nyata.

## Pengembangan tambahan: watershed berbasis gradien

```powershell
.\.venv\Scripts\python.exe soal3/main.py --input soal3/data/koin_nyata_scikit.png --output-dir soal3/hasil_foto_nyata_watershed --method watershed --expected-count 24
```

Metode mengikuti [contoh resmi scikit-image](https://scikit-image.org/docs/stable/auto_examples/applications/plot_coins_segmentation.html):
gradien Sobel menjadi peta batas, kemudian watershed menyebarkan region dari
penanda latar dan objek. Program memakai intensitas ternormalisasi dan
membalik polaritas bila mayoritas bingkai merupakan latar terang. Piksel
di bawah `--marker-low 0.12` menjadi penanda latar; piksel di atas
`--marker-high 0.6` menjadi penanda objek. Piksel sisanya ditentukan oleh
watershed. Pengisian lubang, penyaringan luas, `regionprops`, dan
pengelompokan ukuran tetap berjalan setelahnya.

Ambang penanda tersebut merupakan nilai awal untuk foto ini, bukan nilai
universal. Keduanya dapat disesuaikan dengan syarat
`0 <= marker-low < marker-high <= 1`. Penanda latar dan objek harus tersedia.
Metode ini tetap mengasumsikan koin terpisah dan tidak menjamin keberhasilan
pada latar bertekstur, koin saling menutupi, atau kontras yang sangat rendah.

| Pemeriksaan | Otsu | Watershed |
| --- | --- | --- |
| Jumlah region | 24 | 24 |
| Koin kiri atas terpisah dari latar | Tidak | Ya |
| Pusat 24 koin dipasangkan satu per satu | Tidak seluruhnya | Ya, selisih pusat kurang dari 3 px |
| Semua kotak pembatas terpisah dari bingkai | Tidak | Ya |

Pusat acuan ditandai secara visual dari foto asli. Pemeriksaan ini menguji
identitas/lokasi objek, bukan akurasi setiap piksel mask atau diameter fisik.
Watershed menghasilkan lima kelompok diameter piksel dengan jumlah
10, 8, 2, 3, dan 1. Kelompok tersebut belum divalidasi sebagai kategori
diameter fisik atau nominal mata uang.

Hasil sesudah perbaikan ada di [hasil_foto_nyata_watershed/](hasil_foto_nyata_watershed/).
Hasil lama tetap tersedia untuk perbandingan. Pada data utama 100 koin sintetis,
mask Otsu, CSV pengukuran, dan jumlah tiap kelompok tetap identik.
