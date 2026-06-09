/* ACE — Autonomous Coding Engine: Functional Flow + Technical Architecture deck.
   Run: node build_deck.js  ->  ACE_Architecture.pptx */
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "Nous Infosystems";
pres.company = "Nous Infosystems";
pres.title = "ACE — Autonomous Coding Engine";

const W = 13.33, H = 7.5;
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
function header(slide, kicker, title) {
  slide.background = { color: C.light };
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 1.18, fill: { color: C.white }, line: { type: "none" } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 1.18, w: W, h: 0.03, fill: { color: C.line }, line: { type: "none" } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.34, w: 0.12, h: 0.56, fill: { color: C.teal }, line: { type: "none" } });
  slide.addText(kicker.toUpperCase(), { x: 0.78, y: 0.30, w: 11, h: 0.26, fontFace: BODY, fontSize: 11, color: C.teal, bold: true, charSpacing: 2, margin: 0 });
  slide.addText(title, { x: 0.78, y: 0.52, w: 12.2, h: 0.5, fontFace: HEAD, fontSize: 23, color: C.navy, bold: true, margin: 0 });
}
const sh = () => ({ type: "outer", color: "1B2A4A", blur: 7, offset: 3, angle: 135, opacity: 0.12 });
function card(slide, x, y, w, h, fill) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.07, fill: { color: fill || C.card }, line: { color: C.line, width: 1 }, shadow: sh() });
}
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
  // motif: clean circles bleeding off the right edge (no distorted boxes)
  s.addShape(pres.shapes.OVAL, { x: 9.5, y: -2.7, w: 7.2, h: 7.2, fill: { color: C.navy2, transparency: 45 }, line: { type: "none" } });
  s.addShape(pres.shapes.OVAL, { x: 11.2, y: 3.1, w: 5.0, h: 5.0, fill: { color: C.navy2, transparency: 62 }, line: { type: "none" } });
  s.addShape(pres.shapes.OVAL, { x: 11.0, y: 0.7, w: 3.2, h: 3.2, fill: { color: C.teal, transparency: 86 }, line: { type: "none" } });
  s.addText("NOUS INFOSYSTEMS   ·   FOR VEE HEALTHTEK", { x: 0.8, y: 1.5, w: 10, h: 0.4, fontFace: BODY, fontSize: 13, color: C.teal, bold: true, charSpacing: 3, margin: 0 });
  s.addText("ACE — Autonomous Coding Engine", { x: 0.8, y: 2.15, w: 11.4, h: 1.1, fontFace: HEAD, fontSize: 44, color: C.white, bold: true, margin: 0 });
  s.addText("Agentic AI that turns clinical notes into billable codes", { x: 0.8, y: 3.35, w: 11, h: 0.6, fontFace: BODY, fontSize: 20, color: "CADCFC", margin: 0 });
  s.addText("Functional flow  ·  Technical architecture  ·  Design rationale", { x: 0.82, y: 4.05, w: 11, h: 0.5, fontFace: BODY, fontSize: 14, italic: true, color: "9FB0C7", margin: 0 });
  const chips = ["Reads like a coder", "Cites every code", "Knows when to ask", "Yours to configure"];
  let cx = 0.8;
  chips.forEach((t) => {
    const w = 0.5 + t.length * 0.097;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: 5.15, w, h: 0.46, rectRadius: 0.23, fill: { color: C.navy2 }, line: { color: C.teal, width: 1 } });
    s.addText(t, { x: cx, y: 5.15, w, h: 0.46, fontFace: BODY, fontSize: 10.5, color: "E6EEFA", align: "center", valign: "middle", margin: 0 });
    cx += w + 0.22;
  });
  s.addText("In-person demo · Bangalore · June 2026", { x: 0.8, y: 6.6, w: 11, h: 0.4, fontFace: BODY, fontSize: 11, color: "7E90A8", margin: 0 });
})();

