/* ACE — Autonomous Coding Engine: Functional Flow + Technical Architecture deck.
   Run: node build_deck.js  ->  ACE_Architecture.pptx */
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "Nous Infosystems";
pres.company = "Nous Infosystems";
pres.title = "ACE — Autonomous Coding Engine";

const W = 13.33, H = 7.5;
// Palette — "Midnight + Teal" premium enterprise
const C = {
  bgDark: "0E1B33", navy: "1B2A4A", navy2: "24365C",
  teal: "13B5A6", tealDk: "0E8C81",
  ice: "EAF1F8", light: "F5F8FC", card: "FFFFFF",
  text: "27313F", muted: "6B7A8D", white: "FFFFFF",
  amber: "E8A13A", green: "2E9E6B", slate: "64748B",
  line: "D8E1EC",
};
const HEAD = "Georgia", BODY = "Calibri";

function footer(slide, n) {
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: H - 0.32, w: W, h: 0.32, fill: { color: C.bgDark }, line: { type: "none" } });
  slide.addText("ACE · Autonomous Coding Engine", { x: 0.5, y: H - 0.32, w: 6, h: 0.32, fontFace: BODY, fontSize: 8.5, color: "9FB0C7", valign: "middle", margin: 0 });
  slide.addText("Nous Infosystems  ·  for Vee Healthtek  ·  Confidential", { x: W - 6.5, y: H - 0.32, w: 6, h: 0.32, fontFace: BODY, fontSize: 8.5, color: "9FB0C7", align: "right", valign: "middle", margin: 0 });
  if (n) slide.addText(String(n), { x: W - 0.55, y: H - 0.32, w: 0.4, h: 0.32, fontFace: BODY, fontSize: 8.5, color: C.teal, align: "right", valign: "middle", bold: true, margin: 0 });
}
// content slide header (kicker + title), light background
function header(slide, kicker, title) {
  slide.background = { color: C.light };
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 1.18, fill: { color: C.white }, line: { type: "none" } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 1.18, w: W, h: 0.03, fill: { color: C.line }, line: { type: "none" } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.34, w: 0.12, h: 0.56, fill: { color: C.teal }, line: { type: "none" } });
  slide.addText(kicker.toUpperCase(), { x: 0.78, y: 0.30, w: 11, h: 0.26, fontFace: BODY, fontSize: 11, color: C.teal, bold: true, charSpacing: 2, margin: 0 });
  slide.addText(title, { x: 0.78, y: 0.52, w: 12, h: 0.5, fontFace: HEAD, fontSize: 23, color: C.navy, bold: true, margin: 0 });
}
const sh = () => ({ type: "outer", color: "1B2A4A", blur: 7, offset: 3, angle: 135, opacity: 0.12 });
function card(slide, x, y, w, h, fill) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.07, fill: { color: fill || C.card }, line: { color: C.line, width: 1 }, shadow: sh() });
}
// flow box with title + sub
function flowBox(slide, x, y, w, h, title, sub, fill, tcolor) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill: { color: fill }, line: { type: "none" }, shadow: sh() });
  slide.addText([
    { text: title, options: { fontFace: BODY, fontSize: 11.5, bold: true, color: tcolor || C.white, breakLine: true } },
    { text: sub, options: { fontFace: BODY, fontSize: 8.5, color: tcolor ? C.muted : "D7E3F5" } },
  ], { x: x + 0.08, y, w: w - 0.16, h, align: "center", valign: "middle", margin: 2, lineSpacingMultiple: 0.95 });
}
function arrow(slide, x, y, w) {
  slide.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color: C.teal, width: 2.2, endArrowType: "triangle" } });
}

// ───────────────────────── 1 · TITLE ─────────────────────────
(() => {
  const s = pres.addSlide();
  s.background = { color: C.bgDark };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: C.teal }, line: { type: "none" } });
  // motif: faint stacked rounded rects top-right
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.7, y: -1.2, w: 5, h: 5, rectRadius: 0.2, fill: { color: C.navy2, transparency: 35 }, line: { type: "none" } });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 10.8, y: 3.4, w: 4, h: 4, rectRadius: 0.2, fill: { color: C.navy2, transparency: 55 }, line: { type: "none" } });
  s.addText("NOUS INFOSYSTEMS   ·   FOR VEE HEALTHTEK", { x: 0.8, y: 1.5, w: 10, h: 0.4, fontFace: BODY, fontSize: 13, color: C.teal, bold: true, charSpacing: 3, margin: 0 });
  s.addText("ACE — Autonomous Coding Engine", { x: 0.8, y: 2.15, w: 11.4, h: 1.1, fontFace: HEAD, fontSize: 44, color: C.white, bold: true, margin: 0 });
  s.addText("Agentic AI for medical-coding translation", { x: 0.8, y: 3.35, w: 11, h: 0.6, fontFace: BODY, fontSize: 20, color: "CADCFC", margin: 0 });
  s.addText("Functional Flow  ·  Technical Architecture  ·  Design Rationale", { x: 0.82, y: 4.05, w: 11, h: 0.5, fontFace: BODY, fontSize: 14, italic: true, color: "9FB0C7", margin: 0 });
  // chips
  const chips = ["Graph-RAG grounded", "Citation-backed & auditable", "Confidence-routed autonomy", "Admin-configurable platform"];
  let cx = 0.8;
  chips.forEach((t) => {
    const w = 0.34 + t.length * 0.092;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: 5.15, w, h: 0.46, rectRadius: 0.23, fill: { color: C.navy2 }, line: { color: C.teal, width: 1 } });
    s.addText(t, { x: cx, y: 5.15, w, h: 0.46, fontFace: BODY, fontSize: 10.5, color: "E6EEFA", align: "center", valign: "middle", margin: 0 });
    cx += w + 0.22;
  });
  s.addText("In-person demo · Bangalore · June 2026", { x: 0.8, y: 6.6, w: 11, h: 0.4, fontFace: BODY, fontSize: 11, color: "7E90A8", margin: 0 });
})();

