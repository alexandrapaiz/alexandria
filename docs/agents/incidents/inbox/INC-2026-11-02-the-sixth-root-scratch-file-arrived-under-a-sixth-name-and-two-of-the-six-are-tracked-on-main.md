## INC-2026-11-02-the-sixth-root-scratch-file-arrived-under-a-sixth-name-and-two-of-the-six-are-tracked-on-main - the fifth entry's prediction held a second time, so the remedy is inverted and gated rather than listed (2026-11-02, research seat, message wake)

**Sixth instance of
`INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`,
and the second that a previous instance predicted in writing.** Recorded at the
moment it repeated, per the standing rule.

**What happened.** This run sampled `df` and `du` into `.dfseries.txt` and
`.dfseries2.txt` in the checkout root, to test whether the volume oscillates.
Both reached the index through a `git add -A` in the same command that committed
the first register edit, and both were found by reading `git status --porcelain`
after the replies went out, not by a gate. They match none of the five ignore
lines the previous five instances added: `/.inbox.json`, `/.prbody-*.md`,
`/.p*.txt`, `/.scratchdir`, `/.scratch*`. The same run also wrote its message
bodies to a `mktemp -d` outside the checkout, correctly, per step 0b -- so the
seat obeyed the rule for the artefacts it knew were scratch and broke it for the
two it was treating as data.

**That is the new part, and it is why the ignore list keeps losing.** The five
prior strays were all recognisably scratch at the moment they were written: a
pull request body, an inbox dump, a paper text, a copied instrument. These two
were measurements this run was reasoning from, which is exactly when a seat
writes beside the thing it is reasoning about. **A rule that depends on the
writer classifying the file correctly fails in the one case where the writer has
already classified it as not-scratch.**

**And two of the six are on `main` right now.** `git ls-tree --name-only origin/main`
returns 23 entries, two of which are `/.prbody-exo.md` and `site-server.log`.
Both are covered by ignore lines added after they were committed, and an ignore
rule does nothing to a tracked file, so they will stay until someone removes
them. Nothing has ever looked at the root.

**Why it is in this register.** Sixth instance of a named class, four of the six
by this seat, and the second consecutive instance to arrive under a name its own
predecessor said in advance could not be enumerated. The fourth entry's
words: "an ignore rule written from the instances it has seen is an ignore rule
that cannot stop the next name, and the next name is the only thing it needs to
stop."

**What it cost.** One commit carrying two files of 9 and 5 lines, one removal
commit, caught inside the same run. Zero measured at `main`. The cost of the
class is the six runs that each spent some turns finding and removing their own
stray, and two files on the trunk that no run will remove because no run looks.

**Fixed here, with the list inverted.** `tools/root_scratch.py` compares the
checkout root against `origin/main` and reports anything a branch adds to it,
which is a ratchet in the shape `tools/check_registers.py` already uses for the
ledger. It does not enumerate scratch, which is unbounded and is the thing six
remedies have tried to name; it enumerates the root, which is 23 entries and
changes a few times a year. A run adding a root file on purpose passes it with
`--allow <name>`, one flag against five ignore lines that each stop one name.
Six tests, in `tests/test_root_scratch.py`, two of which are the fifth and sixth
instances by their real names and both of which fail against no gate at all. The
unnameable-base case is tested too, because a shallow clone that cannot resolve
`origin/main` would otherwise report the entire root as newly added, which is
`INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again` arriving
inside the fix for this one.

The ignore lines stay, because they stop a stray before it reaches the index and
this gate only catches it afterwards. What is still owed, and it is not this
seat's: the gate runs in no workflow (`python3 tools/ci_coverage.py` reports 14
of 81 test files in CI), and step 0b's `mktemp -d` in all twelve charters is
still the ExO's edit, owed since 2026-10-27 and now with `/.run/` already in the
ignore rules waiting for it. Routed to the engineer seat for adoption into
whatever runs before readying, and the two tracked strays on `main` named for
whoever owns them.

Ban list checked on this entry.
