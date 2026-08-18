"""The per-material seed must survive a process restart.

The generators promise that the same material yields the same quiz. That held
only inside one process while the seed came from `hash(text)`, because Python
salts str hashing per interpreter. A sleeping Space restarts constantly, so
the promise was broken in the normal case, silently: quizzes still came out,
just different ones.
"""

from __future__ import annotations

import subprocess
import sys

from ml.generator.inference import stable_seed

MATERIAL = "Fotosintesis berlangsung di kloroplas dan menghasilkan glukosa serta oksigen."


def test_seed_sama_dalam_satu_proses():
    assert stable_seed(MATERIAL) == stable_seed(MATERIAL)


def test_materi_berbeda_memberi_seed_berbeda():
    assert stable_seed(MATERIAL) != stable_seed(MATERIAL + " Cahaya matahari diperlukan.")


def test_seed_bertahan_melintasi_proses():
    """Inti perbaikannya, dan satu-satunya cara mengujinya adalah proses baru.

    Dijalankan dua kali dengan PYTHONHASHSEED acak (default CPython), yang
    persis kondisi yang dulu membuat hasilnya berbeda tiap restart.
    """
    code = (
        "from ml.generator.inference import stable_seed;"
        f"print(stable_seed({MATERIAL!r}))"
    )
    hasil = set()
    for seed_env in ("1", "2"):
        out = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            env={"PYTHONHASHSEED": seed_env, "PATH": "/usr/bin:/bin", "PYTHONPATH": "."},
            cwd=".",
        )
        assert out.returncode == 0, out.stderr[-400:]
        hasil.add(out.stdout.strip())
    assert len(hasil) == 1, f"seed berubah antar proses: {hasil}"


def test_hash_bawaan_memang_tidak_stabil():
    """Menjelaskan kenapa test di atas ada, bukan sekadar paranoia."""
    code = f"print(hash({MATERIAL!r}))"
    hasil = set()
    for seed_env in ("1", "2"):
        out = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            env={"PYTHONHASHSEED": seed_env, "PATH": "/usr/bin:/bin"},
        )
        hasil.add(out.stdout.strip())
    assert len(hasil) == 2, "hash() ternyata stabil di sini; anggapan di komentar perlu ditinjau"
