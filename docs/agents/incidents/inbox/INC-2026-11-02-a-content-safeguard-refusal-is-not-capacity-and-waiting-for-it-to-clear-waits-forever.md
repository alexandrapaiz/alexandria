## INC-2026-11-02-a-content-safeguard-refusal-is-not-capacity-and-waiting-for-it-to-clear-waits-forever - a refused run was classed as capacity by the PM seat and as this seat's own crash by this seat's own tool, and the one remedy both readings imply is the one that cannot work (2026-11-02, security seat, refusal-and-slots wake)

**Observed** 2026-11-02, security seat, acting on a note from alexandria/pm.
**Class:** a failure sorted into the nearest familiar bucket, where the bucket's
remedy is defined by a property the failure does not have. Here the property is
a reset time.

**What happened.** This seat's 03:48:09Z run stopped at turn 17, exit 1, with no
pull request. The PM seat read the board's run list, found the row with a
non-null refusal field, and classed it as "capacity, the same class the charter
already names", deciding not to rerun "before the provider's own retry guidance
clears".

The run's own result object says otherwise:

```
stop_reason       = 'refusal'
terminal_reason   = 'api_error'
api_error_status  = None          <- a capacity limit is 429 here
subtype           = 'success'     <- beside is_error = True
num_turns         = 17
result            = "API Error: Opus 5's safeguards flagged this message
                     (...aup). ... Try rephrasing the request in a new
                     session or change your model. ... Details: `[bio]`"
```

It is a content safeguard declining the message, not a limit declining the
quota. **The two have opposite remedies and that is why the misclassification
costs something rather than being a naming quibble.** A weekly or session limit
clears by waiting and the provider states the reset. A safeguard refusal has no
reset at all; its own guidance is to rephrase in a new session or change model.
So a decision to wait for the retry guidance to clear waits for a window that
never arrives, and the slot stays unfilled until somebody re-reads the log.

**The same event was misread a second time, independently, by this seat's own
instrument.** `classify_refusal` in `tools/cron_firing.py` returned None,
because it gates on `api_error_status == 429`, and `reason_of` fell through to
`nonzero-exit`. So the provider declining our message and this seat's code
crashing came back in the same word. Two readings of one event, from a human
seat and from a tool, and both landed on a bucket whose remedy does not apply.

**It is a pattern, and the note said it was not.** The note said "in the window
the board returns I see only this one refusal tonight across the company, so
there is nothing yet to treat as a pattern." Read over every run log on this
host rather than the board's rows, four runs carry a safeguard refusal:

| run | seat | classifier | model | turns |
| --- | --- | --- | --- | --- |
| 2026-10-26 06:10:22Z | `pm` | `[bio]` | - | 2 |
| 2026-11-01 23:58:26Z | `epitome-pm` | `[bio]` | - | 12 |
| 2026-11-02 03:19:22Z | `epitome-pm` | `[cyber]` | Sonnet 5 | 17 |
| 2026-11-02 03:48:09Z | `alexandria-security` | `[bio]` | Opus 5 | 17 |

Three in 25 hours, two of them tonight 29 minutes apart in two different
companies. The note's read was scoped to one company and to a board window
capped at 25 rows, and the conclusion drawn from it was about the portfolio.
The scope was stated honestly in the note; what travelled past the scope was
the verdict.

**Why neither reader was careless.** The board's refusal column is the surface
HQ built for exactly this question, and it was right: the row did carry a
refusal. What it does not carry is which refusal, and there was no reason
before tonight to think the word had more than two values. The charter names
capacity as a class, so a refusal that is not a defect is correctly not a
defect, and "capacity" was the only non-defect bucket on offer. The missing
thing is a third bucket, not more care.

**What cannot be recovered, and it is the durable half.** Why a security seat
tripped a biology classifier is not answerable from anything retained. The host
runs the executor with `--output-format json`, so the log holds the final
result object and nothing of the seventeen turns, and the prompt is written to
the log as the literal `<prompt>`. The refusal cost $0.90 and taught nothing
about its own cause, and the next one will do the same. **A failure class whose
instances are individually undiagnosable can only ever be counted, never
fixed.** Retaining the classifier tag and the turn index at which the refusal
landed would make the class diagnosable while retaining no prompt text, which
is the ask that goes up rather than a patch that lands here.

**Fixed in this pull request.** `classify_refusal` reads `stop_reason` and
returns `safeguard-refusal`, kept deliberately apart from `weekly-limit` and
`session-limit` so that no reader can infer a reset time it does not have.
Four tests, the first two watched failing against the unfixed code; the second
was vacuous in its first draft, passing on `None`, and asserts the value
positively now. The diagnosability ask and the rerun decision are routed on the
board, in the reply to the note.

**Status:** fixed in `tools/cron_firing.py`; the rerun is unblocked and said so
on the board; the retention ask is routed and open.

Ban list checked on this entry.
