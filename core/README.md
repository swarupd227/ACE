# `core/` — Shared Nous RCM platform primitives

Reusable, framework-level building blocks shared across the Nous RCM Intelligence
Framework. Today it is consumed by **`p2r/`** (the Policy-to-Rule platform). The
**ACE** app keeps running on its own in-place copy and will be repointed at `core/`
**after the ACE/Vee demo** (Phase 7 of `RCM_FRAMEWORK_PLAN.md`).

## The one rule

**`core/` depends on nothing above it. The dependency arrow is `p2r → core` (and later
`ace → core`) — never the reverse, and `ace`/`p2r` never import each other.** This is
what keeps the ACE/Vee demo structurally safe from P2R work.

## Stability contract

While the ACE demo is live, changes here are **additive / backward-compatible only**, so
that when ACE adopts `core/` the switch is a mechanical, canary-verified flip.

## Contents

| Module | What it is |
|--------|------------|
| `settings.py` | Env-only configuration (API keys never in code/DB) |
| `llm_client.py` | Provider-agnostic LLM client — structured output, prompt caching, honest `LLMUnavailable` fallback |
| `ir.py` | The canonical Intermediate Representation: every artifact (a code, a rule, a policy provision) carries citations, provenance, effective dating and confidence |
