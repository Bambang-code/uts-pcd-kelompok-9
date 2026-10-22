"""Soal 3: menghitung koin menurut ukuran menggunakan regionprops.

Asumsi soal: latar seragam dan setiap koin terpisah/tidak bersentuhan.
Ukuran adalah diameter ekuivalen dalam piksel, bukan nilai nominal mata uang.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage
from skimage import color, filters, measure, segmentation, util

SOAL_DIR = Path(__file__).resolve().parent


def baca_citra(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Baca grayscale/RGB/RGBA; transparansi dikompositkan di atas putih."""
    if not path.is_file():
        raise ValueError(f"Berkas citra tidak ditemukan: {path}")
    with Image.open(path) as source:
        source = ImageOps.exif_transpose(source)
        if source.mode in ("RGBA", "LA") or "transparency" in source.info:
            rgba = source.convert("RGBA")
            background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            data = np.asarray(Image.alpha_composite(background, rgba).convert("RGB"))
        elif source.mode in ("1", "L", "I", "F") or source.mode.startswith("I;16"):
            data = np.asarray(source)
        else:
            data = np.asarray(source.convert("RGB"))

    if data.ndim not in (2, 3) or min(data.shape[:2]) < 3:
        raise ValueError("Citra harus berukuran minimal 3 x 3 piksel.")
    if not np.isfinite(data).all():
        raise ValueError("Citra mengandung nilai NaN atau tak hingga.")
    if data.ndim == 3:
        original = util.img_as_float(data)
        gray = color.rgb2gray(original)
    else:
        gray = data.astype(np.float64)
        original = gray.copy()

    low, high = float(gray.min()), float(gray.max())
    if high <= low:
        raise ValueError("Citra seragam seluruhnya; tidak ada koin yang dapat dipisahkan.")
    # Normalisasi membuat ambang Otsu dapat dilaporkan pada rentang 0..1.
    gray = (gray - low) / (high - low)
    if data.ndim == 2:
        original = gray.copy()
    return original, gray


def segmentasi_koin(
    gray: np.ndarray,
    min_area: int,
    *,
    method: str = "otsu",
    marker_low: float = 0.12,
    marker_high: float = 0.6,
) -> tuple[np.ndarray, dict]:
    """Otsu untuk latar seragam; watershed opsional untuk gradien pencahayaan.

    Watershed mengikuti gradien Sobel dari penanda latar dan objek.
    Ambang penanda memakai intensitas ternormalisasi setelah penyesuaian
    polaritas, sehingga objek diharapkan terang. Ambang perlu disesuaikan
    pada foto lain; metode ini tidak menjamin pemisahan koin bersentuhan.
    """
    if method not in ("otsu", "watershed"):
        raise ValueError("Metode segmentasi harus otsu atau watershed.")
    if method == "watershed" and not (0 <= marker_low < marker_high <= 1):
        raise ValueError("Penanda harus memenuhi 0 <= marker-low < marker-high <= 1.")
    threshold = float(filters.threshold_otsu(gray))
    bright = gray > threshold
    border = np.concatenate((bright[0], bright[-1], bright[1:-1, 0], bright[1:-1, -1]))
    background_is_bright = float(border.mean()) >= 0.5
    foreground = ~bright if background_is_bright else bright
    marker_metadata = {}
    if method == "watershed":
        contrast = 1.0 - gray if background_is_bright else gray
        markers = np.zeros(gray.shape, dtype=np.int32)
        markers[contrast < marker_low] = 1  # Latar yang diyakini.
        markers[contrast > marker_high] = 2  # Bagian terang dalam koin.
        if not np.any(markers == 1) or not np.any(markers == 2):
            raise ValueError(
                "Penanda latar atau objek kosong; sesuaikan --marker-low dan --marker-high."
            )
        foreground = segmentation.watershed(filters.sobel(contrast), markers) == 2
        marker_metadata = {
            "ambang_penanda_latar": marker_low,
            "ambang_penanda_objek": marker_high,
            "jumlah_piksel_penanda_latar": int(np.count_nonzero(markers == 1)),
            "jumlah_piksel_penanda_objek": int(np.count_nonzero(markers == 2)),
            "gradien": "Sobel",
        }
    foreground = ndimage.binary_fill_holes(foreground)

    initial_labels = measure.label(foreground, connectivity=2)
    areas = np.bincount(initial_labels.ravel())
    keep = areas >= min_area
    keep[0] = False
    mask = keep[initial_labels]
    labels = measure.label(mask, connectivity=2)
    if labels.max() == 0:
        raise ValueError(
            "Tidak ada koin setelah penyaringan luas. Periksa citra atau turunkan --min-area."
        )

    metadata = {
        "metode": (
            "Watershed gradien Sobel + penanda intensitas + polaritas bingkai"
            " + isi lubang + filter luas + komponen 8-tetangga"
            if method == "watershed" else
            "Otsu + polaritas bingkai + isi lubang + filter luas + komponen 8-tetangga"
        ),
        "ambang_otsu_gray_normalisasi": threshold,
        "latar": "terang" if background_is_bright else "gelap",
        "fraksi_bingkai_terang": float(border.mean()),
        "luas_minimum_px2": min_area,
        "jumlah_komponen_dibuang": int(np.count_nonzero(areas[1:] < min_area)),
        **marker_metadata,
    }
    return labels, metadata


