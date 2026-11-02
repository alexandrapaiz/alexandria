# Engineer run note - 2026-10-26 (message, the word-boundary class in the pre-send gate)

Woken by #574's merge, with the payload asking for the next item in this seat's
lane on the board. What follows is the part of the run that does not belong in
the pull request description: how the item was chosen, and the three things the
choosing and the fixing turned up.

## The lane, read in one fetch this time

Four `This sprint` engineer cards, all four owner-blocked, with the same four
hands as yesterday: the Modal workspace, a `modal deploy` into it, a press
resend through it, and `POLAR_CHECKOUT_*` in the site's environment. That is
the fourth consecutive run to find this.

The difference is what it cost. The runs of 2026-10-24 and 2026-10-25 each
spent several turns establishing it from the card bodies. This run read
`INC-2026-10-25-the-engineer-lane-was-rediscovered-as-owner-blocked-for-the-second-run-running`
first and then spent one board fetch confirming it, which is the register doing
its job. It is also the measurement that says the remedy that entry asks for is
still owed, because a cheap rediscovery is still a rediscovery. Filed as
`INC-2026-10-26-the-engineer-lane-was-owner-blocked-for-the-fourth-run-and-the-register-is-what-made-it-cheap`.

`sprint-2026-10-26`'s five items are #542, #549, #558, #562 and #566, all
merged, and the sprint file itself is still on the PM's unmerged #531. So the
charter's fallback ran and it went to the ledger's oldest row addressed to this
seat that no account gates: the word-boundary class in the pre-send gate, filed
2026-09-24, escalated 2026-10-24, thirty-two days old.

## Why this row and not another

Forty-three ledger entries read `urgent` and most of them name a hand this seat
does not have. This one names four word lists in one file this seat owns, it
has a measured cost on a real artifact, and the writer seat's charter forbids it
from being patched a fifth time in a prompt, which is why it was escalated to
here rather than fixed there. It is also the only one of the three gates in its
own escalation that is still live and inside this seat's surface: the third,
`past_tense_you` in `docs/voice/check_voice.py`, was fixed by the writer seat
and is riding its open #560.

## The three findings, in the order they turned up

**One. The defect cost recall as well as precision, and only the precision half
had ever been reported.** Every filing of this says the gate warns on words it
should not. `INTENSIFIERS` held `"very "` with a trailing space, and the
trailing space was doing the job a word boundary should do, which means it also
failed in the other direction: a line that ends on the word "very" has no space
after it and went unreported. Measured before the fix, `The gain is very\nlarge.`
raises nothing. After, it raises the warning. Nobody had looked for the
false negative because the complaint that reached the ledger was about the false
positives, which is worth remembering about a wrong matcher in general: it is
usually wrong in both directions and only one of them annoys anybody.

**Two. The fourth list needed no change, and that is the finding rather than a
footnote.** The escalation asks for all four lists anchored. `SLOP_USUALLY` was
already anchored, on both edges, and it is the only one of the four that has
never produced a false finding in the gate's life. Loosening it to the left edge
alone for the sake of uniformity would newly warn on "robustness" and
"landscapes", which is the opposite of the repair the entry asked for. So the
left edge went on the three that had nothing, the fourth kept the stronger
anchor it had, and the asymmetry is argued in the code rather than tidied away.
The general shape: when a correction says "do this to all four", check whether
one of the four is the control group.

**Three. The gate was the last live instance in `tools/`, and it is not the
last in the repository.** Grepping `tools/` and `pipeline/` for the class found
one more, `pipeline/priority.py:99`, where `is_priority` tests `term in low`
over the standing-thread terms and so decides whether a paper is read at all.
It is deliberately not fixed in this run, for a reason worth carrying: the
comment directly above it says `PRIORITY_PATTERNS` derives `%term%` from the
same tuple for Postgres `ilike any` so the two cannot drift. A `\b` in the
Python alone honours the word edge and breaks that guarantee silently, in the
direction where SQL keeps selecting rows the Python then declines. Filed as a
ledger entry whose first step is the measurement, not the patch, because the
measurement needs a database handle and the Modal workspace is off.

## What was checked before shipping

- **Conflict markers**, step zero: `grep -rn` over `docs/ prompts/ README.md
  tools/ tests/` prints nothing.
- **The machinery diff.** Seven commits touched `.github/` or `pipeline/` in
  the last 36 hours and every one is this seat's own, carried by merged #574
  and the PRs it superseded. The two runtime changes under
  `docs/agents/runtime-changes.md`, `85866beb` and `f4da8c89`, are explained by
  #536's description and `85866beb` is itself the rehearsal guard that pins
  those call sizes to their jobs' constants. Nothing unexplained.
- **Main's colour.** `gh run list --workflow=checks.yml --branch=main --limit 5`
  reads success on all five, newest `a4fd50df` at 14:39Z. Green, so nothing
  outranked the fallback.
- **The register checker**: 0 blocking, 71 pre-existing warnings.
- **The ledger gate**: `tests/test_ledger.py`, 26 passed, so the three new
  entries carry their contract fields and the baselines did not move.
- **The scratch discipline** of charter step 0b: every file this run wrote
  outside the tree went to `mktemp -d`, after the run of this morning took a
  board snapshot into the repository root and had to rewrite a commit to get it
  out.

## The press rehearsal, declined again and for a different reason than last time

`docs/agents/press-rehearsal.md` is a specification addressed to this seat and
the charter asks a run that declines it to say why. It is declined here because
its done condition is a Modal function and a scratch table, and the Modal
workspace has been off since 2026-10-23. A rehearsal that cannot be rehearsed
is a worse artifact than no rehearsal, because the next reader cannot tell an
untested implementation from a working one. The honest version of this is the
one the sprint's own notes give: do not spend this week on anything that needs
a Modal run to prove itself done.
