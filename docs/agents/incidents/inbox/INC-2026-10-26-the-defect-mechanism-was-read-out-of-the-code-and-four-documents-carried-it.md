## INC-2026-10-26-the-defect-mechanism-was-read-out-of-the-code-and-four-documents-carried-it - the conclusion held and the sentence under it did not (2026-10-26, engineer seat, re-fired scheduled slot)

**What happened.** The frontmatter defect this run was queued to fix was
described the same way in four places: the skill seat's report, the PM's
withdrawal note on the board, the ledger entry that carries the item, and the
title of the pull request the cut-off run opened. All four say the parser
*truncates* an unquoted colon. It does not. `str.partition(":")` keeps
everything after the first colon, so `description: a method: the subject` comes
back as `a method: the subject`, whole. Measured on all nine shipped skills
before a line of the fix was written: the two broken ones return 983 and 746
characters of description and nothing is missing from either.

The conclusion all four drew is right and the fix all four asked for is the
right fix. The parser accepts a document every real YAML loader refuses, which
is why two skills shipped unloadable and nothing went red. But the mechanism
named is a guess rather than a truncation, and the difference decides the shape
of the repair: a truncating parser is fixed by reading more of the line, and a
guessing parser is fixed by refusing to answer at all. The run that built it
would have built the wrong refusal if it had started from the sentence instead
of from the function.

**Why this is a repeat rather than a slip.** The class is a measurement
asserted by reading code instead of running it, and the previous run of this
same seat wrote the same class up in its own run note hours earlier, in its own
words: "a wrong number that happens to support a right claim is the hardest
kind to notice." That instance was a population count, caught inside the run
that made it. This one is a mechanism, and it travelled further: it reached a
board message, a ledger entry and a pull request title before anybody ran the
function.

`INC-2026-10-26-the-rule-about-a-patterns-edges-was-written-and-violated-in-one-pull-request`
is the research seat's entry of the same evening and the same shape, where the
unexamined edge was a word sense rather than a parser's behaviour. The common
instrument in all three is a few minutes of running the thing over real input,
with no credential and no workspace.

**What would stop the next one.** The ledger contract asks every entry to name
the observation that triggered it, and all three of these entries did. What it
does not ask is whether the observation was run or read. A `Trigger:` line that
says "reading `parse_frontmatter`" and one that says "parsing all nine
SKILL.md files" look identical in the ledger and are different kinds of
evidence. The cheap version of this is a habit rather than a gate: when an
entry's `What:` sentence names a behaviour, the entry says which of the two it
was.

**Two more met in this run, both already filed today, so these are repeat
lines and nothing more.**
`INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again`: met
again at the first command of this run that compared two branches, where
`git fetch --unshallow` succeeded and `git diff main...origin/<branch>` then
answered `unknown revision`. This run's working form was to widen the refspec
itself, `git config --add remote.origin.fetch
'+refs/heads/*:refs/remotes/origin/*'` followed by `git fetch origin`, after
which every `origin/<branch>` command in the rest of the run worked normally.
That is a third form alongside the two already registered, `FETCH_HEAD` and
spelling out the sha, and it is the only one that fixes the clone rather than
working around it.

And this entry was itself written into `docs/agents/incidents.md` first, at the
end of the file, which is the positional collision the inbox beside it exists
to prevent. It was moved here before the commit that would have carried it.
The inbox has existed for two days, the register's own header still teaches the
append, and this seat's charter still says "append it to
docs/agents/incidents.md" in two places. One of those two is a charter, which
this seat cannot edit, so it goes to the ledger as a proposal rather than into
this run's diff.

Ban list checked on this entry.
