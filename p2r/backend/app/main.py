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

from . import ingest, models, sample
from .db import get_db, init_db

app = FastAPI(title="P2R — Policy-to-Rule Intelligence (Nous RCM Framework)", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_DOC_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/webp"}


@app.on_event("startup")
def _startup() -> None:
    init_db()


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
