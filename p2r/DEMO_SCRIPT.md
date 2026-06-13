# P2R — Policy-to-Rule Intelligence · Demo Script

A ~15-minute walkthrough of the P2R workbench that **doubles as a requirements-clarification
session**. P2R turns payer policies (and, in the roadmap, 835 denials) into validated,
reconciled, human-approved **rules** — and shows those rules feeding the downstream coding
engine. Throughout, the slides marked **▶ Confirm here** are open decisions to settle live
with the client.

> **Ground rules for the room**
> - All data is **synthetic and PHI-free**. The sample payer ("Meridian Health Plan") and its
>   policy are invented for the demo.
> - Do **not** name the client in the product, the repo, or the conversation artifacts.
> - The downstream coding engine ("ACE") runs **untouched**; the integration is write-only,
>   on an explicit click, against a sandbox payer.

---

## 0. Pre-flight (before the client walks in)

```powershell
# 1) Bring up the isolated P2R stack (its own DB, API :8100, web :8180 — never ACE's ports).
docker compose -f p2r/docker-compose.p2r.yml -p p2r up --build -d

# 2) (For the integration beat) make sure the coding engine is up too.
docker compose -f docker-compose.yml up -d

# 3) Confirm the model has credit — open the workbench; the sidebar should show the model id
#    in green and "ACE linked".
```

- **Workbench:** http://localhost:8180
- **API (if asked):** http://localhost:8100 · health at `/health`, contract at `/docs`
- Reset to a clean state (throwaway DB): `docker compose -f p2r/docker-compose.p2r.yml -p p2r down -v` then `up`.

---

## 1. The problem (30 seconds, no screen)

> "Every payer publishes policies — coverage criteria, prior-auth lists, frequency limits,
> modifier and bundling rules — and they change constantly. Today, turning those documents
> into the rules your coding/edits engine enforces is **manual, slow, and uncited**. When a
> policy changes, nobody is sure which existing rule it touches. P2R closes that gap."

---

## 2. Policy Workbench — extraction with citations (3 min)

1. Open **Policy Workbench**. Click **Ingest sample policy**. (Or **Paste a policy** to drop in
   any synthetic policy text live — good if they want to "try their own".)
2. Select the document on the left. The right pane shows the **extracted provisions**, each with:
   - a **provision type** (COVERAGE / PRIOR_AUTH / FREQUENCY / MODIFIER / DOCUMENTATION / BUNDLING),
   - the **codes** it governs (CPT/ICD/modifiers),
   - a **confidence bar** and a **routing decision** (AUTO_LOAD ≥ 0.90 / VERIFY ≥ 0.70 / HOLD),
   - **line-anchored citations** back to the source text.

> **Talking point:** "The model *reads and proposes*; deterministic checks decide. Confidence
> is composite — the model's own estimate, a code-format validator, and a citation check that
> actually re-reads the cited lines. An extraction we can't verify is depressed and held, never
> guessed."

> **▶ Confirm here — policy sources.** Where do policies arrive from — payer portals, a feed,
> email, PDFs? That determines the ingestion connectors we build (the workbench already accepts
> pasted text and PDF/image upload via OCR).

---

## 3. Review Queue — validate & reconcile (4 min, the showpiece)

1. Back on the document, click **Generate rule recommendations** → lands on **Review Queue**.
2. Each candidate rule shows two independent judgments with cited rationale:
   - **Validation** against the policy evidence — SUPPORTED / PARTIAL / UNSUPPORTED.
   - **Reconciliation** against the existing **rule library** — one of:
     - **NET_NEW** — nothing covers this yet (e.g. the coverage, documentation, bundling rules).
     - **UPDATE** — an existing rule should change (the prior-auth rule covered only `72148`; the
       policy adds CT `72131/72132` → UPDATE, with the code-overlap shown).
     - **DUPLICATE** — already covered, no material change.
     - **CONFLICT** — contradicts an existing rule.
3. **Point at the FREQUENCY row.** The policy says "repeat MRI within **12 months**"; the library
   rule says **6 months** → **CONFLICT**, flagged **needs attention**. Filter by **Needs attention
   only** to show the triage view.

> **Talking point:** "This is the part humans dread — figuring out what a new policy *breaks*.
> P2R surfaces it as a verdict with the matched rule and a deterministic code-overlap, so a
> reviewer adjudicates in seconds instead of hours."

