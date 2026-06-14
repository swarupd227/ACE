"""Phase 2 — Denial Pattern Discovery.

Statistics-first mining over canonical 835 remittance data (no LLM in the detection step —
the numbers must be defensible). For each (payer, procedure, CARC) it compares the recent
window against the baseline window with a two-proportion z-test (a changepoint signal),
classifies the pattern (SPIKE / PERSISTENT / EMERGING), scores and ranks it, attaches an
evidence bundle, and proposes a candidate rule. Promoting a signal hands the candidate to the
same P3 Validator Judge that policy provisions use — so denial-derived and policy-derived
rules converge in one review queue.
"""
from __future__ import annotations

import math
from collections import defaultdict

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from core import llm_client

from . import audit, models, sample_835, validate

RECENT_WINDOW = sample_835.RECENT_WINDOW

# CARC → the kind of rule a denial pattern implies.
_CARC_RULE = {
    "197": ("PRIOR_AUTH", "Require prior authorization for {code} ({payer})"),
    "16": ("DOCUMENTATION", "Enforce documentation completeness for {code} ({payer})"),
    "11": ("COVERAGE", "Tighten medical-necessity / diagnosis pairing for {code} ({payer})"),
    "50": ("COVERAGE", "Add medical-necessity criteria for {code} ({payer})"),
    "151": ("FREQUENCY", "Add a frequency limit for {code} ({payer})"),
}


def load_sample(db: Session) -> int:
    """Seed synthetic 835 lines if the table is empty. Returns total row count."""
    existing = db.scalar(select(models.RemittanceLine.id).limit(1))
    if existing is None:
        for r in sample_835.generate():
            db.add(models.RemittanceLine(**r))
        db.commit()
    return db.scalar(select(func.count(models.RemittanceLine.id))) or 0


