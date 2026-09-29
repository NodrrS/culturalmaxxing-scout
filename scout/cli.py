"""Scout — command line.

  python3 scout/cli.py check                      are the keys and the maps working? (6 small calls)
  python3 scout/cli.py find "BRIEF" [--seeds N]   research a brief, and N seeds from data/seeds.json
  python3 scout/cli.py verify [--limit N]         re-check the shops a person already judged, and score
  python3 scout/cli.py probe                      can Tavily see the registered shops' product pages?
  python3 scout/server.py                         the review screen, at http://127.0.0.1:8770

Output goes to scout/runs/YYYY-MM-DD/. Nothing is published and nobody is contacted.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import clients  # noqa: E402
import store  # noqa: E402


def print_step(event: dict) -> None:
    step = event["step"]
    if step == "baseline":
        print(f"  plain    {event['query']!r}  ->  {len(event['results'])} results, for comparison")
    elif step == "map":
        where = f" around {event['near']}" if event.get("near") else ""
        print(f"  map      {', '.join(event['words']) or 'all fashion shops'}{where}  ->  {event['found']} places")
    elif step == "map_failed":
        print(f"  map      failed: {event['reason']}")
    elif step == "google":
        print(f"  google   {event['query']!r}  ->  {event['found']} places on Google Maps")
    elif step == "google_failed":
        print(f"  google   failed: {event['reason']}")
    elif step == "search":
        print(f"  search   {event['query']!r}  ->  {len(event['results'])} results")
    elif step == "read":
        print(f"  read     {event['url']}  ({event['via']}, {event['chars']} chars)")
    elif step == "blocked":
        print(f"  blocked  {event['url']}  (robots.txt)")
    elif step == "read_failed":
        print(f"  failed   {event['url']}")
    elif step == "platform":
        print(f"  feed     {event['website']}  ->  {event['platform']}")
    elif step == "submit_rejected":
        print(f"  redo     records did not match the schema ({len(event['problems'])} problems)")
    elif step == "submit":
        print(f"  submit   {event['shops']} shops")
    elif step == "located":
        print(f"  located  {event['shops']} of {event['total']}: {event['via_map']} from OpenStreetMap, "
              f"{event.get('via_google', 0)} as Google Maps links")


def save(run_id: str, data: dict) -> None:
    print(f"wrote {store.save(run_id, data).relative_to(HERE.parent)}")


def summary(shops: list[dict]) -> None:
    for s in shops:
        flag = "  !" + "; ".join(s["flags"]) if s.get("flags") else ""
        print(f"  {s['verdict']:8} {s['name']}: {s['verdict_reason'][:110]}{flag}")


# ---- check ---------------------------------------------------------------------

def check_nebius() -> bool:
    import agent
    found: dict[str, list[str]] = {}
    for base in dict.fromkeys([clients.nebius_base(), clients.DEFAULT_BASE, clients.US_BASE]):
        try:
            found[base] = clients.list_models(base)
        except clients.ApiError as e:
            print(f"   {base}  answered {e.status}")
    if not found:
        print("   ! no endpoint accepted the key")
        return False
    for base, models in found.items():
        nvidia = [m for m in models if "nemotron" in m.lower()]
        print(f"   {base}  {len(models)} models, Nemotron: {', '.join(nvidia) or 'none'}")
    model, base = clients.nebius_model(), clients.nebius_base()
    if model not in found.get(base, []):
        print(f"   ! {model} is not served at {base}")
        for other, models in found.items():
            hits = [m for m in models if "nemotron" in m.lower()]
            if hits:
                print(f"     set in scout/.env:  NEBIUS_BASE_URL={other}  NEBIUS_MODEL={hits[0]}")
                break
        return False
    say = [agent.tool("say", "Say one word.", agent.obj({"word": {"type": "string"}}))]
    msg = clients.chat([{"role": "user", "content": "Call the tool say with the word hallo."}],
                       tools=say, max_tokens=500)["choices"][0]["message"]
    calls = bool(msg.get("tool_calls"))
    print(f"   tool calling: {'works' if calls else '! no tool call came back'}")
    schema = agent.obj({"city": {"type": "string", "enum": ["Berlin", "Bochum"]}})
    try:
        got = clients.structured(system="You answer questions.", prompt="In which city is Alexanderplatz?",
                                 schema=schema, max_tokens=500)
        print(f"   JSON schema:  works ({got})")
    except ValueError as e:
        print(f"   JSON schema:  ! failed ({e})")
        return False
    return calls


def check_tavily() -> bool:
    data = clients.search("Abaya Berlin Neukölln", max_results=3, exclude_domains=clients.MARKETPLACES)
    for r in data.get("results", []):
        print(f"   {(r.get('title') or '')[:60]}  {r['url']}")
    if not data.get("results"):
        print("   ! the search came back empty")
    return bool(data.get("results"))


def check_osm() -> bool:
    import osm
    started = time.monotonic()
    found = osm.search(["afro", "abaya", "kimono"])
    print(f"   Overpass: {found['found']} fashion places matching afro, abaya or kimono "
          f"({time.monotonic() - started:.0f} s; answers are cached for a day)")
    spot = osm.geocode("Alexanderplatz")
    print(f"   Nominatim: Alexanderplatz is at {spot['lat']}, {spot['lon']}" if spot else "   ! Nominatim found nothing")
    return bool(found["found"]) and bool(spot)


def check_google() -> bool:
    import google_places
    if not google_places.key():
        print(f"   not set; Scout works without it. A Maps Demo Key needs no credit card: {google_places.DEMO_KEY}")
        return True
    found = google_places.search("Abaya Neukölln")
    print(f"   Text Search: {found['found']} places for 'Abaya Neukölln'")
    if not google_places.zero_retention():
        print("   ! Google results stay away from Nemotron until Zero Data Retention is on in Nebius Token Factory"
              " (account profile page) and NEBIUS_ZERO_DATA_RETENTION=on is in scout/.env")
        return False
    return True


def cmd_check(args) -> int:
    import google_places
    import osm
    ok = True
    for title, part in (("1. Nebius Token Factory", check_nebius), ("2. Tavily", check_tavily),
                        ("3. OpenStreetMap (no key needed)", check_osm),
                        ("4. Google Maps (optional, demo key)", check_google)):
        print(title)
        try:
            ok = part() and ok
        except (clients.MissingKey, clients.ApiError, osm.MapError, google_places.GoogleError) as e:
            print(f"   ! {e}")
            ok = False
        except urllib.error.URLError as e:
            print(f"   ! no connection: {e.reason}")
            ok = False
    print(clients.cost_line())
    print("Ready." if ok else "Not ready yet, see the lines marked with !")
    return 0 if ok else 1


# ---- find ----------------------------------------------------------------------

def cmd_find(args) -> int:
    import agent
    seeds = json.loads(store.private_file("seeds.json").read_text())["seeds"][:args.seeds] if args.seeds else []
    run_id = store.new_id("find")
    out = agent.research(seeds, brief=args.brief, extra=args.extra, log=store.Recorder(run_id, then=print_step))
    save(run_id, {"brief": args.brief, "model": clients.nebius_model(), "checked_at": store.now(),
                  "usage": dict(clients.usage), **out})
    summary(out["shops"])
    if out.get("baseline"):
        found = [s for s in out["shops"] if s["verdict"] != "reject"]
        missed = sum(1 for s in found if s["visibility"]["plain_search_rank"] is None)
        print(f"{missed} of {len(found)} don't show up in a plain web search for {out['baseline']['query']!r}.")
    print(clients.cost_line())
    return 0


# ---- verify --------------------------------------------------------------------

def truth() -> list[dict]:
    """The shops a person judged on 19 September: the registry, and the rejected candidates."""
    rows = [{"name": s["name"], "website": s["website"], "expected": "accept", "why": "registered"}
            for s in json.loads(store.private_file("shops.json").read_text())["shops"]]
    rows += [{"name": r["name"], "website": r["site"], "expected": "reject", "why": r["reason"]}
             for r in json.loads(store.private_file("discovery-manual.json").read_text())["rejected"]]
    return rows


def score(rows: list[dict], shops: list[dict]) -> dict:
    import agent
    by_host = {agent.host(s["website"]): s for s in shops if s.get("website")}
    by_name = {s["name"].strip().lower(): s for s in shops}
    table = []
    for row in rows:
        rec = by_host.get(agent.host(row["website"])) or by_name.get(row["name"].strip().lower())
        table.append({"name": row["name"], "expected": row["expected"], "human_reason": row["why"],
                      "scout": rec["verdict"] if rec else "missing",
                      "scout_reason": rec["verdict_reason"] if rec else ""})
    judged = [t for t in table if t["scout"] in ("accept", "reject")]
    return {
        "checked": len(table),
        "agree": sum(1 for t in judged if t["scout"] == t["expected"]),
        "disagree": sum(1 for t in judged if t["scout"] != t["expected"]),
        # "revisit" is not an error: it sends the shop to a person.
        "sent_to_a_person": sum(1 for t in table if t["scout"] == "revisit"),
        "missing": sum(1 for t in table if t["scout"] == "missing"),
        "table": table,
    }


def cmd_verify(args) -> int:
    import agent
    rows = truth()
    if args.limit:
        # Take from both ends so a short run still has shops to accept and to reject.
        half = max(1, args.limit // 2)
        rows = rows[:args.limit - half] + rows[-half:]
    run_id = store.new_id("verify")
    out = agent.research_in_batches([{"name": r["name"], "website": r["website"]} for r in rows],
                                    size=args.batch, log=store.Recorder(run_id, then=print_step))
    result = score(rows, out["shops"])
    save(run_id, {"brief": f"Re-check of {len(rows)} shops a person judged on 19 September",
                  "model": clients.nebius_model(), "checked_at": store.now(),
                  "usage": dict(clients.usage), "score": result, **out})
    for t in result["table"]:
        mark = "ok" if t["scout"] == t["expected"] else ("?" if t["scout"] == "revisit" else "X")
        print(f"  {mark:2} {t['name']:28} human: {t['expected']:7} scout: {t['scout']:8} {t['scout_reason'][:70]}")
    print(f"Agreed with the human on {result['agree']} of {result['checked']}; "
          f"disagreed on {result['disagree']}; sent {result['sent_to_a_person']} to a person; "
          f"{result['missing']} missing.")
    print(clients.cost_line())
    return 0


# ---- probe ---------------------------------------------------------------------

def cmd_probe(args) -> int:
    """For the concierge idea: a search limited to the shops' own sites, with no copy of any catalogue."""
    import agent
    shops = [s for s in json.loads(store.private_file("shops.json").read_text())["shops"] if s.get("crawl", True)]
    rows = []
    for s in shops:
        h = agent.host(s["website"])
        data = clients.search(args.query, include_domains=[h], max_results=5, country=None)
        urls = [r["url"] for r in data.get("results", [])]
        pages = [u for u in urls if any(p in u for p in ("/products/", "/produkt/", "/product/", "/p/"))]
        rows.append({"shop": s["slug"], "host": h, "results": len(urls), "product_pages": len(pages), "urls": urls})
        print(f"  {s['slug']:24} {len(urls)} results, {len(pages)} product pages")
    path = store.RUNS / f"{store.new_id('probe')}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"query": args.query, "rows": rows}, ensure_ascii=False, indent=2))
    print(f"wrote {path.relative_to(HERE.parent)}")
    seen = sum(1 for r in rows if r["results"])
    print(f"Tavily returned pages for {seen} of {len(rows)} shops.")
    print(clients.cost_line())
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    f = sub.add_parser("find")
    f.add_argument("brief")
    f.add_argument("--seeds", type=int, default=0, help="also check the first N seeds from data/seeds.json")
    f.add_argument("--extra", type=int, default=6, help="how many new shops to look for")
    v = sub.add_parser("verify")
    v.add_argument("--limit", type=int, default=0, help="check only N shops (default: all 29)")
    v.add_argument("--batch", type=int, default=4)
    p = sub.add_parser("probe")
    p.add_argument("--query", default="Kleid")
    args = ap.parse_args()

    clients.load_env()
    try:
        return {"check": cmd_check, "find": cmd_find, "verify": cmd_verify, "probe": cmd_probe}[args.cmd](args)
    except (clients.MissingKey, store.MissingData) as e:
        print(e)
    except clients.ApiError as e:
        hint = {401: "the key was not accepted", 403: "the key was not accepted",
                404: "model or endpoint not found; run `check`",
                429: "rate limit; wait a minute", 432: "Tavily plan limit reached",
                433: "Tavily pay-as-you-go limit reached"}.get(e.status, "")
        print(f"{e}\n{hint}".strip())
    except urllib.error.URLError as e:
        print(f"no connection: {e.reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
