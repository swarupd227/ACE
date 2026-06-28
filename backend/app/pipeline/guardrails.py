"""LLM I/O guardrails (E7).

Two deterministic checks wrap the reasoning model:

  * guard_input  — after PII masking, verify no DIRECT identifier slipped through to the model
                   (defense-in-depth). Residuals are re-masked; if policy requires it and a
                   residual still can't be removed, the chart is routed to a human instead.
  * guard_output — the model's text must not echo a direct identifier and must not carry
                   obvious prompt-injection markers; offending content is sanitised + flagged.

Inspectable by design. This is the seam where a managed service (Azure AI Content Safety,
Presidio) plugs in for production — the pipeline contract is unchanged.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import pii

# Obvious prompt-injection / jailbreak markers in model output (defense-in-depth only).
_INJECTION = re.compile(
    r"(?i)\b(ignore (?:all |the )?(?:previous|prior|above) instructions|"
    r"disregard (?:the )?system prompt|reveal your (?:system )?prompt|you are now [a-z])\b")


@dataclass
class GuardResult:
    ok: bool                       # safe to proceed (False = block / route to human)
    text: str                      # possibly sanitised text
    action: str                    # pass | sanitized | block
    findings: list = field(default_factory=list)
    detail: str = ""


def _g(cfg: dict) -> dict:
    return (cfg or {}).get("guardrails", {}) or {}


def enabled(cfg: dict) -> bool:
    return bool(_g(cfg).get("enabled", True))


def guard_input(text: str, cfg: dict) -> GuardResult:
    """Residual-PHI check on the text about to reach the model (after masking)."""
    g = _g(cfg)
    if not enabled(cfg):
        return GuardResult(True, text, "pass")
    residual = pii.scan(text)
    if not residual:
        return GuardResult(True, text, "pass")
    if g.get("redact_input_residuals", True):
        cleaned, masked = pii.redact_residuals(text)
        if g.get("block_on_residual_phi", False) and pii.scan(cleaned):
            return GuardResult(False, cleaned, "block", masked, "residual PHI persisted after re-mask")
        return GuardResult(True, cleaned, "sanitized", masked, "re-masked residual identifiers")
    if g.get("block_on_residual_phi", False):
        return GuardResult(False, text, "block", residual, "residual PHI and input redaction disabled")
    return GuardResult(True, text, "pass", residual, "residual PHI detected (not redacted)")


def guard_output(text: str, cfg: dict) -> GuardResult:
    """Sanitise model output — no echoed identifiers, no injection markers."""
    g = _g(cfg)
    if not enabled(cfg) or not g.get("scan_output", True) or not text:
        return GuardResult(True, text or "", "pass")
    findings = pii.scan(text)
    injection = bool(_INJECTION.search(text))
    if not findings and not injection:
        return GuardResult(True, text, "pass")
    out = text
    if findings:
        out, _ = pii.redact_residuals(out)
    notes = []
    if findings:
        notes.append("redacted echoed identifier(s)")
    if injection:
        notes.append("prompt-injection markers flagged")
    return GuardResult(True, out, "sanitized", findings, "; ".join(notes))
