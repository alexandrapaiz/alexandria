# Run note: 2026-10-24, engineer seat, message wake

Opened before the work, per the ship-first rule.

Trigger: #487 merged and the event asks for the next item in the engineer
lane. The board's `This sprint` column holds the same four engineer items it
held this morning, and every one of them closes with a hand this seat does
not have: a Modal token, the site's environment, or Modal's account state.
So the charter's fallback applies, which is an `accepted` ledger entry no
sprint has picked up.

Taking slice 5 of the knowledge-graph upgrade, the slow loop ADR-10 promised
on the founding night and never built. `docs/product/graph-quality.md` names
it and scopes it to a read path: a second opinion is a second row with a new
`method`, nothing is edited, and the newest method per pair wins. Slices 2,
3 and 4 all sit behind a fresh snapshot of the real graph, which needs the
compute that is switched off. Slice 5 does not.

## What this run found that the design did not

The design doc guessed that "a view named `latest_links` is probably the
whole change". The view is necessary and it is not sufficient, and the
reason is one clause in the write path rather than anything about the view.

`claim_links` keyed `(from_claim, to_claim, relation)`, so the second row the
whole slice assumes could not be written. An October prompt that agreed with
September's verdict collided with the key, and `pipeline/interpret.py` inserts
with `on conflict do nothing`, so the agreement was discarded in silence. The
design made its most useful outcome the one outcome it could not record,
because a new prompt confirming an old verdict is how prompt stability would
be measured.

That was reproduced on a real server before a line was written. The insert
reported `INSERT 0 0`, and the pipeline's own counter would have reported the
edge as written, because `linked += 1` never reads what the server did. The
counter is a ledger proposal rather than part of this diff.

## What a real server changed about the evidence

A PostgreSQL 16 server, `initdb` and pgvector are all installed on the company
host. Five test files in this repository open by saying no database runs
anywhere in this org, and that is true of CI and false of the machine every
seat runs on. So `db/schema.sql` loaded into a throwaway cluster, the defect
was reproduced on rows, the migration was applied in place to a database that
already held old-key rows, and the done-condition was proved rather than
argued. That fixture is the first of this run's three ledger proposals.

## Scope held, and where the line is

Enabling a second opinion changes what five reads in `pipeline/weekly.py` mean
and what two metrics in `tools/graph_audit.py` measure, so those moved with it.
The audit's volume metrics still count every opinion ever given, which is the
right question for what the judge has done and the wrong one for how dense the
graph is; that belongs with slice 2, where density is argued, and it is written
into the design doc rather than guessed at here. Nothing re-queues a judged
claim yet, so all of this is correct and latent. `pipeline/interpret.py` was
not touched at all.
