"""P2R API — Phase 1 (Policy Intelligence Ingestion) on the shared core.

Endpoints turn a payer-policy document (pasted text, an uploaded PDF/image via the
shared vision-OCR, or the built-in sample) into structured, cited PolicyProvision
records with composite confidence and a routing decision.
"""
from __future__ import annotations

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

# One-way reuse: P2R imports the shared core. Nothing here touches the ACE app.
from core import llm_client
from core.ir import ArtifactType

from . import eval as evalh
from . import acquisition, denials, ingest, models, publish, replay, rule_ir, sample, validate
from .db import SessionLocal, get_db, init_db

app = FastAPI(title="P2R — Policy-to-Rule Intelligence (Nous RCM Framework)", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_DOC_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/webp"}


@app.on_event("startup")
def _startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        validate._seed_library(db)       # seed the read-only rule library if empty
        acquisition.seed_registry(db)    # seed payer master (MDM) + acquisition sources
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
def recommend_from_document(doc_id: str, db: Session = Depends(get_db)) -> dict:
    if not llm_client.llm_available():
        raise HTTPException(503, "LLM not configured — set ANTHROPIC_API_KEY")
    try:
        return validate.generate_for_document(db, doc_id)
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
def edit_recommendation(rec_id: str, body: RecPatch, db: Session = Depends(get_db)) -> dict:
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
    return validate.rec_dict(rec)


# --- Phase 5: human approval + "Publish to ACE" integration glimpse ----------
@app.post("/recommendations/{rec_id}/approve")
def approve_recommendation(rec_id: str, db: Session = Depends(get_db)) -> dict:
    """A reviewer signs off a recommendation; only APPROVED rules may be published to ACE."""
    rec = db.get(models.RuleRecommendation, rec_id)
    if rec is None:
        raise HTTPException(404, "recommendation not found")
    if rec.status == "PUBLISHED":
        raise HTTPException(409, "already published")
    rec.status = "APPROVED"
    db.add(rec)
    db.commit()
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
def recommendation_rollback(rec_id: str, db: Session = Depends(get_db)) -> dict:
    """Retract a published rule from ACE and revert it to APPROVED."""
    try:
        return publish.rollback_recommendation(db, rec_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:  # noqa: BLE001 — transport/HTTP failure reaching ACE
        raise HTTPException(502, f"rollback failed: {exc}")


@app.post("/recommendations/{rec_id}/publish-to-ace")
def publish_to_ace(rec_id: str, db: Session = Depends(get_db)) -> dict:
    """Write the approved rule into ACE via its public policy API (sandbox payer only)."""
    try:
        return publish.publish_recommendation(db, rec_id)
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
def acquire_source(source_id: str, db: Session = Depends(get_db)) -> dict:
    """Run the acquisition agent against a source: fetch → change-detect → ingest delta."""
    if not llm_client.llm_available():
        raise HTTPException(503, "LLM not configured — set ANTHROPIC_API_KEY")
    try:
        return acquisition.acquire(db, source_id)
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
def denials_detect(db: Session = Depends(get_db)) -> dict:
    """Re-derive ranked denial signals from the remittance data (statistics-only)."""
    try:
        return denials.detect_signals(db)
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
def denials_promote(signal_id: str, db: Session = Depends(get_db)) -> dict:
    """Promote a denial signal's proposed rule into the P3 review queue."""
    if not llm_client.llm_available():
        raise HTTPException(503, "LLM not configured — set ANTHROPIC_API_KEY")
    try:
        return denials.promote_signal(db, signal_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))


# --- Golden-set evaluation harness ------------------------------------------
@app.get("/eval/golden")
def eval_golden() -> list[dict]:
    """The adjudicated golden cases the harness scores against."""
    return evalh.golden_set()


@app.post("/eval/run")
def eval_run(db: Session = Depends(get_db)) -> dict:
    """Run the real pipeline against the golden set and return scored metrics."""
    if not llm_client.llm_available():
        raise HTTPException(503, "LLM not configured — set ANTHROPIC_API_KEY")
    try:
        return evalh.run_eval(db)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
