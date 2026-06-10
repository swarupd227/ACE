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
    # Orthopedics (added via the specialty accelerator — no engine changes)
    ("M17.11", "Unilateral primary osteoarthritis, right knee", True, "M17.1"),
    ("M17.12", "Unilateral primary osteoarthritis, left knee", True, "M17.1"),
    ("M75.101", "Incomplete rotator cuff tear/rupture of right shoulder, not specified as traumatic", True, "M75.10"),
    ("M75.102", "Incomplete rotator cuff tear/rupture of left shoulder, not specified as traumatic", True, "M75.10"),
    ("M23.205", "Derangement of unspecified meniscus due to old tear or injury, right knee", True, "M23.20"),
    # non-billable parents (specificity gate should reject these)
    ("M17.1", "Unilateral primary osteoarthritis of knee", False, "M17"),
    ("M75.10", "Unspecified rotator cuff tear or rupture, not specified as traumatic", False, "M75.1"),
    # OB/GYN (added via the specialty accelerator — no engine changes)
    ("Z34.82", "Encounter for supervision of normal pregnancy, second trimester", True, "Z34.8"),
    ("Z34.83", "Encounter for supervision of normal pregnancy, third trimester", True, "Z34.8"),
    ("N87.1", "Moderate cervical dysplasia (CIN II)", True, "N87"),
    ("N87.0", "Mild cervical dysplasia (CIN I)", True, "N87"),
    ("N93.9", "Abnormal uterine and vaginal bleeding, unspecified", True, "N93"),
    ("N83.20", "Unspecified ovarian cysts", True, "N83.2"),
    # non-billable parents (specificity gate should reject these)
    ("Z34.8", "Encounter for supervision of other normal pregnancy", False, "Z34"),
    ("N87", "Dysplasia of cervix uteri", False, "N87"),
    # GI / Endoscopy (added via the specialty accelerator — no engine changes)
    ("K63.5", "Polyp of colon", True, "K63"),
    ("K21.9", "Gastro-esophageal reflux disease without esophagitis", True, "K21"),
    ("K29.70", "Gastritis, unspecified, without bleeding", True, "K29.7"),
    ("K57.30", "Diverticulosis of large intestine without perforation or abscess, without bleeding", True, "K57.3"),
    ("Z12.11", "Encounter for screening for malignant neoplasm of colon", True, "Z12.1"),
    # non-billable parent (specificity gate should reject this)
    ("K29.7", "Gastritis, unspecified", False, "K29"),
    # Dermatology (added via the specialty accelerator — no engine changes)
    ("L57.0", "Actinic keratosis", True, "L57"),
    ("C44.91", "Basal cell carcinoma of skin, unspecified", True, "C44.9"),
    ("L82.1", "Other seborrheic keratosis", True, "L82"),
    ("B07.9", "Viral wart, unspecified", True, "B07"),
    ("D48.5", "Neoplasm of uncertain behavior of skin", True, "D48"),
    # non-billable parent (specificity gate should reject this)
    ("C44.9", "Other and unspecified malignant neoplasm of skin, unspecified", False, "C44"),
    # Urology (added via the specialty accelerator — no engine changes; N20.0 kidney stone reused)
    ("N40.1", "Benign prostatic hyperplasia with lower urinary tract symptoms", True, "N40"),
    ("N40.0", "Benign prostatic hyperplasia without lower urinary tract symptoms", True, "N40"),
    ("C67.9", "Malignant neoplasm of bladder, unspecified", True, "C67"),
    ("R31.9", "Hematuria, unspecified", True, "R31"),
    ("N39.0", "Urinary tract infection, site not specified", True, "N39"),
    ("N40", "Enlarged prostate", False, "N40"),  # non-billable parent
    # Ophthalmology
    ("H25.9", "Unspecified age-related cataract", True, "H25"),
    ("H35.30", "Unspecified macular degeneration", True, "H35.3"),
    ("H40.9", "Unspecified glaucoma", True, "H40"),
    ("H25", "Age-related cataract", False, "H25"),  # non-billable parent
    # ENT / Otolaryngology
    ("J35.3", "Hypertrophy of tonsils with hypertrophy of adenoids", True, "J35"),
    ("J35.1", "Hypertrophy of tonsils", True, "J35"),
    ("H65.23", "Chronic serous otitis media, bilateral", True, "H65.2"),
    ("J34.2", "Deviated nasal septum", True, "J34"),
    ("J32.9", "Chronic sinusitis, unspecified", True, "J32"),
    ("J35", "Chronic diseases of tonsils and adenoids", False, "J35"),  # non-billable parent
    ("H65.2", "Chronic serous otitis media", False, "H65.2"),           # non-billable parent
    # Inpatient / MS-DRG (principal + CC/MCC secondary dx; J96.00, A41.9, I50.9, E11.65, J18.9,
    # D64.9, I48.91 already defined above and reused)
    ("N17.9", "Acute kidney failure, unspecified", True, "N17"),
    ("I50.21", "Acute systolic (congestive) heart failure", True, "I50.2"),
    ("J44.1", "Chronic obstructive pulmonary disease with (acute) exacerbation", True, "J44"),
    ("N18.3", "Chronic kidney disease, stage 3 (moderate)", True, "N18"),
    ("C18.9", "Malignant neoplasm of colon, unspecified", True, "C18"),
    ("K56.609", "Unspecified intestinal obstruction", True, "K56.60"),
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
    # Orthopedics — DEMO placeholder (29881 arthroscopy + 20610 joint injection already
    # exist above and are reused via the generic retrieval path; add only net-new codes)
    ("27447", "Arthroplasty, knee, condyle and plateau; medial AND lateral compartments (total knee)", "ORTHO"),
    ("29826", "Arthroscopy, shoulder, surgical; decompression of subacromial space with partial acromioplasty", "ORTHO"),
    ("20550", "Injection(s); single tendon sheath, or ligament, aponeurosis", "ORTHO"),
    # OB/GYN — DEMO placeholder
    ("76805", "Ultrasound, pregnant uterus, >=14 weeks, transabdominal; single or first gestation", "OBGYN"),
    ("57454", "Colposcopy of the cervix with biopsy(s) of the cervix and endocervical curettage", "OBGYN"),
    ("58100", "Endometrial biopsy, without cervical dilation, any method (separate procedure)", "OBGYN"),
    ("58300", "Insertion of intrauterine device (IUD)", "OBGYN"),
    ("59400", "Routine obstetric care; antepartum care, vaginal delivery, and postpartum care (global)", "OBGYN"),
    # GI / Endoscopy — DEMO placeholder
    ("45378", "Colonoscopy, flexible; diagnostic, with or without collection of specimen(s)", "GI"),
    ("45380", "Colonoscopy, flexible; with biopsy, single or multiple", "GI"),
    ("45385", "Colonoscopy, flexible; with removal of lesion(s)/polyp(s) by snare technique", "GI"),
    ("43235", "Esophagogastroduodenoscopy (EGD), flexible; diagnostic", "GI"),
    ("43239", "Esophagogastroduodenoscopy (EGD), flexible; with biopsy, single or multiple", "GI"),
    # Dermatology — DEMO placeholder
    ("11102", "Tangential biopsy of skin (e.g., shave); single lesion", "DERM"),
    ("11104", "Punch biopsy of skin; single lesion", "DERM"),
    ("17000", "Destruction of premalignant lesion (e.g., actinic keratosis); first lesion", "DERM"),
    ("17110", "Destruction of benign lesions other than skin tags; up to 14 lesions", "DERM"),
    # Urology — DEMO placeholder
    ("50590", "Lithotripsy, extracorporeal shock wave (ESWL)", "URO"),
    ("52000", "Cystourethroscopy (separate procedure); diagnostic", "URO"),
    ("52234", "Cystourethroscopy with fulguration and/or resection of small bladder tumor(s)", "URO"),
    ("55700", "Biopsy of prostate; needle or punch, single or multiple", "URO"),
    ("51798", "Measurement of post-void residual urine by ultrasound, non-imaging", "URO"),
    # Anesthesia — DEMO placeholder
    ("00790", "Anesthesia for intraperitoneal procedures in upper abdomen (incl. lap cholecystectomy)", "ANES"),
    ("00840", "Anesthesia for intraperitoneal procedures in lower abdomen", "ANES"),
    ("01402", "Anesthesia for total knee arthroplasty", "ANES"),
    ("01967", "Neuraxial labor analgesia/anesthesia for planned vaginal delivery", "ANES"),
    # Anesthesia qualifying-circumstance add-ons — DEMO placeholder
    ("99100", "Anesthesia for patient of extreme age (under 1 year or over 70), add-on", "ANES"),
    ("99116", "Anesthesia complicated by utilization of total body hypothermia, add-on", "ANES"),
    ("99135", "Anesthesia complicated by utilization of controlled hypotension, add-on", "ANES"),
    ("99140", "Anesthesia complicated by emergency conditions, add-on", "ANES"),
    # Ophthalmology — DEMO placeholder
    ("66984", "Extracapsular cataract removal with insertion of intraocular lens prosthesis, 1 stage", "OPHTH"),
    ("67028", "Intravitreal injection of a pharmacologic agent", "OPHTH"),
    ("65855", "Trabeculoplasty by laser surgery", "OPHTH"),
    ("92134", "Scanning computerized ophthalmic diagnostic imaging, retina (OCT)", "OPHTH"),
    ("92014", "Ophthalmological exam and evaluation, comprehensive, established patient", "OPHTH"),
    # ENT / Otolaryngology — DEMO placeholder
    ("42820", "Tonsillectomy and adenoidectomy; younger than age 12", "ENT"),
    ("69436", "Tympanostomy (ventilating tube insertion), requiring general anesthesia", "ENT"),
    ("31231", "Nasal endoscopy, diagnostic, unilateral or bilateral (separate procedure)", "ENT"),
    ("30520", "Septoplasty or submucous resection, with or without cartilage scoring/contouring/replacement", "ENT"),
    ("31237", "Nasal/sinus endoscopy, surgical; with biopsy, polypectomy or debridement", "ENT"),
]

