# Scout — Live Integration, Quality & Hackathon Demo — Implementation Tasks

## Overview

Bring **Culturalmaxxing Scout** from “26 offline tests pass, never run live” to a **demonstrable hackathon submission**: Nemotron on **Nebius Token Factory** and **Tavily** working end-to-end, human-in-the-loop review on the local screen, measurable agreement with hand-judged ground truth, and a public demo URL plus short video. Nothing is published and nobody is contacted; output stays in `scout/runs/` until a person approves.

> **Scope update, 29 September 2026 (project owner).** The hackathon app helps **people find fashion shops in Berlin that platforms like Google miss**. It becomes a Culturalmaxxing feature **after** the hackathon; that integration is out of scope now. What this changes in this plan:
>
> - **In scope:** search for shoppers, **OpenStreetMap integration (new Phase 2b)**, the map on the screen, the plain-search comparison, Phases 0–3 and 6–9.
> - **After the hackathon (Culturalmaxxing feature):** draft listings (Phase 4), the product-search probe (Phase 5), shop approval and the concierge (Phase 10.1–10.2). The code stays; the screen no longer shows the curator buttons (decisions, draft listing). Their endpoints remain in `scout/server.py`.
> - **Verify** keeps Culturalmaxxing's test of a shop (cultural fashion in Berlin), so its score stays comparable with the hand-judged ground truth. `find` with a request uses the person's request as the test.
> - **Demo policy, to decide:** a live search shows real shops from public sources (OpenStreetMap, their own pages), as any map does. The rule "only invented or consented shops" (Phase 7.3) was written for listings; decide whether it also applies to search results in the video. Private data from `data/` stays out either way.

**Motivation (why this plan exists):**

- Hackathon deadline **30 October 2026, 10:00 Pacific** — submission needs a working demo on Nebius + an NVIDIA open model + Tavily usage story
- README states Scout has **not yet run against live services** — model endpoint quirks, tool calling, and JSON-schema shapes may differ from mocks
- Quality is judged against **private ground truth** (`shops.json`, `discovery-manual.json`) — unavailable in the public repo; verify score is the main tuning loop
- Demo and video must use **invented shops** (`sample-run.json`) or shops that **agreed** to be shown — never leak private registry data

**Current state (audit summary):**

| Area | Status |
| --- | --- |
| Agent loop (4 tools, budgets, source tracing) | **Done** — `scout/agent.py` |
| Schema / closed vocabulary enforcement | **Done** — `scout/clients.py`, `engine/taxonomy.py` |
| Polite fetch + robots.txt + Tavily Extract fallback | **Done** — `engine/fetch.py`, wired in agent |
| Draft listing (feed → rules → Nemotron) | **Done** — `scout/listing.py`, `engine/agent2_extraction.py`, `engine/agent3_taxonomy.py` |
| CLI (`check`, `find`, `verify`, `probe`) | **Done** — `scout/cli.py` |
| Search screen for shoppers (EN/DE, SSE, OpenStreetMap map) | **Done** — `scout/server.py`, `scout/web/`; decision and listing endpoints kept for the later Culturalmaxxing feature |
| OpenStreetMap search and places | **Done, tested live** — `scout/osm.py`, `map_search` tool; see Phase 2b |
| Plain-search comparison | **Done** — each request also runs as a plain Tavily search; screen shows which shops it misses |
| File-backed runs & decisions | **Done** — `scout/store.py` |
| Offline test suite (37 tests) | **Done** — `scout/test_offline.py`, including OpenStreetMap stand-ins |
| Live Nebius / Tavily integration | **Not done** — first step: `python3 scout/cli.py check` |
| Verify score vs human (29 shops) | **Not done** — needs keys + private `data/` |
| Prompt / budget tuning from misses | **Not done** |
| Product search probe (`probe`) | **Not done** — needs keys + `shops.json` |
| Local fonts (Spectral, Karla) | **Not done** — falls back to Georgia / Helvetica |
| Public demo URL | **Not done** |
| YouTube video (< 3 min) | **Not done** |
| CI running `test_offline.py` on push | **Not verified** — add workflow if missing |
| FastAPI backend (`backend/`) | **Scaffold present** — [backend/](./backend/); review HTTP still in `scout/server.py`; **migrate all backend concerns into `backend/`** |

**Target state:**

