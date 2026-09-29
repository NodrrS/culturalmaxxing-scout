"""What visitors tell Scout: reports about shops it showed, and tips about shops it missed.

This is the human part of the loop. A visitor says whether a shop exists and can
correct what Scout got wrong ("a Turkish perfume shop, not an Arab one"). Anyone
can send a tip about a shop Scout missed.

Rules:
- Reports and tips are what people say, not facts. The screen shows them as
  visitor notes; the model sees them as data to check, never as instructions.
- A report never removes a shop. When the latest report says a shop no longer
  exists, a confirmed shop goes back to "not yet confirmed" until someone confirms
  it again. When the latest report says a closed or moved shop is there, it comes
  back as "not yet confirmed" for Scout to check again.
- Reports change how a shop is shown, not the saved run: annotate() applies them
  each time results are shown, so they always reflect the latest reports.
- Nothing personal is stored: no account, no IP address, no browser details. The
  screen asks people not to put names or contact details in their notes.
- At most PER_SHOP_PER_DAY reports per shop a day, and TIPS_PER_DAY tips a day.

Files, never committed: scout/feedback/reports.jsonl and scout/feedback/tips.jsonl
"""
from __future__ import annotations

import datetime as dt
import json
import re
import threading
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).parent
DIR = HERE / "feedback"
NOTE_MAX = 300
PER_SHOP_PER_DAY = 5
TIPS_PER_DAY = 50
RECENT_TIPS = 5
TIP_DAYS = 60
STRONG = ("osm:", "google:")      # map entries are one branch; a website can be a whole chain
# On these sites a shop is one page, not the whole site.
PLATFORMS = {"instagram.com", "facebook.com", "tiktok.com", "linktr.ee", "etsy.com", "youtube.com",
             "pinterest.com", "wa.me", "t.me", "google.com", "openstreetmap.org"}

now = dt.datetime.now   # the offline tests replace this
_lock = threading.Lock()


class FeedbackError(ValueError):
    """The report or tip was not taken; the message says why."""


def clean(text, limit: int) -> str:
    """Plain text: no control characters, single spaces, at most `limit` characters."""
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", str(text or ""))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def site_key(url: str | None) -> str | None:
    if not url:
        return None
    parts = urlsplit(url if "://" in url else f"https://{url}")
    host = parts.netloc.lower().removeprefix("www.").removeprefix("m.")
    if not host:
        return None
    if host in PLATFORMS:
        first = parts.path.strip("/").split("/")[0].lower()
        return f"site:{host}/{first}" if first else None
    return f"site:{host}"


def keys(shop: dict) -> list[str]:
    """Ways to recognise the same shop in another search: map entries, website, name."""
    from agent import name_words   # imported here because agent imports this module
    out = []
    location = shop.get("location") or {}
    if location.get("osm_url"):
        out.append("osm:" + location["osm_url"])
    if location.get("place_id"):
        out.append("google:" + location["place_id"])
    site = site_key(shop.get("website"))
    if site:
        out.append(site)
    words = sorted(name_words(shop.get("name")))
    if words:
        out.append("name:" + " ".join(words))
    return out


def matches(a: list[str], b: list[str]) -> bool:
    strong_a, strong_b = {k for k in a if k.startswith(STRONG)}, {k for k in b if k.startswith(STRONG)}
    if strong_a and strong_b:
        return bool(strong_a & strong_b)
    return bool(set(a) & set(b))


def _file(kind: str) -> Path:
    return DIR / f"{kind}.jsonl"


def load(kind: str = "reports") -> list[dict]:
    path = _file(kind)
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def _append(kind: str, entry: dict) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    with _file(kind).open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def summary(shop: dict, reports: list[dict] | None = None) -> dict | None:
    """What visitors have said about this shop, newest last. None if nothing."""
    shop_keys = keys(shop)
    found = sorted((r for r in (load() if reports is None else reports) if matches(shop_keys, r["keys"])),
                   key=lambda r: r["at"])
    if not found:
        return None
    latest = found[-1]
    return {
        "exists": sum(1 for r in found if r["exists"]),
        "gone": sum(1 for r in found if not r["exists"]),
        "latest": {"exists": latest["exists"], "at": latest["at"][:10]},
        "notes": [{"text": r["note"], "exists": r["exists"], "at": r["at"][:10]}
                  for r in reversed(found) if r["note"]][:3],
    }


def for_model(found: dict | None) -> dict | None:
    """The same, in the words the model gets."""
    if not found:
        return None
    return {"say_it_exists": found["exists"], "say_it_is_gone": found["gone"],
            "latest": f"{'exists' if found['latest']['exists'] else 'gone'} ({found['latest']['at']})",
            "notes": [n["text"] for n in found["notes"]]}


def report(shop: dict, exists: bool, note: str = "", run: str | None = None) -> dict:
    """Keep one visitor report about a shop Scout showed. Returns the shop as it is now shown."""
    if not isinstance(exists, bool):
        raise FeedbackError("say whether the shop exists")
    shop_keys = keys(shop)
    if not shop_keys:
        raise FeedbackError("this shop cannot be recognised again")
    with _lock:
        today = now().date().isoformat()
        todays = [r for r in load() if r["at"].startswith(today) and matches(shop_keys, r["keys"])]
        if len(todays) >= PER_SHOP_PER_DAY:
            raise FeedbackError("this shop has had enough reports today; try again tomorrow")
        _append("reports", {"at": now().isoformat(timespec="seconds"), "run": run,
                            "shop": clean(shop.get("name"), 120), "keys": shop_keys,
                            "exists": exists, "note": clean(note, NOTE_MAX)})
    return annotate([shop])[0]


def annotate(shops: list[dict]) -> list[dict]:
    """Shops as they are shown now: with visitor reports, and the latest report taken into account.

    Pass the shops as they were saved, not shops annotated before."""
    reports = load()
    out = []
    for shop in shops:
        shop = {k: v for k, v in shop.items() if k not in ("reported_gone", "reported_there")}
        found = summary(shop, reports)
        shop["visitor_reports"] = found
        if found and not found["latest"]["exists"] and shop.get("verdict") == "accept":
            shop["verdict"], shop["reported_gone"] = "revisit", found["latest"]["at"]
        elif found and found["latest"]["exists"] and shop.get("verdict") == "reject" \
                and shop.get("status") in ("closed", "moved"):
            shop["verdict"], shop["reported_there"] = "revisit", found["latest"]["at"]
        out.append(shop)
    return out


def tip(name, where="", what="", link="") -> dict:
    """Keep one tip about a shop Scout missed."""
    name, where, what, link = clean(name, 80), clean(where, 80), clean(what, 200), clean(link, 300)
    if len(name) < 2:
        raise FeedbackError("give the shop's name")
    if link and not re.match(r"^https?://[^\s/]+\.[^\s/]+", link, flags=re.I):
        raise FeedbackError("a link has to start with http:// or https://")
    with _lock:
        today = now().date().isoformat()
        if sum(1 for t in load("tips") if t["at"].startswith(today)) >= TIPS_PER_DAY:
            raise FeedbackError("there have been enough tips today; try again tomorrow")
        entry = {"at": now().isoformat(timespec="seconds"), "name": name, "where": where, "what": what,
                 "link": link or None}
        _append("tips", entry)
    return entry


def recent_tips(limit: int = RECENT_TIPS, days: int = TIP_DAYS) -> list[dict]:
    cutoff = (now() - dt.timedelta(days=days)).isoformat(timespec="seconds")
    return [t for t in reversed(load("tips")) if t["at"] >= cutoff][:limit]
