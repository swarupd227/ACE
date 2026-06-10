# Demo Script — ACE Autonomous Coding (Bangalore, ~20–25 min)

**Audience:** Amrish Kumar (CTAIO), Michelle Castillon (CPTO), Murali (Ops), JC (data science), TA.
**Setup before you walk in:** `docker compose up -d`, confirm `http://localhost:8000/api/meta` shows
`llm_available: true`, open `http://localhost:8080`. Make sure the worklist is freshly seeded (pristine,
0 coded) so the live run lands. Keep this script on a second screen.

> One-line framing to open with: *"This is ACE — the autonomous coding engine that runs inside RevAmp's
> Coding Studio. It's a bounded, agentic pipeline: every code is cited, validated, calibrated, and routed
> — and when it isn't sure, it hands the chart to a human. Let me show you on real charts."*

---

## 0. Control Tower (2 min) — `Control Tower`
- Open on the manager's live operating view: **work queues** (STB / QA / Manual / Escalated / CDI) with
  **SLA aging** and **breach** flags. Click a queue to see its items; **select charts and assign** them to
  a coder/auditor from the roster.
- Message: *"This is the operating picture — live queues, SLA, and workforce assignment. Now let's see
  where the work comes from and how each chart is coded."*

## 0.7 Integrations & Ingestion (1.5 min) — `Integrations & Ingestion`
- Show connected source systems (Practice Admin / eCW / Cerner) + channels (FHIR R4 / HL7 v2 / EDI 837 /
  SFTP / REST). **Load a sample report → Ingest into queue → it appears live in the Worklist.**
- **The "real charts aren't clean text" beat:** scroll to **Ingest a scanned document** → upload the sample
  scanned chart (PDF/image) → the model **transcribes it live (vision OCR)** → extracted text appears →
  open the encounter → run coding → same pipeline, same citations. *"Real charts arrive as document
  packets — scans, faxes, PDFs. This is the Document Ingestion & Conditioning front-end doing real OCR
  with the same reasoning model; anything unreadable is marked [illegible], never invented. In production
  this is industrialized — Azure Document Intelligence for bulk OCR, document classification and
  splitting — feeding this identical pipeline."*
- Message: *"Charts arrive from the EHR/PMS; the connectors are simulated, the ingest — text or scanned —
  is real."*

### Anticipated question — "Are real charts this clean? It's never one text blob."
Correct — and the architecture assumes that. The honest answer, in three parts:
1. **Radiology (the anchor) genuinely is text-first**: production radiology coding runs off the dictated
   report (PowerScribe etc.) — a single text document, exactly as demoed.
2. **The pipeline's Stage 1 is literally Document Conditioning**: the conditioning flags you saw
   (`ocr_artifact`, `copy_forward`, `unsigned`, `addendum`, `missing_documentation`) exist because real
   input is messy — RAD10004/RAD10005 show the engine *refusing* incomplete documents rather than coding them.
3. **The scanned-document ingest you just watched is the multi-format path working live**: PDFs, scans and
   faxes are transcribed by the same model family (vision), then enter the identical pipeline. The demo
   charts are synthetic single-text because they are PHI-free seed data — not because the engine expects
   clean input. Production adds document classification, splitting/de-dup and bulk OCR (Azure Document
   Intelligence on their mandated stack) in front of the same Stage 0–5.

### Anticipated question — "Are you removing PII before sending charts to the AI?"
The honest, layered answer:
1. **Today, nothing real reaches the model.** Every demo chart is synthetic, PHI-free seed data by design.
2. **In production the lawful path is the BAA chain, not redaction.** Coding is a HIPAA payment/operations
   use; PHI flows to the model under a Business Associate Agreement — on the mandated Azure stack, models
   in Azure AI Foundry sit under Microsoft's BAA (Claude is available through Foundry, and is HIPAA-eligible
   via Bedrock/Vertex; Anthropic offers enterprise BAA / zero-data-retention terms). US-region residency is
   already an architecture commitment, and API inputs are never used for model training — contractually.
