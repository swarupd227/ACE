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

# Canonical radiology modality tags used on CPT reference rows: XR, CT, MRI, US, MG, NM.
# The ingest `modality` field is free text, so normalize synonyms/casing to the canonical
# tag before the radiology candidate filter. Purely additive: exact tags still match; this
# only prevents a report from missing its codes (→ manual) on a modality-string mismatch.
_MODALITY_ALIASES = {
    "xr": "XR", "x-ray": "XR", "xray": "XR", "x ray": "XR", "cr": "XR", "dx": "XR",
    "radiograph": "XR", "radiography": "XR", "plain film": "XR", "dxa": "XR", "dexa": "XR",
    "bone density": "XR", "fluoro": "XR", "fluoroscopy": "XR",
    "ct": "CT", "cat": "CT", "cta": "CT", "ct angiography": "CT", "ct angio": "CT",
    "mri": "MRI", "mr": "MRI", "mra": "MRI", "mr angiography": "MRI", "mr angio": "MRI",
    "us": "US", "ultrasound": "US", "u/s": "US", "sonography": "US", "sonogram": "US",
    "sono": "US", "echo": "US", "doppler": "US", "duplex": "US", "color doppler": "US",
    "mg": "MG", "mammography": "MG", "mammogram": "MG", "mammo": "MG",
    "nm": "NM", "pet": "NM", "pet/ct": "NM", "nuclear": "NM", "nuclear medicine": "NM",
}

_REGION_LEXICON: dict[str, set[str]] = {
    "head_neuro": {
        "brain", "cranial", "intracranial", "frontal", "temporal", "parietal",
        "occipital", "cerebral", "meningioma", "head", "neuro", "ventricle",
    },
    "chest": {
        "chest", "lung", "lungs", "pulmonary", "pleura", "pleural", "thoracic",
        "pneumonia", "effusion", "atelectasis", "atelectatic", "mediastinum",
    },
    "upper_extremity": {
        "wrist", "hand", "forearm", "radius", "ulna", "carpal", "scaphoid",
        "metacarpal", "phalange", "elbow", "humerus", "shoulder",
    },
    "abdomen_pelvis": {
        "abdomen", "abdominal", "pelvis", "pelvic", "intraabdominal",
        "intra-abdominal", "retroperitoneum", "bowel", "colon", "liver",
        "kidney", "renal", "appendix", "diverticul", "ovary", "uterus",
    },
}

_TOKEN_NORMALIZE = {
    "atelectatic": "atelectasis",
    "atelectases": "atelectasis",
    "effusions": "effusion",
    "fractures": "fracture",
    "dislocations": "dislocation",
}


def _norm_modality(m: str) -> str:
    key = (m or "").strip().lower()
    return _MODALITY_ALIASES.get(key, (m or "").strip().upper())


def _tokens(text: str) -> set[str]:
    raw = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {_TOKEN_NORMALIZE.get(t, t) for t in raw if len(t) > 2 and t not in _STOP}


def _score(query_tokens: set[str], target: str) -> float:
    tt = _tokens(target)
    if not tt or not query_tokens:
        return 0.0
    return len(query_tokens & tt) / (len(query_tokens) ** 0.5)


def _anatomy_tokens_from_analysis(analysis: dict[str, Any]) -> set[str]:
    parts: list[str] = [analysis.get("summary", "")]
    parts.extend(d.get("text", "") for d in (analysis.get("diagnoses") or []) if isinstance(d, dict))
    for p in analysis.get("procedures", []) or []:
        if not isinstance(p, dict):
            continue
        parts.extend([p.get("anatomy", ""), p.get("text", "")])
    return _tokens(" ".join(parts))


def _body_region_hint(tokens: set[str]) -> str | None:
    best_region = None
    best_hits = 0
    for region, hints in _REGION_LEXICON.items():
        hits = len(tokens & hints)
        if hits > best_hits:
            best_hits = hits
            best_region = region
    return best_region if best_hits else None


def _region_from_description(description: str) -> str | None:
    return _body_region_hint(_tokens(description))


def _icd_region_adjustment(description: str, chart_region: str | None) -> float:
    if not chart_region:
        return 0.0
    desc_region = _region_from_description(description)
    if not desc_region:
        return 0.0
    if desc_region == chart_region:
        return 0.25
    return -0.35