def ukur_objek(labels: np.ndarray) -> list[dict]:
    """Ukur setiap komponen dengan skimage.measure.regionprops."""
    objects = []
    for region in measure.regionprops(labels):
        y, x = region.centroid
        y_min, x_min, y_max, x_max = region.bbox
        objects.append(
            {
                "id_objek": int(region.label),
                "kelompok_ukuran": 0,
                "luas_px2": int(region.area),
                "diameter_ekuivalen_px": float(region.equivalent_diameter_area),
                "centroid_x_px": float(x),
                "centroid_y_px": float(y),
                "bbox_x_min_px": int(x_min),
                "bbox_y_min_px": int(y_min),
                "bbox_x_max_eksklusif_px": int(x_max),
                "bbox_y_max_eksklusif_px": int(y_max),
            }
        )
    return objects


def kelompokkan_ukuran(objects: list[dict], tolerance: float) -> list[dict]:
    """Kelompokkan diameter kecil ke besar dengan toleransi relatif median.

    Calon koin ditambahkan ke kelompok terakhir hanya jika SETIAP diameter
    dalam calon kelompok berjarak <= tolerance * median calon kelompok.
    Aturan ini deterministik dan membatasi efek rantai ukuran yang berdekatan.
    Nomor kelompok 1 selalu menunjukkan ukuran terkecil.
    """
    ordered = sorted(objects, key=lambda item: (item["diameter_ekuivalen_px"], item["id_objek"]))
    groups: list[list[dict]] = []
    for obj in ordered:
        if not groups:
            groups.append([obj])
            continue
        candidate = groups[-1] + [obj]
        diameters = np.array([item["diameter_ekuivalen_px"] for item in candidate])
        median = float(np.median(diameters))
        if np.all(np.abs(diameters - median) <= tolerance * median + 1e-12):
            groups[-1].append(obj)
        else:
            groups.append([obj])

    summaries = []
    for size_id, group in enumerate(groups, start=1):
        for obj in group:
            obj["kelompok_ukuran"] = size_id
        diameters = [obj["diameter_ekuivalen_px"] for obj in group]
        summaries.append(
            {
                "kelompok_ukuran": size_id,
                "jumlah_koin": len(group),
                "diameter_median_px": float(np.median(diameters)),
                "diameter_rata_rata_px": float(np.mean(diameters)),
                "diameter_min_px": float(np.min(diameters)),
                "diameter_max_px": float(np.max(diameters)),
                "id_objek": sorted(obj["id_objek"] for obj in group),
            }
        )
    return summaries


def gambar_anotasi(ax, original: np.ndarray, objects: list[dict]) -> None:
    """Tampilkan ID objek dan kelompok ukuran pada pusat masing-masing koin."""
    ax.imshow(original, cmap="gray", vmin=0, vmax=1)
    palette = plt.get_cmap("tab10")
    for obj in objects:
        size_id = obj["kelompok_ukuran"]
        x, y = obj["centroid_x_px"], obj["centroid_y_px"]
        radius = obj["diameter_ekuivalen_px"] / 2
        ax.add_patch(plt.Circle((x, y), radius, fill=False, color=palette((size_id - 1) % 10), lw=1))
        ax.text(
            x,
            y,
            f'{obj["id_objek"]}/K{size_id}',
            ha="center",
            va="center",
            fontsize=5,
            color="white",
            bbox={"facecolor": "black", "alpha": 0.65, "pad": 0.5, "edgecolor": "none"},
        )
    ax.set_axis_off()


