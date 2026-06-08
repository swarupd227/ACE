"""Encounter worklist + detail."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ._serialize import run_to_dict

router = APIRouter()

HIDDEN_CLIENT = "__golden__"


def _latest_run(db: Session, enc_id: str) -> models.CodingRun | None:
    return db.scalars(
        select(models.CodingRun)
        .where(models.CodingRun.encounter_id == enc_id)
        .order_by(models.CodingRun.started_at.desc())
        .limit(1)
    ).first()


@router.get("/encounters")
def list_encounters(db: Session = Depends(get_db)) -> list[dict]:
    encs = db.scalars(
        select(models.Encounter)
        .where(models.Encounter.client != HIDDEN_CLIENT)
        .order_by(models.Encounter.created_at.asc())
    ).all()
    out = []
    for e in encs:
        run = _latest_run(db, e.id)
        out.append({
            "id": e.id, "mrn": e.mrn, "patient_name": e.patient_name, "age": e.age, "sex": e.sex,
            "specialty": e.specialty, "modality": e.modality, "payer": e.payer, "dos": e.dos,
            "client": e.client, "source_system": e.source_system, "scenario": e.scenario,
            "status": e.status,
            "routing_lane": run.routing_lane if run else "",
            "routing_reason": run.routing_reason if run else "",
            "overall_confidence": run.overall_confidence if run else 0.0,
            "latency_ms": run.latency_ms if run else 0,
            "run_id": run.id if run else None,
        })
    return out


@router.get("/encounters/{enc_id}")
def get_encounter(enc_id: str, db: Session = Depends(get_db)) -> dict:
    e = db.get(models.Encounter, enc_id)
    if e is None:
        raise HTTPException(404, "encounter not found")
    run = _latest_run(db, e.id)
    # number the chart for the UI so it can align citations to lines
    chart_lines = [{"n": i + 1, "text": ln} for i, ln in enumerate(e.chart_text.splitlines())]
    return {
        "id": e.id, "mrn": e.mrn, "patient_name": e.patient_name, "age": e.age, "sex": e.sex,
        "specialty": e.specialty, "modality": e.modality, "encounter_type": e.encounter_type,
        "payer": e.payer, "pos": e.pos, "dos": e.dos, "client": e.client,
        "source_system": e.source_system, "report_type": e.report_type, "scenario": e.scenario,
        "status": e.status, "chart_lines": chart_lines,
        "run": run_to_dict(run) if run else None,
    }
