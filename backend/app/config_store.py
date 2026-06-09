"""Admin-editable runtime configuration. Defaults live here; overrides live in the
`app_config` table. The pipeline/validation/SLA/eligibility read the merged config
at runtime, so an admin can tune the platform without code changes."""
from __future__ import annotations

import copy

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models

DEFAULTS: dict = {
    "routing": {"stb_threshold": 0.90, "qa_threshold": 0.75},
    "confidence_weights": {"model": 0.40, "doc_match": 0.25, "rule": 0.25, "historical": 0.10},
    "self_consistency": {"hard_samples": 3},
    "sla_targets_min": {"STB": 180, "QA": 480, "MANUAL": 1440, "ESCALATED": 240, "CDI": 2880},
    "eligibility": {
        "min_doc_chars": 120,
        "exclude_interventional": True,
        "exclude_trauma": True,
        "exclude_incomplete": True,
    },
    "bounded_autonomy": {
        "block_flag": True,
        "ambiguous_or_contradiction": True,
        "critical_care": True,
        "ncci_break": True,
    },
    "specialties": [
        {"name": "Radiology", "enabled": True, "hard": False},
        {"name": "E&M", "enabled": True, "hard": True},
        {"name": "ED", "enabled": True, "hard": True},
        {"name": "Pathology", "enabled": True, "hard": False},
        {"name": "Surgical", "enabled": True, "hard": True},
        {"name": "Cardiology", "enabled": True, "hard": False},
        {"name": "Orthopedics", "enabled": True, "hard": False},
        {"name": "OB/GYN", "enabled": True, "hard": False},
        {"name": "GI / Endoscopy", "enabled": True, "hard": False},
        {"name": "Dermatology", "enabled": True, "hard": False},
        {"name": "Urology", "enabled": True, "hard": False},
        {"name": "Anesthesia", "enabled": True, "hard": False},
        {"name": "Ophthalmology", "enabled": True, "hard": False},
    ],
    "roster": [
        {"name": "Priya N.", "role": "Coder"},
        {"name": "Marcus L.", "role": "Coder"},
        {"name": "Aisha K.", "role": "QA Auditor"},
        {"name": "David R.", "role": "QA Auditor"},
        {"name": "CDI Team", "role": "CDI Specialist"},
    ],
    "connectors": [
        {"name": "Practice Admin", "type": "PMS (VHT-owned)", "channel": "REST / batch", "enabled": True},
        {"name": "eClinicalWorks", "type": "EHR", "channel": "FHIR R4 / HL7 v2", "enabled": True},
        {"name": "Cerner", "type": "EHR", "channel": "FHIR R4 / HL7 v2", "enabled": True},
    ],
    "llm": {
        "provider": "anthropic",            # anthropic | openai_compatible
        "model_default": "claude-sonnet-4-5",
        "model_hard": "claude-opus-4-1",
        "base_url": "",                     # required for openai_compatible (Azure OpenAI / OpenAI / vLLM / Ollama)
        "max_tokens": 4096,
    },
}

# Human-friendly metadata for the Admin UI (label + type hints).
META: dict = {
    "routing": "Confidence thresholds for STB / QA routing",
    "confidence_weights": "Weights of the 4 accuracy-source factors (should sum to 1.0)",
    "self_consistency": "Samples for self-consistency on hard encounters",
    "sla_targets_min": "SLA targets per queue (minutes)",
    "eligibility": "Stage-0 auto-coding eligibility rules",
    "bounded_autonomy": "Hard rules that force human review regardless of confidence",
    "specialties": "Enabled specialties and their model-tier (hard = Opus + self-consistency)",
    "roster": "Coders / auditors available for assignment",
    "connectors": "Source systems (PMS/EHR) shown on the Integrations screen",
    "llm": "The reasoning model — provider, default/hard models and endpoint (API keys stay in the environment)",
}


def all_config(db: Session) -> dict:
    cfg = copy.deepcopy(DEFAULTS)
    for r in db.scalars(select(models.AppConfig)).all():
        cfg[r.key] = r.value
    return cfg


def get(db: Session, key: str):
    return all_config(db).get(key, copy.deepcopy(DEFAULTS.get(key)))


def set_key(db: Session, key: str, value) -> dict:
    row = db.get(models.AppConfig, key)
    if row is None:
        db.add(models.AppConfig(key=key, value=value))
    else:
        row.value = value
    db.commit()
    return value


def seed_defaults(db: Session) -> None:
    existing = {r.key for r in db.scalars(select(models.AppConfig)).all()}
    for k, v in DEFAULTS.items():
        if k not in existing:
            db.add(models.AppConfig(key=k, value=copy.deepcopy(v)))
    db.commit()
