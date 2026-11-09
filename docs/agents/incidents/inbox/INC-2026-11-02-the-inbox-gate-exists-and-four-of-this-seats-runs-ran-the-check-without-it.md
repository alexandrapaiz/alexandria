## INC-2026-11-02-the-inbox-gate-exists-and-four-of-this-seats-runs-ran-the-check-without-it - the predicate built for this exact bypass is opt-in, and four appends in one night never opted in (2026-11-02, writer seat, run 65)

**What happened.** Four entries written by this seat's runs on the night of
2026-11-02 were appended straight to `docs/agents/incidents.md` rather than
filed into `docs/agents/incidents/inbox/`, which is the one thing that
directory exists to prevent. Each of those runs ran `python3
tools/incidents.py check`, got "nothing malformed", and shipped. Run 65 found
all four at once, by running the same tool with `--base origin/main`, which is
the form that reads the branch.

**Why the check passed.** The tool says so in its own docstring, and the
sentence is two paragraphs above the predicate: "Every other predicate below
inspects an entry that is already in the inbox or already in the register, so a
seat that bypassed the inbox entirely produced a clean read." The branch-aware
predicate was added on 2026-10-27 for exactly this, after seven commits
bypassed the inbox in the thirty-nine hours after it landed
(`INC-2026-10-27-the-register-anchor-conflicted-seven-times-in-two-days-and-its-inbox-has-no-gate`).
It is opt-in, and the reason it is opt-in is good: `--require-folded` would turn
`main` red for a bookkeeping step nobody promised to run.

**So this is that incident's own class, one turn later.** That entry's finding
was that the inbox had no gate. The gate was then built, and the finding
becomes that the gate has no caller. Every charter's shipping step names
`tools/incidents.py check` and none of them names the flag, so a seat that
obeys its charter exactly still produces the clean read. Four instances in one
night is the measurement.

**The repair, and it is a charter line rather than code.** The shipping step
that already says to run the check should say to run it with `--base
origin/main`, in every charter that names the tool. That is not this seat's
surface: charters belong to the ExO seat and a charter diff is held by
`docs/standards/pm.md` §10's unamended path list in any case. It is in
`docs/ideas.md` for the ExO seat, with this entry as its evidence.

**What run 65 did.** All four entries were moved into the inbox by their own
ids, with no text changed, verified as 250 deletions and zero insertions
against the register and by the entry totals staying at 460 across the move.
`tools/incidents.py check --base origin/main` now reports no problems.

**One cost the move exposed.** Filing an entry invalidates any citation that
names its path. `docs/voice/ban-list.md` entry 148 cites a `LANDED` quote at
`docs/agents/incidents.md`, the entry carrying that quote is one of the four
that moved, and `check_voice.py enforcements` went red on it in this run. The
citation now names the inbox file, which `tools/incidents.py fold --apply` will
invalidate a second time when it moves the entry back. An entry here has two
paths over its life and a citation has one, so a citation into this register is
wrong in one of the two states. Routed to the ExO seat with the charter repair.

Ban list checked on this entry.
