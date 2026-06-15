"""Stage-5 fitted confidence calibration.

The spec's position: a model saying "95% confident" is not the same as "correct
95% of the time" — so the raw blended confidence is a FEATURE, and routing runs
on a calibrated value fitted from real outcomes:

- training data: eval-harness outcomes (raw confidence vs adjudicated
  correctness per golden case) plus coder feedback on production charts
  (an accept = correct, an override = incorrect)
- fit: isotonic regression via pool-adjacent-violators (monotone, distribution-
  free — the spec's named method for non-uniform miscalibration), per specialty
  with a global '__all__' fallback
- apply: with SAMPLE-SIZE SHRINKAGE toward the raw value
  (lambda = n / (n + K)) — at demo sample sizes the curve barely moves a score;
  at production volumes it converges to the measured curve. Honest by
  construction: sparse data cannot fabricate confidence.

No curve fitted yet -> the raw blend is used unchanged and the trace says so.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .. import models

MIN_SPECIALTY_SAMPLES = 5
MIN_GLOBAL_SAMPLES = 10
SHRINKAGE_K = 25  # samples needed before the fitted curve carries half the weight


def fit_isotonic(samples: list[tuple[float, int]]) -> list[dict]:
    """Pool-adjacent-violators over (raw_confidence, correct01), sorted by raw.
    Returns monotone blocks [{x_min, x_max, y, n}]."""
    if not samples:
        return []
    merged: list[dict] = []
    for x, y in sorted(samples):
        merged.append({"sum": float(y), "n": 1, "x_min": x, "x_max": x})
        while len(merged) >= 2 and (merged[-2]["sum"] / merged[-2]["n"]) > (merged[-1]["sum"] / merged[-1]["n"]):
            b2, b1 = merged.pop(), merged.pop()
            merged.append({"sum": b1["sum"] + b2["sum"], "n": b1["n"] + b2["n"],
                           "x_min": b1["x_min"], "x_max": b2["x_max"]})
    return [{"x_min": round(b["x_min"], 4), "x_max": round(b["x_max"], 4),
             "y": round(b["sum"] / b["n"], 4), "n": b["n"]} for b in merged]


def eval_curve(points: list[dict], x: float) -> float:
    """Evaluate the PAV step function at x (linear between block midpoints)."""
    if not points:
        return x
    if x <= points[0]["x_min"]:
        return points[0]["y"]
    if x >= points[-1]["x_max"]:
        return points[-1]["y"]
    for i, b in enumerate(points):
        if b["x_min"] <= x <= b["x_max"]:
            return b["y"]
        nxt = points[i + 1] if i + 1 < len(points) else None
        if nxt and b["x_max"] < x < nxt["x_min"]:
            span = nxt["x_min"] - b["x_max"]
            t = (x - b["x_max"]) / span if span > 0 else 0.0
            return b["y"] + t * (nxt["y"] - b["y"])
    return x


def _feedback_samples(db: Session) -> dict[str, list[tuple[float, int]]]:
    """Coder feedback on real charts: accepted code = correct, overridden = not."""
    out: dict[str, list[tuple[float, int]]] = {}
    rows = db.execute(
        select(models.CodeResult.confidence, models.CodeResult.is_overridden,
               models.CodeResult.accepted_by, models.Encounter.specialty)
        .join(models.CodingRun, models.CodeResult.run_id == models.CodingRun.id)
        .join(models.Encounter, models.CodingRun.encounter_id == models.Encounter.id)
        .where((models.CodeResult.is_overridden == True)  # noqa: E712
               | (models.CodeResult.accepted_by != ""))
    ).all()
    for conf, overridden, _accepted, spec in rows:
        out.setdefault(spec, []).append((float(conf), 0 if overridden else 1))
    return out


def fit_all(db: Session) -> dict:
    """Fit per-specialty curves (+ the global fallback) from eval outcomes and
    coder feedback. Replaces previously fitted curves."""
    by_spec: dict[str, list[tuple[float, int]]] = {}
    for o in db.scalars(select(models.EvalOutcome)).all():
        by_spec.setdefault(o.specialty, []).append((float(o.confidence), 1 if o.correct else 0))
    for spec, rows in _feedback_samples(db).items():
        by_spec.setdefault(spec, []).extend(rows)

    db.execute(delete(models.CalibrationCurve))
    fitted: dict[str, dict] = {}
    all_samples: list[tuple[float, int]] = []
    for spec, rows in by_spec.items():
        all_samples.extend(rows)
        if len(rows) >= MIN_SPECIALTY_SAMPLES:
            pts = fit_isotonic(rows)
            db.add(models.CalibrationCurve(
                specialty=spec, points=pts, samples=len(rows),
                positives=sum(y for _, y in rows), fitted_at=datetime.now(timezone.utc)))
            fitted[spec] = {"samples": len(rows), "blocks": len(pts)}
    if len(all_samples) >= MIN_GLOBAL_SAMPLES:
        pts = fit_isotonic(all_samples)
        db.add(models.CalibrationCurve(
            specialty="__all__", points=pts, samples=len(all_samples),
            positives=sum(y for _, y in all_samples), fitted_at=datetime.now(timezone.utc)))
        fitted["__all__"] = {"samples": len(all_samples), "blocks": len(pts)}
    db.commit()
    return fitted


def apply(db: Session, specialty: str, raw: float) -> tuple[float, dict]:
    """Calibrate a raw blended confidence. Identity (honestly traced) when no
    curve has been fitted yet."""
    curve = db.scalars(
        select(models.CalibrationCurve).where(models.CalibrationCurve.specialty == specialty)
    ).first() or db.scalars(
        select(models.CalibrationCurve).where(models.CalibrationCurve.specialty == "__all__")
    ).first()
    if curve is None:
        return raw, {"fitted": False,
                     "detail": "no calibration curve fitted yet — raw blend used (run the eval harness to fit)"}
    iso = eval_curve(curve.points or [], raw)
    lam = curve.samples / (curve.samples + SHRINKAGE_K)
    value = round(min(1.0, max(0.0, lam * iso + (1 - lam) * raw)), 3)
    return value, {"fitted": True, "source": curve.specialty, "samples": curve.samples,
                   "raw": round(raw, 3), "isotonic": round(iso, 3),
                   "shrinkage_weight": round(lam, 2)}
