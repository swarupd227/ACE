"""P2R API — Phase 1 (Policy Intelligence Ingestion) on the shared core.

Endpoints turn a payer-policy document (pasted text, an uploaded PDF/image via the
shared vision-OCR, or the built-in sample) into structured, cited PolicyProvision
records with composite confidence and a routing decision.
"""
from __future__ import annotations

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

# One-way reuse: P2R imports the shared core. Nothing here touches the ACE app.
from core import llm_client
from core.ir import ArtifactType

from . import eval as evalh
from . import (acquisition, audit, config_store, denials, ingest, models, publish, replay,
               rule_ir, sample, validate)
from .db import SessionLocal, get_db, init_db

app = FastAPI(title="P2R — Policy-to-Rule Intelligence (Nous RCM Framework)", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_DOC_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/webp"}


def actor_of(x_actor: str = Header(default="system", alias="X-Actor"),
             x_role: str = Header(default="", alias="X-Role")) -> str:
    """The acting user/role from the UI, for Decision-Log attribution (not enforcement)."""
    return f"{x_actor}" + (f" ({x_role})" if x_role else "")


@app.on_event("startup")
def _startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        validate._seed_library(db)       # seed the read-only rule library if empty
        acquisition.seed_registry(db)    # seed payer master (MDM) + acquisition sources
        evalh.seed_golden(db)            # seed the table-backed golden set
    finally:
        db.close()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "p2r", "shared_core": "linked"}


@app.get("/meta")
def meta() -> dict:
    return {
        "platform": "Nous RCM Intelligence Framework",
        "module": "P2R — Policy-to-Rule",
        "phase": "P1 — Policy Intelligence Ingestion",
        "shared_core": ["llm_client", "ir"],
        "llm_available": llm_client.llm_available(),
        "llm_model": llm_client.model_version(),
        "ir_artifact_types": [t.value for t in ArtifactType],
    }


class PolicyIn(BaseModel):
    payer: str = ""
    title: str = ""
    text: str


@app.post("/ingest/policy")
def ingest_policy(body: PolicyIn, db: Session = Depends(get_db)) -> dict:
    if len(body.text.strip()) < 40:
        raise HTTPException(400, "policy text too short to ingest")
    if not llm_client.llm_available():
        raise HTTPException(503, "LLM not configured — set ANTHROPIC_API_KEY")
    return ingest.ingest_policy(db, body.payer, body.title, body.text)


@app.post("/ingest/policy/sample")
def ingest_sample(db: Session = Depends(get_db)) -> dict:
    if not llm_client.llm_available():
        raise HTTPException(503, "LLM not configured — set ANTHROPIC_API_KEY")
    return ingest.ingest_policy(db, sample.SAMPLE_PAYER, sample.SAMPLE_TITLE, sample.SAMPLE_POLICY)


@app.post("/ingest/policy/document")
async def ingest_document(
    file: UploadFile = File(...),
    payer: str = Form(""),
    title: str = Form(""),
    db: Session = Depends(get_db),
) -> dict:
    """Scanned/PDF policy → shared vision OCR → same extraction pipeline."""
    media_type = (file.content_type or "").lower()
    if media_type not in _DOC_TYPES:
        raise HTTPException(400, f"unsupported document type '{media_type}' — use PDF/PNG/JPEG/WebP")
    data = await file.read()
    if len(data) > 12 * 1024 * 1024:
        raise HTTPException(400, "document too large (12 MB max)")
    try:
        text = llm_client.extract_document_text(data, media_type)
    except llm_client.LLMUnavailable as exc:
        raise HTTPException(503, f"document extraction unavailable: {exc}")
    return ingest.ingest_policy(db, payer, title or (file.filename or "uploaded policy"),
                                text, source_type="UPLOAD")


@app.get("/documents")
def list_documents(db: Session = Depends(get_db)) -> list[dict]:
    docs = db.scalars(select(models.PolicyDocument).order_by(models.PolicyDocument.ingested_at.desc())).all()
    return [{"id": d.id, "payer": d.payer, "title": d.title, "doc_kind": d.doc_kind,
             "provision_count": d.provision_count, "source_type": d.source_type,
             "ingested_at": d.ingested_at.isoformat() if d.ingested_at else None} for d in docs]


@app.get("/documents/{doc_id}/provisions")
def document_provisions(doc_id: str, db: Session = Depends(get_db)) -> dict:
    doc = db.get(models.PolicyDocument, doc_id)
    if doc is None:
        raise HTTPException(404, "document not found")
    provs = db.scalars(select(models.PolicyProvision).where(models.PolicyProvision.document_id == doc_id)).all()
    return {"document": {"id": doc.id, "payer": doc.payer, "title": doc.title, "doc_kind": doc.doc_kind},
            "provisions": [ingest._prov_dict(p) for p in provs]}


