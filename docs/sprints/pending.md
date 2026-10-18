## Updated 2026-10-18, ~07:15 UTC (message pass): PR #366 and #370 both already resolved before this pass started, nothing new to merge, confirmed rather than repeated

**Trigger.** The event bundle for this pass named three things: the
writer seat's run finishing with PR #366 open, the same event a second
time from a different report address, and PR #370 opened by
distribution (the lessons.md re-vendor from HQ 4464b1d). Each asked this
seat to check the item against the merge rule, merge what is this
seat's to merge, and hand the next thing to a seat on the board.

**PR #366, already merged by this seat's own prior pass.** The board's
inbox carries a `done` message from `pm`/`alexandria` at 07:12:52 UTC,
ref PR #369: the writer's seventh run fixed the budget-gate failure,
read clean and green under the merge rule (Tier B), and is merged as
`99a1405`. That pass also corrected its own hold from forty minutes
earlier (PR #367's "`prompts/` is Tier C" read), filing
`INC-2026-10-18-tier-c-carve-out-misread-a-sixth-time`. Confirmed rather
than trusted: `gh pr view 366 --json state,mergedAt` reads `MERGED`, and
`99a1405` is the newest commit on `main` before #370's merge. Nothing
left here.

**PR #370, already merged under the exo centralizer's own Tier A lane.**
`gh pr view 370` reads `MERGED`, `gh pr diff 370 --name-only` shows
exactly one path, `docs/standards/lessons.md`, opened ready per
ADR-011. That is the one file the centralizer may self-merge without
the owner (§10), so it was never this seat's decision to make.

**Hand the next thing to a seat: nothing new to hand.** Every open pull
request already names a seat already working it: #358 (engineer, the
checkout alarm's reader) and #356 (frontend, the dead pricing pills) are
both drafts already in progress against their own backlog cards. The
two engineer-facing proposals PR #366 filed in `docs/ideas.md` (a
pre-commit budget check, splitting the press into a write call and a
check call) are `proposed`, not `accepted`, so dispatching either would
invent the owner's verdict rather than relay one. Posted a `done` on the
board naming this rather than repeating #369's account.

**Run health.** `gh run list --limit 30`: the six failures in the last
24 hours are all on `alexandria-writer/2026-10-18-message-payload-audit`
and `alexandria-writer/2026-10-18-message`, the same budget-gate class
PR #366 fixed. No new failure class. `checks.yml` on `main`: success,
from the #366 merge (`99a1405`), 2026-10-18T07:09:33Z.

**Queue gauge, four numbers.**
1. `main`'s newest commit: `99a1405` (the #366 merge), minutes old.
   Newest `checks.yml` on `main`: success.
2. Open pull requests: 12 total (#272, #331, #332, #333, #335, #356,
   #358, #362, #365, #367, #368, #369). 0 opened since the #366 merge.
3. 7-day conversion: 62 merged over 103 opened (0.60), unchanged since
   the last pass — no new merge, no new open.
4. Deepest open chain: 2 (#272 to #331, exo's own), unchanged.

**Owed to the owner, unchanged, not re-litigated here:** the Polar
Merchant-of-Record account, the missing launch PR/FAQ on `main`, this
seat's own open pull requests `#332` and `#335`, and the nine-charter
branch-prefix fix.

**Merged this run:** none. Both named items were already settled, one
by this seat's own prior pass and one by a different seat's own Tier A
lane, before this pass read anything.

## Updated 2026-10-18, ~02:30 UTC (message pass): PR #352 and #357 checked against the merge rule and merged, the board's checkout-probe card closed, a charter fix handed to the owner

**Trigger.** The event bundle for this pass named seven things: four of
this seat's own prior passes already merged (`#347`, `#350`, `#353`,
`#355`, all confirmed on `main` before this run touched anything), PR #352
opening (engineer, the checkout probe, "nothing watched whether a sale can
happen at all"), PR #357 opening (okr, a second pass finding nothing new
to score), and the okr seat's run finishing with the instruction to merge
what is mine and hand the next thing to a seat on the board.

**PR #352 (engineer) checked against the merge rule (Tier B) and merged.**
By the time this pass read it, the PR was no longer the stub the 02:20
pass saw: not a draft, full run note and PR body, no `hold` label, no
comment, no review. `gh pr view` still reported `mergeable: CONFLICTING`,
which `docs/standards/pm.md` §11.2 warns is a cache GitHub may not have
recomputed, so this pass did not take the cached field as fact. Confirmed
directly instead: `git merge-base`, `git merge-tree` against `origin/main`,
and a real `git merge --no-commit --no-ff` in the working tree all agreed
the merge is clean, then aborted the test merge before touching anything.
Checked out the branch in a worktree and ran `tests/test_delivery_health.py`
directly, since the diff touches no path `checks.yml` watches: 29 passed, 0
failed. Diff is `tools/delivery_health.py`, `tests/test_delivery_health.py`,
one new run note, and the three append-only registers, no Tier C path.
Merged with `gh pr merge --merge`, no force, no squash.

**PR #357 (okr) checked against the merge rule (Tier B) and merged.** Not a
draft, `mergeable: MERGEABLE`, no `hold`, no comment. One file,
`docs/okrs/okrs-2026-Q4.md`, a 31-line note recording that nothing on the
board or in `pending.md` names seat `okr` beyond what `#351` already
closed, so this pass did no ceremony and said so. That is itself the
record the evidence rule asks for, not a no-op, so it merges.

**The checkout-probe board card closed, and one follow-up named rather
than re-asked.** Moved board item `01df58a7` (engineer, "nothing watched
whether a sale can happen at all") to Done with the merge and the test
count. The 02:20 pass had already named the one thing still owed on that
surface — the probe's failing assertion travels the same email alerting
path `mba` found notifies nobody, because the cooldown column it depends
on is database-only — so this pass did not re-ask it as a new card.
Engineer had already picked it up independently: **PR #358** ("the
checkout alarm gets a reader on the board") opened at 02:26:43Z, before
this pass's own board comment at 02:29. Still a draft, run note only, not
yet Tier-B-eligible. Named here, not acted on.

**A charter fix, checked and agreed, then queued for the owner rather
than made.** `alexandra-systems/exo-centralizer` handed this seat a
finding (board message, 02:24:14Z, ref `alexandra-systems#233`): nine of
this repository's charters (`engineer`, `finance`, `market`, `okr`, `pm`,
`sales`, `security`, `skill`, `writer`) still name the bare role in their
branch-naming line, while every run today actually branches as
`alexandria-<role>/...`. Verified rather than taken on their count:
`grep -n "branch named" prompts/*.md` across all nine confirms it, and
this charter's own branch lines on the bare names match the pattern. The
finding is real and matters for a reason beyond tidiness: a tripwire that
decides whether a self-merged run shipped anything reads this exact
prefix line as its fallback, so a stale prefix can report a real merge as
a false failure. Not fixed here. This seat's own boundaries section
forbids touching anything under `prompts/`, stricter than the company
standard's general Tier C authorship allowance, so the edit is the
owner's to make even though she could point another seat at drafting it.
Replied to the centralizer in first person on the board, named below as
an owner action.

**`#335` and `#332`, both this seat's own, both from last night, still
open.** Neither was in this pass's event bundle and neither is a Tier B
pull request this seat may merge under its own name (Tier B condition 1:
a PM's own pull request waits for another merger). Unchanged since the
02:20 pass's note; still waiting on the owner or a chair.

**Run health.** `gh run list --limit 30` shows every Actions run since
the last pass green; this pass itself ran entirely through the board and
local checks, not Actions.

**Queue gauge, four numbers.** `main`'s newest commit: this pass's own
`#357` merge, under five minutes old as this is written. Newest
`checks.yml` conclusion on `main`: success, from 02:03:44Z, unchanged
because nothing merged since carried a path that workflow watches. Open
pull requests: 8 total, 1 opened since the last merge to `main` (`#358`,
engineer, already named above). 7-day conversion: 56 merged over 55
opened, better than even. Deepest open chain: none of the 8 titles reads
as a continuation of another; depth 1 across the board.

**Owed to you, unchanged, not re-litigated here:** the Polar
Merchant-of-Record account (five weeks overdue), the missing launch
PR/FAQ on `main`, this seat's own open pull requests `#335` and `#332`
from last night, and now **the nine-charter branch-prefix fix**
(`alexandra-systems#233`), a one line edit per file the owner or a chair
can make directly, or hand to this seat to draft if she would rather it
came as a pull request she merges.

**Merged this run:** Tier B, two (`#352` engineer, `#357` okr).

## Updated 2026-10-18, ~02:20 UTC (message pass): PRs #349, #351, #352 and my own three answered, the dead checkout pills handed to frontend as a decided call, not asked twice

**Trigger.** Five events in this pass's bundle. PR #349 opening (writer,
the pricing page's archive claim). PR #351 opening (okr, O1-KR1 scored
missed). The writer's and okr's runs finishing, both already answered by
the same two PRs. The engineer's run finishing (PR #352, the checkout
probe, still a draft). A note from `alexandra-systems/mba` addressed to
this seat by name, naming one decision as mine to make: the two paid
pricing tiers render dead text with no link, and nobody's card covers
that seam.

**Own last run may still be open, checked first, three found, all
self-merged.** `#347`, `#350` and `#353` were this seat's own open pull
requests from earlier passes tonight, each touching `docs/sprints/pending.md`
only. Self-merged all three under Tier A rather than opening a fourth. Each
merge moved `main` under the next, since they all append at the same top
anchor, so each needed its own docs-only conflict resolved by hand, oldest
entry kept below the newer one each time (`docs/standards/pm.md` §10 rule 5
permits this for docs-only conflicts). `#335` and `#332`, both from last
night, are still open and still `CONFLICTING`; neither is today's event
bundle and neither is touched here.

**PR #351 (okr) checked against the merge rule (Tier B) and merged.** Not a
draft, no `hold` label, no comment, no review, `mergeStateStatus: CLEAN`.
One file, `docs/okrs/okrs-2026-Q4.md`, no Tier C path. Scores O1-KR1 and
O1-KR2 missed with the account, not the code, as the named cause, which
matches what this seat's own prior pass (`#350`) had already relayed from
`alexandra-systems/mba`.

**PR #349 (writer) opened `CONFLICTING`, resolved as a docs-only append,
then checked against the merge rule (Tier B) and merged.** Not a draft, no
`hold` label, no comment, no review. The diff is `docs/agents/incidents.md`,
`docs/ideas.md`, `docs/voice/ban-list.md` and one new file,
`docs/voice/pricing-claims-2026-10-18.md`, so no Tier C path. It had opened
in conflict with PR #348's own entries at the same two append-only anchors.
Resolved on the writer's own branch, kept both sides, PR #348's
already-landed entries first, each restored its own trailing
`Status: proposed` line rather than the two entries sharing the one line
`git` matched as common context (the exact defect
`INC-2026-10-18-keep-both-sides-orphaned` describes, and this pass is the
second time that exact shape has been hit in one night). Verified before
pushing: `tools/ledger.py --check` (0 blocking, at or under baseline) and
`tests/test_check_registers.py` (21 passed).

**PR #352 (engineer, draft, "nothing watched whether a sale can happen at
all"), real work, still not Tier-B-eligible.** The diff is substantial and
sound: a new `check_checkout` surface in `tools/delivery_health.py` that
reads the offers out of `site/lib/polar-core.js`, follows the checkout
redirect, and tells a seller hop from a sign-in hop from a dead one, with
203 lines of tests. But the run note and the PR description are both still
the ship-first stub, unfilled, so the branch looks abandoned from outside
even though it is not. Named on the board for engineer rather than acted
on here, with one addition asked before it is readied: route the probe's
failing assertion to a board item rather than the existing email path,
because `mba`'s note (below) found that path notifies nobody.

**The decision `mba` named as structurally nobody's, taken rather than
asked twice.** Both paid tiers on `libraryofalexandria.dev/pricing` render
`<span className="pill ghost">Opens shortly</span>` with no `href`
(`site/app/pricing/page.jsx:12`), five days past the committed launch date,
and `mba`'s case names the seam precisely: the copy card says it is not
payments plumbing, the payments card says it waits on the account, and
nothing names the button. `mba` put the choice as one of two: a real date,
or the word waitlist with the email form that already works. Decided here
as waitlist, because nobody can set a real date honestly while the payment
account itself is a five-week-overdue owner decision, and a date would be a
second unkept promise stacked on the first. The page already has a working
waitlist anchor two lines above the dead pills (`site/app/pricing/page.jsx:43,77`).
Handed to frontend as a decided call with the file and line named, not as a
question, since this is a copy call inside a seam two cards left open and
not spend, not an account, and not a secret. Replied to `mba` on the board
in first person with the same reasoning, and relayed the alerting-gap
finding to engineer on PR #352's own open branch.

**One `mba` recommendation named but not acted on here.** A second clause
for the objectives file, that the offer was redefined the evening before
O1-KR1 was scored and three of its five conditions were still open the
next morning, is not in `#351` as merged. Left for the OKR seat's next
pass rather than reopening an already-shipped file for one sentence.

**Run health.** `gh run list --limit 30` shows every GitHub Actions run
since the last pass green. None of tonight's message-driven passes
(this one included) run through Actions at all; they report through the
board, and nothing red was found there either.

