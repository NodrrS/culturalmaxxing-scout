"""Shared Claude plumbing for the three agents.

- One model, claude-opus-5. Cost is tuned per agent with `effort`, not by
  switching models: discovery and extraction run at "medium", taxonomy at "low".
- Server-side refusal fallback is on (`fallbacks="default"`), so a declined
  request is retried on Anthropic's recommended fallback model instead of failing.
- Agents that browse finish by calling a strict `submit` tool. That gives a
  schema-valid result without mixing web tools and response formats.
- `pause_turn` (a long server-side web turn) is resumed by re-sending the
  conversation, as the API expects.

Credentials: ANTHROPIC_API_KEY, or a profile from `ant auth login`.
"""
from __future__ import annotations

import json

MODEL = "claude-opus-5"
FALLBACK_BETA = "server-side-fallback-2026-07-01"


def web_search_tool(max_uses: int = 8) -> dict:
    return {
        "type": "web_search_20260209",
        "name": "web_search",
        "max_uses": max_uses,
        "user_location": {"type": "approximate", "city": "Berlin", "country": "DE",
                          "timezone": "Europe/Berlin"},
    }


def web_fetch_tool(max_uses: int = 10, allowed_domains: list[str] | None = None) -> dict:
    tool = {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": max_uses,
            "max_content_tokens": 20000}
    if allowed_domains:
        tool["allowed_domains"] = allowed_domains
    return tool


class AgentRefused(RuntimeError):
    pass


def _client():
    import anthropic  # imported lazily so the no-model path needs no SDK
    return anthropic.Anthropic()


def run_browsing_agent(*, system: str, prompt: str, server_tools: list[dict],
                       submit_name: str, submit_description: str, submit_schema: dict,
                       effort: str = "medium", max_rounds: int = 12) -> dict:
    """Run a web-browsing agent until it calls the submit tool; return its input."""
    client = _client()
    submit = {"name": submit_name, "description": submit_description,
              "strict": True, "input_schema": submit_schema}
    tools = server_tools + [submit]
    messages: list = [{"role": "user", "content": prompt}]

    for _ in range(max_rounds):
        resp = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=system,
            tools=tools,
            messages=messages,
            output_config={"effort": effort},
            betas=[FALLBACK_BETA],
            fallbacks="default",
        )
        if resp.stop_reason == "refusal":
            raise AgentRefused(getattr(resp, "stop_details", None))
        messages.append({"role": "assistant", "content": resp.content})

        for block in resp.content:
            if block.type == "tool_use" and block.name == submit_name:
                data = block.input
                return json.loads(data) if isinstance(data, str) else data

        if resp.stop_reason == "pause_turn":
            continue  # resume the server-side turn; no extra user message
        # The model stopped without submitting (end_turn or max_tokens): ask once more.
        messages.append({"role": "user",
                         "content": f"Call {submit_name} now with what you have. "
                                    "Mark anything you could not confirm as unconfirmed."})
    raise RuntimeError(f"agent did not call {submit_name} within {max_rounds} rounds")


def run_structured(*, system: str, prompt: str, schema: dict, effort: str = "low") -> dict:
    """Single call with a JSON-schema response format (no tools)."""
    client = _client()
    resp = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        betas=[FALLBACK_BETA],
        fallbacks="default",
    )
    if resp.stop_reason == "refusal":
        raise AgentRefused(getattr(resp, "stop_details", None))
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("response truncated; send a smaller batch")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


def nullable(schema: dict) -> dict:
    return {"anyOf": [schema, {"type": "null"}]}


def obj(properties: dict) -> dict:
    """Strict object schema: every property required, nothing extra."""
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}
