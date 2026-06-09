# Nous Value-Add — what's defensible vs. replicable

**Honest premise:** a worklist, a coding screen, and an LLM call are **replicable** — any competent team can
build those, and several coding-AI vendors have. If that were all this were, it would be a commodity. The
defensible value is **not the screens**; it's the **methodology, the accelerator, and the operating
discipline** underneath them. This document names what Nous brings that is hard to copy — and points to
where each lives in the running app.

## The moat map

| Layer | Replicable by anyone? | Where the Nous value is |
|---|---|---|
| Coding UI / worklist | ✅ commodity | — |
| Single LLM "code this chart" call | ✅ commodity | — |
| **Evaluation + calibration harness** | ❌ **hard** | Frozen golden sets, per-specialty calibration, IRR-honest reporting, drift detection — *the* moat |
| **Defensibility engine** | ❌ **hard** | Citation-gated coding, deterministic validation gates, replayable audit packets, bounded autonomy |
| **Specialty Accelerator** | ❌ **hard** | Config-driven onboarding of specialties/clients in *hours*, not a rebuild |
| **Graph-RAG + policy/ontology curation** | ◑ **moderate** | Curated payer-policy + medical-ontology KG that *drives* the necessity gate |
| **Closed-loop learning + ML-Ops** | ◑ **moderate** | Captured corrections → exemplars/fine-tune; invalid-code flagging |
| **Admin-configurable platform** | ◑ **moderate** | Thresholds, weights, rules, SLAs, specialties all tunable by an admin (not hardcoded) |

## The five things competitors can't easily replicate

### 1. The Evaluation & Calibration Harness — *the moat*
Anyone can fine-tune a model; **few can sustain a frozen, adjudicated golden set across seven specialties,
rebuild calibration after every code-set update, and detect drift before it becomes a denial spike.** We
report accuracy **vs. adjudicated consensus with the inter-rater-reliability ceiling** — not a vanity "95%."
That honesty is what survives a CTO's scrutiny and a payer audit. *In the app:* Evaluation Harness screen;
the 4-factor calibrated confidence; Admin → Routing & Calibration.

### 2. The Defensibility Engine
Every code carries a **chart-line citation + guideline reference, verified**, runs through **deterministic
gates** (NCCI/MUE/modifier/specificity/payer-necessity), and produces a **replayable audit packet** with the
model version. **Bounded autonomy** keeps the highest-stakes calls with humans by rule. *Accuracy without
defensibility is a denial waiting to happen* — this is the architecture that makes auto-coding survive a RAC
audit. *In the app:* citations + gates + audit packet on every encounter; bounded-autonomy rules in Admin.

### 3. The Specialty Accelerator
A new specialty or client is **configuration + a golden set, not a six-month rebuild**. Specialties carry
their own code scope, gate set, model tier, and calibration; client-specific payer rules and coding
preferences "port in" per tenant. *This is the economic story: time-to-new-specialty.* *In the app:*
Admin → Specialty Accelerator (enable/disable, model tier); Policy Admin client overlays; 5 specialties live.

### 4. Graph-RAG over a curated payer + ontology knowledge graph
The agent is grounded in a **payer-policy + medical-ontology graph** and may only emit codes it surfaces — a
structural hallucination control that also **drives the deterministic medical-necessity gate**. Building and
*maintaining* this graph (payer-bulletin ingestion, ontology curation, versioning, per-client overlays) is
operational IP, not a one-off. *In the app:* Policy & Knowledge Admin (editable, interactive graph);
per-chart "Knowledge used" evidence.

### 5. Admin-configurable platform + operating model
It is a **platform an admin operates**, not a demo: routing thresholds, the 4-factor weights, self-consistency,
SLAs, eligibility, bounded-autonomy, specialties, and roster are all tunable at runtime. Combined with the
**operating model** (control tower, human pods, the 100%-audit → 95%-certification governance ramp) and native
fit into **RevAmp**, this is a *capability VHT runs*, not a tool VHT rents. *In the app:* Admin / Configuration;
Control Tower; role-based access.

## Beyond the software
- **Domain depth:** the build is shaped by real coding nuance (modifier 26, NCCI bundling, MEAT, DRG impact,
  upcoding controls), not the marketing version — which is what earns the coders' trust.
- **Execution & alignment:** Nous + Vee Healthtek are both **TA Associates portfolio companies** — a trusted,
  fast, aligned build partnership, not a cold vendor.
- **The harness is the deliverable:** once VHT owns the eval/calibration harness, every subsequent specialty is
  a *calibration exercise*, not a research project. That compounding capability is the durable advantage.

## Bottom line
If a competitor copies the screens, they have a demo. The moat is the **eval/calibration discipline, the
defensibility architecture, the accelerator, and the curated knowledge graph** — the parts that make
autonomous coding *deployable, auditable, and expandable*. That is the Nous value-add.
