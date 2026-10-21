# Penyelesaian UTS INF301 - Nomor 1 dan 3

**Kelompok 9 | Pengolahan Citra Digital | Gasal 2026/2027**

## 1. Selisih Laplacian of Gaussian

### Tujuan dan asumsi

Membaca sebuah citra, menerapkan filter Laplacian of Gaussian (LoG) dengan
standar deviasi 0,1 dan 0,2, menyimpan respons sebagai `im1` dan `im2`, lalu
menyimpan selisihnya. Istilah LG pada soal diinterpretasikan sebagai LoG.
Standar deviasi diinterpretasikan dalam satuan piksel pada kedua sumbu.
Selisih didefinisikan sebagai **im1 dikurangi im2**, tetap bertanda.

Citra RGB diubah menjadi grayscale agar filter bekerja pada dua dimensi
spasial. Intensitas dikonversi ke float64 dalam rentang [0, 1]. Transparansi
RGBA dikompositkan ke putih sebelum konversi grayscale.

### Dasar metode

Gaussian dua dimensi diberikan oleh:

\[
G_\sigma(x,y) = \frac{1}{2\pi\sigma^2}
\exp\left(-\frac{x^2+y^2}{2\sigma^2}\right).
\]

Respons LoG secara kontinu adalah:

\[
L_\sigma = \nabla^2(G_\sigma * I)
= \frac{\partial^2(G_\sigma * I)}{\partial x^2}
+ \frac{\partial^2(G_\sigma * I)}{\partial y^2}.
\]

Implementasi memakai `scipy.ndimage.gaussian_laplace`, yang menerapkan
turunan kedua Gaussian pada citra. Perluasan batas menggunakan `reflect`.
Filter tidak dikalikan faktor normalisasi skala sigma kuadrat karena
normalisasi tersebut tidak diminta dalam soal.

\[
im1 = L_{0.1}, \qquad im2 = L_{0.2}, \qquad hasil = im1 - im2.
\]

### Kode semu

```text
MULAI
    BACA citra
    JIKA citra RGBA: kompositkan ke latar putih
    JIKA citra RGB: ubah menjadi grayscale
    KONVERSI intensitas ke float64 [0, 1]
    im1 <- FILTER_LOG(citra, sigma = 0.1, batas = reflect)
    im2 <- FILTER_LOG(citra, sigma = 0.2, batas = reflect)
    hasil <- im1 - im2
    SIMPAN im1, im2, hasil sebagai array float64
    TENTUKAN batas tampilan bersama dari maksimum nilai absolut ketiganya
    SIMPAN visualisasi PNG tanpa mengubah array numerik asli
SELESAI
```

Bagian inti dalam [soal1/main.py](soal1/main.py):

```python
im1 = gaussian_laplace(citra, sigma=0.1, mode="reflect")
im2 = gaussian_laplace(citra, sigma=0.2, mode="reflect")
hasil = im1 - im2
```

### Penyimpanan dan hasil

Array `.npy` menyimpan respons asli termasuk nilai negatif. Mengubah hasil
LoG langsung menjadi `uint8` dapat membuang informasi negatif. Karena itu,
pengurangan dilakukan pada float64 sebelum penyesuaian tampilan.

Untuk PNG, ketiga respons dipetakan dari rentang bersama [-M, M] ke [0, 255],
dengan M adalah maksimum nilai absolut ketiganya. Nilai nol ditampilkan
sebagai abu-abu 128; nilai negatif lebih gelap dan nilai positif lebih terang.
Jika semua respons nol, dipakai M = 1. PNG merupakan visualisasi, sedangkan
`.npy` adalah data untuk perhitungan lanjutan. Rentang disimpan di metadata.

Masukan contoh tersedia di [soal1/data/citra_uji.png](soal1/data/citra_uji.png).
Seluruh keluaran default nomor 1 disimpan di [soal1/hasil/](soal1/hasil/).

![Citra grayscale, im1, im2, dan selisihnya](soal1/hasil/perbandingan.png)

**Catatan sampling sigma kecil.** LoG kontinu ideal memiliki respons nol
pada citra konstan. Pada grid piksel, sigma 0,1 dan 0,2 sangat kecil.
Dengan kernel diskret bawaan SciPy (`truncate=4`), sigma 0,1 memiliki radius
kernel `round(4 * 0.1) = 0`. Untuk citra 2D, responsnya menjadi sekitar
`-200 * I`. Pada sigma 0,2, respons terhadap intensitas konstan c sekitar
`-49.9906834 * c`. Jadi, pada masukan konstan, selisih tidak nol.