- `python3 scout/cli.py check` exits **0** with tool calling + JSON schema + Tavily search on real keys
- At least one **live** `find` brief saved under `scout/runs/` and reviewable in the UI
- A person types a request on the screen and gets checked shops on an OpenStreetMap map, with the ones a plain web search misses marked
- **Verify** run documented: e.g. “agreed with a person on X of 29” (plus revisit/missing breakdown)
- Misses analyzed; prompt and/or budgets adjusted; re-run verify until score is acceptable for demo narrative
- **`probe`** answers whether Tavily can see product pages on registered shops’ domains without copying catalogues
- Review screen polished (fonts optional but preferred), **`#sample`** replay works without keys for judges
- **Demo URL** serves sample replay or a recorded run; **video** shows only invented or consented shops
- Root README **Status** and hackathon checklist updated to match reality

**Reference docs:** [README.md](./README.md), [data/README.md](./data/README.md), [engine/README.md](./engine/README.md), [backend/README.md](./backend/README.md)

**Canonical backend home:** [backend/](./backend/) — FastAPI app, Docker, rate limits, logging, and (over time) the HTTP surface that today lives in `scout/server.py`. **`scout/`** keeps the agent, CLI, engine imports, runs on disk, and offline tests until routers in `backend/` call into it.

**Two HTTP surfaces (temporary split):**

| Role | Location today | Target |
| --- | --- | --- |
| **Review screen** (hackathon demo, human-in-the-loop) | Stdlib SSE — `scout/server.py`, static `scout/web/` | **Migrate** routes + static mount into `backend/`; thin wrapper or deprecation of `scout/server.py` |
| **Public / product REST API** (map, third parties, deploy) | FastAPI scaffold — `backend/main.py`, routers under `backend/src/` | Extend in place; do not start a second backend folder |

Hackathon Phases **0–7** may still run `python3 scout/server.py` for speed. Any new HTTP, hosting, or API work goes under **`backend/`** only. Phase 10 completes migration (review SSE, static `scout/web/`, deploy env, Docker) while `scout/` + `engine/` remain the domain logic layer.

**Related code — Scout (agent + review):**

| Layer | Primary files |
| --- | --- |
| Discovery agent | `scout/agent.py` |
| OpenStreetMap (Overpass, Nominatim) | `scout/osm.py` |
| Google Maps (optional, demo key) | `scout/google_places.py` |
| Nebius + Tavily + schema | `scout/clients.py` |
| Draft listings | `scout/listing.py` |
| Persistence | `scout/store.py` |
| Local HTTP + SSE API | `scout/server.py` |
| Review UI | `scout/web/index.html`, `scout/web/app.js`, `scout/web/app.css` |
| CLI | `scout/cli.py` |
| Engine (fetch, taxonomy, feeds) | `engine/fetch.py`, `engine/taxonomy.py`, `engine/agent2_extraction.py`, `engine/agent3_taxonomy.py`, `engine/links.py` |
| Offline tests | `scout/test_offline.py` |
| Demo data | `scout/web/sample-run.json` |
| Env template | `scout/.env.example` |

**Related code — Backend (`backend/`):**

| Module (under `backend/`) | Role for Scout |
| --- | --- |
| `main.py`, `config_loader`, `config_file.json` | App shell, port/workers, per-route rate limits (expensive `find` / LLM proxy) |
| `src/api_endpoints/routers/.../example_router.py` | Pattern for runs, decisions, listings, review SSE |
| `src/models/models_example.py` | Pydantic request/response models mirroring run JSON shapes |
| `src/utils/secure_file_io.py` | Safer reads/writes under `scout/runs/` (path confinement, atomic JSON) — replace or wrap `store.py` I/O from backend services |
| `src/utils/custom_logger.py`, `limiter.py`, `request_limiter.py` | Production logging + 429 handling vs ad hoc prints in `scout/server.py` |
| `DOCKERFILE`, `docker-compose.yml`, optional Redis | Hosted demo and production; static `scout/web/` served from backend when migrated |
| `.env.example` (RSA keys) | Backend deploy env; merge `NEBIUS_*`, `TAVILY_*`, `CMX_BOT_CONTACT` from `scout/.env.example` into `backend/.env` for hosted runs — never commit |

---

## Phase 0: Environment, secrets & private data

Run once per machine / teammate. Never commit secrets or private shop files.

### 0.1 Local env