HCPCS = [
    ("Q9967", "Low osmolar contrast material, per ml", "ANY"),
    ("A9579", "Gadolinium-based MR contrast agent, per ml", "MRI"),
    # HCC / Risk Adjustment — annual wellness visits (real public G-codes)
    ("G0438", "Annual wellness visit; includes a personalized prevention plan of service, initial visit", "AWV"),
    ("G0439", "Annual wellness visit; includes a personalized prevention plan of service, subsequent visit", "AWV"),
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
    # Anesthesia physical-status modifiers
    ("P1", "A normal healthy patient", "anesthesia", ""),
    ("P2", "A patient with mild systemic disease", "anesthesia", ""),
    ("P3", "A patient with severe systemic disease", "anesthesia", ""),
    ("P4", "A patient with severe systemic disease that is a constant threat to life", "anesthesia", ""),
    ("P5", "A moribund patient not expected to survive without the operation", "anesthesia", ""),
    ("P6", "A declared brain-dead patient (organ donor)", "anesthesia", ""),
]

# --- NCCI PTP (column1 payable / column2 bundled). modifier_allowed True=can unbundle ---
NCCI = [
    ("74176", "74150", False, "CT abdomen is a component of combined CT abdomen+pelvis"),
    ("74176", "72192", False, "CT pelvis is a component of combined CT abdomen+pelvis"),
    ("74177", "74150", False, "CT abdomen component of combined w/contrast study"),
    ("74177", "72192", False, "CT pelvis component of combined w/contrast study"),
    ("71046", "71045", True, "Chest 2-view includes single-view; separate only if distinct"),
    ("45385", "45378", False, "Diagnostic colonoscopy is a component of colonoscopy with polypectomy; not separately reportable"),
    ("43239", "43235", False, "Diagnostic EGD is a component of EGD with biopsy; not separately reportable"),
    ("31237", "31231", False, "Diagnostic nasal endoscopy is a component of surgical nasal/sinus endoscopy; not separately reportable"),
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
    ("27447", 1, "Total knee arthroplasty, one per knee per day"),
    ("29826", 1, "Shoulder arthroscopic decompression, one per shoulder per day"),
    ("57454", 1, "Colposcopy with biopsy, one per day"),
    ("58100", 1, "Endometrial biopsy, one per day"),
    ("45385", 1, "Colonoscopy with polypectomy, one per day"),
    ("43239", 1, "EGD with biopsy, one per day"),
    ("11104", 1, "Punch biopsy single lesion, one per lesion"),
    ("17000", 1, "Destruction of first premalignant lesion, one per day"),
    ("50590", 1, "ESWL lithotripsy, one per day"),
    ("52234", 1, "Cystoscopy with bladder tumor resection, one per day"),
    ("66984", 1, "Cataract extraction with IOL, one per eye per day"),
    ("67028", 1, "Intravitreal injection, one per eye per day"),
    ("42820", 1, "Tonsillectomy and adenoidectomy, one per day"),
    ("69436", 1, "Tympanostomy tube insertion, reported once (bilateral via modifier 50)"),
    ("30520", 1, "Septoplasty, one per day"),
    ("31237", 1, "Surgical nasal/sinus endoscopy, one per day"),
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
    ("Medicare", "27447", "Total knee arthroplasty covered for severe osteoarthritis with functional "
     "limitation after failed conservative therapy.", False, "", ["M17"]),
    ("Anthem", "27447", "Prior authorization required for elective total knee arthroplasty.",
     True, "Auth # required on claim", ["M17"]),
    ("Anthem", "76805", "Obstetric ultrasound covered for pregnancy dating, viability and the fetal "
     "anatomy survey.", False, "", ["Z34", "O09", "O26"]),
    ("Medicare", "57454", "Colposcopy with cervical biopsy covered for abnormal cervical cytology or "
     "documented dysplasia.", False, "", ["N87", "R87"]),
    ("Medicare", "45385", "Colonoscopy with polypectomy covered for polyp, GI bleeding, or screening "
     "findings; report the most extensive technique performed.", False, "", ["K63", "Z12", "K57"]),
    ("Medicare", "43239", "EGD with biopsy covered for dyspepsia, reflux, or suspected mucosal disease "
     "requiring tissue diagnosis.", False, "", ["K21", "K29", "K25"]),
    ("Medicare", "17000", "Destruction of premalignant lesions (actinic keratosis) covered; first lesion "
     "17000, additional lesions reported separately.", False, "", ["L57"]),
    ("Medicare", "11104", "Skin biopsy covered for a lesion suspicious for malignancy or of uncertain "
     "behavior.", False, "", ["C44", "D48", "L82"]),
    ("Medicare", "50590", "ESWL covered for documented upper-urinary-tract calculus.", False, "", ["N20"]),
    ("Medicare", "52234", "Cystoscopy with resection covered for documented bladder tumor.", False, "", ["C67", "D41"]),
    ("Medicare", "00790", "Anesthesia covered with a documented covered surgical procedure and physical "
     "status; report base + time units.", False, "Physical status modifier required", ["K80", "K81"]),
    ("Medicare", "66984", "Cataract surgery with IOL covered for visually significant cataract with "
     "documented functional impairment.", False, "", ["H25", "H26"]),
    ("Medicare", "67028", "Intravitreal anti-VEGF injection covered for neovascular AMD or macular edema.",
     False, "", ["H35"]),
    ("Medicare", "42820", "Tonsillectomy with adenoidectomy covered for recurrent/chronic tonsillitis, "
     "adenotonsillar hypertrophy, or obstructive sleep-disordered breathing.", False, "", ["J35", "G47.3"]),
    ("Aetna", "69436", "Tympanostomy tube insertion covered for recurrent acute otitis media or chronic "
     "otitis media with effusion; report bilateral with modifier 50.", False, "Bilateral → modifier 50", ["H65", "H66"]),
    ("Anthem", "30520", "Prior authorization required for septoplasty; covered for symptomatic deviated "
     "nasal septum with nasal obstruction failing medical therapy.", True, "Auth # required on claim", ["J34.2"]),
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
    # Orthopedics concepts (added with the specialty)
    ("C0409959", "Osteoarthritis of knee", "Disease", [{"system": "ICD10CM", "code": "M17.11"}]),
    ("C0035328", "Rotator cuff tear", "Disease", [{"system": "ICD10CM", "code": "M75.101"}]),
    ("C0022742", "Knee joint structure", "Body Part", []),
    ("C0037004", "Shoulder joint structure", "Body Part", []),
    # OB/GYN concepts (added with the specialty)
    ("C0032961", "Pregnancy", "Finding", [{"system": "ICD10CM", "code": "Z34.82"}]),
    ("C0206630", "Cervical dysplasia", "Disease", [{"system": "ICD10CM", "code": "N87.1"}]),
    ("C0151706", "Abnormal uterine bleeding", "Sign or Symptom", [{"system": "ICD10CM", "code": "N93.9"}]),
    ("C0007874", "Cervix uteri structure", "Body Part", []),
    ("C0042149", "Uterine structure", "Body Part", []),
    # GI / Endoscopy concepts (added with the specialty)
    ("C0009376", "Colonic polyp", "Disease", [{"system": "ICD10CM", "code": "K63.5"}]),
    ("C0017168", "Gastroesophageal reflux disease", "Disease", [{"system": "ICD10CM", "code": "K21.9"}]),
    ("C0017152", "Gastritis", "Disease", [{"system": "ICD10CM", "code": "K29.70"}]),
    ("C0009368", "Colon structure", "Body Part", []),
    ("C0038351", "Stomach structure", "Body Part", []),
    # Dermatology concepts (added with the specialty; skin structure C1123023 already exists, reused)
    ("C0022602", "Actinic keratosis", "Disease", [{"system": "ICD10CM", "code": "L57.0"}]),
    ("C0007117", "Basal cell carcinoma", "Neoplastic Process", [{"system": "ICD10CM", "code": "C44.91"}]),
    # Urology + Ophthalmology concepts (added with the specialties)
    ("C0005695", "Malignant neoplasm of bladder", "Neoplastic Process", [{"system": "ICD10CM", "code": "C67.9"}]),
    ("C0005001", "Benign prostatic hyperplasia", "Disease", [{"system": "ICD10CM", "code": "N40.1"}]),
    ("C0005682", "Urinary bladder structure", "Body Part", []),
    ("C0033572", "Prostatic structure", "Body Part", []),
    ("C0086543", "Cataract", "Disease", [{"system": "ICD10CM", "code": "H25.9"}]),
    ("C0242383", "Age-related macular degeneration", "Disease", [{"system": "ICD10CM", "code": "H35.30"}]),
    ("C0015392", "Eye structure", "Body Part", []),
    # ENT / Otolaryngology concepts (added with the specialty)
    ("C0040421", "Tonsillar and adenoid hypertrophy", "Disease", [{"system": "ICD10CM", "code": "J35.3"}]),
    ("C0029883", "Otitis media with effusion", "Disease", [{"system": "ICD10CM", "code": "H65.23"}]),
    ("C0259779", "Deviated nasal septum", "Disease", [{"system": "ICD10CM", "code": "J34.2"}]),
    ("C0040408", "Palatine tonsil structure", "Body Part", []),
    ("C0025347", "Middle ear structure", "Body Part", []),
    ("C0028429", "Nasal septum structure", "Body Part", []),
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
    ("C0409959", "finding_site", "C0022742"),    # knee osteoarthritis -> knee joint
    ("C0035328", "finding_site", "C0037004"),    # rotator cuff tear -> shoulder joint
    ("C0206630", "finding_site", "C0007874"),    # cervical dysplasia -> cervix
    ("C0151706", "finding_site", "C0042149"),    # abnormal uterine bleeding -> uterus
    ("C0009376", "finding_site", "C0009368"),    # colonic polyp -> colon
    ("C0017152", "finding_site", "C0038351"),    # gastritis -> stomach
    ("C0022602", "finding_site", "C1123023"),    # actinic keratosis -> skin
    ("C0007117", "finding_site", "C1123023"),    # basal cell carcinoma -> skin
    ("C0005695", "finding_site", "C0005682"),    # bladder cancer -> bladder
    ("C0005001", "finding_site", "C0033572"),    # BPH -> prostate
    ("C0086543", "finding_site", "C0015392"),    # cataract -> eye
    ("C0242383", "finding_site", "C0015392"),    # AMD -> eye
    ("C0040421", "finding_site", "C0040408"),    # adenotonsillar hypertrophy -> palatine tonsil
    ("C0029883", "finding_site", "C0025347"),    # otitis media with effusion -> middle ear
    ("C0259779", "finding_site", "C0028429"),    # deviated nasal septum -> nasal septum
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
    ("Orthopedics Coding Guidance", "Procedures",
     "Code the orthopedic procedure documented in the operative/procedure note: total knee arthroplasty "
     "(medial AND lateral compartments) = 27447; arthroscopic subacromial decompression = 29826; "
     "arthroscopic knee meniscectomy = 29881; major-joint aspiration/injection = 20610. Append RT/LT for "
     "laterality. For osteoarthritis, code primary (M17.1x) unless post-traumatic or secondary is "
     "documented; honor the global surgical package and do not unbundle.", "Orthopedics"),
    ("OB/GYN Coding Guidance", "Procedures",
     "Code the OB/GYN service documented: obstetric ultrasound (>=14 weeks, transabdominal) = 76805; "
     "colposcopy of the cervix with biopsy = 57454; endometrial biopsy = 58100; IUD insertion = 58300. "
     "For routine pregnancy supervision, use Z34.8x by trimester (not an O-code) when uncomplicated. "
     "Code cervical dysplasia to specificity (CIN I = N87.0, CIN II = N87.1). When one provider gives "
     "antepartum + delivery + postpartum care, use the global obstetric package (e.g., 59400) rather than "
     "itemizing visits.", "OB/GYN"),
    ("GI Endoscopy Coding Guidance", "Procedures",
     "Report the most extensive endoscopic service performed in a session: colonoscopy with snare "
     "polypectomy = 45385; colonoscopy with biopsy = 45380; diagnostic colonoscopy = 45378; EGD with "
     "biopsy = 43239; diagnostic EGD = 43235. Do NOT separately report the diagnostic scope (45378/43235) "
     "when a therapeutic procedure is done in the same session. Code the finding (e.g., colon polyp K63.5, "
     "gastritis K29.70); for a screening colonoscopy that finds a polyp, sequence the screening Z-code "
     "first.", "GI / Endoscopy"),
    ("Dermatology Coding Guidance", "Procedures",
     "Code the dermatologic procedure performed: shave/tangential biopsy = 11102; punch biopsy = 11104; "
     "destruction of a premalignant lesion (actinic keratosis), first lesion = 17000; destruction of benign "
     "lesions (e.g., warts), up to 14 = 17110. When a biopsy and a same-lesion destruction/excision are done "
     "together, the biopsy is bundled — report only the more extensive service. Code the lesion diagnosis "
     "(e.g., actinic keratosis L57.0, basal cell carcinoma C44.91); use 'uncertain behavior' (D48.5) when "
     "biopsying before a histologic diagnosis.", "Dermatology"),
    ("Urology Coding Guidance", "Procedures",
     "Code the urologic procedure performed: ESWL lithotripsy = 50590; diagnostic cystourethroscopy = "
     "52000; cystoscopy with bladder-tumor resection = 52234; needle prostate biopsy = 55700. Code the "
     "finding (calculus N20.x, bladder neoplasm C67.9, BPH N40.0/N40.1, hematuria R31.9). Diagnostic "
     "cystoscopy is bundled into a same-session therapeutic cystoscopy — do not report both.", "Urology"),
    ("Anesthesia Coding Guidance", "Units",
     "Report the anesthesia CPT for the procedure being anesthetized (e.g., 00790 upper-abdomen / lap "
     "cholecystectomy, 01402 total knee, 01967 labor epidural) and code the underlying diagnosis. Append "
     "the physical-status modifier (P1-P6). Payment is base units + time units (each 15 min); record "
     "anesthesia start/stop time.", "Anesthesia"),
    ("Ophthalmology Coding Guidance", "Procedures",
     "Code the ophthalmic procedure: cataract extraction with IOL = 66984; intravitreal injection = 67028; "
     "laser trabeculoplasty = 65855; OCT of the retina = 92134. Append eye laterality (RT/LT) when "
     "documented. Code the diagnosis (cataract H25.x, macular degeneration H35.3x, glaucoma H40.x); cataract "
     "surgery requires documented visual/functional impairment.", "Ophthalmology"),
    ("ENT/Otolaryngology Coding Guidance", "Procedures",
     "Code the otolaryngology procedure documented: tonsillectomy with adenoidectomy (<12 yrs) = 42820; "
     "bilateral tympanostomy tube insertion = 69436 (append modifier 50 for bilateral); diagnostic nasal "
     "endoscopy = 31231; septoplasty = 30520; surgical nasal/sinus endoscopy with polypectomy = 31237. A "
     "diagnostic nasal endoscopy is bundled into a same-session surgical sinus endoscopy — do not report "
     "both. Code the diagnosis (adenotonsillar hypertrophy J35.3, chronic otitis media with effusion "
     "H65.23, deviated nasal septum J34.2) and capture ear laterality.", "ENT"),
    ("HCC Risk Adjustment Coding Guidance", "Capture",
     "Risk-adjustment coding captures every chronic condition that is active and addressed at the "
     "encounter with MEAT evidence (Monitored, Evaluated, Assessed, or Treated). Code combination codes "
     "to full specificity (diabetes WITH its complication, e.g. E11.42, not E11.9 plus a separate "
     "neuropathy code). Do not code historical or resolved conditions as active, and do not infer a "
     "diagnosis from medications alone. Conditions must be re-documented each calendar year to "
     "risk-adjust. The annual wellness visit is reported with G0438 (initial) or G0439 (subsequent).",
     "HCC / Risk Adjustment"),
]


