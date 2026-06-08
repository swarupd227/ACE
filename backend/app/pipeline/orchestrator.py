"""The agentic orchestrator — runs a chart through Stage 0..5 with veto/downgrade
and an honest manual-route fallback. Every stage appends to an inspectable
stage_log and to the append-only audit ledger.
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..knowledge import graph_rag
from ..llm import prompts
from ..llm.client import LLMUnavailable, complete_json, model_version
from . import validation

# Confidence routing thresholds (calibrated per-specialty in production)
STB_THRESHOLD = 0.90
QA_THRESHOLD = 0.75


def _now():
    return datetime.now(timezone.utc)


def _number_chart(text: str) -> tuple[str, dict[int, str]]:
    lines = text.splitlines()
    numbered = "\n".join(f"{i+1}|{ln}" for i, ln in enumerate(lines))
    lookup = {i + 1: ln for i, ln in enumerate(lines)}
    return numbered, lookup


def _tok(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(t) > 2}


def _audit(db, run, stage, event, detail, actor="system"):
    db.add(models.AuditEntry(
        run_id=run.id, encounter_id=run.encounter_id, stage=stage, actor=actor,
        event=event, detail=detail, model_version=run.model_version,
    ))


# ---------------------------------------------------------------------------
# Stage 0 — eligibility (deterministic)
# ---------------------------------------------------------------------------
def stage0_eligibility(enc: models.Encounter) -> dict:
    checks: list[dict] = []
    text_l = enc.chart_text.lower()

    has_report = len(enc.chart_text.strip()) > 120
    checks.append({"check": "required_documentation", "passed": has_report,
                   "detail": "report present" if has_report else "insufficient/empty documentation"})

    approved = enc.specialty in ("Radiology", "E&M", "ED")
    checks.append({"check": "approved_specialty", "passed": approved, "detail": enc.specialty})

    # exclusion flags
    is_ir = "interventional" in text_l or "angiograph" in text_l or "embolization" in text_l
    is_trauma = "trauma activation" in text_l or "level 1 trauma" in text_l
    incomplete = "addendum pending" in text_l or "report incomplete" in text_l or "to be dictated" in text_l
    excl = []
    if is_ir:
        excl.append("interventional_radiology")
    if is_trauma:
        excl.append("trauma")
    if incomplete:
        excl.append("incomplete_encounter")
    checks.append({"check": "no_exclusion_flags", "passed": not excl,
                   "detail": ("none" if not excl else ", ".join(excl))})

    eligible = all(c["passed"] for c in checks)
    reasons = [c["detail"] for c in checks if not c["passed"]]
    return {"eligible": eligible, "checks": checks, "reason": "; ".join(reasons)}


# ---------------------------------------------------------------------------
# Stage 3b — citation verification (deterministic)
# ---------------------------------------------------------------------------
def verify_citations(code: dict, lookup: dict[int, str]) -> tuple[bool, float]:
    cits = code.get("chart_citations") or []
    if not cits:
        return False, 0.0
    scores = []
    for c in cits:
        ls, le = int(c.get("line_start", 0)), int(c.get("line_end", 0))
        chart_span = " ".join(lookup.get(i, "") for i in range(ls, le + 1))
        claimed = _tok(c.get("text", ""))
        actual = _tok(chart_span)
        if not claimed:
            scores.append(0.0)
        else:
            scores.append(len(claimed & actual) / len(claimed))
    best = max(scores) if scores else 0.0
    return best >= 0.5, round(best, 3)


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------
def run_coding(db: Session, encounter_id: str, extra_context: str = "") -> models.CodingRun:
    enc = db.get(models.Encounter, encounter_id)
    if enc is None:
        raise ValueError("encounter not found")

    run = models.CodingRun(encounter_id=enc.id, status="RUNNING", model_version=model_version())
    db.add(run)
    db.flush()
    t0 = time.time()
    numbered, lookup = _number_chart(enc.chart_text)
    log: list[dict] = []

    def finish(lane: str, reason: str):
        run.routing_lane = lane
        run.routing_reason = reason
        run.status = "DONE"
        run.stage_log = log
        run.latency_ms = int((time.time() - t0) * 1000)
        run.finished_at = _now()
        enc.status = "CODED"
        _audit(db, run, "routing", f"routed:{lane}", {"reason": reason})
        db.commit()
        db.refresh(run)
        return run

    # --- Stage 0 ---
    elig = stage0_eligibility(enc)
    run.eligibility = elig
    log.append({"stage": "0_eligibility", "title": "Auto-Coding Eligibility", "result": elig})
    _audit(db, run, "0_eligibility", "eligibility_checked", elig)
    if not elig["eligible"]:
        return finish("MANUAL", f"Ineligible for auto-coding: {elig['reason']}")

    # --- Stage 1+2 — analysis (conditioning + summary + extraction) ---
    try:
        analysis = complete_json(
            prompts.ANALYSIS_SYSTEM,
            prompts.build_analysis_user(numbered, enc.specialty),
            prompts.ANALYSIS_SCHEMA, temperature=0.0,
        )[0]
    except LLMUnavailable as e:
        log.append({"stage": "1_analysis", "title": "Clinical Analysis", "error": str(e)})
        return finish("MANUAL", "LLM_UNAVAILABLE — no codes fabricated; routed to human coder")

    run.chart_summary = analysis.get("summary", "")
    flags = analysis.get("conditioning_flags", [])
    log.append({"stage": "1_conditioning", "title": "Document Conditioning",
                "sections": analysis.get("sections", []), "flags": flags})
    log.append({"stage": "2_extraction", "title": "Clinical Entity Extraction",
                "diagnoses": analysis.get("diagnoses", []), "procedures": analysis.get("procedures", []),
                "em_factors": analysis.get("em_factors", {})})
    _audit(db, run, "1_analysis", "analysis_done",
           {"summary": run.chart_summary, "flags": flags})

    has_block_flag = any(f.get("severity") == "block" for f in flags)
    is_ambiguous = any(f.get("type") in ("ambiguous", "contradiction", "missing_documentation") for f in flags)

    # --- Retrieval (Graph-RAG) ---
    retr = graph_rag.retrieve(db, enc, analysis)
    log.append({"stage": "rag", "title": "Graph-RAG Retrieval",
                "icd_candidates": retr.icd_candidates, "proc_candidates": retr.proc_candidates,
                "ontology_paths": retr.ontology_paths, "payer_policies": retr.payer_policies,
                "guideline_excerpts": retr.guideline_excerpts, "learned": retr.learned})

    # --- Stage 3 — coding (self-consistency on hard encounters) ---
    n_proc = len(analysis.get("procedures", []))
    hard = enc.specialty in ("E&M", "ED") or is_ambiguous or n_proc > 1
    samples = settings.ace_self_consistency_samples if hard else 1
    temp = 0.4 if samples > 1 else 0.0
    rag_ctx = retr.as_prompt_context()
    if extra_context:
        rag_ctx += ("\n\n## PHYSICIAN CDI CLARIFICATIONS (authoritative — apply these)\n" + extra_context)
    try:
        coding_samples = complete_json(
            prompts.CODING_SYSTEM,
            prompts.build_coding_user(numbered, enc.specialty, analysis, rag_ctx),
            prompts.CODING_SCHEMA, hard=hard, temperature=temp, samples=samples,
        )
    except LLMUnavailable as e:
        log.append({"stage": "3_coding", "title": "Code Generation", "error": str(e)})
        return finish("MANUAL", "LLM_UNAVAILABLE during coding — routed to human coder")

    # aggregate by code, compute self-consistency agreement
    tally: dict[tuple[str, str], dict] = {}
    for s in coding_samples:
        for c in s.get("codes", []):
            key = (c["code_system"], c["code"])
            slot = tally.setdefault(key, {"code": c, "count": 0})
            slot["count"] += 1
    agg_codes = []
    for key, slot in tally.items():
        agreement = slot["count"] / samples
        if agreement >= 0.5:  # majority across samples (always true when samples==1)
            c = dict(slot["code"])
            c["_agreement"] = round(agreement, 3)
            agg_codes.append(c)
    log.append({"stage": "3_coding", "title": "Code Candidate Generation",
                "samples": samples, "hard": hard, "candidates": agg_codes,
                "notes": coding_samples[0].get("notes", "")})
    _audit(db, run, "3_coding", "candidates_generated", {"count": len(agg_codes), "samples": samples})

    # --- Stage 3b — citation verification + Stage 4 — gates + Stage 5 — calibration ---
    code_dicts = [{"code_system": c["code_system"], "code": c["code"]} for c in agg_codes]
    persisted: list[models.CodeResult] = []
    gate_log = []
    for c in agg_codes:
        # Deterministic professional-component handling: a facility radiology read (POS 22/23/19/21)
        # bills the professional component — append modifier 26 if the model didn't. Rules belong in
        # the rule engine, not the model's memory; this keeps radiology coding consistent.
        if c["code_system"] == "CPT" and c["code"][:1] == "7" and enc.pos in ("22", "23", "19", "21"):
            mods = list(c.get("modifiers", []))
            if "26" not in mods and "TC" not in mods:
                mods.append("26")
                c["modifiers"] = mods
                c["rule_justification"] = (c.get("rule_justification", "") +
                                           " [auto: modifier 26 professional component for facility read]").strip()

        cit_ok, cit_score = verify_citations(c, lookup)
        gates = validation.run_gates(db, c, enc, code_dicts, retr.payer_policies)
        gate_pass_ratio = sum(1 for g in gates if g["passed"]) / len(gates) if gates else 0.0
        existence_ok = next((g["passed"] for g in gates if g["gate"] == "code_existence"), False)

        # four confidence factors (VHT spec) + calibrated overall
        conf_model = float(c.get("confidence", 0.0)) * float(c.get("_agreement", 1.0))
        conf_doc_match = cit_score
        conf_rule = gate_pass_ratio
        # historical proxy: boost if a learned correction or golden pattern supports this code
        learning_applied = any(le["use_code"] == c["code"] for le in retr.learned)
        conf_historical = 0.85 if learning_applied else 0.6
        calibrated = round(
            0.40 * conf_model + 0.25 * conf_doc_match + 0.25 * conf_rule + 0.10 * conf_historical, 3
        )

        status = "accepted"
        if not existence_ok or not cit_ok:
            status = "rejected"
        elif not validation.gates_passed(gates):
            status = "needs_review"

        cr = models.CodeResult(
            run_id=run.id, code_system=c["code_system"], code=c["code"],
            description=c.get("description", ""), role=c.get("role", ""),
            modifiers=c.get("modifiers", []), sequence=c.get("sequence", 0),
            confidence=calibrated, conf_model=round(conf_model, 3), conf_doc_match=conf_doc_match,
            conf_rule=round(conf_rule, 3), conf_historical=conf_historical,
            chart_citations=c.get("chart_citations", []),
            guideline_citations=c.get("guideline_citations", []),
            rule_justification=c.get("rule_justification", ""),
            gate_results=gates, status=status, learning_applied=learning_applied,
        )
        db.add(cr)
        persisted.append(cr)
        gate_log.append({"code": c["code"], "status": status, "citation_verified": cit_ok,
                         "citation_score": cit_score, "gates": gates})

    log.append({"stage": "3b_citation", "title": "Citation Verification",
                "verified": [{"code": g["code"], "ok": g["citation_verified"], "score": g["citation_score"]} for g in gate_log]})
    log.append({"stage": "4_validation", "title": "Validation & Compliance Gates", "results": gate_log})

    # --- Stage 5 — calibration + routing ---
    accepted = [cr for cr in persisted if cr.status == "accepted"]
    rejected = [cr for cr in persisted if cr.status == "rejected"]
    needs_review = [cr for cr in persisted if cr.status == "needs_review"]
    overall = round(min((cr.confidence for cr in accepted), default=0.0), 3) if accepted else 0.0
    run.overall_confidence = overall
    run.accuracy_estimate = overall  # calibrated estimate; true accuracy comes from the eval harness

    # bounded-autonomy hard rules → never STB
    bounded = []
    if has_block_flag:
        bounded.append("blocking conditioning flag")
    if is_ambiguous:
        bounded.append("ambiguous/contradictory documentation")
    if any("critical care" in (c.get("description", "").lower()) for c in agg_codes):
        bounded.append("critical-care code present")
    ncci_break = any(
        any(g["gate"] == "ncci_ptp" and not g["passed"] for g in cr.gate_results) for cr in persisted
    )
    if ncci_break:
        bounded.append("NCCI bundle conflict")

    log.append({"stage": "5_calibration", "title": "Confidence Calibration & Routing",
                "overall_confidence": overall, "accepted": len(accepted),
                "needs_review": len(needs_review), "rejected": len(rejected),
                "bounded_autonomy": bounded, "thresholds": {"STB": STB_THRESHOLD, "QA": QA_THRESHOLD}})
    _audit(db, run, "5_calibration", "calibrated", {"overall": overall, "bounded": bounded})

    if not accepted or rejected:
        return finish("MANUAL", "Rejected/uncitable candidates present — human coding required"
                      if rejected else "No defensible codes — human coding required")
    if bounded or needs_review:
        return finish("QA", "; ".join(bounded) or "gate(s) need review")
    if overall >= STB_THRESHOLD:
        return finish("STB", f"All gates passed; calibrated confidence {overall:.2f} ≥ {STB_THRESHOLD}")
    if overall >= QA_THRESHOLD:
        return finish("QA", f"Calibrated confidence {overall:.2f} in QA band")
    return finish("MANUAL", f"Calibrated confidence {overall:.2f} below QA threshold")


def cdi_scan(db: Session, encounter_id: str) -> list[models.CdiQuery]:
    """Run the CDI agent on the latest coded run; persist drafted physician queries.
    Replaces any prior OPEN (unanswered) queries for this encounter."""
    enc = db.get(models.Encounter, encounter_id)
    if enc is None:
        raise ValueError("encounter not found")
    run = db.scalars(
        select(models.CodingRun).where(models.CodingRun.encounter_id == enc.id)
        .order_by(models.CodingRun.started_at.desc()).limit(1)
    ).first()
    codes = [
        {"code_system": c.code_system, "code": c.code, "role": c.role, "description": c.description}
        for c in (run.codes if run else [])
    ]
    numbered, _ = _number_chart(enc.chart_text)
    result = complete_json(
        prompts.CDI_SYSTEM,
        prompts.build_cdi_user(numbered, enc.specialty, codes),
        prompts.CDI_SCHEMA, temperature=0.0,
    )[0]

    # clear prior open queries for this encounter
    for q in db.scalars(
        select(models.CdiQuery).where(
            models.CdiQuery.encounter_id == enc.id, models.CdiQuery.status == "open"
        )
    ).all():
        db.delete(q)

    created: list[models.CdiQuery] = []
    for q in result.get("queries", []):
        opts = q.get("options", [])
        if "Unable to determine" not in opts:
            opts = opts + ["Unable to determine"]
        cq = models.CdiQuery(
            encounter_id=enc.id, run_id=run.id if run else "", specialty=enc.specialty,
            question=q.get("question", ""), clinical_indicators=q.get("clinical_indicators", ""),
            options=opts, target=q.get("target", ""), potential_codes=q.get("potential_codes", []),
            rationale=q.get("rationale", ""),
        )
        db.add(cq)
        created.append(cq)
        if run:
            _audit(db, run, "cdi", "query_drafted", {"target": cq.target, "question": cq.question})
    db.commit()
    for cq in created:
        db.refresh(cq)
    return created

