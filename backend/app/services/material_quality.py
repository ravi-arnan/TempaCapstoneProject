"""Lightweight 'quizability' pre-check (ROADMAP §3.2).

The quiz generator is built for Indonesian learning prose. This flags clearly
unsuitable material early (CVs, English text, bare lists) so users get a helpful
hint instead of a nonsensical quiz — before waiting ~15s for generation.

Deliberately conservative: only blocks material that is clearly a poor fit, so
ordinary Indonesian study text always passes.
"""

from __future__ import annotations

import re

# High-frequency Indonesian function words — dense in real prose, ~absent in
# English text or CV/keyword dumps. A low density is a strong "not Indonesian
# prose" signal.
_ID_FUNCTION_WORDS = {
    "yang", "dan", "di", "ke", "dari", "untuk", "adalah", "dengan", "pada",
    "ini", "itu", "atau", "tidak", "akan", "dalam", "sebagai", "oleh", "juga",
    "karena", "jika", "agar", "supaya", "bisa", "dapat", "merupakan", "yaitu",
    "serta", "namun", "tetapi", "sehingga", "maka", "para", "setiap", "ketika",
    "sebuah", "seorang", "lebih", "saat", "secara", "antara", "tersebut",
}

# The generator already enforces a 100-char floor, so this only guards against
# the rare very-short-but-not-empty case; keep it low to avoid false positives.
_MIN_WORDS = 20
_MIN_ID_RATIO = 0.04
_MIN_SENTENCES = 2


def assess(text: str) -> tuple[bool, str | None]:
    """Return (is_suitable, hint). `hint` is a user-facing reason when unsuitable."""
    words = re.findall(r"[a-zA-ZÀ-ÿ]+", text.lower())
    n = len(words)
    if n < _MIN_WORDS:
        return False, (
            "Materinya terlalu pendek untuk kuis yang baik. Tambahkan penjelasan "
            "lebih lengkap — minimal beberapa kalimat/paragraf."
        )

    id_ratio = sum(1 for w in words if w in _ID_FUNCTION_WORDS) / n
    if id_ratio < _MIN_ID_RATIO:
        return False, (
            "Materi ini sepertinya bukan teks belajar berbahasa Indonesia (mis. CV, "
            "daftar poin, atau berbahasa Inggris), jadi kuisnya kurang akurat. Coba "
            "tempel materi berupa paragraf penjelasan dalam Bahasa Indonesia."
        )

    sentences = [s for s in re.split(r"[.!?]+", text) if len(s.split()) >= 4]
    if len(sentences) < _MIN_SENTENCES:
        return False, (
            "Materi ini kurang berupa kalimat penjelasan (lebih mirip daftar/poin). "
            "Coba tempel materi berupa paragraf agar kuisnya lebih relevan."
        )

    return True, None