# ===========================================================================
# Inpatient / MS-DRG reference data (Tier-B: structurally different from
# outpatient CPT). ICD-10-PCS, the MS-DRG table, CC/MCC lists, the MDC
# assignment and the OR-procedure list are all PUBLIC CMS artifacts (unlike
# CPT). Curated demo subset; the grouper algorithm is real. Production swaps in
# the full CMS definitions / a certified grouper behind the same interface.
# ===========================================================================

# --- ICD-10-PCS procedures (public; 7-character multi-axial) — (code, description, tag) ---
ICD10PCS = [
    ("0DTN0ZZ", "Resection of Sigmoid Colon, Open Approach", "PCS"),
    ("0DTP0ZZ", "Resection of Rectum, Open Approach", "PCS"),
    ("0DBN0ZZ", "Excision of Sigmoid Colon, Open Approach", "PCS"),
    ("0BJ08ZZ", "Inspection of Tracheobronchial Tree, Via Natural or Artificial Opening Endoscopic", "PCS"),
]

# --- MS-DRG table — (drg, title, mdc, mdc_title, type, base_key, severity, weight) ---
# Representative CMS relative weights; three severity tiers per base family.
DRG_DEFS = [
    ("193", "Simple Pneumonia & Pleurisy with MCC", "04",
     "Diseases & Disorders of the Respiratory System", "MED", "PNEUMONIA", "MCC", 1.4196),
    ("194", "Simple Pneumonia & Pleurisy with CC", "04",
     "Diseases & Disorders of the Respiratory System", "MED", "PNEUMONIA", "CC", 0.9688),
    ("195", "Simple Pneumonia & Pleurisy without CC/MCC", "04",
     "Diseases & Disorders of the Respiratory System", "MED", "PNEUMONIA", "NONE", 0.7090),
    ("291", "Heart Failure & Shock with MCC", "05",
     "Diseases & Disorders of the Circulatory System", "MED", "HEART_FAILURE", "MCC", 1.3454),
    ("292", "Heart Failure & Shock with CC", "05",
     "Diseases & Disorders of the Circulatory System", "MED", "HEART_FAILURE", "CC", 0.9534),
    ("293", "Heart Failure & Shock without CC/MCC", "05",
     "Diseases & Disorders of the Circulatory System", "MED", "HEART_FAILURE", "NONE", 0.6762),
    ("329", "Major Small & Large Bowel Procedures with MCC", "06",
     "Diseases & Disorders of the Digestive System", "SURG", "BOWEL_PROC", "MCC", 5.2520),
    ("330", "Major Small & Large Bowel Procedures with CC", "06",
     "Diseases & Disorders of the Digestive System", "SURG", "BOWEL_PROC", "CC", 2.6109),
    ("331", "Major Small & Large Bowel Procedures without CC/MCC", "06",
     "Diseases & Disorders of the Digestive System", "SURG", "BOWEL_PROC", "NONE", 1.7249),
]