4. **Edit** a candidate (Phase-4 authoring): correct the summary or override the verdict, Save.
5. **Approve** a clean recommendation. Notice the **Publish to ACE** action appears only after
   approval — nothing reaches the engine without a human sign-off.

> **▶ Confirm here — human-in-the-loop thresholds.** What should auto-flow vs. always require
> review? The 0.90 / 0.70 ladder is configurable per provision type and payer.

---

## 4. The closed loop — Publish to ACE (2 min)

1. With an approved recommendation, click **Publish to ACE**. The receipt shows the rule written
   into the coding engine as payer-policy entries, tagged `P2R-INTEGRATION`.
2. The sidebar / Review-Queue panel updates: **"ACE linked · N published"**.

> **Talking point:** "P2R is the rule **supply**; the coding engine is the **consumer**. This is
> the same public API the engine already exposes — so P2R output becomes engine input with no
> custom glue. It's write-only, on your click, against a **sandbox payer**, so the live demo of
> the engine is never disturbed."

> **▶ Confirm here — the rule artifact contract.** What exact shape should a published rule take
> for *your* engine — payer-policy rows (as shown), an edits/MUE-style table, a DSL, a decision
> table? We've kept a clean intermediate representation so we can target whichever you standardize on.

> **▶ Confirm here — identity / MDM.** Which master-data product anchors payer, plan, and provider
> identity across P2R and the engine, so a rule attaches to the right entities?

---

## 5. Rule Library (1 min)

Open **Rule Library** — the existing deployed rules that reconciliation compares against. In
production this is your live rule store; here it's a small seeded set chosen to produce the mix
of verdicts you just saw.

> **▶ Confirm here — system of record for rules.** Is there an existing rule store P2R should
> read/write, or does P2R own it?

---

## 6. Evaluation Harness — "the eval is the product" (3 min)

1. Open **Evaluation Harness**. Show the **golden set** (6 adjudicated cases).
2. Click **Run evaluation**. It runs the **real pipeline** — ingest → extract → validate →
   reconcile — against the golden set and scores five metrics: **provision coverage, code recall,
   citation rate, verdict accuracy, attention accuracy**. Every number is computed live; nothing
   is hardcoded, and the eval cleans up after itself.

> **Talking point:** "This is how we make the system trustworthy and how we catch regressions
> when a model or prompt changes. The golden set is the contract; as your adjudicators grow it,
> the harness grows with it."

> **▶ Confirm here — golden-set ownership.** Who adjudicates and owns the golden set, and at what
> volume? That governs our accuracy SLA and the cadence of model updates.

> **▶ Confirm here — denial mining (roadmap).** The same harness extends to 835 denials → root
> cause → candidate rule. Is the denial/835 feed available for a fast-follow phase?

---

## 7. Architecture note (for the technical stakeholders, 1 min)

- Same DNA as the coding engine: **Claude structured outputs, cited extraction, a confidence
  ladder, audit-first, PHI isolation, a golden eval harness.**
- P2R and the engine share a single **`core/`** package (LLM client + canonical IR); P2R depends
  on `core`, never on the engine app — a one-way dependency that keeps the engine demo immune to
  P2R work and makes future convergence into one **Nous RCM Framework** clean.
- Fully containerized, isolated stack: own database and volume, distinct ports.

> **▶ Confirm here — cloud & region.** Target cloud, region/residency, and tenancy model
> (single- vs multi-tenant, data-isolation requirements)?

---

## 8. Close

> "What you saw is real, running software end-to-end on synthetic data: policy in, cited
> provisions out, validated and reconciled against your rules, human-approved, and published to
> the coding engine — with a live eval proving it. The **▶ Confirm here** points are exactly what
> we'd lock down next to turn this into your platform."

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Sidebar model id is red / "LLM offline" | Anthropic key missing or out of credit — check `.env`, top up, restart api. |
| "Publish to ACE" disabled | The coding engine isn't reachable on `:8000`, or the recommendation isn't **Approved** yet. |
| Stale UI after a rebuild | `docker compose -f p2r/docker-compose.p2r.yml -p p2r up -d --build --force-recreate web`; hard-refresh. |
| Want a pristine queue | `down -v` then `up` (the P2R DB is disposable, synthetic-only). |
| Eval shows < 100% | That's honest — a model/prompt change moved an answer. Inspect the failing row; update the prompt or the golden case. |