- [ ] Copy `scout/.env.example` → `scout/.env`
- [ ] Set `NEBIUS_API_KEY` (Nebius Token Factory)
- [ ] Set `TAVILY_API_KEY`
- [ ] Set `CMX_BOT_CONTACT` to a **project** address (shown in User-Agent / bot identity to sites Scout reads)
- [ ] Confirm `scout/.env`, `scout/runs/`, and `data/*` (except `data/README.md`) stay out of git — do not `git add -f` them

### 0.2 Private data (project owner)

- [ ] Obtain `data/shops.json`, `data/discovery-manual.json`, `data/seeds.json` via private channel (see [data/README.md](./data/README.md))
- [ ] Or set `SCOUT_DATA` in `scout/.env` to a folder outside the repo that holds the three files
- [ ] Sanity-check JSON shapes against examples in `data/README.md`

### 0.3 Python

**Scout core (`scout/`, `engine/`):**

- [ ] Use Python **3.14** (or project-tested version); **no pip install** required for CLI, agent, review server, offline tests
- [ ] From repo root: `python3 scout/test_offline.py` — all green before any live spend

**Backend (`backend/`) — venv when running or extending the FastAPI app:**

- [ ] Python **3.12+** per [backend/README.md](./backend/README.md)
- [ ] `cd backend && python -m venv venv` → `pip install -r requirements.txt`
- [ ] Copy `backend/.env.example` → `backend/.env`; generate RSA keys via `backend/src/utils/keys_generator.py` if using encryption helpers; add Scout keys when wiring live routes
- [ ] Smoke: `cd backend && python main.py` → `GET /` returns `"status": "ok"`; optional `GET /docs`
- [ ] Do not add new HTTP servers outside `backend/`; hackathon Phases 0–7 still use `scout/server.py` until those routes are migrated

---

## Phase 1: Live API integration (`check`)

Validate Nebius Nemotron and Tavily before spending credits on full agent runs.

### 1.1 Run check

- [ ] `python3 scout/cli.py check`
- [ ] Record which `NEBIUS_BASE_URL` and `NEBIUS_MODEL` the output recommends if defaults fail
- [ ] Apply recommended lines to `scout/.env` and re-run until **Ready.**

### 1.2 Fix integration gaps (if check fails)

| Symptom | Likely fix |
| --- | --- |
| Model not at default base | Set `NEBIUS_BASE_URL` / `NEBIUS_MODEL` per `check` output |
| Tool calling missing | Adjust `clients.chat` tool payload for Nemotron on Token Factory |
| JSON schema call fails | Adjust `clients.structured` / repair path in `engine/llm.py` consumers |
| Tavily empty / 432 / 433 | Query wording, plan limits, or billing |

- [ ] Document any env vars added beyond `.env.example` (comment-only in example if stable)
- [ ] Log approximate cost line from `clients.cost_line()` for one check run

### 1.3 Smoke: minimal agent run

- [ ] `python3 scout/cli.py find "Abaya Atelier Neukölln"` with small `--extra` (default 6) or shorter brief
- [ ] Confirm `scout/runs/YYYY-MM-DD/*.json` written with `shops`, `usage`, step log
- [ ] Open `python3 scout/server.py` → replay that run from the dropdown or fix errors from live path

### 1.4 Tests

- [ ] Re-run `python3 scout/test_offline.py` — no regressions after client changes
- [ ] If live-only behavior added, keep it behind env or integration marker; do not break offline mocks

---

## Phase 2: Discovery quality (`find` + seeds)

Improve “find cultural shops in Berlin” beyond a one-off smoke test.

### 2.1 Brief library (internal)

- [ ] Define 3–5 German briefs (e.g. bridal South Asian, modest fashion, kimono, Turkish festliche Mode)
- [ ] Optional: one brief per community language angle (document which language queries Nemotron actually uses)
- [ ] Run `find` for each; note marketplace leakage, false accepts, missing Impressum reads

### 2.2 Seeds path

- [ ] With `data/seeds.json`: `python3 scout/cli.py find "…" --seeds N` for small N
- [ ] Confirm seeds merge with brief in agent input (`scout/cli.py` → `agent.research`)

### 2.3 Enforcement review (no prompt change unless needed)

Verify live runs still respect code-enforced rules (README):

- [ ] robots.txt blocks → `crawl: false`, no Tavily Extract bypass
- [ ] Untraceable sources → verdict becomes **revisit**, not silent accept
- [ ] Budget exhaustion → forced submit, no infinite loop

### 2.4 UI path

