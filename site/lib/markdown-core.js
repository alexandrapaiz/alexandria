// Every decision about what markdown is allowed to become, as pure functions.
// No imports, no marked, no DOM. The parser lives next door in markdown.js,
// which is four lines of wiring; everything that could get a script onto the
// page is decided here, where it can be executed by a test.
//
// Keep this file import-free. tests/markdown.test.mjs loads it by reading the
// source and evaluating it, the same trick account-core.js already relies on,
// and that works precisely because there is nothing here to resolve.
//
// Why this exists. The archive renders an issue body that gpt-oss-120b wrote
// from arXiv text, and anyone can put text on arXiv. `marked` stopped
// sanitizing HTML at v8, so before this module a crafted passage in a paper
// reached alexandr.ia as live HTML with no human anywhere in the chain.
//
// The defence is not a sanitizer. Writing an HTML sanitizer is how people get
// this wrong: mXSS, foreign content, comment tricks, unclosed tags. Instead no
// HTML is allowed through at all. Raw HTML in the source becomes visible text,
// so the only tags that can reach the page are the ones marked generates from
// markdown syntax, and those are safe by construction. That leaves URLs as the
// one place an attacker still chooses a string the browser will execute, so
// hrefs get their own check.

// Measured, not guessed: the tags and attributes marked 15 actually emits for
// the whole of GFM (headings, tables, task lists, fenced code, images, rules).
// tools/check_markdown_render.mjs re-derives both lists from the live library,
// so a marked upgrade that starts emitting something new fails a test instead
// of silently widening what the page will accept.
export const ALLOWED_TAGS = [
  "a", "blockquote", "br", "code", "del", "em", "h1", "h2", "h3", "h4", "h5",
  "h6", "hr", "img", "input", "li", "ol", "p", "pre", "strong", "sup",
  "table", "tbody", "td", "th", "thead", "tr", "ul",
];

export const ALLOWED_ATTRS = [
  "align", "alt", "checked", "class", "disabled", "href", "src", "start",
  "title", "type",
];

// http and https for the citations, mailto because an issue may print an
// address. Everything else is refused, `data:` included: a data URL is a
// document the page will run, and no digest needs one.
export const SAFE_SCHEMES = ["http", "https", "mailto"];