# --- CC / MCC severity list — (code, tier) ---
CC_MCC = [
    ("J96.00", "MCC"),  # acute respiratory failure
    ("A41.9", "MCC"),   # sepsis
    ("N17.9", "MCC"),   # acute kidney failure
    ("E11.65", "CC"),   # diabetes with hyperglycemia
    ("D64.9", "CC"),    # anemia, unspecified
    ("J44.1", "CC"),    # COPD with acute exacerbation
    ("N18.3", "CC"),    # CKD stage 3
    ("I48.91", "CC"),   # atrial fibrillation
]

# --- MDC assignment from principal dx — (dx_prefix, mdc, mdc_title, medical_base_key) ---
DX_MDC = [
    ("J18", "04", "Diseases & Disorders of the Respiratory System", "PNEUMONIA"),
    ("I50", "05", "Diseases & Disorders of the Circulatory System", "HEART_FAILURE"),
    ("C18", "06", "Diseases & Disorders of the Digestive System", "BOWEL"),
    ("K56", "06", "Diseases & Disorders of the Digestive System", "BOWEL"),
    ("K57", "06", "Diseases & Disorders of the Digestive System", "BOWEL"),
]

# --- OR procedures — (pcs_code, surgical_base_key, mdc) ---
OR_PROC = [
    ("0DTN0ZZ", "BOWEL_PROC", "06"),
    ("0DTP0ZZ", "BOWEL_PROC", "06"),
    ("0DBN0ZZ", "BOWEL_PROC", "06"),
]


