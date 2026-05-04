import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from groq import Groq

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

logger      = logging.getLogger(__name__)
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# ── Response time tracker ─────────────────────────────────────────────────────
_response_times = []
MAX_TRACKED     = 100


def _record_response_time(ms: float):
    global _response_times
    _response_times.append(ms)
    if len(_response_times) > MAX_TRACKED:
        _response_times = _response_times[-MAX_TRACKED:]


def get_avg_response_ms() -> float:
    if not _response_times:
        return 0.0
    return round(sum(_response_times) / len(_response_times), 2)


def _load_prompt(filename):
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return f.read()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _clean_response(raw: str) -> str:
    return raw.strip().strip("```json").strip("```").strip()


class GroqClient:
    MODEL = "llama-3.3-70b-versatile"

    # ── Optimised retry — faster delays ──────────────────────────────────────
    RETRY_DELAYS = [1, 2, 4]

    # ── Optimised token limits per endpoint ──────────────────────────────────
    # Lower tokens = faster response = under 2s target
    TOKENS = {
        "describe": 600,
        "recommend": 500,
        "report": 800,
    }

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not set in .env file")
        self.client = Groq(api_key=api_key)

    def _call_groq(self, system_prompt: str,
                   user_message: str,
                   temperature: float = 0.3,
                   max_tokens: int = 600) -> str | None:
        """
        Optimised Groq call.
        - Tracks response time
        - Returns None on failure (never crashes)
        """
        last_error = None

        for attempt, delay in enumerate(self.RETRY_DELAYS, start=1):
            try:
                start_ms = time.time()

                response = self.client.chat.completions.create(
                    model=self.MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_message},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                elapsed_ms = (time.time() - start_ms) * 1000
                _record_response_time(elapsed_ms)
                logger.info(f"Groq response: {elapsed_ms:.0f}ms")

                return response.choices[0].message.content

            except Exception as e:
                last_error = e
                logger.warning(f"Groq attempt {attempt} failed: {e}")
                if attempt < len(self.RETRY_DELAYS):
                    time.sleep(delay)

        logger.error(f"All Groq retries failed: {last_error}")
        return None

    # ── /describe ─────────────────────────────────────────────────────────────
    def describe(self, resource: str) -> dict:
        if not resource or not resource.strip():
            return self._describe_fallback()

        # Check cache first
        try:
            from services.cache import get_cached, set_cached
            cached = get_cached("describe", resource)
            if cached:
                return cached
        except Exception:
            pass

        try:
            raw = self._call_groq(
                _load_prompt("describe_system.txt"),
                resource,
                temperature=0.3,
                max_tokens=self.TOKENS["describe"]
            )

            # ── Fallback if Groq returns None ─────────────────────────────────
            if raw is None:
                logger.error("describe() got None from Groq — returning fallback")
                return self._describe_fallback()

            parsed = json.loads(_clean_response(raw))
            parsed["generated_at"] = _now()
            parsed["is_fallback"]  = False

            try:
                from services.cache import set_cached
                set_cached("describe", resource, parsed)
            except Exception:
                pass

            return parsed

        except Exception as e:
            logger.error(f"describe() failed: {e}")
            return self._describe_fallback()

    def _describe_fallback(self) -> dict:
        """
        Fallback template when Groq fails.
        Always returns is_fallback: true
        """
        return {
            "description":  "AI description unavailable at this time.",
            "risk_level":   "UNKNOWN",
            "findings":     [],
            "generated_at": _now(),
            "is_fallback":  True
        }

    # ── /recommend ────────────────────────────────────────────────────────────
    def recommend(self, resource: str) -> dict:
        if not resource or not resource.strip():
            return self._recommend_fallback()

        try:
            from services.cache import get_cached, set_cached
            cached = get_cached("recommend", resource)
            if cached:
                return cached
        except Exception:
            pass

        try:
            raw = self._call_groq(
                _load_prompt("recommend_system.txt"),
                resource,
                temperature=0.4,
                max_tokens=self.TOKENS["recommend"]
            )

            # ── Fallback if Groq returns None ─────────────────────────────────
            if raw is None:
                logger.error("recommend() got None from Groq — returning fallback")
                return self._recommend_fallback()

            parsed = json.loads(_clean_response(raw))
            recs   = (parsed if isinstance(parsed, list)
                      else parsed.get("recommendations", []))
            result = {
                "recommendations": recs[:3],
                "generated_at":    _now(),
                "is_fallback":     False
            }

            try:
                from services.cache import set_cached
                set_cached("recommend", resource, result)
            except Exception:
                pass

            return result

        except Exception as e:
            logger.error(f"recommend() failed: {e}")
            return self._recommend_fallback()

    def _recommend_fallback(self) -> dict:
        """
        Fallback template when Groq fails.
        Always returns is_fallback: true
        """
        return {
            "recommendations": [
                {"action_type": "REVIEW",
                 "description": "Manually review this resource configuration.",
                 "priority":    "HIGH"},
                {"action_type": "AUDIT",
                 "description": "Conduct a security audit of access controls.",
                 "priority":    "MEDIUM"},
                {"action_type": "MONITOR",
                 "description": "Enable monitoring and alerting.",
                 "priority":    "LOW"}
            ],
            "generated_at": _now(),
            "is_fallback":  True
        }

    # ── /generate-report ──────────────────────────────────────────────────────
    def generate_report(self, environment: str) -> dict:
        if not environment or not environment.strip():
            return self._report_fallback()

        try:
            from services.cache import get_cached, set_cached
            cached = get_cached("report", environment)
            if cached:
                return cached
        except Exception:
            pass

        try:
            raw = self._call_groq(
                _load_prompt("report_system.txt"),
                environment,
                temperature=0.3,
                max_tokens=self.TOKENS["report"]
            )

            # ── Fallback if Groq returns None ─────────────────────────────────
            if raw is None:
                logger.error("generate_report() got None — returning fallback")
                return self._report_fallback()

            parsed = json.loads(_clean_response(raw))
            parsed["generated_at"] = _now()
            parsed["is_fallback"]  = False

            try:
                from services.cache import set_cached
                set_cached("report", environment, parsed)
            except Exception:
                pass

            return parsed

        except Exception as e:
            logger.error(f"generate_report() failed: {e}")
            return self._report_fallback()

    def _report_fallback(self) -> dict:
        """
        Fallback template when Groq fails.
        Always returns is_fallback: true
        """
        return {
            "title":           "Security Posture Report — Unavailable",
            "summary":         "Report generation is temporarily unavailable.",
            "overview":        "",
            "key_items":       [],
            "recommendations": [],
            "generated_at":    _now(),
            "is_fallback":     True
        }