3. **Full de-identification would break the coding.** The chart's age, sex, dates and clinical detail are
   exactly what correct coding needs — our own sex/age gates validate codes against demographics. A
   Safe-Harbor-stripped chart cannot be coded accurately.
4. **What carries no coding value, we mask — defense in depth.** Direct identifiers (name, MRN, SSN, phone,
   address) can be redacted at the ingestion/conditioning front-end and re-attached after coding — Azure
   Health Data Services de-identification or Microsoft Presidio, slotted exactly at Stage 1. A per-client
   production configuration, not a rebuild.

## 1. The worklist + the run (3 min) — `Worklist`
- Show the queue (Radiology, E&M, ED; payers; clients Practice Admin/eCW/Cerner).
- **The agentic moment:** on an *uncoded* chart (e.g. one you just ingested), click **Code** → the
  **Agent Console streams the run live** — Eligibility → Conditioning+Extraction Agent (*invoking Claude…*)
  → Graph-RAG Retriever → Coding Agent → Validation Engine (gate-by-gate) → Calibration & Routing, with
  real LLM latency between steps. *"You watch the agent think and call its tools — not a spinner."*
  (On any *coded* chart, the encounter detail has **Watch agent re-run** to replay it live.)
- "Run autonomous coding" is the **batch** equivalent (pre-run before the meeting; narrate the **STB/QA/
  Manual** split + **STB rate** tile afterward).

## 2. Scenario 1 — clean radiology → STB (3 min) — open the chest X-ray (RAD10001)
- Hover a code → **chart lines highlight** (the citation gesture). *"Every code points at the words that justify it."*
- Show the **4-factor confidence** (doc match / historical / rule engine / model).
- Point out **modifier 26** on the imaging CPT and the **component_modifier** gate passing —
  *"facility read = professional component; the system codes it the way your radiology coders do."*
- Show the **validation gates** all green → **STB**. Expand the **Pipeline trace (Stage 0–5)** to show
  every intermediary step (eligibility → conditioning → extraction → retrieval → cited coding → gates →
  calibration) — the architecture, lived per-chart rather than on a slide.

## 3. Scenario 2 — multi-procedure bundling (2 min) — CT abdomen+pelvis (RAD10002)
- One **combined 74177**, NOT unbundled 74150+72192. Call out the **NCCI** gate.
- *"This is the unbundling mistake that drives denials — caught deterministically, not hoped away."*

## 4. Scenario 3 — avoid overcoding (2 min) — rule-out chest X-ray (RAD10003)
- Chart says "rule out pneumonia"; film is clear. System codes **R05.9 cough**, **not pneumonia**.
- *"This is the upcoding failure mode regulators care about. The 'uncertain diagnosis' guideline is cited."*

## 5. Scenario 4 — exception handling (1 min) — incomplete + interventional (RAD10004 / RAD10005)
- Both routed **Manual** at **Stage 0 eligibility** with a reason (incomplete docs / interventional out-of-scope).
- *"It refuses to code what it shouldn't. No fabrication — ever. (No LLM key? Every chart routes here.)"*

## 6. ED depth (2 min) — ED standard (ED30001) + critical care (ED30002)
- ED30001 → **99284** (ED E&M level by MDM) → STB.
- ED30002 → **99291 critical care**, routed **QA by bounded-autonomy rule** (critical-care codes always
  get human eyes regardless of confidence). *"Highest-dollar, highest-scrutiny calls stay with humans."*

## 7. E&M depth (2 min) — established visit (EM20001)
- **99214** (MDM-leveled) + **E11.40** (diabetes WITH neuropathy — supported by the exam) + **I10**.
- *"Specialty accelerator: same pipeline, E&M leveling rules — and it still won't over-specify."*

## 7.5 CDI / physician query — LIVE (3 min) — "co-pilot, not replacement"
1. Open **EM20002** (anemia E&M chart). Note the initial code is **D64.9 (anemia, unspecified)** —
   the type isn't documented.
2. Click **Scan for CDI opportunities** → the **CDI Agent console streams live** (reviewing docs →
   checking codes → drafting queries). ACE drafts a **compliant, non-leading** query: states the
   indicators (Hgb 8.2, iron started), offers options *including "Unable to determine"*, and does not
   lead the physician.
