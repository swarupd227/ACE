"""Idempotent database initialization and data seeding."""
from __future__ import annotations

from sqlalchemy import select, text

from .. import models
from ..db import Base, SessionLocal, engine
from . import charts, reference_data as rd


def init_db() -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)


def _seeded(db) -> bool:
    return db.scalar(select(models.ReferenceCode).limit(1)) is not None


def seed_all(force: bool = False) -> dict:
    init_db()
    db = SessionLocal()
    try:
        if _seeded(db) and not force:
            return {"status": "already_seeded"}

        # reference codes
        for code, desc, billable, parent in rd.ICD10CM:
            db.add(models.ReferenceCode(code_system="ICD10CM", code=code, description=desc,
                                        billable=billable, parent=parent, source="CMS", **rd.EFF))
        for code, desc, modality in rd.CPT:
            db.add(models.ReferenceCode(code_system="CPT", code=code, description=desc,
                                        modality=modality, source="DEMO_PLACEHOLDER", **rd.EFF))
        for code, desc, modality in rd.HCPCS:
            db.add(models.ReferenceCode(code_system="HCPCS", code=code, description=desc,
                                        modality=modality, source="CMS", **rd.EFF))
        for mod, desc, applies, notes in rd.MODIFIERS:
            db.add(models.ModifierRule(modifier=mod, description=desc, applies_to=applies, notes=notes))
        for c1, c2, allowed, rationale in rd.NCCI:
            db.add(models.NcciEdit(column1=c1, column2=c2, modifier_allowed=allowed, rationale=rationale))
        for code, units, rationale in rd.MUE:
            db.add(models.MueLimit(code=code, max_units=units, rationale=rationale))
        for payer, code, mn, auth, modpref, dx in rd.PAYER_POLICY:
            db.add(models.PayerPolicy(payer=payer, code=code, medical_necessity=mn,
                                      requires_auth=auth, modifier_pref=modpref, covered_dx=dx))
        for cui, name, st, maps in rd.ONTOLOGY_CONCEPTS:
            db.add(models.OntologyConcept(cui=cui, name=name, semantic_type=st, maps_to=maps))
        for src, rel, dst in rd.ONTOLOGY_EDGES:
            db.add(models.OntologyEdge(src_cui=src, rel=rel, dst_cui=dst))
        for source, section, t, spec in rd.GUIDELINES:
            db.add(models.GuidelineChunk(source=source, section=section, text=t, specialty=spec))

        # golden set
        for g in charts.GOLDEN_CASES:
            db.add(models.GoldenCase(specialty=g["specialty"], chart_text=g["chart_text"],
                                     truth=g["truth"], irr=g["irr"], ambiguous=g["ambiguous"]))

        # encounters (work items)
        for ch in charts.CHARTS:
            db.add(models.Encounter(**ch))

        db.commit()
        return {
            "status": "seeded",
            "reference_codes": len(rd.ICD10CM) + len(rd.CPT) + len(rd.HCPCS),
            "encounters": len(charts.CHARTS),
            "golden_cases": len(charts.GOLDEN_CASES),
        }
    finally:
        db.close()
