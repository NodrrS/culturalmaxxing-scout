"""Google Maps: leads from the Places API (New), with a Maps Demo Key.

Why: owners often add a new shop to Google Maps in its first days, before anyone
maps it on OpenStreetMap or a search engine finds its website. Scout asks Google
Maps for those leads and checks them like any other.

The key is GOOGLE_MAPS_API_KEY. A Maps Demo Key needs no credit card and has
daily limits; Google offers it for development and testing, not for a launched
product: https://mapsplatform.google.com/maps-demo-key/

What this module does to keep to Google's terms:
- It asks only for Pro fields: name, address, open or closed, kind of place.
  No website, opening hours, ratings or photos, and no coordinates.
- Nothing from Google is cached. Every search goes to Google.
- Only place IDs are kept: they are exempt from Google's caching limits. Links
  to Google Maps are built from them, and the screen credits Google Maps.
- Google places are never drawn on the OpenStreetMap map. A shop that only Google
  knows gets an "Open in Google Maps" link instead.
- The agent may send Google's results to the model only when the Nebius account
  keeps no data (see zero_retention()), because Google's content must not be
  stored by the model.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

import osm

ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
DEMO_KEY = "https://mapsplatform.google.com/maps-demo-key/"
# Text Search Pro: 5,000 free a month on a normal key. Adding websiteUri or opening hours
# would make every request Enterprise (1,000 free a month), so they are left out on purpose.
FIELDS = ",".join(f"places.{f}" for f in ("id", "displayName", "formattedAddress", "businessStatus",
                                          "primaryType", "types"))
STATUS = {"OPERATIONAL": "open", "CLOSED_TEMPORARILY": "closed for now", "CLOSED_PERMANENTLY": "closed for good"}


class GoogleError(RuntimeError):
    """Google Maps could not answer."""


def key() -> str | None:
    return os.environ.get("GOOGLE_MAPS_API_KEY", "").strip() or None


def zero_retention() -> bool:
    """The operator confirms that Zero Data Retention is on in Nebius Token Factory.

    Nebius stores prompts by default to speed up inference. Google's content must
    not be stored by the model, so Google results reach the model only with this set."""
    return os.environ.get("NEBIUS_ZERO_DATA_RETENTION", "").strip().lower() in ("on", "yes", "true", "1")


def enabled() -> bool:
    return bool(key()) and zero_retention()


def _http(url: str, body: bytes, headers: dict, timeout: float) -> tuple[int, str]:
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


transport = _http   # the offline tests replace this


def maps_link(place_id: str, label: str = "Google") -> str:
    """A Google Maps link made from the place ID alone. Maps URLs need no key."""
    return "https://www.google.com/maps/search/?" + urllib.parse.urlencode(
        {"api": 1, "query": label, "query_place_id": place_id})


def place_id_of(url: str) -> str | None:
    """The place ID in a Google Maps link made by maps_link(); None for any other URL."""
    parts = urllib.parse.urlsplit(url if "://" in str(url) else f"https://{url}")
    if not (parts.netloc.removeprefix("www.") == "google.com" and parts.path.startswith("/maps")):
        return None
    found = urllib.parse.parse_qs(parts.query).get("query_place_id")
    return found[0] if found else None


def _why(status: int, body: str) -> str:
    try:
        message = json.loads(body)["error"]["message"]
    except (ValueError, KeyError, TypeError):
        message = body[:160]
    if status == 429:
        return "the daily limit of the Google Maps key is used up; it resets tomorrow"
    if status in (401, 403):
        return f"Google did not accept the key: {message[:160]}"
    return f"Google Maps answered {status}: {message[:160]}"


def place(item: dict) -> dict | None:
    name = ((item.get("displayName") or {}).get("text") or "").strip()
    if not name or not item.get("id"):
        return None
    return {
        "name": name,
        "address": item.get("formattedAddress"),
        "status": STATUS.get(item.get("businessStatus"), "unknown"),
        "kind": item.get("primaryType") or next(iter(item.get("types") or []), None),
        "place_id": item["id"],
        "maps_url": maps_link(item["id"]),
    }


def search(query: str) -> dict:
    """Up to 20 places in Berlin that Google Maps finds for a short text, in any language."""
    api_key = key()
    if not api_key:
        raise GoogleError("GOOGLE_MAPS_API_KEY is not set")
    query = re.sub(r"\s+", " ", str(query or "")).strip()[:120]
    if len(query) < 3:
        return {"error": "give a short search text, such as 'hanbok Berlin'"}
    south, west, north, east = osm.BERLIN
    body = {
        "textQuery": query,
        "languageCode": "de",
        "regionCode": "DE",
        "pageSize": 20,
        "locationRestriction": {"rectangle": {"low": {"latitude": south, "longitude": west},
                                              "high": {"latitude": north, "longitude": east}}},
    }
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key, "X-Goog-FieldMask": FIELDS}
    try:
        status, text = transport(ENDPOINT, json.dumps(body).encode(), headers, 30)
    except OSError as e:
        raise GoogleError(f"Google Maps did not answer: {e}") from None
    if status != 200:
        raise GoogleError(_why(status, text))
    try:
        items = json.loads(text).get("places") or []
    except (ValueError, AttributeError):
        raise GoogleError("Google Maps sent an answer that was not JSON") from None
    places = [p for p in map(place, items) if p]
    return {"places": places, "found": len(places)}
