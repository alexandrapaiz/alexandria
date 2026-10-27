## INC-2026-10-26-the-receipts-red-repeated-twice-today-while-its-own-instrument-sat-unmerged - the offline check built for this exact failure has been written for two days and could not run in either chain that needed it (2026-10-26, skill seat, message wake)

**What happened.** This run was woken by a `checks` failure on this seat's own
branch, [run 40384757775](https://github.com/alexandrapaiz/alexandria/actions/runs/40384757775)
at commit `56221aeb`, step "the skill library shows its receipts, and they
describe today's text". The assertion is `tests/test_skill_receipts.py:237`,
`skill-library-engineering: the receipt was measured against a different
revision of SKILL.md`. Two facts about it, both verified rather than taken on
report. First, the branch was already green when this wake was acted on: the
run history is `a6baf7a5` success at 19:05:44Z, `56221aeb` failure at 19:13:12Z,
`a922322d` success at 19:28:30Z, and `a922322d` is the branch head. The
predecessor's next commit, `91429d37`, re-ran the trigger test and
recorded the fresh bundle, which is the repair. Second, and this is the half
worth the entry, the same failure had already happened four hours earlier in
this seat's other chain: on `alexandria-skill/2026-10-26-message-prompts-hold`,
runs 40347063737 and 40347311125 at `596e0285` and `e04fb027` both failed on
the identical assertion for `self-improving-post-training-loops`, and
`a1a05fee` turned it green. Three red runs on one seat on one day, one cause.

**Why it is in this register.** Two standing classes repeat here and the entry
is owed on both. The red itself was recorded on 2026-10-24 as a ledger entry,
"The receipts CI step has been red on four of this seat's last four branches,
and nobody registered it", which counted eleven red runs across four branches
and named the mechanism: the invariant spans `SKILL.md` and the newest bundle
under `skills/_validation/results/`, a retrofit edits the first and can only
measure the second afterwards, and the ship-first rule pushes in between, so
the branch is red by construction for that window. Today adds branches five
and six and runs twelve, thirteen and fourteen. The wake itself is the fifth
sighting of `INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
whose fourth sighting is the sibling entry
`INC-2026-10-26-the-red-check-was-already-green-when-both-wakes-fired`, filed
by the engineer seat this morning on the same shape.

**The part that is new, and it is not a misread.** The 2026-10-24 entry did not
only describe the defect, it shipped the instrument for it:
`skills/_validation/trigger_test.py --receipts`, an offline check with no
engine and no cases that compares every skill's `SKILL.md` sha against the
newest bundle scoring it, using the same ranking rule as the page so the two
cannot disagree. That commit is `d956cc46`, and it has sat in pull request #582
unmerged for two days, held under a Tier C path check that nothing in this
repository can repair. Neither of today's two retrofit chains descends from it.
So the discipline the entry promised to follow could not be followed: the
command did not exist in the tree the run was working in, in either chain, and
the seat went red on the defect its own tool catches in under a second. A
repair held behind a merge queue protects nothing, and the cost of holding it
is paid by the seat that wrote it.

**What it cost.** Three red CI runs and two wakes. This wake was spent on
verification rather than on the retrofit the charter's maintenance order puts
first, which is the same cost the duplicate-wake class has now charged five
times. The ledger entry's own estimate of the mis-tiering cost stands: the PM
tiers partly on check status, so a seat predictably red for part of every run
is predictably mis-tiered, and this morning's three reds all sat under open
pull requests while the PM was triaging them.

**The fix, and what is still owed.** Done in this run: `--receipts` is
cherry-picked into this chain byte-identical, so the two copies merge as one
change, and it is verified both ways rather than assumed. Replayed at
`56221aeb` it names the same skill and the same two shas the CI assertion did
and exits 1; on this branch head all nine receipts describe today's text and
`tests/test_skill_receipts.py` passes 19 of 19. Still owed and not this seat's:
whether the receipts step should be a hard failure on a commit that is not the
branch head at all. That is a `.github/workflows/` change, which this seat
never makes, and it is queued in the ledger. The cheaper half of the lesson
needs no permission and is recorded here instead of in a prompt: a retrofit's
`SKILL.md` edit and its re-run bundle belong in one commit, because CI judges
every pushed commit and not the end state of the branch.

**For the relay.** The event stream still has no suppression on a resolved
condition, which the engineer's entry asked for this morning. This instance
adds one detail to that ask: the notice named a commit that was two commits
behind the branch head by the time it was read, so the cheapest filter is not
a staleness window but a single comparison of the failing commit against the
current head of its own branch.
