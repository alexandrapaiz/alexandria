"""The press sends the designed email, not markdown in a div.

The owner's ruling of 2026-09-24: "no ui applied to the emails... only the
html. i want the emails to have ui." The template at site/emails/digest.html
had existed since 2026-09-19 and the press had never opened it.

These tests hold the seam that failure lived in. Not the renderer's
typography, which the frontend seat verified at 3x by eye and which these
tests would only restate badly, but the three things that made the gap
invisible and would make it recur:

1. The press actually reaches the template, and the template actually
   reaches the image. A renderer nothing calls is what we already had.
2. Every slot gets filled and every region marker gets consumed, because a
   half-filled template is worse than no template: it mails "{{close}}" to
   a reader.
3. The two properties the send must never lose while gaining a UI, which
   are the plain-text part and the editorial-title subject.

Run with `python3 tests/test_email_template.py` or under pytest.
"""

import re
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

ISSUE = (ROOT / "site" / "content" / "issues" / "2026-W39.md").read_text()

# Read out of the issue rather than copied out of it. This fixture is a live
# editorial artifact that the writer seat rewrites whenever the owner rules on
# voice, and a literal copied from it here turns every legitimate rewrite into
# a red build in the engineer's tests. That is not hypothetical: the W39
# reprint under canon law 14 (2026-09-24) changed the title and added a fifth
# section, and three tests in this file failed on prose they had memorized.
# What these tests are for is the seam, so they assert that the parser and the
# send agree with the source, never that the source still says what it said.
# `er.plain` strips markdown so an emphasized headline still compares equal.
# The extraction itself stays independent of `parse_issue`, which is the thing
# under test here.
ISSUE_TITLE = er.plain(
    next(line[2:].strip() for line in ISSUE.splitlines() if line.startswith("# ")))
ISSUE_SECTIONS = sum(1 for line in ISSUE.splitlines() if line.startswith("## "))
RECIPIENT = "reader@example.com"
UNSUB = "mailto:hello@alexandr.ia?subject=Unsubscribe"


def render_one(key: str = "2026-W39") -> str:
    return er.render_issue(ISSUE, key, RECIPIENT, UNSUB)


# ---------------- 1. the wiring ----------------

def test_image_bundles_the_template_and_the_renderer():
    """The commonest way for this to regress is a render that works locally
    and finds no template in the container."""
    source = (ROOT / "pipeline" / "weekly.py").read_text()
    assert '"site/emails/digest.html", "/root/emails/digest.html"' in source
    assert '"pipeline/email_render.py", "/root/email_render.py"' in source
    assert str(er.BUNDLED) == "/root/emails/digest.html"


def test_send_newsletter_goes_through_the_template():
    """The regression this whole change exists to prevent: the press holding
    a designed template and mailing an inline div anyway."""
    source = (ROOT / "pipeline" / "weekly.py").read_text()
    body = source.split("def send_newsletter")[1].split("\ndef ")[0]
    assert "build_messages(" in body
    assert "Georgia,serif" not in body, (
        "send_newsletter is inlining styles again; the template owns the UI"
    )


def test_missing_template_is_a_legible_error():
    """Probing /root as a non-root user raises rather than answering False.
    That is how this first broke locally."""
    saved = (er.BUNDLED, er.IN_REPO)
    er.BUNDLED, er.IN_REPO = Path("/root/nope.html"), Path("/nonexistent/nope.html")
    try:
        er.template_text()
    except FileNotFoundError as exc:
        assert "add_local_file" in str(exc)
    else:
        raise AssertionError("a missing template must raise FileNotFoundError")
    finally:
        er.BUNDLED, er.IN_REPO = saved


# ---------------- 2. the fill is complete ----------------

def test_every_slot_is_filled_and_no_region_survives():
    html = render_one()
    assert not re.findall(r"{{(\w+)}}", html), "a slot reached the reader unfilled"
    assert not re.findall(r"<!-- (?:BEGIN|END):(\w+) -->", html)


def test_the_issue_is_actually_in_there():
    html = render_one()
    issue = er.parse_issue(ISSUE)
    assert issue["title"] in html
    assert len(issue["sections"]) == ISSUE_SECTIONS, \
        "the parser found a different number of sections than the markdown declares"
    for section in issue["sections"]:
        assert section["items"], f"section {section['title']!r} rendered empty"
        assert section["title"] in html


