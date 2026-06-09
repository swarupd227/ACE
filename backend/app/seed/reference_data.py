"""Reference data for the demo.

PROVENANCE (honest by design):
- ICD-10-CM : REAL, public-domain (CMS/NCHS) — a curated subset for Radiology + E&M.
- HCPCS L2  : REAL, public-domain (CMS) — small subset.
- CPT       : DEMO_PLACEHOLDER. Radiology 70000-series numbers are widely-known facts,
              but descriptors here are our own paraphrase, NOT AMA's copyrighted text.
              Swap in a licensed AMA distribution for production (same table shape).
- NCCI/MUE  : modeled on REAL CMS edit logic, subset.
- Payer policy / ontology / guidelines : representative, clearly-labeled.
"""
from __future__ import annotations

EFF = {"effective_start": "2025-10-01", "effective_end": "2099-12-31"}

# --- ICD-10-CM (real codes; parents included to exercise the specificity gate) ---
ICD10CM = [
    # billable
    ("R07.9", "Chest pain, unspecified", True, "R07"),
    ("R07.89", "Other chest pain", True, "R07.8"),
    ("J18.9", "Pneumonia, unspecified organism", True, "J18"),
    ("R05.9", "Cough, unspecified", True, "R05"),
    ("R10.9", "Unspecified abdominal pain", True, "R10"),
    ("R10.84", "Generalized abdominal pain", True, "R10.8"),
    ("N20.0", "Calculus of kidney", True, "N20"),
    ("R51.9", "Headache, unspecified", True, "R51"),
    ("M54.50", "Low back pain, unspecified", True, "M54.5"),
    ("M25.561", "Pain in right knee", True, "M25.56"),
    ("M25.562", "Pain in left knee", True, "M25.56"),
    ("S52.501A", "Unspecified fracture of lower end of right radius, initial enc, closed", True, "S52.50"),
    ("E11.9", "Type 2 diabetes mellitus without complications", True, "E11"),
    ("E11.40", "Type 2 diabetes mellitus with diabetic neuropathy, unspecified", True, "E11.4"),
    ("E11.42", "Type 2 diabetes mellitus with diabetic polyneuropathy", True, "E11.4"),
    ("I10", "Essential (primary) hypertension", True, ""),
    ("R93.1", "Abnormal findings on diagnostic imaging of heart and coronary circulation", True, "R93"),
    ("R91.8", "Other nonspecific abnormal finding of lung field", True, "R91"),
    ("Z01.89", "Encounter for other specified special examinations", True, "Z01.8"),
    ("J96.00", "Acute respiratory failure, unspecified whether with hypoxia or hypercapnia", True, "J96.0"),
    ("R06.02", "Shortness of breath", True, "R06.0"),
    ("A41.9", "Sepsis, unspecified organism", True, "A41"),
    ("R07.1", "Chest pain on breathing", True, "R07"),
    ("D64.9", "Anemia, unspecified", True, "D64"),
    ("D50.9", "Iron deficiency anemia, unspecified", True, "D50"),
    ("R63.4", "Abnormal weight loss", True, "R63"),
    ("E78.5", "Hyperlipidemia, unspecified", True, "E78"),
    ("E11.65", "Type 2 diabetes mellitus with hyperglycemia", True, "E11.6"),
    ("D22.9", "Melanocytic nevi, unspecified", True, "D22"),
    ("D22.5", "Melanocytic nevi of trunk", True, "D22"),
    ("K80.20", "Calculus of gallbladder without obstruction", True, "K80.2"),
    ("L72.0", "Epidermal cyst", True, "L72"),
    # Cardiology (added via the specialty accelerator — no engine changes)
    ("I35.0", "Nonrheumatic aortic (valve) stenosis", True, "I35"),
    ("I50.9", "Heart failure, unspecified", True, "I50"),
    ("I48.91", "Unspecified atrial fibrillation", True, "I48.9"),
    ("I25.10", "Atherosclerotic heart disease of native coronary artery without angina pectoris", True, "I25.1"),
    ("I20.9", "Angina pectoris, unspecified", True, "I20"),
    ("R00.2", "Palpitations", True, "R00"),
    ("R06.00", "Dyspnea, unspecified", True, "R06.0"),
    # non-billable parents (specificity gate should reject these)
    ("E11.4", "Type 2 diabetes mellitus with neurological complications", False, "E11"),
    ("M25.56", "Pain in knee", False, "M25.5"),
    ("S52.50", "Unspecified fracture of the lower end of radius", False, "S52.5"),
]

