"""Phase 1 ingestion pipeline: policy document → cited PolicyProvision records.

Reuses the shared core LLM client. The confidence is composite (the spec's model):
  confidence = model_self_estimate × code_validator_factor × citation_factor
and routes on the ladder ≥0.90 AUTO_LOAD / ≥0.70 VERIFY / else HOLD. Nothing is
fabricated — an extraction with no verifiable citation is depressed and held.
"""
from __future__ import annotations

import hashlib
import re

from sqlalchemy.orm import Session

from core import llm_client

from . import models, prompts

# Deterministic code validators (regex; same idea as ACE's reference checks).
_RX = {
    "cpt": re.compile(r"^[0-9]{4}[0-9A-Z]$"),
    "icd": re.compile(r"^[A-TV-Z][0-9][0-9A-Z](\.[0-9A-Z]{1,4})?$"),
    "hcpcs": re.compile(r"^[A-V][0-9]{4}$"),
    "modifiers": re.compile(r"^[0-9A-Z]{1,2}$"),
    "pos": re.compile(r"^[0-9]{1,2}$"),
}
_TOK = re.compile(r"[a-z0-9]+")


def _number(text: str) -> tuple[str, dict[int, str]]:
    lines = text.splitlines()
    numbered = "\n".join(f"{i+1}|{ln}" for i, ln in enumerate(lines))
    return numbered, {i + 1: ln for i, ln in enumerate(lines)}


def _validator_factor(code_sets: dict) -> float:
    """Fraction of present codes that are well-formed; lenient floor at 0.6."""
    total = ok = 0
    for kind, rx in _RX.items():
        for c in code_sets.get(kind, []) or []:
            total += 1
            if rx.match(str(c).strip().upper()):
                ok += 1
    if total == 0:
        return 1.0
    return round(0.6 + 0.4 * (ok / total), 3)


def _toks(s: str) -> set[str]:
    return {t for t in _TOK.findall((s or "").lower()) if len(t) > 2}


def _verify_citation(span: dict, lookup: dict[int, str]) -> bool:
    ls, le = int(span.get("line_start", 0)), int(span.get("line_end", 0))
    chart = " ".join(lookup.get(i, "") for i in range(ls, le + 1))
    claimed, actual = _toks(span.get("text", "")), _toks(chart)
    if not claimed:
        return False
    return len(claimed & actual) / len(claimed) >= 0.5


def ingest_policy(db: Session, payer: str, title: str, text: str,
                  source_type: str = "UPLOAD", llm: dict | None = None) -> dict:
    numbered, lookup = _number(text)
    usage: list = []
    result = llm_client.complete_json(
        prompts.POLICY_EXTRACT_SYSTEM, prompts.build_policy_user(numbered, payer),
        prompts.POLICY_SCHEMA, temperature=0.0, llm=llm, usage_sink=usage, cache=True,
    )[0]

    mv = llm_client.model_version(llm)
    doc = models.PolicyDocument(
        payer=payer, title=title, source_type=source_type,
        doc_kind=result.get("doc_kind", ""), content_hash=hashlib.sha256(text.encode()).hexdigest(),
        raw_text=text, model_version=mv,
    )
    db.add(doc)
    db.flush()

    provisions = []
    for p in result.get("provisions", []):
        conf_model = float(p.get("confidence", 0.0))
        vfactor = _validator_factor(p.get("code_sets", {}) or {})
        cits = p.get("citations", []) or []
        verified = [{**c, "verified": _verify_citation(c, lookup)} for c in cits]
        cit_factor = 1.0 if any(c["verified"] for c in verified) else 0.5
        conf = round(conf_model * vfactor * cit_factor, 3)
        routing = "AUTO_LOAD" if conf >= 0.90 else "VERIFY" if conf >= 0.70 else "HOLD"
        prov = models.PolicyProvision(
            document_id=doc.id, payer=payer, provision_type=p.get("provision_type", ""),
            summary=p.get("summary", ""), code_sets=p.get("code_sets", {}),
            conditions=p.get("conditions", {}), effective_from=p.get("effective_from", "") or "",
            effective_thru=p.get("effective_thru", "") or "", citation_spans=verified,
            confidence=conf, conf_model=round(conf_model, 3), conf_validator=vfactor,
            routing=routing, extraction_meta={"model": mv},
        )
        db.add(prov)
        provisions.append(prov)

    doc.provision_count = len(provisions)
    db.commit()
    db.refresh(doc)
    return {
        "document_id": doc.id, "payer": doc.payer, "title": doc.title, "doc_kind": doc.doc_kind,
        "provision_count": doc.provision_count,
        "tokens": {"in": sum(u.get("in", 0) for u in usage), "out": sum(u.get("out", 0) for u in usage)},
        "provisions": [_prov_dict(p) for p in provisions],
    }


def _prov_dict(p: models.PolicyProvision) -> dict:
    return {
        "id": p.id, "provision_type": p.provision_type, "summary": p.summary,
        "code_sets": p.code_sets, "conditions": p.conditions,
        "effective_from": p.effective_from, "effective_thru": p.effective_thru,
        "citation_spans": p.citation_spans, "confidence": p.confidence,
        "conf_model": p.conf_model, "conf_validator": p.conf_validator, "routing": p.routing,
    }
