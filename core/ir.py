"""Canonical Intermediate Representation (IR) — the keystone shared contract.

Every artifact the platform produces — a medical code (ACE), a payer-policy
provision, or an engine rule (P2R) — is the SAME shape: a schema-validated object
that always carries its citations, provenance, effective dating and confidence.
LLMs draft into this IR; deterministic emitters (ACE's validation gates, P2R's rule
compilers) turn it into the final, engine-specific artifact. The model never writes
the production artifact directly.

Designing this contract up front (Phase 0) is what makes the eventual ACE↔P2R
convergence mechanical rather than a redesign. It is intentionally engine-agnostic.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    CODE = "code"                  # ACE: an assigned ICD/CPT/HCPCS code
    POLICY_PROVISION = "provision"  # P2R: an extracted payer-policy provision
    RULE = "rule"                  # P2R: an engine-ready rule recommendation


class Citation(BaseModel):
    """A verbatim anchor back into a source document — the audit defense and the
    hallucination control. No uncited assertion survives the pipeline."""
    source_id: str
    char_start: int = 0
    char_end: int = 0
    text: str = ""


class Provenance(BaseModel):
    """Full lineage: which model/prompt produced this, from which source, when."""
    model_version: str = ""
    prompt_version: str = ""
    source_hash: str = ""
    run_id: str = ""
    created_at: datetime | None = None


class Artifact(BaseModel):
    """The universal IR object. ACE codes and P2R rules are both instances."""
    artifact_type: ArtifactType
    tenant_id: str = ""                       # isolation is first-class
    payload: dict[str, Any] = Field(default_factory=dict)  # type-specific content
    citations: list[Citation] = Field(default_factory=list)
    guideline_citations: list[Citation] = Field(default_factory=list)
    provenance: Provenance = Field(default_factory=Provenance)
    confidence: float = 0.0                   # calibrated, [0,1]
    effective_from: date | None = None
    effective_thru: date | None = None
    resolved: bool = False                    # False → route to a human

    def is_cited(self) -> bool:
        """Hallucination control: an artifact with no citation is not trustworthy."""
        return bool(self.citations)
