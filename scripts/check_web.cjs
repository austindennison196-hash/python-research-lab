/* Real-browser integration checks; requires the optional Playwright development tool. */
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_EXECUTABLE_PATH || undefined,
    headless: true,
    args: ["--no-sandbox"],
  });
  try {
    const page = await browser.newPage({
        viewport: { width: 1440, height: 1100 },
      }),
      errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    const base = process.env.WEB_TEST_URL || "http://127.0.0.1:8765";
    await page.goto(base);
    await page.locator("#loading").waitFor({ state: "hidden" });
    assert.equal(await page.locator("#state-count").textContent(), "2");
    assert.equal(await page.locator("#notation").textContent(), "((x)(x)x)");
    await page.locator("#state").selectOption("111000");
    assert.equal(await page.locator("#notation").textContent(), "(((x)x)x)");
    assert.equal(await page.locator("#tree svg circle").count(), 3);
    await page.locator("#generation").fill("6");
    assert.equal(await page.locator("#state-count").textContent(), "42");
    await page.locator("#depth").selectOption("1");
    assert.equal(await page.locator("#state-count").textContent(), "1");
    await page.locator("#depth").selectOption("0");
    assert.equal(await page.locator("#state-count").textContent(), "0");
    assert.match(
      await page.locator("#selected-word").textContent(),
      /No reachable/,
    );
    await page.locator("#rule").selectOption("zero_occupancy");
    assert.equal(await page.locator("#selected-word").textContent(), "1111110");
    assert.equal(await page.locator("#depth").isDisabled(), true);
    await page.locator("#reset").click();
    await page.locator('#history [data-word="111000"]').click();
    assert.equal(await page.locator("#selected-word").textContent(), "111000");
    const downloadPromise = page.waitForEvent("download");
    await page.locator("#export").click();
    const download = await downloadPromise;
    const exported = JSON.parse(
      await fs.readFile(await download.path(), "utf8"),
    );
    assert.equal(exported.generation, 3);
    assert.equal(exported.states.length, 2);
    assert.ok(exported.transitions.length > 0);
    await page.locator("#play").click();
    await page.waitForFunction(
      () => document.querySelector("#generation").value === "1",
    );
    await page.locator("#play").click();
    await page.locator('[data-tab="physics"]').click();
    await page.locator("#omega").fill("2");
    assert.match(await page.locator("#energy").textContent(), /2\.0000 J/);
    await page.locator("#motion-toggle").click();
    assert.match(await page.locator("#motion-toggle").textContent(), /Resume/);
    await page.locator('[data-tab="information"]').click();
    await page.locator("#probability").fill("0");
    assert.equal(
      await page.locator("#entropy-value").textContent(),
      "0.0000 bits",
    );
    await page.locator("#probability").fill("0.25");
    assert.equal(
      await page.locator("#entropy-value").textContent(),
      "0.8113 bits",
    );
    await page.goto(
      `${base}/#structures?rule=dyck_insertion&generation=4&state=10101010&depth=none`,
    );
    await page.locator("#loading").waitFor({ state: "hidden" });
    assert.equal(await page.locator("#state-count").textContent(), "14");
    assert.equal(
      await page.locator("#selected-word").textContent(),
      "10101010",
    );
    await page.locator("#reset").click();
    await page.screenshot({
      path: "/tmp/research-lab-desktop.png",
      fullPage: true,
    });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({
      path: "/tmp/research-lab-mobile.png",
      fullPage: true,
    });
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth,
      ),
      false,
    );
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.reload();
    await page.locator("#loading").waitFor({ state: "hidden" });
    assert.match(await page.locator("#motion-toggle").textContent(), /Resume/);
    assert.deepEqual(errors, []);
    await page.route("**/data.json", (route) =>
      route.fulfill({ status: 503, body: "unavailable" }),
    );
    await page.reload();
    await page.locator("#error").waitFor({ state: "visible" });
    assert.equal(await page.locator("#export").isDisabled(), true);
    console.log(
      "PASS: real-browser navigation, state/tree updates, constrained paths, export, playback, scientific controls, shared view, responsive layout, reduced motion, and load failure.",
    );
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
