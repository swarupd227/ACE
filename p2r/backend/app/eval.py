"""Golden-set evaluation harness for P2R.

Runs the REAL pipeline (ingest the synthetic sample policy with the live model, then
validate + reconcile each provision against the seeded rule library) and scores the
output against an adjudicated golden set. Nothing is hardcoded — every number comes from
this run, so a model regression shows up immediately. Same discipline as ACE's eval
harness ("the eval harness is the product").

Metrics are reported separately so a single LLM-judgment flip does not zero the whole run:
  * provision_coverage  — did we extract every expected provision type?
  * code_recall         — are the expected codes present in the extracted provisions?
  * citation_rate       — does every extracted provision carry >=1 citation?
  * verdict_accuracy    — does the reconciliation verdict match the adjudicated answer?
  * attention_accuracy  — is the needs-attention flag correct?
The eval ingests a throwaway document and deletes it (and its provisions/recs) afterwards,
so it never pollutes the workbench.
"""
from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from core import llm_client

from . import ingest, models, sample, validate

# Adjudicated golden set for the sample lumbar-imaging policy reconciled against the
# seeded library (RULE-LUM-PA[72148], RULE-LUM-FREQ[72148, 6-mo], RULE-LUM-MOD26[72148, mod 26]).
GOLDEN: list[dict] = [
    {"provision_type": "COVERAGE", "expected_verdict": "NET_NEW", "expected_codes": ["72148"],
     "expected_attention": False, "note": "No coverage rule exists yet."},
    {"provision_type": "PRIOR_AUTH", "expected_verdict": "UPDATE", "expected_codes": ["72148", "72131", "72132"],
     "expected_attention": False, "note": "Policy adds CT 72131/72132 to the 72148-only PA rule."},
    {"provision_type": "FREQUENCY", "expected_verdict": "CONFLICT", "expected_codes": ["72148"],
     "expected_attention": True, "note": "Policy says 12 months; library rule says 6 — contradiction."},
    {"provision_type": "MODIFIER", "expected_verdict": "UPDATE", "expected_codes": ["26"],
     "expected_attention": False, "note": "Adds the 'modifier 50 not applicable' clause."},
    {"provision_type": "DOCUMENTATION", "expected_verdict": "NET_NEW", "expected_codes": [],
     "expected_attention": False, "note": "No documentation rule exists yet."},
    {"provision_type": "BUNDLING", "expected_verdict": "NET_NEW", "expected_codes": ["72131"],
     "expected_attention": False, "note": "No bundling rule exists yet."},
]


def golden_set() -> list[dict]:
    return GOLDEN


def _all_codes(code_sets: dict) -> set[str]:
    out: set[str] = set()
    for v in (code_sets or {}).values():
        if isinstance(v, list):
            out |= {str(c).strip().upper() for c in v}
    return out


def _cleanup(db: Session, doc_id: str) -> None:
    db.execute(delete(models.RuleRecommendation).where(models.RuleRecommendation.source_document_id == doc_id))
    db.execute(delete(models.PolicyProvision).where(models.PolicyProvision.document_id == doc_id))
    db.execute(delete(models.PolicyDocument).where(models.PolicyDocument.id == doc_id))
    db.commit()


def run_eval(db: Session, llm: dict | None = None) -> dict:
    """Ingest the sample policy fresh, generate recommendations, score, then clean up."""
    if not llm_client.llm_available(llm):
        raise RuntimeError("LLM not configured — set ANTHROPIC_API_KEY")

    validate._seed_library(db)  # ensure the reconciliation library exists
    # Keep the real payer (library reconciliation matches on payer); mark the doc via title/source.
    ing = ingest.ingest_policy(db, sample.SAMPLE_PAYER, f"[EVAL] {sample.SAMPLE_TITLE}",
                               sample.SAMPLE_POLICY, source_type="EVAL", llm=llm)
    doc_id = ing["document_id"]
    try:
        gen = validate.generate_for_document(db, doc_id, llm=llm)
        recs = gen["recommendations"]
        provs = db.scalars(
            select(models.PolicyProvision).where(models.PolicyProvision.document_id == doc_id)
        ).all()

        # Index recommendations by provision type (one provision per type in the sample).
        by_type = {r["provision_type"]: r for r in recs}
        cited = sum(1 for p in provs if p.citation_spans)
        citation_rate = round(cited / len(provs), 3) if provs else 0.0

        cases = []
        cov_hits = code_num = code_den = verdict_hits = att_hits = 0
        for g in GOLDEN:
            t = g["provision_type"]
            r = by_type.get(t)
            found = r is not None
            cov_hits += int(found)
            codes = _all_codes(r["code_sets"]) if found else set()
            exp_codes = {c.upper() for c in g["expected_codes"]}
            missing = sorted(exp_codes - codes)
            code_den += len(exp_codes)
            code_num += len(exp_codes) - len(missing)
            verdict_ok = found and r["reconciliation_verdict"] == g["expected_verdict"]
            verdict_hits += int(verdict_ok)
            att_ok = found and bool(r["needs_attention"]) == g["expected_attention"]
            att_hits += int(att_ok)
            cases.append({
                "provision_type": t,
                "found": found,
                "expected_verdict": g["expected_verdict"],
                "actual_verdict": r["reconciliation_verdict"] if found else None,
                "verdict_ok": verdict_ok,
                "matched_rule_id": r["matched_rule_id"] if found else None,
                "expected_codes": g["expected_codes"],
                "missing_codes": missing,
                "expected_attention": g["expected_attention"],
                "actual_attention": bool(r["needs_attention"]) if found else None,
                "attention_ok": att_ok,
                "confidence": r["confidence"] if found else None,
                "note": g["note"],
            })

        n = len(GOLDEN)
        metrics = {
            "provision_coverage": round(cov_hits / n, 3),
            "code_recall": round(code_num / code_den, 3) if code_den else 1.0,
            "citation_rate": citation_rate,
            "verdict_accuracy": round(verdict_hits / n, 3),
            "attention_accuracy": round(att_hits / n, 3),
        }
        return {
            "golden_cases": n,
            "provisions_extracted": len(provs),
            "recommendations": len(recs),
            "model_version": llm_client.model_version(llm),
            "metrics": metrics,
            "cases": cases,
        }
    finally:
        _cleanup(db, doc_id)