export function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// Decode the entity forms a browser resolves inside an attribute, because
// `&#106;avascript:alert(1)` is a working javascript: URL and a plain string
// comparison never sees it. One pass, which is what a browser does too.
function decodeEntities(value) {
  return String(value)
    .replace(/&#x([0-9a-f]+);?/gi, (_, hex) => codePoint(parseInt(hex, 16)))
    .replace(/&#(\d+);?/g, (_, dec) => codePoint(parseInt(dec, 10)))
    .replace(/&colon;/gi, ":")
    .replace(/&tab;/gi, "\t")
    .replace(/&newline;/gi, "\n")
    .replace(/&sol;/gi, "/")
    .replace(/&quot;/gi, '"')
    .replace(/&apos;/gi, "'")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&amp;/gi, "&");
}

function codePoint(number) {
  if (!Number.isFinite(number) || number < 0 || number > 0x10ffff) return "";
  try {
    return String.fromCodePoint(number);
  } catch {
    return "";
  }
}

/**
 * The href to print, or null when there is no safe way to print it.
 *
 * Returning null rather than a scrubbed string is deliberate. A link whose
 * target we refuse loses its link and keeps its words, which is honest: the
 * reader sees the sentence, and no one has to trust that a rewritten URL
 * became harmless.
 */
export function safeHref(raw) {
  if (raw === null || raw === undefined) return null;
  const href = String(raw).trim();
  if (href === "") return null;

  // What the browser will see: entities resolved, and every character it
  // ignores inside a scheme removed. `java\tscript:` and `java&#10;script:`
  // both navigate, so both have to be tested in their collapsed form.
  const probe = decodeEntities(href)
    .replace(/[\u0000-\u0020\u007f-\u00a0\u2028\u2029\ufeff]/g, "")
    .toLowerCase();

  // A scheme is only a scheme before the first /, ? or #. Without that guard
  // the relative path `notes/tuesday:2pm` reads as a `notes` scheme.
  const scheme = probe.match(/^([a-z][a-z0-9+.-]*):/);
  if (scheme) {
    const authority = probe.search(/[/?#]/);
    const colonAt = probe.indexOf(":");
    if (authority === -1 || colonAt < authority) {
      return SAFE_SCHEMES.includes(scheme[1]) ? href : null;
    }
  }

  // No scheme at all: a relative path, a fragment, a query, or //host.
  return href;
}

/**
 * The renderer overrides that do the work, as a plain object for marked's
 * `renderer` option. Three of marked's methods are replaced and the rest of
 * its output is left exactly as it was.
 */
export function hardenedRenderer() {
  return {
    // Raw HTML, inline or block. It becomes text, so <script>alert(1)</script>
    // renders as those eighteen visible characters.
    html(token) {
      return escapeHtml(typeof token === "string" ? token : token?.text ?? "");
    },

    link(token) {
      const inner = this.parser.parseInline(token.tokens ?? []);
      const href = safeHref(token.href);
      if (href === null) return inner;
      const title = token.title ? ` title="${escapeHtml(token.title)}"` : "";
      return `<a href="${escapeHtml(href)}"${title}>${inner}</a>`;
    },

    image(token) {
      const alt = escapeHtml(token.text ?? "");
      const href = safeHref(token.href);
      if (href === null) return alt;
      const title = token.title ? ` title="${escapeHtml(token.title)}"` : "";
      return `<img src="${escapeHtml(href)}" alt="${alt}"${title}>`;
    },
  };
}

/**
 * The attributes of one tag, as {attribute, value} pairs.
 *
 * This consumes each value along with its name, which is the whole point: a
 * link title legitimately reads `n=1 ablation`, and a scan that walked the
 * attribute text looking for `name=` would find `n=` inside that quoted value
 * and call a perfectly good issue dangerous. The escaping has already made the
 * value inert, so what is inside it is text, not markup.
 */
export function attributesOf(attributeText) {
  const pairs = [];
  const syntax = /([a-zA-Z_:][a-zA-Z0-9_:.-]*)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s"'`=<>]+))?/g;
  for (const match of String(attributeText ?? "").matchAll(syntax)) {
    const raw = match[2] ?? "";
    pairs.push({
      attribute: match[1].toLowerCase(),
      value: /^["']/.test(raw) ? raw.slice(1, -1) : raw,
    });
  }
  return pairs;
}

/**
 * The tripwire. Reads finished HTML and returns why it must not be rendered,
 * or null when it is clean.
 *
 * This is not the defence, it is the proof that the defence held. It exists
 * because the defence above depends on marked calling the overrides for every
 * HTML token, and a marked upgrade could add a token type that reaches the
 * page another way. Scanning the output with a regex is sound here, and only
 * here: escaping has already turned every `<` in the text into `&lt;`, so a
 * `<` in this string is always a tag marked generated.
 */
export function unsafeHtmlReason(html) {
  if (typeof html !== "string") return "the renderer produced no string";

  // Comments, doctypes and processing instructions are not tags and the tag
  // scan below would not see them. Markdown never produces one.
  if (/<[!?]/.test(html)) return "the output contains a comment or doctype";

  const tags = /<\/?([a-zA-Z][a-zA-Z0-9-]*)((?:"[^"]*"|'[^']*'|[^>])*)>/g;
  for (const tag of html.matchAll(tags)) {
    const name = tag[1].toLowerCase();
    if (!ALLOWED_TAGS.includes(name)) {
      return `<${name}> is not a tag markdown produces`;
    }
    for (const { attribute, value } of attributesOf(tag[2])) {
      if (!ALLOWED_ATTRS.includes(attribute)) {
        return `${attribute}= on <${name}> is not an attribute markdown produces`;
      }
      if ((attribute === "href" || attribute === "src") && safeHref(decodeEntities(value)) === null) {
        return `an unsafe ${attribute} survived on <${name}>`;
      }
    }
  }

  // Every `<` has to have been part of one of those tags. A leftover one is
  // unescaped text, which is the whole bug this module exists to close.
  const angles = (html.match(/</g) || []).length;
  const opened = (html.match(tags) || []).length;
  if (angles !== opened) return "the output contains an unescaped <";

  return null;
}

/**
 * What to render when the tripwire fires: the issue as text, with its markup
 * lost and every character intact. The reader still gets the words, which is
 * the right failure for a newsletter, and nothing executes.
 */
export function escapedFallback(source) {
  return `<pre class="digest-plain">${escapeHtml(source)}</pre>`;
}
