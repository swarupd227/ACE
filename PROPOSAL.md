# Proposal — Autonomous Medical Coding

**From:** Nous Infosystems  **To:** Vee Healthtek  **Date:** 2026-06-08  **Status:** v1.0 (draft for discussion)
**Sponsors:** Michelle Castillon (CPTO), Amrish Kumar (CTAIO), Murali (Ops) · **Investor stakeholder:** TA Associates

> Framed for TA's directive: **move fast, outcome-based, fixed scope.** We lead with a working demo
> (this repo) on **June 15–16 in Bangalore**, then a **60–90 day pilot**, then scale what performs —
> the exact cadence in Vee Healthtek's own overview deck.

---

## 1. Executive summary
We will stand up a **production-grade, agentic autonomous medical coding** capability inside RevAmp's
Coding Studio that translates clinical documentation into audit-defensible codes and routes each chart
into **Straight-Through Billing (STB) / QA / Manual** by calibrated confidence. We start with a working
demo, prove accuracy on a frozen golden set in shadow mode, then enable STB progressively under VHT's
audit governance. Anchor specialty **Radiology**, immediately followed by **E&M** and **ED** (highest
volume), built as a **specialty accelerator** for fast expansion.

## 2. Outcomes & success metrics
| Metric | Target | Notes |
|---|---|---|
| Coding accuracy (chart level) | **≥90%, progressive** | Ramp from a lower shadow-mode baseline; not a hard go-live floor (confirmed on call) |
| STB / automation maturity | **≥80%** | Confidence-routed straight-through share |
| Manual effort reduction | **≥30%** | Coder-minutes saved on STB + partial QA |
| Turnaround time | **−10–15%** | Per-chart latency |
| Defensibility | 100% audit trail | Citation + guideline + model-version chain on every code |

**Governance gate:** VHT audits **100% of charts** during initial rollout; the model earns
**certification at ≥95% quality**, after which audit sampling tapers and STB share grows.

## 3. Scope
- **Specialties:** Radiology (anchor) → **E&M** → **ED**; Pathology/Surgical as follow-on. Built once as a
  specialty accelerator (per-specialty config + per-client port-in).
- **Clients:** 3–5 pilot clients, prioritized by **data access already in place** — and, where access
  exists (incl. the recent acquisition), aim to run **100% flow** for those clients (per TA's guidance).
- **Platforms / data:** **Practice Admin** (VHT-owned PMS), **eClinicalWorks**, **Cerner**.
- **Out of scope (initially):** Interventional Radiology; real-time retraining (batch first); fine-tune/
  distillation productionization (blueprint now, build during scale).

## 4. Approach & timeline (aggressive, milestone-based)
| Phase | Window | Goal | Key activities |
|---|---|---|---|
| **0 · Demo** | by **Jun 15–16** | Prove approach, workflow, architecture, explainability | Live ACE demo: Radiology + E&M, 4 scenarios, Graph-RAG, gates, audit, eval |
| **1 · Mobilize & foundations** | Weeks 1–4 | Secure env + data; pipeline in VHT's Azure | Azure/Foundry setup (US-region, multi-tenant), data integration agreements, reference + payer-policy curation, golden-set build (Radiology, E&M) |
| **2 · Shadow mode** | Weeks 4–8 | Measure honestly before any STB | Run alongside coders; daily disagreement reports; per-specialty calibration; tune thresholds on real data |
| **3 · Controlled STB go-live (60–90 day pilot)** | Weeks 8–12 | Radiology STB for 1–2 clients, then E&M | Enable STB above thresholds; 100% audit → taper to certification; CDI/override loop live |
| **4 · Scale** | Weeks 12+ | Add ED + more clients; SLM accelerator | ED golden set + tuning; expand clients with data access; begin fine-tune/distill; denial-feedback loop |

## 5. Deliverables
- Production-ready autonomous coding engine inside RevAmp Coding Studio (Azure, US-region).
- Specialty-configured models + calibration per specialty; per-client port-in.
- Graph-RAG knowledge graph (payer policy + medical ontology) + curation pipeline.
- Human-in-the-loop coder workspace (summary, citations, color-coded confidence, override+reason).
- Evaluation harness + frozen golden sets + drift detection; weekly/monthly performance reporting.
- Audit/defense-packet generator; append-only ledger; replayable decisions.
- SOPs, runbooks, and the **AI blueprint** (`BLUEPRINT.md`).

## 6. Commercial model
**Outcome-based, fixed-scope SOW** aligned to automation performance (STB share / accuracy / effort
reduction), with milestone-based payments tied to Phases 0–4. Specific fees and the STB-linked pricing
curve to be finalized with VHT/TA after the pilot scope and volumes are confirmed.

## 7. What we need from Vee Healthtek
1. **Data access** to the pilot clients (Practice Admin / eCW / Cerner) and the AI/data agreements.
2. **Domain SME support** — coding/CDI experts for golden-set adjudication and edge-case rulings
   (Murali offered this on the call).
3. **Payer-policy inputs** — bulletins/medical-necessity for the pilot payers (Anthem, Cigna, Medicare)
   to curate into the knowledge graph (not structured today).
4. **Sample de-identified charts** per specialty and **daily volumes** per in-scope client.
5. **Azure/Foundry** access (US-region) and confirmation of Anthropic availability via Foundry.

## 8. Risks & mitigations
| Risk | Mitigation |
|---|---|
| CPT/AMA licensing | Pluggable code table; load VHT's licensed AMA in prod (demo uses labeled placeholder) |
| Accuracy expectations | Progressive ramp + shadow mode + honest IRR-ceiling reporting; bounded autonomy |
| Payer rules unstructured | Curation pipeline into the knowledge graph; per-client port-in |
| Data access timing | Start with clients/acquisition that already grant access; expand as access lands |
| Aggressive timeline | Specialty accelerator + working demo as the head start; phase-gated go-live |

## 9. Why Nous
Working capability today (not slideware), deep RCM/coding domain alignment, prior autonomous-coding
experience (incl. Medicodio), and TA-portfolio alignment for fast, trusted execution.

---
*Companion documents: `BLUEPRINT.md` (AI architecture), `DESIGN.md` (full design + source reconciliation),
and the running ACE demo in this repo.*
