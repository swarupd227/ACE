# ACE — Autonomous Coding Engine

**A self-contained, agentic medical-coding application — built by Nous Infosystems for Vee Healthtek.**

ACE turns clinical documentation into audit-defensible codes (ICD-10-CM / CPT / HCPCS + modifiers),
routes each chart into **Straight-Through Billing / QA / Manual** by a calibrated confidence score, and
proves every decision with a chart-line + guideline evidence chain. It is framed as the engine inside
Vee Healthtek's **RevAmp Coding Studio**.

> **Specialties in this build:** Radiology, E&M, ED, Pathology, Surgical, Cardiology — all running on one
> "specialty accelerator." New specialties onboard as content + config, not a rebuild.

> **Confidential.** Prepared for Vee Healthtek; not for redistribution. See [`LICENSE`](LICENSE).

---

## Quick start

```bash
cp .env.example .env          # then add your ANTHROPIC_API_KEY
docker compose up --build
```

- **UI:** http://localhost:8080
- **API:** http://localhost:8000/api/health · OpenAPI docs at http://localhost:8000/docs

The stack seeds its database automatically on first boot (reference codes, NCCI/MUE/modifiers, the
payer + ontology knowledge graph, guidelines, synthetic charts, and the golden eval set).

### The one secret
ACE makes **real Claude calls** for reasoning. Put a key in `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

The active model is then **changeable at runtime** in **Admin → Reasoning Model** (Anthropic or any
OpenAI-compatible endpoint — Azure OpenAI, OpenAI, vLLM, Ollama). API keys always stay in the
environment, never in the database or the UI. **If no model is reachable, ACE never fabricates codes** —
it routes every chart to the manual queue with reason `LLM_UNAVAILABLE`.

### Helper scripts (Windows PowerShell `.ps1` / macOS-Linux `.sh`)

| Task | PowerShell | bash |
|---|---|---|
| **Pristine demo** (wipe + rebuild + reseed + pre-code) | `.\scripts\reset-demo.ps1` | `./scripts/reset-demo.sh` |
| …reset without the slow pre-code | `.\scripts\reset-demo.ps1 -NoCode` | `./scripts/reset-demo.sh --no-code` |
| **Redeploy** after code changes (rebuild + force-recreate) | `.\scripts\redeploy.ps1` | `./scripts/redeploy.sh` |
| …just the frontend | `.\scripts\redeploy.ps1 web` | `./scripts/redeploy.sh web` |

> Plain `docker compose up -d` after a rebuild sometimes **doesn't recreate** a container, so the browser
> keeps serving the old build. `redeploy` uses `--force-recreate` and prints the served JS bundle hash.
> Always **hard-refresh** the browser (Ctrl+Shift+R).

---

## The pipeline (Stage 0–5)

| Stage | What it does | What it prevents |
|---|---|---|
| **0 · Eligibility** | required docs, approved specialty, exclusions (trauma, interventional, incomplete) | coding ineligible charts |
| **1 · Conditioning** | section ID, copy-forward / contradiction / unsigned flags, **chart summary** | reasoning on bad input |
| **2 · Extraction** | structured slots: laterality, contrast, view count, encounter type, negation | lost specificity |
| **RAG · Graph-RAG** | candidate codes from code sets + ontology graph + payer policy + learned corrections | ungrounded guesses |
| **3 · Cited coding** | every code cites chart lines + guideline; self-consistency on hard charts | fabricated / uncitable codes |
| **3b · Citation check** | each cited span verified against the chart | unsupported codes |
| **4 · Validation gates** | deterministic: existence, specificity, NCCI, MUE, modifiers, sex/age, payer necessity | compliance failures |
| **5 · Calibration & routing** | 4-factor calibrated confidence → STB / QA / Manual + bounded-autonomy hard rules | confident-but-wrong auto-billing |

**Grounding rule:** the coding agent may only emit codes that retrieval surfaces — so "don't hallucinate"
is a structural property, not a prompt we hope holds.

---

## What's in the app

**Operational screens** (tools you work in, not slideware):

- **Worklist** — the three-lane queue (STB / QA / Manual) by confidence.
- **Control Tower** — live work queues, SLA aging, and workforce assignment.
- **Encounter detail** — chart ↔ citation highlight, 4-factor confidence, validation gates, the Stage 0–5
  trace, the per-chart "knowledge used" panel, the audit packet, and human controls (accept /
  override-with-reason / reassign / escalate / **revert-to-AI**), all audit-logged.
- **CDI / Physician Queries** — the agent drafts compliant, non-leading queries; the answer re-codes the chart.
- **Closed-Loop Learning** — coder corrections become exemplars that shift later similar charts.
- **Evaluation Harness** — accuracy vs adjudicated consensus with the inter-rater-reliability ceiling;
  admins can curate the golden set.
- **Performance Dashboard** — STB rate, calibrated accuracy, manual-effort & TAT reduction, exception
  rate, and the maturity pathway.
- **Integrations & Ingestion** — simulated PMS/EHR connectors (FHIR/HL7/EDI/REST) + live ingest.

**Admin / configuration** (an operator runs the platform — no code, no redeploy):

- **Admin → Configuration** — routing thresholds, the 4-factor weights, self-consistency, bounded-autonomy
  rules, eligibility, SLA targets, the **Specialty Accelerator**, users & roster, **Connectors**, the
  **Reasoning Model** (provider/model/endpoint + a Test-connection button), and an append-only **Change Log**.
- **Policy & Knowledge Admin** — editable payer policies that drive the necessity gate, a **KG Builder**
  (add ontology concepts, map them to codes, draw relationships — read by Graph-RAG on the next run),
  editable **Coding Guidelines**, an interactive **Cytoscape** ontology graph, and **Reference Data**
  (code sets + NCCI / MUE / modifier edits that drive the gates).
- **Role-based access** — Admin / Coder / QA Auditor / CDI Specialist / Supervisor; both navigation and
  action buttons respect the role (maps to SSO in production).

**Agentic UX:** clicking **Code** (or "Watch agent re-run") opens a **live Agent Console** that streams
the run over Server-Sent Events — eligibility → conditioning/extraction → Graph-RAG → coding → validation
→ routing — with real model latency. The same console streams the CDI scan and the batch run.

---

## Data provenance (honest by design)

- **ICD-10-CM / HCPCS** — real public-domain subsets (CMS / NCHS).
- **CPT** — **DEMO placeholder** (real numbers, our own descriptors, *not* AMA text); swap in a licensed
  AMA distribution for production (same table shape).
- **NCCI / MUE** — modeled on real CMS edit logic (subset).
- **Ontology** — a demo concept set; production swaps in licensed SNOMED CT / UMLS at the same shape.
- **Charts** — synthetic and PHI-free. The pipeline genuinely codes them; no answers are pre-stored.

---

## Tech

FastAPI + SQLAlchemy 2 + PostgreSQL/pgvector · Anthropic Claude (or any OpenAI-compatible model) ·
React + TypeScript + Vite + Tailwind + Cytoscape · all via `docker compose`.

```
web (nginx + React)  ──/api──▶  api (FastAPI + agentic orchestrator)  ──▶  db (postgres + pgvector)
                                          │
                                          └─▶  Claude (default) or any OpenAI-compatible endpoint
