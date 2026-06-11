"""Stage-1 patient history — longitudinal checks across the same patient's encounters.

Activated only when an encounter carries a `patient_key` (the EMPI/master-patient-index
identity in production; empty for standalone encounters, so legacy charts are untouched).

Three things this enables:
1. DETERMINISTIC copy-forward: a verbatim run of words shared between the current
   document and a prior encounter's document (difflib longest-common-subsequence on
   word tokens — plain string math, never model judgment). Stronger than the model's
   text-pattern flag, which remains as the backup signal.
2. Prior context for the analysis model, so current-vs-prior contradictions become
   detectable (the prompt explicitly forbids coding from priors).
3. HCC recapture: prior-year HCCs not re-documented this year (computed in the
   orchestrator's HCC stage using the priors fetched here).
"""
from __future__ import annotations

import difflib
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models

# Shorter runs are boilerplate (headers, signature lines); 15+ contiguous words shared
# verbatim with a prior note is carried-forward clinical text.
MIN_VERBATIM_WORDS = 15


def prior_encounters(db: Session, enc: models.Encounter, limit: int = 3) -> list[models.Encounter]:
    if not (enc.patient_key or "").strip():
        return []
    return db.scalars(
        select(models.Encounter).where(
            models.Encounter.patient_key == enc.patient_key,
            models.Encounter.id != enc.id,
            models.Encounter.dos < enc.dos,
        ).order_by(models.Encounter.dos.desc()).limit(limit)
    ).all()


def _words(text: str) -> list[str]:
    return re.findall(r"\S+", (text or "").lower())


def copy_forward_findings(current_text: str, priors: list[models.Encounter]) -> list[dict]:
    """Longest verbatim word-run shared with each prior document. Deterministic."""
    cw = _words(current_text)
    findings: list[dict] = []
    for p in priors:
        pw = _words(p.chart_text)
        if not cw or not pw:
            continue
        m = difflib.SequenceMatcher(None, cw, pw, autojunk=False).find_longest_match(
            0, len(cw), 0, len(pw))
        if m.size >= MIN_VERBATIM_WORDS:
            snippet = " ".join(cw[m.a:m.a + min(m.size, 18)])
            findings.append({
                "prior_mrn": p.mrn, "prior_dos": p.dos, "verbatim_words": m.size,
                "snippet": snippet + ("…" if m.size > 18 else ""),
            })
    return findings


def prior_context(db: Session, priors: list[models.Encounter]) -> str:
    """Compact prior-encounter block for the analysis prompt (capped per encounter)."""
    if not priors:
        return ""
    parts = []
    for p in priors:
        run = db.scalars(
            select(models.CodingRun).where(models.CodingRun.encounter_id == p.id)
            .order_by(models.CodingRun.started_at.desc()).limit(1)
        ).first()
        gist = (run.chart_summary if run and run.chart_summary else p.chart_text)[:400]
        parts.append(f"- {p.dos} · {p.specialty} · {p.mrn}: {gist}")
    return (
        "PRIOR ENCOUNTERS (same patient — use ONLY for copy-forward, contradiction and "
        "temporal checks; do NOT code from priors):\n" + "\n".join(parts)
    )


def prior_hccs(db: Session, priors: list[models.Encounter]) -> dict[str, dict]:
    """Union of HCCs captured on prior encounters: {hcc: {label, coefficient}}.
    Reads prior HccResults; falls back to mapping prior accepted ICD codes."""
    out: dict[str, dict] = {}
    if not priors:
        return out
    dx_map = {m.dx_code: m.hcc for m in db.scalars(select(models.DxHccMap)).all()}
    cats = {c.hcc: c for c in db.scalars(select(models.HccCategory)).all()}
    for p in priors:
        run = db.scalars(
            select(models.CodingRun).where(models.CodingRun.encounter_id == p.id)
            .order_by(models.CodingRun.started_at.desc()).limit(1)
        ).first()
        if run is None:
            continue
        if run.hcc_result:
            for h in run.hcc_result.hccs or []:
                if h.get("hcc") in cats and h["hcc"] not in out:
                    c = cats[h["hcc"]]
                    out[h["hcc"]] = {"label": c.label, "coefficient": c.coefficient}
        else:  # prior coded but without an HCC stage — map its accepted dx codes
            for cr in run.codes:
                if cr.code_system == "ICD10CM" and cr.status == "accepted":
                    hcc = dx_map.get(cr.code)
                    if hcc and hcc in cats and hcc not in out:
                        c = cats[hcc]
                        out[hcc] = {"label": c.label, "coefficient": c.coefficient}
    return out