Contoh yang diperiksa pada SciPy 1.15.3: citra konstan 0,4 menghasilkan
`im1 = -80`, `im2 = -19,9962734`, dan `hasil = -60,0037266`.
Hasil ini merupakan efek sampling kernel, sehingga gambar hasil tidak
ditafsirkan semata-mata sebagai peta tepi. Program tetap memakai sigma sesuai
soal. Untuk eksperimen tambahan, CLI menyediakan `--sigma-1` dan `--sigma-2`;
simpan eksperimen tersebut ke folder berbeda dari hasil utama.

## 3. Jumlah koin untuk setiap ukuran

### Tujuan dan asumsi

Menghitung koin terpisah pada latar seragam serta jumlahnya untuk setiap
ukuran dengan fungsi `regionprops`. Koin diasumsikan terlihat utuh, tidak
bersentuhan atau bertumpuk, dan dapat dibedakan dari latar melalui intensitas.
Mayoritas piksel pada bingkai citra merupakan latar. Semua koin berada pada
skala pengambilan gambar yang sama; efek perspektif diabaikan.

Soal tidak memberikan foto koin untuk diproses. Karena itu, pengujian
menggunakan citra sintetis berisi 100 koin dengan empat radius, yaitu 13,
18, 23, dan 28 piksel; setiap radius berjumlah 25. Posisi diberi variasi
acak dengan seed 9 dan dijaga agar tidak saling menyentuh. Citra tersedia di
[soal3/data/koin_100.png](soal3/data/koin_100.png); metadata validasi terpisah
tersedia di [soal3/data/koin_100_ground_truth.json](soal3/data/koin_100_ground_truth.json).
Implementasi nomor ini berada di [soal3/main.py](soal3/main.py).

### Kode semu

```text
MULAI
    BACA citra, ubah menjadi grayscale dan normalisasi intensitas
    TOLAK citra seragam seluruhnya
    T <- ambang Otsu pada citra grayscale
    terang <- grayscale > T
    JIKA mayoritas bingkai termasuk terang:
        mask <- kebalikan terang       // koin gelap, latar terang
    SELAIN ITU:
        mask <- terang                 // koin terang, latar gelap
    ISI lubang di dalam mask
    LABEL komponen terhubung dengan 8-tetangga
    HAPUS komponen yang luasnya < min_area
    LABEL ulang mask yang telah dibersihkan
    UNTUK setiap region dari regionprops(label):
        UKUR luas, diameter ekuivalen, centroid, bounding box
    URUTKAN objek menurut diameter, dari kecil ke besar
    UNTUK setiap objek:
        COBA gabungkan ke kelompok terakhir
        HITUNG median diameter calon kelompok
        JIKA setiap anggota berjarak <= toleransi * median tersebut:
            TERIMA objek dalam kelompok itu
        SELAIN ITU:
            BUAT kelompok ukuran baru
    HITUNG jumlah objek pada tiap kelompok
    JIKA jumlah total berbeda dari 100: catat peringatan
    SIMPAN mask, label, anotasi, CSV pengukuran, JSON ringkasan
SELESAI
```

### Penggunaan regionprops

Setelah segmentasi, `measure.label(mask, connectivity=2)` memberikan label
integer berbeda pada setiap komponen 8-tetangga. Karena koin terpisah,
satu komponen mewakili satu koin. `measure.regionprops(labels)` kemudian
mengukur setiap region berlabel tersebut.

| Properti | Peran dalam program |
| --- | --- |
| `label` | Identitas unik objek pada CSV dan anotasi |
| `area` | Luas objek dalam piksel persegi |
| `equivalent_diameter_area` | Dasar pengelompokan ukuran koin |
| `centroid` | Posisi tengah untuk menempatkan anotasi |
| `bbox` | Batas objek untuk pemeriksaan posisi dan ukuran |

Diameter ekuivalen adalah diameter lingkaran dengan luas yang sama dengan
region:

\[
d_i = \sqrt{\frac{4 A_i}{\pi}}.
\]

Untuk koin yang tampak mendekati lingkaran, diameter ini merupakan ukuran
yang lebih mudah dibandingkan daripada luas. Nilai `centroid` dari
`regionprops` berurutan (baris, kolom), lalu ditulis sebagai y dan x.
Batas maksimum `bbox` bersifat eksklusif dan diberi nama demikian di CSV.

### Segmentasi dan pengelompokan ukuran