```

Cloud target: **Azure + Azure AI Foundry**, US-region, multi-tenant.

---

## Repository layout

```
backend/      FastAPI app — pipeline/ (orchestrator, validation), knowledge/ (graph_rag),
              routes/, llm/ (client, prompts), seed/ (reference_data, charts), config_store.py
frontend/     React + TypeScript + Vite app (pages/, components/)
scripts/      reset-demo / redeploy helpers (.ps1 + .sh)
deck/         ACE_Architecture.pptx + ACE_demo.mp4 (+ build_deck.js to regenerate)
e2e/          Playwright end-to-end demo capture
docker-compose.yml
```

## Documentation

| Doc | What it is |
|---|---|
| [`DESIGN.md`](DESIGN.md) | Full design; SOW / Use-Case / transcript reconciliation; Azure/Foundry mapping |
| [`BLUEPRINT.md`](BLUEPRINT.md) | AI architecture & workflow blueprint, mapped to the running code |
| [`PROPOSAL.md`](PROPOSAL.md) | Outcome-based proposal and timeline |
| [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) | Step-by-step demo runbook |
| [`NOUS_VALUE_ADD.md`](NOUS_VALUE_ADD.md) | What's defensible / hard-to-replicate vs commodity |
| [`REQUIREMENTS_TRACEABILITY.md`](REQUIREMENTS_TRACEABILITY.md) | Use-Case + SOW requirements → where each is met |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Dev setup, conventions, and the specialty-accelerator recipe |
| [`deck/README.md`](deck/README.md) | How to regenerate the architecture deck and demo video |
