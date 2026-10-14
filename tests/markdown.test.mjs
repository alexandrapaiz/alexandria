// Every decision site/lib/markdown-core.js makes, executed.
//
//     node --test tests/markdown.test.mjs
//
// tests/test_markdown.py runs this too, so `python3 -m pytest tests/ -q`
// covers it and there is still one command for the whole suite.
//
// This half needs no node_modules, which is why it is the half that runs in
// CI: the core module is import-free, so it loads by evaluating its source,
// the same way tests/accounts.test.mjs loads account-core.js. The other half,
// the real parser against a corpus of attacks, is
// tools/check_markdown_render.mjs and it needs marked installed.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const path = fileURLToPath(new URL("../site/lib/markdown-core.js", import.meta.url));
const source = await readFile(path, "utf8");
const core = await import(
  "data:text/javascript;base64," + Buffer.from(source).toString("base64")
);

// ------------------------------------------------------------------ escaping

test("escapeHtml closes every character that could open a tag or an attribute", () => {
  assert.equal(
    core.escapeHtml('<img src=x onerror="alert(1)">'),
    "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;",
  );
  assert.equal(core.escapeHtml("a & b"), "a &amp; b");
  assert.equal(core.escapeHtml("it's"), "it&#39;s");
  // The ampersand has to go first, or every other escape gets double-escaped.
  assert.equal(core.escapeHtml("&lt;"), "&amp;lt;");
});

test("escapeHtml treats nothing as empty rather than printing 'undefined'", () => {
  assert.equal(core.escapeHtml(undefined), "");
  assert.equal(core.escapeHtml(null), "");
});

// --------------------------------------------------------------------- hrefs

const REFUSED = [
  ["a plain javascript URL", "javascript:alert(1)"],
  ["a capitalised one", "JaVaScRiPt:alert(1)"],
  ["a leading-space one", "   javascript:alert(1)"],
  ["a decimal-entity one", "&#106;avascript:alert(1)"],
  ["a zero-padded decimal entity", "&#0000106;avascript:alert(1)"],
  ["a hex-entity one", "&#x6a;avascript:alert(1)"],
  ["an unterminated entity", "&#106avascript:alert(1)"],
  ["a tab inside the scheme", "java\tscript:alert(1)"],
  ["a newline inside the scheme", "java\nscript:alert(1)"],
  ["a null byte inside the scheme", "java\u0000script:alert(1)"],
  ["an &colon; entity", "javascript&colon;alert(1)"],
  ["a data URL", "data:text/html,<script>alert(1)</script>"],
  ["a data image URL", "data:image/svg+xml;base64,PHN2Zz4="],
  ["vbscript", "vbscript:msgbox(1)"],
  ["a file URL", "file:///etc/passwd"],
  ["an empty href", ""],
  ["whitespace only", "   "],
  ["nothing at all", null],
];

for (const [name, href] of REFUSED) {
  test(`safeHref refuses ${name}`, () => {
    assert.equal(core.safeHref(href), null);
  });
}

const ALLOWED = [
  ["an arXiv citation", "https://arxiv.org/abs/1706.03762"],
  ["plain http", "http://example.com"],
  ["a mailto", "mailto:hello@alexandr.ia"],
  ["a site-relative path", "/library/2026-W37"],
  ["a fragment", "#the-week"],
  ["a query", "?week=2026-W37"],
  ["a protocol-relative URL", "//cdn.example.com/a.png"],
  ["a bare relative path", "notes/tuesday.md"],
];

for (const [name, href] of ALLOWED) {
  test(`safeHref allows ${name}`, () => {
    assert.equal(core.safeHref(href), href.trim());
  });
}

test("safeHref does not mistake a colon in a path for a scheme", () => {
  // Without the guard that a scheme ends before the first / ? or #, this
  // relative path reads as a `notes` scheme and a real link disappears.
  assert.equal(core.safeHref("notes/tuesday:2pm"), "notes/tuesday:2pm");
  assert.equal(core.safeHref("/a/b:c"), "/a/b:c");
  assert.equal(core.safeHref("#a:b"), "#a:b");
});

test("safeHref keeps the href it was given, not a rewritten one", () => {
  // A refusal drops the link. Nothing here scrubs a URL and hands back
  // something a reader has to trust became harmless.
  const url = "https://arxiv.org/abs/1?q=a&b=c#s2";
  assert.equal(core.safeHref(url), url);
});

// ----------------------------------------------------------------- renderers

test("the html renderer turns raw HTML into text a reader can see", () => {
  const renderer = core.hardenedRenderer();
  assert.equal(
    renderer.html({ type: "html", text: "<script>alert(1)</script>" }),
    "&lt;script&gt;alert(1)&lt;/script&gt;",
  );
  assert.equal(renderer.html({ text: "<img src=x onerror=alert(1)>" }),
    "&lt;img src=x onerror=alert(1)&gt;");
  // Older marked handed the renderer a string. Accepting both costs one
  // ternary and means a downgrade cannot silently stop escaping.
  assert.equal(renderer.html("<b>"), "&lt;b&gt;");
  assert.equal(renderer.html({}), "");
});

// marked calls these with `this.parser` available. This is the smallest stand-in
// that behaves the way the real one does for a text token.
const withParser = (renderer) => {
  const bound = {};
  for (const [key, fn] of Object.entries(renderer)) {
    bound[key] = fn.bind({
      parser: { parseInline: (tokens) => (tokens ?? []).map((t) => t.text ?? "").join("") },
    });
  }
  return bound;
};