@app.get("/provisions")
def list_provisions(routing: str = "", db: Session = Depends(get_db)) -> list[dict]:
    q = select(models.PolicyProvision).order_by(models.PolicyProvision.created_at.desc())
    if routing:
        q = q.where(models.PolicyProvision.routing == routing)
    return [ingest._prov_dict(p) for p in db.scalars(q).all()]


# --- Phase 3: Validation & Reconciliation -----------------------------------
@app.get("/rule-library")
def rule_library(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(models.RuleLibraryEntry)).all()
    return [{"id": r.id, "payer": r.payer, "title": r.title, "code_sets": r.code_sets, "status": r.status}
            for r in rows]


@app.post("/recommendations/from-document/{doc_id}")
def recommend_from_document(doc_id: str, db: Session = Depends(get_db),
                            actor: str = Depends(actor_of)) -> dict:
    if not llm_client.llm_available():
        raise HTTPException(503, "LLM not configured — set ANTHROPIC_API_KEY")
    try:
        return validate.generate_for_document(db, doc_id, actor=actor)
    except ValueError as exc:
        raise HTTPException(404, str(exc))


@app.get("/recommendations")
def list_recommendations(verdict: str = "", attention: bool = False, status: str = "",
                         db: Session = Depends(get_db)) -> list[dict]:
    q = select(models.RuleRecommendation).order_by(models.RuleRecommendation.created_at.desc())
    if verdict:
        q = q.where(models.RuleRecommendation.reconciliation_verdict == verdict)
    if attention:
        q = q.where(models.RuleRecommendation.needs_attention == True)  # noqa: E712
    if status:
        q = q.where(models.RuleRecommendation.status == status)
    return [validate.rec_dict(r) for r in db.scalars(q).all()]


class RecPatch(BaseModel):
    candidate_summary: str | None = None
    reconciliation_verdict: str | None = None
    code_sets: dict | None = None


@app.patch("/recommendations/{rec_id}")
def edit_recommendation(rec_id: str, body: RecPatch, db: Session = Depends(get_db),
                        actor: str = Depends(actor_of)) -> dict:
    """Phase 4 — a reviewer authors/corrects a candidate rule before approving it."""
    rec = db.get(models.RuleRecommendation, rec_id)
    if rec is None:
        raise HTTPException(404, "recommendation not found")
    if rec.status == "PUBLISHED":
        raise HTTPException(409, "cannot edit a published recommendation")
    if body.candidate_summary is not None:
        rec.candidate_summary = body.candidate_summary
    if body.code_sets is not None:
        rec.code_sets = body.code_sets
    if body.reconciliation_verdict is not None:
        if body.reconciliation_verdict not in {"NET_NEW", "UPDATE", "DUPLICATE", "CONFLICT"}:
            raise HTTPException(400, "invalid reconciliation_verdict")
        rec.reconciliation_verdict = body.reconciliation_verdict
        rec.needs_attention = (body.reconciliation_verdict == "CONFLICT") or rec.needs_attention
    db.add(rec)
    db.commit()
    db.refresh(rec)
    audit.log(db, phase="UX", action="EDIT", actor=actor, entity_type="recommendation",
              entity_id=rec.id, payer=rec.payer, summary="candidate edited before approval")
    return validate.rec_dict(rec)


# --- Phase 5: human approval + "Publish to ACE" integration glimpse ----------
@app.post("/recommendations/{rec_id}/approve")
def approve_recommendation(rec_id: str, db: Session = Depends(get_db),
                           actor: str = Depends(actor_of)) -> dict:
    """A reviewer signs off a recommendation; only APPROVED rules may be published to ACE."""
    rec = db.get(models.RuleRecommendation, rec_id)
    if rec is None:
        raise HTTPException(404, "recommendation not found")
    if rec.status == "PUBLISHED":
        raise HTTPException(409, "already published")
    rec.status = "APPROVED"
    db.add(rec)
    db.commit()
    audit.log(db, phase="UX", action="APPROVE", actor=actor, entity_type="recommendation",
              entity_id=rec.id, payer=rec.payer, summary=f"{rec.provision_type} approved for publication")
    return {"recommendation_id": rec.id, "status": rec.status}


@app.get("/integration/ace/status")
def ace_status() -> dict:
    """Is ACE's public API reachable, and how many P2R-authored policies live there?"""
    return publish.ace_reachable()