def test_links_and_recipient_come_from_the_issue_and_the_row():
    html = render_one()
    assert 'href="https://libraryofalexandria.dev/library/2026-W39"' in html
    assert 'href="https://libraryofalexandria.dev/library"' in html
    assert RECIPIENT in html
    assert UNSUB in html


def test_preheader_is_a_plain_sentence_and_never_the_title():
    issue = er.parse_issue(ISSUE)
    pre = er.preheader_for(issue)
    assert pre and pre != issue["title"]
    assert "<" not in pre and "[" not in pre and "*" not in pre
    assert len(pre) <= 160


def test_optional_regions_are_deleted_not_filled_blank():
    """An issue with no stats line must not ship an empty stats block."""
    minimal = "# A title\n\nAn opening sentence.\n\n## One section\n\n- An item.\n"
    html = er.render(er.parse_issue(minimal),
                     er.build_meta("2026-W39", er.parse_issue(minimal), RECIPIENT, UNSUB))
    assert "{{stats}}" not in html and "{{masthead}}" not in html
    assert not re.findall(r"<!-- (?:BEGIN|END):(\w+) -->", html)


def test_body_text_is_escaped():
    """The issue body is model output and it lands in an HTML document."""
    nasty = "# T\n\nAn opening.\n\n## S\n\n- <script>alert(1)</script> and 5 < 6.\n"
    html = er.render(er.parse_issue(nasty),
                     er.build_meta("2026-W39", er.parse_issue(nasty), RECIPIENT, UNSUB))
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


# ---------------- 3. the edition label ----------------

def test_edition_short_completes_the_footer_sentence():
    """The slot gotcha: it reads "the weekly issue", never a date. The
    sentence is "You are receiving ___ of alexandria at you@example.com"."""
    assert er.edition_for("2026-W39")[1] == "the weekly issue"
    assert er.edition_for("2026-09-19")[1] == "the daily issue"
    html = render_one()
    assert (f"You are receiving the weekly issue of alexandria at "
            f"{RECIPIENT}.") in html


def test_edition_reads_the_cadence_off_the_key():
    """This is what makes the daily press path free when #35/#60 land: the
    key already says which cadence it is."""
    assert er.edition_for("2026-W39")[0] == "Weekly synthesis · September 21–27, 2026"
    assert er.edition_for("2026-09-19")[0] == "Daily dispatch · September 19, 2026"
    # a week that straddles a month boundary
    assert er.edition_for("2026-W40")[0] == ("Weekly synthesis · "
                                             "September 28 – October 4, 2026")


def test_a_daily_key_renders_the_whole_email():
    html = er.render_issue(ISSUE, "2026-09-19", RECIPIENT, UNSUB)
    assert "Daily dispatch · September 19, 2026" in html
    assert 'href="https://libraryofalexandria.dev/library/2026-09-19"' in html
    assert not re.findall(r"{{(\w+)}}", html)


def test_an_unknown_key_still_renders():
    """A label we cannot compute is cosmetic. Refusing to send over it is not."""
    html = er.render_issue(ISSUE, "scratch", RECIPIENT, UNSUB)
    assert not re.findall(r"{{(\w+)}}", html)
    assert "this issue" in html


# ---------------- 4. what the send must not lose ----------------

def test_the_plain_text_part_survives():
    msgs = weekly.build_messages("2026-W39", ISSUE, [(RECIPIENT, None)], "me@x.com")
    _email, _subject, text, html = msgs[0]
    assert text == ISSUE, "the text part must stay the markdown body"
    assert text != html


def test_the_subject_is_the_editorial_title():
    msgs = weekly.build_messages("2026-W39", ISSUE, [(RECIPIENT, None)], "me@x.com")
    assert msgs[0][1] == ISSUE_TITLE, "the subject must be the issue's own headline"
    assert "2026-W39" not in msgs[0][1], "the W code is an internal id"
    assert weekly.email_render().subject_for("no heading here").startswith("This week")


def test_every_recipient_gets_their_own_footer():
    rows = [("a@example.com", "A"), ("b@example.com", "B")]
    msgs = weekly.build_messages("2026-W39", ISSUE, rows, "me@x.com")
    assert len(msgs) == 2
    assert "a@example.com" in msgs[0][3] and "b@example.com" not in msgs[0][3]
    assert "b@example.com" in msgs[1][3]