- [ ] POST `/api/find` from review screen with same brief as CLI
- [ ] Confirm SSE steps match CLI `print_step` semantics
- [ ] Record human **decision** via `/api/decision`; confirm persisted in run file via `store.decide`

---

## Phase 2b: OpenStreetMap

Find shops that have no website, and put every shop you can visit on a map. No key needed.

### 2b.1 Map search (done)

- [x] `scout/osm.py`: Overpass search by a word in the shop's name (word start, any language) or around a place
- [x] Berlin bounding box, not an area query: area queries time out on the busy public servers
- [x] Server list in `OVERPASS_URL` (default: overpass-api.de, then maps.mail.ru); next server on timeout, 429 or 5xx
- [x] Nominatim geocoding bounded to Berlin; at most one request a second
- [x] Disk cache in `scout/cache/` (gitignored): Overpass a day, Nominatim a month
- [x] Agent tool `map_search`; its OpenStreetMap links count as traced sources
- [x] Tested live on 29 September: 3 places for "afro, abaya, kimono" across Berlin, 136 fashion places around Hermannplatz; 15–30 s per uncached search on the public servers

### 2b.2 Places on the map (done)

- [x] New record field `storefront` (`yes` / `no` / `unconfirmed`)
- [x] Location set by code: the shop's own OpenStreetMap entry (same website, same name, or a cited entry with a matching street), else the geocoded address of a storefront
- [x] Never a pin or a shown address for online-only sellers (their Impressum address may be a home) or rejected shops
- [x] Search screen: numbered pins matching the result cards, directions via openstreetmap.org, desaturated tiles from tile.openstreetmap.org, credit under the map, CSP allows only that tile host

### 2b.3 Plain-search comparison (done)

- [x] Each request first runs as a plain Tavily search (10 results, no marketplace filter); each shop gets `visibility.plain_search_rank`
- [x] Screen: "X of Y don't show up in a plain web search for this" — measured against Tavily, not Google; say so in the video

### 2b.4 Still to do

- [ ] Live run with keys: does Nemotron call `map_search` early, with community-language words?
- [ ] Five requests (e.g. hanbok, abaya, aso-ebi fabric, sari blouse tailoring, kimono); note shops found only through the map
- [ ] Public demo: choose a tile provider that allows real traffic (tile.openstreetmap.org is for light use)
- [ ] When routes move to `backend/`, keep `scout/osm.py` as the domain layer; no second map client

---

## Phase 2c: Google Maps (optional, demo key)

Catch shops that opened recently: owners often add them to Google Maps before anyone maps them on OpenStreetMap.

### 2c.1 Built (branch `google-places`)

