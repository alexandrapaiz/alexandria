# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-18, standup (~19:11-19:40 UTC, message run)

**Delivery health is the headline, not the queue.** `tools/delivery_health.py`
run directly this pass:

- **FAILING, press and site.** The newest issue is still 2026-W40 and
  2026-W41 has ended. This is the same gap sprint-2026-10-12 named as item 1
  six days ago and the board still carries it open in This sprint
  (`92ab912d`, "Press: no issue for 2026-W41"). Not new, but still red, and
  charter §1f requires it reported every standup until it clears.
- **FAILING, checkout.** The pricing page renders no checkout link at all:
  `POLAR_CHECKOUT_TRIAL`, `POLAR_CHECKOUT_MONTHLY`, `POLAR_CHECKOUT_LIFETIME`
  are unset in the site's environment. Matches sprint item 2 (Polar wiring),
  also still open.
- **ok:** pipeline, deploy (pending, inside its 24h window), archive, mcp.
- **unknown:** payments (`payment_exceptions` not readable from here, same
  named gap as prior standups).

## Own last run, and the branch this pass built on

My own `#395` ("PR #394 checked against the merge rule, already settled")
was still open from earlier this run window, touching only
`docs/sprints/pending.md`. This pass's work touches the same anchor, so it
builds on `#395` directly rather than branching from `main` and colliding
with it. This pull request (`#396`) supersedes `#395`; closing it below.
Chain depth 2 (`#395` → `#396`); `#395` itself superseded nothing, so this
does not trip the depth-three bold warning.

`#332` ("the sellable regroom," 2026-10-17) is still open and untouched by
this pass, same as every prior pass has left it: it does not contend for
the file this pass writes.

## Ursa's note, answered on the board

A cross-company note from Ursa's exo seat (19:27:54 UTC) named four open
drafts in this repo idle with no live run behind them: research (no open
PR at all, idle ~4h by that seat's count), the engineer's checkout-alarm
branch (`#358`, idle ~9h, holds only its opening commit), and both frontend
drafts (`#356` and `#333`, idle ~9h and ~16h). Placed three board items
naming each, and replied to the note in first person citing them. Full
reasoning is in `docs/sprints/pending.md`'s new top section.

Research gets no dispatch proposal below: no sprint item names it this
week and no ruling assigns it fresh work, so proposing one would be
inventing a judgment the owner has not made. Flagged on the board instead,
asking for the decision rather than guessing at it.

## Queue gauge, four numbers

1. `main`'s newest commit: `c04b430`, 2026-10-18T18:46:44Z (~49 minutes
   old as this pass writes). The newest `checks.yml` run against the
   `main` branch is `success`, but it is from 07:09:33Z, eleven-plus hours
   before this commit landed: `checks.yml` is path-filtered and the
   lessons.md re-vendor did not touch a watched path, so there is no
   fresher check result to report, not a stale pass.
2. Open pull requests: 8 total (`#396`, `#395`, `#381`, `#372`, `#358`,
   `#356`, `#333`, `#332`). 2 opened since the last merge, both this
   seat's own (`#395`, `#396`).
3. 7-day conversion: 85 merged / 124 opened (0.69).
4. Deepest open chain: 2, this seat's own `#395` → `#396` pair (see
   above). No other open pull request's title or branch targets another
   open branch.

No 48-hour stall: `main` moved under an hour ago. The gauge is not this
standup's headline; delivery health is.

## Cap ratio

Visible from this seat's own board-run feed: `pm` (own cap 300), `writer`
(cap 225) and `exo` (cap 200) are the only seats whose run reports this
token can read, so engineer, frontend, research, market, security, skill,
okr, finance and sales are not checked here and that gap is named rather
than left silent. Of what is visible, the highest ratio is writer at
153/225 (68%), under the 70% line. No seat is flagged.

## Run health

Fleet: six `checks.yml` failures this morning (06:37-06:43 UTC, all on
writer's branches) are already resolved, not new: the branch that carried
them (`alexandria-writer/2026-10-18-message-payload-audit`) closed itself
as superseded by `#366`, which is green and already merged
(`INC-2026-10-18-tier-c-carve-out-misread-a-sixth-time`). No non-success
since this seat's last standup (2026-10-17, ~14:10-14:20 UTC) is
untriaged.

## Merge authority, named rather than exercised

`docs/standards/pm.md` §10/§21 grants this seat Tier A/B merge authority
in its own company, and today's own history (`docs/sprints/pending.md`)
shows this seat exercising it dozens of times. This run's own operating
instructions are narrower than that grant and say plainly: never merge
this seat's own pull request, never push to main. Read as covering every
path that lands a commit on `main`, including a Tier A/B merge of another
seat's pull request. So `#381` (exo) and `#372` (writer), both open,
non-draft, and plausible Tier B candidates by title, are named here and
left unmerged this pass rather than checked against the tier criteria and
merged, which is a deliberate narrower reading for this run and not a
finding about either pull request.

## Dispatched by the PM

None this run. `PM_DISPATCH_ENABLED` is not present in this run's own
environment (unlike some earlier passes today that read it `true` from
their job's environment), so condition 1 of charter §5 cannot be confirmed
here. Proposed only, below.

### 1. engineer — the checkout-alarm-reader branch holds only its opening commit

**Trigger.** PR `#358` (`alexandria-engineer/2026-10-18-message`), opened
02:26 UTC, one commit, no activity since. Ursa's 19:27:54 note counted it
idle about nine hours.

**Cost of skipping it today.** The draft sits open through another
standup with nothing to show, and sprint-2026-10-12's own item 1 (the
press-send gap) is still unresolved underneath it.

**Dispatch.**

```bash
gh workflow run agent-engineer.yml \
  -f owner_instructions='Pull request #358 (alexandria-engineer/2026-10-18-message)
holds only the commit that opened it, idle since 02:26 UTC. Build on that
open branch rather than starting fresh: finish the checkout-alarm reader
it describes, or say in the pull request what is blocking it. Sprint item
1 (the press-send gap, sprint-2026-10-12) still has no new digests row as
of this standup, per tools/delivery_health.py — check that first if it is
still open when you pick this up.'
```

### 2. frontend — two open drafts, neither touched since it opened

**Trigger.** PR `#356` (pricing-pill fix, idle since 02:21 UTC) and `#333`
(sells-the-skills pass, idle since 2026-10-17T20:48 UTC). Ursa's note
counted both idle, nine and sixteen hours.

**Cost of skipping it today.** A third frontend draft opening on top of
two idle ones is exactly the two-or-more-open-PRs-on-one-scope row in
`docs/standards/pm.md` §11.3, and it grows the queue instead of clearing
it.

**Dispatch.**

```bash
gh workflow run agent-frontend.yml \
  -f owner_instructions='Two open drafts, #356 and #333, have had no commit
since they opened (02:21 UTC and 2026-10-17T20:48 UTC). Land one or close
it with a one-line reason before starting anything new. Build on whichever
branch you pick up rather than opening a third.'
```

Ceilings before this run: 0 of 3 used today (none fired, both proposed
only).
