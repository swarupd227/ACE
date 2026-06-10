"""Dashboard, knowledge-graph view, reference data, learning log, eval harness."""
from __future__ import annotations

import re

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..db import SessionLocal, get_db
from ..llm.client import LLMUnavailable
from ..pipeline import orchestrator
from ._admin_audit import Actor, get_actor, log_change
from ._sse import sse_response

router = APIRouter()
HIDDEN = "__golden__"

# Reference manual coding turnaround per specialty (minutes/chart). Operational benchmarks,
# configurable per client — used to quantify the AI-assisted TAT reduction.
MANUAL_TAT_BASELINE = {"Radiology": 6.0, "E&M": 9.0, "ED": 12.0, "Pathology": 8.0, "Surgical": 14.0}
# AI-assisted coding TAT per lane during the 100%-audit early rollout (conservative): even STB charts
# get a human audit touch initially, so TAT is reduced but not eliminated. The reduction grows as audit
# sampling tapers post-certification (see maturity pathway). STB = AI draft + quick audit; QA = auditor
# verifies an AI draft; MANUAL = AI pre-extraction assists a full human coder.
_AI_TAT = {"STB": lambda b: 0.40 * b, "QA": lambda b: 0.65 * b, "MANUAL": lambda b: 0.95 * b}


def _maturity_stage(stb_rate: float) -> str:
    if stb_rate >= 0.80:
        return "Autonomous (target)"
    if stb_rate >= 0.60:
        return "Approaching autonomous"
    if stb_rate >= 0.30:
        return "Scaling"
    return "Foundation / shadow"


