"""Nebius Token Factory and Tavily over plain HTTPS.

Standard library only, like the engine's feed path, so there is nothing to
install on hackathon day.

- Nebius Token Factory speaks the OpenAI chat-completions protocol. The default
  model is an NVIDIA Nemotron, because the hackathon requires an NVIDIA open model.
- Tavily does the web search. Reading a page goes through the engine's own
  polite fetcher first (see agent.py); Tavily Extract is the fallback for pages
  that need rendering.

Keys come from the environment or from scout/.env, which is never committed:
  NEBIUS_API_KEY, TAVILY_API_KEY
Optional:
  NEBIUS_BASE_URL   default https://api.tokenfactory.nebius.com/v1/
  NEBIUS_MODEL      default nvidia/nemotron-3-super-120b-a12b
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DEFAULT_BASE = "https://api.tokenfactory.nebius.com/v1/"
US_BASE = "https://api.tokenfactory.us-central1.nebius.com/v1/"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b"
TAVILY = "https://api.tavily.com"
UA = "culturalmaxxing-scout/0.1"

# Marketplaces are never the shop itself. Social pages stay in: many small
# shops have an Instagram page and no website.
MARKETPLACES = ["amazon.de", "amazon.com", "zalando.de", "etsy.com", "ebay.de", "kleinanzeigen.de",
                "aboutyou.de", "otto.de", "temu.com", "shein.com", "aliexpress.com",
                "pinterest.com", "pinterest.de"]

# Running totals for the cost line at the end of a run.
usage = {"tavily_calls": 0, "tavily_credits": 0, "nebius_calls": 0,
         "prompt_tokens": 0, "completion_tokens": 0}


class MissingKey(RuntimeError):
    pass


class ApiError(RuntimeError):
    def __init__(self, service: str, status: int, body: str):
        self.service, self.status, self.body = service, status, body
        super().__init__(f"{service} answered {status}: {body[:300]}")


def load_env(path: Path | None = None) -> None:
    """Read KEY=VALUE lines from scout/.env. Variables already set win."""
    path = path or HERE / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip('"').strip("'")
        if key and value and not os.environ.get(key):
            os.environ[key] = value


def _key(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise MissingKey(f"{name} is not set. Put it in scout/.env (see .env.example).")
    return value


def _http(method: str, url: str, key: str, payload: dict | None, timeout: float) -> tuple[int, str]:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


transport = _http   # the offline tests replace this


def _call(service: str, method: str, url: str, key: str, payload: dict | None = None,
          timeout: float = 120, retries: int = 2) -> dict:
    for attempt in range(retries + 1):
        status, body = transport(method, url, key, payload, timeout)
        if status in (429, 500, 502, 503, 504) and attempt < retries:
            time.sleep(2 * (attempt + 1))
            continue
        if status != 200:
            raise ApiError(service, status, body)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            raise ApiError(service, status, "answer was not JSON: " + body[:200]) from None
    raise ApiError(service, 0, "no answer")


# ---- Nebius Token Factory ------------------------------------------------------

def nebius_base() -> str:
    base = os.environ.get("NEBIUS_BASE_URL", "").strip() or DEFAULT_BASE
    return base if base.endswith("/") else base + "/"


def nebius_model() -> str:
    return os.environ.get("NEBIUS_MODEL", "").strip() or DEFAULT_MODEL


def list_models(base: str | None = None) -> list[str]:
    data = _call("nebius", "GET", (base or nebius_base()) + "models", _key("NEBIUS_API_KEY"), timeout=30)
    return sorted(m["id"] for m in data.get("data", []) if m.get("id"))


def chat(messages: list[dict], *, tools: list[dict] | None = None, tool_choice=None,
         response_format: dict | None = None, model: str | None = None,
         max_tokens: int = 4000, temperature: float = 0.2) -> dict:
    payload: dict = {"model": model or nebius_model(), "messages": messages,
                     "max_tokens": max_tokens, "temperature": temperature}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice or "auto"
    if response_format:
        payload["response_format"] = response_format
    data = _call("nebius", "POST", nebius_base() + "chat/completions", _key("NEBIUS_API_KEY"),
                 payload, timeout=180)
    used = data.get("usage") or {}
    usage["nebius_calls"] += 1
    usage["prompt_tokens"] += used.get("prompt_tokens") or 0
    usage["completion_tokens"] += used.get("completion_tokens") or 0
    return data


_THINK = re.compile(r"<think>.*?</think>", re.S)


def visible(content: str | None) -> str:
    """The answer without the model's reasoning block."""
    return _THINK.sub("", content or "").strip()


def parse_json(content: str | None):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", visible(content))
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


