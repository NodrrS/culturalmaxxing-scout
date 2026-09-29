"""
#############################################################################
### Redis client module
###
### @file redis_client.py
### @date 2025
#############################################################################

Creates an optional Redis connection when REDIS_ENABLED=true.
Connection failures are logged and never crash the application.
"""

#Native imports
import os

#Third-party imports
import redis

#Other files imports
from src.utils.custom_logger import log_handler


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("true", "1", "yes")


REDIS_ENABLED = _parse_bool(os.getenv("REDIS_ENABLED"), False)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

redis_client: redis.Redis | None = None

if REDIS_ENABLED:
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
        )
        redis_client.ping()
        log_handler.info(
            "Redis connected at %s:%s/%s", REDIS_HOST, REDIS_PORT, REDIS_DB
        )
    except Exception as exc:
        redis_client = None
        log_handler.warning("Redis connection failed: %s. Cache unavailable.", exc)
else:
    log_handler.info("Redis is disabled (REDIS_ENABLED=false)")


def get_redis_status() -> str:
    """
    Return Redis health for the API health endpoint.

    Returns:
        str: "disabled", "connected", or "unavailable".
    """
    if not REDIS_ENABLED:
        return "disabled"
    if redis_client is None:
        return "unavailable"
    try:
        redis_client.ping()
        return "connected"
    except Exception:
        return "unavailable"


def close_redis() -> None:
    """Close the Redis connection pool on application shutdown."""
    if redis_client is not None:
        try:
            redis_client.close()
            log_handler.info("Redis connection closed")
        except Exception as exc:
            log_handler.warning("Error closing Redis connection: %s", exc)
