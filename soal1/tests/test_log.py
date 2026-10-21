"""Uji numerik filter LoG dan selisih respons untuk nomor 1."""

import numpy as np
from PIL import Image

from soal1 import main as soal_1


def test_log_sigma_kecil_sesuai_solusi_analitik():
    # Sigma 0.1 memiliki radius kernel diskrit nol. Di dua dimensi,
    # turunan kedua pusat adalah -2 * intensitas / sigma**2 = -80.
    citra = np.full((9, 11), 0.4)
    im1, _, _ = soal_1.hitung_selisih_log(citra, sigma_1=0.1, sigma_2=0.2)
    np.testing.assert_allclose(im1, -80.0, rtol=0, atol=1e-12)


def test_log_sigma_sama_memberi_selisih_nol_persis():
    citra = np.random.default_rng(17).random((13, 19))
    im1, im2, hasil = soal_1.hitung_selisih_log(citra, 0.7, 0.7)
    np.testing.assert_array_equal(im1, im2)
    np.testing.assert_array_equal(hasil, np.zeros(citra.shape))


def test_log_uint8_tetap_signed_dan_npy_mempertahankan_pengurangan(tmp_path):
    citra = np.zeros((21, 21), dtype=np.uint8)
    citra[10, 10] = 255
    lokasi = tmp_path / "impuls.png"
    Image.fromarray(citra).save(lokasi)
    gray = soal_1.baca_grayscale(lokasi)
    assert gray[10, 10] == 1.0
    im1, im2, hasil = soal_1.hitung_selisih_log(citra, 1.0, 2.0)
    for respons in (im1, im2, hasil):
        assert respons.dtype == np.float64
        assert respons.min() < 0 < respons.max()
    soal_1.simpan_hasil(gray, im1, im2, hasil, tmp_path / "hasil", lokasi, 1.0, 2.0)
    tersimpan = [np.load(tmp_path / "hasil" / f"{nama}.npy") for nama in ("im1", "im2", "hasil")]
    np.testing.assert_array_equal(tersimpan[2], tersimpan[0] - tersimpan[1])
    np.testing.assert_array_equal(tersimpan[2], hasil)
    assert tersimpan[2].min() < 0 < tersimpan[2].max()
