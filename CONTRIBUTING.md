# Contributing to ACE

Internal guide for working on the Autonomous Coding Engine.

## Local development

```bash
cp .env.example .env          # add ANTHROPIC_API_KEY
docker compose up --build     # UI :8080, API :8000
```

- After **backend or frontend** changes: `./scripts/redeploy.ps1` (or `.sh`) — rebuilds and
  **force-recreates** the containers, then prints the served bundle hash. Hard-refresh the browser.
- For a **pristine** demo (wipe DB, reseed, pre-code the worklist): `./scripts/reset-demo.ps1`.
  Add `-NoCode` / `--no-code` to skip the slow pre-coding step.

### Layout
- `backend/app/pipeline/` — the agentic orchestrator and the deterministic validation gates.
- `backend/app/knowledge/graph_rag.py` — retrieval/grounding (generic across specialties).
- `backend/app/llm/` — the model client (`client.py`) and prompts (`prompts.py`).
- `backend/app/config_store.py` — runtime, admin-editable config (the engine reads it per run).
- `backend/app/seed/` — `reference_data.py` (codes, edits, KG, guidelines) and `charts.py` (charts + golden set).
- `frontend/src/pages` + `frontend/src/components` — the UI.

## Conventions
- **Secrets** live only in `.env` (gitignored). Never commit keys, and never store them in the
  database or surface them in the UI.
- Keep the **honest fallback**: if the model is unavailable, route to a human — never fabricate codes.
- Anything an operator should be able to change at runtime belongs in **`config_store`** (and the Admin
  screen), not hard-coded. Reference content (codes / edits / KG / guidelines) belongs in **seed data**.
- User-facing copy should be **dynamic** where it reflects state (e.g. specialty lists come from
  `meta.specialties`, model names from `model_version`) — don't hard-code lists that can drift.

## Adding a specialty (the accelerator recipe — no engine changes)

A new specialty is **content + config**, never a pipeline change. Touch only these:

1. `backend/app/config_store.py` — add `{"name": "<Specialty>", "enabled": True, "hard": <bool>}` to `specialties`.
2. `backend/app/seed/reference_data.py` — add its **CPT/HCPCS** and **ICD-10** codes, any **MUE/NCCI**
   edits, **payer policies**, **ontology** concepts + edges, and a **guideline** chunk.
3. `backend/app/llm/prompts.py` — add a `SPECIALTY_GUIDANCE["<Specialty>"]` entry (content only; the
   lookup is a graceful `.get` default, not a gate).
4. `backend/app/seed/charts.py` — add a worklist chart or two and a couple of **golden cases**.
5. `./scripts/reset-demo.ps1` to reseed and pre-code.

The pipeline, retrieval, validation, routing, and orchestrator stay untouched — that's the point.
(Reference: the Cardiology commit.)

## Deck & demo video
See [`deck/README.md`](deck/README.md) to regenerate `ACE_Architecture.pptx` and `ACE_demo.mp4`.

## Git
- Work on a branch; open a PR into `master`.
- Keep commits scoped with a clear subject + body.
