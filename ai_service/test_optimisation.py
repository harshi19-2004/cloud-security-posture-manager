"""
test_optimisation.py
Day 9 Task — AI Developer 1
Tests response time under 2s and fallback templates

How to run:
    python test_optimisation.py
"""

import os
import sys
import json
import time
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


def test_optimisation():
    client = app.test_client()
    passed = 0
    total  = 0

    print(f"\n{'='*55}")
    print(f"  Testing AI Optimisation — Day 9")
    print(f"{'='*55}")

    # ── Test 1: Fallback on empty input ───────────────────────────────────────
    total += 1
    print(f"\n  Test 1: Fallback returned on empty input")
    res  = client.post("/describe",
                       data='{"resource": ""}',
                       content_type="application/json")
    data = safe_json(res)
    if res.status_code == 400:
        ok("Returns 400 on empty input — correct!")
        passed += 1
    else:
        fail(f"Expected 400, got {res.status_code}")

    # ── Test 2: /describe response time ───────────────────────────────────────
    total += 1
    print(f"\n  Test 2: POST /describe response time")
    info("Calling Groq API — measuring time...")
    start = time.time()
    res   = client.post("/describe",
                        data='{"resource": "AWS S3 bucket with public ACL."}',
                        content_type="application/json")
    elapsed = time.time() - start
    data    = safe_json(res)

    info(f"Response time: {elapsed:.2f}s")
    if res.status_code == 200:
        if data.get("is_fallback") == False:
            ok(f"Real AI response in {elapsed:.2f}s")
        else:
            ok(f"Fallback response returned — is_fallback=True")
        passed += 1
    else:
        fail(f"Expected 200, got {res.status_code}")

    # Wait to avoid rate limit
    info("Waiting 10s...")
    time.sleep(10)

    # ── Test 3: Fallback has is_fallback true ─────────────────────────────────
    total += 1
    print(f"\n  Test 3: Verify is_fallback field exists in response")
    res  = client.post("/describe",
                       data='{"resource": "Azure VM with open RDP port."}',
                       content_type="application/json")
    data = safe_json(res)
    if "is_fallback" in data:
        ok(f"is_fallback field present = {data.get('is_fallback')}")
        passed += 1
    else:
        fail("is_fallback field missing from response!")

    # Wait to avoid rate limit
    info("Waiting 10s...")
    time.sleep(10)

    # ── Test 4: /recommend has is_fallback field ──────────────────────────────
    total += 1
    print(f"\n  Test 4: POST /recommend has is_fallback field")
    res  = client.post("/recommend",
                       data='{"resource": "Redis with no password."}',
                       content_type="application/json")
    data = safe_json(res)
    if "is_fallback" in data:
        ok(f"is_fallback field present = {data.get('is_fallback')}")
        passed += 1
    else:
        fail("is_fallback field missing!")

    # Wait to avoid rate limit
    info("Waiting 10s...")
    time.sleep(10)

    # ── Test 5: /generate-report has is_fallback field ────────────────────────
    total += 1
    print(f"\n  Test 5: POST /generate-report has is_fallback field")
    res  = client.post("/generate-report",
                       data='{"environment": "AWS with public RDS."}',
                       content_type="application/json")
    data = safe_json(res)
    if "is_fallback" in data:
        ok(f"is_fallback field present = {data.get('is_fallback')}")
        passed += 1
    else:
        fail("is_fallback field missing!")

    # ── Summary ───────────────────────────────────────────────────────────────
    colour = G if passed == total else (Y if passed >= 3 else R)
    print(f"\n{'='*55}")
    print(f"  SCORE: {colour}{passed}/{total}{X}")
    if passed == total:
        print(f"  {G}All optimisation tests pass!{X}")
    elif passed >= 3:
        print(f"  {Y}Almost! Fix the failing tests.{X}")
    else:
        print(f"  {R}Something wrong — paste output for help.{X}")
    print(f"{'='*55}\n")

    return passed == total


if __name__ == "__main__":
    success = test_optimisation()
    sys.exit(0 if success else 1)