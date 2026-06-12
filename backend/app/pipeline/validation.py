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

        # 8) POS alignment — table-driven place-of-service validity (CMS POS /
        # inpatient-only style). Rows exist only where a restriction applies.
        pos_rule = db.scalars(select(models.PosRule).where(models.PosRule.code == cval)).first()
        if pos_rule is None:
            add("pos_alignment", True, f"POS {encounter.pos} — no restriction on file (curated subset)")
        elif encounter.pos in (pos_rule.allowed_pos or []):
            add("pos_alignment", True, f"POS {encounter.pos} allowed for {cval}")
        else:
            add("pos_alignment", False,
                f"{cval} not valid at POS {encounter.pos} (allowed: {', '.join(pos_rule.allowed_pos)}) — "
                f"{pos_rule.rationale}")

        # 8b) Modifier pairing — per-CPT restrictions (MPFS PC/TC-indicator style)
        # plus the generic contradiction: 50 (bilateral) with RT/LT (unilateral).
        mods_on_code = list(code.get("modifiers", []))
        pair_fails = []
        if mods_on_code:
            bad_pairs = db.scalars(
                select(models.ModifierPairRule).where(
                    models.ModifierPairRule.code == cval,
                    models.ModifierPairRule.modifier.in_(mods_on_code),
                )
            ).all()
            pair_fails += [f"{cval}-{r.modifier}: {r.rationale}" for r in bad_pairs]
            if "50" in mods_on_code and ({"RT", "LT"} & set(mods_on_code)):
                pair_fails.append("50 with RT/LT is contradictory (bilateral vs unilateral)")
        if pair_fails:
            add("modifier_pairing", False, "; ".join(pair_fails))
        else:
            add("modifier_pairing", True, "no invalid modifier pairings")

        # 9) Professional/technical component — facility radiology (7xxxx) and surgical pathology
        # (88xxx) interpretations need modifier 26 (or TC)
        if (cval[:1] == "7" or cval[:2] == "88") and encounter.pos in ("22", "23", "19", "21"):
            mods = code.get("modifiers", [])
            if "26" in mods or "TC" in mods:
                add("component_modifier", True, "professional/technical component identified")
            else:
                add("component_modifier", False,
                    f"facility radiology read (POS {encounter.pos}) requires modifier 26 (professional component)")

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
