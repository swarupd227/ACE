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
from ._admin_audit import Actor, get_actor, log_change

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
def create_policy(body: PolicyIn, db: Session = Depends(get_db),
                  actor: Actor = Depends(get_actor)) -> dict:
    p = models.PayerPolicy(**body.model_dump())
    db.add(p)
    log_change(db, actor, "policy", "create", f"{body.payer}/{body.code}", body.model_dump())
    db.commit()
    db.refresh(p)
    return _pol(p)


@router.put("/policies/{policy_id}")
def update_policy(policy_id: int, body: PolicyIn, db: Session = Depends(get_db),
                  actor: Actor = Depends(get_actor)) -> dict:
    p = db.get(models.PayerPolicy, policy_id)
    if p is None:
        raise HTTPException(404, "policy not found")
    for k, v in body.model_dump().items():
        setattr(p, k, v)
    log_change(db, actor, "policy", "update", f"{body.payer}/{body.code}", body.model_dump())
    db.commit()
    db.refresh(p)
    return _pol(p)


@router.delete("/policies/{policy_id}")
def delete_policy(policy_id: int, db: Session = Depends(get_db),
                  actor: Actor = Depends(get_actor)) -> dict:
    p = db.get(models.PayerPolicy, policy_id)
    if p is None:
        raise HTTPException(404, "policy not found")
    log_change(db, actor, "policy", "delete", f"{p.payer}/{p.code}", {})
    db.delete(p)
    db.commit()
    return {"deleted": policy_id}


# ---------------------------------------------------------------------------
# Knowledge Graph Builder — editable medical ontology (concepts + edges) and
# coding guidelines. These are read live by graph_rag.retrieve() every coding
# run, so edits here change what the coding agent is grounded on (real, not a
# diagram). Concepts surface as ONTOLOGY PATHS (with their mapped codes) and
# guidelines surface as GUIDELINE EXCERPTS in the agent's retrieval context.
# ---------------------------------------------------------------------------
REL_TYPES = ["is_a", "finding_site", "causative_agent", "associated_with",
             "part_of", "due_to", "indicates"]
SEMANTIC_TYPES = ["Disease or Syndrome", "Finding", "Sign or Symptom", "Body Part",
                  "Procedure", "Pharmacologic Substance", "Neoplastic Process",
                  "Pathologic Function", "Injury or Poisoning"]


def _concept(c: models.OntologyConcept) -> dict:
    return {"id": c.id, "cui": c.cui, "name": c.name,
            "semantic_type": c.semantic_type, "maps_to": c.maps_to or []}


def _edge(e: models.OntologyEdge) -> dict:
    return {"id": e.id, "src_cui": e.src_cui, "rel": e.rel, "dst_cui": e.dst_cui}


@router.get("/ontology/concepts")
def list_concepts(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(models.OntologyConcept).order_by(models.OntologyConcept.name)).all()
    return [_concept(c) for c in rows]


@router.get("/ontology/edges")
def list_edges(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(models.OntologyEdge)).all()
    return [_edge(e) for e in rows]


@router.get("/ontology/meta")
def ontology_meta() -> dict:
    return {"rel_types": REL_TYPES, "semantic_types": SEMANTIC_TYPES}


class CodeMap(BaseModel):
    system: str
    code: str


class ConceptIn(BaseModel):
    cui: str = ""
    name: str
    semantic_type: str = ""
    maps_to: list[CodeMap] = []


def _next_cui(db: Session) -> str:
    # Client-authored concepts get a stable C9xxxxx id distinct from seeded ontology.
    existing = {c.cui for c in db.scalars(select(models.OntologyConcept)).all()}
    n = 9000001
    while f"C{n}" in existing:
        n += 1
    return f"C{n}"


@router.post("/ontology/concepts")
def create_concept(body: ConceptIn, db: Session = Depends(get_db),
                   actor: Actor = Depends(get_actor)) -> dict:
    if not body.name.strip():
        raise HTTPException(400, "concept name is required")
    cui = body.cui.strip() or _next_cui(db)
    if db.scalar(select(models.OntologyConcept).where(models.OntologyConcept.cui == cui)):
        raise HTTPException(409, f"concept {cui} already exists")
    c = models.OntologyConcept(
        cui=cui, name=body.name.strip(), semantic_type=body.semantic_type,
        maps_to=[m.model_dump() for m in body.maps_to],
    )
    db.add(c)
    log_change(db, actor, "ontology", "create", f"{cui}:{body.name.strip()}",
               {"maps_to": [m.model_dump() for m in body.maps_to]})
    db.commit()
    db.refresh(c)
    return _concept(c)


