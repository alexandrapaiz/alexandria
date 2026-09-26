# The board

Our own task manager and run log. It replaces Linear, it costs nothing, and
it needs no account, no API key and no vendor. The owner's ruling of
2026-09-26 (HQ ADR-037 item 1, relayed through the PM's sync session in PR
#113) set three requirements: the store is ours, seats cannot create views,
and every seat run reports onto the board.

Written for the next engineer. Every path, command and number below is real,
and the ones that came from a live call say so.

## Components

| Component | Where | Who writes it |
|---|---|---|
| The views: columns, seats, named views | `board/views.json`, on `main` | the owner, by merging a pull request |
| The state: items and run reports | `board/events/**.json`, on the `board` ref | `tools/board.py`, and nothing else |
| The write path, the read path, the fold | `tools/board.py` | the engineer seat |
| The workflow step that reports | queued in [pending-workflow-changes.md](agents/pending-workflow-changes.md) item 5 | the owner or the chair, by hand |
| Tests | `tests/test_board.py`, 37 of them | the engineer seat |

## Data flow

```
a seat's run finishes
  -> .github/workflows/agent-<seat>.yml, step "Post run report to the board"
     -> python3 tools/board.py report --status <job.status>
        -> derives seat, run id, attempt, branch, PR, one-line result
        -> PUT /repos/{repo}/contents/board/events/run/<date>/<seat>-<run>-<attempt>.json
           with branch=board
                                  the board ref
                                       |
   python3 tools/board.py show  <------+------>  the site, next slice
   (git archive, one subprocess)                (one tarball fetch)
```

The PM and the owner write items the same way, by hand:

```bash
python3 tools/board.py item --id board-ui --title "Read-only board view" \
    --status next --assignee frontend
```

## Why the state is not in the two obvious places

**Not in Neon**, which is the project's database of record and would otherwise
be the default. The only database credential a seat's run holds is
`NEON_RO_URL`, and it is read-only on purpose. A Postgres board would mean
minting a writable URL and handing it to all twelve seats, so the price of a
board would be that every agent run could write the corpus. That is an
authority change rather than a storage choice, and it belongs to the owner in
the same way the `workflow`-scoped token on
[pending-workflow-changes.md](agents/pending-workflow-changes.md) does.

**Not on `main`.** A seat may not push to main, so a report would travel by
pull request and appear only after a merge, which is the one moment a board
stops being worth reading. The second reason has a number on it: since
2026-09-25 a push to main runs `deploy-main.yml`, and twelve seats reporting
twice a day would spend 24 production deploys a day against the vendor's
100-a-day limit that HQ incident 5 already cost us a day of production builds
for.

**So the `board` ref, append only, one JSON file per event.** What that buys:

- Conflicts are impossible rather than handled. A run report's path carries the
  run id and the attempt, an item patch's path carries a hash of itself, so two
  writers never address one path. The only retry in the code is for the ref
  moving under a concurrent write, and the API answers that in one round trip.
- Reporting twice is a no-op. The workflow step runs under `if: always()`, and
  a second post of the same attempt prints `exists` and writes nothing.
- The history is the audit. Nothing is ever overwritten, so how an item reached
  `done` is still on the ref, and the current state is a fold over the log.
- It is free and it is ours. A ref in a repository we already have.

The cost, stated plainly: a fold over every event is how you read the board, so
the read grows with the log. At 12 seats reporting twice a day the log grows by
about 9,000 files a year, which `git archive` still hands over in one
subprocess. The day that stops being true, the fix is a rolled-up snapshot file
on the same ref, and the ledger carries it as an idea rather than as code.

This is ADR-9's blackboard, which the pipeline's workers already coordinate
through, pointed at the seats instead of at the papers.

## Why seats cannot create views

The views live on `main`. A seat can edit `board/views.json` on its own branch
and see the result inside its own run, and it cannot show that view to anybody
else, because only the owner's merge puts it on main. That is an enforcement
rather than a convention, and it is the strongest one available to a repository
whose seats all have `contents: write`.

Two smaller gates fall out of the same file. `tools/board.py` has no command
that writes a view. And an item whose status is not one of the columns
`board/views.json` declares is refused before it is written, with the refusal
naming the file, so a seat cannot invent a column either:

```
$ python3 tools/board.py item --id x --status blocked
board: this event was refused:
  status 'blocked' is not a column. The columns are inbox, next, doing, review,
  done, and they are declared in board/views.json on main, so a new one takes a
  pull request the owner merges.
```

Items themselves are open to every seat, and each item event records `by`. That
is a reading of the ruling rather than a quotation of it: the owner named views
as the thing seats may not create, and a seat that cannot file its own
follow-up work would push that work back into prose nobody folds. If she meant
items too, the change is one check in `validate` and one line in this file.

## Commands

```bash
python3 tools/board.py show                     # the board
python3 tools/board.py show --view seats        # grouped by seat, with the run log
python3 tools/board.py show --view runs         # the fleet's last 30 runs
python3 tools/board.py show --json             # the same state, for an agent
python3 tools/board.py show --seat frontend    # one seat's items and runs
python3 tools/board.py report --status success --dry-run   # what a run would post
python3 tools/board.py item --id <id> --status doing       # create or move an item
python3 tools/board.py init                    # create the ref, idempotent
python3 -m pytest tests/test_board.py -q
```

`report` never fails its caller. A board that cannot be written prints
`board: report not posted (...)` on stderr and exits 0, because the board is a
window and not a gate, and a seat's run is not less finished because the report
did not land. `--strict` turns that off, for the tests and for a human
debugging the store.

## Reading it from the site

The next slice is the frontend seat's read-only view. This repository is
public, so the state needs no credential. Both of these were run against the
live ref on 2026-09-26.

**One request for the whole board**, which is the one to build on:

```
GET https://codeload.github.com/alexandrapaiz/alexandria/tar.gz/refs/heads/board
```

1,029 bytes gzipped for the board as it stands. Untar it server-side, keep the
files under `board/events/`, and fold them with the same rules
`tools/board.py fold` uses: items are last-write-wins per field ordered by
`at`, runs keep the latest per seat and the whole list in order.

**One file, if you want a single event:**

```
GET https://raw.githubusercontent.com/alexandrapaiz/alexandria/board/board/events/run/2026-09-26/engineer-36208446311-1.json
```

Do not build the UI on `GET /repos/{repo}/git/trees/board?recursive=1` plus one
request per file. It works, and unauthenticated GitHub API calls are limited to
60 an hour per address, which a page that folds a thousand events exhausts on
its first render.

The views come from `board/views.json` on main, which the site already has in
its own checkout, so the UI reads its columns from the file rather than from
the ref.

## The event shapes

A run report, which is the owner's list of seat, run id, PR and result:

```json
{
  "at": "2026-09-26T01:38:57Z",
  "attempt": 1,
  "branch": "engineer/2026-09-26-board-store",
  "kind": "run",
  "pr": 115,
  "result": "the board's own store, and every run reports onto it",
  "run_id": "36208446311",
  "seat": "engineer",
  "status": "success",
  "url": "https://github.com/alexandrapaiz/alexandria/actions/runs/36208446311"
}
```

An item event, which is a patch. Only the fields it names change, so a move is
an event carrying a status and nothing else:

```json
{
  "at": "2026-09-26T01:39:18Z",
  "assignee": "frontend",
  "by": "engineer",
  "id": "board-ui",
  "kind": "item",
  "note": "queued by the PM in #113; reads the board ref, see docs/board.md",
  "status": "next",
  "title": "Read-only board view on the site"
}
```

`status` must be one of `board/views.json`'s columns. Every other field is
free text, and `ITEM_FIELDS` in `tools/board.py` is the list, so carrying a new
one is one entry there and one line here.

## How it relates to the three surfaces that already exist

The org already coordinates through files, and this one does not delete any of
them. What it changes is which of them holds state that a seat can fold.

- **`docs/ideas.md`**, the ledger. Unchanged, and still the proposal surface
  where agents append and only the owner writes verdicts. The board holds work
  that has been decided, the ledger holds work that has not.
- **`docs/backlog.md`**, which its own first line calls the consolidated board.
  This is the PM's file, rebuilt each Monday during grooming, and it is a
  leverage-ordered read of every seat's proposals. It overlaps this board on
  purpose for now, because migrating it is the PM's call and not this seat's.
  The ledger carries the proposal.
- **`docs/sprints/dispatch-queue.md`**, the PM's queue of who to dispatch next.
  Also unchanged, and also a candidate to become board items later, for the same
  reason and with the same owner.

Until the PM decides, read it this way: the board is where run reports live and
where an item's state is machine-readable, and `docs/backlog.md` stays the
week's ordered narrative. Two surfaces is one too many, and choosing which
survives belongs to the seat that grooms it.

## What this slice does not do

- No UI. The frontend seat has the read-only view, queued by the PM in PR #113.
- No workflow step yet, because no seat can push `.github/workflows/`. It is
  written out ready to apply as item 5 of
  [pending-workflow-changes.md](agents/pending-workflow-changes.md).
- No dependencies between items, no labels, no comments, no due-date alarms.
  Linear has all of them and the board will need some of them. It needs them
  after the first week of real use says which, not before.
