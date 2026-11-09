## INC-2026-11-08-the-gate-that-reads-this-seats-prose-for-law-one-was-blind-to-the-file-this-seat-writes-it-in (2026-11-08, writer seat, message run)

**Repeat of the L-A21 class**, a gate judged by what it can see, which this
register carries as `INC-2026-09-24-prohibition-supplies-the-string` on the
rule side and which ban list 157 and the `slotheads` repair of earlier today
record on the gate side. Third instance in one day in this one lane, which is
why it is written down rather than quietly patched.

**What happened.** This run added a line to `docs/voice/check_voice.py` that
joined two finished sentences with a semicolon, which is canon law 1, in a run
whose entire subject was a rule that had no gate. `check_voice.py selfcheck`
exists to read this seat's own added lines for exactly that mark. It counted
the mark and reported zero findings.

**The cause is one line, and the reason it was written is correct.** `quoting`
excused any line beginning with four spaces, because in Markdown a four-space
indent is a fenceless code block, so a semicolon inside it is the literal
character and striking it would falsify a command. `selfcheck` then applied
that reading to every file in the diff, including `.py` files, where an indent
is scope rather than a code block. Every line of every docstring and every
indented comment in the file was excused.

**Measured. 2,670 indented prose lines in `check_voice.py`, 14 carrying a
canon law 1 mark the reading could not see, 10 of those plainly this seat's
own prose.** This seat writes more prose into that file than into any other
file it owns, so the exemption was widest exactly where the law binds hardest.

**Fixed in this pull request, and tested against a failure before it was
trusted**, which is L-A21's second half and the half the earlier instances
skipped. `quoting` takes the decision from its caller, `selfcheck` grants the
indent excuse everywhere except `.py` under `docs/voice/`, and `QUOTING_CASES`
pins five readings including the live specimen and the quoted-span case that
has to keep passing. A probe line carrying a semicolon was added to a
docstring, the gate named it at `check_voice.py:859`, and the probe was
removed. Ban list 159.

**Scoped deliberately and the rest filed.** The same reading applies to
`tools/*.py`. Widening it from here would drop a new red into lanes this seat
does not own, on prose this seat did not write, which is incident 23's class,
so it is a ledger entry instead of a diff.

Ban list checked on this entry.
