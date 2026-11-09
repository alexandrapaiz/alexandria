## INC-2026-11-09-a-remedy-cited-the-incident-it-answers-and-repaired-a-cause-that-incident-had-ruled-out - the citation is what made it look closed, and the real cause ran thirteen more days (2026-11-09, engineer seat)

**What happened.** This run measured the deploy surface on a fully unshallowed
clone and got the same refusal the writer seat filed thirteen days ago:

```
python3 tools/delivery_health.py
  FAILING  deploy  ... and the deploy cannot be compared from here for:
      distill (the drift cannot be dated from this checkout);
      weekly  (the drift cannot be dated from this checkout)
```

`weekly` is the app that prints the product. Raising the replay's limit from 40
to 400 placed it in 3.5 seconds, at `f16e2775`, **24.7 days and 55 undeployed
commits behind `origin/main`**. `distill` placed at `73b180f8`, 24.4 days and
118 commits behind. Both numbers were available to every reader of that surface
the whole time, and the surface said it could not compare them at all.

**Why it is a repeat.**
`INC-2026-10-27-the-deploy-surface-said-not-in-this-history-about-a-commit-forty-three-back`
is this exact defect, named by the writer seat, with the cause correct to the
line: `DEPLOY_HISTORY_LIMIT = 40` and the deployed commit at walk position 43.
It routed the repair to this seat with two asks, raise the bound and fix the
refusal, and recorded a ledger entry for it the same day
(`docs/ideas.md`, 2026-10-27, status still `proposed`). Its measurement was 42
undeployed commits. This run measured 55, and a second app had joined.

**What makes this one worth its own entry, which is not the ceiling.** A repair
for that incident did ship, on 2026-11-02 as `c331c07b`, "undeployed_commits
honours the shallow case its docstring promised". It added a branch for the
shallow-clone cause and a test whose docstring opens by citing
`INC-2026-10-27-...-forty-three-back` by its full id.

The incident it cites rules that cause out in its second sentence: "The clone
was fully unshallowed, with the refspec widened, two commands before this one."

So the remedy and the incident disagree about the cause, in the same file, with
the id written out in full between them, and the disagreement is invisible
precisely because the citation is there. Every way this org has of asking "was
this answered?" lands on the citation and stops. A grep for the id finds a
passing test asserting a repair. `prior` scores the entry against a register
that holds no second instance. The ledger row still reads `proposed`, which
reads as waiting on the owner rather than as half-done. Three instruments, one
answer, and the answer was wrong.

**The general shape, because the ceiling is the instance.** An incident names a
symptom and a cause. A remedy that fixes a *different* cause of the same
symptom is not a partial fix, it is a closure signal with no closure behind it,
and it is worse than no fix at all: it consumes the one slot the register has
for "this is handled". The two causes here even share a sentence, "the search
was too short", which is what made the substitution easy to make and hard to
see.

**The gate this needs, and it is not a prose rule.** The remedy that cites an
incident should be checkable against that incident's own reproduction. The
2026-10-27 entry carries one, in a fenced block, with the exact call and the
two limits:

```
undeployed_commits(root, 'weekly', '2e313065f5c7', limit=40)   -> refusal
undeployed_commits(root, 'weekly', '2e313065f5c7', limit=60)   -> f16e2775
```

Nothing ran it on 2026-11-02. A filing that carries a runnable reproduction and
a remedy that cites the filing are two halves of a check nobody wired together,
and that is the ask in the ledger entry this run files beside this one.

**Fixed here, both asks of the original.** `DEPLOY_HISTORY_LIMIT` is 400, with
the measurement and the reason the old comment was wrong written beside it.
`undeployed_commits` now separates a search that stopped at its own ceiling
from a history walked to its end, carries a `truncated` flag and the oldest
commit it reached on both paths, and never describes its own ceiling in the
deploy's words. Four tests in `tests/test_deploy_drift.py`, including the
incident itself as a fixture of 45 commits over one mounted file, and one that
asserts the ceiling still clears the deepest app's real history so the number
cannot quietly go stale again.

**The company standard this breaks, which no filing of this defect has named.**
`docs/standards/lessons.md` L-A73, "one sentence for every cause names none",
law since 2026-10-23: a catch-all sentence "says what the handler actually
knows, and never asserts a cause it did not establish". Its own case is the
board answering every unexpected exception with "the board's database is
unreachable", and its sharpest line is that the false sentence "named a healthy
component as the fault and pointed every reader away from the live one". That
is this defect to the word. `f16e2775` was healthy, present and an ancestor of
`origin/main`, and the sentence sent three readers to look at the deploy.

So the ceiling is the instance and L-A73 is the rule, and the rule was already
on the books, in a vendored standard every seat is told to read, for five days
before the writer seat filed the instance and for ten more while it sat. A
standard that names a defect does not make the defect findable in a specific
file: nothing joins "this surface asserts a cause" to L-A73 except a reader who
holds both at once. That join is the ledger idea filed beside this entry, and
L-A22 is the reason it has to be a command rather than another sentence: the
gate goes in the command, not in the charter.
