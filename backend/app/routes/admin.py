"""Admin: platform configuration that drives the engine at runtime."""
from __future__ import annotations

import copy
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import config_store, models
from ..config import settings
from ..db import get_db
from ..llm import client as llm_client
from ..seed.seeder import seed_all, seed_missing
from ._admin_audit import Actor, get_actor, log_change

router = APIRouter()


@router.get("/admin/config")
def get_config(db: Session = Depends(get_db)) -> dict:
    return {
        "config": config_store.all_config(db),
        "meta": config_store.META,
        "defaults": config_store.DEFAULTS,
    }


class ConfigPatch(BaseModel):
    value: Any


@router.put("/admin/config/{key}")
def put_config(key: str, body: ConfigPatch, db: Session = Depends(get_db),
               actor: Actor = Depends(get_actor)) -> dict:
    if key not in config_store.DEFAULTS:
        raise HTTPException(404, f"unknown config key: {key}")
    config_store.set_key(db, key, body.value)
    log_change(db, actor, "config", "update", key, {"value": body.value})
    db.commit()
    return {"key": key, "value": body.value}


@router.post("/admin/config/reset")
def reset_config(db: Session = Depends(get_db), actor: Actor = Depends(get_actor)) -> dict:
    for k, v in config_store.DEFAULTS.items():
        config_store.set_key(db, k, copy.deepcopy(v))
    log_change(db, actor, "config", "reset", "all", {})
    db.commit()
    return {"reset": True}


# --- LLM: live status + a pre-flight connection test ----------------------
@router.get("/admin/llm/status")
def llm_status(db: Session = Depends(get_db)) -> dict:
    llm = config_store.all_config(db).get("llm")
    e = llm_client.effective_llm(llm)
    return {
        "provider": e["provider"],
        "model_default": e["model_default"],
        "model_hard": e["model_hard"],
        "base_url": e["base_url"],
        "active": llm_client.model_version(llm),
        "available": llm_client.llm_available(llm),
        # presence only — keys themselves never leave the server
        "anthropic_key_present": bool(settings.anthropic_api_key),
        "openai_key_present": bool(settings.openai_api_key),
    }


@router.post("/admin/llm/test")
def llm_test(db: Session = Depends(get_db), actor: Actor = Depends(get_actor)) -> dict:
    """Send a tiny structured prompt with the active config to confirm the model
    answers and returns valid structured output — before it codes real charts."""
    import time as _time

    llm = config_store.all_config(db).get("llm")
    schema = {
        "type": "object",
        "properties": {"status": {"type": "string"}, "echo": {"type": "string"}},
        "required": ["status"],
    }
    t0 = _time.time()
    try:
        out = llm_client.complete_json(
            "You are a connectivity check for a medical-coding system.",
            "Reply with status 'ok' and echo the word 'ready'.",
            schema, temperature=0.0, llm=llm,
        )[0]
        ms = int((_time.time() - t0) * 1000)
        log_change(db, actor, "config", "test", "llm", {"model": llm_client.model_version(llm), "ok": True})
        db.commit()
        return {"ok": True, "model": llm_client.model_version(llm), "latency_ms": ms, "sample": out}
    except Exception as exc:
        return {"ok": False, "model": llm_client.model_version(llm), "error": f"{type(exc).__name__}: {exc}"}


# --- Seed endpoint -----------------------------------------------------------

@router.post("/admin/seed")
def trigger_seed(force: bool = False, db: Session = Depends(get_db),
                 actor: Actor = Depends(get_actor)) -> dict:
    """(Re)seed reference data and worklist.

    ?force=false (default): additive — inserts any rows missing from the DB
    without touching existing encounters or coding runs.  Safe to call at any time.

    ?force=true: destructive full reseed — clears all seed-managed tables then
    reloads everything from the seed files.  Existing coding runs are deleted.
    """
    if force:
        result = seed_all(force=True)
    else:
        result = seed_missing()
    log_change(db, actor, "reference", "seed", "all", {"force": force, "result": result})
    db.commit()
    return result


# --- Admin change log (append-only governance trail) -----------------------
@router.get("/admin/audit")
def admin_audit(limit: int = 100, db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(
        select(models.ConfigAudit).order_by(models.ConfigAudit.at.desc()).limit(limit)
    ).all()
    return [
        {"id": r.id, "at": r.at.isoformat(), "actor": r.actor, "role": r.role,
         "area": r.area, "action": r.action, "target": r.target, "detail": r.detail}
        for r in rows
    ]
