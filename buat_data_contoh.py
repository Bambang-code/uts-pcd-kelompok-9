"""Membuat citra sintetis yang dapat direproduksi untuk soal UTS nomor 1 dan 3.

Contoh:
    python buat_data_contoh.py
    python buat_data_contoh.py --output-dir contoh_lain --seed 9

Citra koin adalah data simulasi, bukan foto atau dataset koin dunia nyata.
Metadata kebenaran dasar disimpan terpisah untuk pemeriksaan hasil penghitungan.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def buat_citra_uji(rng: np.random.Generator) -> Image.Image:
    """Buat citra abu-abu dengan tepi lurus, lengkung, tekstur, dan derau."""
    lebar, tinggi = 768, 512
    yy, xx = np.mgrid[:tinggi, :lebar]
    latar = 35.0 + 45.0 * xx / (lebar - 1) + 12.0 * yy / (tinggi - 1)
    citra = Image.fromarray(latar.astype(np.uint8), mode="L")
    gambar = ImageDraw.Draw(citra)

    gambar.rectangle((52, 53, 250, 205), fill=214)
    gambar.rectangle((88, 89, 214, 169), fill=115)
    gambar.ellipse((304, 44, 494, 234), fill=177)
    gambar.ellipse((357, 97, 441, 181), fill=77)
    gambar.polygon([(548, 209), (648, 43), (730, 209)], fill=232)
    gambar.line([(52, 247), (250, 247)], fill=246, width=3)
    gambar.line([(278, 273), (461, 475)], fill=207, width=8)
    gambar.rounded_rectangle((515, 292, 728, 463), radius=30, fill=154)
    gambar.ellipse((567, 322, 676, 431), fill=218)

    piksel = np.asarray(citra, dtype=np.float64).copy()
    # Kotak berpola berguna untuk melihat respons LoG terhadap frekuensi spasial.
    tekstur = ((xx[294:470, 51:252] // 16 + yy[294:470, 51:252] // 16) % 2)
    piksel[294:470, 51:252] = 90.0 + 85.0 * tekstur
    piksel += rng.normal(0.0, 2.2, piksel.shape)
    # Ukuran akhir kecil menjaga berkas respons LoG float64 tetap ringan.
    hasil = Image.fromarray(np.clip(np.rint(piksel), 0, 255).astype(np.uint8), mode="L")
    return hasil.resize((384, 256), Image.Resampling.LANCZOS)


def buat_citra_koin(
    rng: np.random.Generator, seed: int
) -> tuple[Image.Image, dict]:
    """Buat tepat 100 lingkaran terpisah, masing-masing 25 pada empat ukuran."""
    sisi = 1100
    piksel = np.full((sisi, sisi), 24.0, dtype=np.float64)
    daftar_radius = np.repeat([13, 18, 23, 28], 25)
    rng.shuffle(daftar_radius)
    data_koin = []

    for nomor, radius in enumerate(daftar_radius, start=1):
        radius = int(radius)
        baris, kolom = divmod(nomor - 1, 10)
        # Jarak pusat minimal 80 px, sedangkan diameter terbesar hanya 56 px.
        # Karena itu jitter ini tidak dapat menyebabkan koin bersentuhan.
        pusat_x = 100 + 100 * kolom + int(rng.integers(-10, 11))
        pusat_y = 100 + 100 * baris + int(rng.integers(-10, 11))
        batas = radius + 2
        yy, xx = np.mgrid[-batas : batas + 1, -batas : batas + 1]
        jarak = np.hypot(xx, yy)
        cakupan = np.clip(radius + 0.5 - jarak, 0.0, 1.0)

        # Semua detail berada di dalam koin. Nilainya tetap jauh lebih terang
        # daripada latar sehingga gambar sesuai untuk latihan segmentasi.
        warna_dasar = float(rng.uniform(181.0, 208.0))
        permukaan = warna_dasar - 18.0 * xx / radius - 12.0 * yy / radius
        permukaan += 7.0 * np.cos(jarak * np.pi / radius)
        permukaan -= 28.0 * np.exp(-((jarak - 0.88 * radius) / 0.7) ** 2)
        permukaan += 9.0 * np.exp(-((jarak - 0.76 * radius) / 0.65) ** 2)
        permukaan -= 10.0 * np.exp(-((jarak - 0.30 * radius) / 0.9) ** 2)
        permukaan += rng.normal(0.0, 1.0, jarak.shape)
        permukaan = np.clip(permukaan, 125.0, 238.0)

        irisan_y = slice(pusat_y - batas, pusat_y + batas + 1)
        irisan_x = slice(pusat_x - batas, pusat_x + batas + 1)
        bagian = piksel[irisan_y, irisan_x]
        bagian[:] = bagian * (1.0 - cakupan) + permukaan * cakupan
        data_koin.append(
            {
                "id": nomor,
                "pusat_x": pusat_x,
                "pusat_y": pusat_y,
                "radius_px": radius,
                "diameter_px": radius * 2,
            }
        )

    metadata = {
        "deskripsi": "Citra koin sintetis; metadata hanya untuk validasi, bukan masukan algoritma.",
        "seed": seed,
        "lebar_px": sisi,
        "tinggi_px": sisi,
        "jumlah_koin": len(data_koin),
        "jumlah_per_radius_px": {str(r): 25 for r in (13, 18, 23, 28)},
        "koin": data_koin,
    }
    hasil = Image.fromarray(np.rint(piksel).astype(np.uint8), mode="L")
    return hasil, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent,
        help="Akar proyek keluaran; data ditulis ke soal1/data dan soal3/data (default: folder skrip).",
    )
    parser.add_argument("--seed", type=int, default=9, help="Seed acak (default: 9).")
    argumen = parser.parse_args()
    if argumen.seed < 0:
        parser.error("--seed harus bilangan bulat nonnegatif.")
    data_soal1 = argumen.output_dir / "soal1" / "data"
    data_soal3 = argumen.output_dir / "soal3" / "data"
    data_soal1.mkdir(parents=True, exist_ok=True)
    data_soal3.mkdir(parents=True, exist_ok=True)

    # Aliran terpisah menjaga data koin tetap sama bila citra LoG dimodifikasi.
    seed_citra, seed_koin = np.random.SeedSequence(argumen.seed).spawn(2)
    citra_uji = buat_citra_uji(np.random.default_rng(seed_citra))
    citra_koin, metadata = buat_citra_koin(np.random.default_rng(seed_koin), argumen.seed)
    citra_uji.save(data_soal1 / "citra_uji.png")
    citra_koin.save(data_soal3 / "koin_100.png")
    lokasi_metadata = data_soal3 / "koin_100_ground_truth.json"
    lokasi_metadata.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Citra LoG: {data_soal1 / 'citra_uji.png'} (384 x 256 px)")
    print(f"Citra koin: {data_soal3 / 'koin_100.png'} (1100 x 1100 px)")
    print(f"Metadata: {lokasi_metadata} (100 koin; 25 per ukuran)")


if __name__ == "__main__":
    main()
