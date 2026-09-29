# Culturalmaxxing Scout

Scout helps people find fashion shops in Berlin that big platforms and a plain web search miss. You say what you are looking for. Scout searches OpenStreetMap and the web, in German and in the community's own language, and checks every shop. It then shows them on a map, with a source for every fact.

Built for the [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/) with **NVIDIA Nemotron** on **Nebius Token Factory**, **Tavily** for web search and **OpenStreetMap** for places.

## The idea

Berlin has hundreds of small fashion shops run by people from South Asia, Turkey, the Arab world, Africa, Central Asia and East Asia: bridal houses, abaya ateliers, tailors, kimono sellers, slow-fashion labels. Most of them are hard to find online. Many have no website, marketplaces don't list them, and a plain web search mostly returns chains and resellers.

Scout finds them in four steps:

1. **Search the map.** OpenStreetMap is kept up by people who live nearby, and it lists many shops that have no website. Scout searches it by words in a shop's name, in any language, and around the streets where a community shops.
2. **Search the web.** In German first, then in the community's own language (Turkish, Arabic, Russian and others). Marketplaces are filtered out.
3. **Check.** Scout reads the shop's Impressum or a recent listing. Is it in Berlin? Does it sell what you asked for? Is it still trading? Can you visit it?
4. **Show.** Confirmed shops come first, then shops worth a visit to check, on a map with directions. Each result says whether a plain web search for the same request would have found it.

