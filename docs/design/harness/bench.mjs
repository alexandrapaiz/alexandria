// Read the craft off the live pages rather than from memory. The measurement
// is every distinct (property, duration, easing) triple actually computed on
// the hoverable elements of the page, which is the only way to see whether a
// site runs one motion system or a pile of values (ban list entry 25).
import fs from "node:fs";
import { chromium } from "playwright";
const OUT = process.argv[2];
fs.mkdirSync(OUT, { recursive: true });
const SITES = [
  { id: "elicit", url: "https://elicit.com/" },
  { id: "linear", url: "https://linear.app/" },
  { id: "consensus", url: "https://consensus.app/" },
];
const browser = await chromium.launch();
for (const s of SITES) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  try {
    await page.goto(s.url, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForTimeout(3500);
    await page.screenshot({ path: `${OUT}/benchmark-${s.id}.png` });
    const m = await page.evaluate(() => {
      const triples = new Map();
      const els = [...document.querySelectorAll("a,button,[role=button],input,summary,li")].slice(0, 900);
      for (const el of els) {
        const cs = getComputedStyle(el);
        const props = cs.transitionProperty.split(",").map((x) => x.trim());
        const durs = cs.transitionDuration.split(",").map((x) => x.trim());
        const eases = cs.transitionTimingFunction.split(/,(?![^(]*\))/).map((x) => x.trim());
        props.forEach((p, i) => {
          const d = durs[i % durs.length], e = eases[i % eases.length];
          if (!d || d === "0s" || p === "none" || p === "all") return;
          const k = `${p} | ${d} | ${e}`;
          triples.set(k, (triples.get(k) || 0) + 1);
        });
      }
      const radii = new Map(), fonts = new Map();
      for (const el of els) {
        const cs = getComputedStyle(el);
        radii.set(cs.borderRadius, (radii.get(cs.borderRadius) || 0) + 1);
      }
      return {
        triples: [...triples.entries()].sort((a, b) => b[1] - a[1]).slice(0, 14),
        durations: [...new Set([...triples.keys()].map((k) => k.split(" | ")[1]))].sort(),
        curves: [...new Set([...triples.keys()].map((k) => k.split(" | ")[2]))],
        bodyFont: getComputedStyle(document.body).fontFamily.slice(0, 60),
      };
    });
    console.log(`\n===== ${s.id} =====`);
    console.log("durations in use:", m.durations.join("  "));
    console.log("curves in use:");
    m.curves.forEach((c) => console.log("   ", c));
    console.log("top (property | duration | easing):");
    m.triples.forEach(([k, n]) => console.log(`   ${String(n).padStart(4)}x  ${k}`));
  } catch (e) {
    console.log(`\n===== ${s.id} ===== FAILED: ${e.message.slice(0, 120)}`);
  }
  await ctx.close();
}
await browser.close();
