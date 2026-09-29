# Private data

Git ignores everything in this folder except this file. The files that belong here describe real shops that have not agreed to be listed, so they must never be committed.

| File | What it holds | Used by |
|---|---|---|
| `shops.json` | The registry: shops a person has checked and accepted | `verify`, `probe` |
| `discovery-manual.json` | Candidates a person rejected, each with the reason | `verify` |
| `seeds.json` | Names still to check | `find --seeds` |

Get them from the project owner through a private channel. To keep them somewhere else, point `SCOUT_DATA` at that folder in `scout/.env`.

## Shapes

All values below are invented.

`shops.json`

```json
{"shops": [{"slug": "atelier-beispiel", "name": "Atelier Beispiel", "website": "https://atelier-beispiel.example",
            "platform": "shopify", "default_culture": "central_asian", "crawl": true}]}
```

`discovery-manual.json`

```json
{"rejected": [{"name": "Seidenweg Muster", "site": "https://seidenweg-muster.example", "reason": "based in Bochum"}]}
```

`seeds.json`

```json
{"seeds": [{"name": "Haus Muster", "hint": "festive wear, Neukölln"}]}
```
