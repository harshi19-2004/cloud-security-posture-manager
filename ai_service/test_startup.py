"""
test_startup.py
Day 11 Task — AI Developer 1
Tests sentence-transformers pre-loading at startup

How to run:
    python test_startup.py
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
X = "\033[0m"

def ok(m):   print(f"  {G}PASS{X}  {m}")
def fail(m): print(f"  {R}FAIL{X}  {m}")
def info(m): print(f"  {Y}    {X}  {m}")


def test_startup():
    passed = 0
    total  = 0

    print(f"\n{'='*55}")
    print(f"  Testing Startup — Day 11")
    print(f"{'='*55}")

    # ── Test 1: embeddings module imports ─────────────────────────────────────
    total += 1
    print(f"\n  Test 1: embeddings.py imports correctly")
    try:
        from services.embeddings import (
            preload_at_startup,
            is_model_loaded,
            get_model,
            encode_text
        )
        ok("embeddings.py imports successfully")
        passed += 1
    except Exception as e:
        fail(f"Import failed: {e}")

    # ── Test 2: preload starts without error ──────────────────────────────────
    total += 1
    print(f"\n  Test 2: preload_at_startup runs without error")
    try:
        from services.embeddings import preload_at_startup
        preload_at_startup()
        ok("preload_at_startup() called successfully")
        passed += 1
    except Exception as e:
        fail(f"preload_at_startup failed: {e}")

    # ── Test 3: is_model_loaded returns bool ──────────────────────────────────
    total += 1
    print(f"\n  Test 3: is_model_loaded() returns boolean")
    try:
        from services.embeddings import is_model_loaded
        result = is_model_loaded()
        if isinstance(result, bool):
            ok(f"is_model_loaded() returns bool: {result}")
            passed += 1
        else:
            fail(f"Expected bool, got {type(result)}")
    except Exception as e:
        fail(f"is_model_loaded failed: {e}")

    # ── Test 4: App starts with model_loaded field ────────────────────────────
    total += 1
    print(f"\n  Test 4: App root shows model_loaded field")
    try:
        from app import app
        client = app.test_client()
        res    = client.get("/")
        data   = json.loads(res.data)
        if "model_loaded" in data:
            ok(f"model_loaded field present: {data.get('model_loaded')}")
            passed += 1
        else:
            fail("model_loaded field missing from root response")
    except Exception as e:
        fail(f"App test failed: {e}")

    # ── Test 5: Security headers updated ─────────────────────────────────────
    total += 1
    print(f"\n  Test 5: Updated security headers present")
    try:
        from app import app
        client = app.test_client()
        res    = client.get("/health")
        if "Cache-Control" in res.headers:
            ok("Cache-Control header present")
            info(f"Cache-Control = {res.headers.get('Cache-Control')}")
            passed += 1
        else:
            fail("Cache-Control header missing!")
    except Exception as e:
        fail(f"Security header test failed: {e}")

    # ── Summary ───────────────────────────────────────────────────────────────
    colour = G if passed == total else (Y if passed >= 3 else R)
    print(f"\n{'='*55}")
    print(f"  SCORE: {colour}{passed}/{total}{X}")
    if passed == total:
        print(f"  {G}All startup tests pass!{X}")
    elif passed >= 3:
        print(f"  {Y}Almost! Fix the failing tests.{X}")
    else:
        print(f"  {R}Something wrong — paste output for help.{X}")
    print(f"{'='*55}\n")

    return passed == total


if __name__ == "__main__":
    success = test_startup()
    sys.exit(0 if success else 1)