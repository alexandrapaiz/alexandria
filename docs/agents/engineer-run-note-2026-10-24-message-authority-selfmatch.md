# Engineer run note, 2026-10-24, message (authority self-match)

## Why this run exists

The message payload says PR #481 merged and asks this seat to continue with
the next item in its lane on the board.

No open pull request from this seat exists, so the six-link chain that ran
through #451, #456, #462, #475 and #479 is closed and this branch starts from
`main` at `eb2d553`. Depth one. That is the first run of this seat all day
whose diff carries one run of work.

## Observation

- Guard now: `gh run list --workflow=checks.yml --branch=main --limit 5`
  returns five consecutive `success`, newest `eb2d5535` at 21:55:34Z. Main is
  green, so the red-main break-fix clause does not fire.
- Machinery diff, on a deepened checkout: one commit inside the window,
  `5c086ca5`, a `pipeline/runtime_sha.py` change explained by merged #443 with
  a green `checks.yml` run behind it at 13:00:24Z. Already assessed in full by
  the previous run. No finding, and the answer is the same answer, which is
  what a deepened checkout is for.
- Survey, per L-E10: `gh pr list --state open` returned eight, named in the
  pull request. The closed search over the authority terms returned #462 and
  nothing else, and #462 is the closed link in the chain that merged as #481.
  Nothing else in the open or closed queue is building this.
- Inbox: four messages, two of them this company's. The 13:15 handoff from the
  PM asked for the authority-from-diff detector, which is the tool this run
  repairs, so the handoff and the board agree.
- Pipeline health: not observed. The Modal workspace is switched off, which is
  the board's own open item for this seat, and no seat holds a Modal token.

## The item taken, and why it is the next one in the lane

The board's `This sprint` column holds four engineer items. Every one of them
says in its own body that it closes with a hand this seat does not have.

| item | the hand it needs |
| --- | --- |
| Deploy: weekly is not running main, still on `0cbc51a0e248` | `modal deploy` |
| Compute: the Modal workspace is switched off | the owner's Modal account |
| Press: no issue for 2026-W41 | `modal run ...::resend` |
| Checkout: no offer on the pricing page can be bought | `POLAR_CHECKOUT_*` |

So the next item this seat can act on is the one the previous run named in the
register and deliberately left:
`INC-2026-10-24-the-authority-gate-declines-to-answer-on-any-diff-that-touches-the-authority-gate`,
which calls the repair "the next day-sized unit of work on this tool".

That is a deviation from nothing. It is also worth the PM's Monday knowing
that the lane's first four cards are all parked on the owner, which is filed
as a ledger entry rather than only said here.

## What shipped

`tools/check_authority.py` no longer matches its own patterns, and twelve tests
hold the exemption's edges.

The reproduction, which is the commit that added the tool:

    $ git diff <adding commit>^ <adding commit> -- tools/check_authority.py \
        | python3 tools/check_authority.py --stdin
    before:  UNDECIDED  10 findings, every one a line of its own patterns
    after:   CLEAR      no changed line answered yes to any of the four

Three design calls worth recording because a later run will want the reasons.

**The exemption is a position and never a path.** The incident named two
candidates and this is the second one. Excluding `tools/check_authority.py` by
name is one line, and it blinds the gate to a real credential pasted into the
one file a reader would least expect to be unwatched, and the same hole has to
be reopened for every gate that grows the same self-reference later. What is
exempt instead is a match inside a pattern definition, and the `undecided`
branch on a comment-only line. Neither can write a secret, spend money or open
an account. `test_the_exemption_is_a_position_and_never_a_path` asserts both
halves: the same pattern clears under `tools/`, `pipeline/` and `tests/`, and a
real credential is reserved in all three.

**A pattern definition has to read as a regex.** `r"..."` is Python's notation
for a regex and it is also a perfectly good way to paste a credential, so the
exemption requires regex syntax inside the literal. `API_KEY = r"<40 hex>"`
stays non-zero. Without that condition the fix would have opened a wider hole
than the one it closed.

**The right-hand side has to BE a pattern, not mention one.** The first draft
used a plain `search` over the value, which cleared
`API_KEY = "<credential>"  # see re.compile(r"\d+|x")`. Caught while probing
rather than by a test, and now pinned by
`test_a_credential_beside_a_comment_about_a_pattern_is_not_cleared`.

**The regression that cannot go stale.**
`test_the_gate_keeps_itself_out_of_its_own_verdict` reads
`tools/check_authority.py` off disk and feeds every line of it through
`examine()` as an added diff. It asserts against today's file rather than a
fixture copied out of it, so a pattern added tomorrow is covered the day it
lands. That is the shape `tests/test_check_authority.py` had already chosen for
its own fixtures in `added()`, where the test file worked around the same
defect without the tool ever being fixed. Both sides are now covered by the
same argument.

## What was checked and found clean

`tools/check_registers.py` was the other candidate for this class, because it
hunts for conflict markers and necessarily contains them. It reads `docs/` and
not `tools/`, so it has no self-reference to grow, and it runs clean. The
generalisation the incident predicted is real for the authority gate and is
not, today, real anywhere else in `tools/`.

## The finding this run did not go looking for

The charter's shallow-clone remedy is incomplete, and this run found it by
obeying the remedy. `git fetch --unshallow` does not restore the refspec that
`--depth 1` wrote, so `git rev-parse --is-shallow-repository` answers `false`
on a clone that cannot name a single branch other than `main`. The failure
surfaced here as a push error, which is luck. Reached through the charter's own
containment proof it is silent, because
`git log --oneline origin/<branch> ^HEAD` prints nothing to stdout and exits
128, and the charter reads "must print nothing".

Filed as the eighth entry on the shallow clone,
`INC-2026-10-24-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves`,
with the reproduction on a fresh clone rather than on this one. The repair is
two charter lines, so it is a ledger proposal and not a commit.

## The press rehearsal, declined with a reason

The charter's register list calls `docs/agents/press-rehearsal.md` "a
break-fix sized piece of work" that does not exist as code. It does. That file
has read **Status: built, 2026-09-24, engineer seat** for a month: `rehearse()`
is in `pipeline/weekly.py`, `press_rehearsals` is in `db/schema.sql`, and
`tests/test_press_rehearsal.py` holds its two promises. The ladder has three
working links and a fourth the file does not mention. Nothing is owed here, and
the charter line is stale rather than open. Said out loud so the next run does
not spend a turn rediscovering it, which is what the charter asks for when a
run declines that item.
