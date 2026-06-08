"""LLM client with two real backends and an honest failure mode.

- anthropic : real Claude calls, structured output forced via tool-use.
- local     : any OpenAI-compatible endpoint (e.g. Ollama) using JSON mode.

If no backend is reachable we raise LLMUnavailable; callers route the chart to
the manual queue rather than fabricating codes. There is no synthetic "model."
"""
from __future__ import annotations

import json
from typing import Any

import httpx

from ..config import settings


class LLMUnavailable(RuntimeError):
    pass


def model_version() -> str:
    if settings.llm_mode == "anthropic":
        return f"anthropic/{settings.ace_model_default}"
    return f"local/{settings.local_llm_model}"


def _anthropic_json(
    system: str, user: str, schema: dict[str, Any], model: str, temperature: float
) -> dict[str, Any]:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    tool = {
        "name": "emit_result",
        "description": "Return the structured coding result. Every field is required.",
        "input_schema": schema,
    }
    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=temperature,
        system=system,
        tools=[tool],
        tool_choice={"type": "tool", "name": "emit_result"},
        messages=[{"role": "user", "content": user}],
    )
    for block in resp.content:
        if block.type == "tool_use" and block.name == "emit_result":
            return block.input  # already a dict matching the schema
    raise LLMUnavailable("Anthropic returned no tool_use block")


def _local_json(
    system: str, user: str, schema: dict[str, Any], model: str, temperature: float
) -> dict[str, Any]:
    # OpenAI-compatible chat completions with JSON object response format.
    payload = {
        "model": model or settings.local_llm_model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system + "\n\nReturn ONLY a JSON object matching this schema:\n" + json.dumps(schema)},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
        "stream": False,
    }
    url = settings.local_llm_base_url.rstrip("/") + "/chat/completions"
    with httpx.Client(timeout=120) as hc:
        r = hc.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
    content = data["choices"][0]["message"]["content"]
    return json.loads(content)


def complete_json(
    system: str,
    user: str,
    schema: dict[str, Any],
    *,
    hard: bool = False,
    temperature: float = 0.0,
    samples: int = 1,
) -> list[dict[str, Any]]:
    """Return `samples` structured results. Used at temperature>0 for self-consistency."""
    if not settings.llm_available:
        raise LLMUnavailable(
            "No LLM backend configured. Set ANTHROPIC_API_KEY (LLM_MODE=anthropic) "
            "or a reachable LOCAL_LLM_BASE_URL (LLM_MODE=local)."
        )

    model = settings.ace_model_hard if hard else settings.ace_model_default
    out: list[dict[str, Any]] = []
    for _ in range(max(1, samples)):
        try:
            if settings.llm_mode == "anthropic":
                out.append(_anthropic_json(system, user, schema, model, temperature))
            else:
                out.append(_local_json(system, user, schema, settings.local_llm_model, temperature))
        except LLMUnavailable:
            raise
        except Exception as exc:  # network / parse / auth
            raise LLMUnavailable(f"{settings.llm_mode} call failed: {exc}") from exc
    return out
