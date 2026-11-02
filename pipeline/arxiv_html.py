"""Canon law 8's url, decided by code instead of by a model's judgment.

Law 8 says a link goes to the paper's full text, so an arXiv link should be
`arxiv.org/html/<id>`, and `arxiv.org/abs/<id>` only when the paper has no
HTML version. That rule has one question in it that reading the artifact
cannot answer: does the HTML exist? An `abs` link is either a violation of
the law or the law's own fallback working correctly, and the link itself
never says which.

Until this module the question was asked of the generator. `prompts/digest.md`
told a model to rewrite the url it had been handed, and that instruction has
been reworded six times with one revert
(`61384e61`, `77ca3624`, `c04eaec8`, `fe6dc1ee`, `72c89585`, `6723c304`,
`c5a32e4c` reverted by `0251df0b`). The writer seat graded 2026-W42 live and
measured the result: ten arXiv links, nine `abs`, and arXiv serves HTML for
seven of those nine. The rule was not ignored. It was applied by judgment,
and judgment went seven for nine.

So the decision moves to the one place that can be sure of it. The answer is
a HEAD request, and `docs/voice/check_voice.py` has had exactly this function
since it started grading law 8 live. It ran after publication, in the gate
that scores the issue, rather than in the step that writes it.

Two properties this has that a prompt cannot have.

The identifier is never composed. It is read out of the url the pipeline
already holds, suffix and all, so a payload cannot disagree with itself about
whether a paper is `2610.22344` or `2610.22344v1`. That disagreement is ban
list 100, and 2026-W42 carried six bare identifiers against four versioned
ones, which is the tell that at least one was typed rather than copied.

And an unreachable arXiv is not the fallback. `html_full_text` answers None
when it could not ask, which is a third outcome, and this module keeps the
`abs` url while recording that nobody knows. A caller that folds None into
False publishes the fallback as though it had been earned.

No network in the tests: every entry point takes its probe as an argument.
"""

import re
import urllib.error
import urllib.request

#: The same shape `docs/voice/check_voice.py` greps for, so the gate that
#: grades the link and the step that writes it agree on what an arXiv link is.
ARXIV_LINK = re.compile(
    r"(?P<scheme>https?)://arxiv\.org/(?P<path>abs|html|pdf)/"
    r"(?P<ident>\d{4}\.\d{4,5}(?:v\d+)?)/?$"
)

HTML_URL = "https://arxiv.org/html/{ident}"

#: Why one url came out the way it did. These strings are read by humans in
#: the press log and asserted on in the tests, so they are part of the
#: contract rather than decoration.
REWROTE = "rewrote abs to html, arxiv serves the full text"
ALREADY = "already the full text, left alone"
NO_HTML = "no html version, which is law 8's own fallback"
UNREACHED = "could not ask arxiv, so abs stands and was not graded clean"
NOT_ARXIV = "not an arxiv link"

#: Per-identifier, per-process. One weekly payload names the same paper in
#: `new_claims` and in `deep_reads` routinely, and the second mention must not
#: cost a second request.
_HTML_EXISTS: dict[str, bool | None] = {}


def html_full_text(ident, opener=None):
    """Does `arxiv.org/html/<ident>` exist?

    True, False on a 404, and None when the question could not be reached.
    The three-way return is the whole point: see the module docstring on why
    None must not collapse into False.

    A bogus identifier answers 404 on both paths, which is what makes a 404
    on `html` the fallback case rather than evidence of a broken link.
    """
    if ident in _HTML_EXISTS:
        return _HTML_EXISTS[ident]
    open_url = opener or _head
    try:
        out = open_url(HTML_URL.format(ident=ident))
    except urllib.error.HTTPError as exc:
        out = False if exc.code == 404 else None
    except (urllib.error.URLError, OSError, ValueError):
        out = None
    _HTML_EXISTS[ident] = out
    return out


def _head(url):
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return 200 <= resp.status < 300


def law8_url(url, probe=html_full_text):
    """One url in, the law 8 url and the reason out.

    Returns the url unchanged for anything that is not an `abs` link this
    module can resolve, so a blog post, a `pdf` link and an unparseable
    string all pass through untouched with a reason that says so.
    """
    if not isinstance(url, str):
        return url, NOT_ARXIV
    match = ARXIV_LINK.match(url.strip())
    if not match:
        return url, NOT_ARXIV
    if match["path"] != "abs":
        return url, ALREADY
    exists = probe(match["ident"])
    if exists is None:
        return url, UNREACHED
    if not exists:
        return url, NO_HTML
    # The identifier is the one the url carried, suffix included. Nothing here
    # chooses a version, which is what keeps ban list 100 unreachable.
    return HTML_URL.format(ident=match["ident"]), REWROTE


#: Every payload key that holds a link. `superseded` names two papers in one
#: row, so the key is not always `url`, and a hand list of one is how the old
#: paper's link would have been missed.
URL_KEYS = ("url", "old_url", "new_url")


def resolve_payload(payload, probe=html_full_text):
    """Rewrite every arXiv link in a digest payload, and say what happened.

    Walks the payload rather than naming its sections, because `gather` grew
    `deep_reads` and `traction` after law 8 was written and a section added
    tomorrow should be covered the day it appears rather than the day somebody
    remembers this file. For each row it finds with a url key, it replaces the
    url and writes a sibling `<key>_law8` holding the reason.

    Returns a count per reason, for the press log. The counts are the evidence
    that the step ran at all, which an issue that happens to carry no `abs`
    links cannot otherwise show.
    """
    counts = {}

    def visit(node):
        if isinstance(node, dict):
            for key in URL_KEYS:
                if key in node:
                    resolved, reason = law8_url(node[key], probe=probe)
                    node[key] = resolved
                    node[f"{key}_law8"] = reason
                    counts[reason] = counts.get(reason, 0) + 1
            for value in node.values():
                visit(value)
        elif isinstance(node, (list, tuple)):
            for value in node:
                visit(value)

    visit(payload)
    return counts


def summarise(counts):
    """One log line, ordered so the two that need a reader come first."""
    order = (REWROTE, UNREACHED, NO_HTML, ALREADY, NOT_ARXIV)
    parts = [f"{counts[r]} {r}" for r in order if counts.get(r)]
    return "law 8 urls: " + ("; ".join(parts) if parts else "no links in payload")
