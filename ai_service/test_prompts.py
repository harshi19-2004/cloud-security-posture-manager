"""
test_prompts.py
Day 2 Task — AI Developer 1
Tool-59 Cloud Security Posture Manager
"""

import os
import json
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# ── Load .env ─────────────────────────────────────────────────────────────────
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("\n  ERROR: GROQ_API_KEY not found in .env file!")
    sys.exit(1)

client = Groq(api_key=api_key)
MODEL  = "llama-3.3-70b-versatile"
PROMPTS_DIR = Path(__file__).parent / "prompts"

# ── Terminal colours ──────────────────────────────────────────────────────────
G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
X = "\033[0m"

def ok(m):   print(f"  {G}PASS{X}  {m}")
def fail(m): print(f"  {R}FAIL{X}  {m}")
def info(m): print(f"  {Y}    {X}  {m}")

def load_prompt(filename):
    with open(PROMPTS_DIR / filename, encoding="utf-8") as f:
        return f.read()

def ask_groq(system_prompt, user_input, temperature=0.3):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_input},
        ],
        temperature=temperature,
        max_tokens=800,
    )
    return response.choices[0].message.content

# ── 5 real inputs for /describe ───────────────────────────────────────────────
DESCRIBE_INPUTS = [
    "AWS S3 bucket called prod-backups with public read ACL, no encryption, no versioning.",
    "Google Cloud VM with SSH port 22 open to 0.0.0.0/0 and default service account with editor role.",
    "Azure SQL Database with public endpoint enabled, no firewall rules, TDE disabled.",
    "AWS Lambda function with AdministratorAccess IAM role and database password in environment variable.",
    "Kubernetes pod running as root user, hostNetwork true, secrets stored as env vars.",
]

# ── 5 real inputs for /recommend ─────────────────────────────────────────────
RECOMMEND_INPUTS = [
    "AWS EC2 security group with inbound rule allowing all traffic from 0.0.0.0/0 on all ports.",
    "Redis 6 instance on port 6379 with no password, exposed to public internet.",
    "AWS IAM user with AdministratorAccess, no MFA, access keys 18 months old.",
    "AWS EBS production volume with encryption disabled and no snapshots configured.",
    "Docker container running as root with --privileged flag and 2-year-old base image.",
]

# ── 5 real inputs for /generate-report ───────────────────────────────────────
REPORT_INPUTS = [
    "AWS production: 5 EC2 instances, RDS MySQL with public endpoint, S3 public ACL, CloudTrail disabled.",
    "GCP startup: 3 GKE nodes running payments, Cloud SQL no SSL, Cloud Storage bucket-level access off.",
    "Azure company: 20 VMs, no Defender, secrets hardcoded in app config, NSGs allow RDP from any IP.",
    "Multi-cloud AWS and Azure: no private connection between clouds, all traffic over public internet.",
    "On-prem Kubernetes 1.26: RBAC disabled, dashboard exposed on NodePort 30000, etcd not encrypted.",
]

# ── Allowed enum values ───────────────────────────────────────────────────────
VALID_RISK_LEVELS  = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
VALID_SEVERITIES   = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
VALID_ACTION_TYPES = {"PATCH","CONFIGURE","RESTRICT","ENABLE","DISABLE",
                      "ROTATE","AUDIT","MONITOR","REVIEW","ENCRYPT"}
VALID_PRIORITIES   = {"HIGH", "MEDIUM", "LOW"}


def validate_describe(data):
    errors = []
    if not data.get("description"):
        errors.append("Missing 'description' field")
    if data.get("risk_level") not in VALID_RISK_LEVELS:
        errors.append(f"Bad risk_level: '{data.get('risk_level')}'")
    if not isinstance(data.get("findings"), list):
        errors.append("'findings' must be a list")
    return errors


def validate_recommend(data):
    errors = []
    recs = data if isinstance(data, list) else data.get("recommendations", [])
    if len(recs) != 3:
        errors.append(f"Need exactly 3 recommendations, got {len(recs)}")
    for i, r in enumerate(recs):
        if r.get("action_type") not in VALID_ACTION_TYPES:
            errors.append(f"Item {i+1}: bad action_type '{r.get('action_type')}'")
        if r.get("priority") not in VALID_PRIORITIES:
            errors.append(f"Item {i+1}: bad priority '{r.get('priority')}'")
        if not r.get("description"):
            errors.append(f"Item {i+1}: missing description")
    return errors


