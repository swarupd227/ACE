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
from . import anes, apc, drg, hcc, history, pii, validation

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


def _specialty_cfg(cfg: dict, specialty: str) -> dict:
    return next((s for s in cfg.get("specialties", []) if s.get("name") == specialty), {})


def _code_family(code_system: str) -> str:
    if code_system in ("CPT", "HCPCS"):
        return "CPT_HCPCS"
    return code_system


def _family_label(family: str) -> str:
    return {"CPT_HCPCS": "CPT/HCPCS"}.get(family, family)


def _family_matches(code_system: str, family: str) -> bool:
    return _code_family(code_system) == family


def _present_code_families(codes: list[models.CodeResult]) -> set[str]:
    return {_code_family(c.code_system) for c in codes}


def _missing_required_code_families_for_stb(
    cfg: dict, encounter: models.Encounter, accepted: list[models.CodeResult]
) -> list[str]:
    required = _specialty_cfg(cfg, encounter.specialty).get("required_code_families_for_stb", []) or []
    present = _present_code_families(accepted)
    return [family for family in required if family not in present]


def _retrieved_proc_code_set(retr: graph_rag.Retrieval) -> set[str]:
    return {row["code"] for row in (retr.proc_candidates or []) if row.get("code")}


def _is_proc_code(code: dict) -> bool:
    return code.get("code_system") in ("CPT", "HCPCS")


def _spans_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return max(a_start, b_start) <= min(a_end, b_end)


def _diagnosis_support_status(code: dict, analysis: dict) -> str | None:
    if code.get("code_system") != "ICD10CM":
        return None
    desc_tokens = _tok(code.get("description", ""))
    if not desc_tokens:
        return None
    matched: list[str] = []
    citations = code.get("chart_citations") or []
    diagnoses = analysis.get("diagnoses") or []
    for diag in diagnoses:
        if not isinstance(diag, dict):
            continue
        diag_tokens = _tok(diag.get("text", ""))
        if not (desc_tokens & diag_tokens):
            continue
        if citations:
            overlaps = any(
                _spans_overlap(
                    int(c.get("line_start", 0)),
                    int(c.get("line_end", 0)),
                    int(diag.get("line_start", 0)),
                    int(diag.get("line_end", 0)),
                )
                for c in citations
            )
            if not overlaps:
                continue
        matched.append(diag.get("status", ""))
    if "confirmed" in matched:
        return "confirmed"
    if "suspected" in matched:
        return "suspected"
    if "ruled_out" in matched:
        return "ruled_out"
    if "history" in matched:
        return "history"
    return None


_UNCERTAIN_DIAG_PHRASES = (
    "consistent with",
    "compatible with",
    "suggestive of",
    "possible",
    "probably",
    "probable",
    "may represent",
    "could represent",
    "concerning for",
    "suspicious for",
    "cannot exclude",
    "rule out",
)


def _citations_only_uncertain(code: dict) -> bool:
    citations = code.get("chart_citations") or []
    if not citations:
        return False
    saw_uncertain = False
    for cit in citations:
        text = (cit.get("text", "") or "").lower()
        if any(phrase in text for phrase in _UNCERTAIN_DIAG_PHRASES):
            saw_uncertain = True
            continue
        return False
    return saw_uncertain


def _is_definitive_injury_code(code: dict) -> bool:
    if code.get("code_system") != "ICD10CM":
        return False
    val = (code.get("code") or "").upper()
    desc = (code.get("description") or "").lower()
    return val.startswith(("S", "T")) or any(
        term in desc for term in ("fracture", "dislocation", "sprain", "tear", "laceration")
    )


