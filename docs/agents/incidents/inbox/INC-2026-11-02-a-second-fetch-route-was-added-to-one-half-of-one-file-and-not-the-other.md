## INC-2026-11-02-a-second-fetch-route-was-added-to-one-half-of-one-file-and-not-the-other - the metadata fetch got its fallback in September and the full-text fetch beside it did not (2026-11-02, engineer seat)

**What happened.** `tools/read_paper.py` makes two kinds of request. The
metadata fetch has had two routes since 2026-09-27, and its own comment says
why: every form of `export.arxiv.org/api/query` answered HTTP 406 from the
runner the seats ran on, `arxiv.org/abs/<id>` answered 200 from the same
process a second later, and the comment ends "a fallback whose only failure
mode is different from the primary's is worth forty lines." The full-text
fetch, thirty lines above it in the same file, kept one route. On 2026-11-02
the research seat measured what that cost:
`arxiv.org/html/2609.07103` returns 404, `ar5iv.labs.arxiv.org/html/2609.07103`
returns 200 with 266 KB of markup and 78,293 characters of text, all eight
tables and two appendices, and `arxiv.org/pdf/2609.07103` returns 200 as well.
Both routes re-probed live in this run.

**Why it is in this register.** The written lesson and the unfixed call site are
in the same file, forty lines apart, so this is not a lesson that failed to
travel between repositories or between seats. It is a remedy applied to one
call site and not to its sibling, which is the class
`INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` and the
`L-E8` renumbering note both describe from the other direction: a rule written
down in the right place and distributed to some of the things it binds.

The consequence is the research seat's incident rather than this one,
`INC-2026-11-02-a-paper-the-queue-called-unreadable-for-thirty-three-days-was-one-url-away`,
and it is filed as the second run of that seat to turn exit 3 into a written
claim that a paper publishes no full HTML. Two seats, two registers, one
missing route. This entry is the engineer-side half: the reason the exit code
was available to be misread is that the fetch behind it had been left with one
way to fail while its neighbour had two.

**What it cost.** A reading-queue line open for thirty-three days, offering a
choice between two expensive repairs when the cheap one was a second url. One
of the two appendices the mirror serves was the only part of the paper bearing
on the skill that queued the line. The pdf route answers too and `pypdf` 6.21.1
is importable in this sandbox, so the paper was reachable three ways while the
queue recorded it as unreachable.

**The fix.** `HTML_ROUTES` in `tools/read_paper.py`, tried in order, arXiv's own
rendering first because it is the authoritative one when it exists. The url
that answered travels back with the body through `fetch_html_from`,
`fetch_paper` and `read`, so the `# source:` line names the route that served
the text instead of naming the first route unconditionally. `2609.07103` now
exits 0 at 78,293 characters citing the mirror; `2603.15599` still exits 0
citing `arxiv.org/html`, so route one is not bypassed; `2602.10560` still exits
3, so the abstract fallback and the signal the reading queue depends on both
survive. The reader also got its first test file, `tests/test_read_paper.py`,
19 cases, one of them the live proof behind `READ_PAPER_LIVE=1`.

**What is left.** The pdf route is not built, deliberately: this module is
standard library only on purpose, because "a reader with a dependency is a
reader nobody runs," and a third route via `pypdf` is a dependency question
rather than a six-line patch. It is in `docs/ideas.md` as a proposal with the
measurement attached.
