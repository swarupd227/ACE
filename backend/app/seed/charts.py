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
    # 9 — ED standard visit → expect STB (99284)
    dict(
        mrn="ED30001", patient_name="Pat Sullivan", age=54, sex="M", specialty="ED",
        modality="", encounter_type="ed", payer="Medicare", pos="23", dos="2026-04-18",
        client="Riverbend Health", source_system="Cerner", report_type="ed_note",
        scenario="ED — standard visit (MDM leveling)",
        chart_text=(
            "EMERGENCY DEPARTMENT NOTE\n"
            "CHIEF COMPLAINT: Chest pain.\n"
            "HPI: 54-year-old male with hypertension and hyperlipidemia presenting with 2 hours of "
            "substernal chest pain. Multiple comorbidities reviewed.\n"
            "ROS: Cardiovascular and respiratory systems reviewed; no diaphoresis.\n"
            "EXAM: Vitals stable. Heart regular, lungs clear.\n"
            "DATA/MDM: Independent interpretation of ECG (no acute ischemia). Ordered and reviewed "
            "troponin, CBC, CMP, and chest X-ray. Acute illness with systemic symptoms; moderate risk "
            "of morbidity. Decision for prescription management; shared decision-making for discharge. "
            "High medical decision making.\n"
            "DISPOSITION: Discharged with outpatient cardiology follow-up.\n"
            "Electronically signed by Dr. K. Owens, MD."
        ),
    ),
    # 10 — ED critical care → bounded autonomy → QA (99291)
    dict(
        mrn="ED30002", patient_name="Robin Walsh", age=68, sex="F", specialty="ED",
        modality="", encounter_type="ed", payer="Medicare", pos="23", dos="2026-04-18",
        client="Riverbend Health", source_system="Cerner", report_type="ed_note",
        scenario="ED — critical care (bounded autonomy → QA)",
        chart_text=(
            "EMERGENCY DEPARTMENT NOTE\n"
            "CHIEF COMPLAINT: Severe shortness of breath.\n"
            "HPI: 68-year-old female with acute respiratory distress, hypoxic to 84% on room air.\n"
            "EXAM: Tachypneic, accessory muscle use, diffuse crackles.\n"
            "MDM: Acute respiratory failure with hypoxia. High probability of imminent deterioration. "
            "BiPAP initiated, continuous bedside management.\n"
            "CRITICAL CARE TIME: 60 minutes of critical care provided, exclusive of separately "
            "reportable procedures.\n"
            "DISPOSITION: Admitted to ICU.\n"
            "Electronically signed by Dr. K. Owens, MD."
        ),
    ),
    # 11 & 12 — learning-loop pair (same study/anatomy → an override on A transfers to B)
    dict(
        mrn="RAD10009", patient_name="Lee Carter", age=60, sex="M", specialty="Radiology",
        modality="XR", payer="Medicare", pos="22", dos="2026-04-18", client="Lakeshore Clinics",
        source_system="eClinicalWorks", report_type="radiology_report",
        scenario="Radiology — learning loop A (apply a client-specific override here)",
        chart_text=(
            "RADIOLOGY REPORT\n"
            "EXAM: Abdomen X-ray, single view\n"
            "HISTORY: Abdominal pain.\n"
            "TECHNIQUE: Single supine view of the abdomen.\n"
            "FINDINGS: Nonspecific bowel gas pattern. No free air or obstruction.\n"
            "IMPRESSION: No acute abnormality.\n"
            "Electronically signed by Dr. N. Ito, MD."
        ),
    ),
    dict(
        mrn="RAD10010", patient_name="Dana Fox", age=58, sex="F", specialty="Radiology",
        modality="XR", payer="Medicare", pos="22", dos="2026-04-19", client="Lakeshore Clinics",
        source_system="eClinicalWorks", report_type="radiology_report",
        scenario="Radiology — learning loop B (re-code after A's override to see it adopted)",
        chart_text=(
            "RADIOLOGY REPORT\n"
            "EXAM: Abdomen X-ray, single view\n"
            "HISTORY: Abdominal pain.\n"
            "TECHNIQUE: Single supine view of the abdomen.\n"
            "FINDINGS: Nonspecific bowel gas pattern. No obstruction or free air.\n"
            "IMPRESSION: No acute abnormality.\n"
            "Electronically signed by Dr. N. Ito, MD."
        ),
    ),
    # 13 — E&M with a CDI physician-query opportunity (anemia specificity not documented)
    dict(
        mrn="EM20002", patient_name="Frances Doyle", age=72, sex="F", specialty="E&M",
        modality="", encounter_type="established", payer="Medicare", pos="11", dos="2026-04-19",
        client="Summit Primary Care", source_system="Cerner", report_type="office_note",
        scenario="E&M — CDI physician-query opportunity (anemia type not specified)",
        chart_text=(
            "OFFICE VISIT NOTE (Established Patient)\n"
            "HPI: 72-year-old female with several weeks of fatigue and unintentional weight loss.\n"
            "ROS: Fatigue, decreased appetite. No overt bleeding reported.\n"
            "EXAM: Conjunctival pallor noted. Otherwise unremarkable.\n"
            "DATA: CBC shows hemoglobin 8.2 g/dL. Started on ferrous sulfate. Referral to GI placed.\n"
            "ASSESSMENT/PLAN: 1) Anemia - started iron, will work up. 2) Abnormal weight loss - GI "
            "referral. Total time 30 minutes.\n"
            "Electronically signed by Dr. S. Patel, MD."
        ),
    ),
    # 14 — Pathology (surgical pathology of a skin specimen) → expect 88305-26 + D22.5
    dict(
        mrn="PA40001", patient_name="Glen Mercer", age=63, sex="M", specialty="Pathology",
        modality="", encounter_type="", payer="Medicare", pos="22", dos="2026-04-20",
        client="Riverbend Health", source_system="Cerner", report_type="pathology_report",
        scenario="Pathology — surgical pathology specimen leveling",
        chart_text=(
            "SURGICAL PATHOLOGY REPORT\n"
            "SPECIMEN: Skin, left upper back, shave biopsy.\n"
            "CLINICAL HISTORY: Pigmented skin lesion.\n"
            "GROSS: Tan-brown skin fragment measuring 0.8 x 0.5 x 0.2 cm.\n"
            "MICROSCOPIC: Sections show a compound melanocytic nevus with nests of bland melanocytes at "
            "the dermo-epidermal junction and within the dermis. No cytologic atypia or malignancy.\n"
            "FINAL DIAGNOSIS: Compound melanocytic nevus, skin of back. Benign.\n"
            "Electronically signed by Dr. H. Vance, MD, Pathologist."
        ),
    ),
    # 15 — Surgical (outpatient/ASC) → expect 47562 + K80.20
    dict(
        mrn="SG50001", patient_name="Brenda Cho", age=49, sex="F", specialty="Surgical",
        modality="", encounter_type="", payer="Medicare", pos="24", dos="2026-04-20",
        client="Summit Surgical Center", source_system="PracticeAdmin", report_type="op_note",
        scenario="Surgical — outpatient laparoscopic procedure",
        chart_text=(
            "OPERATIVE NOTE\n"
            "PREOPERATIVE DIAGNOSIS: Symptomatic cholelithiasis.\n"
            "POSTOPERATIVE DIAGNOSIS: Same.\n"
            "PROCEDURE PERFORMED: Laparoscopic cholecystectomy.\n"
            "INDICATIONS: Recurrent biliary colic with gallstones documented on ultrasound; no duct "
            "obstruction.\n"
            "FINDINGS: Multiple gallstones; gallbladder removed intact without complication.\n"
            "DESCRIPTION: Standard four-port laparoscopic technique. Critical view of safety obtained. "
            "Cystic duct and artery clipped and divided. Gallbladder dissected from the liver bed and "
            "removed.\n"
            "Electronically signed by Dr. R. Banerjee, MD, Surgeon."
        ),
    ),
    # 16 — Cardiology (added via the specialty accelerator) → expect 93306 + I35.0
    dict(
        mrn="CA60001", patient_name="Harold Ihejirika", age=71, sex="M", specialty="Cardiology",
        modality="", encounter_type="", payer="Medicare", pos="11", dos="2026-04-21",
        client="Riverbend Cardiology", source_system="eClinicalWorks", report_type="echo_report",
        scenario="Cardiology — complete transthoracic echocardiogram",
        chart_text=(
            "ECHOCARDIOGRAPHY REPORT\n"
            "STUDY: Transthoracic echocardiogram, complete, with 2D, M-mode, spectral and color flow Doppler.\n"
            "INDICATION: Exertional dyspnea and systolic murmur.\n"
            "FINDINGS: Left ventricular ejection fraction 55%. Calcified aortic valve with reduced "
            "excursion; peak velocity 4.1 m/s, mean gradient 42 mmHg, valve area 0.9 cm^2 — consistent "
            "with severe aortic stenosis. No significant mitral regurgitation. Normal RV function.\n"
            "IMPRESSION: Severe calcific aortic valve stenosis with preserved LV systolic function.\n"
            "Interpretation performed in the office. Electronically signed by Dr. P. Anand, MD, Cardiologist."
        ),
    ),
    # 17 — Cardiology → expect 93000 + I48.91
    dict(
        mrn="CA60002", patient_name="Lucia Ferraro", age=64, sex="F", specialty="Cardiology",
        modality="", encounter_type="", payer="Medicare", pos="11", dos="2026-04-21",
        client="Riverbend Cardiology", source_system="eClinicalWorks", report_type="ecg_report",
        scenario="Cardiology — 12-lead electrocardiogram",
        chart_text=(
            "ELECTROCARDIOGRAM REPORT\n"
            "STUDY: Routine 12-lead ECG with physician interpretation and report.\n"
            "INDICATION: Palpitations and irregular pulse.\n"
            "FINDINGS: Irregularly irregular rhythm with absent P waves and fibrillatory baseline; "
            "ventricular rate 92 bpm. No acute ST-segment changes. QTc normal.\n"
            "IMPRESSION: Atrial fibrillation with controlled ventricular response.\n"
            "Electronically signed by Dr. P. Anand, MD, Cardiologist."
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
    dict(specialty="ED", irr=0.85, ambiguous=False,
         truth={"icd": ["R07.9"], "cpt": ["99284"]},
         chart_text=(
             "EMERGENCY DEPARTMENT NOTE\nCHIEF COMPLAINT: Chest pain.\n"
             "HPI: Hypertensive, hyperlipidemic patient with substernal chest pain. Comorbidities reviewed.\n"
             "EXAM: Vitals stable, heart regular, lungs clear.\n"
             "MDM: Independent ECG interpretation (no acute ischemia); ordered and reviewed troponin, "
             "CBC, CMP, chest X-ray. Acute illness with systemic symptoms, moderate risk, prescription "
             "management. High medical decision making. Discharged with cardiology follow-up.\n"
             "Electronically signed by provider.")),
    dict(specialty="ED", irr=0.83, ambiguous=False,
         truth={"icd": ["J96.00"], "cpt": ["99291"]},
         chart_text=(
             "EMERGENCY DEPARTMENT NOTE\nCHIEF COMPLAINT: Severe shortness of breath.\n"
             "HPI: Acute respiratory distress, hypoxic to 84% on room air.\n"
             "MDM: Acute respiratory failure with hypoxia; high probability of deterioration. BiPAP "
             "initiated. 60 minutes of critical care provided, exclusive of separate procedures. "
             "Admitted to ICU.\nElectronically signed by provider.")),
    dict(specialty="E&M", irr=0.86, ambiguous=False,
         truth={"icd": ["I10", "E78.5"], "cpt": ["99213"]},
         chart_text=(
             "OFFICE VISIT NOTE (Established Patient)\n"
             "HPI: Routine follow-up for hypertension and hyperlipidemia, both stable. No new complaints.\n"
             "EXAM: Blood pressure at goal. Unremarkable.\n"
             "DATA: Lipid panel reviewed, at target on statin.\n"
             "ASSESSMENT/PLAN: 1) Essential hypertension - stable, continue lisinopril. 2) Hyperlipidemia "
             "- stable, continue statin. Low MDM. Total time 20 minutes.\nElectronically signed by provider.")),
    dict(specialty="E&M", irr=0.86, ambiguous=False,
         truth={"icd": ["E11.65"], "cpt": ["99214"]},
         chart_text=(
             "OFFICE VISIT NOTE (Established Patient)\n"
             "HPI: Type 2 diabetic with worsening home glucose readings. No neuropathy symptoms.\n"
             "EXAM: Unremarkable; feet with intact sensation.\n"
             "DATA: A1C resulted at 10.1%, consistent with hyperglycemia.\n"
             "ASSESSMENT/PLAN: Type 2 diabetes mellitus with hyperglycemia, uncontrolled - intensify "
             "therapy, add agent, diabetic education. Moderate MDM. Total time 30 minutes.\n"
             "Electronically signed by provider.")),
    dict(specialty="Pathology", irr=0.88, ambiguous=False,
         truth={"icd": ["D22.5"], "cpt": ["88305"]},
         chart_text=(
             "SURGICAL PATHOLOGY REPORT\nSPECIMEN: Skin, back, shave biopsy.\n"
             "MICROSCOPIC: Compound melanocytic nevus with bland junctional and dermal nests. No atypia "
             "or malignancy.\nFINAL DIAGNOSIS: Compound melanocytic nevus, skin of back. Benign.\n"
             "Electronically signed by pathologist.")),
    dict(specialty="Surgical", irr=0.90, ambiguous=False,
         truth={"icd": ["K80.20"], "cpt": ["47562"]},
         chart_text=(
             "OPERATIVE NOTE\nPREOPERATIVE DIAGNOSIS: Symptomatic cholelithiasis.\n"
             "PROCEDURE PERFORMED: Laparoscopic cholecystectomy.\nFINDINGS: Multiple gallstones, no duct "
             "obstruction; gallbladder removed intact.\nDESCRIPTION: Four-port laparoscopic technique, "
             "critical view of safety, cystic duct and artery clipped and divided.\n"
             "Electronically signed by surgeon.")),
    dict(specialty="Cardiology", irr=0.90, ambiguous=False,
         truth={"icd": ["I35.0"], "cpt": ["93306"]},
         chart_text=(
             "ECHOCARDIOGRAPHY REPORT\nSTUDY: Transthoracic echocardiogram, complete, with spectral and "
             "color flow Doppler.\nINDICATION: Systolic murmur.\nFINDINGS: Calcified aortic valve, peak "
             "velocity 4.3 m/s, mean gradient 46 mmHg, valve area 0.8 cm^2; LVEF 60%.\nIMPRESSION: Severe "
             "calcific aortic valve stenosis.\nElectronically signed by cardiologist.")),
    dict(specialty="Cardiology", irr=0.88, ambiguous=False,
         truth={"icd": ["I48.91"], "cpt": ["93000"]},
         chart_text=(
             "ELECTROCARDIOGRAM REPORT\nSTUDY: Routine 12-lead ECG with interpretation and report.\n"
             "INDICATION: Palpitations.\nFINDINGS: Irregularly irregular rhythm, absent P waves, "
             "fibrillatory baseline, ventricular rate 88 bpm; no acute ST changes.\nIMPRESSION: Atrial "
             "fibrillation.\nElectronically signed by cardiologist.")),
]
