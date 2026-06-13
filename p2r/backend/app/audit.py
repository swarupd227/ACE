"""Append-only decision log + lineage reconstruction (the governance plane).

Every material action across P1-P4 writes one immutable DecisionLogEntry. There is no update
or delete path. lineage_for() reconstructs the full chain behind a recommendation: the rule,
its validation/reconciliation verdicts, the source it came from (policy document+provision or
denial signal+evidence), the model version, and the ordered decision trail.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


def log(db: Session, *, phase: str, action: str, actor: str = "system",
        entity_type: str = "", entity_id: str = "", payer: str = "",
        summary: str = "", lineage: dict | None = None) -> None:
    db.add(models.DecisionLogEntry(
        phase=phase, action=action, actor=actor, entity_type=entity_type,
        entity_id=entity_id, payer=payer, summary=summary, lineage=lineage or {}))
    db.commit()


def entry_dict(e: models.DecisionLogEntry) -> dict:
    return {"id": e.id, "phase": e.phase, "action": e.action, "actor": e.actor,
            "entity_type": e.entity_type, "entity_id": e.entity_id, "payer": e.payer,
            "summary": e.summary, "lineage": e.lineage,
            "created_at": e.created_at.isoformat() if e.created_at else None}


def entries(db: Session, *, phase: str = "", entity_id: str = "") -> list[dict]:
    q = select(models.DecisionLogEntry).order_by(models.DecisionLogEntry.created_at.desc())
    if phase:
        q = q.where(models.DecisionLogEntry.phase == phase)
    if entity_id:
        q = q.where(models.DecisionLogEntry.entity_id == entity_id)
    return [entry_dict(e) for e in db.scalars(q).all()]


def lineage_for(db: Session, rec_id: str) -> dict:
    """Full lineage from a recommendation back to its origin, plus the decision trail."""
    rec = db.get(models.RuleRecommendation, rec_id)
    if rec is None:
        raise ValueError("recommendation not found")

    out: dict = {
        "recommendation": {
            "id": rec.id, "payer": rec.payer, "origin": rec.origin,
            "provision_type": rec.provision_type, "summary": rec.candidate_summary,
            "validation_verdict": rec.validation_verdict,
            "reconciliation_verdict": rec.reconciliation_verdict,
            "matched_rule_id": rec.matched_rule_id, "confidence": rec.confidence,
            "status": rec.status, "model_version": rec.model_version,
        },
        "source": None,
        "deployment": rec.ace_publish or None,
    }

    if rec.origin == "POLICY" and rec.source_provision_id:
        prov = db.get(models.PolicyProvision, rec.source_provision_id)
        doc = db.get(models.PolicyDocument, rec.source_document_id) if rec.source_document_id else None
        out["source"] = {
            "kind": "policy",
            "document": ({"id": doc.id, "title": doc.title, "payer": doc.payer,
                          "source_type": doc.source_type, "doc_kind": doc.doc_kind,
                          "model_version": doc.model_version} if doc else None),
            "provision": ({"id": prov.id, "provision_type": prov.provision_type,
                           "summary": prov.summary, "citations": prov.citation_spans,
                           "confidence": prov.confidence, "routing": prov.routing} if prov else None),
        }
    elif rec.origin == "DENIAL" and rec.source_signal_id:
        sig = db.get(models.DenialSignal, rec.source_signal_id)
        out["source"] = {
            "kind": "denial",
            "signal": ({"id": sig.id, "procedure_code": sig.procedure_code,
                        "denial_carc": sig.denial_carc, "pattern_type": sig.pattern_type,
                        "recent_denials": sig.recent_denials, "recent_rate": sig.recent_rate,
                        "baseline_rate": sig.baseline_rate, "lift": sig.lift, "z_score": sig.z_score,
                        "evidence": sig.evidence} if sig else None),
        }

    out["decisions"] = entries(db, entity_id=rec_id)
    return out
