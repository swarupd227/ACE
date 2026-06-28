// Nous RCM Studio — ACE (Coding module) comprehensive E2E capture (~3.5 min, captioned).
// Drives the UNIFIED studio at :8200/coding (clean, vendor-neutral build).
//
// KEY: the live vision-OCR call takes ~45s. We DON'T block the camera on it — we fire it as
// a background API request (independent of the page, survives navigation), show a short upload
// beat, tour other screens while it transcribes, then REVEAL the uploaded chart being coded
// live once OCR has finished off-screen. No dead air.
//
// Covers: upload + vision OCR -> worklist -> citations -> confidence + gates -> audit ->
// coder OVERRIDE + comment -> closed-loop LEARNING -> ROLLBACK -> LIVE agentic coding of the
// uploaded chart -> CDI -> Control Tower -> engines (E&M, MS-DRG, CMS-HCC) -> Policy & Knowledge
// Admin (5 tabs) -> config + reasoning model -> RBAC -> audit log -> evals -> outcomes.
const { test, expect } = require("@playwright/test");

const BASE = "http://localhost:8200/coding";
const API = `${BASE}/api`;
const HDRS = { "X-Role": "Admin", "X-Actor": "admin:demo" };

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
const go = (page, p) => page.goto(`${BASE}${p}`, { waitUntil: "domcontentloaded" });

// Render a synthetic "scanned" chart to a PNG buffer (throwaway context → no extra video).
async function scannedChartPng(browser) {
  const ctx = await browser.newContext({ viewport: { width: 880, height: 1040 } });
  const p = await ctx.newPage();
  await p.setContent(`
    <body style="margin:0;background:#eceae3;padding:46px;font-family:'Courier New',monospace;color:#1b1b1b">
      <div style="background:#fbfaf6;border:1px solid #cfcabb;box-shadow:0 2px 10px rgba(0,0,0,.12);padding:42px 46px;max-width:720px;margin:auto;line-height:1.6;font-size:16px">
        <div style="font-weight:700;font-size:19px;letter-spacing:1px">RADIOLOGY REPORT — DIAGNOSTIC IMAGING</div>
        <div style="border-bottom:2px solid #1b1b1b;margin:8px 0 16px"></div>
        PATIENT: Maria Delgado &nbsp; MRN: 88412-7 &nbsp; DOB: 03/14/1964<br/>
        EXAM: CT CHEST WITH IV CONTRAST &nbsp; DOS: 06/24/2026<br/>
        ORDERING: Dr. L. Tran, MD &nbsp;·&nbsp; PAYER: Medicare<br/><br/>
        HISTORY: 61-year-old with persistent cough and an abnormal screening chest X-ray.<br/><br/>
        TECHNIQUE: Helical CT of the thorax acquired following intravenous contrast administration.<br/><br/>
        FINDINGS: A 1.2 cm spiculated nodule is present in the right upper lobe. No pleural
        effusion. No mediastinal or hilar lymphadenopathy. Heart size normal.<br/><br/>
        IMPRESSION: Right upper lobe pulmonary nodule, suspicious for malignancy —
        recommend tissue sampling and short-interval CT follow-up.<br/><br/>
        Electronically signed by A. Reyes, MD &nbsp; 06/24/2026 14:08
      </div>
    </body>`);
  const buf = await p.screenshot();
  await ctx.close();
  return buf;
}

