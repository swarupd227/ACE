"""Graph-RAG retrieval over the payer-policy + medical-ontology knowledge graph,
the code-set reference tables, the indexed coding guidelines, and learned
corrections. This grounds the coding agent (Amrish's #1 ask) and is also a
hallucination control: the agent may only use codes surfaced here.

Retrieval is real and offline: lexical scoring + ontology graph traversal.
pgvector columns are reserved for production embedding retrieval.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models

_STOP = {"the", "a", "an", "of", "and", "or", "with", "without", "no", "left", "right",
         "patient", "history", "for", "to", "in", "on", "is", "are", "was"}


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(t) > 2 and t not in _STOP}


def _score(query_tokens: set[str], target: str) -> float:
    tt = _tokens(target)
    if not tt or not query_tokens:
        return 0.0
    return len(query_tokens & tt) / (len(query_tokens) ** 0.5)


@dataclass
class Retrieval:
    icd_candidates: list[dict[str, Any]] = field(default_factory=list)
    proc_candidates: list[dict[str, Any]] = field(default_factory=list)
    guideline_excerpts: list[dict[str, Any]] = field(default_factory=list)
    payer_policies: list[dict[str, Any]] = field(default_factory=list)
    ontology_paths: list[dict[str, Any]] = field(default_factory=list)
    learned: list[dict[str, Any]] = field(default_factory=list)

    def as_prompt_context(self) -> str:
        import json

        def block(title: str, rows: list[dict]) -> str:
            return f"## {title}\n" + (json.dumps(rows, indent=2) if rows else "(none)") + "\n"

        return "\n".join([
            block("CANDIDATE ICD-10-CM CODES", self.icd_candidates),
            block("CANDIDATE PROCEDURE CODES (CPT/HCPCS)", self.proc_candidates),
            block("ONTOLOGY PATHS (concept graph)", self.ontology_paths),
            block("PAYER POLICY / MEDICAL NECESSITY", self.payer_policies),
            block("GUIDELINE EXCERPTS", self.guideline_excerpts),
            block("LEARNED CORRECTIONS (apply these)", self.learned),
        ])


def pattern_key(specialty: str, analysis: dict) -> str:
    """A stable signature for closed-loop learning matching."""
    procs = analysis.get("procedures") or []
    if procs:
        p = procs[0]
        return f"{specialty}:{p.get('modality','')}:{p.get('anatomy','')}:{p.get('contrast','')}".lower()
    dx = (analysis.get("diagnoses") or [{}])[0]
    return f"{specialty}:dx:{(dx.get('text') or '')[:30]}".lower()


def retrieve(db: Session, encounter: models.Encounter, analysis: dict, *, top_k: int = 12) -> Retrieval:
    r = Retrieval()

    dx_text = " ".join(d.get("text", "") for d in analysis.get("diagnoses", []))
    proc_text = " ".join(
        f"{p.get('modality','')} {p.get('anatomy','')} {p.get('text','')} {p.get('contrast','')}"
        for p in analysis.get("procedures", [])
    )
    dx_tokens = _tokens(dx_text)
    proc_tokens = _tokens(proc_text + " " + encounter.modality)

    # --- ICD-10-CM candidates (lexical over real public descriptions) ---
    icd = db.scalars(select(models.ReferenceCode).where(models.ReferenceCode.code_system == "ICD10CM")).all()
    icd_scored = sorted(
        ((_score(dx_tokens, c.description + " " + c.code), c) for c in icd),
        key=lambda x: x[0], reverse=True,
    )
    r.icd_candidates = [
        {"code": c.code, "description": c.description, "billable": c.billable,
         "sex_restriction": c.sex_restriction, "age_min": c.age_min, "age_max": c.age_max}
        for s, c in icd_scored[:top_k] if s > 0
    ]

    # --- Procedure (CPT/HCPCS) candidates, specialty/modality aware ---
    procs = db.scalars(
        select(models.ReferenceCode).where(models.ReferenceCode.code_system.in_(["CPT", "HCPCS"]))
    ).all()
    if encounter.specialty in ("E&M", "ED"):
        # The billable procedure IS the visit-level code; surface the whole family so the agent
        # can pick the level from MDM/time. No imaging text to score against, so no lexical filter.
        tag = "EM_OFFICE" if encounter.specialty == "E&M" else "ED"
        fam = [c for c in procs if c.modality == tag]
        r.proc_candidates = [
            {"code": c.code, "description": c.description, "modality": c.modality, "source": c.source}
            for c in sorted(fam, key=lambda c: c.code)
        ]
    else:
        if encounter.specialty == "Radiology":
            procs = [c for c in procs if (not c.modality) or c.modality == encounter.modality or c.modality == "ANY"]
        proc_scored = sorted(
            ((_score(proc_tokens, c.description + " " + c.modality), c) for c in procs),
            key=lambda x: x[0], reverse=True,
        )
        r.proc_candidates = [
            {"code": c.code, "description": c.description, "modality": c.modality, "source": c.source}
            for s, c in proc_scored[:top_k] if s > 0
        ]

    # --- Ontology graph traversal: match concepts to diagnoses, walk edges ---
    concepts = db.scalars(select(models.OntologyConcept)).all()
    edges = db.scalars(select(models.OntologyEdge)).all()
    by_cui = {c.cui: c for c in concepts}
    for c in concepts:
        if _score(dx_tokens, c.name) > 0:
            neighbors = [
                {"rel": e.rel, "to": by_cui[e.dst_cui].name if e.dst_cui in by_cui else e.dst_cui}
                for e in edges if e.src_cui == c.cui
            ]
            r.ontology_paths.append({
                "concept": c.name, "semantic_type": c.semantic_type,
                "maps_to": c.maps_to, "edges": neighbors,
            })

    # --- Payer policy for the encounter payer over candidate codes ---
    cand_codes = {x["code"] for x in (r.icd_candidates + r.proc_candidates)}
    pols = db.scalars(select(models.PayerPolicy).where(models.PayerPolicy.payer == encounter.payer)).all()
    r.payer_policies = [
        {"payer": p.payer, "code": p.code, "medical_necessity": p.medical_necessity,
         "requires_auth": p.requires_auth, "modifier_pref": p.modifier_pref, "covered_dx": p.covered_dx}
        for p in pols if p.code in cand_codes
    ]

    # --- Guideline excerpts (lexical over indexed public guidelines) ---
    gl = db.scalars(select(models.GuidelineChunk)).all()
    gl_scored = sorted(
        ((_score(dx_tokens | proc_tokens, g.text + " " + g.section), g) for g in gl),
        key=lambda x: x[0], reverse=True,
    )
    r.guideline_excerpts = [
        {"source": g.source, "section": g.section, "text": g.text}
        for s, g in gl_scored[:5] if s > 0
    ]

    # --- Learned corrections (closed-loop learning) ---
    key = pattern_key(encounter.specialty, analysis)
    learned = db.scalars(
        select(models.LearningExample).where(
            models.LearningExample.pattern_key == key, models.LearningExample.applied == True  # noqa: E712
        )
    ).all()
    r.learned = [
        {"pattern": le.pattern_key, "use_code": le.correct_code, "instead_of": le.wrong_code,
         "code_system": le.code_system, "reason": le.reason}
        for le in learned
    ]
    return r
