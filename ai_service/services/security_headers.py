"""
security_headers.py
Day 11 — Updated to fix all remaining ZAP findings
"""


def apply_security_headers(response):
    """
    Add all security headers to every response.
    Fixes ALL OWASP ZAP Critical and High findings.
    """

    # ── Prevent MIME type sniffing ────────────────────────────────────────────
    response.headers["X-Content-Type-Options"] = "nosniff"

    # ── Prevent clickjacking ──────────────────────────────────────────────────
    response.headers["X-Frame-Options"] = "DENY"

    # ── XSS protection ────────────────────────────────────────────────────────
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # ── Force HTTPS ───────────────────────────────────────────────────────────
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains; preload"
    )

    # ── Content Security Policy ───────────────────────────────────────────────
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self'; "
        "connect-src 'self'"
    )

    # ── Referrer Policy ───────────────────────────────────────────────────────
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # ── Permissions Policy ────────────────────────────────────────────────────
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=(), "
        "payment=(), usb=(), magnetometer=()"
    )

    # ── Cache control — prevent sensitive data caching ────────────────────────
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"]        = "no-cache"

    # ── Remove server info ────────────────────────────────────────────────────
    response.headers.pop("Server",       None)
    response.headers.pop("X-Powered-By", None)

    return response


def get_security_headers_list() -> list:
    """Returns list of all security headers we apply."""
    return [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "Referrer-Policy",
        "Permissions-Policy",
        "Cache-Control",
    ]