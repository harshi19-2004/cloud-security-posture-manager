# Tool-59 — Cloud Security Posture Manager
## AI Developer 1 — Final Submission
## Harshith K S

Sprint: 14 April – 9 May 2026
Demo Day: 9 May 2026

---

## Submission Summary

| Item | Status |
|---|---|
| GitHub Repository | ✅ Submitted |
| Pull Request #1 (Day 1-8) | ✅ Merged by mentor |
| Pull Request #2 (Day 9-12) | ✅ Merged by mentor |
| Pull Request #3 (Day 13-19) | ✅ Open |
| README.md | ✅ Complete |
| Dockerfile | ✅ Builds cleanly |
| All Tests Passing | ✅ Complete |
| Demo Script | ✅ Ready |
| AI Service Demo Ready | ✅ Confirmed |

---

## GitHub Links

**My Fork:**
https://github.com/harshi19-2004/cloud-security-posture-manager

**Mentor Repo:**
https://github.com/tecsxpert/cloud-security-posture-manager

**PR #1 (Merged):**
https://github.com/tecsxpert/cloud-security-posture-manager/pull/1

**PR #2 (Merged):**
https://github.com/tecsxpert/cloud-security-posture-manager/pull/2

**PR #3 (Open):**
https://github.com/tecsxpert/cloud-security-posture-manager/pull/3

---

## Daily Work Summary

| Day | Task | Status |
|---|---|---|
| Day 1 | Flask setup — routes, services, prompts | ✅ Done |
| Day 2 | Prompt templates + test_prompts.py | ✅ Done |
| Day 3 | POST /describe endpoint | ✅ Done |
| Day 4 | POST /recommend endpoint | ✅ Done |
| Day 5 | AI integration + null handling | ✅ Done |
| Day 6 | POST /generate-report endpoint | ✅ Done |
| Day 7 | GET /health + Redis cache | ✅ Done |
| Day 8 | Security headers + ZAP fixes | ✅ Done |
| Day 9 | Final AI optimisation + fallback | ✅ Done |
| Day 10 | README.md complete | ✅ Done |
| Day 11 | sentence-transformers preload | ✅ Done |
| Day 12 | ChromaDB seeded + 30 demo records | ✅ Done |
| Day 13 | Dockerfile + requirements + .env.example | ✅ Done |
| Day 14 | AI dry run + response times recorded | ✅ Done |
| Day 15 | GitHub link submitted to mentor | ✅ Done |
| Day 16 | Final performance verify | ✅ Done |
| Day 17 | Groq API check + endpoints confirmed | ✅ Done |
| Day 18 | Demo preparation + script ready | ✅ Done |
| Day 19 | Final push + submissions confirmed | ✅ Done |
| Day 20 | DEMO DAY | 🎯 Tomorrow! |

---

## AI Service Performance

| Endpoint | Response Time | Status |
|---|---|---|
| GET /health | 3.07ms | ✅ PASS |
| POST /describe | 637ms | ✅ PASS |
| POST /recommend | 596ms | ✅ PASS |
| POST /generate-report | 1409ms | ✅ PASS |

All endpoints under 2000ms target! ✅

---

## Test Files Summary

| Test File | Tests | Status |
|---|---|---|
| test_describe.py | 5/5 | ✅ |
| test_recommend.py | 5/5 | ✅ |
| test_report.py | 5/5 | ✅ |
| test_health.py | 5/5 | ✅ |
| test_security.py | 7/7 | ✅ |
| test_optimisation.py | 5/5 | ✅ |
| test_integration.py | 5/5 | ✅ |
| test_dry_run.py | 4/4 | ✅ |
| test_performance.py | 7/7 | ✅ |
| test_groq_check.py | 5/5 | ✅ |
| test_demo_final.py | 4/4 | ✅ |

---

## Security Features Implemented

| Feature | Details |
|---|---|
| Rate Limiting | 30 requests/min per IP |
| Input Sanitisation | HTML, SQL, prompt injection blocked |
| Security Headers | X-Frame-Options, CSP, HSTS, Cache-Control |
| Fallback Response | is_fallback: true when AI unavailable |
| Redis Cache | SHA256 key, 15 min TTL |
| Non-root Docker | Runs as appuser |
| .env Protection | Never committed to GitHub |

---

## Developer

**Harshith K S** — AI Developer 1
Tool-59 Cloud Security Posture Manager
CampusPe Internship
Generative AI Intern
Sprint: 14 April – 9 May 2026