@router.put("/ontology/concepts/{cid}")
def update_concept(cid: int, body: ConceptIn, db: Session = Depends(get_db),
                   actor: Actor = Depends(get_actor)) -> dict:
    c = db.get(models.OntologyConcept, cid)
    if c is None:
        raise HTTPException(404, "concept not found")
    c.name = body.name.strip() or c.name
    c.semantic_type = body.semantic_type
    c.maps_to = [m.model_dump() for m in body.maps_to]
    log_change(db, actor, "ontology", "update", f"{c.cui}:{c.name}",
               {"maps_to": c.maps_to})
    db.commit()
    db.refresh(c)
    return _concept(c)


@router.delete("/ontology/concepts/{cid}")
def delete_concept(cid: int, db: Session = Depends(get_db),
                   actor: Actor = Depends(get_actor)) -> dict:
    c = db.get(models.OntologyConcept, cid)
    if c is None:
        raise HTTPException(404, "concept not found")
    # Also drop any edges touching this concept so the graph stays consistent.
    for e in db.scalars(select(models.OntologyEdge).where(
        (models.OntologyEdge.src_cui == c.cui) | (models.OntologyEdge.dst_cui == c.cui)
    )).all():
        db.delete(e)
    log_change(db, actor, "ontology", "delete", f"{c.cui}:{c.name}", {})
    db.delete(c)
    db.commit()
    return {"deleted": cid}


class EdgeIn(BaseModel):
    src_cui: str
    rel: str
    dst_cui: str


@router.post("/ontology/edges")
def create_edge(body: EdgeIn, db: Session = Depends(get_db),
                actor: Actor = Depends(get_actor)) -> dict:
    if body.src_cui == body.dst_cui:
        raise HTTPException(400, "an edge cannot link a concept to itself")
    valid = {c.cui for c in db.scalars(select(models.OntologyConcept)).all()}
    for side in (body.src_cui, body.dst_cui):
        if side not in valid:
            raise HTTPException(400, f"unknown concept {side}")
    dup = db.scalar(select(models.OntologyEdge).where(
        models.OntologyEdge.src_cui == body.src_cui,
        models.OntologyEdge.rel == body.rel,
        models.OntologyEdge.dst_cui == body.dst_cui,
    ))
    if dup:
        raise HTTPException(409, "edge already exists")
    e = models.OntologyEdge(src_cui=body.src_cui, rel=body.rel, dst_cui=body.dst_cui)
    db.add(e)
    log_change(db, actor, "ontology", "create", f"{body.src_cui}-{body.rel}->{body.dst_cui}", {})
    db.commit()
    db.refresh(e)
    return _edge(e)


@router.delete("/ontology/edges/{eid}")
def delete_edge(eid: int, db: Session = Depends(get_db),
                actor: Actor = Depends(get_actor)) -> dict:
    e = db.get(models.OntologyEdge, eid)
    if e is None:
        raise HTTPException(404, "edge not found")
    log_change(db, actor, "ontology", "delete", f"{e.src_cui}-{e.rel}->{e.dst_cui}", {})
    db.delete(e)
    db.commit()
    return {"deleted": eid}


# --- Coding guidelines (indexed text that grounds retrieval + citation) -----
def _guideline(g: models.GuidelineChunk) -> dict:
    return {"id": g.id, "source": g.source, "section": g.section,
            "text": g.text, "specialty": g.specialty}


@router.get("/ontology/guidelines")
def list_guidelines(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(models.GuidelineChunk).order_by(models.GuidelineChunk.source)).all()
    return [_guideline(g) for g in rows]


class GuidelineIn(BaseModel):
    source: str
    section: str = ""
    text: str
    specialty: str = ""


@router.post("/ontology/guidelines")
def create_guideline(body: GuidelineIn, db: Session = Depends(get_db),
                     actor: Actor = Depends(get_actor)) -> dict:
    if len(body.text.strip()) < 10:
        raise HTTPException(400, "guideline text too short")
    g = models.GuidelineChunk(source=body.source.strip() or "ClientOverlay",
                              section=body.section, text=body.text.strip(),
                              specialty=body.specialty)
    db.add(g)
    log_change(db, actor, "guideline", "create", f"{g.source}/{g.section}", {"specialty": g.specialty})
    db.commit()
    db.refresh(g)
    return _guideline(g)


