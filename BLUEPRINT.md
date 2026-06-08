# AI Blueprint — Autonomous Medical Coding

**Prepared by Nous Infosystems for Vee Healthtek** · For: Amrish Kumar (CTAIO), Michelle Castillon (CPTO), Dr. Muthu Krishnan (CDTO), Murali (Ops)
**Companion to:** the working **ACE — Autonomous Coding Engine** demo (this repo) and `DESIGN.md`.
**Status:** v1.0 · 2026-06-08

> On the June 5 call, Amrish asked us to share our blueprint — the **workflow, models, embeddings, and
> graphs** we would use for autonomous coding — so VHT can align its own blueprint and TSM direction.
> This document is that blueprint. Every element here is **already implemented and runnable** in the ACE
> demo, so it is an engineering reference, not a concept deck. Section 13 maps each item to the code.

---

## 1. Design principles
1. **Defensibility over raw accuracy.** If we cannot defend a code to a payer/RAC auditor with the
   evidence chain in front of us, the system should not have emitted it. Citations are gates, not garnish.
2. **Bounded autonomy.** The economic win is volume, not the hardest cases. High-stakes/ambiguous charts
   are routed to humans by rule, regardless of model confidence.
3. **Deterministic where determinism belongs.** Code existence, NCCI, MUE, modifiers, sequencing are
   rule-based lookups — LLMs are bad at exhaustive lookups, so we don't use them there.
4. **Honest failure.** No reachable LLM ⇒ route to the manual queue, never fabricate. (Verified behavior.)
5. **Specialty accelerator.** One pipeline, configured per specialty and per client, so each new
   specialty/client is a calibration exercise, not a rebuild.

## 2. The agentic workflow (what runs per chart)
A LangGraph-style orchestrator drives each chart through staged agents and deterministic engines; any
stage can **veto or downgrade** a decision, and failures trigger a bounded re-route to humans.

```
Stage 0  Eligibility gate (deterministic)     required docs · approved specialty/procedure · auth · exclusions
Stage 1  Document conditioning (LLM)          section ID · copy-forward/contradiction/unsigned flags · chart summary
Stage 2  Clinical entity extraction (LLM)     structured slots: laterality, contrast, view count, encounter type, negation, temporality
  ↳      Graph-RAG retrieval                   candidate codes + guideline excerpts + payer policy + ontology paths + learned corrections
Stage 3  Cited code generation (LLM)          schema-bound; every code MUST cite chart lines + a guideline; self-consistency on hard charts
Stage 3b Citation verification (deterministic) cited text must actually exist at the cited lines; else rejected
Stage 4  Validation & compliance gates (det.)  existence · specificity · NCCI · MUE · modifier · sex/age · POS · payer necessity
Stage 5  Calibration & routing                 4-factor calibrated confidence + bounded-autonomy → STB / QA / Manual
```
Cross-cutting: append-only **audit ledger**, **closed-loop learning**, **evaluation harness + drift**.

## 3. Models & tiering
| Where | Demo (now) | Production direction |
|---|---|---|
| Conditioning / extraction | Claude Sonnet (frontier) | Sonnet, or a **fine-tuned SLM** once data volume supports it |
| Coding (reasoning) | Claude Sonnet; **Opus on hard encounters** (E&M, multi-procedure, ambiguous) | Same tiering; **distilled specialty SLMs** for high-volume, low-variance specialties (radiology) to cut latency/cost/hallucination |
| Deterministic gates | Rule engine (no model) | Same |