# --- Dashboard -------------------------------------------------------------
@router.get("/dashboard/stats")
def dashboard(db: Session = Depends(get_db)) -> dict:
    encs = db.scalars(select(models.Encounter).where(models.Encounter.client != HIDDEN)).all()
    total = len(encs)
    lanes = {"STB": 0, "QA": 0, "MANUAL": 0}
    accs, lats = [], []
    tat_base, tat_asst = 0.0, 0.0
    by_spec: dict[str, dict] = {}
    coded = 0
    eligible = 0           # charts that passed Stage-0 eligibility (auto-coding candidates)
    eligible_excluded = 0  # routed to manual purely because they were ineligible
    tokens_in = tokens_out = llm_calls = override_charts = 0
    by_model: dict[str, dict] = {}
    for e in encs:
        run = db.scalars(
            select(models.CodingRun).where(models.CodingRun.encounter_id == e.id)
            .order_by(models.CodingRun.started_at.desc()).limit(1)
        ).first()
        spec = by_spec.setdefault(e.specialty, {"specialty": e.specialty, "total": 0, "eligible": 0, "STB": 0, "QA": 0, "MANUAL": 0, "acc": []})
        spec["total"] += 1
        if run and run.routing_lane:
            coded += 1
            is_eligible = (run.eligibility or {}).get("eligible", True)
            if is_eligible:
                eligible += 1
                spec["eligible"] += 1
            else:
                eligible_excluded += 1
            lanes[run.routing_lane] = lanes.get(run.routing_lane, 0) + 1
            spec[run.routing_lane] = spec.get(run.routing_lane, 0) + 1
            if run.routing_lane != "MANUAL":
                accs.append(run.overall_confidence)
                spec["acc"].append(run.overall_confidence)
            lats.append(run.latency_ms)
            b = MANUAL_TAT_BASELINE.get(e.specialty, 8.0)
            tat_base += b
            tat_asst += _AI_TAT.get(run.routing_lane, lambda x: x)(b)
            # --- model performance (real usage captured per run) ---
            tokens_in += run.input_tokens or 0
            tokens_out += run.output_tokens or 0
            llm_calls += run.llm_calls or 0
            overridden = any(c.is_overridden for c in run.codes)
            if overridden:
                override_charts += 1
            mv = run.model_version or "unknown"
            m = by_model.setdefault(mv, {"model": mv, "charts": 0, "stb": 0, "conf": [], "lat": [], "tin": 0, "tout": 0, "ovr": 0})
            m["charts"] += 1
            m["tin"] += run.input_tokens or 0
            m["tout"] += run.output_tokens or 0
            m["lat"].append(run.latency_ms)
            if run.routing_lane == "STB":
                m["stb"] += 1
            if run.routing_lane != "MANUAL":
                m["conf"].append(run.overall_confidence)
            if overridden:
                m["ovr"] += 1

    # STB rate is measured over eligible (auto-coding-candidate) charts — ineligible charts
    # were never candidates for automation, so they don't count against the automation rate.
    stb_rate = round(lanes["STB"] / eligible, 3) if eligible else 0.0
    avg_acc = round(sum(accs) / len(accs), 3) if accs else 0.0
    manual_reduction = round((lanes["STB"] + 0.5 * lanes["QA"]) / coded, 3) if coded else 0.0
    for s in by_spec.values():
        s["avg_accuracy"] = round(sum(s["acc"]) / len(s["acc"]), 3) if s["acc"] else 0.0
        s.pop("acc")
        s["stb_rate"] = round(s["STB"] / s["eligible"], 3) if s["eligible"] else 0.0

    # --- model performance + drift surface (all from real run data) ---
    def _p95(xs: list) -> int:
        if not xs:
            return 0
        s = sorted(xs)
        return int(s[min(len(s) - 1, int(round(0.95 * (len(s) - 1))))])

    by_model_out = []
    for m in by_model.values():
        n = m["charts"]
        by_model_out.append({
            "model": m["model"], "charts": n,
            "stb_rate": round(m["stb"] / n, 3) if n else 0.0,
            "avg_confidence": round(sum(m["conf"]) / len(m["conf"]), 3) if m["conf"] else 0.0,
            "avg_latency_ms": int(sum(m["lat"]) / len(m["lat"])) if m["lat"] else 0,
            "avg_tokens": int((m["tin"] + m["tout"]) / n) if n else 0,
            "override_rate": round(m["ovr"] / n, 3) if n else 0.0,
        })
    by_model_out.sort(key=lambda x: x["charts"], reverse=True)
    from .. import config_store as _cs
    from ..llm import client as _llm
    total_tokens = tokens_in + tokens_out
    model_performance = {
        "active_model": _llm.model_version(_cs.all_config(db).get("llm")),
        "input_tokens": tokens_in, "output_tokens": tokens_out, "total_tokens": total_tokens,
        "llm_calls": llm_calls,
        "avg_tokens_per_chart": int(total_tokens / coded) if coded else 0,
        "avg_calls_per_chart": round(llm_calls / coded, 1) if coded else 0.0,
        "avg_latency_ms": int(sum(lats) / len(lats)) if lats else 0,
        "p95_latency_ms": _p95(lats),
        "avg_confidence": avg_acc,
        "override_rate": round(override_charts / coded, 3) if coded else 0.0,
        "by_model": by_model_out,
    }

    return {
        "total_encounters": total, "coded": coded, "eligible": eligible,
        "eligible_excluded": eligible_excluded,
        "stb_count": lanes["STB"], "qa_count": lanes["QA"], "manual_count": lanes["MANUAL"],
        "stb_rate": stb_rate, "avg_accuracy": avg_acc,
        "avg_latency_ms": int(sum(lats) / len(lats)) if lats else 0,
        "manual_effort_reduction": manual_reduction,
        "exception_rate": round(lanes["MANUAL"] / coded, 3) if coded else 0.0,
        "tat": {
            "baseline_min": round(tat_base / coded, 1) if coded else 0.0,
            "assisted_min": round(tat_asst / coded, 1) if coded else 0.0,
            "reduction_pct": round(1 - tat_asst / tat_base, 3) if tat_base else 0.0,
        },
        "maturity": {
            "stage": _maturity_stage(stb_rate), "stb_rate": stb_rate, "target": 0.80,
            "stages": ["Foundation / shadow", "Scaling", "Approaching autonomous", "Autonomous (target)"],
        },
        "by_specialty": list(by_spec.values()),
        "model_performance": model_performance,
    }


