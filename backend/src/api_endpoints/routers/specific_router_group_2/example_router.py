"""
#############################################################################
### Example router file
###
### @file example_router.py
### @author Sebastian Russo
### @date 2026
#############################################################################

Reference router for this template. Copy this file (and its matching
``config_file.json`` entries) when adding new endpoint groups.

ONLY ONE ENDPOINT SHOULD BE IN THIS FILE. for other endpoints they should be in
their own file but within this same folder, in order to have a more organized code
in folders and not a single endless file.

Demonstrates:
    - ``config_loader`` for prefix, tag, route, and per-endpoint rate limits
    - Pydantic models for request/response bodies (``src/models/``)
    - ``log_handler`` for structured logging
    - ``limiter`` (SlowAPI) for rate limiting
    - Optional Redis cache via ``example_item_service`` (not direct Redis imports)
"""

#Third-party imports
from fastapi import APIRouter, HTTPException, Request

#Other files imports
from src.utils.custom_logger import log_handler
from src.utils.limiter import limiter as SlowLimiter
from src.core_specs.configuration.config_loader import config_loader
from src.resources.example_item_service import get_example_item_by_id
from src.models.models_example import ExampleItemResponse

"""API ROUTER-----------------------------------------------------------"""
router = APIRouter(
    prefix=config_loader["endpoints"]["example_endpoint_2"]["endpoint_prefix"],
    tags=[config_loader["endpoints"]["example_endpoint_2"]["endpoint_tag"]],
)

"""ENDPOINTS-----------------------------------------------------------"""
@router.get(config_loader["endpoints"]["example_endpoint_2"]["endpoint_route"])
@SlowLimiter.limit(
    f"{config_loader['endpoints']['example_endpoint_2']['request_limit']}/"
    f"{config_loader['endpoints']['example_endpoint_2']['unit_of_time_for_limit']}"
)
async def get_example_item(request: Request, item_id: str) -> ExampleItemResponse:
    """
    Get a single example item by ID (optional Redis cache via service layer).

    Parameters:
        request (Request): Incoming HTTP request (required by the rate limiter).
        item_id (str): Unique item identifier.

    Returns:
        ExampleItemResponse: The requested item.

    Raises:
        HTTPException: 404 if the item does not exist.
    """
    log_handler.debug("Fetching example item %s", item_id)
    item = get_example_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
