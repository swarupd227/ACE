"""Phase 5 — "Publish to ACE" integration glimpse.

Turns a human-APPROVED rule recommendation into payer-policy rows inside ACE, using
ACE's EXISTING public policy API — the same mechanism proven live with the Medicare-policy
edit that changed a medical-necessity gate. This is the closed loop made visible:
P2R authors the rule, ACE consumes it.

Safety by construction (so the scripted Vee/ACE demo can never move):
  * write-only — we POST policies, we never read or mutate ACE's coding state;
  * on explicit click — only an APPROVED recommendation can be published;
  * sandbox payer only — a denylist refuses any scripted demo payer, and every row is
    stamped source="P2R-INTEGRATION" so it is trivially identifiable and removable.
ACE needs no changes: it already exposes POST/GET /api/policies.
"""
from __future__ import annotations

import os

import httpx
from sqlalchemy.orm import Session

from . import models

ACE_BASE_URL = os.getenv("ACE_BASE_URL", "http://host.docker.internal:8000")
ACE_SOURCE_TAG = "P2R-INTEGRATION"

# Belt-and-braces: these are ACE's scripted demo payers. We refuse to publish against any
# of them so a glimpse can never overwrite a policy the Vee demo depends on. The sample
# policy's payer ("Meridian Health Plan") is intentionally NOT one of these.
_DEMO_PAYERS = {"anthem", "cigna", "medicare", "unitedhealthcare", "aetna", "humana", "bcbs"}


def _icd_prefixes(code_sets: dict) -> list[str]:
    return [str(c).strip() for c in (code_sets or {}).get("icd", []) or [] if str(c).strip()]


def _modifier_pref(code_sets: dict) -> str:
    mods = [str(m).strip() for m in (code_sets or {}).get("modifiers", []) or [] if str(m).strip()]
    return mods[0] if mods else ""


def build_policy_payloads(rec: models.RuleRecommendation) -> list[dict]:
    """One ACE payer-policy per CPT code in the recommendation. ACE keys policy on (payer, code)."""
    cpts = [str(c).strip() for c in (rec.code_sets or {}).get("cpt", []) or [] if str(c).strip()]
    if not cpts:
        return []
    necessity = (rec.candidate_summary or "")[:480]
    requires_auth = rec.provision_type == "PRIOR_AUTH"
    modifier_pref = _modifier_pref(rec.code_sets)
    covered_dx = _icd_prefixes(rec.code_sets)
    return [
        {
            "payer": rec.payer,
            "code": code,
            "medical_necessity": necessity,
            "requires_auth": requires_auth,
            "modifier_pref": modifier_pref,
            "covered_dx": covered_dx,
            "source": ACE_SOURCE_TAG,
        }
        for code in cpts
    ]


def ace_reachable(timeout: float = 4.0) -> dict:
    """Lightweight connectivity + sandbox-policy count, for the workbench status panel."""
    try:
        with httpx.Client(base_url=ACE_BASE_URL, timeout=timeout) as c:
            meta = c.get("/api/meta")
            pols = c.get("/api/policies")
            pols.raise_for_status()
            published = [p for p in pols.json() if (p.get("source") == ACE_SOURCE_TAG)]
            return {
                "reachable": True,
                "ace_base_url": ACE_BASE_URL,
                "ace_llm_available": (meta.json().get("llm_available") if meta.status_code == 200 else None),
                "p2r_published_policies": len(published),
            }
    except Exception as exc:  # noqa: BLE001 — surface any transport error honestly
        return {"reachable": False, "ace_base_url": ACE_BASE_URL, "error": str(exc)}


def publish_recommendation(db: Session, rec_id: str) -> dict:
    """Publish an APPROVED recommendation's CPT policies into ACE. Raises ValueError on guard fail."""
    rec = db.get(models.RuleRecommendation, rec_id)
    if rec is None:
        raise ValueError("recommendation not found")
    if rec.status != "APPROVED":
        raise ValueError(f"only APPROVED recommendations can be published (status={rec.status})")
    if (rec.payer or "").strip().lower() in _DEMO_PAYERS:
        raise ValueError(f"refusing to publish against scripted demo payer '{rec.payer}' (sandbox only)")

    payloads = build_policy_payloads(rec)
    if not payloads:
        raise ValueError("recommendation has no CPT code to publish as an ACE policy")

    headers = {"X-Actor": "P2R-INTEGRATION", "X-Role": "Admin"}
    created: list[dict] = []
    with httpx.Client(base_url=ACE_BASE_URL, timeout=15.0, headers=headers) as c:
        for body in payloads:
            resp = c.post("/api/policies", json=body)
            resp.raise_for_status()
            data = resp.json()
            created.append({"code": body["code"], "ace_id": data.get("id"), "payer": data.get("payer")})

    rec.published_to_ace = True
    rec.status = "PUBLISHED"
    rec.ace_publish = {"payer": rec.payer, "source": ACE_SOURCE_TAG, "policies": created,
                       "ace_base_url": ACE_BASE_URL}
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"recommendation_id": rec.id, "published": len(created), "policies": created,
            "source": ACE_SOURCE_TAG, "payer": rec.payer}


def rollback_recommendation(db: Session, rec_id: str) -> dict:
    """Retract a published rule from ACE (delete the policies it created) and revert status."""
    rec = db.get(models.RuleRecommendation, rec_id)
    if rec is None:
        raise ValueError("recommendation not found")
    if not rec.published_to_ace:
        raise ValueError("recommendation is not published")
    policies = (rec.ace_publish or {}).get("policies", [])
    headers = {"X-Actor": "P2R-INTEGRATION", "X-Role": "Admin"}
    deleted = []
    with httpx.Client(base_url=ACE_BASE_URL, timeout=15.0, headers=headers) as c:
        for p in policies:
            aid = p.get("ace_id")
            if aid is None:
                continue
            resp = c.delete(f"/api/policies/{aid}")
            if resp.status_code in (200, 204, 404):  # 404 = already gone; treat as retracted
                deleted.append(aid)
            else:
                resp.raise_for_status()
    rec.published_to_ace = False
    rec.status = "APPROVED"
    rec.ace_publish = {"rolled_back": True, "retracted_ace_ids": deleted, "source": ACE_SOURCE_TAG}
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"recommendation_id": rec.id, "retracted": len(deleted), "ace_ids": deleted,
            "status": rec.status}