// ───────────────────────── 2 · CONTEXT ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Context & Objectives", "Why autonomous coding — and what 'good' means here");
  const colY = 1.55;
  // left: the challenge
  card(s, 0.5, colY, 6.05, 5.2);
  s.addText("The coding challenge", { x: 0.8, y: colY + 0.2, w: 5.5, h: 0.4, fontFace: BODY, fontSize: 15, bold: true, color: C.navy, margin: 0 });
  const ch = [
    ["Narrative → codes", "Clinical reports must become precise ICD-10 / CPT / HCPCS — specificity, bundling and modifiers all matter."],
    ["Accuracy is non-negotiable", "Errors mean denials, compliance exposure and rework; coders are scarce and audited."],
    ["Volume & turnaround", "High chart volume with TAT pressure; coder effort is the cost driver."],
    ["Trust gap with 'black-box' AI", "Leaders need to see why a code was chosen before they let anything auto-bill."],
  ];
  let y = colY + 0.7;
  ch.forEach(([t, d]) => {
    s.addShape(pres.shapes.OVAL, { x: 0.8, y: y + 0.05, w: 0.16, h: 0.16, fill: { color: C.teal }, line: { type: "none" } });
    s.addText([
      { text: t + "  ", options: { bold: true, color: C.text } },
      { text: d, options: { color: C.muted } },
    ], { x: 1.05, y, w: 5.35, h: 0.95, fontFace: BODY, fontSize: 11.5, valign: "top", margin: 0, lineSpacingMultiple: 0.98 });
    y += 1.05;
  });
  // right: targets (KPI callouts)
  card(s, 6.8, colY, 6.03, 5.2, C.navy);
  s.addText("Vee Healthtek success measures", { x: 7.1, y: colY + 0.2, w: 5.4, h: 0.4, fontFace: BODY, fontSize: 15, bold: true, color: C.white, margin: 0 });
  s.addText("Progressive, not a hard day-one floor", { x: 7.1, y: colY + 0.58, w: 5.4, h: 0.3, fontFace: BODY, fontSize: 10.5, italic: true, color: "9FB0C7", margin: 0 });
  const kpi = [
    ["≥ 90%", "chart-level accuracy (SLA)"],
    ["≥ 80%", "straight-through billing (STB) rate, at maturity"],
    ["≥ 30%", "manual-effort reduction"],
    ["10–15%", "turnaround-time reduction"],
  ];
  let ky = colY + 1.0;
  kpi.forEach(([n, l]) => {
    s.addText(n, { x: 7.1, y: ky, w: 2.0, h: 0.62, fontFace: HEAD, fontSize: 27, bold: true, color: C.teal, valign: "middle", margin: 0 });
    s.addText(l, { x: 9.15, y: ky, w: 3.5, h: 0.62, fontFace: BODY, fontSize: 11.5, color: "E6EEFA", valign: "middle", margin: 0 });
    ky += 0.8;
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 7.1, y: ky + 0.05, w: 5.4, h: 0.02, fill: { color: "3A4D72" }, line: { type: "none" } });
  s.addText("Governance ramp: 100% audit early → certify the model at ≥ 95% → taper sampling.", { x: 7.1, y: ky + 0.18, w: 5.45, h: 0.6, fontFace: BODY, fontSize: 10.5, italic: true, color: "CADCFC", valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  footer(s, 2);
})();

// ───────────────────────── 3 · AT A GLANCE ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Solution Overview", "ACE at a glance — four pillars");
  const items = [
    ["01", "Agentic pipeline", "A multi-stage reasoning agent conditions, extracts, codes, validates and routes — observable live via streaming."],
    ["02", "Grounded & defensible", "Graph-RAG grounding + deterministic gates + per-code citations and an append-only audit trail."],
    ["03", "Confidence-routed autonomy", "Calibrated confidence sends charts to Straight-Through Billing, QA, or Manual — with hard human-review rules."],
    ["04", "Configurable platform", "Admins tune routing, gates, the knowledge graph, specialties and roles at runtime — no redeploy."],
  ];
  const cw = 2.93, gap = 0.2, x0 = 0.5, cy = 1.7, chh = 4.9;
  items.forEach(([n, t, d], i) => {
    const x = x0 + i * (cw + gap);
    card(s, x, cy, cw, chh);
    s.addShape(pres.shapes.RECTANGLE, { x, y: cy, w: cw, h: 0.12, fill: { color: C.teal }, line: { type: "none" } });
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: cy + 0.45, w: 0.95, h: 0.95, fill: { color: C.ice }, line: { type: "none" } });
    s.addText(n, { x: x + 0.3, y: cy + 0.45, w: 0.95, h: 0.95, fontFace: HEAD, fontSize: 22, bold: true, color: C.tealDk, align: "center", valign: "middle", margin: 0 });
    s.addText(t, { x: x + 0.28, y: cy + 1.6, w: cw - 0.56, h: 0.7, fontFace: BODY, fontSize: 15, bold: true, color: C.navy, margin: 0 });
    s.addText(d, { x: x + 0.28, y: cy + 2.3, w: cw - 0.56, h: 2.4, fontFace: BODY, fontSize: 11.5, color: C.muted, valign: "top", margin: 0, lineSpacingMultiple: 1.02 });
  });
  footer(s, 3);
})();

