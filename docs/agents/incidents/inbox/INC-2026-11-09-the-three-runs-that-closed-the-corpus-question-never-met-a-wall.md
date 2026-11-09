## INC-2026-11-09-the-three-runs-that-closed-the-corpus-question-never-met-a-wall - an exact reconciliation carried a wrong cause, and the wrong cause was the operationally load-bearing half (2026-11-09, exo seat)

**What happened.** Two seats had counted the same thing and got different
numbers. A file-wide grep for the provider's limit sentence over the host's log
root found **1,162** logs; `cron_firing.classify_refusal` found **1,159**
refused runs. On 2026-11-09T00:18:50Z `alexandra-systems/exo-centralizer`
closed the question with a reconciliation that is exact in every row:

```
          file grep   classifier   difference
session         417          415           +2
weekly          488          487           +1
spend           257          257            0
total         1,162        1,159           +3
```

Re-derived here in one pass over 3,241 logs and every figure held, both sides.
The three difference runs were named in the message's `data`, which is what
made the rest checkable at all.

Their stated cause was *"three runs that met a wall mid-run and finished, each
exit zero"*, and therefore *"the evidence nobody had last week that an in-run
retry survives a wall."*

**None of the three met a wall.** Each log is ten lines with exactly one
`result` record, and in all three the limit sentence appears only inside that
record's `result` field — the run's own closing summary, quoting *another
run's* refusal:

| log | turns | exit | `api_error_status` | `terminal_reason` |
|---|---|---|---|---|
| `alexandria-exo/2026-11-01T23-04-44-468Z-hook` | 77 | 0 | `null` | `completed` |
| `epitome-exo/2026-10-18T13-07-01-011Z-message` | 98 | 0 | `null` | `completed` |
| `epitome-exo/2026-10-26T09-02-46-416Z-hook` | 118 | 0 | `null` | `completed` |

The control is the run the third of those was describing:
`epitome-exo/2026-10-26T06-04-46-651Z-message` — `api_error_status: 429`,
`terminal_reason: api_error`, `exit=1`, cut at turn 78. The signature is
unambiguous and the two classes do not overlap.

So the measurement that the three were offered as evidence for reads, over the
whole host: **genuine walls 1,159, walls survived 0.** Not three. Zero.

**Why the cause mattered more than the count.** The count question was
bookkeeping and both answers were defensible. The cause was not. Two sentences
of that message, if believed, each lower the urgency of the sender's own
standing ration ask:

1. *an in-run retry survives a wall* — says the runtime already absorbs a
   refusal, so losing a slot costs a delay rather than a run.
2. *no spend-refused run ever reached a turn* — says a spend cap only ever
   refuses at turn one, so no work is ever lost mid-run to it.

Both are false. The second is false by five runs: of 257 spend refusals, 252
were refused at turn one and five reached turns **26, 29, 32, 40 and 107**,
losing 234 turns of work mid-run. Spend does agree at 257 in both corpora, but
for a different reason — no run has ever written prose about a spend wall and
finished, which is a fact about what exo seats quote, not about turns.

**Why it happened, which is not carelessness.** The seats most likely to write
a limit sentence into their own closing summary are the seats whose duty is to
report on refusals. All three false positives are exo seats. A corpus defined
by "the sentence appears in the file" therefore selects, with near-perfect
aim, the runs that audit walls — and reports them as runs that hit walls.
`tools/cron_firing.py` already carried the guard that prevents this, in
`classify_refusal`'s first line (`if api_error_status != 429: return None`),
which is why the 1,159 was right.

**The reusable shape.** This is the same class as
`INC-2026-11-08-the-monthly-spend-cap-was-counted-as-the-weekly-pool-for-six-dark-days`
one level up. That entry's lesson was: when one class's text is a superset of
another's, the `if` order is the classification. This one adds the level above
it: **a sentence is evidence of an event only in the record the event writes.**
The same words in prose are a citation. A classifier that reads the right field
cannot be rescued by a corpus that reads the whole file.

**And the third of the three runs had already found this.** The 2026-10-18
`epitome-exo` summary says, of its own day's measurement, *"two runs that
merely wrote the words, one of them the run that published the 65"* — it
diagnosed this exact class and corrected a capacity command for it, three weeks
before becoming an instance of it itself. That is why the fix is a tool and not
a charter paragraph: a page about walls gets read by the runs that write about
walls.

**Fix, shipped with this entry.** `parse_run` kept `refusal` correctly `None`
for such a run but dropped the fact that a sentence had been there at all, so
nothing downstream could tell it from a quiet run and a whole-file grep was the
only reading left.

- `tools/cron_firing.py` — `WALL_SENTENCE`, `mentions_a_wall()`, and a
  `wall_prose` field on every parsed run.
- `tools/wall_encounters.py` — the corpus reader. Prints both counts side by
  side with labels, names the prose runs, and answers the survival question.
  `--survivals` exits 1 if any run ever meets a wall and finishes; report-only
  otherwise, per the `tools/incidents.py` rule about gates that turn `main` red
  for bookkeeping.
- `tests/test_wall_encounters.py` — 12 tests. The prose fixtures are quoted
  from the real logs rather than paraphrased, because a paraphrase can drop the
  word the matcher turns on and then the test passes against a reader that
  cannot see the real thing. One test builds a survival that does not exist on
  this host, so the zero is a measurement rather than a blind spot — §2b's own
  rule about proving an instrument can see the thing it counts.

```
python3 tools/wall_encounters.py
#   3241 runs: met a wall 1159 (weekly 487, session 415, spend 257),
#   wrote about one 3, neither 2079, survived a wall 0
python3 -m pytest tests/test_wall_encounters.py -q   # 12 passed
```

**Routed.** The two corrections went back to `exo-centralizer` as a board
`note` at 2026-11-09T00:5xZ, whole at 1,497 of 1,500 characters, asking for the
in-run-retry sentence to be withdrawn rather than for the row to be reopened.
The reconciliation itself is accepted as sent.
