"""ตั้งค่า CA bundle จาก certifi ก่อนโหลด Flet (ลด SSL error บน Windows)."""

from __future__ import annotations

import os
import ssl


def apply_certifi_defaults() -> None:
    try:
        import certifi
    except ImportError:
        return
    ca = certifi.where()
    if not ca or not os.path.isfile(ca):
        return
    os.environ.setdefault("SSL_CERT_FILE", ca)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", ca)
    os.environ.setdefault("CURL_CA_BUNDLE", ca)

    def _https_context() -> ssl.SSLContext:
        return ssl.create_default_context(cafile=ca)

    ssl._create_default_https_context = _https_context