# --- CPT (DEMO_PLACEHOLDER) — (code, description, modality) ---
CPT = [
    ("71045", "Radiologic exam, chest; single view", "XR"),
    ("71046", "Radiologic exam, chest; 2 views", "XR"),
    ("73030", "Radiologic exam, shoulder; 2+ views", "XR"),
    ("73562", "Radiologic exam, knee; 3 views", "XR"),
    ("73564", "Radiologic exam, knee; 4 or more views", "XR"),
    ("73110", "Radiologic exam, wrist; 3+ views", "XR"),
    ("74018", "Radiologic exam, abdomen; single view", "XR"),
    ("70450", "CT, head or brain; without contrast", "CT"),
    ("70460", "CT, head or brain; with contrast", "CT"),
    ("71250", "CT, thorax; without contrast", "CT"),
    ("74150", "CT, abdomen; without contrast", "CT"),
    ("72192", "CT, pelvis; without contrast", "CT"),
    ("74176", "CT, abdomen and pelvis; without contrast", "CT"),
    ("74177", "CT, abdomen and pelvis; with contrast", "CT"),
    ("74178", "CT, abdomen and pelvis; without then with contrast", "CT"),
    ("72148", "MRI, lumbar spine; without contrast", "MRI"),
    ("72149", "MRI, lumbar spine; with contrast", "MRI"),
    ("73721", "MRI, lower extremity joint; without contrast", "MRI"),
    ("73221", "MRI, upper extremity joint; without contrast", "MRI"),
    ("70551", "MRI, brain; without contrast", "MRI"),
    ("71260", "CT, thorax; with contrast", "CT"),
    # E&M (established / new office visit)
    ("99213", "Office/outpatient visit, established patient, low MDM", "EM_OFFICE"),
    ("99214", "Office/outpatient visit, established patient, moderate MDM", "EM_OFFICE"),
    ("99215", "Office/outpatient visit, established patient, high MDM", "EM_OFFICE"),
    ("99203", "Office/outpatient visit, new patient, low MDM", "EM_OFFICE"),
    ("99204", "Office/outpatient visit, new patient, moderate MDM", "EM_OFFICE"),
    # Emergency Department E&M + critical care
    ("99281", "Emergency department visit, straightforward MDM", "ED"),
    ("99282", "Emergency department visit, low MDM", "ED"),
    ("99283", "Emergency department visit, moderate MDM", "ED"),
    ("99284", "Emergency department visit, high MDM", "ED"),
    ("99285", "Emergency department visit, high complexity MDM", "ED"),
    ("99291", "Critical care, evaluation and management; first 30-74 minutes", "ED"),
    ("99292", "Critical care; each additional 30 minutes", "ED"),
    # Pathology (surgical pathology / cytology) — DEMO placeholder
    ("88304", "Surgical pathology, gross and microscopic exam, level III", "PATH"),
    ("88305", "Surgical pathology, gross and microscopic exam, level IV", "PATH"),
    ("88307", "Surgical pathology, gross and microscopic exam, level V", "PATH"),
    ("88112", "Cytopathology, cell enhancement technique, interpretation", "PATH"),
    ("88342", "Immunohistochemistry, per specimen; initial single antibody stain", "PATH"),
    # Surgical (outpatient / ASC) — DEMO placeholder
    ("11402", "Excision, benign lesion incl margins, trunk/arms/legs; 1.1-2.0 cm", "SURG"),
    ("11602", "Excision, malignant lesion incl margins, trunk/arms/legs; 1.1-2.0 cm", "SURG"),
    ("12002", "Simple repair of superficial wounds; 2.6-7.5 cm", "SURG"),
    ("10060", "Incision and drainage of abscess; simple or single", "SURG"),
    ("20610", "Arthrocentesis/aspiration/injection, major joint or bursa", "SURG"),
    ("29881", "Arthroscopy, knee, surgical; with meniscectomy (medial OR lateral)", "SURG"),
    ("47562", "Laparoscopy, surgical; cholecystectomy", "SURG"),
    # Cardiology (non-invasive + diagnostic) — DEMO placeholder
    ("93306", "Echocardiography, transthoracic, complete, with spectral and color flow Doppler", "CARD"),
    ("93000", "Electrocardiogram, routine ECG with 12 leads; with interpretation and report", "CARD"),
    ("93017", "Cardiovascular stress test; tracing only, with supervision", "CARD"),
    ("93458", "Catheter placement, left heart; with coronary angiography and imaging supervision", "CARD"),
]

