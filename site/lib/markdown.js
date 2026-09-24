import { Marked } from "marked";
import {
  escapedFallback,
  hardenedRenderer,
  unsafeHtmlReason,
} from "./markdown-core.js";

// The one place markdown becomes HTML. Every surface that renders a body goes
// through here, because the bodies are not ours: an issue is written by a model
// from arXiv text that anyone can upload, and `marked` has not sanitized HTML
// since v8. What raw HTML is allowed to become, and which hrefs are allowed to
// survive, is decided in markdown-core.js and executed by tests/markdown.test.mjs.
//
// This is a private Marked instance and not `marked.use()`, which mutates the
// library's shared singleton. A hardening that any other import could switch
// off is not a hardening.
const parser = new Marked({ gfm: true, renderer: hardenedRenderer() });

export function renderMarkdown(source) {
  if (source === null || source === undefined || source === "") return "";

  let html;
  try {
    html = parser.parse(String(source));
  } catch (error) {
    console.error("[markdown] parse failed, rendering as text:", error?.message);
    return escapedFallback(source);
  }

  // Fail closed. The hardening above should make this unreachable, and the
  // point is what happens on the day it is not: a marked upgrade that routes
  // HTML around the renderer loses the page's formatting here rather than
  // handing the page to whoever wrote the paper.
  const reason = unsafeHtmlReason(html);
  if (reason) {
    console.error(`[markdown] refused to render: ${reason}`);
    return escapedFallback(source);
  }

  return html;
}
