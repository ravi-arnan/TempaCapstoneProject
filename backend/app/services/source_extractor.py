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
import ipaddress
import logging
import socket
from typing import Optional
from urllib.parse import urlsplit

import httpx

from app.utils.errors import ApiException

logger = logging.getLogger(__name__)

# Reuse the same min/max length as raw text input
MIN_LENGTH = 100
MAX_LENGTH = 20_000

# URL fetch timeout
URL_FETCH_TIMEOUT_SECONDS = 15.0

# Redirects are followed by hand so every hop can be re-checked. Following them
# inside httpx would let a public URL bounce to an internal one unchecked.
URL_MAX_REDIRECTS = 4
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
        import pdfplumber

        chunks: list[str] = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                try:
                    # pdfplumber handles multi-column and basic tables much better
                    # We extract text, and it usually preserves tabular layout
                    text_page = page.extract_text() or ""
                    chunks.append(text_page)
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

    # 1. Try lightweight extraction first (httpx)
    text = None
    fallback_to_playwright = False
    try:
        html = _fetch_html(url)
        text = _extract_article_with_trafilatura(html)

        if not text or len(text) < MIN_LENGTH:
            logger.info("source_extractor: lightweight extraction insufficient, falling back to Playwright for %s", url)
            fallback_to_playwright = True
    except ApiException:
        # A refused address is the caller's answer, not a reason to retry the
        # same address through a browser.
        raise
    except Exception as exc:
        logger.info("source_extractor: lightweight fetch failed (%s), falling back to Playwright for %s", exc, url)
        fallback_to_playwright = True

    # 2. Fallback to Playwright if needed
    if fallback_to_playwright:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    context = browser.new_context(user_agent=URL_USER_AGENT)
                    context.route("**/*", _block_private_requests)
                    page = context.new_page()
                    page.goto(
                        url, 
                        timeout=URL_FETCH_TIMEOUT_SECONDS * 1000,
                        wait_until="domcontentloaded"
                    )
                    # Auto-scroll to trigger lazy-loaded content
                    page.evaluate("""
                        var scrollInterval = setInterval(function() {
                            window.scrollBy(0, window.innerHeight);
                        }, 200);
                        window.setTimeout(function() {
                            clearInterval(scrollInterval);
                        }, 2000);
                    """)
                    page.wait_for_timeout(2500)
                    html = page.content()
                finally:
                    browser.close()
                
                playwright_text = _extract_article_with_trafilatura(html)
                if playwright_text:
                    text = playwright_text
        except ImportError:
            logger.warning("source_extractor: Playwright not installed. Skipping SPA fallback for %s", url)
        except Exception as exc:
            logger.warning("source_extractor: Playwright fallback failed for %s: %s", url, exc)

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


def _assert_public_url(url: str) -> None:
    """Refuse anything that is not a public http(s) address.

    /quiz/generate-from-url takes a URL from an unauthenticated caller and the
    server fetches it, so without this check the endpoint is a request forgery
    primitive: it will happily read loopback services, the container's own
    ports, private LAN ranges, and cloud metadata at 169.254.169.254, and hand
    the contents back rendered as quiz questions.

    `is_global` is the one flag that covers loopback, private, link-local,
    reserved and unspecified in a single test, for IPv4 and IPv6 alike.

    Known limit: the name is resolved here and connected to separately, so a
    DNS entry that changes between the two calls could still slip through.
    Closing that needs pinning the connection to the resolved address, which
    httpx does not expose cleanly; the checks below stop the whole realistic
    range of hand-typed internal URLs.
    """
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise ApiException(
            status_code=400,
            code=URL_INVALID,
            detail="URL harus dimulai dengan http:// atau https://",
        )
    host = parts.hostname
    if not host:
        raise ApiException(
            status_code=400,
            code=URL_INVALID,
            detail="URL tidak memuat nama host yang sah.",
        )

    port = parts.port or (443 if parts.scheme == "https" else 80)
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError, ValueError) as exc:
        raise ApiException(
            status_code=400,
            code=URL_FETCH_FAILED,
            detail="Alamat URL tidak bisa ditemukan. Cek kembali linknya.",
        ) from exc

    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global or address.is_multicast:
            logger.warning("source_extractor: refused non-public target %s (%s)", host, address)
            raise ApiException(
                status_code=400,
                code=URL_INVALID,
                detail="URL itu menunjuk ke alamat internal, jadi tidak bisa diambil.",
            )


def _fetch_html(url: str) -> str:
    """Fetch a page, validating the target before every hop.

    Redirects are walked by hand: httpx following them itself would let a
    public URL hand off to an internal one without any further check.
    """
    with httpx.Client(
        timeout=URL_FETCH_TIMEOUT_SECONDS,
        headers={"User-Agent": URL_USER_AGENT},
        follow_redirects=False,
    ) as client:
        current = url
        for _ in range(URL_MAX_REDIRECTS):
            _assert_public_url(current)
            resp = client.get(current)
            if resp.is_redirect:
                location = resp.headers.get("location")
                if not location:
                    raise ApiException(
                        status_code=400,
                        code=URL_FETCH_FAILED,
                        detail="Halaman itu membalas redirect yang tidak lengkap.",
                    )
                current = str(httpx.URL(current).join(location))
                continue
            resp.raise_for_status()
            return resp.text

    raise ApiException(
        status_code=400,
        code=URL_FETCH_FAILED,
        detail="Terlalu banyak pengalihan pada URL itu.",
    )


def _block_private_requests(route) -> None:
    """Playwright route guard, same rule as the httpx path.

    The browser resolves and follows on its own, so the check has to sit on
    every request it makes rather than only on the URL we were given.
    """
    try:
        _assert_public_url(route.request.url)
    except ApiException:
        route.abort()
        return
    route.continue_()


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