def validate_report(data):
    errors = []
    for key in ("title", "summary", "overview", "key_items", "recommendations"):
        if key not in data:
            errors.append(f"Missing key: '{key}'")
    recs = data.get("recommendations", [])
    if len(recs) != 5:
        errors.append(f"Need exactly 5 recommendations, got {len(recs)}")
    for i, item in enumerate(data.get("key_items", [])):
        if item.get("severity") not in VALID_SEVERITIES:
            errors.append(f"key_items[{i}]: bad severity '{item.get('severity')}'")
    return errors


def ask_groq_with_retry(prompt, user_input, temperature):
    """Call Groq with automatic retry if rate limit hit"""
    for attempt in range(3):
        try:
            return ask_groq(prompt, user_input, temperature)
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                wait = 30 if attempt == 0 else 60
                print(f"  {Y}Rate limit hit — waiting {wait} seconds...{X}")
                time.sleep(wait)
            else:
                raise e
    return None


def run_suite(label, prompt_file, inputs, validator, temperature=0.3):
    print(f"\n{'='*55}")
    print(f"  Testing: {label}")
    print(f"{'='*55}")
    prompt = load_prompt(prompt_file)
    passed = 0

    for i, user_input in enumerate(inputs, start=1):
        print(f"\n  Input {i}: {user_input[:60]}...")

        # ── Wait 5 seconds between each call to avoid rate limit ─────────────
        if i > 1:
            print(f"  {Y}Waiting 5s to avoid rate limit...{X}")
            time.sleep(5)

        try:
            raw = ask_groq_with_retry(prompt, user_input, temperature)
            if raw is None:
                fail("Failed after 3 retries")
                continue

            clean  = raw.strip().strip("```json").strip("```").strip()
            data   = json.loads(clean)
            errors = validator(data)

            if errors:
                for e in errors:
                    fail(e)
            else:
                ok("Valid JSON structure")
                passed += 1
                if isinstance(data, dict) and "risk_level" in data:
                    info(f"risk_level = {data['risk_level']}")
                elif isinstance(data, dict) and "title" in data:
                    info(f"title = {data['title']}")
                elif isinstance(data, list) and data:
                    info(f"action_type[0] = {data[0].get('action_type')}")

        except json.JSONDecodeError as e:
            fail(f"JSON parse error: {e}")
        except Exception as e:
            fail(f"Error: {e}")

    colour = G if passed == len(inputs) else (Y if passed >= 3 else R)
    print(f"\n  Score: {colour}{passed}/{len(inputs)}{X}")

    # ── Wait 15 seconds between suites ───────────────────────────────────────
    print(f"\n  {Y}Waiting 15s before next test suite...{X}")
    time.sleep(15)

    return passed


def main():
    print(f"\n{'='*55}")
    print(f"  Tool-59 Prompt Tests  |  Model: {MODEL}")
    print(f"{'='*55}")
    print(f"  .env path : {env_path}")
    print(f"  Key loaded: {G}YES{X}")
    print(f"  Note: 5s delay between calls to respect rate limits")

    total  = run_suite("/describe",        "describe_system.txt",   DESCRIBE_INPUTS,  validate_describe,  0.3)
    total += run_suite("/recommend",       "recommend_system.txt",  RECOMMEND_INPUTS, validate_recommend, 0.4)
    total += run_suite("/generate-report", "report_system.txt",     REPORT_INPUTS,    validate_report,    0.3)

    max_score = len(DESCRIBE_INPUTS) + len(RECOMMEND_INPUTS) + len(REPORT_INPUTS)
    colour = G if total == max_score else (Y if total >= 12 else R)

    print(f"\n{'='*55}")
    print(f"  FINAL SCORE: {colour}{total}/{max_score}{X}")
    if total == max_score:
        print(f"  {G}All tests pass! Ready to commit.{X}")
    elif total >= 12:
        print(f"  {Y}Almost there — fix the failing ones.{X}")
    else:
        print(f"  {R}Too many failures — review your prompts.{X}")
    print(f"{'='*55}\n")

    sys.exit(0 if total == max_score else 1)


if __name__ == "__main__":
    main()