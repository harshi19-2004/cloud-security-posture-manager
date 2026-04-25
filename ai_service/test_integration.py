"""
test_integration.py
Day 5 Task — AI Developer 1
Tests AI integration — null handling, all endpoints, async simulation

How to run:
    python test_integration.py
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from app import app
from services.ai_integration import (
    run_describe_on_create,
    run_recommend_on_create,
    run_full_ai_on_create,
    safe_get_description,
    safe_get_risk_level,
    safe_get_recommendations,
)

G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
X = "\033[0m"

def ok(m):   print(f"  {G}PASS{X}  {m}")
def fail(m): print(f"  {R}FAIL{X}  {m}")
def info(m): print(f"  {Y}    {X}  {m}")


def test_integration():
    passed = 0
    total  = 0

    print(f"\n{'='*55}")
    print(f"  Testing AI Integration — Day 5")
    print(f"{'='*55}")

    # ── Test 1: Null input handled gracefully ─────────────────────────────────
    total += 1
    print(f"\n  Test 1: Null/empty input handled gracefully")
    result = run_describe_on_create("")
    if result is None:
        ok("Returns None gracefully for empty input")
        passed += 1
    else:
        fail(f"Expected None, got {result}")

    # ── Test 2: None input handled gracefully ─────────────────────────────────
    total += 1
    print(f"\n  Test 2: None input handled gracefully")
    result = run_recommend_on_create("")
    if result is None:
        ok("Returns None gracefully for empty input")
        passed += 1
    else:
        fail(f"Expected None, got {result}")

    # ── Test 3: safe_get helpers work with None ───────────────────────────────
    total += 1
    print(f"\n  Test 3: Safe helper functions work with None")
    desc  = safe_get_description(None)
    risk  = safe_get_risk_level(None)
    recs  = safe_get_recommendations(None)
    if desc == "" and risk == "UNKNOWN" and recs == []:
        ok("Safe helpers return defaults when AI result is None")
        passed += 1
    else:
        fail(f"desc={desc}, risk={risk}, recs={recs}")

    # ── Test 4: Describe on create — real AI call ─────────────────────────────
    total += 1
    print(f"\n  Test 4: run_describe_on_create — real Groq call")
    info("Calling Groq API — takes a few seconds...")
    result = run_describe_on_create(
        "AWS S3 bucket with public read ACL and no encryption."
    )
    if result is not None:
        has_desc  = "description"  in result
        has_risk  = "risk_level"   in result
        has_gen   = "generated_at" in result
        has_fall  = "is_fallback"  in result
        if all([has_desc, has_risk, has_gen, has_fall]):
            ok("describe on create returns valid result")
            info(f"risk_level  = {result.get('risk_level')}")
            info(f"is_fallback = {result.get('is_fallback')}")
            passed += 1
        else:
            fail("Missing fields in describe result")
    else:
        fail("run_describe_on_create returned None for valid input")

    # Wait to avoid rate limit
    info("Waiting 10s before next API call...")
    time.sleep(10)

    # ── Test 5: Full AI on create — both describe + recommend ─────────────────
    total += 1
    print(f"\n  Test 5: run_full_ai_on_create — describe + recommend together")
    info("Calling Groq API twice — takes 10-15 seconds...")
    result = run_full_ai_on_create(
        "Azure VM with RDP port 3389 open to all IPs, no disk encryption."
    )
    if result is not None:
        has_describe  = "describe"    in result
        has_recommend = "recommend"   in result
        has_attached  = "ai_attached" in result

        if all([has_describe, has_recommend, has_attached]):
            ok("run_full_ai_on_create returns describe + recommend")
            info(f"ai_attached = {result.get('ai_attached')}")
            if result.get("describe"):
                info(f"describe risk_level = {result['describe'].get('risk_level')}")
            if result.get("recommend"):
                recs = result["recommend"].get("recommendations", [])
                info(f"recommend count = {len(recs)}")
            passed += 1
        else:
            fail(f"Missing keys in result: {list(result.keys())}")
    else:
        fail("run_full_ai_on_create returned None")

    # ── Summary ───────────────────────────────────────────────────────────────
    colour = G if passed == total else (Y if passed >= 3 else R)
    print(f"\n{'='*55}")
    print(f"  SCORE: {colour}{passed}/{total}{X}")
    if passed == total:
        print(f"  {G}All tests pass! AI Integration working!{X}")
    elif passed >= 3:
        print(f"  {Y}Almost! Fix the failing tests.{X}")
    else:
        print(f"  {R}Something wrong — paste output for help.{X}")
    print(f"{'='*55}\n")

    return passed == total


if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)