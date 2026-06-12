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
    # create_all only creates missing TABLES — additive columns on existing tables need
    # idempotent ALTERs so a running database upgrades without a destructive reseed.
    # Existing rows default to 'final'/attested, so already-coded charts behave identically.
    with engine.begin() as conn:
        for ddl in (
            "ALTER TABLE encounters ADD COLUMN IF NOT EXISTS patient_key VARCHAR(40) DEFAULT ''",
            "ALTER TABLE encounters ADD COLUMN IF NOT EXISTS doc_status VARCHAR(16) DEFAULT 'final'",
            "ALTER TABLE encounters ADD COLUMN IF NOT EXISTS signed_by VARCHAR(120) DEFAULT ''",
            "ALTER TABLE encounters ADD COLUMN IF NOT EXISTS signed_at TIMESTAMPTZ",
            "ALTER TABLE encounters ADD COLUMN IF NOT EXISTS addendum_at TIMESTAMPTZ",
            "ALTER TABLE coding_runs ADD COLUMN IF NOT EXISTS billed_at TIMESTAMPTZ",
            "ALTER TABLE hcc_results ADD COLUMN IF NOT EXISTS recapture_gaps JSONB DEFAULT '[]'",
        ):
            conn.execute(text(ddl))


def _seeded(db) -> bool:
    return db.scalar(select(models.ReferenceCode).limit(1)) is not None


def _merge_specialty_defaults(stored: list[dict], defaults: list[dict]) -> list[dict]:
    """Merge newly-added specialty fields into an existing runtime config.

    Existing stored values win over defaults so admins keep their edits, but new
    default fields appear automatically on older databases.
    """
    by_name = {s["name"]: dict(s) for s in stored}
    return [{**d, **by_name.get(d["name"], {})} for d in defaults]


def _clear_all_seed_data(db) -> None:
    """Delete all seed-managed rows so seed_all(force=True) is fully idempotent.
    Bulk DELETE bypasses ORM cascade, so FK children must come before parents."""
    for cls in (
        # coding_run children first (FK → coding_runs)
        models.CodeResult,
        models.DrgResult,
        models.HccResult,
        models.AnesResult,
        models.ApcResult,
        # then coding_runs (FK → encounters)
        models.CodingRun,
        # then encounters and the rest of the seed tables
        models.Encounter,
        models.GoldenCase,
        models.ApcEntry,
        models.QualCircumstance,
        models.AnesBaseUnit,
        models.DemographicFactor,
        models.HccHierarchy,
        models.DxHccMap,
        models.HccCategory,
        models.OrProcedure,
        models.MdcAssignment,
        models.CcMcc,
        models.DrgDefinition,
        models.GuidelineChunk,
        models.OntologyEdge,
        models.OntologyConcept,
        models.PayerPolicy,
        models.MueLimit,
        models.NcciEdit,
        models.ModifierRule,
        models.ReferenceCode,
    ):
        db.query(cls).delete(synchronize_session=False)
    db.flush()


