"""Phase 3 — Validation & Reconciliation (the Validator Judge).

For each candidate rule (derived from an ingested provision), retrieve the governing
policy evidence and the existing rule library, then have the model VALIDATE the
candidate against the evidence and RECONCILE it against the library
(NET_NEW / UPDATE / DUPLICATE / CONFLICT) with a cited rationale. A deterministic
code-overlap cross-check grounds the reconciliation. Every recommendation enters the
human review queue; CONFLICT / UNSUPPORTED / low-confidence are flagged for attention.
Reuses the shared core LLM client.
"""
from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from core import llm_client

from . import models, prompts


def _codes(cs: dict) -> set[str]:
    out: set[str] = set()
    for k in ("cpt", "icd", "hcpcs"):
        out |= {str(c).strip().upper() for c in (cs or {}).get(k, []) or []}
    return out


def _overlap(a: dict, b: dict) -> float:
    ca, cb = _codes(a), _codes(b)
    if not ca or not cb:
        return 0.0
    return round(len(ca & cb) / len(ca | cb), 3)


def _seed_library(db: Session) -> None:
    from . import sample
    if db.scalars(select(models.RuleLibraryEntry).limit(1)).first():
        return
    for rid, payer, summary, cs in sample.RULE_LIBRARY_SEED:
        db.add(models.RuleLibraryEntry(id=rid, payer=payer, title=summary,
                                       logic_summary=summary, code_sets=cs, status="active"))
    db.commit()


def generate_for_document(db: Session, doc_id: str, llm: dict | None = None) -> dict:
    doc = db.get(models.PolicyDocument, doc_id)
    if doc is None:
        raise ValueError("document not found")
    # Candidates come from provisions that cleared ingestion (skip HOLD).
    provs = db.scalars(
        select(models.PolicyProvision).where(
            models.PolicyProvision.document_id == doc_id,
            models.PolicyProvision.routing != "HOLD",
        )
    ).all()
    library = db.scalars(select(models.RuleLibraryEntry).where(
        models.RuleLibraryEntry.payer == doc.payer)).all()
    lib_text = json.dumps([{"rule_id": r.id, "title": r.title, "code_sets": r.code_sets}
                           for r in library], indent=2) or "(empty)"
    lib_ids = {r.id for r in library}
    lib_by_id = {r.id: r for r in library}
    mv = llm_client.model_version(llm)

    recs = []
    for p in provs:
        candidate = {"provision_type": p.provision_type, "summary": p.summary, "code_sets": p.code_sets}
        evidence_text = f"[{p.provision_type}] {p.summary}\nConditions: {json.dumps(p.conditions)}"
        result = llm_client.complete_json(
            prompts.VALIDATOR_SYSTEM, prompts.build_validator_user(candidate, evidence_text, lib_text),
            prompts.VALIDATOR_SCHEMA, temperature=0.0, llm=llm, cache=True,
        )[0]
        val = result.get("validation", {})
        rec = result.get("reconciliation", {})
        matched = rec.get("matched_rule_id", "") or ""
        if matched not in lib_ids:   # grounding: only library ids allowed
            matched = ""
        overlap = _overlap(p.code_sets, lib_by_id[matched].code_sets) if matched else 0.0
        conf = round(float(result.get("confidence", 0.0)), 3)
        rverdict = rec.get("verdict", "NET_NEW")
        vverdict = val.get("verdict", "")
        attention = (rverdict == "CONFLICT") or (vverdict != "SUPPORTED") or (conf < 0.75)
        row = models.RuleRecommendation(
            payer=doc.payer, source_provision_id=p.id, source_document_id=doc_id,
            candidate_summary=p.summary, provision_type=p.provision_type, code_sets=p.code_sets,
            validation_verdict=vverdict, validation_rationale=val.get("rationale", ""),
            evidence=[{"provision_id": p.id, "quote": val.get("evidence_quote", "")}],
            reconciliation_verdict=rverdict, matched_rule_id=matched,
            reconciliation_rationale=rec.get("rationale", ""), code_overlap=overlap,
            confidence=conf, status="PENDING_REVIEW", needs_attention=attention, model_version=mv,
        )
        db.add(row)
        recs.append(row)
    db.commit()
    for r in recs:
        db.refresh(r)
    return {"document_id": doc_id, "payer": doc.payer, "count": len(recs),
            "recommendations": [rec_dict(r) for r in recs]}


def rec_dict(r: models.RuleRecommendation) -> dict:
    return {
        "id": r.id, "payer": r.payer, "provision_type": r.provision_type,
        "candidate_summary": r.candidate_summary, "code_sets": r.code_sets,
        "validation_verdict": r.validation_verdict, "validation_rationale": r.validation_rationale,
        "evidence": r.evidence, "reconciliation_verdict": r.reconciliation_verdict,
        "matched_rule_id": r.matched_rule_id, "reconciliation_rationale": r.reconciliation_rationale,
        "code_overlap": r.code_overlap, "confidence": r.confidence, "status": r.status,
        "needs_attention": r.needs_attention,
        "published_to_ace": r.published_to_ace, "ace_publish": r.ace_publish,
    }
