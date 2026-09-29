# Engine modules

The parts of the Culturalmaxxing engine that Scout reuses:

| File | What Scout uses it for |
|---|---|
| [fetch.py](fetch.py) | Polite HTTP: robots.txt before every request, spacing between requests, a named User-Agent. Also Shopify and WooCommerce feed reading and platform detection |
| [taxonomy.py](taxonomy.py) | The closed tag vocabulary and the rules classifier |
| [agent2_extraction.py](agent2_extraction.py) | Reading a shop's products from its feed |
| [agent3_taxonomy.py](agent3_taxonomy.py) | Rules first, and the prompt and schema for what the rules can't settle |
| [links.py](links.py) | Outbound links with UTM parameters |
| [llm.py](llm.py) | Strict JSON-schema helpers |

`llm.py` and the agents also hold the engine's original Claude code paths. Scout doesn't call them: its model calls go to Nemotron through [../scout/clients.py](../scout/clients.py).
