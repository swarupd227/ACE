"""Runtime configuration store (the ACE pattern).

Code DEFAULTS define every tunable knob; rows in app_config override them at runtime. The
ingestion ladder, validator attention threshold, denial-detection parameters, the CARC→rule
map and integration settings are all READ from here on each request, so an Admin change
takes effect on the next run with no redeploy. Secrets (API keys) are never stored here —
they stay in the environment.
"""
from __future__ import annotations

import copy
import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models

DEFAULTS: dict = {
    "confidence": {
        "auto_load": 0.90,       # ingestion routing: ≥ → AUTO_LOAD
        "verify": 0.70,          # ≥ → VERIFY, else HOLD
        "attention_below": 0.75, # P3: flag a recommendation for human attention below this
    },
    "denials": {
        "recent_window_days": 30,
        "z_threshold": 3.0,      # two-proportion z for a SPIKE
        "lift_threshold": 1.5,   # recent_rate / baseline_rate for SPIKE / EMERGING
        "min_denials": 5,        # ignore thin signals
        "persistent_rate": 0.20, # baseline & recent ≥ → PERSISTENT
    },
    "carc_map": {
        "197": "PRIOR_AUTH", "16": "DOCUMENTATION", "11": "COVERAGE",
        "50": "COVERAGE", "151": "FREQUENCY",
    },
    "integration": {
        "ace_base_url": os.getenv("ACE_BASE_URL", "http://host.docker.internal:8000"),
        "source_tag": "P2R-INTEGRATION",
        "demo_payer_denylist": ["anthem", "cigna", "medicare", "unitedhealthcare", "aetna", "humana", "bcbs"],
    },
}


def load(db: Session) -> dict:
    """Merge stored overrides over DEFAULTS (shallow per top-level key)."""
    merged = copy.deepcopy(DEFAULTS)
    for row in db.scalars(select(models.AppConfig)).all():
        if row.key in merged and isinstance(merged[row.key], dict) and isinstance(row.value, dict):
            merged[row.key] = {**merged[row.key], **row.value}
        else:
            merged[row.key] = row.value
    return merged


def section(db: Session, key: str) -> dict:
    return load(db).get(key, {})


def put(db: Session, key: str, value: dict) -> None:
    row = db.get(models.AppConfig, key)
    if row is None:
        db.add(models.AppConfig(key=key, value=value))
    else:
        row.value = value
        db.add(row)
    db.commit()


def reset(db: Session) -> None:
    for row in db.scalars(select(models.AppConfig)).all():
        db.delete(row)
    db.commit()