// ───────────────────────── 4 · FUNCTIONAL FLOW ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Functional Flow", "The operational workflow — intake to billing, with a learning loop");
  const y = 1.5, bh = 0.92, bw = 1.95;
  const xs = [0.5, 2.62, 4.74, 6.86, 8.98];
  flowBox(s, xs[0], y, bw, bh, "Intake", "PMS / EHR via FHIR · HL7 · EDI · batch / REST", C.navy);
  flowBox(s, xs[1], y, bw, bh, "Eligibility gate", "Stage 0 — docs, specialty, exclusions", C.navy);
  flowBox(s, xs[2], y, bw, bh, "Agentic pipeline", "summarize → extract → code → validate", C.tealDk);
  flowBox(s, xs[3], y, bw, bh, "Confidence routing", "calibrated 4-factor score", C.navy);
  flowBox(s, xs[4], y, 3.85, bh, "Billing / clearinghouse", "claim submitted (837)", C.navy);
  [0, 1, 2, 3].forEach((i) => arrow(s, xs[i] + bw, y + bh / 2, xs[i + 1] - xs[i] - bw));

  // lanes heading
  s.addText([
    { text: "Confidence routing  →  ", options: { bold: true, color: C.navy } },
    { text: "each chart goes to exactly one of three lanes", options: { color: C.muted, italic: true } },
  ], { x: 0.5, y: 2.62, w: 12.33, h: 0.3, fontFace: BODY, fontSize: 12, margin: 0 });
  // routing lanes — horizontal row of three
  const ly = 3.02, lh = 0.95, lw = 3.95, lgap = 0.24;
  const lxs = [0.5, 0.5 + lw + lgap, 0.5 + 2 * (lw + lgap)];
  const lanes = [
    ["STB — Straight-Through Billing", "auto-bill, audit-sampled", C.green],
    ["QA review", "auditor verifies the AI draft", C.amber],
    ["Manual coding", "AI pre-extraction assists a coder", C.slate],
  ];
  lanes.forEach(([t, d, col], i) => {
    const x = lxs[i];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: ly, w: lw, h: lh, rectRadius: 0.06, fill: { color: C.white }, line: { color: C.line, width: 1 }, shadow: sh() });
    s.addShape(pres.shapes.RECTANGLE, { x, y: ly, w: 0.13, h: lh, fill: { color: col }, line: { type: "none" } });
    s.addText([
      { text: t, options: { bold: true, color: C.text, fontSize: 12.5, breakLine: true } },
      { text: d, options: { color: C.muted, fontSize: 10.5 } },
    ], { x: x + 0.3, y: ly, w: lw - 0.45, h: lh, fontFace: BODY, valign: "middle", margin: 2, lineSpacingMultiple: 1.0 });
  });
  // CDI branch + learning loop — two wide cards
  const cy = 4.28, ch2 = 1.22, cw2 = 6.06;
  card(s, 0.5, cy, cw2, ch2, C.ice);
  s.addText("CDI / physician query  (branch)", { x: 0.72, y: cy + 0.13, w: cw2 - 0.4, h: 0.3, fontFace: BODY, fontSize: 12.5, bold: true, color: C.navy, margin: 0 });
  s.addText("When documentation can't support a specific code, ACE drafts a compliant, non-leading query; the physician's answer re-codes the chart.", { x: 0.72, y: cy + 0.47, w: cw2 - 0.45, h: 0.72, fontFace: BODY, fontSize: 11, color: C.muted, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  card(s, 0.5 + cw2 + 0.21, cy, cw2, ch2, C.ice);
  s.addText("Closed-loop learning  (feedback)", { x: 0.72 + cw2 + 0.21, y: cy + 0.13, w: cw2 - 0.4, h: 0.3, fontFace: BODY, fontSize: 12.5, bold: true, color: C.navy, margin: 0 });
  s.addText("Coder corrections become retrieval exemplars that visibly shift later similar charts (batched 24–48h in production).", { x: 0.72 + cw2 + 0.21, y: cy + 0.47, w: cw2 - 0.45, h: 0.72, fontFace: BODY, fontSize: 11, color: C.muted, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  // bottom banner
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 5.78, w: 12.33, h: 1.05, rectRadius: 0.06, fill: { color: C.navy }, line: { type: "none" } });
  s.addText([
    { text: "Every chart carries its evidence forward.  ", options: { bold: true, color: C.white } },
    { text: "Eligibility · pipeline trace · 4-factor confidence · chart & guideline citations · validation gates · routing reason — all attached to the encounter and audit packet, so every lane is fully explainable.", options: { color: "CADCFC" } },
  ], { x: 0.78, y: 5.78, w: 11.8, h: 1.05, fontFace: BODY, fontSize: 11.5, valign: "middle", margin: 0, lineSpacingMultiple: 1.02 });
  footer(s, 4);
})();

