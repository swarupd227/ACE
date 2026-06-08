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
    # E&M (established / new office visit) — modality ANY
    ("99213", "Office/outpatient visit, established patient, low MDM", "ANY"),
    ("99214", "Office/outpatient visit, established patient, moderate MDM", "ANY"),
    ("99215", "Office/outpatient visit, established patient, high MDM", "ANY"),
    ("99203", "Office/outpatient visit, new patient, low MDM", "ANY"),
    ("99204", "Office/outpatient visit, new patient, moderate MDM", "ANY"),
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
]
# (src_cui, rel, dst_cui)
ONTOLOGY_EDGES = [
    ("C0032285", "finding_site", "C0024109"),   # pneumonia -> lung
    ("C0032285", "associated_with", "C0010200"), # pneumonia -> cough
    ("C0008031", "associated_with", "C0032285"), # chest pain -> pneumonia
    ("C0011882", "is_a", "C0011860"),            # diabetic neuropathy -> T2DM
    ("C0022650", "finding_site", "C0024109"),
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
]
