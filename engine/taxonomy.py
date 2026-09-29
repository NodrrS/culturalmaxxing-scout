"""Controlled vocabulary and the rules classifier.

This file is the single source of truth for tags. Agent 3 may only emit values
listed here. Anything it believes is missing becomes a *proposal* in the review
queue; a human adds it here (and to the database enum) or rejects it.

CULTURES mirrors the `culture_tag` enum in the app's database.
OCCASIONS and STYLES split the old `occasion_tag` enum, which mixed real
occasions (wedding) with styles (traditional) and categories (accessories).
"""
from __future__ import annotations

import re

CULTURES = ["african", "central_asian", "south_asian", "middle_eastern", "east_asian",
            "balkan", "latin_american", "modest", "fusion"]

CATEGORIES = ["dress", "kurta", "kurta_set", "salwar_suit", "sharara_suit", "palazzo_suit",
              "lehenga_choli", "saree", "blouse", "sherwani", "nehru_jacket", "abaya", "kaftan",
              "kimono", "menswear_suit", "jacket", "coat", "shirt", "top", "trousers", "skirt", "scarf_headwrap",
              "jewellery", "bag", "shoes", "accessory", "home", "other"]

AUDIENCES = ["women", "men", "girls", "boys", "kids", "unisex"]

OCCASIONS = ["wedding", "engagement", "eid", "nowruz", "navratri", "diwali", "raksha_bandhan",
             "festive", "everyday", "office", "summer", "gift"]

STYLES = ["traditional", "modest", "colorful", "streetwear", "made_to_measure"]

# Each craft term should eventually have a sourced, owner-reviewed entry in the
# cultural_context table. Terms without one render the "in review" block.
CRAFT_TERMS = ["adras", "ikat", "jamdani", "chikankari", "bandhani", "ajrakh", "wax_print",
               "adire", "kente", "suzani", "kilim", "zari", "mirror_work", "dori_work",
               "sequin_work", "brocade", "jacquard", "block_print", "handloom", "hand_embroidery",
               "kantha", "shibori", "batik", "quilting"]

PRICE_BANDS = [("budget", 0, 50), ("mid", 50, 150), ("premium", 150, None)]

TRADITIONAL_CATEGORIES = {"kurta", "kurta_set", "salwar_suit", "sharara_suit", "palazzo_suit",
                          "lehenga_choli", "saree", "blouse", "sherwani", "nehru_jacket",
                          "abaya", "kaftan", "kimono"}


def price_band(price: float | None) -> str | None:
    if price is None:
        return None
    for name, lo, hi in PRICE_BANDS:
        if price >= lo and (hi is None or price < hi):
            return name
    return None


