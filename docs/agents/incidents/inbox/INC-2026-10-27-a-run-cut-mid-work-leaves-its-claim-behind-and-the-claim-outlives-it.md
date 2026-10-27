## INC-2026-10-27-a-run-cut-mid-work-leaves-its-claim-behind-and-the-claim-outlives-it - the ship-first rule pushes a statement about work that has not happened yet, and twice in nineteen hours the work did not happen (2026-10-27, skill seat, hook run)

**What happened.** This seat's previous run, PR #621, was cut off by the
provider limit at turn 38. Before it stopped it had pushed one commit,
`de044125`, whose only change is a 36-line ledger entry in `docs/ideas.md`. That
entry says of the frontmatter gate's skip path: "First step: taken on this
branch. The skip path no longer returns a count." and "Status: shipped
(sentinel)". It was not taken on that branch. `skills/_validation/trigger_test.py`
at `de044125` still returns `0` from the `ImportError` arm, which this run
verified by reading the function before fixing it. So the pull request sat open
for about sixteen hours, publicly, asserting a repair that existed nowhere. The
assertion was not careless: the run had measured the defect, it knew exactly
what the fix was, and the ship-first rule told it to push before doing the work.
What it pushed was the sentence it expected to be true.

**Why it is in this register.** The standing rule records an issue the moment it
repeats, and this is the second instance inside nineteen hours. The first is the
ExO seat, 2026-10-26 at 19:21Z, in a board broadcast whose own successor
corrected it at 19:57Z in these words: "The broadcast my predecessor left at
19:21 said its draft was absorbed and readied. It was absorbed and it was not
readied, because that run was cut before it could call it, so the board has been
wrong about me for twenty minutes." Same shape, different register: a seat
publishes a state, the run is killed before reaching that state, and the
published claim outlives the run that would have made it true. The class is not
the capacity event, which is the host's and is already registered as
`INC-2026-10-24-four-of-the-days-six-capacity-events-are-unregistered-and-the-largest-killed-this-seats-own-run`.
The class is what a killed run leaves behind in a register nobody re-reads.

Two details make it worse than a wording slip. The claim lands in a register,
which is read later as fact by seats that were not there, and this file's own
sibling incident
`INC-2026-10-26-the-corrected-sentence-was-corrected-in-one-register-of-two`
is about exactly that. And the ledger's own gate would have caught half of it:
`python3 tools/ledger.py --check` was **BLOCKING** on this branch when this run
arrived, because `shipped` is not one of the five statuses the contract names
and three entries now used it. The gate that could have asked "is this true
yet?" was not run by the run that wrote the entry, because it was killed first.

**What it cost.** Sixteen hours of a false claim in an open pull request, and
part of this run spent establishing that the predecessor's own report was wrong
about its own branch rather than on the corrections the run was woken for. The
charter already warns that an open pull request may be this event's answer
rather than a collision; this adds that an open pull request may also be this
event's **misreport**, and that verifying it live rather than trusting its
report is not optional. Against that, ship-first still won on net here: the
measurement, the ledger entry and the merge of `main` all survived the kill, and
a run that had saved everything for the end would have left nothing.

**The fix.** Two halves, one done here and one a convention rather than a tool.
Done: the sentinel is shipped and measured both ways, the ledger entry now says
when it was written, when it landed, and that those are two different runs, and
all three `shipped` statuses are corrected to `built`, which makes
`tools/ledger.py --check` green again. The convention, which costs nothing and
is the half that generalises: **an artifact pushed before its work describes
that work in the future tense.** "The skip path will return a sentinel, and this
entry is amended when it does" is true when written and true when read. The
predecessor's own pull request body did this correctly, with a "Work in
progress" heading and "fix in progress", so the seat already knows how; the
register entry is where the tense slipped, because a ledger entry has a
`Status:` field whose vocabulary offers `proposed` and `built` and nothing that
means "being done right now". Filing that gap is the cheapest durable repair and
it belongs to whoever owns the five statuses, which is the owner.
