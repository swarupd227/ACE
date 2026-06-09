"""Idempotent database initialization and data seeding."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text

from .. import config_store, models
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
        config_store.seed_defaults(db)  # idempotent — ensures admin config exists
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

        # encounters (work items) — stagger arrival times so SLA aging is realistic
        now = datetime.now(timezone.utc)
        for i, ch in enumerate(charts.CHARTS):
            enc = models.Encounter(**ch)
            # spread arrivals across the last ~3.5 hours so SLA shows a realistic
            # on-track / at-risk / breached mix (deterministic, varied)
            enc.received_at = now - timedelta(minutes=(i * 11 + (i % 3) * 18))
            db.add(enc)

        db.commit()
        return {
            "status": "seeded",
            "reference_codes": len(rd.ICD10CM) + len(rd.CPT) + len(rd.HCPCS),
            "encounters": len(charts.CHARTS),
            "golden_cases": len(charts.GOLDEN_CASES),
        }
    finally:
        db.close()


def seed_missing() -> dict:
    """Incrementally add only the rows not already present (matched by natural key).

    Lets a NEW specialty's reference data, knowledge-graph, guidelines, golden cases
    and worklist charts be loaded into a running database WITHOUT a destructive reseed
    (which would re-code every chart and burn LLM credits). Idempotent — safe to run
    repeatedly; on an up-to-date DB it adds nothing. The new charts arrive as NEW, so a
    subsequent /coding/run-all codes only them (~one specialty's worth)."""
    init_db()
    db = SessionLocal()
    added: dict[str, int] = {}

    def bump(k: str, n: int = 1) -> None:
        if n:
            added[k] = added.get(k, 0) + n

    try:
        config_store.seed_defaults(db)

        # Reconcile the specialties config so a newly-added specialty surfaces in the
        # UI/meta without a reseed (all_config overlays the stored value over DEFAULTS).
        stored = config_store.get(db, "specialties")
        names = {s["name"] for s in stored}
        new_specs = [s for s in config_store.DEFAULTS["specialties"] if s["name"] not in names]
        if new_specs:
            config_store.set_key(db, "specialties", stored + new_specs)
            bump("specialties", len(new_specs))

        # reference codes — key (code_system, code)
        ref = {(c.code_system, c.code) for c in db.scalars(select(models.ReferenceCode)).all()}
        for code, desc, billable, parent in rd.ICD10CM:
            if ("ICD10CM", code) not in ref:
                db.add(models.ReferenceCode(code_system="ICD10CM", code=code, description=desc,
                                            billable=billable, parent=parent, source="CMS", **rd.EFF))
                ref.add(("ICD10CM", code)); bump("reference_codes")
        for code, desc, modality in rd.CPT:
            if ("CPT", code) not in ref:
                db.add(models.ReferenceCode(code_system="CPT", code=code, description=desc,
                                            modality=modality, source="DEMO_PLACEHOLDER", **rd.EFF))
                ref.add(("CPT", code)); bump("reference_codes")
        for code, desc, modality in rd.HCPCS:
            if ("HCPCS", code) not in ref:
                db.add(models.ReferenceCode(code_system="HCPCS", code=code, description=desc,
                                            modality=modality, source="CMS", **rd.EFF))
                ref.add(("HCPCS", code)); bump("reference_codes")

        # modifiers — key (modifier, applies_to)
        mods = {(m.modifier, m.applies_to) for m in db.scalars(select(models.ModifierRule)).all()}
        for mod, desc, applies, notes in rd.MODIFIERS:
            if (mod, applies) not in mods:
                db.add(models.ModifierRule(modifier=mod, description=desc, applies_to=applies, notes=notes))
                mods.add((mod, applies)); bump("modifiers")

        # NCCI — key (column1, column2)
        ncci = {(e.column1, e.column2) for e in db.scalars(select(models.NcciEdit)).all()}
        for c1, c2, allowed, rationale in rd.NCCI:
            if (c1, c2) not in ncci:
                db.add(models.NcciEdit(column1=c1, column2=c2, modifier_allowed=allowed, rationale=rationale))
                ncci.add((c1, c2)); bump("ncci")

        # MUE — key code (unique)
        mue = {m.code for m in db.scalars(select(models.MueLimit)).all()}
        for code, units, rationale in rd.MUE:
            if code not in mue:
                db.add(models.MueLimit(code=code, max_units=units, rationale=rationale))
                mue.add(code); bump("mue")

        # payer policy — key (payer, code)
        pp = {(p.payer, p.code) for p in db.scalars(select(models.PayerPolicy)).all()}
        for payer, code, mn, auth, modpref, dx in rd.PAYER_POLICY:
            if (payer, code) not in pp:
                db.add(models.PayerPolicy(payer=payer, code=code, medical_necessity=mn,
                                          requires_auth=auth, modifier_pref=modpref, covered_dx=dx))
                pp.add((payer, code)); bump("payer_policy")

        # ontology concepts — key cui (unique)
        cuis = {c.cui for c in db.scalars(select(models.OntologyConcept)).all()}
        for cui, name, st, maps in rd.ONTOLOGY_CONCEPTS:
            if cui not in cuis:
                db.add(models.OntologyConcept(cui=cui, name=name, semantic_type=st, maps_to=maps))
                cuis.add(cui); bump("ontology_concepts")

        # ontology edges — key (src, rel, dst)
        edges = {(e.src_cui, e.rel, e.dst_cui) for e in db.scalars(select(models.OntologyEdge)).all()}
        for src, rel, dst in rd.ONTOLOGY_EDGES:
            if (src, rel, dst) not in edges:
                db.add(models.OntologyEdge(src_cui=src, rel=rel, dst_cui=dst))
                edges.add((src, rel, dst)); bump("ontology_edges")

        # guidelines — key (source, section, specialty)
        gl = {(g.source, g.section, g.specialty) for g in db.scalars(select(models.GuidelineChunk)).all()}
        for source, section, t, spec in rd.GUIDELINES:
            if (source, section, spec) not in gl:
                db.add(models.GuidelineChunk(source=source, section=section, text=t, specialty=spec))
                gl.add((source, section, spec)); bump("guidelines")

        # golden set — key (specialty, chart_text)
        gold = {(g.specialty, g.chart_text) for g in db.scalars(select(models.GoldenCase)).all()}
        for g in charts.GOLDEN_CASES:
            key = (g["specialty"], g["chart_text"])
            if key not in gold:
                db.add(models.GoldenCase(specialty=g["specialty"], chart_text=g["chart_text"],
                                         truth=g["truth"], irr=g["irr"], ambiguous=g["ambiguous"]))
                gold.add(key); bump("golden_cases")

        # encounters — key mrn (new charts arrive as NEW, ready for run-all)
        mrns = {e.mrn for e in db.scalars(select(models.Encounter)).all()}
        now = datetime.now(timezone.utc)
        for i, ch in enumerate(charts.CHARTS):
            if ch["mrn"] not in mrns:
                enc = models.Encounter(**ch)
                enc.received_at = now - timedelta(minutes=(i % 6) * 9)
                db.add(enc)
                mrns.add(ch["mrn"]); bump("encounters")

        db.commit()
        return {"status": "ok", "added": added}
    finally:
        db.close()
