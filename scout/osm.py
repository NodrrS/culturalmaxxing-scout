"""OpenStreetMap: the map that people keep up themselves.

Many small shops that a web search never shows are on OpenStreetMap, put there by
people who live nearby, often without a website. Scout uses two public services:

- Overpass API, to find fashion shops in Berlin by name, or around a place.
- Nominatim, to turn a street or an address into coordinates.

Both are run by volunteers, so this module keeps to their usage policies:
- Every request names the app and a contact (CMX_BOT_CONTACT) in its User-Agent.
- Nominatim gets at most one request per second.
- Answers are cached on disk: Overpass for a day, Nominatim for a month.
- Overpass queries use a bounding box, not an area: area queries time out when a
  server is busy. A busy server is skipped for the next one in OVERPASS_URL.

OpenStreetMap data is (c) OpenStreetMap contributors, available under the ODbL.
Every place Scout returns carries the link to its OpenStreetMap page, and the
screen credits OpenStreetMap under the map.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
CACHE = HERE / "cache" / "osm"
OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]
NOMINATIM = "https://nominatim.openstreetmap.org/search"
REPO = "https://github.com/NodrrS/culturalmaxxing-scout"

# south, west, north, east. It takes in a little of Brandenburg; the agent checks addresses anyway.
BERLIN = (52.3383, 13.0884, 52.6755, 13.7611)
SHOPS = ["clothes", "boutique", "fashion", "fabric", "tailor", "bridal", "wedding", "second_hand",
         "fashion_accessories", "bag", "shoes", "jewelry", "hat"]
CRAFTS = ["tailor", "dressmaker"]
DAY = 86400
MAX_WORDS = 8
MAX_PLACES = 30
AROUND_M = 1200

sleep = time.sleep          # the offline tests replace these two
clock = time.monotonic
_last_nominatim = -1e9


class MapError(RuntimeError):
    """OpenStreetMap could not answer."""


def user_agent() -> str:
    contact = os.environ.get("CMX_BOT_CONTACT", "").strip() or "contact-not-configured"
    return f"culturalmaxxing-scout/0.1 (+{REPO}; {contact})"


def _http(method: str, url: str, data: bytes | None, timeout: float) -> tuple[int, str]:
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"User-Agent": user_agent(), "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


transport = _http


def _cached(key: str, max_age: float, fetch):
    path = CACHE / (hashlib.sha256(key.encode()).hexdigest()[:32] + ".json")
    if path.exists():
        try:
            entry = json.loads(path.read_text())
            if time.time() - entry["at"] < max_age:
                return entry["data"]
        except (ValueError, KeyError):
            pass
    data = fetch()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"at": time.time(), "data": data}, ensure_ascii=False))
    return data


# ---- Overpass --------------------------------------------------------------------

def overpass_urls() -> list[str]:
    raw = os.environ.get("OVERPASS_URL", "")
    return [u.strip() for u in raw.split(",") if u.strip()] or OVERPASS


def _overpass(query: str) -> list[dict]:
    def fetch():
        problems = []
        for url in overpass_urls():
            where = urllib.parse.urlsplit(url).netloc
            try:
                status, body = transport("POST", url, urllib.parse.urlencode({"data": query}).encode(), 45)
            except OSError as e:                     # timeouts and refused connections
                problems.append(f"{where}: {e}")
                continue
            if status != 200:
                problems.append(f"{where}: HTTP {status}")
                continue
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                problems.append(f"{where}: the answer was not JSON")
                continue
            if "runtime error" in (data.get("remark") or ""):
                problems.append(f"{where}: {data['remark'][:120]}")
                continue
            return data.get("elements", [])
        raise MapError("the OpenStreetMap servers are busy: " + "; ".join(problems))
    return _cached("overpass\n" + query, DAY, fetch)


def clean_words(words) -> list[str]:
    """Words safe to put into an Overpass pattern: letters, digits, spaces, hyphens, apostrophes."""
    if isinstance(words, str):
        words = [words]
    out: list[str] = []
    for w in words if isinstance(words, list) else []:
        w = re.sub(r"[^\w' -]|_", " ", str(w))
        w = re.sub(r"\s+", " ", w).strip().lower()[:40]
        if len(w) >= 3 and w not in out:
            out.append(w)
    return out[:MAX_WORDS]


def place(element: dict) -> dict | None:
    """One OpenStreetMap element as Scout shows it. None when it has no name or no position."""
    tags = element.get("tags") or {}
    name = (tags.get("name") or "").strip()
    centre = element.get("center") or {}
    lat, lon = element.get("lat", centre.get("lat")), element.get("lon", centre.get("lon"))
    if not name or lat is None or lon is None:
        return None
    street = " ".join(t for t in (tags.get("addr:street"), tags.get("addr:housenumber")) if t)
    town = " ".join(t for t in (tags.get("addr:postcode"), tags.get("addr:city")) if t)
    return {
        "name": name,
        "other_names": sorted({v for k, v in tags.items() if k.startswith("name:") and v != name})[:4],
        "kind": f"shop={tags['shop']}" if tags.get("shop") else f"craft={tags.get('craft')}",
        "clothes": tags.get("clothes"),
        "address": ", ".join(t for t in (street, town) if t) or None,
        "website": tags.get("website") or tags.get("contact:website"),
        "instagram": tags.get("contact:instagram"),
        "opening_hours": tags.get("opening_hours"),
        "last_checked": tags.get("check_date") or tags.get("survey:date"),
        "lat": round(float(lat), 6),
        "lon": round(float(lon), 6),
        "osm_url": f"https://www.openstreetmap.org/{element['type']}/{element['id']}",
    }


def distance_m(a: dict, b: dict) -> float:
    x = math.radians(b["lon"] - a["lon"]) * math.cos(math.radians((a["lat"] + b["lat"]) / 2))
    y = math.radians(b["lat"] - a["lat"])
    return 6371000 * math.hypot(x, y)


def search(words=None, near: str | None = None, radius_m: int = AROUND_M, limit: int = MAX_PLACES) -> dict:
    """Fashion shops on OpenStreetMap in Berlin whose name starts a word with one of `words`,
    or all fashion shops around `near`, or both."""
    words = clean_words(words)
    centre = None
    if near:
        centre = geocode(near)
        if not centre:
            return {"error": f"could not find {near!r} in Berlin on the map"}
    if not words and not centre:
        return {"error": "give words that may be in a shop's name, or a place in Berlin to search around"}
    scope = (f"(around:{int(radius_m)},{centre['lat']},{centre['lon']})" if centre
             else "({},{},{},{})".format(*BERLIN))
    name = '["name"~"(^|[^A-Za-z])({})",i]'.format("|".join(words)) if words else ""
    query = ("[out:json][timeout:25];("
             f'nwr["shop"~"^({"|".join(SHOPS)})$"]{name}{scope};'
             f'nwr["craft"~"^({"|".join(CRAFTS)})$"]{name}{scope};'
             ");out center 150;")
    places = [p for p in map(place, _overpass(query)) if p]
    if centre:
        places.sort(key=lambda p: distance_m(centre, p))
    else:
        places.sort(key=lambda p: p["name"].casefold())
    out = {"places": places[:limit], "found": len(places)}
    if centre:
        out["around"] = centre["label"]
    return out


# ---- Nominatim -------------------------------------------------------------------

def nominatim_url() -> str:
    return os.environ.get("NOMINATIM_URL", "").strip() or NOMINATIM


def geocode(text: str) -> dict | None:
    """Coordinates for a street, square or address in Berlin. None when Nominatim knows no such place."""
    text = re.sub(r"\s+", " ", str(text or "")).strip()[:200]
    if not text:
        return None
    params = {"q": text if "berlin" in text.lower() else f"{text}, Berlin", "format": "jsonv2", "limit": 1,
              "countrycodes": "de", "bounded": 1,
              "viewbox": "{1},{2},{3},{0}".format(*BERLIN)}          # west, north, east, south
    url = nominatim_url() + "?" + urllib.parse.urlencode(params)

    def fetch():
        global _last_nominatim
        wait = _last_nominatim + 1.0 - clock()
        if wait > 0:
            sleep(wait)
        try:
            status, body = transport("GET", url, None, 20)
        except OSError as e:
            raise MapError(f"Nominatim did not answer: {e}") from None
        finally:
            _last_nominatim = clock()
        if status != 200:
            raise MapError(f"Nominatim answered {status}")
        try:
            hits = json.loads(body)
        except json.JSONDecodeError:
            raise MapError("Nominatim's answer was not JSON") from None
        if not hits:
            return None
        hit = hits[0]
        osm_url = (f"https://www.openstreetmap.org/{hit['osm_type']}/{hit['osm_id']}"
                   if hit.get("osm_type") and hit.get("osm_id") else None)
        return {"lat": round(float(hit["lat"]), 6), "lon": round(float(hit["lon"]), 6),
                "label": hit.get("display_name") or text, "osm_url": osm_url}
    return _cached("nominatim\n" + url, 30 * DAY, fetch)
