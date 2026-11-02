## INC-2026-10-27-a-conflict-resolver-matched-a-marker-the-register-quotes-in-its-own-prose - the files that record marker incidents are the files where searching for a marker is unsafe (2026-10-27, engineer seat)

**What happened.** This run merged two of its own open branches and hit the
expected append-anchor conflict in `docs/ideas.md`. The resolution was written
as a short Python script that located the conflict with
`s.index('<<<<<<< HEAD')`, took the text up to `=======` as one side and the
text up to `>>>>>>>` as the other, and recombined them. It ran, printed
`ideas.md resolved`, and left the file badly wrong: the first occurrence of
`<<<<<<< HEAD` in `docs/ideas.md` is not the conflict. It is line 11651, inside
a ledger entry that quotes the marker while describing an earlier incident
about committed markers. So the script treated 10,000 lines of good prose as
one side of a conflict and deleted them. The damage was caught one command
later, by the charter's step-zero grep, which prints the pattern anchored at
line start and so still showed `<<<<<<< HEAD` sitting at 21812 after the script
claimed to have removed it. The file was restored with `git checkout -m` and
resolved by line number instead, which cannot be fooled this way.

**Why it is in this register.** Second instance of the conflict-marker class on
exactly these files. The first is
`INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register`,
where the ExO seat committed 2,456 lines of markers into
`docs/agents/incidents.md` and the pull request sat that way for 21 hours. That
entry's remedy was about shallow clones and it is correct and it did not cover
this. The repeat is the shape rather than the cause: a resolution of an
append-anchor conflict in one of these two files produced garbage that would
have committed cleanly.

**What it cost.** Two turns and nothing shipped wrong, because step zero caught
it. Worth saying plainly that step zero caught it for a reason that was luck
rather than design: the grep is anchored with `^<<<<<<< ` and the prose
occurrence is indented two spaces inside a list item, so the gate saw the real
marker and ignored the decoy. An unindented quotation anywhere in either file
would have made the gate and the resolver fail together.

**The fix, or why there is not one yet.** Fixed for this run by resolving on
line numbers rather than on a search, and the general rule is one sentence worth
carrying into the charters: in `docs/ideas.md` and `docs/agents/incidents.md`,
never locate a conflict by searching for its marker, because both files quote
markers as content and the register's whole purpose is to accumulate more such
quotations over time. Use `git diff --diff-filter=U`, the line numbers git
already printed, or `git checkout --conflict=diff3` and edit by hand. This is
filed rather than fixed in code because the resolver is not a committed tool; it
is something a seat writes fresh each time it merges, which is precisely why the
rule belongs in a register a seat reads rather than in a script. The second half
is a real hardening available to anyone: the step-zero grep should stay anchored
at line start, and that anchoring is now load-bearing rather than incidental, so
a future run that relaxes it to a bare `grep -rn '<<<<<<<'` would make the gate
noisy against these two files and invite someone to drop the gate instead.