// ───────────────────────── 5 · WHERE AI MAKES THE DIFFERENCE ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Where AI Makes the Difference", "Six places the model earns its keep — and the control on each");
  const rows = [
    ["Chart summarization & extraction", "Reads free-text reports into structured findings, procedures, laterality, contrast — a coder-ready summary."],
    ["Grounded code selection", "Graph-RAG surfaces candidate codes; the agent may only emit what's retrieved — structural hallucination control."],
    ["Cited, defensible coding", "Each code is tied to the chart line and the guideline that justify it; citations are verified before acceptance."],
    ["Self-consistency on hard charts", "Multiple independent passes catch 'confident-but-wrong' on ambiguous or multi-procedure cases."],
    ["Calibrated confidence", "A 4-factor score tells the system when to auto-bill vs. ask a human — the model knows what it doesn't know."],
    ["CDI co-pilot & learning", "Drafts compliant physician queries; learns from coder corrections to improve later charts."],
  ];
  const cw = 6.06, ch2 = 1.5, gx = 0.21, x0 = 0.5, y0 = 1.55;
  rows.forEach((r, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = x0 + col * (cw + gx), y = y0 + row * (ch2 + 0.18);
    card(s, x, y, cw, ch2);
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: y + 0.32, w: 0.86, h: 0.86, fill: { color: C.ice }, line: { type: "none" } });
    s.addText(String(i + 1), { x: x + 0.25, y: y + 0.32, w: 0.86, h: 0.86, fontFace: HEAD, fontSize: 22, bold: true, color: C.tealDk, align: "center", valign: "middle", margin: 0 });
    s.addText(r[0], { x: x + 1.3, y: y + 0.2, w: cw - 1.55, h: 0.4, fontFace: BODY, fontSize: 13.5, bold: true, color: C.navy, margin: 0 });
    s.addText(r[1], { x: x + 1.3, y: y + 0.58, w: cw - 1.55, h: 0.85, fontFace: BODY, fontSize: 11, color: C.muted, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  });
  footer(s, 5);
})();

// ───────────────────────── 6 · TECHNICAL ARCHITECTURE (SYSTEM) ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Technical Architecture", "System view — a self-contained, container-based stack");
  // tiers as horizontal bands
  const bx = 0.5, bw = 12.33;
  function tier(y, h, label, col) {
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y, w: 0.05, h, fill: { color: col }, line: { type: "none" } });
    s.addText(label, { x: bx + 0.12, y: y + 0.04, w: 2.2, h: 0.3, fontFace: BODY, fontSize: 9.5, bold: true, color: col, charSpacing: 1, margin: 0 });
  }
  const box = (x, y, w, h, t, sub, fill, tc) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill: { color: fill }, line: { color: C.line, width: 1 }, shadow: sh() });
    s.addText([
      { text: t, options: { bold: true, fontSize: 11.5, color: tc || C.text, breakLine: true } },
      { text: sub, options: { fontSize: 9, color: tc ? "D7E3F5" : C.muted } },
    ], { x: x + 0.1, y, w: w - 0.2, h, fontFace: BODY, align: "center", valign: "middle", margin: 2, lineSpacingMultiple: 0.95 });
  };
  // tier label sits as a small tag above each band's first box (left rail covers the far left)
  const tlabel = (x, y, label, col) => {
    s.addText(label, { x, y, w: 3.0, h: 0.22, fontFace: BODY, fontSize: 9, bold: true, color: col, charSpacing: 2, margin: 0 });
  };
  // Tier 1: clients / sources
  let y = 1.5;
  tlabel(2.9, y - 0.24, "EDGE", C.slate);
  box(2.9, y, 3.0, 0.8, "Coders / QA / CDI / Admin", "browser (RBAC by role)", C.white);
  box(7.4, y, 4.6, 0.8, "PMS / EHR source systems", "Practice Admin · eClinicalWorks · Cerner", C.white);
  // Tier 2: web
  y = 2.62;
  tlabel(2.9, y - 0.24, "PRESENTATION", C.teal);
  box(2.9, y, 4.2, 0.8, "Web app — React + TypeScript + Vite", "served by nginx (reverse proxy, SSE pass-through)", C.navy, C.white);
  box(7.4, y, 4.6, 0.8, "Integration channels", "FHIR R4 · HL7 v2 · EDI 837/835 · REST / batch", C.white);
  // Tier 3: application / agent
  y = 3.74;
  tlabel(2.9, y - 0.24, "APPLICATION", C.tealDk);
  box(2.9, y, 4.2, 1.2, "FastAPI backend (Python 3.12)", "agentic orchestrator · validation engine · SSE event stream · RBAC + change-log", C.tealDk, C.white);
  box(7.4, y, 2.2, 1.2, "Reasoning model", "Anthropic Claude — Sonnet (default) / Opus (hard)", C.navy, C.white);
  box(9.8, y, 2.2, 1.2, "Honest fallback", "no key → route Manual; never fabricate codes", C.white);
  // Tier 4: data
  y = 5.26;
  tlabel(2.9, y - 0.24, "DATA", C.navy);
  box(2.9, y, 4.2, 1.2, "PostgreSQL 16 + pgvector", "encounters · runs · codes · audit ledger · config", C.navy, C.white);
  box(7.4, y, 4.6, 1.2, "Knowledge & reference store", "payer policies · ontology (KG) · ICD-10 / CPT* / HCPCS · NCCI / MUE / modifiers · guidelines", C.white);
  // left rail note
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.45, w: 2.25, h: 5.15, rectRadius: 0.06, fill: { color: C.ice }, line: { type: "none" } });
  s.addText("Packaging", { x: 0.65, y: 1.6, w: 2.0, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: C.navy, margin: 0 });
  s.addText([
    { text: "Docker Compose", options: { bold: true, color: C.text, breakLine: true, fontSize: 11 } },
    { text: "web · api · db — one command up", options: { color: C.muted, breakLine: true, fontSize: 10 } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "Self-contained & offline", options: { bold: true, color: C.text, breakLine: true, fontSize: 11 } },
    { text: "retrieval, gates and audit run without external services", options: { color: C.muted, breakLine: true, fontSize: 10 } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "Cloud target", options: { bold: true, color: C.text, breakLine: true, fontSize: 11 } },
    { text: "Azure + Azure AI Foundry, US-region, multi-tenant", options: { color: C.muted, fontSize: 10 } },
  ], { x: 0.65, y: 1.95, w: 1.98, h: 4.5, fontFace: BODY, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  s.addText("*CPT shown as a clearly-labeled placeholder; production swaps in the licensed AMA CPT set (same shape).", { x: 2.9, y: 6.62, w: 9.9, h: 0.25, fontFace: BODY, fontSize: 8.5, italic: true, color: C.muted, margin: 0 });
  footer(s, 6);
})();

