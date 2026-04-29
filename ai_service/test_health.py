"""
test_health.py
Day 7 Task — AI Developer 1
Tests GET /health endpoint

How to run:
    python test_health.py
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from app import app

G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
X = "\033[0m"

def ok(m):   print(f"  {G}PASS{X}  {m}")
def fail(m): print(f"  {R}FAIL{X}  {m}")
def info(m): print(f"  {Y}    {X}  {m}")

def safe_json(res):
    try:
        if res.data:
            return json.loads(res.data)
    except Exception:
        pass
    return {}


def test_health():
    client = app.test_client()
    passed = 0
    total  = 0

    print(f"\n{'='*55}")
    print(f"  Testing GET /health endpoint")
    print(f"{'='*55}")

    # ── Test 1: Health returns 200 ────────────────────────────────────────────
    total += 1
    print(f"\n  Test 1: GET /health returns 200")
    res  = client.get("/health")
    data = safe_json(res)
    if res.status_code == 200:
        ok("Returns 200 OK")
        passed += 1
    else:
        fail(f"Expected 200, got {res.status_code}")

    # ── Test 2: Has all required fields ──────────────────────────────────────
    total += 1
    print(f"\n  Test 2: Has all required fields")
    required = ["status", "model", "uptime_seconds",
                "uptime_human", "avg_response_ms", "cache"]
    missing  = [k for k in required if k not in data]
    if not missing:
        ok("All required fields present")
        info(f"model          = {data.get('model')}")
        info(f"uptime         = {data.get('uptime_human')}")
        info(f"avg_response   = {data.get('avg_response_ms')}ms")
        passed += 1
    else:
        fail(f"Missing fields: {missing}")

    # ── Test 3: Status is ok ──────────────────────────────────────────────────
    total += 1
    print(f"\n  Test 3: Status field is ok")
    if data.get("status") == "ok":
        ok("Status is 'ok'")
        passed += 1
    else:
        fail(f"Expected 'ok', got '{data.get('status')}'")

    # ── Test 4: Model is correct ──────────────────────────────────────────────
    total += 1
    print(f"\n  Test 4: Model name is correct")
    if data.get("model") == "llama-3.3-70b-versatile":
        ok("Model name is correct")
        passed += 1
    else:
        fail(f"Wrong model: {data.get('model')}")

    # ── Test 5: Cache status present ─────────────────────────────────────────
    total += 1
    print(f"\n  Test 5: Cache status present")
    cache = data.get("cache", {})
    if "redis_connected" in cache and "cache_ttl_seconds" in cache:
        ok("Cache status present in health response")
        info(f"redis_connected  = {cache.get('redis_connected')}")
        info(f"cache_ttl        = {cache.get('cache_ttl_seconds')}s")
        info(f"message          = {cache.get('message')}")
        passed += 1
    else:
        fail(f"Cache status missing fields: {cache}")

    # ── Summary ───────────────────────────────────────────────────────────────
    colour = G if passed == total else (Y if passed >= 3 else R)
    print(f"\n{'='*55}")
    print(f"  SCORE: {colour}{passed}/{total}{X}")
    if passed == total:
        print(f"  {G}All tests pass! /health working!{X}")
    elif passed >= 3:
        print(f"  {Y}Almost! Fix the failing tests.{X}")
    else:
        print(f"  {R}Something wrong — paste output for help.{X}")
    print(f"{'='*55}\n")

    return passed == total


if __name__ == "__main__":
    success = test_health()
    sys.exit(0 if success else 1)