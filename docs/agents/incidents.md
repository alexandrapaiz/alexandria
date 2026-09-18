# Incident register — agent runs and sandboxes

Owner-directed (2026-09-18): a technical record of agents not properly
running, shutting down, or losing work, so failures are learned from
once instead of rediscovered. Append-only, dated, any seat or the chair
may add entries; the ExO reads this file every run (charter step 2) and
turns patterns into charter or workflow fixes.

STANDING RULE (owner, 2026-09-18): any issue that occurs MORE THAN ONCE,
anywhere in the org, is always recorded here at the moment it repeats.
No exceptions, no judgment call. A repeat that goes unrecorded is itself
an incident.

## 2026-09-17/18 — the founding night's failures

1. **OIDC permission missing.** First cloud run (engineer,
   run 35297972051) failed 3/3 attempts: claude-code-action requires
   `id-token: write`, absent from the workflows. FIXED (commit
   c7e67d5) across all workflows.
2. **Default tool sandbox blocks shipping, run still reports
   success.** The smoke run completed green with 17 permission
   denials: the action's default permission mode refused git pushes
   and PR creation, and the job's conclusion hid it. FIXED: 
   `--permission-mode bypassPermissions` (commit 80721ee), justified
   by the isolated ephemeral runner and repo-scoped token.
3. **Run reports success, ships nothing (end-loaded shipping).** Sales
   first run (35305610562): 59 turns, zero denials, subtype success,
   no branch pushed, no PR, all work lost at sandbox teardown. The PM
   scrum-overhaul run (35301912056) had the same no-ship outcome and
   later flipped to a failure conclusion; its logs were not
   retrievable afterward. PATTERN FIX pending with the ExO: every
   charter mandates draft-PR-first (branch, push, `gh pr create
   --draft` within the first turns, commit as you go), plus a
   workflow tripwire flagging any run that ends with no branch
   pushed. Board card exists.
4. **Turn-cap starvation on visual work.** Frontend first run
   (35305207776) died at `error_max_turns` (150): build plus
   Playwright plus reading screenshots is turn-hungry. FIXED: cap
   raised to 250 and first-run scope narrowed; a future fix is
   scripting the screenshot batch so turns go to judgment, not
   plumbing.
5. **Shared-checkout collisions (pre-cloud and ad-hoc runs).** A local
   desktop PM run operated in the interactive session's checkout and
   switched its branch mid-commit (resolved by moving all runs to
   isolated Actions checkouts, ADR-18). The ad-hoc remote OKR and
   market runs shared one clone and raced on branches; both
   self-repaired and reported honestly. Scheduled Actions runs each
   get a fresh checkout, so this class is closed except for ad-hoc
   remote sessions.
6. **Same-anchor ledger appends guarantee merge conflicts.** PRs #2
   and #3 both inserted at docs/ideas.md's `## Proposals` header;
   the second merge conflicted exactly as the ExO's first run
   predicted. FIXED at charter level: ledger-writing seats must check
   open PRs touching ideas.md and declare merge order (PR #4).
7. **Hidden-prompt secret paste stored an empty value.** NEON_RO_URL
   was set to an empty string via a masked terminal prompt; runs then
   failed with a confusing local-socket psql error. The skill agent
   diagnosed it correctly and refused to fabricate data. FIXED by
   re-entry plus a rule: any run depending on a secret verifies it
   with a cheap probe first and reports the probe's result.
8. **Ambiguous run conclusions.** GitHub's run list briefly showed the
   PM overhaul as success before recording failure, which misled
   monitoring. Lesson: trust a run's shipped artifacts (branch, PR),
   never its conclusion alone.

9. **Premium seats silently ran on the default model.** The routing
   table assigned the top model to engineer, exo, security, skill,
   weekly, and frontend, but no `--model` flag was set and
   claude-code-action defaults to Sonnet, so every premium run on
   2026-09-17/18 actually used Sonnet. Caught by an owner-requested
   routing audit reading modelUsage from real run logs. FIXED:
   `--model opus` set explicitly on all six workflows. Lesson: a
   routing policy is config plus verification; assert the model from
   run logs, never from intention.

10. **Turn-cap starvation is a pattern, not a one-off (ExO owns the
   postmortem).** Second and third occurrences: the PM's views/triage
   run and its scrum-overhaul run both died or shipped nothing under a
   60-turn cap, after the frontend's first run died at 150. Owner
   escalated 2026-09-18: "pass this issue on to EXO because it's the
   second time it's happened." Interim fixes: PM raised to 140,
   frontend to 250. ExO's Sunday postmortem should right-size every
   seat's cap against its real workload, and pair it with the
   draft-PR-first rule so a starved run still leaves partial work
   instead of nothing. A cap that silently eats a run's entire output
   is a harness bug, not an agent failure.

11. **The sales seat underdelivers on creativity despite explicit
   liberty grants (owner-reported, second miss).** First, its pitch
   deck answered the wrong audience (an external pitch when the owner
   asked to be pitched herself). Then its sales-plan content, made
   under "complete creative liberty," was judged by the owner as
   "poorly creative": no selling to other companies, no idea list, no
   concrete outreach plan, no immediate first-customers plan for the
   days after launch. Contributing cause worth testing: the seat runs
   on the Sonnet routing tier, and creative breadth under an open
   brief is exactly where the premium tier earns its cost. FIXES this
   session: the seat moves to Opus, and its redispatch carries the
   owner's critique verbatim. ExO's Sunday postmortem should consider
   whether "liberty" dispatches need a different prompt shape (examples
   of the ambition bar, not just permission) across all seats.

11. **The sales seat underdelivered on creativity despite a complete
   liberty grant (owner-reported).** Her critique, in substance: the
   sales plan was poorly creative; she wanted selling to other
   companies, a list of ideas, an outreach plan, and an immediate
   post-launch plan for obtaining the first customers, delivered with
   the personality of a genuinely talented, out-there salesperson.
   FIXES: the charter now carries that personality explicitly, the
   seat moves to the premium model tier (creative breadth under open
   briefs is where it earns its cost), and the redispatch carries the
   critique verbatim. For the ExO's Sunday postmortem: liberty grants
   may need an ambition bar stated in examples, not just permission,
   across every seat; timidity under liberty is now a named failure
   mode.

12. **The PM's triage misprioritized plumbing over product
   (owner-reported).** Her critique, in substance: the PM is
   unfocused and its triage is not ideal. The most important thing
   before a release is a working product, and the product is the
   content: the newsletter has roughly two issues with no testing or
   validation of them, and barely two skills, under-tested. Site
   plumbing led the sprint while the sellable repository of top-tier
   skills and newsletter entries lagged. Her release gate, recorded
   as all-hands decision 11: nothing releases honestly until the
   product scores top tier (a five) on the OKR benchmark against the
   market's comparison set. Also named: a real domain and a UI with
   no coming-soon pages. For the ExO postmortem: triage law needs a
   product-first clause, and the PM's sprint goals should be scored
   against "does this make the product better" before "does this
   make the site work."
