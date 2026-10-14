// The same measurement run against the benchmark sites, turned on ourselves.
// Computed values across every page, so var() tokens resolve and comments do
// not count. Ban list entry 25's test.
import { chromium } from "playwright";
const PAGES = ["/", "/library", "/library/2026-W39", "/skills", "/graph", "/pricing", "/mission", "/desk", "/routines", "/nope"];
const browser = await chromium.launch();
const all = new Map();
for (const vpid of ["desktop", "iphone"]) {
  const vp = vpid === "desktop" ? { width: 1440, height: 900 } : { width: 390, height: 844 };
  const ctx = await browser.newContext({ viewport: vp, hasTouch: vpid !== "desktop", isMobile: vpid !== "desktop", deviceScaleFactor: 1 });
  await ctx.route("**/*", (r) => { const u = new URL(r.request().url()); return (u.hostname === "127.0.0.1" || u.hostname === "localhost") ? r.continue() : r.abort(); });
  for (const p of PAGES) {
    const page = await ctx.newPage();
    await page.goto("http://127.0.0.1:3000" + p, { waitUntil: "networkidle" });
    const t = await page.evaluate(() => {
      const out = [];
      for (const el of document.querySelectorAll("body *")) {
        const cs = getComputedStyle(el);
        const props = cs.transitionProperty.split(",").map((x) => x.trim());
        const durs = cs.transitionDuration.split(",").map((x) => x.trim());
        const eases = cs.transitionTimingFunction.split(/,(?![^(]*\))/).map((x) => x.trim());
        props.forEach((pr, i) => {
          const d = durs[i % durs.length], e = eases[i % eases.length];
          if (!d || d === "0s" || pr === "none") return;
          out.push(`${pr} | ${d} | ${e}`);
        });
        if (cs.animationName && cs.animationName !== "none") {
          cs.animationName.split(",").map((x) => x.trim()).forEach((n, i) => {
            const d = cs.animationDuration.split(",").map((x) => x.trim())[i] || "";
            const e = cs.animationTimingFunction.split(/,(?![^(]*\))/).map((x) => x.trim())[i] || "";
            out.push(`@${n} | ${d} | ${e}`);
          });
        }
      }
      return out;
    });
    t.forEach((k) => all.set(k, (all.get(k) || 0) + 1));
    await page.close();
  }
  await ctx.close();
}
await browser.close();
const rows = [...all.entries()].sort((a, b) => b[1] - a[1]);
const durs = new Set(), curves = new Set();
rows.forEach(([k]) => { const [, d, e] = k.split(" | "); durs.add(d.trim()); curves.add(e.trim()); });
console.log("OUR distinct durations:", [...durs].sort().join("  "));
console.log("OUR distinct curves:");
[...curves].forEach((c) => console.log("   ", c));
console.log("\n(property | duration | easing):");
rows.forEach(([k, n]) => console.log(`  ${String(n).padStart(5)}x  ${k}`));