@router.put("/ontology/guidelines/{gid}")
def update_guideline(gid: int, body: GuidelineIn, db: Session = Depends(get_db),
                     actor: Actor = Depends(get_actor)) -> dict:
    g = db.get(models.GuidelineChunk, gid)
    if g is None:
        raise HTTPException(404, "guideline not found")
    g.source = body.source.strip() or g.source
    g.section = body.section
    g.text = body.text.strip() or g.text
    g.specialty = body.specialty
    log_change(db, actor, "guideline", "update", f"{g.source}/{g.section}", {"specialty": g.specialty})
    db.commit()
    db.refresh(g)
    return _guideline(g)


@router.delete("/ontology/guidelines/{gid}")
def delete_guideline(gid: int, db: Session = Depends(get_db),
                     actor: Actor = Depends(get_actor)) -> dict:
    g = db.get(models.GuidelineChunk, gid)
    if g is None:
        raise HTTPException(404, "guideline not found")
    log_change(db, actor, "guideline", "delete", f"{g.source}/{g.section}", {})
    db.delete(g)
    db.commit()
    return {"deleted": gid}


# ---------------------------------------------------------------------------
# Reference Data admin — code sets + the deterministic edit tables (NCCI / MUE /
# modifiers). These are read live by validation.py, so client overlays and edits
# here change the validation gates on the next coding run.
# ---------------------------------------------------------------------------
def _refcode(c: models.ReferenceCode) -> dict:
    return {"id": c.id, "code_system": c.code_system, "code": c.code, "description": c.description,
            "billable": c.billable, "modality": c.modality, "sex_restriction": c.sex_restriction,
            "age_min": c.age_min, "age_max": c.age_max, "source": c.source,
            "effective_start": c.effective_start, "effective_end": c.effective_end}


@router.get("/reference/codes")
def list_refcodes(system: str = "", q: str = "", limit: int = 200,
                  db: Session = Depends(get_db)) -> list[dict]:
    stmt = select(models.ReferenceCode)
    if system:
        stmt = stmt.where(models.ReferenceCode.code_system == system)
    rows = db.scalars(stmt.order_by(models.ReferenceCode.code_system, models.ReferenceCode.code)).all()
    if q:
        ql = q.lower()
        rows = [c for c in rows if ql in c.code.lower() or ql in c.description.lower()]
    return [_refcode(c) for c in rows[:limit]]


class RefCodeIn(BaseModel):
    code_system: str
    code: str
    description: str
    billable: bool = True
    modality: str = ""
    sex_restriction: str = ""
    age_min: int = 0
    age_max: int = 130
    source: str = "ClientOverlay"


@router.post("/reference/codes")
def create_refcode(body: RefCodeIn, db: Session = Depends(get_db),
                   actor: Actor = Depends(get_actor)) -> dict:
    if db.scalar(select(models.ReferenceCode).where(
        models.ReferenceCode.code_system == body.code_system, models.ReferenceCode.code == body.code
    )):
        raise HTTPException(409, f"{body.code_system}:{body.code} already exists")
    c = models.ReferenceCode(**body.model_dump())
    db.add(c)
    log_change(db, actor, "reference", "create", f"{body.code_system}:{body.code}", {"desc": body.description})
    db.commit()
    db.refresh(c)
    return _refcode(c)


@router.put("/reference/codes/{cid}")
def update_refcode(cid: int, body: RefCodeIn, db: Session = Depends(get_db),
                   actor: Actor = Depends(get_actor)) -> dict:
    c = db.get(models.ReferenceCode, cid)
    if c is None:
        raise HTTPException(404, "code not found")
    for k, v in body.model_dump().items():
        setattr(c, k, v)
    log_change(db, actor, "reference", "update", f"{c.code_system}:{c.code}", {"desc": c.description})
    db.commit()
    db.refresh(c)
    return _refcode(c)


@router.delete("/reference/codes/{cid}")
def delete_refcode(cid: int, db: Session = Depends(get_db),
                   actor: Actor = Depends(get_actor)) -> dict:
    c = db.get(models.ReferenceCode, cid)
    if c is None:
        raise HTTPException(404, "code not found")
    log_change(db, actor, "reference", "delete", f"{c.code_system}:{c.code}", {})
    db.delete(c)
    db.commit()
    return {"deleted": cid}


# --- NCCI PTP bundling edits ------------------------------------------------
def _ncci(e: models.NcciEdit) -> dict:
    return {"id": e.id, "column1": e.column1, "column2": e.column2,
            "modifier_allowed": e.modifier_allowed, "rationale": e.rationale, "source": e.source}


@router.get("/reference/ncci")
def list_ncci(db: Session = Depends(get_db)) -> list[dict]:
    return [_ncci(e) for e in db.scalars(select(models.NcciEdit).order_by(models.NcciEdit.column1)).all()]


class NcciIn(BaseModel):
    column1: str
    column2: str
    modifier_allowed: bool = True
    rationale: str = ""
    source: str = "ClientOverlay"


