# Nous RCM Intelligence Framework — Phased Plan (ACE + P2R)

**Status:** draft for internal review · **Audience:** Nous Product Engineering, Data & AI
**Scope:** how the Policy-to-Rule (P2R) platform is built alongside the existing
Autonomous Coding Engine (ACE) so that (a) the ACE/Vee demo is never impacted, (b) P2R
is demonstrable on its own and can show a live glimpse of its output feeding ACE, and
(c) the two converge into one Nous RCM framework over time.

> Both ACE and P2R are **Nous-owned solution frameworks**. Client requirements informed
> each, but the solution design and IP are ours, so they share one repository and one
> roadmap. Client names are deliberately omitted from this document.

---

## Objectives (ranked)

1. **ACE / Vee demo is never impacted by P2R work.** Critical, non-negotiable.
2. **P2R is demonstrable from the platform**, including a live, opt-in glimpse of a
   validated P2R output flowing into ACE — without disturbing the scripted ACE demo.
3. **P2R reuses ACE components** wherever sensible, so future integration is mechanical,
   not a rewrite.

## The one rule that makes all three co-exist

**The dependency arrow points P2R → ACE, and never back.** ACE's code, containers, and
database depend on nothing from P2R. P2R may consume shared components and may push data
into ACE *only through ACE's public API, on demand*. Because ACE is downstream of nothing,
P2R can be built, broken, and redeployed freely and the ACE demo is **structurally** safe.

## Standing guardrails (apply to every phase)

- **Separate runtime:** P2R has its own `docker-compose`, its own Postgres, its own ports
  (`p2r-*` containers, never `veeheathtech-*`). ACE's stack is never recreated by P2R work.
- **Shared `core/` is append-only / backward-compatible** while the ACE demo is live; any
  change is verified by an ACE canary re-code before it lands.
- **Synthetic / public-CMS data only**; no real data from any client; per-tenant isolation
  in the data model; unresolved cases route to a human; everything cited. (Same honesty
  contract ACE already runs on.)
- **No client names** in code, commits, UI, or docs; target rule engines referred to
  generically; real engine artifact formats are clearly-labeled placeholders until confirmed.

---

## Phase 0 — Foundations & contracts  *(no ACE impact)*

**Goal:** lock the three contracts that are expensive to retrofit, and stand up empty
scaffolding. Build separately, converge cheaply.

- Define the **canonical Intermediate Representation (IR)**: codes, payer policies,
  provisions, rules, edits — all schema-validated objects carrying citations, provenance
  (model/prompt/source-hash), effective dating, and confidence.
- Define the **event contract** for the closed loop: `policy → rule → code → denial → signal`.
- Define the **tenancy model**: tenant scoping + a consented, de-identified analytics
  projection.
- Create `core/` (empty) and `p2r/` (skeleton with its own compose); write the one-way
  dependency rule and the guardrails into `p2r/README`.

**ACE safety:** documentation + new empty dirs only. **Exit:** contracts reviewed; skeleton
boots in isolation. **Effort:** ~0.5–1 day.

## Phase 1 — Shared core extraction  *(no ACE impact)*

**Goal:** real reuse from day one without touching ACE.

- Move the stable, proven primitives into `core/`: LLM client (structured output + prompt
  caching + honest fallback), audit ledger, eval-harness scaffold, config store, Graph-RAG
  retriever, SSE agent console, React workbench shell.
- **P2R imports `core/` immediately.** **ACE keeps running on its own in-place copy** and
  is *not* repointed yet.

**ACE safety:** ACE imports nothing new; its files are untouched. **Exit:** P2R builds
against `core/`; ACE canary chart still codes identically. **Effort:** ~1 day.

## Phase 2 — P2R Phase 1: Policy Intelligence Ingestion  *(demo slice)*

**Goal:** payer policy → structured, cited `PolicyProvision` records + change deltas.

- Document intake reusing ACE's OCR/vision + upload path; the LCD/MCD ingestion already
  designed for ACE, productionized.
- Two-pass, schema-bound extraction with mandatory citations and the confidence ladder
  (auto-load ≥ high / verification queue / hold), reusing ACE's extraction pattern.
- Curated public-CMS source set; MDM-style provision store with effective dating.

**ACE safety:** all in `p2r/`. **Exit:** a real policy doc ingests → cited provisions +
deltas, visible in the P2R workbench. **Effort:** ~2–3 days.

## Phase 3 — P2R Phase 3: Validation & Reconciliation  *(the showpiece)*

**Goal:** the explainable-autonomy beat the client cares about most.