// ───────────────────────── 7 · THE AGENTIC PIPELINE ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Technical Architecture", "The agentic pipeline — Stage 0 to 5");
  const stages = [
    ["0", "Eligibility", "Deterministic gate: required docs, specialty, exclusions. Ineligible → Manual queue with a reason.", C.slate],
    ["1·2", "Conditioning + Extraction", "One LLM analysis call: chart summary + structured findings, procedures, laterality, contrast.", C.tealDk],
    ["RAG", "Graph-RAG retrieval", "Lexical + ontology-graph traversal + payer policy + learned exemplars → grounded candidate codes.", C.teal],
    ["3", "Cited coding", "Agent emits codes (only from retrieval) with chart + guideline citations. Self-consistency on hard charts.", C.tealDk],
    ["3b", "Citation verification", "Each cited span is checked against the chart; unsupported codes are dropped before validation.", C.navy2],
    ["4", "Validation gates", "Deterministic: NCCI bundling, MUE units, modifier validity, specificity, sex/age, payer necessity.", C.navy2],
    ["5", "Calibrate + route", "4-factor confidence → STB / QA / Manual, with bounded-autonomy hard rules forcing human review.", C.navy],
  ];
  const x0 = 0.5, y0 = 1.5, rowH = 0.64, gap = 0.055, w = 12.33;
  stages.forEach(([n, t, d, col], i) => {
    const y = y0 + i * (rowH + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x0, y, w, h: rowH, rectRadius: 0.05, fill: { color: i % 2 ? C.white : "FBFDFF" }, line: { color: C.line, width: 1 } });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x0 + 0.12, y: y + 0.12, w: 0.95, h: rowH - 0.24, rectRadius: 0.05, fill: { color: col }, line: { type: "none" } });
    s.addText(n, { x: x0 + 0.12, y: y + 0.12, w: 0.95, h: rowH - 0.24, fontFace: HEAD, fontSize: 15, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(t, { x: x0 + 1.25, y, w: 2.95, h: rowH, fontFace: BODY, fontSize: 13, bold: true, color: C.navy, valign: "middle", margin: 0 });
    s.addText(d, { x: x0 + 4.25, y, w: w - 4.45, h: rowH, fontFace: BODY, fontSize: 11, color: C.muted, valign: "middle", margin: 0, lineSpacingMultiple: 0.95 });
  });
  s.addText("Live observability: the orchestrator emits an event per stage over Server-Sent Events — the UI streams the agent's reasoning as it runs.", { x: 0.5, y: y0 + 7 * (rowH + gap) + 0.12, w: 12.33, h: 0.35, fontFace: BODY, fontSize: 10.5, italic: true, color: C.tealDk, margin: 0 });
  footer(s, 7);
})();

