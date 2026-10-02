"""The email escapes its text and does not escape its links.

The 2026-09-22 ledger entry "URGENT: the emailed issue has the same HTML hole
the archive had" asked for two things: escape raw HTML on the way into the
email, and "refuse any href whose scheme is not http, https or mailto". The
2026-09-24 template rewrite did the first and only the first. Every slot in
`render` goes through `html.escape` except one, `item_url`, which lands in
`<a href="{{item_url}}">` in site/emails/digest.html, and `inline` escapes a
link's text before it builds the anchor but never looks at the scheme.

So the body is safe and the links are not. The body of an issue is written by
a model from arXiv text, and the URL in a source line is copied out of that
text, which means the shortest path from a crafted paper to a live attribute
in a subscriber's inbox runs through a field nothing checks.

These tests hold the three sinks that reach a reader:

1. `item_url`, the source link under every item, which is the unescaped one.
2. `inline`, the links inside item bodies and bullet points.
3. `legacy_html`, the fallback email, which runs the markdown library with
   `extensions=["extra"]` and passes raw HTML straight through. It only ships
   when the designed render raises, and that is exactly the moment nobody is
   reading the output.

Run with `python3 tests/test_email_urls.py` or under pytest.
"""

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if "modal" not in sys.modules:
    modal = types.ModuleType("modal")
    modal.Cron = lambda *a, **k: None
    modal.Secret = types.SimpleNamespace(from_name=lambda *a, **k: None)

    class _Image:
        def __getattr__(self, name):
            return lambda *a, **k: self

    modal.Image = types.SimpleNamespace(debian_slim=lambda *a, **k: _Image())
    modal.App = lambda *a, **k: types.SimpleNamespace(
        function=lambda *a, **k: (lambda f: f),
        local_entrypoint=lambda *a, **k: (lambda f: f),
    )
    sys.modules["modal"] = modal

from pipeline import email_render as er  # noqa: E402
from pipeline import weekly  # noqa: E402

RECIPIENT = "reader@example.com"
UNSUB = "mailto:hello@alexandr.ia?subject=Unsubscribe"


def issue_with_source(url: str, label: str = "arXiv") -> str:
    """The smallest issue that carries one item with one source link."""
    return (
        "# A week of small print\n\n"
        "The opening paragraph, which the template needs.\n\n"
        "## What shipped\n\n"
        "- **An item with a source**\n"
        f"  *A paper title* — [{label}]({url}) and a sentence after it.\n"
        "  Evidence: 14 of 14 cases.\n"
    )


def render(body: str) -> str:
    return er.render_issue(body, "2026-W40", RECIPIENT, UNSUB)


# ---------------- 1. item_url, the unescaped slot ----------------

def test_a_quote_in_a_source_url_cannot_open_a_new_attribute():
    """`href="{{item_url}}"` with a raw quote in the value ends the attribute
    and everything after it is markup the reader's client will honour."""
    html = render(issue_with_source('https://arxiv.org/abs/1" onmouseover="alert(1)'))
    assert "onmouseover" not in html, (
        "a quote in a source URL escaped the href and injected an attribute")


def test_a_javascript_scheme_in_a_source_url_does_not_survive():
    html = render(issue_with_source("javascript:alert(document.cookie)"))
    assert "javascript:" not in html.lower(), (
        "a javascript: source URL reached the rendered anchor")


def test_a_data_scheme_in_a_source_url_does_not_survive():
    html = render(issue_with_source("data:text/html;base64,PHNjcmlwdD4="))
    assert "data:text/html" not in html.lower(), (
        "a data: source URL reached the rendered anchor")


def test_an_ordinary_source_url_is_untouched():
    """The fix must not cost the product its links."""
    html = render(issue_with_source("https://arxiv.org/abs/2509.01234"))
    assert 'href="https://arxiv.org/abs/2509.01234"' in html


def test_an_ampersand_in_a_source_url_is_escaped_not_dropped():
    """A query string is a legitimate URL and has to arrive intact and valid:
    escaped in the attribute, and still the same link when parsed."""
    html = render(issue_with_source("https://example.org/p?a=1&b=2"))
    assert "https://example.org/p?a=1&amp;b=2" in html
    assert "?a=1&b=2" not in html


# ---------------- 2. inline(), the links inside prose ----------------

def test_inline_refuses_a_javascript_link():
    out = er.inline("see [this](javascript:alert(1)) for details")
    assert "javascript:" not in out.lower()


def test_inline_keeps_an_http_link():
    out = er.inline("see [this](https://example.org/x) for details")
    assert 'href="https://example.org/x"' in out


def test_inline_keeps_a_mailto_link():
    out = er.inline("write to [us](mailto:hello@alexandr.ia)")
    assert 'href="mailto:hello@alexandr.ia"' in out


def test_inline_refuses_a_scheme_hidden_behind_whitespace_and_case():
    """`JaVaScRiPt:` and a leading tab are the two cheapest ways past a naive
    prefix check, so the check is not allowed to be a naive prefix check."""
    for raw in ("JaVaScRiPt:alert(1)", "\tjavascript:alert(1)", "java\tscript:alert(1)"):
        out = er.inline(f"[x]({raw})")
        assert "alert(1)" not in out or "href" not in out, f"{raw!r} survived"


# ---------------- 3. legacy_html, the fallback nobody watches ----------------

def test_the_fallback_email_escapes_raw_html():
    """`markdown` has never sanitized HTML, and this path runs it on a body a
    model wrote. The designed render having been fixed is not a defence: this
    function exists precisely for the run where the designed render failed."""
    html = weekly.legacy_html(
        "# Issue\n\nA line.\n\n<script>alert(1)</script>\n\n"
        '<img src=x onerror="alert(2)">\n')
    assert "<script>" not in html
    assert "onerror" not in html


def test_the_fallback_email_still_renders_markdown():
    html = weekly.legacy_html("# Issue\n\nA line with **bold** in it.\n")
    assert "<h1" in html
    assert "bold" in html


# ---------------- 4. the slot names are not a channel ----------------

def test_an_issue_cannot_name_a_slot_and_be_filled_with_it():
    """`fill` is sequential string replacement, so a title holding the literal
    text of a later slot gets that slot's value substituted into it. The later
    slots include the recipient's own email address."""
    body = (
        "# An issue about {{recipient_email}} templating\n\n"
        "The opening paragraph.\n\n"
        "## What shipped\n\n"
        "- **An item**\n"
        "  A sentence.\n"
    )
    html = render(body)
    head = html.split("What shipped")[0]
    assert RECIPIENT not in head, (
        "the title's literal slot name was replaced with the recipient address")


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"\n{failures} failing")
    sys.exit(1 if failures else 0)