// ───────────────────────── 2 · WHY WE BUILT THIS ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Why We Built This", "Turning clinical notes into clean claims — without losing trust");
  const colY = 1.55;
  card(s, 0.5, colY, 6.05, 5.2);
  s.addText("What makes coding hard", { x: 0.8, y: colY + 0.2, w: 5.5, h: 0.4, fontFace: BODY, fontSize: 15, bold: true, color: C.navy, margin: 0 });
  const ch = [
    ["From notes to codes.", "A clinician writes the story; someone has to turn it into the exact ICD-10, CPT and HCPCS — and get the specificity, bundling and modifiers right."],
    ["Mistakes are costly.", "A wrong code means a denial, a compliance question, or rework. Good coders are hard to find, and everything they touch is audited."],
    ["There's never enough time.", "Volumes are high and turnaround matters. Coder time is the real cost."],
    ["AI has to earn trust.", "Nobody lets a black box bill a claim. People want to see the reasoning before they hand over control."],
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
  card(s, 6.8, colY, 6.03, 5.2, C.navy);
  s.addText("How you'll know it's working", { x: 7.1, y: colY + 0.2, w: 5.4, h: 0.4, fontFace: BODY, fontSize: 15, bold: true, color: C.white, margin: 0 });
  s.addText("These grow over time — they're not a day-one cliff", { x: 7.1, y: colY + 0.58, w: 5.4, h: 0.3, fontFace: BODY, fontSize: 10.5, italic: true, color: "9FB0C7", margin: 0 });
  const kpi = [
    ["≥ 90%", "accuracy across the whole chart"],
    ["≥ 80%", "billed with no human touch, once earned"],
    ["≥ 30%", "less manual coding effort"],
    ["10–15%", "faster turnaround"],
  ];
  let ky = colY + 1.0;
  kpi.forEach(([n, l]) => {
    s.addText(n, { x: 7.1, y: ky, w: 2.0, h: 0.62, fontFace: HEAD, fontSize: 27, bold: true, color: C.teal, valign: "middle", margin: 0 });
    s.addText(l, { x: 9.15, y: ky, w: 3.5, h: 0.62, fontFace: BODY, fontSize: 11.5, color: "E6EEFA", valign: "middle", margin: 0 });
    ky += 0.8;
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 7.1, y: ky + 0.05, w: 5.4, h: 0.02, fill: { color: "3A4D72" }, line: { type: "none" } });
  s.addText("We start with a human checking every chart, certify the model once it holds 95%+, then ease off the sampling.", { x: 7.1, y: ky + 0.18, w: 5.45, h: 0.6, fontFace: BODY, fontSize: 10.5, italic: true, color: "CADCFC", valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  footer(s, 2);
})();

// ───────────────────────── 3 · WHAT WE HEARD FROM VEE ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "What We Heard From Vee", "What you asked for — and how ACE answers it");
  s.addText("From the working session with Amrish (CTAIO), Michelle (CPTO) and the team, plus the SOW and use-case documents.",
    { x: 0.5, y: 1.28, w: 12.33, h: 0.3, fontFace: BODY, fontSize: 10.5, italic: true, color: C.muted, margin: 0 });
  const rows = [
    ["Keep the model honest with a knowledge graph and agentic RAG over payer policy, medical necessity and clinical ontologies.",
     "Graph-RAG grounds every code; the ontology, payer policies and guidelines are built and curated right in the app."],
    ["Summarise the chart for the coder.",
     "Each chart opens with a plain-language summary and structured extraction."],
    ["Colour-code confidence, and make everything observable and traceable.",
     "Three colour-coded lanes, a live agent trace, and a 'knowledge used for this chart' panel."],
    ["Let coders override — and capture the reason.",
     "One-click accept or override with a reason, saved to the audit trail and the learning loop."],
    ["Close the loop in batch, and flag invalid or 'junk' codes.",
     "Corrections become exemplars that shift later charts; deterministic gates reject impossible codes before billing."],
    ["Fine-tune and distil to smaller models on Azure AI Foundry, US-region.",
     "Frontier model today, with a clear path to US-region SLMs — the architecture is ready for it."],
    ["Start with Radiology, expand to E&M, ED and Pathology, and move quickly.",
     "Radiology-led and already multi-specialty; new specialties onboard via config, not a rebuild."],
  ];
  const x0 = 0.5, w = 12.33, cW = [5.6, 6.73], y0 = 1.72, rh = 0.66;
  s.addShape(pres.shapes.RECTANGLE, { x: x0, y: y0, w, h: 0.4, fill: { color: C.navy }, line: { type: "none" } });
  s.addText("You told us", { x: x0 + 0.18, y: y0, w: cW[0] - 0.3, h: 0.4, fontFace: BODY, fontSize: 11.5, bold: true, color: C.white, valign: "middle", margin: 0 });
  s.addText("What ACE does today", { x: x0 + cW[0] + 0.18, y: y0, w: cW[1] - 0.3, h: 0.4, fontFace: BODY, fontSize: 11.5, bold: true, color: C.teal, valign: "middle", margin: 0 });
  let y = y0 + 0.4;
  rows.forEach((r, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: x0, y, w, h: rh, fill: { color: i % 2 ? "FFFFFF" : "EFF4FA" }, line: { color: C.line, width: 0.75 } });
    s.addShape(pres.shapes.RECTANGLE, { x: x0 + cW[0], y: y + 0.1, w: 0.02, h: rh - 0.2, fill: { color: C.line }, line: { type: "none" } });
    s.addText(r[0], { x: x0 + 0.18, y, w: cW[0] - 0.36, h: rh, fontFace: BODY, fontSize: 10.5, color: C.text, valign: "middle", margin: 0, lineSpacingMultiple: 0.95 });
    s.addText(r[1], { x: x0 + cW[0] + 0.18, y, w: cW[1] - 0.36, h: rh, fontFace: BODY, fontSize: 10.5, color: C.tealDk, valign: "middle", margin: 0, lineSpacingMultiple: 0.95 });
    y += rh;
  });
  footer(s, 3);
})();

