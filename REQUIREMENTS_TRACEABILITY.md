# Requirements Traceability — "Speciality Use Case Requirements for Auto Coding V2"

Maps **every line** of the Vee Healthtek Use-Case/acceptance document to where it lives in the ACE app.
Status: ✅ Covered · ◑ Partial (demo-scale/roadmap) · ⬜ Outlined (post-demo).

| # | Requirement (from the doc) | Status | Where in the app |
|---|---|---|---|
| §1/§2 | High autonomous accuracy + continuous improvement | ✅ | Eval Harness (100% on golden set) + Closed-Loop Learning |
| §1/§2 | Reduce coding turnaround time (TAT) | ✅ | Dashboard **Coding TAT reduction** (manual baseline → AI-assisted, %) |
| §1/§2 | Improve productivity / coder efficiency | ✅ | Dashboard **Manual effort reduction** + Control Tower |
| §1/§2 | Progressive increases in STB | ✅ | Dashboard **STB rate** + **Automation maturity pathway** |
| §1/§2 | Scalable framework for specialty expansion | ✅ | 5 specialties live; specialty-accelerator retrieval/config |
| §2 | Clinical scope: X-ray, CT, MRI; structured+unstructured | ✅ | Radiology charts (XR/CT/MRI), narrative + structured |
| §2 | Interventional Radiology excluded | ✅ | Stage 0 eligibility gate routes IR → manual |
| §2/§6 | ≥90% accuracy (chart level) | ✅ | Eval Harness (per-specialty chart accuracy) |
| §2/§6 | 10–15% TAT improvement | ✅ | Dashboard TAT-reduction KPI (reference baselines per specialty) |
| §2/§6 | Progressive automation maturity → ≥80% | ✅ | Dashboard maturity pathway (current position vs ≥80% target) |
| §2/§6 | Manual effort reduction ≥30% | ✅ | Dashboard KPI |
| §3.1 | Extract clinical contextual findings | ✅ | Stage 2 extraction (per-chart pipeline trace) |
| §3.1 | Identify anatomy, procedures, indications, diagnoses | ✅ | Stage 2 structured slots |
| §3.1 | Interpret structured + unstructured narratives | ✅ | Conditioning + extraction |
| §3.2 | CPT, ICD-10, HCPCS, modifier assignment | ✅ | Coding agent (modifiers incl. 26/TC) |
| §3.2 | Coding validation + payer-specific edits | ✅ | Validation gates + Policy & Knowledge Admin |
| §3.2 | Compliance + coding-standards validation | ✅ | Gates + citation/guideline verification |
| §3.3 | High→STB / Medium→QA / Low→Manual | ✅ | Confidence routing (lanes) + Control Tower |
| §3.4 | Capture coder corrections | ✅ | Encounter override |
| §3.4 | Log override decisions | ✅ | Audit ledger + Closed-Loop Learning |
| §3.4 | Continuous model retraining & optimization | ◑ | Exemplar-based learning live (apply/withdraw); 24–48h fine-tune batch described (BLUEPRINT) |
| §4.1 | Code sets ICD-10-CM/CPT/HCPCS | ✅ | Reference tables (real ICD-10/HCPCS; labeled placeholder CPT) |
| §4.1 | Monthly/annual code-set updates | ✅ | Effective-dated tables; effective window shown in Policy Admin → Data Sources |
| §4.1 | Gold-standard 1,000+ Master-Coder charts | ◑ | Frozen golden-set mechanism real (adjudicated + IRR); demo volume ~12 (1,000+ = production data) |
| §4.1 | NCCI / MUE / LCD-NCD | ✅ | Deterministic gates + Policy Admin |
| §4.1 | Payer-specific rules (knowledge graph) | ✅ | Policy & Knowledge Admin (editable, drives gate) + graph |
| §4.1 | Associated patient + encounter data | ✅ | Encounter model (patient/age/sex/payer/POS/DOS) |
| §4.2 | Extraction / recommendation / rule-based checks | ✅ | Pipeline Stages 2–4 |
| §4.3 | Confidence-based routing (STB/QA/escalation) | ✅ | Stage 5 routing |
| §4.4 | Coder reviews; edits captured & logged | ✅ | Encounter workbench + audit |
| §4.5 | Corrections → retraining; improvement demonstrated | ✅ | Learning transfer (a correction shifts a later chart) |
| §5.1 | Scenario 1 — standard radiology → STB | ✅ | Chest X-ray chart → 71046-26 + J18.9, STB |
| §5.2 | Scenario 2 — multi-procedure bundling + modifiers | ✅ | CT abdomen+pelvis → single 74177-26 (NCCI) |
| §5.3 | Scenario 3 — complex narrative, avoid overcoding | ✅ | Rule-out chest X-ray → R05.9 (no pneumonia) |
| §5.4 | Scenario 4 — exception handling, reason flagged | ✅ | Incomplete / interventional → Manual + reason |
| §7.1 | Ingest radiology reports w/ data pipeline | ✅ | **Integrations & Ingestion** screen (live ingest → queue) |
| §7.1 | Simulated/real PMS-EHR integration | ✅ | Integrations connectors (Practice Admin/eCW/Cerner), FHIR/HL7/EDI channels |
| §7.1 | API & batch integrations | ✅ | Live REST API (/docs) + batch "Run autonomous coding" |
| §7.2 | AI extraction / rule engine / confidence / workflow / audit | ✅ | Pipeline + gates + 4-factor confidence + Control Tower + audit ledger |
| §7.3 | Dashboard: accuracy, STB, exception rates | ✅ | Performance Dashboard (incl. explicit **Exception rate** KPI) |
| §7.3 | Demonstration of feedback impact | ✅ | Closed-Loop Learning transfer |
| §8 | Audit traceability of coding decisions | ✅ | Append-only audit ledger + defense packet |
| §8 | Explainability of AI recommendations | ✅ | Citations + rule justification + 4-factor + "Knowledge used" |
| §8 | Controls to prevent coding unsupported documentation | ✅ | Citation requirement + verification + specificity gate + eligibility |
| §8 | Human oversight & compliance controls | ✅ | HITL workbench, bounded autonomy, reassign/escalate/rollback |
| §8 | Model versioning | ✅ | model_version stamped per run (audit + run detail) |
| §8 | De-identified medical charts | ✅ | Synthetic, PHI-free charts |
| §9 | AI reads reports → accurate coding; integrates w/o disruption | ✅ | Whole pipeline + Integrations surface |
| §9 | Reduced manual workload; clear exception pathway | ✅ | Manual-effort KPI + Control Tower exception queue |
| §9 | Labor→automation transition; scalable post-radiology | ✅ | 5 specialties + maturity pathway |
| §10 | Multi-specialty expansion | ✅ | Radiology/E&M/ED/Pathology/Surgical |
| §10 | Increased STB over time | ✅ | Maturity pathway (current → ≥80%) |
| §10 | Integration with CDI workflows | ✅ | CDI / Physician Queries module |
| §10 | Denial-prevention workflows | ⬜ | Outlined in BLUEPRINT/PROPOSAL (post-demo) |
| §10 | Enterprise-scale deployment support | ⬜ | Azure/Foundry mapping (BLUEPRINT) |

## Honest notes on the ◑ / ⬜ items
- **1,000+ gold charts** — the *process* (frozen set, multi-coder adjudication, IRR ceiling) is real; the
  *volume* is demo-scale. 1,000+ master-coded charts is a production data-onboarding deliverable.
- **Continuous retraining** — the closed loop is live as retrieval exemplars; true SLM fine-tune runs as a
  24–48h batch in production (designed in BLUEPRINT, not executed in a self-contained demo).
- **Denial prevention / enterprise deploy** — explicitly "Future Expansion (Post-Demo)" in the doc; we
  *outline readiness* (BLUEPRINT/PROPOSAL) rather than build, as requested.

Everything else in the acceptance document is **implemented and demonstrable in the running app.**
