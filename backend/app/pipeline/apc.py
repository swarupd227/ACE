"""Stage 6 (hospital outpatient only) — the facility-side OPPS / APC pricer.

The SAME coded chart drives two claims. The professional fee (physician work —
the modifier-26 codes ACE already assigns) is priced under the physician fee
schedule. The FACILITY fee is priced under the Outpatient Prospective Payment
System: every HCPCS/CPT carries a status indicator from CMS Addendum B (a
public quarterly artifact) that drives the payment logic implemented here:

    J1  comprehensive APC — one payment for the session; everything else packaged
    T   separately payable surgical — multiple-procedure discount (100% / 50%)
    S   significant procedure — always 100%
    V   clinic / ED visit — 100%
    N   unconditionally packaged — no separate payment
    Q1  conditionally packaged — packaged when an S/T/V/J1 service is on the
        claim, otherwise paid

Runs only for hospital outpatient places of service (POS 22 / 23). ASC (POS 24)
is a different fee schedule and is honestly out of scope. Unlike the DRG / RAF /
anesthesia stages, an incomplete facility estimate does NOT change routing: the
clinical coding (the pro-fee claim) is the deliverable being routed — the
facility view is a parallel payment lens, and gaps are traced, not punished.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


def price(db: Session, codes: list[dict]) -> dict[str, Any]:
    """`codes` = accepted procedure code dicts: {code_system, code}.
    Returns facility payment lines + packaging decisions + an ordered trace."""
    trace: list[dict] = []

    def note(step: str, detail: str) -> None:
        trace.append({"step": step, "detail": detail})

    result = {
        "resolved": False, "lines": [], "packaged": [], "not_covered": [],
        "facility_total": 0.0, "trace": trace,
    }

    procs = [c for c in codes if c["code_system"] in ("CPT", "HCPCS")]
    if not procs:
        note("status_lookup", "no procedure codes — no facility claim lines")
        return result

    entries = {e.code: e for e in db.scalars(select(models.ApcEntry)).all()}
    looked: list[tuple[dict, models.ApcEntry]] = []
    for c in procs:
        e = entries.get(c["code"])
        if e is None:
            result["not_covered"].append(c["code"])
            note("status_lookup", f"{c['code']} → not in the curated Addendum-B subset")
        else:
            looked.append((c, e))
            note("status_lookup", f"{c['code']} → SI {e.status_indicator}"
                 + (f", APC {e.apc} ({e.apc_title}) ${e.national_rate:.2f}" if e.apc else " (packaged)"))

    sis = {e.status_indicator for _, e in looked}
    has_primary = bool(sis & {"S", "T", "V", "J1"})

    def add_line(e: models.ApcEntry, pct: int) -> None:
        allowed = round(e.national_rate * pct / 100.0, 2)
        result["lines"].append({
            "code": e.code, "si": e.status_indicator, "apc": e.apc,
            "apc_title": e.apc_title, "rate": e.national_rate, "pct": pct, "allowed": allowed,
        })

    def package(e: models.ApcEntry, why: str) -> None:
        result["packaged"].append({"code": e.code, "si": e.status_indicator, "note": why})
        note("packaging", f"{e.code} packaged — {why}")

    # --- Comprehensive APC: the highest-rated J1 absorbs the entire session ---
    j1s = sorted((e for _, e in looked if e.status_indicator == "J1"),
                 key=lambda e: e.national_rate, reverse=True)
    if j1s:
        primary = j1s[0]
        add_line(primary, 100)
        note("c_apc", f"comprehensive APC: {primary.code} (APC {primary.apc}, "
             f"${primary.national_rate:.2f}) pays the session; all other services packaged "
             "(complexity adjustments out of demo scope)")
        for _, e in looked:
            if e is not primary:
                package(e, f"packaged into comprehensive APC {primary.apc} ({primary.code})")
    else:
        # --- T: multiple-procedure discounting — highest 100%, the rest 50% ---
        ts = sorted((e for _, e in looked if e.status_indicator == "T"),
                    key=lambda e: e.national_rate, reverse=True)
        for i, e in enumerate(ts):
            pct = 100 if i == 0 else 50
            add_line(e, pct)
            if pct == 50:
                note("discounting", f"{e.code} discounted to 50% (multiple surgical procedures)")
        # --- S / V: always paid in full ---
        for _, e in looked:
            if e.status_indicator in ("S", "V"):
                add_line(e, 100)
        # --- Q1: conditionally packaged ---
        for _, e in looked:
            if e.status_indicator == "Q1":
                if has_primary:
                    package(e, "conditionally packaged (S/T/V service on the claim)")
                else:
                    add_line(e, 100)
                    note("packaging", f"{e.code} Q1 paid separately — no S/T/V/J1 on the claim")
        # --- N: always packaged ---
        for _, e in looked:
            if e.status_indicator == "N":
                package(e, "unconditionally packaged (SI N)")

    result["facility_total"] = round(sum(l["allowed"] for l in result["lines"]), 2)
    result["resolved"] = not result["not_covered"]
    note("facility_total",
         f"facility estimated allowable = ${result['facility_total']:.2f} "
         f"({len(result['lines'])} payable line(s), {len(result['packaged'])} packaged)"
         + (f"; {len(result['not_covered'])} code(s) outside the curated subset" if result["not_covered"] else ""))
    return result