**Queue gauge, four numbers.** `main`'s newest commit: this pass's own
chain of merges, under five minutes old as this is written. Newest
`checks.yml` on `main`: success (unchanged; none of tonight's merges were
code). Open pull requests: 7 total (`#352`, `#335`, `#332`, plus four from
other companies' seats this board also shows this seat), 0 opened against
this company since the last merge. 7-day conversion: improved again with
five more merges landing this pass. Deepest open chain: 1, nothing
currently stacked.

**Owed to you, unchanged, not re-litigated here:** the Polar
Merchant-of-Record account (five weeks overdue), the missing launch
PR/FAQ on `main`, and this seat's own open pull requests `#335` and `#332`
from last night.

**Merged this run:** Tier A, three (`#347`, `#350`, `#353`, own). Tier B,
two (`#351` okr, `#349` writer).

## Updated 2026-10-18, ~02:05 UTC (message pass): PR #348 (the buyer's path becomes measurable) checked against the merge rule and merged, the board card closed

**Trigger.** PR #348 (`alexandria-engineer/2026-10-18-message-buyer-path`,
engineer's third run today, "the buyer's path becomes measurable, visit to
install to payment"). Instruction: review it against the merge rule, merge
it, or say on the board what it still needs and hand that to its seat.

**Own last run may still be open, checked first.** Four found: `#347`
(this seat's own pass minutes earlier, merging `#312`/`#343`/`#346`),
`#350` (this seat's own pass right after it, the pricing-checkout
handoff), and `#335`/`#332` from the night before. All four wait on
another merger under Tier B condition 1 (a PM's own Tier B pull request
waits for the owner or HQ's PM) and all four touch only
`docs/sprints/pending.md`, append-only at the top rather than at a fixed
anchor. Branched from `main` anyway: this pass's own work (reviewing one
engineer pull request) shares no code scope with any of the four, so
whichever merges first gives the others a one-line keep-both, the same
shape this chain has used all day.

**PR #348 opened `CONFLICTING`, then checked against the merge rule
(`docs/standards/pm.md` §10 Tier B, amended §21) and merged.** Not a
draft, no `hold` label, no comment, no review. `gh pr diff --name-only`:
`db/schema.sql`, two new `docs/agents/` and `docs/product/` files,
`docs/agents/incidents.md`, `docs/ideas.md`, three `site/` files (one
new), `tools/buyer_path.py`, and three test files — no `.github/`, no
`prompts/`, no `company.yaml`, no secret, so no Tier C path. The one
check defined, the digest-budget gate, read `SUCCESS`.

It opened in conflict with `main` at the usual two append-only anchors,
`docs/ideas.md` and `docs/agents/incidents.md` (the tail this org's own
ledger and incident register keep colliding at, same shape as `#312`,
`#343` and `#346` today). Resolved it locally first, oldest-then-newest,
to confirm the conflict really was docs-only before touching anything —
then found the engineer's own branch had already pushed the identical
resolution seconds earlier (`mergeStateStatus` flipped to `CLEAN` between
my fetch and my push), so my own local resolution was discarded unpushed
rather than raced against a live branch, the same move `#347` made on
`#312` a few minutes before.

**No other seat holds a claim on the surface.** Read the file lists of
every other open pull request (`#332`, `#333`, `#335`, `#347`, `#349`,
`#350`) rather than their titles: the only overlap anywhere is the same
two append-only anchors shared with `#349` (writer), which is the
ordinary keep-both conflict this org already resolves on whichever
merges second.

**Verified before merging, against the engineer's own resolved tip, not
assumed from the pull request's own report.** Full suite in a venv:
`pytest tests/ -q` → 1698 passed, 12 skipped, 0 failed. `node --test
tests/path.test.mjs` → 25 passed, 0 failed. `python3
tools/check_registers.py` → 0 blocking, 71 warnings, the same baseline
`#347` measured. Merged clean at 2026-10-18T02:03:41Z. `main`'s next
`checks.yml` run came back `success` three seconds after the merge
commit landed.

**Board.** Card `c688ef2e` ("Build a way to measure the buyer's path")
moved from Review to Done, with the merge-rule check posted on it in
first person. The two things the engineer's own report said still need
the owner — applying `db/schema.sql` so the new table exists, and
optionally granting GitHub's `administration: read` traffic permission
for the one unmeasured step, the install — are named there, not
repeated as new pending lines here, because the engineer's own pull
request already names them in full and nothing here adds to that.

**Run health.** `gh run list --limit 30`: all 30 `success` or in
progress, nothing failed since the last pass.

**Queue gauge, four numbers.** `main` under two minutes old at this
pass's own merge, its newest `checks.yml` run `success`. 10 open pull
requests, 0 opened since this pass's own merge (two did open earlier in
the window this merge closes, `#351` okr and `#352` engineer, both
answering `#350`'s board handoffs). 7-day conversion 48 merged over 84
opened (0.57), up from `#347`'s 0.58 reading of six-hour-old numbers
because the denominator moved faster than the numerator in between.
Deepest open chain: 1, nothing currently stacked.

**Owed to you, carried from `#347`/`#350`, not re-verified this pass
since it is out of this pass's one trigger:** the press and site read
FAILING at thirteen-plus days stale (a `modal run` only a human token can
fire), two pending `modal deploy`s on `distill` and `ingest`, the Polar
Merchant-of-Record account, and this seat's own four open pull requests
above waiting on another merger.

**Merged this run (Tier B, `docs/standards/pm.md` §10/§21), one:**
`#348` (engineer).

## Updated 2026-10-18, ~01:50 UTC (message pass): the pricing page's dead checkout links handed to engineer and okr, nothing here mine to merge

**Trigger.** One event this pass answers: a handoff from `alexandra-systems/mba` (board message, `alexandra-systems` PR #216) addressed to this seat by name. The other three events in this pass's batch (PR #343 and #346 opening, the engineer's and writer's runs finishing) are already closed: PR #347, open against `main` as this entry is written, reports merging #312, #343 and #346 and already filed the related "complete archive" claim on the frontend's lane. Checked PR #347's own description before writing anything here rather than redoing its work; it does not mention checkout links at all, so the MBA handoff is the one genuinely new item.

**The finding, read directly rather than relayed.** `libraryofalexandria.dev/pricing` renders "Opens shortly" with no href on both paid tiers, confirmed against `site/app/pricing/page.jsx:12` and the three unset env vars (`POLAR_CHECKOUT_TRIAL`, `POLAR_CHECKOUT_MONTHLY`, `POLAR_CHECKOUT_LIFETIME`). O1-KR1 committed both tiers purchasable end to end on 2026-10-13; today is the fifth day past that date with nothing on the page a person can buy. The code half shipped on time (alexandria PR #285, per MBA's own read of it): entitlement, checkout route, webhook, fail-closed, all real. The blocking half is that the Polar account itself has never been created, which `docs/product/polar-go-live.md` already names as the owner's decision (ADR-30, ADR-31), not a seat's and not mine. MBA has already put that half to the owner directly as this week's case's first recommendation, so this seat is not duplicating that ask.

**What is mine, and what I did with it.** Nothing in either repository's automated checks would have caught this: `tools/delivery_health.py` watches the failure *after* a sale (a verified payment that can't become access) and has no check for the failure *before* one (an offer that can't be bought at all). Handed to `engineer` on the board (handoff, cites MBA's message and the three env var names) to add one outside-in probe to `tools/delivery_health.py`: fetch the public pricing page, assert at least one checkout link is present and resolves with a success status, fail otherwise — the same shape as the existing availability guardrail, sized at MBA's own "a morning, not a project." Handed to `okr` on the board (handoff) to record in `docs/okrs/okrs-2026-Q4.md` that O1-KR1 is not met as of 2026-10-18, with the reason named as the payment account rather than the code, since the code shipped on the committed date. Both are handoffs, not `gh workflow run` dispatches: the event bus (`docs/standards/pm.md` §17) is what has been waking this company's seats all day, and neither `docs/okrs/` nor `tools/` is this seat's writable surface, so the entries themselves are not mine to write.

**Worth a register, not filed as one today.** This is the same shape as incident 24 (a product surface fails silently because nothing outside-in watches it) on a surface delivery-health.md's own table does not yet list (payments). It isn't a repeat of a prior entry, so the standing rule does not require filing it here; naming it for the ExO seat, whose file `docs/agents/delivery-health.md` this would extend with a fifth table row once engineer's probe exists.

---

## Updated 2026-10-18, ~01:43 UTC (message pass): three Tier B merges clear the night's docs-only queue, the press's two-week gap gets a second, verified consequence

**Press is thirteen days stale, not a headline buried in a list.** The
delivery endpoint still reports 2026-W40 (2026-10-05) as the newest issue, and
`tools/delivery_health.py` calls both `press` and `site` FAILING for it.
Two Mondays, 2026-10-12 and 2026-10-19 minus one day, have gone unwritten.
The fix is one `modal run` command costing about eighteen cents, named on
board card `92ab912d`, and it needs a hand on a Modal token that no agent
seat holds. Not new this pass, but independently reverified against the live
site rather than relayed, and sharper than the 2.2-day reading this card
opened with on 2026-10-14.

**Trigger.** Three events, the first two repeats this pass closes exactly the
way the last one closed PR #342: PR #312 opening (engineer, ready for
review) and the writer's own run finishing, which this pass reads as "merge
what is yours, close what is superseded, hand the next thing to a seat." The
third is PR #345 (this seat's own prior pass) having merged, which is the
instruction to continue with the next item in this lane.

**Own last run may still be open, checked first.** `#335`
(`alexandria-pm/2026-10-17-message-seats-off-github-review`) and `#332`
(`alexandria-pm/2026-10-17-message-sellable-regroom`) are both still open
from the night before and both wait on another merger under Tier B
condition 1 (a PM's own Tier B pull request waits for the owner or a chair).
Branched from main anyway: this pass's own work (reviewing three other
seats' pull requests) doesn't share scope with either of theirs. All three,
plus every pull request below, append to `docs/sprints/pending.md` at the
top rather than at a fixed anchor, so whichever merges first gives the
others a one-line keep-both.

## PR #312, #343 and #346: three Tier B merges, the same docs-only collision three times running

**#312** (engineer, "the press stops skipping Mondays in silence") opened
`CONFLICTING` against the same two append-only anchors this chain has hit
all night, `docs/agents/incidents.md` and `docs/ideas.md`. Not a draft, no
`hold` label, checks green (the budget guard). While this run was resolving
the conflict on the branch, the engineer's own concurrent push resolved it
first and the pull request turned `MERGEABLE`/`CLEAN` on its own; this run's
local resolution was discarded unpushed rather than raced against it. One
comment present, from HQ's YC advisory seat, explicitly self-labelled
non-binding ("Not a verdict: a voice in the room") and its own verdict is
"concur. Merge it," so it does not count as the owner comment Tier B
condition 2 guards against. Merged.

That comment also raised the press staleness independently, with one
consequence this seat's own tracking did not have: the pricing page sells
the free tier on "every issue in full" and "the complete archive," words
that are false while the archive has a two-week hole. Verified directly
against the live site rather than taken on the advisory's word (both quotes
below). Commented on card `92ab912d` with the sharper number and filed a new
card, `af60726e`, on the frontend seat's lane for the claim itself, since
it's a different surface and a different fix than the send.

**#343** (engineer, second run, "the two stalled press drafts get a
disposition each") finished #312 before this pass could and closed #315 as
abandoned with its branch kept. Docs-only once #312 landed on main and
dropped out of the diff: a run note, two incident entries, four ledger
entries. No draft, no hold, no comment, no checks defined (correctly: no
`pipeline/` or `skills/` path). Opened `CONFLICTING` against the same two
anchors a second time, resolved on the branch the same way, oldest first,
with the orphaned trailing `- Status: proposed` line this PR's own body
names as a risk restored for every entry it touched. Merged.

**#346** (writer, third run, "the side-by-side the owner asked for on
2026-10-05, and nobody fired") found that card already shipped and instead
migrated 27 days of lost preference data into `docs/agents/preference-data.md`'s
schema. Docs-only: two registers plus four files under
`docs/voice/preferences/`. No draft, no hold, no comment, no checks defined.
Opened `CONFLICTING` against the same two anchors a third time in one pass;
resolved the same way. Merged.

All three verified before push: `tools/check_registers.py` (0 blocking, 71
warnings, at the baseline every one of tonight's passes has carried) and
`tests/test_check_registers.py` plus `tests/test_board.py` (75 passed).
`tests/test_deploy_drift.py`, `tests/test_distill_fulltext_budget.py` and
`tests/test_press_watch.py` green on #312's merged tree (111 passed, 5
skipped locally for a missing `tiktoken`, confirmed unrelated to this diff
by running the same suite against a clean checkout of `origin/main`, where
the same 5 skip and 7 unrelated oauth/db-outage tests also fail for the same
missing-dependency reason this sandbox has).

## Verified directly: the pricing claim against the live site

```
https://libraryofalexandria.dev/api/delivery returned "Newest Press Issue:
Week 2026-W40 (created 2026-10-05)", thirteen days old today.

https://libraryofalexandria.dev/pricing returned "Every issue in full" and
"The complete archive" on the free tier.
```

Both fetched fresh this pass, not relayed from the YC advisory comment,
though it found the same thing first. Filed as board card `af60726e` for
the frontend seat (the claims-gate surface owner for site copy), with the
writer seat advising on the words, the same split this pass's other merges
used for the catalogue and install-line copy.

## Delivery health, read from the artifact per `docs/agents/delivery-health.md`

`python3 tools/delivery_health.py` against the live endpoint, this pass:

- **press: FAILING.** 2026-W40 is the newest issue; 2026-W41 has ended. One
  issue missing, now thirteen days, not the 2.2 this card opened with.
- **site: FAILING.** Same cause, read from the database-backed archive
  rather than a commit: the press wrote no row for 2026-W41.
- **deploy: FAILING, and freshly interesting.** `distill` is 2.0 days behind
  `origin/main` as of this merge: the undeployed commit is `f976b72`, which
  is #312's own fix, landed nine minutes before this reading. `ingest` is
  1.0 days behind on two undeployed commits. Both need `modal deploy`, which
  no agent seat can run.
- **pipeline: ok.** Ingesting and distilling within two days.
- **archive: ok.** The record and the archive both end at 2026-W40, so
  nothing between the database and the public page has drifted further.
- **mcp: ok.** Up, and refusing unauthenticated calls.
- **payments: unknown.** `payment_exceptions` could not be read here; no
  agent seat holds the credential, same as every prior pass.

## Run health

`gh run list --limit 30` across all agent workflows, all green since the
last pass. Fleet health is clean; the open finding above is delivery health,
which is the other half, and the artifact says it plainly rather than by a
scheduler's silence.

## Queue gauge, four numbers

1. **`main`'s age and checks.** Newest commit (#346's merge) under a minute
   old at this writing. Newest `checks.yml` run on `main`: success (fired by
   #312's merge; #343 and #346 were docs-only and correctly triggered none).
2. **Open pull requests.** 7 total: #272, #331, #332, #333, #335, #347
   (this one), #348. Zero opened since the last merge.
3. **Conversion, 7 days.** 47 merged / 81 opened = 0.58, up from 0.54 at the
   last pass six hours ago and 0.49 the pass before that.
4. **Deepest open chain.** Two (`#331`, `#332`, each self-reported "depth
   two, not at the depth-three blocking threshold"). Nothing stacked past
   that.

## Not touched, named rather than acted on

- **#272** (exo, 2026-10-11, Tier C: touches three charters including this
  seat's own, `prompts/pm-agent.md`): still open, not mine to merge or
  close, six days old and idle since its own first hour. The company
  standard's Tier B clause 6 would close an idle pull request past seven
  days; it is not there yet.
- **#331** (exo, draft), **#333** (frontend, draft), **#348** (engineer,
  draft): all live runs, nothing to act on.
- **#335, #332** (this seat's own, open since the night before): unchanged,
  still waiting on another merger.

## Linear trial

Not checked this pass — a message-triggered pass of this size stays inside
the merge-rule and board duties; the weekly note is the ceremony run's.

## Owed to you, unchanged, not re-litigated here

The Modal redeploy for #312's fix and the now two-undeployed-commit `ingest`
drift (both `modal deploy`), the press issue itself (`modal run`, ~18
cents, closes tonight under its own label), the Polar Merchant-of-Record
account (ADR-30), the missing launch PR/FAQ on `main`, and your own open
pull requests `#335` and `#332`.

## Merged this run

**Tier B** (`docs/standards/pm.md` §10, amended §21): `#312` (engineer),
`#343` (engineer), `#346` (writer).

## Boundaries respected

Writable surface only: `docs/sprints/pending.md`, plus resolving the three
docs-only conflicts on the other seats' own branches, which is this seat's
to do under §10 rule 5. No charter, workflow, secret, or product code
touched by this pull request itself.

## Updated 2026-10-18, ~01:20 UTC (message pass): PR #342 (the writer's selling copy) checked against the merge rule and merged, a thirteen-day-stale board card closed, the install page's own unfinished claim handed back to engineer

**Trigger.** Four events this pass answers, two of them repeats of events
the last pass already closed: the engineer's run finishing (PR #339,
already merged by this seat's own prior pass as #344) and three of this
seat's own pull requests merging (#338, #341, #337, also already
self-merged and recorded by that same prior pass). The one genuinely new
event is PR #342 opening (writer, "the skills' selling copy, and the
delta claim it cannot make").

**Own last run may still be open, checked first.** `#335`
(`alexandria-pm/2026-10-17-message-seats-off-github-review`) and `#332`
(`alexandria-pm/2026-10-17-message-sellable-regroom`) are both still
open, both from last night, and both wait on the owner under Tier B
condition 1 (a PM's own Tier B pull request waits for another merger).
Branched from main anyway rather than building on either: this pass's
own work (reviewing one writer pull request) doesn't share scope with
either of theirs, and all three, including this one, append to
`docs/sprints/pending.md` at the top rather than at a fixed anchor, so
whichever merges first gives the others a one-line keep-both the same
way every prior pass in this chain has. `#332` and `#312`/`#343`
(engineer) also touch `docs/ideas.md`; same shape, same resolution.

**PR #342 opened `CONFLICTING`, resolved as a docs-only append, then
checked against the merge rule (Tier B) and merged.** Not a draft, no
`hold` label, no comment, no review. The diff is
`docs/agents/incidents.md`, `docs/ideas.md`, `docs/voice/ban-list.md`
and one new file, `docs/voice/skills-copy-2026-10-18.md`, so no Tier C
path. It had opened in conflict with PR #339's own install-work entries
at the same two append-only anchors in `incidents.md` and `ideas.md`.
Resolved on the writer's own branch by keeping both sides, oldest
(already-landed) first, and restoring each entry its own trailing
`Status: proposed` line rather than leaving two entries share the one
line `git` had matched as common context, which is the exact defect
#339's own commit described fixing for a different pair of entries in
this file last pass. Verified before pushing: `tools/ledger.py --check`
(0 blocking, at or under baseline) and `tests/test_check_registers.py`
plus `tests/test_board.py` (75 passed). `gh pr checks` reports nothing
defined for this diff, which is correct, not pending: nothing in it
touches `pipeline/`, `prompts/digest.md` or `skills/`. Merged clean at
2026-10-18T01:14:57Z.

**What the PR surfaced, relayed on the board rather than decided here.**
The writer's run found the same unhedged claim — "revised when the
evidence moves" — now live on four surfaces the engineer's install work
shipped a run earlier: the readme, the install page, and both plugin
manifest descriptions. `docs/agents/quality-claims.md` already records
that half of the sentence as `queued`, with no revision mechanism ever
fired, and the writer named this by file and sentence rather than
editing it, since those four surfaces are the engineer's, not hers to
set. Filed on the board as the next item in that lane (not dispatched —
the engineer's own last run already has three open pull requests
against it: #343, #312 and #315).

**Board hygiene: one thirteen-day-stale card closed.** `2da782ae`, "The
distill timeout question doesn't hold, the queue-cap math does," had
sat in Backlog since 2026-10-05 with its own diagnosis already finished
and handed to the engineer in its first comment. Re-checked both
numbers against the code fresh rather than trusting the old note;
neither has changed. Moved to Done. The one open thread inside it, why
the chair's manual run once stopped short of its own budget, was always
the engineer's to trace from Modal's run history and stays open there,
not closed by this move.

**PR #343 (engineer, draft, "the two stalled press drafts get a
disposition each"), named rather than acted on.** Still a draft and
still gaining commits as this pass was written (three so far, the
newest eight minutes old), so it fails Tier B's own first test before
anything else is worth reading. It is the engineer's own answer to the
handoff the prior pass's six-hour run already sent about `#312` and
`#315`, so nothing further is owed from this seat; it waits on that run
to mark itself ready.

**Cap ratio, one seat over the line.** The host-window run that opened
#343 reported 190 of its seat's 200-turn cap (95%) on the board before
the pull request existed, well past the 70% line and the closest any
run has come to the hard cap without hitting it. Named for the ExO's
weekly re-derivation, not acted on here; the run has kept landing real
commits past that point, so it is not itself a cap-out, but it is the
sharpest cap-ratio reading recorded yet. The same window's writer run
(97/225, 43%) is unremarkable by comparison.

**Run health.** `gh run list --limit 30` shows every GitHub Actions run
since the last pass green (`checks`, `deploy-main`); it does not cover
tonight's host-window message runs at all, which report through the
board instead, and the cap-ratio line above is read from there for
exactly that reason.

**Queue gauge, four numbers.** `main` current as of this pass's own
merge (under two minutes old at the time of writing), its newest
`checks.yml` run against it still the `success` from the plugin merge
two passes ago, since a docs-only merge does not trigger a new one. 9
open pull requests, essentially none opened since the last merge (this
pass's own draft is the only one). 7-day conversion 43 merged over 79
opened (0.54), better than the six-hour pass's 0.49 earlier tonight.
Deepest open chain: 1, nothing currently stacked.

**Owed to you, unchanged, not re-litigated here:** the Modal redeploy
ahead of Monday's 09:00 UTC press run, the Polar Merchant-of-Record
account (ADR-30, day 23), the missing launch PR/FAQ on `main`, and your
own open pull requests `#335` and `#332`.

**Merged this run (Tier B, `docs/standards/pm.md` §10), one:** `#342`
(writer).



**Trigger.** Two events this pass answers: the writer's run finishing
(PR #340, already checked and merged by this seat's own #341 moments
earlier) and PR #339 opening (engineer, "the nine skills become an
installable plugin, with an install line a stranger can paste").

**Own last run may still be open, checked first, three found.** #338,
#341 and #337 were all this seat's own open pull requests from earlier
passes tonight, and all three touched only `docs/sprints/pending.md`, a
knowledge surface, so I self-merged all three under tier A rather than
opening a fourth pull request on top of them. Main moved under each of
the first two merges, because other seats' passes were landing at the
same time, so each merge needed its own docs-only append conflict
resolved by hand; `docs/standards/pm.md` §10 point 5 says that kind of
conflict is the PM's to resolve. One of those resolutions (#337's) left
a bare duplicate header with no body behind it, my own mistake in the
script that built the conflict resolution; caught and removed in this
pass's own commit rather than left for the next reader to puzzle over.

**PR #340 needed no further action from this pass.** #341 had already
checked it against the merge rule and merged it; nothing was left open
from that event by the time this pass started.

**PR #339 checked against the merge rule (tier B) and merged.** Not a
draft, no `hold` label, no comment, no review. `mergeable: MERGEABLE`,
`mergeStateStatus: CLEAN` (after one "head branch out of date" retry,
once main moved from the tier A merges above). The one check defined,
"digest request fits the model's budget," read `SUCCESS`.
`gh pr diff --name-only` shows twelve changed files, none under
`prompts/`, `.github/` or `company.yaml`, so no Tier C path. Scoped to
board card `126f4250`, "Give a stranger a one-line way to install a
skill," which the chair's 2026-10-17 handoff set as the product bar.
Moved that card to Done and commented the merge-rule check on it.

**What the PR surfaced, relayed rather than decided.**

- A correction to frontend's board card `a1a2f14a`: the catalog page
  already renders nine skills, because `listSkills()` reads the skills
  directory itself. The "two skills" line the card describes is a
  stale comment in `site/lib/skill-shelves.js`, not rendered copy.
  Relayed as a board comment on that card; the real risk the engineer
  found (shelf assignment by keyword fallback) is named there too, so
  frontend reads it before starting.
- The next engineering priority: board card `c688ef2e`, "Build a way to
  measure the buyer's path," which the engineer's own run note on #339
  called a day of work left out on purpose, not missed. Handed to
  engineer as a board handoff, citing the chair's 2026-10-17 Wednesday
  deadline, since nothing in the site tracks a visit, an install or a
  payment today.
- One new item, carried from #339's own words rather than invented: the
  staged workflow replacement at `.github/workflows-pending/checks.yml`
  would clear nine pinned test exceptions at once and still needs a
  workflow-scoped hand, which is HQ's or a chair's to give, not a
  product seat's.

**Owed to you, unchanged from the last pass, not re-litigated here:**
the Modal redeploy ahead of Monday's 09:00 UTC press run, the Polar
Merchant-of-Record account (ADR-30, now day 23), the missing launch
PR/FAQ on `main`, and the llms.txt candidate #341 already asked you to
rule on.

**Merged this run (tier B, `docs/standards/pm.md` §10), one:** `#339`
(engineer). **Self-merged (tier A), three:** `#338`, `#341`, `#337`
(all this seat's own, all pure `docs/sprints/pending.md`).

## Updated 2026-10-17, ~21:20 UTC (message): PR #336 was merged before this seat could review it, and the check comes back clean

**Scope note.** Message pass, triggered by PR #336
(`chair/mark-no-spine`, title "Mark: remove the central hairline") with
instructions to review it against the merge rule: merge it, or say on
the board what it still needs and hand that to its seat. Not a standup
and not the ceremony; today's standup (below) already ran, and this
seat already has two other open message-pass PRs tonight (named next).

**The PR, checked fresh.** `gh pr view 336` shows it created at
2026-10-17T21:14:53Z and merged at 2026-10-17T21:15:02Z, nine seconds
later, author `alexandrapaiz` — the owner merged it herself as a chair,
a door §21 always leaves open. Nothing was left for this seat to merge.

**Checked against the merge rule anyway, so it is on record.** Diff is
one file, `site/app/components/Mark.jsx`, four insertions and three
deletions: the ten-unit center `<rect>` removed and the file's own
comment rewritten to stop describing a hairline that no longer exists.
No Tier C path (not a charter, not secrets, not a seat's authority).
`deploy-main` ran against the merge commit and came back green, and
Vercel's own status on that commit reads "Deployment has completed."
Grepped `site/` and `public/` fresh for any other reference to the
removed rect's coordinates or the old "fanning from a central hairline"
comment: one hit, the file itself, now updated; `MarkLive.jsx` never
drew the line its own comment already said it never had, so the two
marks match as the PR claims. Nothing still needed, nothing to hand
back to its seat.

**The chair had already posted this on the board** (`done`, 21:17 UTC,
subject "The library mark lost its central hairline on the owner's
instruction", ref PR #336) before this run started. This seat's board
note today only adds the retroactive merge-rule check.

**Other open PM PRs tonight, named per charter §"your own last run may
still be open."** #335 (`alexandria-pm/2026-10-17-message-seats-off-github-review`)
and #332 (`alexandria-pm/2026-10-17-message-sellable-regroom`) are both
open and both also touch this file; all three, including this one, are
append-only at different anchors, so the expected merge order is
whichever lands first. #328 (`alexandria-pm/2026-10-17-message-chair-handoff`)
is also still open and still empty — #335's own body says it closed
#328, but `gh pr view 328` shows it is not; left untouched here since
chasing that down is outside this run's one trigger, and named so the
next run does not have to rediscover it.

## Updated 2026-10-18, ~00:55 UTC (message pass): PR #340 checked against the merge rule and merged, one new owner ruling needed

**Trigger.** The event this pass answers: PR #340 (writer, "the prose
benchmark is scored, and /llms.txt has been telling agents something
untrue for a month"). Instruction: review it against the merge rule, merge
it, or say on the board what it still needs and hand that to its seat.

**Own last run may still be open, checked first.** `#338`
(`alexandria-pm/2026-10-18-message`, this seat's own six-hour pass from
minutes earlier) is still open and also touches `docs/sprints/pending.md`.
Branched from main anyway rather than building on it: that pass's scope
(inbox, failed runs, tier B queue, press deadline) is unrelated to this
one PR's review, and `pending.md`'s entries are prepended rather than
anchored, so whichever of us merges first gives the other a one-line
keep-both, the same docs-only shape `#338` itself already names for
`#337`/`#335`/`#332`. `#332` is also still open and touches `docs/ideas.md`,
which PR #340 touched too; same shape, same resolution, no action needed
here.

**PR #340 checked against the merge rule (`docs/standards/pm.md` §10
Tier B, amended §21) and merged.** Not a draft, no `hold` label, no
comment, no review. `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`.
The one check that gates a `prompts/digest.md` change, "digest request
fits the model's budget," read `SUCCESS`. The diff —
`docs/agents/incidents.md`, `docs/ideas.md`, `docs/voice/ban-list.md`,
three new `docs/voice/` files, and a 12-line addition to
`prompts/digest.md` — carries no Tier C path: `prompts/digest.md` is the
digest pipeline's content prompt, not a `*-agent.md` charter, the exact
distinction `INC-2026-10-09-tier-c-carve-out-misread-for-four-days`
already drew for `prompts/distill.md`, and nothing in the diff touches a
seat's own authority, spend, an account, or a secret. Scoped to what the
seat was asked: the board item "Blind prose benchmark" (writer, urgent,
carried since Oct 5), left in Review rather than Done because the
benchmark's own pick — adopt the rewrite's devices as the house style — is
the owner's, not this seat's. No competing claim found in the board
inbox or on these files. Merged clean at 2026-10-18T00:53:13Z.

**What the PR surfaced that still needs you, one new ask.** The writer's
run opened `/llms.txt` for the first time ever (it is served from a
template literal with no heading, so no copy round had read it) and found
four live defects against your own rulings: the site says the library
"reads" every paper twice, against your 2026-09-25 vocabulary ruling; two
claims `docs/agents/quality-claims.md` names by file and line as
`queued`/`not built` ship unhedged; and a launch date of October 13 is
live on October 18. A corrected candidate is drafted at
`docs/voice/llms-txt-2026-10-18.md`. The file itself,
`site/app/llms.txt/route.js`, is the frontend seat's to set, not the
writer's and not mine. Posted as an `ask` to you on the board with this
seat's recommendation (adopt the candidate as drafted) under the silence
rule (charter §22 / standard §22): if you say nothing in 48 hours, it
proceeds and this seat hands the candidate to frontend. A board item is
filed in Backlog so the work isn't only in a PR number.

**Merged this run (Tier B, `docs/standards/pm.md` §10), one:** `#340`
(writer).


## Updated 2026-10-18, ~00:35 UTC (six-hour pass): two Tier B merges clear the press-diagnosis and voice-gate stacks, and a Modal redeploy only a human can run is the one thing standing between Monday's 09:00 UTC issue and the same miss again

**Reconciliation, per charter §1d.** `docs/decisions.md` still stops at the
same point as last pass and `docs/allhands/` still has nothing newer than
2026-09-18-close. Nothing to strike.

**Owed to you, in order of urgency:**

1. **The weekly app is still serving the image built from `3bbf430` of
   2026-10-04, the same one flagged last pass, and none of the last 40
   commits that touch its files appear in its build.** The code fix (the
   degraded-edition repair) has been on `main` since 2026-10-12. The
   missing half is `modal deploy pipeline/weekly.py`, which needs a human
   hand on the Modal token, and the next scheduled press run is
   **2026-10-19 09:00 UTC, about 32 hours from this pass.** This is the
   same item carried every standup since 2026-09-21, and the reason it is
   flagged urgent on the board this time rather than only listed here is
   that the deadline is now inside one day. I am not asking for a new
   decision, only for the one command this org already has written down
   (`docs/sprints/pending.md`'s own "what the chair runs after this PR
   merges" section, further down this file).
2. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now **22 days**. Still no `POLAR_*` secret name in any
   workflow (checked fresh this pass).
3. **The launch PR/FAQ is still missing from `main`.** `docs/prfaq/`
   holds only `README.md`. A different PR/FAQ, for the skills-sellable
   initiative, is drafted in my own open PR #332 and waits on your merge
   same as the rest of that PR; it does not substitute for the original
   launch document #289 was supposed to carry.

**Merged this run (Tier B, `docs/standards/pm.md` §10), two.** An
engineer PR diagnosing the deploy drift above and adding a monitoring
tool for it, and a writer PR fixing two miscounting voice gates. Both
needed the same kind of conflict resolved first: an append-only collision
in `docs/agents/incidents.md` (and `docs/ideas.md` for the second one)
against a `main` that had moved since each branch was cut. Kept both
sides in each case, oldest first. Full account, including which commits,
in `docs/sprints/dispatch-queue.md`.

**My own open PRs, waiting on you, not touched this run.** Three:
one answering a handoff about the skills-sellable regroom, one checking
a chair-merged workflow PR against the merge rule, one confirming a
chair-merged site PR against the merge rule. The standing rule is that a
PM's own Tier B PR waits for another merger, so none of the three moved.

**Failed runs: none in the last 24 hours.** Fleet green across every
workflow.

**Cap ratio.** The two most recent engineer and writer runs: writer
152/225 turns (67.6%), engineer 114/200 (57%). Both under the 70% line,
nothing to name beyond that.

**Queue gauge, four numbers.** `main` is current as of this pass's own
merge, checks green. 12 open pull requests, 1 opened since the last
merge. 7-day conversion 36 merged over 73 opened (0.49). Deepest open
chain right now: 1 — nothing is currently stacked.

**Dispatch: nothing fired, PM_DISPATCH_ENABLED not present in this run's
environment.** Posted a handoff instead (board, not a workflow dispatch)
to the engineer seat naming its two stalled press-reliability drafts
(#312, still conflicting after 34 hours; #315, still just a run note after
34 hours) and the Monday deadline, asking it to finish or mark ready.
Not a redundant dispatch: the engineer already carries those two PRs plus
a fresh one opened minutes ago on the skill-marketplace item, so this is
information for a seat already working, not a new assignment.

## Updated 2026-10-17, ~14:20 UTC (standup): one docs-only Tier B merge, the deploy drift the chair just cleared came right back, engineer is mid-run on its own stalled stack

**Scope note.** Standup shape (charter §0/§4) — today is Saturday, the
next ceremony is Monday 2026-10-19. This seat's own prior PR from
yesterday's message pass (`alexandria-pm/2026-10-17-message`, #322) is
still open, draft; not touched this run while it may still be live, same
as every standup before it has treated a live message-session PR. Full
account of everything below is in `docs/sprints/dispatch-queue.md`.

**Reconciliation, per charter §1d.** `docs/decisions.md` still stops at
ADR-40 (2026-10-05) and `docs/allhands/` still has nothing newer than
2026-09-18-close. Nothing to strike on that evidence. One item to add
instead: a board note from `asc chair:hq-console` (2026-10-16T14:16 UTC)
says the owner was out for surgery and is back at work as of 2026-10-16 —
the "back after eleven days" the 2026-10-16 standup note already carried.

**Owed to you, three lines, in order of urgency:**

1. **The press has now missed its week again — 2026-W41 has ended with
   the newest issue still 2026-W40 — and the deploy fix the chair applied
   yesterday has already drifted.** `asc chair:hq-console` redeployed
   Alexandria's five pipeline apps on 2026-10-16 at 14:45 UTC ("they had
   run the code of October 4 for twelve days"). Measured fresh this run
   with `tools/delivery_health.py`: `weekly` is already 1.9 days and 34
   undeployed commits behind `origin/main` again. The reachable half of
   every fix keeps landing in `main`; the unreachable half is a `modal
   deploy` only a chair or the owner can run, and it needs to happen on a
   cadence, not as a one-time favor, or this line will read the same way
   every standup. Separately, `.github/workflows-pending/press-watch.yml`
   (the second reader that would catch a Monday failure within hours
   instead of within days) is still unapplied — it needs one `git mv`
   from a hand that can write `.github/workflows/`. Dated 2026-09-21,
   carried every standup since.
2. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now **21 days**. No `POLAR_*` secret names found anywhere
   in the workflows this run (checked fresh). The integration has been
   built and waiting since #285; the account itself is still the one step
   no seat can take for you.
3. **The launch PR/FAQ is confirmed missing from `main`, not just
   unclear.** `docs/prfaq/` holds only `README.md` (checked directly this
   run). `#289` shows merged on 2026-10-14, so either a later commit
   dropped the file or the merge never carried it the way the PR's own
   history suggests. If the go/no-go already happened by another route,
   say so next pass and this line strikes; otherwise it is worth
   reconstructing before the next ceremony grades the launch against a
   press release nobody can read.

**Merged this run (Tier B, `docs/standards/pm.md` §10), one:** `#321`
(writer). Full account, including the docs-only conflict resolved by
keeping both sides, in `docs/sprints/dispatch-queue.md`.

**Failed runs, none in 24h, per charter §11.7/§1f.** Nothing to triage.

**Cap ratio:** market run `38922861774`, 138/160 turns (86.3%), above the
70% line, not a cap-out. Named for the ExO's weekly re-derivation, not
acted on here.

**Queue gauge, four numbers:** `main` effectively current (this run's own
merge), checks green; 5 open PRs, 0 opened since the last merge; 7-day
conversion 35/60 (0.58); deepest open chain 1 (no stack currently open —
#315 names itself a sibling of #312, not a supersession). No 48-hour
stall, so this is not the standup's headline today.

**Dispatch: nothing fired.** `PM_DISPATCH_ENABLED` confirmed `true` from
the job's own environment. The one seat with an observed trigger
(engineer: three open PRs on one scope, `#312`/`#315`/`#324`, none
merged) already had a run in progress at check time
(`39039566505`, started 14:09:47 UTC) — dispatching into a live run would
race it, so nothing was fired. Ceilings unchanged: 0 of 3 used today.

**Still open, named rather than acted on:** `#322` (this seat's own
message-session PR, live or abandoned, not touched), `#312`/`#315`
(engineer, both drafts, the two halves of the press-reliability fix,
~24h old, engineer mid-run), `#324` (engineer, draft, opened by the run
in progress as this standup was written), `#272` (exo, Tier C, touches
three charters, conflicting, 6 days old).

**Board.** Inbox clean for `pm`/`alexandria` — nothing addressed here sat
unanswered; the rest is broadcast traffic from sibling PM seats and HQ.
Moved two cards to match reality: the Left-Behind Index page to Done
(PR #306), and the press-send-gap item to In progress (three real PRs
against it now). Posted this pass as a `note`. The sprint object still
reads `sprint-2026-10-05` — the repo's own newest sprint file is
`sprint-2026-10-12`, and even that has no retrospective yet — a gap now
six-plus ceremonies running, named again for Monday rather than forced
here.

**Linear trial (charter §1e2): not re-checked this run.** No evidence
either way surfaced; carried from the last confirmed sighting.

## Updated 2026-10-15, ~15:55 UTC (standup): the dispatch mechanism is actually fixed and confirmed by a real dispatch, PR #60 merges after 25 days, delivery is still the headline

**Scope note.** Standup shape (charter §0/§4), not the ceremony — the
next one is Monday 2026-10-19. This seat's own prior PR from today's
earlier six-hour pass (`alexandria-pm/2026-10-15-message`, #302) is
still open, draft, placeholder-only; not touched this run while it may
still be live, same as every standup before it has treated a live
message-session PR. Full account of everything below is in
`docs/sprints/dispatch-queue.md`.

**Reconciliation, per charter §1d.** `docs/decisions.md` still stops at
ADR-40 (2026-10-05) and `docs/allhands/` still has nothing newer than
2026-09-18-close. Nothing to strike on that evidence.

**The headline: the dispatch actor-gate is fixed, and PR #60 is finally
merged.** `#298` (exo-centralizer) landed `allowed_bots:
"github-actions[bot]"` on every seat workflow, which is the fix
`INC-2026-09-24-dispatch-403`'s amended entry has been waiting on since
2026-10-14. Merged it first, then the once-blocked `#60` (the pre-send
quality checklist, open since 2026-09-20, 25 days) merged clean right
behind it — the engineer's rebase yesterday removed the `prompts/`
file that made every prior standup call it Tier C, and nothing else
about it was ever actually blocked. Full account, including the one
citation gap found (ADR-049, cited in #298's own comment, not yet
vendored into this repo's `docs/decisions.md`), in the dispatch-queue
file.

**Owed to you, three lines, in order of urgency (unchanged in kind,
delivery got worse not better):**

1. **The press has now missed two consecutive weeks.** 2026-W40 is
   still the newest issue and 2026-W41 has already ended.
   `claims` hasn't moved in 8 days, 2,308 papers are waiting in
   `distill_queue`, and this run found a sharper cause than prior
   standups had: the account actually driving distill right now is the
   Groq fallback, not Moonshot, and ADR-39's own 250,000-character
   window is the one thing that fallback's 8,000-token-a-minute limit
   cannot carry. The reachable half of every past fix is in `main`; the
   unreachable half is still a `modal deploy` only you or the chair can
   run — `interpret` is 1.9 days and `triage` 2.8 days behind `main`
   right now (14 and 16 undeployed commits). Dated 2026-09-21, carried
   every standup since.
2. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now **20 days**. The engineer has a second PR in flight
   against this today (#301, currently conflicting against product
   code, not this seat's to text-resolve); the account itself is still
   the one step no seat can take for you.
3. **The launch PR/FAQ (`docs/prfaq/launch-2026-10-13.md`) — status
   unclear, worth your eyes rather than this seat's guess.** `#289`
   shows `MERGED` (2026-10-14T16:13:35Z), but the file is not present on
   `main` now (`docs/prfaq/` holds only `README.md`), and this run did
   not trace why — a later commit may have moved or removed it, or the
   merge may not have carried it the way the PR's own history suggests.
   Launch was dated 2026-10-13, two days ago; if the go/no-go already
   happened by another route, say so next pass and this line strikes.

**Merged this run (Tier B, `docs/standards/pm.md` §10), four:** `#298`,
`#60`, `#299`, `#300`. `#301` (engineer, product code) stays open and
conflicting — not this seat's to text-resolve. Full account, including
the two docs-only conflicts resolved by keeping both sides, in
`docs/sprints/dispatch-queue.md`.

**Failed runs, both triaged, per charter §11.7/§1f:** this seat's own
2026-10-14 standup (`38592352927`) finished 205 turns clean and shipped
nothing at all — new incident filed,
`INC-2026-10-14-the-standup-ran-205-turns-and-shipped-nothing`, with
this file's own growing length named as a likely contributing cause and
a dated-archive split proposed for the next ceremony. The frontend
dispatch that died at the actor gate (`38594124029`) was reran once;
the rerun hit the identical error, because GitHub's rerun replays the
workflow file pinned to the original trigger rather than `main`'s
current version, so `#298`'s fix was never actually in scope for it.

**Cap ratio:** engineer run `38592441554`, 157/200 turns (78.5%), above
the 70% line, not a cap-out. Named for the ExO's weekly re-derivation,
not acted on here.

**Queue gauge, four numbers (new standing line per the 2026-10-04
ruling):** `main` effectively current (this run's own merges), checks
green; 8 open PRs, 0 opened since the last merge; 7-day conversion
27/56 (0.48); deepest open chain 3 (`#292`→`#294`→`#301`, engineer).
No 48-hour stall, so this is not the standup's headline today.

**Dispatch: one fired, and it's the first one to actually reach the
model in the 21 days since `INC-2026-09-24-dispatch-403` was filed.**
Frontend, sprint item 4 (the Left-Behind Index), a fresh
`workflow_dispatch` rather than a second rerun — every §11.4 hard stop
cleared (frontend's last PR merged this run, no human dispatch in the
last two hours, 0-of-3 ceiling before this one, instruction carries only
evidence already on record). Confirmed past the actor gate: the
`claude-code-action` step stayed `in_progress` well past the ~5 seconds
the gate-rejection takes to kill a run, the first time that has ever
happened. Run: https://github.com/alexandrapaiz/alexandria/actions/runs/38764121612.
Outcome (whether it ships the page) not yet known; full command logged
under "Dispatched by the PM" in `docs/sprints/dispatch-queue.md`.
Ceilings after this run: 1 of 3 used today. No other seat has an
observed trigger.

**Still open, named rather than acted on:** `#303` (engineer, draft, a
second run in progress as this standup was written), `#302` (this
seat's own six-hour-pass PR, live or abandoned, not touched), `#297`
(engineer, draft, a message-triggered rebase of the quality gate that
`#60` already landed by a different path — likely redundant now, named
for the engineer's own next run to confirm and close rather than closed
here on a guess), `#272` (exo, Tier C, touches three charters,
conflicting), `#205` (finance, draft, dormant seat), `#203` (okr,
draft).

**Board.** Inbox clean for `pm`/`alexandria` (two broadcast notes from
a sibling company's PM, not addressed here). Sprint object still reads
`sprint-2026-10-05`, the same ceremony-sized gap named since
2026-10-10, now five ceremonies running. Two items from frontend's
2026-10-14 visual run sit in Backlog untouched (masthead-width
inconsistency, verdict-queue density) — design-system calls for the
owner, not this standup's to move.

**Linear trial (charter §1e2): not re-checked this run.** No evidence
either way surfaced; carried from the last confirmed sighting.

## Updated 2026-10-14, ~16:10 UTC (standup): last Monday's ceremony finally lands, the 18-day dispatch block is half-fixed, three Tier B merges

**Scope note.** Standup shape (charter §0/§4), not the ceremony — the
next one is Monday 2026-10-19. But this run also closed a four-day gap
that was not a standup's to leave open: `sprint-2026-10-12.md` (the
2026-10-12 Monday ceremony: closed retro on sprint-2026-10-05, groomed
ledger, the new sprint) was sitting on an open, unmerged pull request
(#281, then carried into #289) the whole time, because the only file in
that chain outside a knowledge surface was the launch PR/FAQ
(`docs/prfaq/launch-2026-10-13.md`), and Tier A's own rule holds the
*whole* pull request for the owner when any file in it is not a
knowledge surface. Split the PR/FAQ into its own pull request (#289,
unchanged, waiting on your go/no-go) and self-merged everything else as
#295, so `main` has had a current sprint file since before today's
standup even started, not since four days ago when it should have.

**Reconciliation, per charter §1d.** `docs/decisions.md` still stops at
ADR-40 (2026-10-05) and `docs/allhands/` still has nothing newer than
2026-09-18-close. Nothing to strike on that evidence.

**The headline: the dispatch mechanism moved for the first time in
eighteen days, and immediately hit a second gate.**
`INC-2026-09-24-dispatch-403` turned out to be exactly what
`docs/standards/pm.md` §11.5 already names: the Claude Code action
overwrites the ambient `GH_TOKEN`/`GITHUB_TOKEN` with its own
installation token, and the job's real token — the one `permissions:
actions: write` governs — survives only as `DEFAULT_WORKFLOW_TOKEN`.
Prefixing the dispatch call with it (`GH_TOKEN="$DEFAULT_WORKFLOW_TOKEN"
gh workflow run agent-frontend.yml ...`) created a real run
(38594124029) for the first time since the incident was filed. That run
then died in 4 seconds, before the model read its prompt:
`claude-code-action` refuses a bot-triggered actor
(`github-actions[bot]`, what `DEFAULT_WORKFLOW_TOKEN` is attributed to)
unless the workflow's `allowed_bots` names it. Both fixes are
`.github/workflows/` changes, which is HQ's surface in every product
repo, not this seat's or the frontend seat's. Handed off to
`alexandra-systems/exo-centralizer` on the board this run, with the run
URL and both fixes named. Full account: the amended
`INC-2026-09-24-dispatch-403` entry in `docs/agents/incidents.md`, dated
today.

**Owed to you, four lines, in order of urgency:**

1. **The launch PR/FAQ go/no-go — new, and it is the only thing left
   blocking #289.** `docs/prfaq/launch-2026-10-13.md`, drafted at the
   2026-10-12 ceremony, one page plus the FAQ, per standard §2c. Your
   merge of #289 is the go decision; everything else that PR carried has
   already landed via #295.
2. **The press hasn't sent since 2026-W40, four weeks running, and the
   pipeline is now 7 days stalled with 2,264 papers waiting.** Unchanged
   in kind from the last three standups; `tools/delivery_health.py` run
   live this standup. The reachable half of the fix is in `main`
   (`INC-2026-10-12-the-deploy-ladder-refuses-the-fix-for-the-outage-it-
   is-in`); the unreachable half is a `modal deploy` only you or the
   chair can run, and the deploy surface now also reports the live site
   is 1.8 days behind `main` (16 undeployed commits). Dated 2026-09-21,
   carried every standup since.
3. **Merge PR #60**, the pre-send quality checklist — **25 days** open.
   `CONFLICTING` regardless of tier (confirmed again this run), so it is
   blocked either way and this seat cannot resolve it (the conflicting
   files are product code — `db/schema.sql`, `mcp/server.py`,
   `pipeline/budget.py`, `pipeline/weekly.py` — not the docs-only kind
   §10 rule 5 lets this seat fix). One correction to four standups' own
   label, found while re-examining `prompts/digest.md` for #291 this
   run: `prompts/daily.md`, the file that made this PR "Tier C" in every
   prior report, is the same kind of file as `digest.md` — a content
   prompt, not a seat charter (`prompts/<role>-agent.md` is the Tier C
   boundary per standard §16) — so the conflict, not the tier, is what's
   actually blocking it. Handed off to the engineer to rebase, since
   that is rule 5's own instruction for a non-docs conflict. Dated
   2026-09-20.
4. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now **19 days**. #285 shipped the full integration eight
   days ago; this is the one remaining step. Dated 2026-09-26.

**Merged this run (Tier B, `docs/standards/pm.md` §10), three:**
- **#288** (engineer, institution backfill — sprint-2026-10-12 item 3) —
  clean, no Tier C path.
- **#290** (skill, harness-engineering v5 + agent-memory-selection) —
  opened `CONFLICTING` against #288 in `docs/agents/incidents.md` and
  `docs/ideas.md` (both append-only, same anchor). Docs-only, resolved
  per §10 rule 5: merged `main` into the branch, kept both sides, pushed,
  merged clean.
- **#291** (writer, the attribution-gate fix + two ban-list entries) —
  touches `prompts/digest.md`, re-examined this run against standard
  §16's own vocabulary (a charter is `prompts/<role>-agent.md`; this
  isn't one) rather than against the label a prior standup gave a
  different file. Opened `CONFLICTING` against the two merges above in
  the same two append-only files; resolved the same way.

**Also split and self-merged under Tier A, #295 (this run's own PR):**
the 2026-10-12 ceremony's sprint, retro and grooming, `org-chart.md`,
and today's `pending.md`/`dispatch-queue.md` — see the headline above.

**Not merged, named rather than acted on:** #272 (exo, Tier C — touches
three agent charters including this seat's own, also `CONFLICTING`),
#205 (finance, draft, dormant seat), #203 (okr, draft), #294 (engineer,
draft, sprint item 5, a run in progress), #293 (a different PM-surface
pull request from the owner's own window session, `alexandria-pm/2026-
10-14-message`, open since 12:27 UTC, a draft with only a placeholder
body at last check — not touched while it may still be live), #289 (the
launch PR/FAQ, now trimmed to that one file, waiting on you per item 1
above).

**One dispatch fired, the first ever to actually create a run, and it
failed — see the headline.** Frontend, sprint item 4 (the Left-Behind
Index), logged in full in `docs/sprints/dispatch-queue.md`'s "Dispatched
by the PM" section with the run URL.

**Board.** Commented on the frontend card (`03029cad`) naming the
dispatch and its failure; left it in Backlog since nothing actually
started. Did not touch the stale sprint object (still reads
`sprint-2026-10-05`) — same ceremony-sized item the 2026-10-10 standup
already flagged, now four ceremonies running.

## Updated 2026-10-13, ~18:35 UTC (standup): launch day itself still shows the gap, two Tier B merges, one dispatch attempted and refused

**Scope note.** Standup shape (charter §0/§4), not the ceremony. Yesterday's
ceremony (#281) never merged; built on it this run rather than branching
blind into the same two files, and it supersedes it as #289. Full account
in `docs/sprints/dispatch-queue.md`.

**Reconciliation, per charter §1d.** `docs/decisions.md` still stops at
ADR-40 (2026-10-05) and `docs/allhands/` still has nothing newer than
2026-09-18-close. Nothing to strike on that evidence.

**The three items below carry forward from yesterday, re-checked against
today's own evidence rather than assumed unchanged:**

1. **Today's press send (launch day itself) is still missing, and it got
   worse, not better.** `python3 tools/delivery_health.py`, run this
   standup against a live `DATABASE_URL`: press and site both `FAILING`,
   2026-W41 missing; pipeline `FAILING`, claims stalled 6 days (was 5
   yesterday), 2223 papers waiting (was 2173). Yesterday's sprint read
   item 1 as closed via #282 — that PR shipped the degraded-path
   mechanism, not a resend, and the mechanism cannot run because no agent
   token holds `modal deploy` (`INC-2026-10-12-the-deploy-ladder-refuses-
   the-fix-for-the-outage-it-is-in`, already filed). The reachable half of
   the fix is in `main`; the unreachable half is a `modal deploy` only you
   or the chair can run. Dated 2026-10-13, carried from 2026-10-12.
2. **Merge PR #60**, the pre-send quality checklist — **23 days** open,
   Tier C (`prompts/daily.md`), conflicting, unchanged for the fourth
   consecutive standup/ceremony. Only your merge opens it. Dated
   2026-09-20.
3. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now **17 days**. #285 merged yesterday and built the full
   checkout/webhook integration against Polar's documented API, so this
   really is the one remaining step now: create the account, paste the
   `POLAR_*` secrets, and the spine goes live with no further engineer
   day needed. Dated 2026-09-26.

**Merged this run (Tier B, §10).** #283 (writer, digest/voice quality bar)
clean; #284 (research, claim-graph precision brief) had a docs-only append
conflict with #283 in `docs/agents/incidents.md`, resolved by keeping both
entries (§10 rule 5 permits this). `main`'s next `checks.yml` run came back
green after both.

**One dispatch attempted, refused at the API, not by rule.** Frontend
(sprint item 4, the Left-Behind Index, carried two sprints, no frontend PR
ever attempted it) fired clean against every hard stop and `PM_DISPATCH_
ENABLED=true`, and GitHub returned `403`, the same `INC-2026-09-24-
dispatch-403` every PM pass has hit for 18+ days. Exact command in
`docs/sprints/dispatch-queue.md` for a human to run.

**Still open, named rather than acted on:** #272 (exo, Tier C — touches
three agent charters including this seat's own, also conflicting), #205
(finance, draft, dormant seat), #203 (okr, draft), #288 (engineer, sprint
item 3, a run in progress as this standup was written — not touched while
its run is live), #287 (a different PM-surface pull request from a
different invocation path, `alexandria-pm/2026-10-13-message-second-pass`,
six hours stale at last check; not enough visibility into that system to
judge it from here, named rather than guessed at).

**Board.** Moved the one card with an obvious match to this run's merges
(`59fcc1f4`, the writer's quality-bar item) to Done with the PR link.
Commented on the frontend card (`03029cad`) naming the dispatch attempt.
Did not touch the stale sprint object (still reads `sprint-2026-10-05`,
"The press runs itself") — that is the full board reconciliation the
2026-10-10 standup already flagged as ceremony-sized, and yesterday's
ceremony's own claimed rename does not appear to have taken; worth the
next ceremony's attention rather than a second attempt here.

## Updated 2026-10-12, Monday ceremony: today's press send is the headline, three Tier B merges, the ledger groomed back to 2026-09-28

**Reconciliation first, per charter §1d.** Read `docs/decisions.md` (stops
at ADR-40, 2026-10-05, nothing newer) and `docs/allhands/` (nothing newer
than 2026-09-18-close) back to the last ceremony. Nothing to strike: no
new ADR or ruling since the 2026-10-10 standup resolved anything this
tracker was still carrying as open.

**Owed to you, three lines, in order of urgency:**

1. **Today's press send may have silently failed.** `pipeline/weekly.py`'s
   09:00 UTC cron fired (confirmed by its own runtime fingerprint) but
   produced no new `digests` row — the receipt and `/library` both still
   show last Monday's `2026-W40` issue. A PM dispatch to the engineer to
   diagnose and, if safe, send it now was attempted and refused with
   `HTTP 403` (repeat of `INC-2026-09-24-dispatch-403`). The exact command
   is in `docs/sprints/dispatch-queue.md` for you or the chair to run by
   hand. Launch is dated 2026-10-13 — tomorrow. Dated 2026-10-12.
2. **Merge PR #60**, the pre-send quality checklist — **22 days** open,
   Tier C (`prompts/daily.md`), conflicting, unchanged for the third
   consecutive ceremony. Only your merge opens it. Dated 2026-09-20.
3. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, now **16 days**. This ceremony's new sprint (item 2) has
   the engineer building the full checkout/webhook integration against
   Polar's documented API regardless, so the account and `POLAR_*`
   secrets are the one remaining step once that PR lands — not a new
   blocker, the same one, closer to done. Dated 2026-09-26.

**Merged this run (Tier B, `docs/standards/pm.md` §10/§21).** Full account
of each in `docs/sprints/dispatch-queue.md`.

- **#277** — re-vendor `docs/standards/pm.md` to HQ `2c0cb30`. Merged.
  **#280**, a duplicate of the same commit, closed rather than merged
  twice.
- **#278** — raise the writer's turn cap 150→225. Merged. Worth your eyes:
  an earlier PM pass today read this exact PR as outside this seat's
  merge authority (a workflow file) and this run read the standard the
  other way and merged it; the standard's own §10 and §15 disagree with
  each other about whether a product seat may touch `.github/workflows`
  at all. Flagged for the ExO, not resolved here.
- **#275** — the engineer's free-tier pacing fix (the cause of the
  five-day claims stall). Merged.

**Left open, each named rather than acted on.** #273 (writer, conflicting,
Tier C), #272 (exo, touches three charters, Tier C), #279 (this seat's
own prior-pass PR, waits for the owner or HQ's PM per Tier B condition 1
— though both items it covers are already independently resolved above),
#205 (finance, draft, dormant), #203 (okr, draft).

**Ledger grooming (`docs/ideas.md`), full account in this week's PR
description.** Groomed the 9 `accepted`-not-flagged-built entries (5 read
as already built in the tree, named for the owner or building seat to
flip; 2 genuinely open and pulled into this week's sprint; 1 correctly
scoped future work; 1 already correctly split). Added dated notes on 6
stale/superseded entries, including a six-filing masthead cluster (the
code defect is fixed, only a regression-test gap remains live) and one
entry whose premise does not hold (institutions data it assumes exists).
96 `proposed` entries dated 2026-09-22 through 2026-09-28 now cross the
two-week mark with no verdict; full list in this week's PR description
under "Awaiting your verdict." The prior ceremony's own 92-entry list
(dated ≤2026-09-21) was never actually written into its PR body despite
saying it would be — treat all 92 as still outstanding too, since nothing
since has resolved them.

**The board was unstable this run** (one read returned a different,
stale sprint record than four subsequent reads; one write failed with
"the board's database is unreachable"). Renamed the sprint it actually
serves to this week's goal, added three cards, moved one stale card to
Done. The full 36-card reconciliation the 2026-10-10 standup named as
ceremony-sized was not attempted against an unstable backend — carried
rather than forced. See `docs/sprints/dispatch-queue.md` for the full
account.

**Run health.** One failure in 24h, already classified as a tripwire
false alarm (the same branch's later pushes went green and merged). The
writer's 2026-10-11 19:46 UTC run finished at 127/150 turns (84.7%, over
the cap-ratio line); the raise merged this run resolves it going forward.

## Updated 2026-10-10, ~16:10 UTC (standup): two Tier B merges, two abandoned drafts closed, nothing failed that wasn't already filed

**Scope note.** Standup shape (charter §0/§4), not the ceremony — full
reconciliation against `docs/decisions.md`/the board is Monday
2026-10-12's job. This run's own open pull request
(`alexandria-pm/2026-10-10-message-pass2`, #264) was already open from a
six-hour pass earlier today; continued on that branch rather than
opening a sixth link in today's chain. Full account of everything below
is in `docs/sprints/dispatch-queue.md`'s matching section.

**Merged under Tier B this run:** #263 (engineer, the delivery receipt's
queue-depth read) and #237 (skill, the agent-containment retrofit, open
since 2026-10-06 — unblocked by resolving a docs-only append conflict in
`docs/agents/incidents.md`/`docs/ideas.md`). `main`'s next `checks.yml`
run came back green after both.

**Closed as abandoned ship-first placeholders, no real work in either:**
#258 (engineer) and #255 (market), both ~23 hours old and holding
nothing but their stub files. Reversible; said so in each closing
comment.

**Still open, named rather than acted on:** #260 (writer, draft, green,
not this seat's to force ready), #203 (okr, 5-day-old draft, substantial
but still a draft), #205 (finance, 5-day-old draft, conflicting, core
numbers never filled in, finance is dormant so nobody to dispatch), #60
(engineer, 20 days, Tier C + conflicting, unchanged), #265 (engineer, a
live schedule-triggered run's own new PR, opened mid-standup — not
touched while its run is in flight).

**Owed to you, one line each, all unchanged from before this run:**
1. **The `sql_query` scope decision** — confirmed still unfixed this run
   by reading `mcp/server.py` directly (no table allowlist). 9 days open.
2. **Merge PR #60** — the pre-send quality checklist, 20 days open,
   Tier C, conflicting, only your merge opens it.
3. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, not re-checked for live keys this run.

**Found, not fixed: the board (`board.libraryofalexandria.dev`) is
materially stale** — its sprint record and its 20 cards are three weeks
behind this repo's actual sprint file and don't reflect either merge
this run made or the already-shipped waitlist/unsubscribe work. Named
here as a ceremony-sized item for Monday rather than attempted as a
standup-sized fix.

**No dispatch fired or proposed.** `PM_DISPATCH_ENABLED` confirmed
`true` directly from this job's environment, org not in synchronous
mode, and nothing in `docs/standards/pm.md` §11.3's criteria table had
an observed trigger this run — the one live defect (the claims stall)
already has #265's run in flight against it. See dispatch-queue.md.

## Updated 2026-10-09, ~20:55 UTC (message run): the writer's cap hit, triaged

**Scope note.** This update is scoped to the one trigger this run was
given — the writer-agent's failed run — rather than a full
reconciliation sweep of this whole file. Entries below this one were
not re-checked against `docs/decisions.md` or the board this run; treat
their dates as last-verified, not current.

**The writer-agent's scheduled run (`37986599276`, 20:22-20:45 UTC)
failed, and here is what it cost and what it owes.** Full account filed
as `INC-2026-10-09-the-writer-hit-the-cap-its-own-raise-queued-five-days-earlier`
in `docs/agents/incidents.md`. In short: the run died at turn 151 against
its own `--max-turns 150`, hard starvation by `turn-caps.md`'s own test.
Six files it had already pushed survived in its draft PR, #260
(`writer/2026-10-09`). Whatever it was still editing on `docs/ideas.md`,
`docs/voice/ban-list.md` and `docs/voice/reviews/2026-10-09.md` beyond
that push did not, because the sandbox was dirty and never got a second
push before teardown.

1. **Owner or chair: apply `pending-workflow-changes.md` item 14, writer's
   line at minimum.** Queued 2026-10-04, never applied, and it is the
   named cause of tonight's loss — the writer's peak was already measured
   at 136 (91% of 150) five days ago with the raise to 300 sitting as a
   one-line diff to `agent-writer.yml`. The other six seats in that item
   (skill, engineer, market, research, security, exo) are at the same
   unapplied distance from the same failure; this is the first of the
   seven to actually hit it, not the only one at risk.
2. **PR #260 (writer, draft) needs a human or a follow-up writer run,
   not a merge as-is.** It holds real content but is missing whatever
   increment the capped-out run was still composing. Left untouched by
   this seat deliberately — judging editorial completeness is not this
   seat's lane. Proposed in `dispatch-queue.md`, not fired (see below).
3. **`PM_DISPATCH_ENABLED` could not be confirmed this run.**
   `gh variable list` returned `HTTP 403` on this token, the same gap
   prior passes hit reading it directly. Treated as not active; nothing
   in this run's queue was fired.

## Updated 2026-10-06, ~17:30 UTC (standup): reconciliation, red `main`'s stuck fix, one dispatch

**Reconciliation first, per charter §1d.** Read `docs/decisions.md` and
the board back to the last pass. One item struck:

- ~~Item: "The merge-authority grant is unconfirmed" (board item
  `00863731`, and this tracker's own 2026-10-05 04:27 and 05:32
  entries)~~ — **resolved.** `docs/standards/pm.md` §21 ("Merges belong
  to the PMs and the chairs, not the owner") is now vendored into this
  repo's own copy, merged as PR #230 (commit `c696875`, 2026-10-06
  00:32:09 UTC). That is the confirmation this item was waiting on; the
  board item is moved to Done with that citation.

**New, top of this run: `main` is red, and the fix is stuck on a Tier C
file.** PR #233 (engineer) measured `main` directly — 19 pytest
failures, all traceable to `skills/agent-containment/SKILL.md` still
carrying an empty `claims` list — and its own branch has none of them.
The PR is otherwise clean, green and mergeable, but its diff touches
`prompts/distill.md` and `prompts/distill-practices.md`, which Tier C
reserves for the owner. This seat cannot merge it under Tier B for that
reason alone. Full account in `docs/sprints/dispatch-queue.md`.

**PR #60**, the pre-send quality checklist, is now **16 days** open,
unchanged status: Tier C, conflicting, waiting only on the owner.

**The Polar Merchant-of-Record account (ADR-30)** remains overdue
since 2026-09-26; no live keys visible in the tree as of this run.

**This seat's own chain.** PR #235 is still the tenth pull request in
today's single PM supersession chain (named in full in the dispatch
queue file). This run continued that branch rather than opening an
eleventh, and posted an `ask` to `alexandra-systems` `pm` on the board
to merge it once ready, the same route `epitome`'s PM used successfully
earlier today for the identical problem (a product PM's own Tier B
pull request has no self-merge path).

**One dispatch proposed, not fired.** Writer, to build on the open
branch for PR #229 and pick up PR #233's fix for the shared test
failure. This session's token got `HTTP 403` trying to fire it (no
`actions: write`), so the command is queued in
`docs/sprints/dispatch-queue.md` for the owner or a chair to run
directly.

## Updated 2026-10-05, ~23:45 UTC (message session): the two prose items move to the writer, reading enjoyability heads the sprint

**Trigger.** A board inbox item from the chair (`388df6c3`, "Reading
enjoyability: the prose is not nailed down, and it is urgent"), citing
the owner's read of the week forty issue this morning. The chair had
already handed the writer the work directly: benchmark the market,
rewrite this week's first section side by side with the original, and
put the bar into the digest prompt and the voice check before the next
send. What the chair handed this seat was narrower: move the two stuck
items off the engineer and onto the writer, so nothing on this keeps
waiting on the owner, and hold the writer to a side-by-side she can
judge within a day.

**Reassigned, both from engineer to writer, both posted to the board
under the writer seat (`7e1841c0`, `59fcc1f4`):**

1. **The blind prose benchmark** (sprint 2026-09-21 item 2). The
   engineer-buildable half — the rubric and the mechanics in
   `docs/evals/2026-09-21-prose-benchmark.md` — stays filed as
   evidence. What was stuck was the human half: scoring it blind
   against the market never got scheduled, and the owner's directive
   this morning widens the comparison set past TLDR AI alone to
   Import AI, The Batch and the Morning Brew register. The writer now
   owns producing the side-by-side itself, not waiting on a scoring
   session to be arranged.
2. **The quality tier held pre-send** (sprint 2026-09-21 item 4). PR
   #60 has been open fifteen days, waiting only on the owner's merge
   per every pending update since 2026-09-28. The writer now puts the
   agreed bar straight into the digest prompt and the voice check,
   which does not require that merge. PR #60's own fate (it may still
   carry engineering-side checks, citation counts and evidence
   density, that this does not replace) is not decided here — flagged
   for the owner and engineer to reconcile, per the register-check
   rule against guessing a judgment nobody has made.

**Reprioritized.** Reading enjoyability is now the sprint's head item,
ahead of main's red build and the subscriber-wiring work, per the
owner's own words this morning: a correct newsletter nobody enjoys
does not keep a reader. This does not change sprint-2026-10-05's
numbered backlog itself (open in the superseded #225, now carried
forward in this PR) — the voice work sits above it as a standing
priority until the owner has judged the side-by-side, and the next
ceremony should make that order literal in the sprint file.

**Done means the owner has picked a version and the next issue was
held to it.** That verdict has not landed yet. Posted on the board
(`388df6c3`) that whoever lands the side-by-side should say so there
first, and that this seat is watching for it at the next run if
nobody has by then.

**Ledger.** `docs/ideas.md`'s prose-benchmark entry (2026-09-18) carries
a dated grooming note recording this reassignment; it has no sibling
entry for the quality tier, which was never a ledger item.

## Updated 2026-10-05 (message run): the distill job's timeout and the reading queue's cap, triaged for the engineer

A handoff from `asc/chair:alexandria`. A manual `distill` run tonight was
cancelled after five papers and about nineteen minutes, with the app
reported stopped, so the chair asked whether the twenty-paper run the
job advertises fits inside its own timeout, and handed both that
question and the reading queue's drain rate to this seat to triage and
pass to the engineer, since both are runtime machinery the chair does
not edit.

**Checked against the code directly, so the engineer starts from facts
rather than the chair's estimate.**

1. **The scheduled function already has a 90-minute timeout, and it is
   sized for twenty papers on purpose.** `distill()` in
   `pipeline/distill.py` runs on `schedule=modal.Cron("0 15 * * *")`
   (line 993) with `timeout=5400` (line 998), and its own comment at
   lines 984-987 does the arithmetic: "20 papers at 3 requests a minute
   is about 20 minutes of calls, and the rest is the embedding sweep."
   `MAX_PAPERS_PER_RUN = 20` (line 234) is the batch the schedule caps
   itself at. The three other timeouts the chair saw in the same file
   (300s/`preflight`, 900s/`rehearse`, 3600s/`bake_off`) all sit on
   CLI-triggered gates, not on anything that runs on a schedule.
2. **That leaves the manual run's failure unexplained, not explained
   away.** Five papers in nineteen minutes is about 3.8 minutes a
   paper, in line with the chair's own three-to-four-minute estimate,
   and twenty papers at that rate is 60-80 minutes, inside the 90-minute
   window on paper. So something stopped the run well short of its own
   timeout. That is the engineer's question to answer from the actual
   Modal run history (a stop command, an error, a rate limit, or a
   second, shorter timeout this seat did not find), not something this
   seat can diagnose from the repository alone.
3. **The reading queue reader's cap checks out exactly against the
   chair's count.** `MAX_PER_RUN = 6` in `pipeline/reading_queue.py`
   (line 52), and `docs/research/reading-queue.md` holds 94 unchecked
   items right now. 94 at 6 a run is 16 runs, matching the chair's
   figure. Whether that cap should move, given the owner's request to
   clear the queue tonight, is the engineer's call under its own
   charter, not a build this seat can schedule.
4. **One small, separate bug found while reading the same file.**
   `pipeline/reading_queue.py`'s own module docstring (lines 15-17)
   says "distill's `max_papers` is 30." The real constant
   (`pipeline/distill.py:234`) is 20. Worth fixing in the same pass so
   the comment stops contradicting the code next to it.

**What this seat is handing the engineer, not deciding itself:** confirm
why the manual run stopped at five papers against a 90-minute budget
that should have covered twenty, size the schedule's timeout and batch
if that investigation says it should change, decide whether the reading
queue's six-a-run cap should move tonight, and fix the stale "30" in
the docstring. None of this needs the owner's word first; it is sizing
and debugging inside the engineer's own lane. Replied in first person on
the board, item to follow.

## Updated 2026-10-05 (Monday ceremony, in progress — placeholder commit to ship the draft PR first, full reconciliation follows in this same PR)

## Updated 2026-10-05, ~19:30 UTC (scheduled ceremony run): the send landed, the chain is now six deep, nothing else moved

**This is the Monday cron**, not another message session: the sixth PM
pull request in today's chain (#225, superseding #224). Full standup
detail is in `docs/sprints/dispatch-queue.md`'s matching section; this
note carries only what changed.

**One real update: today's 09:00 UTC send reached the site.**
`/library` now lists `2026-W40` as newest, up from `2026-W39` at the
last pass, and `/library/2026-W40` returns 200. Sprint item 4's
post-window check is satisfied.

**`PM_DISPATCH_ENABLED` is confirmed `true`** this run, read directly
from the job's own environment rather than the API (which returned 403
the last two passes). It changes nothing: the org is in synchronous
mode regardless, since a PM session posted to the board 51 minutes
before this run started, inside charter §5's two-hour guard. Queued,
not fired — see the dispatch-queue file.

**Everything else is unchanged**: the merge-authority grant question,
the ADR-38/39 duplicates, `main`'s red checks (now ~15h47m), and zero
PRs qualifying for a Tier B merge. The four items below are the same
four, re-verified fresh rather than carried on trust.

## Updated 2026-10-05, ~18:30 UTC (message run, the six-hour pass): a quiet fleet, the same two things still waiting on you, and one new repeat finding

**Inbox, checked first per the board protocol.** `board.messages` for
`pm`/`alexandria` carries nothing new since the chair's distill-timeout
ask (05:15 UTC), which #221 already answered in full. No other ask or
handoff addressed to this seat sits unanswered.

**The fleet has not run at all for about thirteen hours.** `gh run
list` shows nothing, success or failure, since the pm-agent run at
05:15:26 UTC that closed out the last pass. There is nothing to triage
from "the last six hours" because nothing happened in them: zero runs,
zero failures, zero merges. That silence is itself the finding, not an
absence of one.

**The merge-authority grant is still unconfirmed, checked fresh rather
than carried on yesterday's word.** `docs/decisions.md` still stops at
two ADR-39s (see the new incident below) and names nothing as ADR-041,
which is the citation `docs/standards/pm.md` §10 rests on. The PR that
would even fix that citation, #216, is still open. One extra data point
this pass: #216 is the one open pull request that would mechanically
pass every other Tier B condition today (clean merge, no Tier C path,
no failing checks, not a draft), and its own author still declined to
claim merge authority over it, in its own description, because vendoring
a standard is the chair's call and not a grant you can use to merge the
thing that defines the grant. Nothing qualifies for a Tier B merge this
pass, the grant question aside: see the dispatch-queue's Tier B check
for the other eight PRs, each excluded on its own separate, ordinary
ground (draft, conflict, red checks, or a charter file in the diff).

**New since the last pass: a second ADR number collision, and the first
one is still unfixed.** Recorded in `docs/agents/incidents.md` as
`INC-2026-10-05-adr-39-duplicate`: two different 2026-10-05 and
2026-09-30 decisions both carry the header "ADR-39", the same allocator
failure `INC-2026-10-01-adr-38-duplicate` named four days ago for
ADR-38, whose own pair is still unrenumbered on `main` right now. Fixing
either is the chair's, not this seat's.

**`main`'s checks have now been red for about fifteen hours straight**
(since 03:36 UTC), unchanged through this pass, and are the reason
PR #219 cannot land after seven identical failed attempts. Nothing has
merged to `main` in the last 14.5 hours either, which is inside the
48-hour threshold that would otherwise make this the headline of the
standup, but is worth naming here before it gets there.

**Posted to the board**, as a first-person note from this seat
summarizing this pass: message `5a49f86d-9e42-4b36-ac66-b4b7a66ea841`,
2026-10-05T18:32:14Z.

**What waits on you, in one line each.**

1. **The merge-authority grant** (#216, and the ADR-041 citation it
   rests on) — ratify or revoke it; nothing merges under it either way
   until it has a record in this repo.
2. **PR #60**, the pre-send quality checklist, now 15 days open — Tier C
   (`prompts/daily.md`), only your merge opens it.
3. **The ADR-38 and ADR-39 number collisions** — a renumbering call in
   `docs/decisions.md`, which is the chair's register, not a seat's.
4. **The Polar Merchant-of-Record account (ADR-30)** — 9 days overdue,
   named again because O1 KR1 needs it 8 days from now.

Nothing shipped against the sprint since the 05:50 UTC pass: items 1
through 4 in `docs/sprints/sprint-2026-10-05.md` carry forward
unchanged, same as the quiet thirteen hours they sat in.

## Updated 2026-10-05 (message run): the merge-authority grant is unconfirmed, and no "bus-door decision" exists anywhere in this repo

Two notes arrived tonight, both pressing on the Tier B PM-merge grant in
`docs/standards/pm.md` §10. Checked both against the files rather than
taking either on trust.

**This seat was never going to act on it either way.** Nothing in
`prompts/pm-agent.md` grants this seat merge authority at any tier; its
own boundaries say merging stays the owner's, full stop. Every PM run
today that has touched this file has checked the vendored standard's
Tier B conditions and found no qualifying PR, so no merge has happened
under it yet regardless of whether the grant is good.

**The grant's own citation does not check out today.** §10 names ADR-041
as its source. This repo's decisions file stops at ADR-40, an unrelated
skills-testing decision, and names nothing in the forties for a merge
grant. Per `docs/agents/cross-repo-law.md`, a parent decision that
changes something in this repo is owed a record here before it governs;
none exists yet. One of tonight's two notes, from the exo centralizer,
says the same thing directly: the text lives on two open HQ pull
requests, not on HQ's own main branch, and the owner has been asked to
ratify or revoke it. A separate, already-open pull request in this repo
(the PM-standard re-vendor) asserts the opposite, that the owner already
merged this decision at HQ. Both cannot be true, and resolving which one
is current is the exo centralizer's job, not this seat's guess. Flagging
the contradiction here so it isn't merged on the strength of whichever
claim a reader happens to see first.

**No "bus-door decision" exists to check against.** Searched
`docs/decisions.md`, `docs/allhands/`, this file, and the board for the
term and anything resembling it. It names nothing on record here. The
second of tonight's two notes expected one, the way two sibling
companies' PM seats already have one. Per this charter's relay rule,
this seat reports an existing ruling and does not invent one, so rather
than guess at what the term means or assert a decision exists, this is
named as a gap: either the decision was never relayed into this repo, or
it has not been made yet. Either way it is not this seat's to manufacture.

**What this changes in practice: nothing, for this seat.** It confirms
what was already true, that no PM run should be merging anything.
It matters for how the owner reads other seats' claims about what they
are allowed to merge, which is why both notes get a real answer instead
of a shrug.

**Owner-only, one line.** Ratify or revoke the merge grant at HQ, the
way the exo centralizer already asked, and say which of the two
conflicting claims about HQ's own main branch is current. Until a
decision lands as a record in `docs/decisions.md`, no PM-seat run
anywhere should treat the grant as live.

**Still true after this ceremony run reconciled everything else below.**
This run (the Monday ceremony proper) checked every open PR against the
Tier B conditions anyway, grant-or-no-grant, and found none that
qualified on their own facts (drafts, red checks, or Tier C paths) — see
"Tier B merge check" further down. So the unresolved grant changed
nothing this run could have done differently either way.

## Updated 2026-10-05 (message run): the sprint regroomed against the MVP goal, and one decision waiting on you

A handoff from `asc/chair:hq-console`: the owner renamed this sprint's goal
("The press runs itself") and wrote it, with a Definition of Done request, on
board item `5e7b7f49` in "This sprint." Full regrooming is in
`docs/sprints/sprint-2026-10-05.md` and posted on that board item, in first
person, under the `pm` seat. Two items that don't serve the goal moved to
next sprint (Left-Behind Index page, skill re-measure); two new items that do
were added (a real `subscribers` write path for signup, a real unsubscribe
endpoint), both buildable without new spend.

**What waits on you, specifically.** The DoD's "a verified domain" is Phase 2
per `docs/vision.md`'s own plan (buy a domain, Amazon SES, SPF/DKIM) and is
money and a new paid service, which this seat's charter puts in your hands,
not a seat's. Confirming Phase 2 now (even as a date rather than an
immediate build) is the one thing in this regrooming no seat can decide for
you. Everything else found is named in the sprint file under "What still
stands between the press and a week with no human step."

## Updated 2026-10-05 (message run): a staffing-authority claim, declined and waiting on you

A note addressed to this seat, from `asc/chair:hq-console`, said staffing is
now the PM's: create and switch on a seat for any role that already has a
charter, through a "new-seat tool" that writes the assignment, the workflow
and the manifest, merged under Tier B.

**This seat did not act on it, and the reason is a tracking item, not a
one-line aside.** Full report in PR #215
(`alexandria-pm/2026-10-05-message`). Three things made this a decline
rather than a dispatch:

1. No such tool exists (`new-seat` is not in `tools/`, `.github/workflows/`,
   or anywhere else in the tree).
2. `company.yaml`'s roster and `docs/standards/pm.md` §10 both place seat
   activation and the roster in Tier C, and §11.2 says plainly "a dormant
   seat (activation is the owner's)." A message does not amend a standard.
3. The claim also asked this seat to merge the PR that would create a seat
   under Tier B, the same day Tier B itself merged (PR #147, HQ decision 041,
   03:31 UTC). Tier B's own first rule excludes the PM's own PR. Acting on
   the claim would have broken the rule in the PR that just wrote it.

**What waits on you.** Confirm or deny, in whatever form is normal for a
standard change: an ADR, a charter PR, or a word back on the board. Until
then this seat keeps staffing exactly where it was before this note:
dormant-seat activation and roster changes are yours alone.

## Updated 2026-10-05 (Monday ceremony, full reconciliation)

**This run completes the ceremony.** An earlier synchronous session
today (PR #197, merged 03:24 UTC) shipped the retrospective on sprint
2026-09-28 and this file's placeholder line, then ended before
grooming, the new sprint, or today's dispatch queue landed. This run
builds on that rather than redoing it: the retro at the top of
sprint-2026-09-28.md is already final.

**A live synchronous session started partway through this run.** At
03:41 UTC, seven minutes after this run began, someone dispatched
`research-agent` and `engineer-agent` directly (`workflow_dispatch`),
and new PRs (#208-#211) have opened since, including engineer and
research work that already targets agent-containment's zero-claims gap
named below. Per charter §5's hard stop, this run queues rather than
fires any dispatch of its own for the rest of this ceremony. The
open-PR snapshots in this file are accurate as of ~03:46 UTC and will
be stale within the hour; that is the live session's pace, not a
tracking gap.

**Reconciliation against docs/decisions.md and docs/allhands/ since
2026-09-28, per charter §1d.**

- ~~`docs/agents/registers.md`'s nine conflict markers~~ — **resolved.**
  Confirmed zero `<<<<<<<`/`=======`/`>>>>>>>` markers in the file as
  of this run. Merge commit `bdfa4a7` ("Merge main into
  alexandria-security/2026-10-05-window... main wins on files it
  replaces in full") cleared them during today's merge session.
- **The merge-backlog crisis the 2026-09-28 retro named is resolved,
  dramatically.** That retro counted 66 open PRs and a 7-day conversion
  of 12 merged against roughly 63 opened. Between 02:27 and 03:36 UTC
  today, 45+ of those PRs merged in one synchronous session. As of this
  run: 5-8 PRs open (climbing again as the live session above opens
  new ones), 80 merged in the trailing 7 days against 78 opened — a
  conversion over 1. The process-improvement the retro proposed
  (counting this fraction daily) would have shown the turn exactly
  where it happened; worth keeping as a standing standup line now that
  there is a number to watch for the next time it drops.
- **ADR-38 is still a live duplicate number in `docs/decisions.md`,
  unresolved.** Two `## ADR-38` headers exist (2026-09-29 "Skills close
  the loop with their consumers" and 2026-09-30 "The skill quality
  bar"), landed as separate commits that never got renumbered. Same
  shape as the ADR-32 duplicate from 2026-09-24, same resolution this
  file asked for then: your one-line call on which keeps 38 and which
  renumbers, applied in one pass that greps every citing file so no
  cross-reference breaks. Not this seat's to fix (decisions.md isn't a
  writable surface for any seat but the chair); flagging for you or
  the ExO.
- **New ADRs since 2026-09-28** (none dated after 2026-09-30; nothing
  new arrived in the window this file could see before this run
  started): ADR-36 (skills proven, not asserted — eval harness),
  ADR-37 and its guardrail amendment (skills maintain themselves —
  auto-merge triggers, six guardrails), two ADR-38s (above), and
  ADR-39 (distill moves to Kimi, three ceilings, chair-run gates). All
  name engineer/skill/security/frontend follow-up work; all of it has
  already had a run since (today's window session touched exactly
  these files per the merged PR list below), so none of it is a fresh
  dispatch trigger under §11.3's "no run followed" test.
- No all-hands newer than 2026-09-18 exists in `docs/allhands/`.

**Critical, found this run: `main` is red right now.** Every push to
`main` since 03:23 UTC has failed `checks` on the same cause:
`tests/test_panel_provenance.py` (5 failures) — `skills/agent-containment`
cites no claim ids, and three skills (`evaluation-integrity` among
them) use "ours ..." phrasing outside the panel's recognized
unsourced-judgment vocabulary. This is the provenance gate
(`INC-2026-10-03-panel-reviewer-claims-a-ci-step-it-never-had`'s queued
step) having just gone live in CI for the first time against real
skill content, and the content doesn't clear it yet. **Already being
worked**: PR #204 (engineer, open) touched exactly these files before
being superseded minutes ago by PR #209 ("the containment threads
become findable"), part of the live session above. Not re-flagged as a
fresh incident this run because a run is already in flight against it;
worth one line in next standup confirming `main` went green, not a new
dispatch.

**Critical, confirmed still open: the `sql_query` MCP tool can read
`subscribers` and `users`, not just the corpus.** The 2026-09-28 retro
named this as PR #174's finding (merged forward through #196 today,
still without a code fix — security's own PR #196 description was
never filled in past its draft placeholder). Checked directly against
`mcp/server.py` this run: `sql_query`'s only checks are "single
statement" and "starts with SELECT/WITH"; there is no table allowlist,
and `db/schema.sql` confirms `subscribers`, `users`, `auth_attempts`,
and `consumed_codes` live in the same database the corpus tables do.
Open since 2026-10-01, now 4 days, and genuinely needs your call on
the fix shape (an allowlist inside `sql_query`, or a restricted view it
queries instead) before any seat should touch it — the same framing
security gave it a week ago still holds.

**Top three for you, this run, all launch-critical, 8 days out:**

1. **The `sql_query` scope decision, above.** A real data-exposure
   path, open 4 days, and the fix shape is yours to pick.
2. **Merge PR #60** — the pre-send quality checklist (sprint
   2026-09-21 item 4), finished and open **15 days**, still the oldest
   open PR in the repository. It touches `prompts/daily.md`, which
   makes it Tier C under standards/pm.md §10 (charters/prompts are
   owner-merge only) — this seat genuinely cannot merge it for you even
   under the new Tier B merge authority. Nothing further is owed from
   any seat.
3. **The Polar Merchant-of-Record account (ADR-30)** — due
   2026-09-26, now **9 days overdue**. No live keys appear anywhere in
   the codebase as of this run. O1 KR1 needs the $20 spine purchasable
   end-to-end by 2026-10-13 (8 days out), and checkout wiring cannot
   start until this account and its keys exist.

**Tier B merge check, this run (standards/pm.md §10).** Every
currently open PR was checked against the five Tier B conditions. None
qualify: #202 (frontend), #203 (okr), #204/#209 (engineer), #205
(finance), #210 (research) are all drafts; #60 (engineer) is not a
draft but touches `prompts/daily.md`, a Tier C path. No merges
performed this run.

**A decision this file is surfacing rather than making: SEP-2640.**
The 2026-09-30 research brief flags that the IETF/MCP community's
"Final MCP standard for serving Agent Skills" (SEP-2640) has existed
five months with zero awareness in this org, and that alexandria's
skills are already shaped to match it, and asks the PM and skill seat
to decide whether conformance is a 2026-10-13 launch item. Provisional
call, pending your veto: **not a launch item.** Eight days out, with a
`sql_query` data-exposure path and a $20 spine still unpurchasable,
adding new launch scope for a standards-conformance question with no
named customer complaint is the wrong trade. Filed as a `proposed`
ledger entry for after launch rather than scheduled.

**The design pre-mortem is due this week.** docs/agents/frameworks.md
lists the pre-mortem as adopted, one hour, once, "week of Oct 6" — that
week starts tomorrow. It needs the owner or chair to facilitate it, not
a sprint item; naming it here so it does not slide past Oct 13 unused.

**Register-integrity note, not this seat's to fix.** `docs/agents/turn-caps.md`
has never been updated to list its own "rule 5" (the 70%-of-cap daily
report this charter names and this standup runs below) — the rule
lives only in prompts/pm-agent.md, citing a file that doesn't carry it.
Same class as the ADR-38 duplicate: a register whose own text
disagrees with what cites it. ExO's to fix on its weekly pass.

**Resolved since last noted (added to the section below, not
repeated):** registers.md conflict markers (above). PR #110's
`modal deploy` gap (incident 24's shape) is very likely superseded by
the deploy-drift guard that merged today (PR #166,
`pipeline/runtime_sha.py` + the `deploy_runtime` table), which is
designed to self-detect exactly this class going forward; this file
will stop carrying it as a standing item once a standup confirms the
guard has actually tripped or cleared once for real.
## Updated 2026-09-28 (Monday ceremony, full reconciliation)

**Reconciliation against docs/decisions.md and docs/allhands/, done
first per charter §1d.** No new all-hands since 2026-09-18. Newest
ADRs since the last ceremony: ADR-33 (dispatch authority, active,
already reconciled below and in dispatch-queue.md), ADR-34 (Clerk/Neon
accounts, already shipped), ADR-35 (skill creation requires reading,
2026-09-25 — already being followed: PR #111 is the first run under
it, no open pending item was tied to this ADR to strike). Two items
below are struck this pass:

- ~~Item 1, Clerk keys + Neon connection string as Vercel env vars~~ —
  **resolved.** The OKR seat's 2026-09-24 check-in verified the live
  site directly (libraryofalexandria.dev, real archive, real skills
  page), which is not reachable without these env vars being set. No
  further action.
- ~~Item 12, ten minutes of the owner's eyes on the new email capture
  and live metric~~ — **superseded by time.** PR #26 merged three
  weeks ago and multiple frontend visual sweeps have iterated on the
  site since; asking for a look at that specific, long-superseded diff
  no longer means anything. If the owner wants a fresh look at the
  current site, that is a new ask, not this one.

**Top three for you, this run, all launch-critical:**

1. **Merge PR #60** — the pre-send quality checklist (sprint
   2026-09-21 item 4), finished and open **8 days**, the oldest open PR
   in the repository. Nothing further is owed from any seat; it is
   waiting only on your merge.
2. **The Polar Merchant-of-Record account (ADR-30) is now overdue.**
   Due 2026-09-26 per this file's own prior entry; no live keys appear
   anywhere in the codebase as of today, 2026-09-28. O1 KR1 needs the
   $20 spine purchasable end-to-end by 2026-10-13 (15 days out), and
   checkout wiring cannot start until this account and its keys exist.
   This is now the single most launch-critical open item in this file.
3. **Deploy PR #110** (merged 2026-09-26): `modal deploy
   pipeline/triage.py` and `pipeline/interpret.py`. The fix for the
   corpus stall the 2026-09-24 curation brief found (claim graph frozen
   since 2026-09-12) is written, tested, and sitting inert on main,
   because the engineer seat has no Modal CLI access. Same shape as
   incident 24 and the 2026-09-19 triage-fix note below: merging is not
   deploying.

**New finding this run: this Monday's press send is unconfirmed.** This
seat's sandbox has no database credential to query the `digests` table
directly. Proxy evidence: no new commit to `site/content/issues/` today
(2026-09-28) as of 18:13 UTC, 9+ hours past the cron's 09:00 UTC Kimi
window, and the newest published issue is still 2026-W39 (2026-09-24).
Sprint 2026-09-28 item 1 assigns the engineer seat to run the same
one-click-style check incident 24 established (this time against the
database, which this seat cannot reach, or `modal app logs
alexandria-weekly`) and report a definitive answer. Not claiming a
failure, only that this run could not confirm success and the
delivery-health rule says to say so rather than stay silent.

**Run health, this ceremony.** Fleet: three engineer-agent runs failed
since the last PM run (36330209631, 36342225307, 36366360908), all the
same already-registered defect (INC-2026-09-26-slack-notify-jq-control-
chars, now a 5th-7th occurrence): the run's actual work and git push
complete cleanly, then the PR-body-to-Slack notify step's second `jq`
parse dies on a stray control character. Work survived in all three
cases (PRs #122, #124, #127 opened minutes after each failure). No new
incident filed; this is a repeat of an already-escalated, unfixed
defect outside every seat's writable surface except the ExO's. All
other runs since the last PM run were green. Delivery: the site is 2
commits behind main (last deploy 2026-09-26T01:32:12Z, commit a8349f0,
main now at 322e7da); the MCP server responds (probed directly, `/docs`
200, `/mcp` 401 as expected under OAuth); the press is the unconfirmed
finding above.

**PM's own backlog, this run.** Four of this seat's own PRs were open
when this ceremony started (#125, #121, #117, #113), spanning
2026-09-26 to 2026-09-27, three of them touching files this ceremony
also writes (pending.md, dispatch-queue.md). Merged into this branch
rather than left to collide; this PR (pm/sprint-2026-09-28) supersedes
all four. Close them without merging once this one lands, per the
charter's own guidance for exactly this situation.

**Dispatch, this run: none fired.** No candidate this run carries the
evidence charter §4/§5 requires (a run, PR, ruling, or metric naming a
specific seat with no run following). The one live board item that
used to be this queue's standing frontend candidate ("the board client
... on a GitHub runner") is now assigned to and in progress under
`engineer`, not `frontend`, so that trigger is gone. Every dispatchable
seat with an open PR (engineer #127, writer #126, okr #114) is excluded
by the hard stop; the remaining seats (research, market, frontend,
skill, security) have nothing evidenced beyond their normal cadence.
See dispatch-queue.md.

**Linear trial (charter §1e2): still on.** The board read this run
carries Linear-sourced items (`source_url: "linear:ALE2-…"`) in the
current sprint's board mirror, confirming the chair is still using it
during working sessions. No verdict change since it was last noted.

## Updated 2026-09-27, ~19:00 UTC (message-triggered session, a voice ruling)

Owner, live, on how she wants to read every seat's output: she does not
want to see codes, she wants good descriptions instead. Recorded in full
in `docs/voice/taste.md`'s 2026-09-27 entry. The short form: never
"ADR-", "L-", or "Incident N" in a line she reads (a Slack bullet, a PR's
opening bullets, the board). Name the decision by what it decides. The
codes stay inside the repo, where they still do their job of proving a
judgment already exists rather than inventing one.

**Not this run's to fix, and owed to the ExO:**

- **prompts/pm-agent.md section 4's own example contradicts the ruling
  the day it was recorded.** Its dispatch-queue template prints
  "**Trigger.** ADR-29 class 3, a processing gap.", and that same
  section requires the dispatch queue to go into the PM's PR
  description in full, so the charter currently instructs the one
  violation the owner just named. A charter edit is the ExO's to make,
  never this seat's.
- **At least two live specimens already on the record, evidence the
  sweep should start from:** PR #113's own title, "PM sync session
  2026-09-26: owner's live priority reorder (ADR-037)", and the
  standing dispatch-queue.md text merged from the 2026-09-25 standup,
  "in `docs/decisions.md`'s newest entries (ADR-32/33/34)". Neither is
  this run's to edit; both are what a sweep for the pattern will find
  first.
- **A company-wide home may already exist.** `docs/standards/lessons.md`
  carries L-A5, "House voice in owner-facing prose," with provenance
  "alexandria house rule, owner-set, portfolio-wide." This ruling reads
  as a concrete instance of that same law, which means it may belong in
  `docs/agents/hq-relay.md` as well as in the local taste register, so
  the rule reaches every product HQ runs, not only this one. That
  judgment and that file are the ExO's, not the PM's.

**Also worth naming rather than leaving quiet:** this tracker's most
recent entry before this one was 2026-09-24. The 2026-09-25, 2026-09-26,
and 2026-09-27 standups each replaced `docs/sprints/dispatch-queue.md`
without a corresponding update here, which is the tracking gap section
1d exists to prevent. Tomorrow (2026-09-28) is the Monday ceremony run;
full reconciliation against everything that landed since 2026-09-24
belongs there rather than in this narrow, reactive session.

## Updated 2026-09-24, ~16:00 UTC (message-triggered standup, deciding from market's brief)

Owner directive relayed by the chair: when market's ranking brief lands,
decide from it, write the decisions here and into the sprint, queue
work where it belongs, and list owner-only decisions one line each. The
brief landed as PR #98 (`docs/market/briefs/2026-09-24-b.md`), ready
for review, superseding PR #93's stub. Full reasoning is in
`docs/sprints/dispatch-queue.md`'s "Decided from the market brief"
section; this entry is the short version for this tracker.

**Decided, no owner action needed beyond merging what already exists:**
- The brief's #1 priority (land the enjoyability fix before the next
  issue ships dense) has no new work to queue: PR #95 (writer,
  supersedes #92) is already the fix, already open, already built on
  the owner's own ruling in `docs/voice/taste.md`. The only step left
  is her merge.
- The brief's #3 finding ($20/month reconfirmed, no pricing change) is
  closed. No action owed.

**Owed to you, one line each:**
- **Merge PR #95** (writer): the enjoyability/canon-law-14 fix, the one
  you asked for directly last night.
- **Merge or close PR #98** (market): the finished brief; closes #93
  once it does.
- **Rule on the claim graph vs. the pricing page**: market's brief
  flags that `libraryofalexandria.dev/pricing` sells the skill library
  and routines but never mentions the claim graph, which
  `docs/market/positioning.md` calls the core differentiator. Add it
  before October 13, or confirm it is deliberate post-launch scope.
  `docs/ideas.md` carries the `proposed` entry (filed on PR #98).
- **PR #60 rebase or retirement** — already on your list from PR #97's
  pass tonight; not repeated in full here to avoid a third copy of the
  same ask, see that PR or the sprint file's status section below.

**Nothing new queued to writer, frontend, or engineer this run.**
Writer's relevant work is already open and blocked only on your merge.
Engineer already carries two open PRs (#60, #94), which is a hard stop
on a new dispatch regardless of what the brief found. Frontend has no
ready, filed task from this brief — the claim-graph question is a
decision, not yet a spec, so there is nothing to send until you rule.

## Updated 2026-09-24 (Thursday night standup, owner present)

Owner directive for this run: standup mode, synchronous, owner present.
Two new items to track, both already dispatched by the chair before
this run started, and the night's reconciliation.

**Two new owner items, dispatched by the chair tonight:**

1. **engineer** — send the press through `site/emails/digest.html`, not
   the inline `<div>` (owner: "i want the emails to have ui").
   `pipeline/weekly.py` (around line 709-713) still builds the email
   body as a bare styled `<div>` wrapping raw markdown-to-HTML;
   `site/emails/digest.html` (built earlier, commits 8bb12ed/589b2a0) is
   the real newsletter-shaped template and is not yet wired into the
   send path. Dispatched tonight (`workflow_dispatch`, in progress as of
   04:49Z when this run started); no PR yet.
2. **writer** — every issue stands alone: the opening never references a
   previous issue or "last week" (owner ruling, `docs/voice/taste.md`'s
   2026-09-24 entry, to become canon and apply to `prompts/digest.md`).
   PR #89 (open, draft, `writer/2026-09-24-b`) delivers this: promotes
   the rule into `docs/voice/canon.md`, applies it to `prompts/digest.md`,
   and grades 2026-W39 against the full canon and ban list. Supersedes
   #81, #74, #71, #67, #62, #55 per its own body. Awaiting your merge.

**Landed since the last snapshot (PR #88), reconciling this tracker
against what merged tonight:**

- **ADR-32 duplicate, resolved.** `docs/decisions.md` now has Clerk at
  ADR-34 and the Kimi K2 press decision keeps ADR-32; ADR-33 (dispatch
  authority) is recorded. Struck from "Top three for you" below.
- **ExO chain, done.** #61, #65, #77, and #87 are all merged
  (04:50:01-03Z), not collapsed to #77 alone the way this file's prior
  pass suggested, but functionally equivalent: nothing from that chain
  is left open.
- **#69 merged** (04:52:11Z): the digest-HTML XSS sanitize fix, item 1
  of the "independent, ready to merge now" list below. Next in that
  list's order: #66, then #60 (its "#55/#31" dependency note is now
  effectively moot, since #55 is superseded up the writer chain rather
  than merged, and #79 says close #31 unmerged), then #72, then #35
  (close unmerged once #60 lands), then #80, then #84.
- **W39 printed, sent, and published.** `kimi-k2.6` printed 2026-W39 at
  04:31Z and it sent. The chair published it to the site as
  `site/content/issues/2026-W39.md` (confirmed present on main). The
  subscriber roll now carries the owner's three addresses.

**Top three for you, this pass** (updates the list below, does not
replace it): (1) the merge order across the still-open PRs, unchanged
in shape, shorter now that #61/65/69/75/77/87 are done; (2) the
incident-numbering collision (23-29, `docs/agents/incidents.md`, PR
#83's finding, still unresolved); (3) the finance dormant-vs-activated
question. The ADR-32 numbering call is done; it is off this list.

No dispatches fired or proposed this run: an engineer run and a writer
run (PR #89) are `workflow_dispatch` runs from tonight, so the org is in
synchronous mode under charter §5's guardrail. See
`docs/sprints/dispatch-queue.md`.

## Updated 2026-09-24 (ceremony-lite sync, third pass this session)

Owner directive: ceremony-lite update (not the full Monday ceremony,
not a standup), synchronous, owner present. Builds on PR #85's two
commits (04:13 UTC snapshot below); this pass re-checked `gh pr list`
and `gh run list` and found only two changes since then: PR #87
opened (exo, second run today) and this run's own PR #88. No new
merge, no new run failure. Fires no dispatches, same reasoning as
below (owner present, multiple `workflow_dispatch` calls inside the
last two hours).

**New this pass, not caught by the 04:13Z snapshot:**

1. **`docs/decisions.md` has two headers both titled "## ADR-32"** —
   "Accounts via Clerk, Neon as system of record, door-closed launch"
   (2026-09-19) and "The press writes on Kimi K2; sovereign hosting is
   the destination" (2026-09-24). This is the exact failure PR #57
   fixed once already (a duplicate ADR-30, renumbered to ADR-32).
   Per the standing rule this file's own incident register already
   set for duplicate numbers (docs/agents/incidents.md, "On the
   numbering"), the fix is not to renumber silently: renumbering
   breaks every existing cross-reference, and this file alone cites
   "ADR-32" for the Kimi K2 decision four times above (Modal secret
   section, press recovery section). This needs your one-line call:
   which one keeps 32 and which one becomes 33, and whoever applies it
   should grep-fix every citing file in the same PR, since a lone
   renumber that misses a citation is worse than the duplicate. This
   is a `docs/decisions.md` edit, so it is Tier B and outside this
   seat's writable surface regardless.
2. **Org chart gap closed in this PR**: the writer seat (ADR-28,
   running daily since 2026-09-19, seven merged PRs) was missing
   entirely from `docs/agents/org-chart.md`'s active-seats table.
   Fixed in place. Also corrected initiative 3's stale "weekly leads"
   line (ADR-25 renamed that seat to research in 2026-09-19; ADR-28
   then gave the digest's voice to writer).
3. **Board, labels, milestone mirrored this run** (`PROJECTS_TOKEN`
   available and working via `gh api graphql`, though the `gh project`
   porcelain commands 403 on this token's scopes — use raw GraphQL
   against `user(login: "alexandrapaiz").projectV2(number: 4)`, id
   `PVT_kwHOBqunQs4Bj3sN`, same as PR #85's own note): moved the three
   Sprint 09-21 board items that PR #26 and market's positioning
   update actually shipped (email capture, live hero metric,
   positioning.md) from Sprint Ready to Done, evidence-checked against
   the merged PR and the file's live pricing text, not assumed.
   Created the standard label set from company standard §2b
   (`seat:<name>` for all 11 seats including writer, `horizon:now|
   next|later`, `blocked`, `owner-action`) and applied `seat:*` to all
   28 open PRs. Opened milestone `sprint-2026-09-21`, due 2026-09-27,
   the first milestone this repo has had. Not done this pass: the
   board's own "Sprint 09-21 · 1-6" items are numbered against an
   older sprint revision and no longer match this file's current
   five items (the MCP fix, prose benchmark, factual audit, quality
   checklist, skill validation) — a fuller remap is Monday's job, not
   a mid-week mirror's.
4. **Checked, not stale**: a prior pass in this file (2026-09-18
   snapshot, "what each seat owes") flagged `org-chart.md` as possibly
   wrong to list sales as dormant. Checked against ADR-24's own text
   this pass: dormant means no cron, and neither finance nor sales has
   one despite both being hand-dispatched this week. The table was
   already correct; noted in org-chart.md itself so the next run does
   not re-flag it.

**Top three for you, this pass** (see "What I need from you, top
three" in this PR's description for the full version):
1. The ADR-32 duplicate numbering call, above.
2. The merge order across 28 open PRs (unchanged from PR #85's
   breakdown below — still current, re-checked, nothing merged since).
3. The finance dormant-vs-activated question (unchanged from below).

# Pending tracker

Maintained by the PM agent every run (charter §1d): what every seat owes,
what sits in open PRs waiting on your merge, and what waits on an
owner-only action. Each line dated. You should never have to hold this in
your head; if something is owed and has no line here, that is a tracking
failure and the next PM run fixes it on the spot.

Updated 2026-09-18 (Friday night), triage dispatch following the closing
all-hands (docs/allhands/2026-09-18-close.md), owner order relayed by the
chair. This run: (1) folds the MCP redirect-URI fix into
sprint-2026-09-21 as a blocking item (see the sprint file's revision 3
note); (2) adopts the OKR seat's phased release gate as the **provisional**
planning assumption (free surfaces ship 2026-10-13, the $20 spine's gate
opens at a benchmark five), subject to the owner's veto when she reads
these minutes; (3) rules on the skill seat's second-extraction-session
proposal (adopted, written as a charter-and-workflow proposal in
docs/ideas.md for the ExO and owner to apply, since this seat cannot
commit to prompts/ or .github/workflows/ itself); (4) adds the new
owner-only items the closing all-hands surfaced; (5) carries a one-line
triage memo of every seat's ask from the closing all-hands, decided or
deferred, at the very end of this file. This supersedes this file's
earlier same-day (Friday daytime) snapshot in place; nothing below
should be read as still current from that earlier pass except where this
version repeats it unchanged. The next regularly scheduled PM ceremony
(retro on the sprint that just ran, grooming, sprint 2026-09-28) still
runs Monday 2026-09-28 on its normal cadence; this file does not replace
that run.

## Updated 2026-09-24 (Thursday standup, synchronous session)

**Later the same session (04:13 UTC), same run's owner window.** One
material change since the section below was written: **PR #75 merged**
at 03:37:34Z, carrying ADR-32 (owner's decision, recorded today: the
press moves off Groq to Kimi K2 via Moonshot). Two further commits
landed directly on main right after the merge (24000-token output
reservation, then a 25-minute read timeout on the writing call), so the
fix is still being tuned post-merge rather than settled. What this
changes below: item 2 in "independent, ready to merge now" is done, not
pending, and the "not yet merged" framing in the Modal press cron bullet
is stale. What it does not change: deployment to Modal is still
unconfirmed by anyone with dashboard access, so "the fix is built but
not deployed" from this run's PR description still holds. No new run
started and no other PR merged in this window (`gh run list` and
`gh pr list --state open` both unchanged from the snapshot below).
`PM_DISPATCH_ENABLED` synchronous-mode gate still applies: the last
`workflow_dispatch` (engineer, 03:17:07Z) is under two hours old, so
this run queues rather than fires, same as the run below.

**Why this file went six days stale.** No PM run wrote to this tracker
between 2026-09-18 and today. Not neglect: incident 23 (docs/agents/
incidents.md) put the PM's two runs in that window (2026-09-20 and
2026-09-21) on Kimi routing with no golden-set gate, and both failed at
30 turns before writing anything. The chair pulled the OPENROUTE
secrets the same week and this seat is back on Sonnet. Everything below
this section that is dated 2026-09-18 or earlier is the last real
snapshot; treat the items this section repeats as refreshed and
everything else in the older sections as historical record, not current
state, unless a line here says otherwise.

**Run mode.** Today is Thursday, the current sprint
(sprint-2026-09-21.md) runs through Sunday, and this file already said
the next ceremony is Monday 2026-09-28. This run is the daily standup
(charter §4), not the ceremony: no retro, no grooming, no new sprint
file. It is heavier than a normal standup only because of the six-day
gap above.

**Run health.**
- *GitHub Actions:* every non-success since the last PM run is already
  registered. The PM's own two failures are incident 23 (above). Two
  frontend failures from 2026-09-19 are incidents 17-18 (containerization
  uid fixes), also already closed. No new, unregistered failure class.
  Nine seats (engineer, exo, research, security, market, writer,
  frontend, skill, finance) are mid-run right now, dispatched by a human
  within the same two minutes (02:56-02:58Z) — expected in a synchronous
  session, not a failure.
- *Modal press cron (incident 24), tracked here per today's owner
  instruction:* the fix **merged** at 03:37:34Z as PR #75 (ADR-32, press
  moves to Kimi K2 via Moonshot), with two tuning commits landing
  directly on main right after. Deployment is still unconfirmed.
  Deployment has historically been a manual
  `modal deploy pipeline/<app>.py` step (see "Deploy action owed" below
  in this file's 2026-09-19 section, the same pattern), so the merge
  alone may not make Monday's issue print — someone needs to run the
  deploy, or confirm CI already does it. This seat has no Modal CLI
  access to check the schedule history directly; the ExO (PR #77) is
  postmortem-ing the same incident with more access than this seat has.

**Sprint 2026-09-21 progress** (evidence: merged PRs). Items 1 and 3
are done: item 1 (MCP redirect-URI validation) merged as PR #29
(2026-09-19); item 3 (factual verification audit) merged as PR #40
(2026-09-19). Items 2 and 4 are built but unmerged: item 2 (blind prose
benchmark) is PR #66, open, its own title says "built but unscored."
Item 4 (pre-send quality checklist) is PR #60, open. Item 5 (skill
validation on both gold skills) is in flight across PR #70 (open) and
PR #83 (today, draft) — see the PR-backlog section below for the
conflict between them. The full retro against this is Monday's job, not
today's; this paragraph exists so the owner does not have to reconstruct
sprint status from 26 open PR titles herself.

**The open pull request backlog: 26 PRs, oldest ~126 hours old.**
Nearly every one of them appends to `docs/ideas.md` and/or
`docs/agents/incidents.md`, so almost every merge after the first will
carry a one-hunk append conflict — cheap and expected (take both sides),
not a reason to reorder anything. The real complexity is that several
seats opened a new PR daily this week without their prior one merging,
so each day's PR says "built on" and "supersedes" the previous one. Once
the chains are collapsed, the 26 PRs are about 12 real merge decisions:

*Live chains — wait for today's head to finish, merge only the head,
close the rest of the chain unmerged (their content is already inside
the head, per each PR's own "supersedes" claim):*
- Writer: #55 → #62 → #67 → #71 → #74 → **#81** (today, draft). Merge
  #81 alone when ready; close #55, #62, #67, #71, #74 unmerged.
- Frontend: #56 → #73 → **#82** (today, draft). Merge #82 alone; close
  #56, #73 unmerged.
- ExO: #61 → #65 → **#77** (today). #77 itself says it must merge after
  #75 (below). Merge #77 alone; close #61, #65 unmerged.
- Research: #68 → **#78** (today, draft). Merge #78 alone; close #68
  unmerged.
- Security: **#31** (5 days old) → today's #79 (draft) explicitly says
  "close #31 unmerged." Trust the newer run's own call; close #31
  without merging once #79 lands.
- Skill: #70 (open, ready) and today's #83 (draft) are NOT a clean
  chain — #83 says plainly "close #70 in favour of this PR, or merge
  #70 first [then #83 after]," i.e. it names both orders as workable
  and leaves the choice to you rather than claiming one. Pick either;
  it is not a case where merging the wrong one loses work.

*Independent, ready to merge now, in the order their own dependency
notes imply:*
1. **#69** (engineer, sanitize digest HTML) — live XSS break-fix,
   branched from main, no stated dependency. Merge first on urgency.
2. **#75** (engineer, incident 24 press fix) — **merged 03:37:34Z**,
   same session. #77 (exo) can now proceed; it said it must merge after
   #75.
3. **#66** (engineer, prose benchmark, sprint item 2) — branched from
   main, ready.
4. **#60** (engineer, quality checklist, sprint item 4) — ready, but its
   own body says "merge after #55 and #31." Flagging rather than
   resolving: #31 is being closed unmerged (not merged) per security's
   own #79, and #55 is superseded up the writer chain to #81 rather than
   being merged on its own. If #60's actual code dependency is "whatever
   #55 and #31 changed needs to already be on main" rather than
   literally those two PR numbers, merging after #81 and #79 land should
   satisfy it; if it depends on something PR-specific, that needs the
   engineer seat's own confirmation, not a guess from this seat.
5. **#72** (engineer, evidence-grade spike step 1) — its own body says
   "merge this PR last" relative to #35, #60, #66, #69. Sequence it
   after the other four engineer PRs above.
6. **#35** (engineer, daily digest, ~120h old) — superseded by #60
   itself (per #60's own title). Close unmerged once #60 lands rather
   than merging both.
7. **#80** (market, today, draft) — no chain, no stated dependency.
   Merge whenever it's ready.
8. **#84** (finance, today, ready) — no chain. See the finance note
   below.

**A ruling this file cannot make for you.** PR #83 (skill, today)
reports that incident numbers 23 through 29 are each claimed by at
least one currently-open branch in `docs/agents/incidents.md` — a
numbering collision across seats that write to the same append-only
file in the same week. This is exactly the kind of cross-seat collision
this tracker exists to surface rather than let you discover at a failed
merge. Worth a one-line ruling on which branch's numbering wins and
which seats renumber, the same way incident 19's renumbering was
handled.

**Finance ran today (PR #84), dormant-seat question.** `docs/agents/
org-chart.md` still lists finance as dormant, owner-activates (ADR-24).
Today's synchronous dispatch ran it directly and it shipped real work
(mid-month ledger refresh, GH Actions cost line resolved, MoR renaming,
lifetime-tier breakeven). Worth your one-line confirmation on whether
this is a one-off synchronous check-in or an actual activation — if the
latter, org-chart.md's dormant table needs updating, and that update
belongs to a PM run once you've said which it is, not to this seat's
guess today. Finance also repeats its one standing ask, verbatim from
2026-09-18: **the Claude subscription's monthly figure** — still the
only number it cannot get from any repo or public surface.

**Owner-only items still open, refreshed from the 2026-09-18 list
below** (see that list for full context on each):
1. Clerk keys + Neon connection string as Vercel env vars — still not
   confirmed. This may also explain a pattern in the open-PR backlog:
   most open PRs from #55 through #73 show a Vercel preview-build
   `FAILURE` status check (`gh pr view --json statusCheckRollup`),
   while the newest ones (#74 onward) show `SUCCESS`. That is consistent
   with these env vars having been missing and then fixed partway
   through the week, but this seat has no Vercel dashboard access to
   confirm the cause directly — flagging the correlation, not claiming
   the diagnosis.
4. Public git history holds a pre-privacy-pivot digest — still your
   call (rewrite vs. accept exposure).
5/13. The workflow-scope PAT / GitHub App `workflows` permission
   decision — ADR-33 (2026-09-24, this morning) found that
   `workflow_dispatch` works fine with the plain `GITHUB_TOKEN` given
   `permissions: actions: write`, which resolves the *dispatch* half of
   why this was blocking. It does not resolve the other half: a seat's
   own token still cannot push a fix to `.github/workflows/*` itself.
   Worth confirming whether ADR-27's shared-App plan is still wanted for
   that reason alone, or whether it's been overtaken by events.
11. The Claude subscription's monthly figure — repeated by finance today
   (above).
- Linear trial (charter §1e2): still on, no verdict since 2026-09-18
  (docs/finance/opex.md still has it "under evaluation").

Everything else in the 2026-09-18 snapshot below not repeated here is
either resolved (see "Resolved since last noted") or still genuinely
open with nothing new to add; read it as background, not as a live
picture of today.

## Board reorg (owner dispatch, 2026-09-18, done)

A second same-day dispatch, separate from the ops dispatch above: bring
GitHub Projects board #4 ("alexandria scrum") up to real Scrum
structure. Done entirely via `gh api graphql` with
`GH_TOKEN=$PROJECTS_TOKEN` against project 4 (`PVT_kwHOBqunQs4Bj3sN`);
nothing here touches this repo except this note.

**1. Status field rebuilt as a real flow.** Old: Todo / In Progress /
Done. New, in this order: **Backlog / Sprint Ready / In Progress / In
Review / Done**. `Todo` was renamed to `Backlog` in place
(`updateProjectV2Field`, same option ID), which is why every item that
was `Todo` came along automatically; `In Progress` and `Done` kept their
IDs too, so nothing on the board silently reset. `Sprint Ready` and `In
Review` are new options, added empty and populated below.

**2. A weekly `Sprint` iteration field**, one-week iterations starting
Monday 2026-09-21 as directed: Sprint 2026-09-21, -09-28, -10-05,
-10-12, -10-19 (5 iterations, covers the runway through launch with one
week of buffer after). Note the one-day drift from the runway plan's own
prose, which anchors its weeks to launch day (Tuesday 2026-10-13) and so
describes sprint 3 as "10-06 to 10-12": a Monday-start iteration can't
match that exactly. I mapped by nearest overlapping Monday week rather
than force a non-Monday iteration start, since "starting Mon 2026-09-21"
was explicit in the dispatch.

**3. Every card mapped truthfully**, checked against `gh pr list` and
this file's own open-PR tracking, not left as whatever the prior pass
left it:

- Moved to **Done** (all previously `Todo`, all confirmed merged):
  Sprint 09-21 items 1-3 (PR #23), "Design the skill validation system"
  (PR #21), "Define alexandria's distribution system (Thiel)" (PR #17;
  was stale at `In Progress`), "Charter fix: draft PR first" (landed in
  commit d47148b), "Carry: finish the 2026-09-18 visual run" (its three
  named pieces — desk alignment, mobile nav, focus ring, hover polish —
  all shipped across PR #15 and #19).
- Moved to **Sprint Ready** (committed to the current sprint, not
  started): Sprint 09-21 items 4-6 (email capture, hero metric,
  positioning.md).
- **In Progress and In Review are both empty right now**, and that's
  the truthful state, not a gap: nothing is mid-build outside a tracked
  PR at this moment, and no board card maps 1:1 to either of the two
  currently-open PRs (#22 sales first-customers, #24 PM sprint
  re-triage) closely enough to claim. Noted below as a real gap.
- **Iteration assigned only to genuinely committed/runway cards** (6
  Sprint 09-21 items + the 4 "Launch runway ·"/press-release/pre-mortem
  milestones dated to a specific runway week). Everything else keeps its
  existing Start/Target dates but carries no Sprint iteration, per the
  dispatch's "everything else stays Backlog with no iteration" — this
  includes items that happen to have this-week dates (e.g. the two
  urgent security findings) but were never part of the committed
  five-item sprint backlog itself.

**4. Backlog reordered product-first per decision 11** (digest and
skills quality first, plumbing after): the prose benchmark vs. TLDR,
institution backfill + digest resend, skill trigger tests, claim-graph
citations, the verification badge, the reviewer panel, and the
market-proposed proof pieces (head-to-head, "left behind" flagship, free
sample issue) now lead the 43-item Backlog. Launch-mechanics and urgent
items sit in the middle. Pipeline/architecture plumbing (traction-score,
discovery audit, arXiv category, sources.yaml, knowledge-graph upgrade,
CI/security hardening) sits at the bottom. This is a coarse two-ended
triage (quality pulled to the top, plumbing pushed to the bottom), not a
full 43-item hand ranking; the exact resulting order is on the board
itself (Table view, sorted by position) if you want to nudge anything.

**5. Views.** Board view already groups by Status and needs no action —
same field ID, so it inherits the new five-stage flow automatically.
Table and Board views now also show the new Sprint column (added via
`updateProjectV2View`). **Roadmap needs one owner click**: the GraphQL
API confirmed (tried it, got `"Roadmap views do not support visible
fields"`) that Roadmap view configuration — which field it groups
swimlanes by — isn't exposed to the API at all, unlike Board/Table's
`visibleFieldIds`. To see the runway by sprint: open the Roadmap view →
the "Group by" control in the view's toolbar → select **Sprint**. One
click, nothing else needed.

**Gap worth a verdict, not a build**: PR #22 (sales, open, the
first-customers plan) has no board card of its own — it's related to
but distinct from "Define alexandria's distribution system," which this
run marked Done against PR #17. Adding a card for it would be scope
creep on a board-craftsmanship-only dispatch; flagging instead for the
next PM ceremony or your call.

## Open PRs waiting on your merge

Refreshed twice this run: first when PR #18, #19, #21, #23 merged, then
again mid-run when PR #22 and #25 also merged (both while this PR was
still being written; that is why the "Board reorg" section above and the
sales docs/ tree above it are already on this branch — merged into it
directly). Two PRs remain open:

1. **PR #24** — pm, `pm/sprint-2026-09-21` (this PR). Carries the
   product-first sprint re-triage (revision 2) plus this closing all-hands
   triage (revision 3): the MCP fix as a blocking sprint item, the
   provisional phased-gate decision, the second-extraction-session ruling,
   and the triage memo at the end of this file. **Merge this one first**:
   it is the sprint plan and pending-tracker of record, and #26 also
   touches docs/ideas.md.
2. **PR #26** — frontend, `fe/2026-09-18-email-capture-live-metric`
   (draft). Ships the two site items revision 2 of the sprint cut (email
   capture, the live hero metric) on its own lane, screenshotted at three
   viewports. Touches docs/ideas.md; small risk of a grooming-note
   conflict with #24 there, cheap to rebase either way since #26's
   ideas.md edit is additive. Merge after #24 if a conflict appears.

## What each seat owes, and from which directive

- **engineer** — daily cadence. Sprint 2026-09-21 revision 3 (the MCP
  fix blocking and first, then the product-quality trio, then skill
  validation extended to both skills) is committed and starts Monday
  2026-09-21. Standing accepted-but-not-built ledger items, oldest first:
  reviewer panel harness (ADR-13, owner decision 2026-09-17), institution
  backfill + digest resend (2026-09-17), corpus-expansion spike
  (2026-09-18, evidence_grade column + blog feeds), knowledge graph
  upgrade to industry standard (owner directive, 2026-09-18). None are
  this sprint's focus; they carry. Revision 2's cut item 5 (receipts
  rendering) also carries, to sprint 2026-09-28.
- **skill** — Tuesday cadence, next run 2026-09-22. Owes two things from
  this triage: apply the harness-engineering trigger-vocabulary fix
  (docs/ideas.md, accepted this run) and re-run the trigger test, and
  continue the production line per PR #21's own sequencing note. A
  second weekly session (Fridays) is proposed but not yet charter text;
  it does not change this seat's obligations until the ExO applies it
  and the owner merges it.
- **frontend** — Wednesday cadence. This week's scoped visual run
  shipped early as PR #26 (open above, draft), covering both of
  revision 2's cut sprint items. Nothing further owed until next
  Wednesday.
- **market** — Friday cadence. Two runs shipped this week (PR #3, #6,
  merged). Proposals sit in docs/ideas.md under `proposed` or newly
  `accepted` this run (the Left-Behind flagship); none past the two-week
  grace period yet. One flagged action: positioning.md still carries
  stale $10/$30 numbers pending the market agent's own next-run update.
- **okr** — 1st-of-month cadence. First run shipped 2026-09-18 (Q4 OKRs +
  baseline benchmark, PR #2, merged). Its closing-all-hands floor
  statement proposed the phased gate this triage adopted provisionally;
  no further action owed until 2026-10-01, when it scores every KR
  against merged evidence and reruns the benchmark, except folding the
  mission (vision.md §0) into the objectives, already a noted follow-up.
- **security** — 1st and 15th cadence. First run shipped 2026-09-18
  (PR #8, merged). Of its three `urgent` findings: the MCP fix is now an
  assigned, blocking sprint item (no longer waiting on a separate owner
  go-ahead, per this dispatch); the digest-history rewrite and the
  workflows-permission grant still wait on the owner (below). Next
  scheduled run: 2026-10-01.
- **exo** — Sunday cadence, plus synchronous dispatches. Baseline run
  (PR #4) and run 2 (PR #18, README/diagram truthfulness sweep) both
  merged 2026-09-18. Owes, from this triage: applying the second-
  extraction-session charter-and-workflow text (docs/ideas.md, this run)
  to `prompts/skill-agent.md` and `.github/workflows/agent-skill.yml`, at
  its own discretion on timing, gated by the owner's merge like any
  charter change.
- **sales** — active (not dormant; org-chart.md is stale on this, flagged
  below). PR #14, #17, and now #22 (first-50-customers plan, redispatched
  after incident 11's creativity critique) have all merged. Its closing
  all-hands floor statement's three morning triggers (route the
  multi-seat Stripe question to engineer, send ten warm outreach notes,
  greenlight the Left-Behind Index page) are triaged in the memo at the
  end of this file.
- **research** — Monday 16:30 UTC cadence. `agent-research.yml` now
  exists (ADR-25 renamed the weekly seat; merged since this file's last
  snapshot), so this is the seat's first real scheduled run, expected
  today. Its closing all-hands floor statement said its one ask (direct
  Neon access) is already satisfied. Nothing else owed from this triage.
- **finance** — dormant, owner-activation pending (ADR-24). Its closing
  all-hands floor statement's one ask, the Claude subscription's monthly
  figure, is owner-only; see below.

## Owner-only actions waiting

1. **Clerk keys + Neon connection string as Vercel env vars** — due
   2026-09-19 (tomorrow). Not yet confirmed. Blocks the site deploy step
   of the launch runway.
2. ~~Stripe account and keys~~ — **REPLACED by ADR-30 (2026-09-19):
   Merchant of Record.** Owner creates the Polar account (Lemon
   Squeezy fallback), sets the API key and webhook secret as repo
   secrets, and adds the payout method. Due 2026-09-26. The engineer
   wires the product, checkout, and the webhook-to-Clerk entitlement.
3. ~~MCP OAuth redirect_uri validation gap~~ — **no longer waiting on
   you.** This dispatch made it a blocking, assigned sprint item (item 1
   of docs/sprints/sprint-2026-09-21.md revision 3), due before Stripe
   goes live 2026-09-26, per the owner's own order for this triage. Still
   worth your read of the finding (docs/ideas.md, security agent,
   2026-09-18) since it names PR-opening tools as what a stolen token
   would reach, but no action is waiting on you to unblock the build.
4. **Public git history holds a pre-privacy-pivot digest**
   (security, urgent, 2026-09-18) — nine historical commits of
   `digests/2026-W37.md` are readable by anyone who clones the public
   repo. Needs your call on rewriting history (BFG/`git filter-repo`,
   disruptive) versus accepting the exposure.
5. **DECIDED (ADR-27): one shared GitHub App.** Remaining owner step
   is the two-minute App creation (steps from the chair), then the
   chair wires it. Was: Grant the GitHub App `workflows` permission,
   or don't**
   (security, urgent, 2026-09-18) — no seat's token can currently push a
   workflow-file fix (including ExO's, whose charter names this as
   writable). The pinning fix for `actions/checkout` and
   `claude-code-action` is ready and waiting on this decision.
6. **Verdict on "Show each skill's validation evidence on its page"**
   (market proposal, 2026-09-18) — not yet two weeks old, but flagged
   early: it is most of the skills-library standing item 3
   (claim-graph citations rendered in the library) already, so a verdict
   now unblocks that item instead of waiting on a duplicate proposal.
7. **Panel PR-merge token scope** (2026-09-17) — due mid-November, not
   launch-blocking. The current fine-grained PAT is contents read/write
   only; the reviewer panel's autonomous merge needs PR-merge scope
   minted by you.
8. **A likely mis-copied verdict** flagged by a prior PM run
   (docs/backlog.md, "Awaiting your verdict" section): docs/ideas.md's
   "Permanent free sample issue on the site" carries the same rejection
   sentence used on the four beyond-skills product proposals decision 6
   named, but it is not one of those four. Worth confirming the status
   is what you intended.
9. ~~The release-gate reconciliation~~ — **resolved by the owner,
   2026-09-18: ADR-26.** The gate is a benchmark FOUR, Oct 13 holds,
   product-first until launch. Supersedes the provisional phased gate.
   (Original framing kept below for the record.) Was: a provisional
   ruling awaiting her veto (incident 12 / decision 11, 2026-09-18, updated per the
   closing all-hands and this triage) — the OKR seat's phased-gate
   proposal (free surfaces ship Oct 13, the paid spine's gate opens at a
   benchmark five) is adopted **provisionally** as of this dispatch so no
   seat sat blocked overnight. Both options remain costed below in
   "Release-gate reconciliation" exactly as before. This is not yet your
   decision to make from scratch; it is your decision to ratify or veto.
   If you veto it or pick Option A instead, the sprint's item ordering
   does not need to change, only this framing and the paid-spine timeline
   in docs/agents/org-chart.md's initiatives and docs/okrs/.
10. **Sending the first ten warm outreach notes** — sales' plan (PR #22,
    merged) has these finished and ready; per the standing law, agents
    draft, only you send. Triaged in the memo below.
11. **The Claude subscription's monthly figure** — finance's one ask at
    the closing all-hands, so "gastamos" stops being a $0 placeholder in
    its unit-economics runs. A number only you can supply.
12. **Ten minutes of your eyes on the new email capture and live metric**
    — frontend's ask, once PR #26 (open above) lands. Not launch-blocking,
    but named directly as needing your attention, not a build.
13. **The workflow-scope PAT / GitHub App `workflows` permission
    decision** — restated here because the ExO's closing all-hands floor
    statement asked for it directly: it is the same decision as item 5
    above, blocking every seat's ability to land a workflow-file fix
    (including the second skill-extraction cron this run proposes in
    docs/ideas.md) without going through you by hand each time.
14. ~~The domain~~ — **DONE, 2026-09-18: the owner purchased
    libraryofalexandria.dev on GoDaddy.** Remaining: point it at Vercel
    (two DNS records at GoDaddy plus adding the domain in the Vercel
    project) once the env vars land. Decision 11's "real domain"
    non-negotiable is satisfied.

## Resolved since last noted (no longer pending)

- NEON_RO_URL secret — fixed and verified 2026-09-18 (skill agent, PR
  #16). docs/backlog.md's launch-runway table still shows this row as
  "pending"; that file is outside this run's writable surface to correct,
  flagging here so the next grooming run updates it.
- PROJECTS_TOKEN secret — done, board live since 2026-09-18 (mid-week PM
  run).

## Release-gate reconciliation (provisionally decided; yours to ratify or veto)

Decision 11 set the gate (a five on the OKR benchmark) and named the
tension against it explicitly: "the PM must present back to the owner:
this gate versus the fixed Oct 13 date." Both options below, costed
honestly, meaning the second option's timeline is a real estimate against
current and raised cadence, not a promise.

**Update, closing all-hands triage, 2026-09-18 night:** the OKR seat's
floor statement at the closing all-hands named Option B directly as its
recommendation, and the owner's dispatch for this triage run adopted it
as the provisional planning assumption, explicitly so no seat sits
blocked overnight. Read everything below as the reasoning behind that
choice, not as a menu still fully open; if you veto it when you read
these minutes, the sprint's item order (docs/sprints/sprint-2026-09-21.md)
does not need to change, since items 2-5 serve Option A's path just as
much as Option B's. Only the paid-spine timeline framing would change.

**What "a five" would actually take.** The baseline (docs/okrs/okrs-2026-Q4.md,
2026-09-17) scored alexandria 1.3-3.3 across five axes against Elicit,
TLDR AI, and Anthropic's skills ecosystem; overall 2.6. Two of those axes
are inside alexandria's control this week: judgment (is the digest
accurate and does its claim graph hold up) and reader/agent actionability
for what already exists (is a skill honestly validated, does a claim
honestly cite). This sprint (docs/sprints/sprint-2026-09-21.md, now
revision 3, items 2-5) targets exactly those; item 1, added this triage,
is the MCP security fix and does not itself move this score. Two of the
five axes are not a days problem at any
price: **surface** (TLDR's 1.1M readers, Elicit's 2M-researcher product,
Anthropic's 176.9k-star ecosystem) and **speed at scale** (TLDR ships five
times a week to a list two orders of magnitude larger than alexandria's).
No amount of engineering days between now and Oct 13, or Oct 13 plus any
reasonable delay, closes a distribution gap that size. Those two axes move
with calendar time and compounding, not sprints.

- **Option A — Oct 13 becomes conditional on the score.** If "a five"
  means the full comparison-set average across all five axes, this is not
  achievable by any date in weeks; it is a distribution problem measured
  in months to years, and naming Oct 13-plus-N-days as conditional on it
  would just be a slower version of the same overclaim decision 11
  objects to. If "a five" instead means the axes alexandria actually
  controls today, accuracy, judgment, and an honestly validated library,
  brought to full and demonstrated as holding for more than one issue
  (so a clean week reads as a floor, not a lucky one-off), that is
  plausibly a 2-sprint problem: this sprint's items 2-5 land clean
  (5 engineer days, unchanged from before item 1 was added, since item 1
  is a same-week security fix that does not add engineer-days to this
  count), then one more sprint's digest repeats clean under
  the same checklist (another 5 days). Call it **10-14 engineer days,
  landing a conditional launch in the last week of October**, with the
  explicit caveat that the surface and speed axes still would not read
  as a five against the named comparison set, only the axes the gate's
  own language ("the product is the content") was actually about.
- **Option B — phased launch.** Free surfaces (the digest and the public
  site) ship 2026-10-13 as already planned; PR #23 already builds most of
  this, so the added cost is close to zero beyond what is already in
  motion. The $20 paid spine's gate opens only once the skills-repository
  side of the score reaches a five, meaning double digits of validated
  skills, not two. At the current Tuesday cadence (one draft skill a
  week, one validated so far), reaching a credible double-digit library
  (per docs/market/report-2026-09.md §7's own bar for the tier) is
  roughly **8-10 more weeks, mid-to-late November**. At a raised cadence
  (a second weekly extraction session, adopted this triage as a
  charter-and-workflow proposal in docs/ideas.md, conditioned on staying
  honest rather than padded), it is plausibly
  **4-6 more weeks, mid-to-late October**, contingent on the ADR-13
  panel or an equivalent honest check existing to validate them, since
  "validated" cannot mean "shipped fast" without becoming exactly the
  padding decision 11 warns against.

Both options keep the digest free and public on Oct 13 either way; the
only thing either option gates is whether the $20 spine (or a broader
"launch") is allowed to call itself proven on that date. Your call.

## Domain (your purchase, per decision 11)

Decision 11 named a real domain as a release requirement. vision.md's
phase-2 plan already budgets roughly $12/yr for this and the launch
runway has no domain line item yet. Three candidates, none checked for
live availability this run (a registrar check takes you thirty seconds
at purchase time and this run has no way to query one honestly):

1. **alexandria.ai** — the direct brand match, and the TLD the product's
   own category (AI research and orchestration tooling) expects. Likely
   the most expensive or most likely already held of the three; worth
   checking first since it is the best outcome if available.
2. **tryalexandria.com** — the standard fallback shape when a bare brand
   domain is unavailable or priced beyond a $12-20/yr budget; cheap,
   almost certainly available, no brand confusion.
3. **alexandria.sh** — ties the domain to the audience the skills tier
   actually sells to (agent builders, the same crowd agentskills.io's
   own `.io` choice targets) and echoes a shell/tooling register that
   fits "directly applicable orchestration tools," the product's own
   differentiation line. A secondary, more distinctive option if `.ai`
   is gone.

Whichever you buy, the two Vercel/Clerk items already pending above still
need the domain attached once it exists; not a new blocker, just a
dependency to sequence after purchase.

## Coming-soon and empty-surface audit (per decision 11)

Every "Coming soon" string and every surface that renders empty on `main`
today, found by reading `site/app` directly, not by walking the deployed
site (there is no deploy yet). Each row states what removes it honestly,
not just what hides it.

| Surface | What's there today | Removal path |
|---|---|---|
| `/pricing`, both tier pills | Two "Coming soon" pills gate the only calls to action on the page, on top of stale $10/$30 tier copy | PR #23 (merged) fixed the tier copy to free-plus-$20 but left both pills in place on purpose, as the insertion point for email capture. PR #26 (open, draft) now wires real email capture into both pages; once it merges these pills should come down as part of that same change, not linger as leftover copy over a feature that now exists. |
| `/pricing`, "Routines & automations (coming soon)" bullet | Listed as part of what the $20 tier includes, not built | Two honest options: build routines before listing it, or remove the bullet from the tier's feature list until it exists and add it back once real. The second is nearly free and should not wait on a sprint slot. Still open as of this triage. |
| `/routines` | Entire page is "Coming soon." with no other content | Same as above: either build the feature, or remove the page and its nav entry until there is something behind it. A standalone page that says only "coming soon" is the clearest example of what decision 11 named. Still open as of this triage. |
| `/library` (archive) | Renders zero issues on `main` today, because `listIssues()` reads a gitignored directory with nothing checked in | PR #23 (merged) fixed this with one real checked-in issue fixture. Its own PR body already names the next gap: the archive still needs to read the live `digests` table so future weeks do not require the same manual git-history recovery every time; that is a proposed ledger entry (docs/ideas.md, engineer agent), not yet built. |
| `/skills` | Renders real content, not empty, but lists exactly one skill against copy that promises "the best techniques the research has produced" | Not a coming-soon page, so not in scope of this audit's literal ask, but the same honesty problem in substance: this sprint's item 5 (validation extended to both gold skills) is the fix in progress; the receipts-rendering item that would surface it on the page itself carried to sprint 2026-09-28 (see revision 3 note). The market agent's own read (report-2026-09.md §6) already calls this "a promise, not a product" at n=1. |

Four items were flagged as literally empty or "coming soon." Two now have
a merged fix (`/pricing` tier copy via PR #23, `/library` via PR #23) or
an open one close behind (`/pricing`'s pills via PR #26). Two (the
routines bullet and page) still have no build dependency at all and could
be corrected as a copy-only change whenever an engineer session has a
spare few minutes, ahead of any sprint slot.

## Triage memo: the closing all-hands, 2026-09-18 night

One line per seat's ask (docs/allhands/2026-09-18-close.md), decided or
deferred-to-owner, and why. Seats with no explicit ask (ExO's floor
statement named one, folded in below) are omitted.

1. **Engineer** — "merge #24 or say which sprint file is live." Decided:
   revision 3 of sprint-2026-09-21.md (this file's companion) is the live
   plan as of this triage; it becomes binding on your merge of PR #24,
   same as every sprint.
2. **PM (self)** — "the decision 11 ruling." Decided provisionally: the
   phased gate (Option B), pending your veto. See "Release-gate
   reconciliation" above.
3. **OKR** — "the written decision 11 ruling, so October's KR1 has one
   target." Decided provisionally, same ruling as above; the OKR seat's
   own Oct 1 check-in is the next point it gets re-confirmed against
   evidence.
4. **Market** — "whether positioning and pricing claims stay frozen until
   decision 11 resolves." Decided: yes, frozen, since the provisional
   ruling could still be vetoed and a published price claim is harder to
   walk back than a ledger entry. This is a backlog/schedule call within
   PM authority, not a pricing decision itself.
5. **ExO** — "the workflow-scope PAT decision." Deferred to owner: this
   is a GitHub App installation permission, a real authority question
   (per decision 4's carve-out for what the owner alone reserves), not
   something decidable by any agent. Tracked above as items 5 and 13.
6. **Security** — "a decision on the digest-history rewrite." Deferred to
   owner: rewriting public git history is disruptive (force-push, breaks
   two in-flight branches and any existing clones) and irreversible in
   practice; squarely the kind of call decision 4 reserves. Tracked above
   as item 4.
7. **Skill** — "the decision 11 ruling, and whether the failing trigger
   case gets fixed before launch or ships red." Decision 11: same
   provisional ruling as above. The trigger case: decided, fix it on the
   seat's normal Tuesday cadence (docs/ideas.md, accepted this run).
8. **Frontend** — "ten minutes of the owner's eyes on the new email
   capture and live metric." Deferred to owner: her attention is the ask
   itself. Tracked above as item 12.
9. **Research** — no decision needed; its one ask (direct Neon access)
   was already satisfied before this triage.
10. **Finance** — "the Claude subscription's monthly figure." Deferred to
    owner: it is a real dollar figure, squarely money, decision 4's other
    carve-out. Tracked above as item 11.
11. **Sales** — "merge PR #22." Merged by you since this triage started
    (no further action). Its three named morning triggers, decided
    separately: the multi-seat Stripe question is already a proposed
    ledger entry inside PR #22's own docs/ideas.md addition, no new action
    needed; sending the first ten outreach notes is deferred to owner
    (item 10 above, "you send, per the law"); the Left-Behind Index page
    is decided (accepted, docs/ideas.md, this run), since greenlighting a
    page build is a product/backlog call
    within PM authority, not money, a secret, or purpose.

## Deploy action owed: the triage fix (engineer, 2026-09-19)

Added by the engineer seat under the owner's URGENT dispatch of 2026-09-19,
which directed this seat to write the deploy command into this file. This is
the one exception to the rule that the engineer seat never edits
`docs/sprints/`; it is append-only and the PM should treat it as a handover
note, not as planning.

**Merging the PR does not deploy anything.** `docs/scaling.md` states the
current CI/CD honestly: "Push to main, `modal deploy` by hand". Modal runs the
last deployed version of the app, so the tier-fairness fix in
`pipeline/triage.py` sits inert on `main` until someone runs:

    modal deploy pipeline/triage.py

Owner's or chair's action, dated 2026-09-19. Until it runs, the daily 12:00
UTC triage cron keeps executing the old inverted `ORDER BY` and the arXiv
firehose keeps going unread.

Two things to check in the first run's logs afterwards, both new in this
change and both one line:

1. `queue: tier <t>: <n> waiting, oldest <date>` for every tier. The `oldest`
   date on tier `a` is the real expiry deadline for the backlog, which
   `docs/product/triage-capacity.md` could only estimate.
2. `triaged <n> papers ... (a=..., b=...)`. More than one tier in that split
   is the acceptance evidence. One tier means the inversion is back.

Related and separate: research's PR #42 adds `cs.CR` to `sources.yaml`. The
chair redeployed ingest on 2026-09-19, so that one flows with the next ingest
deploy and needs no action here. The two changes are independent, but `cs.CR`
is inert without this one, since new tier `a-low` papers would queue behind
the same wall.

While the logs are open, `modal app logs alexandria-triage` also answers the
open throughput question: the 429's body names which Groq limit binds, and
`docs/product/triage-capacity.md` §"What would actually raise throughput" says
what to do with each possible answer.

## Owner action, 2026-09-24: the Moonshot key as a Modal secret (ADR-32)

The press moves to Kimi K2. The pipeline reads MOONSHOT_API_KEY from
a Modal secret named `moonshot`. Only the owner holds the key (it is
the same key HQ stored as the GitHub secret OPENROUTE_API_KEY, which
is write-only). One terminal command, paste the key when prompted so
it never appears in a transcript:

    modal secret create moonshot MOONSHOT_API_KEY=<paste>

Then the chair deploys and prints. Finance: Moonshot usage is a
direct alexandria cost from this date, roughly $0.05 an issue.

## Press recovery: your one check, and what the chair runs (engineer, 2026-09-24)

Added by the engineer seat under your urgent dispatch of 2026-09-24,
which directed this seat to write the one-click check into this file.
Second use of the same narrow exception as the triage-fix note above:
append-only, a handover note, not planning. The PM should treat it as
such.

### 1. The one-click check only you can run

**Did Monday's 15:00 UTC schedule fire at all?** The repo cannot answer
this and neither can the Modal CLI. `modal app logs alexandria-weekly`
shows no output for 2026-09-21, and no-output is the same value for "the
container never started" and "the container started and died before its
first print". Schedule history lives only in the dashboard.

One click:

> **https://modal.com/apps/alexandria-weekly** → the **weekly** function
> → the **Schedule** or **Runs** tab → look for an entry dated
> **Monday 2026-09-21, 15:00 UTC**.

Three possible answers, and what each one means:

- **A run is listed and it failed.** Then the 404 is the whole story,
  this PR fixes the class, and nothing further is owed.
- **No run is listed.** Then there is a second, independent failure:
  Modal did not fire a cron it was deployed with, and the deployed
  version (v31) is not doing what the code says. That is a new incident,
  and it is the more serious of the two. Tell the chair and it gets its
  own register entry.
- **A run is listed and it succeeded.** Then something wrote nothing and
  reported success, which is incident 8's pattern again and the worst of
  the three answers.

Please note which one it is. It is the difference between one bug and
two, and this PR only fixes one of them.

### 2. Decision 2 is closed: you took it, and the press fits again

This section asked you to choose between shortening the generator prompt,
splitting the issue across several requests, and paying Groq. You chose
a fourth thing the same day, in ADR-32: the press writes on Kimi K2
through the Moonshot account you funded. This PR is that wiring, and the
arithmetic is no longer a complaint:

    kimi-k2.6: prompt 9865 + payload 20205 + output reservation 6000
    + envelope 32 = 36102 tokens against 222822 usable
    (262144-token context less 15% margin); fits, headroom 186720

Nothing was trimmed to reach that. The payload caps and the 6,000-token
output reservation are the same numbers main has carried since they were
set, so the issue Kimi writes is the full-size issue.

**One correction you need, and it is the kind that costs a week.** ADR-32
names the model "Kimi K2", and the obvious model id, `kimi-k2`, was
discontinued by Moonshot on 2026-05-25. A press pointed at it would
answer 404, which is incident 24 happening again on a new provider in its
first week. The live 256K general model is **`kimi-k2.6`**, and that is
what this PR uses. `kimi-k2` is recorded as withdrawn so nothing can
point at it by accident.

**Cost, for finance.** $0.0526 an issue at list price, worst case, with
the output reservation spent in full and no cache hit. That is 52 issues
a year for about $2.70. It matches what ADR-32 told finance to expect.

The two $0 improvements this section proposed are still worth doing and
neither is urgent now. A shorter generator prompt is the writer seat's
call whenever she next opens that file. Splitting the issue across
several requests is in the ledger, and its real value was never the
token count: it is that a per-section request survives the next ceiling
change too.

### 3. Correction to the dispatch: a dedicated Groq key would not help

Your dispatch offered "either the press gets its own key, or the press
runs when the crons are idle". The first option does not work, and the
reason is one sentence on Groq's rate-limit page: "Rate limits apply at
the organization level, not individual users." A second key on the same
account draws on the same 8,000 TPM as the five crons already do. Only a
separate Groq organization or the paid plan changes the number.

So this run took the second option. The press moves from Monday 15:00
UTC to **Monday 09:00 UTC**, two clear hours ahead of the earliest daily
cron and well outside the contested 11:00 to 15:00 band. It is also the
better editorial slot: 09:00 UTC is 5am in New York, so the issue is in
a reader's inbox before the working day, and the week it covers ended
the previous night, so nothing is half-ingested.

**No action owed from you on this one**, beyond knowing the send time
moved. ADR-32 has since retired the reason: the press has its own
provider and its own prepaid account, so it no longer competes with the
daily crons for anything. The slot stays at 09:00 on editorial grounds,
which were always the better argument. The issue covers the week that
ended Sunday, and 09:00 UTC is 5am in New York, so it arrives before the
working day rather than in the middle of it.

### 4. What the chair runs after this PR merges

Merging deploys nothing; Modal runs the last deployed version. Two
commands, and the first is yours because only you hold the key.

**You, once.** Paste the key at the prompt rather than typing it into the
command line, so it never lands in a shell history or a transcript:

    modal secret create moonshot MOONSHOT_API_KEY=<paste>

No agent creates this secret, no agent reads it, and the value appears
nowhere in the repository. `pipeline/weekly.py` references the name and
nothing else.

**Then the chair**, in order, stopping at the first failure:

    python3 pipeline/budget.py \
      && modal run pipeline/weekly.py::preflight \
      && modal run pipeline/weekly.py \
      && modal deploy pipeline/weekly.py

The middle two are the smoke test that
docs/agents/runtime-changes.md requires: this change adds a secret the
run reads, and that law says the next cron is never the first execution
of new machinery. `preflight` asks both providers whether the models
exist and prints what the request would cost. The manual `modal run`
prints a real issue. Only then does the deploy install the schedule.

If the secret is missing, the run does not die on a stack trace. It says
which environment variable is absent, which Modal secret provides it,
and the command above, and it emails you.

One optional secret, no action needed for it to work: `PRESS_ALERT_TO`.
Unset, press alarms go to the Gmail address the `Gmail` secret already
holds, which is yours. Set it if you would rather they went elsewhere.
