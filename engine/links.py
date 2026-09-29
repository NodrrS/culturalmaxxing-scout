"""Outbound links with attribution.

A link can only *earn commission* if the shop recognises it. We cannot make a
shop's checkout record anything on our own. So each shop has an attribution
mode, agreed with the shop:

  utm              Default, no agreement needed. UTM parameters show up in the
                   shop's own analytics (Shopify: Analytics > Sessions by UTM),
                   so they can see the traffic we send. No commission.
  shopify_discount The shop creates a discount code for us. Shopify's shareable
                   link /discount/CODE?redirect=/products/... applies it in the
                   cart, and every order using the code is ours. Simplest real
                   attribution for a Shopify shop with no affiliate app.
  param            The shop runs an affiliate app or network that reads a query
                   parameter (e.g. ?ref=cmx). We append it.

Our own record is the click: log an intent event ("product_click") before
redirecting. That is the number the shop is shown each month.

Label outbound commission links as advertising in the UI (German law, UWG §5a).
UTM parameters set no cookies on our side, so the no-cookie-banner goal holds.
"""
from __future__ import annotations

from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit


def _with_params(url: str, params: dict) -> str:
    p = urlsplit(url)
    q = dict(parse_qsl(p.query))
    q.update(params)
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(q), p.fragment))


def outbound_url(product_url: str, shop: dict, product_ref: str) -> str:
    utm = {"utm_source": "culturalmaxxing", "utm_medium": "referral",
           "utm_campaign": shop["slug"], "utm_content": product_ref}
    attr = shop.get("attribution") or {"mode": "utm"}
    mode = attr.get("mode", "utm")
    if mode == "shopify_discount" and attr.get("code"):
        p = urlsplit(product_url)
        return (f"{p.scheme}://{p.netloc}/discount/{quote(attr['code'])}"
                f"?redirect={quote(p.path)}&{urlencode(utm)}")
    if mode == "param" and attr.get("name"):
        utm[attr["name"]] = attr.get("value", "culturalmaxxing")
    return _with_params(product_url, utm)
