"""Stage 6 (anesthesia only) — the anesthesia unit calculator.

Anesthesia is NOT paid as CPT line-items. The payment formula is

    (base units + time units + modifying units) × anesthesia conversion factor

- base units    : per-code complexity from the public CMS base-unit file
- time units    : documented anesthesia start→stop, 15 minutes per unit (fractional)
- modifying     : physical-status P3-P5 adders (commercial convention — Medicare
                  pays 0 for P-modifiers; the trace says so honestly) and
                  qualifying-circumstance add-on codes (99100/99116/99135/99140)
- conversion factor: $/unit, admin-configurable (varies by locality and payer)

Everything is deterministic and auditable. The anesthesia time is extracted from
the documented "ANESTHESIA START/STOP" times in the record — never estimated by
the model. No documented time, or no base-unit row → unresolved → human review.
"""
from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models

# "Anesthesia start 08:12, stop 09:34" / "ANESTHESIA START: 07:42" / "anesthesia end 0855"
_T = r"(\d{1,2}):?(\d{2})"
_START_RE = re.compile(r"(?:ANESTHESIA\s+)?\bSTART\b[:\s]+" + _T, re.IGNORECASE)
_STOP_RE = re.compile(r"(?:ANESTHESIA\s+)?\b(?:STOP|END)\b[:\s]+" + _T, re.IGNORECASE)


def _minutes(m: re.Match) -> int:
    return int(m.group(1)) * 60 + int(m.group(2))


def calculate(db: Session, codes: list[dict], chart_text: str, cfg: dict) -> dict[str, Any]:
    """`codes` = accepted code dicts: {code_system, code, modifiers}.
    `cfg` = the admin "anesthesia" config (conversion_factor, phys_status_units).
    Returns the unit calculation + an ordered trace."""
    trace: list[dict] = []

    def note(step: str, detail: str) -> None:
        trace.append({"step": step, "detail": detail})

    result = {
        "resolved": False, "code": "", "base_units": 0, "time_minutes": 0,
        "time_units": 0.0, "phys_modifier": "", "phys_units": 0, "qual_circ": [],
        "total_units": 0.0, "conversion_factor": float(cfg.get("conversion_factor", 0.0)),
        "estimated_allowable": 0.0, "trace": trace, "reason": "",
    }

    # --- 1) The anesthesia procedure code (00100-01999) and its CMS base units ---
    anes = next((c for c in codes if c["code_system"] == "CPT"
                 and len(c["code"]) == 5 and c["code"][0] == "0"), None)
    if anes is None:
        result["reason"] = "no anesthesia procedure code (00100-01999) among accepted codes"
        note("base_units", "no anesthesia CPT found")
        return result
    result["code"] = anes["code"]
    row = db.scalars(
        select(models.AnesBaseUnit).where(models.AnesBaseUnit.code == anes["code"])
    ).first()
    if row is None:
        result["reason"] = f"no CMS base-unit entry for {anes['code']} in the curated subset"
        note("base_units", f"{anes['code']} → no base-unit row")
        return result
    result["base_units"] = row.base_units
    note("base_units", f"{anes['code']} → {row.base_units} base units (CMS base-unit file)")

    # --- 2) Time units from documented anesthesia start/stop (15-min units) ---
    m_start, m_stop = _START_RE.search(chart_text), _STOP_RE.search(chart_text)
    if not m_start or not m_stop:
        result["reason"] = "anesthesia start/stop time not documented"
        note("time_units", "no documented ANESTHESIA START/STOP — cannot compute time units")
        return result
    minutes = _minutes(m_stop) - _minutes(m_start)
    if minutes <= 0:
        minutes += 24 * 60  # crossed midnight
    time_units = round(minutes / 15.0, 2)
    result["time_minutes"] = minutes
    result["time_units"] = time_units
    note("time_units", f"documented {m_start.group(0)} → {m_stop.group(0)} = {minutes} min "
         f"÷ 15 = {time_units} time units")

    # --- 3) Modifying units: physical status + qualifying circumstances ---
    phys_units_map = {k: int(v) for k, v in (cfg.get("phys_status_units") or {}).items()}
    phys = next((m for m in (anes.get("modifiers") or []) if m in phys_units_map), "")
    p_units = phys_units_map.get(phys, 0)
    result["phys_modifier"] = phys
    result["phys_units"] = p_units
    if phys:
        note("modifying_units", f"physical status {phys} → +{p_units} unit(s) "
             "(commercial convention; Medicare pays 0 for P-modifiers)")
    else:
        note("modifying_units", "no physical-status modifier on the anesthesia code")

    qc_rows = {q.code: q for q in db.scalars(select(models.QualCircumstance)).all()}
    qc_units = 0
    for c in codes:
        q = qc_rows.get(c["code"])
        if q:
            qc_units += q.units
            result["qual_circ"].append({"code": q.code, "units": q.units, "description": q.description})
            note("modifying_units", f"qualifying circumstance {q.code} ({q.description}) → +{q.units} unit(s)")
    if not result["qual_circ"]:
        note("modifying_units", "no qualifying-circumstance add-on codes")

    # --- 4) Total units × conversion factor = estimated allowable ---
    total = round(row.base_units + time_units + p_units + qc_units, 2)
    cf = result["conversion_factor"]
    result["total_units"] = total
    result["estimated_allowable"] = round(total * cf, 2)
    result["resolved"] = True
    note("payment", f"({row.base_units} base + {time_units} time + {p_units + qc_units} modifying) "
         f"= {total} units × ${cf:.2f}/unit = ${result['estimated_allowable']:.2f} estimated allowable")
    return result
