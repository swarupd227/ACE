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
    # 18 — Orthopedics (added via the specialty accelerator) → expect 27447 + M17.11
    dict(
        mrn="OR70001", patient_name="Walter Greaves", age=68, sex="M", specialty="Orthopedics",
        modality="", encounter_type="", payer="Medicare", pos="24", dos="2026-04-22",
        client="Summit Orthopedic Center", source_system="PracticeAdmin", report_type="op_note",
        scenario="Orthopedics — total knee arthroplasty",
        chart_text=(
            "OPERATIVE NOTE\n"
            "PREOPERATIVE DIAGNOSIS: Severe primary osteoarthritis, right knee.\n"
            "POSTOPERATIVE DIAGNOSIS: Same.\n"
            "PROCEDURE PERFORMED: Total knee arthroplasty, right — replacement of the medial AND lateral "
            "femoral condyles and tibial plateau with a cemented prosthesis.\n"
            "INDICATIONS: End-stage right knee osteoarthritis with bone-on-bone changes and functional "
            "limitation despite NSAIDs, injections and physical therapy.\n"
            "FINDINGS: Tricompartmental cartilage loss; components seated and stable through full range of "
            "motion.\n"
            "Electronically signed by Dr. M. Okafor, MD, Orthopedic Surgeon."
        ),
    ),
    # 19 — Orthopedics → expect 20610 + M75.101
    dict(
        mrn="OR70002", patient_name="Sofia Marin", age=57, sex="F", specialty="Orthopedics",
        modality="", encounter_type="", payer="Medicare", pos="11", dos="2026-04-22",
        client="Summit Orthopedics", source_system="eClinicalWorks", report_type="procedure_note",
        scenario="Orthopedics — major-joint injection",
        chart_text=(
            "PROCEDURE NOTE\n"
            "DIAGNOSIS: Incomplete rotator cuff tear, right shoulder (non-traumatic), with subacromial "
            "bursitis.\n"
            "PROCEDURE: Ultrasound-landmarked subacromial corticosteroid injection of the right shoulder "
            "(major joint/bursa).\n"
            "DETAIL: Sterile prep; 1 mL triamcinolone with lidocaine instilled into the subacromial space; "
            "patient tolerated the procedure well.\n"
            "Electronically signed by Dr. M. Okafor, MD, Orthopedic Surgeon."
        ),
    ),
    # 20 — OB/GYN (obstetrics) → expect 76805 + Z34.82
    dict(
        mrn="OB80001", patient_name="Priya Nadkarni", age=29, sex="F", specialty="OB/GYN",
        modality="", encounter_type="", payer="Anthem", pos="11", dos="2026-04-23",
        client="Riverbend Women's Health", source_system="eClinicalWorks", report_type="ultrasound_report",
        scenario="OB/GYN — obstetric anatomy ultrasound",
        chart_text=(
            "OBSTETRIC ULTRASOUND REPORT\n"
            "STUDY: Transabdominal obstetric ultrasound, single intrauterine gestation, 20 weeks.\n"
            "INDICATION: Routine second-trimester fetal anatomy survey, uncomplicated pregnancy.\n"
            "FINDINGS: Single live intrauterine fetus, cephalic. Biometry consistent with 20w1d. Four-chamber "
            "heart, stomach, bladder, kidneys, spine and cranial anatomy appear normal. Posterior placenta, "
            "not previa. Amniotic fluid normal.\n"
            "IMPRESSION: Normal 20-week fetal anatomy survey; uncomplicated intrauterine pregnancy.\n"
            "Performed in the office. Electronically signed by Dr. L. Mensah, MD, OB/GYN."
        ),
    ),
    # 21 — OB/GYN (gynecology) → expect 57454 + N87.1
    dict(
        mrn="GY80002", patient_name="Carla Jimenez", age=42, sex="F", specialty="OB/GYN",
        modality="", encounter_type="", payer="Medicare", pos="11", dos="2026-04-23",
        client="Riverbend Women's Health", source_system="PracticeAdmin", report_type="procedure_note",
        scenario="OB/GYN — colposcopy with cervical biopsy",
        chart_text=(
            "COLPOSCOPY PROCEDURE NOTE\n"
            "INDICATION: Abnormal cervical cytology (HSIL) on screening Pap.\n"
            "PROCEDURE: Colposcopy of the cervix with cervical biopsy and endocervical curettage.\n"
            "FINDINGS: Acetowhite epithelium with coarse punctation at the squamocolumnar junction; biopsy "
            "taken. Pathology returned moderate cervical dysplasia (CIN II).\n"
            "IMPRESSION: Moderate cervical dysplasia (CIN II).\n"
            "Electronically signed by Dr. L. Mensah, MD, OB/GYN."
        ),
    ),
    # 22 — GI / Endoscopy → expect 45385 + K63.5
    dict(
        mrn="GI90001", patient_name="Theodore Banks", age=58, sex="M", specialty="GI / Endoscopy",
        modality="", encounter_type="", payer="Medicare", pos="24", dos="2026-04-24",
        client="Riverbend Digestive Health", source_system="Cerner", report_type="endoscopy_report",
        scenario="GI / Endoscopy — colonoscopy with snare polypectomy",
        chart_text=(
            "COLONOSCOPY REPORT\n"
            "INDICATION: Average-risk screening colonoscopy; family history reviewed.\n"
            "PROCEDURE: Flexible colonoscopy to the cecum. A 9 mm sessile polyp in the sigmoid colon was "
            "removed in its entirety by snare technique; retrieved for pathology. No other lesions.\n"
            "FINDINGS: Single sigmoid colon polyp, removed by snare. Otherwise normal colonic mucosa to "
            "the cecum.\n"
            "IMPRESSION: Colon polyp, sigmoid, removed by snare polypectomy.\n"
            "Electronically signed by Dr. S. Whitfield, MD, Gastroenterologist."
        ),
    ),
    # 23 — GI / Endoscopy → expect 43239 + K29.70
    dict(
        mrn="GI90002", patient_name="Nadia Hassan", age=46, sex="F", specialty="GI / Endoscopy",
        modality="", encounter_type="", payer="Medicare", pos="24", dos="2026-04-24",
        client="Riverbend Digestive Health", source_system="Cerner", report_type="endoscopy_report",
        scenario="GI / Endoscopy — EGD with biopsy",
        chart_text=(
            "UPPER ENDOSCOPY (EGD) REPORT\n"
            "INDICATION: Persistent epigastric discomfort and reflux symptoms despite PPI therapy.\n"
            "PROCEDURE: Esophagogastroduodenoscopy to the second portion of the duodenum. Gastric antral "
            "mucosa was erythematous; biopsies were obtained.\n"
            "FINDINGS: Erythematous antral mucosa; biopsy taken. Pathology returned chronic gastritis "
            "without bleeding. Esophagus and duodenum normal.\n"
            "IMPRESSION: Gastritis (without bleeding) on antral biopsy.\n"
            "Electronically signed by Dr. S. Whitfield, MD, Gastroenterologist."
        ),
    ),
    # 24 — Dermatology → expect 17000 + L57.0
    dict(
        mrn="DE10001", patient_name="Gordon Hayes", age=72, sex="M", specialty="Dermatology",
        modality="", encounter_type="", payer="Medicare", pos="11", dos="2026-04-25",
        client="Riverbend Dermatology", source_system="eClinicalWorks", report_type="procedure_note",
        scenario="Dermatology — cryotherapy destruction of actinic keratosis",
        chart_text=(
            "DERMATOLOGY PROCEDURE NOTE\n"
            "INDICATION: Rough, scaly lesion on the left dorsal forearm, clinically consistent with actinic "
            "keratosis in a sun-damaged patient.\n"
            "PROCEDURE: Cryotherapy (liquid nitrogen) destruction of a single premalignant lesion (actinic "
            "keratosis), first lesion treated.\n"
            "FINDINGS: One actinic keratosis treated with a freeze-thaw cycle; patient tolerated well.\n"
            "IMPRESSION: Actinic keratosis, destroyed by cryotherapy.\n"
            "Electronically signed by Dr. E. Solis, MD, Dermatologist."
        ),
    ),
    # 25 — Dermatology → expect 11104 + C44.91
    dict(
        mrn="DE10002", patient_name="Bianca Rossi", age=64, sex="F", specialty="Dermatology",
        modality="", encounter_type="", payer="Medicare", pos="11", dos="2026-04-25",
        client="Riverbend Dermatology", source_system="eClinicalWorks", report_type="procedure_note",
        scenario="Dermatology — punch biopsy of a suspicious lesion",
        chart_text=(
            "DERMATOLOGY PROCEDURE NOTE\n"
            "INDICATION: Pearly, telangiectatic papule on the right nasal ala, clinically suspicious for "
            "basal cell carcinoma.\n"
            "PROCEDURE: 3 mm punch biopsy of the right nasal ala lesion; single lesion, specimen to "
            "pathology.\n"
            "PATHOLOGY: Sections show nests of basaloid cells with peripheral palisading — basal cell "
            "carcinoma.\n"
            "IMPRESSION: Basal cell carcinoma, skin of nose (biopsy-confirmed).\n"
            "Electronically signed by Dr. E. Solis, MD, Dermatologist."
        ),
    ),
    # 26 — Urology → expect 50590 + N20.0
    dict(
        mrn="UR10001", patient_name="Martin Quayle", age=55, sex="M", specialty="Urology",
        modality="", encounter_type="", payer="Medicare", pos="24", dos="2026-04-26",
        client="Riverbend Urology", source_system="Cerner", report_type="procedure_note",
        scenario="Urology — extracorporeal shock wave lithotripsy",
        chart_text=(
            "UROLOGY PROCEDURE NOTE\n"
            "INDICATION: 8 mm obstructing calculus in the right renal pelvis with flank pain, confirmed on CT.\n"
            "PROCEDURE: Extracorporeal shock wave lithotripsy (ESWL) of the right renal calculus under "
            "sedation; fluoroscopic localization.\n"
            "FINDINGS: Stone fragmented into passable pieces; no immediate complication.\n"
            "IMPRESSION: Right renal calculus treated with ESWL.\n"
            "Electronically signed by Dr. A. Iyer, MD, Urologist."
        ),
    ),
    # 27 — Urology → expect 52234 + C67.9
    dict(
        mrn="UR10002", patient_name="Eleanor Voss", age=69, sex="F", specialty="Urology",
        modality="", encounter_type="", payer="Medicare", pos="24", dos="2026-04-26",
        client="Riverbend Urology", source_system="Cerner", report_type="procedure_note",
        scenario="Urology — cystoscopy with bladder tumor resection",
        chart_text=(
            "CYSTOSCOPY OPERATIVE NOTE\n"
            "INDICATION: Gross hematuria with a small papillary bladder lesion seen on prior imaging.\n"
            "PROCEDURE: Cystourethroscopy with fulguration and resection of a small bladder tumor on the "
            "right lateral wall; specimen to pathology.\n"
            "FINDINGS: Solitary ~1 cm papillary bladder tumor resected and fulgurated; bladder otherwise "
            "normal.\n"
            "IMPRESSION: Bladder neoplasm, resected.\n"
            "Electronically signed by Dr. A. Iyer, MD, Urologist."
        ),
    ),
    # 28 — Anesthesia → expect 00790 + K80.20
    dict(
        mrn="AN10001", patient_name="Howard Beck", age=51, sex="M", specialty="Anesthesia",
        modality="", encounter_type="", payer="Medicare", pos="24", dos="2026-04-26",
        client="Summit Surgical Center", source_system="PracticeAdmin", report_type="anesthesia_record",
        scenario="Anesthesia — general anesthesia for laparoscopic cholecystectomy",
        chart_text=(
            "ANESTHESIA RECORD\n"
            "PROCEDURE ANESTHETIZED: Laparoscopic cholecystectomy (upper-abdomen intraperitoneal).\n"
            "PREOPERATIVE DIAGNOSIS: Symptomatic cholelithiasis.\n"
            "ANESTHESIA: General endotracheal anesthesia. ASA physical status II (mild systemic disease, "
            "controlled hypertension).\n"
            "TIME: Anesthesia start 08:12, stop 09:34. Stable throughout; no complications.\n"
            "Electronically signed by Dr. C. Romano, MD, Anesthesiologist."
        ),
    ),
    # 29 — Anesthesia → expect 01402 + M17.11
    dict(
        mrn="AN10002", patient_name="Gloria Esposito", age=70, sex="F", specialty="Anesthesia",
        modality="", encounter_type="", payer="Medicare", pos="24", dos="2026-04-26",
        client="Summit Surgical Center", source_system="PracticeAdmin", report_type="anesthesia_record",
        scenario="Anesthesia — anesthesia for total knee arthroplasty",
        chart_text=(
            "ANESTHESIA RECORD\n"
            "PROCEDURE ANESTHETIZED: Total knee arthroplasty, right.\n"
            "PREOPERATIVE DIAGNOSIS: Severe primary osteoarthritis, right knee.\n"
            "ANESTHESIA: Spinal anesthesia with sedation. ASA physical status II.\n"
            "TIME: Anesthesia start 07:40, stop 09:25. Uneventful.\n"
            "Electronically signed by Dr. C. Romano, MD, Anesthesiologist."
        ),
    ),
    # 30 — Ophthalmology → expect 66984 + H25.9
    dict(
        mrn="OP10001", patient_name="Walter Nakamura", age=74, sex="M", specialty="Ophthalmology",
        modality="", encounter_type="", payer="Medicare", pos="24", dos="2026-04-26",
        client="Riverbend Eye Center", source_system="eClinicalWorks", report_type="op_note",
        scenario="Ophthalmology — cataract extraction with IOL",
        chart_text=(
            "OPHTHALMOLOGY OPERATIVE NOTE\n"
            "INDICATION: Visually significant age-related cataract, right eye, with best-corrected acuity "
            "20/80 and difficulty with driving and reading.\n"
            "PROCEDURE: Extracapsular cataract extraction by phacoemulsification with insertion of a "
            "posterior-chamber intraocular lens, right eye, single stage.\n"
            "FINDINGS: Dense nuclear sclerotic cataract removed; IOL well centered.\n"
            "IMPRESSION: Age-related cataract, right eye, treated with phaco + IOL.\n"
            "Electronically signed by Dr. N. Abara, MD, Ophthalmologist."
        ),
    ),
    # 31 — Ophthalmology → expect 67028 + H35.30
    dict(
        mrn="OP10002", patient_name="Sylvia Trent", age=78, sex="F", specialty="Ophthalmology",
        modality="", encounter_type="", payer="Medicare", pos="11", dos="2026-04-26",
        client="Riverbend Eye Center", source_system="eClinicalWorks", report_type="procedure_note",
        scenario="Ophthalmology — intravitreal anti-VEGF injection",
        chart_text=(
            "OPHTHALMOLOGY PROCEDURE NOTE\n"
            "INDICATION: Neovascular (wet) age-related macular degeneration, left eye, with subretinal fluid "
            "on OCT.\n"
            "PROCEDURE: Intravitreal injection of an anti-VEGF pharmacologic agent, left eye, under sterile "
            "technique.\n"
            "FINDINGS: Injection delivered without complication; patient tolerated well.\n"
            "IMPRESSION: Macular degeneration, left eye, treated with intravitreal anti-VEGF.\n"
            "Electronically signed by Dr. N. Abara, MD, Ophthalmologist."
        ),
    ),
    # 32 — ENT → expect 42820 + J35.3
    dict(
        mrn="EN10001", patient_name="Liam Castellano", age=6, sex="M", specialty="ENT",
        modality="", encounter_type="", payer="Medicare", pos="24", dos="2026-05-02",
        client="Cedar Hill ENT Associates", source_system="eClinicalWorks", report_type="op_note",
        scenario="ENT — tonsillectomy with adenoidectomy (pediatric)",
        chart_text=(
            "OTOLARYNGOLOGY OPERATIVE NOTE\n"
            "INDICATION: 6-year-old with recurrent tonsillitis (7 episodes in the past year) and "
            "adenotonsillar hypertrophy causing obstructive sleep-disordered breathing.\n"
            "PROCEDURE: Tonsillectomy and adenoidectomy under general anesthesia.\n"
            "FINDINGS: Markedly enlarged tonsils and adenoids; removed without complication; hemostasis "
            "achieved.\n"
            "IMPRESSION: Hypertrophy of tonsils with hypertrophy of adenoids; recurrent tonsillitis.\n"
            "Electronically signed by Dr. R. Okafor, MD, Otolaryngologist."
        ),
    ),
    # 33 — ENT → expect 69436 + H65.23 (bilateral, modifier 50)
    dict(
        mrn="EN10002", patient_name="Ava Lindqvist", age=4, sex="F", specialty="ENT",
        modality="", encounter_type="", payer="Aetna", pos="24", dos="2026-05-02",
        client="Cedar Hill ENT Associates", source_system="eClinicalWorks", report_type="procedure_note",
        scenario="ENT — bilateral tympanostomy tubes for chronic OME",
        chart_text=(
            "OTOLARYNGOLOGY PROCEDURE NOTE\n"
            "INDICATION: 4-year-old with chronic serous otitis media with effusion, both ears, persisting "
            "beyond 3 months with documented conductive hearing loss.\n"
            "PROCEDURE: Bilateral myringotomy with insertion of tympanostomy (ventilating) tubes under "
            "general anesthesia.\n"
            "FINDINGS: Thick serous effusion evacuated from both middle ears; tubes seated bilaterally.\n"
            "IMPRESSION: Chronic serous otitis media, bilateral.\n"
            "Electronically signed by Dr. R. Okafor, MD, Otolaryngologist."
        ),
    ),
    # 34 — Inpatient (DRG) → medical, MCC → expect DRG 193 (pneumonia w MCC)
    dict(
        mrn="IP10001", patient_name="Harold Beckmann", age=71, sex="M", specialty="Inpatient (DRG)",
        modality="", encounter_type="inpatient", payer="Medicare", pos="21", dos="2026-05-09",
        client="Mercy General Hospital", source_system="Cerner", report_type="discharge_summary",
        scenario="Inpatient — pneumonia + acute respiratory failure (MCC)",
        chart_text=(
            "INPATIENT DISCHARGE SUMMARY\n"
            "ADMISSION: 71-year-old man admitted from the ED with community-acquired pneumonia.\n"
            "PRINCIPAL DIAGNOSIS: Pneumonia, unspecified organism.\n"
            "HOSPITAL COURSE: Started on IV antibiotics. On hospital day 1 he developed acute hypoxic "
            "respiratory failure requiring high-flow oxygen; this resolved by day 3.\n"
            "PROCEDURE: Diagnostic flexible bronchoscopy with inspection of the tracheobronchial tree via "
            "natural opening (no biopsy taken).\n"
            "SECONDARY DIAGNOSES: Acute respiratory failure with hypoxia.\n"
            "DISPOSITION: Discharged home on room air, day 4.\n"
            "Electronically signed by Dr. P. Salvador, MD, Hospitalist."
        ),
    ),
    # 35 — Inpatient (DRG) → surgical (OR procedure), CC → expect DRG 330 (major bowel proc w CC)
    dict(
        mrn="IP10002", patient_name="Geraldine Foss", age=68, sex="F", specialty="Inpatient (DRG)",
        modality="", encounter_type="inpatient", payer="Medicare", pos="21", dos="2026-05-09",
        client="Mercy General Hospital", source_system="Cerner", report_type="discharge_summary",
        scenario="Inpatient — colon resection (OR) with anemia (CC)",
        chart_text=(
            "INPATIENT OPERATIVE / DISCHARGE SUMMARY\n"
            "ADMISSION: 68-year-old woman admitted with an obstructing sigmoid colon mass; preoperative "
            "biopsy confirmed adenocarcinoma of the colon.\n"
            "PRINCIPAL DIAGNOSIS: Malignant neoplasm of the colon.\n"
            "PROCEDURE: Open resection of the sigmoid colon (open sigmoid colectomy).\n"
            "SECONDARY DIAGNOSES: Anemia, unspecified, present preoperatively.\n"
            "HOSPITAL COURSE: Uncomplicated postoperative recovery; tolerating diet at discharge.\n"
            "Electronically signed by Dr. M. Iqbal, MD, General Surgery."
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
    dict(specialty="Orthopedics", irr=0.90, ambiguous=False,
         truth={"icd": ["M17.11"], "cpt": ["27447"]},
         chart_text=(
             "OPERATIVE NOTE\nPREOPERATIVE DIAGNOSIS: Severe primary osteoarthritis, right knee.\n"
             "PROCEDURE PERFORMED: Total knee arthroplasty, right (medial and lateral compartments, "
             "cemented).\nINDICATIONS: End-stage right knee OA with functional limitation after failed "
             "conservative care.\nFINDINGS: Tricompartmental cartilage loss; components stable.\n"
             "Electronically signed by orthopedic surgeon.")),
    dict(specialty="Orthopedics", irr=0.88, ambiguous=False,
         truth={"icd": ["M75.101"], "cpt": ["29826"]},
         chart_text=(
             "OPERATIVE NOTE\nPREOPERATIVE DIAGNOSIS: Incomplete rotator cuff tear, right shoulder, with "
             "impingement.\nPROCEDURE PERFORMED: Right shoulder arthroscopy with subacromial decompression "
             "and partial acromioplasty.\nFINDINGS: Subacromial spurring with bursal-sided partial-thickness "
             "cuff fraying; decompression performed.\nElectronically signed by orthopedic surgeon.")),
    dict(specialty="OB/GYN", irr=0.90, ambiguous=False,
         truth={"icd": ["Z34.82"], "cpt": ["76805"]},
         chart_text=(
             "OBSTETRIC ULTRASOUND REPORT\nSTUDY: Transabdominal obstetric ultrasound, single intrauterine "
             "gestation, 20 weeks.\nINDICATION: Routine second-trimester fetal anatomy survey, uncomplicated "
             "pregnancy.\nFINDINGS: Single live fetus, biometry at 20w; normal anatomy survey; posterior "
             "placenta, not previa; normal fluid.\nIMPRESSION: Normal 20-week anatomy survey, uncomplicated "
             "pregnancy.\nElectronically signed by OB/GYN.")),
    dict(specialty="OB/GYN", irr=0.88, ambiguous=False,
         truth={"icd": ["N87.1"], "cpt": ["57454"]},
         chart_text=(
             "COLPOSCOPY PROCEDURE NOTE\nINDICATION: Abnormal cervical cytology (HSIL) on Pap.\n"
             "PROCEDURE: Colposcopy of the cervix with cervical biopsy and endocervical curettage.\n"
             "FINDINGS: Acetowhite epithelium with punctation; biopsy returned moderate cervical dysplasia "
             "(CIN II).\nIMPRESSION: Moderate cervical dysplasia (CIN II).\nElectronically signed by OB/GYN.")),
    dict(specialty="GI / Endoscopy", irr=0.90, ambiguous=False,
         truth={"icd": ["K63.5"], "cpt": ["45385"]},
         chart_text=(
             "COLONOSCOPY REPORT\nINDICATION: Average-risk screening colonoscopy.\nPROCEDURE: Flexible "
             "colonoscopy to the cecum; a 9 mm sessile sigmoid polyp removed in its entirety by snare "
             "technique and retrieved.\nFINDINGS: Single sigmoid polyp removed by snare; otherwise normal "
             "mucosa.\nIMPRESSION: Colon polyp, removed by snare polypectomy.\nElectronically signed by "
             "gastroenterologist.")),
    dict(specialty="GI / Endoscopy", irr=0.88, ambiguous=False,
         truth={"icd": ["K29.70"], "cpt": ["43239"]},
         chart_text=(
             "UPPER ENDOSCOPY (EGD) REPORT\nINDICATION: Epigastric pain and reflux despite PPI.\n"
             "PROCEDURE: EGD to the second portion of the duodenum; erythematous gastric antrum biopsied.\n"
             "FINDINGS: Antral biopsy returned chronic gastritis without bleeding; esophagus and duodenum "
             "normal.\nIMPRESSION: Gastritis without bleeding.\nElectronically signed by gastroenterologist.")),
    dict(specialty="Dermatology", irr=0.90, ambiguous=False,
         truth={"icd": ["L57.0"], "cpt": ["17000"]},
         chart_text=(
             "DERMATOLOGY PROCEDURE NOTE\nINDICATION: Scaly lesion on the forearm, clinically consistent "
             "with actinic keratosis.\nPROCEDURE: Cryotherapy (liquid nitrogen) destruction of a single "
             "premalignant lesion (actinic keratosis), first lesion.\nIMPRESSION: Actinic keratosis "
             "destroyed by cryotherapy.\nElectronically signed by dermatologist.")),
    dict(specialty="Dermatology", irr=0.88, ambiguous=False,
         truth={"icd": ["C44.91"], "cpt": ["11104"]},
         chart_text=(
             "DERMATOLOGY PROCEDURE NOTE\nINDICATION: Pearly telangiectatic papule on the nose, suspicious "
             "for basal cell carcinoma.\nPROCEDURE: 3 mm punch biopsy of the lesion, single site.\n"
             "PATHOLOGY: Basaloid nests with peripheral palisading — basal cell carcinoma.\nIMPRESSION: "
             "Basal cell carcinoma of skin (biopsy-confirmed).\nElectronically signed by dermatologist.")),
    dict(specialty="Urology", irr=0.90, ambiguous=False,
         truth={"icd": ["N20.0"], "cpt": ["50590"]},
         chart_text=(
             "UROLOGY PROCEDURE NOTE\nINDICATION: 8 mm obstructing right renal pelvis calculus on CT.\n"
             "PROCEDURE: Extracorporeal shock wave lithotripsy (ESWL) of the right renal stone.\n"
             "FINDINGS: Stone fragmented into passable pieces.\nIMPRESSION: Right renal calculus treated "
             "with ESWL.\nElectronically signed by urologist.")),
    dict(specialty="Urology", irr=0.88, ambiguous=False,
         truth={"icd": ["C67.9"], "cpt": ["52234"]},
         chart_text=(
             "CYSTOSCOPY OPERATIVE NOTE\nINDICATION: Gross hematuria with a papillary bladder lesion.\n"
             "PROCEDURE: Cystourethroscopy with fulguration/resection of a small bladder tumor.\nFINDINGS: "
             "Solitary ~1 cm papillary bladder tumor resected.\nIMPRESSION: Bladder neoplasm, resected.\n"
             "Electronically signed by urologist.")),
    dict(specialty="Anesthesia", irr=0.90, ambiguous=False,
         truth={"icd": ["K80.20"], "cpt": ["00790"]},
         chart_text=(
             "ANESTHESIA RECORD\nPROCEDURE ANESTHETIZED: Laparoscopic cholecystectomy (upper abdomen).\n"
             "PREOPERATIVE DIAGNOSIS: Symptomatic cholelithiasis.\nANESTHESIA: General endotracheal; ASA "
             "physical status II.\nTIME: 08:12-09:34, uneventful.\nElectronically signed by anesthesiologist.")),
    dict(specialty="Anesthesia", irr=0.88, ambiguous=False,
         truth={"icd": ["M17.11"], "cpt": ["01402"]},
         chart_text=(
             "ANESTHESIA RECORD\nPROCEDURE ANESTHETIZED: Total knee arthroplasty, right.\nPREOPERATIVE "
             "DIAGNOSIS: Severe primary osteoarthritis, right knee.\nANESTHESIA: Spinal with sedation; ASA "
             "physical status II.\nTIME: 07:40-09:25.\nElectronically signed by anesthesiologist.")),
    dict(specialty="Ophthalmology", irr=0.90, ambiguous=False,
         truth={"icd": ["H25.9"], "cpt": ["66984"]},
         chart_text=(
             "OPHTHALMOLOGY OPERATIVE NOTE\nINDICATION: Visually significant age-related cataract, right "
             "eye, BCVA 20/80.\nPROCEDURE: Phacoemulsification with posterior-chamber intraocular lens "
             "insertion, right eye, one stage.\nIMPRESSION: Age-related cataract treated with phaco + IOL.\n"
             "Electronically signed by ophthalmologist.")),
    dict(specialty="Ophthalmology", irr=0.88, ambiguous=False,
         truth={"icd": ["H35.30"], "cpt": ["67028"]},
         chart_text=(
             "OPHTHALMOLOGY PROCEDURE NOTE\nINDICATION: Neovascular (wet) age-related macular degeneration, "
             "left eye, with subretinal fluid on OCT.\nPROCEDURE: Intravitreal anti-VEGF injection, left "
             "eye.\nIMPRESSION: Macular degeneration treated with intravitreal injection.\nElectronically "
             "signed by ophthalmologist.")),
    dict(specialty="ENT", irr=0.90, ambiguous=False,
         truth={"icd": ["J35.3"], "cpt": ["42820"]},
         chart_text=(
             "OTOLARYNGOLOGY OPERATIVE NOTE\nINDICATION: 7-year-old with adenotonsillar hypertrophy and "
             "recurrent tonsillitis with obstructive sleep-disordered breathing.\nPROCEDURE: Tonsillectomy "
             "and adenoidectomy under general anesthesia.\nIMPRESSION: Hypertrophy of tonsils with "
             "hypertrophy of adenoids.\nElectronically signed by otolaryngologist.")),
    dict(specialty="ENT", irr=0.88, ambiguous=False,
         truth={"icd": ["H65.23"], "cpt": ["69436"]},
         chart_text=(
             "OTOLARYNGOLOGY PROCEDURE NOTE\nINDICATION: 4-year-old with chronic serous otitis media with "
             "effusion, both ears, beyond 3 months with conductive hearing loss.\nPROCEDURE: Bilateral "
             "myringotomy with tympanostomy tube insertion under general anesthesia.\nIMPRESSION: Chronic "
             "serous otitis media, bilateral.\nElectronically signed by otolaryngologist.")),
    dict(specialty="Inpatient (DRG)", irr=0.86, ambiguous=False,
         truth={"icd": ["I50.21", "N17.9"], "cpt": [], "pcs": [], "drg": "291"},
         chart_text=(
             "INPATIENT DISCHARGE SUMMARY\nADMISSION: Admitted with acute decompensated heart failure.\n"
             "PRINCIPAL DIAGNOSIS: Acute systolic (congestive) heart failure.\nHOSPITAL COURSE: Diuresed "
             "with IV furosemide; course complicated by acute kidney injury that resolved before "
             "discharge.\nSECONDARY DIAGNOSES: Acute kidney failure.\nElectronically signed by "
             "hospitalist.")),
    dict(specialty="Inpatient (DRG)", irr=0.84, ambiguous=False,
         truth={"icd": ["K56.609", "A41.9"], "cpt": [], "pcs": ["0DTN0ZZ"], "drg": "329"},
         chart_text=(
             "INPATIENT OPERATIVE / DISCHARGE SUMMARY\nADMISSION: Admitted with intestinal obstruction.\n"
             "PRINCIPAL DIAGNOSIS: Intestinal obstruction.\nPROCEDURE: Open resection of the sigmoid "
             "colon.\nHOSPITAL COURSE: Postoperative course complicated by sepsis treated with IV "
             "antibiotics.\nSECONDARY DIAGNOSES: Sepsis.\nElectronically signed by surgeon.")),
]