# --- Phase 4: Rule IR / compiler, replay & differential testing, rollback ----
@app.get("/recommendations/{rec_id}/rule-ir")
def recommendation_rule_ir(rec_id: str, db: Session = Depends(get_db)) -> dict:
    """Canonical Rule IR + compiled artifacts (engine-agnostic + ACE adapter)."""
    rec = db.get(models.RuleRecommendation, rec_id)
    if rec is None:
        raise HTTPException(404, "recommendation not found")
    return rule_ir.compile_all(rec)


@app.post("/recommendations/{rec_id}/replay")
def recommendation_replay(rec_id: str, db: Session = Depends(get_db)) -> dict:
    """Replay the rule against the historical claim corpus → differential impact."""
    rec = db.get(models.RuleRecommendation, rec_id)
    if rec is None:
        raise HTTPException(404, "recommendation not found")
    return replay.replay_rule(db, rec)


@app.post("/recommendations/{rec_id}/rollback")
def recommendation_rollback(rec_id: str, db: Session = Depends(get_db),
                            actor: str = Depends(actor_of)) -> dict:
    """Retract a published rule from ACE and revert it to APPROVED."""
    try:
        return publish.rollback_recommendation(db, rec_id, actor=actor)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:  # noqa: BLE001 — transport/HTTP failure reaching ACE
        raise HTTPException(502, f"rollback failed: {exc}")


@app.post("/recommendations/{rec_id}/publish-to-ace")
def publish_to_ace(rec_id: str, db: Session = Depends(get_db),
                   actor: str = Depends(actor_of)) -> dict:
    """Write the approved rule into ACE via its public policy API (sandbox payer only)."""
    try:
        return publish.publish_recommendation(db, rec_id, actor=actor)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:  # noqa: BLE001 — transport/HTTP failure reaching ACE
        raise HTTPException(502, f"publish to ACE failed: {exc}")


# --- Phase 1 completion: source registry, acquisition, deltas, payer MDM -----
@app.get("/sources")
def list_sources(db: Session = Depends(get_db)) -> list[dict]:
    return [acquisition.source_dict(s) for s in
            db.scalars(select(models.PolicySource).order_by(models.PolicySource.name)).all()]


@app.post("/sources/{source_id}/acquire")
def acquire_source(source_id: str, db: Session = Depends(get_db),
                   actor: str = Depends(actor_of)) -> dict:
    """Run the acquisition agent against a source: fetch → change-detect → ingest delta."""
    if not llm_client.llm_available():
        raise HTTPException(503, "LLM not configured — set ANTHROPIC_API_KEY")
    try:
        return acquisition.acquire(db, source_id, actor=actor)
    except ValueError as exc:
        raise HTTPException(404, str(exc))


@app.get("/deltas")
def list_deltas(db: Session = Depends(get_db)) -> list[dict]:
    return [acquisition.delta_dict(d) for d in
            db.scalars(select(models.PolicyDelta).order_by(models.PolicyDelta.created_at.desc())).all()]


@app.get("/payer-master")
def payer_master(db: Session = Depends(get_db)) -> list[dict]:
    return [acquisition.master_dict(m) for m in db.scalars(select(models.PayerMaster)).all()]


# --- Phase 2: Denial Pattern Discovery --------------------------------------
@app.post("/denials/load-sample")
def denials_load_sample(db: Session = Depends(get_db)) -> dict:
    """Seed synthetic 835 remittance data (PHI-free)."""
    return {"remittance_lines": denials.load_sample(db)}


@app.post("/denials/detect")
def denials_detect(db: Session = Depends(get_db), actor: str = Depends(actor_of)) -> dict:
    """Re-derive ranked denial signals from the remittance data (statistics-only)."""
    try:
        return denials.detect_signals(db, actor=actor)
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.get("/denials/signals")
def denials_signals(status: str = "", db: Session = Depends(get_db)) -> list[dict]:
    q = select(models.DenialSignal).order_by(models.DenialSignal.rank)
    if status:
        q = q.where(models.DenialSignal.status == status)
    return [denials.signal_dict(s) for s in db.scalars(q).all()]


