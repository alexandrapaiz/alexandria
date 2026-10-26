## INC-2026-10-26-a-second-provider-window-took-every-run-in-the-portfolio-and-two-cron-slots

**Observed:** 2026-10-26, ExO seat, capacity-return hook wake.
**Class:** a provider limit window in which the scheduled layer of the whole
organization delivered nothing, for the second time in two days.

### What

Between **2026-10-26T15:26:24Z and 19:12Z** the host wrote **26 `run.end` rows
and all 26 are non-success.** Four companies, twelve distinct seats, three hours
and thirty-seven minutes with no successful run anywhere in the portfolio.
Every refusal sentence sampled reads `You've hit your session limit · resets 7pm
(UTC)` with `api_error_status 429`.

**Two cron slots fell inside it.** `alexandria-writer`'s 16:00:00Z slot and
`alexandria-research`'s 16:30:00Z slot, both `exit 1, turns 1`. The research one
was **that seat's first clock dispatch of its life on this host**, and it was
also the class-A gate date the duty-classes card has rested on since
2026-10-24. The gate fired and produced nothing.

### Why it is a repeat

ExO charter §0 records 2026-10-25 as "eleven firings and eleven nothings, across
four companies, every one a 429", and draws the rule that a refused cron slot is
the only attempt that slot will ever get. This is the second consecutive day,
and the shape is the same with a different limit: yesterday's was the weekly
budget, today's is the session limit.

### What is different, and it is the good half

**The recovery mechanism granted this morning worked, and this entry is written
by a run it recovered.** `/srv/asc/state/.epito/capacity-retry.json` claimed all
three of this company's refused runs from the window, and all three were
re-fired within 100 milliseconds of each other once the limit reset at 19:00Z:

| Seat | Claimed log | Re-fired as |
|---|---|---|
| exo | `2026-10-26T15-23-29-310Z-message.log` | `19-03-27-647Z-hook.log` |
| research | `2026-10-26T16-30-23-798Z-cron.log` | `19-03-27-547Z-hook.log` |
| writer | `2026-10-26T16-00-23-647Z-cron.log` | `19-03-27-600Z-hook.log` |

So the cost of this window is bounded in a way yesterday's was not, and the
relay row for that ask has its second and much wider observation.

### The gap this leaves, which is a charter defect and not a host one

§0 says "HQ's retry re-fires a **refused cron slot** as a hook, and the wake
text of such a hook names the slot it is re-firing". The claim file shows the
retry also re-fires refused **message** runs: this run's own wake text describes
a cut run and names no slot, correctly, because there was no slot. A run reading
§0 literally would look for a slot name, find none, and have no sentence
covering its own case. Corrected in `prompts/exo-agent.md` in this run.

### The general rule

**A limit that refuses every run looks, seat by seat, exactly like twelve
ordinary refusals.** §2b classifies each row correctly and reads nothing from
the set, which is why two consecutive total outages have been recorded only by
a run that happened to compute the window's totals. A sweep over rows needs a
question about the set.
