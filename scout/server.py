"""Scout — the review screen, served on this machine only.

  python3 scout/server.py [--port 8770]

Every run spends credits, so the server listens on 127.0.0.1, answers only to
its own page, and runs one search at a time.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).parent
WEB = HERE / "web"
sys.path.insert(0, str(HERE))

import agent  # noqa: E402
import clients  # noqa: E402
import google_places  # noqa: E402
import listing  # noqa: E402
import store  # noqa: E402

TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
         ".woff2": "font/woff2", ".svg": "image/svg+xml"}
FONTS = {"Spectral": [("Spectral-Regular.woff2", 400, "normal"), ("Spectral-Medium.woff2", 500, "normal"),
                      ("Spectral-Italic.woff2", 400, "italic")],
         "Karla": [("Karla-Variable.woff2", "400 700", "normal")]}
TILES = "https://tile.openstreetmap.org"   # map tiles, credited under the map
# Run records are written by a model that read the open web. The page escapes them; this is the second lock.
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; font-src 'self'; "
       f"img-src 'self' {TILES}; "
       "connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
REPLAY_STEP = 0.45          # seconds between steps when a recorded run is replayed
running = threading.Lock()  # one live run at a time


class Gone(Exception):
    """The page was closed while Scout was working."""


def friendly(e: Exception) -> str:
    if isinstance(e, clients.MissingKey):
        return str(e)
    if isinstance(e, clients.ApiError):
        why = {401: "the key was not accepted", 403: "the key was not accepted",
               404: "the model or endpoint was not found; run `python3 scout/cli.py check`",
               429: "rate limit reached; wait a minute",
               432: "the Tavily plan limit is reached", 433: "the Tavily pay-as-you-go limit is reached"}
        return f"{e.service.capitalize()} answered {e.status}: {why.get(e.status, e.body[:160])}"
    if isinstance(e, urllib.error.URLError):
        return f"No connection: {e.reason}"
    return str(e)


def status() -> dict:
    return {"nebius_key": bool(os.environ.get("NEBIUS_API_KEY")),
            "tavily_key": bool(os.environ.get("TAVILY_API_KEY")),
            "bot_contact": bool(os.environ.get("CMX_BOT_CONTACT")),
            "google_key": bool(google_places.key()), "google": google_places.enabled(),
            "model": clients.nebius_model(), "runs": store.list_runs()}


def fonts_css() -> str:
    """Only the faces whose files are in web/fonts. The screen never loads a font from a third party."""
    rules = []
    for family, faces in FONTS.items():
        for name, weight, style in faces:
            if (WEB / "fonts" / name).exists():
                rules.append(f'@font-face{{font-family:"{family}";src:url("/fonts/{name}") format("woff2");'
                             f"font-weight:{weight};font-style:{style};font-display:swap}}")
    return "\n".join(rules) + "\n"


class Handler(BaseHTTPRequestHandler):
    server_version = "Scout/0.1"

    def log_message(self, fmt, *args):   # the terminal shows the agent's steps, not every request
        pass

    # ---- answers ----------------------------------------------------------------

    def send(self, code: int, body: bytes, kind: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if kind.startswith("text/html"):
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def json(self, data, code: int = 200) -> None:
        self.send(code, json.dumps(data, ensure_ascii=False).encode(), TYPES[".json"])

    def open_stream(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def emit(self, kind: str, data) -> None:
        try:
            self.wfile.write(f"event: {kind}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode())
            self.wfile.flush()
        except OSError:
            raise Gone() from None

    # ---- who is asking ------------------------------------------------------------

    def own_page(self) -> bool:
        """Refuse requests that another website makes the browser send to this machine."""
        port = self.server.server_address[1]
        own = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if self.headers.get("Host") not in own:
            return False
        origin = self.headers.get("Origin")
        return origin is None or origin in {f"http://{h}" for h in own}

    def body(self) -> dict:
        if (self.headers.get("Content-Type") or "").split(";")[0].strip() != "application/json":
            raise ValueError("send JSON")
        length = int(self.headers.get("Content-Length") or 0)
        if not 0 < length <= 20000:
            raise ValueError("the request is empty or too long")
        data = json.loads(self.rfile.read(length))
        if not isinstance(data, dict):
            raise ValueError("send a JSON object")
        return data

    # ---- routes -------------------------------------------------------------------

    def do_GET(self):
        if not self.own_page():
            return self.json({"error": "not allowed"}, 403)
        url = urlsplit(self.path)
        if url.path == "/api/status":
            return self.json(status())
        if url.path == "/api/replay":
            return self.replay(parse_qs(url.query).get("run", ["sample"])[0])
        if url.path == "/fonts.css":
            return self.send(200, fonts_css().encode(), TYPES[".css"])
        return self.static(url.path)

    def do_POST(self):
        if not self.own_page():
            return self.json({"error": "not allowed"}, 403)
        try:
            data = self.body()
        except (ValueError, json.JSONDecodeError) as e:
            return self.json({"error": str(e)}, 400)
        route = {"/api/find": self.find, "/api/decision": self.decision,
                 "/api/listing": self.listing}.get(urlsplit(self.path).path)
        if not route:
            return self.json({"error": "not found"}, 404)
        return route(data)

    def static(self, path: str) -> None:
        name = "index.html" if path in ("", "/") else path.lstrip("/")
        file = (WEB / name).resolve()
        if WEB.resolve() not in file.parents or not file.is_file() or file.suffix not in TYPES:
            return self.json({"error": "not found"}, 404)
        self.send(200, file.read_bytes(), TYPES[file.suffix])

    def replay(self, run_id: str) -> None:
        try:
            run = store.load(run_id)
        except (ValueError, OSError, json.JSONDecodeError):
            return self.json({"error": "no such run"}, 404)
        events = run.pop("events", [])
        self.open_stream()
        try:
            self.emit("start", {"id": run["id"], "brief": run.get("brief") or "", "replay": True,
                                "sample": bool(run.get("sample"))})
            for event in events:
                time.sleep(REPLAY_STEP)
                self.emit("step", event)
            self.emit("done", run)
        except Gone:
            pass

    def find(self, data: dict) -> None:
        brief = str(data.get("brief") or "").strip()[:300]
        try:
            seeds_n = max(0, min(12, int(data.get("seeds") or 0)))
        except (TypeError, ValueError):
            seeds_n = 0
        if not brief and not seeds_n:
            return self.json({"error": "Write a brief first."}, 400)
        try:
            seeds = json.loads(store.private_file("seeds.json").read_text())["seeds"][:seeds_n] if seeds_n else []
        except store.MissingData as e:
            return self.json({"error": str(e)}, 400)
        if not running.acquire(blocking=False):
            return self.json({"error": "Scout is already working on a brief. Wait for it to finish."}, 409)
        try:
            run_id = store.new_id("find")
            for k in clients.usage:
                clients.usage[k] = 0
            self.open_stream()
            self.emit("start", {"id": run_id, "brief": brief, "replay": False, "sample": False})
            print(f"\n{run_id}  {brief!r}")
            log = store.Recorder(run_id, then=lambda event: self.emit("step", event))
            try:
                out = agent.research(seeds, brief=brief or None, log=log)
            except Gone:
                print("  the page was closed; stopped")
                return
            except (clients.MissingKey, clients.ApiError, urllib.error.URLError, RuntimeError) as e:
                print(f"  stopped: {e}")
                return self.emit("failed", {"message": friendly(e), "usage": dict(clients.usage)})
            run = {"brief": brief, "model": clients.nebius_model(), "checked_at": store.now(),
                   "usage": dict(clients.usage), **out}
            store.save(run_id, run)
            print(f"  {len(out['shops'])} shops. {clients.cost_line()}")
            self.emit("done", dict(run, id=run_id, decisions={}))
        except Gone:
            pass
        finally:
            running.release()

    def decision(self, data: dict) -> None:
        try:
            run_id, shop = str(data["run"]), str(data["shop"])
            store.load(run_id)                                  # the run has to exist
            entry = store.decide(run_id, shop, str(data["decision"]), str(data.get("note") or ""))
        except (KeyError, ValueError, OSError):
            return self.json({"error": "that decision could not be recorded"}, 400)
        self.json(entry)

    def listing(self, data: dict) -> None:
        try:
            run = store.load(str(data["run"]))
            record = next(s for s in run["shops"] if s["name"] == str(data["shop"]))
        except (KeyError, ValueError, OSError, StopIteration):
            return self.json({"error": "no such shop in that run"}, 404)
        if run.get("sample"):
            if record.get("listing"):
                return self.json(record["listing"])
            return self.json({"error": "The sample run has a draft listing for one shop only."}, 404)
        try:
            self.json(listing.draft(record))
        except listing.NoFeed as e:
            self.json({"error": str(e).capitalize() + "."}, 409)
        except (clients.ApiError, clients.MissingKey, urllib.error.URLError, ValueError, OSError) as e:
            self.json({"error": friendly(e)}, 502)


def serve(port: int = 8770) -> ThreadingHTTPServer:
    clients.load_env()
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8770)
    httpd = serve(ap.parse_args().port)
    s = status()
    print(f"Scout is at http://127.0.0.1:{httpd.server_address[1]}")
    print(f"Nebius key: {'set' if s['nebius_key'] else 'missing'} · Tavily key: "
          f"{'set' if s['tavily_key'] else 'missing'} · model: {s['model']}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
