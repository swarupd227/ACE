// End-to-end ingestion tests for the P2R Policy Workbench, against the live app + real model.
// Covers the three ingest paths: built-in sample, pasted text, and uploaded PDF (OCR).
const { test, expect } = require("@playwright/test");
const fs = require("fs");
const path = require("path");

const PDF_PATH = path.join(__dirname, "fixture_policy.pdf");

// Build a minimal, valid single-page PDF with synthetic policy text (no external libs).
function buildPdf() {
  const lines = [
    "SUMMIT HEALTH PLAN - MEDICAL POLICY: MRI OF THE KNEE",
    "Effective Date: 2026-03-01",
    "COVERAGE",
    "MRI of the knee without contrast (73721) is medically necessary for internal",
    "derangement after six weeks of failed conservative therapy.",
    "PRIOR AUTHORIZATION",
    "Prior authorization is required for outpatient knee MRI (73721).",
    "FREQUENCY",
    "Repeat knee MRI within 12 months of a prior study is not covered.",
    "DOCUMENTATION",
    "The order must document the duration of symptoms and prior treatment.",
  ];
  const parts = ["BT", "/F1 11 Tf", "50 740 Td", "13 TL"];
  lines.forEach((ln, i) => {
    const esc = ln.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
    if (i === 0) parts.push(`(${esc}) Tj`);
    else { parts.push("T*"); parts.push(`(${esc}) Tj`); }
  });
  parts.push("ET");
  const content = Buffer.from(parts.join("\n"), "latin1");
  const objs = [
    Buffer.from("<</Type/Catalog/Pages 2 0 R>>"),
    Buffer.from("<</Type/Pages/Kids[3 0 R]/Count 1>>"),
    Buffer.from("<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>"),
    Buffer.from("<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>"),
    Buffer.concat([Buffer.from(`<</Length ${content.length}>>\nstream\n`), content, Buffer.from("\nendstream")]),
  ];
  let out = Buffer.from("%PDF-1.4\n");
  const offsets = [];
  objs.forEach((o, i) => {
    offsets.push(out.length);
    out = Buffer.concat([out, Buffer.from(`${i + 1} 0 obj\n`), o, Buffer.from("\nendobj\n")]);
  });
  const xref = out.length;
  let x = `xref\n0 ${objs.length + 1}\n0000000000 65535 f \n`;
  offsets.forEach((off) => { x += String(off).padStart(10, "0") + " 00000 n \n"; });
  x += `trailer\n<</Size ${objs.length + 1}/Root 1 0 R>>\nstartxref\n${xref}\n%%EOF\n`;
  return Buffer.concat([out, Buffer.from(x)]);
}

const PROVISION_BADGES = /COVERAGE|PRIOR_AUTH|FREQUENCY|DOCUMENTATION|BUNDLING|MODIFIER|POS/;

test.beforeAll(() => { fs.writeFileSync(PDF_PATH, buildPdf()); });
test.afterAll(() => { try { fs.unlinkSync(PDF_PATH); } catch {} });

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("p2r_role", "Admin"));
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Policy Workbench" })).toBeVisible();
});

// Open a document in the list by (partial) title and assert its provisions render.
async function openDocAndAssertProvisions(page, titleRe) {
  const card = page.getByText(titleRe).first();
  await expect(card).toBeVisible({ timeout: 180000 });
  await card.click();
  await expect(page.getByRole("button", { name: /Generate rule recommendations/ })).toBeVisible({ timeout: 30000 });
  await expect(page.getByText(PROVISION_BADGES).first()).toBeVisible();
}

test("ingest the built-in sample policy", async ({ page }) => {
  await page.getByRole("button", { name: /Ingest sample policy/ }).click();
  await openDocAndAssertProvisions(page, /Advanced Imaging of the Lumbar Spine/);
});

test("ingest a pasted policy", async ({ page }) => {
  const text = [
    "E2E PASTE POLICY — LUMBAR SPINE MRI",
    "COVERAGE: MRI of the lumbar spine (72148) is covered for persistent low back pain.",
    "PRIOR AUTHORIZATION: Prior authorization is required for outpatient lumbar MRI (72148).",
    "FREQUENCY: A repeat lumbar MRI within 6 months is not covered absent a clinical change.",
  ].join("\n");
  await page.getByRole("button", { name: /Paste a policy/ }).click();
  await page.getByPlaceholder(/Meridian Health Plan/).fill("E2E Health Plan");
  await page.getByPlaceholder(/Advanced Imaging Policy/).fill("E2E Paste Policy");
  await page.getByPlaceholder(/Paste the full payer policy text/).fill(text);
  await page.getByRole("button", { name: /Extract provisions/ }).click();
  await openDocAndAssertProvisions(page, /E2E Paste Policy/);
});

test("ingest an uploaded PDF via OCR", async ({ page }) => {
  await page.getByRole("button", { name: /Upload PDF/ }).click();
  await page.getByPlaceholder(/CMS LCD/).fill("E2E Upload Plan");
  await page.getByPlaceholder(/defaults to the file name/).fill("E2E Upload Policy");
  await page.setInputFiles('input[type="file"]', PDF_PATH);
  await openDocAndAssertProvisions(page, /E2E Upload Policy/);
});
