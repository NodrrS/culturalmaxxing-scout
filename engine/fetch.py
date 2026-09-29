"""Polite HTTP and the structured-feed readers used by Agent 2.

Why feeds first: Shopify and WooCommerce publish product data as JSON, with
exact prices and stock. Reading that is cheaper, faster and more accurate than
asking a model to read HTML. The model path in agent2_extraction.py is only for
sites that publish no feed.

Politeness rules, enforced here:
- robots.txt is checked before every request; a disallowed URL is skipped.
- At least MIN_INTERVAL seconds between requests to the same host, or the
  site's crawl-delay if it is longer.
- A User-Agent that names the bot and a contact address from CMX_BOT_CONTACT.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
import urllib.robotparser
from html import unescape
from urllib.parse import urljoin, urlsplit

MIN_INTERVAL = 1.5
TIMEOUT = 20
BOT_NAME = "CulturalmaxxingBot"


def user_agent() -> str:
    contact = os.environ.get("CMX_BOT_CONTACT", "contact-not-configured")
    return f"{BOT_NAME}/0.1 (discovery for a Berlin cultural fashion map; {contact})"


class Blocked(Exception):
    """robots.txt disallows this URL for our bot."""


_robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
_last_hit: dict[str, float] = {}


def _origin(url: str) -> str:
    p = urlsplit(url)
    return f"{p.scheme}://{p.netloc}"


def _robots_for(url: str) -> urllib.robotparser.RobotFileParser | None:
    origin = _origin(url)
    if origin not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(origin + "/robots.txt", headers={"User-Agent": user_agent()})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                rp.parse(r.read().decode("utf-8", "replace").splitlines())
        except urllib.error.HTTPError as e:
            # 4xx means "no robots.txt": everything allowed. 5xx: be careful, allow nothing.
            rp.parse([] if 400 <= e.code < 500 else ["User-agent: *", "Disallow: /"])
        except urllib.error.URLError:
            rp = None
        _robots[origin] = rp
    return _robots[origin]


def allowed(url: str) -> bool:
    rp = _robots_for(url)
    return rp is None or rp.can_fetch(BOT_NAME, url)


def get(url: str, accept: str = "*/*") -> tuple[int, bytes]:
    if not allowed(url):
        raise Blocked(url)
    host = urlsplit(url).netloc
    rp = _robots_for(url)
    delay = max(MIN_INTERVAL, (rp.crawl_delay(BOT_NAME) or 0) if rp else 0)
    wait = _last_hit.get(host, 0) + delay - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": user_agent(), "Accept": accept})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                _last_hit[host] = time.monotonic()
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            _last_hit[host] = time.monotonic()
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            return e.code, b""
        except urllib.error.URLError:
            if attempt < 2:
                time.sleep(3)
                continue
            raise
    return 0, b""


def get_json(url: str):
    status, body = get(url, accept="application/json")
    if status != 200 or not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def strip_html(html: str, limit: int = 600) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html or "", flags=re.S | re.I)
    text = unescape(re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"\s+", " ", text).strip()[:limit]


# ---- platform detection ------------------------------------------------------

def detect_platform(site: str) -> str:
    site = site.rstrip("/")
    data = get_json(site + "/products.json?limit=1")
    if isinstance(data, dict) and isinstance(data.get("products"), list):
        return "shopify"
    data = get_json(site + "/wp-json/wc/store/v1/products?per_page=1")
    if isinstance(data, list):
        return "woocommerce"
    return "html"


# ---- feed readers -> normalized products --------------------------------------
# Normalized product fields (all readers produce the same shape):
#   source_id, shop_slug, title, url, price_min, price_max, currency, available,
#   sizes, product_type_raw, tags_raw, image_urls, description_internal, updated_at
# `description_internal` is kept only so Agent 3 can classify. It is never
# displayed: public copy is written fresh and approved by the shop.
# `image_urls` are references, never re-hosted or shown without permission.

def read_shopify(site: str, shop_slug: str, max_products: int = 500, collection: str | None = None) -> list[dict]:
    """collection: read only one Shopify collection (e.g. the clothing section)."""
    site = site.rstrip("/")
    base = f"{site}/collections/{collection}" if collection else site
    out: list[dict] = []
    page = 1
    while len(out) < max_products:
        data = get_json(f"{base}/products.json?limit=250&page={page}")
        items = (data or {}).get("products") or []
        if not items:
            break
        for p in items:
            variants = p.get("variants") or []
            prices = [float(v["price"]) for v in variants if v.get("price") not in (None, "")]
            sizes = [v.get("option1") for v in variants
                     if v.get("option1") and v.get("option1") != "Default Title"]
            tags = p.get("tags") or []
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            out.append({
                "source_id": f"shopify:{urlsplit(site).netloc}:{p['id']}",
                "shop_slug": shop_slug,
                "title": p.get("title", "").strip(),
                "url": f"{site}/products/{p['handle']}",
                "price_min": min(prices) if prices else None,
                "price_max": max(prices) if prices else None,
                "currency": "EUR",
                "available": any(v.get("available") for v in variants),
                "sizes": sizes,
                "sizes_available": [v.get("option1") for v in variants
                                    if v.get("available") and v.get("option1") not in (None, "Default Title")],
                "product_type_raw": p.get("product_type") or "",
                "tags_raw": tags,
                "image_urls": [i.get("src") for i in (p.get("images") or [])[:3] if i.get("src")],
                "description_internal": strip_html(p.get("body_html") or ""),
                "updated_at": p.get("updated_at"),
            })
        page += 1
    return out[:max_products]


def woo_category_id(site: str, slug: str) -> int | None:
    cats = get_json(f"{site.rstrip('/')}/wp-json/wc/store/v1/products/categories?per_page=100") or []
    return next((c["id"] for c in cats if c.get("slug") == slug), None)


def read_woocommerce(site: str, shop_slug: str, max_products: int = 500, category: str | None = None) -> list[dict]:
    """category: a category slug; read only that section (e.g. clothing, not teapots)."""
    site = site.rstrip("/")
    extra = ""
    if category:
        cid = woo_category_id(site, category)
        if cid is None:
            raise ValueError(f"category '{category}' not found on {site}")
        extra = f"&category={cid}"
    out: list[dict] = []
    page = 1
    while len(out) < max_products:
        items = get_json(f"{site}/wp-json/wc/store/v1/products?per_page=100&page={page}{extra}")
        if not isinstance(items, list) or not items:
            break
        for p in items:
            pr = p.get("prices") or {}
            unit = 10 ** int(pr.get("currency_minor_unit", 2) or 0)
            price = float(pr["price"]) / unit if pr.get("price") not in (None, "") else None
            out.append({
                "source_id": f"woo:{urlsplit(site).netloc}:{p['id']}",
                "shop_slug": shop_slug,
                "title": unescape(p.get("name", "")).strip(),
                "url": p.get("permalink"),
                "price_min": price,
                "price_max": price,
                "currency": pr.get("currency_code", "EUR"),
                "available": bool(p.get("is_in_stock")),
                "sizes": [],
                "sizes_available": [],
                "product_type_raw": ", ".join(c.get("name", "") for c in p.get("categories") or []),
                "tags_raw": [t.get("name", "") for t in p.get("tags") or []],
                "image_urls": [i.get("src") for i in (p.get("images") or [])[:3] if i.get("src")],
                "description_internal": strip_html(p.get("short_description") or p.get("description") or ""),
                "updated_at": None,
            })
        page += 1
    return out[:max_products]


def join(site: str, path: str) -> str:
    return urljoin(site.rstrip("/") + "/", path.lstrip("/"))
