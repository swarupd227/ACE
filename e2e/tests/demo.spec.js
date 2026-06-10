// ACE — Autonomous Coding Engine: end-to-end demo capture (< 3 min).
// A logical product tour that mirrors the deck: intake → worklist → coding (a
// brief glimpse of the live agent) → grounded & cited result → confidence →
// control tower → CDI → closed-loop learning → ADMIN functions (configuration,
// knowledge graph, reference data, change log, roles) → outcomes.
const { test, expect } = require("@playwright/test");

const API = "http://localhost:8000/api";

// branded bottom caption bar
async function cap(page, tag, title, sub = "") {
  await page.evaluate(({ tag, title, sub }) => {
    let el = document.getElementById("ace-cap");
    if (!el) {
      el = document.createElement("div");
      el.id = "ace-cap";
      el.style.cssText =
        "position:fixed;left:0;right:0;bottom:0;z-index:2147483647;pointer-events:none;" +
        "background:linear-gradient(180deg,#1B2A4A,#0E1B33);color:#fff;padding:13px 26px;" +
        "font-family:Calibri,'Segoe UI',sans-serif;display:flex;align-items:center;gap:18px;" +
        "box-shadow:0 -8px 28px rgba(0,0,0,.28);border-top:2px solid #13B5A6";
      const b = document.createElement("div");
      b.id = "ace-cap-b";
      b.style.cssText =
        "background:#13B5A6;color:#04201d;font-weight:800;letter-spacing:1px;padding:7px 13px;" +
        "border-radius:9px;font-size:14px;white-space:nowrap";
      const t = document.createElement("div");
      t.id = "ace-cap-t";
      el.appendChild(b); el.appendChild(t); document.body.appendChild(el);
    }
    document.getElementById("ace-cap-b").textContent = tag;
    document.getElementById("ace-cap-t").innerHTML =
      `<div style="font-size:18px;font-weight:700;line-height:1.15">${title}</div>` +
      (sub ? `<div style="font-size:12.5px;color:#CADCFC;margin-top:2px">${sub}</div>` : "");
  }, { tag, title, sub });
}
const wait = (page, s) => page.waitForTimeout(s * 1000);
const settle = async (page) => { await page.waitForLoadState("networkidle").catch(() => {}); await wait(page, 0.4); };
let _f = 0;
const shot = (page, n) => page.screenshot({ path: `frames/${String(++_f).padStart(2, "0")}-${n}.png` }).catch(() => {});

async function find(request, pred) {
  const r = await request.get(`${API}/encounters`);
  return (await r.json()).find(pred);
}

