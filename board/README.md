# The board

The task manager and run log that replaces Linear (HQ ADR-037 item 1,
owner's live ruling 2026-09-26). It is ours: no account, no vendor, no
API key, and $0 a month.

Two halves, deliberately kept on different refs.

- **The views are fixed and live on `main`** (`board/views.json`). A seat
  can propose a view in a pull request, but only the owner's merge makes
  one real, which is how "seats cannot create views" is enforced by
  something stronger than a sentence in a charter.
- **The state is append-only and lives on the `board` branch**, one file
  per event under `board/events/`. Every seat run posts its own report
  there through `tools/board.py`, which is the only writer.

`python3 tools/board.py show` prints the current board. The full design,
including why the state is not in Neon and not on `main`, is in
docs/board.md.
