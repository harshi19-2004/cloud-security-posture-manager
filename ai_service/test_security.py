"""
test_security.py
Day 8 Task — AI Developer 1
Tests all security headers are present on every response

How to run:
    python test_security.py
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from app import app
from services.security_headers import get_security_headers_list

G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
X = "\033[0m"

def ok(m):   print(f"  {G}PASS{X}  {m}")
def fail(m): print(f"  {R}FAIL{X}  {m}")
def info(m): print(f"  {Y}    {X}  {m}")


def check_headers(res, endpoint_name):
    """Check all security headers present in response."""
    headers  = get_security_headers_list()
    all_good = True

    for header in headers:
        if header in res.headers:
            ok(f"{header} present")
        else:
            fail(f"{header} MISSING on {endpoint_name}")
            all_good = False

    return all_good


def test_security():
    client = app.test_client()
    passed = 0
    total  = 0

    print(f"\n{'='*55}")
    print(f"  Testing Security Headers — Day 8")
    print(f"{'='*55}")

    # ── Test 1: Security headers on GET /health ───────────────────────────────
    total += 1
    print(f"\n  Test 1: Security headers on GET /health")
    res = client.get("/health")
    if check_headers(res, "/health"):
        passed += 1

    # ── Test 2: Security headers on POST /describe ────────────────────────────
    total += 1
    print(f"\n  Test 2: Security headers on POST /describe")
    res = client.post("/describe",
                      data='{"resource": "test"}',
                      content_type="application/json")
    if check_headers(res, "/describe"):
        passed += 1

    # ── Test 3: Security headers on POST /recommend ───────────────────────────
    total += 1
    print(f"\n  Test 3: Security headers on POST /recommend")
    res = client.post("/recommend",
                      data='{"resource": "test"}',
                      content_type="application/json")
    if check_headers(res, "/recommend"):
        passed += 1

    # ── Test 4: Security headers on POST /generate-report ────────────────────
    total += 1
    print(f"\n  Test 4: Security headers on POST /generate-report")
    res = client.post("/generate-report",
                      data='{"environment": "test"}',
                      content_type="application/json")
    if check_headers(res, "/generate-report"):
        passed += 1

    # ── Test 5: Security headers on 404 response ─────────────────────────────
    total += 1
    print(f"\n  Test 5: Security headers on 404 response")
    res = client.get("/this-does-not-exist")
    if check_headers(res, "404 page"):
        passed += 1

    # ── Test 6: X-Content-Type-Options is nosniff ────────────────────────────
    total += 1
    print(f"\n  Test 6: X-Content-Type-Options value is nosniff")
    res = client.get("/health")
    if res.headers.get("X-Content-Type-Options") == "nosniff":
        ok("X-Content-Type-Options = nosniff")
        passed += 1
    else:
        fail(f"Wrong value: {res.headers.get('X-Content-Type-Options')}")

    # ── Test 7: X-Frame-Options is DENY ──────────────────────────────────────
    total += 1
    print(f"\n  Test 7: X-Frame-Options value is DENY")
    if res.headers.get("X-Frame-Options") == "DENY":
        ok("X-Frame-Options = DENY")
        passed += 1
    else:
        fail(f"Wrong value: {res.headers.get('X-Frame-Options')}")

    # ── Summary ───────────────────────────────────────────────────────────────
    colour = G if passed == total else (Y if passed >= 5 else R)
    print(f"\n{'='*55}")
    print(f"  SCORE: {colour}{passed}/{total}{X}")
    if passed == total:
        print(f"  {G}All security headers present!{X}")
        print(f"  {G}ZAP Critical/High findings fixed!{X}")
    elif passed >= 5:
        print(f"  {Y}Almost! Fix the failing headers.{X}")
    else:
        print(f"  {R}Something wrong — paste output for help.{X}")
    print(f"{'='*55}\n")

    return passed == total


if __name__ == "__main__":
    success = test_security()
    sys.exit(0 if success else 1)