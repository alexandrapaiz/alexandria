# The board

The company board is `board.libraryofalexandria.dev`. It holds every company
Alexandra Systems runs, and this repository is the `alexandria` company on it.
The board is the state of the work: items in columns, inside a sprint, with the
run reports that touched them beside them.

It is the owner's server, on the host. Nothing in this repository stores board
state. What is here is the door a run on a GitHub runner uses, which is
`tools/board.py`.

The law is `docs/standards/pm.md` §14, the owner's directive of 2026-09-27, and
the decision that follows from it is `ADR-2026-09-28-board-client` in
docs/decisions.md.

## Two doors, one board

| Where the run is | How it reaches the board | What the runtime sets |
|---|---|---|
| The host, under Temporal | the `asc-board` MCP server | `ASC_SEAT`, `ASC_COMPANY` |
| A GitHub runner, under Actions | HTTP, through `tools/board.py` | `BOARD_API_URL`, `BOARD_RUNTIME_TOKEN` |

Both doors carry the same permission line. A seat creates items, moves them,
comments on them and reads them. A seat never creates or renames a company, a
sprint, a column or a view. `tools/board.py` has no command for any of those
four, which is how the line is enforced on this side of the wire rather than
only trusted.

## What a seat does with it

Read it first. The board is the answer to "what is the state of the work," and
it is a better answer than twenty open pull request titles.

```bash
python3 tools/board.py show                      # the whole board
python3 tools/board.py show --seat engineer      # one seat's items and runs
python3 tools/board.py show --json               # the same state, for an agent
python3 tools/board.py get --id <uuid>           # one item, with comments and runs
```

Then write as the work happens.

```bash
# start work: the item moves, by column name rather than by uuid
python3 tools/board.py move --id <uuid> --column "In progress"

# no item for the work? make one, which pm.md §14 requires rather than permits
python3 tools/board.py item --title "Drain the reading queue" --horizon now

# ship: say where it went
python3 tools/board.py comment --id <uuid> --body "shipped in #127"

# the run's last step, once
python3 tools/board.py report --status success
```

Every write takes `--dry-run`, which prints the exact payload and posts
nothing.

## The run report

`report` is what a seat's final workflow step calls. It takes the one thing the
step alone knows, GitHub's `job.status`, and derives the rest: the seat from the
workflow name, the company from the repository name, the run url from
`GITHUB_RUN_ID`, the trigger from `GITHUB_EVENT_NAME`, and the report's one line
from the first bullet of the pull request opened on this branch. That is why the
step is one line in twelve identical workflow files.

It never fails a run. A board that refuses a report prints `::warning::` and
exits 0, because a red job for an undelivered notification is a lie to every
reader of `gh run list`, and the PM's standup reads run health off exactly those
statuses. `INC-2026-09-26-run-report-dash-echo` is six engineer runs marked
`failure` for precisely that mistake in the step this one replaces.

**Reports cannot be corrected.** The board's server answers PATCH, PUT and
DELETE with 501, so a posted report is permanent. Call `report` once, at the
end, and use `--dry-run` when you want to see it first.

## The API, as the live board answers it

Six routes. `$BOARD_API_URL` and `$BOARD_RUNTIME_TOKEN` are in every seat run's
environment; the values are Actions secrets synced from Infisical and belong in
no file.

| Call | Requires | Notes |
|---|---|---|
| `GET /api/health` | nothing | `{"ok": true, "companies": 6, "token_configured": true}` |
| `GET /api/board/<company>` | bearer | columns, the open sprint, items, runs |
| `GET /api/items/<id>?company=<name>` | bearer, `company` | adds `comments` and `runs` |
| `POST /api/items` | `company`, `seat`, `title` | `horizon` is `now`, `next` or `later`; column defaults to the first |
| `POST /api/items/<id>/move` | `company`, `seat`, `column_id` | see below |
| `POST /api/items/<id>/comments` | `company`, `seat`, `body` | |
| `POST /api/runs` | `company`, `seat` | every other field optional: `repo`, `trigger`, `started_at`, `ended_at`, `turns`, `model`, `exit`, `pr_url`, `run_url`, `report`, `item_ids` |

Two places the live board differs from pm.md §14's examples, found by calling
it on 2026-09-28 and reported to the owner rather than patched into the
vendored standard:

- **A move needs `seat`.** The documented example sends `company` and
  `column_id` only, and the board answers `400 company and seat are required`.
- **A move takes only `column_id`, and it must be a uuid.** Naming the column
  gets `400 column_id is not a uuid: None`, so every mover has to read the
  board first to turn `"In progress"` into its id. `tools/board.py move` takes
  the name and does the lookup.

One smaller quirk worth knowing before it wastes an hour: `GET
/api/board/<company>` answers `404 no such route` if the path carries any query
string at all, while `GET /api/items/<id>` requires one. The client sends each
the only way that works.

## What is gone, and why it was here

Until 2026-09-28 this file described a board of our own: an append-only log of
JSON events on a dedicated `board` ref, folded into `board/state.json`, with
views on `main` in `board/views.json` so that only the owner's merge could add
one. It was built that way for one reason, written into its own docstring: the
only database credential a seat's run held was `NEON_RO_URL`, read-only on
purpose, so there was nowhere a seat could write that was not either the
production corpus or `main`.

That reason ended on 2026-09-27. The store is deleted rather than kept as a
fallback, because two boards means every seat has to know which one the PM's
ceremony reads, and the first time they disagree the answer is whichever one the
reader happened to open. The history is in git and the reasoning is in
ADR-2026-09-26-board, which now carries a superseded banner instead of being
removed.
