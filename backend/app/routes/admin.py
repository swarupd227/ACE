"""Admin: platform configuration that drives the engine at runtime."""
from __future__ import annotations

import copy
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import config_store
from ..db import get_db

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
def put_config(key: str, body: ConfigPatch, db: Session = Depends(get_db)) -> dict:
    if key not in config_store.DEFAULTS:
        raise HTTPException(404, f"unknown config key: {key}")
    config_store.set_key(db, key, body.value)
    return {"key": key, "value": body.value}


@router.post("/admin/config/reset")
def reset_config(db: Session = Depends(get_db)) -> dict:
    for k, v in config_store.DEFAULTS.items():
        config_store.set_key(db, k, copy.deepcopy(v))
    return {"reset": True}