def _two_proportion_z(d1: int, n1: int, d2: int, n2: int) -> float:
    if n1 == 0 or n2 == 0:
        return 0.0
    p1, p2 = d1 / n1, d2 / n2
    p = (d1 + d2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return 0.0
    return (p1 - p2) / se


def _classify(recent_rate: float, baseline_rate: float, lift: float, z: float) -> str:
    if z >= 3.0 and lift >= 1.5:
        return "SPIKE"
    if baseline_rate >= 0.20 and recent_rate >= 0.20:
        return "PERSISTENT"
    if lift >= 1.5 and recent_rate >= 0.10:
        return "EMERGING"
    return ""


def detect_signals(db: Session, actor: str = "system") -> dict:
    """Re-derive denial signals from the remittance rows. Replaces prior NEW signals."""
    rows = db.scalars(select(models.RemittanceLine)).all()
    if not rows:
        raise ValueError("no remittance data — load the 835 sample first")

    cutoff = max(r.service_date for r in rows)  # most recent service date (ISO sortable)
    from datetime import date as _date, timedelta
    cutoff_d = _date.fromisoformat(cutoff)
    recent_start = (cutoff_d - timedelta(days=RECENT_WINDOW - 1)).isoformat()

    # Totals per (payer, code) and denials per (payer, code, carc), split by window.
    tot_recent: dict = defaultdict(int)
    tot_base: dict = defaultdict(int)
    den_recent: dict = defaultdict(int)
    den_base: dict = defaultdict(int)
    samples: dict = defaultdict(list)
    for r in rows:
        recent = r.service_date >= recent_start
        key = (r.payer, r.procedure_code)
        (tot_recent if recent else tot_base)[key] += 1
        if r.denied:
            ck = (r.payer, r.procedure_code, r.denial_carc)
            (den_recent if recent else den_base)[ck] += 1
            if recent and len(samples[ck]) < 5:
                samples[ck].append({
                    "claim_id": r.claim_id, "service_date": r.service_date,
                    "carc": r.denial_carc, "reason": r.denial_reason,
                    "billed": r.billed_amount,
                })

    db.execute(delete(models.DenialSignal).where(models.DenialSignal.status == "NEW"))

    candidates = []
    for (payer, code, carc), dr in den_recent.items():
        nr = tot_recent[(payer, code)]
        nb = tot_base[(payer, code)]
        dbn = den_base[(payer, code, carc)]
        recent_rate = dr / nr if nr else 0.0
        baseline_rate = dbn / nb if nb else 0.0
        lift = recent_rate / baseline_rate if baseline_rate > 0 else (recent_rate / 0.01)
        z = _two_proportion_z(dr, nr, dbn, nb)
        pattern = _classify(recent_rate, baseline_rate, lift, z)
        if not pattern or dr < 5:
            continue
        score = round(dr * recent_rate * min(max(lift, 1.0), 10.0) * (1 + max(z, 0) / 10), 2)
        candidates.append({
            "payer": payer, "code": code, "carc": carc, "pattern": pattern,
            "dr": dr, "nr": nr, "recent_rate": round(recent_rate, 3),
            "baseline_rate": round(baseline_rate, 3), "lift": round(lift, 2),
            "z": round(z, 2), "score": score, "samples": samples[(payer, code, carc)],
        })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    created = []
    for rank, c in enumerate(candidates, start=1):
        prov_type, tmpl = _CARC_RULE.get(c["carc"], ("COVERAGE", "Add a rule for {code} ({payer})"))
        summary = (f"{tmpl.format(code=c['code'], payer=c['payer'])} — {c['dr']} denials "
                   f"({int(c['recent_rate']*100)}%) in the last {RECENT_WINDOW} days with CARC "
                   f"{c['carc']} ({sample_835.CARC_REASON.get(c['carc'], '')}), "
                   f"{c['lift']}x baseline.")
        sig = models.DenialSignal(
            payer=c["payer"], procedure_code=c["code"], denial_carc=c["carc"],
            pattern_type=c["pattern"], recent_denials=c["dr"], recent_total=c["nr"],
            recent_rate=c["recent_rate"], baseline_rate=c["baseline_rate"], lift=c["lift"],
            z_score=c["z"], score=c["score"], rank=rank, status="NEW",
            evidence={"aggregates": {k: c[k] for k in ("dr", "nr", "recent_rate", "baseline_rate", "lift", "z")},
                      "sample_lines": c["samples"]},
            proposed_rule={"provision_type": prov_type, "summary": summary,
                           "code_sets": {"cpt": [c["code"]], "icd": [], "hcpcs": [],
                                         "modifiers": [], "pos": []}},
        )
        db.add(sig)
        created.append(sig)
    db.commit()
    for s in created:
        db.refresh(s)
    audit.log(db, phase="P2", action="DETECT", actor=actor,
              entity_type="denial_run", entity_id="",
              summary=f"{len(created)} signals from {len(rows)} remittance lines "
                      f"(top: {', '.join(c['code']+'/'+c['carc'] for c in candidates[:3])})",
              lineage={"signals": len(created), "remittance_lines": len(rows)})
    return {"signals": len(created), "remittance_lines": len(rows),
            "recent_window_days": RECENT_WINDOW, "results": [signal_dict(s) for s in created]}


def promote_signal(db: Session, signal_id: str, actor: str = "system", llm: dict | None = None) -> dict:
    """Hand a denial signal's proposed rule to the P3 Validator Judge → review queue."""
    sig = db.get(models.DenialSignal, signal_id)
    if sig is None:
        raise ValueError("signal not found")
    if sig.status == "PROMOTED" and sig.promoted_recommendation_id:
        raise ValueError("signal already promoted")
    pr = sig.proposed_rule or {}
    ev = sig.evidence.get("aggregates", {})
    evidence_text = (
        f"Denial-pattern evidence ({sig.pattern_type}) for {sig.procedure_code} / {sig.payer}: "
        f"{ev.get('dr')} of {ev.get('nr')} claims ({int((ev.get('recent_rate') or 0)*100)}%) "
        f"denied with CARC {sig.denial_carc} ({sample_835.CARC_REASON.get(sig.denial_carc,'')}) "
        f"in the last {RECENT_WINDOW} days, vs baseline {int((ev.get('baseline_rate') or 0)*100)}% "
        f"(lift {ev.get('lift')}x, z={ev.get('z')})."
    )
    rec = validate.judge_candidate(
        db, payer=sig.payer, provision_type=pr.get("provision_type", "COVERAGE"),
        summary=pr.get("summary", ""), code_sets=pr.get("code_sets", {}),
        evidence_text=evidence_text, evidence_ref={"signal_id": sig.id},
        origin="DENIAL", source_signal_id=sig.id, actor=actor, llm=llm,
    )
    sig.status = "PROMOTED"
    sig.promoted_recommendation_id = rec.id
    sig.model_version = llm_client.model_version(llm)
    db.add(sig)
    db.commit()
    audit.log(db, phase="P2", action="PROMOTE", actor=actor, entity_type="recommendation", entity_id=rec.id,
              payer=sig.payer,
              summary=f"denial signal {sig.procedure_code}/CARC{sig.denial_carc} "
                      f"({sig.pattern_type}) promoted to review",
              lineage={"signal_id": sig.id, "pattern_type": sig.pattern_type})
    return {"signal_id": sig.id, "recommendation_id": rec.id,
            "recommendation": validate.rec_dict(rec)}


def signal_dict(s: models.DenialSignal) -> dict:
    return {
        "id": s.id, "payer": s.payer, "procedure_code": s.procedure_code,
        "denial_carc": s.denial_carc, "pattern_type": s.pattern_type,
        "recent_denials": s.recent_denials, "recent_total": s.recent_total,
        "recent_rate": s.recent_rate, "baseline_rate": s.baseline_rate, "lift": s.lift,
        "z_score": s.z_score, "score": s.score, "rank": s.rank, "status": s.status,
        "evidence": s.evidence, "proposed_rule": s.proposed_rule,
        "promoted_recommendation_id": s.promoted_recommendation_id,
    }
