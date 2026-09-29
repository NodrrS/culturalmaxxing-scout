"""
#############################################################################
### Example item service module
###
### @file example_item_service.py
### @date 2026
#############################################################################

Demo service showing optional Redis caching. Routers call this module;
cache operations stay in ``redis_service``, not in route handlers.
"""

#Native imports
from typing import Dict, Optional

#Other files imports
from src.models.models_example import ExampleItem
from src.resources.cache.redis_service import cache_get, cache_set
from src.utils.custom_logger import log_handler

_CACHE_TTL_SECONDS = 600
_CACHE_KEY_PREFIX = "example_item:"

# In-memory store for demo purposes; replace with a real data source in production.
_items_store: Dict[str, ExampleItem] = {
    "demo-001": ExampleItem(
        id="demo-001",
        name="Demo item",
        description="Seeded item for the Redis cache example",
    ),
}


def get_example_item_by_id(item_id: str) -> Optional[ExampleItem]:
    """
    Fetch an example item, using Redis as an optional cache layer.

    Returns:
        ExampleItem if found, otherwise None.
    """
    cache_key = f"{_CACHE_KEY_PREFIX}{item_id}"

    cached = cache_get(cache_key)
    if cached is not None:
        log_handler.debug("Cache hit for example item %s", item_id)
        return ExampleItem(**cached)

    item = _items_store.get(item_id)
    if item is None:
        return None

    cache_set(cache_key, item.model_dump(), expiration_seconds=_CACHE_TTL_SECONDS)
    log_handler.debug("Cache miss for example item %s", item_id)
    return item
