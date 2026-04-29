"""
GET /health
Day 7 — Returns model name, avg response time, uptime, cache status
"""

import time
from flask import Blueprint, jsonify
from services.cache import get_cache_status

health_bp   = Blueprint("health", __name__)
_start_time = time.time()


@health_bp.route("/health", methods=["GET"])
def health():
    uptime_seconds = int(time.time() - _start_time)

    # Format uptime nicely
    hours   = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60

    return jsonify({
        "status":          "ok",
        "service":         "Tool-59 AI Service",
        "model":           "llama-3.3-70b-versatile",
        "uptime_seconds":  uptime_seconds,
        "uptime_human":    f"{hours}h {minutes}m {seconds}s",
        "avg_response_ms": _get_avg_response_ms(),
        "cache":           get_cache_status(),
        "endpoints": [
            "POST /describe",
            "POST /recommend",
            "POST /generate-report",
            "GET  /health"
        ]
    }), 200


def _get_avg_response_ms() -> float:
    """
    Returns average Groq response time in milliseconds.
    Gets this from groq_client response tracker.
    """
    try:
        from services.groq_client import get_avg_response_ms
        return get_avg_response_ms()
    except Exception:
        return 0.0