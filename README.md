# UTS Pengolahan Citra Digital - Kelompok 9

Penyelesaian **nomor 1 dan 3** untuk INF301, semester gasal 2026/2027.
Program, kode semu, penjelasan metode, data contoh, dan hasil eksekusi tersedia
di repositori ini. Folder `soal2/` disiapkan untuk bagian anggota kelompok lain.

## Cara cepat menjalankan untuk dosen

Gunakan Python 3.10 atau lebih baru. Setelah mengunduh atau clone repositori,
buka terminal di folder repositori, lalu jalankan:

```powershell
python -m pip install -r requirements.txt
python soal1/main.py
python soal3/main.py
```

Pemasangan library cukup dilakukan sekali pada Python yang digunakan.
Virtual environment (`.venv`) bersifat opsional; program dapat dijalankan
dengan Python yang sudah tersedia di komputer dosen setelah dependensi terpasang.
Hasil nomor 1 disimpan ke
`soal1/hasil/`, sedangkan hasil nomor 3 disimpan ke `soal3/hasil/`.
Kedua program dapat dijalankan tanpa membuka jendela grafik. Lokasi data dan
hasil default mengikuti folder program, sehingga tidak bergantung pada
folder kerja saat program dipanggil.

Data contoh dan hasil eksekusi sudah disertakan. Untuk memeriksa hasil tanpa
menjalankan ulang, buka [LAPORAN.md](LAPORAN.md) serta folder hasil tiap soal.

## Berkas utama

| Berkas | Kegunaan |
| --- | --- |
| [soal1/main.py](soal1/main.py) | LoG sigma 0,1 dan 0,2; simpan `im1`, `im2`, dan selisih |
| `soal2/` | Folder yang disediakan untuk pekerjaan nomor 2 |
| [soal3/main.py](soal3/main.py) | Segmentasi koin, `regionprops`, dan jumlah per kelompok ukuran |
| [LAPORAN.md](LAPORAN.md) | Asumsi, kode semu, rumus, metode, hasil, dan batasan |
| `buat_data_contoh.py` | Membuat ulang data sintetis dengan seed tetap |
| [soal1/data/](soal1/data/) | Citra uji LoG |
| [soal1/hasil/](soal1/hasil/) | Array numerik, PNG hasil, panel perbandingan, metadata |
| [soal3/data/](soal3/data/) | Citra 100 koin dan ground truth untuk validasi |
| [soal3/hasil/](soal3/hasil/) | Mask, label, anotasi, tabel pengukuran CSV, ringkasan JSON |
| [soal1/tests/test_log.py](soal1/tests/test_log.py) | Pengujian numerik LoG dan selisih bertanda |
| [soal3/tests/test_koin.py](soal3/tests/test_koin.py) | Pengujian segmentasi dan penghitungan koin |

Data contoh adalah **simulasi**, bukan foto koin nyata. Citra koin memiliki
empat ukuran, masing-masing 25 buah. Program penghitung hanya membaca gambar;
berkas [soal3/data/koin_100_ground_truth.json](soal3/data/koin_100_ground_truth.json)
dipakai untuk pengujian terpisah.

## Nomor 1

```powershell
python soal1/main.py --input "D:\gambar\citra.png" --output-dir soal1/hasil_citra_saya
```

Default memakai [soal1/data/citra_uji.png](soal1/data/citra_uji.png), sigma 0,1 dan 0,2 **piksel**,
`hasil = im1 - im2`, dan perluasan batas `reflect`.

- `im1.npy`, `im2.npy`, `hasil.npy`: nilai sebenarnya, float64 bertanda.
- `im1.png`, `im2.png`, `hasil.png`: pratinjau dengan skala bersama; nol abu-abu.
- `grayscale.png`, `perbandingan.png`, `metadata.json`: masukan grayscale,
  tampilan gabungan, parameter dan rentang nilai.

Pengurangan dilakukan pada respons asli sebelum konversi ke PNG. Sigma pada
soal jauh di bawah satu piksel, sehingga sampling kernel LoG menghasilkan
bias DC; tampilan hasil dapat menyerupai negatif citra. Penjelasan numeriknya
tersedia di laporan. Nilai sigma tidak diganti secara diam-diam.

![Perbandingan hasil nomor 1](soal1/hasil/perbandingan.png)

## Nomor 3

```powershell
python soal3/main.py --input "D:\gambar\koin.png" --output-dir soal3/hasil_koin_saya
```

Default memakai [soal3/data/koin_100.png](soal3/data/koin_100.png).
Koin harus terpisah, terlihat utuh, dan kontras terhadap latar seragam.
Mayoritas piksel bingkai gambar harus merupakan latar. Program memilih
polaritas terang/gelap secara otomatis, lalu mengelompokkan diameter
ekuivalen menggunakan toleransi relatif 8%.

Pilihan penyesuaian:

```powershell
python soal3/main.py --size-tolerance 0.05 --min-area 50 --expected-count 100
```

`--min-area` bersatuan piksel persegi. `--expected-count` hanya menghasilkan
peringatan jika jumlah berbeda; jumlah deteksi tidak dipaksa menjadi 100.
Gunakan `--expected-count 0` untuk menonaktifkan pemeriksaan tersebut.
Kelompok ukuran berupa diameter dalam piksel, bukan nominal mata uang.

Hasil contoh: **100 koin, 4 kelompok ukuran, masing-masing 25 koin**.
Lihat [ringkasan.json](soal3/hasil/ringkasan.json) untuk jumlah dan statistik
ukuran, [objek_koin.csv](soal3/hasil/objek_koin.csv) untuk pengukuran tiap koin,
serta [anotasi_koin.png](soal3/hasil/anotasi_koin.png) untuk posisi dan kelompoknya.

![Ringkasan hasil nomor 3](soal3/hasil/ringkasan_visual.png)

## Membuat ulang data dan menjalankan pengujian (opsional)

```powershell
python buat_data_contoh.py --seed 9
python soal1/main.py
python soal3/main.py
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Perintah `pytest -q` di atas menjalankan seluruh pengujian dari folder
repositori. Untuk menjalankan pengujian tiap bagian secara terpisah:

```powershell
python -m pytest -q soal1/tests
python -m pytest -q soal3/tests
```

Generator menyimpan data ke `soal1/data/` dan `soal3/data/` di dalam folder
repositori secara default. Pembuatan ulang dengan folder dan seed yang sama
menimpa data contoh tersebut. Pada generator, `--output-dir` menentukan folder
akar struktur keluaran. Contohnya, `--output-dir percobaan` membuat
`percobaan/soal1/data/` dan `percobaan/soal3/data/`; gunakan `--input` pada
program terkait untuk memilih citra dari folder percobaan itu.

Implementasi sudah dijalankan dengan Python 3.10, NumPy 2.2.6, SciPy 1.15.3,
scikit-image 0.25.2, Matplotlib 3.10.9, dan Pillow 12.3.0.
