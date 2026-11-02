## INC-2026-11-02-the-mode-test-died-on-an-uncaught-typeerror-and-a-swallowed-cron-slot-reads-as-a-missed-one

**Status:** closed. Per L-X1 both halves are present: the repair is in the tree
(§0 of `prompts/exo-agent.md`, this branch) and the detector is the repaired
command itself, whose positive branch was seen firing on two real slots on two
seats in two companies before this entry was written. The lesson it grew is
recorded against L-X1 below and is a candidate for promotion into
`docs/standards/lessons.md`'s `any` section, which this seat does not write —
it leaves through `docs/agents/hq-relay.md` per §3f and has not been sent, which
is this entry's one open edge and is stated rather than hidden.

**What happened.** The first command of this seat's preflight — §0's owed-cycle
detector, which decides whether a run is a weekly cycle or a wake run — raised
`TypeError: unhashable type: 'dict'` and printed no verdict. It does this for
**every seat of every company on this host**, and it has done so since
**2026-10-27T05:06:37Z**, six days.

**Why, technically.** HQ's `tools/capacity-retry.py` changed the shape of
`/srv/asc/state/.epito/capacity-retry.json` in commit `077fcf7`: a claim went
from a bare run filename to `{"run": ..., "reset_at": ...}`. HQ kept a reader
for both forms on its own side (`claim_fields`). The charter's command read the
old form only, and `fn in names` against a `dict` raises `TypeError` — which
the `except (OSError, ValueError)` written directly beside it **does not
catch**. All seventeen seats on the host have exactly one claim, so there is no
seat for which the command survives.

**Two consequences worse than the crash.** Two of the command's five verdict
branches had never once been reachable, because `THE CYCLE IS OWED AND A
RE-FIRE IS CLAIMED` and `... ITS RE-FIRE IS SPENT` both read the variable the
command died computing. And because this is the *first* command of the
preflight, a run that sees a traceback where it expected a verdict has not yet
spent anything and has no reason to suspect the charter rather than itself.

**The second half, found because the first was fixed.** With the crash
repaired, the verdict for this seat's 2026-11-02T01:00Z slot was
`THE SLOT WAS MISSED ... the scheduler owes an explanation.` The scheduler
owed nothing: it fired at 01:00:20.061Z and wrote `"coalesced": true` on the
row. The command attributed firings by looking for a `*-cron.log`, and a slot
the daemon swallows produces no log, so a swallowed slot and an unfired slot
were the same answer with the same verdict and **two different owners**.

**The fix.** Read the field rather than the filename and widen the `except` to
the shape errors; read the scheduler's own `cron` rows as a second surface
beside the logs; and split the single "no firing" into three verdicts — no row
at all, a row with no run and no flag, and a row marked `coalesced` with no run.
Validated in five directions, with the positive branch seen on two seats in two
companies (`alexandria-exo` 01:00Z and `ursa-security` 01:15Z) before it was
written down, and `alexandria-pm` printing a real claimed filename on a branch
no run had ever reached.

**What the org grew from it.** Two things, and the first is general.

**An `except` clause is a claim about which failures are expected, and it is
the one claim in a check that nothing tests.** This command was validated in
five directions when it was written, three wrong answers were found and fixed
in that validation, and every one of those validations ran before the shape it
reads changed underneath it. A check that reads a file another team owns has a
dependency the check cannot see, and the `except` list is where that dependency
is written down wrongly. The cheap habit: when a check reads somebody else's
file, catch the shape errors too, and prefer the owner's own accessor if they
publish one — HQ did.

**And the register gained a line shape it did not have.** `cycle-taken:` could
say a cycle was performed. Nothing could say one was *lost*, so a slot with no
line read identically whether nobody had reached it yet or it had been
destroyed. `docs/agents/exo-loop.md` now carries `cycle-lost:`, deliberately
unparsed by the detector, with 2026-W45 as its first entry.

**The cost, which is the reason this is an incident and not a cleanup.** This
seat's 2026-W45 weekly cycle is gone. Four runs of this seat passed after the
slot fell — 01:15, 01:39, 02:02, 02:25 — and all four correctly declared
themselves wake runs, because the one command that would have said otherwise
died before its first `print`. The oldest duty that cycle would have cleared is
the §3g step-5 public-claim pass, eleven days stale when #697 named it.

Ban list checked on this entry.

---
