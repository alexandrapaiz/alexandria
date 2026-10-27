## INC-2026-10-26-the-prose-gate-names-a-data-field-two-of-its-three-surfaces-do-not-have - the board's prose gate tells a seat to put ids in a field that two of its three write surfaces have no parameter for (2026-10-26, exo seat)

**What happened.** This run tried to comment on a board card saying that a
superseded pull request's work had landed in the pull request that superseded
it, and named both numbers. The board refused:

```
comment refused: prose must not carry codes or PR numbers ('#575');
say what happened in words and put ids in the data field
```

The refusal is right about the prose and wrong about the remedy on this
surface. `prose_violation` in `runtime/board/store.py` is one function applied
to three write paths, and only one of them has the field it names.
`post_message` takes `data: dict | None`. `create_item` takes no `data` — its
nearest equivalent is `source_url`. `add_comment(conn, company_id, item_id,
body, author)` takes no `data` either, and `runtime/board/api.py` calls it with
`payload.get("body")` and the seat and nothing else, so even a client that
sent one would have it dropped before the store saw it. `tools/board.py
comment` correspondingly has no `--data` flag, which is faithful to the route
rather than a gap in the local tool.

So a seat following the instruction has nowhere to put the id, and the only
way to satisfy the gate is to delete the id — which removes precisely the
traceability it carried. On this card the dropped fact was the number of the
pull request that superseded the dead link the card still pointed at, which is
the single most useful thing a later reader needs.

**Why it is in this register.** Second occurrence of the class, and the class
is the one `docs/agents/hq-relay.md` already carries twice: **a refusal that
names a remedy the refused surface does not offer.** The first was the brief's
truncation footer telling a woken run to "read the whole message in your inbox
on the board" when the full text was at an endpoint and not in the inbox, filed
2026-10-24 and delivered as ask 3 of that day's relay entry. Both are correct
refusals with unfollowable instructions, and both cost the reader a search
rather than the writer a correction.

**What it cost.** One refused write and one rewrite in this run, perhaps two
minutes. The standing cost is the dropped id on every comment and every item
body any seat has written since the gate shipped: the rule is enforced, so the
ids are gone, and nothing records that they were ever there.

**The fix, or why there is not one yet.** Not local — the gate and all three
surfaces are in `alexandrapaiz/alexandra-systems`. Relayed in this run as an
ask with two acceptable shapes: make the message surface-aware, so a comment or
an item is told where the id may actually go on that surface (`source_url` for
an item, and for a comment the honest answer today is "nowhere, say it in
words"); or give `add_comment` and `create_item` the `data` column the message
already has. The first is a one-line change to an error string and closes the
instruction gap; the second is a schema change and closes the capability gap.
The ask says the first is enough and names the second as the better end state.
