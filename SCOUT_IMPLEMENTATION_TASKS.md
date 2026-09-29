# Scout — Live Integration, Quality & Hackathon Demo — Implementation Tasks

## Overview

Bring **Culturalmaxxing Scout** from “26 offline tests pass, never run live” to a **demonstrable hackathon submission**: Nemotron on **Nebius Token Factory** and **Tavily** working end-to-end, human-in-the-loop review on the local screen, measurable agreement with hand-judged ground truth, and a public demo URL plus short video. Nothing is published and nobody is contacted; output stays in `scout/runs/` until a person approves.

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
| Review screen (EN/DE, SSE, decisions, listing) | **Done** — `scout/server.py`, `scout/web/` |
| File-backed runs & decisions | **Done** — `scout/store.py` |
| Offline test suite (26 tests) | **Done** — `scout/test_offline.py` |
| Live Nebius / Tavily integration | **Not done** — first step: `python3 scout/cli.py check` |
| Verify score vs human (29 shops) | **Not done** — needs keys + private `data/` |
| Prompt / budget tuning from misses | **Not done** |
| Product search probe (`probe`) | **Not done** — needs keys + `shops.json` |
| Local fonts (Spectral, Karla) | **Not done** — falls back to Georgia / Helvetica |
| Public demo URL | **Not done** |
| YouTube video (< 3 min) | **Not done** |
| CI running `test_offline.py` on push | **Not verified** — add workflow if missing |

**Target state:**

- `python3 scout/cli.py check` exits **0** with tool calling + JSON schema + Tavily search on real keys
- At least one **live** `find` brief saved under `scout/runs/` and reviewable in the UI
- **Verify** run documented: e.g. “agreed with a person on X of 29” (plus revisit/missing breakdown)
- Misses analyzed; prompt and/or budgets adjusted; re-run verify until score is acceptable for demo narrative
- **`probe`** answers whether Tavily can see product pages on registered shops’ domains without copying catalogues
- Review screen polished (fonts optional but preferred), **`#sample`** replay works without keys for judges
- **Demo URL** serves sample replay or a recorded run; **video** shows only invented or consented shops
- Root README **Status** and hackathon checklist updated to match reality

**Reference docs:** [README.md](./README.md), [data/README.md](./data/README.md), [engine/README.md](./engine/README.md)

**Related code:**

| Layer | Primary files |
| --- | --- |
| Discovery agent | `scout/agent.py` |
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

- [ ] Use Python **3.14** (or project-tested version); no pip install required (stdlib only)
- [ ] From repo root: `python3 scout/test_offline.py` — all green before any live spend

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

## Phase 4: Draft listings (live)

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

## Phase 5: Concierge feasibility (`probe`)

Decide whether a future “occasion concierge” can search **within** shop domains without scraping full catalogues.

### 5.1 Run probe

- [ ] `python3 scout/cli.py probe` (default query `Kleid`; try 1–2 occasion terms if useful)
- [ ] Read JSON under `scout/runs/` (`probe-*.json`): `results`, `product_pages` per shop slug

### 5.2 Decision record

- [ ] Write 2–3 sentences in README or hackathon video script: probe yes/no/partial and why
- [ ] If weak: document fallback (feed-only concierge, no cross-shop product search)

---

## Phase 6: Review UI polish

Local-only server; not a public REST product API.

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
| **B — Tunnel to localhost** | `server.py` on operator machine during judging — fragile |
| **C — Recorded run bundle** | Ship JSON + static UI on GitHub Pages / Nebius-hosted static |

- [ ] Implement chosen strategy
- [ ] Add demo URL to README and Devpost submission
- [ ] Judge path: no API keys required for default experience

### 7.3 Video (< 3 minutes, YouTube)

- [ ] Script: problem → Find → Verify → Judge on screen → Draft listing → sources / robots / no publish
- [ ] Show **only** `sample-run` or consented shops
- [ ] Mention Nebius Nemotron + Tavily roles explicitly (Best Use of Tavily prize)
- [ ] Link video in README

### 7.4 Submission copy

- [ ] Devpost: working demo link, repo link, NVIDIA open model + Token Factory, Tavily integration
- [ ] Update README **Status** date and checklist table (Runs on Nebius, demo URL, video)

---

## Phase 8: CI & regression

### 8.1 Offline tests as gate

- [ ] Add or confirm GitHub Action: `python3 scout/test_offline.py` on push/PR to `main`
- [ ] No network, no keys in CI

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

### 10.3 Public backend API

- [ ] Current `server.py` is **RPC + SSE for localhost review**, not REST for a public map
- [ ] If a public map frontend is built, design new API boundaries; do not treat `/api/find` as stable public contract

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
| Map + concierge + REST | Phase 10 (optional) |

---

## Appendix B: Design notes & snippets

### B.1 Scout pipeline (unchanged architecture)

```
brief ──► Nemotron plans ──► web_search (Tavily)
              ▲    │
              │    ├──────► read_page (fetch → optional Tavily Extract)
              │    ├──────► check_platform (Shopify / Woo feed?)
              └────┴──────► submit_shops ──► schema + sources ──► review queue
```

### B.2 Local review API (not REST)

| Method | Path | Response |
| --- | --- | --- |
| GET | `/api/status` | JSON |
| GET | `/api/replay?run=` | SSE |
| POST | `/api/find` | SSE |
| POST | `/api/decision` | JSON |
| POST | `/api/listing` | JSON |

Runs and shops are identified in **JSON bodies**, not as `/runs/{id}` resources.

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
2. [ ] `python3 scout/cli.py check` — exit 0, tool + schema + search OK
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
| Full REST API for third-party clients | Current server is local review adapter only |
| Copying product descriptions or images into drafts | Policy enforced in listing pipeline |
| Running unbounded parallel finds on server | Blocked by design (API cost + fairness) |
| Occasion concierge MVP | Post-agreement shops; Phase 10 |

---

## Notes

- **Human in the loop:** Automation ends at the review queue; `accept` / `reject` / revisit on screen is the intended workflow for the hackathon story.
- **NVIDIA + Tavily narrative:** Nemotron plans and submits structured shops; Tavily is search plus Extract when the polite fetcher gets a thin page — say both in the video.
- **Priority order:** Phase 0 → Phase 1 (check + smoke find) → Phase 3 (verify) → Phase 7 (demo + video) → Phase 2/4/5 as depth → Phase 6/8/9 in parallel → Phase 10 later.
- **Private data:** Never use real shop names from `data/` in the public demo URL or YouTube; use `sample-run.json` unless written consent exists.
- **Breaking change risk:** Tightening prompts may increase `revisit` — track revisit rate so the map does not starve from over-caution.
