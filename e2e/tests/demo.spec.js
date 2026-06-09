// ACE — Autonomous Coding Engine: end-to-end demo capture (< 3 min).
// A logical coder workflow that highlights, with on-screen captions, exactly
// where the AI is making the difference. Records video via Playwright.
const { test, expect } = require("@playwright/test");

const API = "http://localhost:8000/api";
const STEP = 1; // global pacing multiplier

// ── on-screen branded caption (bottom bar) ─────────────────────────────────
async function caption(page, title, sub = "", tag = "WORKFLOW") {
  await page.evaluate(({ title, sub, tag }) => {
    let el = document.getElementById("ace-cap");
    if (!el) {
      el = document.createElement("div");
      el.id = "ace-cap";
      el.style.cssText =
        "position:fixed;left:0;right:0;bottom:0;z-index:2147483647;pointer-events:none;" +
        "background:linear-gradient(180deg,#1B2A4A,#0E1B33);color:#fff;padding:13px 26px;" +
        "font-family:Calibri,'Segoe UI',sans-serif;display:flex;align-items:center;gap:18px;" +
        "box-shadow:0 -8px 28px rgba(0,0,0,.28);border-top:2px solid #13B5A6";
      const badge = document.createElement("div");
      badge.id = "ace-cap-badge";
      badge.style.cssText =
        "background:#13B5A6;color:#04201d;font-weight:800;letter-spacing:1px;padding:7px 13px;" +
        "border-radius:9px;font-size:15px;white-space:nowrap";
      const txt = document.createElement("div");
      txt.id = "ace-cap-txt";
      el.appendChild(badge);
      el.appendChild(txt);
      document.body.appendChild(el);
    }
    document.getElementById("ace-cap-badge").textContent = tag;
    document.getElementById("ace-cap-txt").innerHTML =
      `<div style="font-size:19px;font-weight:700;line-height:1.15">${title}</div>` +
      (sub ? `<div style="font-size:13px;color:#CADCFC;margin-top:2px">${sub}</div>` : "");
  }, { title, sub, tag });
}
const wait = (page, s) => page.waitForTimeout(s * 1000 * STEP);
let _f = 0;
const shot = (page, name) => page.screenshot({ path: `frames/${String(++_f).padStart(2, "0")}-${name}.png` }).catch(() => {});

async function findId(request, predicate) {
  const res = await request.get(`${API}/encounters`);
  const list = await res.json();
  return list.find(predicate);
}

test("ACE end-to-end demo", async ({ page, request }) => {
  // Run as Admin so coding + CDI actions are available.
  await page.addInitScript(() => localStorage.setItem("ace_role", "Admin"));

  const rad = await findId(request, (e) => e.mrn === "RAD10001") ||
              await findId(request, (e) => e.specialty === "Radiology" && e.routing_lane === "STB");
  const em = await findId(request, (e) => e.mrn === "EM20001") ||
             await findId(request, (e) => e.specialty === "E&M");

  // ── 1 · Intake worklist ──────────────────────────────────────────────────
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await caption(page, "Autonomous Coding Engine — the coder worklist",
    "Charts arrive from the PMS / EHR and are triaged into three lanes by confidence.", "INTAKE");
  await shot(page, "worklist");
  await wait(page, 5);

  // ── 2 · Open a radiology chart ───────────────────────────────────────────
  await page.goto(`/encounter/${rad.id}`);
  await page.waitForLoadState("networkidle");
  await caption(page, "A chest X-ray chart — let's watch ACE code it end-to-end",
    "Clinical narrative in; billable codes out — with the evidence for every decision.", "ENCOUNTER");
  await wait(page, 4.5);

  // ── 3 · THE AI MOMENT: live agentic coding over SSE ──────────────────────
  await caption(page, "AI in action: the agent reasons live, stage by stage",
    "Eligibility → extraction → Graph-RAG retrieval → cited coding → validation → calibrated routing.", "AI · AGENT");
  const watch = page.getByText("Watch agent re-run", { exact: false }).first();
  await watch.scrollIntoViewIfNeeded();
  await watch.click();
  await wait(page, 4);
  await shot(page, "agent-streaming");
  // stream runs in a modal; wait for completion (capped)
  await page.getByText("complete", { exact: false }).first().waitFor({ timeout: 90000 }).catch(() => {});
  await shot(page, "agent-complete");
  await wait(page, 3);
  // close the console
  await page.getByRole("button", { name: "Close" }).click({ timeout: 8000 }).catch(async () => {
    await page.keyboard.press("Escape").catch(() => {});
  });
  await wait(page, 1);

  // ── 4 · Grounded & cited result ──────────────────────────────────────────
  await caption(page, "Every code is grounded in retrieval — and cited",
    "The agent may only emit codes the knowledge graph surfaced; each links to the chart line + guideline.", "DEFENSIBLE");
  await page.mouse.wheel(0, 500);
  await wait(page, 5);
  await shot(page, "cited-codes");
  await page.mouse.wheel(0, 500);
  await wait(page, 4);

  // ── 5 · Calibrated confidence & routing ──────────────────────────────────
  await caption(page, "Calibrated 4-factor confidence decides the lane",
    "Model certainty · documentation match · rule agreement · historical fit → auto-bill, QA, or manual.", "AI · ROUTING");
  await page.mouse.wheel(0, 600);
  await wait(page, 5);
  await page.mouse.wheel(0, -1600);
  await wait(page, 1);

  // ── 6 · CDI co-pilot — AI drafts a compliant query ───────────────────────
  await page.goto(`/encounter/${em.id}`);
  await page.waitForLoadState("networkidle");
  await caption(page, "When documentation is thin, ACE drafts a compliant physician query",
    "A non-leading CDI query — the AI as a co-pilot, not a coder replacement.", "AI · CDI");
  await wait(page, 3);
  const scan = page.getByText("Scan for CDI opportunities", { exact: false }).first();
  await scan.scrollIntoViewIfNeeded();
  await scan.click().catch(() => {});
  await page.getByText("complete", { exact: false }).first().waitFor({ timeout: 70000 }).catch(() => {});
  await wait(page, 2.5);
  await page.getByRole("button", { name: "Close" }).click({ timeout: 6000 }).catch(() => {});
  await wait(page, 1);
  await caption(page, "ACE proposes a non-leading query the physician can answer",
    "The answer re-codes the chart automatically — closing the documentation gap.", "AI · CDI");
  await page.mouse.wheel(0, 400);
  await wait(page, 2);
  await shot(page, "cdi-query");
  await wait(page, 2.5);

  // ── 7 · Outcomes dashboard ───────────────────────────────────────────────
  await page.goto("/dashboard");
  await page.waitForLoadState("networkidle");
  await caption(page, "Outcomes, measured — not claimed",
    "Straight-through-billing rate, calibrated accuracy, turnaround reduction, and the maturity pathway.", "OUTCOMES");
  await wait(page, 3);
  await shot(page, "dashboard");
  await wait(page, 2);
  await page.mouse.wheel(0, 500);
  await wait(page, 4);

  // ── 8 · Close ────────────────────────────────────────────────────────────
  await caption(page, "ACE — grounded, cited, and confidence-routed",
    "Autonomous AI medical coding · Nous Infosystems for Vee Healthtek.", "ACE");
  await wait(page, 4);

  expect(rad).toBeTruthy();
});
