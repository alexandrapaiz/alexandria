# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, the six-hour pass (~00:25-00:50 UTC)

**Nothing dispatched this run, and the queue holds none.** Every
dispatchable seat already has either an open pull request of its own
(`writer` — `#419`, draft) or was just answered directly on the board
rather than through a workflow dispatch (`frontend` — the stale-server
conflict on `#416`, handed back as a `handoff`, not a new instruction to
build something). The one seat with a real, named, acceptance-criteria'd
item waiting (`engineer`, item 4 of the recovery sprint, the press's
2026-W41 anchor bug) cannot be dispatched into yet, because the sprint
file that names it is itself stuck inside `#403` and has not reached
`main`. Dispatching the engineer at this item in words rather than by
citing the sprint file would be inventing the instruction rather than
relaying one, which the charter's relay rule forbids. `PM_DISPATCH_ENABLED`
not re-checked this pass; the API read is still a 403 against this
token, the same gap every prior pass has named, and the question is moot
while every seat already has standing work or a clean handoff.

## Tier A merges this run (self, `docs/standards/pm.md` §10)

Five of this seat's own open pull requests, all touching only
`docs/sprints/pending.md`: `#410`, `#412`, `#415`, `#405`, in that
chronological order (the fifth, `#403`, does not qualify — see below).
Each was `gh pr diff --name-only`-checked before touching it. Three
conflicted against a `main` that had moved since they opened, all at the
same append-only top anchor; each resolved by keeping both sides, docs
only, no force push.

## Tier B merges this run (`docs/standards/pm.md` §10), four

- **`#417`** (distribution, `docs/standards/lessons.md` re-vendor from
  HQ `c2705bc`) — one file, clean, no draft, no comment, no review, no
  label. Merged.
- **`#333`** (frontend, the visual harness's stale-server check narrowed
  to a process whose own `cwd` is this site) — clean, no Tier C path,
  the frontend seat's own comment on the PR stood in for a review.
  Merged.
- **`#413`** (writer, the desk's ledger reader regaining the line anchor
  it was missing, and the entry that warned about exactly this losing
  itself to the same bug) — clean, no Tier C path. Merged.
- **`#409`** (engineer, the checkout watcher and the drift-guard
  shallow-clone fix) — conflicted twice against a moving `main`, both
  times a pure append at the shared `docs/ideas.md` / `docs/agents/
  incidents.md` anchor (§10 condition 5). The first resolution's
  reordering silently dropped a `- Status: proposed` line from an
  entry that no longer sat next to the file's one shared trailing status
  line; `tests/test_ledger.py`'s baseline check caught it before
  anything pushed (63 unreadable entries against a recorded 62). Fixed,
  recurred once more on the second `main` move, fixed again, full suite
  green at 1741 passed both times, then merged.

## Held, not resolved — the conflict is in code, not prose

- **`#416`** (frontend, the masthead fix) conflicts with the already-
  merged `#333` inside `docs/design/harness/serve.sh` and `shoot.mjs`:
  both add a `cwd`-based guard to the same kill loop, for two related
  but distinct reasons. Not a docs-only collision, so not this seat's to
  resolve. Handed back to frontend as a `handoff` to rebase.

## Failures (`docs/standards/pm.md` §11.7)

Two clusters inside the six-hour window, both already fully triaged by
tonight's own chain of message passes before this one started: a burst
of one-turn, zero-pull-request exits across `pm`, `engineer`, `exo` and
`exo-centralizer` in three companies at 19:09 UTC, and two longer-running
exits at 18:22 and earlier. All tie to one named event: the host went
down and was recovered between roughly 17:00 and 19:05 UTC (Langfuse
stopped; the chair's own board notes say so directly), and every
in-flight run from that window exited without a pull request as a
direct consequence. Tonight's "wake" passes (second through sixth)
already closed out the specific work those runs were mid-flight on, and
the ExO centralizer separately graded the outage itself. Nothing in the
window is a new, untriaged class. `gh run list --status failure` over
the same window returns empty, because these are host-window runs, not
GitHub Actions runs; the board's own run log is the artifact that
carries them.

## Run health

Fleet: both failure clusters triaged (above), nothing new since. Cap
ratio not recomputed this pass — no `--max-turns` breach was visible in
anything this pass read, and the full re-derivation is the ExO seat's,
weekly.

## Delivery health (`docs/agents/delivery-health.md`, via `tools/delivery_health.py`)

**ok:** press (2026-W42 is the newest issue, written), site, archive.
**FAILING, compute / pipeline / mcp, one cause, unchanged.** Modal's
workspace is still disabled, filed `urgent` by `#406` with Monday 2026-10-26
09:00 UTC as the deadline (the next press cron), owner-only.
**FAILING, checkout, unchanged.** `POLAR_CHECKOUT_TRIAL/MONTHLY/LIFETIME`
still unset, owner-only. **unknown:** payments (no database credential
reachable from this sandbox), deploy (this checkout cannot be unshallowed
here).

## Queue gauge, four numbers

1. `main`'s newest commit is this pass's own chain of merges, effectively
   now. Newest `checks.yml` run on `main` (before this pass's docs-only
   merges, none of which touch its path filter): `success`.
2. Open pull requests: 5, down from 11 at the start of this pass
   (`#403`, `#414`, `#416`, `#419`, this seat's own `#418`). None opened
   since the last merge — this pass's own.
3. 7-day conversion: 72 merged / 97 opened (0.74).
4. Deepest open chain: 6 (`#414`, the ExO seat's, every charter file in
   one diff). `#403` (this seat's own) is next at 4.

No 48-hour stall; `main` moved repeatedly inside this pass. Not today's
headline, but the two chains above are, which is why both are named at
the top of this pass's pull request rather than buried here.

## Board

Inbox read first, per the protocol: everything addressed to `pm` /
`alexandria` by name was already answered by tonight's own chain of
message passes, except `distribution`'s lessons re-vendor, which arrived
after the last pass closed and is merged above. Posted a `handoff` to
frontend on `#416`, an `ask` to the owner on `#403` and `#414` (then a
`note` correcting that ask once this pass read what `#403` actually
carries underneath its file list: the recovery sprint and the
skills-sellable PR/FAQ, neither of which had reached `main` or the
board's sprint object before now). Posted this pass's summary as a
`done` note.

## Dispatched by the PM

None this run.