HCPCS = [
    ("Q9967", "Low osmolar contrast material, per ml", "ANY"),
    ("A9579", "Gadolinium-based MR contrast agent, per ml", "MRI"),
]

# --- Modifiers ---
MODIFIERS = [
    ("26", "Professional component", "CPT", "Reading/interpretation only (radiology PC)"),
    ("TC", "Technical component", "CPT", "Equipment/technical only"),
    ("59", "Distinct procedural service", "CPT", "Unbundles an NCCI pair when clinically distinct"),
    ("XU", "Unusual non-overlapping service", "CPT", "NCCI-associated X-modifier"),
    ("51", "Multiple procedures", "CPT", ""),
    ("50", "Bilateral procedure", "CPT", ""),
    ("RT", "Right side", "CPT", ""),
    ("LT", "Left side", "CPT", ""),
    ("25", "Significant, separately identifiable E&M", "CPT", "Same-day E&M with a procedure"),
    ("76", "Repeat procedure by same physician", "CPT", ""),
    ("58", "Staged/related procedure during postoperative period", "CPT", ""),
    ("78", "Unplanned return to OR for related procedure", "CPT", ""),
    ("79", "Unrelated procedure during postoperative period", "CPT", ""),
    ("80", "Assistant surgeon", "CPT", ""),
    ("82", "Assistant surgeon (no qualified resident available)", "CPT", ""),
    ("AS", "Physician assistant/NP/CNS as assistant at surgery", "CPT", ""),
    ("62", "Two surgeons (co-surgeons)", "CPT", ""),
    ("22", "Increased procedural services", "CPT", ""),
]

# --- NCCI PTP (column1 payable / column2 bundled). modifier_allowed True=can unbundle ---
NCCI = [
    ("74176", "74150", False, "CT abdomen is a component of combined CT abdomen+pelvis"),
    ("74176", "72192", False, "CT pelvis is a component of combined CT abdomen+pelvis"),
    ("74177", "74150", False, "CT abdomen component of combined w/contrast study"),
    ("74177", "72192", False, "CT pelvis component of combined w/contrast study"),
    ("71046", "71045", True, "Chest 2-view includes single-view; separate only if distinct"),
]

# --- MUE (max units/day) ---
MUE = [
    ("71046", 1, "Chest 2-view, one per day typical"),
    ("74177", 1, "CT abd+pelvis with contrast, one per day"),
    ("74176", 1, "CT abd+pelvis without contrast, one per day"),
    ("70450", 1, "CT head without contrast, one per day"),
    ("72148", 1, "MRI lumbar without contrast, one per day"),
    ("99291", 1, "Critical care first hour, one per day per provider"),
    ("99284", 1, "ED visit, one per encounter"),
    ("93306", 1, "Complete transthoracic echo, one per day typical"),
    ("93000", 1, "Routine 12-lead ECG, one per day typical"),
]

# --- Payer policy (representative) ---
PAYER_POLICY = [
    ("Medicare", "74177", "LCD: CT abd+pelvis with contrast requires documented indication (pain, mass, calculus).",
     False, "", ["R10", "N20", "R19", "C"]),
    ("Medicare", "72148", "NCD/LCD: MRI lumbar covered for radiculopathy/persistent LBP > 6 weeks.",
     False, "", ["M54", "M51", "G55"]),
    ("Anthem", "72148", "Prior authorization required for outpatient MRI lumbar spine.",
     True, "Auth # required on claim", ["M54", "M51"]),
    ("Cigna", "70460", "CT head with contrast requires clinical indication beyond routine headache.",
     False, "", ["R51", "S06", "C71", "I63"]),
    ("Medicare", "71046", "Chest 2-view covered for respiratory symptoms / abnormal findings.",
     False, "", ["R05", "R07", "J18", "R91"]),
    ("Medicare", "47562", "Laparoscopic cholecystectomy covered for symptomatic cholelithiasis / "
     "cholecystitis with documented stones.", False, "", ["K80", "K81", "K82"]),
    ("Anthem", "47562", "Prior authorization required for elective laparoscopic cholecystectomy.",
     True, "Auth # required on claim", ["K80", "K81"]),
    ("Medicare", "88305", "Surgical pathology (level IV) covered for excised tissue requiring "
     "microscopic diagnosis.", False, "", ["D22", "D23", "L72", "C44"]),
    ("Cigna", "99214", "Established E&M level 4 supported by moderate MDM documentation.",
     False, "", []),
    ("Medicare", "93306", "Echocardiography covered for evaluation of murmur, suspected structural "
     "heart disease, heart failure, or arrhythmia.", False, "", ["I35", "I50", "I48", "R00", "R01", "R06"]),
    ("Anthem", "93458", "Prior authorization required for elective left heart catheterization with "
     "coronary angiography.", True, "Auth # required on claim", ["I20", "I25"]),
]