// ───────────────────────── 8 · GRAPH-RAG / KG ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Technical Architecture", "Graph-RAG & the knowledge graph — grounding as a control");
  // left: retrieval inputs → agent
  const lx = 0.5, ly = 1.6;
  card(s, lx, ly, 6.0, 5.25);
  s.addText("What grounds every coding decision", { x: lx + 0.3, y: ly + 0.2, w: 5.4, h: 0.4, fontFace: BODY, fontSize: 14, bold: true, color: C.navy, margin: 0 });
  const srcs = [
    ["Code sets (lexical)", "ICD-10-CM / CPT / HCPCS descriptions, specialty- and modality-aware"],
    ["Medical ontology (graph)", "concepts → codes, with is_a / finding_site / causative_agent edges"],
    ["Payer policy", "medical-necessity & prior-auth for the encounter's payer"],
    ["Coding guidelines", "public ICD-10 / NCCI guidance, retrieved and cited"],
    ["Learned exemplars", "applied coder corrections for this chart pattern"],
  ];
  let y = ly + 0.75;
  srcs.forEach(([t, d]) => {
    s.addShape(pres.shapes.RECTANGLE, { x: lx + 0.3, y: y + 0.05, w: 0.12, h: 0.62, fill: { color: C.teal }, line: { type: "none" } });
    s.addText([
      { text: t + "  ", options: { bold: true, color: C.text } },
      { text: d, options: { color: C.muted } },
    ], { x: lx + 0.52, y, w: 5.25, h: 0.78, fontFace: BODY, fontSize: 11, valign: "top", margin: 0, lineSpacingMultiple: 0.98 });
    y += 0.85;
  });
  // right: the principle + KG note
  card(s, 6.8, ly, 6.03, 2.5, C.navy);
  s.addText("The grounding rule", { x: 7.1, y: ly + 0.2, w: 5.4, h: 0.35, fontFace: BODY, fontSize: 14, bold: true, color: C.white, margin: 0 });
  s.addText("The coding agent may only emit codes that retrieval surfaces. If it isn't grounded, it isn't billed.", { x: 7.1, y: ly + 0.62, w: 5.45, h: 0.7, fontFace: BODY, fontSize: 13, color: "E6EEFA", valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  s.addText("This converts hallucination from a prompt-tuning hope into a structural property of the system — and it makes the medical-necessity gate deterministic.", { x: 7.1, y: ly + 1.45, w: 5.45, h: 0.95, fontFace: BODY, fontSize: 11, italic: true, color: "CADCFC", valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  card(s, 6.8, ly + 2.7, 6.03, 2.55, C.ice);
  s.addText("Curated, client-owned knowledge graph", { x: 7.1, y: ly + 2.9, w: 5.4, h: 0.35, fontFace: BODY, fontSize: 14, bold: true, color: C.navy, margin: 0 });
  s.addText([
    { text: "Admins build the KG in-app", options: { bold: true, color: C.text, breakLine: true, fontSize: 11.5 } },
    { text: "add concepts, map them to codes, and wire relationships — read by Graph-RAG on the very next run.", options: { color: C.muted, breakLine: true, fontSize: 11 } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "Production scale", options: { bold: true, color: C.text, breakLine: true, fontSize: 11.5 } },
    { text: "swaps in licensed SNOMED CT / UMLS at the same shape; pgvector reserved for embedding retrieval.", options: { color: C.muted, fontSize: 11 } },
  ], { x: 7.1, y: ly + 3.3, w: 5.45, h: 1.85, fontFace: BODY, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  footer(s, 8);
})();

// ───────────────────────── 9 · VALIDATION / ROUTING / AUTONOMY ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Technical Architecture", "Deterministic validation, calibrated routing & bounded autonomy");
  const colW = 3.97, x0 = 0.5, gap = 0.21, y = 1.6, h = 5.2;
  const cols = [
    ["Deterministic gates", C.navy, [
      "NCCI PTP bundling (hard vs 59/X)",
      "MUE units-per-day",
      "Modifier validity registry",
      "Code specificity / billable",
      "Sex- and age-plausibility",
      "Payer medical-necessity",
    ], "Rules, not vibes — every gate is inspectable and reads live from editable reference tables."],
    ["Calibrated confidence", C.tealDk, [
      "Model certainty",
      "Documentation match",
      "Rule-engine agreement",
      "Historical pattern fit",
      "→ one calibrated score",
      "→ STB / QA / Manual thresholds",
    ], "A 4-factor blend (weights admin-tunable) — far more trustworthy than a raw model probability."],
    ["Bounded autonomy", C.teal, [
      "Critical-care codes",
      "NCCI bundle break / unbundling",
      "Ambiguous or contradictory docs",
      "Blocking conditioning flag",
      "→ forced human review",
      "regardless of confidence",
    ], "Hard ceilings on what may ever auto-bill — the safety net leadership asked for."],
  ];
  cols.forEach(([t, col, items, note], i) => {
    const x = x0 + i * (colW + gap);
    card(s, x, y, colW, h);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: colW, h: 0.62, fill: { color: col }, line: { type: "none" } });
    // round top corners visually by overlaying nothing; keep simple
    s.addText(t, { x: x + 0.2, y, w: colW - 0.4, h: 0.62, fontFace: BODY, fontSize: 14, bold: true, color: C.white, valign: "middle", margin: 0 });
    let yy = y + 0.85;
    items.forEach((it) => {
      const arrow = it.startsWith("→");
      s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: yy + 0.08, w: 0.13, h: 0.13, fill: { color: arrow ? C.amber : col }, line: { type: "none" } });
      s.addText(it.replace("→ ", ""), { x: x + 0.5, y: yy, w: colW - 0.7, h: 0.4, fontFace: BODY, fontSize: 11.5, bold: arrow, color: arrow ? C.text : C.muted, valign: "top", margin: 0 });
      yy += 0.5;
    });
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.2, y: yy + 0.05, w: colW - 0.4, h: 0.02, fill: { color: C.line }, line: { type: "none" } });
    s.addText(note, { x: x + 0.22, y: yy + 0.15, w: colW - 0.42, h: 1.1, fontFace: BODY, fontSize: 10.5, italic: true, color: C.tealDk, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  });
  footer(s, 9);
})();

// ───────────────────────── 10 · DEFENSIBILITY & GOVERNANCE ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Trust by Design", "Defensibility & governance — built in, not bolted on");
  const items = [
    ["Per-code citations", "Every accepted code links to the chart line and the guideline that justify it; coders see why."],
    ["Append-only audit packet", "Stage, actor, model version and timestamps — your RAC-audit defense, generated automatically."],
    ["Governance change log", "Every admin edit (config, policy, KG, reference data, golden set) recorded with who & when, by role."],
    ["Evaluation harness", "Accuracy reported against adjudicated consensus with the inter-rater reliability ceiling — honest, not inflated."],
    ["Coder override + reason", "Human edits are captured with rationale, feeding the learning loop and the audit trail."],
    ["RBAC by role", "Admin / Coder / QA / CDI / Supervisor — navigation and every action gated; maps to SSO in production."],
  ];
  const cw = 6.06, chh = 1.5, gx = 0.21, x0 = 0.5, y0 = 1.55;
  items.forEach((r, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = x0 + col * (cw + gx), y = y0 + row * (chh + 0.18);
    card(s, x, y, cw, chh);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.13, h: chh, fill: { color: C.teal }, line: { type: "none" } });
    s.addText(r[0], { x: x + 0.35, y: y + 0.2, w: cw - 0.6, h: 0.4, fontFace: BODY, fontSize: 14, bold: true, color: C.navy, margin: 0 });
    s.addText(r[1], { x: x + 0.35, y: y + 0.62, w: cw - 0.6, h: 0.8, fontFace: BODY, fontSize: 11.5, color: C.muted, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  });
  footer(s, 10);
})();

