// MORPH_WHEEL is 480 in MarkLive.jsx: the turn completes over 480px of wheel
// delta while the page holds still. Spend exactly that and no more, so the
// frames are the machine, the middle of the turn, and the open book.
import fs from "node:fs";
import { chromium } from "playwright";
import { ourContext } from "./local-context.mjs";
const OUT = process.argv[2];
fs.mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch();
const ctx = await ourContext(browser, { viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
await page.goto(`http://127.0.0.1:${process.env.FE_PORT || 3000}/`, { waitUntil: "networkidle" });
await page.waitForTimeout(500);
const clip = { x: 420, y: 380, width: 600, height: 420 };
const shot = async (n) => {
  await page.screenshot({ path: `${OUT}/morph-desktop-${n}.png`, clip });
  console.log(`${n}: scrollY=${await page.evaluate(() => window.scrollY)}`);
};
await shot("0-machine");
for (let i = 0; i < 4; i++) { await page.mouse.wheel(0, 60); await page.waitForTimeout(130); }
await shot("1-mid");
for (let i = 0; i < 4; i++) { await page.mouse.wheel(0, 60); await page.waitForTimeout(130); }
await shot("2-book");
await ctx.close();
await browser.close();
