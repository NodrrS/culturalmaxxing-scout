# Culturalmaxxing Scout

Scout helps people find fashion shops in Berlin that big platforms and a plain web search miss. You say what you are looking for. Scout searches OpenStreetMap and the web, in German and in the community's own language, and checks every shop. It then shows them on a map, with a source for every fact.

Built for the [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/) with **NVIDIA Nemotron** on **Nebius Token Factory**, **Tavily** for web search and **OpenStreetMap** for places. **Google Maps** is an optional extra source of leads.

## The idea

Berlin has hundreds of small fashion shops run by people from South Asia, Turkey, the Arab world, Africa, Central Asia and East Asia: bridal houses, abaya ateliers, tailors, kimono sellers, slow-fashion labels. Most of them are hard to find online. Many have no website, marketplaces don't list them, and a plain web search mostly returns chains and resellers.

Scout finds them in four steps:

1. **Search the map.** OpenStreetMap is kept up by people who live nearby, and it lists many shops that have no website. Scout searches it by words in a shop's name, in any language, and around the streets where a community shops.
2. **Search the web.** In German first, then in the community's own language (Turkish, Arabic, Russian and others). Marketplaces are filtered out.
3. **Check.** Scout reads the shop's Impressum or a recent listing. Is it in Berlin? Does it sell what you asked for? Is it still trading? Can you visit it?
4. **Show.** Confirmed shops come first, then shops worth a visit to check, on a map with directions. Each result says whether a plain web search for the same request would have found it.
5. **Learn from visitors.** People who went there say whether a shop exists and correct what Scout got wrong. Anyone can send a tip about a shop Scout missed. See [Visitors in the loop](#visitors-in-the-loop).

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

`check` lists the Nemotron models your key can reach, tries one tool call and one JSON-schema call, runs one Tavily search, and runs one OpenStreetMap search and one address lookup (no key needed). With a Google Maps key, it also runs one Google search. If the default model is served from another endpoint, it prints the two lines to add to `scout/.env`.

Google Maps is optional. See [Google Maps](#google-maps-optional) for the demo key and the one Nebius setting it needs.

```bash
python3 scout/server.py
```

The search screen opens at http://127.0.0.1:8770. The sample search replays without keys, and http://127.0.0.1:8770/#sample plays it on load.

## Commands

| Command | What it does | Needs |
|---|---|---|
| `python3 scout/cli.py check` | Are the keys and the maps working? | Keys |
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
             │    ├──────► google_places ──► Google Maps, optional: leads as place IDs, never a pin
             └────┴──────► submit_shops ──► schema ──► source tracing ──► place on the map ──► screen
```

| Path | Job |
|---|---|
| [scout/agent.py](scout/agent.py) | The prompt, the tools, the loop, the budgets, source tracing, places and the plain-search comparison |
| [scout/osm.py](scout/osm.py) | OpenStreetMap: Overpass search and Nominatim geocoding, polite and cached |
| [scout/google_places.py](scout/google_places.py) | Google Maps, optional: Places API Text Search with a Maps Demo Key |
| [scout/feedback.py](scout/feedback.py) | What visitors report about shops, and the tips they send |
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

## Google Maps (optional)

Owners often add a new shop to Google Maps in its first days, before anyone maps it on OpenStreetMap or a search engine finds its website. With a key, Scout gets a sixth tool, `google_places`, which asks Google Maps for leads and then checks them like any other.

**Setting it up**

1. Get a [Maps Demo Key](https://mapsplatform.google.com/maps-demo-key/). It needs a Google account but no credit card. It has daily limits, and Google offers it for development and testing, not for a launched product.
2. Turn on **Zero Data Retention** on your Nebius Token Factory account profile page. Nebius never trains on your prompts, but it stores them by default to speed up answers, and Google's content must not be stored by the model.
3. Add both lines to `scout/.env`:

```bash
GOOGLE_MAPS_API_KEY=your-demo-key
NEBIUS_ZERO_DATA_RETENTION=on
```

Without the second line, Scout never offers the tool to Nemotron, and `check` says why.

**What the code does about Google's terms**

- It asks only for name, address, open or closed, and the kind of place. That's Google's "Pro" tier, 5,000 free searches a month on a normal key. Website, opening hours and ratings would move every search into the 1,000-a-month tier, so they are left out.
- Nothing from Google is cached; every search goes to Google.
- Only place IDs are kept, because Google exempts them from its storage limits. The step log records place IDs, never names or addresses. Links to Google Maps are built from the place IDs.
- A shop that only Google knows is never drawn on the OpenStreetMap map, and its address is neither stored nor shown. It gets an "Open in Google Maps" button in a separate box with Google's required credit instead. The demo key has no EEA billing account, so the EEA permission to show Google content on other maps may not apply to it.
- An address is geocoded onto the map only when a source other than Google backs the record.

## Visitors in the loop

Scout's answers are a starting point; people who go there know better. Every shop on the screen asks:

1. **"Have you been there? Does this shop exist?"** Yes or no.
2. **"Anything that doesn't match?"** An optional note, for example "it's a Turkish perfume shop, not an Arab one".

Below the results, **"Know a shop Scout missed?"** takes a tip: name, where, what they sell, and an optional link.

**What happens with them**

- **The next time the shop appears,** the card shows what visitors said: how many say it exists or doesn't, and their latest notes, marked "not checked by Scout".
- **The latest report counts.** When it says a shop no longer exists, a confirmed shop goes back to "not yet confirmed" until someone confirms it again. When it says a shop Scout found closed or moved is there, the shop comes back as "not yet confirmed" for another check.
- **A report never removes a shop.** Anyone could send one, so it only changes how sure Scout is.
- **The model sees reports as data.** They travel with the map entries and search results that show the shop again. The model uses a correction unless other evidence contradicts it, and says so in its reason. Instructions written in a note are ignored, like instructions written on a web page.
- **Tips become leads.** Scout adds the five most recent tips to the next searches and checks them like any other lead. A tip is never evidence on its own. The `verify` benchmark ignores tips, so its score stays clean.

**What is kept:** only what people typed and the date. No account, no IP address, no browser details. The form asks people not to put names or contact details in their notes. Each shop takes at most 5 reports a day, and Scout takes at most 50 tips a day. Everything stays on this machine in `scout/feedback/`, which is never committed.

## What the code enforces, whatever the model says

- **robots.txt is final.** If a site asks crawlers to stay out, neither our fetcher nor Tavily reads it, and the record is marked `crawl: false`.
- **Our own fetcher comes first.** It names itself and gives a contact address. Tavily Extract reads a page only when our fetcher gets an empty shell.
- **Sources are traced.** A record may cite only pages and map entries the agent was shown in that run. If none of its sources can be traced, "confirmed" becomes "not yet confirmed".
- **Places come from the code.** A pin is the shop's own OpenStreetMap entry, or the geocoded address of a shop that customers can visit. The model never gives coordinates. An online-only seller's address may be a home, so it is never pinned or shown.
- **The comparison is measured, not claimed.** Each search first runs the same request as a plain web search, and the screen shows which shops that search would have missed. The comparison is with a Tavily search, not with Google.
- **The vocabulary is closed.** Every record is checked against the schema. A value outside the vocabulary goes back to the model with the reason.
- **Budgets are counted in code.** When the map searches, Google searches, web searches or page reads run out, the model has to submit.
- **Visitors can correct Scout, but not erase a shop.** A report changes how sure Scout is, never whether the shop is shown, and it is applied when results are shown, so saved runs stay as they were.
- **Google content stays Google's.** Place IDs only in the logs, no Google coordinates at all, no address known only from Google, and no Google results to the model unless Nebius keeps no data.
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
- [ ] Get a Maps Demo Key, turn on Zero Data Retention in Nebius, and try `google_places` on a shop that opened recently.
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
- Never commit `scout/.env`, `scout/runs/`, `scout/cache/`, `scout/feedback/` or anything in `data/` except its README. `.gitignore` covers them all, so `git add -f` is the only way to get them in. Don't use it for these.

## About Culturalmaxxing

Culturalmaxxing Berlin is a map of the city's cultural fashion shops, for the people who wear these clothes and for everyone curious about them. It sends visitors to the shop, in person or to its own website. It sells nothing itself. Scout becomes part of it after the hackathon.

## Licence

[MIT](LICENSE)