@router.post("/reference/ncci")
def create_ncci(body: NcciIn, db: Session = Depends(get_db),
                actor: Actor = Depends(get_actor)) -> dict:
    e = models.NcciEdit(**body.model_dump())
    db.add(e)
    log_change(db, actor, "ncci", "create", f"{body.column1}|{body.column2}",
               {"modifier_allowed": body.modifier_allowed})
    db.commit()
    db.refresh(e)
    return _ncci(e)


@router.delete("/reference/ncci/{eid}")
def delete_ncci(eid: int, db: Session = Depends(get_db),
                actor: Actor = Depends(get_actor)) -> dict:
    e = db.get(models.NcciEdit, eid)
    if e is None:
        raise HTTPException(404, "edit not found")
    log_change(db, actor, "ncci", "delete", f"{e.column1}|{e.column2}", {})
    db.delete(e)
    db.commit()
    return {"deleted": eid}


# --- MUE limits -------------------------------------------------------------
def _mue(m: models.MueLimit) -> dict:
    return {"id": m.id, "code": m.code, "max_units": m.max_units, "rationale": m.rationale, "source": m.source}


@router.get("/reference/mue")
def list_mue(db: Session = Depends(get_db)) -> list[dict]:
    return [_mue(m) for m in db.scalars(select(models.MueLimit).order_by(models.MueLimit.code)).all()]


class MueIn(BaseModel):
    code: str
    max_units: int
    rationale: str = ""
    source: str = "ClientOverlay"


@router.post("/reference/mue")
def create_mue(body: MueIn, db: Session = Depends(get_db),
               actor: Actor = Depends(get_actor)) -> dict:
    if db.scalar(select(models.MueLimit).where(models.MueLimit.code == body.code)):
        raise HTTPException(409, f"MUE for {body.code} already exists")
    m = models.MueLimit(**body.model_dump())
    db.add(m)
    log_change(db, actor, "mue", "create", body.code, {"max_units": body.max_units})
    db.commit()
    db.refresh(m)
    return _mue(m)


@router.put("/reference/mue/{mid}")
def update_mue(mid: int, body: MueIn, db: Session = Depends(get_db),
               actor: Actor = Depends(get_actor)) -> dict:
    m = db.get(models.MueLimit, mid)
    if m is None:
        raise HTTPException(404, "MUE not found")
    for k, v in body.model_dump().items():
        setattr(m, k, v)
    log_change(db, actor, "mue", "update", m.code, {"max_units": m.max_units})
    db.commit()
    db.refresh(m)
    return _mue(m)


@router.delete("/reference/mue/{mid}")
def delete_mue(mid: int, db: Session = Depends(get_db),
               actor: Actor = Depends(get_actor)) -> dict:
    m = db.get(models.MueLimit, mid)
    if m is None:
        raise HTTPException(404, "MUE not found")
    log_change(db, actor, "mue", "delete", m.code, {})
    db.delete(m)
    db.commit()
    return {"deleted": mid}


# --- Modifier rules ---------------------------------------------------------
def _mod(m: models.ModifierRule) -> dict:
    return {"id": m.id, "modifier": m.modifier, "description": m.description,
            "applies_to": m.applies_to, "notes": m.notes}


@router.get("/reference/modifiers")
def list_modifiers(db: Session = Depends(get_db)) -> list[dict]:
    return [_mod(m) for m in db.scalars(select(models.ModifierRule).order_by(models.ModifierRule.modifier)).all()]


class ModifierIn(BaseModel):
    modifier: str
    description: str
    applies_to: str = ""
    notes: str = ""


@router.post("/reference/modifiers")
def create_modifier(body: ModifierIn, db: Session = Depends(get_db),
                    actor: Actor = Depends(get_actor)) -> dict:
    if db.scalar(select(models.ModifierRule).where(models.ModifierRule.modifier == body.modifier)):
        raise HTTPException(409, f"modifier {body.modifier} already exists")
    m = models.ModifierRule(**body.model_dump())
    db.add(m)
    log_change(db, actor, "modifier", "create", body.modifier, {})
    db.commit()
    db.refresh(m)
    return _mod(m)


@router.delete("/reference/modifiers/{mid}")
def delete_modifier(mid: int, db: Session = Depends(get_db),
                    actor: Actor = Depends(get_actor)) -> dict:
    m = db.get(models.ModifierRule, mid)
    if m is None:
        raise HTTPException(404, "modifier not found")
    log_change(db, actor, "modifier", "delete", m.modifier, {})
    db.delete(m)
    db.commit()
    return {"deleted": mid}


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