# --- Knowledge graph view --------------------------------------------------
@router.get("/kg/graph")
def kg_graph(db: Session = Depends(get_db)) -> dict:
    concepts = db.scalars(select(models.OntologyConcept)).all()
    edges = db.scalars(select(models.OntologyEdge)).all()
    policies = db.scalars(select(models.PayerPolicy)).all()

    nodes = []
    links = []
    for c in concepts:
        nodes.append({"id": c.cui, "label": c.name, "type": "concept", "semantic_type": c.semantic_type})
        for m in c.maps_to:
            code_id = f"{m['system']}:{m['code']}"
            nodes.append({"id": code_id, "label": m["code"], "type": "code", "system": m["system"]})
            links.append({"source": c.cui, "target": code_id, "rel": "maps_to"})
    for e in edges:
        links.append({"source": e.src_cui, "target": e.dst_cui, "rel": e.rel})
    seen_payers = set()
    for p in policies:
        if p.payer not in seen_payers:
            nodes.append({"id": f"payer:{p.payer}", "label": p.payer, "type": "payer"})
            seen_payers.add(p.payer)
        code_id = f"CPT:{p.code}"
        nodes.append({"id": code_id, "label": p.code, "type": "code", "system": "CPT"})
        links.append({"source": f"payer:{p.payer}", "target": code_id, "rel": "policy",
                      "detail": p.medical_necessity, "requires_auth": p.requires_auth})

    # de-dup nodes by id
    uniq = {n["id"]: n for n in nodes}
    return {"nodes": list(uniq.values()), "links": links}


@router.get("/reference/summary")
def reference_summary(db: Session = Depends(get_db)) -> dict:
    def count(model):
        return db.scalar(select(func.count()).select_from(model))

    systems = db.execute(
        select(models.ReferenceCode.code_system, func.count())
        .group_by(models.ReferenceCode.code_system)
    ).all()
    return {
        "code_systems": {s: c for s, c in systems},
        "ncci_edits": count(models.NcciEdit),
        "mue_limits": count(models.MueLimit),
        "modifiers": count(models.ModifierRule),
        "payer_policies": count(models.PayerPolicy),
        "guidelines": count(models.GuidelineChunk),
        "ontology_concepts": count(models.OntologyConcept),
    }


@router.get("/guidelines")
def guidelines(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(models.GuidelineChunk)).all()
    return [{"source": g.source, "section": g.section, "text": g.text, "specialty": g.specialty} for g in rows]


# --- Closed-loop learning --------------------------------------------------
@router.get("/learning")
def learning(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(models.LearningExample).order_by(models.LearningExample.created_at.desc())).all()
    return [
        {"id": le.id, "specialty": le.specialty, "pattern_key": le.pattern_key,
         "wrong_code": le.wrong_code, "correct_code": le.correct_code, "code_system": le.code_system,
         "reason": le.reason, "applied": le.applied, "created_at": le.created_at.isoformat()}
        for le in rows
    ]


class LearningPatch(BaseModel):
    applied: bool


@router.patch("/learning/{ex_id}")
def patch_learning(ex_id: str, body: LearningPatch, db: Session = Depends(get_db)) -> dict:
    le = db.get(models.LearningExample, ex_id)
    if le is None:
        raise HTTPException(404, "learning example not found")
    le.applied = body.applied  # graph_rag only retrieves applied==True exemplars → affects coding
    db.commit()
    return {"id": le.id, "applied": le.applied}


@router.delete("/learning/{ex_id}")
def delete_learning(ex_id: str, db: Session = Depends(get_db)) -> dict:
    le = db.get(models.LearningExample, ex_id)
    if le is None:
        raise HTTPException(404, "learning example not found")
    db.delete(le)
    db.commit()
    return {"deleted": ex_id}


