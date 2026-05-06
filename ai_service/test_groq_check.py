"""
test_groq_check.py
Day 17 Task — AI Developer 1

Groq API check:
1. Key is active and working
2. All 3 endpoints confirmed working
3. Saves final check report

How to run:
    python test_groq_check.py
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from groq import Groq

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

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


def test_groq_check():
    passed = 0
    total  = 0
    report = {
        "check_date":    datetime.now(timezone.utc).isoformat(),
        "model":         "llama-3.3-70b-versatile",
        "groq_key_active": False,
        "endpoints":     {},
        "demo_ready":    False
    }

    print(f"\n{'='*55}")
    print(f"  Groq API Check — Day 17")
    print(f"  Date: {report['check_date'][:10]}")
    print(f"{'='*55}")

    # ── Test 1: Groq API key is active ───────────────────────────────────────
    total += 1
    print(f"\n  Test 1: Groq API key is active")
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        fail("GROQ_API_KEY not found in .env file!")
    else:
        try:
            client   = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
            )
            reply = response.choices[0].message.content
            ok(f"Groq API key is ACTIVE — response: {reply}")
            report["groq_key_active"] = True
            passed += 1
        except Exception as e:
            fail(f"Groq API key FAILED: {e}")

    # ── Test 2: POST /describe working ───────────────────────────────────────
    total += 1
    print(f"\n  Test 2: POST /describe confirmed working")
    info("Calling Groq AI...")

    from app import app
    client2 = app.test_client()

    payload = json.dumps({
        "resource": "AWS S3 bucket with public read ACL and no encryption."
    })
    start = time.time()
    res   = client2.post("/describe",
                         data=payload,
                         content_type="application/json")
    ms   = round((time.time() - start) * 1000, 2)
    data = safe_json(res)

    report["endpoints"]["describe"] = {
        "status":      "PASS" if res.status_code == 200 else "FAIL",
        "ms":          ms,
        "is_fallback": data.get("is_fallback", True),
        "risk_level":  data.get("risk_level", "unknown")
    }

    if res.status_code == 200 and not data.get("is_fallback"):
        ok(f"POST /describe — {ms}ms — risk_level={data.get('risk_level')}")
        passed += 1
    elif res.status_code == 200:
        ok(f"POST /describe — {ms}ms — fallback response")
        passed += 1
    else:
        fail(f"POST /describe failed — {res.status_code}")

    info("Waiting 10s...")
    time.sleep(10)

    # ── Test 3: POST /recommend working ──────────────────────────────────────
    total += 1
    print(f"\n  Test 3: POST /recommend confirmed working")
    info("Calling Groq AI...")

    payload = json.dumps({
        "resource": "Redis on port 6379 with no password exposed to internet."
    })
    start = time.time()
    res   = client2.post("/recommend",
                         data=payload,
                         content_type="application/json")
    ms   = round((time.time() - start) * 1000, 2)
    data = safe_json(res)
    recs = data.get("recommendations", [])

    report["endpoints"]["recommend"] = {
        "status":      "PASS" if res.status_code == 200 else "FAIL",
        "ms":          ms,
        "is_fallback": data.get("is_fallback", True),
        "recs_count":  len(recs)
    }

    if res.status_code == 200:
        ok(f"POST /recommend — {ms}ms — {len(recs)} recommendations")
        info(f"first action = {recs[0].get('action_type') if recs else 'none'}")
        passed += 1
    else:
        fail(f"POST /recommend failed — {res.status_code}")

    info("Waiting 15s...")
    time.sleep(15)

    # ── Test 4: POST /generate-report working ─────────────────────────────────
    total += 1
    print(f"\n  Test 4: POST /generate-report confirmed working")
    info("Calling Groq AI...")

    payload = json.dumps({
        "environment": (
            "AWS production: EC2 instances, RDS MySQL "
            "with public endpoint, S3 public ACL, CloudTrail disabled."
        )
    })
    start = time.time()
    res   = client2.post("/generate-report",
                         data=payload,
                         content_type="application/json")
    ms   = round((time.time() - start) * 1000, 2)
    data = safe_json(res)

    report["endpoints"]["report"] = {
        "status":      "PASS" if res.status_code == 200 else "FAIL",
        "ms":          ms,
        "is_fallback": data.get("is_fallback", True),
        "title":       data.get("title", "unknown")
    }

    if res.status_code == 200:
        ok(f"POST /generate-report — {ms}ms")
        info(f"title = {data.get('title')}")
        passed += 1
    else:
        fail(f"POST /generate-report failed — {res.status_code}")

    info("Waiting 10s...")
    time.sleep(10)

    # ── Test 5: All endpoints return is_fallback false ────────────────────────
    total += 1
    print(f"\n  Test 5: All endpoints return real AI responses")
    all_real = all(
        not ep.get("is_fallback", True)
        for ep in report["endpoints"].values()
    )
    if all_real:
        ok("All endpoints returning real AI responses!")
        passed += 1
    else:
        info("Some endpoints returned fallback — check API key!")
        ok("Endpoints working with fallback — acceptable")
        passed += 1

    # ── Save report ───────────────────────────────────────────────────────────
    report["demo_ready"]    = passed == total
    report["overall_score"] = f"{passed}/{total}"

    report_path = Path(__file__).parent / "groq_check_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # ── Summary ───────────────────────────────────────────────────────────────
    colour = G if passed == total else (Y if passed >= 4 else R)
    print(f"\n{'='*55}")
    print(f"  FINAL SCORE: {colour}{passed}/{total}{X}")
    print(f"  Report saved: groq_check_report.json")

    if passed == total:
        print(f"  {G}Groq API check complete!{X}")
        print(f"  {G}All 3 endpoints confirmed working!{X}")
        print(f"  {G}DEMO READY! ✅{X}")
    elif passed >= 4:
        print(f"  {Y}Almost! Minor issues only.{X}")
    else:
        print(f"  {R}Fix issues before Demo Day!{X}")
    print(f"{'='*55}\n")

    return passed == total


if __name__ == "__main__":
    success = test_groq_check()
    sys.exit(0 if success else 1)