// ───────────────────────── 4 · AT A GLANCE ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "The Idea", "ACE in four parts");
  const items = [
    ["01", "Codes like a careful coder", "It reads the chart, pulls out what matters, picks the codes, checks the rules, and only then decides if it's safe to bill — and you can watch it work."],
    ["02", "Shows its work", "Every code points back to a line in the chart and the rule behind it, with an audit trail you could hand to an auditor."],
    ["03", "Knows when to ask", "A confidence score it actually trusts sends each chart to auto-bill, a quick QA check, or a coder. Some calls always go to a person."],
    ["04", "Yours to run", "Your team tunes the thresholds, the rules, the knowledge graph, the specialties and who can do what — no code, no redeploy."],
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
  footer(s, 4);
})();

// ───────────────────────── 5 · FUNCTIONAL FLOW ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Functional Flow", "How a chart moves — from intake to billing, with a feedback loop");
  const y = 1.5, bh = 0.92, bw = 1.95;
  const xs = [0.5, 2.62, 4.74, 6.86, 8.98];
  flowBox(s, xs[0], y, bw, bh, "Intake", "from the PMS / EHR (FHIR · HL7 · EDI)", C.navy);
  flowBox(s, xs[1], y, bw, bh, "Is it codable?", "right docs, right specialty, no exclusions", C.navy);
  flowBox(s, xs[2], y, bw, bh, "ACE codes it", "read → extract → code → check", C.tealDk);
  flowBox(s, xs[3], y, bw, bh, "How sure is it?", "a confidence score it trusts", C.navy);
  flowBox(s, xs[4], y, 3.85, bh, "Billing / clearinghouse", "claim goes out (837)", C.navy);
  [0, 1, 2, 3].forEach((i) => arrow(s, xs[i] + bw, y + bh / 2, xs[i + 1] - xs[i] - bw));

  s.addText([
    { text: "Based on how sure it is, ", options: { color: C.muted } },
    { text: "each chart goes to exactly one of three lanes:", options: { bold: true, color: C.navy } },
  ], { x: 0.5, y: 2.62, w: 12.33, h: 0.3, fontFace: BODY, fontSize: 12, margin: 0 });
  const ly = 3.02, lh = 0.95, lw = 3.95, lgap = 0.24;
  const lxs = [0.5, 0.5 + lw + lgap, 0.5 + 2 * (lw + lgap)];
  const lanes = [
    ["Straight-through billing", "high confidence — bills automatically, audit-sampled", C.green],
    ["Quick QA check", "an auditor confirms the AI's draft", C.amber],
    ["Coder does it", "AI hands over a head start, a person finishes", C.slate],
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
  const cy = 4.28, ch2 = 1.22, cw2 = 6.06;
  card(s, 0.5, cy, cw2, ch2, C.ice);
  s.addText("If the notes fall short — a physician query", { x: 0.72, y: cy + 0.13, w: cw2 - 0.4, h: 0.3, fontFace: BODY, fontSize: 12.5, bold: true, color: C.navy, margin: 0 });
  s.addText("When the documentation can't support a more specific code, ACE writes a compliant, non-leading question for the physician. Their answer re-codes the chart.", { x: 0.72, y: cy + 0.47, w: cw2 - 0.45, h: 0.72, fontFace: BODY, fontSize: 11, color: C.muted, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  card(s, 0.5 + cw2 + 0.21, cy, cw2, ch2, C.ice);
  s.addText("It gets better over time — the feedback loop", { x: 0.72 + cw2 + 0.21, y: cy + 0.13, w: cw2 - 0.4, h: 0.3, fontFace: BODY, fontSize: 12.5, bold: true, color: C.navy, margin: 0 });
  s.addText("When a coder corrects ACE, that correction quietly improves the next similar chart (batched every 24–48 hours in production).", { x: 0.72 + cw2 + 0.21, y: cy + 0.47, w: cw2 - 0.45, h: 0.72, fontFace: BODY, fontSize: 11, color: C.muted, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 5.78, w: 12.33, h: 1.05, rectRadius: 0.06, fill: { color: C.navy }, line: { type: "none" } });
  s.addText([
    { text: "Everything travels with the chart.  ", options: { bold: true, color: C.white } },
    { text: "The summary, the agent's trace, the confidence score, the citations, the checks and the reason it landed where it did — all attached to the encounter, so any lane can be explained in seconds.", options: { color: "CADCFC" } },
  ], { x: 0.78, y: 5.78, w: 11.8, h: 1.05, fontFace: BODY, fontSize: 11.5, valign: "middle", margin: 0, lineSpacingMultiple: 1.02 });
  footer(s, 5);
})();

// ───────────────────────── 6 · WHAT THE AI ACTUALLY DOES ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "What the AI Actually Does", "Six places the model does the heavy lifting");
  const rows = [
    ["Reads and summarises the chart", "Turns a free-text report into structured findings, procedures, laterality and contrast — a summary a coder can scan in seconds."],
    ["Picks codes it can back up", "It can only choose from codes the knowledge graph surfaced, so it can't invent one."],
    ["Cites every code", "Each code is tied to the line in the chart and the guideline behind it — and those citations are checked before anything is accepted."],
    ["Double-checks the hard ones", "On ambiguous or multi-procedure charts it codes more than once and compares, catching the confident-but-wrong cases."],
    ["Knows when it's unsure", "A confidence score decides whether to auto-bill or hand it to a person. The model knows what it doesn't know."],
    ["Helps with queries, and learns", "Drafts compliant physician queries, and gets a little better with every coder correction."],
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
  footer(s, 6);
})();

