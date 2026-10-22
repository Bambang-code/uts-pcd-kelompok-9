# Soal 1 - Selisih Laplacian of Gaussian

**Dikerjakan oleh Bambang Herlambang (5803024019), Kelompok 9.**

## Tujuan

Membaca citra, menerapkan filter Laplacian of Gaussian (LoG) dengan standar
deviasi **0,1 dan 0,2 piksel**, lalu menyimpan kedua respons sebagai `im1`
dan `im2` serta selisih `hasil = im1 - im2`.

## Cara menjalankan

Gunakan Python 3.10 atau lebih baru. Semua perintah berikut dijalankan dari
**folder utama repositori**, bukan dari dalam folder `soal1/`.
Jika lingkungan belum tersedia, lakukan persiapan sekali:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Jalankan program:

```powershell
.\.venv\Scripts\python.exe soal1/main.py
```

Program langsung memakai Python di `.venv` tanpa aktivasi dan berjalan tanpa
membuka jendela grafik. Masukan default adalah [data/citra_uji.png](data/citra_uji.png),
citra sintetis grayscale berukuran 384 × 256 piksel. Hasil disimpan ke [hasil/](hasil/).

Untuk memakai gambar sendiri:

```powershell
.\.venv\Scripts\python.exe soal1/main.py --input "D:\gambar\citra.png" --output-dir soal1/hasil_citra_saya
```

Uji tambahan dengan foto nyata 512 x 512 piksel tersedia pada
[UJI_FOTO_NYATA.md](UJI_FOTO_NYATA.md). Jalankan dengan:

```powershell
.\.venv\Scripts\python.exe soal1/main.py --input soal1/data/foto_kamera_scikit.png --output-dir soal1/hasil_foto_nyata
```

Hasilnya disimpan terpisah dari contoh sintetis. Sigma tetap 0,1 dan 0,2;
perilaku bias DC pada sigma kecil juga terlihat pada foto nyata tersebut.

## Metode dan kode semu

1. Baca citra grayscale, RGB, atau RGBA. Transparansi RGBA dikompositkan ke putih.
2. Ubah citra menjadi grayscale dengan tipe `float64` dalam rentang `[0, 1]`.
3. Hitung dua respons `scipy.ndimage.gaussian_laplace` dari citra yang sama.
4. Gunakan `mode="reflect"` untuk menangani batas citra.
5. Kurangkan respons asli sebelum membuat visualisasi PNG.

```text
Baca citra dan konversi menjadi grayscale float64
im1 = LoG(citra, sigma=0.1, mode=reflect)
im2 = LoG(citra, sigma=0.2, mode=reflect)
hasil = im1 - im2
Simpan im1, im2, dan hasil sebagai NPY bertanda
Buat PNG dengan satu skala tampilan bersama
Simpan panel perbandingan dan metadata
```

`im2` dihitung dari citra masukan yang sama, bukan dari `im1`.
Implementasi lengkap tersedia pada [main.py](main.py).

## Berkas keluaran

| Berkas dalam `hasil/` | Isi |
| --- | --- |
| `grayscale.png` | Citra masukan setelah konversi grayscale |
| `im1.npy`, `im2.npy`, `hasil.npy` | Respons asli `float64`, termasuk nilai negatif |
| `im1.png`, `im2.png`, `hasil.png` | Pratinjau respons dengan skala bersama |
| [perbandingan.png](hasil/perbandingan.png) | Panel masukan, kedua respons, dan selisih |
| [metadata.json](hasil/metadata.json) | Parameter, dimensi, rentang nilai, dan pemetaan PNG |

![Perbandingan hasil LoG](hasil/perbandingan.png)

PNG memetakan rentang `[-M, M]` ke `[0, 255]`, dengan `M` nilai absolut
terbesar dari ketiga respons (atau 1 jika seluruhnya nol). Nol tampil
abu-abu sekitar 128. Gunakan NPY untuk analisis numerik, karena PNG hanya
pratinjau. Pada contoh yang disertakan, seluruh respons bernilai negatif.

## Interpretasi sigma kecil

Sigma pada soal jauh di bawah satu piksel. Pada lingkungan yang diperiksa
(SciPy 1.15.3), sigma 0,1 dengan parameter bawaan menghasilkan radius kernel
nol dan respons sekitar `-200 × intensitas`. Citra konstan 0,4 menghasilkan
`im1 = -80`, `im2 ≈ -19,9962734`, dan `hasil ≈ -60,0037266`.

Ini merupakan **bias DC akibat sampling kernel diskret**. Karena itu,
hasil dapat menyerupai negatif citra dan perlu ditafsirkan bersama
keterbatasan numeriknya. Sigma tetap mengikuti soal.

## Pengujian

Dari folder utama repositori:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q soal1/tests
```

Tiga pengujian pada [tests/test_log.py](tests/test_log.py) memeriksa respons
analitik sigma kecil, selisih nol saat sigma sama, dan penyimpanan nilai
bertanda. Pemeriksaan tambahan memakai sigma 1 dan 2; parameter utama tugas
tetap 0,1 dan 0,2.

Pembahasan lengkap ada di [laporan kelompok](../LAPORAN.md) dan
[laporan PDF](../laporan/pdf/laporan-uts-pcd-kelompok-9.pdf).
