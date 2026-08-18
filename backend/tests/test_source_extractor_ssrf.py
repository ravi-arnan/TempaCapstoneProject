"""SSRF guard for /quiz/generate-from-url.

The endpoint is unauthenticated and makes the server fetch a URL the caller
chose, so the guard is the only thing standing between a stranger and the
container's own network. Offline: DNS is stubbed, nothing here touches the
network.
"""

from __future__ import annotations

import socket

import pytest

from app.services import source_extractor as se
from app.utils.errors import ApiException


def _stub_dns(monkeypatch, mapping: dict[str, str]):
    """Resolve hosts from a table instead of the real resolver."""

    def fake_getaddrinfo(host, port, *args, **kwargs):
        if host not in mapping:
            raise socket.gaierror(f"tidak ada entri untuk {host}")
        return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (mapping[host], port))]

    monkeypatch.setattr(se.socket, "getaddrinfo", fake_getaddrinfo)


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:7860/openapi.json",   # layanan di dalam container
        "http://localhost/admin",
        "http://169.254.169.254/latest/meta-data/",  # metadata cloud
        "http://10.0.0.5/internal",
        "http://192.168.1.1/",
        "http://[::1]/",
        "http://0.0.0.0/",
    ],
)
def test_alamat_internal_ditolak(monkeypatch, url):
    _stub_dns(monkeypatch, {"localhost": "127.0.0.1"})
    with pytest.raises(ApiException) as exc:
        se._assert_public_url(url)
    assert exc.value.status_code == 400


@pytest.mark.parametrize("url", ["file:///etc/passwd", "gopher://x/", "ftp://x/f"])
def test_skema_selain_http_ditolak(url):
    with pytest.raises(ApiException):
        se._assert_public_url(url)


def test_alamat_publik_diterima(monkeypatch):
    _stub_dns(monkeypatch, {"contoh.example": "93.184.216.34"})
    se._assert_public_url("https://contoh.example/artikel")  # tidak melempar


def test_nama_yang_menunjuk_ke_loopback_tetap_ditolak(monkeypatch):
    # Bentuk yang paling mudah luput: hostname terlihat publik, resolusinya
    # mengarah ke dalam.
    _stub_dns(monkeypatch, {"kelihatan-publik.example": "127.0.0.1"})
    with pytest.raises(ApiException):
        se._assert_public_url("http://kelihatan-publik.example/")


def test_redirect_ke_alamat_internal_dihentikan(monkeypatch):
    """Hop kedua harus diperiksa, bukan cuma URL yang dikirim pengguna."""
    _stub_dns(monkeypatch, {"publik.example": "93.184.216.34", "localhost": "127.0.0.1"})

    class FakeResponse:
        def __init__(self, redirect_to=None):
            self.is_redirect = redirect_to is not None
            self.headers = {"location": redirect_to} if redirect_to else {}
            self.text = "<html>halaman</html>"

        def raise_for_status(self):
            return None

    class FakeClient:
        def __init__(self, *a, **kw):
            self.calls = []

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, url):
            self.calls.append(url)
            if url.startswith("https://publik.example"):
                return FakeResponse(redirect_to="http://localhost/rahasia")
            return FakeResponse()

    monkeypatch.setattr(se.httpx, "Client", FakeClient)
    with pytest.raises(ApiException) as exc:
        se._fetch_html("https://publik.example/artikel")
    assert exc.value.code == se.URL_INVALID


def test_rantai_redirect_dibatasi(monkeypatch):
    _stub_dns(monkeypatch, {"publik.example": "93.184.216.34"})

    class Loop:
        is_redirect = True
        headers = {"location": "https://publik.example/lagi"}

        def raise_for_status(self):
            return None

    class FakeClient:
        def __init__(self, *a, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, url):
            return Loop()

    monkeypatch.setattr(se.httpx, "Client", FakeClient)
    with pytest.raises(ApiException) as exc:
        se._fetch_html("https://publik.example/mulai")
    assert exc.value.code == se.URL_FETCH_FAILED
