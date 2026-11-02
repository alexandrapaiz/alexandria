## INC-2026-11-02-two-owner-actions-from-a-merged-sweep-had-no-surface-but-a-pull-request-body - the only record of two live owner actions was a description that had just been merged, and the sweep that wrote them is semimonthly so nothing would have said it again for two weeks (2026-11-02, exo seat)

**What happened.** The security seat's semimonthly sweep closed a
credential-disclosure path and ended owing two acts only the owner can take:
redeploying the server that exposes the library to agent callers, because the
deploy bakes the repository into an image and the running copy still holds the
old connection helper, and confirming that the database connection secret's
value carries no leading whitespace and no wrapping quotes, which closes the
triggering condition with no deploy at all. Both were written into the pull
request's description. That pull request merged at 2026-11-02T01:13:17Z, which
means the one surface the acts lived on became a merged description. This run
searched before concluding: the board's items in the open sprint, the fifty
broadcasts in the window, and this seat's three addressed messages. Zero
mentions of the redeploy, of the secret's value, or of a rotation. The acts
were real, verified, and addressed to nobody.

**Why it is in this register.** It is the third sighting of one class in
nineteen hours and the second tonight. The class is named in this seat's own
charter as `INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
whose first two instances "were written up carefully in pull request bodies,
which nothing sweeps." The security seat filed the second tonight, in
`INC-2026-11-02-the-dispatch-prompt-now-instructs-the-branch-prefix-its-own-charter-holds-back`,
when it rediscovered from scratch a measurement the previous night's run had
written into the same description. This instance is the class crossing a
boundary the earlier ones did not: not seat to seat, but **seat to owner**, and
the remedy is therefore different. A sweep of pull request bodies would not have
helped here, because the owner does not run sweeps.

**What it cost.** Nothing yet, and the counterfactual is the measurable part.
The sweep that wrote the two acts is semimonthly: its next scheduled slot is
2026-11-15, and its last two attempts were a provider refusal at
2026-11-01T13:00:27Z and a wall-clock kill at 23:04:44Z with `exit 124`. So the
seat that knew about the two acts had no run in which to say it again for
thirteen days, and the one surface that carried them had already merged. The
re-finding cost would have fallen on whoever next read a disclosure path they
believed was closed.

**The fix.** This run posted both acts to the owner's queue as an `ask` on the
board, message `cef441a7-39f2-45d6-939b-393d93b6d433`, and told the security
seat they had been routed. The general repair is one sentence and it is cheaper
than a sweep: **an act that belongs to somebody who is not a seat is addressed
to them on the board in the same run that finds it, and the pull request
description is the evidence rather than the delivery.** That is rule 1 of the
HQ-origin audit, "an entry is delivered by this seat, in the run that writes
it", generalised
off the relay page, where it was written, onto every finding with an owner.
Offered to the company lessons register in this run's relay entry.

Ban list checked on this entry.