**Specialty accelerator path (matches Amrish's "SLM accelerator"):** start with frontier models for
speed-to-accuracy; capture labeled corrections; **fine-tune a foundation model per specialty, then
distill to a smaller model** for latency/cost. Frontier models remain the fallback/hard-case tier.
On the call we confirmed VHT's own TSMs are not demo-ready, so the demo uses frontier models; the
production blueprint folds the TSM/SLM track in as the accelerator.

## 4. Retrieval — Graph-RAG over a payer + ontology knowledge graph
This is Amrish's #1 ask. ACE grounds the coder agent in a knowledge graph and **only lets it emit codes
the retrieval surfaces** — a structural hallucination control.
- **Nodes:** medical-ontology concepts (SNOMED-style), ICD/CPT/HCPCS codes, payers.
- **Edges:** `is_a`, `finding_site`, `associated_with`, `maps_to` (concept→code), `policy` (payer→code).
- **Retrieval = lexical candidate scoring + ontology graph traversal + payer-policy lookup + learned
  corrections**, assembled into the coding agent's context.
- **Payer policy** (Anthem, Cigna, Medicare LCD/NCD-style) + **medical-necessity** + **medical
  ontologies** are first-class — Amrish tied ontologies directly to hallucination reduction, and we model
  them as graph context the agent must respect.
- **Embeddings:** `pgvector` columns are in the schema; the demo uses lexical + graph retrieval to stay
  offline and deterministic. Production turns on embedding retrieval (Azure OpenAI embeddings or a local
  embedder) for fuzzy recall, layered on the same graph.
- Payer rules are **not structured today** (confirmed on call) → we curate them into the graph and
  "port in" per client.

## 5. Hallucination controls (defense in depth)
| Failure mode | Control in ACE |
|---|---|
| Fabricated code | Stage 4 code-existence gate (effective-dated) + Graph-RAG restricts to surfaced codes |
| Wrong-but-real code | Citation requirement + deterministic gates + self-consistency on hard charts |
| Fabricated documentation | Stage 3b citation verification — cited text must exist at the cited lines |
| Specificity inflation (upcoding) | Specificity gate (non-billable parent rejected) + "no specificity beyond the chart" prompt rule |
| Compliance hallucination | Guideline citation required + verified against the indexed guideline corpus |
| Ontology-driven errors | Graph-RAG ontology grounding (Amrish's point) |
| Confident-but-wrong | Self-consistency (N samples) + calibration + **bounded-autonomy hard rules** |

## 6. Confidence model (the four factors VHT specified)
Each code carries a **calibrated** confidence composed from four visible sub-scores:
1. **Clinical-document match** (citation grounding quality, verified)
2. **Historical patterns** (similar gold/learned exemplars)
3. **Rule-engine validations** (gate pass ratio: LCD/NCD, NCCI, modifiers)
4. **AI model certainty** (self-reported × self-consistency agreement)

`calibrated = 0.40·model + 0.25·doc_match + 0.25·rule + 0.10·historical` (per-specialty calibration —
temperature scaling + isotonic regression — fitted on held-out data in production). Routing uses the
**calibrated** score, never raw model output. Color-coded in the UI with the full breakdown on expand.

## 7. Human-in-the-loop & closed-loop learning
- Coder workspace: chart **summary**, rationale, citations, **color-coded confidence**, and per-code
  **accept / override-with-reason**.
- **Closed loop:** an override is captured with its reason and becomes a **retrieval exemplar** keyed to
  the chart pattern; the next similar chart visibly shifts toward the correction. In production this runs
  as a **24–48h batch** into the SLM fine-tune pipeline (the cadence Amrish specified), not real-time.
- **ML-Ops:** the pipeline flags **invalid/junk codes** from model output (Amrish's ask) — caught at the
  existence/citation gates and logged as model-improvement signals.

## 8. Specialty accelerator & multi-tenancy
- **Per-specialty config:** code-set scope, gate set, calibration thresholds, eligibility rules.
- **Per-client port-in:** coding preferences/history and payer-KG rules layer on the shared core.
- **Multi-tenant isolation:** no client-data co-mingling (confirmed requirement). In production, tenant
  isolation at the data and model-context layers; per-client exemplar/KG namespaces.

## 9. Data & code-set management
- Effective-dated reference tables (ICD-10-CM/PCS, CPT, HCPCS) → correct codes per date of service across
  the Oct (ICD) / Jan (CPT) update boundaries; historical sets retained for corrected claims.
- **CPT licensing:** demo uses a clearly-labeled placeholder table; production swaps in VHT's licensed
  AMA distribution (same table shape) — a config change, not a code change.
- Annual code-set update = a planned model re-evaluation + recalibration event.

## 10. Evaluation harness & drift (the moat)
- **Frozen golden sets** per specialty; truth = post-adjudication consensus; ambiguous cases flagged
  "never auto-code."
- Metrics: code-existence, top-1, specificity, modifier, **citation validity**, calibration error (ECE),
  **STB share**, and — reported honestly — **accuracy vs consensus with the IRR ceiling** alongside.
- Drift: weekly golden-set regression, per-payer denial monitoring, per-coder agreement.

## 11. Production architecture (Azure, US-region)
```
EHR/PMS (Practice Admin, eClinicalWorks, Cerner)  ──FHIR/HL7/EDI──▶  RevAmp Coding Studio
                                                                          │
                                                                ACE pipeline (Azure)
                                  ┌───────────────────────────────────────┼───────────────────────────┐
                          Azure AI Foundry                         Postgres/pgvector            Knowledge graph
                  (Azure OpenAI / Anthropic; frontier + SLMs)     (codes, audit, eval)       (payer policy + ontology)
```
- **US-region servers** (mandatory), **multi-tenant isolation**, BA agreements via MS EA.
- Model endpoint is **configurable** (Foundry Azure OpenAI / Anthropic-in-Foundry / local) — the demo's
  Claude path maps directly to a Foundry endpoint in production.
- Integrates **inside RevAmp** as the Coding Studio engine; human-in-the-loop uses RevAmp worklist/
  inventory management.

## 12. Security & compliance
HIPAA-shaped from day one (PHI-safe logging, RBAC, encryption in transit/at rest), append-only audit
ledger, replayable decisions (same chart + model version → same result), SOC 2 / HITRUST-aligned to
VHT's existing posture.

## 13. Blueprint → working ACE demo (proof, not theory)
| Blueprint element | Where it lives in this repo |
|---|---|
| Stage 0–5 orchestrator | `backend/app/pipeline/orchestrator.py` |
| Deterministic gates | `backend/app/pipeline/validation.py` |
| Graph-RAG + knowledge graph | `backend/app/knowledge/graph_rag.py`, `…/seed/reference_data.py` |
| Structured prompts/schemas | `backend/app/llm/prompts.py` |
| LLM client + honest fallback | `backend/app/llm/client.py` |
| 4-factor confidence + routing | `orchestrator.py` (Stage 5) |
| Closed-loop learning | `backend/app/routes/coding.py` (override), `…/routes/insights.py` (learning) |
| Evaluation harness | `backend/app/routes/insights.py` (`/eval/run`) |
| Audit ledger | `models.AuditEntry`, surfaced in the UI audit packet |
| UI (worklist, pipeline, KG, eval, learning) | `frontend/src/pages/*` |
