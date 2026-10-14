// The weekly visual sweep harness.
//
// Three guards exist because of what the 2026-09-30 run recorded. A placeholder
// Clerk key makes clerkMiddleware issue a dev-browser handshake, so every
// screenshot becomes a photograph of a Clerk error document that audits
// perfectly clean. So: every request leaving localhost is blocked, every page
// is asserted to carry a known marker from our own markup before it is
// photographed, and the run fails loudly rather than reporting clean.
//
// The touch viewports force `hover: none` and `pointer: coarse` through CDP,
// because headless Chromium otherwise reports `hover: hover` inside a touch
// context and every @media (hover: none) rule in the stylesheet goes untested.
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const BASE = "http://127.0.0.1:3000";
const OUT = process.argv[2];
const TAG = process.argv[3] || "after";
const ONLY = process.argv[4] || null;
fs.mkdirSync(OUT, { recursive: true });

const VIEWPORTS = [
  { id: "iphone", width: 390, height: 844, touch: true, dsf: 1 },
  { id: "ipad", width: 820, height: 1180, touch: true, dsf: 1 },
  { id: "desktop", width: 1440, height: 900, touch: false, dsf: 1 },
];

const PAGES = [
  { id: "home", url: "/" },
  { id: "library", url: "/library" },
  { id: "issue", url: "/library/2026-W39" },
  { id: "skills", url: "/skills" },
  { id: "graph", url: "/graph" },
  { id: "pricing", url: "/pricing" },
  { id: "mission", url: "/mission" },
  { id: "desk", url: "/desk" },
  { id: "routines", url: "/routines" },
  { id: "notfound", url: "/this-route-does-not-exist" },
];

const failures = [];
const report = [];

const browser = await chromium.launch();

for (const vp of VIEWPORTS) {
  const ctx = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    deviceScaleFactor: vp.dsf,
    hasTouch: vp.touch,
    isMobile: vp.touch,
    reducedMotion: "no-preference",
  });

  // Guard 1: nothing leaves localhost. A handshake redirect to a Clerk host
  // cannot succeed, so it surfaces as a failure instead of as a clean report.
  await ctx.route("**/*", (route) => {
    const u = new URL(route.request().url());
    if (u.hostname === "127.0.0.1" || u.hostname === "localhost") return route.continue();
    return route.abort();
  });

  for (const pg of PAGES) {
    if (ONLY && pg.id !== ONLY) continue;
    const page = await ctx.newPage();
    if (vp.touch) {
      const cdp = await ctx.newCDPSession(page);
      await cdp.send("Emulation.setEmulatedMedia", {
        features: [
          { name: "hover", value: "none" },
          { name: "pointer", value: "coarse" },
          { name: "any-hover", value: "none" },
          { name: "any-pointer", value: "coarse" },
        ],
      });
    }
    const resp = await page.goto(BASE + pg.url, { waitUntil: "networkidle", timeout: 30000 });

    // Guard 2: prove this is our page, from our own markup, before shooting.
    const landed = new URL(page.url());
    const marker = await page.evaluate(() => {
      const wordmark = document.querySelector('a[href="/"]')?.textContent?.trim() || "";
      return {
        host: location.hostname,
        title: document.title,
        wordmark,
        hasNav: !!document.querySelector("nav"),
        bodyChars: (document.body.innerText || "").length,
        h1: document.querySelector("h1")?.innerText?.trim().slice(0, 80) || "",
      };
    });
    const ok =
      (landed.hostname === "127.0.0.1" || landed.hostname === "localhost") &&
      /alexandr/i.test(marker.title) &&
      marker.hasNav &&
      marker.bodyChars > 200;
    if (!ok) {
      failures.push({ page: pg.id, vp: vp.id, status: resp?.status(), landed: page.url(), marker });
      await page.close();
      continue;
    }

    // Measurements that a screenshot cannot settle on its own.
    const audit = await page.evaluate(() => {
      const docW = document.documentElement.scrollWidth;
      const vw = window.innerWidth;
      const out = { docW, vw, overflowX: docW > vw + 1, offenders: [], small: [], faded: [], h1x: null };
      const h1 = document.querySelector("h1");
      if (h1) out.h1x = Math.round(h1.getBoundingClientRect().left);
      for (const el of document.querySelectorAll("body *")) {
        const r = el.getBoundingClientRect();
        const cs = getComputedStyle(el);
        if (cs.display === "none" || cs.visibility === "hidden") continue;
        if (r.width > 0 && (r.right > vw + 1 || r.left < -1)) {
          out.offenders.push({
            tag: el.tagName, cls: el.className?.toString?.().slice(0, 60) || "",
            left: Math.round(r.left), right: Math.round(r.right),
            text: (el.textContent || "").trim().slice(0, 40),
          });
        }
        const tappable = el.matches("a,button,input,select,summary,[role=button]");
        if (tappable && r.width > 0 && r.height > 0 && (r.width < 44 || r.height < 44)) {
          out.small.push({
            tag: el.tagName, cls: el.className?.toString?.().slice(0, 40) || "",
            w: Math.round(r.width), h: Math.round(r.height),
            text: (el.textContent || "").trim().slice(0, 34),
          });
        }
        if (parseFloat(cs.opacity) === 0 && r.width > 4 && r.height > 4) {
          out.faded.push({
            tag: el.tagName, cls: el.className?.toString?.().slice(0, 40) || "",
            text: (el.textContent || "").trim().slice(0, 34),
          });
        }
      }
      // Only the first few of each; the point is to look, not to drown.
      out.offenders = out.offenders.slice(0, 12);
      out.small = out.small.slice(0, 12);
      out.faded = out.faded.slice(0, 12);
      return out;
    });

    const file = path.join(OUT, `${pg.id}-${vp.id}-${TAG}.png`);
    await page.screenshot({ path: file, fullPage: true });
    report.push({ page: pg.id, vp: vp.id, status: resp.status(), title: marker.title, h1: marker.h1, bytes: fs.statSync(file).size, ...audit });
    await page.close();
  }
  await ctx.close();
}
await browser.close();

fs.writeFileSync(path.join(OUT, `_audit-${TAG}.json`), JSON.stringify({ report, failures }, null, 2));

if (failures.length) {
  console.error(`FAIL: ${failures.length} page/viewport combinations did not render our site.`);
  console.error(JSON.stringify(failures.slice(0, 4), null, 2));
  process.exit(1);
}

// Guard 3: uniform byte sizes across different pages mean identical renders.
const sizes = report.map((r) => r.bytes);
const spread = (Math.max(...sizes) - Math.min(...sizes)) / Math.max(...sizes);
console.log(`shot ${report.length} frames, byte-size spread ${(spread * 100).toFixed(1)}%`);
if (spread < 0.05) {
  console.error("FAIL: every frame is within 5% of the same size. That is what identical renders look like.");
  process.exit(1);
}
for (const r of report) {
  const flags = [
    r.overflowX ? `OVERFLOW doc=${r.docW}>vw=${r.vw}` : "",
    r.offenders.length ? `outside=${r.offenders.length}` : "",
    r.small.length ? `small=${r.small.length}` : "",
    r.faded.length ? `opacity0=${r.faded.length}` : "",
  ].filter(Boolean).join(" ");
  console.log(`${r.page.padEnd(10)} ${r.vp.padEnd(8)} h1x=${String(r.h1x).padStart(4)} ${flags}`);
}
