"""Provider-agnostic LLM client with an honest failure mode (shared core).

- anthropic          : real Claude calls, structured output forced via tool-use.
- openai_compatible  : any OpenAI-compatible endpoint (Azure OpenAI, OpenAI,
                       vLLM, Ollama, …) using JSON mode.

The active provider / model / endpoint is supplied at call time as the `llm` dict
(from each app's runtime config). API keys are NEVER in that config — they always
come from the environment (settings). If no backend is reachable we raise
LLMUnavailable; callers route the work item to a human rather than fabricating an
artifact. There is no synthetic "model."

This is the same client ACE proved in production; it is provider/domain-agnostic so
P2R reuses it unchanged for policy extraction and rule reasoning.
"""
from __future__ import annotations

import json
from typing import Any

import httpx

from .settings import settings


class LLMUnavailable(RuntimeError):
    pass


def effective_llm(llm: dict | None = None) -> dict:
    """Merge the supplied `llm` dict with env defaults + secrets. Returns a
    normalized config. Secrets always come from the environment."""
    llm = llm or {}
    provider = llm.get("provider") or ("anthropic" if settings.llm_mode == "anthropic" else "openai_compatible")
    return {
        "provider": provider,
        "model_default": llm.get("model_default") or settings.ace_model_default,
        "model_hard": llm.get("model_hard") or settings.ace_model_hard,
        "base_url": (llm.get("base_url") or settings.local_llm_base_url or "").rstrip("/"),
        "max_tokens": int(llm.get("max_tokens") or 4096),
        # secrets — env only
        "anthropic_api_key": settings.anthropic_api_key,
        "openai_api_key": settings.openai_api_key,
    }


def llm_available(llm: dict | None = None) -> bool:
    e = effective_llm(llm)
    if e["provider"] == "anthropic":
        return bool(e["anthropic_api_key"])
    return bool(e["base_url"])  # OpenAI-compatible: needs an endpoint (key optional, e.g. Ollama)


def model_version(llm: dict | None = None) -> str:
    e = effective_llm(llm)
    tag = "anthropic" if e["provider"] == "anthropic" else "openai"
    return f"{tag}/{e['model_default']}"


def _anthropic_json(system, user, schema, model, temperature, e, cache=False) -> dict[str, Any]:
    import anthropic

    client = anthropic.Anthropic(api_key=e["anthropic_api_key"])
    tool = {
        "name": "emit_result",
        "description": "Return the structured result. Every field is required.",
        "input_schema": schema,
    }
    system_param = system
    if cache:
        # Cache the static prefix (tool schema + system prompt) — it repeats on every
        # call. The dynamic user message is not cached. Blocks under the provider
        # minimum are simply not cached (no error).
        tool["cache_control"] = {"type": "ephemeral"}
        system_param = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
    resp = client.messages.create(
        model=model,
        max_tokens=e["max_tokens"],
        temperature=temperature,
        system=system_param,
        tools=[tool],
        tool_choice={"type": "tool", "name": "emit_result"},
        messages=[{"role": "user", "content": user}],
    )
    u = resp.usage
    usage = {
        "in": getattr(u, "input_tokens", 0), "out": getattr(u, "output_tokens", 0),
        "cache_read": getattr(u, "cache_read_input_tokens", 0) or 0,
        "cache_write": getattr(u, "cache_creation_input_tokens", 0) or 0,
    }
    for block in resp.content:
        if block.type == "tool_use" and block.name == "emit_result":
            return block.input, usage
    raise LLMUnavailable("Anthropic returned no tool_use block")


def _openai_json(system, user, schema, model, temperature, e) -> dict[str, Any]:
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": e["max_tokens"],
        "messages": [
            {"role": "system", "content": system + "\n\nReturn ONLY a JSON object matching this schema:\n" + json.dumps(schema)},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
        "stream": False,
    }
    headers = {"api-key": e["openai_api_key"]} if e["openai_api_key"] else {}
    base = e["base_url"]
    url = base if "chat/completions" in base else base + "/chat/completions"
    with httpx.Client(timeout=120) as hc:
        r = hc.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
    u = data.get("usage", {}) or {}
    usage = {"in": u.get("prompt_tokens", 0), "out": u.get("completion_tokens", 0)}
    content = data["choices"][0]["message"]["content"]
    return json.loads(content), usage


def complete_json(
    system: str,
    user: str,
    schema: dict[str, Any],
    *,
    hard: bool = False,
    temperature: float = 0.0,
    samples: int = 1,
    llm: dict | None = None,
    usage_sink: list | None = None,
    cache: bool = False,
) -> list[dict[str, Any]]:
    """Return `samples` structured results. Secrets are pulled from the environment.
    If `usage_sink` is provided, each successful call appends its real token usage."""
    e = effective_llm(llm)
    if not llm_available(llm):
        raise LLMUnavailable(
            "No LLM backend configured. For the 'anthropic' provider set ANTHROPIC_API_KEY; "
            "for 'openai_compatible' set the endpoint (and OPENAI_API_KEY if the endpoint needs it)."
        )

    model = e["model_hard"] if hard else e["model_default"]
    out: list[dict[str, Any]] = []
    errors: list[str] = []
    for _ in range(max(1, samples)):
        try:
            if e["provider"] == "anthropic":
                result, usage = _anthropic_json(system, user, schema, model, temperature, e, cache=cache)
            else:
                result, usage = _openai_json(system, user, schema, model, temperature, e)
            out.append(result)
            if usage_sink is not None:
                usage_sink.append(usage)
        except Exception as exc:  # transient network / parse / rate-limit on a single sample
            errors.append(f"{type(exc).__name__}: {exc}")
    if not out:
        raise LLMUnavailable(f"{e['provider']} call failed for all {samples} sample(s): {errors}")
    return out
