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


def _load_prompt(filename):
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return f.read()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _clean_response(raw: str) -> str:
    """Strip markdown fences if model adds them."""
    return raw.strip().strip("```json").strip("```").strip()


class GroqClient:
    MODEL        = "llama-3.3-70b-versatile"
    RETRY_DELAYS = [2, 4, 8]

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not set in .env file")
        self.client = Groq(api_key=api_key)

    def _call_groq(self, system_prompt: str,
                   user_message: str,
                   temperature: float = 0.3) -> str | None:
        """
        Call Groq API with retry logic.
        Returns response text or None if all retries fail.
        """
        last_error = None

        for attempt, delay in enumerate(self.RETRY_DELAYS, start=1):
            try:
                response = self.client.chat.completions.create(
                    model=self.MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_message},
                    ],
                    temperature=temperature,
                    max_tokens=800,
                )
                return response.choices[0].message.content

            except Exception as e:
                last_error = e
                logger.warning(f"Groq attempt {attempt} failed: {e}")
                if attempt < len(self.RETRY_DELAYS):
                    time.sleep(delay)

        logger.error(f"All Groq retries failed: {last_error}")
        return None   # ← return None, never crash

    def describe(self, resource: str) -> dict:
        """
        Describe a cloud resource.
        Always returns a dict — never raises exception.
        is_fallback=True if AI failed.
        """
        # ── Null check ────────────────────────────────────────────────────────
        if not resource or not resource.strip():
            logger.warning("describe() called with empty resource")
            return self._describe_fallback()

        try:
            raw = self._call_groq(
                _load_prompt("describe_system.txt"),
                resource,
                temperature=0.3
            )

            # ── Handle null from Groq ─────────────────────────────────────────
            if raw is None:
                logger.error("describe() got None from Groq")
                return self._describe_fallback()

            parsed = json.loads(_clean_response(raw))
            parsed["generated_at"] = _now()
            parsed["is_fallback"]  = False
            return parsed

        except Exception as e:
            logger.error(f"describe() failed: {e}")
            return self._describe_fallback()

    def _describe_fallback(self) -> dict:
        """Fallback response when describe() fails."""
        return {
            "description":  "AI description unavailable at this time.",
            "risk_level":   "UNKNOWN",
            "findings":     [],
            "generated_at": _now(),
            "is_fallback":  True
        }

    def recommend(self, resource: str) -> dict:
        """
        Return 3 recommendations.
        Always returns a dict — never raises exception.
        is_fallback=True if AI failed.
        """
        if not resource or not resource.strip():
            logger.warning("recommend() called with empty resource")
            return self._recommend_fallback()

        try:
            raw = self._call_groq(
                _load_prompt("recommend_system.txt"),
                resource,
                temperature=0.4
            )

            if raw is None:
                logger.error("recommend() got None from Groq")
                return self._recommend_fallback()

            parsed = json.loads(_clean_response(raw))
            recs   = (parsed if isinstance(parsed, list)
                      else parsed.get("recommendations", []))
            return {
                "recommendations": recs[:3],
                "generated_at":    _now(),
                "is_fallback":     False
            }

        except Exception as e:
            logger.error(f"recommend() failed: {e}")
            return self._recommend_fallback()

    def _recommend_fallback(self) -> dict:
        """Fallback response when recommend() fails."""
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

    def generate_report(self, environment: str) -> dict:
        """
        Generate full security report.
        Always returns a dict — never raises exception.
        """
        if not environment or not environment.strip():
            logger.warning("generate_report() called with empty environment")
            return self._report_fallback()

        try:
            raw = self._call_groq(
                _load_prompt("report_system.txt"),
                environment,
                temperature=0.3
            )

            if raw is None:
                logger.error("generate_report() got None from Groq")
                return self._report_fallback()

            parsed = json.loads(_clean_response(raw))
            parsed["generated_at"] = _now()
            parsed["is_fallback"]  = False
            return parsed

        except Exception as e:
            logger.error(f"generate_report() failed: {e}")
            return self._report_fallback()

    def _report_fallback(self) -> dict:
        """Fallback response when generate_report() fails."""
        return {
            "title":           "Security Posture Report — Unavailable",
            "summary":         "Report generation is temporarily unavailable.",
            "overview":        "",
            "key_items":       [],
            "recommendations": [],
            "generated_at":    _now(),
            "is_fallback":     True
        }