// The integration check: the real site/lib/markdown.js, the real marked, and a
// corpus of the things a paper could put in a digest body.
//
//     node tools/check_markdown_render.mjs
//
// tests/markdown.test.mjs executes every pure decision without marked
// installed, which is what runs in CI. This is the other half, and it needs
// node_modules: it proves the decisions are actually wired to the parser, and
// it re-derives the allow-lists from the live library so a marked upgrade that
// starts emitting a new tag fails here instead of quietly widening what the
// page accepts.
//
// Exit 0 when every case holds, 1 on the first that does not.

import { cp, mkdtemp, readFile, symlink, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

// Where marked lives. site/node_modules is the normal answer; MARKED_MODULES
// lets a sandbox that installed it elsewhere point at it.
function findModules() {
  const candidates = [
    process.env.MARKED_MODULES,
    path.join(REPO, "site", "node_modules"),
    path.join(REPO, "node_modules"),
  ].filter(Boolean);
  return candidates.find((dir) => existsSync(path.join(dir, "marked", "package.json")));
}

const modules = findModules();
if (!modules) {
  console.error(
    "marked is not installed. `cd site && npm install`, or set MARKED_MODULES.\n" +
      "The pure half of this check runs without it: node --test tests/markdown.test.mjs",
  );
  process.exit(1);
}

// site/ is a Next.js app whose package.json declares no module type, so Node
// parses its .js files as CommonJS and importing markdown.js directly fails.
// Staging copies the two real files, unmodified, beside a package.json that
// says module. What runs below is the source that ships.
const stage = await mkdtemp(path.join(tmpdir(), "alexandria-markdown-"));
await writeFile(path.join(stage, "package.json"), JSON.stringify({ type: "module" }));
for (const file of ["markdown.js", "markdown-core.js"]) {
  await cp(path.join(REPO, "site", "lib", file), path.join(stage, file));
}
await symlink(modules, path.join(stage, "node_modules"), "dir");

const { renderMarkdown } = await import(path.join(stage, "markdown.js"));
const core = await import(path.join(stage, "markdown-core.js"));
const { Marked } = await import(path.join(stage, "node_modules", "marked", "lib", "marked.esm.js"));

const version = JSON.parse(
  await readFile(path.join(modules, "marked", "package.json"), "utf8"),
).version;

// A second opinion, written independently of markdown-core.js on purpose. If
// both this and the tripwire agree the output is inert, two different readings
// of the HTML agree. It has to tokenize properly for the same reason the
// tripwire does: `&lt;img src=x onerror=...&gt;` is escaped text, not a tag,
// and a regex over the whole string cannot tell those apart.
const DANGEROUS_TAGS =
  /^(script|iframe|svg|math|object|embed|style|form|base|meta|link|body|input|textarea|button|audio|video|details)$/i;

function looksExecutable(html) {
  const tags = /<\/?([a-zA-Z][a-zA-Z0-9-]*)((?:"[^"]*"|'[^']*'|[^>])*)>/g;
  for (const tag of html.matchAll(tags)) {
    const name = tag[1].toLowerCase();
    // <input> is the one marked emits, for a task list, and only ever as a
    // disabled checkbox. Anything else wearing that name did not come from
    // markdown syntax.
    if (name === "input" && /^\s*(checked=""\s*)?disabled=""\s*type="checkbox"\s*$/.test(tag[2])) {
      continue;
    }
    if (DANGEROUS_TAGS.test(name)) return true;

    const attrs = /([a-zA-Z_:][a-zA-Z0-9_:.-]*)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s"'`=<>]+))?/g;
    for (const attr of tag[2].matchAll(attrs)) {
      const attribute = attr[1].toLowerCase();
      if (attribute.startsWith("on")) return true;
      const raw = attr[2] ?? "";
      const value = /^["']/.test(raw) ? raw.slice(1, -1) : raw;
      if (
        (attribute === "href" || attribute === "src") &&
        !/^(https?:|mailto:|[/#?]|$)/i.test(value.trim()) &&
        /^[a-z][a-z0-9+.-]*:/i.test(value.trim())
      ) {
        return true;
      }
    }
  }
  return false;
}

let failures = 0;
function check(name, condition, detail) {
  if (condition) {
    console.log(`  [PASS] ${name}`);
  } else {
    failures += 1;
    console.log(`  [FAIL] ${name}`);
    if (detail !== undefined) console.log(`         ${detail}`);
  }
}

// ---------------------------------------------------------------- the corpus
//
// Every one of these is something a crafted arXiv passage could carry into a
// digest body. The assertion is the same each time: whatever else the page
// says, it must not contain a live version of this.

const attacks = [
  ["a script block", "<script>alert(1)</script>"],
  ["an img onerror", '<img src=x onerror="alert(1)">'],
  ["an svg onload", "<svg/onload=alert(1)>"],
  ["an iframe", '<iframe src="https://evil.example"></iframe>'],
  ["a body onload", "<body onload=alert(1)>"],
  ["a style block", "<style>*{background:url(javascript:alert(1))}</style>"],
  ["an HTML comment", "<!-- <script>alert(1)</script> -->"],
  ["a javascript: link", "[click](javascript:alert(1))"],
  ["an entity-encoded javascript: link", "[click](&#106;avascript:alert(1))"],
  ["a hex-entity javascript: link", "[click](&#x6a;avascript:alert(1))"],
  ["a mixed-case javascript: link", "[click](JaVaScRiPt:alert(1))"],
  ["a tab-split javascript: link", "[click](java\tscript:alert(1))"],
  ["a data: URL link", "[click](data:text/html,<script>alert(1)</script>)"],
  ["a vbscript: link", "[click](vbscript:msgbox(1))"],
  ["a javascript: image", "![x](javascript:alert(1))"],
  ["a data: image", "![x](data:text/html,<script>alert(1)</script>)"],
  ["an autolink to javascript:", "<javascript:alert(1)>"],
  ["a title-attribute break-out", '[click](https://x.co "a\\" onmouseover=\\"alert(1)")'],
  ["an alt-attribute break-out", '![a" onerror="alert(1)](https://x.co/i.png)'],
  ["a base tag", '<base href="https://evil.example/">'],
  ["a form and input", '<form action="https://evil.example"><input name=p></form>'],
  ["an object tag", '<object data="https://evil.example/x.swf"></object>'],
  ["a meta refresh", '<meta http-equiv="refresh" content="0;url=https://evil.example">'],
  ["a link rel stylesheet", '<link rel="stylesheet" href="https://evil.example/x.css">'],
  ["nested raw HTML in a blockquote", "> <img src=x onerror=alert(1)>"],
  ["raw HTML inside a list item", "- <img src=x onerror=alert(1)>"],
  ["raw HTML inside emphasis", "*<img src=x onerror=alert(1)>*"],
  ["raw HTML inside a link's text", "[<img src=x onerror=alert(1)>](https://x.co)"],
  ["raw HTML inside a table cell", "| a |\n|---|\n| <img src=x onerror=alert(1)> |"],
  ["a reference-style javascript: link", "[click][k]\n\n[k]: javascript:alert(1)"],
];

console.log(`\nmarked ${version}, ${attacks.length} attack cases\n`);

// The output is dangerous if it contains a tag, attribute or URL that markdown
// cannot legitimately produce. unsafeHtmlReason is the same judgment the render
// path applies, so asserting with it here also asserts it is strict enough:
// every case below would be caught by it if the renderer ever stopped working.
for (const [name, source] of attacks) {
  const html = renderMarkdown(source);
  const leaked = core.unsafeHtmlReason(html);
  const executable = looksExecutable(html);

  check(name, leaked === null && !executable, `leaked=${leaked} html=${JSON.stringify(html)}`);
}

// ------------------------------------------------------- the legitimate issue
//
// A hardening that also breaks the product is not a fix, so the things a real
// issue does have to keep working.

console.log("\nthe issue still renders\n");

const real = [
  ["a heading", "# The week in agents", /<h1>The week in agents<\/h1>/],
  ["a citation link", "[Attention](https://arxiv.org/abs/1706.03762)", /<a href="https:\/\/arxiv\.org\/abs\/1706\.03762">Attention<\/a>/],
  ["a link with a title", '[x](https://arxiv.org/abs/1 "the paper")', /title="the paper"/],
  ["emphasis and strong", "*a* and **b**", /<em>a<\/em> and <strong>b<\/strong>/],
  ["a fenced code block", "```python\nx = 1\n```", /<pre><code class="language-python">/],
  ["a table", "| a | b |\n|:--|--:|\n| 1 | 2 |", /<th align="left">a<\/th>/],
  ["a task list", "- [x] done", /<input checked="" disabled="" type="checkbox">/],
  ["a relative link", "[all issues](/library)", /<a href="\/library">/],
  ["a mailto link", "[write](mailto:hello@alexandr.ia)", /<a href="mailto:hello@alexandr\.ia">/],
  ["an image", "![a plot](https://arxiv.org/i.png)", /<img src="https:\/\/arxiv\.org\/i\.png" alt="a plot">/],
  ["an autolink", "<https://arxiv.org/abs/1>", /<a href="https:\/\/arxiv\.org\/abs\/1">/],
  ["angle brackets in code stay literal", "`<b>`", /<code>&lt;b&gt;<\/code>/],
];

for (const [name, source, expected] of real) {
  const html = renderMarkdown(source);
  check(name, expected.test(html), `html=${JSON.stringify(html)}`);
}

// The words survive even when the markup does not: a refused link keeps its
// text, and raw HTML becomes something the reader can see.
const refused = renderMarkdown("[the paper](javascript:alert(1))");
check("a refused link keeps its words", refused.includes("the paper"), JSON.stringify(refused));
const shown = renderMarkdown("<script>alert(1)</script>");
check("raw HTML becomes visible text", shown.includes("&lt;script&gt;"), JSON.stringify(shown));

// ------------------------------------------------- the allow-lists are honest
//
// Re-derive what this version of marked emits for the whole of GFM. If it
// emits something the allow-list does not name, the tripwire would fire on a
// legitimate issue and the archive would degrade to plain text. That is a
// failure here, today, rather than on the page.

console.log("\nthe allow-lists match this marked\n");

const gfm = `# h1
## h2
### h3
#### h4
##### h5
###### h6

para *em* **strong** ~~del~~ \`code\`, a [link](https://x.co "t"), a line\\
break.

![alt](https://x.co/i.png "it")

> quote

- a
- [ ] todo
- [x] done

3. three
4. four

\`\`\`python
x = "<b>"
\`\`\`

| a | b | c |
|:--|--:|:-:|
| 1 | 2 | 3 |

---
`;

const plain = new Marked({ gfm: true }).parse(gfm);
const emittedTags = new Set();
const emittedAttrs = new Set();
for (const tag of plain.matchAll(/<\/?([a-zA-Z][a-zA-Z0-9-]*)((?:"[^"]*"|'[^']*'|[^>])*)>/g)) {
  emittedTags.add(tag[1].toLowerCase());
  for (const attr of tag[2].matchAll(/([a-zA-Z_:][a-zA-Z0-9_:.-]*)\s*=/g)) {
    emittedAttrs.add(attr[1].toLowerCase());
  }
}

const unlistedTags = [...emittedTags].filter((t) => !core.ALLOWED_TAGS.includes(t));
const unlistedAttrs = [...emittedAttrs].filter((a) => !core.ALLOWED_ATTRS.includes(a));
check("every tag marked emits is allow-listed", unlistedTags.length === 0, `unlisted: ${unlistedTags}`);
check("every attribute marked emits is allow-listed", unlistedAttrs.length === 0, `unlisted: ${unlistedAttrs}`);
check("the whole GFM document renders unchanged", core.unsafeHtmlReason(renderMarkdown(gfm)) === null,
  core.unsafeHtmlReason(renderMarkdown(gfm)));
console.log(`         tags: ${[...emittedTags].sort().join(" ")}`);
console.log(`         attrs: ${[...emittedAttrs].sort().join(" ")}`);

console.log(
  `\n${failures === 0 ? "OK" : "FAILED"} — ${attacks.length + real.length + 5} checks, ${failures} failed\n`,
);
process.exit(failures === 0 ? 0 : 1);
