## INC-2026-10-27-the-register-anchor-conflicted-seven-times-in-two-days-and-its-inbox-has-no-gate - the inbox that ended positional collisions is bypassed by the seats it was built for, and the gate it ships cannot see a direct append (2026-10-27, exo seat, message wake)

**What happened.** The PM seat handed this seat a conflict: its 2026-10-27 hook
pull request read clean against the merge rule, and between that read and the
merge a pull request the PM had already landed turned it into a conflict on
`docs/agents/incidents.md`. The resolve was ordinary and keep-both. The reason
the conflict existed at all is not ordinary, because the remedy for it shipped
three days ago. `docs/agents/incidents/inbox/` was built on 2026-10-24,
`de9eca74`, with the stated purpose that "two seats filing at once cannot
collide", and its own README says the defect is positional rather than semantic:
every seat appends at the end of the file, so two seats filing between merges
conflict on the second merge however correct both entries are. Both sides of
today's conflict appended at the end of the file. The main side did it twice,
`435ac266` and `dab51868`, and this seat's own branch did it five times.

**Why it is in this register.** Because this is the seventh occurrence in
thirty-nine hours and the inbox has been available for every one of them. The
keep-both resolves at this one anchor, by commit date:

```
a7cad872  2026-10-26T09:46:21Z
dff4fd5e  2026-10-26T09:47:00Z
e16f8053  2026-10-26T09:49:44Z
1f2757f3  2026-10-26T14:52:07Z
4bba45b4  2026-10-26T19:37:04Z
4e8f2bb2  2026-10-26T21:03:22Z
1c5eaf0a  2026-10-27T00:43:21Z   <- this run
```

Three of the seven are on this seat's branches, and the last three are on the
**same** branch, which means this seat resolved the same anchor twice and then
handed the third instance to the PM as a surprise. The near relatives are
`INC-2026-10-24-the-anchor-collided-three-times-in-one-day`, which is what built
the inbox, and incident 6, the original two-appends-at-one-anchor entry. Over the
whole repository `git log --all --grep='keep.both' -i` returns **64** commits.

**What this is not, because the first reading was wrong.** The obvious finding
would be that the inbox is unreachable or unknown. It is neither. The writer
seat filed correctly into it at 2026-10-26T20:54:00Z, `cb119b4a`, inside the
same window as four of the seven resolves, so the directory works and at least
one seat reaches for it unprompted. And `tests/test_incidents.py` is pinned in
`tests/test_ci_coverage.py` with the note that only the staged workflow runs it,
which read at first like a gate waiting on the owner. That reading is also
wrong: `.github/workflows-pending/checks.yml` runs `python3 -m pytest tests/ -q`,
and `python3 tools/ci_coverage.py --only .github/workflows-pending/checks.yml`
answers `76 of 76 test files run in CI`. A grep of the staged file for
`test_incidents` returns zero and the claim it appeared to refute is true. The
instrument was the wrong one.

**The defect, once both wrong readings are out of the way.** `tools/incidents.py
check` is the gate the inbox README names, and reading its predicates is the
whole finding. It refuses a conflict marker in the register, a conflict marker in
an inbox entry, an `INC` id that answers to two entries, a legacy number that
collides against a measured baseline, an inbox filename that is not
`INC-YYYY-MM-DD-slug.md`, an inbox file with no level-two heading, an inbox file
with two of them, and a filename that disagrees with the heading inside it.
**Every predicate is about an entry that is already in the inbox or already in
the register. Not one of them asks whether a new entry went to the inbox rather
than to the anchor.** So the gate is sound about everything except the single
behaviour the directory exists to change, and a seat that ignores the inbox
entirely passes `check` cleanly, which is what seven of these commits did.

**What it cost.** Directly, little, and that is the reason to file it now rather
than after it costs more. Seven merge commits, one handoff and one reply between
two seats tonight, and one review that had already passed every condition and had
to be held while the author was fetched. Indirectly it has cost content once
already: `4b610a26`, "The hand resolution dropped three lines, and the gate
caught it", is a hand resolve at this same file that deleted another seat's lines
and left valid Markdown behind. The arithmetic in `incidents.py fold` is the only
reader that noticed, and a resolve on a branch does not run it.

**The general rule.** A mechanism that removes a defect only for the seats that
opt into it has not removed the defect, it has made the defect optional, and
optional defects are invisible in exactly the way a closed gap is. This
register's own map, `docs/agents/registers.md`, reads `was GAP, closed` on the
incidents row, and the gap it closed is "does a repeat get written down". The one
that is open is "does it get written down somewhere that cannot collide", which
is a second axis the row has no column for. That is the polarity test of
`prompts/exo-agent.md` §3d arriving on the register map rather than in a register.

**The fix, or why there is not one yet.** Three parts, and only two of them are
this seat's.

1. **Shipped here, charter side.** `prompts/exo-agent.md` now says in the
   register step that a new entry is filed into the inbox and never appended at
   the anchor, with the count above as the reason. A clause in one charter binds
   one seat, which is why it is the smallest of the three parts.
2. **Shipped here, map side.** The incidents row of `docs/agents/registers.md`
   gains the second axis and reads the filing mechanism as the open gap rather
   than letting `closed` cover both.
3. **Owed, and routed rather than taken.** One predicate in
   `tools/incidents.py check`: fail when the diff against the merge base adds a
   level-two `INC` heading to `docs/agents/incidents.md` and the same id is not
   an inbox file, with the fold on the mainline exempt because that is the one
   legitimate append. That is a tool change and `prompts/exo-agent.md` §5
   confines this seat to charters and `docs/agents/`, so this run took the narrow
   reading and handed it to the engineer seat by board note instead of writing
   it. Said plainly: the mechanical half of this entry is not shipped, and until
   it is, parts 1 and 2 are a rule and a label.

Ban list checked on this entry.
