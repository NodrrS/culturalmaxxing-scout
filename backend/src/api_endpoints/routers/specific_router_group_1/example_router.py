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
    - ``validators`` for input checks
    - ``data_loader`` for static reference data
    - ``log_handler`` for structured logging
    - ``limiter`` (SlowAPI) for rate limiting
"""

#Native imports
import uuid
from typing import Dict, List, Optional

#Third-party imports
from fastapi import APIRouter, Body, HTTPException, Request

#Other files imports
from src.utils.custom_logger import log_handler
from src.utils.limiter import limiter as SlowLimiter
from src.core_specs.configuration.config_loader import config_loader
from src.core_specs.data.data_loader import data_loader
from src.utils.validators import validate_email_format
from src.models.models_example import (
    ExampleItem,
    ExampleItemCreate,
    ExampleItemResponse,
)

"""VARIABLES-----------------------------------------------------------"""
#In-memory store for demo purposes; replace with a real data source in production.
_items_store: Dict[str, ExampleItem] = {}

"""API ROUTER-----------------------------------------------------------"""
router = APIRouter(
    prefix=config_loader["endpoints"]["example_endpoint_1"]["endpoint_prefix"],
    tags=[config_loader["endpoints"]["example_endpoint_1"]["endpoint_tag"]],
)

"""ENDPOINTS-----------------------------------------------------------"""
@router.get(config_loader["endpoints"]["example_endpoint_1"]["endpoint_route"])
@SlowLimiter.limit(
    f"{config_loader['endpoints']['example_endpoint_1']['request_limit']}/"
    f"{config_loader['endpoints']['example_endpoint_1']['unit_of_time_for_limit']}"
)
async def list_example_items(request: Request) -> List[ExampleItemResponse]:
    """
    List all example items.

    Parameters:
        request (Request): Incoming HTTP request (required by the rate limiter).

    Returns:
        list[ExampleItemResponse]: All stored example items.
    """
    log_handler.debug(
        "Listing example items (supported languages: %s)",
        data_loader.get("languages", []),
    )
    return list(_items_store.values())
