"""SQLAlchemy ORM models — the data backbone for the coding pipeline,
reference data, knowledge graph, audit ledger, and evaluation harness."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Clinical work items
# ---------------------------------------------------------------------------
class Encounter(Base):
    __tablename__ = "encounters"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    mrn: Mapped[str] = mapped_column(String(32))
    patient_name: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    sex: Mapped[str] = mapped_column(String(1))  # M | F
    specialty: Mapped[str] = mapped_column(String(40))       # Radiology | E&M
    modality: Mapped[str] = mapped_column(String(40), default="")  # XR/CT/MRI for radiology
    encounter_type: Mapped[str] = mapped_column(String(40), default="")  # new/established (E&M)
    payer: Mapped[str] = mapped_column(String(60))
    pos: Mapped[str] = mapped_column(String(4), default="11")  # place of service
    dos: Mapped[str] = mapped_column(String(10))  # date of service YYYY-MM-DD
    client: Mapped[str] = mapped_column(String(80), default="")  # source client/health system
    source_system: Mapped[str] = mapped_column(String(40), default="PracticeAdmin")
    report_type: Mapped[str] = mapped_column(String(40), default="report")
    chart_text: Mapped[str] = mapped_column(Text)
    # demo authoring metadata: what this synthetic chart is designed to exercise
    scenario: Mapped[str] = mapped_column(String(80), default="")
    status: Mapped[str] = mapped_column(String(24), default="NEW")  # NEW|CODED|...
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)  # queue arrival (for SLA aging)

    runs: Mapped[list["CodingRun"]] = relationship(back_populates="encounter", cascade="all,delete-orphan")


class CodingRun(Base):
    __tablename__ = "coding_runs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    encounter_id: Mapped[str] = mapped_column(ForeignKey("encounters.id"))
    status: Mapped[str] = mapped_column(String(24), default="PENDING")  # PENDING|RUNNING|DONE|ERROR
    routing_lane: Mapped[str] = mapped_column(String(12), default="")   # STB|QA|MANUAL
    routing_reason: Mapped[str] = mapped_column(Text, default="")
    model_version: Mapped[str] = mapped_column(String(60), default="")
    chart_summary: Mapped[str] = mapped_column(Text, default="")
    eligibility: Mapped[dict] = mapped_column(JSONB, default=dict)      # Stage 0 result
    stage_log: Mapped[list] = mapped_column(JSONB, default=list)        # ordered per-stage trace
    overall_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    accuracy_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    # workflow orchestration (human actions)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    escalated_to: Mapped[str] = mapped_column(String(80), default="")
    assigned_to: Mapped[str] = mapped_column(String(80), default="")
    priority: Mapped[str] = mapped_column(String(12), default="normal")  # normal | high
    ai_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict)  # original AI output for rollback/undo
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    encounter: Mapped[Encounter] = relationship(back_populates="runs")
    codes: Mapped[list["CodeResult"]] = relationship(back_populates="run", cascade="all,delete-orphan")


class CodeResult(Base):
    __tablename__ = "code_results"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(ForeignKey("coding_runs.id"))
    code_system: Mapped[str] = mapped_column(String(12))   # ICD10CM | CPT | HCPCS
    code: Mapped[str] = mapped_column(String(16))
    description: Mapped[str] = mapped_column(Text, default="")
    role: Mapped[str] = mapped_column(String(24), default="")  # principal|primary|secondary|procedure
    modifiers: Mapped[list] = mapped_column(JSONB, default=list)
    sequence: Mapped[int] = mapped_column(Integer, default=0)

    # confidence (calibrated overall + the 4 source factors VHT asked for)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    conf_doc_match: Mapped[float] = mapped_column(Float, default=0.0)
    conf_historical: Mapped[float] = mapped_column(Float, default=0.0)
    conf_rule: Mapped[float] = mapped_column(Float, default=0.0)
    conf_model: Mapped[float] = mapped_column(Float, default=0.0)

    chart_citations: Mapped[list] = mapped_column(JSONB, default=list)
    guideline_citations: Mapped[list] = mapped_column(JSONB, default=list)
    rule_justification: Mapped[str] = mapped_column(Text, default="")
    gate_results: Mapped[list] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(String(24), default="candidate")  # candidate|accepted|rejected|needs_review

    # human-in-the-loop
    is_overridden: Mapped[bool] = mapped_column(Boolean, default=False)
    override_code: Mapped[str] = mapped_column(String(16), default="")
    override_reason: Mapped[str] = mapped_column(Text, default="")
    accepted_by: Mapped[str] = mapped_column(String(80), default="")
    learning_applied: Mapped[bool] = mapped_column(Boolean, default=False)  # influenced by a learned correction

    run: Mapped[CodingRun] = relationship(back_populates="codes")


# ---------------------------------------------------------------------------
# Reference data (effective-dated). ICD-10-CM / HCPCS = real public subsets.
# CPT = clearly-labeled DEMO placeholder (source field), swap-in licensed AMA for prod.
# ---------------------------------------------------------------------------
class ReferenceCode(Base):
    __tablename__ = "reference_codes"
    __table_args__ = (UniqueConstraint("code_system", "code", name="uq_refcode"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code_system: Mapped[str] = mapped_column(String(12))
    code: Mapped[str] = mapped_column(String(16))
    description: Mapped[str] = mapped_column(Text)
    billable: Mapped[bool] = mapped_column(Boolean, default=True)
    parent: Mapped[str] = mapped_column(String(16), default="")
    sex_restriction: Mapped[str] = mapped_column(String(1), default="")  # ""|M|F
    age_min: Mapped[int] = mapped_column(Integer, default=0)
    age_max: Mapped[int] = mapped_column(Integer, default=130)
    modality: Mapped[str] = mapped_column(String(20), default="")        # for CPT radiology
    effective_start: Mapped[str] = mapped_column(String(10), default="2025-10-01")
    effective_end: Mapped[str] = mapped_column(String(10), default="2099-12-31")
    source: Mapped[str] = mapped_column(String(40), default="CMS")        # CMS | AMA | DEMO_PLACEHOLDER


class NcciEdit(Base):
    """NCCI PTP (Procedure-to-Procedure) bundling edit."""
    __tablename__ = "ncci_edits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    column1: Mapped[str] = mapped_column(String(16))  # payable / comprehensive code
    column2: Mapped[str] = mapped_column(String(16))  # bundled / component code
    modifier_allowed: Mapped[bool] = mapped_column(Boolean, default=True)  # 0=never, 1=allowed w/ modifier
    rationale: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(40), default="CMS-NCCI")


class MueLimit(Base):
    """Medically Unlikely Edit — max units per code per day."""
    __tablename__ = "mue_limits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    max_units: Mapped[int] = mapped_column(Integer)
    rationale: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(40), default="CMS-MUE")


class ModifierRule(Base):
    """Validity / meaning of modifiers and which code families they apply to."""
    __tablename__ = "modifier_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    modifier: Mapped[str] = mapped_column(String(4))
    description: Mapped[str] = mapped_column(Text)
    applies_to: Mapped[str] = mapped_column(String(40), default="")  # e.g. "CPT" | "radiology"
    notes: Mapped[str] = mapped_column(Text, default="")


class GuidelineChunk(Base):
    """Indexed coding-guideline text for citation verification + retrieval.
    Public sources only (ICD-10-CM Official Guidelines, NCCI policy manual)."""
    __tablename__ = "guideline_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(80))
    section: Mapped[str] = mapped_column(String(40))
    text: Mapped[str] = mapped_column(Text)
    specialty: Mapped[str] = mapped_column(String(40), default="")


# ---------------------------------------------------------------------------
# Knowledge graph (payer policy + medical ontology) for Graph-RAG
# ---------------------------------------------------------------------------
class PayerPolicy(Base):
    __tablename__ = "payer_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payer: Mapped[str] = mapped_column(String(60))
    code: Mapped[str] = mapped_column(String(16))
    policy_id: Mapped[str] = mapped_column(String(40), default="")
    medical_necessity: Mapped[str] = mapped_column(Text, default="")
    requires_auth: Mapped[bool] = mapped_column(Boolean, default=False)
    modifier_pref: Mapped[str] = mapped_column(String(60), default="")
    covered_dx: Mapped[list] = mapped_column(JSONB, default=list)  # ICD-10 prefixes supporting necessity
    source: Mapped[str] = mapped_column(String(60), default="DEMO-PayerPolicy")


class OntologyConcept(Base):
    __tablename__ = "ontology_concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cui: Mapped[str] = mapped_column(String(24), unique=True)  # concept id
    name: Mapped[str] = mapped_column(String(160))
    semantic_type: Mapped[str] = mapped_column(String(60), default="")
    maps_to: Mapped[list] = mapped_column(JSONB, default=list)  # [{system, code}]


class OntologyEdge(Base):
    __tablename__ = "ontology_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    src_cui: Mapped[str] = mapped_column(String(24))
    rel: Mapped[str] = mapped_column(String(40))  # is_a | finding_site | causative_agent | associated_with
    dst_cui: Mapped[str] = mapped_column(String(24))


# ---------------------------------------------------------------------------
# Audit ledger (append-only) + closed-loop learning + eval harness
# ---------------------------------------------------------------------------
class AuditEntry(Base):
    __tablename__ = "audit_ledger"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(String(32), index=True)
    encounter_id: Mapped[str] = mapped_column(String(32), index=True)
    stage: Mapped[str] = mapped_column(String(40))
    actor: Mapped[str] = mapped_column(String(40), default="system")  # system | model | coder:<id>
    event: Mapped[str] = mapped_column(String(80))
    detail: Mapped[dict] = mapped_column(JSONB, default=dict)
    model_version: Mapped[str] = mapped_column(String(60), default="")
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class LearningExample(Base):
    """A captured coder correction → becomes a retrieval exemplar that visibly
    shifts later similar charts (closed-loop learning; batch 24-48h in prod)."""
    __tablename__ = "learning_examples"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    specialty: Mapped[str] = mapped_column(String(40))
    pattern_key: Mapped[str] = mapped_column(String(120), index=True)  # e.g. modality+anatomy signature
    wrong_code: Mapped[str] = mapped_column(String(16), default="")
    correct_code: Mapped[str] = mapped_column(String(16))
    code_system: Mapped[str] = mapped_column(String(12))
    reason: Mapped[str] = mapped_column(Text, default="")
    snippet: Mapped[str] = mapped_column(Text, default="")
    applied: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CdiQuery(Base):
    """A compliant, non-leading physician query raised when documentation is
    insufficient to support a more specific/accurate code (CDI workflow)."""
    __tablename__ = "cdi_queries"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    encounter_id: Mapped[str] = mapped_column(String(32), index=True)
    run_id: Mapped[str] = mapped_column(String(32), default="")
    specialty: Mapped[str] = mapped_column(String(40), default="")
    status: Mapped[str] = mapped_column(String(16), default="open")  # open | answered
    question: Mapped[str] = mapped_column(Text)
    clinical_indicators: Mapped[str] = mapped_column(Text, default="")
    options: Mapped[list] = mapped_column(JSONB, default=list)  # incl. "Unable to determine"
    target: Mapped[str] = mapped_column(String(120), default="")
    potential_codes: Mapped[list] = mapped_column(JSONB, default=list)
    rationale: Mapped[str] = mapped_column(Text, default="")
    physician_response: Mapped[str] = mapped_column(Text, default="")
    responded_by: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AppConfig(Base):
    """Admin-editable platform configuration (key → JSON value). The pipeline,
    validation, SLA and eligibility read these at runtime so an admin can tune
    the platform without code changes."""
    __tablename__ = "app_config"

    key: Mapped[str] = mapped_column(String(60), primary_key=True)
    value: Mapped[dict] = mapped_column(JSONB)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ConfigAudit(Base):
    """Append-only change log for every admin/governance edit — config changes,
    payer-policy / ontology / guideline / reference-data / golden-set edits.
    Distinct from the per-encounter audit_ledger; this is the platform-admin trail."""
    __tablename__ = "config_audit"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    actor: Mapped[str] = mapped_column(String(60), default="system")
    role: Mapped[str] = mapped_column(String(40), default="")
    area: Mapped[str] = mapped_column(String(40))     # config|policy|ontology|guideline|reference|ncci|mue|modifier|golden|connector
    action: Mapped[str] = mapped_column(String(16))   # create|update|delete|reset
    target: Mapped[str] = mapped_column(String(160), default="")
    detail: Mapped[dict] = mapped_column(JSONB, default=dict)


class GoldenCase(Base):
    """Frozen golden-set case for the evaluation harness."""
    __tablename__ = "golden_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    specialty: Mapped[str] = mapped_column(String(40))
    chart_text: Mapped[str] = mapped_column(Text)
    truth: Mapped[dict] = mapped_column(JSONB)  # adjudicated codes
    irr: Mapped[float] = mapped_column(Float, default=0.0)  # inter-rater reliability for the set
    ambiguous: Mapped[bool] = mapped_column(Boolean, default=False)