# --- Medical ontology (concept graph for Graph-RAG) ---
# (cui, name, semantic_type, maps_to)
ONTOLOGY_CONCEPTS = [
    ("C0032285", "Pneumonia", "Disease", [{"system": "ICD10CM", "code": "J18.9"}]),
    ("C0008031", "Chest pain", "Sign or Symptom", [{"system": "ICD10CM", "code": "R07.9"}]),
    ("C0010200", "Cough", "Sign or Symptom", [{"system": "ICD10CM", "code": "R05.9"}]),
    ("C0022650", "Calculus of kidney", "Disease", [{"system": "ICD10CM", "code": "N20.0"}]),
    ("C0024031", "Low back pain", "Sign or Symptom", [{"system": "ICD10CM", "code": "M54.50"}]),
    ("C0011882", "Diabetic neuropathy", "Disease", [{"system": "ICD10CM", "code": "E11.40"}]),
    ("C0011860", "Type 2 diabetes mellitus", "Disease", [{"system": "ICD10CM", "code": "E11.9"}]),
    ("C0018681", "Headache", "Sign or Symptom", [{"system": "ICD10CM", "code": "R51.9"}]),
    ("C0024109", "Lung structure", "Body Part", []),
    ("C0205054", "Hilar region", "Body Part", []),
    ("C0002871", "Anemia", "Disease", [{"system": "ICD10CM", "code": "D64.9"}]),
    ("C0162316", "Iron deficiency anemia", "Disease", [{"system": "ICD10CM", "code": "D50.9"}]),
    ("C0001339", "Acute respiratory failure", "Disease", [{"system": "ICD10CM", "code": "J96.00"}]),
    ("C0027960", "Melanocytic nevus", "Disorder", [{"system": "ICD10CM", "code": "D22.5"}]),
    ("C0008350", "Cholelithiasis", "Disease", [{"system": "ICD10CM", "code": "K80.20"}]),
    ("C0016976", "Gallbladder structure", "Body Part", []),
    ("C1123023", "Skin structure", "Body Part", []),
    # Cardiology concepts (added with the specialty)
    ("C0018787", "Heart structure", "Body Part", []),
    ("C0018801", "Heart failure", "Disease", [{"system": "ICD10CM", "code": "I50.9"}]),
    ("C0004238", "Atrial fibrillation", "Disease", [{"system": "ICD10CM", "code": "I48.91"}]),
    ("C0003507", "Aortic valve stenosis", "Disease", [{"system": "ICD10CM", "code": "I35.0"}]),
    ("C0030252", "Palpitations", "Sign or Symptom", [{"system": "ICD10CM", "code": "R00.2"}]),
]
# (src_cui, rel, dst_cui)
ONTOLOGY_EDGES = [
    ("C0032285", "finding_site", "C0024109"),   # pneumonia -> lung
    ("C0032285", "associated_with", "C0010200"), # pneumonia -> cough
    ("C0008031", "associated_with", "C0032285"), # chest pain -> pneumonia
    ("C0011882", "is_a", "C0011860"),            # diabetic neuropathy -> T2DM
    ("C0022650", "finding_site", "C0024109"),
    ("C0162316", "is_a", "C0002871"),            # iron deficiency anemia -> anemia
    ("C0008350", "finding_site", "C0016976"),    # cholelithiasis -> gallbladder
    ("C0027960", "finding_site", "C1123023"),    # melanocytic nevus -> skin
    ("C0001339", "finding_site", "C0024109"),    # acute respiratory failure -> lung
    ("C0018801", "finding_site", "C0018787"),    # heart failure -> heart
    ("C0004238", "finding_site", "C0018787"),    # atrial fibrillation -> heart
    ("C0003507", "finding_site", "C0018787"),    # aortic stenosis -> heart
    ("C0004238", "associated_with", "C0030252"), # atrial fibrillation -> palpitations
]

