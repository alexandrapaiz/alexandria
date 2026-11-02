// The social card the site serves to every link preview, executed.
//
//     node --test tests/social-card.test.mjs
//
// site/lib/social-card.js is loaded the way tests/waitlist.test.mjs loads its
// subject and for the same reason: the site is a Next.js app whose
// package.json declares no module type, so Node's own resolution of a .js file
// there is not the resolution Next performs. One difference — this subject
// imports a sibling, `./public-routes.js`, and a data: URL has no base to
// resolve that against, so the specifier is rewritten to the sibling's own
// absolute path before the source is evaluated. The sibling is loaded from
// disk either way, so the constant under test is the repository's.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const subject = fileURLToPath(new URL("../site/lib/social-card.js", import.meta.url));
const sibling = new URL("../site/lib/public-routes.js", import.meta.url).href;
const source = (await readFile(subject, "utf8")).replace("./public-routes.js", sibling);
const card = await import(
  "data:text/javascript;base64," + Buffer.from(source).toString("base64")
);

const await_origin = await import(
  "data:text/javascript;base64,"
    + Buffer.from((await readFile(fileURLToPath(new URL("../site/lib/public-routes.js", import.meta.url)), "utf8")))
        .toString("base64"),
);

const layout = await readFile(
  fileURLToPath(new URL("../site/app/layout.jsx", import.meta.url)),
  "utf8",
);

const WORDS = {
  title: "library of alexandr.ia",
  description: "What changed in AI research this week.",
};

// ------------------------------------------------------ what a crawler gets

test("every tag a link preview reads is present", () => {
  const m = card.socialCard(WORDS);
  assert.equal(m.openGraph.type, "website");
  assert.equal(m.openGraph.locale, "en_US");
  assert.equal(m.openGraph.title, WORDS.title);
  assert.equal(m.openGraph.description, WORDS.description);
  assert.equal(m.openGraph.siteName, WORDS.title);
  assert.equal(m.twitter.title, WORDS.title);
  assert.equal(m.twitter.description, WORDS.description);
});

test("og:url is not written here, because metadataBase resolves it per route", () => {
  // Writing it would stamp one address onto all eleven indexable routes.
  assert.equal("url" in card.socialCard(WORDS).openGraph, false);
});

// ------------------------------------------------- the image and the card type

test("with no image declared, the card is a summary and no image tag is emitted", () => {
  assert.equal(card.OG_IMAGE, null);
  const m = card.socialCard(WORDS);
  assert.equal(m.twitter.card, "summary");
  assert.equal("images" in m.openGraph, false);
});

test("declaring an image moves the card type with it, rather than leaving it behind", () => {
  // The two decisions are one decision. This executes the second half against
  // a copy of the module with the image set, so the coupling is tested rather
  // than described in a comment nobody re-reads.
  const patched = source.replace("export const OG_IMAGE = null;", 'export const OG_IMAGE = "/og.png";');
  assert.notEqual(patched, source, "the image declaration was not found to patch");
  return import("data:text/javascript;base64," + Buffer.from(patched).toString("base64")).then((withImage) => {
    const m = withImage.socialCard(WORDS);
    assert.equal(m.twitter.card, "summary_large_image");
    assert.deepEqual(m.openGraph.images, ["https://libraryofalexandria.dev/og.png"]);
  });
});

// ------------------------------------------------- the one way this breaks hard

test("the declared origin is a URL the constructor accepts", () => {
  // `app/layout.jsx` evaluates `new URL(SITE_ORIGIN)` at module load, so a
  // malformed origin is not a bad tag, it is every page of the site failing to
  // render. The constructor is the only validator that counts, so it is the one
  // this asserts with.
  const routes = await_origin;
  assert.doesNotThrow(() => new URL(routes.SITE_ORIGIN));
  assert.equal(new URL(routes.SITE_ORIGIN).protocol, "https:");
  assert.equal(routes.SITE_ORIGIN.endsWith("/"), false, "a trailing slash doubles in every resolved URL");
});

// ----------------------------------------------------------- the words

test("the card refuses to invent words the page does not have", () => {
  assert.throws(() => card.socialCard({ title: "only a title" }));
  assert.throws(() => card.socialCard({ description: "only a description" }));
  assert.throws(() => card.socialCard({}));
});

test("the layout declares the words once and hands them to the card", () => {
  // The wiring, checked as text because layout.jsx cannot be imported outside
  // Next. If somebody re-types the title into the card call, this fails.
  assert.match(layout, /const TITLE = /);
  assert.match(layout, /const DESCRIPTION =/);
  assert.match(layout, /socialCard\(\{\s*title:\s*TITLE,\s*description:\s*DESCRIPTION,?\s*\}\)/);
  assert.match(layout, /metadataBase: new URL\(SITE_ORIGIN\)/);
  // Three, counted rather than assumed: the declared constant, the nav logo
  // and the footer. The first draft of this test asserted two and the suite
  // corrected it. The two visible ones are rendered text in the house's own
  // lower case and belong to the frontend seat, so they are not folded into
  // TITLE here; what this number guards is a fourth appearance, which would
  // mean somebody re-typed the title into the metadata instead of reading it.
  assert.equal(
    (layout.match(/library of alexandr\.ia/g) || []).length,
    3,
    "the title appears as the declared constant, the nav logo and the footer, nowhere else",
  );
});