def test_a_render_failure_still_delivers_the_issue():
    mod = weekly.email_render()
    saved = mod.template_text
    mod.template_text = lambda: (_ for _ in ()).throw(RuntimeError("template moved"))
    try:
        msgs = weekly.build_messages("2026-W39", ISSUE,
                                     [("a@x.com", None), ("b@x.com", None)], "me@x.com")
    finally:
        mod.template_text = saved
    assert len(msgs) == 2
    assert all(m[3] for m in msgs), "a failed render must still produce an email"
    assert msgs[0][1] == ISSUE_TITLE, "the subject survives a template failure"
    assert msgs[0][2] == ISSUE


# ---------------- 4. the links, which are the slot nothing escaped ----------
#
# The 2026-09-22 ledger entry filed `urgent` by the engineer seat asked for two
# things in the emailed issue: escape raw HTML, and "refuse any href whose
# scheme is not http, https or mailto". The 2026-09-24 template rewrite above
# did the first and only the first. Every slot in `render` went through
# `html.escape` except one, `item_url`, which lands in `<a href="{{item_url}}">`
# in site/emails/digest.html; and `inline` escaped a link's text before it built
# the anchor without ever looking at the scheme.
#
# So the body was safe and the links were not. A source URL is copied out of
# arXiv text by a model, which makes it the shortest path there is from a
# crafted paper to a live attribute in a subscriber's inbox.
#
# Three sinks reach a reader and all three are held here: `item_url`, `inline`,
# and `legacy_html`, the fallback that runs the markdown library over the same
# body and only ships when the designed render failed, which is exactly the
# moment nobody is reading the output.

def issue_with_source(url: str, label: str = "arXiv") -> str:
    """The smallest issue carrying one item with one source link."""
    return (
        "# A week of small print\n\n"
        "The opening paragraph, which the template needs.\n\n"
        "## What shipped\n\n"
        "- **An item with a source**\n"
        f"  *A paper title* \u2014 [{label}]({url}) and a sentence after it.\n"
        "  Evidence: 14 of 14 cases.\n"
    )


def render_body(body: str) -> str:
    return er.render_issue(body, "2026-W40", RECIPIENT, UNSUB)


def test_a_quote_in_a_source_url_cannot_open_a_new_attribute():
    """`href="{{item_url}}"` with a raw quote in the value ends the attribute,
    and everything after it is markup the reader's client will honour."""
    html = render_body(issue_with_source('https://arxiv.org/abs/1" onmouseover="alert(1)'))
    # The escaped form, `onmouseover=&quot;`, is inert text inside the href and
    # is allowed to be there. What must not exist is the unescaped form, which
    # is the same string having become an attribute of its own.
    assert 'onmouseover="' not in html, "a quote in a source URL injected an attribute"


def test_a_javascript_source_url_does_not_survive():
    html = render_body(issue_with_source("javascript:alert(document.cookie)"))
    assert "javascript:" not in html.lower()


def test_a_data_source_url_does_not_survive():
    """`data:` is refused for the same reason site/lib/markdown-core.js refuses
    it: a data URL is a document the client will run, and no issue needs one."""
    html = render_body(issue_with_source("data:text/html;base64,PHNjcmlwdD4="))
    assert "data:text/html" not in html.lower()


def test_a_refused_source_url_keeps_the_citation():
    """Refusing a link must not delete the attribution. A reader who cannot
    click the source should still be told what the source was."""
    html = render_body(issue_with_source("javascript:alert(1)"))
    assert "A paper title" in html


def test_an_ordinary_source_url_is_untouched():
    """The fix is not allowed to cost the product its links."""
    html = render_body(issue_with_source("https://arxiv.org/abs/2509.01234"))
    assert 'href="https://arxiv.org/abs/2509.01234"' in html


def test_an_ampersand_in_a_source_url_is_escaped_and_still_the_same_link():
    """A query string is a legitimate URL. It has to arrive escaped in the
    attribute and still resolve to the link the issue cited."""
    html = render_body(issue_with_source("https://example.org/p?a=1&b=2"))
    assert "https://example.org/p?a=1&amp;b=2" in html
    assert "?a=1&b=2" not in html


def test_inline_refuses_a_javascript_link_and_keeps_the_words():
    out = er.inline("see [this](javascript:alert(1)) for details")
    assert "javascript" not in out.lower()
    assert "this" in out, "a refused link loses its href, not its sentence"


def test_inline_keeps_http_and_mailto():
    assert 'href="https://example.org/x"' in er.inline("[a](https://example.org/x)")
    assert 'href="mailto:hello@alexandr.ia"' in er.inline("[a](mailto:hello@alexandr.ia)")


