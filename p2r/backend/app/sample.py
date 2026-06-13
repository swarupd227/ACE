"""A synthetic, public-CMS-style payer medical policy for the demo (PHI-free).
Multiple provision types in one document so ingestion surfaces several at once."""

SAMPLE_PAYER = "Meridian Health Plan"
SAMPLE_TITLE = "Medical Policy: Advanced Imaging of the Lumbar Spine (MRI/CT)"
SAMPLE_POLICY = """MEDICAL POLICY — ADVANCED IMAGING OF THE LUMBAR SPINE
Policy Number: RAD-014    Line of Business: Commercial, Medicare Advantage
Effective Date: 2026-01-01    Last Reviewed: 2025-11-15

COVERAGE
MRI of the lumbar spine without contrast (72148) is considered medically necessary for
low back pain (M54.5x) that has persisted beyond six weeks despite conservative therapy,
or when red-flag findings (suspected malignancy, infection, or cauda equina) are documented.

PRIOR AUTHORIZATION
Prior authorization is required for outpatient lumbar spine MRI (72148) and CT (72131,
72132) for non-emergent indications. Authorization is not required when ordered from the
emergency department.

FREQUENCY
Repeat lumbar MRI within 12 months of a prior study is not covered unless there is a
documented significant change in clinical status.

MODIFIER
When only the professional interpretation is provided at a facility, append modifier 26.
Modifier 50 is not applicable to spine imaging codes.

DOCUMENTATION
The order must document the duration of symptoms, prior conservative treatment, and the
clinical indication. Absent this documentation the service is denied as not medically necessary.

BUNDLING
CT lumbar spine without contrast (72131) is not separately reportable with CT of the
abdomen and pelvis performed in the same session.

Electronically published by the Meridian Health Plan Medical Policy Committee.
"""

# Existing deployed rules to reconcile candidates against (read-only library).
# Deliberately overlaps the sample policy so reconciliation surfaces a mix of verdicts:
#   PA rule covers only 72148 (policy adds CT 72131/72132 → UPDATE);
#   frequency rule says 6 months (policy says 12 → CONFLICT/UPDATE);
#   modifier-26 rule exists (policy adds the '50 not applicable' clause → UPDATE/DUPLICATE);
#   no coverage/documentation/bundling rules exist yet → NET_NEW.
RULE_LIBRARY_SEED = [
    ("RULE-LUM-PA", "Meridian Health Plan",
     "Prior authorization required for outpatient lumbar spine MRI (72148).", {"cpt": ["72148"]}),
    ("RULE-LUM-FREQ", "Meridian Health Plan",
     "Repeat lumbar spine MRI within 6 months of a prior study is not covered.", {"cpt": ["72148"]}),
    ("RULE-LUM-MOD26", "Meridian Health Plan",
     "Append modifier 26 for the professional component of facility spine imaging reads.",
     {"cpt": ["72148"], "modifiers": ["26"]}),
]
