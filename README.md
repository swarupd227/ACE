# ACE — Autonomous Coding Engine

**A self-contained, agentic medical-coding demo built for Vee Healthtek (by Nous Infosystems).**
ACE translates clinical documentation into audit-defensible codes (ICD-10-CM / CPT / HCPCS + modifiers),
routes each chart into **Straight-Through Billing / QA / Manual** by calibrated confidence, and proves
every decision with a chart-line + guideline evidence chain. Framed as the engine inside **RevAmp's
Coding Studio**.

> Specialties in this build: **Radiology** (anchor) + **E&M**. See `DESIGN.md` for the full design,
> the SOW/Use-Case/transcript reconciliation, and the production (Azure/Foundry) mapping.

## Quick start

```bash
cp .env.example .env          # then add your ANTHROPIC_API_KEY
docker compose up --build
```

- UI:  http://localhost:8080
- API: http://localhost:8000/api/health  ·  docs at http://localhost:8000/docs

The stack seeds its database (reference codes, NCCI/MUE, payer + ontology knowledge graph, guidelines,
synthetic charts, golden set) automatically on first boot.

### The one secret
ACE makes **real Claude calls** for reasoning. Put a key in `.env`:
```
LLM_MODE=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```
Air-gapped alternative: `LLM_MODE=local` pointing `LOCAL_LLM_BASE_URL` at an OpenAI-compatible server
(e.g. Ollama). **If no LLM is reachable, ACE never fabricates codes** — it routes every chart to the
manual queue with reason `LLM_UNAVAILABLE`.

## The five-stage (plus Stage 0) pipeline
| Stage | What it does | What it prevents |
|---|---|---|
| 0 · Eligibility | required docs, approved specialty/procedure, exclusions (trauma, interventional, incomplete) | coding ineligible charts |
| 1 · Conditioning | section ID, copy-forward/contradiction/unsigned flags, **chart summary** | reasoning on bad input |
| 2 · Extraction | structured slots: laterality, contrast, view count, encounter type, negation, temporality | lost specificity |
| 3 · Cited coding | Graph-RAG-grounded; every code must cite chart lines + guideline; self-consistency on hard charts | fabricated / uncitable codes |
| 4 · Validation gates | deterministic: existence, specificity, NCCI, MUE, modifiers, sex/age, payer necessity | compliance failures |
| 5 · Calibration & routing | 4-factor calibrated confidence → STB/QA/Manual + bounded-autonomy rules | confident wrong answers |

## Demo storyline (see DEMO_SCRIPT.md for the full runbook)
1. **Control Tower** → the manager's live operating view: work queues (STB/QA/Manual/Escalated/CDI), SLA aging, and workforce assignment.
2. **Worklist** → run autonomous coding → watch the **STB/QA/Manual** split.
3. **Scenario 1** (chest X-ray) → clean codes (71046-26), cited, high 4-factor confidence → **STB**.
4. **Scenario 2** (CT abdomen+pelvis) → single **74177** (bundling/NCCI) + modifier logic on the gates checklist.
5. **Scenario 3** (rule-out, normal film) → **avoids overcoding** pneumonia (specificity control).
6. **Scenario 4** (incomplete / interventional) → **eligibility → Manual** with reason.
7. **ED** → standard visit + **critical care → QA via bounded autonomy**; **E&M** → MDM leveling.
8. **CDI / Physician Queries** → scan the anemia chart → compliant query → physician answer **re-codes** D64.9 → D50.9.
9. **Override a code** → **Closed-Loop Learning** populates and shifts later similar charts.
10. **Policy & Knowledge Admin** (edit a payer policy → it drives the necessity gate), **Evaluation Harness**, **Audit packet**, **Dashboard** round out the story.

Specialties: **Radiology, E&M, ED, Pathology, Surgical**. Screens (operational tools, not slideware):
Worklist · **Control Tower** (queues + SLA + assignment) · CDI · Dashboard (STB, accuracy, manual-effort
& TAT reduction, exception rate, maturity pathway) · **Policy & Knowledge Admin** (editable, drives
coding) · **Integrations & Ingestion** (simulated EHR connectors + live ingest + REST/batch) · Evaluation
Harness · Closed-Loop Learning (apply/withdraw exemplars) · Encounter detail. Traceability to the
Use-Case acceptance criteria is in `REQUIREMENTS_TRACEABILITY.md`. **Agentic UX:** clicking **Code**
(or "Watch agent re-run") opens a **live Agent Console** that streams the run over **SSE** —
eligibility → conditioning/extraction agent → Graph-RAG → coding agent → validation gates → routing,
with real LLM latency. The same live console streams the **CDI scan** (agent reasoning) and the **batch
run** (per-chart progress). The Policy & Knowledge Admin **Explore Graph** tab is an **interactive
Cytoscape force-directed ontology graph** (fcose layout, search, zoom, drag, click-to-inspect) in the
style of Microsoft's Ontology-Playground. Human controls: accept / override-with-reason / **reassign** / **escalate** /
**revert-to-AI (rollback)** — all audit-logged. The architecture/pipeline is shown **per-chart** (Stage 0–5
trace), not as a standalone diagram.

## Data provenance (honest by design)
- **ICD-10-CM / HCPCS** — real public-domain subsets (CMS/NCHS).
- **CPT** — **DEMO placeholder** (real 70000-series numbers, our own descriptors, *not* AMA text);
  swap in a licensed AMA distribution for production (same table shape).
- **NCCI/MUE** — modeled on real CMS edit logic (subset).
- **Charts** — synthetic, PHI-free. The pipeline genuinely codes them; no answers are pre-stored.

## Tech
FastAPI + SQLAlchemy + Postgres/pgvector · Anthropic Claude (local fallback) ·
React + TypeScript + Vite + Tailwind · all via `docker compose`.

## Architecture
```
web (nginx + React)  ──/api──▶  api (FastAPI + orchestrator)  ──▶  db (postgres + pgvector)
                                         │
                                         └─▶ Claude (frontier) or local LLM
```