def seed_all(force: bool = False) -> dict:
    init_db()
    db = SessionLocal()
    try:
        config_store.seed_defaults(db)  # idempotent — ensures admin config exists
        if _seeded(db) and not force:
            return {"status": "already_seeded"}

        if force:
            _clear_all_seed_data(db)

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
        for code, desc, modality in rd.ICD10PCS:
            db.add(models.ReferenceCode(code_system="ICD10PCS", code=code, description=desc,
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

        # inpatient / MS-DRG reference data
        for drg, title, mdc, mdc_t, typ, base, sev, wt in rd.DRG_DEFS:
            db.add(models.DrgDefinition(drg=drg, title=title, mdc=mdc, mdc_title=mdc_t,
                                        drg_type=typ, base_key=base, severity=sev, weight=wt))
        for code, tier in rd.CC_MCC:
            db.add(models.CcMcc(code=code, tier=tier))
        for dx_prefix, mdc, mdc_t, base in rd.DX_MDC:
            db.add(models.MdcAssignment(dx_prefix=dx_prefix, mdc=mdc, mdc_title=mdc_t, medical_base_key=base))
        for pcs, base, mdc in rd.OR_PROC:
            db.add(models.OrProcedure(pcs_code=pcs, surgical_base_key=base, mdc=mdc))

        # HCC / Risk Adjustment reference data
        for hcc, label, coef in rd.HCC_CATEGORIES:
            db.add(models.HccCategory(hcc=hcc, label=label, coefficient=coef))
        for dx, hcc in rd.DX_HCC:
            db.add(models.DxHccMap(dx_code=dx, hcc=hcc))
        for sup, infr in rd.HCC_HIER:
            db.add(models.HccHierarchy(superior_hcc=sup, suppressed_hcc=infr))
        for sex, amin, amax, factor in rd.DEMO_FACTORS:
            db.add(models.DemographicFactor(sex=sex, age_min=amin, age_max=amax, factor=factor))

        # anesthesia unit calculation reference data
        for code, units in rd.ANES_BASE_UNITS:
            db.add(models.AnesBaseUnit(code=code, base_units=units))
        for code, units, desc in rd.QUAL_CIRC:
            db.add(models.QualCircumstance(code=code, units=units, description=desc))

        # facility / OPPS reference data (Addendum-B subset)
        for code, si, apc, title, rate in rd.APC_ADDENDUM_B:
            db.add(models.ApcEntry(code=code, status_indicator=si, apc=apc,
                                   apc_title=title, national_rate=rate))

        # golden set
        for g in charts.GOLDEN_CASES:
            db.add(models.GoldenCase(specialty=g["specialty"], chart_text=g["chart_text"],
                                     truth=g["truth"], irr=g["irr"], ambiguous=g["ambiguous"]))

        # encounters (work items) — stagger arrival times so SLA aging is realistic
        now = datetime.now(timezone.utc)
        for i, ch in enumerate(charts.CHARTS):
            ch = {**ch, "scenario": ch.get("scenario", "")[:80]}
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
        merged_specs = _merge_specialty_defaults(stored, config_store.DEFAULTS["specialties"])
        if merged_specs != stored:
            prev_names = {s["name"] for s in stored}
            new_count = sum(1 for s in merged_specs if s["name"] not in prev_names)
            config_store.set_key(db, "specialties", merged_specs)
            bump("specialties", max(new_count, 1))

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
        for code, desc, modality in rd.ICD10PCS:
            if ("ICD10PCS", code) not in ref:
                db.add(models.ReferenceCode(code_system="ICD10PCS", code=code, description=desc,
                                            modality=modality, source="CMS", **rd.EFF))
                ref.add(("ICD10PCS", code)); bump("reference_codes")

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
        pp_rows = {(p.payer, p.code): p for p in db.scalars(select(models.PayerPolicy)).all()}
        for payer, code, mn, auth, modpref, dx in rd.PAYER_POLICY:
            row = pp_rows.get((payer, code))
            if row is None:
                db.add(models.PayerPolicy(payer=payer, code=code, medical_necessity=mn,
                                          requires_auth=auth, modifier_pref=modpref, covered_dx=dx))
                pp_rows[(payer, code)] = True
                bump("payer_policy")
            else:
                changed = (
                    row.medical_necessity != mn
                    or row.requires_auth != auth
                    or row.modifier_pref != modpref
                    or list(row.covered_dx or []) != list(dx or [])
                )
                if changed:
                    row.medical_necessity = mn
                    row.requires_auth = auth
                    row.modifier_pref = modpref
                    row.covered_dx = dx
                    bump("payer_policy")

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

        # inpatient / MS-DRG — DRG defs by drg; cc/mcc by code; mdc by (dx_prefix,mdc); or-proc by pcs
        drgs = {d.drg for d in db.scalars(select(models.DrgDefinition)).all()}
        for drg, title, mdc, mdc_t, typ, base, sev, wt in rd.DRG_DEFS:
            if drg not in drgs:
                db.add(models.DrgDefinition(drg=drg, title=title, mdc=mdc, mdc_title=mdc_t,
                                            drg_type=typ, base_key=base, severity=sev, weight=wt))
                drgs.add(drg); bump("drg_definitions")
        ccm = {c.code for c in db.scalars(select(models.CcMcc)).all()}
        for code, tier in rd.CC_MCC:
            if code not in ccm:
                db.add(models.CcMcc(code=code, tier=tier)); ccm.add(code); bump("cc_mcc")
        mdcs = {(m.dx_prefix, m.mdc) for m in db.scalars(select(models.MdcAssignment)).all()}
        for dx_prefix, mdc, mdc_t, base in rd.DX_MDC:
            if (dx_prefix, mdc) not in mdcs:
                db.add(models.MdcAssignment(dx_prefix=dx_prefix, mdc=mdc, mdc_title=mdc_t, medical_base_key=base))
                mdcs.add((dx_prefix, mdc)); bump("mdc_assignments")
        orps = {o.pcs_code for o in db.scalars(select(models.OrProcedure)).all()}
        for pcs, base, mdc in rd.OR_PROC:
            if pcs not in orps:
                db.add(models.OrProcedure(pcs_code=pcs, surgical_base_key=base, mdc=mdc))
                orps.add(pcs); bump("or_procedures")

        # HCC / Risk Adjustment — categories by hcc; map by dx; hierarchy by pair; demo by band
        hccs = {h.hcc for h in db.scalars(select(models.HccCategory)).all()}
        for hcc, label, coef in rd.HCC_CATEGORIES:
            if hcc not in hccs:
                db.add(models.HccCategory(hcc=hcc, label=label, coefficient=coef))
                hccs.add(hcc); bump("hcc_categories")
        dxmap = {m.dx_code for m in db.scalars(select(models.DxHccMap)).all()}
        for dx, hcc in rd.DX_HCC:
            if dx not in dxmap:
                db.add(models.DxHccMap(dx_code=dx, hcc=hcc)); dxmap.add(dx); bump("dx_hcc_map")
        hier = {(h.superior_hcc, h.suppressed_hcc) for h in db.scalars(select(models.HccHierarchy)).all()}
        for sup, infr in rd.HCC_HIER:
            if (sup, infr) not in hier:
                db.add(models.HccHierarchy(superior_hcc=sup, suppressed_hcc=infr))
                hier.add((sup, infr)); bump("hcc_hierarchies")
        bands = {(d.sex, d.age_min, d.age_max) for d in db.scalars(select(models.DemographicFactor)).all()}
        for sex, amin, amax, factor in rd.DEMO_FACTORS:
            if (sex, amin, amax) not in bands:
                db.add(models.DemographicFactor(sex=sex, age_min=amin, age_max=amax, factor=factor))
                bands.add((sex, amin, amax)); bump("demographic_factors")

        # anesthesia units — base units by code; qualifying circumstances by code
        abu = {a.code for a in db.scalars(select(models.AnesBaseUnit)).all()}
        for code, units in rd.ANES_BASE_UNITS:
            if code not in abu:
                db.add(models.AnesBaseUnit(code=code, base_units=units))
                abu.add(code); bump("anes_base_units")
        qcs = {q.code for q in db.scalars(select(models.QualCircumstance)).all()}
        for code, units, desc in rd.QUAL_CIRC:
            if code not in qcs:
                db.add(models.QualCircumstance(code=code, units=units, description=desc))
                qcs.add(code); bump("qual_circumstances")

        # facility / OPPS — Addendum-B entries by code
        apcs = {a.code for a in db.scalars(select(models.ApcEntry)).all()}
        for code, si, apc, title, rate in rd.APC_ADDENDUM_B:
            if code not in apcs:
                db.add(models.ApcEntry(code=code, status_indicator=si, apc=apc,
                                       apc_title=title, national_rate=rate))
                apcs.add(code); bump("apc_entries")

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
                ch = {**ch, "scenario": ch.get("scenario", "")[:80]}
                enc = models.Encounter(**ch)
                enc.received_at = now - timedelta(minutes=(i % 6) * 9)
                db.add(enc)
                mrns.add(ch["mrn"]); bump("encounters")

        db.commit()
        return {"status": "ok", "added": added}
    finally:
        db.close()
