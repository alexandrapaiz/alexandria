// The states the charter names: the scroll reveal's range actually opening at
// every viewport (ban list 24 is invisible in a normal browser), the morph's
// start and end, reduced motion, and hover under a real pointer profile.
import fs from "node:fs";
import { chromium } from "playwright";
import { ourContext } from "./local-context.mjs";
const BASE = `http://127.0.0.1:${process.env.FE_PORT || 3000}`;
const OUT = process.argv[2];
fs.mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch();
const VPS = [
  { id: "iphone", width: 390, height: 844, touch: true },
  { id: "ipad", width: 820, height: 1180, touch: true },
  { id: "desktop", width: 1440, height: 900, touch: false },
];

// 1. The scene-two reveal, measured at rest and after scrolling, every viewport.
console.log("== scene two: computed opacity at rest -> after scroll ==");
for (const vp of VPS) {
  const ctx = await ourContext(browser, { viewport: { width: vp.width, height: vp.height }, hasTouch: vp.touch, isMobile: vp.touch });
  const page = await ctx.newPage();
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  const sel = [".statement", ".hero-act", ".about-inline"];
  const rest = await page.evaluate((s) => s.map((x) => { const e = document.querySelector(x); return e ? +getComputedStyle(e).opacity : null; }), sel);
  // Scroll to the bottom in steps, the way a reader does.
  await page.evaluate(async () => {
    const h = document.documentElement.scrollHeight;
    for (let y = 0; y <= h; y += 200) { window.scrollTo(0, y); await new Promise((r) => requestAnimationFrame(r)); }
  });
  await page.waitForTimeout(900);
  const after = await page.evaluate((s) => s.map((x) => { const e = document.querySelector(x); return e ? +getComputedStyle(e).opacity : null; }), sel);
  console.log(`${vp.id.padEnd(8)} rest=${JSON.stringify(rest)} -> scrolled=${JSON.stringify(after)}`);
  await page.screenshot({ path: `${OUT}/home-scene2-${vp.id}.png` });
  await ctx.close();
}

// 2. The morph. On desktop it is driven by wheel; on touch it autoplays.
console.log("== morph ==");
{
  const ctx = await ourContext(browser, { viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  await page.waitForTimeout(400);
  // The budget is MORPH_WHEEL in MarkLive.jsx, which is 480px of wheel delta
  // for the whole turn, so half of it is the middle and all of it is the
  // book. This script used to spend 14 * 90 before the "mid" frame and 24 * 90
  // more before the "book" frame, which is 1260 and then 3420 against a budget
  // of 480. Both overspends land past the turn, the completed morph schedules
  // its flight to scene two after 450ms, and the frames this script filed as
  // "the middle of the turn" and "the open book" were two photographs of
  // scene two with no mark in them at all. They audited clean, which is
  // `INC-2026-10-15-the-visual-harness-had-three-traps` happening again: a
  // frame labelled as a state it does not show. morph.mjs in this directory
  // had the number right the whole time; this script reinvented it.
  const MORPH_WHEEL = 480;
  const spend = async (px) => {
    for (let i = 0; i < 4; i++) { await page.mouse.wheel(0, px / 4); await page.waitForTimeout(130); }
  };
  await page.screenshot({ path: `${OUT}/morph-desktop-0-machine.png`, clip: { x: 360, y: 100, width: 720, height: 760 } });
  await spend(MORPH_WHEEL / 2);
  console.log("scrollY at half the turn (must be 0, the page holds still):", await page.evaluate(() => window.scrollY));
  await page.screenshot({ path: `${OUT}/morph-desktop-1-mid.png`, clip: { x: 360, y: 100, width: 720, height: 760 } });
  await spend(MORPH_WHEEL / 2);
  console.log("scrollY at the end of the turn (must be 0):", await page.evaluate(() => window.scrollY));
  await page.screenshot({ path: `${OUT}/morph-desktop-2-book.png`, clip: { x: 360, y: 100, width: 720, height: 760 } });
  await ctx.close();
}
{
  const ctx = await ourContext(browser, { viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  await page.goto(BASE + "/", { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(250);
  await page.screenshot({ path: `${OUT}/morph-start-iphone.png`, clip: { x: 60, y: 260, width: 270, height: 340 } });
  await page.waitForTimeout(3200);
  await page.screenshot({ path: `${OUT}/morph-end-iphone.png`, clip: { x: 60, y: 260, width: 270, height: 340 } });
  console.log("phone scrollY (must be 0, the morph may not scroll the page):", await page.evaluate(() => window.scrollY));
  await ctx.close();
}

// 3. Reduced motion: the reduced experience must be a designed one, not a
//    broken one, which means everything legible at rest.
console.log("== prefers-reduced-motion ==");
for (const vp of VPS) {
  const ctx = await ourContext(browser, { viewport: { width: vp.width, height: vp.height }, hasTouch: vp.touch, isMobile: vp.touch, reducedMotion: "reduce" });
  const page = await ctx.newPage();
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  await page.waitForTimeout(600);
  const op = await page.evaluate(() => [".statement", ".hero-act", ".about-inline"].map((x) => { const e = document.querySelector(x); return e ? +getComputedStyle(e).opacity : null; }));
  console.log(`${vp.id.padEnd(8)} reduced-motion opacity at rest = ${JSON.stringify(op)}`);
  if (vp.id === "desktop") await page.screenshot({ path: `${OUT}/home-reducedmotion-desktop.png`, fullPage: true });
  await ctx.close();
}
await browser.close();
