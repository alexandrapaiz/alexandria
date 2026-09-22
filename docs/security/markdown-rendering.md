# Rendering a body the corpus wrote

Engineer run 2026-09-22. Closes the `urgent` ledger entry "Sanitize the issue
body before it renders as HTML" (2026-09-19, security agent) for the web
surfaces. The email surface is still open and is recorded at the bottom.

## The hole

`site/app/library/[week]/page.jsx` passed an issue body through `marked.parse`
into `dangerouslySetInnerHTML`. `marked` has not sanitized HTML since v8, so
raw HTML in the body reached the page intact.

The body is not ours. `pipeline/weekly.py` has gpt-oss-120b write it from
claims distilled out of arXiv abstracts and full text, and anyone can put text
on arXiv. So the chain from a crafted passage in a paper to live HTML on
alexandr.ia had no human being in it anywhere. `/desk` and `/skills` share the
same sink on bodies a human merged, which is lower risk and the same bug.

## What the fix is, and what it deliberately is not

It is not a sanitizer. Writing one is how people get this wrong, because the
interesting failures are in the parsing rather than the filtering: mXSS,
foreign content in `<svg>` and `<math>`, comment tricks, unclosed tags. A
sanitizer also means trusting that a rewritten string became harmless.

Instead no HTML is allowed through at all. Raw HTML in the source becomes
visible text, so the only tags that can reach the page are the ones `marked`
generates from markdown syntax, and those are safe because markdown syntax
cannot express a script or an event handler. That leaves URLs as the one place
where an attacker still chooses a string the browser will act on, so hrefs get
their own check.

Three parts:

1. **Escape.** The renderer's `html` hook turns every raw HTML token, block and
   inline, into escaped text. `<script>alert(1)</script>` renders as those
   eighteen visible characters.
2. **Refuse.** `safeHref` allows `http`, `https`, `mailto`, and anything with
   no scheme at all, which covers relative paths, fragments and queries.
   Everything else is refused, `data:` included, because a data URL is a
   document the browser will run and no issue needs one. A refused link loses
   its link and keeps its words, so the reader still gets the sentence.
3. **Check, then fail closed.** `unsafeHtmlReason` reads the finished HTML and
   names anything markdown cannot legitimately produce. When it finds
   something, `renderMarkdown` renders the body as escaped text instead. The
   first two parts are the defence and this is the proof they held, which
   matters on the day a `marked` upgrade routes HTML around the renderer.

## Where it lives

- `site/lib/markdown-core.js` holds every decision as pure import-free
  functions. Import-free is a requirement, not a preference: the test loads it
  by evaluating its source, so the logic runs in CI with no `node_modules`.
- `site/lib/markdown.js` is the wiring, and it is deliberately thin. It builds
  a private `Marked` instance rather than calling `marked.use()`, because
  `use()` mutates the library's shared singleton and a hardening any other
  import could switch off is not a hardening.
- The library, desk and skills routes call `renderMarkdown`. Nothing else on
  the site may import `marked`, and a test asserts it.

## The allow-lists are measured

`ALLOWED_TAGS` and `ALLOWED_ATTRS` are not a guess at what markdown produces.
`tools/check_markdown_render.mjs` renders a document covering the whole of GFM
through an unmodified `marked` and re-derives both lists, then fails if the
library emits anything the allow-list does not name. That failure matters
because it is not a security hole, it is the reverse: an unlisted tag would
make the tripwire fire on a legitimate issue and drop the archive to plain
text. The check keeps that discovery in the test run rather than on the page.

The one false-positive class found while building this is worth recording. A
scan that looked for `name=` across a whole tag found `n=` inside the quoted
title of `[the paper](https://arxiv.org/abs/1 "n=1 ablation")` and called a
good issue dangerous. Attribute values have to be consumed with their names,
which is what `attributesOf` does.

## Evidence

- `tests/markdown.test.mjs`, 54 executed cases, no `node_modules` needed.
- `tests/test_markdown.py`, 11 source guards, including the one that matters
  most for regression: a fourth surface rendering a body the direct way fails
  a test.
- `tools/check_markdown_render.mjs`, 47 checks against real `marked` 15.0.12,
  31 of them attacks.
- The real 2026-W37 issue, both gold skills and the current sprint file all
  render byte for byte identically to the old unsafe path, so this closes the
  hole without changing a single published page.
- `next build` passes and a payload-carrying fixture served by `next start`
  renders every attack as visible text. The only tag with attributes anywhere
  in that rendered issue was the legitimate citation link.

## Still open: the email

`send_newsletter` in `pipeline/weekly.py` builds the HTML part with Python's
`markdown` library, and that library passes raw HTML through exactly the way
`marked` does. Verified against the pinned `markdown==3.7`: a `<script>` block
survives, an `onerror` attribute survives live, and `[click](javascript:...)`
becomes a working `href`. Every subscriber gets that part.

This run did not fix it, for three reasons stated plainly rather than left
implicit. It lives in `pipeline/weekly.py`, which this seat's own open PR #60
is already editing. The likely fix adds a dependency to the Modal image, and
image changes are governed by `docs/agents/runtime-changes.md`. And the web
surface was the one with a session on it. It is recorded in `docs/ideas.md`
with status `urgent` so tomorrow's run and the PM both see it.
