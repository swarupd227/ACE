"""Reference data for the demo.

PROVENANCE (honest by design):
- ICD-10-CM : REAL, public-domain (CMS/NCHS) — curated subset for Radiology + E&M,
              expanded with common radiology indications (signs/symptoms + findings).
- HCPCS L2  : REAL, public-d
omain (CMS) — incl. iodinated/gadolinium contrast + radiopharm.
- CPT       : DEMO_PLACEHOLDER. The 70000-series radiology numbers are widely-published
              facts (verified against CMS/AAPC fee-schedule references), but the
              descriptors here are our own paraphrase, NOT AMA's copyrighted text.
              Swap in a licensed AMA distribution for production (same table shape).
              Now covers X-ray, CT/CTA, MRI/MRA, Ultrasound, Doppler/duplex, mammography
              and DXA across head/neck, chest, spine, abdomen/pelvis and extremities.
- NCCI/MUE  : modeled on REAL CMS edit logic (component coding, one-per-day defaults), subset.
- APC/OPPS  : representative national amounts grouped into the published imaging-level
              buckets; the packaging/discounting logic is real.
- Payer policy / ontology / guidelines : representative, clearly-labeled.

Inpatient (MS-DRG), HCC and anesthesia tables are intentionally NOT expanded here:
their precise weights/coefficients/base-units are external CMS artifacts that must be
loaded from the official files rather than recalled, and partial expansion would risk
grouper inconsistency. They keep their existing curated subsets.
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

    # =======================================================================
    # RADIOLOGY INDICATIONS EXPANSION — REAL public-domain ICD-10-CM
    # (CMS/NCHS). Common signs/symptoms and findings that prompt imaging, so
    # the agent can code the ordering indication when no definitive dx exists.
    # =======================================================================
    # Abdominal pain by quadrant (drives CT/US abdomen)
    ("R10.11", "Right upper quadrant pain", True, "R10.1"),
    ("R10.12", "Left upper quadrant pain", True, "R10.1"),
    ("R10.13", "Epigastric pain", True, "R10.1"),
    ("R10.31", "Right lower quadrant pain", True, "R10.3"),
    ("R10.32", "Left lower quadrant pain", True, "R10.3"),
    ("R10.30", "Lower abdominal pain, unspecified", True, "R10.3"),
    ("R10.0", "Acute abdomen", True, "R10"),
    ("R19.00", "Intra-abdominal and pelvic swelling, mass and lump, unspecified site", True, "R19.0"),
    ("R19.8", "Other specified symptoms and signs involving the digestive system and abdomen", True, "R19"),
    ("R16.0", "Hepatomegaly, not elsewhere classified", True, "R16"),
    ("R16.1", "Splenomegaly, not elsewhere classified", True, "R16"),
    ("R18.8", "Other ascites", True, "R18"),
    ("K92.2", "Gastrointestinal hemorrhage, unspecified", True, "K92"),
    # Chest / pulmonary imaging indications & findings
    ("R91.1", "Solitary pulmonary nodule", True, "R91"),
    ("J90", "Pleural effusion, not elsewhere classified", True, ""),
    ("J98.11", "Atelectasis", True, "J98.1"),
    ("R09.1", "Pleurisy", True, "R09"),
    ("I26.99", "Other pulmonary embolism without acute cor pulmonale", True, "I26.9"),
    ("C34.90", "Malignant neoplasm of unspecified part of unspecified bronchus or lung", True, "C34.9"),
    # Spine / musculoskeletal imaging indications
    ("M54.12", "Radiculopathy, cervical region", True, "M54.1"),
    ("M54.16", "Radiculopathy, lumbar region", True, "M54.1"),
    ("M54.17", "Radiculopathy, lumbosacral region", True, "M54.1"),
    ("M54.2", "Cervicalgia", True, "M54"),
    ("M54.6", "Pain in thoracic spine", True, "M54"),
    ("M54.9", "Dorsalgia, unspecified", True, "M54"),
    ("M51.26", "Other intervertebral disc displacement, lumbar region", True, "M51.2"),
    ("M48.06", "Spinal stenosis, lumbar region", True, "M48.0"),
    ("M25.511", "Pain in right shoulder", True, "M25.51"),
    ("M25.512", "Pain in left shoulder", True, "M25.51"),
    # Neuro imaging indications (R51.9 headache already defined above and reused)
    ("R55", "Syncope and collapse", True, ""),
    ("R56.9", "Unspecified convulsions", True, "R56"),
    ("G45.9", "Transient cerebral ischemic attack, unspecified", True, "G45"),
    ("I63.9", "Cerebral infarction, unspecified", True, "I63"),
    # Vascular / Doppler indications
    ("I71.4", "Abdominal aortic aneurysm, without rupture", True, "I71"),
    ("I73.9", "Peripheral vascular disease, unspecified", True, "I73"),
    ("I65.23", "Occlusion and stenosis of bilateral carotid arteries", True, "I65.2"),
    ("I82.409", "Acute embolism and thrombosis of unspecified deep veins of unspecified lower extremity", True, "I82.40"),
    # GU / renal imaging indications
    ("N13.30", "Unspecified hydronephrosis", True, "N13.3"),
    ("N28.1", "Cyst of kidney, acquired", True, "N28"),
    ("R31.0", "Gross hematuria", True, "R31"),
    # Thyroid / neck US indications
    ("E04.1", "Nontoxic single thyroid nodule", True, "E04"),
    ("E04.2", "Nontoxic multinodular goiter", True, "E04"),
    # Breast imaging indications
    ("N63.0", "Unspecified lump in unspecified breast", True, "N63"),
    ("R92.8", "Other abnormal and inconclusive findings on diagnostic imaging of breast", True, "R92"),
    ("Z12.31", "Encounter for screening mammogram for malignant neoplasm of breast", True, "Z12.3"),
    # Constitutional / lymphatic imaging indications
    ("R50.9", "Fever, unspecified", True, "R50"),
    ("R59.0", "Localized enlarged lymph nodes", True, "R59"),
    ("R59.1", "Generalized enlarged lymph nodes", True, "R59"),
    # Abnormal imaging finding codes (when the read itself is the codable result)
    ("R93.5", "Abnormal findings on diagnostic imaging of other abdominal regions, including retroperitoneum", True, "R93"),
    ("R93.89", "Abnormal findings on diagnostic imaging of other specified body structures", True, "R93.8"),
    # non-billable parents (specificity gate should reject these)
    ("R10.1", "Pain localized to upper abdomen", False, "R10"),
    ("R10.3", "Pain localized to other parts of lower abdomen", False, "R10"),
    ("M54.1", "Radiculopathy", False, "M54"),
    ("E04", "Other nontoxic goiter", False, "E04"),

    # =======================================================================
    # TRAUMA / INJURY EXPANSION — Chapter 19 fractures/dislocations/sprains ('S')
    # + Chapter 20 external-cause transport accidents ('V'). REAL public-domain
    # ICD-10-CM (CMS/NCHS), verified against the NLM Clinical Tables ICD-10-CM API
    # (clinicaltables.nlm.nih.gov). These are the bread-and-butter of trauma imaging
    # (XR/CT/MRI) and also feed ED and Orthopedics.
    #
    # 7th character 'A' = INITIAL ENCOUNTER for CLOSED fracture — the dominant
    # scenario in diagnostic imaging. 'X' is the required placeholder so the 7th
    # character lands in the 7th position. Laterality (right/left/unspecified) is
    # coded where documented. V (external-cause) codes describe the MECHANISM of
    # injury and are ALWAYS SECONDARY — never first-listed/principal.
    # =======================================================================
    # --- Skull / facial fractures (head CT / facial XR) ---
    ("S02.0XXA", "Fracture of vault of skull, initial encounter for closed fracture", True, "S02.0"),
    ("S02.109A", "Fracture of base of skull, unspecified side, initial encounter for closed fracture", True, "S02.10"),
    ("S02.2XXA", "Fracture of nasal bones, initial encounter for closed fracture", True, "S02.2"),
    # --- Spine fractures (CT/MRI spine; osteoporotic compression common in elderly) ---
    ("S22.009A", "Unspecified fracture of unspecified thoracic vertebra, initial encounter for closed fracture", True, "S22.00"),
    ("S32.009A", "Unspecified fracture of unspecified lumbar vertebra, initial encounter for closed fracture", True, "S32.00"),
    ("S32.010A", "Wedge compression fracture of first lumbar vertebra, initial encounter for closed fracture", True, "S32.01"),
    # --- Rib fracture (chest XR/CT) ---
    ("S22.39XA", "Fracture of one rib, unspecified side, initial encounter for closed fracture", True, "S22.39"),
    # --- Clavicle / shoulder / humerus (shoulder XR 73030) ---
    ("S42.001A", "Fracture of unspecified part of right clavicle, initial encounter for closed fracture", True, "S42.00"),
    ("S42.002A", "Fracture of unspecified part of left clavicle, initial encounter for closed fracture", True, "S42.00"),
    ("S42.009A", "Fracture of unspecified part of unspecified clavicle, initial encounter for closed fracture", True, "S42.00"),
    ("S42.201A", "Unspecified fracture of upper end of right humerus, initial encounter for closed fracture", True, "S42.20"),
    ("S42.202A", "Unspecified fracture of upper end of left humerus, initial encounter for closed fracture", True, "S42.20"),
    ("S42.301A", "Unspecified fracture of shaft of humerus, right arm, initial encounter for closed fracture", True, "S42.30"),
    ("S42.302A", "Unspecified fracture of shaft of humerus, left arm, initial encounter for closed fracture", True, "S42.30"),
    # --- Forearm / wrist (wrist XR 73110); S52.501A right radius already defined above ---
    ("S52.502A", "Unspecified fracture of the lower end of left radius, initial encounter for closed fracture", True, "S52.50"),
    ("S52.509A", "Unspecified fracture of the lower end of unspecified radius, initial encounter for closed fracture", True, "S52.50"),
    ("S52.531A", "Colles' fracture of right radius, initial encounter for closed fracture", True, "S52.53"),
    ("S52.532A", "Colles' fracture of left radius, initial encounter for closed fracture", True, "S52.53"),
    ("S52.601A", "Unspecified fracture of lower end of right ulna, initial encounter for closed fracture", True, "S52.60"),
    ("S52.602A", "Unspecified fracture of lower end of left ulna, initial encounter for closed fracture", True, "S52.60"),
    ("S62.001A", "Unspecified fracture of navicular [scaphoid] bone of right wrist, initial encounter for closed fracture", True, "S62.00"),
    ("S62.002A", "Unspecified fracture of navicular [scaphoid] bone of left wrist, initial encounter for closed fracture", True, "S62.00"),
    ("S62.300A", "Unspecified fracture of second metacarpal bone, right hand, initial encounter for closed fracture", True, "S62.30"),
    ("S62.301A", "Unspecified fracture of second metacarpal bone, left hand, initial encounter for closed fracture", True, "S62.30"),
    # --- Hip / femur (hip XR / pelvis CT; fragility fracture in elderly) ---
    ("S72.001A", "Fracture of unspecified part of neck of right femur, initial encounter for closed fracture", True, "S72.00"),
    ("S72.002A", "Fracture of unspecified part of neck of left femur, initial encounter for closed fracture", True, "S72.00"),
    ("S72.009A", "Fracture of unspecified part of neck of unspecified femur, initial encounter for closed fracture", True, "S72.00"),
    ("S72.301A", "Unspecified fracture of shaft of right femur, initial encounter for closed fracture", True, "S72.30"),
    ("S72.302A", "Unspecified fracture of shaft of left femur, initial encounter for closed fracture", True, "S72.30"),
    # --- Knee / lower leg (knee XR 73562) ---
    ("S82.101A", "Unspecified fracture of upper end of right tibia, initial encounter for closed fracture", True, "S82.10"),
    ("S82.102A", "Unspecified fracture of upper end of left tibia, initial encounter for closed fracture", True, "S82.10"),
    ("S82.201A", "Unspecified fracture of shaft of right tibia, initial encounter for closed fracture", True, "S82.20"),
    ("S82.202A", "Unspecified fracture of shaft of left tibia, initial encounter for closed fracture", True, "S82.20"),
    ("S82.401A", "Unspecified fracture of shaft of right fibula, initial encounter for closed fracture", True, "S82.40"),
    ("S82.402A", "Unspecified fracture of shaft of left fibula, initial encounter for closed fracture", True, "S82.40"),
    # --- Ankle malleolus (ankle XR) ---
    ("S82.61XA", "Displaced fracture of lateral malleolus of right fibula, initial encounter for closed fracture", True, "S82.6"),
    ("S82.62XA", "Displaced fracture of lateral malleolus of left fibula, initial encounter for closed fracture", True, "S82.6"),
    ("S82.51XA", "Displaced fracture of medial malleolus of right tibia, initial encounter for closed fracture", True, "S82.5"),
    ("S82.52XA", "Displaced fracture of medial malleolus of left tibia, initial encounter for closed fracture", True, "S82.5"),
    # --- Foot (foot XR) ---
    ("S92.001A", "Unspecified fracture of right calcaneus, initial encounter for closed fracture", True, "S92.00"),
    ("S92.002A", "Unspecified fracture of left calcaneus, initial encounter for closed fracture", True, "S92.00"),
    ("S92.301A", "Fracture of unspecified metatarsal bone(s), right foot, initial encounter for closed fracture", True, "S92.30"),
    ("S92.302A", "Fracture of unspecified metatarsal bone(s), left foot, initial encounter for closed fracture", True, "S92.30"),
    # --- Dislocations / sprains (MRI/US joints; 7th char 'A' = initial encounter) ---
    ("S43.004A", "Unspecified dislocation of right shoulder joint, initial encounter", True, "S43.00"),
    ("S83.511A", "Sprain of anterior cruciate ligament of right knee, initial encounter", True, "S83.51"),
    ("S83.512A", "Sprain of anterior cruciate ligament of left knee, initial encounter", True, "S83.51"),
    ("S83.241A", "Other tear of medial meniscus, current injury, right knee, initial encounter", True, "S83.24"),
    ("S83.242A", "Other tear of medial meniscus, current injury, left knee, initial encounter", True, "S83.24"),
    ("S93.401A", "Sprain of unspecified ligament of right ankle, initial encounter", True, "S93.40"),
    ("S93.402A", "Sprain of unspecified ligament of left ankle, initial encounter", True, "S93.40"),
    # --- External cause: transport accidents (Chapter 20 'V') — ALWAYS SECONDARY ---
    ("V03.10XA", "Pedestrian on foot injured in collision with car, pick-up truck or van in traffic accident, initial encounter", True, "V03.1"),
    ("V13.4XXA", "Pedal cycle driver injured in collision with car, pick-up truck or van in traffic accident, initial encounter", True, "V13.4"),
    ("V27.49XA", "Other motorcycle driver injured in collision with fixed or stationary object in traffic accident, initial encounter", True, "V27.49"),
    ("V43.52XA", "Car driver injured in collision with other type car in traffic accident, initial encounter", True, "V43.52"),
    ("V43.62XA", "Car passenger injured in collision with other type car in traffic accident, initial encounter", True, "V43.62"),
    ("V47.5XXA", "Car driver injured in collision with fixed or stationary object in traffic accident, initial encounter", True, "V47.5"),
    ("V89.2XXA", "Person injured in unspecified motor-vehicle accident, traffic, initial encounter", True, "V89.2"),
    # non-billable parents (specificity gate should reject these in favor of the laterality codes)
    ("S42.00", "Fracture of unspecified part of clavicle", False, "S42.0"),
    ("S72.00", "Fracture of unspecified part of neck of femur", False, "S72.0"),
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

    # =======================================================================
    # RADIOLOGY EXPANSION (DEMO_PLACEHOLDER) — real, widely-published CPT
    # numbers (verified against CMS/AAPC fee-schedule references); descriptors
    # are our own paraphrase, NOT AMA's copyrighted text. Modality tags drive
    # the Radiology retrieval filter: XR / CT / MRI / US / MG.
    # =======================================================================

    # --- Plain radiography · head & neck (XR) ---
    ("70140", "Radiologic exam, facial bones; fewer than 3 views", "XR"),
    ("70150", "Radiologic exam, facial bones; complete, minimum 3 views", "XR"),
    ("70160", "Radiologic exam, nasal bones; complete", "XR"),
    ("70210", "Radiologic exam, paranasal sinuses; fewer than 3 views", "XR"),
    ("70220", "Radiologic exam, paranasal sinuses; complete, minimum 3 views", "XR"),
    ("70250", "Radiologic exam, skull; fewer than 4 views", "XR"),
    ("70260", "Radiologic exam, skull; complete, minimum 4 views", "XR"),
    ("70360", "Radiologic exam, neck; soft tissue", "XR"),
    # --- Plain radiography · chest & ribs (XR) ---
    ("71047", "Radiologic exam, chest; 3 views", "XR"),
    ("71048", "Radiologic exam, chest; 4 or more views", "XR"),
    ("71100", "Radiologic exam, ribs, unilateral; 2 views", "XR"),
    ("71110", "Radiologic exam, ribs, bilateral; 3 views", "XR"),
    # --- Plain radiography · spine (XR) ---
    ("72020", "Radiologic exam, spine; single view, specified level", "XR"),
    ("72040", "Radiologic exam, cervical spine; 2-3 views", "XR"),
    ("72050", "Radiologic exam, cervical spine; 4-5 views", "XR"),
    ("72052", "Radiologic exam, cervical spine; 6 or more views", "XR"),
    ("72070", "Radiologic exam, thoracic spine; 2 views", "XR"),
    ("72072", "Radiologic exam, thoracic spine; 3 views", "XR"),
    ("72080", "Radiologic exam, thoracolumbar spine; 2 views", "XR"),
    ("72100", "Radiologic exam, lumbosacral spine; 2-3 views", "XR"),
    ("72110", "Radiologic exam, lumbosacral spine; 4 or more views", "XR"),
    ("72170", "Radiologic exam, pelvis; 1-2 views", "XR"),
    ("72190", "Radiologic exam, pelvis; 3 or more views", "XR"),
    # --- Plain radiography · upper extremity (XR) ---
    ("73000", "Radiologic exam, clavicle; complete", "XR"),
    ("73010", "Radiologic exam, scapula; complete", "XR"),
    ("73020", "Radiologic exam, shoulder; 1 view", "XR"),
    ("73060", "Radiologic exam, humerus; minimum 2 views", "XR"),
    ("73070", "Radiologic exam, elbow; 2 views", "XR"),
    ("73080", "Radiologic exam, elbow; 3 or more views", "XR"),
    ("73090", "Radiologic exam, forearm; 2 views", "XR"),
    ("73100", "Radiologic exam, wrist; 2 views", "XR"),
    ("73120", "Radiologic exam, hand; 2 views", "XR"),
    ("73130", "Radiologic exam, hand; 3 or more views", "XR"),
    ("73140", "Radiologic exam, finger(s); minimum 2 views", "XR"),
    # --- Plain radiography · lower extremity (XR) ---
    ("73501", "Radiologic exam, hip, unilateral; 1 view", "XR"),
    ("73502", "Radiologic exam, hip, unilateral; 2-3 views", "XR"),
    ("73503", "Radiologic exam, hip, unilateral; 4 or more views", "XR"),
    ("73521", "Radiologic exam, hips, bilateral; 2 views", "XR"),
    ("73522", "Radiologic exam, hips, bilateral; 3-4 views", "XR"),
    ("73523", "Radiologic exam, hips, bilateral; 5 or more views", "XR"),
    ("73551", "Radiologic exam, femur; 1 view", "XR"),
    ("73552", "Radiologic exam, femur; 2 or more views", "XR"),
    ("73560", "Radiologic exam, knee; 1 or 2 views", "XR"),
    ("73565", "Radiologic exam, knee; both knees, standing AP", "XR"),
    ("73590", "Radiologic exam, tibia and fibula; 2 views", "XR"),
    ("73600", "Radiologic exam, ankle; 2 views", "XR"),
    ("73610", "Radiologic exam, ankle; 3 or more views", "XR"),
    ("73620", "Radiologic exam, foot; 2 views", "XR"),
    ("73630", "Radiologic exam, foot; 3 or more views", "XR"),
    ("73650", "Radiologic exam, calcaneus; minimum 2 views", "XR"),
    ("73660", "Radiologic exam, toe(s); minimum 2 views", "XR"),
    # --- Plain radiography · abdomen (XR) ---
    ("74019", "Radiologic exam, abdomen; 2 views", "XR"),
    ("74021", "Radiologic exam, abdomen; 3 or more views", "XR"),
    ("74022", "Radiologic exam, acute abdomen series, including a chest view", "XR"),
    # --- Bone densitometry (DXA, X-ray based) ---
    ("77080", "DXA bone density study, axial skeleton (hips, pelvis, spine)", "XR"),
    ("77081", "DXA bone density study, appendicular skeleton (peripheral)", "XR"),

    # --- CT · head & neck (CT) ---
    ("70470", "CT, head or brain; without then with contrast", "CT"),
    ("70480", "CT, orbit/sella/posterior fossa/ear; without contrast", "CT"),
    ("70481", "CT, orbit/sella/posterior fossa/ear; with contrast", "CT"),
    ("70482", "CT, orbit/sella/posterior fossa/ear; without then with contrast", "CT"),
    ("70486", "CT, maxillofacial area; without contrast", "CT"),
    ("70487", "CT, maxillofacial area; with contrast", "CT"),
    ("70488", "CT, maxillofacial area; without then with contrast", "CT"),
    ("70490", "CT, soft tissue neck; without contrast", "CT"),
    ("70491", "CT, soft tissue neck; with contrast", "CT"),
    ("70492", "CT, soft tissue neck; without then with contrast", "CT"),
    # --- CT · chest (CT) ---
    ("71270", "CT, thorax; without then with contrast", "CT"),
    # --- CT · spine (CT) ---
    ("72125", "CT, cervical spine; without contrast", "CT"),
    ("72126", "CT, cervical spine; with contrast", "CT"),
    ("72127", "CT, cervical spine; without then with contrast", "CT"),
    ("72128", "CT, thoracic spine; without contrast", "CT"),
    ("72129", "CT, thoracic spine; with contrast", "CT"),
    ("72130", "CT, thoracic spine; without then with contrast", "CT"),
    ("72131", "CT, lumbar spine; without contrast", "CT"),
    ("72132", "CT, lumbar spine; with contrast", "CT"),
    ("72133", "CT, lumbar spine; without then with contrast", "CT"),
    # --- CT · pelvis & abdomen (CT) ---
    ("72193", "CT, pelvis; with contrast", "CT"),
    ("72194", "CT, pelvis; without then with contrast", "CT"),
    ("74160", "CT, abdomen; with contrast", "CT"),
    ("74170", "CT, abdomen; without then with contrast", "CT"),
    # --- CT · extremities (CT) ---
    ("73200", "CT, upper extremity; without contrast", "CT"),
    ("73201", "CT, upper extremity; with contrast", "CT"),
    ("73202", "CT, upper extremity; without then with contrast", "CT"),
    ("73700", "CT, lower extremity; without contrast", "CT"),
    ("73701", "CT, lower extremity; with contrast", "CT"),
    ("73702", "CT, lower extremity; without then with contrast", "CT"),
    # --- CT angiography (CTA, tagged CT) ---
    ("70496", "CT angiography, head; with contrast and post-processing", "CT"),
    ("70498", "CT angiography, neck; with contrast and post-processing", "CT"),
    ("71275", "CT angiography, chest (non-coronary); with contrast", "CT"),
    ("73206", "CT angiography, upper extremity; with contrast", "CT"),
    ("73706", "CT angiography, lower extremity; with contrast", "CT"),
    ("72191", "CT angiography, pelvis; with contrast", "CT"),
    ("74174", "CT angiography, abdomen and pelvis; with contrast", "CT"),
    ("74175", "CT angiography, abdomen; with contrast", "CT"),
    # --- Cardiac CT (CT) ---
    ("75571", "CT, heart; coronary artery calcium scoring", "CT"),
    ("75574", "CT angiography, coronary arteries (CCTA), with contrast and 3D", "CT"),

    # --- MRI · head & neck (MRI) ---
    ("70540", "MRI, orbit/face/neck; without contrast", "MRI"),
    ("70542", "MRI, orbit/face/neck; with contrast", "MRI"),
    ("70543", "MRI, orbit/face/neck; without then with contrast", "MRI"),
    ("70552", "MRI, brain; with contrast", "MRI"),
    ("70553", "MRI, brain; without then with contrast", "MRI"),
    # --- MRI · chest (MRI) ---
    ("71550", "MRI, chest; without contrast", "MRI"),
    ("71551", "MRI, chest; with contrast", "MRI"),
    ("71552", "MRI, chest; without then with contrast", "MRI"),
    # --- MRI · spine (MRI) ---
    ("72141", "MRI, cervical spine; without contrast", "MRI"),
    ("72142", "MRI, cervical spine; with contrast", "MRI"),
    ("72156", "MRI, cervical spine; without then with contrast", "MRI"),
    ("72146", "MRI, thoracic spine; without contrast", "MRI"),
    ("72147", "MRI, thoracic spine; with contrast", "MRI"),
    ("72157", "MRI, thoracic spine; without then with contrast", "MRI"),
    ("72158", "MRI, lumbar spine; without then with contrast", "MRI"),
    # --- MRI · pelvis & abdomen (MRI) ---
    ("72195", "MRI, pelvis; without contrast", "MRI"),
    ("72196", "MRI, pelvis; with contrast", "MRI"),
    ("72197", "MRI, pelvis; without then with contrast", "MRI"),
    ("74181", "MRI, abdomen; without contrast", "MRI"),
    ("74182", "MRI, abdomen; with contrast", "MRI"),
    ("74183", "MRI, abdomen; without then with contrast", "MRI"),
    # --- MRI · extremities (MRI) ---
    ("73218", "MRI, upper extremity (non-joint); without contrast", "MRI"),
    ("73219", "MRI, upper extremity (non-joint); with contrast", "MRI"),
    ("73220", "MRI, upper extremity (non-joint); without then with contrast", "MRI"),
    ("73222", "MRI, upper extremity joint; with contrast", "MRI"),
    ("73223", "MRI, upper extremity joint; without then with contrast", "MRI"),
    ("73718", "MRI, lower extremity (non-joint); without contrast", "MRI"),
    ("73719", "MRI, lower extremity (non-joint); with contrast", "MRI"),
    ("73720", "MRI, lower extremity (non-joint); without then with contrast", "MRI"),
    ("73722", "MRI, lower extremity joint; with contrast", "MRI"),
    ("73723", "MRI, lower extremity joint; without then with contrast", "MRI"),
    # --- MR angiography (MRA, tagged MRI) ---
    ("70544", "MR angiography, head; without contrast", "MRI"),
    ("70545", "MR angiography, head; with contrast", "MRI"),
    ("70546", "MR angiography, head; without then with contrast", "MRI"),
    ("70547", "MR angiography, neck; without contrast", "MRI"),
    ("70548", "MR angiography, neck; with contrast", "MRI"),
    ("70549", "MR angiography, neck; without then with contrast", "MRI"),
    ("71555", "MR angiography, chest (non-coronary); with or without contrast", "MRI"),
    ("72159", "MR angiography, spinal canal; with or without contrast", "MRI"),
    ("72198", "MR angiography, pelvis; with or without contrast", "MRI"),
    ("73225", "MR angiography, upper extremity; with or without contrast", "MRI"),
    ("73725", "MR angiography, lower extremity; with or without contrast", "MRI"),
    ("74185", "MR angiography, abdomen; with or without contrast", "MRI"),

    # --- Ultrasound · body (US) ---
    ("76536", "Ultrasound, soft tissue of head and neck (e.g., thyroid, parathyroid)", "US"),
    ("76604", "Ultrasound, chest (excluding the heart)", "US"),
    ("76641", "Ultrasound, breast, unilateral; complete", "US"),
    ("76642", "Ultrasound, breast, unilateral; limited", "US"),
    ("76700", "Ultrasound, abdomen; complete", "US"),
    ("76705", "Ultrasound, abdomen; limited or follow-up", "US"),
    ("76706", "Ultrasound, abdominal aorta screening for aneurysm (AAA)", "US"),
    ("76770", "Ultrasound, retroperitoneum (kidneys/aorta/nodes); complete", "US"),
    ("76775", "Ultrasound, retroperitoneum; limited", "US"),
    ("76776", "Ultrasound, transplanted kidney, with duplex Doppler", "US"),
    ("76856", "Ultrasound, pelvis (non-obstetric); complete", "US"),
    ("76857", "Ultrasound, pelvis (non-obstetric); limited or follow-up", "US"),
    ("76830", "Ultrasound, transvaginal (non-obstetric)", "US"),
    ("76831", "Saline infusion sonohysterography, including color flow Doppler", "US"),
    ("76870", "Ultrasound, scrotum and contents", "US"),
    ("76872", "Ultrasound, transrectal", "US"),
    ("76881", "Ultrasound, extremity, non-vascular; complete joint", "US"),
    ("76882", "Ultrasound, extremity, non-vascular; limited (joint/soft tissue)", "US"),
    # --- Ultrasound · obstetric (US) ---
    ("76801", "Ultrasound, pregnant uterus, < 14 weeks; single/first gestation, transabdominal", "US"),
    ("76802", "Ultrasound, pregnant uterus, < 14 weeks; each additional gestation (add-on)", "US"),
    ("76810", "Ultrasound, pregnant uterus, >= 14 weeks; each additional gestation (add-on)", "US"),
    ("76811", "Ultrasound, pregnant uterus, >= 14 weeks; detailed fetal anatomic exam, single", "US"),
    ("76812", "Ultrasound, pregnant uterus, >= 14 weeks; detailed, each additional gestation (add-on)", "US"),
    ("76815", "Ultrasound, pregnant uterus; limited (one or more fetuses)", "US"),
    ("76816", "Ultrasound, pregnant uterus; follow-up, per fetus", "US"),
    ("76817", "Ultrasound, pregnant uterus; transvaginal", "US"),
    # --- Doppler / duplex vascular ultrasound (tagged US) ---
    ("93880", "Duplex scan, extracranial (carotid) arteries; complete bilateral", "US"),
    ("93882", "Duplex scan, extracranial (carotid) arteries; unilateral or limited", "US"),
    ("93886", "Transcranial Doppler study of intracranial arteries; complete", "US"),
    ("93922", "Limited bilateral noninvasive physiologic studies, extremity arteries", "US"),
    ("93923", "Complete bilateral noninvasive physiologic studies, extremity arteries", "US"),
    ("93925", "Duplex scan, lower extremity arteries/bypass grafts; complete bilateral", "US"),
    ("93926", "Duplex scan, lower extremity arteries/bypass grafts; unilateral or limited", "US"),
    ("93930", "Duplex scan, upper extremity arteries/bypass grafts; complete bilateral", "US"),
    ("93931", "Duplex scan, upper extremity arteries/bypass grafts; unilateral or limited", "US"),
    ("93970", "Duplex scan, extremity veins; complete bilateral", "US"),
    ("93971", "Duplex scan, extremity veins; unilateral or limited", "US"),
    ("93975", "Duplex scan, abdominal/pelvic/scrotal arterial and venous flow; complete", "US"),
    ("93976", "Duplex scan, abdominal/pelvic/scrotal arterial and venous flow; limited", "US"),
    ("93978", "Duplex scan, aorta/IVC/iliac vasculature; complete", "US"),
    ("93979", "Duplex scan, aorta/IVC/iliac vasculature; unilateral or limited", "US"),
    ("93990", "Duplex scan of hemodialysis access (graft/fistula)", "US"),
    # --- Mammography (MG) ---
    ("77065", "Diagnostic mammography, unilateral; including CAD when performed", "MG"),
    ("77066", "Diagnostic mammography, bilateral; including CAD when performed", "MG"),
    ("77067", "Screening mammography, bilateral; including CAD when performed", "MG"),
    ("77061", "Diagnostic digital breast tomosynthesis, unilateral", "MG"),
    ("77062", "Diagnostic digital breast tomosynthesis, bilateral", "MG"),
    ("77063", "Screening digital breast tomosynthesis, bilateral (add-on)", "MG"),
]

HCPCS = [
    ("Q9967", "Low osmolar contrast material, 300-399 mg/ml iodine concentration, per ml", "ANY"),
    ("A9579", "Gadolinium-based MR contrast agent, not otherwise specified, per ml", "MRI"),
    # HCC / Risk Adjustment — annual wellness visits (real public G-codes)
    ("G0438", "Annual wellness visit; includes a personalized prevention plan of service, initial visit", "AWV"),
    ("G0439", "Annual wellness visit; includes a personalized prevention plan of service, subsequent visit", "AWV"),
    # --- Radiology contrast / radiopharmaceuticals (REAL public-domain CMS L2) ---
    ("Q9965", "Low osmolar contrast material, 100-199 mg/ml iodine concentration, per ml", "ANY"),
    ("Q9966", "Low osmolar contrast material, 200-299 mg/ml iodine concentration, per ml", "ANY"),
    ("A9575", "Gadoterate meglumine-based MR contrast agent, per ml", "MRI"),
    ("A9581", "Gadoxetate disodium, per ml", "MRI"),
    ("A9585", "Gadobutrol, per 0.1 ml", "MRI"),
    ("A9500", "Technetium Tc-99m sestamibi, diagnostic, per study dose", "NM"),
    ("A9503", "Technetium Tc-99m medronate (MDP), diagnostic, per study dose, up to 30 millicuries", "NM"),
]

# --- Modifiers ---
MODIFIERS = [
    ("26", "Professional component", "CPT", "Reading/interpretation only (radiology PC)"),
    ("TC", "Technical component", "CPT", "Equipment/technical only"),
    ("59", "Distinct procedural service", "CPT", "Unbundles an NCCI pair when clinically distinct"),
    ("XU", "Unusual non-overlapping service", "CPT", "NCCI-associated X-modifier"),
    # X{EPSU} — selective, more-specific subsets of modifier 59 (CMS MLN MM8863). Use the
    # specific X-modifier instead of 59 whenever possible. The NCCI gate accepts any of
    # 59/XE/XS/XP/XU to unbundle a PTP pair.
    ("XE", "Separate encounter", "CPT", "X{EPSU} subset of 59: distinct because it occurred during a separate encounter"),
    ("XS", "Separate structure", "CPT", "X{EPSU} subset of 59: distinct because performed on a separate organ/structure (e.g., imaging of a different anatomic site)"),
    ("XP", "Separate practitioner", "CPT", "X{EPSU} subset of 59: distinct because performed by a different practitioner"),
    ("51", "Multiple procedures", "CPT", ""),
    ("50", "Bilateral procedure", "CPT", ""),
    ("RT", "Right side", "CPT", ""),
    ("LT", "Left side", "CPT", ""),
    ("25", "Significant, separately identifiable E&M", "CPT", "Same-day E&M with a procedure"),
    ("76", "Repeat procedure by same physician", "CPT", ""),
    ("77", "Repeat procedure by another physician or other qualified health care professional", "CPT",
     "Same procedure repeated by a DIFFERENT provider on the same day (e.g., a second radiologist repeats/re-reads a study); not for E&M"),
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
    # --- Radiology component coding (combined-contrast studies bundle the singles) ---
    ("70470", "70450", False, "CT head w/o is a component of the combined without-then-with study"),
    ("70470", "70460", False, "CT head with is a component of the combined without-then-with study"),
    ("71270", "71250", False, "CT chest w/o is a component of the combined without-then-with study"),
    ("71270", "71260", False, "CT chest with is a component of the combined without-then-with study"),
    ("74170", "74150", False, "CT abdomen w/o is a component of the combined without-then-with study"),
    ("74170", "74160", False, "CT abdomen with is a component of the combined without-then-with study"),
    ("74178", "74176", False, "CT abd+pelvis w/o is a component of the combined without-then-with study"),
    ("74178", "74177", False, "CT abd+pelvis with is a component of the combined without-then-with study"),
    ("72156", "72141", False, "MRI cervical w/o is a component of the combined without-then-with study"),
    ("72156", "72142", False, "MRI cervical with is a component of the combined without-then-with study"),
    ("72158", "72148", False, "MRI lumbar w/o is a component of the combined without-then-with study"),
    ("72158", "72149", False, "MRI lumbar with is a component of the combined without-then-with study"),
    ("74174", "74175", False, "CTA abdomen+pelvis includes CTA abdomen; report the combined code"),
    # --- Complete-vs-limited ultrasound (complete includes a limited study) ---
    ("76700", "76705", True, "Complete abdominal US includes a limited study; report only one per session unless distinct"),
    ("76700", "76770", True, "Complete abdominal US views retroperitoneal structures; report retroperitoneal-only when the exam is limited to those structures"),
    ("76770", "76775", True, "Complete retroperitoneal US includes a limited study"),
    ("76856", "76857", True, "Complete pelvic US includes a limited study"),
    # --- Duplex/Doppler: complete bilateral includes a unilateral/limited study ---
    ("93880", "93882", True, "Complete bilateral carotid duplex includes a unilateral/limited study"),
    ("93970", "93971", True, "Complete bilateral venous duplex includes a unilateral/limited study"),
    ("93925", "93926", True, "Complete bilateral lower-extremity arterial duplex includes a unilateral/limited study"),
    ("93930", "93931", True, "Complete bilateral upper-extremity arterial duplex includes a unilateral/limited study"),
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
    # --- Radiology cross-sectional / advanced imaging (representative; one/day typical) ---
    ("70460", 1, "CT head with contrast, one per day typical"),
    ("70470", 1, "CT head w/o then with, one per day typical"),
    ("70486", 1, "CT maxillofacial, one per day typical"),
    ("70490", 1, "CT soft tissue neck, one per day typical"),
    ("70496", 1, "CTA head, one per day typical"),
    ("70498", 1, "CTA neck, one per day typical"),
    ("70551", 1, "MRI brain w/o, one per day typical"),
    ("70552", 1, "MRI brain with, one per day typical"),
    ("70553", 1, "MRI brain w/o then with, one per day typical"),
    ("71260", 1, "CT chest with contrast, one per day typical"),
    ("71270", 1, "CT chest w/o then with, one per day typical"),
    ("71275", 1, "CTA chest, one per day typical"),
    ("72125", 1, "CT cervical spine w/o, one per day typical"),
    ("72131", 1, "CT lumbar spine w/o, one per day typical"),
    ("72141", 1, "MRI cervical spine w/o, one per day typical"),
    ("72146", 1, "MRI thoracic spine w/o, one per day typical"),
    ("74150", 1, "CT abdomen w/o, one per day typical"),
    ("74160", 1, "CT abdomen with, one per day typical"),
    ("74170", 1, "CT abdomen w/o then with, one per day typical"),
    ("74174", 1, "CTA abdomen and pelvis, one per day typical"),
    ("74181", 1, "MRI abdomen w/o, one per day typical"),
    ("76700", 1, "Complete abdominal US, one per day typical"),
    ("76770", 1, "Complete retroperitoneal US, one per day typical"),
    ("76856", 1, "Complete pelvic US, one per day typical"),
    ("76536", 1, "Thyroid/soft-tissue neck US, one per day typical"),
    ("76805", 1, "Obstetric US >= 14 weeks, one per day typical"),
    ("76817", 1, "Transvaginal obstetric US, one per day typical"),
    ("93880", 1, "Complete carotid duplex, one per day typical"),
    ("93970", 1, "Complete extremity venous duplex, one per day typical"),
    ("93925", 1, "Complete lower-extremity arterial duplex, one per day typical"),
    ("93930", 1, "Complete upper-extremity arterial duplex, one per day typical"),
    ("77065", 1, "Diagnostic mammography unilateral, one per day typical"),
    ("77066", 1, "Diagnostic mammography bilateral, one per day typical"),
    ("77067", 1, "Screening mammography bilateral, one per day typical"),
    ("77080", 1, "DXA axial bone density, one per day typical"),
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
    ("Medicare", "43239", "EGD with biopsy covered for dyspepsia, reflux, suspected mucosal disease "
     "requiring tissue diagnosis, or evaluation of iron-deficiency anemia / GI blood loss.",
     False, "", ["K21", "K29", "K25", "D50", "K92"]),
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
    # --- Radiology medical necessity (representative LCD/NCD-style) ---
    ("Medicare", "70450", "CT head/brain without contrast covered for acute neurologic symptoms "
     "(headache red flags, syncope, seizure, suspected stroke).", False, "", ["R51", "R55", "R56", "G45", "I63"]),
    ("Medicare", "70551", "MRI brain covered for new neurologic deficit, suspected mass, or persistent "
     "headache with red-flag features.", False, "", ["R51", "G45", "I63", "R55"]),
    ("Anthem", "70551", "Prior authorization required for outpatient brain MRI.",
     True, "Auth # required on claim", ["R51", "G45", "I63"]),
    ("Medicare", "72141", "MRI cervical spine covered for radiculopathy or myelopathy, or neck pain with "
     "neurologic deficit persisting after conservative care.", False, "", ["M54.1", "M54.2", "M50"]),
    ("Anthem", "72141", "Prior authorization required for outpatient cervical spine MRI.",
     True, "Auth # required on claim", ["M54.1", "M54.2"]),
    ("Medicare", "71250", "CT chest covered for an indeterminate pulmonary nodule, abnormal chest "
     "radiograph, or evaluation of suspected thoracic pathology.", False, "", ["R91", "R09", "C34", "J98"]),
    ("Medicare", "71275", "CTA chest covered for suspected pulmonary embolism or thoracic vascular "
     "pathology with a documented indication.", False, "", ["I26", "R09.1", "R07.1"]),
    ("Medicare", "93970", "Extremity venous duplex covered for suspected deep vein thrombosis or "
     "documented leg swelling/pain.", False, "", ["I82", "R60", "M79.6"]),
    ("Medicare", "93880", "Carotid duplex covered for TIA, stroke, amaurosis fugax, or a documented "
     "cervical bruit.", False, "", ["G45", "I63", "I65", "R55"]),
    ("Medicare", "74174", "CTA abdomen and pelvis covered for suspected aortic aneurysm/dissection or "
     "mesenteric/visceral vascular pathology.", False, "", ["I71", "I73", "R10"]),
    ("Medicare", "76700", "Complete abdominal ultrasound covered for abdominal pain, organomegaly, or a "
     "palpable mass.", False, "", ["R10", "R16", "R19", "K92.2"]),
    ("Medicare", "76770", "Retroperitoneal (renal) ultrasound covered for hematuria, suspected "
     "hydronephrosis, calculus, or renal mass.", False, "", ["N13", "N20", "N28", "R31"]),
    ("Medicare", "76856", "Pelvic ultrasound covered for pelvic pain, mass, or abnormal bleeding.",
     False, "", ["R10.2", "N93", "N83", "R19.00"]),
    # (Anthem 76805 obstetric ultrasound policy already defined above)
    ("Medicare", "76536", "Thyroid/soft-tissue neck ultrasound covered for a thyroid nodule, goiter, or "
     "palpable neck mass.", False, "", ["E04", "R22.1", "R59"]),
    ("Medicare", "77067", "Screening mammography covered once every 12 months for women aged 40 and older.",
     False, "", ["Z12.31"]),
    ("Medicare", "77066", "Diagnostic mammography covered for a breast lump, abnormal screening finding, "
     "or other breast sign/symptom.", False, "", ["N63", "R92", "N64"]),
    ("Medicare", "77080", "DXA bone density covered every 24 months for osteoporosis screening/monitoring "
     "in qualifying beneficiaries (more often if medically necessary).", False, "", ["M81", "M80", "Z13.820"]),
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
    # Radiology concepts (real UMLS CUIs; supplements lexical retrieval)
    ("C0034065", "Pulmonary embolism", "Disease", [{"system": "ICD10CM", "code": "I26.99"}]),
    ("C0032227", "Pleural effusion", "Disease", [{"system": "ICD10CM", "code": "J90"}]),
    ("C0022646", "Kidney structure", "Body Part", []),
    ("C0023884", "Liver structure", "Body Part", []),
    # =======================================================================
    # TRAUMA / MUSCULOSKELETAL KNOWLEDGE GRAPH for the Chapter 19 'S' injury
    # codes. Real UMLS CUIs verified via the Wikidata UMLS-CUI cross-reference
    # (property P2892). Bone/joint structures are finding_site targets; the
    # fracture/dislocation concepts map to a representative billable injury code
    # and are linked is_a 'Bone fracture'. Knee joint (C0022742) and shoulder
    # joint (C0037004) already exist above and are reused. This enriches
    # Graph-RAG retrieval + explainability for radiology/ED/ortho trauma reports.
    # =======================================================================
    # Skeletal / joint structures (Body Part; maps_to empty — finding_site targets)
    ("C0037303", "Skull structure", "Body Part", []),
    ("C0027422", "Nasal bone structure", "Body Part", []),
    ("C0037949", "Vertebral column structure", "Body Part", []),
    ("C0039987", "Thoracic vertebra structure", "Body Part", []),
    ("C0024091", "Lumbar vertebrae structure", "Body Part", []),
    ("C0035561", "Rib structure", "Body Part", []),
    ("C0008913", "Clavicle structure", "Body Part", []),
    ("C0020164", "Humerus structure", "Body Part", []),
    ("C0034627", "Radius bone structure", "Body Part", []),
    ("C0041600", "Ulna structure", "Body Part", []),
    ("C0223724", "Scaphoid bone structure", "Body Part", []),
    ("C0025526", "Metacarpal bone structure", "Body Part", []),
    ("C0015811", "Femur structure", "Body Part", []),
    ("C0040184", "Tibia structure", "Body Part", []),
    ("C0016068", "Fibula structure", "Body Part", []),
    ("C0030647", "Patella structure", "Body Part", []),
    ("C0730182", "Ankle joint structure", "Body Part", []),
    ("C0006655", "Calcaneus structure", "Body Part", []),
    ("C0025584", "Metatarsal bone structure", "Body Part", []),
    ("C0224498", "Meniscus structure", "Body Part", []),
    # Fracture / dislocation / sprain concepts (Injury or Poisoning) → representative billable code
    ("C0016658", "Bone fracture", "Injury or Poisoning", []),
    ("C0035522", "Rib fracture", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S22.39XA"}]),
    ("C0521169", "Vertebral compression fracture", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S32.010A"}]),
    ("C0020162", "Humerus fracture", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S42.201A"}]),
    ("C0435585", "Distal radius fracture", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S52.501A"}]),
    ("C0009353", "Colles' fracture", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S52.531A"}]),
    ("C0041601", "Ulna fracture", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S52.601A"}]),
    ("C0015806", "Femoral neck fracture", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S72.001A"}]),
    ("C0015802", "Femoral fracture", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S72.301A"}]),
    ("C0262489", "Tibial plateau fracture", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S82.101A"}]),
    ("C0040185", "Tibia fracture", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S82.201A"}]),
    ("C0037005", "Shoulder dislocation", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S43.004A"}]),
    ("C0409312", "Anterior cruciate ligament injury", "Injury or Poisoning", [{"system": "ICD10CM", "code": "S83.511A"}]),
    # External cause — transport accident (mechanism of injury → Chapter 20 'V' codes)
    ("C0000932", "Motor vehicle traffic accident", "Injury or Poisoning",
     [{"system": "ICD10CM", "code": "V89.2XXA"}, {"system": "ICD10CM", "code": "V03.10XA"}]),
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
    ("C0034065", "finding_site", "C0024109"),    # pulmonary embolism -> lung
    ("C0032227", "finding_site", "C0024109"),    # pleural effusion -> lung
    ("C0022650", "finding_site", "C0022646"),    # calculus of kidney -> kidney
    # --- Trauma / musculoskeletal: fracture/injury -> finding_site (bone/joint) ---
    ("C0035522", "finding_site", "C0035561"),    # rib fracture -> rib
    ("C0521169", "finding_site", "C0024091"),    # vertebral compression fracture -> lumbar vertebrae
    ("C0020162", "finding_site", "C0020164"),    # humerus fracture -> humerus
    ("C0435585", "finding_site", "C0034627"),    # distal radius fracture -> radius
    ("C0009353", "finding_site", "C0034627"),    # Colles' fracture -> radius
    ("C0041601", "finding_site", "C0041600"),    # ulna fracture -> ulna
    ("C0015806", "finding_site", "C0015811"),    # femoral neck fracture -> femur
    ("C0015802", "finding_site", "C0015811"),    # femoral fracture -> femur
    ("C0262489", "finding_site", "C0040184"),    # tibial plateau fracture -> tibia
    ("C0040185", "finding_site", "C0040184"),    # tibia fracture -> tibia
    ("C0037005", "finding_site", "C0037004"),    # shoulder dislocation -> shoulder joint
    ("C0409312", "finding_site", "C0022742"),    # ACL injury -> knee joint
    # --- Fracture hierarchy (is_a) ---
    ("C0035522", "is_a", "C0016658"),            # rib fracture is_a bone fracture
    ("C0521169", "is_a", "C0016658"),            # compression fracture is_a bone fracture
    ("C0020162", "is_a", "C0016658"),            # humerus fracture is_a bone fracture
    ("C0435585", "is_a", "C0016658"),            # distal radius fracture is_a bone fracture
    ("C0009353", "is_a", "C0016658"),            # Colles' fracture is_a bone fracture
    ("C0041601", "is_a", "C0016658"),            # ulna fracture is_a bone fracture
    ("C0015806", "is_a", "C0016658"),            # femoral neck fracture is_a bone fracture
    ("C0015802", "is_a", "C0016658"),            # femoral fracture is_a bone fracture
    ("C0262489", "is_a", "C0016658"),            # tibial plateau fracture is_a bone fracture
    ("C0040185", "is_a", "C0016658"),            # tibia fracture is_a bone fracture
    # --- Mechanism: transport accident associated_with the resulting injury ---
    ("C0262489", "associated_with", "C0000932"), # tibial plateau fracture <-> MV traffic accident
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
    ("ICD-10-CM Official Guidelines", "I.B.13",
     "Laterality: Some ICD-10-CM codes indicate laterality (right, left, or bilateral), specified by the "
     "final character of the code. If no bilateral code is provided and the condition is bilateral, "
     "assign separate codes for both the left and right side. If the side is not identified in the medical "
     "record, assign the code for the unspecified side. In imaging, code the side the report documents "
     "(e.g., right vs left vs unspecified distal radius fracture); use the unspecified-side code only when "
     "the report does not state the side.", "Radiology"),
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
    ("Radiology Coding Guidance", "ContrastPhases",
     "For CT and MRI, three studies exist per region: 'without contrast', 'with contrast', and "
     "'without followed by with contrast'. Select the single code matching the phases performed. Do not "
     "report the without and with codes separately when a combined-phase code exists.", "Radiology"),
    ("Radiology Coding Guidance", "Ultrasound",
     "A complete ultrasound study requires that all required elements of the anatomic region be "
     "documented; otherwise report the limited study. A complete abdominal ultrasound (76700) views the "
     "liver, gallbladder, pancreas, spleen, kidneys, and upper abdominal aorta/IVC; report a "
     "retroperitoneal study (76770/76775) only when the exam is limited to those structures.", "Radiology"),
    ("Radiology Coding Guidance", "Doppler",
     "Duplex scans combine grey-scale imaging with spectral/color Doppler. Choose 'complete bilateral' "
     "vs 'unilateral or limited' by what was performed (e.g., carotid 93880 vs 93882; extremity veins "
     "93970 vs 93971). Do not report a unilateral/limited duplex in addition to the complete bilateral "
     "study of the same vasculature on the same day.", "Radiology"),
    ("Radiology Coding Guidance", "Angiography",
     "CT angiography (CTA) and MR angiography (MRA) include image post-processing and are coded by region "
     "(e.g., CTA chest 71275, CTA head 70496, MRA neck 70547-70549). Do not separately report the "
     "non-angiographic CT/MRI of the same region performed solely to create the angiographic dataset.",
     "Radiology"),
    ("Radiology Coding Guidance", "Mammography",
     "Screening mammography (77067, bilateral) is for an asymptomatic patient; diagnostic mammography "
     "(77065 unilateral, 77066 bilateral) is for a breast sign/symptom or to evaluate an abnormal "
     "screening finding. If a screening study converts to diagnostic the same day, report the diagnostic "
     "code with the appropriate modifier per payer policy.", "Radiology"),
    ("Radiology Coding Guidance", "Screening",
     "When a screening study (e.g., screening mammography Z12.31, screening AAA ultrasound) is performed, "
     "sequence the screening Z-code as the reason for the exam; report any incidental finding secondarily. "
     "Do not replace the screening indication with a finding code.", "Radiology"),
    ("Radiology Coding Guidance", "AbnormalFindings",
     "When imaging is abnormal but no definitive diagnosis is established, code the specific abnormal "
     "finding (e.g., solitary pulmonary nodule R91.1, abnormal retroperitoneal imaging R93.5) or the "
     "sign/symptom that prompted the study, per the uncertain-diagnosis rule.", "Radiology"),
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


# ===========================================================================
# Facility vs Professional — APC / OPPS (Tier-B #4). CMS Addendum B (status
# indicators, APC assignments) is a PUBLIC artifact published quarterly; rates
# here are representative national amounts. The packaging / discounting /
# C-APC payment logic is real. ASC (POS 24) = different fee schedule, excluded.
# (code, status_indicator, apc, apc_title, national_rate)
# SI: J1 comprehensive · T discounted surgical · S significant · V visit ·
#     N packaged · Q1 conditionally packaged
# ===========================================================================
APC_ADDENDUM_B = [
    # Imaging without contrast — Q1 (packaged when a surgical/visit service is on the claim)
    ("71045", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("71046", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("73030", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("73110", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("73562", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("73564", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("74018", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("70450", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    ("71250", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    ("74150", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    ("72192", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    ("74176", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("72148", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("70551", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("73721", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("73221", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    # Imaging with contrast
    ("70460", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("71260", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("72149", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("74177", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("74178", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    # Contrast material — always packaged
    ("Q9967", "N", "", "Packaged supply (contrast material)", 0.0),
    ("A9579", "N", "", "Packaged supply (MR contrast agent)", 0.0),
    # ED visits — V (paid) + critical care S; add-on 99292 packaged
    ("99281", "V", "5021", "Type A ED Visit, Level 1", 74.00),
    ("99282", "V", "5022", "Type A ED Visit, Level 2", 145.00),
    ("99283", "V", "5023", "Type A ED Visit, Level 3", 259.00),
    ("99284", "V", "5024", "Type A ED Visit, Level 4", 427.00),
    ("99285", "V", "5025", "Type A ED Visit, Level 5", 626.00),
    ("99291", "S", "5041", "Critical Care", 734.00),
    ("99292", "N", "", "Packaged add-on (critical care, addl 30 min)", 0.0),
    # Pathology
    ("88304", "Q1", "5672", "Level 2 Pathology", 70.00),
    ("88305", "Q1", "5673", "Level 3 Pathology", 129.00),
    ("88307", "Q1", "5674", "Level 4 Pathology", 271.00),
    ("88112", "Q1", "5672", "Level 2 Pathology", 70.00),
    ("88342", "Q1", "5673", "Level 3 Pathology", 129.00),
    # GI endoscopy — comprehensive APCs (C-APC): one payment per session
    ("45378", "J1", "5311", "Level 1 Lower GI Procedures", 836.00),
    ("45380", "J1", "5312", "Level 2 Lower GI Procedures", 1015.00),
    ("45385", "J1", "5312", "Level 2 Lower GI Procedures", 1015.00),
    ("43235", "J1", "5301", "Level 1 Upper GI Procedures", 806.00),
    ("43239", "J1", "5301", "Level 1 Upper GI Procedures", 806.00),
    # Surgery (hospital outpatient)
    ("47562", "J1", "5341", "Level 1 Laparoscopy & Related Services", 6233.00),

    # --- Radiology expansion (representative OPPS buckets; rates reuse the
    #     existing level amounts already in this table) ---
    # Plain radiography → Level 1 Imaging without Contrast (5521)
    ("71047", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("71048", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("72040", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("72050", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("72100", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("72110", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("72170", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("72190", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("73560", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("73600", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("73610", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("73620", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("73630", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("74019", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("74021", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    ("74022", "Q1", "5521", "Level 1 Imaging without Contrast", 83.00),
    # CT single-region without contrast → Level 2 Imaging without Contrast (5522)
    ("70486", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    ("70490", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    ("72125", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    ("72128", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    ("72131", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    ("73200", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    ("73700", "Q1", "5522", "Level 2 Imaging without Contrast", 120.00),
    # MRI single-region without contrast → Level 3 Imaging without Contrast (5523)
    ("70540", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("71550", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("72141", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("72146", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("72195", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("73218", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("73718", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    ("74181", "Q1", "5523", "Level 3 Imaging without Contrast", 238.00),
    # CT single-region with contrast → Level 2 Imaging with Contrast (5572)
    ("70487", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("70491", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("72126", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("72129", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("72132", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("72193", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("73201", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("73701", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    ("74160", "Q1", "5572", "Level 2 Imaging with Contrast", 315.00),
    # CT combined-phase + CTA → Level 3 Imaging with Contrast (5573)
    ("70470", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("71270", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("74170", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72127", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72130", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72133", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72194", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73202", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73702", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70496", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70498", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("71275", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73206", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73706", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72191", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("74174", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("74175", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    # MRI with-contrast / combined-phase + MRA → Level 3 Imaging with Contrast (5573)
    ("70542", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70543", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70552", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70553", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("71551", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("71552", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72142", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72147", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    # (72149 MRI lumbar with contrast already in the table above)
    ("72156", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72157", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72158", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72196", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72197", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73219", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73220", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73222", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73223", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73719", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73720", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73722", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73723", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("74182", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("74183", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70544", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70545", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70546", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70547", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70548", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("70549", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("71555", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72159", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("72198", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73225", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("73725", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
    ("74185", "Q1", "5573", "Level 3 Imaging with Contrast", 506.00),
]