def validate(value, schema: dict, path: str = "$") -> list[str]:
    """Check a value against the subset of JSON Schema the engine uses.

    The server is asked to follow the schema, but the closed vocabulary must not
    depend on that alone, so every answer is checked again here.
    """
    if "anyOf" in schema:
        if any(not validate(value, s, path) for s in schema["anyOf"]):
            return []
        return [f"{path}: matches none of the allowed forms"]
    kind = schema.get("type")
    if kind == "null":
        return [] if value is None else [f"{path}: must be null"]
    if kind == "object":
        if not isinstance(value, dict):
            return [f"{path}: must be an object"]
        props = schema.get("properties", {})
        errors = [f"{path}.{k}: missing" for k in schema.get("required", []) if k not in value]
        for k, v in value.items():
            if k in props:
                errors += validate(v, props[k], f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}.{k}: not an allowed field")
        return errors
    if kind == "array":
        if not isinstance(value, list):
            return [f"{path}: must be a list"]
        errors = []
        for i, v in enumerate(value):
            errors += validate(v, schema.get("items", {}), f"{path}[{i}]")
        return errors
    if kind == "string" and not isinstance(value, str):
        return [f"{path}: must be a string"]
    if kind == "boolean" and not isinstance(value, bool):
        return [f"{path}: must be true or false"]
    if kind in ("number", "integer") and (isinstance(value, bool) or not isinstance(value, (int, float))):
        return [f"{path}: must be a number"]
    if "enum" in schema and value not in schema["enum"]:
        return [f"{path}: '{value}' is not one of {schema['enum']}"]
    return []


def structured(*, system: str, prompt: str, schema: dict, model: str | None = None,
               max_tokens: int = 4000) -> dict:
    """One call that must return JSON matching `schema`. One repair round if it does not."""
    messages = [
        {"role": "system", "content": system + "\n\nAnswer with JSON only, matching this JSON schema:\n"
                                      + json.dumps(schema, ensure_ascii=False)},
        {"role": "user", "content": prompt},
    ]
    # Nebius documents the first shape; the second is the OpenAI one.
    formats = [{"type": "json_schema", "json_schema": schema},
               {"type": "json_schema", "json_schema": {"name": "result", "schema": schema, "strict": True}}]
    errors: list[str] = []
    for _ in range(2):
        data, refused = None, None
        for fmt in formats:
            try:
                data = chat(messages, response_format=fmt, model=model, max_tokens=max_tokens, temperature=0)
                formats = [fmt]
                break
            except ApiError as e:
                if e.status not in (400, 422):
                    raise
                refused = e
        if data is None:
            raise refused
        content = data["choices"][0]["message"].get("content")
        try:
            result = parse_json(content)
            errors = validate(result, schema)
        except (json.JSONDecodeError, TypeError) as e:
            result, errors = None, [f"not valid JSON: {e}"]
        if not errors:
            return result
        messages += [{"role": "assistant", "content": visible(content)},
                     {"role": "user", "content": "That did not match the schema:\n- "
                                                 + "\n- ".join(errors[:10]) + "\nSend the corrected JSON only."}]
    raise ValueError("model output did not match the schema: " + "; ".join(errors[:5]))


# ---- Tavily --------------------------------------------------------------------

def _tavily(path: str, payload: dict, timeout: float = 60) -> dict:
    payload["include_usage"] = True
    data = _call("tavily", "POST", TAVILY + path, _key("TAVILY_API_KEY"), payload, timeout=timeout)
    usage["tavily_calls"] += 1
    usage["tavily_credits"] += (data.get("usage") or {}).get("credits") or 0
    return data


def search(query: str, *, max_results: int = 6, depth: str = "basic", country: str | None = "germany",
           include_domains: list[str] | None = None, exclude_domains: list[str] | None = None,
           time_range: str | None = None) -> dict:
    payload: dict = {"query": query, "search_depth": depth, "max_results": max_results, "topic": "general"}
    if country:
        payload["country"] = country
    if include_domains:
        payload["include_domains"] = include_domains
    if exclude_domains:
        payload["exclude_domains"] = exclude_domains
    if time_range:
        payload["time_range"] = time_range
    return _tavily("/search", payload)


def extract(urls: list[str], *, depth: str = "basic", fmt: str = "markdown") -> dict:
    return _tavily("/extract", {"urls": urls[:20], "extract_depth": depth, "format": fmt}, timeout=90)


def map_site(url: str, *, limit: int = 30, max_depth: int = 1,
             select_paths: list[str] | None = None) -> dict:
    payload: dict = {"url": url, "limit": limit, "max_depth": max_depth, "allow_external": False}
    if select_paths:
        payload["select_paths"] = select_paths
    return _tavily("/map", payload, timeout=160)


def cost_line() -> str:
    return (f"Tavily: {usage['tavily_calls']} calls, {usage['tavily_credits']} credits · "
            f"Nebius: {usage['nebius_calls']} calls, {usage['prompt_tokens']} tokens in, "
            f"{usage['completion_tokens']} out")