@app.get("/denials/remittances")
def denials_remittances(procedure_code: str = "", denied: bool | None = None,
                        limit: int = 200, db: Session = Depends(get_db)) -> list[dict]:
    q = select(models.RemittanceLine).order_by(models.RemittanceLine.service_date.desc())
    if procedure_code:
        q = q.where(models.RemittanceLine.procedure_code == procedure_code)
    if denied is not None:
        q = q.where(models.RemittanceLine.denied == denied)  # noqa: E712
    rows = db.scalars(q.limit(min(limit, 1000))).all()
    return [{"id": r.id, "payer": r.payer, "claim_id": r.claim_id,
             "procedure_code": r.procedure_code, "denied": r.denied,
             "denial_carc": r.denial_carc, "denial_reason": r.denial_reason,
             "billed_amount": r.billed_amount, "service_date": r.service_date} for r in rows]


@app.post("/denials/signals/{signal_id}/promote")
def denials_promote(signal_id: str, db: Session = Depends(get_db),
                    actor: str = Depends(actor_of)) -> dict:
    """Promote a denial signal's proposed rule into the P3 review queue."""
    if not llm_client.llm_available():
        raise HTTPException(503, "LLM not configured — set ANTHROPIC_API_KEY")
    try:
        return denials.promote_signal(db, signal_id, actor=actor)
    except ValueError as exc:
        raise HTTPException(400, str(exc))


# --- Admin: runtime configuration (drives the engine) -----------------------
@app.get("/admin/config")
def admin_get_config(db: Session = Depends(get_db)) -> dict:
    return {"config": config_store.load(db), "defaults": config_store.DEFAULTS}


class ConfigPut(BaseModel):
    value: dict


@app.put("/admin/config/{key}")
def admin_put_config(key: str, body: ConfigPut, db: Session = Depends(get_db),
                     actor: str = Depends(actor_of)) -> dict:
    if key not in config_store.DEFAULTS:
        raise HTTPException(400, f"unknown config key '{key}'")
    config_store.put(db, key, body.value)
    audit.log(db, phase="UX", action="CONFIG", actor=actor, entity_type="config", entity_id=key,
              summary=f"updated config '{key}'", lineage={"value": body.value})
    return {"config": config_store.load(db)}


@app.post("/admin/config/reset")
def admin_reset_config(db: Session = Depends(get_db), actor: str = Depends(actor_of)) -> dict:
    config_store.reset(db)
    audit.log(db, phase="UX", action="CONFIG_RESET", actor=actor, entity_type="config",
              summary="reset all config to defaults")
    return {"config": config_store.load(db)}


@app.get("/admin/llm/status")
def admin_llm_status() -> dict:
    return {"available": llm_client.llm_available(), "model": llm_client.model_version(),
            "anthropic_key": bool(__import__("os").getenv("ANTHROPIC_API_KEY")),
            "openai_key": bool(__import__("os").getenv("OPENAI_API_KEY"))}


@app.post("/admin/llm/test")
def admin_llm_test() -> dict:
    if not llm_client.llm_available():
        return {"ok": False, "error": "LLM not configured"}
    try:
        schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}
        out = llm_client.complete_json("You are a connectivity probe.",
                                       "Return {\"ok\": true}.", schema, temperature=0.0)[0]
        return {"ok": bool(out.get("ok")), "model": llm_client.model_version()}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


# --- Admin: rule library CRUD (the reconciliation targets) ------------------
class RuleLibIn(BaseModel):
    id: str
    payer: str
    title: str = ""
    code_sets: dict = {}
    status: str = "active"


@app.post("/rule-library")
def create_rule(body: RuleLibIn, db: Session = Depends(get_db), actor: str = Depends(actor_of)) -> dict:
    if db.get(models.RuleLibraryEntry, body.id):
        raise HTTPException(409, "rule id already exists")
    r = models.RuleLibraryEntry(id=body.id, payer=body.payer, title=body.title,
                                logic_summary=body.title, code_sets=body.code_sets, status=body.status)
    db.add(r)
    db.commit()
    audit.log(db, phase="UX", action="RULE_CREATE", actor=actor, entity_type="rule", entity_id=body.id,
              payer=body.payer, summary=f"added library rule {body.id}")
    return {"id": r.id}


@app.put("/rule-library/{rule_id}")
def update_rule(rule_id: str, body: RuleLibIn, db: Session = Depends(get_db),
                actor: str = Depends(actor_of)) -> dict:
    r = db.get(models.RuleLibraryEntry, rule_id)
    if r is None:
        raise HTTPException(404, "rule not found")
    r.payer, r.title, r.logic_summary = body.payer, body.title, body.title
    r.code_sets, r.status = body.code_sets, body.status
    db.add(r)
    db.commit()
    audit.log(db, phase="UX", action="RULE_UPDATE", actor=actor, entity_type="rule", entity_id=rule_id,
              payer=body.payer, summary=f"edited library rule {rule_id}")
    return {"id": r.id}


