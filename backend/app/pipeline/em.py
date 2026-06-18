"""Stage-6 deterministic Outpatient E&M leveler (the volume engine).

The LLM extracts the medical-decision-making (MDM) factors and total time; this engine DECIDES
the supportable visit level deterministically — the 2-of-3 MDM selection across
(problems, data, risk) and, when documented, total-time — then validates the LLM-assigned visit
code and surfaces over- or under-leveling. Same "LLMs reason, deterministic gates decide"
posture as the DRG / HCC / anesthesia / APC engines.

DEMO posture: the tier→code mapping and the time floors below are illustrative PLACEHOLDERS,
not licensed AMA content — swap the licensed CPT leveling tables for production (the same posture
as ACE's placeholder CPT code tables). The 2-of-3 selection is a methodology, not content.
"""
from __future__ import annotations

# Complexity tiers, ascending.
_TIERS = ["straightforward", "low", "moderate", "high"]
_TIER_ALIASES = {
    "minimal": "straightforward", "none": "straightforward", "straightforward": "straightforward",
    "limited": "low", "low": "low",
    "moderate": "moderate", "mod": "moderate",
    "extensive": "high", "severe": "high", "high": "high",
}
# tier → (established office code, new office code) — DEMO placeholder mapping.
_CODE_BY_TIER = {
    "straightforward": ("99212", "99202"),
    "low": ("99213", "99203"),
    "moderate": ("99214", "99204"),
    "high": ("99215", "99205"),
}
# Illustrative total-time floors in minutes — DEMO placeholders (swap licensed AMA values for prod).
_TIME_FLOOR = {
    "established": [("99215", 40), ("99214", 30), ("99213", 20), ("99212", 10)],
    "new": [("99205", 60), ("99204", 45), ("99203", 30), ("99202", 15)],
}
_OFFICE_CODES = {c for pair in _CODE_BY_TIER.values() for c in pair} | {"99211"}


def _norm_tier(text: str) -> str:
    t = (text or "").strip().lower()
    for key, tier in _TIER_ALIASES.items():
        if key in t:
            return tier
    return "straightforward"


def _rank(tier: str) -> int:
    return _TIERS.index(tier)


def _code_tier(code: str) -> int:
    """Ordinal rank of an office visit code (for over/under-level comparison)."""
    for tier, (est, new) in _CODE_BY_TIER.items():
        if code in (est, new):
            return _rank(tier)
    return 0  # 99211 (nurse visit) ranks lowest


def _mdm_tier(problems: str, data: str, risk: str) -> str:
    """2-of-3 selection: the highest tier met by at least two of the three MDM elements."""
    ranks = sorted([_rank(_norm_tier(problems)), _rank(_norm_tier(data)), _rank(_norm_tier(risk))],
                   reverse=True)
    return _TIERS[ranks[1]]  # the 2nd-highest is met by >= 2 elements


def _time_code(enc_type: str, minutes: int) -> str:
    for code, floor in _TIME_FLOOR.get(enc_type, []):  # descending
        if minutes and minutes >= floor:
            return code
    return ""


def modifier_25(em_factors: dict, accepted_codes: list[dict]) -> dict:
    """Evidence gate for modifier 25 (separately identifiable E&M on a same-day procedure day).

    Applies 25 ONLY when a same-day minor procedure coexists with a separately identifiable E&M
    that the documentation supports; otherwise withholds it (the E&M is bundled into the
    procedure). Withholding when unsupported is the OIG's perennial audit target.
    """
    ef = em_factors or {}
    em_code = next((c["code"] for c in accepted_codes if c.get("code") in _OFFICE_CODES), "")
    # A same-day procedure is evidenced by a coded procedure CPT/HCPCS (authoritative), not the
    # model's free-text flag. Modifier 25 is in scope whenever an E&M and a procedure coexist.
    proc_codes = [c["code"] for c in accepted_codes
                  if c.get("code_system") in ("CPT", "HCPCS")
                  and c.get("code") not in _OFFICE_CODES and c.get("code") != em_code]
    applicable = bool(em_code) and bool(proc_codes)
    if not applicable:
        return {"applicable": False, "action": "n/a", "em_code": em_code, "procedures": proc_codes,
                "reason": "no same-day E&M + procedure pairing"}

    supported = bool(ef.get("separately_identifiable_em"))
    evidence = (ef.get("separate_em_evidence") or "").strip()
    if supported:
        return {"applicable": True, "action": "apply", "supported": True, "em_code": em_code,
                "procedures": proc_codes, "evidence": evidence,
                "reason": "separately identifiable E&M is documented"}
    return {"applicable": True, "action": "withhold", "supported": False, "em_code": em_code,
            "procedures": proc_codes, "evidence": evidence,
            "reason": "no documentation of a separately identifiable E&M — E&M bundled into the procedure"}


def level(em_factors: dict, accepted_codes: list[dict], encounter_type: str = "") -> dict:
    """Deterministically derive the supportable E&M level and validate the coded visit code."""
    ef = em_factors or {}
    enc_raw = (encounter_type or ef.get("encounter_type") or "established").strip().lower()
    enc_type = "new" if "new" in enc_raw else "established"
    coded = next((c["code"] for c in accepted_codes if c.get("code") in _OFFICE_CODES), "")

    trace: list[str] = []
    if not coded:
        return {"resolved": False, "reason": "no office E&M visit code on the chart",
                "encounter_type": enc_type, "trace": trace}

    # MDM path (2-of-3)
    p, d, r = _norm_tier(ef.get("problems")), _norm_tier(ef.get("data_complexity")), _norm_tier(ef.get("risk"))
    mdm_tier = _mdm_tier(ef.get("problems"), ef.get("data_complexity"), ef.get("risk"))
    mdm_code = _CODE_BY_TIER[mdm_tier][0 if enc_type == "established" else 1]
    trace.append(f"MDM 2-of-3 — problems={p}, data={d}, risk={r} → {mdm_tier} → {mdm_code}")

    # Time path (only when time is documented)
    minutes = int(ef.get("total_time_minutes") or 0)
    time_code = _time_code(enc_type, minutes)
    if minutes:
        trace.append(f"Total time {minutes} min → {time_code or 'below level floor'}")

    # Supportable level = the higher of MDM and time (a level is supported by EITHER method).
    candidates = [c for c in (mdm_code, time_code) if c]
    supported = max(candidates, key=_code_tier)
    trace.append(f"Supportable level: {supported} (higher of MDM / time)")

    cr, sr = _code_tier(coded), _code_tier(supported)
    if cr == sr:
        agreement = "confirmed"
    elif cr > sr:
        agreement = "over-leveled"
    else:
        agreement = "under-leveled"
    trace.append(f"Coded {coded} vs supportable {supported} → {agreement}")

    return {
        "resolved": True, "encounter_type": enc_type, "coded_code": coded,
        "mdm_tier": mdm_tier, "mdm_code": mdm_code, "time_minutes": minutes, "time_code": time_code,
        "supported_code": supported, "agreement": agreement, "trace": trace,
    }
