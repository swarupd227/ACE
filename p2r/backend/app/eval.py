"""Golden-set evaluation harness (production-grade, multi-phase).

Runs the REAL pipeline and scores it per phase against adjudicated golden data:
  * P1 (extraction):   provision coverage, code recall, citation validity.
  * P2 (detection):    precision/recall of the denial miner vs the planted patterns.
  * P3 (reconciliation): validation + reconciliation verdict accuracy, attention accuracy.
  * Calibration:       are confidence scores aligned with correctness?
Every number is computed live. Each run is persisted (EvalRun) for history and model-version
drift. The policy golden set is table-backed (EvalGoldenCase) so adjudicators can curate it.
The throwaway eval document is deleted afterwards so the workbench is never polluted.
"""
from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from core import llm_client

from . import denials, ingest, models, sample, validate

# Seed for the table-backed policy golden set.
_GOLDEN_SEED: list[dict] = [
    {"provision_type": "COVERAGE", "expected_verdict": "NET_NEW", "expected_codes": ["72148"],
     "expected_attention": False, "note": "No coverage rule exists yet."},
    {"provision_type": "PRIOR_AUTH", "expected_verdict": "UPDATE", "expected_codes": ["72148", "72131", "72132"],
     "expected_attention": False, "note": "Policy adds CT 72131/72132 to the 72148-only PA rule."},
    {"provision_type": "FREQUENCY", "expected_verdict": "CONFLICT", "expected_codes": ["72148"],
     "expected_attention": True, "note": "Policy 12mo vs library 6mo — contradiction."},
    {"provision_type": "MODIFIER", "expected_verdict": "UPDATE", "expected_codes": ["26"],
     "expected_attention": False, "note": "Adds the 'modifier 50 not applicable' clause."},
    {"provision_type": "DOCUMENTATION", "expected_verdict": "NET_NEW", "expected_codes": [],
     "expected_attention": False, "note": "No documentation rule exists yet."},
    {"provision_type": "BUNDLING", "expected_verdict": "NET_NEW", "expected_codes": ["72131"],
     "expected_attention": False, "note": "No bundling rule exists yet."},
]

# Planted denial patterns (P2 ground truth — what the miner must recover from the synthetic 835).
DENIAL_GOLDEN: list[dict] = [
    {"code": "72148", "carc": "197"},
    {"code": "72131", "carc": "11"},
    {"code": "45378", "carc": "16"},
]


def seed_golden(db: Session) -> None:
    if db.scalar(select(models.EvalGoldenCase.id).limit(1)) is None:
        for g in _GOLDEN_SEED:
            db.add(models.EvalGoldenCase(**g))
        db.commit()


def golden_set(db: Session) -> list[dict]:
    seed_golden(db)
    return [{"id": g.id, "provision_type": g.provision_type, "expected_verdict": g.expected_verdict,
             "expected_codes": g.expected_codes, "expected_attention": g.expected_attention,
             "note": g.note} for g in db.scalars(select(models.EvalGoldenCase)).all()]


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


