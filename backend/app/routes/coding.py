"""Run the coding pipeline; human-in-the-loop override/accept; audit & learning."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ..knowledge import graph_rag
from ..pipeline import orchestrator
from ..schemas import AcceptRequest, OverrideRequest
from ._serialize import run_to_dict

router = APIRouter()
HIDDEN_CLIENT = "__golden__"


@router.post("/encounters/{enc_id}/code")
def code_encounter(enc_id: str, db: Session = Depends(get_db)) -> dict:
    enc = db.get(models.Encounter, enc_id)
    if enc is None:
        raise HTTPException(404, "encounter not found")
    run = orchestrator.run_coding(db, enc_id)
    return run_to_dict(run)


@router.post("/coding/run-all")
def run_all(db: Session = Depends(get_db)) -> dict:
    # Re-process every non-hidden chart so the demo button is always reliable.
    encs = db.scalars(
        select(models.Encounter).where(models.Encounter.client != HIDDEN_CLIENT)
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
