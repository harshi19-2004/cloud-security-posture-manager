"""
test_demo_final.py
Day 18 Task — AI Developer 1

Final demo test — simulates exactly what you will
show on Demo Day. Run this before the presentation!

How to run:
    python test_demo_final.py
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

# ── Demo inputs — exactly what you will show on Demo Day ─────────────────────
DEMO_RESOURCE    = "AWS S3 bucket with public read ACL and no encryption."
DEMO_ENVIRONMENT = "AWS production: EC2 instances, RDS MySQL with public endpoint, S3 public ACL, CloudTrail disabled."


def test_demo_final():
    client = app.test_client()
    passed = 0
    total  = 0

    print(f"\n{'='*55}")
    print(f"  FINAL DEMO TEST — Day 18")
    print(f"  Simulating exact Demo Day presentation")
    print(f"{'='*55}")

    # ── Demo Step 1: Health check ─────────────────────────────────────────────
    total += 1
    print(f"\n  [DEMO STEP 1] GET /health")
    print(f"  Say: 'The AI service is running on port 5000'")
    res  = client.get("/health")
    data = safe_json(res)
    if res.status_code == 200:
        ok(f"Health check PASS")
        info(f"model  = {data.get('model')}")
        info(f"status = {data.get('status')}")
        passed += 1
    else:
        fail(f"Health check FAILED — {res.status_code}")

    # ── Demo Step 2: Describe ─────────────────────────────────────────────────
    total += 1
    print(f"\n  [DEMO STEP 2] POST /describe")
    print(f"  Say: 'Watch the AI analyse this cloud resource'")
    info(f"Input: {DEMO_RESOURCE}")
    payload = json.dumps({"resource": DEMO_RESOURCE})
    start   = time.time()
    res     = client.post("/describe",
                          data=payload,
                          content_type="application/json")
    ms   = round((time.time() - start) * 1000, 2)
    data = safe_json(res)

    if res.status_code == 200:
        ok(f"Describe PASS — {ms}ms")
        info(f"risk_level     = {data.get('risk_level')}")
        info(f"findings_count = {len(data.get('findings', []))}")
        info(f"is_fallback    = {data.get('is_fallback')}")
        print(f"\n  {G}What to say:{X}")
        print(f"  'The AI found risk level: {data.get('risk_level')}'")
        print(f"  '{len(data.get('findings', []))} specific security issues identified'")
        passed += 1
    else:
        fail(f"Describe FAILED — {res.status_code}")

    info("Waiting 10s...")
    time.sleep(10)

    # ── Demo Step 3: Recommend ────────────────────────────────────────────────
    total += 1
    print(f"\n  [DEMO STEP 3] POST /recommend")
    print(f"  Say: 'Now the AI gives 3 prioritised fixes'")
    payload = json.dumps({"resource": DEMO_RESOURCE})
    start   = time.time()
    res     = client.post("/recommend",
                          data=payload,
                          content_type="application/json")
    ms   = round((time.time() - start) * 1000, 2)
    data = safe_json(res)
    recs = data.get("recommendations", [])

    if res.status_code == 200:
        ok(f"Recommend PASS — {ms}ms")
        for i, rec in enumerate(recs, 1):
            info(f"Rec {i}: {rec.get('action_type')} — {rec.get('priority')}")
        print(f"\n  {G}What to say:{X}")
        if recs:
            print(f"  'First fix: {recs[0].get('action_type')} — priority {recs[0].get('priority')}'")
        passed += 1
    else:
        fail(f"Recommend FAILED — {res.status_code}")

    info("Waiting 15s...")
    time.sleep(15)

    # ── Demo Step 4: Generate Report ──────────────────────────────────────────
    total += 1
    print(f"\n  [DEMO STEP 4] POST /generate-report")
    print(f"  Say: 'Finally the AI generates a full security report'")
    payload = json.dumps({"environment": DEMO_ENVIRONMENT})
    start   = time.time()
    res     = client.post("/generate-report",
                          data=payload,
                          content_type="application/json")
    ms   = round((time.time() - start) * 1000, 2)
    data = safe_json(res)

    if res.status_code == 200:
        ok(f"Generate Report PASS — {ms}ms")
        info(f"title     = {data.get('title')}")
        info(f"key_items = {len(data.get('key_items', []))}")
        info(f"recs      = {len(data.get('recommendations', []))}")
        print(f"\n  {G}What to say:{X}")
        print(f"  'Title: {data.get('title')}'")
        print(f"  '{len(data.get('key_items', []))} security findings, {len(data.get('recommendations', []))} recommendations'")
        passed += 1
    else:
        fail(f"Generate Report FAILED — {res.status_code}")

    # ── Summary ───────────────────────────────────────────────────────────────
    colour = G if passed == total else (Y if passed >= 3 else R)
    print(f"\n{'='*55}")
    print(f"  DEMO FINAL SCORE: {colour}{passed}/{total}{X}")
    if passed == total:
        print(f"  {G}All demo steps working!{X}")
        print(f"  {G}You are ready for Demo Day! 🎉{X}")
        print(f"\n  Practice your script 3 more times!")
        print(f"  Read demo_script.md for exact words to say!")
    else:
        print(f"  {R}Fix failing steps before Demo Day!{X}")
    print(f"{'='*55}\n")

    return passed == total


if __name__ == "__main__":
    success = test_demo_final()
    sys.exit(0 if success else 1)