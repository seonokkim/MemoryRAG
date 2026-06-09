import { expect, test } from "@playwright/test";

/**
 * Live stack E2E: FE (Vite proxy) → FastAPI coach workflow.
 * Prerequisite: backend running at http://127.0.0.1:8000 with .env loaded.
 */
test.describe("AI Coach live API", () => {
  test("coach chat uses real backend (not mock fallback)", async ({ page }) => {
    const coachResponses: { status: number; body: unknown }[] = [];
    page.on("response", async response => {
      if (response.url().includes("/api/coach/chat") && response.request().method() === "POST") {
        coachResponses.push({
          status: response.status(),
          body: await response.json().catch(() => null),
        });
      }
    });

    await page.goto("/coach");
    await expect(page.getByText("LIVE API")).toBeVisible({ timeout: 15_000 });

    await page.getByRole("button", { name: "Why do I keep slicing?" }).click();

    await expect(page.getByTestId("coach-live-reply")).toBeVisible({ timeout: 120_000 });
    await expect(page.getByText(/Coach API error/i)).not.toBeVisible();

    expect(coachResponses.length).toBeGreaterThan(0);
    const last = coachResponses[coachResponses.length - 1];
    expect(last.status).toBe(200);
    const body = last.body as {
      conversation_id?: number;
      message_id?: number;
      answer?: string;
    };
    expect(body.conversation_id).toBeGreaterThan(0);
    expect(body.message_id).toBeGreaterThan(0);
    expect(body.answer?.length).toBeGreaterThan(10);
  });
});
