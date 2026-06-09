import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 180_000,
  expect: { timeout: 120_000 },
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  webServer: {
    command: "pnpm dev",
    url: "http://localhost:5173",
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
