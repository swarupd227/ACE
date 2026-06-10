"""Stage 6 (risk-adjustment only) — the CMS-HCC RAF scorer.

A real, deterministic implementation of CMS-HCC risk-adjustment scoring, reading
the public CMS model artifacts (dx→HCC mappings, hierarchies, coefficients,
demographic factors) from the database:

    accepted dx ──▶ HCC condition categories ──▶ hierarchy resolution ──▶ Σ coefficients
    age/sex     ──▶ demographic base factor   ──────────────────────────▶ RAF score

Deliberately rule-based (the model never invents an HCC) and fully auditable:
every step lands in a trace, including the diagnoses that do NOT risk-adjust and
the categories suppressed by a hierarchy — the two things an HCC auditor asks
about first. Curated CMS-HCC V24 subset for the demo; production swaps in the
full annual CMS model file behind this same interface. If the patient falls
outside the curated demographic segment, the result is unresolved and the chart
routes to a human — we never guess a RAF.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


def score(db: Session, codes: list[dict], age: int, sex: str) -> dict[str, Any]:
    """`codes` = accepted code dicts: {code_system, code, description}.
    Returns the RAF assignment + an ordered trace."""
    trace: list[dict] = []

    def note(step: str, detail: str) -> None:
        trace.append({"step": step, "detail": detail})

    result = {
        "resolved": False, "raf": 0.0, "demographic": {}, "hccs": [],
        "suppressed": [], "unmapped": [], "trace": trace, "reason": "",
    }

    # --- 1) Demographic base factor ---
    band = db.scalars(
        select(models.DemographicFactor).where(
            models.DemographicFactor.sex == sex,
            models.DemographicFactor.age_min <= age,
            models.DemographicFactor.age_max >= age,
        )
    ).first()
    if band is None:
        result["reason"] = f"no demographic factor for {sex} age {age} in the curated segment"
        note("demographic", f"{sex} {age} → outside the curated community/aged segment")
        return result
    result["demographic"] = {
        "band": f"{band.sex} {band.age_min}-{band.age_max}",
        "factor": band.factor, "segment": band.segment,
    }
    note("demographic", f"{sex} {age} → band {band.sex} {band.age_min}-{band.age_max} "
         f"({band.segment}) factor {band.factor:.3f}")

    # --- 2) Map diagnoses to HCC condition categories ---
    dx = [c for c in codes if c["code_system"] == "ICD10CM"]
    dx_map = {m.dx_code: m.hcc for m in db.scalars(select(models.DxHccMap)).all()}
    cats = {c.hcc: c for c in db.scalars(select(models.HccCategory)).all()}
    mapped: dict[str, list[str]] = {}  # hcc -> [dx codes]
    for d in dx:
        hcc = dx_map.get(d["code"])
        if hcc and hcc in cats:
            mapped.setdefault(hcc, []).append(d["code"])
            note("dx_mapping", f"{d['code']} → HCC {hcc} ({cats[hcc].label})")
        else:
            result["unmapped"].append(d["code"])
            note("dx_mapping", f"{d['code']} → no HCC (does not risk-adjust)")

    # --- 3) Hierarchy resolution: a superior HCC suppresses its inferiors ---
    hier = db.scalars(select(models.HccHierarchy)).all()
    active = set(mapped)
    for h in hier:
        if h.superior_hcc in active and h.suppressed_hcc in active:
            active.discard(h.suppressed_hcc)
            result["suppressed"].append({"hcc": h.suppressed_hcc, "by": h.superior_hcc})
            note("hierarchy", f"HCC {h.suppressed_hcc} suppressed by HCC {h.superior_hcc} "
                 f"(only the most severe in a family pays)")
    if not result["suppressed"]:
        note("hierarchy", "no hierarchy conflicts among mapped categories")

    # --- 4) RAF = demographic factor + Σ active HCC coefficients ---
    raf = band.factor
    for hcc in sorted(active, key=lambda h: cats[h].coefficient, reverse=True):
        c = cats[hcc]
        raf += c.coefficient
        result["hccs"].append({
            "hcc": hcc, "label": c.label, "coefficient": c.coefficient,
            "dx": mapped[hcc],
        })
    result["raf"] = round(raf, 3)
    result["resolved"] = True
    note("raf", f"RAF = {band.factor:.3f} (demographic) + "
         + " + ".join(f"{cats[h].coefficient:.3f} (HCC {h})" for h in sorted(active, key=lambda h: cats[h].coefficient, reverse=True))
         + f" = {result['raf']:.3f}" if active else f"RAF = {band.factor:.3f} (demographic only — no HCCs captured)")
    return result
