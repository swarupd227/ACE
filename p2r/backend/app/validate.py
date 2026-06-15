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

from . import audit, config_store, models, prompts


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
    """Seed the read-only rule library (Meridian sample + Medicare lumbar set). Additive per-id."""
    from . import sample
    existing = {r.id for r in db.scalars(select(models.RuleLibraryEntry)).all()}
    added = False
    for rid, payer, summary, cs in (sample.RULE_LIBRARY_SEED + sample.MEDICARE_RULE_LIBRARY_SEED):
        if rid in existing:
            continue
        db.add(models.RuleLibraryEntry(id=rid, payer=payer, title=summary,
                                       logic_summary=summary, code_sets=cs, status="active"))
        added = True
    if added:
        db.commit()


def _library_ctx(db: Session, payer: str):
    # Tolerant payer match: a library rule applies if its payer name is a case-insensitive
    # substring of the document's payer (or vice versa). So "Medicare (CMS LCD L34220)" matches
    # the "Medicare" rules, and "Meridian Health Plan" still matches its own rules.
    p = (payer or "").strip().lower()
    allrules = db.scalars(select(models.RuleLibraryEntry)).all()
    library = [r for r in allrules if r.payer and p and
               (r.payer.lower() in p or p in r.payer.lower())]
    lib_text = json.dumps([{"rule_id": r.id, "title": r.title, "code_sets": r.code_sets}
                           for r in library], indent=2) if library else "(empty)"
    return lib_text, {r.id for r in library}, {r.id: r for r in library}


def judge_candidate(db: Session, *, payer: str, provision_type: str, summary: str,
                    code_sets: dict, evidence_text: str, evidence_ref: dict,
                    origin: str = "POLICY", source_provision_id: str = "",
                    source_document_id: str = "", source_signal_id: str = "",
                    actor: str = "system", llm: dict | None = None) -> models.RuleRecommendation:
    """Validate one candidate against its evidence and reconcile it against the library.

    Shared by P1 (policy provisions) and P2 (denial signals) — the single P3 judge.
    """
    lib_text, lib_ids, lib_by_id = _library_ctx(db, payer)
    candidate = {"provision_type": provision_type, "summary": summary, "code_sets": code_sets}
    result = llm_client.complete_json(
        prompts.VALIDATOR_SYSTEM, prompts.build_validator_user(candidate, evidence_text, lib_text),
        prompts.VALIDATOR_SCHEMA, temperature=0.0, llm=llm, cache=True,
    )[0]
    val = result.get("validation", {})
    rec = result.get("reconciliation", {})
    matched = rec.get("matched_rule_id", "") or ""
    if matched not in lib_ids:   # grounding: only library ids allowed
        matched = ""
    overlap = _overlap(code_sets, lib_by_id[matched].code_sets) if matched else 0.0
    conf = round(float(result.get("confidence", 0.0)), 3)
    rverdict = rec.get("verdict", "NET_NEW")
    vverdict = val.get("verdict", "")
    attn_below = config_store.section(db, "confidence").get("attention_below", 0.75)
    attention = (rverdict == "CONFLICT") or (vverdict != "SUPPORTED") or (conf < attn_below)
    row = models.RuleRecommendation(
        payer=payer, origin=origin, source_provision_id=source_provision_id,
        source_document_id=source_document_id, source_signal_id=source_signal_id,
        candidate_summary=summary, provision_type=provision_type, code_sets=code_sets,
        validation_verdict=vverdict, validation_rationale=val.get("rationale", ""),
        evidence=[{**evidence_ref, "quote": val.get("evidence_quote", "")}],
        reconciliation_verdict=rverdict, matched_rule_id=matched,
        reconciliation_rationale=rec.get("rationale", ""), code_overlap=overlap,
        confidence=conf, status="PENDING_REVIEW", needs_attention=attention,
        model_version=llm_client.model_version(llm),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    audit.log(db, phase="P3", action="JUDGE", actor=actor, entity_type="recommendation", entity_id=row.id,
              payer=payer, summary=f"{provision_type}: validation={vverdict}, reconciliation={rverdict}"
              + (f" (vs {matched})" if matched else ""),
              lineage={"origin": origin, "source_provision_id": source_provision_id,
                       "source_document_id": source_document_id, "source_signal_id": source_signal_id,
                       "confidence": conf, "model_version": row.model_version})
    return row


def generate_for_document(db: Session, doc_id: str, actor: str = "system", llm: dict | None = None) -> dict:
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
    recs = []
    for p in provs:
        evidence_text = f"[{p.provision_type}] {p.summary}\nConditions: {json.dumps(p.conditions)}"
        recs.append(judge_candidate(
            db, payer=doc.payer, provision_type=p.provision_type, summary=p.summary,
            code_sets=p.code_sets, evidence_text=evidence_text,
            evidence_ref={"provision_id": p.id}, origin="POLICY",
            source_provision_id=p.id, source_document_id=doc_id, actor=actor, llm=llm,
        ))
    return {"document_id": doc_id, "payer": doc.payer, "count": len(recs),
            "recommendations": [rec_dict(r) for r in recs]}


def rec_dict(r: models.RuleRecommendation) -> dict:
    return {
        "id": r.id, "payer": r.payer, "origin": r.origin,
        "source_document_id": r.source_document_id, "source_provision_id": r.source_provision_id,
        "source_signal_id": r.source_signal_id,
        "provision_type": r.provision_type,
        "candidate_summary": r.candidate_summary, "code_sets": r.code_sets,
        "validation_verdict": r.validation_verdict, "validation_rationale": r.validation_rationale,
        "evidence": r.evidence, "reconciliation_verdict": r.reconciliation_verdict,
        "matched_rule_id": r.matched_rule_id, "reconciliation_rationale": r.reconciliation_rationale,
        "code_overlap": r.code_overlap, "confidence": r.confidence, "status": r.status,
        "needs_attention": r.needs_attention,
        "published_to_ace": r.published_to_ace, "ace_publish": r.ace_publish,
    }
