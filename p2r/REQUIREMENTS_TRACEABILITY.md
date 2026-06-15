# P2R — Requirements Traceability

The five requirements of the Policy-to-Rule Intelligence platform, each mapped to its
implementation and verification. All five are **built and verified end-to-end** on real models
and synthetic, PHI-free data. The client and its engine product names are intentionally absent;
the downstream coding engine is referred to generically (here, ACE serves as the concrete target).

Scope note — two requirements have a deliberately bounded external seam, built the honest way:
- **P1 acquisition** ingests from registered sources exposing sandbox/synthetic content; live
  crawling of real payer sites is out of scope. The registry, polling, hashing, change-detection,
  versioning, delta and MDM logic are all real.
- **P4 compilation** emits a canonical Rule IR plus a concrete engine artifact (ACE) and an
  engine-agnostic package; the *exact* target-engine schema is the client's to provide (their own
  stated #1 unknown), and plugs in at the documented adapter seam.

| # | Requirement (as provided) | Status | Implementation | Verified |
|---|---|---|---|---|
| **P1** | An agent that autonomously retrieves payer policies, extracts content, and loads structured data into MDM | ✅ Complete | `acquisition.py` (source registry, poll + hash + change-detect, deterministic delta, payer MDM), `ingest.py` (cited extraction + confidence ladder), `sample.py` (versioned source). UI: **Sources & Acquisition** | Acquire #1 → NEW_POLICY (6 provisions); #2 → REVISION with precise delta (added POS; changed FREQUENCY 12→24mo, PRIOR_AUTH +CPT 72133); #3 → no change |
| **P2** | ML/AI over pooled remit (835) data to surface emerging denial patterns and propose candidate rules | ✅ Complete | `denials.py` (two-proportion changepoint test, SPIKE/PERSISTENT/EMERGING classification, ranking, evidence bundles, candidate-rule proposal), `sample_835.py` (synthetic 835). UI: **Denial Discovery** | 2,970 lines → 3 ranked signals re-derived by statistics (SPIKE z=11.5, EMERGING z=6.9, PERSISTENT); promote → P3 |
| **P3** | (a) Validate each candidate against policy evidence with rationale; (b) update vs net-new vs duplicate vs conflict | ✅ Complete | `validate.py` (`judge_candidate` — the shared P3 judge for both policy- and denial-origin candidates), `prompts.py` (Validator schema). UI: **Review Queue** | Sample policy → 6 verdicts incl. CONFLICT; denial signal → DUPLICATE of existing rule, all cited |
| **P4** | Auto-generate rule logic in the format ingestible by the target engine; replay; promote/rollback | ✅ Complete | `rule_ir.py` (canonical IR + compiler: engine-agnostic package + ACE adapter), `replay.py` (differential vs claim history), `publish.py` (publish + `rollback_recommendation`). UI: Review Queue **Replay / Rollback / IR** | IR + both artifacts compiled; replay = 105 addressable denials / 19.4% projected reduction / $126K; publish→rollback restored engine state |
| **UX** | Review/approval interface spanning P2–P4: queue, rationale, accept/edit/reject, **audit trail with full lineage** | ✅ Complete | Review Queue (queue, rationale, edit/approve/reject); `audit.py` (append-only `DecisionLogEntry`, `lineage_for`). UI: **Decision Log** + Review Queue **Lineage** | Append-only trail [P2 DETECT → P3 JUDGE → P2 PROMOTE → UX APPROVE]; lineage resolves rule → source signal (z=11.5) → decision trail |

## Architecture invariants (held throughout)
- **One-way dependency** `p2r → core`, never the reverse; `p2r` and the coding engine app never import each other.
- **Engine integration is write-only**, on explicit click, against a sandbox payer — the scripted engine demo is structurally immune to P2R.
- **Honesty:** models reason; deterministic code decides and writes. Denial detection is statistics-only (no LLM in the numbers). Every recommendation is cited and confidence-gated; unresolved → human review, never fabricated. Synthetic / PHI-free data only.

## Open decisions (surfaced in the demo as "Confirm here")
Policy acquisition sources & cadence · the exact target-engine rule artifact contract · identity/MDM
product · cloud / region / tenancy · golden-set ownership & accuracy SLA · the 835 denial feed ·
human-in-the-loop thresholds.