3. Click the physician answer **"Iron deficiency anemia"** → the encounter **re-codes to D50.9**
   (iron-deficiency anemia) — more specific, audit-defensible, captured automatically.
- *"This is the CDI revenue + integrity story from your own case studies — AI as a CDI co-pilot. It
  drafts the query, the physician decides, and coding updates on the answer."* (See the **CDI / Physician
  Queries** screen for the full queue.)

## 8. Closed-loop learning — LIVE (3 min) — the money moment
1. Open **RAD10009** ("learning loop A"). Note the abdominal-pain code the model picked.
2. Click **Override**, enter a **client-specific preference** (e.g. correct code + reason
   *"Client policy: use R10.84 for abdominal-pain studies"*), submit.
3. Open **Closed-Loop Learning** → the correction now appears, keyed to the chart pattern.
4. Go to **RAD10010** ("learning loop B"), click **Code** → it now adopts the corrected code with a
   **`learned`** badge and higher *historical* confidence.
- *"Corrections don't evaporate. In production this is a 24–48h batch into the SLM fine-tune pipeline."*

## 8.6 Workflow actions (1 min) — orchestration controls
- On any coded encounter, point to **Reassign queue** (STB / QA / Manual) and **Escalate to senior
  reviewer**. Reassign a chart from STB → QA ("spot audit"), then **Escalate** it — note the
  worklist now shows the **escalated flag / high priority**, and both actions land in the **audit
  ledger**. Then click **Revert to AI recommendation** to undo all human edits back to the original
  AI output (also audit-logged). *"Supervisors keep full control — routing, reassignment, escalation,
  and rollback, all audit-logged."*

## 9. Defensibility + honest measurement (2 min)
- On any coded chart, open the **Audit packet** → append-only evidence chain (stage, actor, event, model
  version, timestamps). *"This is your RAC-audit defense, generated automatically."*
- `Policy & Knowledge Admin` → **edit a payer policy live** (add a covered diagnosis, toggle prior-auth,
  or add a client overlay) — these drive the medical-necessity gate on the next coding run. The **Explore
  Graph** tab is an **interactive Cytoscape force-directed ontology graph** (search, zoom, drag, click a
  node to inspect its relationships); **Data Sources** shows provenance. On any encounter, the
  **"Knowledge used for this chart"** panel proves which facts shaped *that* decision.
- `Evaluation Harness` → click **Run evaluation** → per-specialty accuracy **vs adjudicated consensus
  with the IRR ceiling**. *"We never claim to beat the laws of inter-coder agreement; we report honestly."*
- `Performance Dashboard` → STB rate, calibrated accuracy, **manual-effort reduction**, **coding TAT
  reduction** (manual baseline → AI-assisted), **exception rate**, and the **automation-maturity pathway**
  (current position vs the ≥80% target); note the **100%-audit → 95%-certification** governance ramp.

## 9.5 Admin, configurability & RBAC (3 min) — the Nous platform layer
*Switch the top-bar **Role** to **Admin** for this section. This is the "anyone can demo a coding model;
nobody hands you a configurable platform" beat.*

- **Build the Knowledge Graph live** — `Policy & Knowledge Admin → KG Builder`. *"The ontology isn't a
  picture; it's editable, and the agent reads it on every run."* Click **Add concept** → e.g.
  `Pulmonary embolism` (semantic type *Disease or Syndrome*), map it to `ICD10CM:I26.99` and `CPT:71275`,
  Create. Add a **relationship** (`Pulmonary embolism —finding_site→ Lung`). Flip to **Explore Graph** —
  the new node is already in the Cytoscape graph. *"On the next chart that mentions this finding, that
  concept and its codes are surfaced to the coding agent as grounded candidates — this is how a client
  curates the KG without engineering. Production swaps in licensed SNOMED CT / UMLS at the same shape."*
- **Coding Guidelines** tab → add a public guideline (source / section / specialty / text). *"Retrieved
  into the agent's context and used for citation verification — your coding rules, governed in one place."*
