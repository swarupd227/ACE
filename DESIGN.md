# Autonomous Medical Coding — Solution Design

**Project codename:** (TBD) · **Client:** Vee Healthtek · **Build partner:** Nous Infosystems
**Document status:** v0.3 — Nous spec + VHT SOW/Use-Case **+ client-call transcript (June 5) incorporated**. Living document.
**Author:** Engineering · **Last updated:** 2026-06-08
**⏰ HARD DEADLINE: in-person demo in Bangalore ~June 15–16, 2026 (~1 week out). See §16.**

> **Two source perspectives, reconciled (see §15):** the **Nous "Deep Domain" spec** defines *engineering
> depth* (5-stage pipeline, 7 hallucination controls, eval harness, defensibility). The **Vee Healthtek
> SOW + Use-Case** define the *acceptance criteria* (Radiology-first, STB, ≥90% accuracy, 3-lane routing,
> 4 mandatory scenarios, eligibility gate, learning loop). The app must pass VHT's acceptance criteria,
> built inside the Nous-grade architecture. **§15 is the authoritative requirements section.**

> This design turns the Nous "Demo Enhancement Specification · Deep Domain" into a concrete,
> buildable, self-contained Docker application: an **Agentic AI system that translates clinical
> documentation into defensible medical codes**. It is engineered to be *real in every sense* —
> a genuine five-stage agentic pipeline running against authoritative code sets, with no fabricated
> logic and no hardcoded "answers."

---

## 1. Context that shapes every decision

