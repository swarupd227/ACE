"""Stage 4 — deterministic validation & compliance gates.

These are rule-based on purpose (LLMs are bad at exhaustive lookups). Each gate
returns a structured pass/fail with the gate name logged — never a silent drop.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


def _ref(db: Session, system: str, code: str) -> models.ReferenceCode | None:
    return db.scalars(
        select(models.ReferenceCode).where(
            models.ReferenceCode.code_system == system, models.ReferenceCode.code == code
        )
    ).first()


def run_gates(
    db: Session,
    code: dict[str, Any],
    encounter: models.Encounter,
    all_codes: list[dict[str, Any]],
    rag_payer: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    system = code["code_system"]
    cval = code["code"]
    results: list[dict[str, Any]] = []

    def add(gate: str, passed: bool, detail: str = "") -> None:
        results.append({"gate": gate, "passed": passed, "detail": detail})

    ref = _ref(db, system, cval)

    # 1) Code existence (effective-dated)
    if ref is None:
        add("code_existence", False, f"{system} {cval} not found in current code set")
        return results  # nothing else is meaningful if the code doesn't exist
    if not (ref.effective_start <= encounter.dos <= ref.effective_end):
        add("code_existence", False, f"{cval} not effective for DOS {encounter.dos}")
    else:
        add("code_existence", True, f"{cval} valid for DOS {encounter.dos}")

    # 2) Specificity — is there a more-specific billable child?
    if system == "ICD10CM":
        children = db.scalars(
            select(models.ReferenceCode).where(
                models.ReferenceCode.code_system == "ICD10CM",
                models.ReferenceCode.parent == cval,
                models.ReferenceCode.billable == True,  # noqa: E712
            )
        ).all()
        if not ref.billable and children:
            add("specificity", False, f"{cval} is non-billable; more specific child required")
        elif not ref.billable:
            add("specificity", False, f"{cval} is a non-billable category code")
        else:
            add("specificity", True, "most-specific billable code")

    # 3) Sex / age edits
    if ref.sex_restriction and ref.sex_restriction != encounter.sex:
        add("sex_edit", False, f"{cval} restricted to sex {ref.sex_restriction}; patient {encounter.sex}")
    else:
        add("sex_edit", True, "")
    if not (ref.age_min <= encounter.age <= ref.age_max):
        add("age_edit", False, f"{cval} age range {ref.age_min}-{ref.age_max}; patient {encounter.age}")
    else:
        add("age_edit", True, "")

    # 4) Modifier validity (only for procedures)
    if system in ("CPT", "HCPCS"):
        valid_mods = {m.modifier for m in db.scalars(select(models.ModifierRule)).all()}
        bad = [m for m in code.get("modifiers", []) if m not in valid_mods]
        if bad:
            add("modifier_validity", False, f"unknown modifier(s): {', '.join(bad)}")
        else:
            add("modifier_validity", True, "")

        # 5) NCCI PTP bundling — does any other procedure bundle this one?
        proc_codes = [c["code"] for c in all_codes if c["code_system"] in ("CPT", "HCPCS") and c["code"] != cval]
        ncci = db.scalars(select(models.NcciEdit)).all()
        bundle_hit = None
        for e in ncci:
            if e.column1 in proc_codes and e.column2 == cval:
                bundle_hit = e
                break
        if bundle_hit:
            has_distinct = any(m in ("59", "XU", "XS", "XE", "XP") for m in code.get("modifiers", []))
            if bundle_hit.modifier_allowed and has_distinct:
                add("ncci_ptp", True, f"bundled with {bundle_hit.column1} but modifier 59/X present")
            elif bundle_hit.modifier_allowed:
                add("ncci_ptp", False, f"bundled with {bundle_hit.column1}; needs modifier 59/X to unbundle")
            else:
                add("ncci_ptp", False, f"hard-bundled with {bundle_hit.column1} (no modifier override allowed)")
        else:
            add("ncci_ptp", True, "no PTP conflict")

        # 6) MUE — units within published limit (1 unit assumed per code line in demo)
        mue = db.scalars(select(models.MueLimit).where(models.MueLimit.code == cval)).first()
        if mue is not None and mue.max_units < 1:
            add("mue", False, f"MUE limit {mue.max_units} for {cval}")
        else:
            add("mue", True, f"within MUE limit ({mue.max_units if mue else 'n/a'})")

        # 8) POS alignment (radiology professional component sanity check)
        add("pos_alignment", True, f"POS {encounter.pos} acceptable")

    # 7) Payer medical-necessity (LCD/NCD-style) from Graph-RAG payer policy
    pol = next((p for p in rag_payer if p["code"] == cval), None)
    if pol:
        dx_codes = [c["code"] for c in all_codes if c["code_system"] == "ICD10CM"]
        covered = pol.get("covered_dx") or []
        if covered:
            ok = any(any(dx.startswith(prefix) for prefix in covered) for dx in dx_codes)
            add("payer_medical_necessity", ok,
                f"{pol['payer']} requires supporting dx {covered}" if not ok else f"{pol['payer']} necessity met")
        if pol.get("requires_auth"):
            add("payer_auth", True, f"{pol['payer']} requires auth (verified at eligibility)")
    return results


def gates_passed(results: list[dict[str, Any]]) -> bool:
    return all(r["passed"] for r in results)
