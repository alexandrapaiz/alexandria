### 2026-11-09 - A ledger entry this seat has built has no status that says so, unless the owner moved it first

- Trigger: this run built the 2026-10-27 entry "The deploy surface's search
  window is shorter than the drift it measures, and it says so wrongly" in
  full, both of its asks. Its status is `proposed`. The charter is explicit in
  both directions: only the owner moves `proposed` to `accepted`, and this seat
  moves `accepted` to `built`. There is no move from `proposed` to `built`, so
  the entry stays `proposed` on the surface the PM grooms from, and the next
  Monday ceremony can groom an already-built item into a sprint.
- What: the gap is not an oversight in the charter, it is a consequence of the
  statuses being a single column doing two jobs. One is the owner's decision,
  which is hers alone and correctly gated. The other is the state of the work,
  which is a fact any seat can observe. Today a `proposed` entry can be
  unstarted, half-built, or finished and merged, and all three read the same.
  It happened here because a break-fix outranks the ledger in the charter's own
  priority order, so this seat was right to build an entry the owner had not
  ruled on, and then had nowhere to say it.
- First step: the smallest version is one new status, `built-unruled`, meaning
  the work is done and the owner's decision was never needed because something
  else outranked it. A seat may move `proposed` to that and to nothing else,
  and the owner's `accepted` or `rejected` still lands on top of it, so no
  authority moves. `tools/ledger.py` gains it as a legal value and the PM's
  grooming read filters it out. The alternative, which is a second column for
  work state, is better designed and is a schema change across 23,000 lines, so
  it should not be chosen without the owner saying the one-status version is
  too crude.
- Whose call: the owner's, because it is the ledger's own vocabulary and this
  seat does not get to name a state it may then enter.
- Cost: $0
- Status: proposed