def _integral_soft_tissue_symptom(code: dict, all_codes: list[dict]) -> bool:
    if code.get("code_system") != "ICD10CM":
        return False
    cval = (code.get("code") or "").upper()
    desc = (code.get("description") or "").lower()
    if not (
        "soft tissue disorder" in desc
        or "localized swelling" in desc
        or "edema" in desc
        or cval.startswith(("M79", "R22", "R60"))
    ):
        return False
    cited_text = " ".join((c.get("text", "") or "").lower() for c in (code.get("chart_citations") or []))
    if not any(term in cited_text for term in ("swelling", "soft tissue swelling", "pain", "edema", "lump", "mass")):
        return False
    return any(_is_definitive_injury_code(other) for other in all_codes if other is not code)


def _diagnosis_candidate_drop_reason(
    code: dict,
    analysis: dict,
    chart_region: str | None,
    all_codes: list[dict],
    retrieved_icd_candidates: list[dict],
) -> str | None:
    if code.get("code_system") != "ICD10CM":
        return None
    region_match = validation._code_matches_region(code.get("description", ""), chart_region)
    if region_match is False:
        return f"ICD does not align with chart body region ({chart_region})"
    if _integral_soft_tissue_symptom(code, all_codes):
        return "Symptom/soft-tissue finding is integral to a more definitive injury diagnosis"
    support = _diagnosis_support_status(code, analysis)
    if support == "suspected":
        return "Diagnosis supported only by suspected/consistent-with documentation"
    if support == "ruled_out":
        return "Diagnosis is documented as ruled out"
    if support == "history":
        return "Diagnosis is documented as historical rather than active"
    if _citations_only_uncertain(code):
        return "Diagnosis supported only by uncertain citation language"
    if _is_generic_imaging_abnormality(code) and _has_structural_abnormality_signal(code):
        alternatives = _region_specific_disease_candidates(chart_region, retrieved_icd_candidates, code)
        if alternatives:
            return "Generic imaging-abnormality code is less appropriate than available region-specific diagnosis candidates"
    return None


def _modality_mismatch(enc: models.Encounter, chart_modality: str | None) -> str | None:
    if not chart_modality or not enc.modality:
        return None
    saved = graph_rag._norm_modality(enc.modality)
    extracted = graph_rag._norm_modality(chart_modality)
    if not saved or not extracted or saved == extracted:
        return None
    return f"saved modality {saved} differs from chart modality {extracted}"


_STRUCTURAL_ABNORMALITY_TERMS = (
    "mass",
    "lesion",
    "tumor",
    "neoplasm",
    "nodule",
    "collection",
    "hematoma",
    "cyst",
    "extra-axial",
)


def _is_generic_imaging_abnormality(code: dict) -> bool:
    if code.get("code_system") != "ICD10CM":
        return False
    cval = (code.get("code") or "").upper()
    desc = (code.get("description") or "").lower()
    return cval.startswith(("R90", "R91", "R92", "R93")) or "abnormal findings on diagnostic imaging" in desc


def _citation_text(code: dict) -> str:
    return " ".join((c.get("text", "") or "").lower() for c in (code.get("chart_citations") or []))


def _has_structural_abnormality_signal(code: dict) -> bool:
    return any(term in _citation_text(code) for term in _STRUCTURAL_ABNORMALITY_TERMS)


def _region_specific_disease_candidates(
    chart_region: str | None, all_codes: list[dict], current: dict
) -> list[dict]:
    matches = []
    for other in all_codes:
        if other is current or other.get("code_system") != "ICD10CM":
            continue
        oval = (other.get("code") or "").upper()
        if oval.startswith("R"):
            continue
        region_match = validation._code_matches_region(other.get("description", ""), chart_region)
        if region_match is False:
            continue
        matches.append(other)
    return matches


