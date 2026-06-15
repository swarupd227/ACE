"""Phase 1 completion — source registry, acquisition agent, change deltas, payer MDM.

A registered PolicySource is polled by the acquisition agent: it fetches the source's current
content, hashes it, and only when the hash changes does it ingest a new version (reusing the
P1 extraction pipeline) and compute a structured delta against the prior version. Payer
identity is mastered in PayerMaster (MDM). Live payer-site crawling is out of scope — sources
expose sandbox/synthetic content — but the change-detection, versioning and delta logic are real.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import audit, ingest, models, sample


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _versions_for(source_name: str) -> tuple[list[str], str]:
    for s in sample.SOURCE_SEED:
        if s["name"] == source_name:
            return s["versions"], s.get("title", "")
    return [], ""


def seed_registry(db: Session) -> None:
    """Seed payer master + policy sources if empty."""
    if db.scalar(select(models.PayerMaster.payer_id).limit(1)) is None:
        for m in sample.PAYER_MASTER_SEED:
            db.add(models.PayerMaster(**m))
    if db.scalar(select(models.PolicySource.id).limit(1)) is None:
        for s in sample.SOURCE_SEED:
            db.add(models.PolicySource(
                payer=s["payer"], name=s["name"], source_type=s["source_type"],
                location=s["location"], cadence=s["cadence"],
            ))
    db.commit()


def ensure_payer_master(db: Session, payer: str) -> None:
    slug = payer.lower().replace(" ", "-")[:40]
    if db.get(models.PayerMaster, slug) is None:
        # match by name/alias before creating a new master
        existing = db.scalars(select(models.PayerMaster)).all()
        for m in existing:
            if payer == m.name or payer in (m.aliases or []):
                return
        db.add(models.PayerMaster(payer_id=slug, name=payer))
        db.commit()


def _provs(db: Session, doc_id: str) -> list[models.PolicyProvision]:
    return list(db.scalars(select(models.PolicyProvision).where(
        models.PolicyProvision.document_id == doc_id)))


def _codes_sig(cs: dict) -> set[str]:
    out: set[str] = set()
    for k, v in (cs or {}).items():
        if isinstance(v, list):
            out |= {f"{k}:{str(c).strip().upper()}" for c in v}
    return out


_THRESHOLD = re.compile(r"(\d+)\s*-?\s*(month|week|day|year)", re.I)


def _citation_text(p: models.PolicyProvision) -> str:
    return " ".join(c.get("text", "") for c in (p.citation_spans or []))


def _threshold_sig(p: models.PolicyProvision) -> set[str]:
    # Numeric time-thresholds (e.g. "24 months") from the VERBATIM cited source text — not the
    # paraphrased summary — so a limit change is caught without model-wording noise. Digit-anchored,
    # so word-form durations ("six weeks") don't register.
    return {f"{n} {u.lower()}" for n, u in _THRESHOLD.findall(_citation_text(p))}


def _delta(prev: list[models.PolicyProvision], new: list[models.PolicyProvision]) -> dict:
    pb = {p.provision_type: p for p in prev}
    nb = {p.provision_type: p for p in new}
    added = sorted(set(nb) - set(pb))
    removed = sorted(set(pb) - set(nb))
    changed = []
    # Compare on STRUCTURED signals (codes + conditions), not the model's prose summary, so
    # the delta is deterministic and free of paraphrase noise.
    for t in sorted(set(pb) & set(nb)):
        before_sig = _codes_sig(pb[t].code_sets) | _threshold_sig(pb[t])
        after_sig = _codes_sig(nb[t].code_sets) | _threshold_sig(nb[t])
        if before_sig != after_sig:
            changed.append({
                "type": t, "before": pb[t].summary, "after": nb[t].summary,
                "added_signals": sorted(after_sig - before_sig),
                "removed_signals": sorted(before_sig - after_sig),
            })
    bits = []
    if added:
        bits.append(f"added {', '.join(added)}")
    if removed:
        bits.append(f"removed {', '.join(removed)}")
    if changed:
        bits.append(f"changed {', '.join(c['type'] for c in changed)}")
    return {"added": added, "removed": removed, "changed": changed,
            "summary": "; ".join(bits) if bits else "no material change"}


def acquire(db: Session, source_id: str, actor: str = "acquisition-agent",
            llm: dict | None = None, emit=None) -> dict:
    """Poll a source: fetch its current version, ingest + delta only if the content changed."""
    e = emit or (lambda ev: None)
    src = db.get(models.PolicySource, source_id)
    if src is None:
        raise ValueError("source not found")
    versions, title = _versions_for(src.name)
    if not versions:
        raise ValueError("source has no content configured")

    e({"type": "log", "phase": "P1", "message": f"Polling '{src.name}'…"})
    idx = min(src.fetch_count, len(versions) - 1)  # successive polls reveal successive revisions
    content = versions[idx]
    new_hash = hashlib.sha256(content.encode()).hexdigest()
    src.last_checked = _now_iso()
    e({"type": "log", "phase": "P1", "message": f"Fetched content (sha256 {new_hash[:12]}…)."})

    if new_hash == src.last_content_hash:
        src.fetch_count += 1
        db.add(src)
        db.commit()
        e({"type": "log", "phase": "P1", "message": "No change since last poll — nothing to ingest."})
        return {"source_id": src.id, "changed": False, "reason": "content unchanged since last poll"}

    e({"type": "log", "phase": "P1", "message": "Content changed — extracting cited provisions…"})
    prev_doc_id = src.last_document_id
    prev_provs = _provs(db, prev_doc_id) if prev_doc_id else []
    ing = ingest.ingest_policy(db, src.payer, title, content, source_type="ACQUIRED", llm=llm)
    doc_id = ing["document_id"]
    ensure_payer_master(db, src.payer)
    new_provs = _provs(db, doc_id)
    e({"type": "log", "phase": "P1", "message": f"Extracted {len(new_provs)} provisions; computing delta…"})

    change_type = "REVISION" if prev_doc_id else "NEW_POLICY"
    d = _delta(prev_provs, new_provs) if prev_doc_id else {
        "added": sorted({p.provision_type for p in new_provs}), "removed": [], "changed": [],
        "summary": f"initial acquisition — {len(new_provs)} provisions"}
    delta = models.PolicyDelta(
        source_id=src.id, payer=src.payer, document_id=doc_id, prev_document_id=prev_doc_id,
        change_type=change_type, added=d["added"], removed=d["removed"], changed=d["changed"],
        summary=d["summary"],
    )
    db.add(delta)

    src.last_content_hash = new_hash
    src.last_document_id = doc_id
    src.fetch_count += 1
    db.add(src)
    db.commit()
    db.refresh(delta)
    e({"type": "log", "phase": "P1", "message": f"{change_type}: {d['summary']}"})
    audit.log(db, phase="P1", action="ACQUIRE", actor=actor,
              entity_type="document", entity_id=doc_id, payer=src.payer,
              summary=f"{change_type} from '{src.name}' — {d['summary']}",
              lineage={"source_id": src.id, "prev_document_id": prev_doc_id,
                       "delta": delta_dict(delta)})
    return {"source_id": src.id, "changed": True, "change_type": change_type,
            "document_id": doc_id, "provisions": ing["provision_count"], "delta": delta_dict(delta)}


def source_dict(s: models.PolicySource) -> dict:
    return {"id": s.id, "payer": s.payer, "name": s.name, "source_type": s.source_type,
            "location": s.location, "cadence": s.cadence, "status": s.status,
            "fetch_count": s.fetch_count, "last_checked": s.last_checked,
            "last_document_id": s.last_document_id}


def delta_dict(d: models.PolicyDelta) -> dict:
    return {"id": d.id, "source_id": d.source_id, "payer": d.payer, "document_id": d.document_id,
            "prev_document_id": d.prev_document_id, "change_type": d.change_type,
            "added": d.added, "removed": d.removed, "changed": d.changed, "summary": d.summary,
            "created_at": d.created_at.isoformat() if d.created_at else None}


def master_dict(m: models.PayerMaster) -> dict:
    return {"payer_id": m.payer_id, "name": m.name, "aliases": m.aliases,
            "lines_of_business": m.lines_of_business, "status": m.status}
