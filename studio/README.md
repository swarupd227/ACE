# Nous RCM Studio — unified app

One origin, one gateway, **one shared database**, both modules behind it:

- **Coding** (ACE) at `/coding/`
- **Policy & Denials** (P2R) at `/policy/`
- a landing module-chooser at `/`

This is the **merge** of the two previously separate apps into a single product, done
**without** rewriting either frontend. Each app is built unchanged except for three
env-driven knobs (base path, router basename, API base) and an env-gated module switcher
in its sidebar. The standalone stacks (`docker-compose.yml`, `p2r/...`) still work exactly
as before — this stack sits alongside them.

## Architecture (Phase A + B + F)

```
                         http://localhost:8200
                                  │
                        ┌─────────▼──────────┐   one nginx, one origin
                        │   studio-gateway   │
                        │  /        landing  │
                        │  /coding/ → ACE SPA│
                        │  /policy/ → P2R SPA│
                        └───┬────────────┬───┘
            /coding/api/*   │            │   /policy/api/*
                  ┌─────────▼──┐    ┌────▼─────────┐
                  │  ace-api   │    │   p2r-api    │── ACE_BASE_URL=http://ace-api:8000
                  └─────┬──────┘    └──────┬───────┘   (closed loop: Publish to ACE)
                        │  one cluster     │
                    ┌───▼──────────────────▼───┐
                    │           db             │   Phase F: single Postgres,
                    │  database ace │ database p2r│  one volume (studio_pgdata)
                    └──────────────────────────┘
```

- **Phase F:** one Postgres instance hosts both logical databases (`ace`, `p2r`) on a single
  volume. The `db-init/` script creates the `p2r` database (and pgvector in both) on first
  boot. No more drift between separate DB stacks.
- Single published port (`8200`); everything else talks over the compose network, so it
  **coexists with all other local stacks with no port conflicts**.
- The `/policy/api` → P2R → `ace-api` path means **"Publish to ACE" works inside the stack**.

## Run

```bash
docker compose -f studio/docker-compose.studio.yml -p studio up --build -d
# → http://localhost:8200
```

Override the host port if 8200 is taken:

```bash
STUDIO_PORT=8300 docker compose -f studio/docker-compose.studio.yml -p studio up --build -d
```

Stop / reset:

```bash
docker compose -p studio down            # stop
docker compose -p studio down -v         # stop + wipe the shared DB (re-seed on next up)
```

## What changed in the two apps (all reversible, default-safe)

| File | Change | Standalone default |
|---|---|---|
| `frontend/vite.config.ts`, `p2r/frontend/vite.config.ts` | `base: process.env.VITE_BASE_PATH \|\| "/"` | `/` |
| `frontend/src/main.tsx`, `p2r/frontend/src/main.tsx` | `BrowserRouter basename={VITE_ROUTER_BASE \|\| "/"}` | `/` |
| `*/components/Layout.tsx` | module switcher shown only when `VITE_STUDIO === "1"` | hidden |

The gateway image sets those env vars at build time (`/coding/`, `/policy/`). Run standalone
and nothing changes.

## Seeding the Coding worklist with prior coded state

A fresh stack seeds charts in `NEW` status (STB reads 0 until coded). To inherit an existing
coded worklist without re-running the LLM, clone an existing ACE database into the shared
cluster's `ace` database:

```bash
docker compose -p studio stop ace-api
docker exec <source-ace-db> pg_dump -U ace -d ace --clean --if-exists -f /tmp/ace.sql
docker cp <source-ace-db>:/tmp/ace.sql ./ace.sql && docker cp ./ace.sql studio-db-1:/tmp/ace.sql
docker exec studio-db-1 psql -U ace -d ace -f /tmp/ace.sql
docker compose -p studio start ace-api
```

## Roadmap beyond this round

Deeper convergence — ACE adopting the shared `core/` (Phase C), unified RBAC (Phase D), and
the first-class closed loop (Phase G) — is in `../MERGE_PLAN.md`.