# ---- rules -----------------------------------------------------------------
# Ordered: the first matching category rule wins, so specific patterns come first.
CATEGORY_RULES: list[tuple[str, str]] = [
    (r"sherwani", "sherwani"),
    (r"sharara", "sharara_suit"),
    (r"palazzo|plazzo", "palazzo_suit"),
    (r"lehenga|lehnga|chaniya choli", "lehenga_choli"),
    (r"saree blouse|stitched blouse|\bblouse\b(?!.*saree)", "blouse"),
    (r"\bsaree\b|\bsari\b", "saree"),
    (r"pathani", "kurta_set"),
    (r"kurta.*(pyjama|pajama|churidar|trouser|pants?\b|pent\b|salwar|\bset\b)", "kurta_set"),
    (r"salwar|kameez|\bsuit\b", "salwar_suit"),
    (r"nehru jacket", "nehru_jacket"),
    (r"\bkurti\b|\bkurta\b", "kurta"),
    (r"\babaya\b|\bjilbab\b", "abaya"),
    (r"kaftan|caftan|takchita|jellaba|djellaba", "kaftan"),
    (r"kimono|yukata|haori|happi", "kimono"),
    (r"\bobi\b|obijime|obiage|uchiwa|sensu|tabisocken|socken|\bsocks\b|haarspange|haarnadel|kanzashi|hairpin|anhänger|\bstrap\b|charm", "accessory"),
    (r"geldbörse|portemonnaie|\bpurse\b|\bpouch\b|\bwallet\b|furoshiki", "bag"),
    (r"hijab|khimar|niqab|kopftuch|\bshayla\b|\bturban\b|underscarf|untertuch", "scarf_headwrap"),
    (r"bangle|earring|necklace|jhumk|maang ?tikka|anklet|payal|waist ?chain|\bring\b|jewell?ery|choker|\bnath\b|bracelet|haath ?phool", "jewellery"),
    (r"rakhi", "accessory"),
    (r"dupatta|\bstole\b|scarf|hijab|head ?wrap", "scarf_headwrap"),
    (r"\bbag\b|potli|clutch|tasche|\btote\b", "bag"),
    (r"cushion|decor|diya|toran|kissen|\btea\b|\btee\b|teeschale|teekanne|matcha|\bcup\b|becher", "home"),
    (r"sandal|slipper|\bboots?\b|\bschuhe?\b|\bgeta\b|\bzori\b|\btabi\b|sneaker", "shoes"),
    (r"anzug|anzüge|smoking|tuxedo|2-teiler|3-teiler", "menswear_suit"),
    (r"\bdress\b|kleid\b|kleider\b|\bgown\b|robe de", "dress"),
    (r"\bcoat\b|\bmantel\b|trenchcoat", "coat"),
    (r"jacket|\bjacke\b|blazer|\bweste\b|\bvest\b", "jacket"),
    (r"trousers|\bpants\b|\bhose\b|culotte|jumpsuit|overall", "trousers"),
    (r"\bskirt\b|\brock\b", "skirt"),
    (r"\bshirt\b|\bhemd\b|\bbluse\b", "shirt"),
    (r"\btop\b|tunic|tunika|jumper|sweater|pullover|cardigan|strick", "top"),
    (r"\bfan\b|fächer|umbrella|schirm|brooch|brosche|belt|gürtel|\bpin\b", "accessory"),
]

# Used only when no title rule matched.
PRODUCT_TYPE_FALLBACK = {
    "suits": "salwar_suit", "kurta": "kurta", "indian jewellery": "jewellery",
    "modern jewellery": "jewellery", "waist chain": "jewellery", "rakhi": "accessory",
    "saree with unstitched blouse": "saree", "navaratri collection": "lehenga_choli",
}

OCCASION_RULES = [
    (r"navr?a?atri|garba|dandiya|chaniya", "navratri"),
    (r"rakhi", "raksha_bandhan"),
    (r"rakhi", "gift"),
    (r"festive|festival", "festive"),
    (r"wedding|bridal|dulhan|shaadi|braut|hochzeit", "wedding"),
    (r"ballkleid|abendkleid|abiball|evening|gala", "festive"),
    (r"engagement|nisan|nişan", "engagement"),
    (r"\bdiwali\b", "diwali"),
    (r"\beid\b|bayram", "eid"),
    (r"nowruz|nouruz|navruz", "nowruz"),
    (r"\boffice\b", "office"),
    (r"casual", "everyday"),
]

CRAFT_RULES = [
    (r"chikankari|chikan", "chikankari"), (r"bandhani|bandhej", "bandhani"),
    (r"ajrakh", "ajrakh"), (r"jamdani", "jamdani"), (r"\bikat\b", "ikat"),
    (r"\badras\b", "adras"), (r"wax ?print|ankara", "wax_print"), (r"brocade", "brocade"),
    (r"jacquard", "jacquard"), (r"\bzari\b", "zari"), (r"mirr[oi]r work", "mirror_work"),
    (r"\bdori\b", "dori_work"), (r"sequin", "sequin_work"), (r"block ?print", "block_print"),
    (r"handloom", "handloom"), (r"hand[- ]embroider", "hand_embroidery"),
    (r"suzani", "suzani"), (r"kilim|kelim", "kilim"), (r"kente", "kente"),
    (r"kantha", "kantha"), (r"shibori", "shibori"), (r"batik", "batik"), (r"quilt", "quilting"),
    (r"handbestickt|hand embroidered|hand-embroidered", "hand_embroidery"),
]

