"""LLM client with two real backends and an honest failure mode.

- anthropic          : real Claude calls, structured output forced via tool-use.
- openai_compatible  : any OpenAI-compatible endpoint (Azure OpenAI, OpenAI,
                       vLLM, Ollama, …) using JSON mode.

The ACTIVE provider / model / endpoint is admin-configurable at runtime (passed
in as `llm` from config_store). API keys are NEVER in that config — they always
come from the environment (settings). If no backend is reachable we raise
LLMUnavailable; callers route the chart to the manual queue rather than
fabricating codes. There is no synthetic "model."
"""
from __future__ import annotations

import json
from typing import Any

import httpx

from ..config import settings


class LLMUnavailable(RuntimeError):
    pass


def effective_llm(llm: dict | None = None) -> dict:
    """Merge the admin config-store 'llm' dict with env defaults + secrets.
    Returns a normalized config. Secrets always come from the environment."""
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


def _anthropic_json(system, user, schema, model, temperature, e) -> dict[str, Any]:
    import anthropic

    client = anthropic.Anthropic(api_key=e["anthropic_api_key"])
    tool = {
        "name": "emit_result",
        "description": "Return the structured coding result. Every field is required.",
        "input_schema": schema,
    }
    resp = client.messages.create(
        model=model,
        max_tokens=e["max_tokens"],
        temperature=temperature,
        system=system,
        tools=[tool],
        tool_choice={"type": "tool", "name": "emit_result"},
        messages=[{"role": "user", "content": user}],
    )
    usage = {"in": getattr(resp.usage, "input_tokens", 0), "out": getattr(resp.usage, "output_tokens", 0)}
    for block in resp.content:
        if block.type == "tool_use" and block.name == "emit_result":
            return block.input, usage
    raise LLMUnavailable("Anthropic returned no tool_use block")


def _openai_json(system, user, schema, model, temperature, e) -> dict[str, Any]:
    # OpenAI-compatible chat completions with JSON object response format.
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
    headers = {}
    if e["openai_api_key"]:
        headers["Authorization"] = f"Bearer {e['openai_api_key']}"
    url = e["base_url"] + "/chat/completions"
    with httpx.Client(timeout=120) as hc:
        r = hc.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
    u = data.get("usage", {}) or {}
    usage = {"in": u.get("prompt_tokens", 0), "out": u.get("completion_tokens", 0)}
    content = data["choices"][0]["message"]["content"]
    return json.loads(content), usage


EXTRACT_SYSTEM = """You are the document-conditioning OCR step of a medical-coding pipeline.
Transcribe the attached clinical document into plain text, faithfully and completely.
RULES:
- Transcribe VERBATIM. Never paraphrase, summarize, or invent content that is not visible.
- Preserve the document's section structure (one section per line, e.g. 'EXAM:', 'FINDINGS:').
- Mark anything you cannot read as [illegible]. Do not guess.
- Output ONLY the transcription — no commentary."""


def extract_document_text(
    data: bytes, media_type: str, *, llm: dict | None = None, usage_sink: list | None = None
) -> str:
    """Vision OCR for scanned charts (PDF / PNG / JPEG): returns the verbatim plain-text
    transcription that then enters the normal pipeline at Stage 1 (conditioning).
    Anthropic provider only (document/image blocks); honest LLMUnavailable otherwise."""
    import base64

    e = effective_llm(llm)
    if not llm_available(llm):
        raise LLMUnavailable("No LLM backend configured for document extraction.")
    if e["provider"] != "anthropic":
        raise LLMUnavailable(
            "Scanned-document extraction currently requires the Anthropic provider "
            "(vision document blocks). Switch the reasoning model in Admin, or ingest text."
        )

    import anthropic

    block_type = "document" if media_type == "application/pdf" else "image"
    client = anthropic.Anthropic(api_key=e["anthropic_api_key"])
    resp = client.messages.create(
        model=e["model_default"],
        max_tokens=e["max_tokens"],
        temperature=0.0,
        system=EXTRACT_SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {"type": block_type,
                 "source": {"type": "base64", "media_type": media_type,
                            "data": base64.standard_b64encode(data).decode()}},
                {"type": "text", "text": "Transcribe this clinical document."},
            ],
        }],
    )
    if usage_sink is not None:
        usage_sink.append({"in": getattr(resp.usage, "input_tokens", 0),
                           "out": getattr(resp.usage, "output_tokens", 0)})
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    if len(text) < 20:
        raise LLMUnavailable("Document extraction produced no usable text.")
    return text


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
) -> list[dict[str, Any]]:
    """Return `samples` structured results. `llm` is the runtime config-store
    config; secrets are pulled from the environment regardless. If `usage_sink`
    is provided, each successful call appends its real token usage to it."""
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
                result, usage = _anthropic_json(system, user, schema, model, temperature, e)
            else:
                result, usage = _openai_json(system, user, schema, model, temperature, e)
            out.append(result)
            if usage_sink is not None:
                usage_sink.append(usage)
        except Exception as exc:  # transient network / parse / rate-limit on a single sample
            errors.append(f"{type(exc).__name__}: {exc}")
    # Self-consistency tolerates partial failures: only fail if EVERY sample failed.
    if not out:
        raise LLMUnavailable(f"{e['provider']} call failed for all {samples} sample(s): {errors}")
    return out
