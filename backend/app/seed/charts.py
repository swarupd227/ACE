"""Synthetic, PHI-free clinical charts. Real pipeline codes them live — no answers
are stored on the chart. Designed to exercise the four mandatory demo scenarios
(Use-Case §5) plus E&M, payer policy, and the eligibility gate."""
from __future__ import annotations

CHARTS = [
    # 1 — Standard radiology (single study) → expect STB
    dict(
        mrn="RAD10001", patient_name="Jordan Avery", age=58, sex="M", specialty="Radiology",
        modality="XR", payer="Medicare", pos="22", dos="2026-04-12", client="Riverbend Health",
        source_system="PracticeAdmin", report_type="radiology_report",
        scenario="Scenario 1 — Standard radiology (single procedure)",
        chart_text=(
            "RADIOLOGY REPORT\n"
            "EXAM: Chest X-ray, PA and lateral (2 views)\n"
            "HISTORY: 58-year-old male with productive cough and fever for 4 days.\n"
            "TECHNIQUE: Two views of the chest were obtained. No contrast.\n"
            "FINDINGS: There is a focal area of airspace consolidation in the right lower lobe. "
            "No pleural effusion or pneumothorax. Heart size normal.\n"
            "IMPRESSION: Right lower lobe consolidation consistent with pneumonia.\n"
            "Electronically signed by Dr. P. Nair, MD."
        ),
    ),
    # 2 — Multi-procedure: CT abdomen AND pelvis with contrast → expect single 74177 (bundling)
    dict(
        mrn="RAD10002", patient_name="Sam Delgado", age=47, sex="F", specialty="Radiology",
        modality="CT", payer="Medicare", pos="22", dos="2026-04-13", client="Riverbend Health",
        source_system="PracticeAdmin", report_type="radiology_report",
        scenario="Scenario 2 — Multi-procedure (CT abdomen + pelvis)",
        chart_text=(
            "RADIOLOGY REPORT\n"
            "EXAM: CT of the abdomen and pelvis with IV contrast\n"
            "HISTORY: 47-year-old female with generalized abdominal pain.\n"
            "TECHNIQUE: Helical CT images of the abdomen and pelvis were acquired following "
            "intravenous administration of low-osmolar iodinated contrast. Oral contrast also given.\n"
            "FINDINGS: No acute abnormality of the solid organs. No free air or free fluid. "
            "Appendix is normal. No obstructing renal calculus.\n"
            "IMPRESSION: No acute findings to explain generalized abdominal pain.\n"
            "Electronically signed by Dr. L. Osei, MD."
        ),
    ),
    # 3 — Complex/ambiguous: rule-out language, normal findings → avoid overcoding pneumonia
    dict(
        mrn="RAD10003", patient_name="Taylor Brooks", age=34, sex="F", specialty="Radiology",
        modality="XR", payer="Medicare", pos="22", dos="2026-04-14", client="Lakeshore Clinics",
        source_system="eClinicalWorks", report_type="radiology_report",
        scenario="Scenario 3 — Complex diagnosis mapping (avoid overcoding)",
        chart_text=(
            "RADIOLOGY REPORT\n"
            "EXAM: Chest X-ray, single view\n"
            "HISTORY: 34-year-old with persistent dry cough. Rule out pneumonia.\n"
            "TECHNIQUE: Single AP view of the chest.\n"
            "FINDINGS: Lungs are clear. No consolidation, effusion, or pneumothorax. "
            "Cardiomediastinal silhouette is normal.\n"
            "IMPRESSION: No acute cardiopulmonary process. No radiographic evidence of pneumonia.\n"
            "Electronically signed by Dr. R. Kim, MD."
        ),
    ),
    # 4 — Exception: incomplete documentation → eligibility fail → MANUAL
    dict(
        mrn="RAD10004", patient_name="Casey Monroe", age=61, sex="M", specialty="Radiology",
        modality="CT", payer="Cigna", pos="22", dos="2026-04-14", client="Lakeshore Clinics",
        source_system="eClinicalWorks", report_type="radiology_report",
        scenario="Scenario 4 — Exception handling (incomplete documentation)",
        chart_text=(
            "RADIOLOGY REPORT\n"
            "EXAM: CT head\n"
            "HISTORY: Headache.\n"
            "TECHNIQUE: \n"
            "FINDINGS: Report incomplete — images acquired, full dictation to be dictated by "
            "attending radiologist.\n"
            "IMPRESSION: Addendum pending.\n"
        ),
    ),
    # 4b — Exception: interventional radiology → excluded by eligibility
    dict(
        mrn="RAD10005", patient_name="Riley Hassan", age=70, sex="M", specialty="Radiology",
        modality="CT", payer="Medicare", pos="22", dos="2026-04-15", client="Riverbend Health",
        source_system="PracticeAdmin", report_type="radiology_report",
        scenario="Scenario 4 — Exception handling (interventional, out of scope)",
        chart_text=(
            "RADIOLOGY REPORT\n"
            "EXAM: Transarterial chemoembolization of hepatic artery\n"
            "HISTORY: 70-year-old male with hepatocellular carcinoma.\n"
            "TECHNIQUE: Interventional procedure. Right common femoral arterial access obtained. "
            "Selective angiography and embolization of the right hepatic artery performed.\n"
            "IMPRESSION: Successful chemoembolization.\n"
            "Electronically signed by Dr. M. Farah, MD."
        ),
    ),
    # 5 — E&M established; documents 'diabetes' only; meds hint at more → avoid overcoding E11.40
    dict(
        mrn="EM20001", patient_name="Morgan Lee", age=66, sex="F", specialty="E&M",
        modality="", encounter_type="established", payer="Medicare", pos="11", dos="2026-04-16",
        client="Summit Primary Care", source_system="Cerner", report_type="office_note",
        scenario="E&M — established visit, MDM leveling + avoid overcoding",
        chart_text=(
            "OFFICE VISIT NOTE (Established Patient)\n"
            "HPI: 66-year-old female with type 2 diabetes here for follow-up. Reports tingling in "
            "both feet for several weeks. Blood sugars running high at home.\n"
            "ROS: Positive for bilateral foot paresthesia. No chest pain, no shortness of breath.\n"
            "MEDICATIONS: Metformin 1000 mg BID. Lisinopril 10 mg daily.\n"
            "EXAM: Feet with decreased monofilament sensation bilaterally. Otherwise unremarkable.\n"
            "DATA: A1C resulted today at 9.2%.\n"
            "ASSESSMENT/PLAN: 1) Type 2 diabetes mellitus, uncontrolled — increase metformin, "
            "discussed diet. 2) Hypertension — stable, continue lisinopril. Total time 35 minutes.\n"
            "Electronically signed by Dr. S. Patel, MD."
        ),
    ),
    # 6 — MRI lumbar (Anthem prior-auth policy)
    dict(
        mrn="RAD10006", patient_name="Alex Rivera", age=52, sex="M", specialty="Radiology",
        modality="MRI", payer="Anthem", pos="22", dos="2026-04-16", client="Lakeshore Clinics",
        source_system="eClinicalWorks", report_type="radiology_report",
        scenario="Radiology — payer prior-authorization policy (Anthem MRI)",
        chart_text=(
            "RADIOLOGY REPORT\n"
            "EXAM: MRI lumbar spine without contrast\n"
            "HISTORY: 52-year-old male with chronic low back pain for 3 months, radiating to leg.\n"
            "TECHNIQUE: Multiplanar multisequence MRI of the lumbar spine without contrast.\n"
            "FINDINGS: L4-L5 disc bulge with mild central canal narrowing. No fracture.\n"
            "IMPRESSION: L4-L5 degenerative disc disease. Low back pain.\n"
            "Electronically signed by Dr. T. Wells, MD."
        ),
    ),
    # 7 — Knee XR, right knee pain
    dict(
        mrn="RAD10007", patient_name="Jamie Park", age=45, sex="F", specialty="Radiology",
        modality="XR", payer="Medicare", pos="22", dos="2026-04-17", client="Summit Primary Care",
        source_system="Cerner", report_type="radiology_report",
        scenario="Radiology — knee X-ray (laterality + view count)",
        chart_text=(
            "RADIOLOGY REPORT\n"
            "EXAM: Right knee X-ray, 3 views\n"
            "HISTORY: 45-year-old female with right knee pain after a fall.\n"
            "TECHNIQUE: Three views of the right knee were obtained.\n"
            "FINDINGS: No acute fracture or dislocation. Mild medial compartment joint space narrowing. "
            "No effusion.\n"
            "IMPRESSION: No acute fracture. Mild osteoarthritic change, right knee.\n"
            "Electronically signed by Dr. H. Gomez, MD."
        ),
    ),
    # 8 — CT head without contrast, headache (Cigna)
    dict(
        mrn="RAD10008", patient_name="Devin Cole", age=39, sex="M", specialty="Radiology",
        modality="CT", payer="Cigna", pos="22", dos="2026-04-17", client="Riverbend Health",
        source_system="PracticeAdmin", report_type="radiology_report",
        scenario="Radiology — CT head without contrast",
        chart_text=(
            "RADIOLOGY REPORT\n"
            "EXAM: CT head without contrast\n"
            "HISTORY: 39-year-old male with new severe headache.\n"
            "TECHNIQUE: Non-contrast axial CT images of the head.\n"
            "FINDINGS: No acute intracranial hemorrhage, mass effect, or midline shift. "
            "Ventricles normal in size.\n"
            "IMPRESSION: No acute intracranial abnormality. Headache.\n"
            "Electronically signed by Dr. A. Sharma, MD."
        ),
    ),
]


