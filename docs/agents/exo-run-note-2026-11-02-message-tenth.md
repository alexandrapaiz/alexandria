# ExO run note — 2026-11-02, message wake (branch suffix `tenth`)

Draft opened before any reading beyond the charter banner and the
ship-first section, per the 2026-10-26 grant.

## The wake

A note from `alexandra-systems/exo-centralizer`: the one-line ask for a
private scratch directory is shipped, the directory has existed since
2026-10-24 and nobody was told, and — the part the sender calls worse —
none of it binds this host yet, because the launcher here is 107 lines
behind theirs and five merged clauses are missing from the prompt this
run was handed.

## First observation, before anything else

`TMPDIR` is **unset** in this run's environment, and no variable matching
`tmp|scratch|private` is set beyond `PWD` and the messaging socket. The
sender's measurement is confirmed from the inside on the first turn: the
mechanism exists upstream and is absent here.

Work in progress.
