## INC-2026-11-09-a-path-filtered-feed-was-added-to-catch-normative-spec-changes-and-watched-the-schema-for-forty-days - the comment above the row asserted the purpose the row defeated, and nothing we run could report it (2026-11-09, security seat, message wake)

**What happened.** A handoff asked this seat about an A2A specification clause
that merged 2026-07-30 and is still untagged. While answering it, this run
found that the feed `sources.yaml` added for exactly this purpose could not
have delivered the clause.

| | configured | corrected |
|---|---|---|
| row | `gh-a2a-spec-changelog` | `gh-a2a-spec-prose` |
| path | `specification/` | `docs/specification.md` |
| newest entry on 2026-11-09 | **2026-07-21** | 2026-10-12 |
| carries A2A PR 2081 | **no** | **yes** |

A2A pull request 2081 merged 2026-07-30T20:24:35Z and changed exactly one
file, `docs/specification.md`. The configured feed watches the
`specification/` directory, which holds A2A's machine-readable schema. Its
newest commit is nine days older than the clause and it has not moved in 111
days.

The comment above the row, written the same day the row was, says the reason
the row exists is that releases feeds "return the tag while the normative
change lives in the spec tree." That sentence is correct and the row below it
watched the wrong tree. The sibling row added in the same commit,
`ce640aa2` of 2026-09-30, points `gh-mcp-spec-changelog` at
`docs/specification` and has the path right.

**Why this is a repeat and of what.** Two classes, and the second is the one
worth the entry.

The first is the charter's own named specimen class, a comment that lies about
the code, whose first instance is `pipeline/weekly.py`'s docstring naming a
mail provider the org rejected. This is the second confirmed instance and it
had been lying for 40 days.

The second is the class this register already holds several instances of under
other names: **a gate or an instrument that reports on itself rather than on
its subject.** `tools/feed_health.py` asks whether a feed answers. This feed
answers, with twenty real entries, HTTP 200, a path filter that genuinely
narrows. Every check we own reads it as healthy. Nothing we run asks the only
question that would have caught this, which is whether what a source delivers
has anything to do with why it was added. The nearest siblings already filed
are the coverage ratchet that is invisible on the pull request that breaks it,
and the branch-name gate that answers "free" when its call fails. The shape is
the same: an instrument whose green is about its own execution.

**How it was found, and the part that is not luck.** It was not found by
looking at feeds. It was found because a handoff asserted that a specific
normative sentence existed upstream, and checking that assertion against our
own ingestion is a different operation from checking that our ingestion runs.
The earlier run of this same seat, pull request #860, had already pointed at
this feed as the mitigation for the handoff's class, correctly in design and
without checking that the row implemented it. Two runs of one seat looked at
the same row 90 minutes apart and the second one measured it.

**What this run did.** Added `gh-a2a-spec-prose` with the correct path, kept
the existing row because a schema change is still worth watching, and
rewrote the comment to carry the measurement instead of the belief. The
corrected feed holds the clause commit in its current window, so the clause is
recoverable on the next ingest rather than lost. Full reasoning in
`docs/security/audit-2026-11-09-a2a-untagged.md`.

**What remains, and it is the general repair rather than this row.** A check
that compares what a path-filtered source delivers against the stated reason it
was added. Filed for the engineer at
`docs/ideas/inbox/2026-11-09-no-check-asks-whether-a-feed-answers-about-the-thing-it-was-added-for.md`.
Fixing one row leaves the other 60-odd source rows unexamined, and the only
reason this one was examined is that somebody upstream happened to write a
sentence a seat here was asked to go and verify.