# Frozen golden set (adjudicated truth) for the evaluation harness.
# Independent, realistic full reports (distinct from the worklist charts).
GOLDEN_CASES = [
    dict(specialty="Radiology", irr=0.94, ambiguous=False,
         truth={"icd": ["J18.9"], "cpt": ["71046"]},
         chart_text=(
             "RADIOLOGY REPORT\nEXAM: Chest X-ray, PA and lateral (2 views)\n"
             "HISTORY: Productive cough and fever for several days.\n"
             "TECHNIQUE: Two views of the chest were obtained without contrast.\n"
             "FINDINGS: Focal airspace consolidation in the right lower lobe. No effusion or pneumothorax.\n"
             "IMPRESSION: Right lower lobe consolidation consistent with pneumonia.\n"
             "Electronically signed by attending radiologist.")),
    dict(specialty="Radiology", irr=0.94, ambiguous=False,
         truth={"icd": ["R10.84"], "cpt": ["74177"]},
         chart_text=(
             "RADIOLOGY REPORT\nEXAM: CT of the abdomen and pelvis with IV contrast\n"
             "HISTORY: Generalized abdominal pain.\n"
             "TECHNIQUE: Helical CT of the abdomen and pelvis after intravenous iodinated contrast.\n"
             "FINDINGS: No acute abnormality of the solid organs. No free air or free fluid.\n"
             "IMPRESSION: No acute findings to explain generalized abdominal pain.\n"
             "Electronically signed by attending radiologist.")),
    dict(specialty="Radiology", irr=0.90, ambiguous=True,
         truth={"icd": ["R05.9"], "cpt": ["71045"]},
         chart_text=(
             "RADIOLOGY REPORT\nEXAM: Chest X-ray, single view\n"
             "HISTORY: Persistent dry cough. Rule out pneumonia.\n"
             "TECHNIQUE: Single AP view of the chest.\n"
             "FINDINGS: Lungs are clear. No consolidation, effusion, or pneumothorax.\n"
             "IMPRESSION: No acute cardiopulmonary process. No radiographic evidence of pneumonia.\n"
             "Electronically signed by attending radiologist.")),
    dict(specialty="Radiology", irr=0.95, ambiguous=False,
         truth={"icd": ["M54.50"], "cpt": ["72148"]},
         chart_text=(
             "RADIOLOGY REPORT\nEXAM: MRI lumbar spine without contrast\n"
             "HISTORY: Chronic low back pain for several months radiating to the leg.\n"
             "TECHNIQUE: Multiplanar multisequence MRI of the lumbar spine without contrast.\n"
             "FINDINGS: L4-L5 disc bulge with mild central canal narrowing. No fracture.\n"
             "IMPRESSION: L4-L5 degenerative disc disease. Low back pain.\n"
             "Electronically signed by attending radiologist.")),
    dict(specialty="E&M", irr=0.86, ambiguous=False,
         truth={"icd": ["E11.40", "I10"], "cpt": ["99214"]},
         chart_text=(
             "OFFICE VISIT NOTE (Established Patient)\n"
             "HPI: Type 2 diabetic here for follow-up with bilateral foot tingling for several weeks.\n"
             "MEDICATIONS: Metformin 1000 mg BID. Lisinopril 10 mg daily.\n"
             "EXAM: Decreased monofilament sensation in both feet. Otherwise unremarkable.\n"
             "DATA: A1C resulted today at 9.2%.\n"
             "ASSESSMENT/PLAN: 1) Type 2 diabetes with neuropathy, uncontrolled - adjust therapy. "
             "2) Hypertension - stable. Total time 35 minutes.\nElectronically signed by provider.")),
    dict(specialty="Radiology", irr=0.95, ambiguous=False,
         truth={"icd": ["M25.561"], "cpt": ["73562"]},
         chart_text=(
             "RADIOLOGY REPORT\nEXAM: Right knee X-ray, 3 views\n"
             "HISTORY: Right knee pain after a fall.\n"
             "TECHNIQUE: Three views of the right knee were obtained.\n"
             "FINDINGS: No acute fracture or dislocation. Mild medial compartment joint space narrowing.\n"
             "IMPRESSION: No acute fracture. Mild osteoarthritic change, right knee.\n"
             "Electronically signed by attending radiologist.")),
]
