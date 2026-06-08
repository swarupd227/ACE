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

## Demo storyline (maps to the four mandatory scenarios)
1. **Worklist** → run autonomous coding → watch the **STB/QA/Manual** split.
2. **Scenario 1** (chest X-ray) → clean codes, cited, high 4-factor confidence → **STB**.
3. **Scenario 2** (CT abdomen+pelvis) → **bundling/NCCI** + modifier logic on the gates checklist.
4. **Scenario 3** (rule-out, normal film) → **avoids overcoding** pneumonia (specificity control).
5. **Scenario 4** (incomplete / interventional) → **eligibility → Manual** with reason.
6. **E&M** chart → MDM leveling, avoids overcoding diabetes complication.
7. **Override a code** → **Closed-Loop Learning** populates and shifts later similar charts.
8. **Knowledge Graph**, **Evaluation Harness**, **Audit packet**, **Dashboard** round out the story.

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