test("Nous RCM Studio — ACE comprehensive tour", async ({ page, request, browser }) => {
  test.setTimeout(420000);
  await page.addInitScript(() => localStorage.setItem("ace_role", "Admin"));
  const encs = await (await request.get(`${API}/encounters`)).json();
  const pick = (pred) => encs.find(pred);
  const rad = pick((e) => e.mrn === "RAD10001") || pick((e) => e.specialty === "Radiology" && e.status === "CODED");
  const em = pick((e) => e.mrn === "EM20001") || pick((e) => e.specialty === "E&M");
  const ip = pick((e) => e.mrn === "IP10001") || pick((e) => e.specialty === "Inpatient (DRG)");
  const hcc = pick((e) => e.mrn === "HC10001") || pick((e) => e.specialty === "HCC / Risk Adjustment");

  // Fire the live vision-OCR ingest in the BACKGROUND (independent of the page). By the time
  // we reach the agentic-coding reveal (~55s of other scenes later) it has finished off-camera.
  const png = await scannedChartPng(browser);
  const ocrPromise = request.post(`${API}/ingest/document`, {
    headers: HDRS,
    multipart: {
      file: { name: "scanned_ct_chest.png", mimeType: "image/png", buffer: png },
      specialty: "Radiology", modality: "CT", payer: "Medicare", pos: "22",
    },
    timeout: 150000,
  }).then((r) => (r.ok() ? r.json() : null)).catch(() => null);

  // 0 · TITLE CARD ────────────────────────────────────────────────────────────
  await page.setContent(`
    <body style="margin:0;background:#0E1B33;height:100vh;display:flex;align-items:center;justify-content:center;font-family:Calibri,'Segoe UI',sans-serif">
      <div style="position:fixed;left:0;top:0;bottom:0;width:14px;background:#13B5A6"></div>
      <div style="text-align:left;max-width:940px;padding:0 60px">
        <div style="color:#13B5A6;font-weight:800;letter-spacing:4px;font-size:16px">NOUS INFOSYSTEMS &nbsp;·&nbsp; NOUS RCM STUDIO</div>
        <div style="color:#fff;font-family:Georgia,serif;font-weight:700;font-size:52px;margin-top:18px">ACE — Autonomous Coding Engine</div>
        <div style="color:#CADCFC;font-size:23px;margin-top:14px">From a scanned chart to a cited, audit-ready code — autonomously</div>
        <div style="color:#7E90A8;font-size:16px;margin-top:24px;font-style:italic">Upload &amp; agentic coding · human-in-the-loop &amp; learning · knowledge admin · evals</div>
      </div>
    </body>`);
  await wait(page, 3);

  // 1 · UPLOAD A SCANNED CHART (OCR already running in the background) ─────────
  await go(page, "/integrations"); await settle(page);
  await page.getByText("Ingest a scanned document", { exact: false }).first().scrollIntoViewIfNeeded().catch(() => {});
  const fileInput = page.locator('input[type="file"][accept*="pdf"]').first();
  await fileInput.setInputFiles({ name: "scanned_ct_chest.png", mimeType: "image/png", buffer: png }).catch(() => {});
  await cap(page, "INTAKE", "Upload a scanned chart — the model reads it",
    "Real charts arrive as scans / faxes / PDFs. ACE is transcribing it now with vision OCR…");
  await wait(page, 5);
  await cap(page, "INTAKE", "…and while it transcribes, here's where it lands",
    "The extracted text enters the same Stage 0–5 pipeline. Let's tour the queue — we'll come back to this chart.");
  await wait(page, 2.5);

  // 2 · WORKLIST — three lanes ────────────────────────────────────────────────
  await go(page, "/"); await settle(page);
  await cap(page, "WORKLIST", "Every chart, triaged into three lanes",
    "Straight-through billing, a quick QA check, or a coder — by how sure ACE is.");
  await wait(page, 4.5);

  // 3 · GROUNDED & CITED + CONFIDENCE + GATES ─────────────────────────────────
  if (rad) {
    await go(page, `/encounter/${rad.id}`); await settle(page);
    await cap(page, "EVIDENCE", "Grounded and cited — you can see the 'why'",
      "Every code points back to a line in the chart and the guideline behind it.");
    await wait(page, 2.5);
    await page.evaluate(() => window.scrollTo({ top: 1180, behavior: "instant" }));
    await wait(page, 1.2);
    await page.locator("text=/^7\\d{4}$/").first().hover().catch(() => {});
    await wait(page, 2);
    await page.mouse.wheel(0, -900); await wait(page, 0.5);
    await cap(page, "CONFIDENCE + GATES", "A score it can trust — and hard rule checks",
      "Four confidence signals decide the lane; deterministic NCCI / MUE / modifier gates run every time.");
    await wait(page, 4);

    // 4 · AUDIT PACKET ────────────────────────────────────────────────────────
    await cap(page, "AUDIT", "Defensible by default — the audit packet",
      "Each step, who did it, which model and when — ready for an auditor.");
    await page.getByText("Audit packet", { exact: false }).first().click().catch(() => {});
    await wait(page, 3);
    await page.getByText("Audit packet", { exact: false }).first().click().catch(() => {});

    // 5 · CODER OVERRIDE + COMMENT → LEARNING ─────────────────────────────────
    await cap(page, "HUMAN-IN-THE-LOOP", "A coder corrects a code — with a reason",
      "The correction and the coder's comment are captured for the learning loop.");
    await page.evaluate(() => window.scrollTo({ top: 1180, behavior: "instant" }));
    await wait(page, 1);
    await page.getByRole("button", { name: "Override" }).first().click().catch(() => {});
    await wait(page, 0.8);
    await page.getByPlaceholder("Correct code (e.g. 71045)").first().fill("71250").catch(() => {});
    await page.getByPlaceholder("Reason (captured for learning)").first()
      .fill("Contrast study — use the with-contrast CT code per the report.").catch(() => {});
    await wait(page, 1.5);
    await page.getByText("Submit correction", { exact: false }).first().click().catch(() => {});
    await wait(page, 2.5);

    // 6 · CLOSED-LOOP LEARNING ────────────────────────────────────────────────
    await go(page, "/learning"); await settle(page);
    await cap(page, "LEARNING", "The correction becomes a learned pattern",
      "Reason + pattern are recorded and quietly shift later, similar charts — closed-loop.");
    await wait(page, 4);

    // 7 · ROLLBACK ────────────────────────────────────────────────────────────
    await go(page, `/encounter/${rad.id}`); await settle(page);
    await page.getByText("Revert to AI recommendation", { exact: false }).first().scrollIntoViewIfNeeded().catch(() => {});
    await cap(page, "ROLLBACK", "Every change is reversible",
      "One click reverts the chart to ACE's original recommendation — fully audited either way.");
    await wait(page, 3.5);
  }

  // 8 · REVEAL: LIVE AGENTIC CODING OF THE UPLOADED CHART ──────────────────────
  const ocrEnc = await ocrPromise;                 // finished off-camera by now
  const liveId = (ocrEnc && ocrEnc.id) || (rad && rad.id);
  if (liveId) {
    await go(page, `/encounter/${liveId}`); await settle(page);
    await cap(page, "AGENTIC CODING", "Now — watch ACE code the chart we uploaded, live",
      ocrEnc ? "The transcribed CT-chest report, coded by the bounded agent: extract → retrieve → cite → gate → route."
             : "A bounded agent: extract → Graph-RAG retrieval → cited coding → gates → calibration → routing.");
    await page.getByText("Watch agent re-run", { exact: false }).first().click().catch(() => {});
    await page.getByText("Coding Agent", { exact: false }).first().waitFor({ state: "visible", timeout: 12000 }).catch(() => {});
    await wait(page, 20);
    await page.keyboard.press("Escape").catch(() => {});
    await page.mouse.click(25, 320).catch(() => {});
    await wait(page, 1);
  }

  // 9 · CDI CO-PILOT ──────────────────────────────────────────────────────────
  await go(page, "/cdi"); await settle(page);
  await cap(page, "CDI", "Compliant physician queries",
    "When documentation falls short, ACE drafts a non-leading query — the answer re-codes the chart.");
  await wait(page, 4);

  // 10 · CONTROL TOWER ────────────────────────────────────────────────────────
  await go(page, "/control-tower"); await settle(page);
  await cap(page, "CONTROL TOWER", "Queues, SLA aging, assignment & escalation",
    "Supervisors see what's at risk and route work across the team.");
  await wait(page, 4);

  // 11 · SPECIALTY ENGINES — E&M leveling, then DRG / HCC ──────────────────────
  if (em) {
    await go(page, `/encounter/${em.id}`); await settle(page);
    await cap(page, "E&M LEVELING", "Outpatient E&M, leveled deterministically",
      "2021 MDM 2-of-3 + total time, modifier-25 evidence gate, new-vs-established, prolonged services.");
    await wait(page, 4.5);
  }
  if (ip) {
    await go(page, `/encounter/${ip.id}`); await settle(page);
    await page.getByText("MS-DRG", { exact: false }).first().scrollIntoViewIfNeeded().catch(() => {});
    await cap(page, "PAYMENT MODELS", "A real MS-DRG grouper — fully traced",
      "Principal dx → MDC → surgical/medical → CC/MCC severity → the DRG and its weight.");
    await wait(page, 4);
  }
  if (hcc) {
    await go(page, `/encounter/${hcc.id}`); await settle(page);
    await page.getByText("CMS-HCC", { exact: false }).first().scrollIntoViewIfNeeded().catch(() => {});
    await cap(page, "PAYMENT MODELS", "HCC risk adjustment, anesthesia units, facility APCs",
      "Five payment models on one engine — each deterministic and audited.");
    await wait(page, 4);
  }

  // 12 · POLICY & KNOWLEDGE ADMIN — the editable knowledge that grounds coding ─
  await go(page, "/policy"); await settle(page);
  await cap(page, "KNOWLEDGE ADMIN", "Payer policies & client overlays",
    "Medical-necessity, prior-auth and modifier rules per payer — they drive the gates on the next run.");
  await wait(page, 3.5);
  await page.getByRole("button", { name: /KG Builder/i }).first().click().catch(() => {});
  await wait(page, 0.8);
  await cap(page, "KNOWLEDGE ADMIN", "Build the medical knowledge graph in-app",
    "Add a concept, map it to codes, draw a relationship — the agent uses it on the next chart.");
  await wait(page, 3.5);
  await page.getByRole("button", { name: /Explore Graph/i }).first().click().catch(() => {});
  await wait(page, 1);
  await cap(page, "KNOWLEDGE ADMIN", "The knowledge graph, live",
    "Concepts, relationships and guidelines that ground retrieval — visualized.");
  await wait(page, 3.5);
  await page.getByRole("button", { name: /Reference Data/i }).first().click().catch(() => {});
  await wait(page, 1);
  await cap(page, "KNOWLEDGE ADMIN", "Edit the code sets, NCCI / MUE & modifier rules",
    "The gates are data, not hard-code — every edit is logged and effective on the next run.");
  await wait(page, 3.5);
  await page.getByRole("button", { name: /Coding Guidelines/i }).first().click().catch(() => {});
  await wait(page, 1);
  await cap(page, "KNOWLEDGE ADMIN", "Curate the guidelines the agent must cite",
    "Public-source guidance retrieved into the agent's context and used for citation verification.");
  await wait(page, 3.5);

  // 13 · ADMIN / CONFIG + reasoning model ─────────────────────────────────────
  await go(page, "/admin"); await settle(page);
  await cap(page, "CONFIG", "You configure the engine — not us",
    "Routing thresholds, confidence weights, self-consistency, budgets — changed at runtime.");
  await wait(page, 3.5);
  await page.getByText("Reasoning Model", { exact: false }).first().click().catch(() => {});
  await wait(page, 1);
  await cap(page, "CONFIG", "Even the reasoning model is yours to switch",
    "Change provider or model at runtime and test the connection — API keys never leave the environment.");
  await wait(page, 3.5);

  // 14 · RBAC — roles reshape the app ─────────────────────────────────────────
  await go(page, "/"); await settle(page);
  const roleSel = page.locator('select:has(option:text-is("CDI Specialist"))').first();
  await roleSel.selectOption({ label: "CDI Specialist" }).catch(() => {});
  await wait(page, 1.4);
  await cap(page, "RBAC", "Roles decide who can do what",
    "As a CDI Specialist the menu shrinks and coding turns view-only — nav and actions both respect the role.");
  await wait(page, 3.5);
  await roleSel.selectOption({ label: "Admin" }).catch(() => {});
  await wait(page, 0.6);

  // 15 · GLOBAL AUDIT LOG ─────────────────────────────────────────────────────
  await go(page, "/audit"); await settle(page);
  await cap(page, "AUDIT LOG", "One timeline for everything that happened",
    "Every coding decision and every governance change — filterable, searchable, exportable.");
  await wait(page, 3.5);

  // 16 · EVALUATION HARNESS ───────────────────────────────────────────────────
  await go(page, "/eval"); await settle(page);
  await cap(page, "EVALS", "The eval is the product",
    "The live pipeline is scored against an adjudicated golden set — honestly, with the IRR ceiling.");
  await wait(page, 3);
  await page.getByText("Manage golden set", { exact: false }).first().click().catch(() => {});
  await wait(page, 3.5);

  // 17 · OUTCOMES DASHBOARD ───────────────────────────────────────────────────
  await go(page, "/dashboard"); await settle(page);
  await cap(page, "OUTCOMES", "Measured — not claimed",
    "Auto-bill rate, calibrated accuracy, turnaround vs baseline, maturity, and model drift.");
  await wait(page, 4);

  // 18 · CLOSE ────────────────────────────────────────────────────────────────
  await cap(page, "ACE", "Grounded, cited, and yours to run",
    "Autonomous AI medical coding · Nous Infosystems · Nous RCM Studio.");
  await wait(page, 3.5);

  expect(encs.length).toBeGreaterThan(0);
});