# Words that suggest a tag we do not have yet. Rules never invent tags; they
# only flag the product so Agent 3 or a human can propose one.
UNKNOWN_SIGNALS = [(r"\bonam\b", "occasion", "onam"), (r"farshi", "category", "farshi_salwar"),
                   (r"hanbok", "category", "hanbok"), (r"qipao|cheongsam", "category", "qipao"),
                   (r"hanfu", "category", "hanfu"), (r"samue", "category", "samue"),
                   (r"jinbei", "category", "jinbei"), (r"tenugui", "category", "tenugui")]


def _text(product: dict) -> str:
    parts = [product.get("title_en") or product.get("title", ""), product.get("product_type_raw", "")]
    parts += product.get("tags_raw", [])
    return " ".join(p for p in parts if p).lower()


def classify_rules(product: dict, shop: dict) -> dict:
    """Deterministic first pass. Returns a classification with a confidence.

    Only 'high' confidence results skip Agent 3.
    """
    text = _text(product)
    title = (product.get("title_en") or product.get("title", "")).lower()

    category, cat_source = None, None
    for pattern, value in CATEGORY_RULES:
        if re.search(pattern, title):
            category, cat_source = value, "title"
            break
    if category is None:
        category = PRODUCT_TYPE_FALLBACK.get(product.get("product_type_raw", "").strip().lower())
        cat_source = "product_type" if category else None

    tags = [t.lower() for t in product.get("tags_raw", [])]
    audience = None
    if re.search(r"\bboys?'?s?\b", text):
        audience = "boys"
    elif re.search(r"\bgirls?'?s?\b", text):
        audience = "girls"
    elif re.search(r"\bkids?\b|\bkinder\b|children", text):
        audience = "kids"
    elif re.search(r"\bmen'?s?\b|\bmens\b|for men|sherwani|pathani|\bherren\b|männer", text) or "men" in tags:
        audience = "men"
    elif re.search(r"\bwom[ae]n'?s?\b|ladies|\bdamen\b|\bfrauen\b", text) or "women" in tags:
        audience = "women"
    elif category in {"salwar_suit", "sharara_suit", "palazzo_suit", "lehenga_choli", "saree", "blouse", "abaya", "skirt"}:
        audience = "women"

    occasions = []
    for pattern, value in OCCASION_RULES:
        if re.search(pattern, text) and value not in occasions:
            occasions.append(value)

    styles = ["traditional"] if category in TRADITIONAL_CATEGORIES else []
    if shop.get("default_culture") == "modest" and category not in (None, "home", "jewellery", "shoes"):
        styles.append("modest")

    craft = []
    for pattern, value in CRAFT_RULES:
        if re.search(pattern, text) and value not in craft:
            craft.append(value)

    proposals = [{"field": f, "term": term, "reason": f"keyword '{term}' has no tag yet"}
                 for pattern, f, term in UNKNOWN_SIGNALS if re.search(pattern, text)]

    culture = shop.get("default_culture")
    if cat_source == "title" and audience and culture:
        confidence = "high"
    elif category and culture:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "source_id": product["source_id"],
        "culture": culture,
        "category": category,
        "audience": audience,
        "occasions": occasions,
        "styles": styles,
        "craft_terms": craft,
        "price_band": price_band(product.get("price_min")),
        "proposals": proposals,
        "confidence": confidence,
        "needs_review": confidence != "high" or bool(proposals),
        "classified_by": "rules",
    }