# --- Evaluation harness ----------------------------------------------------
@router.get("/eval/summary")
def eval_summary(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(models.GoldenCase)).all()
    by_spec: dict[str, dict] = {}
    for g in rows:
        s = by_spec.setdefault(g.specialty, {"specialty": g.specialty, "size": 0, "irr": []})
        s["size"] += 1
        s["irr"].append(g.irr)
    for s in by_spec.values():
        s["irr_ceiling"] = round(sum(s["irr"]) / len(s["irr"]), 3)
        s.pop("irr")
    return {"golden_sets": list(by_spec.values()), "total": len(rows)}


# --- Golden-set management (admins curate the eval truth set) ---------------
def _golden(g: models.GoldenCase) -> dict:
    return {"id": g.id, "specialty": g.specialty, "chart_text": g.chart_text,
            "truth": g.truth, "irr": g.irr, "ambiguous": g.ambiguous}


@router.get("/eval/golden")
def list_golden(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(models.GoldenCase).order_by(models.GoldenCase.specialty, models.GoldenCase.id)).all()
    return [_golden(g) for g in rows]


class GoldenIn(BaseModel):
    specialty: str
    chart_text: str
    truth: dict = {}        # {"icd": [...], "cpt": [...]}
    irr: float = 0.9
    ambiguous: bool = False


@router.post("/eval/golden")
def create_golden(body: GoldenIn, db: Session = Depends(get_db),
                  actor: Actor = Depends(get_actor)) -> dict:
    if len(body.chart_text.strip()) < 40:
        raise HTTPException(400, "golden chart_text too short to be a real case")
    g = models.GoldenCase(specialty=body.specialty, chart_text=body.chart_text.strip(),
                          truth=body.truth, irr=body.irr, ambiguous=body.ambiguous)
    db.add(g)
    log_change(db, actor, "golden", "create", body.specialty, {"truth": body.truth})
    db.commit()
    db.refresh(g)
    return _golden(g)


@router.put("/eval/golden/{gid}")
def update_golden(gid: int, body: GoldenIn, db: Session = Depends(get_db),
                  actor: Actor = Depends(get_actor)) -> dict:
    g = db.get(models.GoldenCase, gid)
    if g is None:
        raise HTTPException(404, "golden case not found")
    g.specialty = body.specialty
    g.chart_text = body.chart_text.strip() or g.chart_text
    g.truth = body.truth
    g.irr = body.irr
    g.ambiguous = body.ambiguous
    log_change(db, actor, "golden", "update", f"{g.specialty}#{g.id}", {"truth": g.truth})
    db.commit()
    db.refresh(g)
    return _golden(g)


@router.delete("/eval/golden/{gid}")
def delete_golden(gid: int, db: Session = Depends(get_db),
                  actor: Actor = Depends(get_actor)) -> dict:
    g = db.get(models.GoldenCase, gid)
    if g is None:
        raise HTTPException(404, "golden case not found")
    log_change(db, actor, "golden", "delete", f"{g.specialty}#{g.id}", {})
    db.delete(g)
    db.commit()
    return {"deleted": gid}


def _modality_from_text(t: str) -> str:
    tl = t.lower()
    if "mri" in tl:
        return "MRI"
    if "ct " in tl or "ct," in tl or "ct of" in tl:
        return "CT"
    if "x-ray" in tl or "radiograph" in tl:
        return "XR"
    return ""


