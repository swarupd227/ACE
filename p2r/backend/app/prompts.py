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
