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

from .. import config_store, models
from ..config import settings
from ..knowledge import graph_rag
from ..llm import prompts
from ..llm.client import LLMUnavailable, complete_json, model_version
from . import anes, drg, hcc, validation

# Confidence routing thresholds (calibrated per-specialty in production)
STB_THRESHOLD = 0.90
QA_THRESHOLD = 0.75

# Tracks with their own deterministic payment-model stage (Stage 6).
INPATIENT = "Inpatient (DRG)"        # MS-DRG grouper
RISK_ADJ = "HCC / Risk Adjustment"   # CMS-HCC RAF scorer
ANESTHESIA = "Anesthesia"            # base + time + modifying units × CF


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
def stage0_eligibility(enc: models.Encounter, cfg: dict) -> dict:
    checks: list[dict] = []
    text_l = enc.chart_text.lower()
    elig_cfg = cfg.get("eligibility", {})

    min_chars = elig_cfg.get("min_doc_chars", 120)
    has_report = len(enc.chart_text.strip()) > min_chars
    checks.append({"check": "required_documentation", "passed": has_report,
                   "detail": "report present" if has_report else f"insufficient documentation (< {min_chars} chars)"})

    enabled = [s["name"] for s in cfg.get("specialties", []) if s.get("enabled")]
    approved = enc.specialty in enabled
    checks.append({"check": "approved_specialty", "passed": approved, "detail": enc.specialty})

    # exclusion flags (each toggleable by admin config)
    is_ir = "interventional" in text_l or "angiograph" in text_l or "embolization" in text_l
    is_trauma = "trauma activation" in text_l or "level 1 trauma" in text_l
    incomplete = "addendum pending" in text_l or "report incomplete" in text_l or "to be dictated" in text_l
    excl = []
    if elig_cfg.get("exclude_interventional", True) and is_ir:
        excl.append("interventional_radiology")
    if elig_cfg.get("exclude_trauma", True) and is_trauma:
        excl.append("trauma")
    if elig_cfg.get("exclude_incomplete", True) and incomplete:
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
def run_coding(db: Session, encounter_id: str, extra_context: str = "", emit=None) -> models.CodingRun:
    enc = db.get(models.Encounter, encounter_id)
    if enc is None:
        raise ValueError("encounter not found")

    # --- admin-configurable runtime settings (incl. the active LLM) ---
    cfg = config_store.all_config(db)
    llmc = cfg.get("llm")
    stb_t = cfg["routing"]["stb_threshold"]
    qa_t = cfg["routing"]["qa_threshold"]
    weights = cfg["confidence_weights"]
    ba = cfg["bounded_autonomy"]

    run = models.CodingRun(encounter_id=enc.id, status="RUNNING", model_version=model_version(llmc))
    db.add(run)
    db.flush()
    t0 = time.time()
    numbered, lookup = _number_chart(enc.chart_text)
    log: list[dict] = []
    usage: list[dict] = []   # real per-call token usage, accumulated across the run

    # --- agentic event stream (no-op unless an emitter is passed) ---
    emit = emit or (lambda *a, **k: None)

    def say(actor: str, msg: str, level: str = "info") -> None:
        emit({"type": "log", "actor": actor, "msg": msg, "level": level, "ts": _now().isoformat()})

    def step(key: str, title: str) -> None:
        emit({"type": "stage", "key": key, "title": title, "ts": _now().isoformat()})

    say("Orchestrator", f"Coding run started · {enc.patient_name} · {enc.specialty} {enc.modality}".strip(), "head")

    def finish(lane: str, reason: str):
        run.routing_lane = lane
        run.routing_reason = reason
        run.status = "DONE"
        run.stage_log = log
        run.latency_ms = int((time.time() - t0) * 1000)
        run.input_tokens = sum(u.get("in", 0) for u in usage)
        run.output_tokens = sum(u.get("out", 0) for u in usage)
        run.llm_calls = len(usage)
        run.finished_at = _now()
        enc.status = "CODED"
        say("Calibration & Routing",
            f"routed → {lane} · {reason}",
            {"STB": "good", "QA": "warn", "MANUAL": "bad"}.get(lane, "info"))
        emit({"type": "routing", "lane": lane, "reason": reason})
        db.flush()  # ensure code rows have ids before we snapshot them
        # Snapshot the original AI output so a coder can roll back human edits deterministically.
        run.ai_snapshot = {
            "routing_lane": lane, "routing_reason": reason,
            "overall_confidence": run.overall_confidence,
            "codes": [
                {"id": c.id, "code": c.code, "description": c.description, "role": c.role,
                 "modifiers": list(c.modifiers or []), "status": c.status}
                for c in run.codes
            ],
        }
        _audit(db, run, "routing", f"routed:{lane}", {"reason": reason})
        db.commit()
        db.refresh(run)
        return run

    # --- Stage 0 ---
    step("0", "Eligibility")
    say("Stage 0 · Eligibility Gate", "checking required docs, approved specialty, exclusion flags…", "tool")
    elig = stage0_eligibility(enc, cfg)
    say("Stage 0 · Eligibility Gate",
        "eligible — entering pipeline" if elig["eligible"] else f"INELIGIBLE: {elig['reason']}",
        "good" if elig["eligible"] else "bad")
    run.eligibility = elig
    log.append({"stage": "0_eligibility", "title": "Auto-Coding Eligibility", "result": elig})
    _audit(db, run, "0_eligibility", "eligibility_checked", elig)
    if not elig["eligible"]:
        return finish("MANUAL", f"Ineligible for auto-coding: {elig['reason']}")

    # --- Stage 1+2 — analysis (conditioning + summary + extraction) ---
    step("1", "Conditioning")
    say("Conditioning + Extraction Agent", f"invoking {model_version(llmc)} — sectioning, summary, structured extraction…", "tool")
    try:
        analysis = complete_json(
            prompts.ANALYSIS_SYSTEM,
            prompts.build_analysis_user(numbered, enc.specialty),
            prompts.ANALYSIS_SCHEMA, temperature=0.0, llm=llmc, usage_sink=usage,
        )[0]
    except LLMUnavailable as e:
        log.append({"stage": "1_analysis", "title": "Clinical Analysis", "error": str(e)})
        return finish("MANUAL", "LLM_UNAVAILABLE — no codes fabricated; routed to human coder")

    run.chart_summary = analysis.get("summary", "")
    flags = analysis.get("conditioning_flags", [])
    step("2", "Extraction")
    say("Conditioning + Extraction Agent",
        f"{len(analysis.get('diagnoses', []))} diagnoses · {len(analysis.get('procedures', []))} procedures · {len(flags)} flag(s) · summary ready", "good")
    for f in flags:
        say("  ⚑ Conditioning flag", f"{f.get('type')}: {f.get('detail')}", "warn")
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
    step("rag", "Graph-RAG")
    say("Graph-RAG Retriever", "querying payer-policy + ontology knowledge graph and code sets…", "tool")
    retr = graph_rag.retrieve(db, enc, analysis)
    say("Graph-RAG Retriever",
        f"{len(retr.icd_candidates)} ICD · {len(retr.proc_candidates)} proc candidates · "
        f"{len(retr.ontology_paths)} ontology paths · {len(retr.payer_policies)} payer policies · {len(retr.learned)} learned", "good")
    log.append({"stage": "rag", "title": "Graph-RAG Retrieval",
                "icd_candidates": retr.icd_candidates, "proc_candidates": retr.proc_candidates,
                "ontology_paths": retr.ontology_paths, "payer_policies": retr.payer_policies,
                "guideline_excerpts": retr.guideline_excerpts, "learned": retr.learned})

    # --- Stage 3 — coding (self-consistency on hard encounters) ---
    n_proc = len(analysis.get("procedures", []))
    spec_cfg = next((s for s in cfg.get("specialties", []) if s["name"] == enc.specialty), {})
    hard = bool(spec_cfg.get("hard")) or is_ambiguous or n_proc > 1
    samples = cfg["self_consistency"]["hard_samples"] if hard else 1
    temp = 0.4 if samples > 1 else 0.0
    rag_ctx = retr.as_prompt_context()
    if extra_context:
        rag_ctx += ("\n\n## PHYSICIAN CDI CLARIFICATIONS (authoritative — apply these)\n" + extra_context)
    step("3", "Cited coding")
    say("Coding Agent",
        f"assigning cited codes · {'hard' if hard else 'standard'} model · self-consistency {samples}×…", "tool")
    try:
        coding_samples = complete_json(
            prompts.CODING_SYSTEM,
            prompts.build_coding_user(numbered, enc.specialty, analysis, rag_ctx),
            prompts.CODING_SCHEMA, hard=hard, temperature=temp, samples=samples, llm=llmc, usage_sink=usage,
        )
    except LLMUnavailable as e:
        log.append({"stage": "3_coding", "title": "Code Generation", "error": str(e)})
        return finish("MANUAL", "LLM_UNAVAILABLE during coding — routed to human coder")

    # aggregate by code, compute self-consistency agreement. A malformed entry in one
    # sample (e.g., a bare string instead of a code object) simply doesn't count toward
    # agreement — robustness over crashing the whole chart on one flaky sample.
    tally: dict[tuple[str, str], dict] = {}
    for s in coding_samples:
        if not isinstance(s, dict):
            continue
        for c in s.get("codes", []):
            if not isinstance(c, dict) or "code_system" not in c or "code" not in c:
                continue
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
    say("Coding Agent",
        f"{len(agg_codes)} candidate code(s): " + ", ".join(c["code"] for c in agg_codes), "good")

    # --- Stage 3b — citation verification + Stage 4 — gates + Stage 5 — calibration ---
    step("4", "Validation gates")
    say("Validation Engine", "verifying citations + running deterministic gates (existence, NCCI, MUE, modifiers, specificity, payer necessity)…", "tool")
    # Deterministic code-system normalization: CPT is HCPCS Level I, so models sometimes
    # claim a Level-II G/A/Q-code as "CPT". If the code is absent under its claimed family
    # but present under the sibling family in the reference data, correct the family rather
    # than rejecting an otherwise-valid, cited code. Data-driven — never invents a code.
    for c in agg_codes:
        if c["code_system"] in ("CPT", "HCPCS"):
            sibling = "HCPCS" if c["code_system"] == "CPT" else "CPT"
            if (validation._ref(db, c["code_system"], c["code"]) is None
                    and validation._ref(db, sibling, c["code"]) is not None):
                say("Validation Engine",
                    f"normalized {c['code_system']} {c['code']} → {sibling} (HCPCS family lookup)", "warn")
                c["code_system"] = sibling
                c["rule_justification"] = (c.get("rule_justification", "") +
                                           f" [auto: code-system normalized to {sibling}]").strip()
    code_dicts = [{"code_system": c["code_system"], "code": c["code"]} for c in agg_codes]
    persisted: list[models.CodeResult] = []
    gate_log = []
    for c in agg_codes:
        # Deterministic professional-component handling: a facility radiology read (7xxxx) or surgical
        # pathology interpretation (88xxx) at POS 22/23/19/21 bills the professional component — append
        # modifier 26 if the model didn't. Rules belong in the rule engine, not the model's memory.
        _is_prof = c["code"][:1] == "7" or c["code"][:2] == "88"
        if c["code_system"] == "CPT" and _is_prof and enc.pos in ("22", "23", "19", "21"):
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
        _np = sum(1 for g in gates if g["passed"])
        _fail = ", ".join(g["gate"] for g in gates if not g["passed"])
        say(f"  Validation · {c['code_system']} {c['code']}",
            f"{_np}/{len(gates)} gates {'✓' if not _fail else '✗ ' + _fail} · citation {'✓' if cit_ok else '✗'} ({cit_score})",
            "good" if (not _fail and cit_ok) else ("bad" if not cit_ok else "warn"))

        # four confidence factors (VHT spec) + calibrated overall
        conf_model = float(c.get("confidence", 0.0)) * float(c.get("_agreement", 1.0))
        conf_doc_match = cit_score
        conf_rule = gate_pass_ratio
        # historical proxy: boost if a learned correction or golden pattern supports this code
        learning_applied = any(le["use_code"] == c["code"] for le in retr.learned)
        conf_historical = 0.85 if learning_applied else 0.6
        calibrated = round(
            weights["model"] * conf_model + weights["doc_match"] * conf_doc_match
            + weights["rule"] * conf_rule + weights["historical"] * conf_historical, 3
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
    step("5", "Calibration & routing")
    say("Calibration & Routing", "calibrating multi-axis confidence and applying bounded-autonomy rules…", "tool")
    accepted = [cr for cr in persisted if cr.status == "accepted"]
    rejected = [cr for cr in persisted if cr.status == "rejected"]
    needs_review = [cr for cr in persisted if cr.status == "needs_review"]
    overall = round(min((cr.confidence for cr in accepted), default=0.0), 3) if accepted else 0.0
    run.overall_confidence = overall
    run.accuracy_estimate = overall  # calibrated estimate; true accuracy comes from the eval harness

    # bounded-autonomy hard rules → never STB (each toggleable by admin config)
    bounded = []
    if ba.get("block_flag", True) and has_block_flag:
        bounded.append("blocking conditioning flag")
    if ba.get("ambiguous_or_contradiction", True) and is_ambiguous:
        bounded.append("ambiguous/contradictory documentation")
    if ba.get("critical_care", True) and any("critical care" in (c.get("description", "").lower()) for c in agg_codes):
        bounded.append("critical-care code present")
    ncci_break = any(
        any(g["gate"] == "ncci_ptp" and not g["passed"] for g in cr.gate_results) for cr in persisted
    )
    if ba.get("ncci_break", True) and ncci_break:
        bounded.append("NCCI bundle conflict")

    # --- Stage 6 (inpatient only) — MS-DRG grouping ---
    if enc.specialty == INPATIENT:
        step("6", "MS-DRG grouping")
        say("MS-DRG Grouper", "assigning MDC → surgical/medical partition → base DRG → CC/MCC severity tier…", "tool")
        acc_codes = [
            {"code_system": cr.code_system, "code": cr.code, "role": cr.role,
             "sequence": cr.sequence, "description": cr.description}
            for cr in accepted
        ]
        dg = drg.group(db, acc_codes)
        db.add(models.DrgResult(
            run_id=run.id, encounter_id=enc.id, drg=dg["drg"], title=dg["title"],
            mdc=dg["mdc"], mdc_title=dg["mdc_title"], drg_type=dg["drg_type"],
            severity=dg["severity"], weight=dg["weight"], pdx=dg["pdx"],
            or_procedure=dg["or_procedure"], cc_mcc_drivers=dg["cc_mcc_drivers"],
            trace=dg["trace"], resolved=dg["resolved"],
        ))
        log.append({"stage": "6_drg", "title": "MS-DRG Assignment", "result": dg})
        _audit(db, run, "6_drg", "drg_assigned" if dg["resolved"] else "drg_unresolved",
               {"drg": dg["drg"], "weight": dg["weight"], "severity": dg["severity"],
                "type": dg["drg_type"], "resolved": dg["resolved"]})
        if dg["resolved"]:
            say("MS-DRG Grouper",
                f"DRG {dg['drg']} · {dg['title']} · {dg['drg_type']} · severity {dg['severity']} · "
                f"relative weight {dg['weight']:.4f}", "good")
        else:
            bounded.append(f"DRG unresolved ({dg['reason']}) — human grouping required")
            say("MS-DRG Grouper", f"DRG unresolved — {dg['reason']}; routing to human", "bad")

    # --- Stage 6 (risk adjustment only) — CMS-HCC RAF scoring ---
    if enc.specialty == RISK_ADJ:
        step("6", "HCC / RAF scoring")
        say("HCC RAF Scorer", "mapping diagnoses → HCC categories, resolving hierarchies, computing RAF…", "tool")
        acc_codes = [
            {"code_system": cr.code_system, "code": cr.code, "description": cr.description}
            for cr in accepted
        ]
        hr = hcc.score(db, acc_codes, enc.age, enc.sex)
        db.add(models.HccResult(
            run_id=run.id, encounter_id=enc.id, raf=hr["raf"], demographic=hr["demographic"],
            hccs=hr["hccs"], suppressed=hr["suppressed"], unmapped=hr["unmapped"],
            trace=hr["trace"], resolved=hr["resolved"],
        ))
        log.append({"stage": "6_hcc", "title": "HCC / RAF Scoring", "result": hr})
        _audit(db, run, "6_hcc", "raf_scored" if hr["resolved"] else "raf_unresolved",
               {"raf": hr["raf"], "hccs": [h["hcc"] for h in hr["hccs"]],
                "suppressed": hr["suppressed"], "resolved": hr["resolved"]})
        if hr["resolved"]:
            say("HCC RAF Scorer",
                f"RAF {hr['raf']:.3f} · {len(hr['hccs'])} HCC(s) captured"
                + (f" · {len(hr['suppressed'])} suppressed by hierarchy" if hr["suppressed"] else "")
                + (f" · {len(hr['unmapped'])} dx do not risk-adjust" if hr["unmapped"] else ""), "good")
        else:
            bounded.append(f"RAF unresolved ({hr['reason']}) — human review required")
            say("HCC RAF Scorer", f"RAF unresolved — {hr['reason']}; routing to human", "bad")

    # --- Stage 6 (anesthesia only) — base + time + modifying units × conversion factor ---
    if enc.specialty == ANESTHESIA:
        step("6", "Anesthesia units")
        say("Anesthesia Unit Calculator",
            "looking up CMS base units, computing 15-min time units from documented start/stop…", "tool")
        acc_codes = [
            {"code_system": cr.code_system, "code": cr.code, "modifiers": list(cr.modifiers or [])}
            for cr in accepted
        ]
        ar = anes.calculate(db, acc_codes, enc.chart_text, cfg.get("anesthesia", {}))
        db.add(models.AnesResult(
            run_id=run.id, encounter_id=enc.id, code=ar["code"], base_units=ar["base_units"],
            time_minutes=ar["time_minutes"], time_units=ar["time_units"],
            phys_modifier=ar["phys_modifier"], phys_units=ar["phys_units"],
            qual_circ=ar["qual_circ"], total_units=ar["total_units"],
            conversion_factor=ar["conversion_factor"],
            estimated_allowable=ar["estimated_allowable"],
            trace=ar["trace"], resolved=ar["resolved"],
        ))
        log.append({"stage": "6_anes", "title": "Anesthesia Unit Calculation", "result": ar})
        _audit(db, run, "6_anes", "units_calculated" if ar["resolved"] else "units_unresolved",
               {"code": ar["code"], "total_units": ar["total_units"],
                "estimated_allowable": ar["estimated_allowable"], "resolved": ar["resolved"]})
        if ar["resolved"]:
            say("Anesthesia Unit Calculator",
                f"{ar['code']}: {ar['base_units']} base + {ar['time_units']} time "
                f"({ar['time_minutes']} min) + {ar['phys_units']} modifying = {ar['total_units']} units "
                f"× ${ar['conversion_factor']:.2f} = ${ar['estimated_allowable']:.2f}", "good")
        else:
            bounded.append(f"anesthesia units unresolved ({ar['reason']}) — human review required")
            say("Anesthesia Unit Calculator", f"unresolved — {ar['reason']}; routing to human", "bad")

    log.append({"stage": "5_calibration", "title": "Confidence Calibration & Routing",
                "overall_confidence": overall, "accepted": len(accepted),
                "needs_review": len(needs_review), "rejected": len(rejected),
                "bounded_autonomy": bounded, "thresholds": {"STB": stb_t, "QA": qa_t}})
    _audit(db, run, "5_calibration", "calibrated", {"overall": overall, "bounded": bounded})

    if not accepted or rejected:
        return finish("MANUAL", "Rejected/uncitable candidates present — human coding required"
                      if rejected else "No defensible codes — human coding required")
    if bounded or needs_review:
        return finish("QA", "; ".join(bounded) or "gate(s) need review")
    if overall >= stb_t:
        return finish("STB", f"All gates passed; calibrated confidence {overall:.2f} ≥ {stb_t}")
    if overall >= qa_t:
        return finish("QA", f"Calibrated confidence {overall:.2f} in QA band")
    return finish("MANUAL", f"Calibrated confidence {overall:.2f} below QA threshold")


def cdi_scan(db: Session, encounter_id: str, emit=None) -> list[models.CdiQuery]:
    """Run the CDI agent on the latest coded run; persist drafted physician queries.
    Replaces any prior OPEN (unanswered) queries for this encounter."""
    emit = emit or (lambda *a, **k: None)

    def say(actor: str, msg: str, level: str = "info") -> None:
        emit({"type": "log", "actor": actor, "msg": msg, "level": level, "ts": _now().isoformat()})

    enc = db.get(models.Encounter, encounter_id)
    if enc is None:
        raise ValueError("encounter not found")
    llmc = config_store.all_config(db).get("llm")
    say("CDI Agent", f"reviewing documentation for {enc.patient_name} · {enc.specialty}", "head")
    run = db.scalars(
        select(models.CodingRun).where(models.CodingRun.encounter_id == enc.id)
        .order_by(models.CodingRun.started_at.desc()).limit(1)
    ).first()
    codes = [
        {"code_system": c.code_system, "code": c.code, "role": c.role, "description": c.description}
        for c in (run.codes if run else [])
    ]
    say("CDI Agent", f"checking {len(codes)} assigned code(s) for documentation gaps · invoking {model_version(llmc)}…", "tool")
    numbered, _ = _number_chart(enc.chart_text)
    result = complete_json(
        prompts.CDI_SYSTEM,
        prompts.build_cdi_user(numbered, enc.specialty, codes),
        prompts.CDI_SCHEMA, temperature=0.0, llm=llmc,
    )[0]
    nq = len(result.get("queries", []))
    say("CDI Agent",
        f"{nq} compliant quer{'y' if nq == 1 else 'ies'} drafted" if nq else "documentation is sufficient — no queries needed",
        "good" if nq else "info")

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
        say(f"  Query · {cq.target}", cq.question[:90] + ("…" if len(cq.question) > 90 else ""), "warn")
        if run:
            _audit(db, run, "cdi", "query_drafted", {"target": cq.target, "question": cq.question})
    db.commit()
    for cq in created:
        db.refresh(cq)
    return created

