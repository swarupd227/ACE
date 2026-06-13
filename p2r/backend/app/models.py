"""P2R data model — Phase 1 (Policy Intelligence Ingestion).

Mirrors the design's policy_document / policy_provision tables. Every provision
carries citation spans, a composite confidence, and a routing decision — the same
cited, confidence-gated discipline ACE uses for codes.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    payer: Mapped[str] = mapped_column(String(80), default="")
    title: Mapped[str] = mapped_column(String(200), default="")
    source_type: Mapped[str] = mapped_column(String(24), default="UPLOAD")  # UPLOAD|API|PORTAL|EMAIL
    doc_kind: Mapped[str] = mapped_column(String(40), default="")  # medical_policy|reimbursement|fee_schedule|bulletin
    content_hash: Mapped[str] = mapped_column(String(64), default="")
    raw_text: Mapped[str] = mapped_column(Text, default="")
    provision_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(24), default="ingested")
    model_version: Mapped[str] = mapped_column(String(60), default="")
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class PolicyProvision(Base):
    """One normalized policy provision extracted from a document, with citations."""
    __tablename__ = "policy_provisions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(ForeignKey("policy_documents.id"), index=True)
    payer: Mapped[str] = mapped_column(String(80), default="")
    provision_type: Mapped[str] = mapped_column(String(24), default="")  # COVERAGE|PRIOR_AUTH|FREQUENCY|MODIFIER|POS|DOCUMENTATION|BUNDLING|FEE
    summary: Mapped[str] = mapped_column(Text, default="")
    code_sets: Mapped[dict] = mapped_column(JSONB, default=dict)   # {cpt:[],icd:[],hcpcs:[],modifiers:[],pos:[]}
    conditions: Mapped[dict] = mapped_column(JSONB, default=dict)  # normalized predicates
    effective_from: Mapped[str] = mapped_column(String(10), default="")
    effective_thru: Mapped[str] = mapped_column(String(10), default="")
    citation_spans: Mapped[list] = mapped_column(JSONB, default=list)  # [{line_start,line_end,text,verified}]
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    conf_model: Mapped[float] = mapped_column(Float, default=0.0)
    conf_validator: Mapped[float] = mapped_column(Float, default=0.0)
    routing: Mapped[str] = mapped_column(String(16), default="")   # AUTO_LOAD|VERIFY|HOLD
    extraction_meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
