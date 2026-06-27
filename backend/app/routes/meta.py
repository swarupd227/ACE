"""Health + metadata (LLM mode, model, data provenance) for the UI."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import config_store
from ..config import settings
from ..db import get_db
from ..llm import client as llm_client

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/meta")
def meta(db: Session = Depends(get_db)) -> dict:
    llm = config_store.all_config(db).get("llm")
    e = llm_client.effective_llm(llm)
    return {
        "product": "ACE — Autonomous Coding Engine",
        "framing": "Engine inside Nous RCM Studio",
        "env": settings.ace_env,
        "llm_mode": e["provider"],
        "llm_available": llm_client.llm_available(llm),
        "model_default": e["model_default"],
        "model_hard": e["model_hard"],
        "model_version": llm_client.model_version(llm),
        "self_consistency_samples": settings.ace_self_consistency_samples,
        # live from config_store so admin-added specialties appear everywhere
        "specialties": [s["name"] for s in (config_store.all_config(db).get("specialties") or []) if s.get("enabled", True)],
        "provenance": {
            "ICD10CM": "REAL public-domain subset (CMS/NCHS)",
            "HCPCS": "REAL public-domain subset (CMS)",
            "CPT": "DEMO placeholder (not AMA text); swap licensed AMA for production",
            "NCCI/MUE": "Modeled on real CMS edit logic (subset)",
            "guidelines": "ICD-10-CM Official Guidelines (public), paraphrased",
            "effective_dating": "ICD-10-CM FY2026 (eff 2025-10-01), CPT 2026 (eff 2026-01-01); "
                                "prior-year sets retained for back-dated/corrected claims",
        },
    }
