"""Pydantic schemas for the API surface."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


# --- Encounters ------------------------------------------------------------
class EncounterSummary(BaseModel):
    id: str
    mrn: str
    patient_name: str
    age: int
    sex: str
    specialty: str
    modality: str
    payer: str
    dos: str
    client: str
    scenario: str
    status: str
    routing_lane: str = ""
    overall_confidence: float = 0.0


class Citation(BaseModel):
    section: str = ""
    line_start: int = 0
    line_end: int = 0
    text: str = ""


class GuidelineCitation(BaseModel):
    source: str = ""
    section: str = ""
    text: str = ""


class GateResult(BaseModel):
    gate: str
    passed: bool
    detail: str = ""


class CodeOut(BaseModel):
    id: str
    code_system: str
    code: str
    description: str
    role: str
    modifiers: list[str] = []
    sequence: int = 0
    confidence: float
    conf_doc_match: float
    conf_historical: float
    conf_rule: float
    conf_model: float
    chart_citations: list[dict[str, Any]] = []
    guideline_citations: list[dict[str, Any]] = []
    rule_justification: str = ""
    gate_results: list[dict[str, Any]] = []
    status: str
    is_overridden: bool = False
    override_code: str = ""
    override_reason: str = ""


class RunDetail(BaseModel):
    id: str
    encounter_id: str
    status: str
    routing_lane: str
    routing_reason: str
    model_version: str
    chart_summary: str
    eligibility: dict[str, Any]
    stage_log: list[dict[str, Any]]
    overall_confidence: float
    accuracy_estimate: float
    latency_ms: int
    codes: list[CodeOut]


# --- Human-in-the-loop -----------------------------------------------------
class OverrideRequest(BaseModel):
    override_code: str
    reason: str
    coder_id: str = "coder:demo"


class AcceptRequest(BaseModel):
    coder_id: str = "coder:demo"


# --- Dashboard / eval ------------------------------------------------------
class DashboardStats(BaseModel):
    total_encounters: int
    coded: int
    stb_count: int
    qa_count: int
    manual_count: int
    stb_rate: float
    avg_accuracy: float
    avg_latency_ms: int
    manual_effort_reduction: float
    by_specialty: list[dict[str, Any]]
