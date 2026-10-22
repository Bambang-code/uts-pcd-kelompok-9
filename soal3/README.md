# Soal 3 - Penghitungan Koin Menurut Ukuran

**Dikerjakan oleh Bambang Herlambang (5803024019), Kelompok 9.**

## Tujuan dan asumsi

Menghitung jumlah koin pada setiap kelompok ukuran menggunakan
`skimage.measure.regionprops`. Koin diasumsikan **utuh, tidak saling
bersentuhan, kontras terhadap latar seragam**, dan dibandingkan pada skala
citra yang sama. Mayoritas piksel bingkai gambar harus merupakan latar.

Ukuran dinyatakan sebagai **diameter ekuivalen dalam piksel**, bukan nominal
uang atau diameter dalam milimeter.

## Cara menjalankan

Gunakan Python 3.10 atau lebih baru. Semua perintah berikut dijalankan dari
**folder utama repositori**, bukan dari dalam folder `soal3/`.
Jika lingkungan belum tersedia, lakukan persiapan sekali:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Jalankan program:

```powershell
.\.venv\Scripts\python.exe soal3/main.py
```

Program langsung memakai Python di `.venv` tanpa aktivasi dan berjalan tanpa
membuka jendela grafik. Masukan default adalah [data/koin_100.png](data/koin_100.png).
Hasil disimpan ke [hasil/](hasil/).

Untuk memakai gambar sendiri:

```powershell
.\.venv\Scripts\python.exe soal3/main.py --input "D:\gambar\koin.png" --output-dir soal3/hasil_koin_saya
```

## Metode dan kode semu

Bagian ini menjelaskan metode bawaan `--method otsu` sesuai asumsi soal.
Untuk pengembangan tambahan pada foto dengan pencahayaan tidak merata,
tersedia `--method watershed`; lihat [uji foto nyata](UJI_FOTO_NYATA.md).

1. Baca citra, konversi ke grayscale, dan normalisasi ke rentang `[0, 1]`.
2. Gunakan ambang Otsu. Mayoritas piksel bingkai menentukan polaritas latar.
3. Isi lubang mask dan buang komponen dengan luas kurang dari 50 piksel persegi.
4. Label ulang komponen menggunakan konektivitas 8.
5. Ukur objek dengan `regionprops`, lalu kelompokkan berdasarkan diameter.

```text
Baca citra; ubah menjadi grayscale dan normalisasi
Mask = segmentasi Otsu dengan polaritas berdasarkan bingkai
Isi lubang; buang komponen dengan luas < 50 piksel persegi
Label komponen 8 tetangga
Objek = regionprops(label)
Urutkan objek berdasarkan diameter ekuivalen
Untuk setiap objek:
    Bentuk calon kelompok bersama kelompok terakhir
    Terima jika seluruh anggota berada dalam ±8% median calon kelompok
    Jika gagal, buat kelompok baru
Hitung jumlah anggota setiap kelompok
Simpan mask, label, anotasi, CSV, dan ringkasan JSON
```

Implementasi lengkap tersedia pada [main.py](main.py).

## Peran regionprops dan aturan ukuran

| Atribut | Penggunaan |
| --- | --- |
| `label` | Identitas objek |
| `area` | Luas objek dalam piksel persegi |
| `equivalent_diameter_area` | Diameter ekuivalen untuk pengelompokan |
| `centroid` | Posisi anotasi |
| `bbox` | Batas lokasi objek |

Diameter dihitung sebagai `d = sqrt(4A / pi)`, dengan `A` luas objek.
Kelompok diberi nama K1, K2, dan seterusnya dari kecil ke besar.
Pemeriksaan toleransi mencakup **seluruh anggota calon kelompok** terhadap
median yang dihitung ulang, bukan hanya dua objek bertetangga.

| Parameter | Default | Arti |
| --- | --- | --- |
| `--min-area` | `50` | Luas minimum objek dalam piksel persegi |
| `--size-tolerance` | `0.08` | Toleransi relatif diameter, yaitu 8% |
| `--expected-count` | `100` | Jumlah acuan untuk peringatan; `0` menonaktifkannya |

`--expected-count` hanya memberi peringatan. Program tidak memaksa jumlah
objek menjadi 100 atau jumlah kelompok menjadi empat.

## Data dan hasil contoh

Data adalah **simulasi**, bukan foto koin nyata: 100 koin pada citra
1100 × 1100 piksel, dibuat dengan seed 9. Data acuan pada
[koin_100_ground_truth.json](data/koin_100_ground_truth.json) hanya digunakan
untuk validasi; program penghitung membaca gambar saja.

| Kelompok | Median diameter (px) | Jumlah |
| --- | --- | --- |
| K1 | 25,85 | 25 |
| K2 | 36,00 | 25 |
| K3 | 45,95 | 25 |
| K4 | 55,93 | 25 |
| **Total** | | **100** |

![Ringkasan hasil penghitungan koin](hasil/ringkasan_visual.png)

## Berkas keluaran

| Berkas dalam `hasil/` | Isi |
| --- | --- |
| [mask_koin.png](hasil/mask_koin.png) | Mask biner objek |
| [label_koin.png](hasil/label_koin.png) | Warna berbeda untuk identitas komponen |
| [anotasi_koin.png](hasil/anotasi_koin.png) | ID objek dan kelompok ukuran |
| [ringkasan_visual.png](hasil/ringkasan_visual.png) | Masukan, mask, dan anotasi |
| [objek_koin.csv](hasil/objek_koin.csv) | Pengukuran tiap objek |
| [ringkasan.json](hasil/ringkasan.json) | Jumlah, statistik kelompok, parameter, dan peringatan |

Warna pada gambar label menunjukkan identitas komponen, bukan kelas ukuran.

## Pengujian dan batasan

Dari folder utama repositori:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q soal3/tests
```

Lima pengujian pada [tests/test_koin.py](tests/test_koin.py) mencakup
kecocokan terhadap data acuan, inversi latar, perubahan skala, lubang dan
derau pada contoh sembilan koin, serta penolakan masukan seragam atau kosong.

Empat kasus tambahan pada [tests/test_watershed.py](tests/test_watershed.py)
memeriksa mask pada gradien latar terang/gelap, pemetaan 24 pusat koin pada
foto nyata, serta penolakan penanda tidak valid. Total pengujian proyek
adalah 12: tiga LoG, lima koin inti, dan empat kasus watershed.

Koin bersentuhan dapat menyatu menjadi satu komponen. Koin terpotong,
bayangan, latar bertekstur, dan perspektif dapat mengganggu hasil. Ukuran
yang sangat dekat dapat tergabung akibat toleransi pengelompokan.
Periksa mask dan anotasi ketika mengganti citra masukan.

Pembahasan lengkap ada di [laporan kelompok](../LAPORAN.md) dan
[laporan PDF](../laporan/pdf/laporan-uts-pcd-kelompok-9.pdf).
