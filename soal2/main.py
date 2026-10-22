"""
UTS INF301 - Soal 2
Memecah teks (berbagai karakter, berbagai orientasi) menjadi gambar karakter
individual menggunakan label + regionprops.

Install: pip install scikit-image numpy matplotlib
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, color, filters, measure, morphology

# ---------------- Parameter ----------------
INPUT_PATH = "teks.png"        # ganti dengan nama file gambar soal
OUTPUT_DIR = "hasil_karakter"  # folder tempat karakter disimpan
MIN_AREA = 10                  # abaikan region kecil (noise)
PADDING = 3                    # margin hitam di sekeliling tiap karakter
# -------------------------------------------


def urutkan_baris_teks(regions, img_shape, tol_frac=0.045):
    """
    Urutkan region sesuai urutan baca:
      1. kelompokkan karakter ke dalam baris teks (garis lurus/miring)
         menggunakan RANSAC line fitting pada titik centroid,
      2. urutkan baris dari atas ke bawah,
      3. dalam tiap baris, urutkan dari kiri ke kanan.
    tol_frac = toleransi jarak titik ke garis, relatif terhadap ukuran citra.
    """
    H, W = img_shape
    tol = tol_frac * max(H, W)
    pts = np.array([[r.centroid[1], r.centroid[0]] for r in regions])  # (x, y)

    remaining = list(range(len(regions)))
    lines = []
    while remaining:
        if len(remaining) < 3:              # sisa 1-2 karakter -> satu baris
            lines.append(remaining)
            break
        _, inliers = measure.ransac(pts[remaining], measure.LineModelND,
                                    min_samples=2, residual_threshold=tol,
                                    max_trials=2000)
        idx = [remaining[i] for i in np.where(inliers)[0]]
        lines.append(idx)
        remaining = [i for i in remaining if i not in idx]

    # Baris teratas lebih dulu (berdasarkan rata-rata koordinat y)
    lines.sort(key=lambda l: pts[l, 1].mean())

    ordered = []
    for l in lines:
        # kiri -> kanan (cukup untuk teks yang tidak vertikal)
        ordered += [regions[i] for i in sorted(l, key=lambda i: pts[i, 0])]
    return ordered


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Baca citra dan ubah ke grayscale
    img = io.imread(INPUT_PATH)
    if img.ndim == 3:
        gray = color.rgb2gray(img[..., :3])
    else:
        gray = img.astype(float) / img.max()

    # 2. Segmentasi: thresholding Otsu -> citra biner
    thresh = filters.threshold_otsu(gray)
    bw = gray > thresh
    # Pastikan karakter = foreground (putih). Jika background putih, balik.
    if bw.mean() > 0.5:
        bw = ~bw

    # 3. Bersihkan noise kecil
    bw = morphology.remove_small_objects(bw, min_size=MIN_AREA)

    # 4. Labeling connected component (8-connectivity agar goresan
    #    diagonal pada huruf yang miring tetap menyatu)
    label_img = measure.label(bw, connectivity=2)

    # 5. regionprops: ambil properti tiap region (bounding box, area, dll.)
    regions = measure.regionprops(label_img)

    # Buang region yang terlalu besar untuk berupa satu karakter
    # (misalnya garis tepi/border gambar yang ikut terdeteksi)
    H, W = bw.shape
    regions = [
        r for r in regions
        if (r.bbox[2] - r.bbox[0]) < 0.5 * H      # tinggi
        and (r.bbox[3] - r.bbox[1]) < 0.5 * W     # lebar
    ]
    print(f"Jumlah karakter terdeteksi: {len(regions)}")

    # Urutkan sesuai urutan baca: baris teks dari atas ke bawah,
    # tiap baris dari kiri ke kanan
    regions = urutkan_baris_teks(regions, bw.shape)

    # 6. Simpan tiap karakter sebagai gambar terpisah
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(bw, cmap="gray")

    for i, r in enumerate(regions, start=1):
        minr, minc, maxr, maxc = r.bbox

        # r.image = mask biner region saja (piksel karakter lain yang
        # kebetulan masuk bounding box tidak ikut terpotong)
        char = (r.image * 255).astype(np.uint8)
        char = np.pad(char, PADDING, mode="constant", constant_values=0)

        io.imsave(os.path.join(OUTPUT_DIR, f"karakter_{i:02d}.png"),
                  char, check_contrast=False)

        # Gambar kotak bounding box pada citra untuk visualisasi
        ax.add_patch(plt.Rectangle((minc - 0.5, minr - 0.5),
                                   maxc - minc, maxr - minr,
                                   edgecolor="red", fill=False, linewidth=1))
        ax.text(minc, minr - 2, str(i), color="yellow", fontsize=7)

    ax.set_title(f"Hasil segmentasi: {len(regions)} karakter")
    ax.axis("off")
    plt.savefig(os.path.join(OUTPUT_DIR, "_visualisasi_bbox.png"),
                dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()