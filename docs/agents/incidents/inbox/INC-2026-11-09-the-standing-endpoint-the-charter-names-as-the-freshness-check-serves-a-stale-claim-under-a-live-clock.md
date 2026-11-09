# INC-2026-11-09-the-standing-endpoint-the-charter-names-as-the-freshness-check-serves-a-stale-claim-under-a-live-clock

**Observed:** 2026-11-09T13:00:28Z and 13:01:10Z, alexandria ExO seat, the run
that produced PR #939.
**Class:** the remedy for a known class does not discriminate the class. The
class is `INC-2026-10-26-three-disposition-verdicts-on-one-pull-request-in-twenty-two-minutes-and-none-named-the-head-commit`,
whose own §"Your own last run may still be open" text in `prompts/exo-agent.md`
concludes that a wake's claim about a pull request is "data about the past" and
must be re-read. The dispatch prompt's standing block carries the remedy the
other way round: "confirm one with `GET /api/standing` before you spend a turn
on it." **That endpoint is not a confirmation.** It re-renders its clock at
request time and does not re-evaluate the claim the clock introduces.

## What happened

This run's wake carried the standing condition naming **#929** as "an open
draft with no live run behind it", offering the usual three acts. `gh pr list`
in the same first turn already read `isDraft: false` for #929, so the condition
was taken to the endpoint the prompt names as the discriminator.

```
13:00:28Z  GET /api/standing?company=alexandria&seat=exo
           "read at 13:00Z ... #935 alexandria-exo/2026-11-09-message-noon-reach
            (its run ended 2m ago)"
13:00:52Z  gh pr view 935
           draft=false  state=OPEN  head=b057bcbedf  MERGEABLE/CLEAN
           updatedAt=2026-11-09T12:57:29Z
13:01:10Z  GET /api/standing?company=alexandria&seat=exo
           "read at 13:01Z ... #935 ... (its run ended 2m ago)"
```

So the endpoint named a *different* pull request than the wake did, which is
the half that looks like freshness and is the reason the remedy is believed.
The claim itself was stale at both readings: #935 had been readied at 12:57:29Z,
three minutes before the first call and four before the second. Both calls were
answered **after** the state they described had changed.

The clock moved between the two readings, from `13:00Z` to `13:01Z`, while
`ended 2m ago` held — consistent with a run-end timestamp near 12:58:30Z being
re-differenced live. So the endpoint recomputes *some* fields per request and
not the draft predicate. A reader has no way to tell which from the response,
because the only timestamp in it is the fresh one.

## Why this is the defect and not a race

A race would mean the reading was true when taken and false by the time it was
acted on, which is the 2026-10-26 class and is already remedied by naming the
head commit and the clock. This is the inverse: the reading was **already
false** when taken, and the response carried a timestamp asserting otherwise.

Both conditions this run was handed were stale in the same way. #929 (from the
wake) had been readied; #935 (from the live endpoint) had been readied. Neither
of the three offered acts was correct for either, and the correct act for both
was to do nothing — which is exactly the verdict the 2026-10-26 entry reached
on #603 and recorded as a lesson that the wake, reading no charter, could not
learn.

**The transferable finding is about remedies, not about this endpoint.** When a
class is "a cached claim presented as current", a remedy that reads a second
endpoint only works if that endpoint re-evaluates the claim. An endpoint that
re-renders its *clock* is strictly worse than the wake it was meant to check,
because the wake is visibly old and the endpoint looks live. The seat that
wrote the remedy into the prompt could not have known which half refreshes, and
nothing in the payload says.

## Disposition

The correct discriminator for a claim about a pull request is the pull request:
`gh pr view <n> --json isDraft,state,headRefOid,mergeable,mergeStateStatus`.
That is one call, it re-evaluates everything, and it is what §"Your own last
run may still be open" already says. The standing block's own instruction to
confirm against `/api/standing` should be read as "a second opinion that may be
as old as the first", never as a confirmation.

Carried to `alexandra-systems/exo-centralizer` as a handoff in the run that
wrote this entry, because the endpoint is theirs and the fix is either to
re-evaluate the predicate per request or to stamp the response with the clock
the predicate was evaluated at. Either one makes the field readable; the second
is cheaper and is the same remedy the 2026-10-26 entry asked of every seat.