- **Reference Data** tab → *"Even the edit engine is yours to govern."* Sub-tabs: **Code sets**
  (add a client-overlay ICD/CPT/HCPCS code), **NCCI bundling** (add a bundling edit — drives the bundling
  gate), **MUE limits** (units-per-day gate), **Modifiers** (validity gate), **Provenance**. *"These
  aren't a static reference dump — they drive the deterministic validation gates on the next run."*
- **Admin / Configuration** — *"Every threshold is a setting, not a code change."* Show the tabs:
  **Routing & Calibration** (drag the STB threshold 0.90 → 0.99 and Save), **Bounded Autonomy** toggles,
  **Eligibility**, **SLA Targets**, **Specialty Accelerator** (enable a specialty / set its model tier),
  **Users & Roster**, **Connectors** (toggle a PMS/EHR feed on/off — reflected on the Integrations screen).
  *"On the next run that chart re-routes STB → QA — the engine reads this config at runtime."*
- **Specialty accelerator — the proof** → point at **Cardiology** (echocardiogram → 93306, ECG → 93000)
  and **Orthopedics** (total knee arthroplasty → 27447, joint injection → 20610) in the worklist.
  *"Both were added with no pipeline changes — just their codes, a few knowledge-graph concepts, payer
  policy, coding guidance and a golden set, plus a config entry. The same engine that does Radiology now
  does cardiac, ortho, women's health, GI endoscopy, dermatology, urology, anesthesia, eye care and ENT,
  and the Evaluation Harness already scores them. That's how fourteen specialties — Radiology, E&M, ED,
  Pathology, Surgical, Cardiology, Orthopedics, OB/GYN, GI / Endoscopy, Dermatology, Urology, Anesthesia,
  Ophthalmology and ENT — run on one accelerator. New specialties are content, not a rebuild."*
- **Inpatient / MS-DRG — the Tier-B engineering track** → open an **Inpatient (DRG)** chart (e.g. IP10001
  pneumonia, IP10002 colon resection). *"Outpatient is CPT + NCCI/MUE. Inpatient is a different mental
  model, and we built the real engineering for it: ICD-10-PCS procedures and a deterministic MS-DRG
  grouper — principal diagnosis → MDC → surgical/medical partition → base DRG → CC/MCC severity tier."*
  Point at the **DRG result card**: DRG number, relative weight, and the **severity driver** (the MCC/CC
  secondary that moved the DRG and the payment). Expand **"Show grouper logic"** for the audited step-by-step.
  *"This is where CDI revenue lives — capture the documented MCC and the DRG (and the reimbursement) changes.
  The grouper is real; the code/weight tables are a curated public-CMS subset, swapped for the full
  definitions or a certified grouper in production. ICD-10-PCS, the DRG weights and the CC/MCC lists are all
  public — so this is actually more defensible than outpatient CPT."* The Evaluation Harness scores **DRG
  accuracy** for these cases too.
- **HCC / Risk Adjustment — the RevCap adjacency** → open an **HCC / Risk Adjustment** chart (HC10001 AWV).
  *"This one is strategic: RevCap is already HCC-focused, so ACE doesn't replace it — it extends it with
  agentic capture and a defensible audit trail. Risk adjustment is a third payment model: longitudinal
  diagnosis capture, not per-claim procedures."* Point at the **RAF result card**: the RAF score, the
  demographic base factor, each **HCC with its coefficient**, and two beats auditors love — *"hyperlipidemia
  documented but it **doesn't risk-adjust**, so we don't pretend it does; and if both diabetes-with- and
  -without-complications are coded, the **hierarchy suppresses** the lesser one — only the most severe in a
  family pays."* Expand **"Show RAF computation"** for the full audited math. *"The CMS-HCC mappings,
  hierarchies and coefficients are public CMS artifacts — curated V24 subset here, full annual model file in
  production. The capture is MEAT-grounded and cited, which is exactly what a RADV audit asks for."* The
  Evaluation Harness scores **RAF accuracy** for these cases.