Ambang Otsu memisahkan dua kelas intensitas dengan memaksimalkan variasi
antarkelas. Kelas mayoritas pada bingkai dipilih sebagai latar, sehingga
koin terang maupun gelap dapat diproses. Pengisian lubang mencegah detail
gelap di dalam koin mengurangi luas. Penyaringan luas minimum 50 piksel
persegi membuang komponen kecil yang dianggap derau.

Pengelompokan tidak memerlukan jumlah ukuran yang telah diketahui.
Diameter diurutkan dan dimasukkan ke kelompok secara deterministik.
Toleransi default 8% berarti setiap anggota calon kelompok harus memenuhi:

\[
|d_i - \operatorname{median}(D)| \leq 0.08\operatorname{median}(D).
\]

Pemeriksaan dilakukan kembali pada seluruh anggota calon kelompok untuk
membatasi efek rantai diameter yang berdekatan. Kelompok diberi nomor
dari ukuran terkecil ke terbesar. Ini merupakan pengelompokan berdasarkan
toleransi, sehingga dua ukuran fisik yang terlalu dekat dapat bergabung.
Toleransi perlu disesuaikan dengan resolusi, variasi segmentasi, dan selisih
ukuran yang ingin dibedakan. Tanpa kalibrasi, hasil bersatuan piksel dan
tidak menentukan diameter milimeter atau nominal mata uang.

### Hasil pengujian contoh

Dengan parameter default, hasil pada data sintetis adalah:

| Kelompok | Diameter acuan (px) | Median terukur (px) | Jumlah acuan | Jumlah terdeteksi |
| --- | ---: | ---: | ---: | ---: |
| K1 | 26 | 25,85 | 25 | 25 |
| K2 | 36 | 36,00 | 25 | 25 |
| K3 | 46 | 45,95 | 25 | 25 |
| K4 | 56 | 55,93 | 25 | 25 |
| **Total** | | | **100** | **100** |

Perbedaan kecil diameter muncul karena rasterisasi dan ambang pada tepi
lingkaran. Ground truth digunakan hanya dalam pengujian, tidak dibaca oleh
algoritma penghitung. Tidak ada angka 25 atau empat kelompok yang dipaksakan
dalam proses inferensi. Angka 100 dipakai hanya sebagai pemeriksaan jumlah
yang diharapkan.

Seluruh keluaran default nomor 3 disimpan di [soal3/hasil/](soal3/hasil/).

![Masukan, mask, dan anotasi hasil penghitungan](soal3/hasil/ringkasan_visual.png)

[objek_koin.csv](soal3/hasil/objek_koin.csv) menyimpan satu baris per koin.
[ringkasan.json](soal3/hasil/ringkasan.json) menyimpan
jumlah total, jumlah tiap kelompok, statistik diameter, parameter, dan
peringatan. `mask_koin.png` menunjukkan hasil segmentasi;
`label_koin.png` memberi warna per objek; `anotasi_koin.png` menampilkan
format **ID/Kelompok**, misalnya `7/K1`.

### Batas penerapan

Koin yang menyentuh akan dianggap satu komponen; koin terpotong dapat
terukur lebih kecil. Latar tidak seragam, bayangan kuat, atau intensitas
koin yang sangat mirip latar dapat menyebabkan kesalahan segmentasi.
Pengisian lubang mengasumsikan koin berbentuk cakram penuh. Pengujian
sintetis menunjukkan kesesuaian dengan asumsi soal, bukan jaminan akurasi
pada semua foto nyata.

## Reproduksi dan referensi

Perintah instalasi dan pengujian ada di [README.md](README.md). Dari folder
repositori, jalankan masing-masing bagian dengan:

```powershell
.\.venv\Scripts\python.exe soal1/main.py
.\.venv\Scripts\python.exe soal3/main.py
```

Lokasi data dan hasil default mengikuti folder masing-masing program.
Generator `buat_data_contoh.py` membuat data di `soal1/data/` dan `soal3/data/`;
opsi `--output-dir` pada generator menentukan folder akar untuk struktur
keluaran tersebut.

Pengujian mencakup respons LoG numerik, selisih bertanda, kesesuaian deteksi
tiap koin terhadap ground truth, polaritas latar, perubahan resolusi,
serta pengisian lubang dan pembuangan derau kecil.

- Soal UTS INF301 Pengolahan Citra Digital, Universitas Katolik Widya Mandala
  Surabaya, semester gasal 2026/2027, dokumen yang diberikan pengguna.
- [Dokumentasi SciPy: gaussian_laplace](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_laplace.html).
- [Dokumentasi scikit-image: regionprops](https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.regionprops).
- [Dokumentasi scikit-image: threshold_otsu](https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_otsu).
