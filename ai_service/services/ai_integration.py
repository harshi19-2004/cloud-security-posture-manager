"""
ai_integration.py
Day 5 — AI Developer 1

This file ties all 3 AI endpoints together.
It simulates what AiServiceClient.java does on the Java side —
calling AI when a record is created and attaching the result.

If AI fails for any reason → returns None gracefully (never crashes).
"""

import logging
from services.groq_client import GroqClient

logger      = logging.getLogger(__name__)
groq_client = GroqClient()


def run_describe_on_create(resource: str) -> dict | None:
    """
    Called automatically when a new cloud resource record is created.
    Runs /describe and attaches AI result to the record.

    Returns:
        dict  — AI result if successful
        None  — if AI fails (handle null gracefully!)
    """
    if not resource or not resource.strip():
        logger.warning("run_describe_on_create: empty resource, skipping AI call")
        return None

    try:
        result = groq_client.describe(resource.strip())

        # If fallback returned, still attach it but log it
        if result.get("is_fallback"):
            logger.warning("run_describe_on_create: AI returned fallback response")

        return result

    except Exception as e:
        logger.error(f"run_describe_on_create failed: {e}")
        return None          # ← handle null gracefully


def run_recommend_on_create(resource: str) -> dict | None:
    """
    Called automatically when a new cloud resource record is created.
    Runs /recommend and attaches 3 recommendations to the record.

    Returns:
        dict  — AI result if successful
        None  — if AI fails (handle null gracefully!)
    """
    if not resource or not resource.strip():
        logger.warning("run_recommend_on_create: empty resource, skipping AI call")
        return None

    try:
        result = groq_client.recommend(resource.strip())

        if result.get("is_fallback"):
            logger.warning("run_recommend_on_create: AI returned fallback response")

        return result

    except Exception as e:
        logger.error(f"run_recommend_on_create failed: {e}")
        return None          # ← handle null gracefully


def run_full_ai_on_create(resource: str) -> dict:
    """
    Runs BOTH describe and recommend when a record is created.
    This is the main function Java's AiServiceClient calls.

    Always returns a dict — never crashes.
    If AI fails, returns null values gracefully.

    Returns:
        {
            "describe":    { ...AI result... } or None,
            "recommend":   { ...AI result... } or None,
            "ai_attached": True if at least one succeeded
        }
    """
    describe_result  = run_describe_on_create(resource)
    recommend_result = run_recommend_on_create(resource)

    ai_attached = (describe_result is not None or
                   recommend_result is not None)

    return {
        "describe":    describe_result,
        "recommend":   recommend_result,
        "ai_attached": ai_attached
    }


def safe_get_description(ai_result: dict | None) -> str:
    """
    Safely extract description from AI result.
    Returns empty string if result is None or missing.
    """
    if ai_result is None:
        return ""
    return ai_result.get("description", "")


def safe_get_risk_level(ai_result: dict | None) -> str:
    """
    Safely extract risk_level from AI result.
    Returns UNKNOWN if result is None or missing.
    """
    if ai_result is None:
        return "UNKNOWN"
    return ai_result.get("risk_level", "UNKNOWN")


def safe_get_recommendations(ai_result: dict | None) -> list:
    """
    Safely extract recommendations list from AI result.
    Returns empty list if result is None or missing.
    """
    if ai_result is None:
        return []
    return ai_result.get("recommendations", [])