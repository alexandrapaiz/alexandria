### 2026-11-09 - Craft scan: ArgoCD ranks "I could not tell" below "I can tell it is broken", and this repository ranks it above

- Trigger: today's run found `weekly` reported as unmeasurable by the deploy
  surface for thirteen days while it was in fact 24.7 days and 55 commits
  behind. The surface was not silent about it: an earlier repair
  (`INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see`) made the
  undated apps ride along on the FAILING headline rather than be dropped by
  it. They rode along in a sub-clause, after four other apps' numbers, under a
  verdict about those other apps. So the scan went to the product that has
  solved exactly this problem for a decade.
- Worth stealing, and it is one line of design: ArgoCD's application health is
  "the worst health of its immediate child resources", over the priority
  `Healthy, Suspended, Progressing, Missing, Degraded, Unknown`. **`Unknown` is
  last, below `Degraded`.** An app it cannot assess is reported as worse than
  an app it has assessed and found broken. The reasoning is sound and it is the
  inverse of this repository's: `exit_code` in `tools/delivery_health.py`
  returns 1 for any FAILING and 2 for any UNKNOWN, so one measured failure
  anywhere demotes every unmeasurable surface into a footnote under somebody
  else's verdict. A failure is one known thing. An unknown hides an unbounded
  number of them, which is precisely what happened here: `distill` was also
  unmeasurable, and it was 118 commits behind.
- What alexandria does better, and it is the half ArgoCD is weak on: every
  unknown state in this file carries its own cause and the command that
  resolves it, in the sentence a reader acts on. "This checkout is a shallow
  clone ... `git fetch --unshallow`". "The search's own ceiling ... raise the
  limit past 40 to look further back". ArgoCD's `Unknown` is a bare enum, and
  its own operator manual lists it in the priority order without defining
  anywhere what it operationally means, so an operator who gets one has a rank
  and no next action. A state that names its remedy is the thing this product
  is actually good at, and it is why the fix today took one afternoon rather
  than a diagnosis.
- First step, if the owner wants the stealable half: `exit_code` and the
  rendered headline order the states as ArgoCD does, so a surface that could
  not be measured becomes the headline rather than a clause inside another
  surface's. It is roughly ten lines and one table in
  `docs/agents/delivery-health.md`. The counter-argument is real and belongs in
  the decision: an unknown that outranks a failure will, on the day both are
  true, bury a live outage under a measurement problem. ArgoCD's answer is that
  both are shown per-resource and only the roll-up is pessimistic, which this
  surface already does, so the change is to the roll-up alone.
- Cost: $0
- Status: proposed
