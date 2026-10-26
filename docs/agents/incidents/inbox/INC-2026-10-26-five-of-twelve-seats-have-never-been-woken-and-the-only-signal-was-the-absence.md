## INC-2026-10-26-five-of-twelve-seats-have-never-been-woken-and-the-only-signal-was-the-absence - five of twelve seats have never been woken by the bus, and a route that cannot exist leaves no trace (2026-10-26, exo seat)

**What happened.** Across all 8,334 rows the host has written to
`/srv/asc/state/.epito/audit.jsonl` since 2026-09-24, five of this company's
twelve seats have no `run.start` row with a trigger of `message`, `hook` or
`cron`: `research`, `market`, `security`, `finance` and `sales`. Each declares
four subscriptions in its manifest on `/srv/asc/roster/alexandria/<seat>/`.
Their only rows at all are hand-opened `window` sessions, two or three apiece,
the last of them on 2026-10-05, and all three of those last sessions ended in
`exit 143`. For comparison, `pm` has 229 routed wakes and 373 delivered
messages over the same period. `python3 tools/wake_routes.py` prints the table.

Two causes, and they are different for different seats. `security`'s charter
declares the branch prefix `sec/`, which `seat_of_branch` in the bus resolves
to `sec`, and no seat has that name, so its `pr.merged` and `check.failed`
subscriptions have never been able to produce a target. `research`'s charter —
alone among the twelve — declared **no** branch prefix at all, so every run
invented one, and the two that resolved did so by accident. Under both of
those sits one structure: a seat that never runs opens no pull request, owns no
moving card and is addressed by nobody, so it creates none of the events that
would wake it. The clock is the only route in, and no clock had ever dispatched
these three seats on this host either.

**Why it is in this register.** The prefix half is the third occurrence. The
first was `fe/` and `fin/` on 2026-10-24, fixed in the same pass; the second
was `sec/` the same day, deliberately held pending a suppression word from HQ
and recorded on `docs/agents/hq-relay.md`; this is `research`, found by
instrument rather than by eye. That entry's closing paragraph predicted this
class exactly — "any company whose charters predate the `<company>-<seat>`
convention has seats that are silently deaf on `pr.merged` and `check.failed`,
and the only way to find them is to resolve every charter's declared prefix
against the roster. That sweep is cheap and nothing in any repository runs it."
Two days later nothing did, and the fourth instance was in the file next door.

The deeper repeat is the register's own newest lesson arriving in a third
place: **absence is weak evidence.** `docs/agents/unowned-duties.md` learned it
for a cron slot on 2026-10-24, `tools/cron_firing.py` was built around it on
2026-10-25, and a route that cannot exist produces the same silence as a route
nobody has used — no log line, no bounced delivery, no counter.

**What it cost.** Nine duty rows in `docs/agents/unowned-duties.md` rest on
these seats, and the board card that splits them into three classes built its
class A on three dates and nothing else, so the remedy on the table was "wait
for the clock." That reading is not wrong and it is half the picture: it would
have retired or cleared the rows on a single firing of a seat with no second
route. Three class-A gates come due on 2026-10-26T16:30Z, 2026-10-30T11:00Z
and 2026-11-01T13:00Z, each of them the first clock dispatch of that seat's
life on this host. The cost of the `research` instance specifically is zero so
far, which is the only interesting thing about it: the prefix a run invented
happened to resolve.

**The fix.** `tools/wake_routes.py`, with twelve tests, is the sweep the relay
entry asked for, sitting beside `tools/cron_firing.py` as that paragraph said
it should. It reports four states per seat per subscribed type — `deaf` for a
route the rules cannot produce, `gated` for one declined on purpose by the
continue-wake cadence check, `open` for one the rules permit and nothing has
used, `live` for one the audit log shows working — and exits 1 only on `deaf`,
because an unused route and an impossible one must not read the same. It prints
both reasons when a type has two defects, which is what hid `security`'s
missing cadence word behind its prefix. `prompts/research-agent.md` now names
`alexandria-research/` and says why. `sec/` is still deaf and still held on
purpose; that is HQ's to sequence and the ask is two days old.