def run_eval(db: Session, actor: str = "system", llm: dict | None = None, emit=None) -> dict:
    e = emit or (lambda ev: None)
    if not llm_client.llm_available(llm):
        raise RuntimeError("LLM not configured — set ANTHROPIC_API_KEY")
    e({"type": "log", "phase": "setup", "message": "Seeding rule library + golden set…"})
    validate._seed_library(db)
    seed_golden(db)
    golden = golden_set(db)

    # --- P1 + P3: ingest a throwaway copy of the sample policy, judge it ---
    e({"type": "log", "phase": "P1", "message": "P1 · Ingesting sample policy & extracting cited provisions…"})
    ing = ingest.ingest_policy(db, sample.SAMPLE_PAYER, f"[EVAL] {sample.SAMPLE_TITLE}",
                               sample.SAMPLE_POLICY, source_type="EVAL", llm=llm)
    doc_id = ing["document_id"]
    try:
        e({"type": "log", "phase": "P1", "message": f"Extracted {ing['provision_count']} provisions."})
        e({"type": "log", "phase": "P3", "message": "P3 · Validating & reconciling candidates against the library…"})
        gen = validate.generate_for_document(db, doc_id, actor="eval", llm=llm)
        recs = gen["recommendations"]
        provs = db.scalars(select(models.PolicyProvision).where(
            models.PolicyProvision.document_id == doc_id)).all()
        by_type = {r["provision_type"]: r for r in recs}
        cited = sum(1 for p in provs if p.citation_spans)

        cov = code_num = code_den = vacc = aacc = 0
        cases = []
        calib = {"correct_conf": [], "wrong_conf": []}
        for g in golden:
            t = g["provision_type"]
            r = by_type.get(t)
            found = r is not None
            cov += int(found)
            exp_codes = {c.upper() for c in g["expected_codes"]}
            codes = _all_codes(r["code_sets"]) if found else set()
            missing = sorted(exp_codes - codes)
            code_den += len(exp_codes)
            code_num += len(exp_codes) - len(missing)
            vok = found and r["reconciliation_verdict"] == g["expected_verdict"]
            vacc += int(vok)
            aok = found and bool(r["needs_attention"]) == g["expected_attention"]
            aacc += int(aok)
            if found:
                (calib["correct_conf"] if vok else calib["wrong_conf"]).append(r["confidence"])
            cases.append({"provision_type": t, "found": found, "expected_verdict": g["expected_verdict"],
                          "actual_verdict": r["reconciliation_verdict"] if found else None, "verdict_ok": vok,
                          "expected_codes": g["expected_codes"], "missing_codes": missing,
                          "attention_ok": aok, "confidence": r["confidence"] if found else None})
        n = len(golden) or 1
        p1 = {"provision_coverage": round(cov / n, 3),
              "code_recall": round(code_num / code_den, 3) if code_den else 1.0,
              "citation_validity": round(cited / len(provs), 3) if provs else 0.0}
        p3 = {"verdict_accuracy": round(vacc / n, 3), "attention_accuracy": round(aacc / n, 3)}
        e({"type": "log", "phase": "P3", "message": f"Verdict accuracy {int(p3['verdict_accuracy']*100)}% over {n} candidates."})
    finally:
        _cleanup(db, doc_id)

    # --- P2: does the denial miner recover the planted patterns? ---
    e({"type": "log", "phase": "P2", "message": "P2 · Running the denial miner over the 835 corpus…"})
    denials.load_sample(db)
    found_sigs = denials.detect_signals(db, actor="eval")["results"]
    found_keys = {(s["procedure_code"], s["denial_carc"]) for s in found_sigs}
    gold_keys = {(g["code"], g["carc"]) for g in DENIAL_GOLDEN}
    tp = len(found_keys & gold_keys)
    p2 = {"recall": round(tp / len(gold_keys), 3) if gold_keys else 0.0,
          "precision": round(tp / len(found_keys), 3) if found_keys else 0.0,
          "planted": len(gold_keys), "found": len(found_keys), "recovered": tp}
    e({"type": "log", "phase": "P2", "message": f"Recovered {tp}/{len(gold_keys)} planted patterns."})
    e({"type": "log", "phase": "score", "message": "Scoring + calibration…"})

    # --- Calibration: mean confidence of correct vs wrong verdicts ---
    cc, wc = calib["correct_conf"], calib["wrong_conf"]
    calibration = {
        "mean_conf_correct": round(sum(cc) / len(cc), 3) if cc else None,
        "mean_conf_wrong": round(sum(wc) / len(wc), 3) if wc else None,
        "n_correct": len(cc), "n_wrong": len(wc),
    }

    overall = round(sum([p1["provision_coverage"], p1["code_recall"], p1["citation_validity"],
                         p3["verdict_accuracy"], p2["recall"]]) / 5, 3)
    phases = {"P1": p1, "P2": p2, "P3": p3, "calibration": calibration, "cases": cases}

    mv = llm_client.model_version(llm)
    run = models.EvalRun(model_version=mv, overall_score=overall, phases=phases, actor=actor)
    db.add(run)
    db.commit()
    db.refresh(run)

    return {"run_id": run.id, "model_version": mv, "overall_score": overall,
            "golden_cases": n, "phases": phases}


def history(db: Session) -> list[dict]:
    rows = db.scalars(select(models.EvalRun).order_by(models.EvalRun.created_at.desc())).all()
    return [{"run_id": r.id, "model_version": r.model_version, "overall_score": r.overall_score,
             "phases": r.phases, "actor": r.actor,
             "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows]
