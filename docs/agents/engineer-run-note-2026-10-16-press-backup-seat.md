# Engineer run note, 2026-10-16 (message dispatch, press backup seat)

This file is the first commit of the run, pushed before the work, so the
pull request exists even if the session dies at turn 90 (incident 3).

Dispatch: a second handoff from the chair's hq-console, addressed to this
seat, carrying the owner's second instruction for alexandria today. When
the press's provider refuses, reroute to Sonnet on her subscription,
because an issue that skips a Monday costs more than a model swap.

The constraint that shapes the design: the Modal pipeline can hold API
keys only, so Sonnet on the owner's Claude subscription cannot run there.
It runs on the host, where every seat already writes with Claude Code on
that subscription. So the fallback is not another provider inside the
pipeline. It is a seat.

A sibling run of this same dispatch is live on PR #312
(`alexandria-engineer/2026-10-16-message`), building the pipeline half:
provider fallback inside the press and a board post naming the provider
that wrote the issue. This branch is the host half and does not touch
`pipeline/llm.py`. Merge order and the shared files are named at the top
of this run's pull request.

Planned, in order:
1. A failed-run event on the board, posted by the press when it cannot
   write, naming the ISO week it failed on.
2. A press-backup seat on the roster: a manifest with its secrets named
   and never valued, woken by that event, whose only job is to write the
   named week's issue from the corpus through the library's own tools,
   hold it to the voice check, and send it down the same mail path.
3. A rehearsal that proves it: this week's issue written by the seat's
   own path, with sending held, for the owner to read beside the
   writer's side-by-side.