# ===========================================================================
# HCC / Risk Adjustment reference data (Tier-B #2). The CMS-HCC model —
# dx→HCC mappings, hierarchies, coefficients and demographic factors — is a
# PUBLIC CMS artifact published annually (like the DRG tables, unlike CPT).
# Curated V24 community/non-dual/aged subset; the RAF scorer is real.
# Strategic fit: Vee's RevCap is HCC-focused — ACE extends what they already do.
# ===========================================================================

# --- HCC condition categories — (hcc, label, coefficient[CNA]) ---
HCC_CATEGORIES = [
    ("17", "Diabetes with Acute Complications", 0.302),
    ("18", "Diabetes with Chronic Complications", 0.302),
    ("19", "Diabetes without Complication", 0.105),
    ("85", "Congestive Heart Failure", 0.331),
    ("96", "Specified Heart Arrhythmias", 0.268),
    ("111", "Chronic Obstructive Pulmonary Disease", 0.335),
    ("138", "Chronic Kidney Disease, Moderate (Stage 3)", 0.069),
    ("11", "Colorectal, Bladder, and Other Cancers", 0.307),
    ("12", "Breast, Prostate, and Other Cancers and Tumors", 0.150),
]

# --- ICD-10-CM → HCC mapping — (dx_code, hcc) ---
DX_HCC = [
    ("E11.9", "19"),
    ("E11.40", "18"),
    ("E11.42", "18"),
    ("E11.65", "18"),
    ("I50.9", "85"),
    ("I50.21", "85"),
    ("I48.91", "96"),
    ("J44.1", "111"),
    ("N18.3", "138"),
    ("C18.9", "11"),
    ("C67.9", "11"),
]

