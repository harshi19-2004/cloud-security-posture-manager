"""
test_dry_run.py
Day 14 Task — AI Developer 1

AI dry run on demo machine.
Tests all 3 endpoints live and records response times.
Saves results to dry_run_results.json as backup.

How to run:
    python test_dry_run.py
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone
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


def run_dry_run():
    client  = app.test_client()
    results = {
        "dry_run_date":    datetime.now(timezone.utc).isoformat(),
        "machine":         os.environ.get("COMPUTERNAME", "demo-machine"),
        "model":           "llama-3.3-70b-versatile",
        "endpoints":       {},
        "overall_status":  "PASS",
        "total_time_ms":   0
    }

    print(f"\n{'='*55}")
    print(f"  Tool-59 AI Service — Demo Dry Run")
    print(f"  Date: {results['dry_run_date'][:10]}")
    print(f"  Model: {results['model']}")
    print(f"{'='*55}")

    # ── Test 1: GET /health ───────────────────────────────────────────────────
    print(f"\n  [1/4] Testing GET /health...")
    start = time.time()
    res   = client.get("/health")
    ms    = round((time.time() - start) * 1000, 2)
    data  = safe_json(res)

    results["endpoints"]["health"] = {
        "endpoint":      "GET /health",
        "status_code":   res.status_code,
        "response_ms":   ms,
        "status":        "PASS" if res.status_code == 200 else "FAIL",
        "model":         data.get("model", "unknown"),
        "uptime":        data.get("uptime_human", "unknown")
    }

    if res.status_code == 200:
        ok(f"GET /health — {ms}ms")
        info(f"model  = {data.get('model')}")
        info(f"uptime = {data.get('uptime_human')}")
    else:
        fail(f"GET /health — {res.status_code}")
        results["overall_status"] = "FAIL"

    # ── Test 2: POST /describe ────────────────────────────────────────────────
    print(f"\n  [2/4] Testing POST /describe...")
    info("Calling Groq AI — please wait...")
    payload = json.dumps({
        "resource": "AWS S3 bucket with public read ACL, no encryption, versioning disabled."
    })
    start = time.time()
    res   = client.post("/describe",
                        data=payload,
                        content_type="application/json")
    ms   = round((time.time() - start) * 1000, 2)
    data = safe_json(res)

    results["endpoints"]["describe"] = {
        "endpoint":      "POST /describe",
        "status_code":   res.status_code,
        "response_ms":   ms,
        "status":        "PASS" if res.status_code == 200 else "FAIL",
        "risk_level":    data.get("risk_level", "unknown"),
        "is_fallback":   data.get("is_fallback", True),
        "findings_count": len(data.get("findings", []))
    }

    if res.status_code == 200:
        ok(f"POST /describe — {ms}ms")
        info(f"risk_level     = {data.get('risk_level')}")
        info(f"findings_count = {len(data.get('findings', []))}")
        info(f"is_fallback    = {data.get('is_fallback')}")
        if ms > 2000:
            info(f"WARNING: response time {ms}ms exceeds 2000ms target!")
    else:
        fail(f"POST /describe — {res.status_code}")
        results["overall_status"] = "FAIL"

    # Wait to avoid rate limit
    info("Waiting 10s before next call...")
    time.sleep(10)

    # ── Test 3: POST /recommend ───────────────────────────────────────────────
    print(f"\n  [3/4] Testing POST /recommend...")
    info("Calling Groq AI — please wait...")
    payload = json.dumps({
        "resource": "Azure VM with RDP port 3389 open to all IPs and no disk encryption."
    })
    start = time.time()
    res   = client.post("/recommend",
                        data=payload,
                        content_type="application/json")
    ms   = round((time.time() - start) * 1000, 2)
    data = safe_json(res)
    recs = data.get("recommendations", [])

    results["endpoints"]["recommend"] = {
        "endpoint":           "POST /recommend",
        "status_code":        res.status_code,
        "response_ms":        ms,
        "status":             "PASS" if res.status_code == 200 else "FAIL",
        "recommendations":    len(recs),
        "is_fallback":        data.get("is_fallback", True),
        "first_action_type":  recs[0].get("action_type") if recs else "none"
    }

    if res.status_code == 200:
        ok(f"POST /recommend — {ms}ms")
        info(f"recommendations = {len(recs)}")
        info(f"first action    = {recs[0].get('action_type') if recs else 'none'}")
        info(f"is_fallback     = {data.get('is_fallback')}")
        if ms > 2000:
            info(f"WARNING: response time {ms}ms exceeds 2000ms target!")
    else:
        fail(f"POST /recommend — {res.status_code}")
        results["overall_status"] = "FAIL"

    # Wait to avoid rate limit
    info("Waiting 15s before next call...")
    time.sleep(15)

    # ── Test 4: POST /generate-report ─────────────────────────────────────────
    print(f"\n  [4/4] Testing POST /generate-report...")
    info("Calling Groq AI — please wait...")
    payload = json.dumps({
        "environment": (
            "AWS production: 3 EC2 instances, RDS MySQL with "
            "public endpoint, S3 bucket with public ACL, "
            "CloudTrail disabled, no GuardDuty enabled."
        )
    })
    start = time.time()
    res   = client.post("/generate-report",
                        data=payload,
                        content_type="application/json")
    ms   = round((time.time() - start) * 1000, 2)
    data = safe_json(res)

    results["endpoints"]["report"] = {
        "endpoint":    "POST /generate-report",
        "status_code": res.status_code,
        "response_ms": ms,
        "status":      "PASS" if res.status_code == 200 else "FAIL",
        "title":       data.get("title", "unknown"),
        "key_items":   len(data.get("key_items", [])),
        "recs_count":  len(data.get("recommendations", [])),
        "is_fallback": data.get("is_fallback", True)
    }

    if res.status_code == 200:
        ok(f"POST /generate-report — {ms}ms")
        info(f"title      = {data.get('title')}")
        info(f"key_items  = {len(data.get('key_items', []))}")
        info(f"recs_count = {len(data.get('recommendations', []))}")
        info(f"is_fallback = {data.get('is_fallback')}")
        if ms > 2000:
            info(f"WARNING: response time {ms}ms exceeds 2000ms target!")
    else:
        fail(f"POST /generate-report — {res.status_code}")
        results["overall_status"] = "FAIL"

    # ── Calculate total time ──────────────────────────────────────────────────
    total_ms = sum(
        e.get("response_ms", 0)
        for e in results["endpoints"].values()
    )
    results["total_time_ms"] = total_ms

    # ── Save results to JSON ──────────────────────────────────────────────────
    results_path = Path(__file__).parent / "dry_run_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # ── Print summary ─────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  DRY RUN SUMMARY")
    print(f"{'='*55}")

    for name, ep in results["endpoints"].items():
        status = ep.get("status", "FAIL")
        ms     = ep.get("response_ms", 0)
        colour = G if status == "PASS" else R
        print(f"  {colour}{status}{X}  {ep['endpoint']} — {ms}ms")

    print(f"\n  Total API time : {total_ms}ms")
    print(f"  Results saved  : dry_run_results.json")

    overall = results["overall_status"]
    colour  = G if overall == "PASS" else R
    print(f"\n  OVERALL: {colour}{overall}{X}")
    print(f"{'='*55}\n")

    # ── Print backup screenshot instructions ──────────────────────────────────
    if overall == "PASS":
        print(f"  {G}All 3 endpoints working!{X}")
        print(f"  {Y}Take screenshots now for Demo Day backup:{X}")
        print(f"  1. Screenshot of this terminal output")
        print(f"  2. Screenshot of dry_run_results.json")
        print(f"  3. Screenshot of GET /health response")
        print()

    return overall == "PASS"


if __name__ == "__main__":
    success = run_dry_run()
    sys.exit(0 if success else 1)