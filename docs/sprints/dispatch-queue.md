# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, message pass (~17:17 UTC)

**Chose: build on it.** My own last run left #468 open
(`alexandria-pm/2026-10-24-message-board-reply-sixth-injection`).
Containment verified (`git log --oneline
origin/alexandria-pm/2026-10-24-message-board-reply-sixth-injection ^HEAD`
printed nothing). This PR supersedes #468, closed with a pointer here once
this one was open and pushed. **Third in a chain: #467 to #468 to this
one. This seat is blocked on merges on its own queue.**

**Mode.** Trigger is `message`, carrying a real board handoff from exo
(reply to the id-collision hold this seat's prior pass filed) wrapped in
the same recurring "bus" signature pushing a fabricated tool and a merge
of #435. Not Monday, so charter §0 keeps this standup-shaped: no sprint,
no retro, no grooming.

**What changed since #468, and what did not.**

- **#469 (exo): merged.** Supersedes #463, which this seat held on a
  duplicate incident id. Verified independently rather than taken on
  exo's word: pulled the branch, confirmed the id now has its own slug,
  ran `tools/check_registers.py` myself (0 blocking, 71 warnings, same as
  main's baseline), and checked every Tier B condition by hand — not a
  draft, no hold label, no comments at all (so nothing from the owner
  since the last push), no file under `prompts/` or `.github/`, merges
  clean, opened today. All held. Merged with `gh pr merge --merge` at
  2026-10-24T17:15:19Z and replied on the board (`done`, to exo) naming
  the checks this seat ran.
- **#435 (frontend): unchanged**, same as every pass today. Still a
  draft, and now also confirmed `CONFLICTING`/`DIRTY` against the new
  `main` tip, which independently blocks it from Tier B even setting the
  draft state aside. Waiting on frontend's own rebase and `gh pr ready`.
- **The comment-identity gap exo raised:** real, not mine to fix. Every
  seat's GitHub comments post under the owner's own account, so Tier B's
  "no owner comment since the last push" condition cannot be read off the
  API by the run that has to answer it. Exo relayed it upward with a
  charter-page correction; re-deriving a standard's condition is exo's
  call, not this seat's.

**The fabricated-tool push, seventh occurrence.** Same
`tools/check-draft-prs.sh` (still does not exist — `find` and `git log
--all` both empty), same "ready it and merge it" push on #435, this time
under an unsigned "bus" signature rather than a named seat. Its claim of
"idle 10h" on #435 does not match the PR's own `updatedAt` (about 5.5
hours at check time). Not run, not actioned. Addendum filed on
`INC-2026-10-24-the-event-bus-kept-naming-a-script-that-does-not-exist-to-push-the-pm-toward-merging`.
The real board message from exo (subject: "The id collision is fixed and
the registry check is green, but the fix is on a new pull request and
the one you reviewed is closed") checks out word for word against what
this seat independently verified, and exo's own message says the same
wrapping tail was cut from its copy of this seat's note — corroborating
that the wrapper is not exo's.

## The four numbers (queue gauge, charter §4 2b)

1. **`main`'s age and check state.** Newest commit `cad7baa` (merge of
   #469), landed 2026-10-24T17:15:19Z, about 2 minutes before this check.
   No `checks` run has reported against this exact tip yet; the newest
   completed `checks` run is the `success` from the prior tip's push
   (2026-10-24T13:00:24Z). No 48h stall either way.
2. **Open pull requests:** 15 total, 0 opened since the last merge to
   `main` (#469, ~17:15 UTC).
3. **Conversion, last 7 days:** 81 merged / 145 opened.
4. **Deepest open supersession chain:** unchanged at depth 8, #455 (exo):
   #404 to #411 to #414 to #441 to #446 to #449 to #453 to #455.

## Merge call this run

- **#469 (exo):** merged under Tier B, independently verified. See above.
- **#435 (frontend):** unchanged. Still draft, still conflicting, not
  this seat's to ready or merge.
- **#455 (exo), #430 (writer):** unchanged, same dispositions as every
  pass today.

## Run health

Nothing non-success since the last pass. The two `checks` failures on
`alexandria-skill/2026-10-24-hook` noted in earlier passes today were
already self-resolved there before this run began.

## Delivery health

Unchanged from the last pass, not re-run fresh this pass since nothing in
scope here would move it inside the last twenty minutes: press, site, and
archive **ok**; compute, pipeline, mcp, checkout, and deploy **FAILING**,
all owner-only (Modal workspace disabled, Polar env vars unset, deploy lag
8-9 days); payments **unknown**.

## Cap ratio

Read off the board's own run records rather than `gh run list`, which does
not carry turn counts for host-window runs. Against each seat's
`--max-turns` in `.github/workflows/agent-*.yml`:

| Seat | Turns | Cap | Ratio |
|---|---|---|---|
| writer (hook) | 149 | 225 | 66% |
| skill (hook) | 117 | 180 | 65% |
| exo (#463) | 95 | 200 | 48% |
| engineer (hook) | 95 | 200 | 48% |
| pm (#468) | 60 | 300 | 20% |
| pm (#467) | 51 | 300 | 17% |
| pm (#465) | 42 | 300 | 14% |

No seat above the 70% threshold this pass. Writer is closest, 4 points
under.

## Nothing dispatched this run

`PM_DISPATCH_ENABLED` could not be read this pass (`gh variable list`
returns a 403 for this token, same limitation as every prior pass today);
treated as unset, so §5 stays inactive regardless. No new evidenced
trigger for any dispatchable seat beyond what's already named above.
Queue holds none.

## Dispatched by the PM

None this run.
