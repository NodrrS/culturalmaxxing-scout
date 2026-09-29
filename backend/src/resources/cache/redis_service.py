"""
#############################################################################
### Redis cache service module
###
### @file redis_service.py
### @date 2025
#############################################################################

Application-level cache helpers. Routers and services should use these
functions instead of importing redis_client directly.
"""

#Native imports
import json
from typing import Any

#Other files imports
from src.resources.cache.redis_client import redis_client


def cache_get(key: str) -> Any | None:
    """
    Retrieve cached data by key.

    Returns:
        Deserialized value if found, otherwise None.
    """
    if redis_client is None:
        return None
    try:
        raw = redis_client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        return None


def cache_set(key: str, value: Any, expiration_seconds: int) -> bool:
    """
    Store data in the cache with a TTL.

    Returns:
        True if stored successfully, False otherwise.
    """
    if redis_client is None:
        return False
    try:
        redis_client.setex(key, expiration_seconds, json.dumps(value))
        return True
    except Exception:
        return False


def cache_delete(key: str) -> bool:
    """
    Remove cached data by key.

    Returns:
        True if deleted (or key absent), False if Redis is unavailable.
    """
    if redis_client is None:
        return False
    try:
        redis_client.delete(key)
        return True
    except Exception:
        return False
