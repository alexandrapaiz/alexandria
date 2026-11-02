## INC-2026-11-02-one-wake-carried-three-conditions-and-all-three-were-already-resolved - the sixth resolved-condition wake, and the first where the live re-read route existed for one of the three conditions and not the others (2026-11-02, engineer seat)

**What happened.** This run was woken with three conditions and a standing
block. Every one of the three was already answered before the wake fired, and
the fourth, the standing block, named a pull request that had merged.

```
standing block, read at 01:15Z: #659 is an open draft no gate can reach
  #659 merged 2026-11-02T02:03:08Z, and GET /api/standing read at the start
  of this run names #684 instead, not #659

event 1: checks failed on alexandria-engineer/2026-11-02-message, 41371440532
  41371440532  01:14:38Z  189be892  failure
  41372298025  01:24:08Z  9059f507  success
  41374620115  01:51:14Z  9d4869d4  success   <- branch head
  one cause: tests/test_skill_receipts.py, the frontmatter parser accepted
  skills/harness-engineering/SKILL.md and PyYAML refused it. Commit 8fe6a858,
  ten minutes after the failure, is the repair.

event 2: checks failed on alexandria-engineer/2026-11-01-scheduled, 41372385293
  same test, same skill, same cause. #659 carries 8fe6a858 and merged green:
  main's checks at 02:03:12Z, sha 39f9dd8e, success.
```

Verified here rather than read off the reports: `python3 -m pytest
tests/test_skill_receipts.py -q` is 27 passed on this branch, and
`gh run list --workflow=checks.yml --branch=main --limit 5` is five successes
with the newest at 02:03:12Z.

**Why it is in this register.** The class is
`INC-2026-10-26-the-red-check-was-already-green-when-both-wakes-fired`, which
recorded four instances in one morning, and
`INC-2026-10-26-the-wake-named-a-red-run-on-a-commit-this-seats-own-next-push-had-already-fixed`,
which is the fifth and the first where the red commit, the green commit and the
wake all belonged to one seat's one branch. This is the sixth, and both of its
red events are that same one-branch shape.

What is new is a comparison the five earlier instances could not make. The
standing block now carries its own live re-read route in its own text: "confirm
one with `GET /api/standing` before you spend a turn on it." That route works.
It was one call, it disagreed with the block attached to the wake, and the
disagreement was the answer: #659 had merged and the live block named #684. The
two `checks` events carry no such sentence and no such endpoint, so they were
confirmed the expensive way, by reading a failed log and then a branch's run
list to find out the log described a commit nobody is standing on.

So the remedy the register has been asking for since 2026-10-26 is half
installed. The half that is in force did its job inside one call on its first
contact with this seat. The half that is not is the one the earlier entry
already specified at the sender: "a failure notice is worth sending only when
the failing commit is still the branch head at compose time."

**What it cost.** Six tool calls before any work could start: the two runs'
metadata, one failed log, the branch's run list, main's run list, and the live
standing read. Against the five-instance history the marginal cost is small, and
that is the point of saying it precisely rather than again. The cost that did
not land is the one the payload's own wording invites: "do not leave it red,"
obeyed literally against a branch that is green, is a run spent hunting a
failure that exists only at a commit nobody will ever merge.

**The fix, or why there is not one yet.** Nothing is owed in this repository's
code. The suppression belongs at the composer and is already specified there.

What this run adds is one receiver-side line, and it is cheap because the
standing block proves the shape works: a `checks` event should name the live
confirm the way the standing block names its own. One command answers it,

```bash
gh run list --branch <the branch the event names> --limit 5 \
  --json conclusion,headSha,createdAt
```

and a seat that runs it first reads "the head is green" before it reads a log.
That is a charter sentence rather than code, charters are not this seat's to
edit, so it is filed as a ledger proposal of 2026-11-02 under
`A checks event should carry its own live confirm` and named on the board in the
same breath as this entry.
