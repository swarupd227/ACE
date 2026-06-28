"""Connector orchestration helpers (E1): inbound sync + outbound billing hand-off.

Keeps the integration logic out of the coding pipeline. The orchestrator calls
`maybe_auto_handoff` once a run finalises; the Integrations screen calls `sync_inbound`
and `manual_handoff`.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from .base import InboundChart
from .practice_admin import get_connector


# --- inbound: pull charts from the PMS and create encounters ----------------
def sync_inbound(db: Session, cfg: dict, limit: int = 5) -> dict:
    conn = get_connector(cfg)
    charts = conn.pull_charts(limit=limit)
    created, skipped = [], 0
    for ch in charts:
        if ch.external_id and db.scalar(
            select(models.Encounter.id).where(models.Encounter.external_id == ch.external_id)
        ):
            skipped += 1
            continue
        enc = _encounter_from_chart(db, ch, cfg)
        created.append({"id": enc.id, "mrn": enc.mrn, "specialty": enc.specialty,
                        "external_id": enc.external_id, "source_system": enc.source_system})
    db.commit()
    return {"connector": conn.connector, "mode": conn.status().mode,
            "pulled": len(charts), "created": created, "skipped": skipped}


def _encounter_from_chart(db: Session, ch: InboundChart, cfg: dict) -> models.Encounter:
    text = ch.text or ""
    if ch.document and ch.content_type:
        # Scanned packet → vision OCR (same path as the upload card).
        from core import llm_client
        text = llm_client.extract_document_text(ch.document, ch.content_type,
                                                llm=cfg.get("llm"), usage_sink=[])
    mrn = ch.mrn or f"PA{abs(hash(ch.external_id)) % 100000:05d}"
    enc = models.Encounter(
        mrn=mrn, patient_name=ch.patient_name, age=ch.age, sex=ch.sex,
        specialty=ch.specialty, modality=ch.modality, payer=ch.payer, pos=ch.pos,
        dos=ch.dos or "2026-06-25", client="Practice Admin", source_system="Practice Admin",
        external_id=ch.external_id, report_type="pms_pull", chart_text=text,
        scenario="Pulled from Practice Admin", status="NEW",
        doc_status=ch.doc_status or "final",
    )
    db.add(enc)
    db.flush()
    return enc


# --- outbound: push a coded result to the PMS work item / billing queue ------
def _codes_summary(run: models.CodingRun) -> list[dict]:
    out = []
    for c in run.codes:
        if c.status == "rejected":
            continue
        out.append({"system": c.code_system,
                    "code": c.override_code if getattr(c, "is_overridden", False) else c.code,
                    "modifiers": list(c.modifiers or []), "description": c.description,
                    "role": c.role})
    return out


def do_handoff(db: Session, enc: models.Encounter, run: models.CodingRun, cfg: dict,
               trigger: str = "auto") -> models.BillingHandoff:
    conn = get_connector(cfg)
    codes = _codes_summary(run)
    payload = {
        "external_id": enc.external_id, "mrn": enc.mrn, "specialty": enc.specialty,
        "payer": enc.payer, "dos": enc.dos, "pos": enc.pos,
        "lane": run.routing_lane, "confidence": run.overall_confidence, "codes": codes,
    }
    res = conn.push_result(payload)
    ho = models.BillingHandoff(
        encounter_id=enc.id, run_id=run.id, connector=conn.connector, mode=conn.status().mode,
        external_id=enc.external_id, work_item_id=res.work_item_id,
        billing_status=res.billing_status or ("accepted" if res.ok else "error"),
        lane=run.routing_lane, trigger=trigger, codes=codes, detail=res.detail,
    )
    db.add(ho)
    db.commit()
    db.refresh(ho)
    return ho


def maybe_auto_handoff(db: Session, enc: models.Encounter, run: models.CodingRun,
                       cfg: dict, emit=None) -> models.BillingHandoff | None:
    """Called by the orchestrator when a run finalises. Auto-posts straight-through (STB)
    charts to the source billing queue when enabled. Soft-fail: never breaks coding."""
    conn = get_connector(cfg)
    if not conn.auto_handoff_stb or run.routing_lane != "STB":
        return None
    ho = do_handoff(db, enc, run, cfg, trigger="auto")
    if emit:
        emit({"type": "log", "actor": "Billing Hand-off",
              "msg": f"posted to {conn.name} → work item {ho.work_item_id} ({ho.billing_status})",
              "level": "good"})
    return ho


def recent_handoffs(db: Session, limit: int = 25) -> list[dict]:
    rows = db.scalars(
        select(models.BillingHandoff).order_by(models.BillingHandoff.created_at.desc()).limit(limit)
    ).all()
    return [
        {"id": h.id, "encounter_id": h.encounter_id, "external_id": h.external_id,
         "work_item_id": h.work_item_id, "billing_status": h.billing_status, "lane": h.lane,
         "trigger": h.trigger, "mode": h.mode, "connector": h.connector,
         "codes": h.codes, "detail": h.detail,
         "created_at": h.created_at.isoformat() if h.created_at else ""}
        for h in rows
    ]
