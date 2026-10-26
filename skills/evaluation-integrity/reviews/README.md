# evaluation-integrity: consumer reports

The lane is open and empty. File as `YYYY-MM-DD-<consumer>.md` against the
contract in
[skills/_validation/reviews/README.md](../../_validation/reviews/README.md).

Rewritten 2026-10-24, because the ADR-38 retrofit cut this file from ten
sections to five deltas and the three sections this page used to ask about are
no longer the three worth asking about. No delta has been exercised by anything
but a claim id, and none has a measured delta, so every line below is a request
for the first evidence of any kind.

Most wanted, in priority order:

- **Delta 1, the oracle.** The four-step attack is the cheapest thing in this
  file to run against your own rubrics. Report the exploit rate you got and,
  more importantly, which oracle produced it, because the one measured result
  here says the rate is mostly a fact about the oracle and the direction is
  what survives. This is the one delta where a consumer can produce a number
  the library does not have.
- **Delta 5, the noise band and the audit.** The five-repeat-run floor is ours
  rather than the paper's and it is a guess. A report naming how many repeats
  it actually took before a spread appeared would replace a guess with a
  measurement, and that single number would change the skill's text.
- **Delta 4, the panel.** Three of the four portable parts are marked ours
  rather than the paper's, and the whole section rests on one competition
  system. A report saying which of the three survived contact, especially
  whether discarding unparsable judgments changed anything in practice, is
  evidence that does not exist anywhere yet.

Two things this lane specifically wants told:

- **Say when a delta was confirmatory.** Under ADR-38 several reports showing
  zero decision changes make a skill a deprecation candidate exactly as a
  regressed eval would, so a confirmatory report is not a null result here. It
  is the measurement that retires a delta.
- **Say if delta 3 was already in your head.** Its channel half, closing the
  shortcut in the environment rather than in the instructions, is the delta
  this seat most expects a strong model to supply unprompted. It survived the
  retrofit on the defect ordering and the four named channels. If you read it
  and learned nothing, say so, and it goes.
