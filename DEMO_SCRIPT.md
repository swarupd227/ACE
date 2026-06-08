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

## 0.7 Integrations & Ingestion (1 min) — `Integrations & Ingestion`
- Show connected source systems (Practice Admin / eCW / Cerner) + channels (FHIR R4 / HL7 v2 / EDI 837 /
  SFTP / REST). **Load a sample report → Ingest into queue → it appears live in the Worklist.**
- Message: *"Charts arrive from the EHR/PMS; the connectors are simulated, the ingest is real."*

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
2. Click **Scan for CDI opportunities** → ACE drafts a **compliant, non-leading** query: states the
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
  Graph** tab shows the payer/ontology graph (click a node); **Data Sources** shows provenance. On any
  encounter, the **"Knowledge used for this chart"** panel proves which facts shaped *that* decision.
- `Evaluation Harness` → click **Run evaluation** → per-specialty accuracy **vs adjudicated consensus
  with the IRR ceiling**. *"We never claim to beat the laws of inter-coder agreement; we report honestly."*
- `Performance Dashboard` → STB rate, calibrated accuracy, **manual-effort reduction**, **coding TAT
  reduction** (manual baseline → AI-assisted), **exception rate**, and the **automation-maturity pathway**
  (current position vs the ≥80% target); note the **100%-audit → 95%-certification** governance ramp.

## Close (30 sec)
*"Working today, not slideware. Radiology depth your coders will recognize, E&M and ED on the same
accelerator, every decision defensible, and it bounds itself when it can't be sure. The blueprint and a
fast-timeline proposal are in your hands."*

---
### Fallbacks / gotchas
- If a chart routes to QA unexpectedly, open it — the **routing reason** explains exactly why (that's a
  feature; use it).
- If the learning transfer doesn't show on B, confirm A's override saved (Learning page) and that B is the
  same study type; re-click **Code** on B.
- Eval/run and run-all make real Claude calls (~20–25s/chart). Pre-run them once before the meeting if you
  want instant screens, or run live for authenticity.
