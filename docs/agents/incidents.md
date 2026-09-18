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

12. **Two runs of the same dispatch executed concurrently on the same
   branch, and the second nearly force-pushed over the first.** The
   owner's sales redispatch started twice (runs 35308818120 at 04:55:32Z
   and 35308901891 at 04:56:54Z, 82 seconds apart). Both checked out,
   both wrote the same four deliverables, both pushed to
   `sales/2026-09-18-first-customers`. Three separate hazards came out
   of it, all of which nearly cost real work:
   - **Near-miss data loss.** The second run finished its documents
     against a branch tip it had read once, then attempted
     `push --force-with-lease`. The lease correctly rejected it as
     "stale info" — the tip had moved three commits in the interim.
     Without `--force-with-lease` this would have silently destroyed
     ~1,800 lines of the first run's work. **The lease is the only
     reason there is anything to read in PR #22.** Rule worth making
     general: an agent seat must never plain `--force` a shared branch.
   - **Stale base silently reverting main.** The first run was cut from
     f8c3b1b, 40 seconds before f98126a landed on main. Its branch
     therefore carried a *revert* of the sales charter's new personality
     section and of incident item 11 — the exact two things the
     dispatch was about. Merging that PR would have deleted them. Fixed
     by merging main into the branch. Rule: a seat should verify its
     base contains the change its own dispatch references.
   - **Repeat of item 8 (ambiguous run conclusions).** `gh run list`
     reported run 35308818120 as `completed success` while its commits
     were still landing (05:08:04Z). Recorded as a repeat per the
     standing rule. Item 8's lesson held and was followed: the branch
     and PR were trusted over the run's stated conclusion, which is how
     the collision was caught at all.
   RESOLUTION this session: no work was lost. The second run merged main
   to restore the charter, then *extended* the first run's documents
   instead of replacing them — closing the outreach plan's own flagged
   verification gap (HN thread 49689454's commenters, unverified across
   two prior runs) and adding the B2B constructions the first run's
   section did not defend. For the ExO: the dispatch mechanism should
   not be able to start the same seat twice, and seats sharing a branch
   need a stated convention for who rebases onto whom.
