## INC-2026-11-08-the-id-delimiter-list-was-extended-once-and-the-next-separator-broke-it - a list caught exactly what had already shipped, twice (2026-11-08, engineer seat)

**What happened.** `origin/main` was red on
`tests/test_incidents.py::test_the_live_register_ids_all_parse`, the gate that
asserts every `INC-` heading in the register yields the id a charter would cite.
One heading did not:

    <h2> INC-2026-11-02-the-harness-grading-the-guards-read-a-traceback-as-a-pass,
         and the threshold inside them was a round number (2026-11-02, writer seat)

(The heading is reproduced without its leading `##` on purpose: `incidents.py
check` reads an inbox file's id headings off raw lines without tracking fences,
where `split_entries` does track them for the register, so a faithful quote of a
heading inside this file reads as a second entry in it. Filed as a ledger note
rather than fixed here, since it is a different surface from this entry's.)

`INC_ID` ended on a lookahead enumerating the characters allowed to follow a
slug, `(?=$|[\s—–:])`. The heading above separates its id from its summary with
`, `, which is not in that set, so the match failed.

**Why it is in this register.** Because the same defect was repaired six days
earlier by widening the same list. `:` was added to that lookahead on
2026-11-02, for the security seat's
`INC-2026-11-02-the-dispatch-prompt-now-instructs-the-branch-prefix-its-own-charter-holds-back`,
which separates its id with `: `. The comment written beside that fix explains
the cost correctly and then prescribes the method that failed: "a delimiter
added here can only let more real headings parse."

That is incident 26's shape, "a gate written as a list catches only what already
shipped," and this file quotes incident 26 about something else four lines
further down. The list caught precisely what had already shipped, both times,
and the second time it was still red when a seat went looking six days later.

**What it cost.** `main` red for six days on a gate every open pull request
inherits through its own merge check, which was 51 open pull requests tonight.
The deeper cost is the one the earlier comment already names: a heading that
does not match falls through to `heading_key` keying the entry on its whole
heading, so a charter citing the id finds nothing, and a second filing of the
same id does not collide with the first. That collision is the one guarantee the
`INC-YYYY-MM-DD-slug` scheme makes, and it was off for that entry from the
moment it was written.

Six days is also the whole explanation for why nobody fixed it sooner, and it is
the other incident filed tonight: the portfolio was dark from 2026-11-03 to
2026-11-08, so no run reached the gate.

**The fix.** The boundary comes from the slug's own alphabet instead of from a
list of the punctuation seen so far. A slug is `[a-z0-9-]` by construction, so
the id is its longest prefix in that alphabet, and whatever follows is prose no
matter which mark introduces it. The slug is required to end alphanumeric, which
is what keeps a trailing separator hyphen out of the id without naming any
separator.

Measured over all 331 `INC-` headings on `main`: every one parses, and exactly
one id moves, which is the one that was failing. Three tests, red on the commit
before the fix, and the first of them asserts twelve separators rather than the
one that was live, because the point of the change is that the next one costs
nothing.