test("a link with a safe href renders as a link", () => {
  const r = withParser(core.hardenedRenderer());
  assert.equal(
    r.link({ href: "https://arxiv.org/abs/1", title: null, tokens: [{ text: "Attention" }] }),
    '<a href="https://arxiv.org/abs/1">Attention</a>',
  );
});

test("a link with a refused href keeps its words and loses its link", () => {
  const r = withParser(core.hardenedRenderer());
  const html = r.link({ href: "javascript:alert(1)", title: null, tokens: [{ text: "the paper" }] });
  assert.equal(html, "the paper");
  assert.ok(!html.includes("<a"));
});

test("a link title cannot break out of its attribute", () => {
  const r = withParser(core.hardenedRenderer());
  const html = r.link({
    href: "https://x.co",
    title: 'a" onmouseover="alert(1)',
    tokens: [{ text: "click" }],
  });
  assert.ok(html.includes("&quot;"), html);
  assert.equal(core.unsafeHtmlReason(html), null);
});

test("an image alt cannot break out of its attribute", () => {
  const r = withParser(core.hardenedRenderer());
  const html = r.image({ href: "https://x.co/i.png", title: null, text: 'a" onerror="alert(1)' });
  assert.ok(html.includes("&quot;"), html);
  assert.equal(core.unsafeHtmlReason(html), null);
});

test("an image with a refused src keeps its alt text", () => {
  const r = withParser(core.hardenedRenderer());
  assert.equal(r.image({ href: "javascript:alert(1)", text: "a plot" }), "a plot");
});

// ---------------------------------------------------------------- attributes

test("attributesOf reads a value as a value, not as more attributes", () => {
  // The regression this exists for. A link title legitimately reads
  // "n=1 ablation", and a scan that hunted for `name=` across the whole tag
  // found `n=` inside the quoted value and called a good issue dangerous.
  const pairs = core.attributesOf(' href="https://x.co" title="n=1 ablation"');
  assert.deepEqual(pairs.map((p) => p.attribute), ["href", "title"]);
  assert.equal(pairs[1].value, "n=1 ablation");
});

test("attributesOf reads marked's valueless task-list attributes", () => {
  const pairs = core.attributesOf(' checked="" disabled="" type="checkbox"');
  assert.deepEqual(pairs.map((p) => p.attribute), ["checked", "disabled", "type"]);
});

// ------------------------------------------------------------------ tripwire

test("the tripwire passes the HTML markdown legitimately produces", () => {
  const fine = [
    "<h1>The week in agents</h1>",
    '<p>a <a href="https://arxiv.org/abs/1" title="n=1">link</a>.</p>',
    '<pre><code class="language-python">x = &quot;&lt;b&gt;&quot;\n</code></pre>',
    '<table>\n<thead>\n<tr>\n<th align="left">a</th>\n</tr>\n</thead>\n</table>',
    '<li><input checked="" disabled="" type="checkbox"> done</li>',
    '<p><img src="https://x.co/i.png" alt="a plot"></p>',
    "<p>a<br>b</p>",
    "<ol start=\"3\"><li>three</li></ol>",
  ];
  for (const html of fine) assert.equal(core.unsafeHtmlReason(html), null, html);
});

test("the tripwire does not fire on prose that talks about attributes", () => {
  // The escaping already happened, so this is text. A checker that flagged it
  // would drop a legitimate issue to plain text for writing about the bug.
  assert.equal(core.unsafeHtmlReason("<p>the paper sets onerror= on the tag</p>"), null);
  assert.equal(
    core.unsafeHtmlReason("<p><code>&lt;img src=x onerror=alert(1)&gt;</code></p>"),
    null,
  );
});

const CAUGHT = [
  ["a script tag", "<p><script>alert(1)</script></p>"],
  ["an svg", "<p><svg onload=alert(1)></svg></p>"],
  ["an iframe", '<p><iframe src="https://evil.example"></iframe></p>'],
  ["an event handler", '<p><img src="/a.png" onerror="alert(1)"></p>'],
  ["a javascript href", '<p><a href="javascript:alert(1)">x</a></p>'],
  ["an entity-encoded javascript href", '<p><a href="&#106;avascript:alert(1)">x</a></p>'],
  ["a data src", '<p><img src="data:text/html,x"></p>'],
  ["an HTML comment", "<!-- x --><p>a</p>"],
  ["a doctype", "<!DOCTYPE html><p>a</p>"],
  ["a style attribute", '<p style="position:fixed">a</p>'],
  ["an unescaped angle bracket", "<p>a < b</p>"],
];

for (const [name, html] of CAUGHT) {
  test(`the tripwire catches ${name}`, () => {
    assert.notEqual(core.unsafeHtmlReason(html), null, html);
  });
}

test("the tripwire refuses anything that is not a string", () => {
  for (const value of [null, undefined, 7, {}]) {
    assert.notEqual(core.unsafeHtmlReason(value), null);
  }
});

// ------------------------------------------------------------------ fallback

test("the fallback keeps every word and executes nothing", () => {
  const html = core.escapedFallback("# Title\n\n<script>alert(1)</script>");
  assert.ok(html.includes("# Title"));
  assert.ok(html.includes("&lt;script&gt;"));
  assert.equal(core.unsafeHtmlReason(html), null);
});

test("the scheme allow-list is only the three schemes an issue needs", () => {
  assert.deepEqual([...core.SAFE_SCHEMES].sort(), ["http", "https", "mailto"]);
});
