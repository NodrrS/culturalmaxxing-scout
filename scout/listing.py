"""From a shop Scout found to a draft listing.

Uses the engine as it is. The shop's own feed is read with no model call, the
rules tag what they can, and only the uncertain rest goes to Nemotron, with the
closed vocabulary as the schema, so it cannot invent a tag.

The result is a draft for the shop to approve. It holds facts and links: no
product descriptions and no photographs, because both belong to the shop.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "engine"))

import agent  # noqa: E402
import clients  # noqa: E402
from links import outbound_url  # noqa: E402  engine
from taxonomy import CULTURES, price_band  # noqa: E402  engine

FEEDS = ("shopify", "woocommerce")


class NoFeed(Exception):
    """The shop publishes no product feed, or asks crawlers to stay out."""


def engine_shop(record: dict) -> dict:
    """A Scout record in the shape the engine's agents expect."""
    if not record.get("website"):
        raise NoFeed("the shop has no website")
    if record.get("crawl") is False:
        raise NoFeed("the shop's robots.txt asks crawlers to stay out; ask the shop directly")
    culture = record.get("culture_guess")
    return {
        "slug": re.sub(r"[^a-z0-9]+", "-", record["name"].lower()).strip("-") or "shop",
        "name": record["name"],
        "website": agent.with_scheme(record["website"]).rstrip("/"),
        "platform": record.get("platform") if record.get("platform") in FEEDS else None,
        "default_culture": culture if culture in CULTURES else None,
        "status": "not_contacted",
    }


def read(shop: dict, max_products: int = 60) -> list[dict]:
    """Read the shop's feed with the engine's polite fetcher. No model call."""
    from agent2_extraction import extract_products
    platform, products = extract_products(shop, use_llm=False, max_products=max_products)
    if platform not in FEEDS:
        raise NoFeed("the shop publishes no Shopify or WooCommerce feed")
    shop["platform"] = platform
    return products


def tag(products: list[dict], shop: dict, use_model: bool = True, model_limit: int = 20) -> tuple[list[dict], list[dict]]:
    """Rules first. Nemotron only for what the rules could not settle, at most model_limit products."""
    from agent3_taxonomy import SYSTEM, _schema, classify
    items, proposals = classify(products, shop, use_llm=False)
    pending = [i for i in items if i["confidence"] != "high"][:model_limit]
    if not (use_model and pending and os.environ.get("NEBIUS_API_KEY")):
        return items, proposals

    by_id = {p["source_id"]: p for p in products}
    payload = [{
        "source_id": r["source_id"],
        "title": by_id[r["source_id"]].get("title_en") or by_id[r["source_id"]]["title"],
        "product_type": by_id[r["source_id"]]["product_type_raw"],
        "tags": by_id[r["source_id"]]["tags_raw"],
        "description": by_id[r["source_id"]]["description_internal"][:400],
        "rules_guess": {k: r[k] for k in ("category", "audience", "occasions", "craft_terms")},
    } for r in pending]
    result = clients.structured(
        system=SYSTEM,
        prompt=f"Shop: {shop['name']} (default culture: {shop.get('default_culture')}).\n"
               f"Classify these {len(payload)} products:\n{json.dumps(payload, ensure_ascii=False)}",
        schema=_schema(), max_tokens=8000)
    fresh = {}
    for item in result["items"]:
        if item["source_id"] in by_id:                       # ignore ids the model made up
            item["price_band"] = price_band(by_id[item["source_id"]].get("price_min"))
            item["classified_by"] = "nemotron"
            fresh[item["source_id"]] = item
    items = [fresh.get(i["source_id"], i) for i in items]
    proposals = [dict(pr, source_id=i["source_id"]) for i in items for pr in i.get("proposals", [])]
    return items, proposals


def summarise(products: list[dict], items: list[dict], proposals: list[dict], shop: dict, show: int = 6) -> dict:
    tags = {i["source_id"]: i for i in items}
    stocked = [p for p in products if p.get("available")]
    prices = [p["price_min"] for p in stocked if p.get("price_min") is not None]
    categories = Counter(i["category"] for i in items if i.get("category"))
    crafts = Counter(c for i in items for c in i.get("craft_terms", []))
    wanted = Counter((p["field"], p["term"]) for p in proposals)

    picks = [p for p in stocked if tags[p["source_id"]]["confidence"] in ("high", "medium")
             and tags[p["source_id"]].get("category") not in (None, "home", "other")]
    # One product per category first, so the sample shows the range of the shop.
    seen, first, rest = set(), [], []
    for p in picks:
        cat = tags[p["source_id"]]["category"]
        (rest if cat in seen else first).append(p)
        seen.add(cat)
    sample = []
    for n, p in enumerate((first + rest)[:show], 1):
        t = tags[p["source_id"]]
        sample.append({
            "title": p.get("title_en") or p["title"], "title_original": p["title"],
            "price": p.get("price_min"), "currency": p.get("currency", "EUR"),
            "category": t["category"], "audience": t.get("audience"), "occasions": t.get("occasions", []),
            "craft_terms": t.get("craft_terms", []), "confidence": t["confidence"],
            "tagged_by": t.get("classified_by", "rules"),
            "url": outbound_url(p["url"], shop, f"s{n}"),
        })
    return {
        "status": "draft_awaiting_shop_approval",
        "shop": shop["name"], "platform": shop.get("platform"),
        "read": len(products), "in_stock": len(stocked),
        "price_from": min(prices) if prices else None, "price_to": max(prices) if prices else None,
        "tagged": {c: sum(1 for i in items if i["confidence"] == c) for c in ("high", "medium", "low")},
        "tagged_by": dict(Counter(i.get("classified_by", "rules") for i in items)),
        "categories": categories.most_common(6),
        "craft_terms": crafts.most_common(6),
        "proposals": [{"field": f, "term": t, "products": n} for (f, t), n in wanted.most_common(5)],
        "sample": sample,
    }


def draft(record: dict, max_products: int = 60, use_model: bool = True) -> dict:
    shop = engine_shop(record)
    products = read(shop, max_products)
    items, proposals = tag(products, shop, use_model=use_model)
    return summarise(products, items, proposals, shop)
