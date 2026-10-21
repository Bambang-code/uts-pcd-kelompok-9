"""Uji penghitungan dan pengelompokan koin untuk nomor 3."""

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from soal3 import main as soal_3


SOAL_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def contoh_koin():
    lokasi = SOAL_DIR / "data" / "koin_100.png"
    metadata = json.loads(
        (SOAL_DIR / "data" / "koin_100_ground_truth.json").read_text(encoding="utf-8")
    )
    return lokasi, metadata


def analisis_koin(lokasi, min_area=50):
    _, gray = soal_3.baca_citra(lokasi)
    labels, metadata = soal_3.segmentasi_koin(gray, min_area)
    objects = soal_3.ukur_objek(labels)
    groups = soal_3.kelompokkan_ukuran(objects, tolerance=0.08)
    return labels, objects, groups, metadata


def periksa_semua_koin(objects, groups, truth, scale=1.0):
    """Cocokkan setiap objek lewat pusat, kemudian periksa ukuran dan kelasnya."""
    assert len(objects) == truth["jumlah_koin"] == 100
    assert [g["jumlah_koin"] for g in groups] == [25, 25, 25, 25]
    centers = np.array([[c["pusat_x"], c["pusat_y"]] for c in truth["koin"]])
    # Pemetaan pusat piksel saat resize PIL, termasuk pergeseran setengah piksel.
    centers = (centers + 0.5) * scale - 0.5
    radii = sorted({c["radius_px"] for c in truth["koin"]})
    pasangan = set()
    for obj in objects:
        posisi = np.array([obj["centroid_x_px"], obj["centroid_y_px"]])
        jarak = np.linalg.norm(centers - posisi, axis=1)
        indeks = int(np.argmin(jarak))
        assert jarak[indeks] < 1.0
        assert indeks not in pasangan, "Satu koin sebenarnya dipasangkan dua kali."
        pasangan.add(indeks)
        koin = truth["koin"][indeks]
        assert obj["diameter_ekuivalen_px"] == pytest.approx(
            2 * koin["radius_px"] * scale, abs=1.2
        )
        assert obj["kelompok_ukuran"] == radii.index(koin["radius_px"]) + 1
    assert len(pasangan) == 100


def test_koin_semua_diameter_dan_kelas_sesuai_ground_truth(contoh_koin):
    lokasi, truth = contoh_koin
    _, objects, groups, metadata = analisis_koin(lokasi)
    assert metadata["latar"] == "gelap"
    periksa_semua_koin(objects, groups, truth)


def test_koin_latar_terang_tetap_mendapat_semua_ukuran(contoh_koin, tmp_path):
    lokasi, truth = contoh_koin
    with Image.open(lokasi) as image:
        inverted = 255 - np.asarray(image)
    lokasi_baru = tmp_path / "latar_terang.png"
    Image.fromarray(inverted).save(lokasi_baru)
    _, objects, groups, metadata = analisis_koin(lokasi_baru)
    assert metadata["latar"] == "terang"
    periksa_semua_koin(objects, groups, truth)


def test_koin_resolusi_setengah_diameter_mengikuti_skala(contoh_koin, tmp_path):
    lokasi, truth = contoh_koin
    lokasi_kecil = tmp_path / "koin_setengah.png"
    with Image.open(lokasi) as image:
        image.resize((image.width // 2, image.height // 2), Image.Resampling.LANCZOS).save(lokasi_kecil)
    _, objects, groups, _ = analisis_koin(lokasi_kecil, min_area=12)
    periksa_semua_koin(objects, groups, truth, scale=0.5)


def test_lubang_diisi_derau_dihapus_dan_jumlah_tidak_dipaksa_100(tmp_path):
    yy, xx = np.mgrid[:240, :240]
    citra = np.full((240, 240), 24, dtype=np.uint8)
    centers = [(40 + 70 * kolom, 40 + 70 * baris) for baris in range(3) for kolom in range(3)]
    for indeks, (x, y) in enumerate(centers):
        radius = 10 if indeks < 7 else 18
        jarak_kuadrat = (xx - x) ** 2 + (yy - y) ** 2
        citra[jarak_kuadrat <= radius**2] = 210
        citra[jarak_kuadrat <= 3**2] = 24
    specks = [(5, 5), (5, 220), (220, 5), (220, 220)]
    for x, y in specks:
        citra[y, x] = 210
    lokasi = tmp_path / "sembilan_koin_berlubang.png"
    Image.fromarray(citra).save(lokasi)
    labels, objects, groups, metadata = analisis_koin(lokasi, min_area=50)
    assert len(objects) == 9
    assert [g["jumlah_koin"] for g in groups] == [7, 2]
    assert metadata["jumlah_komponen_dibuang"] == len(specks)
    for x, y in centers:
        assert labels[y, x] > 0
    for x, y in specks:
        assert labels[y, x] == 0
    for obj in objects:
        ukuran = 20 if obj["kelompok_ukuran"] == 1 else 36
        assert obj["diameter_ekuivalen_px"] == pytest.approx(ukuran, abs=0.3)


def test_baca_koin_menolak_citra_kosong_dan_seragam(tmp_path):
    for nilai in (0, 127, 255):
        lokasi = tmp_path / f"seragam_{nilai}.png"
        Image.fromarray(np.full((20, 20), nilai, dtype=np.uint8)).save(lokasi)
        with pytest.raises(ValueError, match="seragam"):
            soal_3.baca_citra(lokasi)
    kosong = tmp_path / "kosong.png"
    kosong.write_bytes(b"")
    with pytest.raises((OSError, ValueError)):
        soal_3.baca_citra(kosong)
