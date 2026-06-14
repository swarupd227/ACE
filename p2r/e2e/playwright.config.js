// Playwright config for P2R ingestion end-to-end tests (runs against the live app).
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  timeout: 240000,           // each ingestion calls the real model
  expect: { timeout: 150000 },
  fullyParallel: false,
  workers: 1,                // one at a time — shared backend DB
  use: {
    baseURL: process.env.P2R_BASE_URL || "http://localhost:8180",
    viewport: { width: 1366, height: 768 },
    actionTimeout: 30000,
    video: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  reporter: [["list"]],
  outputDir: "./recordings",
});