// ───────────────────────── 7 · SYSTEM ARCHITECTURE ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Technical Architecture", "How it's put together — one self-contained stack");
  const box = (x, y, w, h, t, sub, fill, tc) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill: { color: fill }, line: { color: C.line, width: 1 }, shadow: sh() });
    s.addText([
      { text: t, options: { bold: true, fontSize: 11.5, color: tc || C.text, breakLine: true } },
      { text: sub, options: { fontSize: 9, color: tc ? "D7E3F5" : C.muted } },
    ], { x: x + 0.1, y, w: w - 0.2, h, fontFace: BODY, align: "center", valign: "middle", margin: 2, lineSpacingMultiple: 0.95 });
  };
  const tlabel = (x, y, label, col) => {
    s.addText(label, { x, y, w: 3.0, h: 0.22, fontFace: BODY, fontSize: 9, bold: true, color: col, charSpacing: 2, margin: 0 });
  };
  let y = 1.46;
  tlabel(2.9, y - 0.24, "WHO USES IT", C.slate);
  box(2.9, y, 3.0, 0.76, "Coders / QA / CDI / Admin", "in the browser, gated by role", C.white);
  box(7.4, y, 4.6, 0.76, "PMS / EHR source systems", "Practice Admin · eClinicalWorks · Cerner", C.white);
  y = 2.56;
  tlabel(2.9, y - 0.24, "WHAT THEY SEE", C.teal);
  box(2.9, y, 4.2, 0.76, "Web app — React + TypeScript + Vite", "served by nginx (also passes the live agent stream)", C.navy, C.white);
  box(7.4, y, 4.6, 0.76, "Integration channels", "FHIR R4 · HL7 v2 · EDI 837/835 · REST / batch", C.white);
  y = 3.66;
  tlabel(2.9, y - 0.24, "WHERE THE WORK HAPPENS", C.tealDk);
  box(2.9, y, 4.2, 1.08, "FastAPI backend (Python 3.12)", "the coding agent, the rule checks, the live trace, roles and the change log", C.tealDk, C.white);
  box(7.4, y, 2.2, 1.08, "Reasoning model", "Anthropic Claude — Sonnet by default, Opus on hard charts", C.navy, C.white);
  box(9.8, y, 2.2, 1.08, "Safe fallback", "no model key? it routes to a human instead of guessing", C.white);
  y = 4.96;
  tlabel(2.9, y - 0.24, "WHAT IT KNOWS", C.navy);
  box(2.9, y, 4.2, 1.08, "PostgreSQL 16 + pgvector", "encounters, runs, codes, the audit trail and settings", C.navy, C.white);
  box(7.4, y, 4.6, 1.08, "Knowledge & reference store", "payer policies · the ontology (KG) · ICD-10 / CPT* / HCPCS · NCCI / MUE / modifiers · guidelines", C.white);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.42, w: 2.25, h: 4.62, rectRadius: 0.06, fill: { color: C.ice }, line: { type: "none" } });
  s.addText("How it ships", { x: 0.65, y: 1.6, w: 2.0, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: C.navy, margin: 0 });
  s.addText([
    { text: "One Docker command", options: { bold: true, color: C.text, breakLine: true, fontSize: 11 } },
    { text: "web, api and database come up together", options: { color: C.muted, breakLine: true, fontSize: 10 } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "Runs on its own", options: { bold: true, color: C.text, breakLine: true, fontSize: 11 } },
    { text: "retrieval, the checks and the audit trail need no outside services", options: { color: C.muted, breakLine: true, fontSize: 10 } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "Built for your cloud", options: { bold: true, color: C.text, breakLine: true, fontSize: 11 } },
    { text: "Azure + Azure AI Foundry, US-region, multi-tenant", options: { color: C.muted, fontSize: 10 } },
  ], { x: 0.65, y: 1.95, w: 1.98, h: 4.5, fontFace: BODY, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  s.addText("*CPT is shown as a clearly-labelled placeholder; in production we drop in your licensed AMA CPT set — same shape.", { x: 2.9, y: 6.34, w: 9.9, h: 0.25, fontFace: BODY, fontSize: 8.5, italic: true, color: C.muted, margin: 0 });
  footer(s, 7);
})();