# --- Hierarchies — (superior_hcc, suppressed_hcc): superior wins when both map ---
HCC_HIER = [
    ("17", "18"),
    ("17", "19"),
    ("18", "19"),
    ("11", "12"),
]

# --- Demographic base factors (community, non-dual, aged) — (sex, age_min, age_max, factor) ---
DEMO_FACTORS = [
    ("M", 65, 69, 0.312),
    ("F", 65, 69, 0.323),
    ("M", 70, 74, 0.379),
    ("F", 70, 74, 0.395),
    ("M", 75, 79, 0.491),
    ("F", 75, 79, 0.492),
]


# ===========================================================================
# Anesthesia unit calculation (Tier-B #3). Anesthesia is paid as
# (base + time + modifying units) × conversion factor — NOT as CPT line-items.
# The CMS anesthesia base-unit file and conversion factor are PUBLIC artifacts.
# Curated subset for the seeded codes; the calculator is real.
# ===========================================================================

# --- CMS base units per anesthesia code — (code, base_units) ---
ANES_BASE_UNITS = [
    ("00790", 7),   # upper-abdomen intraperitoneal (incl. lap chole)
    ("00840", 6),   # lower-abdomen intraperitoneal
    ("01402", 7),   # total knee arthroplasty
    ("01967", 5),   # neuraxial labor analgesia
]

# --- Qualifying circumstances — (code, units, description) ---
QUAL_CIRC = [
    ("99100", 1, "Patient of extreme age (under 1 year or over 70)"),
    ("99116", 5, "Total body hypothermia"),
    ("99135", 5, "Controlled hypotension"),
    ("99140", 2, "Emergency conditions"),
]
