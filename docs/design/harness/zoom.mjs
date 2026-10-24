// Close looks. A full-page screenshot of a 5000px page scaled to fit is not a
// look at the type; this shoots viewport-sized frames at a given scroll offset,
// or clips a named element, so the pixels are judged at 1:1.
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";
import { ourContext } from "./local-context.mjs";
const BASE = `http://127.0.0.1:${process.env.FE_PORT || 3000}`;
const [, , OUT, SPECJSON] = process.argv;
fs.mkdirSync(OUT, { recursive: true });
const specs = JSON.parse(SPECJSON);
// `page.evaluate` given a STRING evaluates it as an expression. So a spec that
// passes "() => { rows[1].open = true }" does not open anything: it evaluates
// to a function object, Playwright serialises that as undefined, and the run
// gets a screenshot of the state it asked to change plus a probe that reads
// `undefined`. Nothing errors. On 2026-10-15 that produced three frames of
// closed rows labelled as open frames, and the only reason it was caught is
// that the probe printed `undefined` where it should have printed a count.
//
// So both forms are accepted and a function is always called. A spec may pass
// an expression, an arrow function, or an IIFE, and all three do the obvious
// thing. This is the harness's job rather than the spec author's, because the
// failure is silent and the spec author is a different run each week.
const call = (src) =>
  `(() => { const _f = (${src}); return typeof _f === "function" ? _f() : _f; })()`;

const browser = await chromium.launch();
for (const s of specs) {
  const vp = s.vp || { width: 1440, height: 900 };
  const ctx = await ourContext(browser, {
    viewport: vp,
    hasTouch: !!s.touch, isMobile: !!s.touch,
    reducedMotion: s.reducedMotion || "no-preference",
  });
  const page = await ctx.newPage();
  if (s.touch) {
    const cdp = await ctx.newCDPSession(page);
    await cdp.send("Emulation.setEmulatedMedia", { features: [
      { name: "hover", value: "none" }, { name: "pointer", value: "coarse" },
      { name: "any-hover", value: "none" }, { name: "any-pointer", value: "coarse" }] });
  }
  await page.goto(BASE + s.url, { waitUntil: "networkidle" });
  // Same guard shoot.mjs carries. A stale server serving chunk hashes that no
  // longer exist returns 200 for the document and 400 for every asset, so the
  // page is unstyled and unhydrated while curl reports a perfect 200 with the
  // right byte count. Caught once this run; it fails loudly here now.
  const sane = await page.evaluate(() => ({
    styled: getComputedStyle(document.body).fontFamily.length > 0 &&
            getComputedStyle(document.querySelector("nav,header") || document.body).display !== "inline",
    err: /Application error|client-side exception/.test(document.body.innerText || ""),
    sheets: document.styleSheets.length,
  }));
  if (sane.err || sane.sheets === 0) {
    console.error(`FAIL ${s.id}: page did not render (sheets=${sane.sheets}, appError=${sane.err})`);
    process.exit(1);
  }
  if (s.scroll) { await page.evaluate((y) => window.scrollTo(0, y), s.scroll); await page.waitForTimeout(700); }
  if (s.eval) await page.evaluate(call(s.eval));
  if (s.wait) await page.waitForTimeout(s.wait);
  const file = path.join(OUT, `${s.id}.png`);
  if (s.clip) {
    const box = await page.locator(s.clip).first().boundingBox();
    if (!box) { console.log(`${s.id}: SELECTOR NOT FOUND ${s.clip}`); await ctx.close(); continue; }
    const pad = s.pad ?? 16;
    await page.screenshot({ path: file, clip: {
      x: Math.max(0, box.x - pad), y: Math.max(0, box.y - pad),
      width: Math.min(vp.width - Math.max(0, box.x - pad), box.width + pad * 2),
      height: Math.min(vp.height - Math.max(0, box.y - pad), box.height + pad * 2) } });
  } else {
    await page.screenshot({ path: file });
  }
  if (s.probe) console.log(`${s.id}:`, JSON.stringify(await page.evaluate(call(s.probe))));
  console.log(`${s.id} -> ${file}`);
  await ctx.close();
}
await browser.close();