// ───────────────────────── 8 · THE AGENTIC PIPELINE ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Technical Architecture", "Inside the coding agent — the steps it runs, in order");
  const stages = [
    ["0", "Is it codable?", "A plain rule check: right documents, supported specialty, no exclusions. If not, it goes to a coder with the reason.", C.slate],
    ["1·2", "Read & extract", "One model call reads the chart and pulls out the findings, procedures, laterality and contrast in structured form.", C.tealDk],
    ["RAG", "Find candidate codes", "Graph-RAG pulls candidates from the code sets, the ontology, payer policy and past corrections — the only codes it may use.", C.teal],
    ["3", "Code it, with citations", "It picks codes and cites the chart line and guideline for each. Hard charts get a second, independent pass.", C.tealDk],
    ["3b", "Check the citations", "Every cited line is verified against the chart; anything unsupported is dropped before the rules run.", C.navy2],
    ["4", "Run the rule checks", "Plain, deterministic checks: NCCI bundling, MUE units, valid modifiers, specificity, sex/age, payer necessity.", C.navy2],
    ["5", "Score & route", "A confidence score sends it to auto-bill, QA or a coder — with hard limits that always send certain cases to a person.", C.navy],
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
  s.addText("You can watch all of this happen — the app streams each step live as the agent runs.", { x: 0.5, y: y0 + 7 * (rowH + gap) + 0.12, w: 12.33, h: 0.35, fontFace: BODY, fontSize: 10.5, italic: true, color: C.tealDk, margin: 0 });
  footer(s, 8);
})();

