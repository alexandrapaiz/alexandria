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
    assert 'href="https://alexandr.ia/library/2026-W39"' in html
    assert 'href="https://alexandr.ia/library"' in html
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
    assert 'href="https://alexandr.ia/library/2026-09-19"' in html
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
