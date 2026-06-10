"""Stage 6 (inpatient only) — the MS-DRG grouper.

A real, deterministic implementation of the Medicare Severity DRG grouping logic,
reading the public CMS artifacts (MDC assignment, OR-procedure list, the MS-DRG
table, CC/MCC lists) from the database:

    principal dx ──▶ MDC ──▶ surgical / medical partition ──▶ base DRG family
                                                            └▶ CC/MCC severity tier ──▶ final DRG + weight

It is deliberately rule-based (LLMs do not group reliably) and fully auditable:
every step is recorded in a trace. The data is a curated demo subset; the
algorithm is production-shaped — swap in the full CMS definitions or a certified
grouper (3M/Optum) behind this same interface. We never fabricate a DRG: if the
principal dx maps to no curated MDC, or the base family has no matching tier, the
result is unresolved and the chart routes to a human.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models

_SEV_RANK = {"MCC": 3, "CC": 2, "NONE": 1}


def _pick_pdx(dx: list[dict]) -> dict | None:
    """Principal diagnosis = the principal/primary-role dx with the lowest sequence;
    fall back to the first diagnosis (UHDDS: condition chiefly responsible for admission)."""
    if not dx:
        return None
    ranked = sorted(
        dx, key=lambda d: (0 if d.get("role") in ("principal", "primary") else 1, d.get("sequence", 0))
    )
    return ranked[0]


def group(db: Session, codes: list[dict]) -> dict[str, Any]:
    """`codes` = accepted code dicts: {code_system, code, role, sequence, description}.
    Returns the DRG assignment + an ordered trace."""
    trace: list[dict] = []

    def note(step: str, detail: str) -> None:
        trace.append({"step": step, "detail": detail})

    dx = [c for c in codes if c["code_system"] == "ICD10CM"]
    pcs = [c for c in codes if c["code_system"] == "ICD10PCS"]

    base_result = {
        "resolved": False, "drg": "", "title": "", "mdc": "", "mdc_title": "",
        "drg_type": "", "severity": "NONE", "weight": 0.0, "pdx": "",
        "or_procedure": "", "cc_mcc_drivers": [], "trace": trace, "reason": "",
    }

    pdx = _pick_pdx(dx)
    if pdx is None:
        base_result["reason"] = "no principal diagnosis to assign an MDC"
        note("principal_dx", "no ICD-10-CM diagnosis available")
        return base_result
    base_result["pdx"] = pdx["code"]
    note("principal_dx", f"{pdx['code']} — {pdx.get('description', '')}")

    # --- 1) MDC assignment from the principal dx (longest-prefix match) ---
    mdc_rows = db.scalars(select(models.MdcAssignment)).all()
    match = None
    for m in mdc_rows:
        if pdx["code"].startswith(m.dx_prefix):
            if match is None or len(m.dx_prefix) > len(match.dx_prefix):
                match = m
    if match is None:
        base_result["reason"] = f"principal dx {pdx['code']} maps to no curated MDC"
        note("mdc_assignment", f"{pdx['code']} → no MDC in the curated subset")
        return base_result
    base_result["mdc"] = match.mdc
    base_result["mdc_title"] = match.mdc_title
    note("mdc_assignment", f"{pdx['code']} → MDC {match.mdc} ({match.mdc_title})")

    # --- 2) Surgical vs medical partition (is there an OR procedure?) ---
    or_rows = {o.pcs_code: o for o in db.scalars(select(models.OrProcedure)).all()}
    or_hit = next((p for p in pcs if p["code"] in or_rows), None)
    if or_hit is not None:
        base_result["drg_type"] = "SURG"
        base_key = or_rows[or_hit["code"]].surgical_base_key
        base_result["or_procedure"] = or_hit["code"]
        note("partition", f"OR procedure {or_hit['code']} present → SURGICAL partition (base {base_key})")
    else:
        base_result["drg_type"] = "MED"
        base_key = match.medical_base_key
        if pcs:
            note("partition", f"{len(pcs)} procedure(s) present but none is an OR procedure → MEDICAL partition (base {base_key})")
        else:
            note("partition", f"no procedure → MEDICAL partition (base {base_key})")

    # --- 3) CC/MCC severity sweep of the secondary diagnoses ---
    cc_rows = {c.code: c.tier for c in db.scalars(select(models.CcMcc)).all()}
    drivers = []
    for d in dx:
        if d["code"] == pdx["code"]:
            continue
        tier = cc_rows.get(d["code"])
        if tier:
            drivers.append({"code": d["code"], "tier": tier, "description": d.get("description", "")})
    severity = "NONE"
    if any(x["tier"] == "MCC" for x in drivers):
        severity = "MCC"
    elif any(x["tier"] == "CC" for x in drivers):
        severity = "CC"
    base_result["severity"] = severity
    base_result["cc_mcc_drivers"] = drivers
    if drivers:
        note("severity", "severity " + severity + " from " +
             ", ".join(f"{x['code']} ({x['tier']})" for x in drivers))
    else:
        note("severity", "no CC/MCC secondary diagnoses → without CC/MCC")

    # --- 4) Final DRG = base family + severity tier ---
    fam = db.scalars(
        select(models.DrgDefinition).where(models.DrgDefinition.base_key == base_key)
    ).all()
    if not fam:
        base_result["reason"] = f"no DRG family for base key {base_key}"
        note("drg_assignment", f"base {base_key} has no DRG definitions")
        return base_result
    chosen = next((d for d in fam if d.severity == severity), None)
    if chosen is None:
        # degrade to the next-lower available tier (real groupers collapse absent tiers)
        for sev in sorted({d.severity for d in fam}, key=lambda s: _SEV_RANK.get(s, 0), reverse=True):
            if _SEV_RANK.get(sev, 0) <= _SEV_RANK.get(severity, 0):
                chosen = next(d for d in fam if d.severity == sev)
                note("drg_assignment", f"no exact '{severity}' tier; collapsed to '{sev}'")
                break
    if chosen is None:
        base_result["reason"] = f"base {base_key} has no tier ≤ {severity}"
        return base_result

    base_result.update({
        "resolved": True, "drg": chosen.drg, "title": chosen.title,
        "drg_type": chosen.drg_type, "weight": chosen.weight,
    })
    note("drg_assignment", f"DRG {chosen.drg} — {chosen.title} (relative weight {chosen.weight:.4f})")
    return base_result