def _eval_core(db: Session, emit) -> dict:
    """Run the live pipeline over the frozen golden set, emitting per-case
    progress. Returns the aggregate summary. `emit(dict)` streams SSE events."""
    from .. import config_store
    from ..llm import client as _llm

    def say(actor, msg, level="info"):
        emit({"type": "log", "actor": actor, "msg": msg, "level": level,
              "ts": datetime.now(timezone.utc).isoformat()})

    if not _llm.llm_available(config_store.all_config(db).get("llm")):
        raise LLMUnavailable("LLM not configured — eval requires the reasoning model")

    golden = db.scalars(select(models.GoldenCase)).all()
    # clean previous hidden eval encounters
    old = db.scalars(select(models.Encounter).where(models.Encounter.client == HIDDEN)).all()
    for e in old:
        # bulk DELETE bypasses the ORM relationship cascade, so clear children first
        # (code_results FK -> coding_runs FK -> encounters) to avoid a FK violation.
        run_ids = db.scalars(
            select(models.CodingRun.id).where(models.CodingRun.encounter_id == e.id)
        ).all()
        if run_ids:
            db.execute(delete(models.CodeResult).where(models.CodeResult.run_id.in_(run_ids)))
            db.execute(delete(models.DrgResult).where(models.DrgResult.run_id.in_(run_ids)))
            db.execute(delete(models.HccResult).where(models.HccResult.run_id.in_(run_ids)))
            db.execute(delete(models.AnesResult).where(models.AnesResult.run_id.in_(run_ids)))
            db.execute(delete(models.ApcResult).where(models.ApcResult.run_id.in_(run_ids)))
        db.execute(delete(models.CodingRun).where(models.CodingRun.encounter_id == e.id))
        db.delete(e)
    db.commit()

    total = len(golden)
    say("Evaluation Harness", f"scoring {total} adjudicated golden case(s) against the live pipeline…", "head")
    emit({"type": "progress", "done": 0, "total": total})
    results = []
    agg: dict[str, dict] = {}
    for i, g in enumerate(golden):
        # RAF depends on demographics, so risk-adjustment golden cases run as a fixed
        # 72-year-old male (the band the golden truth RAFs were adjudicated against).
        is_hcc = g.specialty == "HCC / Risk Adjustment"
        enc = models.Encounter(
            mrn=f"GOLD{i:04d}", patient_name="Golden Case",
            age=72 if is_hcc else 55, sex="M" if is_hcc else "F",
            specialty=g.specialty, modality=_modality_from_text(g.chart_text),
            encounter_type="established" if g.specialty == "E&M" else "",
            payer="Medicare Advantage" if is_hcc else "Medicare",
            pos=("11" if g.specialty == "E&M" or is_hcc
                 else "21" if g.specialty == "Inpatient (DRG)" else "22"),
            dos="2026-04-15", client=HIDDEN, source_system="eval", chart_text=g.chart_text,
            scenario="golden", status="NEW",
        )
        db.add(enc)
        db.flush()
        run = orchestrator.run_coding(db, enc.id)
        pred_icd = {c.code for c in run.codes if c.code_system == "ICD10CM" and c.status == "accepted"}
        pred_cpt = {c.code for c in run.codes if c.code_system in ("CPT", "HCPCS") and c.status == "accepted"}
        pred_pcs = {c.code for c in run.codes if c.code_system == "ICD10PCS" and c.status == "accepted"}
        truth_icd = set(g.truth.get("icd", []))
        truth_cpt = set(g.truth.get("cpt", []))
        truth_pcs = set(g.truth.get("pcs", []))
        truth_drg = g.truth.get("drg", "")
        pred_drg = run.drg_result.drg if run.drg_result else ""
        truth_raf = g.truth.get("raf")
        pred_raf = run.hcc_result.raf if run.hcc_result else None
        truth_units = g.truth.get("units")
        pred_units = run.anes_result.total_units if run.anes_result else None
        truth_fac = g.truth.get("facility_total")
        pred_fac = run.apc_result.facility_total if run.apc_result else None
        icd_ok = bool(truth_icd & pred_icd) if truth_icd else True
        cpt_ok = bool(truth_cpt & pred_cpt) if truth_cpt else True
        pcs_ok = bool(truth_pcs & pred_pcs) if truth_pcs else True
        drg_ok = (pred_drg == truth_drg) if truth_drg else True
        raf_ok = (pred_raf is not None and abs(pred_raf - truth_raf) <= 0.005) if truth_raf else True
        units_ok = (pred_units is not None and abs(pred_units - truth_units) <= 0.1) if truth_units else True
        fac_ok = (pred_fac is not None and abs(pred_fac - truth_fac) <= 0.01) if truth_fac else True
        chart_ok = icd_ok and cpt_ok and pcs_ok and drg_ok and raf_ok and units_ok and fac_ok
        cit_ok = all(c.conf_doc_match >= 0.5 for c in run.codes if c.status == "accepted") if run.codes else False

        a = agg.setdefault(g.specialty, {"specialty": g.specialty, "n": 0, "icd": 0, "cpt": 0, "chart": 0, "cit": 0, "stb": 0, "irr": [], "drg": 0, "drg_n": 0, "raf": 0, "raf_n": 0})
        a["n"] += 1
        a["icd"] += int(icd_ok)
        a["cpt"] += int(cpt_ok)
        a["chart"] += int(chart_ok)
        a["cit"] += int(cit_ok)
        a["stb"] += int(run.routing_lane == "STB")
        a["irr"].append(g.irr)
        if truth_drg:
            a["drg_n"] += 1
            a["drg"] += int(drg_ok)
        if truth_raf:
            a["raf_n"] += 1
            a["raf"] += int(raf_ok)
        if truth_units:
            a.setdefault("units_n", 0); a.setdefault("units", 0)
            a["units_n"] += 1
            a["units"] += int(units_ok)
        if truth_fac:
            a.setdefault("fac_n", 0); a.setdefault("fac", 0)
            a["fac_n"] += 1
            a["fac"] += int(fac_ok)
        results.append({
            "specialty": g.specialty, "truth": g.truth,
            "predicted_icd": sorted(pred_icd), "predicted_cpt": sorted(pred_cpt or pred_pcs),
            "predicted_drg": pred_drg, "drg_ok": drg_ok,
            "predicted_raf": pred_raf, "raf_ok": raf_ok,
            "predicted_units": pred_units, "units_ok": units_ok,
            "icd_ok": icd_ok, "cpt_ok": cpt_ok, "chart_ok": chart_ok, "lane": run.routing_lane,
        })
        pred = (sorted(pred_cpt) + sorted(pred_pcs) + sorted(pred_icd)
                + ([f"DRG {pred_drg}"] if pred_drg else [])
                + ([f"RAF {pred_raf}"] if pred_raf is not None else [])
                + ([f"{pred_units}u"] if pred_units is not None else [])) or ["(none)"]
        say(f"  case {i + 1}/{total} · {g.specialty}",
            f"predicted {', '.join(pred)} — {'PASS' if chart_ok else 'MISS'}",
            "good" if chart_ok else "bad")
        emit({"type": "progress", "done": i + 1, "total": total})

    by_spec = []
    for a in agg.values():
        n = a["n"]
        row = {
            "specialty": a["specialty"], "size": n,
            "icd_accuracy": round(a["icd"] / n, 3),
            "cpt_accuracy": round(a["cpt"] / n, 3),
            "chart_accuracy": round(a["chart"] / n, 3),
            "citation_validity": round(a["cit"] / n, 3),
            "stb_share": round(a["stb"] / n, 3),
            "irr_ceiling": round(sum(a["irr"]) / len(a["irr"]), 3),
        }
        if a.get("drg_n"):
            row["drg_accuracy"] = round(a["drg"] / a["drg_n"], 3)
        if a.get("raf_n"):
            row["raf_accuracy"] = round(a["raf"] / a["raf_n"], 3)
        if a.get("units_n"):
            row["units_accuracy"] = round(a["units"] / a["units_n"], 3)
        if a.get("fac_n"):
            row["facility_accuracy"] = round(a["fac"] / a["fac_n"], 3)
        by_spec.append(row)
    db.commit()
    overall_chart = round(sum(r["chart_ok"] for r in results) / len(results), 3) if results else 0.0
    say("Evaluation Harness", f"done · overall chart accuracy {round(overall_chart * 100)}% on {len(results)} case(s)", "good")
    return {"overall_chart_accuracy": overall_chart, "by_specialty": by_spec, "cases": results}