// ───────────────────────── 9 · GRAPH-RAG / KG ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Technical Architecture", "Graph-RAG & the knowledge graph — why the model can't go off-script");
  const lx = 0.5, ly = 1.6;
  card(s, lx, ly, 6.0, 5.25);
  s.addText("What grounds every coding decision", { x: lx + 0.3, y: ly + 0.2, w: 5.4, h: 0.4, fontFace: BODY, fontSize: 14, bold: true, color: C.navy, margin: 0 });
  const srcs = [
    ["The code sets", "ICD-10-CM, CPT and HCPCS descriptions, matched to the specialty and modality"],
    ["The medical ontology", "clinical concepts linked to codes and to each other (is-a, finding-site, caused-by)"],
    ["Payer policy", "medical-necessity and prior-auth rules for that chart's payer"],
    ["Coding guidelines", "public ICD-10 / NCCI guidance, pulled in and cited"],
    ["Past corrections", "what your coders fixed on charts like this one"],
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
  card(s, 6.8, ly, 6.03, 2.5, C.navy);
  s.addText("The one rule that matters", { x: 7.1, y: ly + 0.2, w: 5.4, h: 0.35, fontFace: BODY, fontSize: 14, bold: true, color: C.white, margin: 0 });
  s.addText("The agent can only use codes that retrieval brings back. If a code isn't grounded, it doesn't get billed.", { x: 7.1, y: ly + 0.62, w: 5.45, h: 0.7, fontFace: BODY, fontSize: 13, color: "E6EEFA", valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  s.addText("That turns 'don't make things up' from a hope into a property of the system — and it's what lets the medical-necessity check be a plain, deterministic rule.", { x: 7.1, y: ly + 1.45, w: 5.45, h: 0.95, fontFace: BODY, fontSize: 11, italic: true, color: "CADCFC", valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  card(s, 6.8, ly + 2.7, 6.03, 2.55, C.ice);
  s.addText("A knowledge graph your team owns", { x: 7.1, y: ly + 2.9, w: 5.4, h: 0.35, fontFace: BODY, fontSize: 14, bold: true, color: C.navy, margin: 0 });
  s.addText([
    { text: "Built and curated in the app.  ", options: { bold: true, color: C.text, breakLine: true, fontSize: 11.5 } },
    { text: "Add a concept, map it to codes, draw a relationship — and the agent uses it on the very next chart.", options: { color: C.muted, breakLine: true, fontSize: 11 } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "At production scale,  ", options: { bold: true, color: C.text, breakLine: true, fontSize: 11.5 } },
    { text: "we drop in licensed SNOMED CT / UMLS in the same shape; pgvector is ready for embedding search.", options: { color: C.muted, fontSize: 11 } },
  ], { x: 7.1, y: ly + 3.3, w: 5.45, h: 1.85, fontFace: BODY, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  footer(s, 9);
})();

// ───────────────────────── 10 · VALIDATION / ROUTING / AUTONOMY ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Technical Architecture", "The rule checks, the confidence score, and the hard limits");
  const colW = 3.97, x0 = 0.5, gap = 0.21, y = 1.6, h = 5.2;
  const cols = [
    ["The rule checks", C.navy, [
      "NCCI bundling (hard, or fixable with a modifier)",
      "MUE — units allowed per day",
      "Is the modifier even valid?",
      "Is the code specific / billable?",
      "Does it fit the patient's sex and age?",
      "Does the payer cover it?",
    ], "Plain rules, not guesswork — every check is inspectable and reads live from tables your team can edit."],
    ["The confidence score", C.tealDk, [
      "How sure is the model?",
      "Does the chart back it up?",
      "Do the rules agree?",
      "Does it match past charts?",
      "→ one score it can trust",
      "→ the auto-bill / QA / coder line",
    ], "A blend of four signals (you set the weights) — far more trustworthy than a raw model percentage."],
    ["The hard limits", C.teal, [
      "Critical-care codes",
      "Breaking an NCCI bundle",
      "Notes that disagree with themselves",
      "A blocking documentation flag",
      "→ always sent to a person",
      "no matter how confident",
    ], "A ceiling on what can ever bill on its own — the safety net your leadership asked for."],
  ];
  cols.forEach(([t, col, items, note], i) => {
    const x = x0 + i * (colW + gap);
    card(s, x, y, colW, h);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: colW, h: 0.62, fill: { color: col }, line: { type: "none" } });
    s.addText(t, { x: x + 0.2, y, w: colW - 0.4, h: 0.62, fontFace: BODY, fontSize: 14, bold: true, color: C.white, valign: "middle", margin: 0 });
    let yy = y + 0.85;
    items.forEach((it) => {
      const ar = it.startsWith("→");
      s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: yy + 0.08, w: 0.13, h: 0.13, fill: { color: ar ? C.amber : col }, line: { type: "none" } });
      s.addText(it.replace("→ ", ""), { x: x + 0.5, y: yy, w: colW - 0.7, h: 0.4, fontFace: BODY, fontSize: 11, bold: ar, color: ar ? C.text : C.muted, valign: "top", margin: 0, lineSpacingMultiple: 0.95 });
      yy += 0.5;
    });
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.2, y: yy + 0.05, w: colW - 0.4, h: 0.02, fill: { color: C.line }, line: { type: "none" } });
    s.addText(note, { x: x + 0.22, y: yy + 0.15, w: colW - 0.42, h: 1.1, fontFace: BODY, fontSize: 10.5, italic: true, color: C.tealDk, valign: "top", margin: 0, lineSpacingMultiple: 1.0 });
  });
  footer(s, 10);
})();