| Fact | Source | Why it matters for the build |
|---|---|---|
| TA Associates took a **majority stake in Vee Healthtek ($250M, Nov 2024)** | [PR Newswire](https://www.prnewswire.com/news-releases/vee-healthtek-joins-ta-associates-portfolio-with-strategic-growth-investment-302309977.html) | The buyer is PE-backed. The dominant lens is **defensibility + measurable ROI**, not "cool AI." |
| **Nous Infosystems is also a TA Associates portfolio company** | [TA news](https://www.ta.com/news/ta-announces-strategic-investment-in-nous-infosystems-to-support-continued-growth-and-innovation/) | This is a **portfolio-synergy build**, not a cold sale. TA is in the room to see two of its companies create value together. |
| Vee Healthtek: ~**5,000 employees**, ~**$100M FY25 revenue**, RCM + HIM + risk adjustment, AAPC/AHIMA-certified coders, HIPAA-regulated, large US hospital & payer clients | [Vee Healthtek](https://www.veehealthtek.com/), [Becker's](https://www.beckershospitalreview.com/healthcare-information-technology/vee-healthtek-enters-new-strategic-partnership-aims-for-healthcare-innovation/) | The audience are **expert coders + an incoming CTO**. Domain accuracy must survive a coding director's quiz; architecture must survive a CTO's scrutiny. |
| Nous: digital product engineering, AI on Microsoft/Azure, global delivery (US/UK/DE/CA/RS/IN) | [Nous](https://www.nousinfosystems.com/) | Azure is a natural target cloud; the demo must be cloud-portable but **self-contained for the call**. |

**Audience-driven priorities** (from the spec's own audience list):
1. **Coding & HIM leadership** → domain accuracy must be real and inspectable.
2. **Incoming CTO** → architecture depth, calibration, eval rigor must be real.
3. **Nous build team** → this doc is the implementation reference.
4. **TA Associates** → "we understand the actual problem, not the marketing version."

---

## 2. Scope & terminology

### 2.1 "Medical Coding **Translation**"
The user brief says *Translation*; the source spec says *Autonomous Coding*. These are the same core
task viewed from one angle: **translating unstructured clinical narrative into the standardized code
languages of billing** (ICD-10-CM/PCS, CPT, HCPCS Level II) — plus modifiers, sequencing, and DRG.
We treat "translation" as the end-to-end act of rendering a chart into an audit-defensible coded claim.

> ⚠️ **Open question for the call/transcript:** confirm whether "translation" also means **code-set
> crosswalking** (e.g., ICD-9↔ICD-10, ICD-10↔SNOMED, CMS-HCC v24↔v28). If yes, we add a dedicated
> Crosswalk agent + GEMs/SNOMED maps. Default assumption for now: narrative→code translation.

### 2.2 What we are building *now*
A **self-contained Docker application** that is a *faithful, working implementation* of the spec —
not a slideware demo. It runs the real five-stage agentic pipeline on charts, computes real codes,
fires real validation gates, produces real audit packets, and shows real evaluation metrics. It is
the **demo of the production system**, built so the same codebase grows into the production system.

### 2.3 What is explicitly out of scope for the Docker demo
- Live EHR integration (Epic/Oracle Health) — we **simulate** the integration surface (FHIR-shaped
  ingest, InBasket-style query routing) so it is swappable later, but no real EHR connection.
- Real PHI. We use **synthetic-but-clinically-realistic charts** (see §4.1). Synthetic *input* is not
  fake *logic* — the pipeline genuinely codes them; nothing is pre-answered.
- Production payer contracts. We ship a representative payer-policy table, structured to be replaced
  by the real ingestion pipeline.

---

## 3. The "real, no shortcuts" principle — and the data reality

The brief demands no fake logic and no hardcoded data. In medical coding that demand collides with
**code-set licensing**, so we name it honestly here and design around it.

| Asset | Licensing reality | How we handle it (self-contained) |
|---|---|---|
| **ICD-10-CM / ICD-10-PCS** (codes + descriptions) | Public domain (CMS/NCHS), annual files | **Bundle full current + prior year**, effective-dated. Real. |
| **ICD-10-CM Official Guidelines** | Public domain (CMS/NCHS) | **Bundle full text, indexed** for RAG + citation verification. Real. |
| **HCPCS Level II** | Public domain (CMS), quarterly | Bundle. Real. |
| **NCCI PTP edits + MUE** | Public (CMS), quarterly | Bundle as deterministic gate tables. Real. |
| **LCD / NCD** | Public (CMS Medicare Coverage Database) | Bundle a representative jurisdiction subset, effective-dated. Real. |
| **CPT codes + descriptors** | **AMA copyright — license required** | ⚠️ Cannot freely redistribute. **Demo options below.** |
| **AHA Coding Clinic / AMA CPT Assistant** | Copyright/subscription | ⚠️ Cannot bundle. Citation-verification corpus is **ICD-10 Guidelines + NCCI manual (public)** for the demo; pluggable for licensed sources in prod. |
| **Patient charts** | PHI / privacy | **Synthetic generation** (§4.1). Real pipeline, safe input. |

**CPT handling — recommended default for the demo:** lead specialty demos with **Radiology and
HCC/E&M** framed via ICD-10 + HCPCS where possible, and represent CPT with a **small, internally
authored placeholder code table** (clearly labeled, structurally identical to the real AMA table) so
the *pipeline and gates are genuinely exercised* without redistributing AMA IP. The architecture
reads CPT from a provider interface; dropping in a licensed AMA distribution in production is a config
change, not a code change. **This is the one place "real" is bounded by law, and we say so out loud —
which itself lands well with a compliance-minded buyer.**

> Decision needed (see §13): does the client want us to (a) ship the AMA-placeholder approach, or
> (b) operate against their existing AMA CPT license inside the container at runtime?

**LLM reality:** the reasoning agents make **real Anthropic Claude API calls** (Sonnet for most
specialties, Opus for hard ones — inpatient/surgical, per spec §3). "Self-contained" therefore means
*one secret* — an API key — injected at runtime. We also design a **local-model fallback** (e.g., a
quantized clinical model via vLLM/Ollama) for a fully air-gapped run, with an explicit quality caveat.
Default: Claude API. (See §13 decision.)

---

## 4. Agentic architecture

The spec's five stages map cleanly onto an **agentic system**: an **Orchestrator** drives a chart
through specialized **agents** (LLM-reasoning) and deterministic **tools/engines** (rule-based gates),
where any stage can **veto or downgrade confidence**, and failures trigger a **bounded re-reasoning
loop** before routing to a human. This is the core "agentic" claim, made concrete.

```
                         ┌──────────────────────────────────────────────────────────┐
                         │                    ORCHESTRATOR                            │
                         │  (LangGraph-style state machine; per-chart run record,     │
                         │   veto/downgrade, bounded re-reasoning, routing decision)  │
                         └──────────────────────────────────────────────────────────┘
   chart in ──►  [1] Conditioning Agent ──► [2] Extraction Agent ──► [3] Coding Agent ──► [4] Validation Engine ──► [5] Calibration & Routing ──► out
                  (LLM + classifiers)        (LLM, structured)        (LLM, cited,         (DETERMINISTIC rules:    (temperature scaling +
                  section ID, OCR fix,       diagnoses/procedures/    schema-bound JSON,    code-existence, NCCI,    isotonic regression;
                  copy-forward, contradiction, meds/devices, negation, every code carries   MUE, LCD/NCD, modifier,  multi-axis confidence;
                  addendum, signature        temporal, E&M MDM        chart + guideline     sex/age, POS, sequencing) per-specialty thresholds;
                  detection                  indicators              citations)            ↺ re-reason on fail      auto-code vs human queue)
                                                                          │                                              │
                                                                          ▼                                              ▼
                                                                 Citation Verifier                              CDI / Physician-Query Agent
                                                                 (text + guideline grounding)                  (drafts compliant, non-leading
                                                                          │                                     queries when docs insufficient)
                                                                          ▼
                                                                 Self-Consistency (N-sample
                                                                 agreement on hard encounters)

   Cross-cutting, always-on:
     • Audit Ledger (append-only evidence chain: chart, citations, guideline refs, model version, confidences, gate logs, reviewer actions)
     • Evaluation Harness (frozen golden sets, per-specialty metrics, calibration fitting, adversarial set, drift detection)
     • Reference Data Service (effective-dated code sets, NCCI/MUE, LCD/NCD, payer policy)
```

### 4.1 Stage 1 — Document Conditioning Agent
- **Section identification** (HPI/ROS/PE/MDM/A&P) — LLM classifier with rules fallback.
- **OCR-artifact repair** — clinical-vocabulary-aware correction pass.
- **Copy-forward detection** — diff current note against prior encounters (n-gram/embedding overlap);
  flag verbatim carry-over so it cannot drive *this* encounter's codes.
- **Addendum + timestamp** parsing; **signature/attestation** verification; **contradiction
  detection** (physician vs nurse, HPI vs A&P, current vs prior).
- **Output:** a normalized, sectioned chart + a list of conditioning flags (each is demo-visible and
  audit-logged). *This is the spec's highest-credibility, most-skipped-by-competitors stage — we make
  it visible.*
- **Synthetic chart generator** lives here as a dev/eval tool: produces realistic notes per specialty
  *with injected defects* (copy-forward, contradiction, missing signature, ambiguity) — these become
  both demo charts and adversarial eval cases. The generator never emits the "right code"; truth for
  golden sets comes from independent coding (§7).

### 4.2 Stage 2 — Clinical Entity Extraction Agent
Structured slot-filling (not free-text strings), per spec §3.1:
- Diagnoses with **laterality, encounter type (initial/subsequent/sequela), acuity, manifestation,
  complication**.
- Procedures with **route, approach, site, bilaterality, multiple-procedure indicators**.
- Medications (dose/route/indication → drug-disease alignment, J-codes), devices/implants/supplies
  (HCPCS L2), E&M MDM indicators (problems × data × risk).
- **Negation & uncertainty** ("rule out" ≠ confirmed), **temporal** ("history of" → Z-codes vs active).
- Optional: biomedical NER model (scispaCy/medspaCy) as a second extractor for cross-check.

### 4.3 Stage 3 — Code Candidate Generation Agent (the core)
- **Schema-bound structured output** (Claude tool-use / JSON schema). Every candidate code **must**
  populate two citation arrays — `chart_citations` (section + line range + exact text) and
  `guideline_citations` (source + section + text). **Empty citations ⇒ candidate rejected before
  Stage 4.** This is the single most important architectural control.
- Multi-axis self-reported confidence (existence/specificity/compliance) captured as *features*, not
  verdicts.
- Model tiering: Sonnet default; **Opus for inpatient med-surg & complex surgical**.

### 4.4 Stage 3.5 — Citation Verifier + Self-Consistency (hallucination controls)
- **Citation verification:** confirm cited chart text actually exists at the cited location; confirm
  guideline citations against the indexed guideline corpus. Failure ⇒ re-reason or human.
- **Self-consistency:** on hard encounters, run N samples at non-zero temperature; require agreement;
  disagreement ⇒ human regardless of confidence.
- Implements spec §5 controls 2,3,5; controls 1,4 live in Stages 3–4; control 6 (adversarial) in the
  eval harness; control 7 (bounded autonomy) in Stage 5.

### 4.5 Stage 4 — Validation & Compliance Engine (DETERMINISTIC)
Rule-based, not LLM (LLMs are bad at exhaustive lookups). Ten gates from spec §3.1:
code-existence (effective-dated) · specificity (more-specific child?) · modifier validity · **NCCI
PTP** · **MUE** · **LCD/NCD** medical-necessity · payer-policy · sex/age edits · POS alignment ·
**UHDDS sequencing** (inpatient). Every gate emits pass/fail **with the gate name logged**; a failure
routes to bounded re-reasoning (Stage 3 with the failure as context) or to the human queue. No silent
drops.

### 4.6 Stage 5 — Confidence Calibration & Routing
- **Calibration** fitted per specialty on a held-out set: temperature scaling (uniform) + isotonic
  regression (non-uniform). Calibrated confidence — not raw model output — drives routing.
- **Multi-axis** routing (a chart can be high code-confidence / low modifier-confidence).
- **Per-specialty, per-customer thresholds** tuned to maximize *auto-coded share* under accuracy
  floors (spec's real production trade-off, §2.3).
- **Bounded-autonomy hard rules** (always human, regardless of confidence): DRG > $X; recent denial
  same patient/payer; NCCI bundle-break; recent payer policy change; critical-care codes; HCC above
  threshold; within ICD-10 October damping window.

### 4.7 Cross-cutting agents/services
- **CDI / Physician-Query Agent:** when docs don't support a warranted code, drafts a **compliant,
  non-leading** query (presents options, allows "unable to determine"); routes to a simulated CDI
  inbox; response updates the encounter.
- **Audit/Defense-Packet generator:** assembles the full evidence chain for any historical claim.
- **Evaluation Harness** (§7) and **Drift Monitor** — first-class, not bolt-ons. "The eval harness is
  the product" (spec §6).

---

## 5. Data model (Postgres + pgvector)

Core tables (illustrative):
- `encounters` (id, patient ref, dos, specialty, payer, POS, status, source_chart)
- `chart_documents` (sectioned text, conditioning_flags jsonb, signatures, addenda)
- `entities` (encounter_id, type, structured slots jsonb)
- `code_candidates` (encounter_id, code_system, code, axis confidences, chart_citations jsonb,
  guideline_citations jsonb, verified bool, gate_results jsonb, status)
- `coded_claims` (final accepted set, sequencing, modifiers, DRG, routing_decision, reviewer_id)
- `audit_ledger` (append-only; run_id, stage, model_version, prompt_hash, inputs/outputs, timestamps)
- **Reference (effective-dated):** `icd10cm`, `icd10pcs`, `hcpcs`, `cpt` (placeholder/licensed),
  `ncci_ptp`, `mue`, `lcd_ncd`, `payer_policy`, `hcc_model` (v24/v28), `guideline_chunks` (+ vector).
- **Eval:** `golden_sets`, `golden_cases`, `eval_runs`, `eval_metrics`, `adversarial_cases`,
  `drift_observations`.

Append-only audit ledger + effective-dated reference data are what make **re-coding** and **RAC
defense** genuine rather than cosmetic.

---

## 6. UI — world-class, 14-screen flow

**Stack:** React + TypeScript + Vite, Tailwind + shadcn/ui, TanStack Query, Recharts/visx, Framer
Motion for the pipeline animation. Design language: clean clinical, dense-but-legible, accessible
(WCAG AA), keyboard-first for coders.

Screens map to spec §8.7 (the 14-screen upgraded flow):
1. **Worklist landing** — the coder's real queue (volume, specialty, priority).
2. **Five-stage pipeline architecture** — the opening reframe (live, not a static diagram).
3. **Trigger autonomous run** — fire the batch; show throughput.
4. **Worklist after run + auto-coded share** — the economic headline.
5. **Chart viewer with live citations** — click a code, the supporting chart lines highlight.
6. **Validation-gates checklist** — 10 gates, pass/fail per candidate.
7. **ED encounter — modifier-25 / critical-care reasoning** — specialty depth.
8. **Hallucination-controls case study (sepsis)** — all 7 controls firing; the restructured wow.
9. **CDI / physician-query workflow** — the "co-pilot, not replacement" moment.
10. **Coder accepts/edits recommendation** — human-in-the-loop.
11. **Audit ledger / defense packet** — the compliance-officer closer; exportable.
12. **Productivity dashboard** — operational metrics.
13. **Evaluation harness + drift detection** — proof the numbers are honest.
14. **Code-set update handling + denial-trend** — operational discipline.

**Priority-keep order if the demo slot is short** (spec): screens **2, 5, 8, 11**.

The chart viewer ↔ citation highlight interaction is the signature UI moment: it makes
*defensibility* tangible in one gesture.

---

## 7. Evaluation harness (the moat)

- **Frozen golden sets** per specialty (synthetic for the demo; the *process* is real): each case
  independently coded by a coding routine **+ at least one independent pass**, disagreements
  adjudicated; truth = post-adjudication set; ambiguous cases flagged "never auto-code."
- **Metrics per specialty:** code-existence accuracy, top-1, top-3, specificity match, modifier
  accuracy, **DRG match (inpatient)**, citation validity, **ECE (calibration error)**, **auto-coded
  share at threshold**, adversarial pass rate.
- **IRR as the honest ceiling** — we report "X% vs post-adjudication consensus where IRR = Y%," never
  "X% vs truth."
- **Continuous eval:** shadow-mode comparison view; weekly golden-set regression (>1pp flag); drift
  observations; per-payer denial monitoring (simulated feed).

---

## 8. Tech stack

| Layer | Choice | Rationale |
|---|---|---|
| Frontend | React + TS + Vite, Tailwind + shadcn/ui | World-class UI fast; strong a11y; great for dense clinical views |
| API | **FastAPI (Python)** | First-class for clinical NLP/ML libs, schema validation (Pydantic), async |
| Agent orchestration | **LangGraph** (state machine) over Anthropic SDK | Explicit graph = veto/downgrade/re-reason loop is inspectable & testable |
| LLM | **Anthropic Claude** (Sonnet default, Opus for hard) + local fallback | Real reasoning; tiering per spec; offline option for air-gapped runs |
| Deterministic gates | Pure Python rule engine over reference tables | LLMs are bad at exhaustive lookups; rules are right here |
| Clinical NLP | medspaCy/scispaCy (optional cross-check) | Second extractor; negation/temporal |
| Data | **PostgreSQL + pgvector** | Relational gates + RAG vectors in one engine; simple to containerize |
| Async/jobs | Redis + a worker (RQ/Celery) | Batch coding runs, drift jobs |
| Reference loaders | Python ETL into effective-dated tables | Bundle public CMS data at image build |
| Packaging | **docker-compose** (web, api, worker, db, redis) | Single `docker compose up`; one secret (API key) |

---

## 9. Self-contained Docker packaging

```
docker-compose.yml
  ├── web      (nginx serving built React app)
  ├── api      (FastAPI + LangGraph orchestrator)
  ├── worker   (batch coding, eval, drift jobs)
  ├── db       (postgres + pgvector; reference data seeded at init)
  └── redis    (queues)
```
- **`docker compose up`** brings up the whole demo. Reference code sets + guideline index + synthetic
  charts + golden sets are **seeded at build/first-run** (idempotent migration + loader).
- **One secret:** `ANTHROPIC_API_KEY` via `.env`. With `LLM_MODE=local`, no external calls (quality
  caveat shown in UI).
- Deterministic, reproducible: pinned deps, pinned code-set versions (effective-dated), seeded RNG for
  synthetic generation so demos are repeatable.

---

## 10. Build phases (for the application, distinct from the 12-month client engagement in spec §9)

- **Phase A — Skeleton & spine (foundation):** docker-compose up green; Postgres + reference loaders
  (ICD-10-CM, HCPCS, NCCI, MUE, ICD-10 Guidelines index); FastAPI + LangGraph orchestrator shell;
  audit ledger from day one; React shell + worklist (screens 1, 4).
- **Phase B — The pipeline, end to end (one specialty: Radiology):** all five stages live; citation +
  verification; deterministic gates; calibration scaffold; chart viewer with citation highlight
  (screens 2, 3, 5, 6).
- **Phase C — Hallucination controls + specialty depth:** self-consistency; bounded autonomy;
  ED + E&M; sepsis case study (screens 7, 8); CDI query agent (screen 9).
- **Phase D — Defensibility + honesty:** audit/defense packet export; eval harness + drift; code-set
  update handling; denial trend (screens 10–14).
- **Phase E — Polish:** motion, empty/error states, performance, demo script & seeded scenarios.

> We do **not** start Phase A until the transcript + extra docs land and §13 decisions are made.

---

## 11. Security, compliance, defensibility (baked in, not bolted on)
- HIPAA-shaped from the start even on synthetic data: PHI-safe logging, role-based access (coder /
  CDI / compliance / admin), full audit trail, encryption at rest/in transit.
- **Defensibility principle (spec):** if we can't defend a decision to an auditor with the evidence
  chain in front of us, the system shouldn't have made it. The audit ledger + citation chain enforce
  this structurally.
- Re-coding capability (same chart + same model version ⇒ re-derivable decision) for audit + model
  improvement.

---

## 12. Risks & mitigations
| Risk | Mitigation |
|---|---|
| CPT/Coding Clinic licensing limits "realness" | Placeholder tables structurally identical to licensed; pluggable; **stated openly** to a compliance buyer |
| LLM hallucination undermines trust | Seven layered controls; citations are gates not garnish; deterministic validation; bounded autonomy |
| "Self-contained" vs real LLM | Default Claude API (one secret) + documented local fallback |
| Synthetic charts seen as "fake" | Frame clearly: real pipeline, safe input; generator injects realistic defects; truth via independent adjudication |
| Demo overruns 20-min slot | Priority screens 2/5/8/11; feature-flag the rest |

---

## 13. Decisions — status after SOW/Use-Case
1. ~~**"Translation" semantics**~~ → **RESOLVED (assumed).** No client doc says "translation"; all say
   "Autonomous Medical Coding." Treat as **narrative→code**. Crosswalking not in scope unless raised.
2. ~~**LLM mode**~~ → **RESOLVED: Claude API + local fallback.** Real Claude (Sonnet default, Opus for
   hard cases) via `ANTHROPIC_API_KEY`; offline local-model flag for air-gapped runs. For production,
   keep the endpoint configurable (Azure OpenAI/Bedrock/Anthropic-in-VPC) to fit VHT's SOC2/HITRUST VPC.
3. ~~**CPT**~~ → **RESOLVED: labeled placeholder CPT table** (radiology 70000-series), structurally
   identical to AMA's and clearly labeled; licensed AMA distribution swaps in for production. See §15.6.
4. ~~**Lead specialty**~~ → **RESOLVED: Radiology first** (X-ray/CT/MRI; **Interventional Radiology
   excluded**). Engagement specialties after: Orthopedics, ED, Outpatient Surgical.
5. ~~**Hosting target**~~ → **RESOLVED (transcript): Azure + Azure AI Foundry, US-region mandatory,
   multi-tenant with strict no-co-mingling.** Production models via Foundry (Azure OpenAI confirmed;
   Anthropic-via-Foundry TBC). **Demo:** self-contained Docker, frontier model (Claude) — explicitly
   endorsed for the demo since VHT's own TSMs aren't demo-ready. See §16.

---

## 14. Pending inputs
- [ ] Client call **transcript** (incoming) — will refine priorities and the remaining §13 decisions (LLM mode, CPT, hosting).
- [x] Additional client **documentation** — **received & incorporated in §15**: SOW for AI Partner V2,
  Specialty Use-Case Requirements for Auto Coding V2, Vee Healthtek Overview.
- [ ] Still needed from client: payer mix for the pilot customer, sample (de-identified) radiology
  report formats, target STB ramp curve, and which EHR the pilot site uses.

*Append answers here as they arrive; this document is the single source of truth for the build.*

---

## 15. Vee Healthtek SOW & Use-Case — Authoritative Requirements & Reconciliation

> This section is derived directly from the three client documents (SOW for AI Partner V2; Specialty
> Use-Case Requirements for Auto Coding V2; Vee Healthtek Overview, Apr 2026). **Where it differs from
> the generic Nous playbook flow, this section wins** for the demo we are building.

### 15.1 Who is in the room (tailor the demo to them)
From the Overview leadership page — the technical/clinical validators are likely:
- **Dr. Muthu Krishnan — Chief Digital Technology Officer** (ex Athenahealth, IKS Health, Conifer):
  the "incoming CTO"-style tech-depth validator. Architecture, model governance, calibration, security.
- **Michelle Castillon — Chief Product Transformation Officer** (ex Conifer, Tenet): product/workflow fit.
- **Matt Michaels — CEO**; **Dr. Gauri Puri — Chief Business & Strategy** (outcome/commercials).
VHT operates at scale and with heavy credibility: **32M coding charts/yr, 95% current coding accuracy,
100% AAPC/AHIMA/IAO-certified coders, 7 of 20 best US health systems, SOC 2 Type II + HITRUST, ISO
27001/9001, HIPAA.** Implication: the audience are **expert coders** — the radiology coding must be
*correct*, and the system must look like *their* QA program, not a generic AI demo.

### 15.2 Strategic framing: we are the "Autonomize" stage of *their own* roadmap
The Overview lays out VHT's maturity model: **Stabilize → Scale → Autonomize**, where Autonomize =
"agentic workflows + control tower + policy library; humans handle the hard 15–20%." Their platform is
**RevAmp**, and their re-engineered coding step is a **"Coding Studio" that suggests ICD/CPT, previews
DRG/APC, links evidence.** They already brand agentic AI internally (case study: agent **"Emily"** cut
eligibility denials 26%). **Frame our app as the autonomous coding engine inside RevAmp's Coding Studio**
— not a standalone tool. The Docker app should visually echo this (RevAmp-style integration surface,
control-tower/guardrails language).

### 15.3 The KPI model the client actually uses (supersedes "auto-coded share" wording)
| KPI | Client target (SOW §5 / Use-Case §6) | How we instrument it |
|---|---|---|
| **Straight-Through Billing (STB) rate** | Progressive ramp; **automation maturity pathway to ≥80%** | = share of charts cleared High-confidence with all gates passing, no human touch |
| **Coding accuracy (chart level)** | **≥90%** with continuous improvement | measured vs adjudicated golden set; report IRR ceiling alongside |
| **Manual effort reduction** | **≥30%** | coder-minutes saved = STB charts × avg manual time |
| **Turnaround time (TAT)** | **10–15% improvement** | per-chart latency tracked, before/after |
| **Exception resolution** | SLA-based turnaround | routed-case clock in the worklist |
> **Note:** the Nous spec's per-specialty 88–96% targets still guide *internal* tuning, but the
> **contractual headline is a flat ≥90% chart-level floor + an STB ramp to ≥80%.** UI shows both.
> **VHT governance:** VHT does **100% audit during initial rollout** and **certifies the model only when
> quality ≥95%.** Build the QA/audit workflow assuming a human auditor reviews everything early, tapering
> as certification is earned — this is the demo's credibility spine.

### 15.4 The 3-lane confidence routing (client-mandated, primary workflow)
This replaces the generic routing visual as the **center of the demo** (Use-Case §3.3, Step 3):
- **High confidence → STB lane** (straight-through to billing, no human touch)
- **Medium confidence → QA review lane** (auditor verifies)
- **Low confidence / exception → Manual coder lane** (full human coding, with reason flagged)
Our richer controls (bounded-autonomy hard rules, self-consistency disagreement, gate failures,
eligibility failures) are the **forces that demote a chart out of STB** into QA or Manual.

### 15.5 Stage 0 — Auto-Coding Eligibility Gate (NEW; client-required, runs before the pipeline)
SOW §2.2C: **only charts meeting all eligibility criteria may enter auto-coding.** Checks:
required documentation present (report/images as applicable) · approved specialty & procedure type ·
valid or retro-eligible authorization · no exclusion flags (experimental, **trauma**, incomplete
encounter; **Interventional Radiology excluded**). **Failing charts auto-route to the Manual Coding
Queue with a reason code.** → Add this as **Stage 0** ahead of Document Conditioning in §4's pipeline.
It is also Demo Scenario 4 (exception handling).

### 15.6 Radiology-first clinical scope & coding specifics
- **In scope:** diagnostic **X-ray, CT, MRI**; structured *and* unstructured radiology reports.
  **Excluded:** Interventional Radiology.
- Radiology coding levers our Stage-2/3 must nail (also the demo scenarios): **modality + contrast**
  (w/ vs w/o vs w&w/o), **view counts** (e.g., "3 views L knee"), **anatomic region/laterality**,
  **multi-procedure bundling** (CT abdomen + pelvis → 74178 family; NCCI/MUE), **professional vs
  technical component (modifier 26 / TC)**, linkage of **CPT to the ordering diagnosis**.
- **CPT reality (decision #3):** radiology is CPT-heavy (70000-series), so the AMA-licensing question is
  now front-and-center. For the demo, recommend the labeled placeholder CPT table (structurally real,
  swap-in licensed AMA in prod) **or** loading VHT's AMA license into the container. Flag explicitly.

### 15.7 Coding output structure (SOW §2.2A) — refines the data model in §5
- **Diagnoses:** Principal, Primary, Secondary (ICD-10-CM).
- **Procedures:** Primary CPT, Secondary CPTs, **Modifiers**, **Assistant Surgeon**, **POS**.
- **Confidence score per code** + (SOW §2.2E) **linked evidence snippet, source-document reference,
  rule justification, confidence explanation** — every decision **versioned & replayable**.

### 15.8 Accuracy/confidence source model (SOW §2.3B) — make these four factors explicit & visible
Confidence shown on each auto-coded ICD/CPT is composed from:
1. **Clinical-document match strength** (citation/grounding quality)
2. **Historical coding patterns** (similar past charts / master-coder gold set)
3. **Rule-engine validations** (LCD/NCD, NCCI/CCI, modifier checks)
4. **AI model certainty** (calibrated)
→ Our Stage 5 calibration must **expose these four sub-scores** behind the single confidence number
(a hover/expand in the UI). This is exactly the explainability VHT asks for.

### 15.9 Closed-loop learning (Use-Case §3.4 & Step 5) — must be demonstrated live
Capture coder corrections, log overrides, feed retraining; the demo must **show feedback impact
(model improvement)**. For the Docker app: a **correction → captured override → "applied learning"**
view that visibly changes a subsequent similar chart's recommendation/confidence (real mechanism:
correction stored as a few-shot/gold exemplar + per-pattern rule, re-run shows the shift — not a faked
number).

### 15.10 The four mandatory demo scenarios = our acceptance tests (Use-Case §5)
Build the seed radiology charts and the demo storyline around exactly these:
| # | Scenario | Input | Required outcome |
|---|---|---|---|
| 1 | **Standard radiology** | single procedure (e.g., chest X-ray) | accurate code(s) + **STB-eligible** |
| 2 | **Multi-procedure** | CT abdomen + pelvis | correct **bundling / multiple-CPT** + **modifier logic** |
| 3 | **Complex diagnosis mapping** | narrative-heavy report | correct **ICD-10 extraction**, **avoid overcoding** |
| 4 | **Exception handling** | missing/ambiguous documentation | **routed to coder**, **reason flagged** (ties to Stage 0) |
These map cleanly onto our hallucination controls (Scenario 3 = specificity-inflation / overcoding
control; Scenario 4 = eligibility + bounded autonomy).

### 15.11 Integration & interoperability surface (SOW §2.2D, Use-Case §7.1)
Production: integrate with **EHR (Epic/Cerner/eClinicalWorks), RCM/RevAmp, clearinghouses/billing**
via **HL7/FHIR, EDI/X12, APIs, batch**. Demo: **simulate** this with a FHIR-shaped ingest endpoint +
a batch radiology-report loader, structured so the real connectors drop in later. "Simulated or real
PMS/EHR connectivity" is explicitly acceptable for the demo (Use-Case §7.1).

### 15.12 Refocused demo flow for the Docker app (radiology STB storyline)
Reconciles the Nous 14-screen flow (§6) with the client's required steps & scenarios:
1. **Radiology worklist** (the coder's queue; volume, TAT clock)
2. **5-stage pipeline + Stage 0 eligibility** architecture (the bounded-pipeline reframe)
3. **Run autonomous coding** on a batch → **3-lane split (STB / QA / Manual)** with STB% + accuracy
4. **Scenario 1** — standard chest X-ray: codes + citations + 4-factor confidence → **STB**
5. **Scenario 2** — CT abdomen+pelvis: bundling/NCCI/MUE + modifier logic → validation-gates checklist
6. **Scenario 3** — narrative-heavy: correct ICD-10, **overcoding blocked** (specificity control)
7. **Scenario 4** — missing/ambiguous: **eligibility/exception → Manual queue, reason flagged**
8. **Coder review & correction** (human-in-the-loop; edits captured/logged)
9. **Closed-loop learning** — correction changes a later similar chart (feedback impact)
10. **Audit / evidence-replay packet** (versioned, replayable decision — compliance closer)
11. **Dashboards** — accuracy, STB rate, exception rate, manual-effort reduction, TAT
12. **Evaluation harness + drift** (how ≥90% is proven; path to ≥80% maturity & VHT 95% certification)
> Priority-keep if time is short: **2, 3, 5, 7, 10** (pipeline, STB split, gates, exception routing, audit).

### 15.13 Net changes to the build vs §§3–12
- **Add Stage 0 (eligibility)** ahead of the pipeline.
- **Promote the 3-lane STB/QA/Manual routing** to the primary workflow visual.
- **Reframe** around **STB rate** + flat **≥90%** accuracy + **≥80% maturity** KPIs.
- **Expose the 4-factor confidence** breakdown in the UI.
- **Add the closed-loop learning** demonstration.
- **Radiology-only** seed data, golden set, and gates for v1 (CPT 70000-series, NCCI/MUE, modifier 26/TC,
  contrast/view-count logic).
- **Frame as a module of RevAmp's Coding Studio**, with a simulated EHR/FHIR integration surface.

---

## 16. Client Call Transcript (June 5, 2026) — Decisions & New Requirements (LATEST, authoritative)

> Source: "Vee Healthtek–Nous Meeting" transcript. Where this conflicts with earlier sections,
> **this wins.** It also confirms the relationship: **Nous = build partner, Vee Healthtek = client,
> TA Associates = common investor** (Ritej Bachhawat, TA, on the call pushing speed).

### 16.1 The deadline and the deliverables
- **In-person demo in Bangalore ~June 15–16, 2026** (Michelle + Murali travelling). ~1 week out. **Speed
  is an explicit, repeated requirement** (Ritej/TA: "aggressive timeline… competitive field… do it fast").
- Commercial direction: **outcome-based, fixed SOW, tight timeline.** Referenced Nous's prior experience
  with **Medicodio** as the comparable.
- We owe VHT, beyond the demo: **(a) our AI blueprint/architecture** (Amrish explicitly asked for the
  workflow, models, embeddings, graphs we'll use — they're aligning their own blueprint to it),
  **(b) the demo app, (c) the proposal with aggressive timelines.**

### 16.2 The people who decide (tailor to them)
- **Amrish (Ambarish) Kumar — Chief Technology & AI Officer, *newly joined*** (ex Cerner/Oracle Health,
  ex Elevance Health AI lead). **THE technical decision-maker** = the "incoming CTO" the Nous spec wrote
  for. His asks are requirements (16.4).
- **Michelle Castillon — Chief Product Transformation Officer** — sponsor & point of contact.
- **Muralidhar "Murali" Padmanabharao — Operations** — outcomes, domain SME support offer.
- **Jonathan Cachat (JC) — lead data scientist**; **Baliga — IT (India)**; **Rajesh — mid-cycle product
  lead**; **Rituja — product**. Nous side: Neil (CTO), Pratik (AI Practice Head), Karen (AI architect),
  Lavanya (delivery), Tarun (sales solution), Sandhya (healthcare SME), Rachel (client partner).

### 16.3 Scope — refined (supersedes "radiology-only")
- **Multi-specialty from the pilot**, built as a **"specialty accelerator"** (Amrish): specialized/small
  models + config that deploy across specialties with **minimum per-client customization**.
- Specialties: **Radiology** (anchor — "commoditized, quick to prove, high accuracy") **+ E&M + ED**
  (highest volume) + possibly **Pathology**. *Demo:* anchor on **Radiology**, **show a 2nd specialty
  (E&M)** to prove the accelerator is multi-specialty. Breadth < depth-of-approach for the demo.
- **3–5 pilot clients**, but TA wants to **cover the full set of clients that already grant data access**
  (esp. a recent acquisition with full coding-data access → candidate for 100% flow). Data access today:
  **Practice Admin (VHT's own PMS, 30+ clients), eClinicalWorks, Cerner (~15 clients).** → these are the
  **integration targets** (simulate for the demo).
- **The demo can be simulated/synthesized**; integrations simulated; **synthetic data is fine** (Nous to
  supply its own). Primary objective Michelle/Murali/Amrish stated: **show the approach, the full
  workflow, the architecture, and explainability** — *how we build/develop/deploy*, not breadth.

### 16.4 New technical requirements (mostly Amrish) — fold into §4/§5/§6
1. **Knowledge graph + Graph/agentic RAG** over **payer policy guidelines (Anthem, Cigna, …) + medical
   necessity guidelines + medical ontologies.** He explicitly tied **medical ontologies to hallucination
   reduction**. → Upgrade §4's "RAG over guidelines" to **Graph RAG / agentic RAG**: a **payer↔policy↔
   code knowledge graph** + ontology grounding (SNOMED/ICD/RxNorm/LOINC-style), correlated to specialty.
   Payer rules are **not structured today — must be curated** (per-client "port-in").
2. **Chart summarization** presented to the coder (new output).
3. **Color-coded confidence scoring** in the UI, plus the **4-factor breakdown** (§15.8), plus
   **observability/monitoring/traceability** of the AI scoring.
4. **Human-in-the-loop coder workspace**: rationale/explainability, summarization, ICD/CPT/modifier with
   **choose/update/override + capture reason**, acceptance, confidence — built **inside the RevAmp
   ecosystem** (can be a separate app accessed through it; integrate with their worklist/inventory mgmt).
5. **Feedback/retraining = batch first (24–48h window)**, real-time later. ML-Ops pipeline must **flag
   invalid/junk codes** from AI output.
6. **Fine-tuning + distillation to SLMs** for latency/cost/lower-hallucination is desired (the "specialty
   accelerator"). Multi-tenant, **no client-data co-mingling**; per-client port-in for coding
   history/preferences and payer-KG rules.
7. **Azure + Azure AI Foundry**, **US-region servers mandatory**, BA agreements via MS EA. Frontier model
   for the demo (Claude). Their own **TSMs are not demo-ready** — do not use them in the demo.
8. **Progressive accuracy**, not a hard 90% floor at go-live: start low, ramp to **≥90% accuracy /
   ≥80% STB** (supersedes the "flat ≥90% floor" framing in §15.3). The "90% SLA" in the SOW is **coding
   accuracy, not availability** (clarified live).

### 16.5 VHT's current state (so we position, not duplicate)
- Platform **RevAmp** = RCM ecosystem (UI, worklist, inventory mgmt). Internal coding tool **RevCap** =
  autonomous-coding *principles* but **HCC/risk-based**, not agentic, not general. ~**"20% down the path"**
  — mostly strategy/infrastructure; data-science team started on use cases.
- **Existing clinical-NLP coding pipeline** (JC), built ~2 yrs ago, **not in production/cloud**:
  segment notes → demographics → **MEAT + SOAP** extraction → flow identifier (labs/radiology/notes) →
  diagnosis prediction **(BioBERT)** → **MedSpaCy** evidence collection → internal **ICD-10 mapping**
  (CDC dictionary) → **Qwen LLM** validates ICD-10 vs diagnosis, returns top-3 + final pick.
  **MedGemma** (open-source) also used. **Claimed 90%+ accuracy.** **No RAG/embeddings/agentic
  validation/knowledge graph** on the coding side (KG only planned for the **denials** side).
- They published a **TSM (task-specific models)** blog; Nous endorses the specialized-model approach
  (off-shelf or fine-tuned for accuracy + control).
- Azure AI Foundry recently CISO-approved for limited POCs (PHI previously blocked foundation models).

### 16.6 Net additional changes to the build (on top of §15.13)
- Add a **Graph RAG / payer-policy + ontology knowledge-graph** subsystem (Amrish's #1 ask; also a
  hallucination control). Curate a representative payer-policy + ontology slice for the demo.
- Add **chart summarization** to the coder workspace and pipeline outputs.
- Add **color-coded confidence** + observability/traceability views; keep the 4-factor breakdown.
- Add **override-with-reason capture** + **batch (24–48h) feedback loop** + **invalid/junk-code flagging**.
- Reframe as a **specialty accelerator**: specialty config + per-client port-in; demo **Radiology + E&M**.
- Architecture narrative = **Azure + Foundry, US-region, multi-tenant isolation**; demo stays
  self-contained Docker (Claude frontier + local fallback), with the production mapping shown.
- Integration surface simulates **Practice Admin, eClinicalWorks, Cerner** (+ RevAmp worklist).
- Reframe KPIs to **progressive ramp → ≥90% accuracy / ≥80% STB**, with the early **100%-audit →
  95%-certification** governance (§15.3) as the trust story.

### 16.7 Recommended demo scope for ~June 15 (aggressive but credible)
Given ~1 week, build a **real, working, self-contained Docker app** that nails *approach + workflow +
architecture + explainability* on **Radiology (anchor) + one E&M case**, with simulated integration:
- **Must-have:** Stage 0–5 pipeline running live on synthetic charts; 3-lane STB/QA/Manual routing;
  citations + chart summarization; **color-coded 4-factor confidence**; validation gates (NCCI/MUE/
  modifier/LCD-NCD) for radiology; coder workspace with override+reason; audit/replay packet;
  dashboard (accuracy, STB%, exceptions, TAT); the **4 mandatory radiology scenarios** (§15.10).
- **High-value:** Graph-RAG/payer-KG view (even a curated slice) — directly answers Amrish; closed-loop
  learning (correction → improves a later chart); the architecture/"specialty accelerator" screen;
  E&M second-specialty case to prove multi-specialty.
- **Narrative overlays (no heavy build):** Azure/Foundry production-mapping screen; US-region/
  multi-tenant isolation note; batch-feedback + ML-Ops invalid-code flagging shown in the learning view.
- **Out of scope for the demo:** real EHR connectivity, real payer-policy ingestion at scale, fine-tune/
  distillation pipeline (describe in the blueprint, don't build).

### 16.7.1 LOCKED build scope (user, 2026-06-08)
- **Specialties:** Radiology (anchor, 4 scenarios) **+ E&M** (proves the specialty accelerator).
- **Graph-RAG / payer-policy + ontology knowledge graph:** **build a working slice** (visible in UI).
- **Kickoff:** build now. Stack: FastAPI + Postgres/pgvector + Anthropic Claude (local fallback) backend;
  React + TS + Vite + Tailwind + shadcn frontend; `docker compose up` self-contained.

### 16.8 Still owed by the client (chase via Michelle)
Daily chart volumes per in-scope client; final in-scope client/platform list; any specific coding
standards/data constraints beyond the docs; confirmation of Anthropic-via-Foundry availability.
