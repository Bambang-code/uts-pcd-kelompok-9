"""Pengujian tambahan watershed; jumlah saja tidak cukup untuk validasi."""

from pathlib import Path

import numpy as np
import pytest

from soal3 import main as soal_3


@pytest.mark.parametrize("inverted", [False, True])
def test_watershed_koin_pada_gradien_latar(inverted):
    yy, xx = np.mgrid[:240, :330]
    gray = 0.02 + 0.38 * xx / 329 + 0.05 * yy / 239
    truth = np.zeros(gray.shape, dtype=bool)
    centers = [(55, 65, 18), (160, 65, 25), (270, 65, 18),
               (95, 180, 25), (240, 180, 18)]
    for x, y, radius in centers:
        truth |= (xx - x) ** 2 + (yy - y) ** 2 <= radius**2
    gray[truth] = 0.9
    gray = (gray - gray.min()) / (gray.max() - gray.min())
    if inverted:
        gray = 1 - gray
    labels, _ = soal_3.segmentasi_koin(gray, 50, method="watershed")
    assert labels.max() == len(centers)
    assert len({labels[y, x] for x, y, _ in centers}) == len(centers)
    assert all(labels[y, x] > 0 for x, y, _ in centers)
    mask = labels > 0
    assert np.count_nonzero(mask & truth) / np.count_nonzero(mask | truth) > 0.94


def test_watershed_foto_nyata_setiap_koin_terpisah_dari_latar():
    path = Path(__file__).resolve().parents[1] / "data/koin_nyata_scikit.png"
    _, gray = soal_3.baca_citra(path)
    labels, _ = soal_3.segmentasi_koin(gray, 50, method="watershed")
    # Pusat acuan ditandai secara visual pada foto asli, bukan diambil dari output.
    centers = [(44, 54), (100, 56), (155, 51), (215, 51), (276, 52), (335, 44),
               (45, 124), (102, 126), (154, 127), (205, 124), (271, 119), (336, 125),
               (44, 197), (102, 196), (154, 198), (212, 193), (274, 194), (347, 187),
               (46, 260), (114, 266), (172, 261), (244, 263), (301, 263), (358, 268)]
    objects = soal_3.ukur_objek(labels)
    assert len(objects) == 24
    matched = set()
    for x, y in centers:
        label = int(labels[y, x])
        assert label > 0 and label not in matched
        matched.add(label)
        obj = next(o for o in objects if o["id_objek"] == label)
        assert np.hypot(obj["centroid_x_px"] - x, obj["centroid_y_px"] - y) < 3
        assert obj["bbox_x_min_px"] > 0 and obj["bbox_y_min_px"] > 0
        assert obj["bbox_x_max_eksklusif_px"] < gray.shape[1]
        assert obj["bbox_y_max_eksklusif_px"] < gray.shape[0]
    assert len(matched) == 24


def test_watershed_penanda_tidak_valid_ditolak():
    gray = np.linspace(0, 1, 100).reshape(10, 10)
    with pytest.raises(ValueError, match="Penanda harus"):
        soal_3.segmentasi_koin(gray, 1, method="watershed", marker_low=0.8, marker_high=0.2)
    with pytest.raises(ValueError, match="Penanda latar atau objek kosong"):
        soal_3.segmentasi_koin(gray, 1, method="watershed", marker_low=0, marker_high=1)
