"""Stage-1 privacy guard — pre-model PII masking.

Masks DIRECT identifiers that carry no coding value (patient name, MRN, DOB,
SSN, phone) from the document text before ANY model call. Age, sex, dates of
service and the clinical narrative are deliberately KEPT — they are exactly
what correct coding needs (our sex/age gates validate codes against them).

Properties that matter:
- Line-preserving: replacements never add or remove lines, so the model's
  line-number citations still align with the original chart shown to coders.
- Deterministic and inspectable: plain regex + the encounter's own known
  name/MRN — no model involvement in the redaction itself.
- Demo-grade patterns by design. Production swaps in a clinical
  de-identification service (Azure Health Data Services de-id / Presidio)
  behind this same hook; the pipeline contract is unchanged.
"""
from __future__ import annotations

import re

# Labeled fields: value stops at a separator (· | , ; newline) or the next
# known label, so "PATIENT: Jane Doe MRN: 123" doesn't swallow the MRN.
_STOP = r"(?:(?!\s*\b(?:MRN|DOB|SSN|PHONE|SEX|AGE|DOS)\b)[^·|,;\n])+"
_LABELED = [
    ("name", re.compile(r"(?i)\b(patient(?:\s+name)?|pt\s+name)\s*[:#]\s*(" + _STOP + ")")),
    ("mrn", re.compile(r"(?i)\b(MRN)\s*[:#]?\s*([A-Za-z0-9\-]{3,})")),
    ("dob", re.compile(r"(?i)\b(DOB|date\s+of\s+birth)\s*[:#]?\s*([0-9][0-9/.\-]{5,9})")),
]
_BARE = [
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("phone", re.compile(r"\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b")),
]


def mask_identifiers(text: str, known_name: str = "", known_mrn: str = "") -> tuple[str, list[dict]]:
    """Returns (masked_text, findings) where findings = [{type, count}, ...].
    Masked text is what goes to the model; the stored chart is untouched."""
    counts: dict[str, int] = {}

    def bump(kind: str, n: int) -> None:
        if n:
            counts[kind] = counts.get(kind, 0) + n

    out = text
    for kind, rx in _LABELED:
        out, n = rx.subn(lambda m, k=kind: f"{m.group(1)}: [masked-{k}]", out)
        bump(kind, n)
    # The encounter's own demographics, wherever they appear in the narrative.
    if known_name and len(known_name.strip()) >= 4:
        out, n = re.subn(re.escape(known_name.strip()), "[masked-name]", out, flags=re.IGNORECASE)
        bump("name", n)
    if known_mrn and len(known_mrn.strip()) >= 4:
        out, n = re.subn(re.escape(known_mrn.strip()), "[masked-mrn]", out)
        bump("mrn", n)
    for kind, rx in _BARE:
        out, n = rx.subn(f"[masked-{kind}]", out)
        bump(kind, n)

    findings = [{"type": k, "count": v} for k, v in sorted(counts.items())]
    return out, findings


def summary(findings: list[dict]) -> str:
    if not findings:
        return "no direct identifiers found in the document text — nothing to mask"
    parts = ", ".join(f"{f['type']} ×{f['count']}" for f in findings)
    total = sum(f["count"] for f in findings)
    return (f"masked {total} direct identifier(s) before any model call — {parts} "
            "(age, sex and dates of service kept — coding needs them)")
