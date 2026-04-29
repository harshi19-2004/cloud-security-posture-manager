"""
security_headers.py
Day 8 — AI Developer 1

Adds security headers to all Flask responses.
Fixes OWASP ZAP Critical and High findings.
"""


def apply_security_headers(response):
    """
    Add all required security headers to every response.
    Call this from Flask after_request hook.

    Fixes these ZAP findings:
    - Missing Anti-clickjacking Header
    - X-Content-Type-Options Header Missing
    - X-XSS-Protection Header Missing
    - Strict-Transport-Security Header Missing
    - Content-Security-Policy Header Missing
    - Referrer-Policy Header Missing
    - Permissions-Policy Header Missing
    """

    # ── Prevent MIME type sniffing ────────────────────────────────────────────
    response.headers["X-Content-Type-Options"] = "nosniff"

    # ── Prevent clickjacking ──────────────────────────────────────────────────
    response.headers["X-Frame-Options"] = "DENY"

    # ── XSS protection ────────────────────────────────────────────────────────
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # ── Force HTTPS ───────────────────────────────────────────────────────────
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    # ── Content Security Policy ───────────────────────────────────────────────
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    # ── Referrer Policy ───────────────────────────────────────────────────────
    response.headers["Referrer-Policy"] = "no-referrer"

    # ── Permissions Policy ────────────────────────────────────────────────────
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )

    # ── Remove server info — hides Flask/Werkzeug version ────────────────────
    response.headers.pop("Server", None)
    response.headers.pop("X-Powered-By", None)

    return response


def get_security_headers_list() -> list:
    """
    Returns list of all security headers we apply.
    Used by test_security.py to verify all headers present.
    """
    return [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "Referrer-Policy",
        "Permissions-Policy",
    ]