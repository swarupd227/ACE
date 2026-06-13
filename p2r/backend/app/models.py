"""P2R data model — Phase 1 (Policy Intelligence Ingestion).

Mirrors the design's policy_document / policy_provision tables. Every provision
carries citation spans, a composite confidence, and a routing decision — the same
cited, confidence-gated discipline ACE uses for codes.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
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


class RuleLibraryEntry(Base):
    """An existing, deployed rule — the read-only library P3 reconciles against."""
    __tablename__ = "rule_library"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # e.g. RULE-LUM-PA
    payer: Mapped[str] = mapped_column(String(80), default="")
    title: Mapped[str] = mapped_column(Text, default="")
    logic_summary: Mapped[str] = mapped_column(Text, default="")
    code_sets: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(16), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class RemittanceLine(Base):
    """Phase 2 input: one canonical 835 remittance line (synthetic, PHI-free)."""
    __tablename__ = "remittance_lines"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    payer: Mapped[str] = mapped_column(String(80), default="", index=True)
    claim_id: Mapped[str] = mapped_column(String(32), default="")
    procedure_code: Mapped[str] = mapped_column(String(16), default="", index=True)  # CPT/HCPCS
    denied: Mapped[bool] = mapped_column(Boolean, default=False)
    denial_carc: Mapped[str] = mapped_column(String(8), default="")  # Claim Adjustment Reason Code
    denial_rarc: Mapped[str] = mapped_column(String(8), default="")  # Remittance Advice Remark Code
    denial_reason: Mapped[str] = mapped_column(String(160), default="")
    billed_amount: Mapped[float] = mapped_column(Float, default=0.0)
    paid_amount: Mapped[float] = mapped_column(Float, default=0.0)
    service_date: Mapped[str] = mapped_column(String(10), default="")  # YYYY-MM-DD
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DenialSignal(Base):
    """Phase 2 output: a ranked, evidence-backed denial pattern + a proposed candidate rule."""
    __tablename__ = "denial_signals"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    payer: Mapped[str] = mapped_column(String(80), default="")
    procedure_code: Mapped[str] = mapped_column(String(16), default="")
    denial_carc: Mapped[str] = mapped_column(String(8), default="")
    pattern_type: Mapped[str] = mapped_column(String(20), default="")  # SPIKE|PERSISTENT|CO_OCCURRENCE
    recent_denials: Mapped[int] = mapped_column(Integer, default=0)
    recent_total: Mapped[int] = mapped_column(Integer, default=0)
    recent_rate: Mapped[float] = mapped_column(Float, default=0.0)
    baseline_rate: Mapped[float] = mapped_column(Float, default=0.0)
    lift: Mapped[float] = mapped_column(Float, default=0.0)         # recent_rate / baseline_rate
    z_score: Mapped[float] = mapped_column(Float, default=0.0)      # two-proportion test
    score: Mapped[float] = mapped_column(Float, default=0.0)        # composite ranking score
    rank: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="NEW")  # NEW|PROMOTED|DISMISSED
    evidence: Mapped[dict] = mapped_column(JSONB, default=dict)     # aggregates + sample remit lines
    proposed_rule: Mapped[dict] = mapped_column(JSONB, default=dict)  # {provision_type, summary, code_sets}
    promoted_recommendation_id: Mapped[str] = mapped_column(String(32), default="")
    model_version: Mapped[str] = mapped_column(String(60), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class RuleRecommendation(Base):
    """Phase 3 output: a validated, reconciled candidate rule awaiting human review."""
    __tablename__ = "rule_recommendations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    payer: Mapped[str] = mapped_column(String(80), default="")
    origin: Mapped[str] = mapped_column(String(16), default="POLICY")  # POLICY (P1) | DENIAL (P2)
    source_provision_id: Mapped[str] = mapped_column(String(32), default="")
    source_document_id: Mapped[str] = mapped_column(String(32), default="")
    source_signal_id: Mapped[str] = mapped_column(String(32), default="")
    candidate_summary: Mapped[str] = mapped_column(Text, default="")
    provision_type: Mapped[str] = mapped_column(String(24), default="")
    code_sets: Mapped[dict] = mapped_column(JSONB, default=dict)
    # (a) validation against policy evidence
    validation_verdict: Mapped[str] = mapped_column(String(16), default="")  # SUPPORTED|PARTIAL|UNSUPPORTED
    validation_rationale: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[list] = mapped_column(JSONB, default=list)  # [{provision_id, text}]
    # (b) reconciliation against the rule library
    reconciliation_verdict: Mapped[str] = mapped_column(String(16), default="")  # NET_NEW|UPDATE|DUPLICATE|CONFLICT
    matched_rule_id: Mapped[str] = mapped_column(String(40), default="")
    reconciliation_rationale: Mapped[str] = mapped_column(Text, default="")
    code_overlap: Mapped[float] = mapped_column(Float, default=0.0)  # deterministic cross-check
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="PENDING_REVIEW")  # PENDING_REVIEW|APPROVED|PUBLISHED
    needs_attention: Mapped[bool] = mapped_column(Boolean, default=False)
    model_version: Mapped[str] = mapped_column(String(60), default="")
    # Phase 5 — "Publish to ACE" integration glimpse (write-only, sandbox payer).
    published_to_ace: Mapped[bool] = mapped_column(Boolean, default=False)
    ace_publish: Mapped[dict] = mapped_column(JSONB, default=dict)  # {payer, source, policies:[{code,ace_id}], at}
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