@app.delete("/rule-library/{rule_id}")
def delete_rule(rule_id: str, db: Session = Depends(get_db), actor: str = Depends(actor_of)) -> dict:
    r = db.get(models.RuleLibraryEntry, rule_id)
    if r is None:
        raise HTTPException(404, "rule not found")
    db.delete(r)
    db.commit()
    audit.log(db, phase="UX", action="RULE_DELETE", actor=actor, entity_type="rule", entity_id=rule_id,
              summary=f"removed library rule {rule_id}")
    return {"deleted": rule_id}


# --- Admin: source registry CRUD --------------------------------------------
class SourceIn(BaseModel):
    payer: str
    name: str
    source_type: str = "PORTAL"
    location: str = ""
    cadence: str = "weekly"
    status: str = "active"


@app.post("/sources")
def create_source(body: SourceIn, db: Session = Depends(get_db), actor: str = Depends(actor_of)) -> dict:
    s = models.PolicySource(**body.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    audit.log(db, phase="UX", action="SOURCE_CREATE", actor=actor, entity_type="source",
              entity_id=s.id, payer=body.payer, summary=f"registered source '{body.name}'")
    return acquisition.source_dict(s)


@app.put("/sources/{source_id}")
def update_source(source_id: str, body: SourceIn, db: Session = Depends(get_db),
                  actor: str = Depends(actor_of)) -> dict:
    s = db.get(models.PolicySource, source_id)
    if s is None:
        raise HTTPException(404, "source not found")
    for k, v in body.model_dump().items():
        setattr(s, k, v)
    db.add(s)
    db.commit()
    audit.log(db, phase="UX", action="SOURCE_UPDATE", actor=actor, entity_type="source",
              entity_id=source_id, payer=body.payer, summary=f"updated source '{body.name}'")
    return acquisition.source_dict(s)


# --- Governance: append-only decision log + lineage -------------------------
@app.get("/audit")
def audit_log(phase: str = "", entity_id: str = "", db: Session = Depends(get_db)) -> list[dict]:
    """The append-only decision log across all phases (filterable)."""
    return audit.entries(db, phase=phase, entity_id=entity_id)


@app.get("/recommendations/{rec_id}/lineage")
def recommendation_lineage(rec_id: str, db: Session = Depends(get_db)) -> dict:
    """Full lineage from a rule back to its source (policy or denial) + decision trail."""
    try:
        return audit.lineage_for(db, rec_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc))


# --- Golden-set evaluation harness ------------------------------------------
@app.get("/eval/golden")
def eval_golden(db: Session = Depends(get_db)) -> list[dict]:
    """The adjudicated (table-backed) golden cases the harness scores against."""
    return evalh.golden_set(db)


class GoldenIn(BaseModel):
    provision_type: str
    expected_verdict: str
    expected_codes: list[str] = []
    expected_attention: bool = False
    note: str = ""


@app.post("/eval/golden")
def eval_golden_create(body: GoldenIn, db: Session = Depends(get_db), actor: str = Depends(actor_of)) -> dict:
    g = models.EvalGoldenCase(**body.model_dump())
    db.add(g)
    db.commit()
    audit.log(db, phase="UX", action="GOLDEN_ADD", actor=actor, entity_type="golden", entity_id=g.id,
              summary=f"added golden case {body.provision_type}={body.expected_verdict}")
    return {"id": g.id}


@app.delete("/eval/golden/{case_id}")
def eval_golden_delete(case_id: str, db: Session = Depends(get_db), actor: str = Depends(actor_of)) -> dict:
    g = db.get(models.EvalGoldenCase, case_id)
    if g is None:
        raise HTTPException(404, "golden case not found")
    db.delete(g)
    db.commit()
    audit.log(db, phase="UX", action="GOLDEN_DELETE", actor=actor, entity_type="golden", entity_id=case_id,
              summary="removed golden case")
    return {"deleted": case_id}


@app.post("/eval/run")
def eval_run(db: Session = Depends(get_db), actor: str = Depends(actor_of)) -> dict:
    """Run the real multi-phase pipeline against the golden set; persists the run."""
    if not llm_client.llm_available():
        raise HTTPException(503, "LLM not configured — set ANTHROPIC_API_KEY")
    try:
        return evalh.run_eval(db, actor=actor)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))


@app.get("/eval/history")
def eval_history(db: Session = Depends(get_db)) -> list[dict]:
    """Past eval runs (for history + model-version drift)."""
    return evalh.history(db)
