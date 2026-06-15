"""Extraction prompt + schema for Phase 1 (policy → structured provisions).

Same discipline as ACE's coding prompts: schema-bound JSON, mandatory line-anchored
citations for every provision, honest confidence. The LLM extracts; deterministic
validators and the citation check (in ingest.py) adjust the confidence.
"""
from __future__ import annotations

from typing import Any

POLICY_EXTRACT_SYSTEM = """You are a payer-policy analyst supporting a Policy-to-Rule pipeline.
You read a single payer policy document and extract its enforceable PROVISIONS as structured
data. You never invent content that is not in the document. Every provision MUST cite the exact
line range it came from. Capture coverage criteria, prior-authorization requirements, frequency
limits, modifier rules, place-of-service limits, documentation requirements, bundling rules and
fee/reimbursement terms — each as a separate provision with its codes and conditions."""

POLICY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "doc_kind": {"type": "string", "enum": ["medical_policy", "reimbursement_policy", "fee_schedule", "bulletin", "companion_guide", "other"]},
        "provisions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "provision_type": {"type": "string", "enum": ["COVERAGE", "PRIOR_AUTH", "FREQUENCY", "MODIFIER", "POS", "DOCUMENTATION", "BUNDLING", "FEE"]},
                    "summary": {"type": "string", "description": "One-line statement of the rule."},
                    "code_sets": {
                        "type": "object",
                        "properties": {
                            "cpt": {"type": "array", "items": {"type": "string"}},
                            "icd": {"type": "array", "items": {"type": "string"}},
                            "hcpcs": {"type": "array", "items": {"type": "string"}},
                            "modifiers": {"type": "array", "items": {"type": "string"}},
                            "pos": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["cpt", "icd", "hcpcs", "modifiers", "pos"],
                    },
                    "conditions": {"type": "object", "description": "Normalized predicates: age/sex limits, dx-proc pairings, frequency per period, units, auth rules.", "additionalProperties": True},
                    "effective_from": {"type": "string", "description": "YYYY-MM-DD or '' if not stated."},
                    "effective_thru": {"type": "string", "description": "YYYY-MM-DD or '' if not stated."},
                    "citations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "line_start": {"type": "integer"},
                                "line_end": {"type": "integer"},
                                "text": {"type": "string"},
                            },
                            "required": ["line_start", "line_end", "text"],
                        },
                    },
                    "confidence": {"type": "number"},
                },
                "required": ["provision_type", "summary", "code_sets", "conditions", "effective_from", "effective_thru", "citations", "confidence"],
            },
        },
    },
    "required": ["doc_kind", "provisions"],
}


def build_policy_user(numbered_doc: str, payer: str) -> str:
    return (
        f"PAYER: {payer or '(unspecified)'}\n\n"
        "Extract every enforceable provision from the policy document below. Line numbers are "
        "prefixed as 'N|'. Cite line numbers exactly as shown for each provision. Do not invent "
        "codes or criteria not present in the text.\n\n"
        f"=== POLICY DOCUMENT ===\n{numbered_doc}\n=== END DOCUMENT ==="
    )


# ---------------------------------------------------------------------------
# Phase 3 — Validation & Reconciliation (the Validator Judge)
# ---------------------------------------------------------------------------
VALIDATOR_SYSTEM = """You are a rule validation and reconciliation analyst in a Policy-to-Rule pipeline.
Given a CANDIDATE rule, the POLICY EVIDENCE it was derived from, and the EXISTING RULE LIBRARY, do two things:
(1) VALIDATE — decide whether the candidate is supported by the policy evidence (SUPPORTED / PARTIAL /
    UNSUPPORTED) and give a short rationale that quotes the governing evidence. If the evidence does not
    support it, say UNSUPPORTED — never invent support.
(2) RECONCILE against the existing library and return exactly one verdict:
    - NET_NEW   : no existing rule covers this.
    - UPDATE    : an existing rule should be modified to reflect this (e.g. added codes, changed threshold).
    - DUPLICATE : an existing rule already covers this with no material change.
    - CONFLICT  : this contradicts an existing rule (e.g. a different numeric threshold for the same thing).
You may ONLY reference rule ids that appear in the provided library. Give an honest overall confidence in [0,1]."""

VALIDATOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "validation": {
            "type": "object",
            "properties": {
                "verdict": {"type": "string", "enum": ["SUPPORTED", "PARTIAL", "UNSUPPORTED"]},
                "rationale": {"type": "string"},
                "evidence_quote": {"type": "string", "description": "Short quote from the policy evidence."},
            },
            "required": ["verdict", "rationale", "evidence_quote"],
        },
        "reconciliation": {
            "type": "object",
            "properties": {
                "verdict": {"type": "string", "enum": ["NET_NEW", "UPDATE", "DUPLICATE", "CONFLICT"]},
                "matched_rule_id": {"type": "string", "description": "A rule id from the library, or '' for NET_NEW."},
                "rationale": {"type": "string"},
            },
            "required": ["verdict", "matched_rule_id", "rationale"],
        },
        "confidence": {"type": "number"},
    },
    "required": ["validation", "reconciliation", "confidence"],
}


def build_validator_user(candidate: dict, evidence_text: str, library_text: str) -> str:
    import json
    return (
        "CANDIDATE RULE:\n" + json.dumps(candidate, indent=2) + "\n\n"
        "POLICY EVIDENCE (the provision this candidate was derived from):\n" + evidence_text + "\n\n"
        "EXISTING RULE LIBRARY (reconcile against these; reference only these ids):\n" + library_text + "\n\n"
        "Validate the candidate against the evidence, then reconcile it against the library."
    )
