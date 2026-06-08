"""Prompts and structured-output schemas for the reasoning agents.

Two LLM round-trips per chart (keeps demo latency sane while staying real):
  A) ANALYSIS  — document conditioning + summarization + structured entity extraction
  B) CODING    — cited code candidates with per-code confidence and guideline references
Stage 3b (citation verification), Stage 4 (validation gates) and Stage 5
(calibration/routing) are deterministic and live outside the model.
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# A) ANALYSIS
# ---------------------------------------------------------------------------
ANALYSIS_SYSTEM = """You are a clinical documentation analyst supporting a medical-coding pipeline.
You read a single clinical chart and produce a STRUCTURED analysis. You never invent
content that is not present in the chart. When a fact is absent, say so explicitly.
You are precise about laterality, contrast, view counts, encounter type, negation
("rule out X" is NOT X), and temporality ("history of" is not an active condition)."""

ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string", "description": "3-5 sentence coder-facing summary of the encounter."},
        "sections": {
            "type": "array",
            "description": "Identified chart sections.",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "line_start": {"type": "integer"},
                    "line_end": {"type": "integer"},
                },
                "required": ["name", "line_start", "line_end"],
            },
        },
        "conditioning_flags": {
            "type": "array",
            "description": "Quality/compliance flags: copy_forward, contradiction, unsigned, addendum, ocr_artifact, missing_documentation, ambiguous.",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "detail": {"type": "string"},
                    "severity": {"type": "string", "enum": ["info", "warn", "block"]},
                },
                "required": ["type", "detail", "severity"],
            },
        },
        "diagnoses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "status": {"type": "string", "enum": ["confirmed", "suspected", "ruled_out", "history"]},
                    "laterality": {"type": "string"},
                    "acuity": {"type": "string"},
                    "line_start": {"type": "integer"},
                    "line_end": {"type": "integer"},
                },
                "required": ["text", "status", "line_start", "line_end"],
            },
        },
        "procedures": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "modality": {"type": "string", "description": "XR/CT/MRI/US or '' for E&M"},
                    "anatomy": {"type": "string"},
                    "laterality": {"type": "string"},
                    "contrast": {"type": "string", "enum": ["with", "without", "with_and_without", "n/a", "unknown"]},
                    "views": {"type": "integer"},
                    "line_start": {"type": "integer"},
                    "line_end": {"type": "integer"},
                },
                "required": ["text", "modality", "anatomy", "contrast", "line_start", "line_end"],
            },
        },
        "em_factors": {
            "type": "object",
            "description": "E&M leveling factors; use zeros/empty for radiology.",
            "properties": {
                "encounter_type": {"type": "string"},
                "problems": {"type": "string"},
                "data_complexity": {"type": "string"},
                "risk": {"type": "string"},
                "total_time_minutes": {"type": "integer"},
                "separate_procedure_same_day": {"type": "boolean"},
            },
            "required": ["encounter_type", "problems", "data_complexity", "risk", "total_time_minutes", "separate_procedure_same_day"],
        },
    },
    "required": ["summary", "sections", "conditioning_flags", "diagnoses", "procedures", "em_factors"],
}


def build_analysis_user(numbered_chart: str, specialty: str) -> str:
    return (
        f"SPECIALTY: {specialty}\n\n"
        "Analyze the following chart. Line numbers are prefixed as 'N|'. "
        "Cite line numbers exactly as shown. Do not code yet.\n\n"
        f"=== CHART ===\n{numbered_chart}\n=== END CHART ==="
    )


# ---------------------------------------------------------------------------
# B) CODING
# ---------------------------------------------------------------------------
CODING_SYSTEM = """You are a certified medical coder (AAPC/AHIMA-level) assigning billable codes.
HARD RULES:
- Assign ONLY codes that the documentation supports. Never assert specificity the chart
  does not contain (no upcoding). If documentation is insufficient, choose the less-specific
  supported code or omit it and explain.
- EVERY code MUST include at least one chart citation (section + exact line range) AND a
  guideline reference. If you cannot cite, do not emit the code.
