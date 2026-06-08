"""Dashboard, knowledge-graph view, reference data, learning log, eval harness."""
from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..db import get_db
from ..llm.client import LLMUnavailable
from ..pipeline import orchestrator

router = APIRouter()
HIDDEN = "__golden__"


# --- Dashboard -------------------------------------------------------------
@router.get("/dashboard/stats")
def dashboard(db: Session = Depends(get_db)) -> dict:
    encs = db.scalars(select(models.Encounter).where(models.Encounter.client != HIDDEN)).all()
    total = len(encs)
    lanes = {"STB": 0, "QA": 0, "MANUAL": 0}
    accs, lats = [], []
    by_spec: dict[str, dict] = {}
    coded = 0
    eligible = 0           # charts that passed Stage-0 eligibility (auto-coding candidates)
    eligible_excluded = 0  # routed to manual purely because they were ineligible
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

    # STB rate is measured over eligible (auto-coding-candidate) charts — ineligible charts
    # were never candidates for automation, so they don't count against the automation rate.
    stb_rate = round(lanes["STB"] / eligible, 3) if eligible else 0.0
    avg_acc = round(sum(accs) / len(accs), 3) if accs else 0.0
    manual_reduction = round((lanes["STB"] + 0.5 * lanes["QA"]) / coded, 3) if coded else 0.0
    for s in by_spec.values():
        s["avg_accuracy"] = round(sum(s["acc"]) / len(s["acc"]), 3) if s["acc"] else 0.0
        s.pop("acc")
        s["stb_rate"] = round(s["STB"] / s["eligible"], 3) if s["eligible"] else 0.0

    return {
        "total_encounters": total, "coded": coded, "eligible": eligible,
        "eligible_excluded": eligible_excluded,
        "stb_count": lanes["STB"], "qa_count": lanes["QA"], "manual_count": lanes["MANUAL"],
        "stb_rate": stb_rate, "avg_accuracy": avg_acc,
        "avg_latency_ms": int(sum(lats) / len(lats)) if lats else 0,
        "manual_effort_reduction": manual_reduction,
        "by_specialty": list(by_spec.values()),
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


def _modality_from_text(t: str) -> str:
    tl = t.lower()
    if "mri" in tl:
        return "MRI"
    if "ct " in tl or "ct," in tl or "ct of" in tl:
        return "CT"
    if "x-ray" in tl or "radiograph" in tl:
        return "XR"
    return ""


@router.post("/eval/run")
def eval_run(db: Session = Depends(get_db)) -> dict:
    if not settings.llm_available:
        raise LLMUnavailable("LLM not configured — eval requires the reasoning model")

    golden = db.scalars(select(models.GoldenCase)).all()
    # clean previous hidden eval encounters
    old = db.scalars(select(models.Encounter).where(models.Encounter.client == HIDDEN)).all()
    for e in old:
        db.execute(delete(models.CodingRun).where(models.CodingRun.encounter_id == e.id))
        db.delete(e)
    db.commit()

    results = []
    agg: dict[str, dict] = {}
    for i, g in enumerate(golden):
        enc = models.Encounter(
            mrn=f"GOLD{i:04d}", patient_name="Golden Case", age=55, sex="F",
            specialty=g.specialty, modality=_modality_from_text(g.chart_text),
            encounter_type="established" if g.specialty == "E&M" else "",
            payer="Medicare", pos="11" if g.specialty == "E&M" else "22",
            dos="2026-04-15", client=HIDDEN, source_system="eval", chart_text=g.chart_text,
            scenario="golden", status="NEW",
        )
        db.add(enc)
        db.flush()
        try:
            run = orchestrator.run_coding(db, enc.id)
        except LLMUnavailable:
            raise
        pred_icd = {c.code for c in run.codes if c.code_system == "ICD10CM" and c.status == "accepted"}
        pred_cpt = {c.code for c in run.codes if c.code_system in ("CPT", "HCPCS") and c.status == "accepted"}
        truth_icd = set(g.truth.get("icd", []))
        truth_cpt = set(g.truth.get("cpt", []))
        icd_ok = bool(truth_icd & pred_icd) if truth_icd else True
        cpt_ok = bool(truth_cpt & pred_cpt) if truth_cpt else True
        chart_ok = icd_ok and cpt_ok
        cit_ok = all(c.conf_doc_match >= 0.5 for c in run.codes if c.status == "accepted") if run.codes else False

        a = agg.setdefault(g.specialty, {"specialty": g.specialty, "n": 0, "icd": 0, "cpt": 0, "chart": 0, "cit": 0, "stb": 0, "irr": []})
        a["n"] += 1
        a["icd"] += int(icd_ok)
        a["cpt"] += int(cpt_ok)
        a["chart"] += int(chart_ok)
        a["cit"] += int(cit_ok)
        a["stb"] += int(run.routing_lane == "STB")
        a["irr"].append(g.irr)
        results.append({
            "specialty": g.specialty, "truth": g.truth,
            "predicted_icd": sorted(pred_icd), "predicted_cpt": sorted(pred_cpt),
            "icd_ok": icd_ok, "cpt_ok": cpt_ok, "chart_ok": chart_ok, "lane": run.routing_lane,
        })

    by_spec = []
    for a in agg.values():
        n = a["n"]
        by_spec.append({
            "specialty": a["specialty"], "size": n,
            "icd_accuracy": round(a["icd"] / n, 3),
            "cpt_accuracy": round(a["cpt"] / n, 3),
            "chart_accuracy": round(a["chart"] / n, 3),
            "citation_validity": round(a["cit"] / n, 3),
            "stb_share": round(a["stb"] / n, 3),
            "irr_ceiling": round(sum(a["irr"]) / len(a["irr"]), 3),
        })
    db.commit()
    overall_chart = round(sum(r["chart_ok"] for r in results) / len(results), 3) if results else 0.0
    return {"overall_chart_accuracy": overall_chart, "by_specialty": by_spec, "cases": results}
