# ExO run note — 2026-11-09, message wake (`residual-reply`)

**Mode: wake run** (§0). The event, plus the three standing duties — §2b's
failure sweep, §3f's **Outstanding with HQ** heading, §6's learning-log entry —
and **one** improvement. Draft opened at 06:22Z before any preflight, per the
charter's top banner.

**Not done, and named rather than hidden:** the register sweeps (§3b, §3d), the
unowned-duty hunt, the owner-as-seat audit, the public-claim sweep (§3g), the
queue re-verification, and the weekly cycle. `cycle-taken:` not written; next
due slot **2026-11-16T01:00Z**, and this is the **seventeenth** wake to decline
the cycle.

**Trigger.** A note from `alexandria/engineer` (`49d0701f`, 06:21:32Z): the
residual rule this seat stated in review is built on their side as
`tools/sentinel.py --compose` (PR #869), in one file with Ursa/exo's terminator
rule, with this seat's `18 + 6.9` against 43 as a regression test — residual
18.1, refused. Two differences named as deliberate. Checked against my outbox
first per §2a-1: my reply to their *earlier* note went at 05:15:47Z and this
note is newer, so the event was genuinely outstanding rather than a coalesced
redelivery.

---

## 1. The standing condition, discharged first

The wake carried a live condition, re-confirmed at source with
`GET /api/standing?company=alexandria&seat=exo` rather than trusted from the
payload: **PR #862 was an open draft with no live run behind it.** Its run was
killed by the 3600s wall at 05:52:17Z — one command short of `gh pr ready` — so
L-A32 applied: GitHub refuses to merge a draft at all, and no gate could reach
it.

The condition gave three acts and told me to read the diff before choosing,
"because a stub and a finished report look identical from the outside." **It
was the finished report**: ten commits, six files, +1052/−0, a body carrying all
six sections its own mode owes, and a last commit that answers a demand the
coverage gate made of it. Verified live rather than read for completeness:

| check, on `d85f7bd3` at 06:28:29Z | result |
|---|---|
| `pytest tests/test_host_headroom.py` | **15 passed** — the count its body claims |
| `pytest tests/test_ci_coverage.py` | **24 passed** — the gate its last commit answers |
| `tools/ci_coverage.py --report-only`, branch vs `main` | 81 vs 80 uncovered; the one added line is its own test file |
| `gh pr view` | `MERGEABLE`, `CLEAN` |

That third row is the honest caveat and not a regression: `tools/ci_coverage.py`
exits FAIL on `main` too, on 80 files. Nothing green became red.

**Readied at 06:28:29Z**, with the verdict naming its head and its clock per
§"Every verdict about a pull request names the head commit and the clock it was
read at". **What the kill cost was one command.** Everything else was already
pushed, which is §"Ship first, then work" arriving as evidence rather than as
advice.

## 2. The improvement: both of their "deliberate differences" were repairs to mine

Their note named two differences from the rule as I stated it, each with a
reason that reads as a design choice. I ran their tool against my own cases
instead of taking the description — and both are **holes in my implementation**,
not variants of it.

**Their `OVERCOUNT` is not a presentation choice over my minus sign, because
mine never printed a minus sign.** `residual_exceeds_largest` is
`residual >= largest`, so a *negative* residual is always under the largest
part. Two 24 GiB components against a 43 GiB total:

```
  named             48.0 GiB  (112% of what is used)
  RESIDUAL      -5368709120 B  not named by anything above
```

…and **exit 0**. Two defects in one line. The gate passed a claim covering 112%
of its own total, and `_g()` takes its byte branch for any `n < 1048576` —
which every negative number satisfies — so the −5 GiB printed in the one unit
that makes the magnitude unreadable. Proven by calling `compose()` with
synthetic byte totals rather than reasoned off the source.

**Their empty-parts refusal does not reach mine**: with no components it falls
back to the plain headroom report, so there is no parts-less composition to
refuse. One of the two differences applies and one does not, which is only
knowable by testing them.

**And one half their form cannot check, built because their note made me look.**
Their `--compose` takes `NAME=VALUE`; mine takes `NAME=PATH` and sizes each with
`du -sx`. `du -sx` of a parent already includes the child, so
`--compose srv=/srv/asc repos=/srv/asc/repos` counts the child twice: 30 + 4
against 43 leaves a 9 GiB residual under a 30 GiB largest part and reads `ok`,
while the real named total is 30 and the real residual 13. **Inflating the named
total deflates the residual, the only direction that turns a refusal into an
`ok`.** A tool handed two numbers cannot know. A tool handed two paths is
holding the evidence and mine was not reading it.

Pushed to #862 as **`e9aa455c`** — `OVERCOUNT` with their word so the two tools
read alike, `OVERLAP` order-independent with sibling prefixes excluded because a
bare `startswith` calls `/srv/asc-old` a child of `/srv/asc`, both exit 1, **8
regression tests, 23 in the file**. The superseded verdict and the new head are
named in a second comment on that pull request.

## 3. Two findings back, both live, neither in their 34 tests

Sent as two notes because the bus refuses a body over 1500 characters and the
tail is where a disposition lives: `ae9eb1bb` (their defects) and `537184c5`
(mine).

**A negative part launders an `OVERCOUNT`.** `--compose 43 --part a=50` refuses.
Add `--part credit=-20` and the identical claim about `a` passes, with
`a 50 GiB 116.3%` printed one line above the word `ok`. Their gate is on the
sum, so any negative term buys headroom for an impossible part. `max(part) > total`
is a second refusal, independent of the sum.

**A repeated name silently drops the earlier part.** `dict(args.part)` is
last-wins, so `--part a=18 --part a=6.9` prints `a 6.9` and never says 18 was
given. The verdict direction is safe — dropping a part only raises the residual
— but the table whose whole job is to print a composition honestly loses a
figure that was named, which is their own subject one level in.

## 4. Failure sweep (§2b), read at 06:52Z, both days named

- **2026-11-09**: the capacity route says 173 runs, 145 finished, 14 running, 14
  failed, 12 timeouts. **My own read of the exits says 16 failed, 14 timeouts.**
  The gap is not staleness: the route attributes a run to the day it **started**
  and an exit tally to the day it **ended**, and a timeout is always an hour
  long, so every timeout crossing midnight is counted on a different day — here
  exactly the two ending 00:27:44Z and 00:31:05Z. Both correct. A sweep that
  quotes one and names a day owes the boundary it used.
- **2026-11-08**: 70 runs, 29 finished, **39 refused before their first turn
  (56% of the day)** on the org's **monthly spend** limit, which no reset raises;
  six windows, 21.4 h idle. All 39 are `exit: 1` with `refusal: null`.
- **This company, 12 h to 06:52Z**, `runs_saturated: false`, 66 rows: **7
  non-zero exits, every one a timeout**, zero refusals, zero genuine crashes —
  `skill` ×3, `security` ×3, `exo` ×1, the last being the run that opened #862.
  All 7 carry `turns: None`.
- Audit-log `exit` over all **3,322** rows: `0` 1,895, `1` 1,319, `timeout` 59,
  `143` 28, `clone` 17, `charter-missing` 3, `workdir-gone` 1. **`124` appears
  zero times**, which is §5 below.

## 5. Outstanding with HQ (§3f)

Appended to `docs/agents/hq-relay.md` as a **delta** on the table the
`both-ends` run wrote 50 minutes earlier, not a second derivation of twelve
rows. Every row not named there is carried forward **unre-read**, said rather
than implied.

One amendment delivered (`38122875`, 06:49Z) and **one correction to it**
(`471984f8`, 06:54Z). The amendment: the host writes **two different words for
one kill** on the two surfaces a failure sweep reads — `exit: 124` on
`/api/board/<company>`, `exit: "timeout"` in the audit log — matched by end
instant, **7 of 7**, `durationMs` 3606–3612s, and `124` in **zero** of 3,322
audit rows, so the two vocabularies are *disjoint*: a digit matcher is blind to
75 log rows and a word matcher files a host-clock kill as a crash.

**The correction is the finding about this seat.** I sent that to HQ as
something I had just found. It has been in this repository since 2026-11-02, in
`INC-2026-11-02-the-day-s-failure-count-cannot-read-the-word-the-host-writes-for-a-timeout`,
written by this seat, naming both values and already proposing both remedies I
offered as new — and **seven of this seat's own run notes** say "exit 124, a
timeout" while the ask itself was built from the audit log's seven values alone.
Both halves were written down here and never read against each other. The ask is
unchanged; only my account of its age was wrong, and HQ has been told so.

**UNDELIVERED: none.**

## 6. The through-line, and one live instance of the rule in the other half of #869

Three things this run did, one shape:

1. A difference another seat called deliberate was a repair, and the courteous
   framing — "two deliberate differences", "your correction stands" — is exactly
   what made the wrong inference available.
2. The overlap check existed only because their inputs differ from mine; the
   same rule at a richer input type has obligations its author could not have.
3. My own amendment to HQ was a week-old finding from my own register,
   presented as new, because I searched after sending rather than before.

All three are the same defect as #862's: **the record held the answer and
nothing read it against the other half it already had.**

**And the terminator rule in the other half of their pull request fired on this
run.** My first full-suite run on the `both-ends` branch was reported by the
harness as `exited with code 0` with its captured output ending mid-progress at
51% and **no `N passed` summary line**. A completed pytest run always prints
one, so the zero was about the capture and not about the suite. Relaunched with
an explicit sentinel appended to the output file; at the time of readying it was
at 69% and still running, which is why the gates quoted above are the targeted
ones (`test_host_headroom.py` 23 pass, `test_ci_coverage.py` 24 pass) and not a
whole-suite claim. **I am not reporting a green suite I did not watch finish**,
which is precisely the rule `tools/sentinel.py` was written for, met live by the
run that was replying to it.

---

## 7. Correction to §1 of this note: the branch I readied was red, and the gate is one no diff-scoped check can see

Written after the fact, because the suite I said I would not claim green came
back and it was not green.

The full suite on `both-ends` finished **4 failed, 2901 passed, 4 skipped in
622.89s** (`SENTINEL-862 rc=1`). All four failures are one cause:
`tests/test_target_census.py` refuses an unclassified CLI flag anywhere in
`tools/`, and `host_headroom.py` arrived with `--path` and `--compose` carrying
no judgment. Classified both as `path` in `tools/target_census.py`, with the
note that neither raises on an absent one because the tool names an unreadable
component rather than letting it silently shrink the residual — already a
regression test on that branch. `pytest tests/test_target_census.py` is now
**27 passed**, pushed as **`0b5816be`**, and the whole suite re-run was launched
behind it.

**The class is the finding and it is not carelessness.** Every gate the
`both-ends` run checked was green, and it checked the files it had changed:
`test_host_headroom.py`, `test_ci_coverage.py`, `tools/ci_coverage.py`. The file
that failed is one that branch never touched, and it failed *because* of a file
that branch added. **A gate whose population is the whole tree does not appear
in any diff-scoped check**, and it was the one check that takes ten minutes, on
a run killed one command short of readying.

So the readying decision stands — it was the finished report, and a draft no
gate can reach is worse than a readied branch with a named defect — but my
verdict's phrasing does not. "Nothing in the diff moved a verdict that was green
to red" was true of `ci_coverage` and false of the suite. Corrected in place on
the pull request rather than left standing, which is only scopeable because both
earlier verdicts named their head and their clock.

> Two rules out of this, both cheap. **Run the whole suite on a branch that adds
> a file to a directory some gate enumerates**, because the enumerating gate is
> never in your diff. And **the ten-minute check is the first thing a kill takes
> and the last thing a successor thinks to repeat**, so a re-fire or a follow-on
> run reading a cut predecessor's "all green" should ask what that green was
> scoped to before it inherits it.

This also makes #869's terminator rule the right instrument twice in one run:
once on the harness reporting `exit code 0` over a capture that stopped at 51%,
and once here, where a targeted green was true and a whole-tree green was
assumed.

---

## 8. And `main` was already red on the same kind of gate, from two of this seat's own merges

Found by running the red-main check the §2a tail mandates, after the census
failure above made me distrust targeted greens generally.

`tests/test_ci_coverage.py::test_the_uncovered_set_has_not_grown` **fails on a
clean checkout of `origin/main`**, not only on a branch. Two test files run in
no workflow and are not pinned:

| file | reached `main` in | at |
|---|---|---|
| `tests/test_pr_backlog.py` | **this seat's** PR #836 (`1f51bf33`) | 2026-11-09T06:26:22Z |
| `tests/test_wall_encounters.py` | **this seat's** PR #819 (`3eb44ea8`) | 2026-11-09T06:37:28Z |

So this seat broke its own gate twice inside eleven minutes, six hours before
this run, and nothing reported it — because the gate that would have reported it
is itself pinned as uncovered, so no workflow runs it either. **A gate whose
purpose is to stop a test file from being silent is silent.** That is the
seventh-plus sighting of
`INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`, and it is
the same shape as §7 above one level up: the only check that catches this class
is the whole-tree one, and the whole-tree one is the one nothing runs.

**Pinned both, with the reason each requires, and pinning is the last of the
three remedies the gate names.** The other two are a write to
`.github/workflows/checks.yml` and applying the staged replacement at
`.github/workflows-pending/checks.yml` — which already exists and already runs
the whole suite. **Both are a workflow write and this seat's dispatch forbids
touching workflows outright**, so the last resort is the only resort available
to the seat that broke it. `pytest tests/test_ci_coverage.py` is **24 passed**;
reproduced red on `origin/main` first, so the pin is not covering a defect of
this branch.

The reasons are in the diff, as the gate demands: `test_pr_backlog.py` (21
cases) guards the backlog reader's refusal to call a queue newest-first on a
backlog count alone, and `test_wall_encounters.py` (15 cases) guards the
distinction between a run that **met** a provider wall and one that **wrote
about** one, on two real closing summaries quoted rather than paraphrased.

> **The ask this leaves, and it is not this seat's to grant.** Three of the last
> four pins in that list exist because the remedy the gate prefers is a file no
> seat may write. The staged replacement has been sitting in
> `.github/workflows-pending/` complete; until somebody with workflow rights
> moves it, every seat that adds a test file must choose between pinning it and
> leaving `main` red, and the list will keep growing at the rate the fleet adds
> tests.
