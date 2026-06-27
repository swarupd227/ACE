# Nous RCM Studio — Merge Plan (ACE + P2R → one app)

Concrete execution plan for converging the two apps. Supersedes the deferred Phase 7–8
of `RCM_FRAMEWORK_PLAN.md` with an implementable, increment-by-increment path.

**Guardrail (unchanged):** umbrella brand is **Nous RCM**; the client name never appears in
code, UI, commits, or docs. Both apps are Nous-owned IP.

## Target end-state

One **Nous RCM Studio**: one URL, one login/RBAC, shared `core/`, two modules — **Coding**
(ACE) and **Policy & Denials** (P2R) — with the closed loop (`policy → rule → code → denial
→ signal`) as a first-class flow.

## Increment status

| Phase | Outcome | Status |
|------|---------|--------|
| **A — Unified shell** | one React origin, module switcher, shared look | ✅ done (`studio/`) |
| **B — One gateway** | single port, `/coding` + `/policy` + `/*/api` proxy; kills port pain | ✅ done (`studio/gateway`) |
| C — ACE adopts `core/` | repoint ACE LLM/audit/eval/config to shared core, canary-gated | ⏳ next |
| D — Unified identity & RBAC | one role model, module-scoped perms, shared auth middleware | ⏳ |
| E — Backend topology | keep 2 services behind gateway **or** one FastAPI process | ⏳ (decision) |
| **F — Data convergence** | one Postgres cluster, `ace` + `p2r` databases, one volume | ✅ done (`studio/db-init`) |
| G — Closed loop as product | event contract; ACE gates subscribe; denials feed P2R mining | ⏳ future |

## A + B — what shipped

- New `studio/` stack: `docker compose -f studio/docker-compose.studio.yml -p studio up`.
- One nginx gateway serves landing + both SPAs and proxies `/coding/api/*`→ACE,
  `/policy/api/*`→P2R. See `studio/README.md`.
- The two frontends are reused **unchanged** except three env-driven knobs (base path,
  router basename, API base) + an env-gated module switcher. Standalone builds unaffected.
- `ACE_BASE_URL=http://ace-api:8000` inside the stack → "Publish to ACE" works over the
  compose network (no host-port juggling).

## C — ACE adopts shared `core/` (next, canary-gated)

ACE currently keeps its **own** copy of the LLM client (`backend/app/llm`), audit, eval, and
config; P2R already imports `core/`. Repoint ACE **module-by-module**, each verified by a
canary re-code that proves identical coding output before the change lands:

1. `core/llm_client` ← ACE's LLM client (structured output, prompt caching, honest fallback).
2. Shared audit ledger + eval-harness scaffold.
3. Shared config store.
Exit: both apps build on `core/`; ACE behavior provably unchanged.

## D — Unified identity & RBAC

Reconcile the two taxonomies into one module-scoped model:

| Coding (ACE) | Policy (P2R) | Unified role |
|---|---|---|
| Admin | Admin | **Admin** (both modules) |
| Supervisor | Reviewer | **Supervisor / Approver** |
| Coder | Rule Author | **Author / Coder** (module-scoped) |
| QA Auditor | Auditor | **Auditor** (read + sign-off) |
| CDI Specialist | — | **CDI** (coding only) |

One auth middleware in `core/` issues the role; each module filters its nav by the role's
module-scoped permissions. Single role selector in the shell.

## E — Backend topology decision

Both valid; the gateway makes it reversible:
- **Two services behind the gateway** (recommended) — clean separation, independent deploy.
- **One FastAPI process** mounting both routers under `/api/coding` and `/api/policy`.

## F — Data convergence

One Postgres cluster; schemas `coding`, `policy`, and shared `reference` / `tenant` /
`audit`. Migrate via `pg_dump`/restore into schemas; canary re-code + P2R replay after.

## G — Closed loop as product

Event contract so ACE gates **subscribe** to P2R-published policies (instead of static
seeding) and ACE denials/overrides **feed** P2R denial mining. The differentiated framework
story; scoped separately.

## Sequencing

A → B shipped together (the demo-able single app). C–F run post-demo with no deadline
pressure, each canary-gated so ACE/P2R behavior is provably preserved. G is a separate
product workstream.
