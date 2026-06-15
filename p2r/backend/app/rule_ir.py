"""Phase 4 — Canonical Rule Intermediate Representation (IR) + compiler.

An approved recommendation is lowered to a single canonical Rule IR, then compiled to
target-specific artifacts. Two targets ship:
  * "ace"     — the concrete coding-engine format (payer-policy rows), proven end-to-end.
  * "generic" — an engine-agnostic rule package (a small, explicit DSL). This is the seam the
                client's RCx/ClaimStaker adapter plugs into; the doc itself flags the exact
                RCx/ClaimStaker schema as its #1 unknown, so we compile to a clean IR and a
                representative package an adapter maps to their spec.
The IR is the keystone contract shared with ACE via core/ir.py.
"""
from __future__ import annotations

from . import models, publish

# provision type -> canonical engine action
_ACTION = {
    "PRIOR_AUTH": "REQUIRE_PRIOR_AUTH",
    "FREQUENCY": "LIMIT_FREQUENCY",
    "COVERAGE": "REQUIRE_MEDICAL_NECESSITY",
    "DOCUMENTATION": "REQUIRE_DOCUMENTATION",
    "BUNDLING": "BUNDLE_NOT_SEPARATELY_PAYABLE",
    "MODIFIER": "REQUIRE_MODIFIER",
    "POS": "RESTRICT_PLACE_OF_SERVICE",
    "FEE": "APPLY_FEE_TERM",
}


def build_ir(rec: models.RuleRecommendation) -> dict:
    cs = rec.code_sets or {}
    return {
        "rule_id": f"P2R-{rec.id[:8].upper()}",
        "version": 1,
        "payer": rec.payer,
        "rule_type": rec.provision_type,
        "action": _ACTION.get(rec.provision_type, "MANUAL_REVIEW"),
        "applies_to": {
            "cpt": cs.get("cpt", []) or [], "icd": cs.get("icd", []) or [],
            "hcpcs": cs.get("hcpcs", []) or [], "modifiers": cs.get("modifiers", []) or [],
            "pos": cs.get("pos", []) or [],
        },
        "statement": rec.candidate_summary,
        "disposition": "DENY" if rec.provision_type in ("COVERAGE", "FREQUENCY", "BUNDLING") else "FLAG",
        "origin": rec.origin,
        "reconciliation_verdict": rec.reconciliation_verdict,
        "confidence": rec.confidence,
        "provenance": {
            "source_document_id": rec.source_document_id or None,
            "source_provision_id": rec.source_provision_id or None,
            "source_signal_id": rec.source_signal_id or None,
            "model_version": rec.model_version,
        },
    }


def compile_generic(ir: dict) -> dict:
    """Engine-agnostic rule package — the adapter target for RCx/ClaimStaker (or any engine)."""
    a = ir["applies_to"]
    return {
        "rule_id": ir["rule_id"],
        "version": ir["version"],
        "payer": ir["payer"],
        "when": {k: v for k, v in {
            "procedure_in": a["cpt"] + a["hcpcs"], "diagnosis_in": a["icd"],
            "modifier_in": a["modifiers"], "place_of_service_in": a["pos"],
        }.items() if v},
        "require": ir["action"],
        "disposition": ir["disposition"],
        "rationale": ir["statement"],
        "source": ir["provenance"],
        "_adapter_note": "Engine-agnostic IR; an RCx/ClaimStaker adapter maps this to the engine's native schema.",
    }


def compile_all(rec: models.RuleRecommendation) -> dict:
    ir = build_ir(rec)
    return {
        "ir": ir,
        "artifacts": {
            "ace": publish.build_policy_payloads(rec),   # concrete engine format (proven)
            "generic": compile_generic(ir),              # adapter seam
        },
    }
