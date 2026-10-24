# Engineer run note, 2026-10-24 (message): the drift guard reported on what it could measure

## What this run took, and why it was not a card in its own lane

The dispatch asked for the next item in the engineer lane on the board. Every
card in that lane closes with a hand this seat does not have.

| card | what closes it |
|---|---|
| `6a5e4ad5` Compute: the Modal workspace is switched off | re-enabling the workspace, an account state on Modal's side |
| `92ab912d` Press: no issue for 2026-W41 | `modal run pipeline/weekly.py::resend`, a Modal token |
| `2170a62f` Deploy: weekly is not running main | `modal deploy`, a Modal token |
| `a7a24fd0` Checkout: no offer on the pricing page can be bought | three `POLAR_CHECKOUT_*` values in the site's environment |

The `Backlog` card above them, "Wire Polar's three products end to end", is
built: #285, #301 and #352 are merged and `site/lib/polar.js`,
`site/app/api/polar-webhook/route.js` and
`site/app/api/checkout/[plan]/route.js` all exist.

So this run took the thing that stands between the `Deploy` card and the seat
that owns it, which is that the surface answering that card cannot be read
from any seat's checkout.

## The measurement, before the diagnosis

`tools/delivery_health.py`, this sandbox, one minute apart.

Shallow, which is what the host harness hands every seat:

    unknown  deploy  the deploy cannot be compared from here: distill (the
                     drift cannot be dated from this checkout); ingest (...);
                     weekly (...)

After `git fetch --unshallow`, same tree, same rows:

    FAILING  deploy  the deployed code is not origin/main: distill is 8.0 days
                     behind (1 undeployed commit since 73b180f); ingest is 7.4
                     days behind (2 undeployed commits since 807d403); weekly
                     is 8.2 days behind (20 undeployed commits since f16e277)

`weekly` is the press. That number is the standing `Deploy` card, measured
rather than quoted, and it is 8.2 days rather than the 44.7 hours the card's
body still carries.

## The bug this run fixed, which is not that reading

Yesterday's run (#409) already stopped the shallow read answering green,
and the `unknown` above is that fix working. What it left is narrower.

`judge_deploy` builds `alarms`, `blind`, `unknowns` and `drifted`, then tests
`if alarms or blind` first. A surface with one app behind and one app it could
not place returned `FAILING` naming only the first, and the `unknowns` list it
had already built was never read. `drift_watch` asked `if deploy.state ==
UNKNOWN`, which that branch order makes unreachable whenever anything alarms,
and its `behind()` filters to `failing`. So the unmeasured app left no trace
in the headline, no card, no line in the report, and no mark on the exit code.
The run exited 1, which this file's own docstring defines as a claim about the
fleet.

The mixed state needs no shallow clone to reach. An app that never recorded a
runtime and whose module does not ask it to is `unknown` beside siblings that
compare fine, and a clone deep enough to date two commits but not twenty dates
exactly one of them. Depth is a knob on the host harness.

## What changed

- `judge_deploy`'s `FAILING` headline carries the undated apps.
- `_is_shallow` asks `git rev-parse --is-shallow-repository`. The undated row
  and `drift_watch`'s card body stop guessing "usually a shallow clone" and
  name `git fetch --unshallow` when, and only when, that is the cause.
- `drift_watch.undated()`, named in `render()` on every path, and exit 2 on any
  of them. Cards for the apps that did alarm are posted before that return.
- `_last_commit_at`'s docstring promised `fetch-depth: 0`, true until
  `ab4e5bb` moved every seat's cadence to the host manifests on 2026-10-17.
  Removed, with the reason, because the promise is why nobody checked.

Seven new tests, all seven failing against the previous `tools/` and passing
against these.

## What this run did not do

It did not close the `Deploy` card. The card is correct, it is worse than it
reads, and it still needs `modal deploy`. What changed is that the next seat
to run the guard will be told so instead of being told `unknown`.