- A **Validator Judge** that takes a candidate rule, retrieves governing provisions
  (hybrid RAG), and emits **NET-NEW / UPDATE / DUPLICATE / CONFLICT** with a cited rationale
  — reusing ACE's cited-reasoning + adversarial-verify machinery.
- Reconciliation against a (read-only, curated) sample rule library.

**ACE safety:** all in `p2r/`. **Exit:** a candidate rule produces a cited verdict with
rationale in the workbench review queue. **Effort:** ~3–4 days.

## Phase 4 — P2R Phase 4: Rule Authoring & Productionization  *(demo slice)*

**Goal:** approved recommendation → engine-ready artifact, honestly.

- LLM drafts into the schema-validated **Rule IR**; a **deterministic compiler** emits a
  clearly-labeled placeholder engine format (swapped for the real spec once confirmed).
- **Replay test harness** over a golden claim corpus — ACE's eval harness reused.
- Promotion workflow with human sign-off; full audit lineage.

**ACE safety:** all in `p2r/`. **Exit:** approve → compile → replay → "ready to promote",
all traced. **Effort:** ~2–3 days.

## Phase 5 — Integration glimpse: "Publish to ACE"  *(careful, opt-in)*

**Goal:** show the closed loop live without disturbing the scripted ACE demo.

- In the P2R workbench, an approved policy/rule has a **"Publish to ACE"** action that calls
  **ACE's existing public policy API** (the mechanism we already proved with the live
  Medicare-policy edit → re-code → gate change).
- Targets a **dedicated sandbox tenant/chart tagged `P2R-INTEGRATION`**, outside the
  scripted ACE flow. Optional belt-and-braces: run the teaser against a second, throwaway
  ACE instance on a copy DB.

**ACE safety:** write-only via public API, on explicit click, against a sandbox tenant; the
scripted demo charts/lanes never change. **Exit:** publish in P2R → re-code the sandbox
chart in ACE → gate reflects the P2R-authored policy. **Effort:** ~1 day.

## Phase 6 — P2R demo packaging  *(client-facing)*

**Goal:** a clean P2R demo that doubles as a requirements-clarification session.

- Workbench polish (shared design system → looks like one platform), a P2R demo script,
  a golden-set eval, and a deck/flow chart in the ACE collateral style.
- **Deliberately surface the client's open decisions** on screen (cloud, MDM product, exact
  engine artifact format) as "confirm here" prompts — the demo drives discovery.

**ACE safety:** P2R-only. **Exit:** end-to-end P2R walkthrough rehearsed; ACE glimpse beat
included. **Effort:** ~2 days.

---

## Phase 7 — Convergence  *(after the ACE/Vee demo)*

**Goal:** ACE and P2R formally become two apps on one Nous RCM platform.

- **Repoint ACE at `core/`** (the flip the fork-then-extract path was designed for),
  verified module-by-module with canary re-codes.
- Consolidate duplicated config/audit/eval into the shared core; one workbench shell.

**Why now and not earlier:** done without demo-deadline pressure, with tests. **Exit:** both
apps run on `core/`; ACE behavior unchanged.

## Phase 8 — Full closed-loop integration & productionization  *(future)*

**Goal:** the differentiated framework story.

- Event-bus integration: P2R's MDM **publishes** validated policies/rules; ACE's gates and
  knowledge graph **subscribe** instead of being seeded statically.
- The loop runs end-to-end: ACE denials/overrides become P2R denial signals.
- Add **P2R Phase 2 (denial pattern discovery)** — statistics-first mining (changepoint,
  FP-growth, FDR); the most net-new, least-ACE-reuse module, scoped here.
- Cloud-native hardening (AKS/IaC/blue-green), durable orchestration, tenant management,
  SLM-distillation path for unit cost.

---

## Sequencing summary

| Phase | Outcome | ACE impact | Window |
|------|---------|-----------|--------|
| 0 | Contracts (IR/event/tenancy) + skeleton | none | now |
| 1 | Shared `core/`; P2R imports it | none (ACE on own copy) | now |
| 2 | P2R policy ingestion | none | now |
| 3 | P2R validation/reconciliation (showpiece) | none | now |
| 4 | P2R rule authoring + replay | none | now |
| 5 | "Publish to ACE" sandbox glimpse | sandbox tenant only | now |
| 6 | P2R demo packaged for the client | none | now |
| 7 | ACE adopts `core/` — convergence | deliberate, post-demo | after Vee demo |
| 8 | Closed-loop integration + denial mining + prod | platform-level | future |

**Critical-path for the client demo:** Phases 0 → 1 → 2 → 3 → 5 → 6 (Phase 4 can trail if
time-boxed). Everything through Phase 6 is **zero-impact** on the ACE/Vee demo by construction.
