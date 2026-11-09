## INC-2026-11-09-a-voice-gate-fix-rewrote-497-lines-of-another-seats-register-and-the-conflict-is-what-found-it - a one-file character cleanup was run over a 7,000-line shared register, and nothing but a merge conflict would have said so (2026-11-09, security seat, message wake)

**Repeat of
`INC-2026-11-09-this-seats-own-hand-resolution-deleted-two-lines-of-another-entry-and-a-ratchet-caught-it-rather-than-a-reader`,
filed by this seat earlier the same evening.** Recorded at the moment it
repeated, per the standing rule. Same seat, same night, same register family,
and the same thing caught it: a mechanical check rather than a reader.

**What happened.** `tools/ban_list.py` failed this run's new documents on
non-ASCII characters, which is correct and is entry 13 of the ban list. The fix
was a small script that replaced the section sign, the em dash and the right
arrow across a list of files, and `docs/agents/hq-relay.md` was on that list
because this run had appended one ask to it.

The script did not distinguish the 76 lines this run wrote from the 7,000 it
did not. It rewrote **497 existing lines** of the ExO seat's relay register,
none of them this seat's prose and none of them in need of correction. The diff
against the merge base read 576 insertions and 500 deletions on a file this run
had intended to append to.

**Nothing in the run would have reported it.** The voice gate passed, because
the file was now ASCII. The incident and ledger gates passed, because neither
reads that file. The marker check passed, because there were no markers. Every
check this charter prescribes was green on a diff that silently rewrote another
seat's register.

What found it was `tools/resolve_register_conflict.py`, and it found it by
refusing: "ours changed something that is not the end of the file, so this is
not two appends." That refusal is the only sentence in the run that was about
the real problem, and the tool was reached only because `main` moved and the
pull request went conflicting. Had nothing merged in the intervening hour, the
rewrite would have shipped.

**The resolution.** `git checkout origin/main -- docs/agents/hq-relay.md`, then
the 76-line ask re-appended. Verified by the only check that was ever going to
catch this: the diff against `main` for that file now reads 76 insertions and
**zero deletions**. The same count was run over the three other shared
registers this branch touches, and `docs/agents/incidents.md` and
`docs/ideas.md` are both zero. `docs/security/upstreams.md` shows six, and
those are a predecessor run's deliberate correction of a stale elapsed count,
with the reason written in the diff.

**Why the earlier instance did not prevent this one.** The earlier entry is
about a hand resolution and its remedy is an arithmetic proof over a merge. This
is not a merge. It is an edit, on one branch, by a script with a file list, and
no rule in this charter covers the shape "a fix applied to a file you only meant
to append to". The remedy that transfers is not about conflicts at all.

**The remedy, as a check rather than a resolution.** Before shipping, ask of
every shared register on the branch whether the diff against `main` removes any
line, and require a stated reason for each one that does:

```bash
for f in $(git diff --name-only origin/main...HEAD -- docs/); do
  n=$(git diff origin/main -- "$f" | grep -c '^-[^-]')
  [ "$n" -gt 0 ] && echo "$f: $n removed lines"
done
```

An append-only register is defined by that number being zero, and no gate in
this repository asks the question today. `tools/check_registers.py` is the
natural home and this is one function, so it is in the ledger inbox for the
engineer rather than built here.

**The general shape.** A character-level fix has no natural scope, so its scope
becomes whatever file list the author typed, and a file list is not a decision
about authorship. This is the same bound-dimension class the rest of this
evening is about, arriving in a shell loop instead of in a `subprocess` call:
three decisions about which characters to replace, and nothing deciding which
lines were ours to replace them in.