// ───────────────────────── 11 · DEFENSIBILITY & GOVERNANCE ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Trust by Design", "Why every claim can be explained and defended");
  const items = [
    ["Every code is cited", "Each accepted code links back to the chart line and the guideline that justify it — coders see the why."],
    ["A complete audit trail", "Each step, who did it, which model and when — the record you'd hand to a RAC auditor, written automatically."],
    ["Every admin change is logged", "Config, policy, knowledge-graph, reference-data and gold-set edits — all recorded with who changed what, and when."],
    ["Honest accuracy numbers", "Measured against adjudicated consensus, with the limit of where coders themselves disagree — no inflated claims."],
    ["Overrides keep the reason", "When a coder changes a code, the rationale is captured — feeding both the audit trail and the learning loop."],
    ["Roles control who can do what", "Admin, coder, QA, CDI, supervisor — both the menus and the buttons; maps to your SSO in production."],
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
  footer(s, 11);
})();

// ───────────────────────── 12 · DESIGN RATIONALE ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Design Rationale", "The big choices — what we weighed, and why we landed where we did");
  const rows = [
    ["The reasoning engine", "in-house NLP / small models  ·  a frontier LLM  ·  a mix", "Frontier Claude now, for accuracy and clean citations — with a clear path to smaller US-region models for cost and latency."],
    ["Stopping hallucination", "careful prompting  ·  plain RAG  ·  Graph-RAG + rule checks", "Ground it in retrieval and check it with rules. The agent can only use codes it was given — not a prompt we hope holds."],
    ["Deciding what to auto-bill", "the model's raw % ·  a blended, calibrated score", "A blended score you can trust, so the auto-bill / QA / coder line is one the business actually sets."],
    ["Checking the codes", "let the model check itself  ·  a real rule engine", "Plain, deterministic rules — NCCI, MUE, modifiers, payer — so every check can be inspected and defended."],
    ["Where knowledge lives", "a separate vector database  ·  Postgres + pgvector", "One database, fewer moving parts, easier to run — and pgvector is there when we turn on embedding search."],
    ["How much to automate", "full auto  ·  human-in-the-loop  ·  bounded autonomy", "Automate the easy calls, but keep hard limits that always route the risky ones to a person."],
    ["Keeping it configurable", "settings baked into code  ·  settings in the database", "Thresholds, rules, SLAs, the knowledge graph and roles all change at runtime — no redeploy, no waiting on us."],
    ["Spending on the hard charts", "double-check everything  ·  never  ·  only when it's hard", "Spend the extra effort only where it pays off — the ambiguous and multi-procedure charts."],
  ];
  const x0 = 0.5, y0 = 1.45, w = 12.33;
  const cW = [2.6, 4.4, 5.33];
  s.addShape(pres.shapes.RECTANGLE, { x: x0, y: y0, w, h: 0.42, fill: { color: C.navy }, line: { type: "none" } });
  ["The decision", "What we considered", "Where we landed — and why"].forEach((t, i) => {
    const cx = x0 + cW.slice(0, i).reduce((a, b) => a + b, 0);
    s.addText(t, { x: cx + 0.15, y: y0, w: cW[i] - 0.2, h: 0.42, fontFace: BODY, fontSize: 11.5, bold: true, color: C.white, valign: "middle", margin: 0 });
  });
  let y = y0 + 0.42;
  const rh = 0.6;
  rows.forEach((r, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: x0, y, w, h: rh, fill: { color: i % 2 ? "FFFFFF" : "EFF4FA" }, line: { color: C.line, width: 0.75 } });
    s.addText(r[0], { x: x0 + 0.15, y, w: cW[0] - 0.2, h: rh, fontFace: BODY, fontSize: 11, bold: true, color: C.navy, valign: "middle", margin: 0 });
    s.addText(r[1], { x: x0 + cW[0] + 0.15, y, w: cW[1] - 0.25, h: rh, fontFace: BODY, fontSize: 10, color: "475569", valign: "middle", margin: 0, lineSpacingMultiple: 0.92 });
    s.addText(r[2], { x: x0 + cW[0] + cW[1] + 0.15, y, w: cW[2] - 0.25, h: rh, fontFace: BODY, fontSize: 10, color: C.text, valign: "middle", margin: 0, lineSpacingMultiple: 0.92 });
    y += rh;
  });
  footer(s, 12);
})();

