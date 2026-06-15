# `p2r/` — Policy-to-Rule Intelligence platform (Nous RCM Framework)

P2R turns payer-policy changes and pooled denial evidence into validated, engine-ready
rules. It is the **rule-supply** half of the Nous RCM Framework; **ACE** is the
claim-time coding half. P2R's output (validated policies/rules) is exactly what ACE
consumes at its validation gates.

## Isolation guarantees (why this never touches the ACE/Vee demo)

- **Separate stack.** Own compose file (`docker-compose.p2r.yml`), own Postgres, own
  ports (API on host **8100**, not 8000/8080). Containers run under the **`p2r`** compose
  project — never the `veeheathtech` project. ACE's `docker-compose.yml`, `backend/`,
  and `frontend/` are never modified by P2R work.
- **One-way dependency.** `p2r → core` only. P2R never imports from `ace`, and `ace`
  never imports from `p2r`. ACE is downstream of nothing, so it is structurally immune.
- **Shared reuse via `core/`.** P2R imports the proven primitives (LLM client, IR, …)
  from `core/`. ACE keeps its own in-place copy until it adopts `core/` after the demo.

See `RCM_FRAMEWORK_PLAN.md` (repo root) for the full phased plan. This is the Phase 0/1
skeleton: it boots in isolation and proves the `p2r → core` reuse path.

## Run (isolated, alongside ACE)

```bash
docker compose -f p2r/docker-compose.p2r.yml -p p2r up --build -d
curl http://localhost:8100/health
curl http://localhost:8100/meta
```
