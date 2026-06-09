"""Shared helpers for the admin change-log: an actor dependency (read from the
X-Actor / X-Role headers the frontend sends from the active role) and a
log_change() that appends a ConfigAudit row. The caller's existing db.commit()
persists it (log_change only adds to the session)."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header
from sqlalchemy.orm import Session

from .. import models


@dataclass
class Actor:
    name: str
    role: str


def get_actor(
    x_actor: str = Header(default="system", alias="X-Actor"),
    x_role: str = Header(default="", alias="X-Role"),
) -> Actor:
    return Actor(name=x_actor or "system", role=x_role or "")


def log_change(db: Session, actor: Actor, area: str, action: str,
               target: str = "", detail: dict | None = None) -> None:
    db.add(models.ConfigAudit(
        actor=actor.name, role=actor.role, area=area, action=action,
        target=target, detail=detail or {},
    ))
