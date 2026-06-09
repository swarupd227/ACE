"""Operational tooling: Control Tower (work queues + SLA + assignment) and
Policy & Knowledge Admin (editable payer policies that drive the necessity gate)."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import config_store, models
from ..db import get_db

router = APIRouter()
HIDDEN = "__golden__"

# Demo workforce roster (reference data, not fabricated logic).
ROSTER = ["Priya N. (Coder)", "Marcus L. (Coder)", "Aisha K. (QA Auditor)",
          "David R. (QA Auditor)", "CDI Team"]

# SLA targets in minutes, per queue.
SLA_TARGETS = {"STB": 180, "QA": 480, "MANUAL": 1440, "ESCALATED": 240, "CDI": 2880}


def _sla_status(age_min: float, target: int) -> str:
    if age_min > target:
        return "breached"
    if age_min > 0.6 * target:
        return "at_risk"
    return "on_track"


# ---------------------------------------------------------------------------
# Control Tower
# ---------------------------------------------------------------------------
@router.get("/control-tower")
def control_tower(db: Session = Depends(get_db)) -> dict:
    now = datetime.now(timezone.utc)
    cfg = config_store.all_config(db)
    sla = cfg.get("sla_targets_min", SLA_TARGETS)
    roster = [f"{r['name']} ({r['role']})" for r in cfg.get("roster", [])] or ROSTER
    encs = db.scalars(select(models.Encounter).where(models.Encounter.client != HIDDEN)).all()
    open_cdi_enc = {
        q.encounter_id for q in db.scalars(
            select(models.CdiQuery).where(models.CdiQuery.status == "open")
        ).all()
    }

    items: list[dict] = []
    for e in encs:
        run = db.scalars(
            select(models.CodingRun).where(models.CodingRun.encounter_id == e.id)
            .order_by(models.CodingRun.started_at.desc()).limit(1)
        ).first()
        if run is None or not run.routing_lane:
            continue
        recv = e.received_at or e.created_at
        if recv.tzinfo is None:
            recv = recv.replace(tzinfo=timezone.utc)
        age_min = round((now - recv).total_seconds() / 60.0, 1)
        items.append({
            "run_id": run.id, "encounter_id": e.id, "patient_name": e.patient_name, "mrn": e.mrn,
            "specialty": e.specialty, "payer": e.payer, "lane": run.routing_lane,
            "priority": run.priority, "escalated": run.escalated, "assigned_to": run.assigned_to,
            "age_minutes": age_min, "has_open_cdi": e.id in open_cdi_enc,
        })

    def queue(key: str, label: str, members: list[dict]) -> dict:
        target = sla.get(key, 480)
        for m in members:
            m["sla_status"] = _sla_status(m["age_minutes"], target)
        members.sort(key=lambda m: m["age_minutes"], reverse=True)
        return {
            "key": key, "label": label, "sla_target_min": target, "count": len(members),
            "breached": sum(1 for m in members if m["sla_status"] == "breached"),
            "items": members,
        }

    queues = [
        queue("STB", "Straight-Through Billing", [i for i in items if i["lane"] == "STB"]),
        queue("QA", "QA Review", [dict(i) for i in items if i["lane"] == "QA"]),
        queue("MANUAL", "Manual Coding", [dict(i) for i in items if i["lane"] == "MANUAL"]),
        queue("ESCALATED", "Escalated", [dict(i) for i in items if i["escalated"]]),
        queue("CDI", "CDI Open Queries", [dict(i) for i in items if i["has_open_cdi"]]),
    ]
    total = len(items)
    return {
        "roster": roster,
        "sla_targets": sla,
        "summary": {
            "total": total,
            "unassigned": sum(1 for i in items if not i["assigned_to"]),
            "breached": sum(1 for q in queues[:3] for m in q["items"] if m["sla_status"] == "breached"),
        },
        "queues": queues,
    }


class AssignRequest(BaseModel):
    run_ids: list[str]
    assigned_to: str
    actor: str = "supervisor:demo"


@router.post("/control-tower/assign")
def assign(body: AssignRequest, db: Session = Depends(get_db)) -> dict:
    n = 0
    for rid in body.run_ids:
        run = db.get(models.CodingRun, rid)
        if run is None:
            continue
        run.assigned_to = body.assigned_to
        db.add(models.AuditEntry(run_id=run.id, encounter_id=run.encounter_id, stage="workflow",
                                 actor=body.actor, event="assigned", detail={"to": body.assigned_to}))
        n += 1
    db.commit()
    return {"assigned": n, "to": body.assigned_to}


# ---------------------------------------------------------------------------
# Policy & Knowledge Admin — editable payer policies that drive the gate
# ---------------------------------------------------------------------------
def _pol(p: models.PayerPolicy) -> dict:
    return {
        "id": p.id, "payer": p.payer, "code": p.code, "policy_id": p.policy_id,
        "medical_necessity": p.medical_necessity, "requires_auth": p.requires_auth,
        "modifier_pref": p.modifier_pref, "covered_dx": p.covered_dx, "source": p.source,
    }


@router.get("/policies")
def list_policies(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(models.PayerPolicy).order_by(models.PayerPolicy.payer, models.PayerPolicy.code)).all()
    return [_pol(p) for p in rows]


class PolicyIn(BaseModel):
    payer: str
    code: str
    medical_necessity: str = ""
    requires_auth: bool = False
    modifier_pref: str = ""
    covered_dx: list[str] = []
    source: str = "ClientOverlay"


@router.post("/policies")
def create_policy(body: PolicyIn, db: Session = Depends(get_db)) -> dict:
    p = models.PayerPolicy(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return _pol(p)


@router.put("/policies/{policy_id}")
def update_policy(policy_id: int, body: PolicyIn, db: Session = Depends(get_db)) -> dict:
    p = db.get(models.PayerPolicy, policy_id)
    if p is None:
        raise HTTPException(404, "policy not found")
    for k, v in body.model_dump().items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return _pol(p)


@router.delete("/policies/{policy_id}")
def delete_policy(policy_id: int, db: Session = Depends(get_db)) -> dict:
    p = db.get(models.PayerPolicy, policy_id)
    if p is None:
        raise HTTPException(404, "policy not found")
    db.delete(p)
    db.commit()
    return {"deleted": policy_id}


# ---------------------------------------------------------------------------
# Integrations / Ingestion — simulated PMS/EHR connectivity + real batch ingest
# ---------------------------------------------------------------------------
SOURCE_SYSTEMS = [
    {"name": "Practice Admin", "type": "PMS (VHT-owned)", "channel": "REST / batch"},
    {"name": "eClinicalWorks", "type": "EHR", "channel": "FHIR R4 / HL7 v2"},
    {"name": "Cerner", "type": "EHR", "channel": "FHIR R4 / HL7 v2"},
]
CHANNELS = ["FHIR R4 (DiagnosticReport)", "HL7 v2 (ORU^R01)", "EDI X12 837/835", "Batch SFTP", "REST API"]


@router.get("/integrations")
def integrations(db: Session = Depends(get_db)) -> dict:
    counts: dict[str, int] = {}
    for e in db.scalars(select(models.Encounter).where(models.Encounter.client != HIDDEN)).all():
        counts[e.source_system] = counts.get(e.source_system, 0) + 1
    connectors = [
        {**s, "status": "connected",
         "charts_ingested": counts.get(s["name"], 0) or counts.get(s["name"].replace(" ", ""), 0)}
        for s in SOURCE_SYSTEMS
    ]
    return {"connectors": connectors, "channels": CHANNELS, "api_docs": "/docs",
            "note": "Demo simulates connectivity; the REST ingest below is live."}


class IngestIn(BaseModel):
    report_text: str
    specialty: str = "Radiology"
    modality: str = ""
    payer: str = "Medicare"
    pos: str = "22"
    mrn: str = ""
    patient_name: str = "Ingested Patient"
    sex: str = "F"
    age: int = 55
    dos: str = "2026-04-21"
    source_system: str = "Practice Admin"


@router.post("/ingest")
def ingest(body: IngestIn, db: Session = Depends(get_db)) -> dict:
    if len(body.report_text.strip()) < 20:
        raise HTTPException(400, "report_text too short to ingest")
    mrn = body.mrn or f"ING{abs(hash(body.report_text)) % 100000:05d}"
    enc = models.Encounter(
        mrn=mrn, patient_name=body.patient_name, age=body.age, sex=body.sex,
        specialty=body.specialty, modality=body.modality, payer=body.payer, pos=body.pos,
        dos=body.dos, client="Ingested", source_system=body.source_system,
        report_type="ingested", chart_text=body.report_text, scenario="Live ingest",
        status="NEW",
    )
    db.add(enc)
    db.commit()
    db.refresh(enc)
    return {"id": enc.id, "mrn": enc.mrn, "specialty": enc.specialty, "status": enc.status,
            "source_system": enc.source_system}