def test_inline_refuses_a_scheme_a_client_would_collapse():
    """A mail client drops tabs, newlines and no-break spaces before it
    resolves a URL, so `java<tab>script:` navigates. The check reads the
    collapsed form for that reason, and case is not a defence either."""
    for raw in ("JaVaScRiPt:alert(1", "\tjavascript:alert(1", "java\tscript:alert(1",
                "\u00a0javascript:alert(1", "java\nscript:alert(1"):
        out = er.inline(f"[x]({raw})")
        assert "href" not in out, f"{raw!r} produced an anchor"


def test_the_fallback_email_escapes_raw_html():
    """`markdown` has not escaped raw HTML since v8, and this path runs it over
    a body a model wrote. The designed render having been fixed is no defence:
    this function exists for the send where the designed render failed."""
    html = weekly.legacy_html(
        "# Issue\n\nA line.\n\n<script>alert(1)</script>\n\n"
        '<img src=x onerror="alert(2)">\n')
    # Escaped, these are words on a page. Unescaped, they are a tag and an
    # event handler, so the test is which of the two the reader receives.
    assert "&lt;script&gt;" in html and "<script" not in html
    assert "&lt;img" in html and "<img" not in html


def test_the_fallback_email_refuses_a_javascript_href():
    html = weekly.legacy_html("# Issue\n\n[c](javascript:alert(1)) and text.\n")
    assert "javascript" not in html.lower()


def test_the_fallback_email_still_renders_markdown():
    """Escaping is done with `<` and a bare `&` rather than `html.escape`, on
    purpose: `>` at the start of a line is markdown's blockquote, and escaping
    it would cost the fallback email every quotation an issue carries."""
    html = weekly.legacy_html(
        "# Issue\n\nA & B with **bold**.\n\n> quoted\n\n"
        "[d](https://x.org/a?p=1&q=2)\n")
    assert "<h1" in html and "<strong>bold</strong>" in html
    assert "<blockquote>" in html
    assert "A &amp; B" in html
    assert 'href="https://x.org/a?p=1&amp;q=2"' in html


def test_the_fallback_path_is_really_exercised_by_the_build():
    """Without `markdown` installed, `legacy_html` takes its own import-error
    branch and the three tests above pass against a `<pre>` block instead of
    against the production render. That is a green build measuring nothing, so
    the dependency is pinned in the file CI installs and asserted here."""
    reqs = (ROOT / "requirements-dev.txt").read_text()
    assert "markdown==3.7" in reqs, "requirements-dev.txt must pin the email's markdown"
    import markdown  # noqa: F401  the import is the assertion
    assert "<pre" not in weekly.legacy_html("# Issue\n\nA line.\n")


def test_the_email_and_the_site_allow_the_same_schemes():
    """One body renders on two surfaces. The site's `safeHref` is the reference
    implementation and the email is the half that lagged it by ten days, so a
    scheme added to one and not the other is the divergence worth a red build.
    The schemes are shared; the absolute-URL requirement is the email's alone
    and is documented in `url_allowed`."""
    source = (ROOT / "site" / "lib" / "markdown-core.js").read_text()
    listed = re.search(r"SAFE_SCHEMES\s*=\s*\[([^\]]*)\]", source)
    assert listed, "site/lib/markdown-core.js no longer declares SAFE_SCHEMES"
    site_schemes = sorted(re.findall(r'"([a-z]+)"', listed.group(1)))
    email_schemes = sorted(s.rstrip(":/") for s in er.SAFE_SCHEMES)
    assert site_schemes == email_schemes, (
        f"site allows {site_schemes}, the email allows {email_schemes}")


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  ok  {name}")
            except Exception as exc:
                failed += 1
                print(f"FAIL  {name}: {type(exc).__name__}: {exc}")
    print("\n" + ("all green" if not failed else f"{failed} failing"))
    sys.exit(1 if failed else 0)


def test_a_repeated_title_carries_its_dates_in_the_subject():
    """2026-09-28: the Monday issue went out under the same subject as the two
    sends before it and read as a repeat. The subject of a repeated title now
    ends with the week's dates; a fresh title is left alone."""
    same = er.disambiguate_subject("Harness distillation without the harness at runtime",
                                       "Harness distillation without the harness at runtime", "2026-W39")
    assert same.startswith("Harness distillation without the harness at runtime ("), same
    assert "2026" in same, same
    fresh = er.disambiguate_subject("A new title", "An old title", "2026-W39")
    assert fresh == "A new title", fresh
    none = er.disambiguate_subject("A new title", "", "2026-W39")
    assert none == "A new title", none