- [x] `scout/google_places.py`: Places API (New) Text Search, restricted to the Berlin box, Pro fields only (name, address, status, types): 5,000 free a month on a normal key; no website, hours or location
- [x] Agent tool `google_places`, offered only when `GOOGLE_MAPS_API_KEY` is set **and** `NEBIUS_ZERO_DATA_RETENTION=on` (Nebius stores prompts by default; Google's content must not be stored by the model)
- [x] No caching of Google answers; step log keeps place IDs only; links built from place IDs
- [x] Google-only shops: no pin on the OpenStreetMap map, address not stored or shown, an "Open in Google Maps" box with Google's required attribution
- [x] Nominatim geocoding only for records backed by a non-Google source
- [x] `check` part 4 (optional); 6 offline tests

### 2c.2 Still to do

- [ ] Project owner: create a Maps Demo Key (no credit card) and turn on Zero Data Retention on the Nebius Token Factory account profile page
- [ ] Live run: does Nemotron use `google_places` for "Neueröffnung" style requests, and do its leads survive the checks?
- [ ] Before any launch: the demo key is for development and testing only. A normal key needs a billing account; with an EEA billing address, Google content may then be shown on non-Google maps
- [ ] When routes move to `backend/`, keep `scout/google_places.py` as the domain layer

---

## Phase 3: Verification benchmark (`verify`)

Measure Scout against hand-judged ground truth; primary tuning loop.

### 3.1 Short run

- [ ] `python3 scout/cli.py verify --limit 6`
- [ ] Inspect printed table: `ok`, `X`, `?` (revisit), missing
- [ ] Save run JSON; note `score.agree`, `score.disagree`, `score.sent_to_a_person`, `score.missing`

### 3.2 Full run

- [ ] `python3 scout/cli.py verify` (all ~29 rows from `truth()` in `cli.py`)
- [ ] Publish summary line for README / video: **“Agreed with a person on X of 29”** (define whether revisit counts as disagreement for the headline — recommend: headline = accept/reject match only; revisit reported separately)

### 3.3 Miss analysis

- [ ] Bucket disagreements: wrong city, closed shop, marketplace reseller, culture tag, missing from search, Impressum not read
- [ ] For each bucket, decide: prompt change (`scout/agent.py` SYSTEM), budget change (`agent.py` constants), or tool behavior (`fetch.py` / Tavily params)

### 3.4 Tune and re-run

- [ ] Apply minimal prompt/budget diffs (prefer small changes per iteration)
- [ ] Re-run `--limit 6` after each change to save credits
- [ ] Full verify once satisfied with short-run trend

### 3.5 Regression

- [ ] `test_offline.py` still passes
- [ ] Offline tests for verify scoring (`test_score_counts_revisit_separately`, `test_truth_reads_the_private_files`) still valid if `score()` logic changes

---

## Phase 4: Draft listings (live) — after the hackathon (Culturalmaxxing feature)

Prove end-to-end “accept → draft listing” for shops with feeds.

### 4.1 CLI / engine

- [ ] From a verify or find run, pick an **accept** with Shopify/Woo feed (`check_platform` in agent log)
- [ ] Trigger listing draft via review UI **Draft listing** or code path `listing.draft(record)` (`scout/listing.py`)
- [ ] Confirm: tags from closed vocabulary; product **links** only; no copied descriptions or photos (see `test_listing_holds_facts_and_links_but_no_descriptions_or_photos`)

### 4.2 Rules vs Nemotron (`engine/agent3_taxonomy.py`)

- [ ] Note how many products rules classify vs model (`agent3_taxonomy.py` + tests `test_nemotron_only_gets_what_the_rules_left…`)
- [ ] Live failures: `listing.NoFeed`, robots / `crawl: false` → expect 409 from `/api/listing`

### 4.3 Sample run (public demo)

- [ ] Ensure `scout/web/sample-run.json` replays at `http://127.0.0.1:8770/#sample` without keys
- [ ] Sample includes at least one shop with listing draft for UI demo

---

## Phase 5: Concierge feasibility (`probe`) — after the hackathon (Culturalmaxxing feature)

Decide whether a future “occasion concierge” can search **within** shop domains without scraping full catalogues.

### 5.1 Run probe

- [ ] `python3 scout/cli.py probe` (default query `Kleid`; try 1–2 occasion terms if useful)
- [ ] Read JSON under `scout/runs/` (`probe-*.json`): `results`, `product_pages` per shop slug

### 5.2 Decision record

- [ ] Write 2–3 sentences in README or hackathon video script: probe yes/no/partial and why
- [ ] If weak: document fallback (feed-only concierge, no cross-shop product search)

---

## Phase 6: Review UI polish

Local **review** server still runs from `scout/server.py` in Phases 1–7; Phase 6 polish applies there until the review API and static assets **move to `backend/`** (see Phase 10.3 and Appendix E).

### 6.1 Typography

- [ ] Add `Spectral-Regular.woff2`, `Spectral-Medium.woff2`, `Spectral-Italic.woff2`, `Karla-Variable.woff2` under `scout/web/fonts/` (see `server.py` `FONTS` map)
- [ ] Verify `/fonts.css` generated and no third-party font requests

### 6.2 UX smoke

- [ ] EN/DE toggle persists (`localStorage` `scout-lang`)
- [ ] Busy state: second find blocked with 409 message
- [ ] Error paths: missing keys, bad key, Tavily limits — plain language (`server.friendly`)
- [ ] CSP / `own_page()` — cross-origin requests rejected (covered offline in `test_screen_refuses_other_websites_and_strange_paths`)

### 6.3 Optional UX improvements (only if time)

- [ ] Show verify score file picker if verify runs listed in `/api/status`
- [ ] Copy button for run id / cost summary for demo narration

---

## Phase 7: Hackathon deliverables

Align with [README.md](./README.md) hackathon checklist.

### 7.1 Repository & licence

- [ ] Public repo accessible; MIT [LICENSE](./LICENSE) present
- [ ] No secrets or private shop data in history

### 7.2 Working demo URL

Choose one approach and document it in README:

| Strategy | Notes |
| --- | --- |
| **A — Static replay host** | Host `index.html` + assets + `sample-run.json` only; `#sample` on load; no live keys on server |
| **B — Tunnel to localhost** | `scout/server.py` on operator machine during judging — fragile |
| **C — Recorded run bundle** | Ship JSON + static UI on GitHub Pages / Nebius-hosted static |
| **D — Backend Docker (static or API)** | `cd backend && docker-compose up --build`: serve **static** `scout/web/` + `sample-run.json` from the backend image or sidecar; **or** read-only replay routes in `backend/src/api_endpoints/` — still **no** judge-facing API keys on the public demo |

- [ ] Implement chosen strategy
- [ ] Add demo URL to README and Devpost submission
- [ ] Judge path: no API keys required for default experience

### 7.3 Video (< 3 minutes, YouTube)

- [ ] Script: problem → a request → map search + web search in several languages → checked shops on the map → "X of Y not in a plain web search" → sources / robots / business data only
- [ ] Show **only** `sample-run` or consented shops — or real public search results, if the team decides so (see the scope update)
- [ ] Mention Nebius Nemotron, Tavily and OpenStreetMap roles explicitly (Best Use of Tavily prize)
- [ ] Link video in README

### 7.4 Submission copy

- [ ] Devpost: working demo link, repo link, NVIDIA open model + Token Factory, Tavily integration
- [ ] Update README **Status** date and checklist table (Runs on Nebius, demo URL, video)

---

## Phase 8: CI & regression

### 8.1 Offline tests as gate

- [ ] Add or confirm GitHub Action: `python3 scout/test_offline.py` on push/PR to `main`
- [ ] No network, no keys in CI
- [ ] Optional (after backend routes land): CI job `cd backend && pip install -r requirements.txt && pytest tests/` — add `backend/tests/` as needed

### 8.2 Pre-push habit (contributors)

- [ ] Document in README **Working together**: run offline tests before push (already stated — keep accurate)

### 8.3 Live integration tests (optional, off by default)

- [ ] If added: separate script or marker, secrets in GitHub Actions only, never on fork PRs from untrusted contributors

---

## Phase 9: Documentation & handoff

### 9.1 README

- [ ] Refresh **Status**, **Open tasks** (check off completed items)
- [ ] Add **Verify score** line when Phase 3 complete
- [ ] Link to this file from README **Further reading** or **Working together**
- [ ] When Phase 10 starts: link [backend/README.md](./backend/README.md) and Appendix E from README **Next**

### 9.2 Operator runbook (short)

- [ ] “Check fails” → keys, base URL, model name
- [ ] “Verify missing many” → Tavily coverage, batch size `--batch`
- [ ] “Listing 409 NoFeed” → shop has no public feed or crawl false
- [ ] “Tavily 432/433” → plan / PAYG limits

### 9.3 Mark progress in this file

- [ ] Flip `[ ]` → `[x]` on tasks as work lands

---

## Phase 10: Post-hackathon (optional roadmap)

Not required for 30 October submission; tracks README “Next” item.

### 10.1 Shop approval workflow

- [ ] Export accepted runs → format suitable for Culturalmaxxing Berlin map (separate repo / product)
- [ ] Contact flow for shop approval before any public listing

### 10.2 Occasion concierge

- [ ] Depends on agreed shops + probe results
- [ ] Likely new agent brief, not an extension of Scout verify loop

### 10.3 Public backend API (all HTTP lives in `backend/`)

- [ ] **`backend/` is the only backend package** — extend [backend/](./backend/) (trim example routers, set `API_TITLE`, keep health check + Docker)
- [ ] **Migrate** `scout/server.py` behavior into FastAPI routers + services (status, replay SSE, find SSE, decision, listing, static files, CSP, fonts, single-run lock)
- [ ] Mount or copy `scout/web/` for the review UI from the backend process (paths documented in README)
- [ ] Document boundary during migration: CLI and tests may still mention `scout/server.py` until a `backend`-entry review command replaces it
- [ ] Public map contract: new resource routes in `backend/src/core_specs/configuration/config_file.json` + routers; import `scout.agent`, `scout.listing`, `scout.store` — do not duplicate handler logic in a second server
- [ ] Wire secrets in **`backend/.env`**: `NEBIUS_API_KEY`, `TAVILY_API_KEY`, `CMX_BOT_CONTACT` (+ RSA vars from `.env.example` only if used); rate-limit live find via SlowAPI in `backend/`
- [ ] Persistence: backend services call `scout/store.py` or wrap with `backend/src/utils/secure_file_io.py` and `set_allowed_root` pointing at `scout/runs/`
- [ ] OpenAPI at `/docs` is the stable contract for a Culturalmaxxing map frontend
- [ ] Deploy via `backend/docker-compose.yml`; Redis optional (cache GETs), not a substitute for run files

---

## Appendix A: Goal → phase mapping

| Goal | Phase |
| --- | --- |
| Keys and private data in place | Phase 0 |
| Nemotron + Tavily proven (`check`) | Phase 1 |
| Live find + review screen | Phase 1–2 |
| Agreement with human judgments | Phase 3 |
| Draft listings on real feeds | Phase 4 |
| Concierge / product-search feasibility | Phase 5 |
| Fonts and UI polish | Phase 6 |
| Demo URL + video + Devpost | Phase 7 |
| CI offline tests | Phase 8 |
| Docs and runbook | Phase 9 |
| Map + concierge + REST | Phase 10 (optional) — **Appendix E**; complete **`backend/`** migration |
| Docker static / hosted demo (optional) | Phase 7 strategy D or Appendix E.4 |

---

## Appendix B: Design notes & snippets

### B.1 Scout pipeline (unchanged architecture)

```
brief ──► plain web search (Tavily, for comparison)
  └────► Nemotron plans ──► map_search (OpenStreetMap: Overpass, Nominatim)
              ▲    │
              │    ├──────► web_search (Tavily)
              │    ├──────► read_page (fetch → optional Tavily Extract)
              │    ├──────► check_platform (Shopify / Woo feed?)
              └────┴──────► submit_shops ──► schema + sources ──► places (code) ──► screen with map
```

### B.2 Local review API (`scout/server.py` today → `backend/` after migration)

| Method | Path | Response |
| --- | --- | --- |
| GET | `/api/status` | JSON |
| GET | `/api/replay?run=` | SSE |
| POST | `/api/find` | SSE |
| POST | `/api/decision` | JSON |
| POST | `/api/listing` | JSON |

Runs and shops are identified in **JSON bodies**, not as `/runs/{id}` resources. **Implement these paths in `backend/`** when migrating off stdlib; the public map may add **resource-oriented** `/v1/...` routes alongside or instead — see Appendix E.

### B.3 Verify score (headline metrics)

From `scout/cli.py` → `score()`:

- **agree** — Scout verdict equals human `expected` (`accept` / `reject`) among judged rows
- **disagree** — verdict mismatch
- **sent_to_a_person** — Scout `revisit` (not counted as agree/disagree error by design)
- **missing** — no matching shop in Scout output

Recommend README headline: `agree` of `checked`, with revisit and missing reported separately.

### B.4 Env template (minimum)

```bash
NEBIUS_API_KEY=
TAVILY_API_KEY=
CMX_BOT_CONTACT=
# Optional after check:
# NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/
# NEBIUS_MODEL=nvidia/nemotron-3-super-120b-a12b
# SCOUT_DATA=/path/to/private/data
```

### B.5 Cost discipline

- One live find at a time on the server (`running` lock in `server.py`)
- Use `verify --limit 6` for prompt experiments
- Record `usage` from each run JSON for demo talking points

---

## Appendix C: Manual verification checklist

After Phases 1–7:

1. [ ] `python3 scout/test_offline.py` — all pass, no network
2. [ ] `python3 scout/cli.py check` — exit 0, tool + schema + search + OpenStreetMap OK
3. [ ] CLI `find` with invented-style brief — run file on disk, sensible verdicts + sources
4. [ ] `python3 scout/server.py` — live find from UI, steps stream, decisions saved
5. [ ] `#sample` — full replay without keys; footer/copy states data is invented
6. [ ] `verify --limit 6` then full verify — score recorded in README or run JSON
7. [ ] Draft listing on sample + one live accept (if keys and feed available)
8. [ ] Demo URL loads for judge without your `.env`
9. [ ] Video plays, under 3 minutes, only safe shop names

---

## Appendix D: Out of scope / waivers

| Item | Reason |
| --- | --- |
| Publishing listings to a public map | Product decision; Scout explicitly has no publish button |
| Emailing or contacting shops | Ethics / scope; bot contact is for transparency on crawl only |
| Committing `data/shops.json` or ground truth | Privacy; gitignored |
| Replacing file store with Postgres | Not needed for hackathon; YAGNI |
| Full REST API for third-party clients | Hackathon: may still use `scout/server.py`; all new backend work and final product API live under **`backend/`** only |
| Copying product descriptions or images into drafts | Policy enforced in listing pipeline |
| Running unbounded parallel finds on server | Blocked by design (API cost + fairness) |
| Occasion concierge MVP | Post-agreement shops; Phase 10 |

---

## Appendix E: Migrating backend concerns to `backend/`

Use when moving HTTP, deploy, and public API off `scout/server.py` into [backend/](./backend/). Skip for hackathon Phases 0–7 unless using strategy **7.2 D** (Docker from `backend/`).

### E.1 Monorepo layout (single backend folder)

- [ ] All FastAPI code, Docker, backend `.env`, and backend tests live under **`backend/`** — no parallel `api/` or duplicate app roots
- [ ] Remove or rename example router groups under `backend/src/api_endpoints/routers/`; keep `root_endpoint.py` health check
- [ ] Configure imports so `backend/` can call `scout.*` and `engine.*` from repo root (e.g. `PYTHONPATH`, package layout, or documented `sys.path` in `main.py`)

### E.2 Migrate review server (`scout/server.py`)

- [ ] Port `/api/status`, `/api/replay`, `/api/find`, `/api/decision`, `/api/listing` to routers + services in `backend/src/`
- [ ] Preserve SSE event shape expected by `scout/web/app.js` (or update frontend once under `backend/static/` / mounted `scout/web/`)
- [ ] Port static hosting, `fonts.css`, CSP, `own_page()` / origin checks, and the **one live find at a time** lock
- [ ] Deprecate `python3 scout/server.py` in README when `cd backend && python main.py` (or compose) is equivalent

### E.3 Config-driven public routes (`backend/src/core_specs/configuration/config_file.json`)

Suggested endpoint keys (names illustrative — align with OpenAPI):

| Config key | Method | Public path (example) | Backing code |
| --- | --- | --- | --- |
| `runs_list` | GET | `/v1/runs` | `store.list_runs()` |
| `runs_get` | GET | `/v1/runs/{run_id}` | `store.load_run(...)` |
| `decisions_create` | POST | `/v1/runs/{run_id}/decisions` | `store.decide(...)` |
| `find_create` | POST | `/v1/find` | `agent.research(...)` — strict rate limit + auth |
| `listing_create` | POST | `/v1/runs/{run_id}/shops/{slug}/listing` | `listing.draft(...)` |

- [ ] Add matching Pydantic models under `backend/src/models/` (follow `models_example.py` Base/Create/Response split)
- [ ] Set SlowAPI limits on any route that triggers Nebius/Tavily spend

### E.4 Static review UI

- [ ] Serve `scout/web/` from the backend app (static mount or copy into `backend/static/` — one documented approach)
- [ ] Judges’ keyless demo still follows Phase 7 strategies A/C/D; production demo must not ship operator `.env`

### E.5 Ops

- [ ] `cd backend && docker-compose up --build` with secrets via host env file (never in image layers)
- [ ] Logs under `backend/logs/`; correlate with run ids in messages
- [ ] Optional `REDIS_ENABLED=true` only for caching idempotent GETs — run files remain source of truth until Postgres is added in `backend/src/resources/db/`

---

## Notes

- **Human in the loop:** Automation ends at the review queue; `accept` / `reject` / revisit on screen is the intended workflow for the hackathon story.
- **NVIDIA + Tavily + OpenStreetMap narrative:** Nemotron plans and submits structured shops; Tavily is search, the plain-search comparison, and Extract when the polite fetcher gets a thin page; OpenStreetMap finds shops without websites and places them on the map — say all three in the video.
- **Priority order:** Phase 0 → Phase 1 (check + smoke find) → Phase 2b.4 (live map runs) → Phase 3 (verify) → Phase 7 (demo + video) → Phase 2 as depth → Phase 6/8/9 in parallel → Phases 4, 5 and 10 after the hackathon.
- **Backend folder:** All HTTP, Docker, deploy env, and FastAPI routes belong in **`backend/`**; migrate off `scout/server.py` in Phase 10 / Appendix E — do not add a second backend tree.
- **Private data:** Never use real shop names from `data/` in the public demo URL or YouTube; use `sample-run.json` unless written consent exists.
- **Breaking change risk:** Tightening prompts may increase `revisit` — track revisit rate so the map does not starve from over-caution.