// ───────────────────────── 11 · ARCHITECTURE REASONING & OPTIONS ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Design Rationale", "Architecture decisions — options considered & why we chose");
  const rows = [
    ["Reasoning engine", "Local NLP / SLM (BioBERT, MedSpaCy)  ·  frontier LLM  ·  hybrid", "Frontier Claude now for accuracy, reasoning & citations; roadmap distills to US-region SLMs for cost / latency / residency."],
    ["Hallucination control", "Prompt-only  ·  plain RAG  ·  Graph-RAG + deterministic gates", "Graph-RAG grounding + gates — the agent can only emit retrieved codes; structural, not a prompt-tuning hope."],
    ["Confidence & routing", "Raw model probability  ·  calibrated multi-factor", "Calibrated 4-factor score — trustworthy STB / QA / Manual thresholds the business can set."],
    ["Validation", "LLM self-check  ·  deterministic rule engine", "Deterministic engine for auditability — NCCI / MUE / modifier / payer are rules, fully inspectable."],
    ["Knowledge store", "Dedicated vector DB  ·  PostgreSQL + pgvector", "One transactional store — simpler ops, no extra service; pgvector reserved for embedding retrieval."],
    ["Autonomy model", "Full auto  ·  human-in-loop  ·  bounded autonomy", "Bounded autonomy — hard rules force review (critical care, NCCI break, ambiguity) regardless of score."],
    ["Configurability", "Hardcoded thresholds  ·  runtime config store", "DB-backed config — admins tune routing, gates, SLAs, the KG & roles with no redeploy."],
    ["Hard-chart accuracy", "Always self-consistency  ·  never  ·  targeted", "Targeted self-consistency only on hard charts — accuracy where it matters, cost controlled."],
  ];
  const x0 = 0.5, y0 = 1.5, w = 12.33;
  const cW = [2.5, 4.5, 5.33];
  // header row
  s.addShape(pres.shapes.RECTANGLE, { x: x0, y: y0, w, h: 0.42, fill: { color: C.navy }, line: { type: "none" } });
  ["Decision", "Options considered", "Choice & rationale"].forEach((t, i) => {
    const cx = x0 + cW.slice(0, i).reduce((a, b) => a + b, 0);
    s.addText(t, { x: cx + 0.15, y: y0, w: cW[i] - 0.2, h: 0.42, fontFace: BODY, fontSize: 11.5, bold: true, color: C.white, valign: "middle", margin: 0 });
  });
  let y = y0 + 0.42;
  const rh = 0.6;
  rows.forEach((r, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: x0, y, w, h: rh, fill: { color: i % 2 ? "FFFFFF" : "EFF4FA" }, line: { color: C.line, width: 0.75 } });
    s.addText(r[0], { x: x0 + 0.15, y, w: cW[0] - 0.2, h: rh, fontFace: BODY, fontSize: 11, bold: true, color: C.navy, valign: "middle", margin: 0 });
    s.addText(r[1], { x: x0 + cW[0] + 0.15, y, w: cW[1] - 0.25, h: rh, fontFace: BODY, fontSize: 10, color: C.muted, valign: "middle", margin: 0, lineSpacingMultiple: 0.92 });
    s.addText(r[2], { x: x0 + cW[0] + cW[1] + 0.15, y, w: cW[2] - 0.25, h: rh, fontFace: BODY, fontSize: 10, color: C.text, valign: "middle", margin: 0, lineSpacingMultiple: 0.92 });
    y += rh;
  });
  footer(s, 11);
})();

// ───────────────────────── 12 · SECURITY / DEPLOYMENT ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Security, Deployment & Data", "Production posture and the licensing reality");
  const cols = [
    ["Deployment & residency", C.navy, [
      "Azure + Azure AI Foundry; US-region mandatory",
      "Multi-tenant with strict no co-mingling",
      "Docker today → AKS / container apps in cloud",
      "SLM distillation for cost, latency & data residency",
    ]],
    ["Data & secrets", C.tealDk, [
      "Synthetic, PHI-free charts in the demo",
      "Single secret (model API key) in env, never in git",
      "Audit ledger + change log for traceability",
      "SOC 2 controls & encryption at deployment",
    ]],
    ["Licensing reality", C.teal, [
      "Public now: ICD-10-CM / HCPCS / NCCI / MUE / guidelines",
      "CPT (AMA) = labeled placeholder → client license in prod",
      "Ontology: demo set → licensed SNOMED CT / UMLS",
      "Same data shapes — a swap, not a rebuild",
    ]],
  ];
  const colW = 3.97, x0 = 0.5, gap = 0.21, y = 1.6, h = 4.4;
  cols.forEach(([t, col, items], i) => {
    const x = x0 + i * (colW + gap);
    card(s, x, y, colW, h);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: colW, h: 0.62, fill: { color: col }, line: { type: "none" } });
    s.addText(t, { x: x + 0.2, y, w: colW - 0.4, h: 0.62, fontFace: BODY, fontSize: 13.5, bold: true, color: C.white, valign: "middle", margin: 0 });
    let yy = y + 0.85;
    items.forEach((it) => {
      s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: yy + 0.07, w: 0.13, h: 0.13, fill: { color: col }, line: { type: "none" } });
      s.addText(it, { x: x + 0.5, y: yy, w: colW - 0.72, h: 0.78, fontFace: BODY, fontSize: 11, color: C.muted, valign: "top", margin: 0, lineSpacingMultiple: 0.98 });
      yy += 0.82;
    });
  });
  // bottom strip: honest residuals
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 6.15, w: 12.33, h: 0.75, rectRadius: 0.06, fill: { color: C.ice }, line: { type: "none" } });
  s.addText([
    { text: "Honest about demo-scale:  ", options: { bold: true, color: C.navy } },
    { text: "mechanisms are real; gold-chart volume, SLM retraining and denial-prevention scale post-demo — nothing is faked, and the fallback never invents codes.", options: { color: C.text } },
  ], { x: 0.75, y: 6.15, w: 11.9, h: 0.75, fontFace: BODY, fontSize: 11, valign: "middle", margin: 0, lineSpacingMultiple: 0.98 });
  footer(s, 12);
})();