def simpan_hasil(
    output_dir: Path,
    original: np.ndarray,
    labels: np.ndarray,
    objects: list[dict],
    summary: dict,
) -> None:
    """Simpan citra, pengukuran tanpa pembulatan, dan ringkasan yang dapat diaudit."""
    output_dir.mkdir(parents=True, exist_ok=True)
    Image.fromarray(((labels > 0) * 255).astype(np.uint8)).save(output_dir / "mask_koin.png")
    colored_labels = color.label2rgb(labels, bg_label=0, bg_color=(0, 0, 0))
    Image.fromarray(util.img_as_ubyte(colored_labels)).save(output_dir / "label_koin.png")

    height, width = labels.shape
    scale = min(14 / max(height, width), 1 / 100)
    fig, ax = plt.subplots(figsize=(max(width * scale, 4), max(height * scale, 4)))
    gambar_anotasi(ax, original, objects)
    ax.set_title(f'{len(objects)} koin; label = ID/Kelompok ukuran', fontsize=10)
    fig.tight_layout()
    fig.savefig(output_dir / "anotasi_koin.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes[0].imshow(original, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("Citra masukan")
    axes[1].imshow(labels > 0, cmap="gray", vmin=0, vmax=1)
    axes[1].set_title("Mask koin (putih = objek)")
    gambar_anotasi(axes[2], original, objects)
    axes[2].set_title(f'{len(objects)} koin / {summary["jumlah_kelompok_ukuran"]} ukuran')
    for ax in axes:
        ax.set_axis_off()
    counts = "; ".join(f'K{g["kelompok_ukuran"]}: {g["jumlah_koin"]}' for g in summary["kelompok_ukuran"])
    fig.suptitle(f"Hasil soal 3 — {counts}", fontsize=11, wrap=True)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(output_dir / "ringkasan_visual.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    with (output_dir / "objek_koin.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(objects[0]))
        writer.writeheader()
        writer.writerows(objects)
    with (output_dir / "ringkasan.json").open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=SOAL_DIR / "data" / "koin_100.png", help="Citra koin masukan.")
    parser.add_argument("--output-dir", type=Path, default=SOAL_DIR / "hasil", help="Folder hasil.")
    parser.add_argument(
        "--method", choices=("otsu", "watershed"), default="otsu",
        help="Otsu untuk soal utama; watershed untuk uji tambahan pencahayaan tidak merata.",
    )
    parser.add_argument("--marker-low", type=float, default=0.12, help="Ambang penanda latar watershed (0..1).")
    parser.add_argument("--marker-high", type=float, default=0.6, help="Ambang penanda objek watershed (0..1).")
    parser.add_argument(
        "--size-tolerance", type=float, default=0.08,
        help="Toleransi relatif diameter terhadap median kelompok; 0.08 berarti 8%% (default).",
    )
    parser.add_argument("--min-area", type=int, default=50, help="Luas minimum objek dalam piksel (default: 50).")
    parser.add_argument(
        "--expected-count", type=int, default=100,
        help="Jumlah koin yang diharapkan; hanya untuk peringatan, 0 menonaktifkan (default: 100).",
    )
    args = parser.parse_args(argv)
    if not np.isfinite(args.size_tolerance) or not 0 <= args.size_tolerance < 1:
        parser.error("--size-tolerance harus bernilai 0 sampai kurang dari 1.")
    if args.min_area < 1:
        parser.error("--min-area harus minimal 1.")
    if args.expected_count < 0:
        parser.error("--expected-count tidak boleh negatif.")

    try:
        original, gray = baca_citra(args.input)
        labels, segmentation_info = segmentasi_koin(
            gray, args.min_area, method=args.method,
            marker_low=args.marker_low, marker_high=args.marker_high,
        )
        objects = ukur_objek(labels)
        groups = kelompokkan_ukuran(objects, args.size_tolerance)
        warnings = []
        if args.expected_count and len(objects) != args.expected_count:
            warnings.append(
                f"Terdeteksi {len(objects)} koin; jumlah yang diharapkan {args.expected_count}. "
                "Periksa mask, min-area, serta apakah ada koin bersentuhan."
            )
        input_label = args.input.resolve()
        try:
            input_label = input_label.relative_to(SOAL_DIR.parent)
        except ValueError:
            pass
        summary = {
            "soal": 3,
            "input": input_label.as_posix(),
            "tinggi_citra_px": int(labels.shape[0]),
            "lebar_citra_px": int(labels.shape[1]),
            "asumsi": (
                "Koin utuh dan terpisah pada latar polos dengan gradien pencahayaan; "
                "penanda intensitas harus sesuai; ukuran pada skala citra yang sama."
                if args.method == "watershed" else
                "Latar seragam, koin terpisah, ukuran dibandingkan pada skala citra yang sama."
            ),
            "jumlah_koin": len(objects),
            "jumlah_diharapkan": args.expected_count if args.expected_count else None,
            "jumlah_sesuai_harapan": len(objects) == args.expected_count if args.expected_count else None,
            "jumlah_kelompok_ukuran": len(groups),
            "definisi_ukuran": "Diameter ekuivalen = sqrt(4 * luas / pi), satuan piksel.",
            "metode_pengelompokan": "Urut diameter menaik; semua anggota berjarak <= toleransi * median calon kelompok.",
            "toleransi_ukuran_relatif": args.size_tolerance,
            "segmentasi": segmentation_info,
            "kelompok_ukuran": groups,
            "peringatan": warnings,
            "berkas_hasil": [
                "mask_koin.png", "label_koin.png", "anotasi_koin.png",
                "ringkasan_visual.png", "objek_koin.csv", "ringkasan.json",
            ],
        }
        if args.input.resolve() in {args.output_dir.resolve() / name for name in summary["berkas_hasil"]}:
            raise ValueError("Folder keluaran akan menimpa citra masukan; gunakan --output-dir lain.")
        simpan_hasil(args.output_dir, original, labels, objects, summary)
    except (OSError, ValueError) as exc:
        print(f"Kesalahan: {exc}", file=sys.stderr)
        return 2

    print(f"Jumlah koin terdeteksi: {len(objects)}")
    for group in groups:
        print(
            f'K{group["kelompok_ukuran"]}: {group["jumlah_koin"]} koin, '
            f'diameter median {group["diameter_median_px"]:.2f} px'
        )
    for warning in warnings:
        print(f"Peringatan: {warning}", file=sys.stderr)
    print(f"Hasil tersimpan di: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