def _analysis_modality(analysis: dict[str, Any]) -> str:
    for proc in analysis.get("procedures", []) or []:
        if not isinstance(proc, dict):
            continue
        mod = _norm_modality(proc.get("modality", ""))
        if mod:
            return mod
    return ""


@dataclass
class Retrieval:
    icd_candidates: list[dict[str, Any]] = field(default_factory=list)
    proc_candidates: list[dict[str, Any]] = field(default_factory=list)
    guideline_excerpts: list[dict[str, Any]] = field(default_factory=list)
    payer_policies: list[dict[str, Any]] = field(default_factory=list)
    ontology_paths: list[dict[str, Any]] = field(default_factory=list)
    learned: list[dict[str, Any]] = field(default_factory=list)
    chart_region: str | None = None
    chart_modality: str | None = None

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

    dx_text = " ".join(
        [analysis.get("summary", "")]
        + [d.get("text", "") for d in analysis.get("diagnoses", [])]
    )
    proc_text = " ".join(
        f"{p.get('modality','')} {p.get('anatomy','')} {p.get('text','')} {p.get('contrast','')}"
        for p in analysis.get("procedures", [])
    )
    anatomy_tokens = _anatomy_tokens_from_analysis(analysis)
    chart_region = _body_region_hint(anatomy_tokens)
    chart_modality = _analysis_modality(analysis)
    r.chart_region = chart_region
    r.chart_modality = chart_modality or None
    dx_tokens = _tokens(dx_text)
    proc_tokens = _tokens(proc_text + " " + (chart_modality or encounter.modality))

    # --- ICD-10-CM candidates (lexical over real public descriptions) ---
    icd = db.scalars(select(models.ReferenceCode).where(models.ReferenceCode.code_system == "ICD10CM")).all()
    icd_scored = sorted(
        ((
            _score(dx_tokens, c.description + " " + c.code)
            + _icd_region_adjustment(c.description, chart_region),
            c,
        ) for c in icd),
        key=lambda x: x[0], reverse=True,
    )
    r.icd_candidates = [
        {"code": c.code, "description": c.description, "billable": c.billable,
         "sex_restriction": c.sex_restriction, "age_min": c.age_min, "age_max": c.age_max}
        for s, c in icd_scored[:top_k] if s > 0
    ]

    # --- Procedure candidates, specialty/modality aware ---
    if encounter.specialty == "Inpatient (DRG)":
        # Inpatient codes ICD-10-PCS procedures (a different code set from outpatient CPT).
        pcs = db.scalars(
            select(models.ReferenceCode).where(models.ReferenceCode.code_system == "ICD10PCS")
        ).all()
        pcs_scored = sorted(
            ((_score(proc_tokens, c.description + " " + c.code), c) for c in pcs),
            key=lambda x: x[0], reverse=True,
        )
        r.proc_candidates = [
            {"code": c.code, "description": c.description, "modality": "ICD10PCS", "source": c.source}
            for s, c in pcs_scored[:top_k] if s > 0
        ]
    elif encounter.specialty in ("E&M", "ED"):
        # The billable procedure IS the visit-level code; surface the whole family so the agent
        # can pick the level from MDM/time. No imaging text to score against, so no lexical filter.
        procs = db.scalars(
            select(models.ReferenceCode).where(models.ReferenceCode.code_system.in_(["CPT", "HCPCS"]))
        ).all()
        tag = "EM_OFFICE" if encounter.specialty == "E&M" else "ED"
        fam = [c for c in procs if c.modality == tag]
        r.proc_candidates = [
            {"code": c.code, "description": c.description, "modality": c.modality, "source": c.source}
            for c in sorted(fam, key=lambda c: c.code)
        ]
    else:
        procs = db.scalars(
            select(models.ReferenceCode).where(models.ReferenceCode.code_system.in_(["CPT", "HCPCS"]))
        ).all()
        if encounter.specialty == "Radiology":
            enc_mod = chart_modality or _norm_modality(encounter.modality)
            procs = [c for c in procs
                     if (not c.modality) or c.modality == "ANY" or _norm_modality(c.modality) == enc_mod]
        elif encounter.specialty == "Pathology":
            procs = [c for c in procs if c.modality in ("PATH", "ANY", "")]
        elif encounter.specialty == "Surgical":
            procs = [c for c in procs if c.modality in ("SURG", "ANY", "")]
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
