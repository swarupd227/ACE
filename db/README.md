# ACE — Database DDL & Export

| File | What it is |
|------|------------|
| `schema.sql` | Schema-only DDL (all 32 tables, indexes, constraints, the `vector` extension) — no data |
| `ace_database_export.sql` | Full point-in-time export (schema **and** data, plain-SQL `COPY` format) |

Both are produced by `pg_dump` 16 from the running `pgvector/pgvector:pg16` container with
`--no-owner --no-privileges`, so they restore into any Postgres 16 database regardless of role names.

**Data provenance:** every row is synthetic, PHI-free demo data. Reference content is public CMS
material (ICD-10-CM, HCPCS, NCCI/MUE-modeled edits, MS-DRG, CMS-HCC, anesthesia base units,
Addendum-B subset); CPT rows are clearly-labeled demo placeholders (`source = DEMO_PLACEHOLDER`).
The export is a snapshot — the live database moves with every coding run.

## Restore

```bash
createdb -U <user> ace_restored
psql -U <user> -d ace_restored -v ON_ERROR_STOP=1 -f ace_database_export.sql
```

(Requires the `pgvector` extension to be installed — it is in the `pgvector/pgvector:pg16` image.
The dump itself runs `CREATE EXTENSION vector`.)

## Regenerate

```powershell
# schema-only DDL
docker compose exec -T db sh -c "pg_dump -U ace -d ace --schema-only --no-owner --no-privileges > /tmp/schema.sql"
docker cp veeheathtech-db-1:/tmp/schema.sql db/schema.sql

# full export (schema + data)
docker compose exec -T db sh -c "pg_dump -U ace -d ace --no-owner --no-privileges > /tmp/export.sql"
docker cp veeheathtech-db-1:/tmp/export.sql db/ace_database_export.sql
```

Note: copy the files out with `docker cp` (not PowerShell `>` redirection, which re-encodes
them with a BOM that `psql` rejects).

## Schema note

The application also applies additive, idempotent `ALTER TABLE … ADD COLUMN IF NOT EXISTS`
migrations at startup (`backend/app/seed/seeder.py: init_db`) for columns added after a database
was first created — `schema.sql` always reflects the post-migration state of the live database.