**Scope.** For the hackathon, Scout is a standalone app for shoppers. After the hackathon it becomes a feature of [Culturalmaxxing Berlin](#about-culturalmaxxing). The shop approval flow and the draft listings in the code belong to that later step, not to the hackathon app.

## Status

**29 September 2026:** the 37 offline tests pass. The OpenStreetMap search and geocoding were tested live. Nemotron and Tavily have **not yet run live**. The first job is `python3 scout/cli.py check` with real keys.

## Quick start

Python only, standard library, nothing to install. Tested with Python 3.14.

```bash
cp scout/.env.example scout/.env
```

Fill in `NEBIUS_API_KEY`, `TAVILY_API_KEY` and `CMX_BOT_CONTACT` (a project address shown to every site and map service Scout asks).

```bash
python3 scout/cli.py check
```

`check` lists the Nemotron models your key can reach, tries one tool call and one JSON-schema call, runs one Tavily search, and runs one OpenStreetMap search and one address lookup (no key needed). If the default model is served from another endpoint, it prints the two lines to add to `scout/.env`.

```bash
python3 scout/server.py
```

The search screen opens at http://127.0.0.1:8770. The sample search replays without keys, and http://127.0.0.1:8770/#sample plays it on load.

## Commands

| Command | What it does | Needs |
|---|---|---|
| `python3 scout/cli.py check` | Are the keys and the map working? | Keys |
| `python3 scout/cli.py find "REQUEST"` | Find shops for a request, for example `find "a hanbok for a wedding"`. `--seeds N` also checks N names from `data/seeds.json` | Keys |
| `python3 scout/cli.py verify` | Re-check shops a person already judged by hand, and score Scout against that person. `--limit 6` for a short run | Keys, private data |
| `python3 scout/cli.py probe` | Can Tavily see the registered shops' product pages? For the later Culturalmaxxing feature | Keys, private data |
| `python3 scout/server.py` | The search screen | Keys for live searches |
| `python3 scout/test_offline.py` | The offline tests. No keys, no network | Nothing |

## How it works

```
request ──► plain web search, kept for comparison
   │
   └──► Nemotron plans ──► map_search ─────► OpenStreetMap: shops by name, or around a place
             ▲    │
             │    ├──────► web_search ─────► Tavily, Germany first, marketplaces filtered out
             │    ├──────► read_page ──────► robots.txt ──► our named fetcher ──► Tavily Extract only
             │    │                          says no: stop                        if the page needs rendering
             │    ├──────► check_platform ► does the shop sell online?
             │    │
             └────┴──────► submit_shops ──► schema ──► source tracing ──► place on the map ──► screen
```

| Path | Job |
|---|---|
| [scout/agent.py](scout/agent.py) | The prompt, the five tools, the loop, the budgets, source tracing, places and the plain-search comparison |
| [scout/osm.py](scout/osm.py) | OpenStreetMap: Overpass search and Nominatim geocoding, polite and cached |
| [scout/clients.py](scout/clients.py) | Nebius and Tavily over plain HTTPS, the schema check, the cost counter |
| [scout/server.py](scout/server.py), [scout/web/](scout/web/) | The search screen with its map, in English and German |
| [scout/store.py](scout/store.py) | Runs, step logs and decisions as plain files |
| [scout/cli.py](scout/cli.py) | The commands above |
| [scout/listing.py](scout/listing.py) | Draft listings from a shop's feed, for the later Culturalmaxxing feature |
| [engine/](engine/) | The parts of the Culturalmaxxing engine that Scout reuses: the polite fetcher, the tag vocabulary and rules, feed reading, link building |
| [backend/](backend/) | The FastAPI backend, where the HTTP surface moves over time. See [SCOUT_IMPLEMENTATION_TASKS.md](SCOUT_IMPLEMENTATION_TASKS.md) |

## OpenStreetMap

| Job | Service | How Scout uses it |
|---|---|---|
| Find shops | [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) | Fashion shops (clothes, boutique, fabric, tailor, bridal, shoes, bags, jewellery and more) by a word at the start of a word in their name, or around a street or square. The search covers a box around Berlin. When a server is busy, the next one is tried |
| Place a shop | [Nominatim](https://nominatim.org/) | The published address of a shop you can visit, turned into coordinates |
| Show the map | tile.openstreetmap.org | The map tiles on the screen, desaturated so the pins stand out. No map library |

Both data services are run by volunteers, so Scout keeps to their usage policies. Every request names the app and a contact. Nominatim gets at most one request a second. Answers are cached in `scout/cache/`, Overpass answers for a day and Nominatim answers for a month. The screen credits OpenStreetMap under the map, and every place links to its OpenStreetMap page. Map data is © OpenStreetMap contributors, under the [ODbL](https://www.openstreetmap.org/copyright).

A heads-up for a public demo: the map tiles load from OpenStreetMap's servers, which see each visitor's IP address, and those servers are meant for light use. A demo with real traffic needs a tile provider that allows it.

## What the code enforces, whatever the model says

- **robots.txt is final.** If a site asks crawlers to stay out, neither our fetcher nor Tavily reads it, and the record is marked `crawl: false`.
- **Our own fetcher comes first.** It names itself and gives a contact address. Tavily Extract reads a page only when our fetcher gets an empty shell.
- **Sources are traced.** A record may cite only pages and map entries the agent was shown in that run. If none of its sources can be traced, "confirmed" becomes "not yet confirmed".
- **Places come from the code.** A pin is the shop's own OpenStreetMap entry, or the geocoded address of a shop that customers can visit. The model never gives coordinates. An online-only seller's address may be a home, so it is never pinned or shown.
- **The comparison is measured, not claimed.** Each search first runs the same request as a plain web search, and the screen shows which shops that search would have missed. The comparison is with a Tavily search, not with Google.
- **The vocabulary is closed.** Every record is checked against the schema. A value outside the vocabulary goes back to the model with the reason.
- **Budgets are counted in code.** When the map searches, web searches or page reads run out, the model has to submit.
- **Pages are data.** Page text and map entries reach the model only as tool answers, never as instructions.
- **Business data only.** Scout records the channels a business publishes for customers, never private addresses or personal numbers.
- **The screen is local.** It listens on 127.0.0.1, refuses requests from other websites, runs one search at a time, and loads nothing from outside except map tiles.

## Private data

Three files describe real shops that have not agreed to be listed: the shop registry, the seeds, and the hand-judged ground truth. They are not in this repository, and git ignores them. See [data/README.md](data/README.md).

Everything in [scout/web/sample-run.json](scout/web/sample-run.json) and in the tests is invented. The shops don't exist, and the `.example` domains lead nowhere.

## Demo and real shops: to decide

A live search shows real shops from public sources, their OpenStreetMap entries and their own pages, as any map or search engine does. Two rules still hold: nothing from `data/` appears in a demo or video, and no address is shown for an online-only seller. Whether the video shows a live search with real shop names, or only the sample search, is for the team to decide before recording.

## Hackathon checklist

Submissions close **30 October 2026, 10:00 Pacific**.

| Requirement | State |
|---|---|
| Runs on Nebius Token Factory | Built, not yet run live |
| Uses an NVIDIA open model | Nemotron is the default model |
| Public repository | This one |
| Open-source licence | MIT, see [LICENSE](LICENSE) |
| Working demo URL | To do |
| Video under 3 minutes, on YouTube | To do |
| Best Use of Tavily, a separate prize | Tavily does the web search, the plain-search comparison, and Extract as the fallback reader |

## Open tasks

- [ ] Run `check` with real keys. Fix whatever the live Nemotron and Tavily answers show.
- [ ] Try five requests, for example a hanbok for a wedding, an abaya, aso-ebi fabric, sari blouse tailoring, a kimono. Note which shops the plain search misses.
- [ ] Run `verify --limit 6`, then the full set. Note the score, for example "agreed with a person on X of 29".
- [ ] Tune the prompt and the budgets on the misses.
- [ ] Decide what the demo and the video may show (see above).
- [ ] Add the Spectral and Karla font files to `scout/web/fonts/`. The screen loads no font from a third party and falls back to Georgia and Helvetica until then.
- [ ] Put up a demo URL.
- [ ] Record the video.
- [ ] After the hackathon, with Culturalmaxxing: shop approval, draft listings, the occasion concierge.

## Working together

- Work on a branch and open a pull request into `main`.
- Run `python3 scout/test_offline.py` before you push.
- Never commit `scout/.env`, `scout/runs/`, `scout/cache/` or anything in `data/` except its README. `.gitignore` covers them all, so `git add -f` is the only way to get them in. Don't use it for these.

## About Culturalmaxxing

Culturalmaxxing Berlin is a map of the city's cultural fashion shops, for the people who wear these clothes and for everyone curious about them. It sends visitors to the shop, in person or to its own website. It sells nothing itself. Scout becomes part of it after the hackathon.

## Licence

[MIT](LICENSE)
