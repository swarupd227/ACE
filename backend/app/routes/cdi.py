"""CDI / physician-query workflow endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..db import SessionLocal, get_db
from ..pipeline import orchestrator
from ._serialize import run_to_dict
from ._sse import sse_response

router = APIRouter()


def _q(q: models.CdiQuery, enc: models.Encounter | None = None) -> dict:
    d = {
        "id": q.id, "encounter_id": q.encounter_id, "specialty": q.specialty, "status": q.status,
        "question": q.question, "clinical_indicators": q.clinical_indicators, "options": q.options,
        "target": q.target, "potential_codes": q.potential_codes, "rationale": q.rationale,
        "physician_response": q.physician_response, "responded_by": q.responded_by,
        "created_at": q.created_at.isoformat() if q.created_at else None,
    }
    if enc is not None:
        d["patient_name"] = enc.patient_name
        d["mrn"] = enc.mrn
    return d


@router.post("/encounters/{enc_id}/cdi-scan")
def cdi_scan(enc_id: str, db: Session = Depends(get_db)) -> list[dict]:
    if db.get(models.Encounter, enc_id) is None:
        raise HTTPException(404, "encounter not found")
    queries = orchestrator.cdi_scan(db, enc_id)
    return [_q(q) for q in queries]


@router.get("/encounters/{enc_id}/cdi-scan/stream")
def cdi_scan_stream(enc_id: str) -> StreamingResponse:
    """Run the CDI agent and STREAM its reasoning as SSE."""
    def work(emit):
        db = SessionLocal()
        try:
            if db.get(models.Encounter, enc_id) is None:
                emit({"type": "error", "detail": "encounter not found"})
                return
            queries = orchestrator.cdi_scan(db, enc_id, emit=emit)
            emit({"type": "done", "queries": [_q(q) for q in queries]})
        finally:
            db.close()

    return sse_response(work)


@router.get("/encounters/{enc_id}/cdi")
def cdi_for_encounter(enc_id: str, db: Session = Depends(get_db)) -> list[dict]:
    qs = db.scalars(
        select(models.CdiQuery).where(models.CdiQuery.encounter_id == enc_id)
        .order_by(models.CdiQuery.created_at.desc())
    ).all()
    return [_q(q) for q in qs]


@router.get("/cdi/queries")
def cdi_queue(db: Session = Depends(get_db)) -> list[dict]:
    qs = db.scalars(select(models.CdiQuery).order_by(models.CdiQuery.created_at.desc())).all()
    out = []
    for q in qs:
        enc = db.get(models.Encounter, q.encounter_id)
        out.append(_q(q, enc))
    return out


class CdiResponse(BaseModel):
    response: str
    responder: str = "physician:demo"


@router.post("/cdi/queries/{query_id}/respond")
def cdi_respond(query_id: str, body: CdiResponse, db: Session = Depends(get_db)) -> dict:
    q = db.get(models.CdiQuery, query_id)
    if q is None:
        raise HTTPException(404, "query not found")
    q.physician_response = body.response
    q.responded_by = body.responder
    q.status = "answered"
    q.answered_at = datetime.now(timezone.utc)
    db.commit()

    # Re-code the encounter with the physician clarification injected as authoritative context.
    run = None
    if body.response.strip().lower() != "unable to determine":
        clarification = f"- {q.question} -> Physician answer: {body.response}"
        run = orchestrator.run_coding(db, q.encounter_id, extra_context=clarification)

    return {"query": _q(q), "recoded": run is not None, "run": run_to_dict(run) if run else None}
