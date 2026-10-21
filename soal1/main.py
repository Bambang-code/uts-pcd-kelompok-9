"""Nomor 1: selisih dua respons Laplacian of Gaussian (LoG).

Nilai utama disimpan sebagai float64 di .npy. PNG hanya visualisasi dengan
skala bersama; pengurangan dilakukan sebelum normalisasi tampilan.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_laplace
from skimage import color, io, util

SOAL_DIR = Path(__file__).resolve().parent


def baca_grayscale(path: Path) -> np.ndarray:
    """Baca grayscale/RGB/RGBA, hasil intensitas float64 dalam [0, 1]."""
    citra = util.img_as_float64(io.imread(path))
    if citra.ndim == 3 and citra.shape[-1] == 4:
        citra = color.rgba2rgb(citra)  # Komposit transparansi ke putih.
    if citra.ndim == 3 and citra.shape[-1] == 3:
        citra = color.rgb2gray(citra)
    if citra.ndim != 2 or citra.size == 0:
        raise ValueError("Masukan harus berupa satu citra grayscale, RGB, atau RGBA.")
    if not np.isfinite(citra).all() or citra.min() < 0 or citra.max() > 1:
        raise ValueError("Intensitas citra harus finite dan berada dalam [0, 1].")
    return citra


def hitung_selisih_log(
    citra: np.ndarray, sigma_1: float = 0.1, sigma_2: float = 0.2
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Hitung im1, im2, dan im1 - im2 tanpa clipping/normalisasi respons.

    Sigma bersatuan piksel. Mode reflect dipakai di batas citra.
    Konversi float mencegah overflow dan hilangnya respons negatif.
    """
    citra = util.img_as_float64(np.asarray(citra))
    if citra.ndim != 2 or citra.size == 0 or not np.isfinite(citra).all():
        raise ValueError("Citra harus berupa matriks 2D berisi nilai finite.")
    if not all(np.isfinite(s) and s > 0 for s in (sigma_1, sigma_2)):
        raise ValueError("Standar deviasi harus positif dan finite.")
    im1 = gaussian_laplace(citra, sigma=sigma_1, mode="reflect")
    im2 = gaussian_laplace(citra, sigma=sigma_2, mode="reflect")
    hasil = im1 - im2
    return im1, im2, hasil


def simpan_hasil(
    citra: np.ndarray,
    im1: np.ndarray,
    im2: np.ndarray,
    hasil: np.ndarray,
    output_dir: Path,
    input_path: Path,
    sigma_1: float,
    sigma_2: float,
) -> None:
    """Simpan data numerik, pratinjau, panel perbandingan, dan metadata."""
    output_dir.mkdir(parents=True, exist_ok=True)
    batas = max(float(np.max(np.abs(a))) for a in (im1, im2, hasil)) or 1.0
    Image.fromarray(np.rint(citra * 255).astype(np.uint8)).save(output_dir / "grayscale.png")
    statistik = {}
    for nama, array in (("im1", im1), ("im2", im2), ("hasil", hasil)):
        np.save(output_dir / f"{nama}.npy", array)
        preview = np.rint(255 * (np.clip(array / batas, -1, 1) + 1) / 2)
        Image.fromarray(preview.astype(np.uint8)).save(output_dir / f"{nama}.png")
        statistik[nama] = {"min": float(array.min()), "max": float(array.max())}

    fig, axes = plt.subplots(1, 4, figsize=(14, 4.3), layout="constrained")
    axes[0].imshow(citra, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("Citra grayscale")
    judul = (f"im1: LoG sigma={sigma_1:g}", f"im2: LoG sigma={sigma_2:g}", "hasil = im1 - im2")
    for ax, array, title in zip(axes[1:], (im1, im2, hasil), judul):
        respons = ax.imshow(array, cmap="gray", vmin=-batas, vmax=batas)
        ax.set_title(title)
    for ax in axes:
        ax.axis("off")
    fig.colorbar(respons, ax=list(axes[1:]), shrink=0.6, label="Respons LoG (skala bersama)")
    fig.suptitle("Nomor 1 - Selisih Laplacian of Gaussian")
    fig.savefig(output_dir / "perbandingan.png", dpi=150)
    plt.close(fig)

    input_label = input_path.resolve()
    try:
        input_label = input_label.relative_to(SOAL_DIR.parent)
    except ValueError:
        pass
    metadata = {
        "input": input_label.as_posix(),
        "shape": list(citra.shape),
        "sigma_1_px": sigma_1,
        "sigma_2_px": sigma_2,
        "filter": "scipy.ndimage.gaussian_laplace",
        "mode": "reflect",
        "hasil": "im1 - im2 (signed, float64)",
        "png_range": [-batas, batas],
        "png_mapping": "round(255 * (value / bound + 1) / 2); zero = 128",
        "statistik": statistik,
        "catatan": "Sigma < 0.5 piksel dapat menghasilkan bias DC akibat sampling kernel; lihat LAPORAN.md.",
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=SOAL_DIR / "data" / "citra_uji.png")
    parser.add_argument("--output-dir", type=Path, default=SOAL_DIR / "hasil")
    parser.add_argument("--sigma-1", type=float, default=0.1)
    parser.add_argument("--sigma-2", type=float, default=0.2)
    args = parser.parse_args()
    try:
        nama_hasil = {"grayscale.png", "perbandingan.png", "metadata.json"}
        nama_hasil.update(f"{nama}.{ext}" for nama in ("im1", "im2", "hasil") for ext in ("npy", "png"))
        if args.input.resolve() in {args.output_dir.resolve() / nama for nama in nama_hasil}:
            raise ValueError("Folder keluaran akan menimpa citra masukan; gunakan --output-dir lain.")
        citra = baca_grayscale(args.input)
        im1, im2, hasil = hitung_selisih_log(citra, args.sigma_1, args.sigma_2)
        simpan_hasil(citra, im1, im2, hasil, args.output_dir, args.input, args.sigma_1, args.sigma_2)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Gagal: {exc}\n")
    print(f"Selesai: im1 (sigma={args.sigma_1:g}), im2 (sigma={args.sigma_2:g}), hasil = im1 - im2.")
    print(f"Data .npy dan visualisasi .png tersimpan di {args.output_dir}")
    if min(args.sigma_1, args.sigma_2) < 0.5:
        print("Catatan: sigma sangat kecil; baca pembahasan sampling kernel di LAPORAN.md.")


if __name__ == "__main__":
    main()