// ───────────────────────── 13 · ROADMAP ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Adoption Path", "A maturity ramp — earn autonomy, don't assume it");
  const phases = [
    ["Shadow", "AI codes alongside coders; 100% human audit. Calibrate, build the gold set, prove accuracy.", C.slate],
    ["STB pilot", "Turn on Straight-Through Billing for high-confidence lanes; QA samples taper as certification holds.", C.tealDk],
    ["Scale", "Expand specialties via the accelerator; STB rate climbs toward ≥ 80% as the model is certified at ≥ 95%.", C.navy],
  ];
  const y = 2.0, bw = 3.85, gap = 0.5, x0 = 0.65, bh = 2.5;
  phases.forEach(([t, d, col], i) => {
    const x = x0 + i * (bw + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, rectRadius: 0.07, fill: { color: C.white }, line: { color: C.line, width: 1 }, shadow: sh() });
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: bw, h: 0.12, fill: { color: col }, line: { type: "none" } });
    s.addShape(pres.shapes.OVAL, { x: x + bw / 2 - 0.45, y: y + 0.4, w: 0.9, h: 0.9, fill: { color: col }, line: { type: "none" } });
    s.addText(String(i + 1), { x: x + bw / 2 - 0.45, y: y + 0.4, w: 0.9, h: 0.9, fontFace: HEAD, fontSize: 26, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(t, { x: x + 0.2, y: y + 1.4, w: bw - 0.4, h: 0.4, fontFace: BODY, fontSize: 16, bold: true, color: C.navy, align: "center", margin: 0 });
    s.addText(d, { x: x + 0.25, y: y + 1.82, w: bw - 0.5, h: 0.6, fontFace: BODY, fontSize: 10.8, color: C.muted, align: "center", valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
    if (i < 2) arrow(s, x + bw + 0.07, y + bh / 2, gap - 0.14);
  });
  // KPI ribbon
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.65, y: 5.0, w: 12.03, h: 1.6, rectRadius: 0.06, fill: { color: C.navy }, line: { type: "none" } });
  s.addText("What moves at each step", { x: 0.9, y: 5.12, w: 11, h: 0.35, fontFace: BODY, fontSize: 13, bold: true, color: C.white, margin: 0 });
  const k = [["Chart accuracy", "≥ 90% SLA"], ["STB rate", "→ ≥ 80%"], ["Manual effort", "− ≥ 30%"], ["Turnaround", "− 10–15%"]];
  k.forEach(([l, v], i) => {
    const x = 0.95 + i * 3.0;
    s.addText(v, { x, y: 5.5, w: 2.8, h: 0.55, fontFace: HEAD, fontSize: 22, bold: true, color: C.teal, margin: 0 });
    s.addText(l, { x, y: 6.05, w: 2.8, h: 0.4, fontFace: BODY, fontSize: 11, color: "CADCFC", margin: 0 });
  });
  footer(s, 13);
})();

// ───────────────────────── 14 · WHY NOUS / CLOSE ─────────────────────────
(() => {
  const s = pres.addSlide();
  s.background = { color: C.bgDark };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: C.teal }, line: { type: "none" } });
  s.addText("WHY NOUS", { x: 0.8, y: 0.7, w: 10, h: 0.4, fontFace: BODY, fontSize: 13, bold: true, color: C.teal, charSpacing: 3, margin: 0 });
  s.addText("Not a model — a defensible, configurable platform", { x: 0.8, y: 1.15, w: 11.8, h: 0.9, fontFace: HEAD, fontSize: 28, bold: true, color: C.white, margin: 0 });
  const items = [
    ["Eval & calibration harness", "Honest accuracy vs. adjudicated consensus — the trust instrument that lets autonomy grow safely."],
    ["Defensibility engine", "Citations + deterministic gates + audit packet — every claim is auditable."],
    ["Specialty accelerator", "New specialties onboard via config + a gold set, not a rebuild."],
    ["Graph-RAG curation", "A client-owned knowledge graph, built and governed in-app."],
    ["Configurable platform & operating model", "Runtime control of routing, gates, SLAs, roles — plus the control-tower & governance ramp."],
    ["RevAmp-native", "Designed to live inside Vee Healthtek's coding ecosystem."],
  ];
  const cw = 5.9, chh = 1.18, x0 = 0.8, y0 = 2.3, gx = 0.3;
  items.forEach((r, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = x0 + col * (cw + gx), y = y0 + row * (chh + 0.16);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: chh, rectRadius: 0.06, fill: { color: C.navy }, line: { type: "none" } });
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.12, h: chh, fill: { color: C.teal }, line: { type: "none" } });
    s.addText(r[0], { x: x + 0.32, y: y + 0.14, w: cw - 0.5, h: 0.4, fontFace: BODY, fontSize: 13, bold: true, color: C.white, margin: 0 });
    s.addText(r[1], { x: x + 0.32, y: y + 0.5, w: cw - 0.5, h: 0.62, fontFace: BODY, fontSize: 10.5, color: "AFC0D8", valign: "top", margin: 0, lineSpacingMultiple: 0.98 });
  });
  s.addText("Working today, not slideware — and built to earn autonomy chart by chart.", { x: 0.8, y: 6.75, w: 11.8, h: 0.5, fontFace: BODY, fontSize: 14, italic: true, color: "CADCFC", margin: 0 });
})();

pres.writeFile({ fileName: "ACE_Architecture.pptx" }).then((f) => console.log("WROTE", f));
