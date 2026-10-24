// The mail surface. The site harness (serve.sh + shoot.mjs) cannot reach it:
// the issue in mail is a standalone HTML file rendered by the press, not a
// route, so nothing in this directory photographed it until 2026-10-24.
//
//   node mail.mjs <out-dir> <tag> <file.html> [file2.html ...]
//
// Shoots each file at the charter's three viewports in both colour schemes,
// then audits what a mail client actually breaks: horizontal overflow past
// the 600px table, text that fell below the canon's small-print floor, and
// any ink whose colour equals the paper it sits on, which is how a dark-mode
// rule that forgot a selector presents itself.
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { writeFileSync } from "node:fs";
import { basename, resolve } from "node:path";

const [out, tag, ...files] = process.argv.slice(2);
if (!out || !tag || !files.length) {
  console.error("usage: mail.mjs <out-dir> <tag> <file.html> [...]");
  process.exit(2);
}
mkdirSync(out, { recursive: true });

const VIEWPORTS = [
  ["iphone", 390, 844],
  ["ipad", 820, 1180],
  ["desktop", 1440, 900],
];
const SCHEMES = ["light", "dark"];

// What the audit reads out of the page, per frame.
const AUDIT = () => {
  const paper = (el) => {
    for (let n = el; n; n = n.parentElement) {
      const bg = getComputedStyle(n).backgroundColor;
      const m = bg.match(/rgba?\(([^)]+)\)/);
      if (!m) continue;
      const [r, g, b, a = "1"] = m[1].split(",").map((s) => s.trim());
      if (parseFloat(a) > 0) return [+r, +g, +b];
    }
    return [255, 255, 255];
  };
  const lum = ([r, g, b]) => {
    const f = (c) => {
      c /= 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const ratio = (a, b) => {
    const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
    return (x + 0.05) / (y + 0.05);
  };

  const doc = document.documentElement;
  const overflow = doc.scrollWidth - doc.clientWidth;

  const tiny = [];
  const invisible = [];
  const seen = new Set();
  for (const el of document.querySelectorAll("div, td, a, span, em")) {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const text = Array.from(el.childNodes)
      .filter((n) => n.nodeType === 3)
      .map((n) => n.textContent.trim())
      .join(" ")
      .trim();
    if (!text) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === "hidden" || cs.display === "none") continue;
    const size = parseFloat(cs.fontSize);
    const key = text.slice(0, 40) + "|" + el.tagName;
    if (seen.has(key)) continue;
    seen.add(key);
    if (size < 12) tiny.push({ text: text.slice(0, 60), size });
    const m = cs.color.match(/rgba?\(([^)]+)\)/);
    if (!m) continue;
    const [r2, g2, b2] = m[1].split(",").map((s) => parseFloat(s));
    const c = ratio([r2, g2, b2], paper(el));
    if (c < 3) {
      invisible.push({
        text: text.slice(0, 60),
        tag: el.tagName,
        cls: el.className || "",
        color: cs.color,
        paper: `rgb(${paper(el).join(", ")})`,
        ratio: +c.toFixed(2),
      });
    }
  }

  // Every element's right edge against the 600px table, which is the one
  // width a mail client will not reflow for us.
  const widest = Math.max(
    0,
    ...Array.from(document.querySelectorAll("*")).map((el) => {
      const r = el.getBoundingClientRect();
      return r.width ? r.right : 0;
    }),
  );

  return { overflow, widest: Math.round(widest), tiny, invisible };
};

const browser = await chromium.launch({
  executablePath: process.env.CHROME,
  args: ["--no-sandbox", "--force-color-profile=srgb"],
});
const report = {};
for (const file of files) {
  const name = basename(file).replace(/\.html$/, "");
  for (const scheme of SCHEMES) {
    for (const [vp, width, height] of VIEWPORTS) {
      const ctx = await browser.newContext({
        viewport: { width, height },
        colorScheme: scheme,
        deviceScaleFactor: 1,
        reducedMotion: "no-preference",
      });
      const page = await ctx.newPage();
      await page.goto("file://" + resolve(file));
      await page.waitForLoadState("load");
      const audit = await page.evaluate(AUDIT);
      const key = `${name}-${scheme}-${vp}`;
      report[key] = audit;
      await page.screenshot({
        path: `${out}/${name}-${tag}-${scheme}-${vp}-${width}x${height}.png`,
        fullPage: true,
      });
      await ctx.close();
      const bad =
        audit.overflow > 0 || audit.tiny.length || audit.invisible.length;
      console.log(
        `${bad ? "FAIL" : "ok  "} ${key.padEnd(34)} overflow=${audit.overflow} widest=${audit.widest} tiny=${audit.tiny.length} low-contrast=${audit.invisible.length}`,
      );
      for (const i of audit.invisible) {
        console.log(
          `       ${i.ratio}:1  ${i.tag}.${i.cls}  ${i.color} on ${i.paper}  "${i.text}"`,
        );
      }
      for (const t of audit.tiny) {
        console.log(`       ${t.size}px  "${t.text}"`);
      }
    }
  }
}
await browser.close();
writeFileSync(`${out}/mail-audit-${tag}.json`, JSON.stringify(report, null, 2));
console.log(`\nwrote ${out}/mail-audit-${tag}.json`);