@router.post("/eval/run")
def eval_run(db: Session = Depends(get_db)) -> dict:
    """Synchronous eval (kept for API/back-compat); the UI uses the streaming variant."""
    return _eval_core(db, lambda ev: None)


@router.get("/eval/run/stream")
def eval_run_stream() -> StreamingResponse:
    """Run the eval harness and STREAM per-case progress as SSE (so the UI shows
    live progress instead of an opaque spinner)."""
    def work(emit):
        db = SessionLocal()
        try:
            summary = _eval_core(db, emit)
            emit({"type": "done", **summary})
        finally:
            db.close()

    return sse_response(work)


# --- Global audit timeline -------------------------------------------------
# One unified, filterable trail that merges the two append-only ledgers:
#   • coding  — per-encounter pipeline/decision events (audit_ledger / AuditEntry)
#   • governance — admin & config changes (config_audit / ConfigAudit)
# This is the compliance "single pane of glass"; the per-chart Audit packet and the
# Admin Change Log remain as the scoped drill-downs.
@router.get("/audit/global")
def global_audit(
    source: str = "",      # "" (all) | coding | governance
    q: str = "",           # free-text over actor / category / action / target / detail
    encounter: str = "",   # MRN or encounter_id substring
    limit: int = 250,
    db: Session = Depends(get_db),
) -> dict:
    events: list[dict] = []

    if source in ("", "coding"):
        rows = db.scalars(
            select(models.AuditEntry).order_by(models.AuditEntry.ts.desc()).limit(1000)
        ).all()
        enc_ids = {r.encounter_id for r in rows if r.encounter_id}
        encs = {}
        if enc_ids:
            encs = {
                e.id: e for e in db.scalars(
                    select(models.Encounter).where(models.Encounter.id.in_(enc_ids))
                ).all()
            }
        for r in rows:
            e = encs.get(r.encounter_id)
            events.append({
                "id": r.id,
                "ts": r.ts.isoformat(),
                "source": "coding",
                "actor": r.actor or "system",
                "role": "",
                "category": r.stage,
                "action": r.event,
                "target": (e.mrn if e else r.encounter_id) or "",
                "specialty": (e.specialty if e else ""),
                "encounter_id": r.encounter_id or "",
                "run_id": r.run_id or "",
                "model_version": r.model_version or "",
                "detail": r.detail or {},
            })

    if source in ("", "governance"):
        rows = db.scalars(
            select(models.ConfigAudit).order_by(models.ConfigAudit.at.desc()).limit(1000)
        ).all()
        for r in rows:
            events.append({
                "id": r.id,
                "ts": r.at.isoformat(),
                "source": "governance",
                "actor": r.actor or "system",
                "role": r.role or "",
                "category": r.area,
                "action": r.action,
                "target": r.target or "",
                "specialty": "",
                "encounter_id": "",
                "run_id": "",
                "model_version": "",
                "detail": r.detail or {},
            })

    if encounter:
        el = encounter.lower()
        events = [
            ev for ev in events
            if el in (ev["target"] or "").lower() or el in (ev["encounter_id"] or "").lower()
        ]
    if q:
        ql = q.lower()
        def _hay(ev: dict) -> str:
            return " ".join([
                ev["actor"], ev["category"], ev["action"], ev["target"],
                ev["role"], ev["model_version"], str(ev["detail"]),
            ]).lower()
        events = [ev for ev in events if ql in _hay(ev)]

    events.sort(key=lambda ev: ev["ts"], reverse=True)
    matched = len(events)

    # Facets computed over the full matched set (so the chips are honest counts).
    def _tally(key: str) -> dict:
        out: dict[str, int] = {}
        for ev in events:
            out[ev[key]] = out.get(ev[key], 0) + 1
        return dict(sorted(out.items(), key=lambda kv: kv[1], reverse=True))

    facets = {
        "by_source": _tally("source"),
        "by_category": _tally("category"),
        "by_actor": _tally("actor"),
    }
    summary = {
        "matched": matched,
        "coding_events": facets["by_source"].get("coding", 0),
        "governance_events": facets["by_source"].get("governance", 0),
        "distinct_actors": len(facets["by_actor"]),
        "newest": events[0]["ts"] if events else None,
        "oldest": events[-1]["ts"] if events else None,
    }
    return {"events": events[:limit], "summary": summary, "facets": facets}
