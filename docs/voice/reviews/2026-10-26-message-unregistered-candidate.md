# The register that answers "has this surface been written for" cannot see a surface it has no row for

**Writer run 58, 2026-10-26, message.** Draft, filling in.

The writer lane's Backlog, This sprint and In progress columns are all empty
again, so the item is the one this run can prove: `check_voice.py candidates`
fails a candidate only when the surface it drafts for already holds a row by
another candidate. A candidate for a surface with no row at all passes, and the
gate then prints the same reassuring line it prints when a run has done the
bookkeeping right.

Yesterday's own run is the instance. Pull request #600 added two candidate files
under `docs/voice/` and never touched `docs/voice/awaiting-her-word.md`.
