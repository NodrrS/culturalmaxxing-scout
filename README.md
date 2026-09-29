# Culturalmaxxing Scout

Scout finds Berlin's cultural fashion shops that the big platforms miss. It checks each one against its own Impressum and drafts a listing for the shop to approve. Every fact carries a source. Nothing is published and nobody is contacted.

Built for the [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/) with **NVIDIA Nemotron** on **Nebius Token Factory**, and **Tavily** for search.

## The idea

Berlin has hundreds of small fashion shops run by people from South Asia, Turkey, the Arab world, Africa, Central Asia and East Asia: bridal houses, abaya ateliers, kimono sellers, slow-fashion labels. Most of them are hard to find online. Marketplaces don't list them, and a general search mostly returns chains and resellers.

[Culturalmaxxing Berlin](#about-culturalmaxxing) is a map of these shops. Scout is how the map grows without guessing:

1. **Find.** Search in German, then in the community's own language (Turkish, Arabic, Russian and others). Results from Germany come first, and marketplaces are filtered out.
2. **Verify.** Read the shop's Impressum for a Berlin business address. Check that it is still trading and whether it publishes a product feed.
3. **Judge.** Mark each shop accept, reject or "for a person", with a reason and a source for every fact. A closed shop, or one based outside Berlin, counts as a finding too.
4. **Draft.** For an accepted shop, read its own product feed, tag the products with a closed vocabulary, and draft a listing. The shop approves it before it appears anywhere.

A person makes every decision on a review screen. There is no publish button.

## Status

**29 September 2026:** the 26 offline tests pass. Scout has **not yet run against the live services**. The first job is `python3 scout/cli.py check` with real keys.

## Quick start

Python only, standard library, nothing to install. Tested with Python 3.14.

```bash
cp scout/.env.example scout/.env
```

Fill in `NEBIUS_API_KEY`, `TAVILY_API_KEY` and `CMX_BOT_CONTACT` (a project address shown to every site Scout reads).

```bash
python3 scout/cli.py check
```

`check` lists the Nemotron models your key can reach, tries one tool call and one JSON-schema call, and runs one search. If the default model is served from another endpoint, it prints the two lines to add to `scout/.env`.

```bash
python3 scout/server.py
```

The review screen opens at http://127.0.0.1:8770. The sample run replays without keys, and http://127.0.0.1:8770/#sample plays it on load.

## Commands

| Command | What it does | Needs |
|---|---|---|
| `python3 scout/cli.py check` | Are both keys working? | Keys |
| `python3 scout/cli.py find "BRIEF"` | Research a brief. `--seeds N` also checks N names from `data/seeds.json` | Keys |
| `python3 scout/cli.py verify` | Re-check shops a person already judged by hand, and score Scout against that person. `--limit 6` for a short run | Keys, private data |
| `python3 scout/cli.py probe` | Can Tavily see the registered shops' product pages? | Keys, private data |
| `python3 scout/server.py` | The review screen | Keys for live runs |
| `python3 scout/test_offline.py` | The offline tests. No keys, no network | Nothing |

## How it works

```
brief ──► Nemotron plans ──► web_search ──► Tavily, Germany first, marketplaces filtered out
              ▲    │
              │    ├──────► read_page ────► robots.txt ──► our named fetcher ──► Tavily Extract only
              │    │                        says no: stop                        if the page needs rendering
              │    ├──────► check_platform ► Shopify or WooCommerce feed?
              │    │
              └────┴──────► submit_shops ──► schema check ──► source tracing ──► review queue ──► a person decides
```

| Path | Job |
|---|---|
| [scout/clients.py](scout/clients.py) | Nebius and Tavily over plain HTTPS, the schema check, the cost counter |
| [scout/agent.py](scout/agent.py) | The prompt, the four tools, the loop, the budgets, source tracing |
| [scout/listing.py](scout/listing.py) | From an accepted shop to a draft listing: feed first, rules next, Nemotron for the rest |
| [scout/store.py](scout/store.py) | Runs, step logs and decisions as plain files |
| [scout/server.py](scout/server.py), [scout/web/](scout/web/) | The review screen, in English and German |
| [scout/cli.py](scout/cli.py) | The commands above |
| [engine/](engine/) | The parts of the Culturalmaxxing engine that Scout reuses: the polite fetcher, the tag vocabulary and rules, feed reading, link building |

## What the code enforces, whatever the model says

- **robots.txt is final.** If a site asks crawlers to stay out, neither our fetcher nor Tavily reads it, and the record is marked `crawl: false`.
- **Our own fetcher comes first.** It names itself and gives a contact address. Tavily Extract reads a page only when our fetcher gets an empty shell.
- **Sources are traced.** A record may cite only pages the agent was shown in that run. If none of its sources can be traced, "accept" becomes "for a person".
- **The vocabulary is closed.** Every record is checked against the schema. A value outside the vocabulary goes back to the model with the reason.
- **Budgets are counted in code.** When the searches or page reads run out, the model has to submit.
- **Pages are data.** Page text reaches the model only as a tool answer, never as an instruction.
- **Business data only.** Scout records the channels a business publishes for customers, never private addresses or personal numbers.
- **Draft listings hold facts and links.** No product descriptions and no photographs: both belong to the shop.
- **The screen is local.** It listens on 127.0.0.1, refuses requests from other websites, and runs one search at a time.

## Private data

Three files describe real shops that have not agreed to be listed: the shop registry, the seeds, and the hand-judged ground truth. They are not in this repository, and git ignores them. See [data/README.md](data/README.md).

Everything in [scout/web/sample-run.json](scout/web/sample-run.json) and in the tests is invented. The shops don't exist, and the `.example` domains lead nowhere.

## Hackathon checklist

Submissions close **30 October 2026, 10:00 Pacific**.

| Requirement | State |
|---|---|
| Runs on Nebius Token Factory | Built, not yet run live |
| Uses an NVIDIA open model | Nemotron is the default model |
| Public repository | This one |
| Open-source licence | **Missing.** To be chosen before submission |
| Working demo URL | To do |
| Video under 3 minutes, on YouTube | To do |
| Best Use of Tavily, a separate prize | Tavily does search, and Extract as the fallback reader |

## Open tasks

- [ ] Run `check` with real keys. Fix whatever the live Nemotron and Tavily answers show.
- [ ] Run `verify --limit 6`, then the full set. Note the score, for example "agreed with a person on X of 29".
- [ ] Tune the prompt and the budgets on the misses.
- [ ] Run `probe` to decide whether a product search across shops is possible without copying any catalogue.
- [ ] Add the Spectral and Karla font files to `scout/web/fonts/`. The screen loads no font from a third party and falls back to Georgia and Helvetica until then.
- [ ] Choose a licence.
- [ ] Put up a demo URL.
- [ ] Record the video. Show only invented shops or shops that have agreed.
- [ ] Next: an occasion concierge for shoppers ("I'm invited to a mehndi. What do I wear, and where in Berlin?"), once the first shops have agreed.

## Working together

- Work on a branch and open a pull request into `main`.
- Run `python3 scout/test_offline.py` before you push.
- Never commit `scout/.env`, `scout/runs/` or anything in `data/` except its README. `.gitignore` covers all three, so `git add -f` is the only way to get them in. Don't use it for these.

## About Culturalmaxxing

Culturalmaxxing Berlin is a map of the city's cultural fashion shops, for the people who wear these clothes and for everyone curious about them. It sends visitors to the shop, in person or to its own website. It sells nothing itself.
