"""Sandbox charts for the Practice Admin connector (E1).

Synthetic, PHI-free notes used ONLY in sandbox mode to exercise the inbound pull before the
real Practice Admin API exists. MVP specialties only: E&M, ED, Radiology (Amrish's priority).
The live connector returns real charts instead; nothing here ships to production.
"""
from __future__ import annotations

# Each entry mirrors what a Practice Admin "new chart" record would carry.
SANDBOX_CHARTS: list[dict] = [
    {
        "external_id": "PA-EM-1007",
        "specialty": "E&M", "modality": "Established Patient", "payer": "BCBS", "pos": "11",
        "patient_name": "Sandbox Patient A", "age": 58, "sex": "F", "dos": "2026-06-24",
        "text": (
            "OFFICE VISIT — ESTABLISHED PATIENT\n"
            "CC: Follow-up of type 2 diabetes and hypertension.\n"
            "HPI: 58F, both conditions stable on current therapy; reports good home glucose logs.\n"
            "EXAM: BP 132/80. No acute distress.\n"
            "ASSESSMENT/PLAN: (1) Type 2 diabetes without complication — continue metformin, A1c ordered. "
            "(2) Essential hypertension — continue lisinopril. Two stable chronic problems; prescription "
            "drug management. Total time 25 minutes.\n"
            "Electronically signed by J. Okafor, MD."
        ),
    },
    {
        "external_id": "PA-ED-2042",
        "specialty": "ED", "modality": "Level 3", "payer": "BCBS", "pos": "23",
        "patient_name": "Sandbox Patient B", "age": 41, "sex": "M", "dos": "2026-06-25",
        "text": (
            "EMERGENCY DEPARTMENT NOTE\n"
            "CC: Right ankle injury after a fall.\n"
            "HPI: 41M twisted right ankle stepping off a curb; able to bear weight with pain.\n"
            "EXAM: Lateral malleolus tenderness, mild swelling, no deformity, neurovascularly intact.\n"
            "MDM: X-ray ordered and reviewed — no fracture. Ankle sprain.\n"
            "PLAN: RICE, ankle brace, NSAIDs, return precautions. Discharged.\n"
            "Electronically signed by R. Mehta, MD."
        ),
    },
    {
        "external_id": "PA-RAD-3091",
        "specialty": "Radiology", "modality": "XR", "payer": "BCBS", "pos": "22",
        "patient_name": "Sandbox Patient C", "age": 63, "sex": "F", "dos": "2026-06-25",
        "text": (
            "RADIOLOGY REPORT\n"
            "EXAM: Chest X-ray, 2 views (PA and lateral).\n"
            "HISTORY: Cough.\n"
            "FINDINGS: Lungs clear. No focal consolidation, effusion, or pneumothorax. "
            "Heart size normal. No acute osseous abnormality.\n"
            "IMPRESSION: No acute cardiopulmonary process.\n"
            "Electronically signed by A. Reyes, MD."
        ),
    },
]
