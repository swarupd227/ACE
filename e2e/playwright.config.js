// Playwright config for the ACE end-to-end demo capture.
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  timeout: 300000,
  expect: { timeout: 15000 },
  use: {
    baseURL: "http://localhost:8080",
    viewport: { width: 1366, height: 768 },
    video: { mode: "on", size: { width: 1366, height: 768 } },
    actionTimeout: 30000,
    launchOptions: { args: ["--force-device-scale-factor=1"] },
  },
  reporter: [["list"]],
  outputDir: "./recordings",
});
