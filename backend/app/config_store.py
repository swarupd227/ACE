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
        "unsigned_note": True,
        "copy_forward": True,
        "critical_care": True,
        "ncci_break": True,
    },
    "specialties": [
        {"name": "Radiology", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "E&M", "enabled": True, "hard": True, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "ED", "enabled": True, "hard": True, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "Pathology", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "Surgical", "enabled": True, "hard": True, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "Cardiology", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "Orthopedics", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "OB/GYN", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "GI / Endoscopy", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "Dermatology", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "Urology", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "Anesthesia", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "Ophthalmology", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "ENT", "enabled": True, "hard": False, "required_code_families_for_stb": ["CPT_HCPCS"]},
        {"name": "Inpatient (DRG)", "enabled": True, "hard": True, "required_code_families_for_stb": []},
        {"name": "HCC / Risk Adjustment", "enabled": True, "hard": True, "required_code_families_for_stb": []},
    ],
    "roster": [
        # specialties = what this person is credentialed to work; below-threshold charts
        # auto-route to a least-loaded specialty MATCH, never a generic queue. An entry
        # without a list matches every specialty (backward compatible).
        {"name": "Priya N.", "role": "Coder",
         "specialties": ["Radiology", "E&M", "ED", "Cardiology", "Orthopedics", "ENT", "Ophthalmology"]},
        {"name": "Marcus L.", "role": "Coder",
         "specialties": ["Surgical", "Pathology", "GI / Endoscopy", "OB/GYN", "Dermatology", "Urology",
                          "Anesthesia", "Inpatient (DRG)", "HCC / Risk Adjustment"]},
        {"name": "Aisha K.", "role": "QA Auditor",
         "specialties": ["Radiology", "E&M", "ED", "Pathology", "Cardiology", "Orthopedics", "ENT",
                          "Ophthalmology"]},
        {"name": "David R.", "role": "QA Auditor",
         "specialties": ["Surgical", "GI / Endoscopy", "OB/GYN", "Dermatology", "Urology", "Anesthesia",
                          "Inpatient (DRG)", "HCC / Risk Adjustment"]},
        {"name": "CDI Team", "role": "CDI Specialist"},
    ],
    "connectors": [
        {"name": "Practice Admin", "type": "PMS (VHT-owned)", "channel": "REST / batch", "enabled": True},
        {"name": "eClinicalWorks", "type": "EHR", "channel": "FHIR R4 / HL7 v2", "enabled": True},
        {"name": "Cerner", "type": "EHR", "channel": "FHIR R4 / HL7 v2", "enabled": True},
    ],
    "privacy": {
        # Mask direct identifiers (name/MRN/DOB/SSN/phone) from the model's copy of the
        # chart before ANY model call. Age/sex/DOS are kept — coding needs them.
        "mask_identifiers": True,
    },
    "anesthesia": {
        # Representative national CMS anesthesia conversion factor ($/unit); varies by
        # locality and payer — admin-tunable. Physical-status unit adders follow
        # commercial convention (Medicare pays 0 for P-modifiers; the trace says so).
        "conversion_factor": 20.32,
        "phys_status_units": {"P1": 0, "P2": 0, "P3": 1, "P4": 2, "P5": 3, "P6": 0},
    },
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
    "privacy": "Pre-model PII masking — direct identifiers are masked before any model call (age/sex/DOS kept)",
    "anesthesia": "Anesthesia unit payment — conversion factor ($/unit) and physical-status unit adders",
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