def _failed_gate_names(code_results: list[models.CodeResult]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for cr in code_results:
        for gate in cr.gate_results or []:
            if gate.get("passed"):
                continue
            name = gate.get("gate", "")
            if name and name not in seen:
                names.append(name)
                seen.add(name)
    return names


def _missing_required_code_family_reason(
    missing_required: list[str], persisted: list[models.CodeResult]
) -> str:
    messages: list[str] = []
    for family in missing_required:
        related = [cr for cr in persisted if _family_matches(cr.code_system, family)]
        label = _family_label(family)
        if not related:
            messages.append(f"No {label} candidates were generated")
            continue
        failed = _failed_gate_names(related)
        if failed:
            messages.append(f"No accepted {label} remained after validation ({', '.join(failed)})")
        else:
            messages.append(f"No accepted {label} remained after validation")
    return "; ".join(messages)


def _needs_review_reason(needs_review: list[models.CodeResult]) -> str:
    failed = _failed_gate_names(needs_review)
    if failed:
        return "Needs review: " + ", ".join(failed)
    return "gate(s) need review"


def _confidence_penalty_cfg(cfg: dict) -> dict[str, float]:
    raw = cfg.get("confidence_penalties", {}) or {}

    def bounded(name: str, default: float) -> float:
        try:
            value = float(raw.get(name, default))
        except (TypeError, ValueError):
            value = default
        return max(0.0, min(1.0, value))

    return {
        "needs_review_code_multiplier": bounded("needs_review_code_multiplier", 0.70),
        "qa_review_multiplier": bounded("qa_review_multiplier", 0.75),
        "manual_lane_multiplier": bounded("manual_lane_multiplier", 0.40),
        "manual_without_accepted_confidence": bounded("manual_without_accepted_confidence", 0.0),
        "rejected_code_confidence": bounded("rejected_code_confidence", 0.0),
    }


def _lane_adjusted_overall_confidence(
    lane: str,
    accepted: list[models.CodeResult],
    needs_review: list[models.CodeResult],
    penalties: dict[str, float],
) -> float:
    accepted_floor = min((cr.confidence for cr in accepted), default=0.0)
    review_floor = min((cr.confidence for cr in [*accepted, *needs_review]), default=0.0)
    if lane == "STB":
        return round(accepted_floor, 3)
    if lane == "QA":
        if needs_review:
            return round(review_floor * penalties["qa_review_multiplier"], 3)
        return round(accepted_floor, 3)
    if not accepted:
        return round(penalties["manual_without_accepted_confidence"], 3)
    return round(review_floor * penalties["manual_lane_multiplier"], 3)


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
    # Privacy guard: the model only ever sees the MASKED text. Masking is
    # line-preserving, so citations still align with the original chart.
    mask_on = cfg.get("privacy", {}).get("mask_identifiers", True)
    if mask_on:
        chart_for_model, pii_findings = pii.mask_identifiers(
            enc.chart_text, known_name=enc.patient_name, known_mrn=enc.mrn)
    else:
        chart_for_model, pii_findings = enc.chart_text, []
    numbered, lookup = _number_chart(chart_for_model)
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
        if lane == "STB":
            run.billed_at = _now()  # straight-through → the claim goes out
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

    # --- Stage 1 privacy guard — mask direct identifiers before any model call ---
    if mask_on:
        say("Privacy Guard", pii.summary(pii_findings), "good" if pii_findings else "info")
        log.append({"stage": "1_privacy", "title": "PII Masking (pre-model)",
                    "enabled": True, "masked": pii_findings,
                    "note": "Direct identifiers masked from the model's copy; age/sex/DOS kept (coding needs them). "
                            "Production: clinical de-id service behind the same hook."})
        _audit(db, run, "1_privacy", "identifiers_masked",
               {"masked": pii_findings, "total": sum(f["count"] for f in pii_findings)})

    # --- Stage 1 patient history — longitudinal checks (only when patient_key links priors) ---
    priors = history.prior_encounters(db, enc)
    cf_findings: list[dict] = []
    prior_ctx = ""
    if priors:
        cf_findings = history.copy_forward_findings(enc.chart_text, priors)
        prior_ctx = history.prior_context(db, priors)
        say("Patient History",
            f"{len(priors)} prior encounter(s) for this patient — "
            + (f"VERBATIM carry-forward detected: {cf_findings[0]['verbatim_words']} words match "
               f"{cf_findings[0]['prior_mrn']} ({cf_findings[0]['prior_dos']})" if cf_findings
               else "no verbatim carry-forward (deterministic text comparison)"),
            "warn" if cf_findings else "good")
        log.append({"stage": "1_history", "title": "Patient History (longitudinal)",
                    "priors": [{"mrn": p.mrn, "dos": p.dos, "specialty": p.specialty} for p in priors],
                    "copy_forward": cf_findings,
                    "note": "Copy-forward here is deterministic word-run comparison against the prior "
                            "documents; the model also sees prior summaries for contradiction checks."})
        _audit(db, run, "1_history", "priors_checked",
               {"priors": len(priors), "copy_forward": cf_findings})

    # --- Stage 1+2 — analysis (conditioning + summary + extraction) ---
    step("1", "Conditioning")
    say("Conditioning + Extraction Agent", f"invoking {model_version(llmc)} — sectioning, summary, structured extraction…", "tool")
    try:
        analysis = complete_json(
            prompts.ANALYSIS_SYSTEM,
            prompts.build_analysis_user(numbered, enc.specialty, prior_context=prior_ctx),
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
                "guideline_excerpts": retr.guideline_excerpts, "learned": retr.learned,
                "chart_region": retr.chart_region, "chart_modality": retr.chart_modality})
    retrieved_proc_codes = _retrieved_proc_code_set(retr)
    modality_mismatch = _modality_mismatch(enc, retr.chart_modality)
    if modality_mismatch:
        say("Metadata Guard", modality_mismatch, "warn")
        log.append({"stage": "rag_metadata", "title": "Chart vs Metadata Cross-Check",
                    "issue": modality_mismatch})
        _audit(db, run, "rag_metadata", "modality_mismatch", {
            "saved_modality": enc.modality,
            "chart_modality": retr.chart_modality,
        })

    # --- Stage 3 – coding (self-consistency on hard encounters) ---
    n_proc = len(analysis.get("procedures", []))
    spec_cfg = _specialty_cfg(cfg, enc.specialty)
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

    filtered_codes = []
    dropped_candidates = []
    for c in agg_codes:
        drop_reason = _diagnosis_candidate_drop_reason(
            c, analysis, retr.chart_region, agg_codes, retr.icd_candidates
        )
        if drop_reason:
            dropped_candidates.append({
                "code": c.get("code"),
                "description": c.get("description", ""),
                "code_system": c.get("code_system"),
                "reason": drop_reason,
            })
        else:
            filtered_codes.append(c)
    if dropped_candidates:
        say("Deterministic Filters",
            f"dropped {len(dropped_candidates)} unsupported candidate(s): "
            + ", ".join(d["code"] for d in dropped_candidates), "warn")
        log.append({"stage": "3a_candidate_filtering", "title": "Deterministic Candidate Filtering",
                    "dropped_candidates": dropped_candidates})
        _audit(db, run, "3a_candidate_filtering", "candidates_dropped", dropped_candidates)
    agg_codes = filtered_codes

    # --- Stage 3b — citation verification + Stage 4 — gates + Stage 5 — calibration ---
    step("4", "Validation gates")
    say("Validation Engine", "verifying citations + running deterministic gates (existence, NCCI, MUE, modifiers, specificity, payer necessity)…", "tool")
    # Deterministic code-system normalization: CPT is HCPCS Level I, so models sometimes
    # claim a Level-II G/A/Q-code as "CPT". If the code is absent under its claimed family
    # but present under the sibling family in the reference data, correct the family rather
    # than rejecting an otherwise-valid, cited code. Data-driven — never invents a code.
    for c in agg_codes:
        if c["code_system"] == "ICD10CM" and validation._ref(db, "ICD10CM", c["code"]) is None:
            children = db.scalars(
                select(models.ReferenceCode).where(
                    models.ReferenceCode.code_system == "ICD10CM",
                    models.ReferenceCode.parent == c["code"],
                    models.ReferenceCode.billable == True,  # noqa: E712
                )
            ).all()
            if len(children) == 1:
                only = children[0]
                say("Validation Engine",
                    f"normalized ICD10CM {c['code']} → {only.code} (single billable child)", "warn")
                c["code"] = only.code
                c["description"] = only.description
                c["rule_justification"] = (
                    c.get("rule_justification", "") + f" [auto: normalized to billable child {only.code}]"
                ).strip()
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
        ungrounded_proc = _is_proc_code(c) and c["code"] not in retrieved_proc_codes
        gates = []
        if ungrounded_proc:
            gates.append({
                "gate": "retrieval_grounding",
                "passed": False,
                "detail": f"{c['code_system']} {c['code']} not present in retrieved candidate procedure context",
            })
            _audit(db, run, "4_validation", "ungrounded_procedure_code", {
                "code_system": c["code_system"],
                "code": c["code"],
                "retrieved_proc_codes": sorted(retrieved_proc_codes),
            })
        gates.extend(validation.run_gates(
            db, c, enc, code_dicts, retr.payer_policies, chart_region=retr.chart_region
        ))
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
        if ungrounded_proc or not existence_ok or not cit_ok:
            status = "rejected"
        elif not validation.gates_passed(gates):
            status = "needs_review"

        penalties = _confidence_penalty_cfg(cfg)
        adjusted_confidence = calibrated
        if status == "needs_review":
            adjusted_confidence = round(calibrated * penalties["needs_review_code_multiplier"], 3)
        elif status == "rejected":
            adjusted_confidence = round(penalties["rejected_code_confidence"], 3)

        cr = models.CodeResult(
            run_id=run.id, code_system=c["code_system"], code=c["code"],
            description=c.get("description", ""), role=c.get("role", ""),
            modifiers=c.get("modifiers", []), sequence=c.get("sequence", 0),
            confidence=adjusted_confidence, conf_model=round(conf_model, 3), conf_doc_match=conf_doc_match,
            conf_rule=round(conf_rule, 3), conf_historical=conf_historical,
            chart_citations=c.get("chart_citations", []),
            guideline_citations=c.get("guideline_citations", []),
            rule_justification=c.get("rule_justification", ""),
            gate_results=gates, status=status, learning_applied=learning_applied,
        )
        db.add(cr)
        persisted.append(cr)
        gate_log.append({"code": c["code"], "status": status, "citation_verified": cit_ok,
                         "citation_score": cit_score, "gates": gates,
                         "retrieval_grounded": not ungrounded_proc})

    log.append({"stage": "3b_citation", "title": "Citation Verification",
                "verified": [{"code": g["code"], "ok": g["citation_verified"], "score": g["citation_score"]} for g in gate_log]})
    log.append({"stage": "4_validation", "title": "Validation & Compliance Gates", "results": gate_log})

    # --- Stage 5 — calibration + routing ---
    step("5", "Calibration & routing")
    say("Calibration & Routing", "calibrating multi-axis confidence and applying bounded-autonomy rules…", "tool")
    accepted = [cr for cr in persisted if cr.status == "accepted"]
    rejected = [cr for cr in persisted if cr.status == "rejected"]
    needs_review = [cr for cr in persisted if cr.status == "needs_review"]
    missing_required = _missing_required_code_families_for_stb(cfg, enc, accepted)
    confidence_penalties = _confidence_penalty_cfg(cfg)
    routing_overall = round(min((cr.confidence for cr in accepted), default=0.0), 3) if accepted else 0.0
    display_overall = routing_overall

    # bounded-autonomy hard rules → never STB (each toggleable by admin config)
    bounded = []
    if ba.get("block_flag", True) and has_block_flag:
        bounded.append("blocking conditioning flag")
    if ba.get("ambiguous_or_contradiction", True) and is_ambiguous:
        bounded.append("ambiguous/contradictory documentation")
    if ba.get("metadata_modality_mismatch", True) and modality_mismatch:
        bounded.append(modality_mismatch)
    if ba.get("unsigned_note", True):
        # Deterministic metadata check first (FHIR docStatus-style); the model's
        # text-derived 'unsigned' flag remains as the backup signal.
        if (enc.doc_status or "final") != "final":
            bounded.append(f"document not attested (doc_status={enc.doc_status}) — cannot drive billing")
        elif any(f.get("type") == "unsigned" and f.get("severity") in ("warn", "block") for f in flags):
            # severity-gated: models sometimes emit an info-level 'unsigned' flag just to
            # NOTE that a signature is present — only warn/block means actually unsigned.
            bounded.append("unsigned/unattested note — cannot drive billing")
    if ba.get("copy_forward", True) and cf_findings:
        f0 = cf_findings[0]
        bounded.append(f"verbatim text carried forward from {f0['prior_mrn']} ({f0['prior_dos']}) "
                       "— review before billing")
    # Late-entered addendum: an addendum timestamped AFTER a prior billed run is a
    # compliance flag (deterministic timestamp comparison, never model judgment).
    if enc.addendum_at:
        prior_billed = [
            (r.billed_at or r.finished_at) for r in db.scalars(
                select(models.CodingRun).where(
                    models.CodingRun.encounter_id == enc.id,
                    models.CodingRun.id != run.id,
                    models.CodingRun.routing_lane == "STB",
                )
            ).all() if (r.billed_at or r.finished_at)
        ]
        if prior_billed and enc.addendum_at > max(prior_billed):
            bounded.append("late addendum after billing — compliance review required")
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
        # Recapture: HCCs documented on this patient's PRIOR encounters that are not
        # re-captured in this run. Conditions must be re-documented annually to pay.
        recapture = []
        if priors:
            prior_set = history.prior_hccs(db, priors)
            current_set = {h["hcc"] for h in hr["hccs"]}
            recapture = [
                {"hcc": h, "label": v["label"], "coefficient": v["coefficient"]}
                for h, v in sorted(prior_set.items(), key=lambda kv: kv[1]["coefficient"], reverse=True)
                if h not in current_set
            ]
            if recapture:
                lost = sum(g["coefficient"] for g in recapture)
                say("HCC RAF Scorer",
                    f"recapture opportunity: {len(recapture)} prior-year HCC(s) not re-documented "
                    f"this year — {lost:.3f} RAF at stake "
                    f"({', '.join('HCC ' + g['hcc'] for g in recapture)})", "warn")
                _audit(db, run, "6_hcc", "recapture_gaps",
                       {"gaps": recapture, "raf_at_stake": round(lost, 3)})
        db.add(models.HccResult(
            run_id=run.id, encounter_id=enc.id, raf=hr["raf"], demographic=hr["demographic"],
            hccs=hr["hccs"], suppressed=hr["suppressed"], unmapped=hr["unmapped"],
            recapture_gaps=recapture, trace=hr["trace"], resolved=hr["resolved"],
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

    # --- Stage 6 (hospital outpatient, POS 22/23) — facility-side APC / OPPS pricing ---
    # A parallel payment lens on the SAME coded chart (pro-fee + facility fee). Unlike the
    # DRG/RAF/anesthesia stages it never alters routing: the clinical coding is what gets
    # routed; facility-estimate gaps are traced on the card, not punished.
    if enc.pos in ("22", "23") and accepted:
        step("6", "Facility APC/OPPS")
        say("OPPS Facility Pricer",
            "pricing the facility side — Addendum-B status indicators, packaging, discounting…", "tool")
        acc_codes = [{"code_system": cr.code_system, "code": cr.code} for cr in accepted]
        pr = apc.price(db, acc_codes)
        db.add(models.ApcResult(
            run_id=run.id, encounter_id=enc.id, lines=pr["lines"], packaged=pr["packaged"],
            not_covered=pr["not_covered"], facility_total=pr["facility_total"],
            trace=pr["trace"], resolved=pr["resolved"],
        ))
        log.append({"stage": "6_apc", "title": "Facility APC / OPPS Pricing", "result": pr})
        _audit(db, run, "6_apc", "facility_priced",
               {"facility_total": pr["facility_total"], "lines": len(pr["lines"]),
                "packaged": len(pr["packaged"]), "resolved": pr["resolved"]})
        say("OPPS Facility Pricer",
            f"facility estimate ${pr['facility_total']:.2f} · {len(pr['lines'])} payable · "
            f"{len(pr['packaged'])} packaged"
            + (f" · {len(pr['not_covered'])} outside curated subset" if pr["not_covered"] else ""),
            "good" if pr["resolved"] else "warn")

    calibration_log = {
        "stage": "5_calibration",
        "title": "Confidence Calibration & Routing",
        "routing_confidence": routing_overall,
        "overall_confidence": display_overall,
        "accepted": len(accepted),
        "needs_review": len(needs_review),
        "rejected": len(rejected),
        "bounded_autonomy": bounded,
        "missing_required_code_families_for_stb": missing_required,
        "thresholds": {"STB": stb_t, "QA": qa_t},
    }
    log.append(calibration_log)

    def finalize_lane(lane: str, reason: str):
        final_overall = _lane_adjusted_overall_confidence(lane, accepted, needs_review, confidence_penalties)
        run.overall_confidence = final_overall
        run.accuracy_estimate = final_overall  # calibrated estimate; true accuracy comes from the eval harness
        calibration_log["lane"] = lane
        calibration_log["overall_confidence"] = final_overall
        calibration_log["confidence_penalties"] = confidence_penalties
        _audit(
            db,
            run,
            "5_calibration",
            "calibrated",
            {"routing_overall": routing_overall, "overall": final_overall, "bounded": bounded, "lane": lane},
        )
        return finish(lane, reason)

    if not accepted or rejected:
        return finalize_lane("MANUAL", "Rejected/uncitable candidates present - human coding required"
                             if rejected else "No defensible codes - human coding required")
    if missing_required:
        reason = _missing_required_code_family_reason(missing_required, persisted)
        _audit(db, run, "5_calibration", "missing_required_code_families",
               {"specialty": enc.specialty, "missing": missing_required})
        return finalize_lane("MANUAL", reason)
    if bounded or needs_review:
        return finalize_lane("QA", "; ".join(bounded) or _needs_review_reason(needs_review))
    if routing_overall >= stb_t:
        return finalize_lane("STB", f"All gates passed; calibrated confidence {routing_overall:.2f} >= {stb_t}")
    if routing_overall >= qa_t:
        return finalize_lane("QA", f"Calibrated confidence {routing_overall:.2f} in QA band")
    return finalize_lane("MANUAL", f"Calibrated confidence {routing_overall:.2f} below QA threshold")


def cdi_scan(db: Session, encounter_id: str, emit=None) -> list[models.CdiQuery]:
    """Run the CDI agent on the latest coded run; persist drafted physician queries.
    Replaces any prior OPEN (unanswered) queries for this encounter."""
    emit = emit or (lambda *a, **k: None)

    def say(actor: str, msg: str, level: str = "info") -> None:
        emit({"type": "log", "actor": actor, "msg": msg, "level": level, "ts": _now().isoformat()})

    enc = db.get(models.Encounter, encounter_id)
    if enc is None:
        raise ValueError("encounter not found")
    cfg = config_store.all_config(db)
    llmc = cfg.get("llm")
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
    # The CDI agent gets the same privacy-guarded copy as the coding agent.
    chart_for_model = enc.chart_text
    if cfg.get("privacy", {}).get("mask_identifiers", True):
        chart_for_model, cdi_pii = pii.mask_identifiers(
            enc.chart_text, known_name=enc.patient_name, known_mrn=enc.mrn)
        if cdi_pii:
            say("Privacy Guard", pii.summary(cdi_pii), "good")
    numbered, _ = _number_chart(chart_for_model)
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

