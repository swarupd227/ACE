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
    # Episode-of-care triad (ICD-10 7th character: A initial / D subsequent / S sequela);
    # the initial-encounter 'A' code is seeded near the top with the radiology set.
    ("S52.501D", "Unspecified fracture of lower end of right radius, subsequent enc, routine healing", True, "S52.50"),
    ("S52.501S", "Unspecified fracture of lower end of right radius, sequela", True, "S52.50"),
    # History-of codes (temporal slot: 'history of' is not an active condition)
    ("Z87.891", "Personal history of nicotine dependence", True, "Z87.89"),
    ("Z86.73", "Personal history of TIA and cerebral infarction without residual deficits", True, "Z86.7"),
    # Contraceptive management (device beat)
    ("Z30.430", "Encounter for insertion of intrauterine contraceptive device", True, "Z30.43"),
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

    # =======================================================================
    # RADIOLOGY EXPANSION PHASE 2 — Additional ICD-10-CM codes from CMS/NCHS
    # public-domain ICD-10-CM tabular (FY2025), verified against NLM Clinical
    # Tables ICD-10-CM API (clinicaltables.nlm.nih.gov). Covers M / S / R /
    # J / K / Z / G series that drive common radiology report indications.
    # =======================================================================

    # -----------------------------------------------------------------------
    # M SERIES — Musculoskeletal / spine (MSK MRI, CT spine, XR)
    # -----------------------------------------------------------------------
    # Spondylosis with radiculopathy (lumbar/cervical MRI)
    ("M47.812", "Spondylosis with radiculopathy, cervical region", True, "M47.81"),
    ("M47.813", "Spondylosis with radiculopathy, cervicothoracic region", True, "M47.81"),
    ("M47.815", "Spondylosis with radiculopathy, thoracolumbar region", True, "M47.81"),
    ("M47.816", "Spondylosis with radiculopathy, lumbar region", True, "M47.81"),
    ("M47.817", "Spondylosis with radiculopathy, lumbosacral region", True, "M47.81"),
    # Other spondylosis (without radiculopathy)
    ("M47.892", "Other spondylosis, cervical region", True, "M47.89"),
    ("M47.895", "Other spondylosis, thoracolumbar region", True, "M47.89"),
    ("M47.896", "Other spondylosis, lumbar region", True, "M47.89"),
    ("M47.897", "Other spondylosis, lumbosacral region", True, "M47.89"),
    # Spinal stenosis (more specific than parent M48.06)
    ("M48.061", "Spinal stenosis, lumbar region, without neurogenic claudication", True, "M48.06"),
    ("M48.062", "Spinal stenosis, lumbar region, with neurogenic claudication", True, "M48.06"),
    # Cervical disc disease (cervical MRI)
    ("M50.12", "Cervical disc degeneration with radiculopathy, mid-cervical region", True, "M50.1"),
    ("M50.20", "Other cervical disc displacement, unspecified cervical region", True, "M50.2"),
    ("M50.22", "Other cervical disc displacement, mid-cervical region, group unspecified", True, "M50.2"),
    # Lumbar/lumbosacral disc disease
    ("M51.16", "Intervertebral disc degeneration with radiculopathy, lumbar region", True, "M51.1"),
    ("M51.17", "Intervertebral disc degeneration with radiculopathy, lumbosacral region", True, "M51.1"),
    ("M51.27", "Other intervertebral disc displacement, lumbosacral region", True, "M51.2"),
    ("M51.36", "Other intervertebral disc degeneration, lumbar region", True, "M51.3"),
    ("M51.37", "Other intervertebral disc degeneration, lumbosacral region", True, "M51.3"),
    ("M51.46", "Schmorl's nodes, lumbar region", True, "M51.4"),
    # Spondylolisthesis
    ("M43.16", "Spondylolisthesis, lumbar region", True, "M43.1"),
    ("M43.17", "Spondylolisthesis, lumbosacral region", True, "M43.1"),
    # Discitis
    ("M46.46", "Discitis, unspecified, lumbar region", True, "M46.4"),
    ("M46.42", "Discitis, unspecified, cervical region", True, "M46.4"),
    # Scoliosis (spinal XR / MRI)
    ("M41.9",  "Scoliosis, unspecified", True, "M41"),
    ("M41.20", "Other idiopathic scoliosis, site unspecified", True, "M41.2"),
    ("M41.25", "Other idiopathic scoliosis, thoracolumbar region", True, "M41.2"),
    ("M41.26", "Other idiopathic scoliosis, lumbar region", True, "M41.2"),
    # Hip osteoarthritis (hip XR / MRI)
    ("M16.11", "Unilateral primary osteoarthritis, right hip", True, "M16.1"),
    ("M16.12", "Unilateral primary osteoarthritis, left hip", True, "M16.1"),
    ("M16.31", "Unilateral secondary osteoarthritis, right hip", True, "M16.3"),
    ("M16.32", "Unilateral secondary osteoarthritis, left hip", True, "M16.3"),
    # Rotator cuff — complete tears (shoulder MRI/US)
    ("M75.111", "Complete rotator cuff tear or rupture of right shoulder, not specified as traumatic", True, "M75.11"),
    ("M75.112", "Complete rotator cuff tear or rupture of left shoulder, not specified as traumatic", True, "M75.11"),
    # Wrist / hand joint stiffness / pain (wrist/hand MRI/US)
    ("M25.461", "Stiffness of right wrist, not elsewhere classified", True, "M25.46"),
    ("M25.462", "Stiffness of left wrist, not elsewhere classified", True, "M25.46"),
    ("M79.641", "Pain in right hand", True, "M79.64"),
    ("M79.642", "Pain in left hand", True, "M79.64"),
    ("M79.621", "Pain in right upper arm", True, "M79.62"),
    ("M79.622", "Pain in left upper arm", True, "M79.62"),
    ("M79.671", "Pain in right foot", True, "M79.67"),
    ("M79.672", "Pain in left foot", True, "M79.67"),
    # Soft tissue / other MSK
    ("M79.89", "Other specified soft tissue disorders", True, "M79.8"),
    ("M79.3",  "Panniculitis, unspecified", True, "M79"),
    ("M86.9",  "Osteomyelitis, unspecified", True, "M86"),
    # Osteoporosis / bone density (DXA / bone scan)
    ("M81.0",  "Age-related osteoporosis without current pathological fracture", True, "M81"),
    ("M81.8",  "Other osteoporosis without current pathological fracture", True, "M81"),
    ("M84.351A", "Stress fracture, right femur, initial encounter for fracture", True, "M84.35"),
    ("M84.352A", "Stress fracture, left femur, initial encounter for fracture", True, "M84.35"),
    ("M84.361A", "Stress fracture, right tibia, initial encounter for fracture", True, "M84.36"),
    ("M84.362A", "Stress fracture, left tibia, initial encounter for fracture", True, "M84.36"),
    ("M84.371A", "Stress fracture, right ankle, initial encounter for fracture", True, "M84.37"),
    ("M84.374A", "Stress fracture, right foot, initial encounter for fracture", True, "M84.37"),
    # Cervical root / lumbar root nerve disorders (spine MRI)
    ("G54.2",  "Cervical root disorders, not elsewhere classified", True, "G54"),
    ("G54.4",  "Lumbosacral root disorders, not elsewhere classified", True, "G54"),
    # non-billable parents
    ("M47.81", "Spondylosis with radiculopathy", False, "M47.8"),
    ("M47.89", "Other spondylosis", False, "M47.8"),
    ("M50.1",  "Cervical disc disorder with radiculopathy", False, "M50"),
    ("M51.1",  "Thoracic, thoracolumbar, and lumbosacral intervertebral disc degeneration with radiculopathy", False, "M51"),
    ("M51.3",  "Other intervertebral disc degeneration", False, "M51"),

    # -----------------------------------------------------------------------
    # S SERIES — Additional trauma (fractures, contusions, organ injuries)
    # -----------------------------------------------------------------------
    # Radius / ulna fractures
    ("S52.571A", "Salter-Harris Type III physeal fracture of lower end of right radius, initial encounter", True, "S52.57"),
    ("S52.572A", "Salter-Harris Type III physeal fracture of lower end of left radius, initial encounter", True, "S52.57"),
    ("S52.611A", "Displaced fracture of right ulna styloid process, initial encounter for closed fracture", True, "S52.61"),
    ("S52.612A", "Displaced fracture of left ulna styloid process, initial encounter for closed fracture", True, "S52.61"),
    # Pelvic fractures
    ("S32.591A", "Other fracture of right pubis, initial encounter for closed fracture", True, "S32.59"),
    ("S32.592A", "Other fracture of left pubis, initial encounter for closed fracture", True, "S32.59"),
    ("S32.511A", "Fracture of superior rim of right acetabulum, initial encounter for closed fracture", True, "S32.51"),
    ("S32.512A", "Fracture of superior rim of left acetabulum, initial encounter for closed fracture", True, "S32.51"),
    # Femur fractures
    ("S72.141A", "Displaced intertrochanteric fracture of right femur, initial encounter for closed fracture", True, "S72.14"),
    ("S72.142A", "Displaced intertrochanteric fracture of left femur, initial encounter for closed fracture", True, "S72.14"),
    ("S72.321A", "Displaced transverse fracture of shaft of right femur, initial encounter for closed fracture", True, "S72.32"),
    ("S72.322A", "Displaced transverse fracture of shaft of left femur, initial encounter for closed fracture", True, "S72.32"),
    # TBI / head trauma (head CT)
    ("S06.0X0A", "Concussion without loss of consciousness, initial encounter", True, "S06.0X"),
    ("S06.0X1A", "Concussion with loss of consciousness of 30 minutes or less, initial encounter", True, "S06.0X"),
    ("S06.300A", "Unspecified focal traumatic brain injury without loss of consciousness, initial encounter", True, "S06.30"),
    ("S06.301A", "Unspecified focal traumatic brain injury with loss of consciousness of 30 min or less, initial encounter", True, "S06.30"),
    ("S09.90XA", "Unspecified injury of head, initial encounter", True, "S09.9"),
    # Thoracic trauma (chest CT)
    ("S27.0XXA", "Traumatic pneumothorax, initial encounter", True, "S27.0"),
    ("S27.1XXA", "Traumatic hemothorax, initial encounter", True, "S27.1"),
    ("S27.2XXA", "Traumatic hemopneumothorax, initial encounter", True, "S27.2"),
    ("S27.001A", "Unspecified injury of right lung, initial encounter", True, "S27.00"),
    ("S27.002A", "Unspecified injury of left lung, initial encounter", True, "S27.00"),
    # Abdominal organ trauma (abdominal CT)
    ("S36.113A", "Laceration of liver, unspecified degree, initial encounter", True, "S36.11"),
    ("S36.115A", "Moderate laceration of liver, initial encounter", True, "S36.11"),
    ("S36.30XA", "Unspecified injury of stomach, initial encounter", True, "S36.3"),
    ("S36.400A", "Unspecified injury of small intestine, initial encounter", True, "S36.40"),
    ("S36.500A", "Unspecified injury of ascending [right] colon, initial encounter", True, "S36.50"),
    # Renal / urinary trauma
    ("S37.001A", "Unspecified injury of right kidney, initial encounter", True, "S37.00"),
    ("S37.002A", "Unspecified injury of left kidney, initial encounter", True, "S37.00"),
    ("S37.031A", "Laceration of right kidney, unspecified degree, initial encounter", True, "S37.03"),
    ("S37.032A", "Laceration of left kidney, unspecified degree, initial encounter", True, "S37.03"),
    ("S37.20XA", "Unspecified injury of bladder, initial encounter", True, "S37.2"),
    # Knee / lower extremity contusions (knee MRI/US/XR)
    ("S80.01XA", "Contusion of right knee, initial encounter", True, "S80.0"),
    ("S80.02XA", "Contusion of left knee, initial encounter", True, "S80.0"),

    # -----------------------------------------------------------------------
    # R SERIES — Additional signs, symptoms & abnormal imaging findings
    # -----------------------------------------------------------------------
    ("R04.2",   "Haemoptysis", True, "R04"),
    ("R17",     "Unspecified jaundice", True, ""),
    ("R18.0",   "Malignant ascites", True, "R18"),
    ("R16.2",   "Hepatosplenomegaly, not elsewhere classified", True, "R16"),
    ("R19.03",  "Right lower quadrant abdominal swelling, mass and lump", True, "R19.0"),
    ("R19.04",  "Left lower quadrant abdominal swelling, mass and lump", True, "R19.0"),
    ("R19.09",  "Other intra-abdominal and pelvic swelling, mass and lump", True, "R19.0"),
    ("R20.2",   "Paraesthesia of skin", True, "R20"),
    ("R26.81",  "Unsteadiness on feet", True, "R26.8"),
    ("R27.0",   "Ataxia, unspecified", True, "R27"),
    ("R42",     "Dizziness and giddiness", True, ""),
    ("R47.0",   "Dysphasia and aphasia", True, "R47"),
    ("R47.1",   "Dysarthria and anarthria", True, "R47"),
    ("R52",     "Pain, unspecified", True, ""),
    ("R53.1",   "Weakness", True, "R53"),
    ("R53.83",  "Other fatigue", True, "R53.8"),
    ("R57.0",   "Cardiogenic shock", True, "R57"),
    ("R58",     "Hemorrhage, not elsewhere classified", True, ""),
    ("R60.0",   "Localized oedema", True, "R60"),
    ("R60.9",   "Oedema, unspecified", True, "R60"),
    ("R68.89",  "Other specified general symptoms and signs", True, "R68.8"),
    # Abnormal diagnostic imaging findings (R93 expansion)
    ("R93.0",   "Abnormal findings on diagnostic imaging of skull and head, not elsewhere classified", True, "R93"),
    ("R93.2",   "Abnormal findings on diagnostic imaging of liver and biliary tract", True, "R93"),
    ("R93.41",  "Abnormal radiologic finding on imaging of renal pelvis, ureter, and bladder", True, "R93.4"),
    ("R93.42",  "Abnormal radiologic finding on imaging of adrenal gland", True, "R93.4"),
    ("R93.6",   "Abnormal findings on diagnostic imaging of limbs", True, "R93"),
    ("R93.7",   "Abnormal findings on diagnostic imaging of other parts of musculoskeletal system", True, "R93"),
    ("R93.811", "Abnormal findings on diagnostic imaging of right testicle", True, "R93.81"),
    ("R93.812", "Abnormal findings on diagnostic imaging of left testicle", True, "R93.81"),

    # -----------------------------------------------------------------------
    # J SERIES — Pulmonary / chest imaging indications
    # -----------------------------------------------------------------------
    ("J18.0",  "Bronchopneumonia, unspecified organism", True, "J18"),
    ("J18.1",  "Lobar pneumonia, unspecified organism", True, "J18"),
    ("J43.9",  "Emphysema, unspecified", True, "J43"),
    ("J47.0",  "Bronchiectasis with acute lower respiratory infection", True, "J47"),
    ("J47.1",  "Bronchiectasis with exacerbation", True, "J47"),
    ("J47.9",  "Bronchiectasis, uncomplicated", True, "J47"),
    ("J70.0",  "Acute pulmonary manifestations due to radiation", True, "J70"),
    ("J70.1",  "Chronic and other pulmonary manifestations due to radiation", True, "J70"),
    ("J81.0",  "Acute pulmonary oedema", True, "J81"),
    ("J84.10", "Pulmonary fibrosis, unspecified", True, "J84.1"),
    ("J84.01", "Alveolar and parietoalveolar conditions", True, "J84.0"),
    ("J84.89", "Other specified interstitial pulmonary diseases", True, "J84.8"),
    ("J85.1",  "Abscess of lung with pneumonia", True, "J85"),
    ("J85.2",  "Abscess of lung without pneumonia", True, "J85"),
    ("J86.9",  "Pyothorax without fistula", True, "J86"),
    ("J91.0",  "Malignant pleural effusion", True, "J91"),
    ("J93.11", "Primary spontaneous pneumothorax", True, "J93.1"),
    ("J93.12", "Secondary spontaneous pneumothorax", True, "J93.1"),
    ("J93.9",  "Pneumothorax, unspecified", True, "J93"),
    ("J94.0",  "Chylous effusion", True, "J94"),
    ("J98.19", "Other pulmonary collapse", True, "J98.1"),
    ("J98.2",  "Interstitial emphysema", True, "J98"),
    ("J98.3",  "Compensatory emphysema", True, "J98"),
    ("J98.51", "Mediastinitis", True, "J98.5"),
    ("J98.59", "Other diseases of mediastinum, not elsewhere classified", True, "J98.5"),
    ("J98.6",  "Disorders of diaphragm", True, "J98"),

    # -----------------------------------------------------------------------
    # K SERIES — GI / abdominal imaging indications
    # -----------------------------------------------------------------------
    # Gallbladder / biliary (US / CT / MRCP)
    ("K80.00", "Calculus of gallbladder with acute cholecystitis without obstruction", True, "K80.0"),
    ("K80.10", "Calculus of gallbladder with chronic cholecystitis without obstruction", True, "K80.1"),
    ("K80.50", "Calculus of bile duct without cholangitis or cholecystitis, without obstruction", True, "K80.5"),
    ("K81.0",  "Acute cholecystitis", True, "K81"),
    ("K81.1",  "Chronic cholecystitis", True, "K81"),
    ("K81.9",  "Cholecystitis, unspecified", True, "K81"),
    ("K82.0",  "Obstruction of gallbladder", True, "K82"),
    ("K83.0",  "Primary sclerosing cholangitis", True, "K83"),
    ("K83.1",  "Obstruction of bile duct", True, "K83"),
    # Pancreas (CT / MRCP / EUS)
    ("K85.10", "Biliary acute pancreatitis without necrosis or infection", True, "K85.1"),
    ("K86.0",  "Alcohol-induced chronic pancreatitis", True, "K86"),
    ("K86.1",  "Other chronic pancreatitis", True, "K86"),
    ("K86.2",  "Cyst of pancreas", True, "K86"),
    ("K86.3",  "Pseudocyst of pancreas", True, "K86"),
    # Liver / portal (US / CT / MRI)
    ("K74.60", "Unspecified cirrhosis of liver", True, "K74.6"),
    ("K74.69", "Other cirrhosis of liver", True, "K74.6"),
    ("K75.0",  "Abscess of liver", True, "K75"),
    ("K76.0",  "Fatty (change of) liver, not elsewhere classified", True, "K76"),
    ("K76.5",  "Portal hypertension", True, "K76"),
    ("K70.30", "Alcoholic cirrhosis of liver without ascites", True, "K70.3"),
    ("K70.31", "Alcoholic cirrhosis of liver with ascites", True, "K70.3"),
    # Intestine / appendix / hernia (CT abdomen)
    ("K35.20", "Acute appendicitis with generalized peritonitis, without abscess", True, "K35.2"),
    ("K35.80", "Other and unspecified acute appendicitis without abscess", True, "K35.8"),
    ("K37",    "Unspecified appendicitis", True, ""),
    ("K57.32", "Diverticulitis of large intestine without perforation or abscess, without bleeding", True, "K57.3"),
    ("K57.20", "Diverticulitis of large intestine with perforation and abscess, without bleeding", True, "K57.2"),
    ("K63.0",  "Abscess of intestine", True, "K63"),
    ("K66.1",  "Haemoperitoneum", True, "K66"),
    ("K56.50", "Intestinal adhesions [bands] without obstruction", True, "K56.5"),
    ("K56.51", "Intestinal adhesions [bands] with partial obstruction", True, "K56.5"),
    ("K56.52", "Intestinal adhesions [bands] with complete obstruction", True, "K56.5"),
    ("K40.90", "Unilateral inguinal hernia, without obstruction or gangrene, not specified as recurrent", True, "K40.9"),
    ("K44.9",  "Diaphragmatic hernia without obstruction or gangrene", True, "K44"),
    ("K92.0",  "Haematemesis", True, "K92"),
    ("K92.1",  "Melaena", True, "K92"),

    # -----------------------------------------------------------------------
    # Z SERIES — Screening / history / status (radiology ordering context)
    # -----------------------------------------------------------------------
    ("Z12.39", "Encounter for other screening for malignant neoplasm of breast", True, "Z12.3"),
    ("Z12.73", "Encounter for screening for malignant neoplasm of ovary", True, "Z12.7"),
    ("Z13.820","Encounter for screening for osteoporosis", True, "Z13.82"),
    ("Z15.01", "Genetic susceptibility to malignant neoplasm of breast", True, "Z15.0"),
    ("Z15.09", "Genetic susceptibility to other malignant neoplasm", True, "Z15.0"),
    ("Z47.1",  "Aftercare following joint replacement surgery", True, "Z47"),
    ("Z79.01", "Long-term (current) use of anticoagulants", True, "Z79.0"),
    ("Z79.02", "Long-term (current) use of antithrombotics/antiplatelets", True, "Z79.0"),
    ("Z79.4",  "Long-term (current) use of insulin", True, "Z79"),
    ("Z79.52", "Long-term (current) use of systemic steroids", True, "Z79.5"),
    ("Z80.3",  "Family history of malignant neoplasm of breast", True, "Z80"),
    ("Z85.3",  "Personal history of malignant neoplasm of breast", True, "Z85"),
    ("Z85.46", "Personal history of malignant neoplasm of prostate", True, "Z85.4"),
    ("Z85.118","Personal history of malignant neoplasm of other part of bronchus and lung", True, "Z85.11"),
    ("Z86.711","Personal history of pulmonary embolism", True, "Z86.71"),
    ("Z86.010","Personal history of colonic polyps", True, "Z86.01"),
    ("Z87.01", "Personal history of pneumonia (recurrent)", True, "Z87.0"),
    ("Z87.310","Personal history of (healed) traumatic fracture", True, "Z87.31"),
    ("Z87.39", "Personal history of other musculoskeletal disorders", True, "Z87.3"),
    ("Z87.891","Personal history of other specified conditions", True, "Z87.89"),
    ("Z95.0",  "Presence of cardiac pacemaker", True, "Z95"),
    ("Z95.1",  "Presence of aortocoronary bypass graft", True, "Z95"),
    ("Z96.641","Presence of right artificial knee joint", True, "Z96.64"),
    ("Z96.642","Presence of left artificial knee joint", True, "Z96.64"),
    ("Z96.651","Presence of right artificial hip joint", True, "Z96.65"),
    ("Z96.652","Presence of left artificial hip joint", True, "Z96.65"),
    ("Z98.89", "Other specified postprocedural states", True, "Z98.8"),

    # -----------------------------------------------------------------------
    # G SERIES — Neurological indications (brain/spine MRI)
    # -----------------------------------------------------------------------
    ("G35",    "Multiple sclerosis", True, ""),
    ("G43.909","Migraine, unspecified, not intractable, without status migrainosus", True, "G43.90"),
    ("G44.309","Post-traumatic headache, unspecified, not intractable", True, "G44.30"),
    ("G47.33", "Obstructive sleep apnea (adult) (pediatric)", True, "G47.3"),
    ("G56.01", "Carpal tunnel syndrome, right upper limb", True, "G56.0"),
    ("G56.02", "Carpal tunnel syndrome, left upper limb", True, "G56.0"),
    ("G57.01", "Lesion of sciatic nerve, right lower limb", True, "G57.0"),
    ("G57.02", "Lesion of sciatic nerve, left lower limb", True, "G57.0"),
    ("G89.21", "Chronic pain due to trauma", True, "G89.2"),
    ("G89.29", "Other chronic pain", True, "G89.2"),
    ("G89.3",  "Neoplasm related pain (acute) (chronic)", True, "G89"),
    ("G91.0",  "Communicating hydrocephalus", True, "G91"),
    ("G91.1",  "Obstructive hydrocephalus", True, "G91"),
    ("G93.1",  "Anoxic brain damage, not elsewhere classified", True, "G93"),
    ("G93.40", "Encephalopathy, unspecified", True, "G93.4"),
    ("G93.41", "Metabolic encephalopathy", True, "G93.4"),
    ("G93.49", "Other encephalopathy", True, "G93.4"),
    ("G93.5",  "Compression of brain", True, "G93"),
    ("G93.6",  "Cerebral oedema", True, "G93"),
    ("G93.9",  "Disorder of brain, unspecified", True, "G93"),
    ("G95.11", "Acute infarction of spinal cord (embolic) (nonembolic)", True, "G95.1"),
    ("G95.89", "Other specified diseases of spinal cord", True, "G95.8"),
    ("G95.9",  "Disease of spinal cord, unspecified", True, "G95"),
    ("G96.0",  "Cerebrospinal fluid leak, not from spinal puncture", True, "G96"),
    ("I65.21", "Occlusion and stenosis of right carotid artery", True, "I65.2"),
    ("I65.22", "Occlusion and stenosis of left carotid artery", True, "I65.2"),
    ("I65.29", "Occlusion and stenosis of unspecified carotid artery", True, "I65.2"),
    ("I61.9",  "Nontraumatic intracerebral haemorrhage, unspecified", True, "I61"),
    ("I26.09", "Other pulmonary embolism with acute cor pulmonale", True, "I26.0"),
    # non-billable parents for new G/I codes
    ("G93.4",  "Other and unspecified encephalopathy", False, "G93"),
    ("G56.0",  "Carpal tunnel syndrome", False, "G56"),
    ("G57.0",  "Lesion of sciatic nerve", False, "G57"),
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
    # E&M (established / new office visit) — full leveled ranges
    ("99211", "Office/outpatient visit, established patient, minimal (nurse) visit", "EM_OFFICE"),
    ("99212", "Office/outpatient visit, established patient, straightforward MDM", "EM_OFFICE"),
    ("99213", "Office/outpatient visit, established patient, low MDM", "EM_OFFICE"),
    ("99214", "Office/outpatient visit, established patient, moderate MDM", "EM_OFFICE"),
    ("99215", "Office/outpatient visit, established patient, high MDM", "EM_OFFICE"),
    ("99202", "Office/outpatient visit, new patient, straightforward MDM", "EM_OFFICE"),
    ("99203", "Office/outpatient visit, new patient, low MDM", "EM_OFFICE"),
    ("99204", "Office/outpatient visit, new patient, moderate MDM", "EM_OFFICE"),
    ("99205", "Office/outpatient visit, new patient, high MDM", "EM_OFFICE"),
    ("99417", "Prolonged outpatient E&M, each additional 15 minutes (commercial add-on)", "EM_OFFICE"),
    ("G2212", "Prolonged outpatient E&M, each additional 15 minutes (Medicare add-on)", "EM_OFFICE"),
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

    # =======================================================================
    # RADIOLOGY CPT EXPANSION — additional 7-series codes (70000-79999)
    # Real CPT code numbers verified against CMS physician fee schedule and
    # AAPC/AMA published code sets; descriptors are our own paraphrase.
    # =======================================================================

    # --- CT colonography (CT) ---
    ("74261", "CT colonography, diagnostic; including image postprocessing", "CT"),
    ("74262", "CT colonography, screening; including image postprocessing", "CT"),
    # --- GI fluoroscopy / contrast studies (FL) ---
    ("74240", "Radiological exam, upper GI tract; without KUB, single contrast", "FL"),
    ("74246", "Radiological exam, upper GI tract; with or without KUB, double contrast", "FL"),
    ("74247", "Radiological exam, upper GI tract, with small bowel; single or double contrast", "FL"),
    ("74248", "Radiological exam, small intestine; serial films, with or without KUB", "FL"),
    ("74249", "Radiological exam, upper GI tract, air contrast, KUB and/or delayed films", "FL"),
    ("74270", "Radiological exam, colon; single contrast (barium enema)", "FL"),
    ("74280", "Radiological exam, colon; air-contrast (double-contrast barium enema)", "FL"),
    ("74283", "Therapeutic enema, contrast or air, for intussusception or other indication", "FL"),
    ("74300", "Cholangiography and/or pancreatography; intraoperative, radiological supervision", "FL"),
    ("74305", "Cholangiography and/or pancreatography; post-operative, radiological supervision", "FL"),
    ("74320", "Cholangiography, percutaneous, transhepatic", "FL"),
    ("74340", "Introduction of long gastrointestinal tube, fluoroscopic guidance", "FL"),
    ("74355", "Percutaneous placement of gastrostomy or gastrojejunostomy tube", "FL"),
    ("74360", "Intraluminal dilation of stenotic bowel via balloon catheter", "FL"),
    ("74363", "Percutaneous transhepatic dilation of biliary duct stricture", "FL"),
    # --- Urinary tract / genitourinary fluoroscopy (FL) ---
    ("74400", "Urography (excretory or IV pyelography); with or without KUB", "FL"),
    ("74410", "Urography, infusion method; drip technique", "FL"),
    ("74415", "Urography, infusion method; with nephrotomography", "FL"),
    ("74420", "Urography, retrograde, with or without KUB", "FL"),
    ("74430", "Cystography; minimum 3 views, radiological supervision", "FL"),
    ("74450", "Urethrocystography, retrograde; radiological supervision", "FL"),
    ("74455", "Urethrocystography, voiding (VCUG); radiological supervision", "FL"),
    ("74470", "Radiological examination, renal cyst aspiration or injection", "FL"),
    ("74480", "Introduction of ureteral catheter or stent; radiological supervision", "FL"),
    ("74485", "Dilation of ureter or ureteral stricture; radiological supervision", "FL"),
    # --- Cardiac MRI (MRI) ---
    ("75557", "Cardiac MRI for morphology and function; without contrast", "MRI"),
    ("75559", "Cardiac MRI for morphology and function; without and with contrast", "MRI"),
    ("75561", "Cardiac MRI for morphology and function; without contrast, with cardiovascular stress imaging", "MRI"),
    ("75563", "Cardiac MRI for morphology and function; without and with contrast, with stress imaging", "MRI"),
    # --- Invasive angiography / venography (radiological supervision) (IR) ---
    ("75600", "Aortography, thoracic, by serialography; radiological supervision and interpretation", "IR"),
    ("75625", "Aortography, abdominal; by serialography, radiological supervision", "IR"),
    ("75630", "Aortography, abdominal plus bilateral iliofemoral runoff; radiological supervision", "IR"),
    ("75710", "Angiography, extremity, unilateral; radiological supervision", "IR"),
    ("75716", "Angiography, extremity, bilateral; radiological supervision", "IR"),
    ("75726", "Angiography, visceral, selective or superselective; radiological supervision", "IR"),
    ("75736", "Angiography, pelvic; radiological supervision", "IR"),
    ("75743", "Angiography, pulmonary, unilateral; radiological supervision", "IR"),
    ("75746", "Angiography, pulmonary, bilateral; radiological supervision", "IR"),
    ("75756", "Angiography, cervicocerebral, unilateral; radiological supervision", "IR"),
    ("75774", "Angiography, selective, each additional vessel after basic study (add-on)", "IR"),
    ("75820", "Venography, extremity, unilateral; radiological supervision", "IR"),
    ("75822", "Venography, extremity, bilateral; radiological supervision", "IR"),
    ("75825", "Venography, caval; superior or inferior, radiological supervision", "IR"),
    ("75827", "Venography, superior vena cava; radiological supervision", "IR"),
    ("75860", "Venography, venous sinus (dural venous sinus); radiological supervision", "IR"),
    ("75889", "Hepatic venography, wedge or free; radiological supervision", "IR"),
    ("75891", "Hepatic venography, wedge pressure measurement only; radiological supervision", "IR"),
    # --- Ultrasound guidance / elastography / specialized US (US) ---
    ("76376", "3D rendering of CT, MRI, or ultrasound imaging data; not requiring concurrent supervision", "US"),
    ("76377", "3D rendering; with postprocessing under concurrent physician supervision", "US"),
    ("76390", "MR spectroscopy", "MRI"),
    ("76391", "MRI, elastography", "MRI"),
    ("76510", "Ophthalmic ultrasound, diagnostic; complete with A and B scan", "US"),
    ("76512", "Ophthalmic ultrasound; B-scan, with or without quantitative A-scan", "US"),
    ("76514", "Corneal pachymetry, unilateral or bilateral", "US"),
    ("76516", "Ophthalmic biometry by ultrasound echography; A-scan only", "US"),
    ("76519", "Ophthalmic biometry by ultrasound; A-scan with intraocular lens power calculation", "US"),
    ("76800", "Ultrasound, spinal canal and contents", "US"),
    ("76936", "Ultrasound guided compression repair of arterial pseudoaneurysm or AV fistula", "US"),
    ("76937", "Ultrasound guidance for vascular access, evaluation of access sites", "US"),
    ("76940", "Ultrasound guidance for parenchymal tissue ablation monitoring", "US"),
    ("76942", "Ultrasonic guidance for needle placement (biopsy, aspiration, injection, or localization)", "US"),
    ("76946", "Ultrasonic guidance for amniocentesis, imaging supervision and interpretation", "US"),
    ("76965", "Ultrasonic guidance for interstitial radioelement application", "US"),
    ("76977", "Ultrasound bone density measurement, peripheral site(s)", "US"),
    ("76978", "Ultrasound, targeted dynamic microbubble sonographic contrast; first lesion", "US"),
    ("76979", "Ultrasound, targeted dynamic microbubble sonographic contrast; each additional lesion (add-on)", "US"),
    ("76981", "Ultrasound elastography; parenchyma (e.g., organ)", "US"),
    ("76982", "Ultrasound elastography; first target lesion", "US"),
    ("76983", "Ultrasound elastography; each additional target lesion (add-on)", "US"),
    # --- Nuclear medicine (NM) ---
    # Thyroid / parathyroid
    ("78012", "Thyroid uptake, multiple determinations; measurement and report", "NM"),
    ("78013", "Thyroid imaging; with or without vascular flow", "NM"),
    ("78014", "Thyroid imaging; with vascular flow", "NM"),
    ("78015", "Thyroid carcinoma metastases imaging; limited area", "NM"),
    ("78018", "Thyroid carcinoma metastases imaging; whole body", "NM"),
    ("78070", "Parathyroid planar imaging; with or without subtraction", "NM"),
    ("78071", "Parathyroid planar imaging with SPECT", "NM"),
    ("78072", "Parathyroid planar imaging with SPECT and concurrently acquired CT", "NM"),
    # Hepatobiliary / GI
    ("78215", "Liver and spleen imaging; static only", "NM"),
    ("78216", "Liver and spleen imaging; static and vascular flow", "NM"),
    ("78226", "Hepatobiliary system imaging (HIDA scan); including gallbladder", "NM"),
    ("78227", "Hepatobiliary system imaging; including gallbladder, with pharmacologic intervention (CCK/morphine)", "NM"),
    ("78278", "Acute GI blood loss imaging", "NM"),
    ("78290", "Meckel's diverticulum and intestinal transit imaging", "NM"),
    # Bone
    ("78300", "Bone and/or joint imaging; limited area", "NM"),
    ("78305", "Bone and/or joint imaging; multiple areas", "NM"),
    ("78306", "Bone and/or joint imaging; whole body", "NM"),
    ("78315", "Bone and/or joint imaging; 3-phase study", "NM"),
    ("78320", "Bone and/or joint imaging; tomographic (SPECT)", "NM"),
    ("78350", "Bone density, dual photon absorptiometry; axial skeleton (spine/hip)", "NM"),
    ("78351", "Bone density, dual photon absorptiometry; appendicular skeleton", "NM"),
    # Cardiac
    ("78451", "Myocardial perfusion imaging, tomographic (SPECT); single study at rest or stress", "NM"),
    ("78452", "Myocardial perfusion imaging, tomographic (SPECT); multiple studies at rest and/or stress", "NM"),
    ("78459", "Myocardial imaging, PET; metabolic evaluation study with or without quantification", "NM"),
    ("78469", "Myocardial imaging, PET; perfusion study with or without quantification", "NM"),
    ("78472", "Cardiac blood pool imaging, gated equilibrium; planar, single study", "NM"),
    ("78473", "Cardiac blood pool imaging, gated equilibrium; multiple studies", "NM"),
    ("78481", "Cardiac blood pool imaging; first pass technique, single study", "NM"),
    ("78491", "Myocardial imaging, PET, perfusion; single study at rest or stress", "NM"),
    ("78492", "Myocardial imaging, PET, perfusion; multiple studies at rest and/or stress", "NM"),
    ("78494", "Cardiac blood pool imaging, SPECT", "NM"),
    # Pulmonary
    ("78579", "Pulmonary ventilation imaging; aerosol", "NM"),
    ("78580", "Pulmonary perfusion imaging; with or without quantification", "NM"),
    ("78582", "Pulmonary ventilation and perfusion imaging; with or without quantification (V/Q scan)", "NM"),
    ("78597", "Quantitative differential pulmonary perfusion; without ventilation", "NM"),
    ("78598", "Quantitative differential pulmonary perfusion and ventilation imaging", "NM"),
    # Brain / CNS
    ("78600", "Brain imaging, planar; limited", "NM"),
    ("78606", "Brain imaging, planar; with vascular flow", "NM"),
    ("78610", "Brain imaging, vascular flow only", "NM"),
    ("78630", "Cerebrospinal fluid flow imaging (not including cisternography)", "NM"),
    ("78635", "Cerebrospinal fluid flow imaging, complete (including cisternography)", "NM"),
    ("78645", "Cerebrospinal fluid shunt evaluation", "NM"),
    # Genitourinary / renal
    ("78700", "Kidney imaging morphology; without pharmacologic intervention", "NM"),
    ("78707", "Kidney imaging morphology; with vascular flow and function, without pharmacologic intervention", "NM"),
    ("78708", "Kidney imaging morphology; with vascular flow and function, with pharmacologic intervention", "NM"),
    ("78725", "Kidney function study, non-imaging radioisotopic technique", "NM"),
    ("78740", "Ureteral reflux study, radionuclide cystogram", "NM"),
    ("78761", "Testicular imaging with vascular flow", "NM"),
    # Tumor / infection localization
    ("78800", "Radiopharmaceutical localization of tumor or distribution, planar; limited area", "NM"),
    ("78801", "Radiopharmaceutical localization of tumor; planar, multiple areas", "NM"),
    ("78802", "Radiopharmaceutical localization of tumor; whole body", "NM"),
    ("78803", "Radiopharmaceutical localization of tumor; tomographic (SPECT)", "NM"),
    ("78804", "Radiopharmaceutical localization of tumor; whole body, multiple days imaging", "NM"),
    ("78805", "Radiopharmaceutical localization of inflammatory process; planar, limited area", "NM"),
    ("78806", "Radiopharmaceutical localization of inflammatory process; whole body", "NM"),
    ("78807", "Radiopharmaceutical localization of inflammatory process; tomographic (SPECT)", "NM"),
    # PET / PET-CT (oncology)
    ("78811", "Tumor imaging, whole body; PET only", "NM"),
    ("78812", "Tumor imaging, whole body; PET with concurrently acquired CT (without contrast)", "NM"),
    ("78813", "Tumor imaging, whole body; PET with concurrently acquired CT (with contrast)", "NM"),
    ("78814", "Tumor imaging, limited area (skull base to mid-thigh); PET only", "NM"),
    ("78815", "Tumor imaging, limited area; PET with concurrently acquired CT (without contrast)", "NM"),
    ("78816", "Tumor imaging, limited area; PET with concurrently acquired CT (with contrast)", "NM"),
    # SPECT/CT hybrid
    ("78830", "SPECT with concurrently acquired CT (without contrast); for attenuation correction/localization", "NM"),
    ("78832", "SPECT/CT; with concurrently acquired CT (with or without contrast)", "NM"),
    ("78835", "SPECT/CT; additional study", "NM"),
    # --- Radiation therapy planning (RT) ---
    ("77295", "3-dimensional radiotherapy plan, including dose-volume histograms", "RT"),
    ("77300", "Basic radiation dosimetry calculation, direct measurement", "RT"),
    ("77301", "Intensity modulated radiotherapy (IMRT) plan, including dose-volume histograms", "RT"),
    ("77338", "Multi-leaf collimator (MLC) device(s) for IMRT plan design and construction (add-on)", "RT"),
    ("77370", "Special medical radiation physics consultation", "RT"),
    ("77371", "Stereotactic radiosurgery (SRS); multi-source cobalt 60 based, first session", "RT"),
    ("77372", "Stereotactic radiosurgery (SRS); linear accelerator based, first session", "RT"),
    ("77373", "Stereotactic body radiation therapy (SBRT), treatment delivery, per fraction", "RT"),
    ("77385", "Intensity modulated radiation treatment delivery (IMRT); simple", "RT"),
    ("77386", "Intensity modulated radiation treatment delivery (IMRT); complex", "RT"),
    ("77387", "Guidance for localization of target volume for delivery of radiation treatment", "RT"),
    ("77402", "Radiation treatment delivery, ≥1 MeV; simple", "RT"),
    ("77407", "Radiation treatment delivery, ≥1 MeV; intermediate", "RT"),
    ("77412", "Radiation treatment delivery, ≥1 MeV; complex", "RT"),
    ("77432", "Stereotactic radiation treatment management of cranial lesion(s)", "RT"),
    ("77435", "Stereotactic body radiation therapy, treatment management, per treatment course", "RT"),
    ("77469", "Intraoperative radiation treatment management", "RT"),
    ("77470", "Special treatment procedure (e.g., total body irradiation, hemibody irradiation, per oral or endocavitary irradiation)", "RT"),
    # --- Unlisted radiology procedure codes ---
    ("76496", "Unlisted fluoroscopic procedure", "FL"),
    ("76497", "Unlisted CT procedure", "CT"),
    ("76498", "Unlisted MRI procedure", "MRI"),
    ("76499", "Unlisted diagnostic radiographic procedure", "XR"),
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
    # Drugs and devices (real public HCPCS Level II — medication/device extraction slots)
    ("J0178", "Injection, aflibercept, 1 mg", "OPHTH"),
    ("J7298", "Levonorgestrel-releasing intrauterine contraceptive system, 52 mg, 5-year duration", "OBGYN"),
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
    ("74176", "74150", True, "CT abdomen component of combined abd+pelvis; modifier -59 if genuinely separate"),
    ("74176", "72192", True, "CT pelvis component of combined abd+pelvis; modifier -59 if genuinely separate"),
    ("74177", "74150", True, "CT abdomen component of combined w/contrast; modifier -59 if genuinely separate"),
    ("74177", "72192", True, "CT pelvis component of combined w/contrast; modifier -59 if genuinely separate"),
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
    # -------------------------------------------------------------------------
    # CMS Practitioner PTP Edits v32.2.0 / Q3 2026 (effective 2026-07-01)
    # Source: payerready.com NCCI Bundling DB (675 K+ records; tool cap = 10/col1)
    # Indicator 0 → modifier_allowed=False (hard bundle, no override)
    # Indicator 1 → modifier_allowed=True  (modifier -59/XE/XS/XP/XU may unbundle)
    # Indicator 9 (inactive/deleted) edits are omitted — both codes freely billable.
    # Pairs that duplicated existing entries above are also omitted.
    # -------------------------------------------------------------------------

    # --- Plain X-ray: skull / facial ---
    ("70110", "36591", False, "Blood collection from implanted venous access device bundled with imaging"),
    ("70110", "36592", False, "Blood collection from central line bundled with imaging"),
    ("70110", "70100", False, "Mandible complete (4 views) includes less-than-complete study"),
    ("70110", "96523", False, "Irrigation of implanted venous access device bundled with imaging"),
    ("70160", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70160", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70160", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70250", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70250", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70250", "70260", False, "Skull complete (4+ views) includes less-complete study"),
    ("70250", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70330", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70330", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70330", "70328", True, "Unilateral TMJ X-ray included in bilateral; modifier if truly unilateral only"),
    ("70330", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70360", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70360", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70360", "96523", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- Plain X-ray: chest ---
    ("71045", "0175T", True, "Transthoracic echo guidance; modifier if distinct procedure"),
    ("71045", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71045", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71045", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71046", "0175T", True, "Transthoracic echo guidance with 2-view chest; modifier if distinct"),
    ("71046", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71046", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71046", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71047", "0175T", True, "Echo guidance with 3-view chest; modifier if distinct"),
    ("71047", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71047", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71047", "71045", True, "Single-view chest included in 3-view; modifier if distinct"),
    ("71047", "71046", True, "Two-view chest included in 3-view; modifier if distinct"),
    ("71047", "71101", True, "Bilateral ribs w/chest included in 3-view chest; modifier if distinct"),
    ("71047", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71100", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71100", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71100", "71010", True, "Unilateral rib X-ray included in bilateral rib without chest; modifier if distinct"),
    ("71100", "71020", True, "Chest 2-view included in bilateral rib with chest; modifier if distinct"),
    ("71100", "71022", True, "Unilateral rib+chest included in bilateral rib+chest; modifier if distinct"),
    ("71100", "71030", True, "Chest 4+ views included in bilateral rib+chest study; modifier if distinct"),
    ("71100", "71045", True, "Single-view chest included in bilateral rib+chest; modifier if distinct"),
    ("71100", "71110", True, "Bilateral ribs 3 views included in bilateral ribs 4 views; modifier if distinct"),
    ("71100", "71111", True, "Bilateral ribs+chest included in comprehensive bilateral rib study; modifier if distinct"),
    ("71100", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71101", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71101", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71101", "71010", True, "Unilateral rib included in unilateral rib+chest; modifier if distinct"),
    ("71101", "71021", True, "Unilateral rib+chest (fewer views) included in comprehensive; modifier if distinct"),
    ("71101", "71022", True, "Component included in comprehensive unilateral rib study; modifier if distinct"),
    ("71101", "71023", True, "Component included in comprehensive unilateral rib study; modifier if distinct"),
    ("71101", "71030", True, "Chest 4+ views included in unilateral rib+chest; modifier if distinct"),
    ("71101", "71034", True, "Chest+fluoro included in unilateral rib study; modifier if distinct"),
    ("71101", "71045", True, "Single-view chest included in unilateral rib+chest; modifier if distinct"),
    ("71101", "71046", True, "Two-view chest included in unilateral rib+chest; modifier if distinct"),

    # --- Plain X-ray: spine ---
    ("72040", "0348T", True, "External fixation system; modifier if anatomically distinct"),
    ("72040", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72040", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72040", "72010", True, "Full spine survey included in cervical spine; modifier if distinct"),
    ("72040", "72050", True, "Cervical 4+ views included in 2-3 view study; modifier if distinct"),
    ("72040", "72052", True, "Cervical flex/ext included in cervical spine; modifier if distinct"),
    ("72040", "72081", True, "Spine 1-view included in cervical spine; modifier if distinct"),
    ("72040", "72082", True, "Spine 2-3 views included in cervical spine; modifier if distinct"),
    ("72040", "72083", True, "Spine 4-5 views included in cervical spine; modifier if distinct"),
    ("72040", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72072", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72072", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72072", "72070", True, "Thoracic spine 2-3 views included in 4+ views; modifier if distinct"),
    ("72072", "72080", True, "Thoracic spine 1 view included in 2-3 views; modifier if distinct"),
    ("72072", "72090", True, "Scoliosis study included in thoracic spine; modifier if distinct"),
    ("72072", "96523", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- Plain X-ray: pelvis / hip ---
    ("72170", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72170", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72170", "72190", True, "Pelvis AP included in complete pelvis study; modifier if distinct"),
    ("72170", "73501", True, "Hip unilateral 1-view included with pelvis; modifier if distinct"),
    ("72170", "73502", True, "Hip unilateral 2-view included with pelvis; modifier if distinct"),
    ("72170", "73503", True, "Hip unilateral 3+-view included with pelvis; modifier if distinct"),
    ("72170", "73520", True, "Bilateral hips included with pelvis; modifier if distinct"),
    ("72170", "73521", True, "Bilateral hip 1-view included with pelvis; modifier if distinct"),
    ("72170", "73522", True, "Bilateral hip 2-view included with pelvis; modifier if distinct"),
    ("72170", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72220", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72220", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72220", "72081", True, "Spine 1-view included in sacrum/coccyx study; modifier if distinct"),
    ("72220", "72082", True, "Spine 2-3 views included in sacrum/coccyx; modifier if distinct"),
    ("72220", "72083", True, "Spine 4-5 views included in sacrum/coccyx; modifier if distinct"),
    ("72220", "72084", True, "Spine 6+ views included in sacrum/coccyx; modifier if distinct"),
    ("72220", "73542", True, "Sacroiliac joints included in sacrum/coccyx; modifier if distinct"),
    ("72220", "96523", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- Plain X-ray: upper extremity ---
    ("73080", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73080", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73080", "73070", True, "Elbow 2-view included in 3+ view; modifier if distinct"),
    ("73080", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73090", "0349T", True, "Bone fixation device service; modifier if distinct"),
    ("73090", "20696", True, "External fixation system adjustment; modifier if distinct"),
    ("73090", "20697", True, "External fixation system adjustment; modifier if distinct"),
    ("73090", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73090", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73090", "73092", False, "Forearm 2-view includes infant forearm X-ray; not separately reportable"),
    ("73090", "76006", True, "Stress view of forearm; modifier if distinct"),
    ("73090", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73130", "0349T", True, "Bone fixation device service; modifier if distinct"),
    ("73130", "0749T", True, "Included procedure; modifier if distinct"),
    ("73130", "0750T", True, "Included procedure; modifier if distinct"),
    ("73130", "20696", True, "External fixation system adjustment; modifier if distinct"),
    ("73130", "20697", True, "External fixation system adjustment; modifier if distinct"),
    ("73130", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73130", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73130", "73120", True, "Hand 2-view included in 3+ view; modifier if distinct"),
    ("73130", "73140", True, "Finger X-ray included in hand study; modifier if distinct"),
    ("73130", "96523", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- Plain X-ray: lower extremity (hip) ---
    ("73502", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73502", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73502", "72170", True, "Pelvis included with hip 2-view; modifier if distinct"),
    ("73502", "72190", True, "AP pelvis included with hip 2-view; modifier if distinct"),
    ("73502", "73501", True, "Hip 1-view included in hip 2-view; modifier if distinct"),
    ("73502", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73503", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73503", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73503", "72170", True, "Pelvis included with hip 3+-view; modifier if distinct"),
    ("73503", "72190", True, "AP pelvis included with hip 3+-view; modifier if distinct"),
    ("73503", "73501", True, "Hip 1-view included in hip 3+-view; modifier if distinct"),
    ("73503", "73502", True, "Hip 2-view included in hip 3+-view; modifier if distinct"),
    ("73503", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73523", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73523", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73523", "72170", True, "Pelvis included with bilateral hip; modifier if distinct"),
    ("73523", "72190", True, "AP pelvis included with bilateral hip; modifier if distinct"),
    ("73523", "73501", True, "Hip unilateral 1-view included in bilateral; modifier if distinct"),
    ("73523", "73502", True, "Hip unilateral 2-view included in bilateral; modifier if distinct"),
    ("73523", "73503", True, "Hip unilateral 3+-view included in bilateral; modifier if distinct"),
    ("73523", "73521", True, "Bilateral hip 1-view included in bilateral hip 2-3 view; modifier if distinct"),
    ("73523", "73522", True, "Bilateral hip 2-view included in bilateral hip 3+ view; modifier if distinct"),
    ("73523", "96523", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- Plain X-ray: lower extremity (femur / knee / leg / ankle / foot) ---
    ("73552", "0350T", True, "Bone fixation device service; modifier if distinct"),
    ("73552", "20696", True, "External fixation system adjustment; modifier if distinct"),
    ("73552", "20697", True, "External fixation system adjustment; modifier if distinct"),
    ("73552", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73552", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73552", "73551", True, "Femur 1-view included in femur 2-view; modifier if distinct"),
    ("73552", "77073", True, "Bone length study included in femur X-ray; modifier if distinct"),
    ("73552", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73562", "01380", False, "Anesthesia for knee procedures bundled with knee X-ray"),
    ("73562", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73562", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73562", "73560", True, "Knee 1-view included in knee 2-view; modifier if distinct"),
    ("73562", "73565", False, "AP weight-bearing knee included in knee 2-view with WB; not separately reportable"),
    ("73562", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73590", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73590", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73590", "73592", True, "Infant/child leg X-ray included in tibia/fibula; modifier if distinct"),
    ("73590", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73600", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73600", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73600", "73592", True, "Infant/child leg included in ankle 2-view; modifier if distinct"),
    ("73600", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73610", "0350T", True, "Bone fixation device service; modifier if distinct"),
    ("73610", "20696", True, "External fixation system adjustment; modifier if distinct"),
    ("73610", "20697", True, "External fixation system adjustment; modifier if distinct"),
    ("73610", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73610", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73610", "73592", True, "Infant/child leg included in ankle 3+ view; modifier if distinct"),
    ("73610", "73600", False, "Ankle 2-view included in ankle 3+-view; not separately reportable"),
    ("73610", "73615", True, "Ankle arthrography included in ankle 3+-view; modifier if distinct"),
    ("73610", "73630", True, "Foot X-ray included with ankle; modifier if distinct"),
    ("73610", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73620", "0350T", True, "Bone fixation device service; modifier if distinct"),
    ("73620", "20696", True, "External fixation system adjustment; modifier if distinct"),
    ("73620", "20697", True, "External fixation system adjustment; modifier if distinct"),
    ("73620", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73620", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73620", "73630", True, "Foot 3+ views; modifier if distinct from foot 2-view"),
    ("73620", "73660", True, "Toe X-ray included in foot study; modifier if distinct"),
    ("73620", "76006", True, "Stress view of foot; modifier if distinct"),
    ("73620", "77075", True, "Long bone survey included in foot study; modifier if distinct"),
    ("73620", "96523", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- Plain X-ray: abdomen ---
    ("74018", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74018", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74018", "74019", True, "Abdomen 2-view included in abdomen 1-view series; modifier if distinct"),
    ("74018", "74021", True, "Abdomen 3-view included in 1-view; modifier if distinct"),
    ("74018", "74022", True, "Abdomen complete series (4+) included; modifier if distinct"),
    ("74018", "74240", True, "UGI series included with abdomen; modifier if distinct"),
    ("74018", "74241", True, "UGI with KUB included with abdomen; modifier if distinct"),
    ("74018", "74245", True, "UGI+small bowel included with abdomen; modifier if distinct"),
    ("74018", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74021", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74021", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74021", "74018", True, "Abdomen 1-view included in 2-view; modifier if distinct"),
    ("74021", "74019", True, "Abdomen 2-view included in 3-view; modifier if distinct"),
    ("74021", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74022", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74022", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74022", "71010", True, "Chest 1-view included in abdomen series+chest; modifier if distinct"),
    ("74022", "71045", True, "Chest single view included in abdomen series; modifier if distinct"),
    ("74022", "74000", True, "Abdomen AP included in complete series; modifier if distinct"),
    ("74022", "74010", True, "Abdomen AP+lat included in complete series; modifier if distinct"),
    ("74022", "74018", True, "Abdomen 1-view included in complete series; modifier if distinct"),
    ("74022", "74019", True, "Abdomen 2-view included in complete series; modifier if distinct"),
    ("74022", "74020", True, "Abdomen decubitus included in complete series; modifier if distinct"),
    ("74022", "74021", True, "Abdomen 3-view included in complete series; modifier if distinct"),

    # --- Plain X-ray / fluoroscopy: urography / fluoroscopy ---
    ("74420", "0596T", False, "Ureteral catheterization bundled with urography"),
    ("74420", "0597T", False, "Ureteral catheterization bundled with urography"),
    ("74420", "0708T", True, "Included procedure; modifier if distinct"),
    ("74420", "0709T", True, "Included procedure; modifier if distinct"),
    ("74420", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("74420", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("74420", "36410", True, "Venipuncture; modifier if distinct"),
    ("74420", "36425", True, "Venipuncture; modifier if distinct"),
    ("74420", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74420", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("76000", "01922", False, "Anesthesia for radiological procedure bundled with fluoroscopy"),
    ("76000", "0544T", True, "Implanted cardiac monitor; modifier if distinct"),
    ("76000", "0548T", True, "Included procedure; modifier if distinct"),
    ("76000", "0571T", True, "Included procedure; modifier if distinct"),
    ("76000", "0572T", True, "Included procedure; modifier if distinct"),
    ("76000", "0573T", True, "Included procedure; modifier if distinct"),
    ("76000", "0574T", True, "Included procedure; modifier if distinct"),
    ("76000", "0581T", True, "Included procedure; modifier if distinct"),
    ("76000", "0582T", True, "Included procedure; modifier if distinct"),
    ("76000", "0584T", True, "Included procedure; modifier if distinct"),
    ("76010", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("76010", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("76010", "71010", True, "Chest 1-view included in foreign body X-ray; modifier if distinct"),
    ("76010", "71015", True, "Chest stereo included in foreign body X-ray; modifier if distinct"),
    ("76010", "71020", True, "Chest 2-view included in foreign body X-ray; modifier if distinct"),
    ("76010", "71021", True, "Chest 1-view+apical included in foreign body X-ray; modifier if distinct"),
    ("76010", "71022", True, "Chest 2-view+apical included in foreign body X-ray; modifier if distinct"),
    ("76010", "71023", True, "Chest 2-view+fluoro included in foreign body X-ray; modifier if distinct"),
    ("76010", "71030", True, "Chest 4+ views included in foreign body X-ray; modifier if distinct"),
    ("76010", "71034", True, "Chest+fluoroscopy included in foreign body X-ray; modifier if distinct"),

    # --- CT: head / neck ---
    ("70450", "01922", False, "Anesthesia for radiological procedure bundled with CT head w/o"),
    ("70450", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70450", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70450", "70480", True, "CT orbit/ear w/o included in CT head w/o; modifier if distinct"),
    ("70450", "70481", True, "CT orbit/ear with contrast included; modifier if distinct"),
    ("70450", "70482", True, "CT orbit/ear w/o+with included; modifier if distinct"),
    ("70450", "76350", False, "Computed tomography guidance bundled with CT head"),
    ("70460", "01922", False, "Anesthesia bundled with CT head with contrast"),
    ("70460", "0708T", True, "Included procedure; modifier if distinct"),
    ("70460", "0709T", True, "Included procedure; modifier if distinct"),
    ("70460", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("70460", "36005", True, "IV injection for venography; modifier if distinct"),
    ("70460", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("70460", "36406", True, "Venipuncture; modifier if distinct"),
    ("70460", "36410", True, "Venipuncture; modifier if distinct"),
    ("70460", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70460", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70480", "01922", False, "Anesthesia bundled with CT orbit/ear/fossa w/o"),
    ("70480", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70480", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70480", "76350", False, "CT guidance bundled with CT orbit"),
    ("70480", "76380", True, "Limited follow-up CT; modifier if distinct"),
    ("70480", "92002", True, "Eye exam included; modifier if distinct"),
    ("70480", "92004", True, "Eye exam included; modifier if distinct"),
    ("70480", "92012", True, "Eye exam included; modifier if distinct"),
    ("70480", "92014", True, "Eye exam included; modifier if distinct"),
    ("70480", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70486", "01922", False, "Anesthesia bundled with CT maxillofacial w/o"),
    ("70486", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70486", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70486", "76350", False, "CT guidance bundled with CT maxillofacial"),
    ("70486", "76380", True, "Limited follow-up CT; modifier if distinct"),
    ("70486", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70490", "01922", False, "Anesthesia bundled with CT soft tissue neck w/o"),
    ("70490", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70490", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70490", "76350", False, "CT guidance bundled with CT neck"),
    ("70490", "76380", True, "Limited follow-up CT; modifier if distinct"),
    ("70490", "78072", True, "Parathyroid imaging; modifier if distinct"),
    ("70490", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70496", "01916", False, "Anesthesia for CTA procedure bundled"),
    ("70496", "01922", False, "Anesthesia for radiological procedure bundled with CTA head"),
    ("70496", "01924", False, "Anesthesia bundled with CTA head"),
    ("70496", "01925", False, "Anesthesia bundled with CTA head"),
    ("70496", "01926", False, "Anesthesia bundled with CTA head"),
    ("70496", "0694T", False, "Included procedure bundled with CTA head"),
    ("70496", "0708T", True, "Included procedure; modifier if distinct"),
    ("70496", "0709T", True, "Included procedure; modifier if distinct"),
    ("70496", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("70496", "36005", True, "IV injection; modifier if distinct"),

    # --- CT: chest ---
    ("71250", "01922", False, "Anesthesia bundled with CT chest w/o"),
    ("71250", "0558T", True, "Included procedure; modifier if distinct"),
    ("71250", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71250", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71250", "71271", False, "CT chest lung cancer screening included in standard CT chest w/o"),
    ("71250", "75571", True, "Cardiac CT for calcium scoring; modifier if distinct"),
    ("71250", "76350", False, "CT guidance bundled with CT chest"),
    ("71250", "76380", True, "Limited follow-up CT; modifier if distinct"),
    ("71250", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71275", "01916", False, "Anesthesia bundled with CTA chest"),
    ("71275", "01922", False, "Anesthesia bundled with CTA chest"),
    ("71275", "01924", False, "Anesthesia bundled with CTA chest"),
    ("71275", "01925", False, "Anesthesia bundled with CTA chest"),
    ("71275", "01926", False, "Anesthesia bundled with CTA chest"),
    ("71275", "0558T", True, "Included procedure; modifier if distinct"),
    ("71275", "0694T", False, "Included procedure bundled with CTA chest"),
    ("71275", "0708T", True, "Included procedure; modifier if distinct"),
    ("71275", "0709T", True, "Included procedure; modifier if distinct"),
    ("71275", "36000", True, "Peripheral IV placement; modifier if distinct"),

    # --- CT: spine ---
    ("72125", "01922", False, "Anesthesia bundled with CT cervical spine w/o"),
    ("72125", "0558T", True, "Included procedure; modifier if distinct"),
    ("72125", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72125", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72125", "72240", True, "Myelography cervical included with CT cervical; modifier if distinct"),
    ("72125", "72270", True, "Myelography complete included; modifier if distinct"),
    ("72125", "72292", True, "CT myelography included; modifier if distinct"),
    ("72125", "76350", False, "CT guidance bundled with CT cervical spine"),
    ("72125", "76380", True, "Limited follow-up CT; modifier if distinct"),
    ("72125", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72128", "01922", False, "Anesthesia bundled with CT thoracic spine w/o"),
    ("72128", "0558T", True, "Included procedure; modifier if distinct"),
    ("72128", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72128", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72128", "72255", True, "Myelography thoracic included with CT thoracic; modifier if distinct"),
    ("72128", "72270", True, "Myelography complete included; modifier if distinct"),
    ("72128", "72292", True, "CT myelography included; modifier if distinct"),
    ("72128", "76350", False, "CT guidance bundled with CT thoracic spine"),
    ("72128", "76380", True, "Limited follow-up CT; modifier if distinct"),
    ("72128", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72131", "01922", False, "Anesthesia bundled with CT lumbar spine w/o"),
    ("72131", "0558T", True, "Included procedure; modifier if distinct"),
    ("72131", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72131", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72131", "72265", True, "Myelography lumbar included with CT lumbar; modifier if distinct"),
    ("72131", "72270", True, "Myelography complete included; modifier if distinct"),
    ("72131", "72292", True, "CT myelography included; modifier if distinct"),
    ("72131", "76350", False, "CT guidance bundled with CT lumbar spine"),
    ("72131", "76380", True, "Limited follow-up CT; modifier if distinct"),
    ("72131", "96523", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- CT/CTA: abdomen and pelvis ---
    ("74174", "01916", False, "Anesthesia bundled with CTA abdomen+pelvis"),
    ("74174", "01922", False, "Anesthesia bundled with CTA abdomen+pelvis"),
    ("74174", "01924", False, "Anesthesia bundled with CTA abdomen+pelvis"),
    ("74174", "01925", False, "Anesthesia bundled with CTA abdomen+pelvis"),
    ("74174", "01926", False, "Anesthesia bundled with CTA abdomen+pelvis"),
    ("74174", "0558T", True, "Included procedure; modifier if distinct"),
    ("74174", "0694T", False, "Included procedure bundled with CTA abdomen+pelvis"),
    ("74174", "0708T", True, "Included procedure; modifier if distinct"),
    ("74174", "0709T", True, "Included procedure; modifier if distinct"),
    ("74174", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("74176", "01922", False, "Anesthesia bundled with CT abdomen+pelvis w/o"),
    ("74176", "0558T", True, "Included procedure; modifier if distinct"),
    ("74176", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74176", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74176", "72193", True, "CT pelvis with contrast component; modifier if distinct"),
    ("74176", "72194", True, "CT pelvis w/o then with component; modifier if distinct"),
    ("74176", "74160", True, "CT abdomen with contrast component; modifier if distinct"),
    ("74176", "74170", True, "CT abdomen w/o then with component; modifier if distinct"),
    ("74177", "01922", False, "Anesthesia bundled with CT abdomen+pelvis with contrast"),
    ("74177", "0558T", True, "Included procedure; modifier if distinct"),
    ("74177", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("74177", "36005", True, "IV injection; modifier if distinct"),
    ("74177", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("74177", "36410", True, "Venipuncture; modifier if distinct"),
    ("74177", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74177", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74177", "72193", True, "CT pelvis with contrast component; modifier if distinct"),
    ("74178", "01922", False, "Anesthesia bundled with CT abdomen+pelvis w/o then with"),
    ("74178", "0558T", True, "Included procedure; modifier if distinct"),
    ("74178", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("74178", "36005", True, "IV injection; modifier if distinct"),
    ("74178", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("74178", "36410", True, "Venipuncture; modifier if distinct"),
    ("74178", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74178", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74178", "72192", True, "CT pelvis w/o component; modifier if distinct"),
    ("74178", "72193", True, "CT pelvis with contrast component; modifier if distinct"),

    # --- CT: cardiac ---
    ("75571", "01922", False, "Anesthesia bundled with cardiac CT for calcium scoring"),
    ("75571", "0558T", True, "Included procedure; modifier if distinct"),
    ("75571", "0694T", True, "Included procedure; modifier if distinct"),
    ("75571", "0903T", True, "Included procedure; modifier if distinct"),
    ("75571", "0904T", True, "Included procedure; modifier if distinct"),
    ("75571", "0905T", True, "Included procedure; modifier if distinct"),
    ("75571", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("75571", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("75571", "76000", True, "Fluoroscopy; modifier if distinct"),
    ("75571", "76001", True, "Extended fluoroscopy; modifier if distinct"),

    # --- MRI: head / neck ---
    ("70336", "01922", False, "Anesthesia bundled with MRI temporomandibular joint"),
    ("70336", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70336", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70336", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70540", "01922", False, "Anesthesia bundled with MRI orbit/face/neck w/o"),
    ("70540", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70540", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70540", "61715", True, "Intracranial procedure; modifier if distinct"),
    ("70540", "70547", True, "MRA neck included; modifier if distinct"),
    ("70540", "70548", True, "MRA neck with contrast included; modifier if distinct"),
    ("70540", "76016", True, "Mammographic guidance; modifier if distinct"),
    ("70540", "76017", True, "Included procedure; modifier if distinct"),
    ("70540", "76018", True, "Included procedure; modifier if distinct"),
    ("70540", "76019", True, "Included procedure; modifier if distinct"),
    ("70543", "01922", False, "Anesthesia bundled with MRI orbit/face/neck w/o then with"),
    ("70543", "0708T", True, "Included procedure; modifier if distinct"),
    ("70543", "0709T", True, "Included procedure; modifier if distinct"),
    ("70543", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("70543", "36005", True, "IV injection; modifier if distinct"),
    ("70543", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("70543", "36406", True, "Venipuncture; modifier if distinct"),
    ("70543", "36410", True, "Venipuncture; modifier if distinct"),
    ("70543", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70543", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70544", "01916", False, "Anesthesia bundled with MRA head w/o contrast"),
    ("70544", "01922", False, "Anesthesia bundled with MRA head w/o contrast"),
    ("70544", "01924", False, "Anesthesia bundled with MRA head"),
    ("70544", "01925", False, "Anesthesia bundled with MRA head"),
    ("70544", "01926", False, "Anesthesia bundled with MRA head"),
    ("70544", "0694T", True, "Included procedure; modifier if distinct"),
    ("70544", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70544", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70544", "61715", True, "Intracranial procedure; modifier if distinct"),
    ("70544", "76350", False, "Guidance bundled with MRA head"),
    ("70551", "01922", False, "Anesthesia bundled with MRI brain w/o"),
    ("70551", "0865T", False, "Deep brain stimulation mapping bundled with MRI brain"),
    ("70551", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70551", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("70551", "61715", True, "Intracranial procedure; modifier if distinct"),
    ("70551", "70544", True, "MRA head w/o included with MRI brain; modifier if distinct"),
    ("70551", "70545", True, "MRA head with contrast included; modifier if distinct"),
    ("70551", "70555", True, "Functional MRI included; modifier if distinct"),
    ("70551", "70557", True, "MRI brain w/o intraoperative; modifier if distinct"),
    ("70551", "76350", False, "Guidance bundled with MRI brain w/o"),
    ("70552", "01922", False, "Anesthesia bundled with MRI brain with contrast"),
    ("70552", "0708T", True, "Included procedure; modifier if distinct"),
    ("70552", "0709T", True, "Included procedure; modifier if distinct"),
    ("70552", "0865T", False, "Deep brain stimulation mapping bundled with MRI brain"),
    ("70552", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("70552", "36005", True, "IV injection; modifier if distinct"),
    ("70552", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("70552", "36406", True, "Venipuncture; modifier if distinct"),
    ("70552", "36410", True, "Venipuncture; modifier if distinct"),
    ("70552", "36591", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- MRI: chest ---
    ("71550", "01922", False, "Anesthesia bundled with MRI chest w/o"),
    ("71550", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71550", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("71550", "76350", False, "Guidance bundled with MRI chest"),
    ("71550", "96523", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- MRI: spine ---
    ("72141", "01922", False, "Anesthesia bundled with MRI cervical spine w/o"),
    ("72141", "0609T", False, "Intraoperative stimulation monitoring bundled with MRI cervical"),
    ("72141", "0610T", False, "Intraoperative stimulation monitoring bundled with MRI cervical"),
    ("72141", "0611T", False, "Intraoperative stimulation monitoring bundled with MRI cervical"),
    ("72141", "0612T", False, "Intraoperative stimulation monitoring bundled with MRI cervical"),
    ("72141", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72141", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72141", "76350", False, "Guidance bundled with MRI cervical spine"),
    ("72141", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72148", "01922", False, "Anesthesia bundled with MRI lumbar spine w/o"),
    ("72148", "0609T", False, "Intraoperative stimulation monitoring bundled with MRI lumbar"),
    ("72148", "0610T", False, "Intraoperative stimulation monitoring bundled with MRI lumbar"),
    ("72148", "0611T", False, "Intraoperative stimulation monitoring bundled with MRI lumbar"),
    ("72148", "0612T", False, "Intraoperative stimulation monitoring bundled with MRI lumbar"),
    ("72148", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72148", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72148", "76350", False, "Guidance bundled with MRI lumbar spine"),
    ("72148", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72156", "01922", False, "Anesthesia bundled with MRI cervical spine w/o then with"),
    ("72156", "0609T", False, "Intraoperative stimulation monitoring bundled with MRI cervical"),
    ("72156", "0610T", False, "Intraoperative stimulation monitoring bundled with MRI cervical"),
    ("72156", "0611T", False, "Intraoperative stimulation monitoring bundled with MRI cervical"),
    ("72156", "0612T", False, "Intraoperative stimulation monitoring bundled with MRI cervical"),
    ("72156", "0708T", True, "Included procedure; modifier if distinct"),
    ("72156", "0709T", True, "Included procedure; modifier if distinct"),
    ("72156", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("72156", "36005", True, "IV injection; modifier if distinct"),
    ("72156", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("72157", "01922", False, "Anesthesia bundled with MRI thoracic spine w/o then with"),
    ("72157", "0609T", False, "Intraoperative stimulation monitoring bundled with MRI thoracic"),
    ("72157", "0610T", False, "Intraoperative stimulation monitoring bundled with MRI thoracic"),
    ("72157", "0611T", False, "Intraoperative stimulation monitoring bundled with MRI thoracic"),
    ("72157", "0612T", False, "Intraoperative stimulation monitoring bundled with MRI thoracic"),
    ("72157", "0708T", True, "Included procedure; modifier if distinct"),
    ("72157", "0709T", True, "Included procedure; modifier if distinct"),
    ("72157", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("72157", "36005", True, "IV injection; modifier if distinct"),
    ("72157", "36011", True, "Selective catheter placement; modifier if distinct"),

    # --- MRI: pelvis ---
    ("72195", "01922", False, "Anesthesia bundled with MRI pelvis w/o"),
    ("72195", "0582T", True, "Included procedure; modifier if distinct"),
    ("72195", "0655T", True, "Included procedure; modifier if distinct"),
    ("72195", "0714T", True, "Included procedure; modifier if distinct"),
    ("72195", "0867T", True, "Included procedure; modifier if distinct"),
    ("72195", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72195", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("72195", "51721", False, "Urodynamics procedure bundled with MRI pelvis"),
    ("72195", "55881", False, "Included procedure bundled with MRI pelvis"),
    ("72195", "55882", False, "Included procedure bundled with MRI pelvis"),
    ("72197", "01922", False, "Anesthesia bundled with MRI pelvis w/o then with"),
    ("72197", "0582T", True, "Included procedure; modifier if distinct"),
    ("72197", "0655T", True, "Included procedure; modifier if distinct"),
    ("72197", "0708T", True, "Included procedure; modifier if distinct"),
    ("72197", "0709T", True, "Included procedure; modifier if distinct"),
    ("72197", "0714T", True, "Included procedure; modifier if distinct"),
    ("72197", "0867T", True, "Included procedure; modifier if distinct"),
    ("72197", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("72197", "36005", True, "IV injection; modifier if distinct"),
    ("72197", "36011", True, "Selective catheter placement; modifier if distinct"),

    # --- MRI: upper extremity ---
    ("73218", "0594T", True, "Included procedure; modifier if distinct"),
    ("73218", "0648T", True, "Included procedure; modifier if distinct"),
    ("73218", "01922", False, "Anesthesia bundled with MRI upper extremity w/o"),
    ("73218", "20696", True, "External fixation system adjustment; modifier if distinct"),
    ("73218", "20697", True, "External fixation system adjustment; modifier if distinct"),
    ("73218", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73218", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73218", "73219", True, "MRI upper extremity with contrast included; modifier if distinct"),
    ("73218", "76350", False, "Guidance bundled with MRI upper extremity"),
    ("73218", "96523", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73220", "01922", False, "Anesthesia bundled with MRI upper extremity w/o then with"),
    ("73220", "0708T", True, "Included procedure; modifier if distinct"),
    ("73220", "0709T", True, "Included procedure; modifier if distinct"),
    ("73220", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("73220", "36005", True, "IV injection; modifier if distinct"),
    ("73220", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("73220", "36406", True, "Venipuncture; modifier if distinct"),
    ("73220", "36410", True, "Venipuncture; modifier if distinct"),
    ("73220", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73220", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73222", "01922", False, "Anesthesia bundled with MRI upper extremity joint w/o"),
    ("73222", "0708T", True, "Included procedure; modifier if distinct"),
    ("73222", "0709T", True, "Included procedure; modifier if distinct"),
    ("73222", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("73222", "36005", True, "IV injection; modifier if distinct"),
    ("73222", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("73222", "36406", True, "Venipuncture; modifier if distinct"),
    ("73222", "36410", True, "Venipuncture; modifier if distinct"),
    ("73222", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73222", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73223", "01922", False, "Anesthesia bundled with MRI upper extremity joint w/o then with"),
    ("73223", "0708T", True, "Included procedure; modifier if distinct"),
    ("73223", "0709T", True, "Included procedure; modifier if distinct"),
    ("73223", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("73223", "36005", True, "IV injection; modifier if distinct"),
    ("73223", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("73223", "36406", True, "Venipuncture; modifier if distinct"),
    ("73223", "36410", True, "Venipuncture; modifier if distinct"),
    ("73223", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73223", "36592", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- MRI: lower extremity ---
    ("73701", "01922", False, "Anesthesia bundled with MRI lower extremity w/o"),
    ("73701", "0708T", True, "Included procedure; modifier if distinct"),
    ("73701", "0709T", True, "Included procedure; modifier if distinct"),
    ("73701", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("73701", "36005", True, "IV injection; modifier if distinct"),
    ("73701", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("73701", "36406", True, "Venipuncture; modifier if distinct"),
    ("73701", "36410", True, "Venipuncture; modifier if distinct"),
    ("73701", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73701", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73723", "01922", False, "Anesthesia bundled with MRI lower extremity joint w/o then with"),
    ("73723", "0708T", True, "Included procedure; modifier if distinct"),
    ("73723", "0709T", True, "Included procedure; modifier if distinct"),
    ("73723", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("73723", "36005", True, "IV injection; modifier if distinct"),
    ("73723", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("73723", "36406", True, "Venipuncture; modifier if distinct"),
    ("73723", "36410", True, "Venipuncture; modifier if distinct"),
    ("73723", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("73723", "36592", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- MRI: abdomen ---
    ("74181", "01922", False, "Anesthesia bundled with MRI abdomen w/o"),
    ("74181", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("74181", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("74181", "36410", True, "Venipuncture; modifier if distinct"),
    ("74181", "36425", True, "Venipuncture; modifier if distinct"),
    ("74181", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74181", "36592", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74181", "76350", False, "Guidance bundled with MRI abdomen"),
    ("74181", "90782", True, "Therapeutic injection; modifier if distinct"),
    ("74181", "90783", True, "Therapeutic injection; modifier if distinct"),
    ("74183", "01922", False, "Anesthesia bundled with MRI abdomen w/o then with"),
    ("74183", "0708T", True, "Included procedure; modifier if distinct"),
    ("74183", "0709T", True, "Included procedure; modifier if distinct"),
    ("74183", "36000", True, "Peripheral IV placement; modifier if distinct"),
    ("74183", "36005", True, "IV injection; modifier if distinct"),
    ("74183", "36011", True, "Selective catheter placement; modifier if distinct"),
    ("74183", "36406", True, "Venipuncture; modifier if distinct"),
    ("74183", "36410", True, "Venipuncture; modifier if distinct"),
    ("74183", "36591", False, "Bundled catheter service — always denied same-day as imaging"),
    ("74183", "36592", False, "Bundled catheter service — always denied same-day as imaging"),

    # --- MRA: abdomen+pelvis ---
    ("74185", "01916", False, "Anesthesia bundled with MRA abdomen"),
    ("74185", "01922", False, "Anesthesia bundled with MRA abdomen"),
    ("74185", "01924", False, "Anesthesia bundled with MRA abdomen"),
    ("74185", "01925", False, "Anesthesia bundled with MRA abdomen"),
    ("74185", "01926", False, "Anesthesia bundled with MRA abdomen"),
    ("74185", "0694T", False, "Included procedure bundled with MRA abdomen"),
    ("74185", "0708T", True, "Included procedure; modifier if distinct"),
    ("74185", "0709T", True, "Included procedure; modifier if distinct"),
    ("74185", "36000", True, "Peripheral IV placement; modifier if distinct"),
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
    ("J7298", 1, "One IUD device per insertion"),
    ("58300", 1, "IUD insertion, one per day"),
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
     False, "", ["R05", "R07", "J18", "R91", "J90", "J98"]),
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

    # ===========================================================================
    # STATE-SPECIFIC LCD / NCD RADIOLOGY POLICIES
    # MAC jurisdiction map:
    #   Noridian-CA  → Noridian Healthcare Solutions, JE — California, Hawaii, Nevada
    #   Novitas-TX   → Novitas Solutions, JH — Texas, AR, CO, LA, MS, NM, OK
    #   NGS-NY       → NGS / Wellpoint Federal, JK — New York, CT, MA, ME, NH, RI, VT
    #   FirstCoast-FL → First Coast Service Options, JN — Florida, PR, USVI
    #   Noridian-NV  → Noridian Healthcare Solutions, JE — Nevada (same MAC as CA)
    #   Noridian-WA  → Noridian Healthcare Solutions, JF — Washington, OR, AK, ID, MT, ND, SD, UT, WY
    #
    # All entries below are Traditional Medicare (FFS); requires_auth=False for all
    # because prior auth applies only to Medicare Advantage (Part C) plans.
    # ICD-10 code lists sourced from CMS Billing & Coding Articles (companion to LCDs).
    # LCD IDs verified against CMS Medicare Coverage Database (cms.gov/medicare-coverage-database).
    # ===========================================================================

    # ---------------------------------------------------------------------------
    # CALIFORNIA — Noridian Healthcare Solutions (JE)
    # ---------------------------------------------------------------------------

    # LCD L34220 — MRI Lumbar Spine (multi-MAC; Noridian JE active)
    # Billing & Coding Article A57206; conservative-therapy prerequisite (4–6 wks)
    # unless red-flag: cauda equina, suspected malignancy, fracture, or new neurologic deficit.
    ("Noridian-CA", "72148",
     "LCD L34220: MRI lumbar spine (Noridian JE, California). Covered for radiculopathy, "
     "disc herniation, spinal stenosis, or spondylosis with neurologic deficit after 4-6 weeks "
     "of conservative therapy or immediately with red-flag findings (cauda equina, malignancy, "
     "fracture). Documentation must include duration of symptoms, conservative-therapy history, "
     "and neurological exam. (Billing & Coding Article A57206)",
     False, "", ["M54.16", "M54.40", "M54.41", "M54.42", "M54.3", "M51.16", "M51.17",
                 "M51.26", "M51.36", "M48.06", "M47.816", "M96.1", "G54.4", "M54.50"]),

    # LCD L37373 — MRI and CT Scans of the Head and Neck (Noridian JE active; replaces L35175 for CA)
    # Billing & Coding Article A57204 R16, effective 2026-01-01
    ("Noridian-CA", "70551",
     "LCD L37373: MRI brain without contrast (Noridian JE, California — active LCD, supersedes L35175). "
     "Covered for new neurologic deficit, suspected demyelinating disease (MS), seizure evaluation, "
     "TIA/stroke work-up, suspected intracranial neoplasm, or persistent headache with red-flag features. "
     "Headache alone (R51) without red flags is generally insufficient. (Billing & Coding Article A57204 R16)",
     False, "", ["G35", "G43.909", "G45.9", "I63.9", "I61.9", "R55", "G40.909", "C71.9",
                 "G44.1", "G91.9", "R51.9"]),

    ("Noridian-CA", "70450",
     "LCD L37373: CT head without contrast (Noridian JE, California). Covered for acute neurologic "
     "symptoms including headache red flags, syncope, seizure, suspected stroke/hemorrhage, or head "
     "trauma. Must document clinical indication and support CT over alternative imaging. "
     "(Billing & Coding Article A57204 R16)",
     False, "", ["R51.9", "R55", "R56.9", "G45.9", "I63.9", "I61.9", "S09.90XA", "G40.909"]),

    ("Noridian-CA", "72141",
     "LCD L37373: MRI cervical spine without contrast (Noridian JE, California). Covered for "
     "cervical radiculopathy, myelopathy, or neck pain with neurologic deficit persisting after "
     "conservative care. Cervicalgia alone (M54.2) is typically insufficient without radiculopathy "
     "or neurologic findings. (Billing & Coding Article A57204 R16)",
     False, "", ["M54.12", "M50.12", "M50.32", "M48.02", "M47.812", "G54.2", "M54.2"]),

    # LCD L34415 — CT Abdomen and Pelvis (multi-MAC; Noridian JE active)
    # Billing & Coding Article A56421; AUC/CDSM documentation required under PAMA
    ("Noridian-CA", "74177",
     "LCD L34415: CT abdomen and pelvis with contrast (Noridian JE, California). Covered for "
     "abdominal pain, suspected appendicitis, renal/ureteral calculus, intra-abdominal mass, "
     "unexplained weight loss, or staging of known malignancy. PAMA/AUC: ordering physician must "
     "document consultation of a qualified Clinical Decision Support Mechanism (CDSM). "
     "(Billing & Coding Article A56421)",
     False, "", ["R10.11", "R10.31", "R10.9", "K35.80", "N20.0", "N20.1", "R19.00",
                 "R63.4", "C18.9", "K57.30", "K80.20"]),

    # LCD L34577 — Retroperitoneal/Abdominal Ultrasound (multi-MAC; Noridian JE active)
    # Billing & Coding Article A55336
    ("Noridian-CA", "76700",
     "LCD L34577: Complete abdominal ultrasound (Noridian JE, California). Covered when all major "
     "abdominal organs are examined (liver, gallbladder, CBD, pancreas, spleen, kidneys, aorta, IVC). "
     "Supported indications include abdominal pain, organomegaly, palpable mass, ascites, suspected AAA, "
     "or known hepatic/renal pathology. Do NOT bill 76700 and 76770 together unless separate exams on "
     "distinct anatomic regions are documented. (Billing & Coding Article A55336)",
     False, "", ["R10.11", "R10.9", "K80.20", "K85.90", "K74.60", "R16.0", "R16.2",
                 "N20.0", "I71.4", "C22.0", "R93.2"]),

    # NCD 220.4 + LCD L33950 — Screening/Diagnostic Mammography (Noridian JE)
    # Billing & Coding Article A56448; facility must be MQSA-certified
    ("Noridian-CA", "77067",
     "NCD 220.4 / LCD L33950: Screening mammography (Noridian JE, California). Covered annually "
     "for women aged 40+; one baseline allowed ages 35–39. Z12.31 is required primary ICD-10 for "
     "asymptomatic screening. Women with BRCA mutation or strong family history may qualify for "
     "supplemental breast MRI. Facility must be FDA/MQSA-certified. At least 11 full months must "
     "elapse between covered screening exams. (Billing & Coding Article A56448)",
     False, "", ["Z12.31", "Z15.01", "Z80.3", "Z85.3"]),

    ("Noridian-CA", "77066",
     "LCD L33950: Diagnostic mammography (Noridian JE, California). Covered for a breast lump, "
     "nipple discharge, skin changes, abnormal screening finding, or personal/family history requiring "
     "diagnostic follow-up. Switch from screening (77067) to diagnostic (77065/77066) when patient "
     "is symptomatic. (Billing & Coding Article A56448)",
     False, "", ["N63.9", "N64.4", "N64.51", "R92.8", "Z85.3", "Z80.3"]),

    # LCD L35753 / L35397 — Non-Invasive Cerebrovascular Arterial Studies (carotid duplex)
    ("Noridian-CA", "93880",
     "LCD L35753: Carotid duplex scan, complete bilateral (Noridian JE, California). Covered for "
     "TIA, recent stroke, amaurosis fugax, documented cervical bruit, or known/suspected carotid "
     "stenosis. Headache alone (R51) or neck pain alone (M54.2) results in denial. Study must include "
     "duplex scanning: color Doppler, spectral Doppler with waveform analysis, and peak systolic "
     "velocity documentation. Annual studies allowed for known 20-49% stenosis. "
     "(Billing & Coding Article A52992)",
     False, "", ["I65.21", "I65.22", "I65.29", "G45.9", "G45.3", "R09.89", "I63.9", "R55"]),

    # ---------------------------------------------------------------------------
    # TEXAS — Novitas Solutions (JH)
    # ---------------------------------------------------------------------------

    # LCD L34220 — MRI Lumbar Spine (Novitas JH)
    ("Novitas-TX", "72148",
     "LCD L34220: MRI lumbar spine (Novitas JH, Texas). Covered for lumbar radiculopathy, disc "
     "herniation with sciatica, spinal stenosis, or post-laminectomy syndrome with recurrent "
     "symptoms. Conservative therapy (physiotherapy, NSAIDs) for 4–6 weeks required before MRI "
     "unless red-flag conditions present. Document specific clinical question MRI is expected to "
     "answer. (Billing & Coding Article A57206)",
     False, "", ["M54.16", "M54.40", "M54.41", "M54.42", "M54.3", "M51.16", "M51.17",
                 "M51.26", "M51.36", "M48.06", "M47.816", "M96.1", "G54.4", "M54.50"]),

    # LCD L35397 — Non-Invasive Cerebrovascular Arterial Studies (Novitas JH — TX-specific LCD)
    # Billing & Coding Articles A52992, A57592, A57670
    # This is the TX-jurisdiction-specific LCD for carotid duplex
    ("Novitas-TX", "93880",
     "LCD L35397: Carotid duplex, complete bilateral (Novitas JH, Texas — TX-specific LCD). "
     "Covered for TIA, ischemic stroke, amaurosis fugax, cervical bruit on exam, known carotid "
     "stenosis follow-up (annual for 20-49%; per symptoms for ≥50%), and pre/post-carotid "
     "endarterectomy surveillance. Asymptomatic screening without vascular risk factors is denied. "
     "Duplex study must document real-time B-mode imaging plus pulsed Doppler waveform analysis. "
     "(Billing & Coding Articles A52992, A57592)",
     False, "", ["I65.21", "I65.22", "I65.29", "G45.3", "G45.9", "R09.89", "I63.031",
                 "I63.9", "R55", "R22.1"]),

    # LCD L35175 — MRI and CT Head and Neck (Novitas JH)
    ("Novitas-TX", "70551",
     "LCD L35175: MRI brain without contrast (Novitas JH, Texas). Covered for suspected "
     "demyelinating disease (MS), new focal neurologic deficit, seizure, TIA/stroke work-up, "
     "suspected intracranial mass, or headache with red-flag features (sudden onset, worst ever, "
     "progressive, or associated neurologic signs). (Billing & Coding Article A57215)",
     False, "", ["G35", "G43.909", "G45.9", "I63.9", "I61.9", "R55", "G40.909", "C71.9",
                 "G44.1", "G91.9", "R51.9"]),

    ("Novitas-TX", "70450",
     "LCD L35175: CT head without contrast (Novitas JH, Texas). Covered for acute head trauma, "
     "sudden severe headache, first seizure, syncope with suspected neurologic cause, suspected "
     "intracranial hemorrhage, or acute stroke symptoms. (Billing & Coding Article A57215)",
     False, "", ["R51.9", "R55", "R56.9", "G45.9", "I63.9", "I61.9", "G40.909", "S09.90XA"]),

    ("Novitas-TX", "72141",
     "LCD L35175: MRI cervical spine without contrast (Novitas JH, Texas). Covered for cervical "
     "radiculopathy or myelopathy, neck pain with upper-extremity neurologic deficit, or cervical "
     "disc disease with persistent symptoms after conservative care. (Billing & Coding Article A57215)",
     False, "", ["M54.12", "M50.12", "M50.32", "M48.02", "M47.812", "G54.2"]),

    # LCD L34415 — CT Abdomen and Pelvis (Novitas JH)
    ("Novitas-TX", "74177",
     "LCD L34415: CT abdomen and pelvis with contrast (Novitas JH, Texas). Covered for acute "
     "abdominal pain, suspected appendicitis, renal colic, intra-abdominal mass, GI hemorrhage, "
     "diverticulitis, or malignancy staging. PAMA AUC/CDSM documentation required for outpatient "
     "advanced imaging orders. (Billing & Coding Article A56421)",
     False, "", ["R10.11", "R10.31", "R10.9", "K35.80", "N20.0", "N20.1", "R19.00",
                 "K57.30", "K92.1", "C18.9", "R63.4"]),

    # LCD L33459 — CT Thorax / CTA Chest PE Protocol (Novitas JH)
    # Billing & Coding Article A56580
    ("Novitas-TX", "71275",
     "LCD L33459: CTA chest, PE protocol (Novitas JH, Texas). Covered for suspected pulmonary "
     "embolism with documented clinical pre-test probability. IV contrast is mandatory; do NOT "
     "separately bill 76376/76377 for 3D reconstruction as it is included in 71275. "
     "Document Wells Score or equivalent pre-test probability assessment. "
     "(Billing & Coding Article A56580)",
     False, "", ["I26.99", "I26.09", "I26.90", "R07.1", "R09.1", "Z87.891"]),

    ("Novitas-TX", "71250",
     "LCD L33459: CT thorax without contrast (Novitas JH, Texas). Covered for indeterminate "
     "pulmonary nodule follow-up (Lung-RADS), abnormal chest radiograph, suspected thoracic "
     "pathology, evaluation of mediastinal mass, or interstitial lung disease. "
     "(Billing & Coding Article A56580)",
     False, "", ["R91.1", "R91.8", "J98.11", "J84.9", "J93.9", "C34.90", "D14.31", "J18.9"]),

    # LCD L33627 — Non-Invasive Vascular Studies / Peripheral Venous (Novitas JH)
    # Billing & Coding Articles A52993, A56758
    ("Novitas-TX", "93970",
     "LCD L33627: Extremity venous duplex, complete bilateral (Novitas JH, Texas). Covered for "
     "clinically suspected DVT (edema, tenderness, erythema), work-up for suspected pulmonary "
     "embolism source, chronic venous insufficiency, or vein mapping for CABG/dialysis access. "
     "Clinical signs and symptoms must be documented; study must include compression maneuvers, "
     "color Doppler, and spectral analysis. Cannot bill 93970/93971 with 93922–93931 on same day "
     "for same extremity. (Billing & Coding Articles A52993, A56758)",
     False, "", ["I82.401", "I82.402", "I82.4Z1", "I82.413", "I87.2", "I80.3", "I26.99",
                 "Z01.810", "Z01.818"]),

    # ---------------------------------------------------------------------------
    # NEW YORK — NGS / Wellpoint Federal (JK)
    # ---------------------------------------------------------------------------

    # LCD L34220 — MRI Lumbar Spine (NGS JK)
    ("NGS-NY", "72148",
     "LCD L34220: MRI lumbar spine (NGS/Wellpoint Federal JK, New York). Covered for radiculopathy, "
     "disc herniation, spinal stenosis, spondylosis with neurologic deficit, or post-laminectomy "
     "syndrome. Conservative therapy for 4–6 weeks generally required before MRI absent red-flag "
     "findings. Documentation must include clinical signs, duration, and prior treatment response. "
     "(Billing & Coding Article A57206)",
     False, "", ["M54.16", "M54.40", "M54.41", "M54.42", "M51.16", "M51.17", "M51.26",
                 "M51.36", "M48.06", "M47.816", "M96.1", "G54.4", "M54.50"]),

    # LCD L35175 — MRI and CT Head and Neck (NGS JK)
    ("NGS-NY", "70551",
     "LCD L35175: MRI brain without contrast (NGS/Wellpoint Federal JK, New York). Covered for "
     "suspected MS or demyelinating disease, seizure evaluation, TIA/stroke work-up, new neurologic "
     "deficit, suspected intracranial mass, or persistent headache with red-flag features. "
     "(Billing & Coding Article A57215)",
     False, "", ["G35", "G43.909", "G45.9", "I63.9", "I61.9", "R55", "G40.909", "C71.9",
                 "G44.1", "G91.9"]),

    ("NGS-NY", "70450",
     "LCD L35175: CT head without contrast (NGS/Wellpoint Federal JK, New York). Covered for "
     "acute head trauma, sudden severe headache, first seizure, syncope, suspected stroke or "
     "intracranial hemorrhage. (Billing & Coding Article A57215)",
     False, "", ["R51.9", "R55", "R56.9", "G45.9", "I63.9", "I61.9", "G40.909"]),

    ("NGS-NY", "72141",
     "LCD L35175: MRI cervical spine without contrast (NGS/Wellpoint Federal JK, New York). "
     "Covered for cervical radiculopathy, myelopathy, or neck pain with neurologic deficit after "
     "conservative treatment. (Billing & Coding Article A57215)",
     False, "", ["M54.12", "M50.12", "M50.32", "M48.02", "M47.812", "G54.2"]),

    # LCD L33459 — CTA Chest PE Protocol (NGS JK)
    ("NGS-NY", "71275",
     "LCD L33459: CTA chest, PE protocol (NGS/Wellpoint Federal JK, New York). Covered for "
     "documented clinical suspicion of pulmonary embolism. IV contrast required; 3D reconstruction "
     "is bundled — do not bill 76376/76377 separately. Document pre-test probability (Wells Score "
     "or equivalent). (Billing & Coding Article A56580)",
     False, "", ["I26.99", "I26.09", "I26.90", "R07.1", "R09.1", "Z87.891"]),

    ("NGS-NY", "71250",
     "LCD L33459: CT thorax without contrast (NGS/Wellpoint Federal JK, New York). Covered for "
     "indeterminate pulmonary nodule, abnormal chest radiograph requiring further evaluation, "
     "suspected interstitial lung disease, mediastinal mass, or pleural pathology. "
     "(Billing & Coding Article A56580)",
     False, "", ["R91.1", "R91.8", "J98.11", "J84.9", "J93.9", "C34.90", "J90", "J18.9"]),

    # LCD L37636 — Nonobstetric Pelvic Ultrasound (NGS JK)
    # Billing & Coding Article A56671
    ("NGS-NY", "76856",
     "LCD L37636: Pelvic ultrasound, complete non-obstetric (NGS/Wellpoint Federal JK, New York). "
     "Covered for pelvic pain, evaluation of uterine fibroids, ovarian cysts or mass, endometriosis, "
     "abnormal uterine bleeding, postmenopausal bleeding, infertility evaluation, or lower urinary "
     "tract symptoms. Post-void residual volume measurement (51798) must NOT be billed under "
     "76856/76857. (Billing & Coding Article A56671)",
     False, "", ["D25.9", "E28.2", "N80.9", "N84.0", "N85.00", "N91.0", "N91.1", "N92.0",
                 "N93.9", "N94.4", "N95.0", "N97.9", "R10.32", "R19.09"]),

    # LCD L33627 — Extremity Venous Duplex / DVT (NGS JK)
    ("NGS-NY", "93970",
     "LCD L33627: Extremity venous duplex, complete bilateral (NGS/Wellpoint Federal JK, New York). "
     "Covered for suspected DVT with clinical signs (edema, tenderness, erythema, warmth), "
     "suspected PE source evaluation, chronic venous insufficiency, or preoperative vein mapping. "
     "(Billing & Coding Articles A52993, A56758)",
     False, "", ["I82.401", "I82.402", "I82.4Z1", "I87.2", "I80.3", "I26.99",
                 "Z01.810", "Z01.818"]),

    # LCD L34577 — Abdominal Ultrasound (NGS JK)
    ("NGS-NY", "76700",
     "LCD L34577: Complete abdominal ultrasound (NGS/Wellpoint Federal JK, New York). Covered for "
     "abdominal pain, hepatomegaly, splenomegaly, suspected AAA, cholelithiasis follow-up, or "
     "known hepatic/pancreatic/renal pathology requiring surveillance. All major abdominal organs "
     "must be evaluated and documented to bill 76700 rather than limited 76705. "
     "(Billing & Coding Article A55336)",
     False, "", ["R10.9", "R10.11", "K80.20", "K85.90", "K74.60", "R16.0", "R16.2",
                 "I71.4", "N20.0", "R93.2"]),

    # LCD L35753 — Non-Invasive Cerebrovascular Arterial Studies (NGS JK)
    ("NGS-NY", "93880",
     "LCD L35753: Carotid duplex, complete bilateral (NGS/Wellpoint Federal JK, New York). "
     "Covered for TIA, ischemic stroke, amaurosis fugax, or documented cervical bruit. Annual "
     "surveillance permitted for known stenosis 20–49%. Post-endarterectomy: 6-week, 6-month, "
     "and 1-year ipsilateral follow-up studies are covered. Study must document duplex scanning "
     "with color Doppler and spectral Doppler waveform analysis. "
     "(Billing & Coding Article A52992)",
     False, "", ["I65.21", "I65.22", "I65.29", "G45.9", "G45.3", "R09.89", "I63.9", "R55"]),

    # ---------------------------------------------------------------------------
    # FLORIDA — First Coast Service Options (JN)
    # ---------------------------------------------------------------------------

    # LCD L34220 — MRI Lumbar Spine (First Coast JN)
    ("FirstCoast-FL", "72148",
     "LCD L34220: MRI lumbar spine (First Coast Service Options JN, Florida). Covered for lumbar "
     "radiculopathy, disc herniation with sciatica, spinal stenosis, degenerative disc disease with "
     "neurologic deficit, spondylosis with radiculopathy, or post-laminectomy syndrome. Conservative "
     "therapy prerequisite (4–6 weeks) unless red flags present. (Billing & Coding Article A57206)",
     False, "", ["M54.16", "M54.40", "M54.41", "M54.42", "M54.3", "M51.16", "M51.17",
                 "M51.26", "M51.36", "M48.06", "M47.816", "M96.1", "G54.4", "M54.50"]),

    # LCD L35175 — MRI and CT Head and Neck (First Coast JN)
    ("FirstCoast-FL", "70551",
     "LCD L35175: MRI brain without contrast (First Coast JN, Florida). Covered for suspected "
     "demyelinating disease, new focal neurologic deficit, seizure evaluation, TIA/stroke work-up, "
     "suspected intracranial neoplasm, hydrocephalus, or persistent headache with documented red-flag "
     "features. Routine headache without red flags is denied. (Billing & Coding Article A57215)",
     False, "", ["G35", "G43.909", "G45.9", "I63.9", "I61.9", "R55", "G40.909", "C71.9",
                 "G44.1", "G91.9"]),

    ("FirstCoast-FL", "70450",
     "LCD L35175: CT head without contrast (First Coast JN, Florida). Covered for head trauma, "
     "sudden severe headache (thunderclap), first seizure, syncope with suspected neurologic etiology, "
     "or acute stroke/hemorrhage evaluation. (Billing & Coding Article A57215)",
     False, "", ["R51.9", "R55", "R56.9", "G45.9", "I63.9", "I61.9", "G40.909", "S09.90XA"]),

    ("FirstCoast-FL", "72141",
     "LCD L35175: MRI cervical spine without contrast (First Coast JN, Florida). Covered for "
     "cervical radiculopathy or myelopathy, upper-extremity neurologic deficit, or cervical disc "
     "disease with symptoms persisting beyond conservative care. (Billing & Coding Article A57215)",
     False, "", ["M54.12", "M50.12", "M50.32", "M48.02", "M47.812", "G54.2"]),

    # LCD L34415 — CT Abdomen and Pelvis (First Coast JN)
    ("FirstCoast-FL", "74177",
     "LCD L34415: CT abdomen and pelvis with contrast (First Coast JN, Florida). Covered for "
     "acute abdominal pain, suspected appendicitis, renal colic, intra-abdominal mass, diverticulitis, "
     "GI bleeding, or malignancy staging. PAMA AUC/CDSM documentation required. "
     "(Billing & Coding Article A56421)",
     False, "", ["R10.11", "R10.31", "R10.9", "K35.80", "N20.0", "N20.1", "R19.00",
                 "K57.30", "K92.1", "C18.9", "R63.4"]),

    # LCD L37636 — Nonobstetric Pelvic Ultrasound (First Coast JN — FCSO source LCD)
    # Billing & Coding Article A56671; First Coast is primary source for this LCD
    ("FirstCoast-FL", "76856",
     "LCD L37636: Pelvic ultrasound, complete non-obstetric (First Coast JN, Florida). "
     "Covered for uterine fibroids (leiomyoma), PCOS, endometriosis, endometrial polyp or hyperplasia, "
     "abnormal uterine/vaginal bleeding, postmenopausal bleeding, primary/secondary amenorrhea, "
     "excessive menstruation, pelvic pain, infertility, or pelvic mass. Post-void residual (51798) "
     "must NOT be billed under 76856/76857. (Billing & Coding Article A56671)",
     False, "", ["D25.9", "E28.2", "N80.9", "N84.0", "N85.00", "N85.2", "N91.0", "N91.1",
                 "N92.0", "N92.4", "N93.9", "N94.4", "N94.5", "N95.0", "N97.9",
                 "R10.32", "R19.03", "R19.09"]),

    # LCD L34577 — Abdominal Ultrasound (First Coast JN)
    ("FirstCoast-FL", "76700",
     "LCD L34577: Complete abdominal ultrasound (First Coast JN, Florida). Covered for abdominal "
     "pain, hepatomegaly, splenomegaly, cholelithiasis, suspected AAA, pancreatitis evaluation, "
     "cirrhosis monitoring, or renal calculus. All major abdominal organs must be examined to bill "
     "76700; if exam limited to retroperitoneum only, bill 76770. (Billing & Coding Article A55336)",
     False, "", ["R10.9", "R10.11", "K80.20", "K85.90", "K74.60", "K76.0", "R16.0", "R16.2",
                 "N20.0", "I71.4", "C22.0", "R93.2"]),

    # NCD 220.4 + LCD L33950 — Mammography (First Coast JN)
    ("FirstCoast-FL", "77067",
     "NCD 220.4 / LCD L33950: Screening mammography (First Coast JN, Florida). Covered annually "
     "for women aged 40+; one baseline exam at age 35–39. Z12.31 required as primary diagnosis. "
     "At least 11 full months must elapse between covered screenings. Facility must be FDA/MQSA-certified. "
     "Symptomatic patients should be coded to diagnostic mammography (77065/77066), not screening. "
     "(Billing & Coding Article A56448)",
     False, "", ["Z12.31", "Z15.01", "Z80.3", "Z85.3"]),

    ("FirstCoast-FL", "77066",
     "LCD L33950: Diagnostic mammography bilateral (First Coast JN, Florida). Covered for breast "
     "lump, nipple discharge, skin thickening, abnormal screening finding, or personal/family history "
     "requiring diagnostic follow-up. (Billing & Coding Article A56448)",
     False, "", ["N63.9", "N64.4", "N64.51", "R92.8", "Z85.3", "Z80.3"]),

    # LCD L33459 — CTA Chest / CT Thorax (First Coast JN)
    ("FirstCoast-FL", "71275",
     "LCD L33459: CTA chest, PE protocol (First Coast JN, Florida). Covered for documented clinical "
     "suspicion of pulmonary embolism. IV contrast required; 3D reconstruction bundled into 71275 — "
     "do not separately bill 76376/76377. Pre-test probability must be documented. "
     "(Billing & Coding Article A56580)",
     False, "", ["I26.99", "I26.09", "I26.90", "R07.1", "R09.1", "Z87.891"]),

    ("FirstCoast-FL", "71250",
     "LCD L33459: CT thorax without contrast (First Coast JN, Florida). Covered for indeterminate "
     "pulmonary nodule (Lung-RADS follow-up), abnormal chest radiograph, interstitial lung disease, "
     "mediastinal mass, or pleural pathology. (Billing & Coding Article A56580)",
     False, "", ["R91.1", "R91.8", "J98.11", "J84.9", "J93.9", "C34.90", "J90"]),

    # LCD L33627 / L33693 — Extremity Venous Duplex (First Coast JN)
    ("FirstCoast-FL", "93970",
     "LCD L33627: Extremity venous duplex, complete bilateral (First Coast JN, Florida). Covered "
     "for suspected DVT with clinical signs, PE source evaluation, chronic venous insufficiency, or "
     "preoperative vein mapping (CABG, dialysis access). Clinical documentation of signs/symptoms "
     "required; cannot bill 93970/93971 with 93922–93931 same day same extremity. "
     "(Billing & Coding Articles A52993, A56758)",
     False, "", ["I82.401", "I82.402", "I82.4Z1", "I87.2", "I80.3", "I26.99",
                 "Z01.810", "Z01.818"]),

    # LCD L35753 — Carotid Duplex (First Coast JN)
    ("FirstCoast-FL", "93880",
     "LCD L35753: Carotid duplex, complete bilateral (First Coast JN, Florida). Covered for TIA, "
     "ischemic stroke, amaurosis fugax, documented cervical bruit, or known carotid stenosis "
     "surveillance. Annual studies for 20–49% stenosis; post-endarterectomy protocol: 6-week, "
     "6-month, 1-year. Study must document duplex scan components (B-mode, color Doppler, spectral "
     "Doppler with peak systolic velocity). (Billing & Coding Article A52992)",
     False, "", ["I65.21", "I65.22", "I65.29", "G45.9", "G45.3", "R09.89", "I63.9", "R55"]),

    # ---------------------------------------------------------------------------
    # NEVADA — Noridian Healthcare Solutions (JE)
    # Same MAC as California (Noridian JE); same LCD IDs apply.
    # ---------------------------------------------------------------------------

    # LCD L34220 — MRI Lumbar Spine (Noridian JE, Nevada)
    ("Noridian-NV", "72148",
     "LCD L34220: MRI lumbar spine (Noridian JE, Nevada). Covered for radiculopathy, "
     "disc herniation, spinal stenosis, or spondylosis with neurologic deficit after 4-6 weeks "
     "of conservative therapy, or immediately with red-flag findings (cauda equina, suspected "
     "malignancy, fracture, new neurologic deficit). Documentation must include symptom duration, "
     "prior conservative therapy, and clinical indication. (Billing & Coding Article A57206)",
     False, "", ["M54.16", "M54.40", "M54.41", "M54.42", "M54.3", "M51.16", "M51.17",
                 "M51.26", "M51.36", "M48.06", "M47.816", "M96.1", "G54.4", "M54.50"]),

    # LCD L37373 — MRI and CT Scans of the Head and Neck (Noridian JE, Nevada)
    ("Noridian-NV", "70551",
     "LCD L37373: MRI brain without contrast (Noridian JE, Nevada — active LCD, supersedes L35175). "
     "Covered for new neurologic deficit, suspected demyelinating disease (MS), seizure evaluation, "
     "TIA/stroke work-up, suspected intracranial neoplasm, or persistent headache with red-flag features. "
     "Headache alone (R51) without red flags is generally insufficient. (Billing & Coding Article A57204 R16)",
     False, "", ["G35", "G43.909", "G45.9", "I63.9", "I61.9", "R55", "G40.909", "C71.9",
                 "G44.1", "G91.9", "R51.9"]),

    ("Noridian-NV", "70450",
     "LCD L37373: CT head without contrast (Noridian JE, Nevada). Covered for acute neurologic "
     "symptoms including headache red flags, syncope, seizure, suspected stroke/hemorrhage, or head "
     "trauma. Must document clinical indication. (Billing & Coding Article A57204 R16)",
     False, "", ["R51.9", "R55", "R56.9", "G45.9", "I63.9", "I61.9", "S09.90XA", "G40.909"]),

    ("Noridian-NV", "72141",
     "LCD L37373: MRI cervical spine without contrast (Noridian JE, Nevada). Covered for "
     "cervical radiculopathy, myelopathy, or neck pain with neurologic deficit persisting after "
     "conservative care. Cervicalgia alone (M54.2) is typically insufficient without radiculopathy "
     "or neurologic findings. (Billing & Coding Article A57204 R16)",
     False, "", ["M54.12", "M50.12", "M50.32", "M48.02", "M47.812", "G54.2", "M54.2"]),

    # LCD L34415 — CT Abdomen and Pelvis (Noridian JE, Nevada)
    ("Noridian-NV", "74177",
     "LCD L34415: CT abdomen and pelvis with contrast (Noridian JE, Nevada). Covered for "
     "abdominal pain, suspected appendicitis, renal/ureteral calculus, intra-abdominal mass, "
     "unexplained weight loss, or staging of known malignancy. PAMA AUC/CDSM documentation "
     "required for outpatient advanced imaging orders. (Billing & Coding Article A56421)",
     False, "", ["R10.11", "R10.31", "R10.9", "K35.80", "N20.0", "N20.1", "R19.00",
                 "R63.4", "C18.9", "K57.30", "K80.20"]),

    # LCD L34577 — Complete Abdominal Ultrasound (Noridian JE, Nevada)
    ("Noridian-NV", "76700",
     "LCD L34577: Complete abdominal ultrasound (Noridian JE, Nevada). Covered when all major "
     "abdominal organs are examined (liver, gallbladder, CBD, pancreas, spleen, kidneys, aorta, IVC). "
     "Supported indications include abdominal pain, organomegaly, palpable mass, ascites, suspected AAA, "
     "or known hepatic/renal pathology. Do NOT bill 76700 and 76770 together unless separate exams. "
     "(Billing & Coding Article A55336)",
     False, "", ["R10.11", "R10.9", "K80.20", "K85.90", "K74.60", "R16.0", "R16.2",
                 "N20.0", "I71.4", "C22.0", "R93.2"]),

    # NCD 220.4 + LCD L33950 — Screening/Diagnostic Mammography (Noridian JE, Nevada)
    ("Noridian-NV", "77067",
     "NCD 220.4 / LCD L33950: Screening mammography (Noridian JE, Nevada). Covered annually "
     "for women aged 40+; one baseline allowed ages 35–39. Z12.31 is required primary ICD-10. "
     "At least 11 full months must elapse between covered screenings. Facility must be FDA/MQSA-certified. "
     "(Billing & Coding Article A56448)",
     False, "", ["Z12.31", "Z15.01", "Z80.3", "Z85.3"]),

    ("Noridian-NV", "77066",
     "LCD L33950: Diagnostic mammography (Noridian JE, Nevada). Covered for breast lump, "
     "nipple discharge, skin changes, abnormal screening finding, or personal/family history "
     "requiring diagnostic follow-up. (Billing & Coding Article A56448)",
     False, "", ["N63.9", "N64.4", "N64.51", "R92.8", "Z85.3", "Z80.3"]),

    # LCD L37636 — Nonobstetric Pelvic Ultrasound (Noridian JE, Nevada)
    ("Noridian-NV", "76856",
     "LCD L37636: Pelvic ultrasound, complete non-obstetric (Noridian JE, Nevada). Covered for "
     "pelvic pain, uterine fibroids, ovarian cysts or mass, endometriosis, abnormal uterine bleeding, "
     "postmenopausal bleeding, infertility evaluation, or lower urinary tract symptoms. Post-void "
     "residual (51798) must NOT be billed under 76856/76857. (Billing & Coding Article A56671)",
     False, "", ["D25.9", "E28.2", "N80.9", "N84.0", "N85.00", "N91.0", "N91.1", "N92.0",
                 "N93.9", "N94.4", "N95.0", "N97.9", "R10.32", "R19.09"]),

    # LCD L33459 — CTA Chest / CT Thorax (Noridian JE, Nevada)
    ("Noridian-NV", "71275",
     "LCD L33459: CTA chest, PE protocol (Noridian JE, Nevada). Covered for documented clinical "
     "suspicion of pulmonary embolism. IV contrast required; 3D reconstruction bundled into 71275 — "
     "do not separately bill 76376/76377. Document pre-test probability (Wells Score or equivalent). "
     "(Billing & Coding Article A56580)",
     False, "", ["I26.99", "I26.09", "I26.90", "R07.1", "R09.1", "Z87.891"]),

    ("Noridian-NV", "71250",
     "LCD L33459: CT thorax without contrast (Noridian JE, Nevada). Covered for indeterminate "
     "pulmonary nodule follow-up (Lung-RADS), abnormal chest radiograph, suspected interstitial "
     "lung disease, mediastinal mass, or pleural pathology. (Billing & Coding Article A56580)",
     False, "", ["R91.1", "R91.8", "J98.11", "J84.9", "J93.9", "C34.90", "D14.31", "J18.9"]),

    # LCD L35753 — Non-Invasive Cerebrovascular Arterial Studies (Noridian JE, Nevada)
    ("Noridian-NV", "93880",
     "LCD L35753: Carotid duplex scan, complete bilateral (Noridian JE, Nevada). Covered for "
     "TIA, recent stroke, amaurosis fugax, documented cervical bruit, or known/suspected carotid "
     "stenosis. Annual surveillance for 20–49% stenosis; post-endarterectomy: 6-week, 6-month, "
     "1-year follow-up. Study must include duplex scanning with color Doppler and spectral Doppler. "
     "(Billing & Coding Article A52992)",
     False, "", ["I65.21", "I65.22", "I65.29", "G45.3", "G45.9", "R09.89", "I63.031",
                 "I63.9", "R55", "R22.1"]),

    # LCD L33627 — Extremity Venous Duplex / DVT (Noridian JE, Nevada)
    ("Noridian-NV", "93970",
     "LCD L33627: Extremity venous duplex, complete bilateral (Noridian JE, Nevada). Covered for "
     "clinically suspected DVT (edema, tenderness, erythema), work-up for suspected pulmonary "
     "embolism source, chronic venous insufficiency, or vein mapping for CABG/dialysis access. "
     "Clinical signs and symptoms must be documented; include compression maneuvers and waveform "
     "analysis. (Billing & Coding Articles A52993, A56758)",
     False, "", ["I82.401", "I82.402", "I82.4Z1", "I87.2", "I80.3", "I26.99",
                 "Z01.810", "Z01.818"]),

    # ---------------------------------------------------------------------------
    # WASHINGTON — Noridian Healthcare Solutions (JF)
    # MAC Jurisdiction F: Alaska, Arizona, Idaho, Montana, North Dakota, Oregon,
    # South Dakota, Utah, Washington, Wyoming
    # ---------------------------------------------------------------------------

    # LCD L34220 — MRI Lumbar Spine (Noridian JF, Washington)
    ("Noridian-WA", "72148",
     "LCD L34220: MRI lumbar spine (Noridian JF, Washington). Covered for lumbar radiculopathy, "
     "disc herniation with sciatica, spinal stenosis, spondylosis with neurologic deficit, or "
     "post-laminectomy syndrome. Conservative therapy for 4–6 weeks generally required before MRI "
     "absent red-flag conditions (cauda equina, suspected malignancy, fracture, new neurologic deficit). "
     "Document symptom duration, prior treatment, and clinical indication. (Billing & Coding Article A57206)",
     False, "", ["M54.16", "M54.40", "M54.41", "M54.42", "M54.3", "M51.16", "M51.17",
                 "M51.26", "M51.36", "M48.06", "M47.816", "M96.1", "G54.4", "M54.50"]),

    # LCD L37373 — MRI and CT Scans of the Head and Neck (Noridian JF, Washington)
    ("Noridian-WA", "70551",
     "LCD L37373: MRI brain without contrast (Noridian JF, Washington — active LCD). Covered for "
     "new neurologic deficit, suspected demyelinating disease (MS), seizure evaluation, TIA/stroke "
     "work-up, suspected intracranial neoplasm, or persistent headache with red-flag features. "
     "Headache alone (R51) without red flags is generally insufficient. (Billing & Coding Article A57204 R16)",
     False, "", ["G35", "G43.909", "G45.9", "I63.9", "I61.9", "R55", "G40.909", "C71.9",
                 "G44.1", "G91.9", "R51.9"]),

    ("Noridian-WA", "70450",
     "LCD L37373: CT head without contrast (Noridian JF, Washington). Covered for acute neurologic "
     "symptoms including headache red flags, syncope, seizure, suspected stroke/hemorrhage, or head "
     "trauma. Must document clinical indication. (Billing & Coding Article A57204 R16)",
     False, "", ["R51.9", "R55", "R56.9", "G45.9", "I63.9", "I61.9", "S09.90XA", "G40.909"]),

    ("Noridian-WA", "72141",
     "LCD L37373: MRI cervical spine without contrast (Noridian JF, Washington). Covered for "
     "cervical radiculopathy, myelopathy, or neck pain with neurologic deficit after conservative "
     "care. Cervicalgia alone (M54.2) is typically insufficient without radiculopathy or neurologic "
     "findings. (Billing & Coding Article A57204 R16)",
     False, "", ["M54.12", "M50.12", "M50.32", "M48.02", "M47.812", "G54.2", "M54.2"]),

    # LCD L34415 — CT Abdomen and Pelvis (Noridian JF, Washington)
    ("Noridian-WA", "74177",
     "LCD L34415: CT abdomen and pelvis with contrast (Noridian JF, Washington). Covered for "
     "acute abdominal pain, suspected appendicitis, renal/ureteral calculus, intra-abdominal mass, "
     "diverticulitis, GI bleeding, unexplained weight loss, or malignancy staging. PAMA AUC/CDSM "
     "documentation required for outpatient advanced imaging orders. (Billing & Coding Article A56421)",
     False, "", ["R10.11", "R10.31", "R10.9", "K35.80", "N20.0", "N20.1", "R19.00",
                 "R63.4", "C18.9", "K57.30", "K80.20"]),

    # LCD L34577 — Complete Abdominal Ultrasound (Noridian JF, Washington)
    ("Noridian-WA", "76700",
     "LCD L34577: Complete abdominal ultrasound (Noridian JF, Washington). Covered when all major "
     "abdominal organs are examined (liver, gallbladder, CBD, pancreas, spleen, kidneys, aorta, IVC). "
     "Indications include abdominal pain, organomegaly, palpable mass, ascites, suspected AAA, or "
     "known hepatic/renal/pancreatic pathology. Do NOT bill 76700 and 76770 together unless separate "
     "exams. (Billing & Coding Article A55336)",
     False, "", ["R10.11", "R10.9", "K80.20", "K85.90", "K74.60", "R16.0", "R16.2",
                 "N20.0", "I71.4", "C22.0", "R93.2"]),

    # NCD 220.4 + LCD L33950 — Screening/Diagnostic Mammography (Noridian JF, Washington)
    ("Noridian-WA", "77067",
     "NCD 220.4 / LCD L33950: Screening mammography (Noridian JF, Washington). Covered annually "
     "for women aged 40+; one baseline allowed ages 35–39. Z12.31 is required primary ICD-10. "
     "At least 11 full months must elapse between covered screenings. Facility must be FDA/MQSA-certified. "
     "(Billing & Coding Article A56448)",
     False, "", ["Z12.31", "Z15.01", "Z80.3", "Z85.3"]),

    ("Noridian-WA", "77066",
     "LCD L33950: Diagnostic mammography (Noridian JF, Washington). Covered for breast lump, "
     "nipple discharge, skin changes, abnormal screening finding, or personal/family history "
     "requiring diagnostic follow-up. (Billing & Coding Article A56448)",
     False, "", ["N63.9", "N64.4", "N64.51", "R92.8", "Z85.3", "Z80.3"]),

    # LCD L37636 — Nonobstetric Pelvic Ultrasound (Noridian JF, Washington)
    ("Noridian-WA", "76856",
     "LCD L37636: Pelvic ultrasound, complete non-obstetric (Noridian JF, Washington). Covered for "
     "pelvic pain, uterine fibroids, ovarian cysts or mass, endometriosis, abnormal uterine bleeding, "
     "postmenopausal bleeding, infertility evaluation, or lower urinary tract symptoms. Post-void "
     "residual (51798) must NOT be billed under 76856/76857. (Billing & Coding Article A56671)",
     False, "", ["D25.9", "E28.2", "N80.9", "N84.0", "N85.00", "N91.0", "N91.1", "N92.0",
                 "N93.9", "N94.4", "N95.0", "N97.9", "R10.32", "R19.09"]),

    # LCD L33459 — CTA Chest / CT Thorax (Noridian JF, Washington)
    ("Noridian-WA", "71275",
     "LCD L33459: CTA chest, PE protocol (Noridian JF, Washington). Covered for documented clinical "
     "suspicion of pulmonary embolism. IV contrast required; 3D reconstruction bundled into 71275 — "
     "do not separately bill 76376/76377. Document pre-test probability (Wells Score or equivalent). "
     "(Billing & Coding Article A56580)",
     False, "", ["I26.99", "I26.09", "I26.90", "R07.1", "R09.1", "Z87.891"]),

    ("Noridian-WA", "71250",
     "LCD L33459: CT thorax without contrast (Noridian JF, Washington). Covered for indeterminate "
     "pulmonary nodule follow-up (Lung-RADS), abnormal chest radiograph, suspected interstitial "
     "lung disease, mediastinal mass, or pleural pathology. (Billing & Coding Article A56580)",
     False, "", ["R91.1", "R91.8", "J98.11", "J84.9", "J93.9", "C34.90", "D14.31", "J18.9"]),

    # LCD L35753 — Non-Invasive Cerebrovascular Arterial Studies (Noridian JF, Washington)
    ("Noridian-WA", "93880",
     "LCD L35753: Carotid duplex scan, complete bilateral (Noridian JF, Washington). Covered for "
     "TIA, recent stroke, amaurosis fugax, documented cervical bruit, or known/suspected carotid "
     "stenosis. Annual surveillance for 20–49% stenosis; post-endarterectomy: 6-week, 6-month, "
     "1-year follow-up. Study must include duplex scanning with color Doppler and spectral Doppler "
     "waveform analysis. (Billing & Coding Article A52992)",
     False, "", ["I65.21", "I65.22", "I65.29", "G45.3", "G45.9", "R09.89", "I63.031",
                 "I63.9", "R55", "R22.1"]),

    # LCD L33627 — Extremity Venous Duplex / DVT (Noridian JF, Washington)
    ("Noridian-WA", "93970",
     "LCD L33627: Extremity venous duplex, complete bilateral (Noridian JF, Washington). Covered for "
     "clinically suspected DVT (edema, tenderness, erythema, warmth), work-up for suspected pulmonary "
     "embolism source, chronic venous insufficiency, or preoperative vein mapping for CABG/dialysis "
     "access. Clinical signs and symptoms must be documented. (Billing & Coding Articles A52993, A56758)",
     False, "", ["I82.401", "I82.402", "I82.4Z1", "I87.2", "I80.3", "I26.99",
                 "Z01.810", "Z01.818"]),

    # ---------------------------------------------------------------------------
    # NATIONAL (NCD) — Supplemental entries referencing explicit NCD IDs
    # These apply across all six states and fill gaps not covered by the
    # existing generic "Medicare" entries above.
    # ---------------------------------------------------------------------------

    # NCD 220.2 — MRI (explicit NCD coverage for cardiac device patients)
    ("Medicare", "70553",
     "NCD 220.2 / LCD L37373+L35175: MRI brain without then with contrast. Covered for intracranial "
     "mass characterization, metastatic disease work-up, or post-treatment follow-up. Also covered "
     "for patients with FDA-labeled MRI-conditional implanted cardiac devices (pacemakers, ICDs, "
     "CRT-D/CRT-P) under NCD 220.2 update. Contrast administration must be documented with "
     "indication. (NCD 220.2; CMS coverage database)",
     False, "", ["C71.9", "C79.31", "G35", "G45.9", "I63.9", "Z95.0"]),

    # LCD L33459 — CT Thorax (explicit LCD entry with L33459 ID for national Medicare)
    ("Medicare", "71250",
     "LCD L33459: CT thorax without contrast. Covered for indeterminate pulmonary nodule "
     "(Fleischner Society Lung-RADS follow-up), abnormal chest radiograph requiring further "
     "evaluation, suspected interstitial lung disease, mediastinal mass, or pleural pathology. "
     "NCD 220.1 frequency limit: no more than 6 studies of the same CPT per calendar year. "
     "(LCD L33459; Billing & Coding Article A56580)",
     False, "", ["R91.1", "R91.8", "J98.11", "J84.9", "J93.9", "C34.90", "J90", "D14.31"]),

    # LCD L34415 — CT Abdomen+Pelvis: appendicitis / diverticulitis expansion
    ("Medicare", "74176",
     "LCD L34415: CT abdomen and pelvis without contrast (Medicare, national). Covered when "
     "contrast is contraindicated (renal insufficiency, contrast allergy) with documented indication. "
     "Supported diagnoses include abdominal pain, calculus evaluation, diverticulosis, or mass. "
     "PAMA AUC/CDSM documentation required for outpatient advanced imaging orders. "
     "(LCD L34415; Billing & Coding Article A56421)",
     False, "", ["R10.9", "R10.11", "R10.31", "N20.0", "K57.30", "R19.00", "C18.9"]),

    # LCD L37636 — Pelvic Ultrasound: expanded ICD set for national Medicare
    ("Medicare", "76856",
     "LCD L37636: Pelvic ultrasound, complete non-obstetric (Medicare, national — updated policy). "
     "Covered for pelvic pain, abnormal uterine bleeding, postmenopausal bleeding, fibroids, PCOS, "
     "endometriosis, ovarian cyst or mass, endometrial polyp/hyperplasia, dysmenorrhea, amenorrhea, "
     "or pelvic mass. Post-void residual measurement (51798) is NOT separately billable under "
     "76856/76857. (LCD L37636; Billing & Coding Article A56671)",
     False, "", ["R10.2", "N93.9", "N83.20", "N80.9", "D25.9", "E28.2", "N84.0",
                 "N85.00", "N95.0", "N94.4", "N92.0", "R19.09"]),

    # LCD L33627 — DVT venous duplex: expanded ICD set for national Medicare
    ("Medicare", "93971",
     "LCD L33627: Extremity venous duplex, unilateral or limited (Medicare, national). Covered for "
     "unilateral DVT symptoms, follow-up after positive bilateral study, or one-extremity vein mapping. "
     "Cannot bill 93971 with 93970 on the same day for the same extremity. "
     "(LCD L33627; Billing & Coding Articles A52993, A56758)",
     False, "", ["I82.401", "I82.402", "I82.4Z1", "I87.2", "I80.3", "I26.99"]),

    # NCD 220.4 + LCD L33950 — Screening mammography: BRCA/hereditary risk expansion
    ("Medicare", "77067",
     "NCD 220.4 / LCD L33950: Screening mammography, bilateral (Medicare, national — expanded). "
     "Covered annually for women aged 40+; one baseline at 35–39. BRCA mutation carriers (Z15.01) "
     "and women with strong family history (Z80.3) qualify; code primary as Z12.31 for asymptomatic "
     "screening. 11 full months must elapse between covered screenings. Facility must be "
     "FDA/MQSA-certified. (NCD 220.4; LCD L33950; Billing & Coding Article A56448)",
     False, "", ["Z12.31", "Z15.01", "Z80.3", "Z85.3"]),
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
    # Atelectasis (UMLS C0004144) — maps to J98.11. Covers all clinical synonyms
    # ("bibasilar atelectasis", "subsegmental atelectasis", "atelectatic changes",
    # "linear atelectasis", "discoid atelectasis", "platelike atelectasis") via the
    # "atelectasis" token in the lexical scorer. Edges link it to the lung finding_site
    # and to pneumonia (the two conditions co-occur on chest X-ray so the pneumonia
    # concept node also surfaces it via graph traversal when consolidation is the chief
    # finding). UMLS CUI verified via NLM VSAC / Wikidata P2892.
    ("C0004144", "Atelectasis", "Disease", [{"system": "ICD10CM", "code": "J98.11"}]),
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
    ("C0004144", "finding_site", "C0024109"),    # atelectasis -> lung
    ("C0032285", "associated_with", "C0004144"), # pneumonia associated_with atelectasis
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
     "finding (e.g., solitary pulmonary nodule R91.1) or the sign/symptom that prompted the study, "
     "per the uncertain-diagnosis rule (§IV.H for outpatient). NOTE: R93.x codes apply ONLY to "
     "incidental findings — see the IncidentalFindings guideline; do not apply R93.x to the primary "
     "finding being evaluated.",
     "Radiology"),
    ("Radiology Coding Guidance", "OutpatientUncertainDiagnosis",
     "ICD-10-CM Official Guidelines §IV.H (Outpatient Uncertain Diagnosis — HIGHEST PRIORITY): "
     "For outpatient encounters, including all radiology reports, do NOT code a diagnosis described "
     "as 'suspected', 'probable', 'possible', 'consistent with', 'cannot be excluded', 'cannot rule "
     "out', or followed by 'clinical correlation recommended'. Code the documented sign, symptom, or "
     "abnormal finding instead. This rule applies to ALL outpatient settings and overrides §I.C.x "
     "inpatient rules. EXAMPLE: CT abdomen for RLQ pain, impression 'early appendicitis cannot be "
     "excluded' → R10.31 (right lower quadrant pain) only; K35.80 must NOT be assigned. Contrast: "
     "if the impression states 'acute appendicitis' definitively → K35.80 is appropriate.",
     "Radiology"),
    ("Radiology Coding Guidance", "IncidentalFindings",
     "ICD-10-CM Guideline Section I.C.18: R93.x (Abnormal findings on diagnostic imaging) codes are "
     "appropriate ONLY for truly incidental findings — discovered unexpectedly, unrelated to the study "
     "indication, and not captured by another assigned code. R93.x is NOT appropriate when the abnormal "
     "finding (1) directly explains or supports the presenting symptom, (2) IS the study indication "
     "(e.g., follow-up of a known nodule), or (3) is subsumed by a more specific assigned diagnosis. "
     "INCORRECT: CT abdomen/pelvis for RLQ pain finds periappendiceal inflammation → code R10.31 only; "
     "R93.5 must NOT be added (the inflammation is the radiologic correlate of the symptom). "
     "CORRECT: CT chest for cough incidentally finds a liver lesion → code cough + R93.2 (liver finding "
     "is unrelated to the chest study indication).",
     "Radiology"),
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
# Strategic fit: typical risk-adjustment tooling is HCC-focused — ACE extends that.
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


# ===========================================================================
# Stage-4 table-driven gates (closing the two spec gaps).
# POS_RULES — place-of-service validity (rows only where a restriction exists;
# unlisted codes pass with an honest "no restriction on file" detail).
# MODIFIER_PAIR_RULES — per-CPT modifier pairings that are INVALID (MPFS
# PC/TC-indicator style), e.g. modifier 50 on inherently-bilateral codes.
# ===========================================================================

# (code, allowed_pos, rationale)
POS_RULES = [
    ("99281", ["23"], "ED visit codes are valid only in the emergency department"),
    ("99282", ["23"], "ED visit codes are valid only in the emergency department"),
    ("99283", ["23"], "ED visit codes are valid only in the emergency department"),
    ("99284", ["23"], "ED visit codes are valid only in the emergency department"),
    ("99285", ["23"], "ED visit codes are valid only in the emergency department"),
    ("99291", ["23", "21"], "critical care delivered in the ED or inpatient setting"),
    ("99292", ["23", "21"], "critical care add-on follows 99291"),
    ("99203", ["11", "19", "22"], "office/outpatient visit"),
    ("99204", ["11", "19", "22"], "office/outpatient visit"),
    ("99213", ["11", "19", "22"], "office/outpatient visit"),
    ("99214", ["11", "19", "22"], "office/outpatient visit"),
    ("99215", ["11", "19", "22"], "office/outpatient visit"),
    ("G0438", ["11", "19", "22"], "annual wellness visit — office/outpatient"),
    ("G0439", ["11", "19", "22"], "annual wellness visit — office/outpatient"),
    ("47562", ["21", "22", "24"], "laparoscopic cholecystectomy requires a facility setting"),
    ("45378", ["22", "24"], "endoscopy suite — hospital outpatient or ASC"),
    ("45380", ["22", "24"], "endoscopy suite — hospital outpatient or ASC"),
    ("45385", ["22", "24"], "endoscopy suite — hospital outpatient or ASC"),
    ("43235", ["22", "24"], "endoscopy suite — hospital outpatient or ASC"),
    ("43239", ["22", "24"], "endoscopy suite — hospital outpatient or ASC"),
    ("27447", ["21", "22", "24"], "total knee arthroplasty requires a facility setting"),
    ("29881", ["21", "22", "24"], "surgical arthroscopy requires a facility setting"),
    ("29826", ["21", "22", "24"], "surgical arthroscopy requires a facility setting"),
    ("66984", ["22", "24"], "cataract surgery — hospital outpatient or ASC"),
    ("65855", ["11", "22", "24"], "laser trabeculoplasty — office laser suite or facility"),
    ("50590", ["21", "22", "24"], "lithotripsy requires a facility setting"),
    ("52234", ["21", "22", "24"], "operative cystoscopy requires a facility setting"),
    ("42820", ["21", "22", "24"], "tonsillectomy requires a facility setting"),
    ("69436", ["21", "22", "24"], "tympanostomy under general anesthesia requires a facility"),
]

# (code, modifier, rationale)
MODIFIER_PAIR_RULES = [
    ("77067", "50", "descriptor is already bilateral — modifier 50 is invalid"),
    ("77066", "50", "descriptor is already bilateral — modifier 50 is invalid"),
    ("66984", "50", "bilateral cataract is staged — report per eye with RT/LT, not 50"),
    ("99213", "26", "E/M services have no professional/technical split"),
    ("99214", "26", "E/M services have no professional/technical split"),
    ("99215", "26", "E/M services have no professional/technical split"),
    ("99283", "26", "E/M services have no professional/technical split"),
    ("99284", "26", "E/M services have no professional/technical split"),
    ("99285", "26", "E/M services have no professional/technical split"),
    ("99291", "26", "E/M services have no professional/technical split"),
    ("47562", "26", "surgical procedure — no professional/technical split"),
    ("45385", "26", "surgical procedure — no professional/technical split"),
    ("43239", "26", "surgical procedure — no professional/technical split"),
]