- **Anesthesia units — payment math, not line-items** → open an **Anesthesia** chart (AN10001 lap chole).
  *"Anesthesia doesn't pay like CPT line-items: it's **(base + time + modifying units) × a conversion
  factor**. The model codes the anesthesia CPT, the diagnosis and the ASA physical-status modifier — and
  then the deterministic calculator takes over: base units from the public CMS file, time units from the
  **documented anesthesia start/stop** divided into 15-minute units — never estimated by the model — and
  the P3 modifier adds a unit under commercial convention (the trace honestly notes Medicare pays zero for
  it)."* Point at the **unit card**: base + time + modifying = total units × $/unit = estimated allowable.
  Expand **"Show unit calculation"** for the audited math. *"The conversion factor is admin-configurable —
  it varies by locality and payer."* The Evaluation Harness scores **units accuracy** for these cases.
- **Facility vs Professional (APC / OPPS) — two claims from one chart** → open **GI90003** (double scope at
  hospital outpatient). *"At a hospital outpatient department, the same chart produces TWO claims: the
  professional fee — the coded lines you see, both scopes — and the **facility fee under OPPS**. Every code
  carries a status indicator from CMS Addendum B, and the pricer applies the real payment logic: both scopes
  here are **comprehensive-APC (J1)**, so the facility gets **one session payment** — the colonoscopy's APC —
  and the EGD packages into it. Pro-fee pays both; facility pays once. That asymmetry is exactly what
  out-patient CDI teams manage."* Then open a **Radiology** chart: the pro-fee line carries **modifier 26**
  (the read), and the facility card shows the technical side — with the chest X-ray **conditionally packaged
  (Q1)** when a paying service is on the claim, or paid alone when it isn't. ED charts show the visit-level
  V-code APCs and **packaged add-ons** (99292). *"Status indicators, packaging, multiple-procedure
  discounting and C-APCs — Addendum B is public CMS data, curated subset here, full quarterly file in
  production. And note: the facility lens never changes clinical routing — it's a parallel payment view."*
  The Evaluation Harness scores **facility-estimate accuracy** for these cases.
- **Change Log** tab (Admin / Configuration) → *"And every one of these edits is itself governed."* Show
  the append-only trail: who (by role), when, what area, action, and target — for config, policy, KG,
  guideline, reference-data, and golden-set edits. *"Your audit and compliance teams asked who changed the
  rules — here it is, automatically."*
- **Evaluation Harness → Manage golden set** → *"The eval set is the product, so admins curate it."* Add /
  edit / delete an adjudicated gold case (chart + truth ICD/CPT + IRR). *"New truth cases onboard a
  specialty without engineering; the harness scores the live pipeline against exactly this set."*
- **RBAC by role** — use the **Role** dropdown to switch personas; the app reshapes per role:
  - **Admin** — full surface (Policy/KG, Integrations, Admin Config, everything).
  - **Coder** — Worklist / CDI / Dashboard only; **can** run coding, override, escalate; **cannot** see
    Admin, Policy/KG, or Integrations.
  - **QA Auditor** — Control Tower + override/reassign/rollback; cannot run autonomous coding (Worklist
    shows a **view-only** pill and **queued** rows instead of Run/Code buttons).
  - **CDI Specialist** — CDI queue + physician-response actions; coding actions are gated off.
  - **Supervisor** — Control Tower assignment + reassign/rollback; read across dashboards.
  *"Nav AND every action button respect the role — and in production this maps to your SSO groups and
  tenant scopes (US-region, no co-mingling)."* Switch back to **Admin** to finish.

## Close (30 sec)
*"Working today, not slideware. Radiology depth your coders will recognize, E&M and ED on the same
accelerator, every decision defensible, and it bounds itself when it can't be sure. And it's a
**platform** — your admins build the knowledge graph, tune the thresholds, and govern who can do what,
without calling us. The blueprint and a fast-timeline proposal are in your hands."*

---
### Fallbacks / gotchas
- If a chart routes to QA unexpectedly, open it — the **routing reason** explains exactly why (that's a
  feature; use it).
- If the learning transfer doesn't show on B, confirm A's override saved (Learning page) and that B is the
  same study type; re-click **Code** on B.
- Eval/run and run-all make real Claude calls (~20–25s/chart). Pre-run them once before the meeting if you
  want instant screens, or run live for authenticity.
