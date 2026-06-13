"""Synthetic 835 remittance data for Phase 2 (Denial Pattern Discovery).

Deterministic (seeded) and PHI-free. Three denial patterns are deliberately embedded so the
statistical detectors have real signal to find — nothing is hand-labelled, the detectors must
re-derive them from the rows:
  * SPIKE      — CPT 72148 (lumbar MRI), CARC 197 (auth missing): low baseline, jumps in the
                 last 30 days  → should propose a PRIOR_AUTH rule.
  * PERSISTENT — CPT 45378 (colonoscopy), CARC 16 (missing documentation): high throughout
                 → should propose a DOCUMENTATION rule.
  * EMERGING   — CPT 72131 (CT lumbar), CARC 11 (dx inconsistent): rising coverage denials
                 → should propose a COVERAGE rule.
Background codes carry only low, flat denial noise so the signals stand out.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

ANCHOR = date(2026, 6, 1)   # latest service date; fixed for reproducibility
DAYS = 90                   # window depth
RECENT_WINDOW = 30          # "recent" = last 30 days

PAYER = "Meridian Health Plan"

# CARC reference (public X12 code list) used in the synthetic data.
CARC_REASON = {
    "197": "Precertification/authorization absent",
    "16": "Claim lacks information or has submission/billing error",
    "11": "Diagnosis inconsistent with the procedure",
    "50": "Non-covered; not deemed a medical necessity",
    "151": "Payment adjusted; information does not support this many services",
}

# (code, billed, daily_volume, baseline_rate, recent_rate, carc)
_CODES = [
    ("72148", 1200.0, 6, 0.05, 0.46, "197"),  # SPIKE  -> PRIOR_AUTH
    ("45378", 900.0, 7, 0.31, 0.31, "16"),    # PERSISTENT -> DOCUMENTATION
    ("72131", 1100.0, 5, 0.07, 0.27, "11"),   # EMERGING -> COVERAGE
    ("93306", 700.0, 6, 0.03, 0.03, "16"),    # background noise
    ("99213", 150.0, 9, 0.02, 0.02, "16"),    # background noise
]


def generate() -> list[dict]:
    rng = random.Random(42)
    rows: list[dict] = []
    cid = 0
    for d in range(DAYS):
        svc = ANCHOR - timedelta(days=(DAYS - 1 - d))
        recent = (DAYS - 1 - d) < RECENT_WINDOW
        for code, billed, vol, base_rate, recent_rate, carc in _CODES:
            rate = recent_rate if recent else base_rate
            for _ in range(vol):
                cid += 1
                denied = rng.random() < rate
                rows.append({
                    "payer": PAYER,
                    "claim_id": f"CLM{cid:06d}",
                    "procedure_code": code,
                    "denied": denied,
                    "denial_carc": carc if denied else "",
                    "denial_rarc": "",
                    "denial_reason": CARC_REASON[carc] if denied else "",
                    "billed_amount": billed,
                    "paid_amount": 0.0 if denied else round(billed * 0.8, 2),
                    "service_date": svc.isoformat(),
                })
    return rows
