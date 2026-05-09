"""Source extractor — converts PDF / URL into plain text material.

Owner: Ravi (frontend coordinator pulled this in for multi-source support).

Responsibilities:
    1. PDF: extract text using pypdf (text-PDFs only; no OCR for image-PDFs)
    2. URL: fetch + extract article body using trafilatura (handles boilerplate)

After extraction, the resulting text feeds into the existing quiz_generator
service exactly like raw text input would.
"""

from __future__ import annotations

import io
import logging
from typing import Optional

import httpx

from app.utils.errors import ApiException

logger = logging.getLogger(__name__)

# Reuse the same min/max length as raw text input
MIN_LENGTH = 100
MAX_LENGTH = 20_000

# URL fetch timeout
URL_FETCH_TIMEOUT_SECONDS = 15.0
URL_USER_AGENT = (
    "Mozilla/5.0 (compatible; AsahlagiBot/1.0; capstone TP-G005)"
)


# Error codes (extend the central registry)
PDF_INVALID = "PDF_INVALID"
PDF_EMPTY = "PDF_EMPTY"
PDF_TOO_SHORT = "PDF_TOO_SHORT"
PDF_TOO_LONG = "PDF_TOO_LONG"

URL_INVALID = "URL_INVALID"
URL_FETCH_FAILED = "URL_FETCH_FAILED"
URL_EMPTY_CONTENT = "URL_EMPTY_CONTENT"
URL_TOO_SHORT = "URL_TOO_SHORT"
URL_TOO_LONG = "URL_TOO_LONG"


# ============================================================================
# PDF
# ============================================================================


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract plain text from a PDF byte stream.

    Returns concatenated text from all pages. Suitable for text-PDFs.
    For scanned/image PDFs, no text is returned (no OCR — out of scope).

    Raises:
        ApiException(PDF_INVALID): file is corrupt or unreadable
        ApiException(PDF_EMPTY): no extractable text (likely scanned image PDF)
        ApiException(PDF_TOO_SHORT/PDF_TOO_LONG): length out of range
    """
    if not pdf_bytes:
        raise ApiException(
            status_code=400,
            code=PDF_INVALID,
            detail="File PDF kosong atau tidak terbaca.",
        )

    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        chunks: list[str] = []
        for page in reader.pages:
            try:
                chunks.append(page.extract_text() or "")
            except Exception as exc:  # noqa: BLE001
                logger.warning("source_extractor: page extract failed: %s", exc)
                continue
        text = "\n".join(c.strip() for c in chunks if c.strip())
    except ApiException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.warning("source_extractor: PDF parse failed: %s", exc)
        raise ApiException(
            status_code=400,
            code=PDF_INVALID,
            detail="File PDF tidak bisa diproses. Pastikan file PDF valid.",
        ) from exc

    text = text.strip()
    if not text:
        raise ApiException(
            status_code=400,
            code=PDF_EMPTY,
            detail=(
                "Tidak ada teks yang bisa diekstrak dari PDF ini. "
                "Mungkin PDF berupa scan/gambar — coba ketik ulang materinya."
            ),
        )

    return _validate_length(text, code_short=PDF_TOO_SHORT, code_long=PDF_TOO_LONG)


# ============================================================================
# URL
# ============================================================================


def extract_text_from_url(url: str) -> str:
    """Fetch a URL and extract the main article body.

    Uses trafilatura for boilerplate removal (ads, nav, comments stripped).

    Raises:
        ApiException(URL_INVALID): malformed URL
        ApiException(URL_FETCH_FAILED): network error / non-2xx response
        ApiException(URL_EMPTY_CONTENT): no extractable article content
        ApiException(URL_TOO_SHORT/URL_TOO_LONG): length out of range
    """
    url = url.strip()
    if not url:
        raise ApiException(
            status_code=400,
            code=URL_INVALID,
            detail="URL tidak boleh kosong.",
        )
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ApiException(
            status_code=400,
            code=URL_INVALID,
            detail="URL harus dimulai dengan http:// atau https://",
        )

    try:
        with httpx.Client(
            timeout=URL_FETCH_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": URL_USER_AGENT},
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            html = response.text
    except httpx.HTTPError as exc:
        logger.warning("source_extractor: URL fetch failed for %s: %s", url, exc)
        raise ApiException(
            status_code=400,
            code=URL_FETCH_FAILED,
            detail=(
                "Gagal mengambil konten dari URL. "
                "Pastikan URL valid dan halaman bisa diakses publik."
            ),
        ) from exc

    text = _extract_article_with_trafilatura(html)
    if not text:
        raise ApiException(
            status_code=400,
            code=URL_EMPTY_CONTENT,
            detail=(
                "Tidak ada konten artikel yang bisa diambil dari halaman ini. "
                "Halaman mungkin butuh login atau isinya kebanyakan gambar/video."
            ),
        )

    return _validate_length(text, code_short=URL_TOO_SHORT, code_long=URL_TOO_LONG)


def _extract_article_with_trafilatura(html: str) -> Optional[str]:
    """Run trafilatura on raw HTML to get the main article text."""
    try:
        import trafilatura

        # include_comments=False strips comment sections;
        # include_tables=True keeps tabular data which is often informative.
        result = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        )
        return result.strip() if result else None
    except Exception as exc:  # noqa: BLE001
        logger.warning("source_extractor: trafilatura extract failed: %s", exc)
        return None


# ============================================================================
# Shared validation
# ============================================================================


def _validate_length(text: str, *, code_short: str, code_long: str) -> str:
    """Apply min/max length validation. Raises with the given error codes."""
    if len(text) < MIN_LENGTH:
        raise ApiException(
            status_code=400,
            code=code_short,
            detail=(
                f"Teks yang berhasil diekstrak terlalu pendek "
                f"({len(text)} karakter). Minimal {MIN_LENGTH} karakter."
            ),
        )
    if len(text) > MAX_LENGTH:
        # Don't reject — truncate. User experience smoother than hard error.
        logger.info(
            "source_extractor: truncating text from %d to %d chars",
            len(text),
            MAX_LENGTH,
        )
        text = text[:MAX_LENGTH]
    return text