// ───────────────────────── 13 · SECURITY / DEPLOYMENT ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Security, Deployment & Data", "Where it runs, what it protects, and the licensing reality");
  const cols = [
    ["Where it runs", C.navy, [
      "Azure + Azure AI Foundry, US-region",
      "Multi-tenant, with strict separation between clients",
      "Docker today → AKS / container apps in the cloud",
      "A path to smaller in-region models for cost & residency",
    ]],
    ["What it protects", C.tealDk, [
      "Demo data is synthetic — no real patient information",
      "One secret (the model key), kept out of source control",
      "A full audit trail and an admin change log",
      "SOC 2 controls and encryption at deployment",
    ]],
    ["The licensing reality", C.teal, [
      "Public now: ICD-10-CM, HCPCS, NCCI, MUE, guidelines",
      "CPT (AMA) is a placeholder → your licence in production",
      "Ontology: a demo set → licensed SNOMED CT / UMLS",
      "Same shapes throughout — it's a swap, not a rebuild",
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
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 6.15, w: 12.33, h: 0.75, rectRadius: 0.06, fill: { color: C.ice }, line: { type: "none" } });
  s.addText([
    { text: "Straight about what's demo-scale:  ", options: { bold: true, color: C.navy } },
    { text: "the mechanisms are real; the volume of gold charts, the model retraining and denial-prevention grow after the demo. Nothing is faked, and if the model isn't available it routes to a person rather than guess.", options: { color: C.text } },
  ], { x: 0.75, y: 6.15, w: 11.9, h: 0.75, fontFace: BODY, fontSize: 11, valign: "middle", margin: 0, lineSpacingMultiple: 0.98 });
  footer(s, 13);
})();

// ───────────────────────── 14 · ROADMAP ─────────────────────────
(() => {
  const s = pres.addSlide();
  header(s, "Adoption Path", "Earn autonomy — don't assume it");
  const phases = [
    ["Shadow", "ACE codes next to your coders while humans check everything. We calibrate, build the gold set, and prove the accuracy.", C.slate],
    ["Pilot", "Turn on auto-billing for the high-confidence lane. QA sampling eases off as the model keeps holding its numbers.", C.tealDk],
    ["Scale", "Add specialties through config and watch the auto-bill rate climb toward 80%, as the model is certified at 95%+.", C.navy],
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
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.65, y: 5.0, w: 12.03, h: 1.6, rectRadius: 0.06, fill: { color: C.navy }, line: { type: "none" } });
  s.addText("What moves as we go", { x: 0.9, y: 5.12, w: 11, h: 0.35, fontFace: BODY, fontSize: 13, bold: true, color: C.white, margin: 0 });
  const k = [["Chart accuracy", "90%+"], ["Auto-billed", "80%+"], ["Less manual effort", "30%+"], ["Faster turnaround", "10–15%"]];
  k.forEach(([l, v], i) => {
    const x = 0.95 + i * 3.0;
    s.addText(v, { x, y: 5.5, w: 2.8, h: 0.55, fontFace: HEAD, fontSize: 22, bold: true, color: C.teal, margin: 0 });
    s.addText(l, { x, y: 6.05, w: 2.8, h: 0.4, fontFace: BODY, fontSize: 11, color: "CADCFC", margin: 0 });
  });
  footer(s, 14);
})();

// ───────────────────────── 15 · WHY NOUS / CLOSE ─────────────────────────
(() => {
  const s = pres.addSlide();
  s.background = { color: C.bgDark };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: C.teal }, line: { type: "none" } });
  s.addText("WHY NOUS", { x: 0.8, y: 0.7, w: 10, h: 0.4, fontFace: BODY, fontSize: 13, bold: true, color: C.teal, charSpacing: 3, margin: 0 });
  s.addText("Not just a model — a platform you can run and trust", { x: 0.8, y: 1.15, w: 11.8, h: 0.9, fontFace: HEAD, fontSize: 28, bold: true, color: C.white, margin: 0 });
  const items = [
    ["We measure honestly", "Accuracy against adjudicated consensus — the instrument that lets you grow autonomy without guessing."],
    ["Everything is defensible", "Citations, real rule checks and a full audit trail — every claim can be explained."],
    ["New specialties are quick", "They onboard through config and a gold set — not another build."],
    ["You own the knowledge", "A knowledge graph your team builds and curates inside the app."],
    ["You run it, not us", "Thresholds, rules, SLAs, roles, the control tower and the governance ramp are all yours."],
    ["It fits your world", "Designed to live inside Vee Healthtek's RevAmp coding ecosystem."],
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
  s.addText("This is working software today — and it's built to earn your trust one chart at a time.", { x: 0.8, y: 6.75, w: 11.8, h: 0.5, fontFace: BODY, fontSize: 14, italic: true, color: "CADCFC", margin: 0 });
})();

pres.writeFile({ fileName: "ACE_Architecture.pptx" }).then((f) => console.log("WROTE", f));
