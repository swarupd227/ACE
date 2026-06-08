"""Run the coding pipeline; human-in-the-loop override/accept; audit & learning."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ..knowledge import graph_rag
from ..pipeline import orchestrator
from pydantic import BaseModel

from ..schemas import AcceptRequest, OverrideRequest
from ._serialize import run_to_dict

router = APIRouter()
HIDDEN_CLIENT = "__golden__"


class ReassignRequest(BaseModel):
    lane: str  # STB | QA | MANUAL
    reason: str = ""
    actor: str = "coder:demo"
    assigned_to: str = ""


class EscalateRequest(BaseModel):
    to: str = "Senior Coder / CDI"
    reason: str = ""
    actor: str = "coder:demo"


@router.post("/runs/{run_id}/reassign")
def reassign_run(run_id: str, body: ReassignRequest, db: Session = Depends(get_db)) -> dict:
    run = db.get(models.CodingRun, run_id)
    if run is None:
        raise HTTPException(404, "run not found")
    if body.lane not in ("STB", "QA", "MANUAL"):
        raise HTTPException(400, "lane must be STB, QA, or MANUAL")
    prev = run.routing_lane
    run.routing_lane = body.lane
    run.routing_reason = f"Reassigned {prev}→{body.lane} by {body.actor}" + (f": {body.reason}" if body.reason else "")
    if body.assigned_to:
        run.assigned_to = body.assigned_to
    db.add(models.AuditEntry(run_id=run.id, encounter_id=run.encounter_id, stage="workflow",
                             actor=body.actor, event="reassigned",
                             detail={"from": prev, "to": body.lane, "reason": body.reason, "assigned_to": body.assigned_to}))
    db.commit()
    db.refresh(run)
    return run_to_dict(run)


@router.post("/runs/{run_id}/rollback")
def rollback_run(run_id: str, db: Session = Depends(get_db)) -> dict:
    """Revert all human edits (overrides, accepts, reassign, escalate) back to the original
    AI recommendation, deterministically, from the snapshot captured at coding time."""
    run = db.get(models.CodingRun, run_id)
    if run is None:
        raise HTTPException(404, "run not found")
    snap = run.ai_snapshot or {}
    if not snap:
        raise HTTPException(400, "no AI snapshot available for this run")

    by_id = {c["id"]: c for c in snap.get("codes", [])}
    for c in run.codes:
        s = by_id.get(c.id)
        if s:
            c.code = s["code"]
            c.description = s["description"]
            c.modifiers = s.get("modifiers", [])
            c.status = s.get("status", "accepted")
        c.is_overridden = False
        c.override_code = ""
        c.override_reason = ""
        c.accepted_by = ""

    run.routing_lane = snap.get("routing_lane", run.routing_lane)
    run.routing_reason = snap.get("routing_reason", run.routing_reason)
    run.overall_confidence = snap.get("overall_confidence", run.overall_confidence)
    run.escalated = False
    run.escalated_to = ""
    run.assigned_to = ""
    run.priority = "normal"
    db.add(models.AuditEntry(run_id=run.id, encounter_id=run.encounter_id, stage="workflow",
                             actor="coder:demo", event="rolled_back",
                             detail={"restored_lane": run.routing_lane}))
    db.commit()
    db.refresh(run)
    return run_to_dict(run)


@router.post("/runs/{run_id}/escalate")
def escalate_run(run_id: str, body: EscalateRequest, db: Session = Depends(get_db)) -> dict:
    run = db.get(models.CodingRun, run_id)
    if run is None:
        raise HTTPException(404, "run not found")
    run.escalated = True
    run.escalated_to = body.to
    run.priority = "high"
    db.add(models.AuditEntry(run_id=run.id, encounter_id=run.encounter_id, stage="workflow",
                             actor=body.actor, event="escalated",
                             detail={"to": body.to, "reason": body.reason}))
    db.commit()
    db.refresh(run)
    return run_to_dict(run)


@router.post("/encounters/{enc_id}/code")
def code_encounter(enc_id: str, db: Session = Depends(get_db)) -> dict:
    enc = db.get(models.Encounter, enc_id)
    if enc is None:
        raise HTTPException(404, "encounter not found")
    run = orchestrator.run_coding(db, enc_id)
    return run_to_dict(run)


@router.post("/coding/run-all")
def run_all(db: Session = Depends(get_db)) -> dict:
    # Code only NEW (uncoded) charts — so ingesting one chart and running codes just that one
    # (~25s) instead of re-coding the whole batch. A fresh reseed leaves everything NEW, so the
    # first run still codes all. To re-code an already-coded chart, use its per-row "Code" action.
    encs = db.scalars(
        select(models.Encounter).where(
            models.Encounter.client != HIDDEN_CLIENT, models.Encounter.status == "NEW"
        )
    ).all()
    lanes = {"STB": 0, "QA": 0, "MANUAL": 0}
    for e in encs:
        run = orchestrator.run_coding(db, e.id)
        lanes[run.routing_lane] = lanes.get(run.routing_lane, 0) + 1
    return {"coded": len(encs), "lanes": lanes}


@router.get("/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)) -> dict:
    run = db.get(models.CodingRun, run_id)
    if run is None:
        raise HTTPException(404, "run not found")
    return run_to_dict(run)


@router.get("/runs/{run_id}/audit")
def get_audit(run_id: str, db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(
        select(models.AuditEntry).where(models.AuditEntry.run_id == run_id)
        .order_by(models.AuditEntry.ts.asc())
    ).all()
    return [
        {"id": r.id, "stage": r.stage, "actor": r.actor, "event": r.event,
         "detail": r.detail, "model_version": r.model_version, "ts": r.ts.isoformat()}
        for r in rows
    ]


@router.post("/codes/{code_id}/accept")
def accept_code(code_id: str, body: AcceptRequest, db: Session = Depends(get_db)) -> dict:
    c = db.get(models.CodeResult, code_id)
    if c is None:
        raise HTTPException(404, "code not found")
    c.status = "accepted"
    c.accepted_by = body.coder_id
    db.add(models.AuditEntry(run_id=c.run_id, encounter_id=db.get(models.CodingRun, c.run_id).encounter_id,
                             stage="human_review", actor=body.coder_id, event="code_accepted",
                             detail={"code": c.code}))
    db.commit()
    return {"status": "accepted", "code": c.code}


@router.post("/codes/{code_id}/override")
def override_code(code_id: str, body: OverrideRequest, db: Session = Depends(get_db)) -> dict:
    """Coder override → captured with reason → becomes a learning example (closed loop)."""
    c = db.get(models.CodeResult, code_id)
    if c is None:
        raise HTTPException(404, "code not found")
    run = db.get(models.CodingRun, c.run_id)
    enc = db.get(models.Encounter, run.encounter_id)

    new_ref = db.scalars(
        select(models.ReferenceCode).where(
            models.ReferenceCode.code_system == c.code_system,
            models.ReferenceCode.code == body.override_code,
        )
    ).first()

    old_code = c.code
    c.is_overridden = True
    c.override_code = body.override_code
    c.override_reason = body.reason
    c.status = "accepted"
    c.accepted_by = body.coder_id
    if new_ref:
        c.code = new_ref.code
        c.description = new_ref.description

    # derive a pattern key from this run's analysis (stored in stage_log)
    analysis = {}
    for s in run.stage_log or []:
        if s.get("stage") == "2_extraction":
            analysis = {"procedures": s.get("procedures", []), "diagnoses": s.get("diagnoses", [])}
    key = graph_rag.pattern_key(enc.specialty, analysis)

    db.add(models.LearningExample(
        specialty=enc.specialty, pattern_key=key, wrong_code=old_code,
        correct_code=body.override_code, code_system=c.code_system, reason=body.reason,
        snippet=run.chart_summary[:240], applied=True,
    ))
    db.add(models.AuditEntry(run_id=c.run_id, encounter_id=enc.id, stage="human_review",
                             actor=body.coder_id, event="code_overridden",
                             detail={"from": old_code, "to": body.override_code, "reason": body.reason}))
    db.commit()
    return {"status": "overridden", "from": old_code, "to": body.override_code,
            "learning_pattern": key}
