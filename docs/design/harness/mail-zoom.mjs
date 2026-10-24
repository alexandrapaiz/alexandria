// Close looks at the mail surface, at 1:1, because a full-page frame of an
// issue is five thousand pixels tall and every reading of it is a downscale.
//
//   node mail-zoom.mjs <out-dir> <file.html> <spec.json>
//
// The spec is a list of {name, text, pad, scheme, viewport}. `text` finds the
// element by the words in it, which is the only stable handle an inline-styled
// email gives you: it has no ids and five class names, all of them shared.
import { chromium } from "playwright";
import { mkdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const [out, file, specPath] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const spec = JSON.parse(readFileSync(specPath, "utf8"));

const browser = await chromium.launch({
  executablePath: process.env.CHROME,
  args: ["--no-sandbox", "--force-color-profile=srgb"],
});

for (const s of spec) {
  const [w, h] = s.viewport ?? [390, 844];
  const ctx = await browser.newContext({
    viewport: { width: w, height: h },
    colorScheme: s.scheme ?? "light",
    deviceScaleFactor: 1,
  });
  const page = await ctx.newPage();
  await page.goto("file://" + resolve(file));
  await page.waitForLoadState("load");

  const box = await page.evaluate((needle) => {
    // The innermost element that contains the words, so a <td> wrapper does
    // not win over the <div> that actually draws them.
    let best = null;
    for (const el of document.querySelectorAll("div, td, tr, table")) {
      if (!el.textContent.includes(needle)) continue;
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) continue;
      if (!best || r.height < best.h) {
        best = { x: r.x, y: r.y, w: r.width, h: r.height };
      }
    }
    return best;
  }, s.text);

  if (!box) {
    console.log(`MISS ${s.name}: no element contains "${s.text}"`);
    await ctx.close();
    continue;
  }
  const pad = s.pad ?? 16;
  const clip = {
    x: Math.max(0, box.x - pad),
    y: Math.max(0, box.y - pad),
    width: Math.min(w, box.w + pad * 2),
    height: box.h + pad * 2,
  };
  const tag = `${s.name}-${s.scheme ?? "light"}-${w}`;
  await page.screenshot({ path: `${out}/${tag}.png`, clip, fullPage: true });
  console.log(
    `ok   ${tag.padEnd(40)} ${Math.round(box.w)}x${Math.round(box.h)} at y=${Math.round(box.y)}`,
  );
  await ctx.close();
}
await browser.close();