test("ACE end-to-end product tour", async ({ page, request }) => {
  await page.addInitScript(() => localStorage.setItem("ace_role", "Admin"));

  // 0 · TITLE CARD — FIRST action so the recording never opens on a blank frame.
  // The encounter lookups run during the card's dwell time, not before it.
  await page.setContent(`
    <body style="margin:0;background:#0E1B33;height:100vh;display:flex;align-items:center;justify-content:center;font-family:Calibri,'Segoe UI',sans-serif">
      <div style="position:fixed;left:0;top:0;bottom:0;width:14px;background:#13B5A6"></div>
      <div style="text-align:left;max-width:900px;padding:0 60px">
        <div style="color:#13B5A6;font-weight:800;letter-spacing:4px;font-size:16px">NOUS INFOSYSTEMS &nbsp;·&nbsp; FOR VEE HEALTHTEK</div>
        <div style="color:#fff;font-family:Georgia,serif;font-weight:700;font-size:54px;margin-top:18px">ACE — Autonomous Coding Engine</div>
        <div style="color:#CADCFC;font-size:24px;margin-top:14px">Agentic AI that turns clinical notes into billable codes</div>
        <div style="color:#7E90A8;font-size:16px;margin-top:26px;font-style:italic">An end-to-end product tour &nbsp;·&nbsp; ~2½ minutes</div>
      </div>
    </body>`);
  const encs = await (await request.get(`${API}/encounters`)).json();
  const pick = (pred) => encs.find(pred);
  const rad = pick((e) => e.mrn === "RAD10001") || pick((e) => e.specialty === "Radiology" && e.routing_lane === "STB");
  const em = pick((e) => e.mrn === "EM20001") || pick((e) => e.specialty === "E&M");
  const ip = pick((e) => e.mrn === "IP10001") || pick((e) => e.specialty === "Inpatient (DRG)");
  const hcc = pick((e) => e.mrn === "HC10001") || pick((e) => e.specialty === "HCC / Risk Adjustment");
  await wait(page, 3.0);

  // 1 · INTAKE / INTEGRATIONS — feeds + scanned-document OCR ──────────────────
  await page.goto("/integrations"); await settle(page);
  await cap(page, "INTAKE", "Charts arrive from your PMS and EHR — or as a scan",
    "FHIR, HL7, EDI, REST — and scanned PDFs / faxes, transcribed live by the model (vision OCR).");
  await shot(page, "intake"); await wait(page, 3);
  await page.getByText("Ingest a scanned document", { exact: false }).first().scrollIntoViewIfNeeded().catch(() => {});
  await wait(page, 2.5); await shot(page, "intake-scan");

  // 2 · WORKLIST (3 lanes) ─────────────────────────────────────────────────────
  await page.goto("/"); await settle(page);
  await cap(page, "WORKLIST", "Every chart, triaged into three lanes",
    "Straight-through billing, a quick QA check, or a coder — by how sure ACE is.");
  await shot(page, "worklist"); await wait(page, 4);

  // 3 · ACE CODES THE CHART — brief glimpse of the live agent ─────────────────
  await page.goto(`/encounter/${rad.id}`); await settle(page);
  await cap(page, "CODING", "ACE codes the chart",
    "It reads, extracts, retrieves grounded codes, checks the rules and scores its confidence — live.");
  await wait(page, 1.5);
  await page.getByText("Watch agent re-run", { exact: false }).first().click().catch(() => {});
  await page.getByText("Autonomous Coding Agent", { exact: false }).first().waitFor({ state: "visible", timeout: 12000 }).catch(() => {});
  await wait(page, 5);                 // a short glimpse of the stream — not the whole run
  await shot(page, "coding-glimpse");
  await page.mouse.click(30, 360).catch(() => {});   // click backdrop to close the console
  await wait(page, 1);

  // 4 · GROUNDED & CITED RESULT ───────────────────────────────────────────────
  await cap(page, "EVIDENCE", "Grounded and cited — you can see the 'why'",
    "Every code points back to a line in the chart and the guideline behind it.");
  await wait(page, 2);   // show the 'knowledge used for this chart' grounding panel
  await shot(page, "evidence-grounding");
  await page.evaluate(() => window.scrollTo({ top: 1180, behavior: "instant" }));  // down to the codes + clinical chart
  await wait(page, 1.4);
  await page.locator("text=/^7\\d{4}$/").first().hover().catch(() => {});   // hover a CPT code to highlight its evidence in the chart
  await wait(page, 1.4);
  await shot(page, "evidence-citations"); await wait(page, 2.5);

  // 5 · CONFIDENCE + RULE CHECKS ──────────────────────────────────────────────
  await page.mouse.wheel(0, -900); await wait(page, 0.6);
  await cap(page, "CONFIDENCE", "A confidence score it can trust",
    "Four signals decide the lane — and the deterministic rule checks are shown right here.");
  await wait(page, 4);

  // 6 · AUDIT PACKET ──────────────────────────────────────────────────────────
  await cap(page, "AUDIT", "Defensible by default — the audit packet",
    "Each step, who did it, which model and when — ready for an auditor.");
  await page.getByText("Audit packet", { exact: false }).first().click().catch(() => {});
  await wait(page, 1); await shot(page, "audit"); await wait(page, 3);

  // 6b · FIVE PAYMENT MODELS — DRG, then RAF ──────────────────────────────────
  if (ip) {
    await page.goto(`/encounter/${ip.id}`); await settle(page);
    await cap(page, "PAYMENT MODELS", "Beyond pro-fee — a real MS-DRG grouper",
      "Principal dx → MDC → surgical or medical → CC/MCC severity → the DRG and its weight, fully traced.");
    await page.getByText("MS-DRG", { exact: false }).first().scrollIntoViewIfNeeded().catch(() => {});
    await wait(page, 4.5); await shot(page, "drg-card");
  }
  if (hcc) {
    await page.goto(`/encounter/${hcc.id}`); await settle(page);
    await cap(page, "PAYMENT MODELS", "HCC risk adjustment, anesthesia units, facility APCs",
      "Five payment models on one engine — RAF scores, unit math and OPPS pricing, each deterministic and audited.");
    await page.getByText("CMS-HCC", { exact: false }).first().scrollIntoViewIfNeeded().catch(() => {});
    await wait(page, 4.5); await shot(page, "hcc-card");
  }

  // 7 · CONTROL TOWER (workflow / actions) ────────────────────────────────────
  await page.goto("/control-tower"); await settle(page);
  await cap(page, "CONTROL TOWER", "Queues, SLA aging and assignment",
    "Supervisors see what's at risk and assign work across the team.");
  await shot(page, "control-tower"); await wait(page, 4);

  // 8 · CDI CO-PILOT ──────────────────────────────────────────────────────────
  await page.goto(`/encounter/${em.id}`); await settle(page);
  await cap(page, "CDI", "A compliant physician query, drafted for you",
    "When the notes fall short, the physician's answer re-codes the chart.");
  await wait(page, 1);
  await page.getByText("Scan for CDI opportunities", { exact: false }).first().scrollIntoViewIfNeeded().catch(() => {});
  await page.getByText("Scan for CDI opportunities", { exact: false }).first().click().catch(() => {});
  await page.getByText("complete", { exact: false }).first().waitFor({ timeout: 45000 }).catch(() => {});
  await page.mouse.click(30, 360).catch(() => {});
  await wait(page, 1); await page.mouse.wheel(0, 350); await shot(page, "cdi"); await wait(page, 4);

  // 9 · CLOSED-LOOP LEARNING ──────────────────────────────────────────────────
  await page.goto("/learning"); await settle(page);
  await cap(page, "LEARNING", "It improves from your coders' corrections",
    "A fix becomes an example that quietly shifts later, similar charts.");
  await shot(page, "learning"); await wait(page, 4);

  // 9b · GLOBAL AUDIT LOG ─────────────────────────────────────────────────────
  await page.goto("/audit"); await settle(page);
  await cap(page, "AUDIT LOG", "One timeline for everything that happened",
    "Every coding decision and every governance change — filterable, searchable, exportable.");
  await shot(page, "audit-log"); await wait(page, 4);

  // 10 · ADMIN — CONFIGURATION + THE REASONING MODEL ──────────────────────────
  await page.goto("/admin"); await settle(page);
  await cap(page, "ADMIN", "You configure the engine — not us",
    "Routing thresholds, confidence weights, SLAs, autonomy limits — changed at runtime.");
  await shot(page, "admin-config"); await wait(page, 3.5);
  await page.getByText("Reasoning Model", { exact: false }).first().click().catch(() => {});
  await wait(page, 1);
  await cap(page, "ADMIN", "Even the reasoning model is yours to switch",
    "Change provider or model at runtime and test the connection — API keys never leave the environment.");
  await shot(page, "admin-llm"); await wait(page, 4);

  // 11 · KNOWLEDGE GRAPH BUILDER ──────────────────────────────────────────────
  await page.goto("/policy"); await settle(page);
  await page.getByText("KG Builder", { exact: false }).first().click().catch(() => {});
  await wait(page, 1);
  await cap(page, "KNOWLEDGE", "Build your knowledge graph in the app",
    "Add a concept, map it to codes, draw a relationship — the agent uses it on the next chart.");
  await shot(page, "kg-builder"); await wait(page, 4);

  // 12 · REFERENCE DATA + CHANGE LOG ──────────────────────────────────────────
  await page.getByText("Reference Data", { exact: false }).first().click().catch(() => {});
  await wait(page, 1);
  await cap(page, "GOVERNANCE", "Edit the code sets and rules — every change is logged",
    "Client overlays drive the gates; the change log records who changed what, and when.");
  await shot(page, "reference-data"); await wait(page, 4);

  // 13 · ROLES (RBAC reshapes the app) — switch live on the worklist ──────────
  await page.goto("/"); await settle(page);
  const roleSel = page.locator('select:has(option:text-is("CDI Specialist"))').first();
  await roleSel.selectOption({ label: "CDI Specialist" }).catch(() => {});
  await wait(page, 1.6);   // React re-renders nav + buttons for the new role
  await cap(page, "ROLES", "Roles decide who can do what",
    "As a CDI Specialist the menus shrink and coding turns view-only — both nav and buttons respect the role.");
  await wait(page, 3.5); await shot(page, "role-restricted"); await wait(page, 1.5);
  await roleSel.selectOption({ label: "Admin" }).catch(() => {});
  await wait(page, 0.6);

  // 14 · OUTCOMES DASHBOARD — including model performance / drift ─────────────
  await page.goto("/dashboard"); await settle(page);
  await cap(page, "OUTCOMES", "Measured — not claimed",
    "Auto-bill rate, calibrated accuracy, turnaround, and the maturity pathway.");
  await shot(page, "dashboard"); await wait(page, 3.5);
  await page.getByText("Model performance", { exact: false }).first().scrollIntoViewIfNeeded().catch(() => {});
  await cap(page, "OUTCOMES", "The model is measured too",
    "Real token usage, latency, confidence and override rate — per model version, so drift is visible.");
  await wait(page, 4); await shot(page, "dashboard-model");

  // 15 · CLOSE ────────────────────────────────────────────────────────────────
  await cap(page, "ACE", "Grounded, cited, and yours to run",
    "Autonomous AI medical coding · Nous Infosystems for Vee Healthtek.");
  await wait(page, 3.5);

  expect(rad).toBeTruthy();
});