- Use ONLY codes that appear in the provided CANDIDATE REFERENCE context. Do not invent codes.
- Respect the retrieved payer policy and NCCI/MUE notes provided.
- Provide an honest self-confidence in [0,1] per code and a one-line rule justification.
You will be told the specialty. Output diagnoses (ICD-10-CM) and procedures (CPT/HCPCS)
with modifiers where the documentation supports them."""

CODING_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "codes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code_system": {"type": "string", "enum": ["ICD10CM", "CPT", "HCPCS"]},
                    "code": {"type": "string"},
                    "description": {"type": "string"},
                    "role": {"type": "string", "enum": ["principal", "primary", "secondary", "procedure"]},
                    "modifiers": {"type": "array", "items": {"type": "string"}},
                    "sequence": {"type": "integer"},
                    "confidence": {"type": "number"},
                    "chart_citations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "section": {"type": "string"},
                                "line_start": {"type": "integer"},
                                "line_end": {"type": "integer"},
                                "text": {"type": "string"},
                            },
                            "required": ["section", "line_start", "line_end", "text"],
                        },
                    },
                    "guideline_citations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source": {"type": "string"},
                                "section": {"type": "string"},
                                "text": {"type": "string"},
                            },
                            "required": ["source", "section", "text"],
                        },
                    },
                    "rule_justification": {"type": "string"},
                },
                "required": [
                    "code_system", "code", "description", "role", "modifiers", "sequence",
                    "confidence", "chart_citations", "guideline_citations", "rule_justification",
                ],
            },
        },
        "notes": {"type": "string", "description": "Any coding caveats, overcoding risks avoided, or documentation gaps."},
    },
    "required": ["codes", "notes"],
}


SPECIALTY_GUIDANCE = {
    "Radiology": (
        "RADIOLOGY RULES:\n"
        "- Choose the CPT matching the documented MODALITY and CONTRAST: with vs without vs "
        "without-then-with. Oral/rectal contrast alone counts as WITHOUT contrast.\n"
        "- Choose the CPT matching the documented number of VIEWS; never exceed documented views.\n"
        "- When the study is performed at a facility (POS 22 outpatient hospital, 23 ER), append "
        "modifier 26 (professional component) to the imaging CPT — you are coding the radiologist's read.\n"
        "- For unilateral extremity studies, append RT or LT when laterality is documented.\n"
        "- Use a single COMBINATION code when one exists (e.g., CT abdomen+pelvis); do not unbundle.\n"
        "- Link to the ordering indication; if no definitive diagnosis, code the sign/symptom."
    ),
    "E&M": (
        "E&M RULES:\n"
        "- Assign the visit-level CPT (established 99213-99215 / new 99203-99205) from the documented "
        "MDM or total time. Do not infer a higher level than documented.\n"
        "- Code all conditions addressed; use combination codes (e.g., diabetes WITH a complication) "
        "only when the link is documented."
    ),
    "ED": (
        "ED RULES:\n"
        "- Assign the ED E&M level (99281-99285) from documented MDM.\n"
        "- Use critical care (99291; +99292 each additional 30 min) ONLY when >=30 minutes of critical "
        "care AND a high-acuity, life-threatening condition are documented.\n"
        "- If a separately identifiable E&M is performed with a same-day procedure, consider modifier 25."
    ),
    "Pathology": (
        "PATHOLOGY RULES:\n"
        "- Assign the surgical pathology CPT (88300-88309) by SPECIMEN type and COMPLEXITY level; a skin "
        "lesion examined microscopically is typically level IV (88305).\n"
        "- Append modifier 26 (professional component) for the pathologist's interpretation at a facility.\n"
        "- Code the diagnosis from the microscopic/final diagnosis, not the clinical history."
    ),
    "Surgical": (
        "SURGICAL RULES:\n"
        "- Assign the CPT for the procedure actually performed (operative note).\n"
        "- Apply modifiers when supported: 51 multiple procedures, 59 distinct service, 78/79 return to "
        "OR, 50/RT/LT laterality, 80/82/AS assistant surgeon, 58 staged.\n"
        "- Honor the global package and add-on-code rules; do not unbundle. Code the post-op diagnosis."
    ),
}


# ---------------------------------------------------------------------------
# C) CDI — physician query drafting
# ---------------------------------------------------------------------------
CDI_SYSTEM = """You are a Clinical Documentation Integrity (CDI) specialist. Given a chart and the codes
assigned to it, identify places where the clinical indicators suggest a MORE SPECIFIC or higher-acuity
code, but the documentation does not yet support it. For each, draft a COMPLIANT, NON-LEADING physician
query.

COMPLIANCE RULES (critical):
- Do NOT lead the physician to a specific answer.
- Present multiple clinically reasonable options AND always include "Unable to determine".
- State the objective clinical indicators (labs, meds, findings) that prompted the query.
- Only raise a query when there is a GENUINE, defensible documentation gap. If documentation is already
  sufficient and specific, return an empty list. Do not manufacture queries."""

CDI_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "queries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The non-leading question to the physician."},
                    "clinical_indicators": {"type": "string", "description": "Objective findings prompting the query."},
                    "options": {"type": "array", "items": {"type": "string"},
                                "description": "Reasonable options; MUST include 'Unable to determine'."},
                    "target": {"type": "string", "description": "What is being clarified (e.g., 'anemia type')."},
                    "potential_codes": {"type": "array", "items": {"type": "string"},
                                        "description": "Codes that could apply depending on the answer."},
                    "rationale": {"type": "string", "description": "Why this matters (specificity/acuity/revenue/compliance)."},
                },
                "required": ["question", "clinical_indicators", "options", "target", "potential_codes", "rationale"],
            },
        }
    },
    "required": ["queries"],
}


def build_cdi_user(numbered_chart: str, specialty: str, codes: list[dict]) -> str:
    import json

    code_lines = "\n".join(f"- {c['code_system']} {c['code']} ({c['role']}): {c['description']}" for c in codes)
    return (
        f"SPECIALTY: {specialty}\n\n"
        "CODES ASSIGNED:\n" + (code_lines or "(none)") + "\n\n"
        "Review the chart for documentation gaps and draft compliant, non-leading queries (or return "
        "an empty list if documentation is sufficient).\n\n"
        f"=== CHART (N| line numbers) ===\n{numbered_chart}\n=== END CHART ==="
    )


def build_coding_user(numbered_chart: str, specialty: str, analysis: dict, rag_context: str) -> str:
    import json

    return (
        f"SPECIALTY: {specialty}\n\n"
        + SPECIALTY_GUIDANCE.get(specialty, "") + "\n\n"
        "PRIOR ANALYSIS (entities, flags):\n" + json.dumps(analysis, indent=2) + "\n\n"
        "RETRIEVED CONTEXT — candidate reference codes, guideline excerpts, payer policy, "
        "NCCI/MUE notes, and any learned corrections. Use ONLY codes listed here:\n"
        f"{rag_context}\n\n"
        "Now assign the billable codes with citations and confidence.\n\n"
        f"=== CHART (N| line numbers) ===\n{numbered_chart}\n=== END CHART ==="
    )
