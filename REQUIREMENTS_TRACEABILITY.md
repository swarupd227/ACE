# Requirements Traceability — Vee Healthtek (Use-Case + SOW)

Single source of truth mapping **every line** of the two Vee Healthtek requirement documents to where it
lives in the ACE app. Covers:
- **Part A** — *Speciality Use Case Requirements for Auto Coding V2* (the demo acceptance criteria)
- **Part B** — *Statement of Work for AI Partner V2* (the broader engagement scope)

**Legend:** ✅ Covered (in the running app) · ◑ Partial (demo-scale / mechanism real, volume or depth is
production) · ⬜ Outlined (designed in BLUEPRINT/PROPOSAL, post-demo per the docs).

> **Maintenance convention:** update this file whenever a requirement's status changes (new feature, gap
> closed, scope change). Bump _Last updated_ and reference the commit. Keep Part A/B in sync with the app.

**Last updated:** 2026-06-08 · commit `abc7af9` · app = 8 screens, 5 specialties.

---

## Part A — Speciality Use Case Requirements for Auto Coding V2

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

---

## Part B — Statement of Work for AI Partner V2

| § | Requirement (from the SOW) | Status | Where in the app / notes |
|---|---|---|---|
| 2.1 | Automated assignment of ICD-10-CM | ✅ | Coding agent → ICD-10-CM |
| 2.1 | Automated assignment of CPT/HCPCS | ✅ | Coding agent (placeholder CPT; real HCPCS) |
| 2.1 | Modifiers & associated coding logic | ✅ | Modifiers incl. 26/TC/51/59/RT-LT/78-79/80-82/AS; auto-26 rule |
| 2.1 | Interpret structured & unstructured docs | ✅ | Conditioning + extraction |
| 2.1 | Real-time confidence scoring + intelligent exception handling | ✅ | 4-factor confidence + routing + Stage-0 exceptions |
| 2.1 | HITL: coders, auditors, supervisors, client stakeholders | ✅ | Encounter workbench + Control Tower roster (Coder/QA Auditor/CDI) |
| 2.1 | Compliance validation: NCCI / LCD-NCD / client / payer rules | ✅ | Gates + Policy Admin (incl. client overlays) |
| 2.1 | Explainability, evidence traceability, audit-ready docs | ✅ | Citations + rule justification + audit ledger / defense packet |
| 2.1 | Workflow orchestration: **rollback, reassignment, QA routing, escalation** | ✅ | Reassign / Escalate / **Revert-to-AI (rollback)** + lanes |
| 2.1 | Continuous AI training, tuning, optimization | ◑ | Exemplar learning live; SLM fine-tune batch described (BLUEPRINT) |
| 2.1 | Straight-Through Billing support | ✅ | STB lane + STB-rate KPI |
| 2.2A | Baseline models; specialty customization | ✅ (config) | Specialty-aware retrieval/guidance/gates (5 specialties) |
| 2.2A | Continuous improvement via feedback loops & labeled data | ◑ | Closed-Loop Learning (exemplars); labeled-data retraining = prod |
| 2.2A | Periodic tuning / retraining | ◑ | Described (BLUEPRINT 24–48h batch) |
| 2.2A | AI Model Invocation: specialty-aware models | ✅ | Per-specialty config + model tiering (Sonnet/Opus) |
| 2.2A | Versioned payloads (rules, guidelines, **model version**) | ✅ | model_version stamped per run (audit + run detail) |
| 2.2A | Async, fault-tolerant execution | ◑ | LLM-failure fallback + self-consistency tolerance; demo runs sequentially (prod = queue/worker) |
| 2.2A | Outputs: Principal/Primary/Secondary diagnoses | ✅ | CodeResult.role |
| 2.2A | Outputs: Primary/Secondary CPT, Modifiers, **Assistant Surgeon**, POS | ✅ | CodeResult (modifiers incl. 80/82/AS; POS on encounter) |
| 2.2A | Confidence score per code | ✅ | Per-code calibrated confidence (color-coded) |
| 2.2B | Data: code sets, gold charts, NCCI/MUE/LCD-NCD, payer KG, encounter data | ✅ / ◑ | All present; gold set demo-scale (see notes) |
| 2.2C | Auto-coding eligibility (docs/auth/specialty/exclusions) → manual + reason | ✅ | Stage 0 eligibility gate |
| 2.2D | Integration: EHR / RCM / clearinghouse / billing; APIs, batch, pipelines | ✅ (simulated) | Integrations & Ingestion (connectors + FHIR/HL7/EDI/REST + live ingest + batch) |
| 2.2E | Each code: evidence snippet + source ref + rule justification + confidence explanation | ✅ | Encounter detail code card |
| 2.2E | Decisions versioned & replayable | ✅ | Audit ledger + rollback snapshot |
| 2.2F | Autonomous workflows; intelligent low-confidence routing | ✅ | Orchestrator + lanes |
| 2.2F | QA & audit workflows | ✅ | QA lane + Control Tower + audit packet |
| 2.2F | CDI escalation triggers | ✅ | CDI module + escalate action |
| 2.2F | Workforce management & operational governance | ✅ | Control Tower assignment + SLA |
| 2.2G | Dashboards: accuracy, STB, TAT, exception, productivity, audit/compliance trends | ✅ | Performance Dashboard (accuracy, STB, TAT reduction, exception, manual-effort) |
| 2.2G | Weekly/monthly performance reports | ⬜ | Dashboard is live; scheduled report export = roadmap |
| 2.3A | Confidence indicator on auto-coded ICD **and** CPT | ✅ | Color-coded confidence per code |
| 2.3B | Accuracy from doc-match + historical + rule-engine + model certainty | ✅ | Exact **4-factor** confidence breakdown |
| 3 | Implementation phases (Discovery→Pilot→Go-live→Scale) | ⬜ | Engagement plan in PROPOSAL.md |
| 4 | Deliverables: platform / specialty models / interfaces / dashboards / audit / SOPs | ✅ / ◑ | Platform, dashboards, audit ✅; SOPs/training = DEMO_SCRIPT/README/BLUEPRINT |
| 5 | SLAs: ≥90% accuracy; STB ramp; near-real-time TAT; exception SLA | ✅ | Eval + maturity + TAT KPI + Control Tower SLA timers |
| 6 | VHT 100% audit early → certify model at ≥95% | ✅ (modeled) | Maturity pathway + QA lane (governance ramp) |
| 7 | HIPAA / SOC2 / encryption / audit / explainability | ✅ / ⬜ | HIPAA-shaped + audit + explainability ✅; SOC2/encryption = deployment (BLUEPRINT) |
| 8 | Term & termination | n/a | Commercial/legal (PROPOSAL) |

