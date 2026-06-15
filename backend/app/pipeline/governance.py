"""Token & cost governance — active management on top of real token metering.

- cost_usd: translate token counts to dollars at admin-configured per-model rates
  (cache-read tokens are billed at ~10% of input, reflected here).
- spent_today / budget_status: a daily token budget with a warn → throttle →
  route-to-human ladder. The orchestrator consults budget_status before spending:
  exhausted budget routes the chart to a human (the same honest fallback used when
  the model is unavailable — never fabricated codes), throttle disables
  self-consistency to conserve. OFF by default, so nothing changes until an admin
  sets a budget.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select

from .. import models

CACHE_READ_DISCOUNT = 0.10  # cache-read input billed at ~10% of normal input


def _rate(rates: dict, model_version: str, kind: str) -> float:
    mv = (model_version or "").lower()
    for key, r in (rates or {}).items():
        if key != "default" and key in mv:
            return float(r.get(kind, 0.0))
    return float((rates or {}).get("default", {"in": 3.0, "out": 15.0}).get(kind, 0.0))


def cost_usd(rates: dict, model_version: str, in_tok: int, out_tok: int, cache_read: int = 0) -> float:
    return round(
        (in_tok / 1e6) * _rate(rates, model_version, "in")
        + (cache_read / 1e6) * _rate(rates, model_version, "in") * CACHE_READ_DISCOUNT
        + (out_tok / 1e6) * _rate(rates, model_version, "out"),
        4,
    )


def spent_today(db) -> int:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    total = db.execute(
        select(
            func.coalesce(func.sum(models.CodingRun.input_tokens), 0)
            + func.coalesce(func.sum(models.CodingRun.output_tokens), 0)
            + func.coalesce(func.sum(models.CodingRun.cache_read_tokens), 0)
        ).where(models.CodingRun.finished_at >= start)
    ).scalar()
    return int(total or 0)


def budget_status(db, gov: dict) -> dict:
    enabled = bool((gov or {}).get("enabled"))
    budget = int((gov or {}).get("daily_budget_tokens") or 0)
    spent = spent_today(db)
    out = {"enabled": enabled, "budget": budget, "spent": spent,
           "state": "ok", "pct": 0.0, "remaining": None}
    if not enabled or budget <= 0:
        return out
    pct = spent / budget
    out["pct"] = round(pct, 3)
    out["remaining"] = max(0, budget - spent)
    warn = (gov.get("warn_pct") or 70) / 100.0
    throttle = (gov.get("throttle_pct") or 85) / 100.0
    if pct >= 1.0:
        out["state"] = "exhausted"
    elif pct >= throttle:
        out["state"] = "throttle"
    elif pct >= warn:
        out["state"] = "warn"
    return out