# --- Guideline chunks (ICD-10-CM Official Guidelines are public domain; paraphrased) ---
GUIDELINES = [
    ("ICD-10-CM Official Guidelines", "I.B.18",
     "Uncertain diagnosis: Do not code conditions documented as 'probable', 'suspected', "
     "'questionable', 'rule out', or 'working diagnosis'. Code to the highest degree of certainty, "
     "e.g., signs/symptoms.", ""),
    ("ICD-10-CM Official Guidelines", "I.B.4",
     "Signs and symptoms: Codes for signs/symptoms are acceptable when a related definitive "
     "diagnosis has not been established.", ""),
    ("ICD-10-CM Official Guidelines", "I.A.15",
     "'With' should be interpreted to mean 'associated with' or 'due to'. Code linked conditions "
     "to the most specific combination code when documentation supports the relationship.", ""),
    ("Radiology Coding Guidance", "Contrast",
     "'With contrast' requires contrast administered intravascularly, intra-articularly, or "
     "intrathecally. Oral and/or rectal contrast alone is coded as 'without contrast'.", "Radiology"),
    ("Radiology Coding Guidance", "Combination",
     "When a combined study code exists (e.g., CT abdomen and pelvis), report the single combination "
     "code rather than the individual component codes.", "Radiology"),
    ("NCCI Policy Manual", "Ch.1",
     "Do not unbundle component services included in a comprehensive code. A modifier 59/X may be "
     "used only when services are distinct and supported by documentation.", ""),
    ("E&M Documentation Guidelines (2021)", "MDM",
     "E&M level selection is based on Medical Decision Making (number/complexity of problems, amount "
     "of data, risk) or total time. Do not infer specificity not documented.", "E&M"),
    ("Radiology Coding Guidance", "Components",
     "Modifier 26 reports the professional component (the physician's interpretation); modifier TC the "
     "technical component (equipment/technologist). For a radiologist's interpretation of imaging "
     "performed at a facility (POS 22 outpatient hospital, 23 emergency room), append modifier 26.", "Radiology"),
    ("Radiology Coding Guidance", "Laterality",
     "For unilateral extremity imaging, append RT (right) or LT (left) to identify the side imaged when "
     "the documentation specifies laterality.", "Radiology"),
    ("Radiology Coding Guidance", "Views",
     "Select the CPT that matches the documented number of views (e.g., single vs 2-view chest; 3-view "
     "vs 4+-view knee). Do not bill a higher view-count code than documented.", "Radiology"),
    ("Radiology Coding Guidance", "OrderingDx",
     "Link the imaging CPT to the diagnosis/indication from the order; when no definitive diagnosis is "
     "established on the read, code the sign/symptom that prompted the study.", "Radiology"),
    ("ED Coding Guidance", "Levels",
     "ED E&M (99281-99285) is leveled by Medical Decision Making. Critical care (99291, +99292 each "
     "additional 30 min) requires documentation of at least 30 minutes of critical care and a patient "
     "with high probability of imminent or life-threatening deterioration.", "ED"),
    ("Pathology Coding Guidance", "Levels",
     "Surgical pathology CPT (88300-88309) is selected by specimen and complexity level; a skin "
     "specimen examined microscopically is typically level IV (88305). Append modifier 26 for the "
     "pathologist's professional interpretation at a facility.", "Pathology"),
    ("Surgical Coding Guidance", "Modifiers",
     "Apply surgical modifiers: 51 multiple procedures, 59 distinct service, 78/79 return to OR, "
     "50/RT/LT laterality, 80/82/AS assistant surgeon, 58 staged. Honor the global surgical package "
     "and add-on-code rules; do not unbundle component services.", "Surgical"),
    ("Cardiology Coding Guidance", "Procedures",
     "Code the cardiac procedure documented: a complete transthoracic echocardiogram with Doppler is "
     "93306; a routine 12-lead ECG with interpretation is 93000. Append modifier 26 when only the "
     "physician's interpretation is performed at a facility. Code the cardiac diagnosis/indication "
     "(e.g., heart failure, valvular disease, arrhythmia); use a sign/symptom when no definitive "
     "diagnosis is established.", "Cardiology"),
]