---

## Honest notes on the ◑ / ⬜ items
- **1,000+ gold charts** — the *process* (frozen set, multi-coder adjudication, IRR ceiling) is real; the
  *volume* is demo-scale. 1,000+ master-coded charts is a production data-onboarding deliverable.
- **Continuous retraining** — the closed loop is live as retrieval exemplars; true SLM fine-tune runs as a
  24–48h batch in production (designed in BLUEPRINT, not executed in a self-contained demo).
- **Denial prevention / enterprise deploy** — explicitly "Future Expansion (Post-Demo)" in the doc; we
  *outline readiness* (BLUEPRINT/PROPOSAL) rather than build, as requested.
- **Async/fault-tolerant distributed execution (SOW 2.2A)** — the orchestrator already tolerates LLM
  failures and partial self-consistency; the demo runs sequentially. Production = a queue/worker fabric
  (designed in BLUEPRINT), not built into the self-contained demo.
- **Scheduled weekly/monthly reports (SOW 2.2G)** — the live dashboard exists; scheduled export/delivery
  is a packaging step, not built.
- **SOC 2 / encryption / vendor assessment (SOW 7)** — deployment-time controls (Azure/Foundry, US-region,
  multi-tenant) covered in BLUEPRINT; the app is HIPAA-shaped (PHI-safe synthetic data, RBAC-ready, audit).
- **Implementation phases / term (SOW 3, 8)** — engagement/commercial items in PROPOSAL.md, not app features.

Everything else in **both** documents is **implemented and demonstrable in the running app.**
