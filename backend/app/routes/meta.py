"""Health + metadata (LLM mode, model, data provenance) for the UI."""
from __future__ import annotations

from fastapi import APIRouter

from ..config import settings
from ..llm.client import model_version

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/meta")
def meta() -> dict:
    return {
        "product": "ACE — Autonomous Coding Engine",
        "framing": "Engine inside RevAmp Coding Studio",
        "env": settings.ace_env,
        "llm_mode": settings.llm_mode,
        "llm_available": settings.llm_available,
        "model_default": settings.ace_model_default,
        "model_hard": settings.ace_model_hard,
        "model_version": model_version(),
        "self_consistency_samples": settings.ace_self_consistency_samples,
        "specialties": ["Radiology", "E&M", "ED", "Pathology", "Surgical"],
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
