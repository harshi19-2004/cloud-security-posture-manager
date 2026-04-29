"""
cache.py
Day 7 — AI Developer 1

Redis AI cache with SHA256 key and 15 minute TTL.
Falls back to no-cache if Redis is not running.
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Try to connect to Redis — fallback to None if not available
try:
    import redis
    REDIS_URL    = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info("Redis connected successfully")
except Exception as e:
    redis_client    = None
    REDIS_AVAILABLE = False
    logger.warning(f"Redis not available — cache disabled: {e}")

# 15 minutes TTL in seconds
CACHE_TTL = 15 * 60


def make_cache_key(endpoint: str, input_text: str) -> str:
    """
    Create SHA256 cache key from endpoint name + input text.
    Same input always gives same key.

    Example:
        make_cache_key("describe", "AWS S3 bucket...")
        → "ai:describe:a3f8c2d1..."
    """
    raw     = f"{endpoint}:{input_text.strip().lower()}"
    sha256  = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"ai:{endpoint}:{sha256}"


def get_cached(endpoint: str, input_text: str) -> dict | None:
    """
    Get cached AI response from Redis.

    Returns:
        dict  — cached result if found
        None  — if not in cache or Redis unavailable
    """
    if not REDIS_AVAILABLE or redis_client is None:
        return None

    try:
        key    = make_cache_key(endpoint, input_text)
        cached = redis_client.get(key)

        if cached:
            logger.info(f"Cache HIT for key: {key[:40]}...")
            data = json.loads(cached)
            data["cache_hit"] = True
            return data

        logger.info(f"Cache MISS for key: {key[:40]}...")
        return None

    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None


def set_cached(endpoint: str, input_text: str, result: dict) -> bool:
    """
    Save AI response to Redis cache with 15 min TTL.

    Returns:
        True  — if saved successfully
        False — if failed or Redis unavailable
    """
    if not REDIS_AVAILABLE or redis_client is None:
        return False

    try:
        key  = make_cache_key(endpoint, input_text)
        data = result.copy()
        data["cached_at"] = datetime.now(timezone.utc).isoformat()
        data.pop("cache_hit", None)

        redis_client.setex(key, CACHE_TTL, json.dumps(data))
        logger.info(f"Cache SET for key: {key[:40]}... TTL={CACHE_TTL}s")
        return True

    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False


def get_cache_status() -> dict:
    """
    Returns Redis connection status for /health endpoint.
    """
    if not REDIS_AVAILABLE or redis_client is None:
        return {
            "redis_connected": False,
            "cache_ttl_seconds": CACHE_TTL,
            "message": "Redis not available — running without cache"
        }

    try:
        info = redis_client.info()
        return {
            "redis_connected":    True,
            "cache_ttl_seconds":  CACHE_TTL,
            "redis_version":      info.get("redis_version", "unknown"),
            "connected_clients":  info.get("connected_clients", 0),
            "message":            "Redis connected and cache active"
        }
    except Exception as e:
        return {
            "redis_connected":   False,
            "cache_ttl_seconds": CACHE_TTL,
            "message":           f"Redis error: {e}"
        }