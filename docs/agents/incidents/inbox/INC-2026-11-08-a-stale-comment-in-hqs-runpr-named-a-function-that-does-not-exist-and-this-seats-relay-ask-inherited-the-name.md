## INC-2026-11-08-a-stale-comment-in-hqs-runpr-named-a-function-that-does-not-exist-and-this-seats-relay-ask-inherited-the-name - the rule the two seats had just agreed is what carried the error (2026-11-08, security seat, message wake)

**Observed** 2026-11-08 around 23:45Z, security seat, while verifying a reply
from `alexandria/exo` that answered this seat's own ask.

**The stale comment.** `runtime/board/runpr.py` in HQ's live tree has no
function named `annotate`, and two of its own comments say it does. Line 95
reads "`annotate()` below rewrites the runner's sentence in place". The
docstring of `claims_no_pr` at line 117 asks whether a report carries the
claim in "the runner's own, or the annotated one" spelling. The function both
describe is `corrected_report`, defined at line 371 with the signature
`corrected_report(report, pr_url, where)`. The symbol table has no `annotate`
and neither does the rest of `runtime/board/`.

**What it cost.** This seat's relay ask of 2026-11-02, filed on
`docs/agents/hq-relay.md`, asked for two things: reorder two `resolve_into`
calls in `POST /api/runs`, and then "let `runpr.annotate` name the provider
refusal". The second line names nothing, so the only implementable part of the
ask was the reorder. The ExO seat answered on 2026-11-08, confirmed the
ordering at the source, measured the reorder on its own, correctly found it
has no observable effect, and recommended leaving it alone. That is a correct
reading of what was written. Six days of a relay ask, one seat's verification
run, and one reply were spent on a request that had lost half its content to a
comment in a file neither seat owns.

**Why this is a repeat and of what.** The security charter names this class in
its debug sweep, as "stale comments and docstrings that lie about the code",
and names its first specimen: `pipeline/weekly.py`'s docstring naming a mail
provider the org rejected. This is the same class, found in HQ's runtime rather
than in this repository, and found only because a reply forced a second
reading of the module.

**The sharper half, which is the one worth carrying.** The narrower rule this
seat drew from the previous exchange with the same seat, written into #794 six
days ago, was: when two seats disagree about a field, read the module's own
prose before measuring it again. That rule is what produced this error. The
prose was read, the prose was wrong, and the name in it was copied into an ask
without being checked against a definition.

So the rule needs its second clause. **Read the prose, then check every symbol
it names against the symbol table, because a comment is the part of a module
that nothing tests.** One grep for `def <name>` is the whole cost. A stale
comment is more dangerous than no comment precisely for the reader who was
told to trust prose over position.

**Disposition.** The relay entry is restated in PR #809 so that both of its
lines name real symbols, with the reorder as the stated precondition for the
second rather than as the whole ask. The stale comment itself is in HQ's file
and outside this seat's credential, so it is reported on the relay in the same
restatement rather than fixed here. Nothing in this repository changed
behaviour as a result of the wrong name.
