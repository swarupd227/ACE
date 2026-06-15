"""Phase 4 — Replay testing & differential validation.

Before a rule is promoted, replay it against the historical claim corpus (the synthetic 835
remittance lines) and report the differential: how many claims it touches, how many denials it
would have addressed, and the projected dollar impact. This is real arithmetic over the data —
it ties an authored rule back to the denial evidence that motivates it.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models

# Which denial reason (CARC) a rule of each type is designed to prevent.
_ADDRESSES = {
    "PRIOR_AUTH": {"197"},
    "DOCUMENTATION": {"16"},
    "COVERAGE": {"11", "50"},
    "FREQUENCY": {"151"},
}


def replay_rule(db: Session, rec: models.RuleRecommendation) -> dict:
    cs = rec.code_sets or {}
    codes = {str(c).strip().upper() for c in (cs.get("cpt", []) or []) + (cs.get("hcpcs", []) or [])}
    if not codes:
        return {"recommendation_id": rec.id, "evaluated": 0, "note": "rule has no procedure code to replay"}

    target_carcs = _ADDRESSES.get(rec.provision_type, set())
    rows = db.scalars(select(models.RemittanceLine).where(
        models.RemittanceLine.payer == rec.payer)).all()

    evaluated = matched = denied = addressable = 0
    addressable_amount = 0.0
    samples = []
    for r in rows:
        if r.procedure_code.upper() not in codes:
            continue
        matched += 1
        evaluated += 1
        if r.denied:
            denied += 1
            if not target_carcs or r.denial_carc in target_carcs:
                addressable += 1
                addressable_amount += r.billed_amount or 0.0
                if len(samples) < 5:
                    samples.append({"claim_id": r.claim_id, "procedure_code": r.procedure_code,
                                    "carc": r.denial_carc, "reason": r.denial_reason,
                                    "service_date": r.service_date, "billed": r.billed_amount})

    denial_rate = round(denied / matched, 3) if matched else 0.0
    projected_rate = round((denied - addressable) / matched, 3) if matched else 0.0
    return {
        "recommendation_id": rec.id,
        "rule_type": rec.provision_type,
        "codes": sorted(codes),
        "addresses_carc": sorted(target_carcs),
        "claims_matched": matched,
        "current_denials": denied,
        "current_denial_rate": denial_rate,
        "addressable_denials": addressable,            # denials this rule would prevent
        "projected_denial_rate": projected_rate,       # after enforcing the rule upstream
        "projected_denial_reduction": round(denial_rate - projected_rate, 3),
        "addressable_amount": round(addressable_amount, 2),
        "sample_claims": samples,
    }
