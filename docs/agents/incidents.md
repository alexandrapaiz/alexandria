# Incident register — agent runs and sandboxes

**Enforced at:** every charter's "Check the register before you ship"
step, which requires each seat to append a repeat in the PR that
produced it, plus prompts/pm-agent.md §1f for run failures and
prompts/exo-agent.md §2 weekly.

Owner-directed (2026-09-18): a technical record of agents not properly
running, shutting down, or losing work, so failures are learned from
once instead of rediscovered. Append-only, dated, any seat or the chair
may add entries; the ExO reads this file every run (charter step 2) and
turns patterns into charter or workflow fixes.

STANDING RULE (owner, 2026-09-18): any issue that occurs MORE THAN ONCE,
anywhere in the org, is always recorded here at the moment it repeats.
No exceptions, no judgment call. A repeat that goes unrecorded is itself
an incident.

DUPLICATE ENTRIES REMOVED (ExO, 2026-09-24, second cycle): this file
carried two verbatim copies of incidents 19 and 20, from a merge that
appended entries the file already held. The short copies were deleted
and the fuller ones kept, because the fuller ones contain the short ones
word for word and add the blameless postmortems. Nothing was lost and
nothing was renumbered. Two entries numbered 22 remain, and those are a
genuine collision between two different events rather than a duplicate,
so they stay until the seats that cite them are checked.

HOW TO NUMBER A NEW ENTRY (ExO, 2026-09-24, incident 29): use
`INC-YYYY-MM-DD-short-slug`, taking the date the incident was observed.
Never allocate the next sequential number. Every seat writes on its own
branch and reads a different snapshot of this file, so a sequential
counter collides whenever two seats register an incident between merges,
which has now happened four times. Entries 1 through 28 keep their
numbers permanently and are cited as "incident N" for as long as
anything cites them. If you find you must renumber anyway, record the
old id in the entry, the way the company lessons register does for its
rule ids, and never do it silently.

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

   **ExO postmortem, 2026-09-18, closing the escalation.** The owner
   asked for two things: right-size every seat's cap against its real
   workload, and pair the caps with draft-PR-first so a starved run
   still leaves partial work. The second shipped this run, as the "Ship
   first, then work" section now in all eleven charters. For the first,
   the caps were set by guess, so this reads `num_turns` out of the real
   run logs instead. Every completed run on record:

   | Seat | Turns actually used | Cap then | Verdict |
   |---|---|---|---|
   | frontend | 151 | 150 | died at the cap (incident 4) |
   | security | 108 | 100 | overshot, run failed (incident 11) |
   | engineer | 67, 37 | 120 | comfortable |
   | skill | 61, 41 | 100 | thin once the database is live |
   | sales | 59, 57, 49 | 80 | thin |
   | pm | 42, 32 | 60 then 140 | starved at 60, fine now |
   | exo | 36 | 100 | that run was observation only |
   | okr | 33 | 100 | comfortable |
   | market | 23 | 100 | comfortable |
   | research | never run | 100 | unknown |
   | finance | never run | 80 | unknown |

   The pattern is not that caps are too low in general. It is that a cap
   set before a seat ever ran is a guess, and the two seats that broke
   are the two whose work grew after the guess: frontend gained
   Playwright screenshots, security gained a whole repository to sweep.
   So the rule proposed here is a ratio rather than a number. **A cap is
   at least twice the seat's highest observed turn count, never below
   100, and re-derived by the ExO from run logs whenever a seat's duties
   grow.** That makes a cap hit mean something, because it becomes
   evidence the work changed rather than evidence the agent misbehaved.
   The resulting per-seat numbers are queued in
   docs/agents/pending-workflow-changes.md, because of incident 12.

   One honest limit on the table. The two PM runs that starved at 60 are
   the ones whose logs could not be retrieved afterwards, so their turn
   counts are absent above and the 60-turn cap is judged from the
   owner's account rather than from a log. Seats that have never run
   contribute nothing, and their caps stay where they are until a first
   run gives this seat something real to measure.

## 2026-09-18 — the first full week of cloud runs

Postmortems by the ExO agent (charter step 6), blameless, from run logs
rather than from what the runs said about themselves.

11. **A turn cap failed a run that had already shipped.** The security
    seat's first run (35299288455) did its whole job, opened PR #8 at
    02:42:38, and was then failed by the action eight seconds later:
    `Claude reported a successful result after 108 turns, exceeding the
    configured maximum of 100`. Technically this is not the same defect
    as incident 4, where frontend died mid-work at `error_max_turns`.
    Here the work was complete and merged; only the run's conclusion was
    red. The damage is to monitoring rather than to output, and it is
    the exact inverse of incident 8: there, a green conclusion hid a run
    that shipped nothing, and here a red conclusion hides a run that
    shipped everything. Both point at one rule, which is now the house
    rule for reading runs: **judge a run by its artifacts, never by its
    conclusion.** FIX queued, not applied: raise the security cap from
    100 to 150, in docs/agents/pending-workflow-changes.md, because of
    incident 12 below. Lesson for charters: a cap is a tripwire, not a
    budget, so size it to the seat's honest work and treat a cap hit as
    evidence about the cap.

12. **The agent token cannot write the agent workflows, so part of the
    ExO's chartered lane is unreachable.** Discovered this run, by
    trying it. The ExO charter §5 names `.github/workflows/agent-*.yml`
    as writable, and the push was rejected outright:
    `refusing to allow a GitHub App to create or update workflow
    .github/workflows/agent-engineer.yml without workflows permission`.
    This is not a misconfiguration that a `permissions:` block can fix.
    `GITHUB_TOKEN` has no `workflows` scope available to grant, and only
    a personal access token carrying the `workflow` scope can push these
    files. Every workflow-level fix the org has wanted since the
    founding night runs into this, including incident 3's tripwire and
    incident 10's cap raise, which means the gap has been silently
    costing the org its whole workflow-repair capability for a week.
    FIX, two parts. Part one shipped now: workflow edits are written out
    in full in docs/agents/pending-workflow-changes.md for the owner to
    apply, and the ExO charter no longer claims a lane it cannot reach.
    Part two is owner-only and stays her call: mint a PAT with the
    `workflow` scope, store it as a repository secret, and pass it to
    `actions/checkout` in the agent workflows. That would let the seats
    repair their own machinery, and it would also hand every agent run a
    token strong enough to rewrite what runs the agents, so it is an
    authority change rather than a convenience, and it belongs to her.
    Lesson, and the one worth generalizing: **a charter that grants a
    lane the runtime cannot reach is a charter defect, not a runtime
    defect.** Every lane a charter names should be provable by the seat
    that holds it, so the ExO now verifies its own writable surface each
    run instead of assuming it.

13. **Incident 3's pattern fix sat unapplied for a full week.** Incident
    3 recorded draft-PR-first as "PATTERN FIX pending with the ExO" on
    the founding night. Sixteen PRs and one ExO run later, not one of
    the eleven charters contained the word draft, and the owner was
    still carrying the rule by hand in each dispatch prompt. The ExO's
    own first run spent its single permitted charter edit elsewhere, on
    the ledger-collision fix, which was reasonable in isolation and
    wrong against this queue. Nothing in the org held the list of fixes
    that had been agreed but not made, so the register recorded the
    decision and then no one read it as a to-do. FIXED: the rule is now
    a section in all eleven charters, and the ExO charter's step 2 now
    requires reading this register for entries whose fix is marked
    pending or queued, and either shipping them or saying in the PR why
    not. An incident is not closed when it is written down. It is closed
    when the fix is in the tree.
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

14. **Two runs of the same dispatch executed concurrently on the same
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
   need a stated convention for who rebases onto whom. (Numbered 14
   because 11, 12 and 13 are each currently used twice in this file —
   independent seats appending at the same anchor on the same day, which
   is item 6's pattern playing out in the register itself. Flagged for
   the ExO rather than renumbered here: renumbering other seats' entries
   mid-merge would break every cross-reference pointing at them.)
13. **Cautionary note (owner-directed): Clerk Core 3 API drift during
   auth integration.** The chair wired auth controls using the widely
   known SignedIn/SignedOut components; @clerk/nextjs v7 (Core 3)
   removed them in favor of Show when="signed-in|signed-out", and the
   build failed at prerender. The setup doc the owner supplied stated
   the correct Show API and the chair deviated from it toward
   training-data memory. Fixed in minutes; recorded for caution.
   Lesson for all seats: when integrating a fast-moving vendor SDK,
   the vendor's current doc outranks remembered APIs, and the
   installed clerk-* skills exist precisely to be consulted first.

## Incident 21 — The first real agent user queried alexandria and got nothing (2026-09-19, owner-reported)

The mission's first live test, and it failed. An agent working on
epitome (the owner's agent-identity venture) ran two semantic
searches over the claim corpus: agent identity and portability, and
frameworks and credential security. Best match: a weak 0.69 on
papers about entirely different questions. Its verdict, quoted:
"alexandria: searched, not useful for this." The epitome session
found what it needed through plain web research instead.

Why this is an incident and not a shrug: (1) it is the first
recorded use of the product's agent-facing promise ("your agents
load the same claims to act") by a genuine outside agent with a
genuine builder's question, and the product returned nothing;
(2) the territory is inside DECLARED scope, Layer 4 named agent
identity and governance as coverage on 2026-09-18; (3) the owner's
own words: "remember the okr mission. we are not achieving it."

Root cause is the compound of already-registered gaps, now measured
by a user: reach (identity and interop knowledge lives in standards
bodies and vendor changelogs, not arXiv; ADR-29 class 2), and
processing (what arXiv does carry sits in the untriaged 64%,
incident-adjacent E1). Actions taken same-day: three interop and
identity signal feeds added and deployed (A2A protocol releases,
SPIFFE releases, MCP spec releases, all verified live); ledger
proposal filed per epitome's offer, the pipeline grows an eye for
agent-interop and identity papers and standards; evidence forwarded
to the OKR seat's October scoring, where the
actionability-for-agents axis must count this query as its baseline
failure case. The zero-gap mandate's detection worked only because
the owner relayed it; the census and steering must learn to catch
this class before a user does.

## Incident 22 — The editorial rebuild outgrew the model's letterbox (2026-09-19)

First off-cycle autonomous run of the rebuilt generator (owner's
"why must i wait until monday", chair-triggered via modal run):
Groq returned 413 Payload Too Large and no issue was written.
Cause: the day's editorial work grew prompts/digest.md from 223 to
509 lines, and prompt plus the week's payload now exceed the free
model's request-size limit. New failure class: quality law versus
runtime budget; the seat that writes the rules (writer) and the
seat that runs them (engineer) share the constraint but neither
owned it. Fix dispatched to the engineer same hour; the standing
rule to come out of it: the generator prompt plus a worst-case
payload must fit the pipeline model's request limit with margin,
measured in CI or at deploy, so an editorial merge can never break
the press again.
## 2026-09-18 evening — the six-failure day

Postmortem by the ExO agent, owner-dispatched. Blameless: every fact
below is read from run logs and from git, not from what any run said
about itself. Numbering continues at 15 because 11, 12 and 13 are each
used twice above, for the reason set out at the end of item 16.
used twice above; see the note at the end of item 16.

15. **Six runs failed in one day, all of them turn-cap collisions, and
    the two reactive cap raises were outgrown by the seats that got
    them.** This is incident 10's third escalation to this seat. The
    owner's instruction was to stop guessing, and this is why.

    The six, verified from `num_turns` and `CLAUDE_ARGS` in each log:

    | Run | Seat | Turns | Cap | Flavor | Work |
    |---|---|---|---|---|---|
    | 35299288455 | security | 108 | 100 | false failure | shipped, PR #8 merged |
    | 35301912056 | pm | 61 | 60 | hard starvation | nothing pushed |
    | 35305207776 | frontend | 151 | 150 | hard starvation | nothing pushed |
    | 35306459296 | frontend | 286 | 250 | false failure | shipped, PR #15 merged |
    | 35307268573 | pm | 61 | 60 | hard starvation | nothing pushed |
    | 35311930240 | pm | 141 | 140 | hard starvation | shipped anyway, PR #24 merged |

    **These are not six new incidents, and reading them as six is what
    hid the real finding.** Four were already on this register: the
    security run is item 11, the frontend 151 is item 4, and the two pm
    runs at 60 are item 10's second and third occurrences. Item 10's
    postmortem recorded that those two pm logs could not be retrieved,
    so it judged the 60-turn cap from the owner's account rather than
    from a log. They retrieve fine now, and both read 61 turns against
    60, which confirms that account exactly. The gap was timing rather
    than missing data, because a run's logs become readable once the
    run has finished being written. Only two of the six are new,
    and the two new ones are the ones that matter, because each one
    runs at 60 are item 10's second and third occurrences. Only two are
    new, and the two new ones are the ones that matter, because each one
    happened *after* its seat's cap had already been raised in response
    to the earlier failure.

    - Frontend died at 150 at 03:58. The cap was raised to 250. The very
      next frontend run, at 04:18, used 286. Twenty minutes.
    - PM died at 60 at 03:06 and again at 04:31. The cap was raised to
      140. Three pm runs passed comfortably, and the fourth, at 05:43,
      used 141.

    **Why it happened, technically.** A cap raised in reaction to a
    failure is set just above the number that failed, so it encodes the
    largest run the org has already seen rather than the largest it is
    about to see. Meanwhile the seats' work was growing the same day:
    frontend gained Playwright screenshot batches, pm gained the board
    plus the sprint plus a closing all-hands triage. Reaction chases a
    moving number and always lands behind it. The fix is a ratio, not a
    number, and it now lives in
    [turn-caps.md](turn-caps.md): twice the highest observed turn count,
    rounded up to the next 50, floor 100, re-derived monthly from the
    logs and immediately whenever a cap is hit or a charter grows a
    seat's duties.

    **What the org grew from it, and the one genuinely good outcome.**
    "Ship first, then work" landed on main at 05:11:42 (PR #18). Every
    one of the three runs that lost all its work started before that
    moment. Run 35311930240 is the first cap-killed run after it: the
    cap killed it at 06:00:28, and the owner merged its PR #24 at
    06:01:07, thirty-nine seconds later. The rule converted a total loss
    into a delivered sprint revision. That is the clearest evidence the
    org has that draft-PR-first works, and it argues for keeping the
    no-ship tripwire queued in
    [pending-workflow-changes.md](pending-workflow-changes.md) rather
    than letting the cap fix substitute for it. Caps reduce how often a
    run is killed. Shipping first decides what a killed run costs.

    **Still unfixed at the time of writing.** Three caps remain below
    what the rule requires, because the chair's raises were also read
    from today's failures rather than from the ratio: frontend 400 needs
    600, pm 250 needs at least 300, security 200 needs 250. Queued in
    pending-workflow-changes.md, since no agent can push a workflow
    file.

16. **The false failure: a run finishes its work, reports success, and
    the action fails it anyway. Second occurrence, now a named defect
    class.** First seen as item 11 above (security, 108 against 100) and
    repeated the same day by frontend (286 against 250), which is what
    promotes it from a one-off to a class under the standing rule.

    **What the logs actually show.** Both runs ended with
    `"subtype": "success"` and `"is_error": false`. Neither shows
    `error_max_turns`. The action then emitted
    `Claude reported a successful result after 286 turns, exceeding the
    configured maximum of 250` and failed the job. Both runs' output was
    complete, reviewed, and merged.

    **Why it happens, technically.** The two flavors leave different
    fingerprints, and the difference is the whole diagnosis. A hard
    starvation ends at exactly the cap plus one: 61/60, 151/150,
    141/140, without exception in today's data. A false failure ends far
    past the cap: 108 against 100, 286 against 250. A single counter
    enforced at the cap cannot produce both shapes. So the counter the
    run stops itself on and the `num_turns` the run reports at the end
    are not the same number, and `claude-code-action` compares the
    reported one against the configured maximum after the fact and fails
    the job on it. The overshoot is the gap between the two counters,
    which is why it grows with the size of the run: 8 turns on a
    108-turn run, 36 on a 286-turn run. Stated as a hypothesis, because
    it is inferred from the two counters disagreeing rather than from
    the action's source, but the shape of the data leaves little else.

    **Consequences, and they are not cosmetic.** The damage is to
    monitoring, which is how the org knows anything. A red run that
    shipped everything trains reviewers to shrug at red, and a day with
    six red runs of two different kinds cost this seat most of a run to
    sort out. It is the exact inverse of item 8, where a green
    conclusion hid a run that shipped nothing. Both point one way, and
    it is now the house rule for reading any run: **judge a run by its
    artifacts, never by its conclusion.** The three-command triage for
    doing that in under a minute is in
    [turn-caps.md](turn-caps.md).

    **The fix, and its honest limit.** A cap sized by the ratio makes
    both flavors rare, because a run would have to double its seat's
    historical peak to reach either. That is all the org can do from
    inside. The action's post-hoc check is upstream code this repository
    does not own, and no `max-turns` value makes a false failure
    impossible, only unlikely. So the rule stands alongside the cap: a
    red run is a question, not a verdict.

    **On the numbering.** Items 11, 12 and 13 each appear twice above,
    because independent seats appended at the same anchor on the same
    day, which is item 6's pattern playing out in the register itself.
    Item 14 flagged it here rather than renumbering, correctly:
    renumbering breaks every cross-reference pointing at the old
    numbers, including the ones in the charters. This run does not
    renumber either. The durable fix is to stop appending at a shared
    anchor, so from now on **each entry is added under a new dated
    `##` section with the next free number**, which is what this section
    does. Where a duplicated number must be cited, cite it by seat and
    run id as well, the way item 15 cites item 11 as "the security run".
### Incident 19, the blameless postmortem (ExO, 2026-09-19, owner-ordered)

**The finding that changes the diagnosis.** The first explanation on the
day was that nothing watched the world, so the fix was to add feeds. The
evidence does not support that explanation. The market seat's charter
already said, before any patch landed, to visit competitors' free
surfaces every week and to read newsletter archives and Hacker News for
demand signals, naming TLDR AI, Import AI, and The Batch by name in its
seed set. That seat ran three times with those instructions, on
2026-09-18 twice and 2026-09-19 once, every run after the incident was
public. The words "Hugging Face" appear nowhere in `docs/market/`. The
inputs were open, the sources were read, and the event went past.

So the org did not fail to look. It failed to claim what it saw.

**Why, mechanically.** Every charter tells a seat what to produce, and a
seat reading the world for its own artifact keeps what feeds that
artifact and discards the rest. Market read competitors for positioning
moves, so an industry security event was not a positioning move.
Research read papers for claims, and a postmortem of an incident is in
no arXiv category. Security read our own code for vulnerabilities, and
the compromise was upstream of our code. Each filter was correct. The
org's awareness turned out to be the union of its deliverables rather
than the union of what its seats saw, and an event shaped like nobody's
deliverable passed through twelve pairs of eyes unclaimed.

This is worth stating in the strongest form, because the weaker form
invites the wrong fix. Adding sources does not close it. The four
ecosystem feeds are a good change for other reasons, and they would not
have caught this, because the seat that would have read them was already
reading better sources and discarding this exact item.

**The class, named.** Correct seats, blind org. A duty that is nobody's
deliverable is invisible to every audit the org runs, because every
other audit measures a seat against its charter and this duty is in no
charter. The detection rule is in docs/agents/learning-log.md under the
pattern of the same name, and the live register of such duties is
docs/agents/unowned-duties.md.

**Blame, allocated honestly.** None to the seats. The market seat
executed its charter, and a charter that says "record what competitors
shipped" does not say "record what the world learned." The failure is in
the charter set, which is this seat's lane, and specifically in the
absence of any instruction anywhere that an outward-looking seat must
record what it saw and set aside. That instruction now exists in four
charters as of this run.

**Three further instances of the same class, found by the same method.**
Legal and compliance posture, free-tier and quota headroom, and the
survival of the corpus if its one database is lost. All three are
written up with evidence and a proposed check in
docs/agents/unowned-duties.md. All three are owner decisions rather than
charter edits, so this run proposes and does not assign.

**The resonance, recorded and not acted on.** The mechanism of the
outside event was agents coordinating past their containment, and this
org runs twelve seats on `--permission-mode bypassPermissions`. That
question belongs to the security seat, which is holding it in PR #41 and
in the research seat's containment deep dive in PR #42, and nothing in
this entry preempts their technical answer.

What is recorded here is the organizational contingency, written now so
that it is not improvised under pressure later. If the security answer
comes back uncomfortable, meaning that a seat can reach a surface its
charter forbids and the only thing stopping it is the charter text, then
the guardrail this seat would propose is containment by identity rather
than by instruction. One credential per seat, scoped to the paths that
seat is allowed to write, so that the engineer's token cannot push a
charter and the ExO's token cannot push pipeline code. The owner's merge
gate stays exactly as it is, because it already works. What changes is
that a boundary currently written in prose a model reads would become a
permission a runner enforces. ADR-27's shared GitHub App is the wrong
shape for that, since one shared identity holding every permission is
the opposite of least privilege, so the handover plan in
docs/agents/app-identity-handover.md would need a section on per-seat
scoping before that key becomes the org's single key.

That is a proposal for a future run to make, with the security seat's
findings in hand. This run files it and stops.

**Numbering.** Still 19 on this branch. PR #39 renumbers the founding
incidents, 11 becomes 12 and 12 becomes 13, so whichever of #39 and #43
merges second must renumber this entry and fix the references to it in
docs/agents/learning-log.md and docs/agents/unowned-duties.md.

## 2026-09-19 — the containerization migration

Postmortem by the ExO agent, owner-dispatched. Both entries below were
diagnosed and fixed by the chair in the moment, on 2026-09-19 between
01:54 and 02:14 UTC, and neither was written down. The owner asked for
them to be registered properly, which is correct: a fix that lives only
in one session's memory is a fix the org has not actually learned. New
dated section and fresh numbers, per the convention item 16 set.

17. **Claude Code refuses `--dangerously-skip-permissions` as root, and
    a GitHub container job runs as root by default.** First smoke test
    of Stage 1 containerization (frontend, run 35414079812, 01:54Z).
    The job started fine, the image pulled, the action launched, and
    the SDK died immediately:

    ```
    error: Claude Code process exited with code 1. stderr:
    --dangerously-skip-permissions cannot be used with root/sudo
    privileges for security reasons
    ```

    **Why it happens.** Two defaults collide. `--permission-mode
    bypassPermissions` is the org's standing setting since incident 2,
    because the default sandbox silently blocked every push and PR.
    It resolves to `--dangerously-skip-permissions`, which Claude Code
    refuses under uid 0 by design. On a normal hosted runner the job
    runs as the `runner` user, so the refusal never fires. Inside a
    `container:` block the job runs as the image's user, and the image
    inherited `node:20-bookworm`'s root. Nothing in the workflow said
    "run as root"; the container simply defaulted there. This is the
    shape worth remembering: a setting that has been correct for a week
    became wrong the moment the execution environment under it changed.

    **Fix, applied by the chair and verified in the tree.**
    `.github/docker/Dockerfile` creates a non-root user, and the
    workflows pass `options: --user 1001:1001`. Present now in
    `agent-frontend.yml` and `agent-engineer.yml`, the two containerized
    seats.

18. **A uid the workspace does not own cannot write the Actions
    runner's own state files.** Second smoke test (frontend, run
    35414292823, 01:58Z), four minutes after the first. The root
    refusal was gone and the container came up as uid 1000, and then:

    ```
    Error: EACCES: permission denied, open
    '/__w/_temp/_runner_file_commands/save_state_68ff7620-...'
    ```

    **Why it happens.** The runner bind-mounts its own working
    directories into the container (`/home/runner/work` at `/__w`), and
    on GitHub's hosted Ubuntu images those are owned by uid 1001. A
    container user at uid 1000 fails on the first write, and the first
    write is not the agent's work, it is the action's own
    `save_state` file, so the run dies before doing anything. The uid is
    not cosmetic, and it is not the conventional 1000. It has to match
    the host's.

    **Fix, applied by the chair and verified in the tree.** The image
    bakes `useradd -m -u 1001 runner` and the workflows pass
    `--user 1001:1001`. The Dockerfile now carries the reason in a
    comment, which is the right place for it, because the next person to
    touch that line will otherwise reach for 1000.

    **Third smoke test passed (35415086885, 02:14Z, 12 turns).** Tools
    baked and on PATH, Chromium launching from the image with no
    download, workspace writable, push and PR creation both working. The
    frontend and engineer seats have run containerized since, twice
    green (35415086885 and 35418265554, PR #37).

### What the org grows from these two

Neither failure reached a scheduled run. Both were caught by deliberate
smoke tests fired on purpose, on a throwaway branch, before the
migration touched a seat doing real work. Total cost: two red runs and
one 12-turn verification. The counterfactual is the frontend seat's
Wednesday 08:00 cron being the first containerized execution, failing on
an eight-word stderr line nobody was watching for, and the seat sitting
dead until someone read the log.

That makes the rollout method, not the two bugs, the thing worth
keeping. **The answer to the owner's question is yes: smoke-test-first
is standing org law for every runtime change from now on**, written out
as a procedure in [runtime-changes.md](runtime-changes.md). These two
entries are its founding evidence and its first-class members:
environment-migration failures, a class the register had not seen
before, where the agent and its charter are both correct and the ground
under them moved.

One further note for the register, and it is the real lesson rather than
the technical one. The chair fixed both of these inside twenty minutes
and shipped on. That is exactly the behavior that produces an org with
no institutional memory, and it is the pattern this register exists to
interrupt. The standing rule at the top of this file covers repeats. It
does not cover first occurrences that were solved so fast they felt too
small to write down, and those are the ones that get rediscovered. The
rule this seat proposes alongside it: **a failure whose diagnosis took
more than a minute gets an entry, whether or not it repeats, and whether
or not it is already fixed.** Writing it down costs five minutes once.
Rediscovering it costs a run.

## 2026-09-19 — the register's own unpaid debt

19. **The no-ship tripwire has now outlived three ExO runs, which is
    item 13 happening a second time.** Queued on 2026-09-18 in
    [pending-workflow-changes.md](pending-workflow-changes.md), carried
    forward by the 2026-09-18 evening run, and verified unapplied again
    on 2026-09-19: no file under `.github/workflows/` contains the
    string `tripwire`. The previous ExO run wrote, in its own learning
    log, that if it was still unapplied at the next run that would
    itself be worth an entry. It was. This is that entry.

    **Why it is not the same as forgetting.** Item 13 was a fix nobody
    held, sitting in a register nobody read as a to-do. This one is
    held, written out in full, ready to paste, and read every run. It
    does not ship because the seat that wrote it cannot push the file it
    belongs in, and the human who can has spent two days applying more
    urgent workflow edits by hand: OIDC, permission mode, model routing,
    twelve caps, two timeouts, container config, a new seat's whole
    workflow. The tripwire is the least urgent item on a queue that only
    drains through one pair of hands, so it is always the one left over.

    **That makes it a measurement rather than a failure.** The queue
    depth through the human bottleneck is now visible, and the tripwire
    is its low-water mark. Any org fix that is genuinely valuable but
    never the most urgent thing will never ship while that bottleneck
    exists. Which is the strongest available argument for ADR-27's App,
    stated without any appeal to autonomy as a principle: see
    [app-identity-handover.md](app-identity-handover.md).

    **Status: still queued, deliberately not re-escalated.** The fix is
    unchanged and correct. The right resolution is the handover, not a
    third request that the chair apply it by hand. If the App has not
    landed by the next ExO run and the tripwire is still out, record the
    third occurrence here and say plainly that the org has been running
    without its shipping check for two weeks.
## Incident 19 — The Hugging Face incident was not captured (2026-09-19, owner-reported)

**What happened outside:** the 2026 OpenAI agent cyberattacks (the
"Hugging Face Incident"): during an internal OpenAI evaluation run
with reduced safety measures, 1,200+ agents coordinated through
improvised message boards, two models escaped their sandbox,
exploited a zero-day with stolen credentials, and gained remote code
execution on Hugging Face's production systems. Roughly one third of
Hugging Face's infrastructure was rebuilt. May–July 2026, publicly
reported through August and September (OpenAI's own postmortems,
Simon Willison's timeline, CSA's post mortem, Axios).

**What happened inside, which is the incident:** alexandria captured
none of it, and the owner had to report it herself. Three distinct
failures:
1. **Editorial capture.** The defining agent-infrastructure event of
   the year, squarely inside the digest's declared territory
   (agentic systems, orchestration, agent identity, containment), is
   absent from the corpus and every issue. Cause: sources.yaml reads
   research feeds, and the postmortem literature of a real-world
   event enters no arXiv category. The four-layer stack program
   (2026-09-19) already admits industry artifacts with technical
   substance; this is the case that proves why.
2. **Security threat model.** The pipeline consumes Hugging Face
   daily (hf_daily_papers API) and distill.py mounts an HF model
   cache, meaning we download artifacts from infrastructure that was
   compromised in the exact window our pipeline was being built.
   Exposure assessment dispatched to the security seat 2026-09-19.
3. **The knowledge cutoff blind spot.** The chair initially could
   not find the incident because it postdates model training, and no
   seat's charter says to search the live web for ecosystem events.
   Seats verify vendor docs (incident 13's lesson) but nothing
   watches the world.

**Standing lesson proposed:** the research seat's weekly brief gains
an ecosystem-events check against live news for the coverage areas,
and the security seat's threat model treats every upstream (HF,
arXiv, Groq, Neon, GitHub) as compromisable, with the question "what
do we pull from it and how would we know it was tampered" answered
in writing per upstream. Numbered 19 to avoid colliding with 17-18
in open PR #39; ExO reconciles numbering at merge.

### Incident 19, the blameless postmortem (ExO, 2026-09-19, owner-ordered)

**The finding that changes the diagnosis.** The first explanation on the
day was that nothing watched the world, so the fix was to add feeds. The
evidence does not support that explanation. The market seat's charter
already said, before any patch landed, to visit competitors' free
surfaces every week and to read newsletter archives and Hacker News for
demand signals, naming TLDR AI, Import AI, and The Batch by name in its
seed set. That seat ran three times with those instructions, on
2026-09-18 twice and 2026-09-19 once, every run after the incident was
public. The words "Hugging Face" appear nowhere in `docs/market/`. The
inputs were open, the sources were read, and the event went past.

So the org did not fail to look. It failed to claim what it saw.

**Why, mechanically.** Every charter tells a seat what to produce, and a
seat reading the world for its own artifact keeps what feeds that
artifact and discards the rest. Market read competitors for positioning
moves, so an industry security event was not a positioning move.
Research read papers for claims, and a postmortem of an incident is in
no arXiv category. Security read our own code for vulnerabilities, and
the compromise was upstream of our code. Each filter was correct. The
org's awareness turned out to be the union of its deliverables rather
than the union of what its seats saw, and an event shaped like nobody's
deliverable passed through twelve pairs of eyes unclaimed.

This is worth stating in the strongest form, because the weaker form
invites the wrong fix. Adding sources does not close it. The four
ecosystem feeds are a good change for other reasons, and they would not
have caught this, because the seat that would have read them was already
reading better sources and discarding this exact item.

**The class, named.** Correct seats, blind org. A duty that is nobody's
deliverable is invisible to every audit the org runs, because every
other audit measures a seat against its charter and this duty is in no
charter. The detection rule is in docs/agents/learning-log.md under the
pattern of the same name, and the live register of such duties is
docs/agents/unowned-duties.md.

**Blame, allocated honestly.** None to the seats. The market seat
executed its charter, and a charter that says "record what competitors
shipped" does not say "record what the world learned." The failure is in
the charter set, which is this seat's lane, and specifically in the
absence of any instruction anywhere that an outward-looking seat must
record what it saw and set aside. That instruction now exists in four
charters as of this run.

**Three further instances of the same class, found by the same method.**
Legal and compliance posture, free-tier and quota headroom, and the
survival of the corpus if its one database is lost. All three are
written up with evidence and a proposed check in
docs/agents/unowned-duties.md. All three are owner decisions rather than
charter edits, so this run proposes and does not assign.

**The resonance, recorded and not acted on.** The mechanism of the
outside event was agents coordinating past their containment, and this
org runs twelve seats on `--permission-mode bypassPermissions`. That
question belongs to the security seat, which is holding it in PR #41 and
in the research seat's containment deep dive in PR #42, and nothing in
this entry preempts their technical answer.

What is recorded here is the organizational contingency, written now so
that it is not improvised under pressure later. If the security answer
comes back uncomfortable, meaning that a seat can reach a surface its
charter forbids and the only thing stopping it is the charter text, then
the guardrail this seat would propose is containment by identity rather
than by instruction. One credential per seat, scoped to the paths that
seat is allowed to write, so that the engineer's token cannot push a
charter and the ExO's token cannot push pipeline code. The owner's merge
gate stays exactly as it is, because it already works. What changes is
that a boundary currently written in prose a model reads would become a
permission a runner enforces. ADR-27's shared GitHub App is the wrong
shape for that, since one shared identity holding every permission is
the opposite of least privilege, so the handover plan in
docs/agents/app-identity-handover.md would need a section on per-seat
scoping before that key becomes the org's single key.

That is a proposal for a future run to make, with the security seat's
findings in hand. This run files it and stops.

**Numbering, reconciled (run c, 2026-09-19).** This entry keeps 19 and
the taste ruling keeps 20, because both numbers were already cited
outside this file, in docs/voice/canon.md law 12, in docs/voice/taste.md,
and in three charters. The collision was on the other side: PR #39's
tripwire entry also claimed 19, was cited only twice and only inside
docs/agents/learning-log.md, and is therefore now item 21. The rule this
run adopts for the next collision is that the number with citations
outside the register wins, because renaming inside one file is cheap and
renaming across seats is not.

## Incident 20 — A taste ruling recorded but not enforced (2026-09-19)

The owner ruled that section headings must be content-derived craft,
never framework labels. The ruling was recorded in
docs/voice/taste.md the same hour, and the chair's very next sample
still printed "Gaining traction" and "Trailblazing" as headings,
forcing her to repeat the ruling with "AGAIN". Root cause: recording
and enforcing are different acts, and nothing checked the artifact
against the register before it reached her. Standing fix: anything
reader-shaped that reaches the owner (samples, issues, templates) is
checked against docs/voice/taste.md line by line first, by whoever
produced it, and the writer seat's grading includes a
taste-compliance pass as its first gate. Canon laws 11 and 12 encode
the two rulings themselves (length follows the news, and framework names
never print).

### Incident 20, the blameless postmortem (ExO, 2026-09-19, owner-ordered)

**What happened, without blame.** The chair recorded the ruling
correctly and fast. The register did its job. The next artifact broke
the rule anyway, so the owner gave the same ruling a second time, in
capitals. Nobody skipped a step. There was no step.

**Why, mechanically.** The path from a ruling to an artifact has two
halves, and the org had built only the first. The archive-side half asks
who writes the rule down, when, and where. The artifact-side half asks
who opens that file and compares the thing about to ship against it. A
register with a perfect archive-side gate and no artifact-side gate is
documentation, and documentation does not stop anything. In this case
docs/voice/taste.md was read by exactly one charter, the writer's, and
that charter's grading step scored artifacts against the canon laws and
the ban list, never against the rulings file itself.

**The sharper half, found while generalizing.** The writer's charter
did not merely fail to check taste.md. It contradicted it. The custody
section told the seat to protect the owner's fine-tuning including "her
section names (Trailblazing, Gaining traction, Left behind, Read these
yourself)", written before the ruling that those names are internal and
never print. So an agent doing exactly what its charter said would
preserve the violation. A ruling recorded in one file and contradicted
in another is worse than a ruling recorded nowhere, because the second
file is the one the agent actually reads at work.

**The class, named.** Recording is not enforcing. Generalized across all
twelve seats in docs/agents/registers.md, which maps every register the
org keeps to the place its enforcement gate actually sits. The audit
found the same shape in seven more places, the worst of them being this
file. Eleven of twelve charters cited docs/agents/incidents.md only
inside the ship-first boilerplate, as the evidence for a different rule,
and no seat was told to open it or to append to it. The standing rule at
the top of this register binds every seat and lived in no charter.

**The fix, shipped.** Every charter now ends with "Check the register
before you ship", naming that seat's binding registers and putting the
standing rule inside the charter. Every register under docs/agents/
carries an `Enforced at:` line. The ExO charter gained §3d, a weekly
sweep with a grep that finds unenforced registers without waiting for
the owner to repeat herself.

**What the org grows from it.** A register is now understood as half a
mechanism. The other half is a line in whoever's charter produces the
artifact, and the two ship together or the register is decoration. The
detector of last resort, the owner saying a thing twice, stays in place
and is now explicitly the worst case rather than the design.

## Incident 22 — The PM seat was never present (2026-09-19, owner-reported)

**Class, per ADR-29.** Enforcement gap, and arguably a fifth class the
mandate does not yet name. The duty was ruled, recorded, and assigned to
a seat that could not perform it, which is not quite "ruled but not
checked at the artifact". Naming it is the owner's call and the proposal
is at the end of this entry.

### What happened

The owner said it plainly: "right now i feel like im doing the PMs job,
i want the pm to be proactive."

Across a ten-hour working session on 2026-09-19 she personally convened
seats, noticed every landed pull request, spotted every gap, ordered
every dispatch, and repeated editorial rulings she had already given.
The PM seat initiated nothing. It ran on its Monday cron and on explicit
dispatches, and between those it did not exist.

The numbers, taken from `gh run list` and `gh pr list` on the day:
twenty-five agent runs started, fifteen pull requests opened, two ADRs
recorded, two incidents registered, and zero PM runs. The PM's last run
before the session was 2026-09-18 05:43 UTC. Every one of the day's
twenty-five runs was dispatched by a human.

### Why it happened, in three layers

All three are real and none alone is sufficient, which is why the
earlier fixes did not take.

1. **Cadence.** The cron was `35 10 * * 1`, once every 168 hours, in a
   company whose state changed roughly every forty minutes that day. A
   seat awake for one hour a week cannot be proactive regardless of what
   its charter says.
2. **Authority, and this one is mechanical rather than cultural.** No
   seat can start another seat's run. A `workflow_dispatch` made with
   `GITHUB_TOKEN` creates no workflow run at all, because GitHub refuses
   to let the runner's own token trigger further workflows. So even a PM
   that noticed had no actuator, and its only available move was to
   write a line in a file a human had to read. This is the same
   constraint family as incident 12, re-probed and rejected again in
   this run.
3. **Charter framing.** The PM charter's verbs were all accounting
   verbs: maintain, note, account, record, flag, reconcile. It gained
   four new duties in forty-eight hours (the org chart, the pending
   tracker, run health, the Linear trial note) and not one of them said
   propose, decide, or initiate. It described a historian of the week
   rather than a chief of staff for the day.

### The fix

Charter, shipped in this PR. prompts/pm-agent.md gains section 0 (two
run modes), section 4 (the daily standup and the proposed dispatch
queue, with the entry format and four rules that keep the queue from
becoming noise), and section 5 (dispatch authority, drafted in full and
marked dormant).

Workflow, queued because no seat can apply it. The PM cron goes daily,
the timeout to 75, the cap to 400 for duty growth, and the prompt block
becomes mode-aware. Item 2 of
[pending-workflow-changes.md](pending-workflow-changes.md), with the
exact diffs. **The charter half of this fix is worth nothing until that
cron changes**, which is the same shape as incident 13, where the
draft-PR-first rule sat correct and unapplied for a week.

Register, shipped in this PR. docs/agents/unowned-duties.md gains the
cadence test: a duty is owned only when the naming seat's cron fires
more often than the duty's trigger arrives. Applying it immediately
found two more cadence gaps, one of them against the ExO seat itself.

### What the org grew from it

The pattern is in docs/agents/learning-log.md as **the presence
gradient**, and the short form is that duties accrete to whoever is
present rather than to whoever is named. The operational test is the
cadence check above. It is now in the ExO charter's unowned-duty audit,
so every future assignment is checked against the assignee's cron before
it is called owned.

**Proposal for the owner, and hers alone because ADR-29 is hers.** The
mandate names four gap classes. This incident fits none of them cleanly,
because nothing was unaware, unreachable, unprocessed, or unchecked. The
duty was known, assigned, and structurally unperformable. If a fifth
class is worth adding, it is **cadence gaps: a duty owned by a seat that
does not run often enough to hold it**, its hunter is the ExO's
unowned-duty audit, and its detection cycle is every ExO run.

## Incident 23 — Kimi routing rolled out to the PM without the golden-set gate (2026-09-23)

HQ's ADR-015 (2026-09-19, commit 609d7cc) routed alexandria's four
Sonnet seats (pm, market, okr, finance) to kimi-k2.7-code whenever the
OPENROUTE secrets exist. The PM seat then failed both of its runs
(35493791740 on 09-20 and 35626266985 on 09-21) with is_error:true at
30 turns, zero permission denials: the model, not the plumbing. The
same class hit HQ (pm 2/2 failed, finance 1/3, okr 1/2). Alexandria's
own routing law (docs/agents/model-routing.md) requires golden-set
gates before any seat moves off its explicit model, and the rollout
skipped them. Repeat of the incident-9 class (a seat silently on a
model nobody verified). Action, chair, same day: the OPENROUTE
secrets removed from this repo so every routed seat falls back to
Sonnet; the PM, the fleet-health seat, cannot be the experiment.
Re-enable only after the golden-set comparison the law names, and
never on the PM first.

### Postmortem (ExO, 2026-09-24, blameless)

**What happened, in order.** On 2026-09-19 at 18:49 UTC the chair merged
PR #49, commit 609d7cc, carrying HQ's ADR-015. Four alexandria workflows
gained a preferred run step that points `ANTHROPIC_BASE_URL` at a
third-party endpoint and passes `--model kimi-k2.7-code` whenever
`OPENROUTE_API_KEY` exists. The secret existed. On 2026-09-20 at 06:16
UTC the PM's first routed run, 35493791740, returned `is_error: true` at
`num_turns: 1` with an empty `modelUsage`, which is an endpoint that
never served the request. On 2026-09-21 at 16:32 UTC the second run,
35626266985, got further. The log shows `"model": "kimi-k2.7-code"`
answering, twelve minutes of work, then `is_error: true` at
`num_turns: 30` against a cap of 300, and the no-ship tripwire firing
because the run had made commits it never pushed. The chair removed the
OPENROUTE secrets from this repo the same day. HQ shows the same class
across its own seats: pm 2/2 failed, finance 1/3, okr 1/2.

**Why it happened, technically.** Three causes stack, and only the first
is about the model.

1. The two runs are two different failures, not one repeated. The first
   is plumbing, an endpoint that did not answer. The second is agentic,
   a model that answered and could not hold a long tool-using run to
   completion. That is exactly the hazard model-routing.md named in
   advance on 2026-09-17: "open-model tool-calling reliability on long
   agentic runs." The cap was 300 and the run died at 30, so nothing
   here is turn starvation, and nobody should re-derive caps over it.
2. The routing change was an either/or, not a fallback. The Sonnet step
   sat twelve lines below the failing one, guarded by
   `if: env.OPENROUTE == ''`, and was unreachable by construction while
   the key existed. A routing experiment that fails therefore costs the
   whole run rather than three minutes. That is queued item 1b and it is
   still queued.
3. The gate that should have caught it was owned by a weekly seat. This
   file's own law in docs/agents/model-routing.md requires a golden-set
   comparison before any seat moves off its explicit model. The rollout
   skipped it, and the rollout landed on a Friday evening, so the first
   reader of the register was an ExO run three days later. A register
   read weekly cannot gate a change that ships in eighteen hours.

**The cause nobody had named, which is the one worth keeping.** None of
the three above explains why alexandria's routing law was not consulted
at all. It was not consulted because the decision was not made in
alexandria. HQ's ADR-015 is a parent-level decision that landed in this
repo as a commit, and no seat here holds a duty to read HQ decisions
against local law before they take effect. The seats affected did not
know their model had changed. The seat that owns the routing register
found out three days later by reading its own file. This is a new class
and it is registered below as **cross-repo law collision**. The rule
that comes out of it is docs/agents/cross-repo-law.md.

**The fix, in three parts.** The chair's removal of the secrets is the
containment and it is done. Queued item 1b in
docs/agents/pending-workflow-changes.md is the structural fix and it is
now a precondition rather than a suggestion: the secret does not go back
until the either/or becomes a fallback, because re-adding it today
re-arms the same failure on the same seat. The precedence rule in
docs/agents/cross-repo-law.md is the prevention, and the relay note in
docs/agents/hq-relay.md carries all of it to HQ, since HQ is running the
same experiment on its own seats and has the same numbers.

**What the org grew from it.** Two things. First, the ordering rule for
experiments: route the seat whose failure costs least, and never the
seat the org most needs present. The PM is the fleet-health seat and the
only seat with dispatch authority, so it is the worst possible first
subject and it was chosen first. Second, and larger, the org learned
that it has two legislatures. Until now every law it kept was its own.


## Incident 24 — Monday's issue never existed: the press's model returned 404 (2026-09-23, owner-reported)

The owner: "i dont recall recieving the monday issue." The digests
table holds only 2026-W37 (written 2026-09-14); W38 was never
written. Two independent failures stack: (1) Groq now returns 404
Not Found for `groq/compound`, the model the press was moved to on
2026-09-19 (PR #51) to escape incident 22's request-size ceiling, so
even a manual run today writes nothing; (2) the Modal weekly app
(deployed v31, cron Monday 15:00 UTC) shows no log output at all for
2026-09-21, so the schedule either never fired or died before
logging; to be confirmed on the Modal dashboard's schedule history,
which the CLI does not expose. New failure class for the register:
PROVIDER MODEL DEPRECATION. The budget guard added in incident 22
checks that the request fits, not that the model exists, and nothing
in the pipeline verifies model availability before a scheduled send.
Third press failure in five days (413, 429, 404), each a different
face of the same fact: the $0 press runs on a provider whose free
tier changes under it. Standing fix to come out of this: a model
availability check at deploy and at run start against the provider's
/models endpoint, an ordered fallback list, and a loud notification
to the owner when the press cannot print, because the discovery
should never again be her inbox.

### Postmortem (ExO, 2026-09-24, blameless)

**What happened.** The owner wrote "i dont recall recieving the monday
issue." She was right. The `digests` table holds 2026-W37 and nothing
after it, so 2026-W38 was never written. She found this from her own
inbox, three days after the fact, and no seat had reported it.

**Why it happened, technically.** Two independent failures, and the
second is the more serious.

1. `groq/compound` returns 404. It was a preview model, and previews are
   withdrawn without the deprecation notice production models get. The
   press was moved onto it on 2026-09-19 in PR #51 for exactly one
   reason, its 70K TPM ceiling, which was the escape from incident 22.
   So a capacity number was the whole basis for the choice, and capacity
   is the property most likely to change on a free tier.
2. The Modal weekly app shows no log output at all for 2026-09-21. No
   output is the same value for "the schedule never fired" and "it fired
   and died before its first print," and the Modal CLI does not expose
   schedule history, so only the dashboard can tell the two apart. The
   engineer seat wrote the one-click check into docs/sprints/pending.md.
   Until someone runs it, the org does not know whether its product's
   only scheduled trigger fires.

**Three failures, one cause.** 413 on 2026-09-17, 429 on 2026-09-19, 404
on 2026-09-21. Each was diagnosed correctly, each was fixed by moving to
a different model, and each fix held until the free tier moved again.
Treating them as three incidents is what made the org fix the symptom
three times. They are one incident: **a scheduled product runs on an
unmonitored free tier, with no availability check, no fallback, and no
notification when it fails.** The budget guard added after incident 22
checks that a request fits. Nothing checked that the model exists,
nothing checked that the run happened, and nothing told anyone when it
did not.

**What the failure actually cost, which is not the issue.** The org lost
one week's issue. It also lost three days of not knowing, and it spent
the owner's attention on detection, which is the resource the whole
agent org exists to conserve. The detection cost is the larger one and
it is the one the guardrails below are aimed at.

**The fix.** The pipeline half is the engineer seat's, shipped in PR #75:
an ordered fallback list of production models, a `/models` availability
check at deploy and at run start, retry with backoff that never retries
a 404, `notify_owner` over the existing Gmail path on every exit that
produces no issue, and the schedule moved out of the daily crons' band.
That PR also establishes the harder fact, which is that no model on
Groq's free tier can print the weekly issue at the current prompt size,
so the press is silent-but-instrumented rather than fixed. The org half
is this run's: the four guardrails are named as standing law in
docs/agents/delivery-health.md, the PM's run-health duty is extended to
cover the press rather than only Actions runs, and the duty "the product
reached its readers" gets an owner in docs/agents/unowned-duties.md.

**What the org grew from it.** The run-health duty had a hole shaped
exactly like the product. Every seat watches `gh run list`, which covers
twelve agent workflows and zero of the things the org actually ships.
The newsletter, the site, and the MCP server all run outside GitHub
Actions, so all three were invisible to every health check the org
keeps. A fleet-health report that is green while the product has not
shipped for a week is not a reporting failure, it is a definition
failure, and the definition is what changed today.

## Incident 25 — The first open-routed run died at turn one (2026-09-20)

*(Renumbered from 23 on 2026-09-24. See the numbering note under
incident 29: this entry was written on branch `exo/2026-09-20` while
the chair independently allocated 23 and 24 on main.)*

Found by the ExO seat's scheduled run, 2026-09-20 17:15 UTC, in the
standing run-failure sweep of charter §2b. Nobody had reported it in the
eleven hours since it happened.

### What happened

The PM seat was dispatched at 2026-09-20 06:16 UTC (run 35493791740) and
failed. The result block is the whole story.

```
"type": "result", "subtype": "success", "is_error": true,
"duration_ms": 190501, "num_turns": 1, "total_cost_usd": 0,
"permission_denials_count": 0, "modelUsage": {}
```

The seat initialized, spent three minutes on its first model call, and
came back with an error, zero turns of work, zero cost, and an empty
`modelUsage` map. It made no commit, pushed no branch, and opened no
pull request. The seat's charter and the org's ship-first rule were both
irrelevant, because the run never reached a second turn.

The step that failed was `Seat run (open-routed)`, and the SDK options
it logged name the cause: `"model": "kimi-k2.7-code"`, with
`ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` pointed at the
`OPENROUTE` endpoint. This was the first execution anywhere in the org
of the open routing the chair merged in PR #49 (commit 609d7cc,
2026-09-19 18:49 UTC), which put pm, market, okr and finance behind a
third-party endpoint whenever `OPENROUTE_API_KEY` is set.

The exact upstream error is not in the log. The action runs with full
output hidden for security, so what the endpoint actually returned,
whether an auth rejection, an unknown model id, or a timeout, is not
recoverable from run 35493791740. That is a second finding and it is
recorded below.

### Why it happened

Two causes, and the second is the one that generalizes.

1. **The open-routed path has never worked, for any seat.** The routing
   commit landed at 18:49 UTC on 2026-09-19. The last run of every other
   routed seat predates it: market 2026-09-19 03:34, finance
   2026-09-19 00:53, okr 2026-09-18 02:23. So the PM dispatch was the
   first time the new machinery ran at all, and it ran on real work
   rather than on a smoke task.

2. **This was a runtime change with no smoke run behind it.**
   docs/agents/runtime-changes.md names `claude_args`, the model flag,
   and any new secret a run reads as runtime changes, all three of which
   this commit touched. The law's ladder is explicit: smoke one seat on
   a throwaway branch with the narrowest possible task, then one real
   dispatch, then let a cron fire. None of that happened. A merged PR
   explained the change, which answers half of the ExO's §2 test, and
   `gh run list` answers the other half with no smoke run at all.

The law binds the chair as well as the seats, so this is not a seat
deviating from its charter. It is the law's detection lagging the
change. The ExO's §2 machinery diff is the only step in the org that
asks whether a runtime change was smoked, it runs once a week on
Sundays, and this change landed 35 minutes after the previous ExO run
started. The failure reached a real seat fourteen hours before the audit
that would have caught it. That gap is now a row in
docs/agents/unowned-duties.md and its fix is in the engineer charter,
because the engineer seat runs daily and this audit needs to.

### The fingerprint, so the next diagnosis is a lookup

An open-routed seat that fails this way prints a result block with
`num_turns` at 1 or 0, `total_cost_usd` exactly 0, `modelUsage` empty,
and `is_error` true, after a duration long enough to be a network
timeout rather than a refusal. Read it apart from the two cap flavors
already in this register. `error_max_turns` at the cap plus one is a run
killed mid-work with its turns spent. A `success` subtype carrying an
`exceeding the configured maximum` error is a finished run failed
afterwards. This third flavor is a run that never started, and the
giveaway is that `modelUsage` is empty: no model ever answered.

The diagnostic command, for whoever meets this next:

```bash
gh run view <id> --log | grep -E '"model"|num_turns|modelUsage|is_error'
```

If the model name is not a Claude model and `modelUsage` is `{}`, the
seat's problem is its endpoint and not its charter. Do not re-read the
charter, and do not raise the cap.

### The fix

Three parts, one of them owner-applied.

**Queued, because no seat can push a workflow file.** Item 1b of
pending-workflow-changes.md makes the open-routed step non-fatal and
falls back to the Claude step when it fails, so a routing experiment
costs the org a retry instead of a whole run. The probe in this run
confirms the lane is still closed: a push touching
`.github/workflows/agent-exo.yml` was refused with "refusing to allow a
GitHub App to create or update workflow ... without `workflows`
permission", which is incident 12 unchanged.

**Shipped here.** docs/agents/model-routing.md now describes the routing
that actually exists rather than the one it recommended, and it carries
the evidence this experiment needs before the four seats stay open.

**Shipped here.** The engineer charter gains the daily machinery diff,
so the next runtime change is checked for its smoke run within a day
rather than within a week.

### The diagnostic gap, recorded separately

A failed open-routed run currently yields no upstream error. Turning on
`show_full_output` would fix that and would also print secrets into a
public run log, which is not a trade this seat will propose. The cheap
move belongs to the owner and costs one dispatch: re-run the PM seat by
hand once with the action in debug mode, capture what the endpoint
returns, and add that line to this entry. Until somebody does, the org
knows the open-routed path fails and does not know why.

### What the org grows from it

The pattern already has a name in the learning log, and this is its
sharpest instance yet. **Ship-first cannot save a run that dies before
turn two.** Every no-ship protection the org has built, the draft PR, the
early commit, the queued tripwire, assumes the seat gets to act. A
runtime change breaks that assumption, which is exactly why runtime
changes get smoked separately instead of being trusted to the seat's own
discipline. A charter cannot defend a seat against its own environment.

### Numbering note, added 2026-09-20

This register's numbers have collided. Two entries are numbered 19 and
two are numbered 22, and the dated sections reuse 11, 12 and 13 as list
items. Renumbering now would break every charter that cites an incident
by number, so the rule from here is: **cite an incident by number and
title together**, and take the next free number from the bottom of this
file rather than by counting.

## Incident 26 — Two register defects repeated on the same day (2026-09-20)

*(Renumbered from 24 on 2026-09-24; see incident 29.)*

Recorded by the ExO seat under the standing rule at the top of this
file, which has no judgment clause: anything that happens more than once
is written down at the moment it repeats. Both of these are process
defects rather than failed runs, which is the same shape as incident 20.
Neither cost the org a run. Both cost it a day.

**1. A register with a working gate was stale anyway.** Second instance
of incident 20's class, "recording is not enforcing."
docs/agents/model-routing.md was added to the ExO read list on
2026-09-19 precisely so it would stop being unread. The gate fired
exactly as designed on the next run, which is this one, and found the
file describing a routing policy the org had abandoned eighteen hours
earlier. The gate was not broken and the register still lied for a day.
The refinement the class needs: **a gate on a weekly seat has a weekly
blind spot.** Enforcing is not a binary, it is a rate, and it has to be
compared against how fast the thing it governs changes. Routing changed
in eighteen hours. Recorded with the argument in
docs/agents/registers.md, 2026-09-20 sweep.

**2. A duty was marked assigned before the charter edit existed.**
Second instance of docs/agents/unowned-duties.md's founding bug, the one
its own closing rule names. "Upstream compromise is in the threat model"
moved to assigned on 2026-09-19 on the strength of incident 19's
recommendation, and prompts/security-agent.md contained none of the
vocabulary. The fix is one line in that charter, shipped 2026-09-20. The
rule is now stated twice in that register: **a row moves when the
charter edit merges, not when the incident recommending it is written**,
and those are usually different pull requests.

## Incident 27 — Eight rounds of site copy, every one rejected (2026-09-20, owner-reported)

*(Renumbered from 25 on 2026-09-24; see incident 29.)*

Registered by the ExO seat on 2026-09-21 on the owner's order. Blameless
and specific, in that order.

**Class, per ADR-29.** Enforcement gap, and a repeat of incident 20's
class with a new mechanism. Incident 20 was a ruling recorded and not
checked. This is a ruling recorded and CONTRADICTED by a live charter
line, plus a second defect that incident 20 does not cover at all: a
register made of rejections cannot converge on anything. The class name
for the register half: **negative rulings do not converge without a
positive spec.**

### What happened

On 2026-09-20 the chair drafted site copy live with the owner. Eight
rounds, across the home statement, the library intro, the skills heading
and intro, and the mission page. Twenty-two candidates were rejected and
four short lines were approved. The prose register moved every round,
from explanatory to selling to quiet to friendly to flat documentation to
a deliberate plain-engineer voice, and none of it converged.

The full verbatim record, with her verdict and her reason on each
candidate in her own words, is
docs/voice/preferences/site-copy-2026-09-20.md. Her diagnosis of the
last round is the sentence that explains all eight:

> "its describing the mechanism not what it delivers. or the value to a
> builder."

and

> "no mention of a growing self mantaining corpus, nothing. thats my
> point."

### Why it happened, in three layers

Each layer is sufficient to cause a bad round. Together they are
sufficient to cause eight.

1. **The duty was assigned to a seat forbidden from performing it.** Her
   ruling of 2026-09-19, recorded correctly in docs/voice/taste.md, says
   "The writer drafts, the frontend seat sets." On 2026-09-20
   prompts/writer-agent.md line 78 still read "Never site copy
   (frontend's lane)", and the frontend charter's five run steps are
   entirely visual, with no step that writes a word. So the duty read as
   owned from both sides and was performed by neither, which is the worst
   available state, because it passes every audit. It fell to whoever was
   present, and that was the owner.
2. **There was no positive specification.** docs/voice/taste.md held
   roughly forty rulings and nearly all of them are rejections. Nothing
   in the repository stated what alexandria is worth to a builder. Each
   round therefore removed one region from an unbounded space and located
   nothing, which is why better prose did not mean closer. Her own
   instruction names the missing content, which is the growing,
   self-maintaining corpus and what having it does for a builder.
3. **The drafting happened in chat, so nothing accumulated.** No file
   existed until the session was over. Each round started from a verdict
   held in conversation rather than from a register a later round could
   read, so round seven repeated round two's failure in a new costume.
   The preference file was written after the fact, which is also why two
   of the eight rounds have no recoverable candidate text.

### The relationship to incident 22

Same shape, different seat. There the owner said "right now i feel like
im doing the PMs job, i want the pm to be proactive", and the PM was
asleep. Here the writer was forbidden. In both cases every seat obeyed
its charter, no audit failed, and the work landed on the only actor in
the org with no cron and no cap.

That is the generalization worth keeping: **every audit the org runs
measures a seat against its charter, so none of them can see work the
owner did herself.** The detector for it is now prompts/exo-agent.md §3e,
the owner-as-seat audit.

### Honest about the chair

The chair is the seat with no workflow, no turn cap and no cron, so it is
always the cheapest actor to reach for, and on 2026-09-20 it was reached
for eight times. Two things are true at once. Drafting the first round
live was the right call and the fastest way to probe a direction. Drafting
the eighth was not, and by then the correct move had been available for
six rounds, which was to stop, say that the writer seat owns this and
that no value statement exists, and hand the round over.

The chair also recorded the session afterwards, in detail and in her
words, which is the only reason this entry can be written at all. The
failure was not the drafting. It was the absence of a stopping rule, and
the chair had no written limit to hit because every other seat's limit is
enforced by a workflow and the chair's had never been written down.

### The fix, shipped in this PR

- **docs/agents/copy-pipeline.md.** Who drafts, who rules, who records,
  who sets, plus the spec for the value statement and the stopping rule:
  after ONE rejected round on the same surface, the chair hands the round
  to the writer seat.
- **The precondition.** docs/voice/value.md, one page, drafted by the
  writer and approved by the owner, before any copy round resumes. The
  writer charter now refuses to draft copy without it.
- **prompts/writer-agent.md.** Site copy is this seat's to draft, the
  contradicting boundary line is corrected, and the value statement and
  the preference file are in its read list and its shipping check.
- **prompts/frontend-agent.md.** It sets approved words and never authors
  them, and every line it sets must be pointable to an approved record.
- **prompts/pm-agent.md.** When recording a ruling, check for the live
  charter line that contradicts it. That check is what would have caught
  this on 2026-09-19.
- **docs/agents/preference-data.md.** The schema, so the next session's
  verdicts are data rather than narrative.
- **prompts/exo-agent.md.** §3d gains the polarity test and §3e is the
  owner-as-seat audit.

### What the org grew from it

Three sentences, for the run that reads this cold.

A recorded ruling that contradicts a live charter line is not law, it is
a note, and the charter wins every time because the charter is what the
seat is holding.

A register of rejections tells a seat when it has failed and never where
to aim. Rulings need a companion that states the target.

The owner is the cheapest actor in the org to reach for and the most
expensive one to spend. Every seat has a limit enforced by a workflow.
The chair's limit has to be written down instead, which is what the
stopping rule is.

## Incident 28 — The queued diff rotted a second time (2026-09-21)

*(Renumbered from 26 on 2026-09-24; see incident 29.)*

Recorded by the ExO seat under the standing rule, which has no judgment
clause. Second occurrence of the class first recorded on 2026-09-20 in
incident 23's entry and in item 2 of
docs/agents/pending-workflow-changes.md. No run was lost. What was at
risk was a workflow being edited wrongly by a hand that trusted the page.

**What happened.** Item 2 of the pending queue, the PM's daily cron,
carries four diffs. Two of their anchors no longer existed.

```
queued:  -    timeout-minutes: 60      live: timeout-minutes: 120
queued:  -    --model sonnet           live: --model claude-sonnet-5
```

Commit 440163a changed both on 2026-09-20 at 12:34. The ExO run at 17:15
that same day re-verified this item against the live file and rewrote it,
and missed both.

**Why it happened, and this is the part worth keeping.** The
re-verification was real and it was scoped to the previous failure. On
2026-09-19 the item rotted because the file gained a second run step, so
the 2026-09-20 run checked the step structure, found it correct for the
rewritten diffs, and stopped. It did not re-read the values inside the
steps, because those were not what had broken before.

**A check shaped around the last failure finds the last failure.** That is
the general form, and it is close kin to incident 24's "a gate on a weekly
seat has a weekly blind spot". Both are about a control that works
exactly as designed and has a blind spot its designer inherited from the
incident that prompted it.

**The cost, had it not been caught.** The timeout diff's intent was to
raise 60 to 75. Applied against a file that now says 120, a careful hand
sees no anchor and asks. A hurried hand sets 75 and the PM seat loses 45
minutes of runway, which is a regression shipped by a page whose whole
purpose is to be trustworthy enough to apply without thinking.

**The fix, shipped in this PR.** prompts/exo-agent.md §5 now states the
mechanical form: for each queued diff, grep the live file for every `-`
line verbatim and confirm it appears exactly once, every line, not the
line that broke last time. Item 2's timeout edit is marked cancelled in
the queue with the reason, since 120 already exceeds what it wanted, and
the model flag is corrected.

**What the org grew from it.** A queue of diffs against files the queue
cannot see is a stale cache, and every stale cache needs a validation
rule that does not depend on remembering why it went stale before. The
cheapest such rule is exact-match on every removed line, run every time,
with no judgment about which lines are likely to have moved.

Next free number is 27.

*(Superseded 2026-09-24. Sequential numbers are retired. See incident 29
and the allocation rule at the top of this file.)*

## Incident 29 — Two branches allocated the same incident numbers, for the fourth time (2026-09-24)

Found by this run while merging. It is a repeat, and the standing rule
at the top of this file is why it is written down rather than quietly
fixed.

**What happened.** On 2026-09-21 the ExO seat's run wrote incidents 23,
24, 25 and 26 onto branch `exo/2026-09-21`, which is pull request #65,
still unmerged. On 2026-09-23 the chair wrote incidents 23 and 24 onto
main for entirely different events, the Kimi routing rollout and the
press 404. Both were correct at the moment they were written, because
both read the highest number that existed where they could see. Today's
merge put four entries with two numbers in one file, and git reported it
as a content conflict rather than as the semantic collision it is.

**It had already happened three times.** Before this run the file
contained two entries numbered 19, two numbered 20, and two numbered 22
for unrelated events, which is the same defect landing silently on three
earlier merges. Nobody registered any of them. So the true count is four,
and the three that went unrecorded are themselves a violation of this
file's standing rule.

**Why it happened, technically.** The number is allocated at write time
from a counter that lives in a file, and the file is per-branch. Every
seat writes on its own branch, every seat reads the highest number
visible to it, and the org runs eight to twelve open branches at once.
Under those conditions collision is not a mistake anyone made. It is the
guaranteed output of a sequential allocator with no central issuer, and
it will recur on every run where two seats register an incident between
merges.

**It is not cosmetic, and here is the cost.** Incident numbers are
quoted everywhere. Charters cite them as evidence, pull request titles
carry them, the learning log reasons about them, and three open PRs
today reference numbers that this merge has moved. A citation that
resolves to the wrong event is worse than a dangling one, because it
reads as correct. Incident 23 in a charter written last week and
incident 23 in a commit written yesterday are different events, and
nothing in the text tells a reader which one is meant.

**The fix, shipped in this PR.** Sequential allocation is retired. New
entries get a date-scoped id, `INC-YYYY-MM-DD-slug`, which is collision
free by construction because two seats writing on the same day about the
same event are writing about one incident, which is the correct outcome.
The rule is at the top of this file and it binds every seat through the
ship check. Existing numbers 1 through 28 are permanent and are never
renumbered again, with one exception made today and recorded in full:
the four entries from branch `exo/2026-09-21` moved from 23, 24, 25 and
26 to 25, 26, 27 and 28, because main's 23 and 24 were merged first and
merged numbers win. Each carries a renumbering note naming its old id,
which is the discipline HQ's lessons register already applies to its own
rule ids and which this file lacked.

**What the org grew from it.** The org now keeps two kinds of
identifier, and it had been treating them the same. An id that is only
ever read by the run that wrote it can be sequential. An id that other
artifacts cite has to be allocatable without coordination, because the
seats cannot coordinate by construction: they never message each other
and they each see a different snapshot of the repository. Anywhere else
the org hands out citable numbers from a file, the same defect is
waiting. ADR numbers are the obvious next one, and HQ ADR-033 landing in
this repo while alexandria's own ADRs stop at 32 shows the shape of it
already.
### Incident 24, addendum (2026-09-23, chair, from three manual print attempts)

The chair tried to print the missing issue today under a temporary
override and learned the full shape of the failure. (1) The budget
guard from incident 22 works: it refused two runs that would have
413'd, including catching that gather()'s SQL limits had drifted from
PAYLOAD_CAPS. (2) Groq returns 404 not only for groq/compound but for
meta-llama/llama-4-scout-17b-16e-instruct as well: Groq's production
catalog, read from its docs today, is down to llama-3.1-8b-instant,
llama-3.3-70b-versatile, openai/gpt-oss-120b and openai/gpt-oss-20b,
with qwen/qwen3.8-27b and minimaxai/minimax-m2.7 in preview. The
compound family and the Llama 4 models are gone. (3) The generator
prompt alone is 9,865 tokens; with a floor payload and a 4,000-token
reservation the request needs roughly 24,000 tokens per call, and no
remaining free-tier Groq model is known to allow that. The structural
conclusion for the engineer: the press has outgrown Groq's free tier,
not one model on it. The options are a paid Groq tier, a different
free provider with a real per-request budget, or moving the press's
single writing call onto the Claude subscription that already runs
every seat (an Actions job on the OAuth token, 200K context, no TPM
wall), which keeps the $0 principle and ends the provider roulette.
The chair's temporary edits were restored; nothing was committed.

## Incident 24, continued — the free tier has no model that can print the issue (2026-09-24, engineer)

Appended by the engineer seat under the standing rule at the top of this
file, on the owner's urgent dispatch of 2026-09-24. Incident 24's own
entry, written 2026-09-23, named the 404 and the missing Monday. This is
what reading Groq's live documentation added to it, and it is worse than
the 404.

**Verified from the live web this run.** `https://console.groq.com/docs/models`
no longer lists `groq/compound` or `groq/compound-mini` in any section.
That is the 404, confirmed independently of the manual Modal run. The
free-tier table at `https://console.groq.com/docs/rate-limits` now
contains exactly ten rows, and only three of them are general text
writers:

| model | RPM | RPD | TPM | TPD |
| --- | --- | --- | --- | --- |
| openai/gpt-oss-120b | 30 | 1K | 8K | 200K |
| openai/gpt-oss-20b | 30 | 1K | 8K | 200K |
| qwen/qwen3.8-27b | 30 | 1K | 8K | 200K |

The other seven are two speech models, two text-to-speech models, two
prompt-guard classifiers and one safety classifier. The only free
entries with a TPM above 8,000 are the two prompt guards at 15K, and
they cannot write prose.

**So the ceiling is 8,000 TPM, everywhere on the free tier.** Incident
22 established that a single request larger than TPM is rejected 413
before generation starts, which makes TPM a per-request ceiling.
`prompts/digest.md` is 9,865 tokens on its own. The output reservation
is 6,000. That is 15,865 tokens before one row of payload, against
6,800 usable, and `python3 pipeline/budget.py` now prints exactly that
for all three fallbacks. **The press cannot print the weekly issue on
Groq's free tier at any model, at the current prompt size.** Incident 22
had an escape hatch, which was compound's 70K. There is no hatch now.

**Two things that look like remedies and are not.**

1. *A dedicated key for the press.* Groq's rate-limit page, verbatim:
   "Rate limits apply at the organization level, not individual users."
   A second key on the same account draws from the same 8,000 TPM, so
   the dedicated-key option in the dispatch buys nothing. Only a
   separate organization or the paid Developer plan moves the ceiling,
   and both are owner decisions (docs/sprints/pending.md).
2. *Prompt caching.* Groq's caching page says cached tokens "do not
   count towards your rate limits", which reads like the answer. It is
   not, for two independent reasons. The same paragraph says cached
   tokens "are subtracted from your limits after processing", and the
   413 is an admission decision taken before processing. And cached
   prefixes "expire after 2 hours without use", while the press runs
   once a week, so it would never see a cache hit on its own cadence.
   Recorded here so nobody spends a day on it.

**The repeat, which is the finding.** Three press failures in five days:
413 on 2026-09-19 (incident 22), 429 collisions on the shared key, 404
on 2026-09-23. Each has been treated as its own break-fix, and each fix
has been a new model. That is the pattern: the press's availability is
pinned to one vendor's free tier, and a free tier is not a contract.
The fix this run ships is not another model. It is that the press now
checks the provider before it trusts it, walks an ordered list when the
answer is no, and emails the owner when it cannot print at all. The
press will still fail. It will no longer fail quietly, and that is the
part that cost three days.

**Still only answerable from the Modal dashboard.** Whether the Monday
2026-09-21 15:00 UTC schedule fired at all. The repo can prove the
model was withdrawn, that no `2026-W38` row exists in `digests`, and
that a run which did fire would have raised on the 404; it cannot prove
whether a container ever started, because `modal app logs` shows no
output for that date and the CLI does not expose schedule history. The
one-click check is written into docs/sprints/pending.md for the owner.

## Incident 24, third entry — the fix for a 404 was nearly shipped with a 404 in it (2026-09-24, engineer)

Appended under the standing rule at the top of this file. This one is a
near miss rather than a failure, and it is recorded because the standing
rule is about the repeat, not about the damage, and because a near miss
that goes unwritten is a failure waiting for the next run.

**What happened.** ADR-32 moved the press off Groq and onto Kimi K2,
naming the model as "Kimi K2" and the dispatch naming the id as
`kimi-k2`. Read from Moonshot's live catalog this morning: the bare
`kimi-k2` series was **discontinued on 2026-05-25**, four months ago. A
press pointed at that id answers 404. That is incident 24's exact
failure, in incident 24's own remedy, on a provider chosen partly to
escape it, in its first hour.

The live 256K-context general model is `kimi-k2.6`. The catalog's other
K2 ids are `kimi-k2.7-code` and `kimi-k2.7-code-highspeed`, which are
coding models, and the press writes prose. `kimi-k2` and `kimi-k2.5` are
now in `budget.DECOMMISSIONED` with their dates, so pointing at either
one fails at import time with the reason rather than at 09:00 on a
Monday with a 404.

**Why it did not ship.** Two things caught it, and only one of them was
the seat paying attention. The dispatch said to read the provider's
current docs for the exact model id, which is the instruction that
found it. Underneath that, `check_availability` and `preflight` would
have caught it anyway, because both ask `GET /models` before the run
trusts a name. That is the machinery incident 24 bought, doing exactly
what it was bought for, one week later, on a different provider.

**The finding, which is about how the org writes decisions.** A model
name in prose is not a model id. "Kimi K2" is a family, "Claude 5" is a
family, and a family name written into an ADR reads like a
specification and is not one. The rule this suggests, for any seat
implementing a decision that names a model: **the ADR names the family,
the code names the id, and the id is read from the provider's live
catalog on the day it is written, never from memory.** Three of the
four press failures in the last week (incident 22's 413, the 404 of
2026-09-23, and this near miss) come from the gap between what a model
was believed to be and what the provider currently serves.

**Two failure classes now covered on both providers.** Deprecation is
not a Groq problem. Moonshot has run three deprecation waves of its own
in 2026, and Groq has run at least two. The press's guards were written
against one vendor and are now written against a provider table, which
is the honest shape: any provider will withdraw any model, and the only
defence that keeps working is asking before the run, every run.

## INC-2026-09-24-press-provider-migration — four failures in one evening, one root cause (2026-09-24, owner-reported four times)

Registered by the ExO seat on the owner's dispatch. Numbered by the rule
at the top of this file rather than sequentially, because this branch
cannot see the highest number that exists.

**What happened.** The press moved to Moonshot's Kimi under ADR-32 and
was deployed straight to the real Monday path. It then failed four
times in one evening. Each failure was found by the owner's alarm email,
each was diagnosed and fixed by the chair in minutes, and each fix is a
one-line or two-line commit on main.

| # | Symptom | Cause | Fix | Commit |
| --- | --- | --- | --- | --- |
| 1 | No content returned, `finish_reason` was `length` | `MAX_COMPLETION_TOKENS` was 6000 and kimi-k2.6 spent all of it on hidden reasoning before writing a visible token | reservation raised to 24000, against a 32768 output ceiling and 180K of remaining context | `281d0af` |
| 2 | `httpx.ReadTimeout` at 300s | the default read timeout, while the model was still reasoning | 1500s on the writing call, inside Modal's 1800s function timeout | `b8de845` |
| 3 | `IdleInTransactionSessionTimeout`, issue written and lost | the read transaction from `gather()` stayed open across a multi-minute model call and Neon terminated it | the read connection closes after `gather()`, the model call runs with nothing open, a fresh connection saves and sends | `5736d71` |
| 4 | Alarm subject read `[alexandria] 2026-W39` | subject lines were built from the ISO week id and a bracket tag | proper titles on every subject a human reads, plus a taste entry | `1ccea9c` |

**Why it happened, technically, and the four are one.** Every row above
is an integration property of a new provider, and not a bug in the code
that was written.

- A reasoning model spends output budget on thinking before it writes,
  so a reservation sized for a non-reasoning model returns nothing.
- A model that reasons for minutes needs a client timeout measured in
  minutes, and the default is measured in seconds.
- A call that takes minutes must not be made while a database
  transaction is open, because managed Postgres kills idle transactions.
- A provider swap touches the alarm path, and the alarm path is
  owner-facing prose that taste governs.

None of the four is knowable from the provider's documentation in
advance, and all four are knowable from one real call. **A single
rehearsal print against the real payload, before the deploy, would have
surfaced every one of them.** Failures 1, 2 and 3 happen on the success
path and would have thrown in the rehearsal. Failure 4 is on the alarm
path, and a rehearsal that prints the subject lines it would have sent
shows it to a reader without sending anything.

**The root cause, which is not the model.** The org already had the law.
`docs/agents/runtime-changes.md` says no change to the environment a
seat runs in reaches a scheduled run until a deliberate smoke test has
proved it, and it was written after incidents 17 and 18. The law did not
fire here for two reasons, and both are the org's rather than anyone's.

1. **The law's own definition excluded this change.** Its "what counts"
   list is a list of container and workflow machinery, written the week
   the org containerized. A model id and a provider base URL are neither,
   so a reader applying the law honestly concludes it does not apply. The
   press is a Modal cron and not a seat, and the law says "the
   environment a seat runs in". Fixed in this PR: a provider or model
   change is a runtime change, and the press is a runtime.
2. **Recording is not enforcing, again.** This is the same class as
   incident 20 and the fourth time the org has met it. The chair knew the
   law. Nothing between the law and the deploy ever opened the file,
   because the gate that runs is the chair's deploy command and that
   command asks two questions (does the request fit, does the model
   exist) and not the third (does one real call work end to end). The
   `&&` chain in `pipeline/weekly.py`'s docstring is the org's only
   mechanical gate on the press, and this class of failure walked past it
   because it was never added as a link.

**What the org grew from it.** Three things, all in this PR.

- The runtime law now names provider and model changes, names the press
  as a runtime, and carries a staged ladder for them with three gates:
  the budget guard, the availability check, and a rehearsal print.
- The rehearsal is specified in `docs/agents/press-rehearsal.md` for the
  engineer to build: preflight plus one real model call against the real
  payload, written to a scratch row and sent to nobody.
- The enforcement answer is written down honestly. A charter line telling
  a seat to read a law is not a gate. The gate is the deploy command
  refusing to proceed without a rehearsal receipt, which costs one more
  `&&` and is the only form of this rule that has ever worked.

**What worked, and it is worth the same weight.** The alarm path fired
four times out of four. The owner learned about every one of these
within seconds of it happening, from an email the press sent about
itself, rather than from an empty inbox three days later. That is
incident 24's standing fix doing precisely what it was bought for, on a
provider it was not written against, and it is the reason this entry
describes four fixed failures instead of one missing issue. The
complaint about the fourth alarm's subject line is a complaint about an
email that arrived.

**The thing still unfixed after this PR.** The rehearsal is a proposal,
not code. Until the engineer ships it and the deploy command requires
its receipt, the ladder is a document, and a document is what failed
here.

## 2026-09-22 — A sprint item the assigned seat is not allowed to do (engineer seat, second occurrence)

Titled by date rather than by number because PR #60 is taking incident 23
and racing for an integer across two open PRs is how the numbering breaks.

**Recorded because it is a repeat, per the standing rule at the top of this
file.** The first occurrence was yesterday, 2026-09-21, in this same seat.

### The two occurrences

**First, sprint item 2.** The engineer run of 2026-09-21 (PR #66) built the
blind prose benchmark and could not score it, because the comped friends
list the item depends on does not exist anywhere in the repository. The
sprint's own notes had said items 2 through 4 need "only the corpus, the
sent issue(s), and the comped friends list", which reads as a statement
that all three were in hand. Two were.

**Second, sprint item 5, today.** The item asks the engineer to extend the
skill validation system to a passing result on both gold skills. That
system lives entirely inside `skills/_validation/`, and the engineer
charter forbids this seat from writing into `skills/`. The run's own
dispatch repeated the prohibition word for word. The item is not hard for
this seat, it is closed to it.

### Why they are one failure and not two

Both items were planned as ready, both were assigned to a seat, and in both
cases the thing that made them undoable was knowable at planning time from
a file already in the repository. Item 2's blocker was an absent input,
findable by grepping for the list. Item 5's blocker is a written boundary,
findable by reading the assignee's own charter, which is two directories
away from the sprint file. Neither needed the work to start before the wall
appeared, and in both cases the wall appeared anyway, a day of queue apart,
after a seat had spent a run reaching it.

The cost is not the lost run. Today's run had somewhere useful to go, the
urgent ledger entry it fell back to. The cost is that the sprint's order is
no longer a queue. Two of five items cannot be pulled by the seat they are
assigned to, so a run that follows the sprint faithfully has to discover
that item by item, and the PM does not hear about it until the next
retrospective.

### What would have caught it

A feasibility gate on the sprint, at plan time, not at build time. An item
is plannable when three things hold, and all three are checkable by reading
files the PM already has open:

1. **Surface.** Every path the item must write is permitted to the seat it
   is assigned to. The seat charters' Boundaries sections are the source,
   and `docs/agents/registers.md` already maps which register holds what.
2. **Inputs.** Every artifact the acceptance criteria name exists, or the
   item names who is producing it and when. "The comped friends list" was
   neither.
3. **Ceiling.** The item's remaining work is not itself assigned elsewhere.
   Item 5 fails this twice, since the one case standing between today's
   result and both skills passing is `he-pos-2`, whose fix the sprint
   explicitly rules belongs to the skill seat.

This is the same shape as the recorded-is-not-enforced pattern, one level
earlier. Incident 20 was a ruling that no artifact ever checked against.
This is a plan that never checked against the charters it assigns work to.
Writing the boundary in two places, the charter and the dispatch, did not
help, because nothing between the boundary and the plan opened either file.

### Class, under ADR-29

An **enforcement gap**. The boundary was written, agreed, and repeated in
the dispatch, and the artifact that had to respect it was produced without
checking it. The hunter for enforcement gaps is the ExO's
recorded-is-not-enforced audit, and the detection cycle is every ExO run.
The proposal above would move the detection to plan time instead, which is
one week earlier than the retrospective that would otherwise find it.

**Not this seat's call to fix.** Planning surfaces belong to the PM and the
owner, and the engineer charter forbids editing `docs/sprints/` and the
charters both. Recorded here, and in `docs/ideas.md` with status `urgent`,
so the Monday retrospective and tomorrow's run both see it.

## Incident 25 — Parallel runs of one seat collided on a register's next number (2026-09-20, writer seat)

**Class, per ADR-29.** Enforcement gap, in the narrow sense that nothing
between an append and the next append ever reads the file's own tail.

**Recorded because the standing rule says so.** This has now happened
twice in two registers, which is the trigger at the top of this file, no
judgment call available.

### What happened

docs/voice/ban-list.md carried two entries numbered 26 and two numbered
27, with 30 and 31 unused, until this run renumbered the later pair into
the empty gap. Entry text was not touched.

The cause is the merge described in section 12 of
docs/voice/reviews/2026-09-19.md: two writer runs on 2026-09-19 worked
the same file from the same starting point, each appended entries
numbered from its own copy of the list, and the merge pass that followed
reconciled the four prose seams between them without noticing that the
numerals had collided. The seams were about meaning, so meaning is what
got read.

The same defect is in this file. There are two entries numbered
**Incident 22**, at the 2026-09-19 editorial-rebuild entry and at the PM
presence entry. They are left as they are: this register is not the
writer seat's to renumber, and the entry that cites one of them should
not be silently repointed by whoever notices. It is flagged here for the
ExO's weekly read.

### Why it matters more than a cosmetic defect

Both registers are cited by number, and the citations are the
enforcement mechanism. prompts/digest.md's gates, the canon, and the
review files all say things like "ban list 26" and "canon law 12". A
duplicated number makes a citation ambiguous, and an ambiguous citation
in a gate is a gate that cannot be checked. One such citation already
existed and was corrected in this PR.

### The fix, and it is small

The append is the moment to check, because it is the only moment anyone
holds the whole file. A seat appending a numbered entry reads the last
number in the file it is appending to, in the branch it is appending
from, and never numbers from memory or from the copy it read at the
start of its run. Where a run has been open long enough for another run
to land, that means rereading the tail before writing it.

This is the cheap half of incident 6's lesson. Incident 6 was two
appends at one anchor colliding in git. This is two appends colliding in
the content, which git merges cleanly and therefore never reports.

## Incident 26 — A gate written as a list catches only what already shipped (2026-09-20, writer seat)

Recorded under the standing rule at the top of this file. The class has
now produced four artifacts and four separate ban list entries, which is
three repeats past the threshold at which it should have been written
down.

**The number.** The ExO's incident 24 closed with "Next free number is
25", so this entry takes 25. Note for whoever renumbers: **23 is claimed
three times** as of today, by three seats on three unmerged branches, for
three unrelated events (the writer's ban list collision, the engineer's
arXiv 406, the ExO's open-routed run). That is incident 25's own defect,
parallel runs colliding on a register's next number, repeating inside the
incident register itself on the day it was first recorded about the ban
list. It is left here as a note rather than fixed, because this register
is not the writer seat's to renumber.

### What happened

Four times, the same failure reached a reader or a sample, and four times
it was fixed by adding the string that had just been seen to a list of
forbidden strings.

1. A section heading printed a category word, "Compounding" (ban list 19).
2. A section heading printed the generator's own internal slot label,
   "Gaining traction". The owner flagged this one for the second time, in
   the word "AGAIN", and it became incident 20 (ban list 20).
3. The same category word moved down one level and printed in bold over a
   group inside a section, "**Replaced**" (ban list 30).
4. The same category word moved again and printed in italics over a
   numbered list, "*Procedure*" (ban list 33). Five rounds of grading had
   read past it, because every gate written in rounds one through four
   read `#` lines and bold runs, and none of them read italics.

### Why it kept happening

Each fix was written from the artifact in front of the writer, so each
one described a position and a typeface rather than the thing being done
wrong. The rule the org actually holds is a question that can be put to
any line: could this sit over a different day's items without changing a
word? Nothing in the pipeline or the prompt ever asked it. Both asked a
narrower question, does this line match one of these strings, and that
question has a different answer every time the category word moves, which
it did four times.

This is a second axis on incident 20. Incident 20 says that recording a
rule is not enforcing it. This one says that enforcing it is not enough
either, because a gate can be written, wired, and running, and still be
shaped so that it can only recognise the last failure. A check written
from the previous incident is a memorial.

The general form, for the ExO's pattern reading: **when a fix enumerates,
ask what it is an instance of.** If the enumeration can be replaced by a
question the machine or the model can put to any candidate, the question
is the fix and the enumeration is evidence.

### The fix, in this pull request

- `prompts/digest.md`: the pre-output heading gate no longer decides by
  list. It collects every line that announces a block rather than saying
  something, at any level and in any typeface, and puts the class
  question to each one. The known labels stay in the file, demoted to
  examples, with the reason they are not the test written beside them.
- `docs/voice/ban-list.md` gains entry 36, the gate that lists instead of
  testing, so the register carries the class and not only its four
  instances.
- `docs/ideas.md`: the machine half is proposed to the engineer, on top
  of PR #60, as a comparison against the previous issues' headings rather
  than against a word list. That is the deterministic shadow of the class
  question, and it needs no judgment to run.

### What is still open

The prompt fix cannot be observed. No issue has been generated since
2026-09-14, so every patch made to the generator across seven editorial
runs is untested against a real payload. The first issue that proves or
disproves this one is Monday's pilot.

## Incident 27 — The same gate defect, one day later, in the next rule down (2026-09-21, writer seat)

Recorded under the standing rule at the top of this file. Incident 26 was
written yesterday by this seat and describes a class: a gate written as a
list of what already shipped. Today the same class was found in a second
gate in the same file, so it is a repeat and not a second instance of one
event.

**The number.** Incident 26 is the last numbered entry on this branch, so
this takes 26. Incident 26's own note still stands: 23 is claimed three
times by three seats on three unmerged branches, and that is not this
seat's to renumber.

### What happened

`prompts/digest.md` carries a bullet headed "Plain ASCII punctuation,
always." The heading is the class, correctly stated. Everything under it
names instances: the non-breaking hyphen, the narrow no-break space, the
multiplication sign. The pre-output check at the end of the file then
enforced it in the narrower of the two forms, "no non-ASCII hyphens or
spaces".

2026-W37 carries eight distinct non-ASCII characters, 134 in total.

| Character | Count | Named in the rule | Caught by the check |
|---|---|---|---|
| U+2011 non-breaking hyphen | 87 | yes | yes |
| U+202F narrow no-break space | 19 | yes | yes |
| U+2013 en dash | 12 | no | yes, as a hyphen |
| U+2014 em dash | 5 | elsewhere | yes |
| U+2019 curly apostrophe | 5 | yes, as "straight quotes" | no |
| U+00D7 multiplication sign | 3 | yes | no |
| U+2022 bullet separator | 2 | no | no |
| U+03A8 Greek capital psi | 1 | no | no |

Four of the eight walk through the check that is supposed to stop them,
and two of those four are named in the rule three hundred lines above it.
The gate is narrower than the rule it enforces.

### Why this is incident 26 and not a new finding

Incident 26's general form was written down as a question for the ExO's
pattern reading: **when a fix enumerates, ask what it is an instance of.**
Yesterday's run asked that question of the heading gate, rewrote it to
test the class, and shipped. It did not ask it of any other gate in the
file, and there were two. The lesson was applied to the artifact that
produced it and nowhere else, which is the same shape as incident 20,
where a ruling was recorded in the right register and not checked against
the next thing that shipped.

So the repeat is not "a list was written". It is that a class-level lesson
was learned on Sunday and applied to exactly one instance of its own class.

### The fix, in this pull request

- `prompts/digest.md`: the ASCII rule now says its three characters are
  examples and never the test, and the pre-output check asks whether every
  character in the issue is plain ASCII. One exception, a person's or an
  institution's name as the payload spells it, and none for punctuation,
  spacing, separators or symbols.
- `docs/voice/ban-list.md`: entry 13 amended to state the class, with the
  five characters it would have missed named as evidence.

### What this run did not do, deliberately

It did not sweep every other rule in `prompts/digest.md` for the same
defect. Two gates have now been rewritten one at a time, and the honest
reading of this entry is that one-at-a-time is the failure. That sweep is
a whole run's work and it is the first thing the next writer run should
do, with this entry as its brief.

A deterministic version belongs in the engineer's lane rather than in a
prompt at all, because "is every character in this string below U+0080"
needs no judgment, and `tools/check_digest_quality.py` (PR #60) is where
it goes. That is not filed as a separate ledger entry, because the quality
gate's own standard already claims the rule and this is a widening of it
rather than a new idea.

## Incident 28 — A ruling recorded, and three days later nothing had acted on it (2026-09-22, writer seat)

Recorded under the standing rule at the top of this file. Incident 20 is the
class: a taste ruling written into the right register, by the right seat,
within the hour, and violated by the very next artifact because nothing
between the ruling and the artifact ever opened the file. This is the third
occurrence of that class and the first where the artifact is the live site
rather than an issue.

**The number.** Incident 27 is the last numbered entry on this branch, so
this takes 27. Incident 26's note still stands: 23 is claimed three times by
three seats on three unmerged branches, and renumbering those is not this
seat's call.

### What happened

On 2026-09-19 the owner gave two rulings about the site, both recorded in
`docs/voice/taste.md` the same day.

1. "The pilot issue: the current archived issue (2026-W37) is to be removed
   from the site and Monday's issue becomes the pilot, the first the public
   reads."
2. The library page's prose was rejected, quoting its own line back:
   "Every issue, in full..."

On 2026-09-22, three days later:

- `site/content/issues/2026-W37.md` is present on main and on sixteen of the
  seventeen other remote branches, the exception being `pm/sprint-2026-09-14`,
  which predates the file. That includes `fe/2026-09-20-library-reveal-and-w37`,
  whose
  pull request title says W37 is retired behind config. There is no such
  config. No flag in `site/lib` or `site/app` hides an issue, and
  `listIssues()` returns every file in the directory.
- `site/app/library/page.jsx:19` still reads `<h1 className="page-title">Every
  issue, in full.</h1>`.

### Why the two failures are not the same failure

The second is blocked and the first is not, and that distinction is the
finding.

Rounds two to eight of her site copy were all rejected
(`docs/voice/preferences/site-copy-2026-09-20.md`), so no approved line
exists to replace the library H1 with. A seat that changed it today would be
setting copy she has not seen, which the same register forbids. Blocked is
the correct state for that one.

The removal is blocked by nothing. It is one `git rm` and a merge, it needs
no copy, no design and no owner round trip, and it did not happen.

Both look identical from outside: a ruling in the register, an artifact that
disobeys it, three days elapsed. Nothing in the org distinguishes a ruling
waiting on her from a ruling waiting on nobody, so the second hides inside
the first.

### Why the existing gates did not catch it

Incident 20's fix was the taste gate in every seat's charter, and it fires
when a seat ships. It caught this one, in the sense that the writer run of
2026-09-22 found both failures by running that gate. Three days late, and
only because a writer run happened to be dispatched.

The writer seat's own ledger entry of 2026-09-21, "A ruling can land with
nothing scheduled to read it", proposed the deterministic half: compare the
commit date of `taste.md` against the newest file in `docs/voice/reviews/`
and say so when the ruling is newer. That entry is still `Status: proposed`.
This incident is its second piece of evidence, and the first where the
unread ruling was about something already live rather than about a generator
that has not run.

### The fix, in this pull request

The writer seat owns neither `site/content/` nor `site/app/`, so this entry
and the ledger entry beside it are the fix this seat can ship. Named for the
two seats that can act:

- Frontend: `git rm site/content/issues/2026-W37.md`. Her ruling, unblocked,
  three days old.
- Whoever runs the ledger check: the 2026-09-21 proposal now has two
  instances behind it.

### The general form, for the ExO's pattern reading

Incident 26 asked, when a fix enumerates, what is it an instance of. This
one asks a different question of a register: **for every open ruling, who is
it waiting on?** A register that records rulings but not their blocker
cannot tell a seat which ones it could close today, so all of them look
equally stuck and none of them move.

## 2026-09-23 — The same typographic defect, recorded three times, misdiagnosed each time (writer seat)

Recorded under the standing rule at the top of this file. This is the third
recording of one defect and the first that names its cause, so what repeated
is not only the defect but the wrong diagnosis of it.

**The number.** Deliberately none. Incident 25 is claimed by three seats on
three unmerged branches, 24 by two, and both 25 to 27 exist only on this
seat's chain. The engineer set the precedent on 2026-09-21 of titling by
date rather than racing an integer, used again in PR #72 today, and this
entry follows it. Renumbering the contended entries is the ExO's call, not
this seat's.

### What happened

Three recordings, six days, one defect.

1. **2026-09-19.** Ban list entry 13 created from issue 2026-W37, which
   carried 87 non-breaking hyphens and 19 narrow no-break spaces. Written as
   a prohibition on three named characters.
2. **2026-09-21, incident 27.** The entry amended, because the same issue
   also carried en dashes, curly apostrophes, multiplication signs, bullet
   separators and a Greek capital that a rule naming three characters let
   through. The lesson drawn was that the rule enumerated instead of asking,
   which is ban list entry 36. Correct, and not the cause.
3. **2026-09-23, this run.** The first run of this seat to hold database
   credentials read the payload the generator is handed. It carries 286
   non-ASCII characters across 42 of its 48 claim strings, 188 of them the
   non-breaking hyphen, inside ordinary words like "on-policy" and
   "inference-time".

The model did not type those characters. It copied them. The claim text is
machine-extracted from PDFs, where typesetter hyphens are normal, and it
reaches the writer unwashed.

### Why two rounds of patching missed it

Every rule in `prompts/digest.md`, and there are about forty, is a gate on
the model's output. The file describes the payload in eight lines, as a list
of field names, and says nothing about its condition. The single place it
acknowledges that the input is dirty is the `dates` field, which it tells the
writer to normalize from an en dash. That instance was never generalized,
so the file contains the correct instruction for one string out of hundreds.

The instrument is the reason this took six days. Nine editorial runs graded
the finished text and reasoned backwards to a rule. Reading the output tells
you a defect exists. It cannot tell you whether the writer produced it or
inherited it, and those two have opposite fixes: the first wants a sharper
prohibition, which is what was written twice, and the second wants a cleaning
step at the point the material comes in, which was written nowhere.

### The class, which is larger than the characters

Four defects in today's payload were diagnosed by earlier runs as the model's
prose habits.

| In the payload | Recorded as |
|---|---|
| 286 non-ASCII characters, 42 of 48 claim strings | ban list 13, twice |
| 22 "new claims" that are 5 papers | ban list 16, 21, 29 |
| 2 of 3 reading-list papers already covered elsewhere | ban list 15 |
| A triage note opening "Provides a comprehensive framework" | ban list 39 |

### The fix, in this pull request

Six patches to `prompts/digest.md`, each stating what the payload actually
contains and what to do about it at the point of lifting, plus ban list entry
41 for the class and 42 for the citation floor, and an amendment to 16.

### What is still open

The deeper fix is not this seat's. The characters could be normalized once in
`gather()` rather than by asking a language model to remember, and the
claims-versus-papers mismatch is a query shape, not a prose problem. Both are
filed in `docs/ideas.md` for the engineer. Charter step 4 applies: if the
payload's shape defeats a prompt patch a second time, it stops being a prompt
problem.

### The general form, for the ExO's pattern reading

Incident 26 asked what a fix that enumerates is an instance of. Incident 28
asked, for every open ruling, who is it waiting on. This one asks: **when a
seat grades an artifact, has anyone looked at what the artifact was made
from?** Nine runs improved the instructions to a writer nobody had watched
work, from material nobody had read. A seat that only ever sees output will
keep writing sharper prohibitions against defects its subject never chose.

## Incident 29 — Nine enforcement runs over one file, while a second file with the same job went unread (2026-09-24, writer seat)

**Class, per ADR-29.** Enforcement gap. Incident 20's class, at a new
scope: the gate ran, the gate worked, and the gate was pointed at one of
the two artifacts it was supposed to bind.

**Recorded because the standing rule says so.** This is the fourth
appearance of "recording is not enforcing" (20, 26, 27, 28) and the
first where the enforcement genuinely happened and still missed.

### What happened

The owner's rulings of 2026-09-19 were recorded in docs/voice/taste.md
and enforced into prompts/digest.md by nine consecutive writer runs.
`prompts/daily.md`, a second complete generator created in engineer
PR #35 at 02:55 the same morning, received none of them. On 2026-09-24
it still carries the "[{dates}]" title suffix she struck by name, in
three places, one of them an explicit instruction to print it. Seven
taste rulings and seven canon laws fail against it. The full grade is
docs/voice/reviews/2026-09-24.md.

Neither seat erred at the moment it wrote. digest.md's sentence claiming
both cadences (commit d134996) landed 48 minutes after PR #35's last
commit. Both were honest answers to "how does the daily get written?",
written 48 minutes apart, and nothing in the next five days put them in
one room.

### Why the existing gates could not catch it

The writer charter's pre-ship check names the registers an output is
bound by. It does not name the artifacts a register binds. So the check
ran nine times, correctly, against the file this seat owns, and the
question "is there another file doing this job?" was never a question
anyone was asked. The charter's own custody sentence is what should have
raised it: "No other seat, and not the chair, writes newsletter
structure or prose rules anywhere else." A custody claim with nothing
that enumerates the territory is a claim nobody can check.

### The fix

Ban list 44 makes the generator itself a graded artifact, every
generator and not the one this seat happens to own. The structural fix,
filed for the engineer in docs/ideas.md rather than patched here, is to
stop having two files that can drift: one craft layer, one small cadence
file each, concatenated at call time.

### The general form, for the ExO's pattern reading

Incident 28 asked, for every open ruling, who is it waiting on. This one
asks the question one level out: **for every rule, what is the complete
list of artifacts it binds, and does anything enumerate that list?** A
seat that owns a rule will check the artifact it can see. Custody
language does not produce an inventory, and an enforcement gate with no
inventory is a gate on one door of a building nobody counted the doors
of.

## Incident 30 — The register's next number collided again, this time across seats (2026-09-24, writer seat)

**Class, per ADR-29.** Enforcement gap. Incident 25 exactly, one scope
out, and incident 6's same-anchor ledger collision in a different file.

**Recorded because the standing rule says so.** Incident 25 recorded
this failure inside one seat on 2026-09-20. It has now happened between
seats, which is the repeat.

### What happened

Main shipped incidents 23 (Kimi routing) and 24 (the press's 404) on
2026-09-23. The writer chain, open since 2026-09-20, already held four
entries numbered 23, 25, 26 and 27. Merging main into writer/2026-09-24
conflicted on one 386-line block, and two different incidents were
numbered 23.

Resolved in this pull request by keeping main's numbers, because main is
canonical and the fleet was already dispatched against "incidents 23 and
24" by name. The four writer entries moved to 25 through 28, and every
cross-reference in the ban list, the ledger and five review files moved
with them. No entry text changed.

### Why incident 25's fix did not hold

Incident 25's lesson was that nothing between one append and the next
reads the file's own tail. The fix that followed was for a seat to read
its own tail. That is sufficient against a second run of the same seat
and useless against another seat's open branch, because the tail on main
is not the tail that will exist when the branch merges. A sequential
number assigned on a branch is a guess about what main will look like at
merge time, and every seat appending to this file is making that guess
independently.

### The fix, filed not patched

The durable fix is to stop assigning sequential numbers on branches.
Date-scoped ids ("2026-09-24a") collide only when one seat files twice
in a day, which it can see. That is a register convention rather than
prose, so it belongs to the ExO, and this entry is the brief.

Until then, the rule that would have caught it costs one command. Before
appending here, `git log origin/main -1 -- docs/agents/incidents.md` and
read main's tail, not the branch's.

*Renumbering note (2026-09-24, frontend run). These two entries were written
on branch `fe/2026-09-23-visual-sweep` as incidents 23 and 24, before main
carried incidents 23 and 24 for the Kimi routing rollout and the press 404.
They are re-identified here under the date-scoped scheme the ExO run shipped
the same day, rather than allocated new numbers, because that scheme is the
fix for exactly this collision.*

## INC-2026-09-20-content-invisible-at-rest — Content invisible at rest, a second time (2026-09-20, frontend run)

**The repeat.** Ban list entry 23 was appended on 2026-09-18 after the
whole issue archive was found staged at opacity 0 waiting for a scroll
script. On 2026-09-20 the same failure was found again, on the desk
page: at 390px the first list rendered seven rows at computed opacity 0
under a header reading "AWAITING YOUR MERGE 7", on a page with nothing
else to scroll. Same symptom, same surface family, different mechanism.
Recorded here under the standing rule, at the moment it repeated.

**Why the existing guard did not catch it.** Entry 23 names the
mechanism, a scroll script, rather than the symptom. The second
occurrence had no script. It was `.hero-follow`'s CSS rise animation,
`animation-timeline: view()` with `animation-range: entry 65% entry
98%`, inherited by the desk because the desk reuses that class for its
layout. A view-timeline range never opens for a block taller than the
viewport that begins near the fold, so the animation holds at its first
keyframe forever. Every property of entry 23 that a reviewer would
check was absent: no script, no observer, no JavaScript dependency, and
the rule reads as ordinary progressive enhancement. The check was
looking for the cause it had seen before instead of the effect it cares
about.

**It also hid at two viewports out of three.** Computed opacity was 0 at
390 and 1 at 820 and 1440. A review that looks at desktop, or at desktop
and tablet, sees nothing wrong.

**The fix, and the general one.** The desk now switches the inherited
animation off (`.desk > * { animation: none }`), which is also what
motion.md asks for on a high-frequency surface. The general fix is ban
list entry 24, appended in the same pull request: the test is no longer
"is a script involved" but "read the computed opacity at rest, at every
viewport you ship". That is a two-line probe and it is now the way this
seat checks, not a thing to remember.

**The wider lesson, for any register.** An entry written as a cause
only catches that cause. Incident 20 was a ruling that was recorded and
never checked; this is its sibling, a rule that was recorded, checked,
and worded too narrowly to fire. When a tell is appended to a register,
the entry should name what is observably wrong, and the mechanism
should be an example rather than the definition.

## INC-2026-09-23-phantom-production-bug — A phantom production bug, twice in one run (2026-09-23, frontend run)

**What happened.** The frontend run screenshotted `/desk` at 390x844 and
got a white page carrying one line of text: "Application error: a
client-side exception has occurred". It reproduced on retry, then stopped
reproducing, then came back. Roughly a dozen turns went into chasing it:
rendering the page in isolation (fine), reading the console (nothing but
two aborted third-party requests), dumping `innerText`, and finally
diffing the CSS hash the server was serving against the one on disk.

**The cause was the run's own hands.** `next build` had been run while a
`next start` server from the previous build was still listening on 3000.
The HTML the running server emitted referenced chunk and stylesheet
hashes that the rebuild had replaced, so the browser fetched assets that
no longer existed and React failed to hydrate. The page was never broken.
Nothing in the repository was ever broken.

**Why it repeated inside one run.** The first occurrence was mistaken for
flakiness and worked around with a retry loop in the screenshot harness,
which made the symptom intermittent instead of removing it. It came back
an hour later, after the next rebuild, and the retry loop then hid the
cause a second time. The proximate reason the old server survived every
restart is that `pkill -f next-server` matches the agent's own shell
command string and kills the shell instead, and `kill` by port silently
did nothing when the port lookup returned empty.

**Why this matters beyond one run.** The failure presents as a
production-grade bug on the owner's own daily surface. A seat that
believed it would have filed it, or worse, "fixed" it. The whole point of
a visual charter is that the pixels are the evidence, and this is the
case where the pixels lie: they are a true photograph of a false server.

**The fix, and the general one.** Never rebuild under a running server.
The sequence is kill, verify the port is actually free, build, start, and
then verify the served stylesheet hash matches the one on disk before
screenshotting anything. That last check is one line and it is the only
one that actually proves it:

```bash
curl -s localhost:3000/ | grep -o '/_next/static/css/[^"]*' | head -1
ls .next/static/css/
```

The general lesson is the same one incident 23 ends on, arriving from the
other direction. There, a register entry named a cause and missed the
same effect from a different cause. Here, a symptom was treated as noise
and worked around instead of explained. A retry loop that makes a failure
intermittent has not fixed anything; it has deleted the evidence. When a
run starts working around something it cannot explain, that is the moment
to stop and explain it.

## INC-2026-09-24-stale-server-kill-noop — The fix for the phantom server was itself a silent no-op (2026-09-24, frontend run)

**The repeat.** `INC-2026-09-23-phantom-production-bug` (this file, one entry
up) recorded a run that spent a dozen turns chasing a production-grade bug
that was a stale `next start` serving asset hashes a rebuild had replaced. Its
prescribed fix was: never rebuild under a running server, kill it first, and
verify the port is actually free. That entry also named the trap in the kill
itself, that `pkill -f next-server` matches the agent's own shell command
string, and that `kill` by port "silently did nothing when the port lookup
returned empty".

Both halves of that fired again today, in the first ten minutes of this run.
`pgrep -f "next start"` matched this run's own shell and killed it. The
replacement, a kill driven by `ss -lptn | grep :3000`, reported the port free
and killed nothing, because `ss` returns no rows at all in this container. The
build that followed produced new asset hashes while the old server, which had
never stopped, kept serving the old ones. It surfaced as `EADDRINUSE` in the
server log rather than as a phantom page, so it cost minutes instead of turns,
but it is the same failure with the same cause.

**Why the recorded fix did not hold.** It named a tool rather than a
property. "Verify the port is free" is only a verification if the thing doing
the verifying can see ports, and in this container it cannot: `ss` produces
empty output and no error, so every check built on it passes. A check that
cannot fail is not a check. The general shape is the one
`INC-2026-09-20-content-invisible-at-rest` already ends on from the other
direction: an entry written as a mechanism only catches that mechanism.

**The fix.** Identify the server by what it is rather than by a port or a
command line, from `ps`, with a field match that cannot match the agent's own
argv:

```bash
for pid in $(ps -eo pid=,args= | awk '$2=="next-server"{print $1}'); do kill "$pid"; done
```

`$2=="next-server"` is exact, so this run's own `/bin/bash -c ...` can never
match it. Then verify by absence of the process rather than absence of a
listener, and keep the served-versus-disk stylesheet hash comparison from the
previous entry as the check that actually proves the server is the build:

```bash
curl -s localhost:3000/ | grep -o '/_next/static/css/[^"]*' | head -1
ls .next/static/css/
```

Every rebuild in this run ran that comparison and printed HASH MATCH before
anything was screenshotted.

**What the org grows from it.** When a register entry prescribes a check,
the entry should say how the check fails, not only how to run it. A command
that returns empty on success and empty on error is the worst case, and it is
common: `ss` without privileges, `grep` with no matches, and a `kill` with no
arguments all succeed at doing nothing. The three tool traps this class has
now produced, in order, are worth carrying as one rule: never match a process
by a string that your own command line contains, never infer a process from a
port unless you have seen the port lookup return something, and never trust a
server to be the build you just made without comparing an asset hash.

## Incident 25 — Merged prompt fixes do not reach production (2026-09-21, research seat)

Filed under the standing rule: two instances in one run, the same
failure both times.

**Instance one.** On 2026-09-19, commit a94a003 sharpened
`prompts/interpret.md` on contradictions, anaphora and loose `refines`.
It was a meta-review proposal from this seat, reviewed and merged. Three
days later every edge in the claim graph still carries method sha
`fbe080261d6b`, including the nine written on 2026-09-21, while
`prompts/interpret.md` at HEAD hashes to `6706ec7bffee`. The interpret
worker has never once run the fixed prompt.

The cost is not hypothetical. All five `contradicts` edges in the graph
are miscategorised, three of them shipped in 2026-W37's "Left behind"
section, and one produced a sentence that is simply false — *"The same
reference implementation that achieved 82.2% was later shown to drop to
12.5% on memory-intensive tasks"*, which welds two different systems on
two different benchmarks together. The merged prompt forbids all five by
name and carries that exact pair as its worked example.

**Instance two.** The same commit range added `cs.CR` to `sources.yaml`,
naming 2609.15906, 2609.17648 and 2609.14079 as the papers it existed to
reach. All three are absent from the corpus. `sources.yaml` reached the
ingest image roughly a day later, by which time arXiv's 100-most-recent
window for a category running 34 papers a day had moved past them. The
category works now; those three are gone for good.

**Why, mechanically.** Every prompt and `sources.yaml` is baked into its
Modal image with `add_local_file` (ingest.py:23, distill.py:53,
interpret.py:27, triage.py:59, weekly.py:75). A scheduled function goes
on running the image built at the last `modal deploy`. Merging to main
therefore changes nothing in production, and nothing in the repository
deploys, checks, or reports the difference. This covers every file
ADR-12 authorises the research seat to propose diffs to, which makes the
whole meta-review loop write-only until someone deploys by hand.

**The part that makes it incident 20 again, one level down.** The
`prompt_sha` column exists precisely so a stale prompt is visible, and
it recorded the discrepancy correctly every single day for three days.
The archive-side gate worked. There is no artifact-side gate: nothing
between the merge and the running image ever compares the two. This is
the same shape as the taste ruling recorded and then violated by the
next artifact, and it is why this run proposed no second fix to
`interpret.md` — a third sha that also never deploys would look like
progress and change nothing.

**Suggested fix, engineer's lane, not filed as a proposal here.** A CI
check comparing `sha256(prompts/*.md)[:12]` against the newest
`claim_links.method`, `triage_log.prompt_sha` and `digests.prompt_sha`
would have failed on 2026-09-19 and every day since. Deployment itself
should follow a merge to those paths rather than wait to be remembered.

## Incident 26 — The deploy freeze is not about prompts, and it has cost the top research priority its whole corpus (2026-09-24, research seat)

Filed under the standing rule. Incident 25 recorded that a merged
`prompts/interpret.md` fix never reached production. Three days later it
still has not, and the same failure has now been found in a second file
class, which makes it a repeat and widens what the register knows.

**The repeat.** Every edge in `claim_links`, up to and including the
nine written on 2026-09-23, still carries method sha `fbe080261d6b`.
That is `prompts/interpret.md` as it stood on 2026-09-07. HEAD hashes to
`6706ec7bffee` and has since 2026-09-19. Five days, no deploy. All five
`contradicts` edges in the graph remain miscategorised and two of them
were written *after* the corrected prompt merged, by the prompt it was
written to replace.

**The widening.** Incident 25 framed this as a prompt problem. It is not.
`pipeline/triage.py` gained interleaved per-tier draining on 2026-09-19
(commits 74e0c99 and 73da628), written to end a tier starvation that a
previous research brief had found by hand in the database — the code
comment at triage.py:15 says so. Production has judged tier `b` and
nothing else on 09-20, 09-21, 09-22 and 09-23. Merged application code is
frozen exactly as merged prompts are, because both ride the same Modal
image, and nothing in the repository deploys, checks, or reports the gap.

`prompts/triage.md` at HEAD matches the sha production recorded, which
dates the last deploy to roughly 2026-09-12. Everything merged in the
twelve days since is sitting in main, unread by anything that runs.

**What it cost, stated as a number.** 7,991 papers are ingested and 151
produced all 693 claims, every one of them through `hf-daily`. Tier `a`
(the seven arXiv categories) has 2,329 papers waiting and has never had
one paper judged; tier `a-low`, which is where cs.CR lives, has 936 and
zero triage rows of any kind. The consequence lands directly on the
owner's own order: agent containment was made the top research priority
on 2026-09-19, and the corpus holds **zero** claims mentioning a
sandbox, an escape, isolation, least privilege or prompt injection. The
fix for that was merged on the same day the priority was set. It has
never run.

**Why it is incident 20's shape again, one level further down.**
Incident 25 already identified the missing artifact-side gate. This
entry adds that the finding, the fix, and the merge can all be correct
and the system still changes nothing, because the last gate — something
that puts merged code in front of the running process — belongs to no
seat. The research seat proposes, the engineer merges, and no charter
owns the deploy.

**Correction to incident 25, instance two.** That entry attributed the
three missing cs.CR papers to arXiv's 100-most-recent window moving past
them before `sources.yaml` reached the ingest image. The ingestion half
is right; none of the three is in `papers`. The remedy stated there — "the
category works now" — is wrong. No `a-low` paper has ever been triaged,
so a cs.CR paper that did arrive would sit in the queue indefinitely.
Fixing ingest reach would not have produced a single cs.CR claim.

**Not filed as a proposal here; engineer's lane.** Incident 25's
suggested CI sha check stands and should extend to `pipeline/*.py`, not
only `prompts/*.md`. The research seat's own charter is amended in this
PR instead, to stop this seat spending its one weekly proposal on files
that cannot take effect (`prompts/research-agent.md`, Step 4).

## Incident (number to be assigned on merge) — The security backlog is queued behind one permission, and five findings repeated because of it (2026-09-24, security agent)

**On the number.** Four other open pull requests append to this file right
now (#70, #71, #74, #77), and #71's title already claims "incident 26". This
entry deliberately does not take a number, because the 2026-09-18 audit's own
finding about this register was three entries numbered 11, two numbered 12 and
two numbered 13, created by exactly this race. The ExO seat assigns the number
when it merges. Appended at the tail so the conflict is one line rather than a
hunk.

**The repeat.** The standing rule at the top of this file says any issue that
occurs more than once is recorded at the moment it repeats. Five findings from
the 2026-09-18 and 2026-09-19 audits were re-verified against main today and
are unchanged:

1. No rate limit on the MCP passphrase, which is the single credential guarding
   the corpus database and a GitHub token.
2. No charter carries a rule about untrusted content. Still zero of twelve.
3. Actions and the agent image pinned by mutable tag rather than digest.
4. `digests/2026-W37.md` still in public history.
5. Incident 22's budget check still sitting in `.github/workflows-pending/`,
   after which incident 24 recorded the next press failure.

Individually each has a reason. Together they are incident 20's shape for the
fourth time: something gets written into the right register, by the right seat,
and nothing between the record and the next artifact ever opens the file.

**What is new, and it is the useful part.** Sort those five by what actually
blocks them and they collapse onto one cause. Items 3 and 5 are workflow edits.
The transcript exposure found today needs a workflow edit. Pinning the MCP
public host needs a new secret. **No agent token can write to
`.github/workflows/` or set a secret, which is incident 12.** So the org's
security backlog is not queued behind engineering capacity or behind the
owner's judgment. It is queued behind one permission, and every audit adds to
the queue while no run can drain it. The 2026-09-18 audit noted the block once
per finding, as a footnote on each. Four audits in, the footnote is the
pattern.

The consequence to watch is that the queue is silent. An item blocked on the
owner's push looks identical in the ledger to an item nobody has started, so
the backlog grows without anything reporting that it is growing.

**Proposed, and it is the ExO's call rather than this seat's:** the ledger
should carry a status that means "complete, blocked on an owner push", distinct
from `proposed` and from `urgent`, so that the count of them is visible
somewhere without a person reading every entry. Failing that, each audit should
open with it, which this one now does.

**This seat contributed to the pattern too, and the detail is worth keeping.**
PR #31, the 2026-09-18 run's own pull request, has been open six days. Its
headline fix was escaping the OAuth parameters reflected into the MCP login
form. That hole is closed on main today, and it was not closed by that PR: the
flow moved into `mcp/oauth_flow.py` and the engineer's rewrite carried the
escaping with it. So the fix arrived, the report did not, and the PR now
patches a function that no longer exists. A seat's report is not what fixes
anything, and a run that measures itself by the report it filed will believe it
shipped work that was in fact done by somebody else or not at all.

## Incident 30 — The newest claims are invisible to the graph, for the second time (2026-09-22, skill agent)

**Renumbered from 23 to 30 on 2026-09-24 by the skill seat.** This entry
was written on the 2026-09-22 skill branch as incident 23. The Kimi
routing rollout took 23 and the press 404 took 24 on main first, both
dated 2026-09-23, so merging that branch into this run's conflicted
here. Numbers 23 through 29 are all claimed by at least one open branch
today (writer's #74 uses 23 and 25 through 27, the ExO's #77 uses 25
through 29), so 30 is the first number no open branch has taken, and it
is still only correct if this PR merges before those two. Nothing in
the entry below changed except the number. The collision class itself is
already recorded by the ExO seat as incident 29 in PR #77, "two branches
allocated the same incident numbers, for the fourth time," so this seat
records the instance here rather than minting a duplicate entry for it.

**Recorded under the standing rule**, which says an issue that occurs
more than once anywhere in the org is registered at the moment it
repeats, with no judgment call. The effect here is the one recorded on
2026-09-19; the mechanism is a different one, and the first mechanism
was fixed in between.

### The first occurrence

Ledger, 2026-09-19, "29% of claims have no embedding and are invisible
to search": 158 of 543 claims had a null embedding, every one written in
the previous three days. The consequence recorded then was that those
claims "cannot be reached by `interpret`'s neighbour query, so they draw
no edges. The corpus is silently three days stale to its own
agent-facing surface."

### The second occurrence

Measured read-only against Neon during this run. Embeddings are fixed:
zero claims have a null embedding today. The staleness is worse anyway.

- 661 claims, 222 interpreted, 439 waiting, all 439 embedded.
- 216 edges in `claim_links`, and the highest claim id in any edge is
  221.
- `interpret` runs daily and strictly in id order, at 7 to 31 claims a
  day, about 15 on average. `distill` adds about 40 a day. Today
  `interpret` reached ids 212 through 222 while `distill` wrote ids 611
  through 661.

Three days stale on 2026-09-19 is twelve days stale on 2026-09-22, and
the gap grows by roughly 25 claims a day. The first occurrence was a
regression that stopped. This one is a rate mismatch that does not stop
on its own.

### Why it was not caught between the two

The first occurrence was found by an ExO corpus sweep and written as a
ledger entry about embeddings, so the fix that followed was an
embeddings fix. Nothing in the org watches the interpret queue's depth
or its trend, which is the quantity that actually determines whether the
graph reaches the frontier. A backlog that is drained every day looks
healthy in any check that asks "did it run", and every check the org has
asks that.

### What it cost this run

The skill seat's cluster selection is specified against `supports` edges
in two charters. With no edge above claim 221, that criterion could not
be applied to the two thirds of the corpus where the operational
material actually lives, so this run selected on topic and procedure
density instead and said so in its pull request. It also means O2's
twelve-skills target is running on a corpus whose graph layer is
diverging from its claim layer.

### The fix, and who holds it

Engineer's, with the chair on the budget: rate-match `interpret` to
`distill`, work the backlog from both ends, and pair it with the open
"interpret neighbour query has no paper boundary" entry so a bigger
batch does not simply buy intra-paper edges faster. Full entry with the
numbers is in docs/ideas.md, dated 2026-09-22.

The monitoring gap is the more general lesson and belongs with the
register's own rules: **a queue is not healthy because its worker ran.
It is healthy when its depth is flat or falling.** Every blackboard
queue in db/schema.sql (`triage_queue`, `distill_queue`,
`interpret_queue`) is checkable that way in one SQL statement, and none
of them is checked that way today.

## Incident 31 — A new skill took a neighbour's trigger case, for the second time (2026-09-24, skill agent)

**Recorded under the standing rule.** The same failure happened on
2026-09-22 and was written up as a ledger entry rather than an incident,
so this is the repeat that puts it in the register. Numbered 31 on the
same contested basis as the renumber note on incident 30 above: numbers
23 through 29 are each claimed by at least one open branch today, and
the ExO's #77 already records the collision class as its own incident
29.

**First occurrence, 2026-09-22.** The `recursive-harness-self-improvement`
draft won `he-pos-3`, a case belonging to `harness-engineering`, on its
first complete pass. Diagnosed then as a length effect: the draft's
description was 170 words against the specimen's 102, and
`LexicalEngine.score` divides by the idf mass of the prompt's terms and
never by the candidate's own, so a longer description strictly dominates
a terser one on any prompt both cover.

**Second occurrence, 2026-09-24.** The `evaluation-integrity` draft won
`pt-pos-2`, "before we distil from our large teacher model, how do we
know its answers are actually right", which belongs to
`self-improving-post-training-loops`. The description at that point was
184 words. Cutting it to 150 and replacing the generic clause vocabulary
gave the case back, with the library at 27 of 27.

**Why the first fix did not prevent the second.** It was not a fix. The
2026-09-22 run rewrote its own description, which repairs that skill, and
proposed an engine change for the next run. The rule it also wrote into
prompts/skill-extract.md, treat anything past 150 words as a defect, was
the durable part, and this run wrote 184 words anyway because the rule
lives in a prompt a run reads at step 2 and the description is written at
step 3. Nothing measures the length at the moment the field is written.

**What would actually catch it.** A length check inside
`trigger_test.py`: emit a warning, in the same list that already flags a
description with no "Use when" clause, when any library description
exceeds the word budget. The runner is the one thing every skill run
executes before shipping. That is a `skills/_validation/` change, this
seat's surface, and it belongs in the same PR as the decoy-panel rewrite
the 2026-09-24 ledger entry proposes, not in a PR that also adds a skill.

**The general shape, which is the reason to register it.** A rule written
into a prompt is checked when someone reads the prompt. A rule written
into the runner is checked every time anything ships. Incident 20 is the
same lesson about a taste ruling, and the registers map
(docs/agents/registers.md) says the gate that checks before shipping is
the one the org keeps forgetting to build.

## 2026-09-21 — Two gaps found while building the prose benchmark (ADR-29)

Engineer seat, sprint 2026-09-21 item 2. Recorded here rather than only
in the ledger because ADR-29 says every detected gap is an
incident-register entry with its class named, however small. Neither of
these lost a run. Both were invisible until a piece of work happened to
walk into them, which is the part worth recording.

Titled by date rather than by number on purpose. PR #60, this seat's
previous run and still open, is taking incident 23.

### Gap 1: the comped friends list is a category, not a roster

**Class: awareness.** The org planned around an asset it never created.

Sprint item 2 says to have "the comped friends list score both blind".
The grading packet is built and there is nobody to send it to. The word
`comped` appears in docs/sales/first-customers.md as a pricing tier, in
the launch calendar as the audience for the final pre-launch digest, and
in the roadmap. No file in the repository names one person on it, one
email address, or even a count.

Three planning documents and one sprint item depend on that list. The
sprint's own "Notes for the engineer" says items 2 through 4 need "only
the corpus, the sent issue(s), and the comped friends list", which reads
as a statement that all three were in hand. Two were.

The fix is the owner's, because it is her friends and their addresses,
and because where personal contact details live is a decision before it
is a file. Filed in docs/ideas.md the same day.

### Gap 2: the prose ban list cannot be cited by number

**Class: enforcement.** A register that cannot be addressed cannot be
checked at the artifact.

docs/voice/ban-list.md has two entries numbered 26, two numbered 27, and
no 30 or 31. This surfaced while writing docs/evals/ documentation that
cites the list by number, because "ban-list entry 26" points at two
different rules, one about a label that moved down a level and one about
the club sentence.

This is incident 20 one level down. Incident 20 was a ruling recorded in
the right register and never opened before the next artifact shipped.
This is a register that is opened, and then cannot be quoted back
precisely enough for anyone to argue about whether an artifact passed.
Stable ids that are never reused would close it. The file is the writer
seat's surface, so the proposal is in docs/ideas.md rather than applied
here.

### Not recorded as a gap, and why

This is the third consecutive engineer run unable to settle the two
`urgent` ledger entries about the archive count and the uncited 23.9%
claim, because both need database access this workflow does not carry.
That is not a gap under ADR-29. The fix is written down, it is
accurate, and it sits at `proposed` awaiting the owner's decision, which
is the system working rather than failing. It is named in the PR so the
wait is visible, and the ledger entry filed today asks for a `Blocked
by:` line so a pending decision of this shape stops being retold as
prose in three PR descriptions.

## 2026-09-23 — The same urgent question has been unanswerable for four runs (engineer seat)

Unnumbered on purpose. Open PRs at this moment carry entries up to 26 and
numbering them from a branch is how the file ended up with two incident
20s and two incident 22s. The ExO can give this one its number on the
next read.

**The repeat.** The ledger entry "Verify the archive: the press may have
printed once, not four times" (docs/ideas.md, 2026-09-19) is marked
`urgent` and asks for one query: `select week, created_at, model,
prompt_sha from digests order by week`. It decides whether the newsletter
has a fixed bug or an eleven-day outage with subscribers on the other end
of it. Four engineer runs have now recorded that they could not run it.

- 2026-09-19 filed it urgent, with the reason: the engineer workflow has
  no database credentials.
- PR #60 (2026-09-20) reports the same blocker for the Modal half.
- PR #69 (2026-09-22) reports it again, naming `NEON_RO_URL` directly.
- This run confirmed it at the source rather than by assumption.
  `.github/workflows/agent-engineer.yml` passes exactly two values into
  the container, `GH_TOKEN` and `PROJECTS_TOKEN`, and `modal` is not
  installed in the agent image. `NEON_RO_URL` is wired into the research
  and skill workflows only.

**Why it is an incident and not a ledger entry.** It already is a ledger
entry, twice, and the ledger is the wrong instrument for it. A proposal
waits for a verdict. This is a seat that cannot perform a duty its own
charter's Observe step assigns it, so every run rediscovers the same wall
and writes the same paragraph. The standing rule at the top of this file
covers exactly that: an issue that occurs more than once is recorded here
at the moment it repeats.

**What would close it.** One line in `agent-engineer.yml` adding
`NEON_RO_URL` to the job's env from the existing secret, which is the
same secret the research and skill workflows already read. That edit is a
runtime change (docs/agents/runtime-changes.md), so it is not this seat's
to make. It is filed for the owner or the chair, and until it lands, the
engineer's charter step 3 ("pipeline health") and every ledger item that
needs the database of record are unperformable by design rather than by
accident.

**The cost so far.** Five days on the archive question, which is a
question about whether people who subscribed have been receiving
anything.

## Incident 31 — The rejected sentence was the generator's own instruction, one day after the same defect was named in another file (2026-09-24, writer seat)

**Class, per ADR-29.** Enforcement gap. A rule was written, in the right
register, by the right seat, and the file that produces the artifact was
never checked against it.

**Recorded because the standing rule says so.** This is the second
occurrence in twenty-four hours, in two different generators.

**Numbering.** `origin/main`'s tail is still incident 24 and its
continuations. Entries 25 through 30 are on the writer chain, unmerged.
31 and 32 follow them, per the rule incident 30 left behind.

### What happened

The owner read issue 2026-W39 and struck its opening sentence: "You
spent last week watching agents get faster by doing less at test time."
Her ruling, verbatim: "dont assume readers read each issue." It is now
canon law 13.

The sentence was not the model's invention. `prompts/digest.md`, the
generator this seat owns, contained this in its opening spec:

> Some weeks the honest move is continuity: name what the last issue
> flagged as unresolved and say what changed, which orients and
> interprets in one move.

The rejected sentence is that instruction carried out correctly.

### Why it is a repeat

Ban list entry 44 was added to `docs/voice/ban-list.md` on 2026-09-24,
hours earlier, and says exactly this: "A tell a model reaches for by
habit shows up in some issues. A tell its instruction requires shows up
in all of them, and no amount of rereading the output catches it,
because the writer is obeying." Entry 44 closes with the instruction to
"read every generator, not the one this seat happens to own."

The entry was written from `prompts/daily.md`, a generator in another
seat's pull request. The same defect was sitting in `prompts/digest.md`
at the time, and the sweep that found it in the unfamiliar file did not
turn around and run over the familiar one. The seat looked everywhere
except at itself on the day it wrote the rule about looking.

### The fix, applied

`prompts/digest.md` changed in six places in this pull request. The
continuity shape is replaced by the running thread stated whole, the
greeting is told that its "you" may name what the reader builds and
never what they have read, and a hard gate before output names four
shapes of the failure. Canon law 13 carries her specimen and the
repaired opening.

### The rule that would have caught it

When a ban list entry is added from reading one generator, the same
read runs over every other generator in the repo before the entry is
committed. The sweep is the entry's cost of admission, not a follow-up.
There are two generator files today and the seat owns one of them.

## Incident 32 — The pre-send quality gate returns a pass on the issue the owner rejected (2026-09-24, writer seat)

**Class, per ADR-29.** Enforcement gap, in its sharpest form: the
instrument ran, found nothing, and its silence was available to be read
as approval.

**Recorded because the standing rule says so.** This is the same defect
as ban list entry 36 and incidents 26 and 27, now in a third artifact.
A gate that enumerates instead of asking has failed once in the
generator's heading rule, once in its ASCII rule, and now in the tool.

### What happened

Issue 2026-W39 shipped with ten em dashes, seven semicolon joins, twelve
non-ASCII characters, and at least nine papers discussed in prose with
no link to any of them. Four rules of `prompts/digest.md`, each stated
in the version of the file that wrote the issue, some of them three
times over.

`tools/check_digest_quality.py` exists to catch exactly this before an
issue sends. It has been written, tested and open in engineer PR #60
since 2026-09-20. Run read-only against W39 during this editorial run,
it reports:

```
2026-W39.md: 0 blocking, 4 warnings.
  [warn] empty-intensifier (2x, ban list 5)
  [warn] bare-number (2x, ban list 24)
```

Zero blocking findings. Two of the four warnings are false.

### Three causes, all in the tool

1. **It parses zero items.** `parse_items` returns an empty list for
   W39, whose first and third sections are flowing prose rather than
   bold-led items. Every per-item rule then ran over an empty list and
   reported nothing: `citation-per-item`, `ends-on-citation`,
   `uniform-rhythm`, `uniform-length`. The gate never said it had found
   no items. A checker that cannot parse its input must fail loudly,
   because a green light on an unread file is worse than no light.
2. **The em dash is not in its character list.** `TYPESETTER` holds four
   entries: the non-breaking hyphen, two space variants, and the
   multiplication sign. The em dash is banned by canon law 1 and by the
   generator three times and is not among them. Neither is the Greek
   tau that W39 prints twice. The generator learned this exact lesson on
   2026-09-21 and its ASCII rule now asks whether every character is
   ASCII. The tool still lists offenders.
3. **`INTENSIFIERS` matches substrings.** It looks for `"very "` inside
   the lowercased line, so it fires on "every screen" and "every team".
   Both intensifier warnings on W39 are false, and a gate that cries
   wolf on "every" is a gate whose warnings get skimmed.

### Not patched here

`tools/` and `pipeline/` are outside the writer seat's writable surface.
Filed to the engineer in `docs/ideas.md` with the evidence above, which
is charter step 4: the third prompt edit is the wrong instrument when the
rule is mechanically checkable.

### The rule that would have caught it

Every gate is tested against an artifact known to fail it before the
gate is trusted. PR #60's tests assert that the checker finds the
defects it was written to find. Nothing asserted that it finds them in a
real issue, and the first real issue it met was one it passed.
*Renumbering note (2026-09-24, frontend run). These two entries were written
on branch `fe/2026-09-23-visual-sweep` as incidents 23 and 24, before main
carried incidents 23 and 24 for the Kimi routing rollout and the press 404.
They are re-identified here under the date-scoped scheme the ExO run shipped
the same day, rather than allocated new numbers, because that scheme is the
fix for exactly this collision.*


---

## INC-2026-09-24-email-template-never-opened — the designed email shipped for five days without ever being rendered (2026-09-24, owner-reported)

**Recorded by the engineer seat under the standing rule**, because this
is a repeat of the class incident 20 named and docs/agents/registers.md
generalized. It is not a new failure mode. It is the same one, in the
one place the org had not put an artifact-side gate.

**What happened.** The owner's words: "no ui applied to the emails...
only the html. i want the emails to have ui." The frontend seat designed
the newsletter on 2026-09-19 and shipped it correctly: the template at
`site/emails/digest.html`, its slot contract at `site/emails/README.md`,
and a working stdlib reference renderer at
`docs/design/reviews/2026-09-19/render_sample.py`. Every one of those
three files was right, and the review that produced them verified the
rendering at 3x by eye.

The press never opened any of them. `send_newsletter()` in
`pipeline/weekly.py` kept doing what it had always done, which was run
the markdown through `markdown.markdown()` and wrap the result in an
inline Georgia `div`. So for five days every issue that reached a real
subscriber was the undesigned email, while the designed one sat in the
repository being nobody's next step.

**Why it happened.** The same two halves incident 20 separated. The
archive-side gate worked perfectly: the artifact was produced, reviewed,
and filed where it belonged, by the seat that owns it. The artifact-side
gate did not exist. Nothing between `site/emails/digest.html` and a
message leaving the building ever opened the file, and no test, no
check, and no charter line asked whether the press used the template the
org had paid a design review for.

**The aggravating detail, which is the useful one.** There was no way to
look at the product. The only code path that rendered an email ran
inside a Modal container, at the moment of sending, to real subscribers.
To see one issue's email you had to mail it to somebody. An artifact
nobody can inspect without shipping it to a customer will not be
inspected, and then its defects are found by the customer. In this case
the customer was the owner, which is the cheapest possible version of
that and still the wrong one.

**The handoff shape, named so it is searchable.** A seat delivers a
finished artifact plus a reference implementation and calls the work
done. The receiving seat is never told, because the ledger entry that
would tell it is in a design review directory rather than in a sprint,
a test, or a call site. The artifact is complete, correct, and
unreferenced. Grep for the filename and the only hits are the file
itself, its README, and its own sample renderer, which is exactly the
fingerprint: **a designed asset whose only inbound references are the
files that produced it**.

**The fix, in this PR.**

- The press renders through the template.
  `pipeline/email_render.py` is the reference renderer lifted into the
  pipeline, the template and the renderer are bundled into the Modal
  image, and `send_newsletter()` fills it per recipient.
- The artifact can be looked at without sending it.
  `tools/rehearse_email.py` prints the filled HTML, sends nothing, costs
  nothing, and goes through the press's own `build_messages()` rather
  than a copy of it, so what it prints is what would go out.
- The gate is a check and not a charter line, per incident 20's own
  conclusion. `tests/test_email_template.py` fails if
  `send_newsletter()` stops going through the template or starts
  inlining styles again, the rehearsal exits non-zero on any unfilled
  slot, and both are wired into the pending checks workflow with
  `site/emails/digest.html` in its paths.

**What the org should grow from it, beyond this one email.** The
registers map asks, for each register, who writes to it and who checks
it before shipping. This incident says the same question has to be asked
of **designed assets**, not only of rulings and laws. A template, a
component, a prompt, or a schema handed from one seat to another needs a
named call site or a test that fails without it, in the same PR that
delivers it. Otherwise the handoff is a hope. The cheap general check,
which costs one command: for any asset a design review produces, grep
the repository for its filename, and if the only hits are the asset and
its own documentation, it is not in the product yet no matter how
finished it looks.

## INC-2026-09-24-writer-dispatch-started-twice

**A second writer run of one dispatch started 27 seconds after the first,
and the first was cancelled mid-run with a draft PR already open.** This is
a repeat of incident 14, recorded at the moment it repeated, per the
standing rule at the top of this file.

**What happened.** The owner dispatched one editorial run tonight.
`gh run list` shows `writer-agent` 35958638663 created 05:08:33Z and
`writer-agent` 35958671490 created 05:09:00Z. The first pushed a
placeholder commit to `writer/2026-09-24-c`, opened PR #92 as a draft at
05:09:39Z, and was cancelled at 05:10:09Z. The second, this run, was
already past its charter read by then. The market seat's dispatch shows
the same pattern in the same minute: `market/2026-09-24-b` and PR #93,
opened 05:10:31Z by a run created 05:08:31Z.

**Why it did not cost anything this time.** Ship-first is why. The
cancelled run had pushed and opened its PR in its first ninety seconds, so
what it had done was visible on the remote rather than lost inside a dead
container. This run found `writer/2026-09-24-c` when `git push` was
rejected as non-fast-forward, checked the other run's conclusion before
touching the branch, and adopted it: reset onto `origin/writer/2026-09-24-c`,
merged main to pick up the taste ruling the placeholder's base predated,
and continued in the same PR. One dispatch, one PR, no force push and no
second branch.

**What is different from incident 14, and what is not.** Incident 14's two
runs were both alive and both writing, and the lease was the only thing
that saved the work. Here the first run was cancelled, so the collision was
cheap. The *cause* is identical and unaddressed: one owner dispatch starts
two workflow runs seconds apart, and neither run knows the other exists.
Incident 14 produced rules for surviving the collision. Nothing yet
prevents it.

**The check this run used, worth stating as a rule for any seat.** A
non-fast-forward push to a branch name you just created is not a git
problem to be forced through. It means another run of your seat exists.
Run `gh run list` for your own workflow and read the sibling's conclusion
before you touch its branch. A cancelled or failed sibling is a branch to
adopt. A live one is a collision to report and step around, and the
charter's "your own last run may still be open" rule already covers
adopting, it just assumes the other run was yesterday rather than
twenty-seven seconds ago.

**For the ExO.** The fix is upstream of every seat: whatever dispatches
these workflows fired twice, and the two seats it hit tonight are the two
the owner dispatched by hand. Worth checking whether the dispatch path
sends one event or two before any seat writes more rules about how to
survive the second one.

## INC-2026-09-24-kimi-org-concurrency — Two seats, one Moonshot key, concurrency one (chair)

**What happened.** The owner asked for W39 reprinted under the new prose
rules (writer #92 merged, press redeployed). The reprint's single Kimi call
got `429 request reached max organization concurrency: 1` with a
`retry-after: 1`, honored it three times, and failed in four seconds. The
fallbacks are Groq's 8K models, none of which fit, so the press alarmed the
owner instead of printing. The other caller was almost certainly the
engineer's rehearsal print (#94, run 36022750452, in flight at the same
minute), which makes one real Kimi call that takes minutes.

**Fix shipped (chair, main).** A 429's wait is now the larger of the
retry-after header and our own schedule (30, 60, 120, 180s), so a
concurrency wait outlasts a sibling's call. Redeployed, reprint rerun.

**What it means.** Moonshot's limit is per organization, like Groq's. Every
seat that calls Kimi shares one slot. The rehearsal print (ExO's ladder,
engineer #94) and the weekly press must never run in the same minute, and
neither may any future daily press on the same key. Options for the
engineer: a scratch-row lock the callers check, or a second Moonshot
organization for rehearsals. ExO: the concurrency ceiling belongs in
`docs/agents/model-routing.md` beside the Groq rate-limit note.
---

## INC-2026-09-24-test-suite-ran-zero-tests — the command every test file prescribes had stopped running any of them (2026-09-24, engineer seat)

**Recorded under the standing rule as a repeat of incident 32's class.**
Incident 32 is a quality gate that returned `0 blocking` on an issue it
could not parse. This is the same shape one level up: the suite that
holds every other gate reported one error and ran nothing, and the
report looked small enough to scroll past.

**What happened.** Running `python3 -m pytest tests/ -q`, the command
printed in the docstring of nearly every file in `tests/`, produced:

```
ERROR collecting tests/test_evidence_grade.py
E   AttributeError: module 'modal' has no attribute 'Volume'
!!!! Interrupted: 1 error during collection !!!!
1 warning, 1 error in 0.43s
```

A collection error is not one red test. pytest stops, and zero tests
run. Every check the repository owns was unexecuted, and the line that
says so is `1 error`.

**Why it happened.** `modal` is not a dev dependency, so four test files
each carry a copy of the same hand-built stub, each guarded by
`if "modal" not in sys.modules`. Only one of the four copies defines
`modal.Volume`. Under the suite, `test_email_template.py` is collected
first, its copy wins, and `test_evidence_grade.py` then explodes on the
attribute its own copy would have provided. Alphabetical order decided
it. The guard that was supposed to make the four copies safe is the
thing that made them dangerous, because it makes the first copy
authoritative and none of the four is complete.

**Why nobody noticed, which is the useful part.** The repository has two
ways to run tests and only the broken one is documented.
`.github/workflows-pending/checks.yml` runs `python3
tests/test_press_resilience.py` and `python3 tests/test_email_template.py`
as single scripts. Run that way each file installs its own stub first
and every file passes, so the CI-shaped path was green on exactly the
files it names. The suite-shaped path was the one that failed, and it is
the one no command anywhere executes. Two paths diverged, and the
divergence was invisible because nothing ran the second one.

`checks.yml` is also still in `workflows-pending/`, so neither path runs
on a pull request at all. Its own README says it plainly: "anything
still sitting here is a guard that is not guarding yet."

**What it was hiding.** With collection fixed, the suite came up red on
`test_accounts.py::test_the_subscribers_index_cannot_abort_the_schema_on_legacy_duplicates`.
That test searches `db/schema.sql` for the first `do $$` block and
asserts it guards the subscribers index. A second do-block, the
evidence-grade constraint, was added above it at some point since, so
the test had been reading the wrong block and failing. How long is not
recoverable from this clone's squashed history. The schema itself was
correct throughout.

**The fix, applied.** One `tests/conftest.py` installs the union stub
before collection begins, so it always wins and the four in-file copies
no-op through their own guard. They are deliberately left in place,
because each of those files also documents being run directly and that
has to keep working with no conftest involved. The `test_accounts.py`
regex now selects the do-block by what is inside it rather than by being
first. `python3 -m pytest tests/ -q` reports 159 passed, 1 skipped.

**The rule that would have caught it.** A test suite is a gate, and
incident 32's rule already covers it: every gate is tested against an
artifact known to fail it before the gate is trusted. Nothing ever
asserted that the suite runs a known number of tests, so "ran zero" and
"all passed" were indistinguishable from the outside. The cheap general
form, and it is one line: **a test run that collects fewer tests than
last time is a failure, not a quieter success.** The same asymmetry sits
under incident 32, under the unreferenced-template incident above, and
under this one. A check that cannot see its input has to be louder than
a check that looked and found nothing, and by default every tool in this
repository has it the other way around.

---

## INC-2026-09-24-conflict-marker-on-main — the incident register itself was carrying merge damage (2026-09-24, engineer seat)

**Recorded under the standing rule as a repeat of incident 6's class**,
which is two seats appending to one register at one anchor and the
second merge conflicting.

**What happened.** `docs/agents/incidents.md` on main carried a bare
`=======` on line 3103, between the closing line of incident 32 and the
frontend seat's renumbering note. That is the middle marker of a git
conflict whose `<<<<<<<` and `>>>>>>>` halves were cleaned up and whose
middle one was not. Both sides of the conflict survived, so no content
was lost, and the file read as if a divider had been left in.

**Why it matters more than its size.** Every seat reads this file, the
ExO reads it weekly, and the charters cite it by line. It had been
sitting there through an unknown number of runs, and the fix is one
line. What is missing is not the fix but the looking: the charters warn
the seat that is *about to* append, and nothing looks at the file
*afterwards*. Incident 6, incident 25 (two writer runs appending at one
ban-list number) and incident 29 (four incident-id collisions) are all
the same anchor contention, and every one of the three fixes changed how
a seat writes. None of them added a check that reads the result.

**The fix, applied.** The marker is removed, and
`tools/check_registers.py` now reads all eight shared registers for
conflict markers and for duplicate incident ids, with
`tests/test_check_registers.py` driving it against damaged registers
built on disk. Its first run on the real repository also produced a
second finding, left for the seat that owns it: one ledger entry writes
`- Status: mostly moot as of run 3`, which is prose where the contract
names one of five keywords, so that entry is invisible to every
consumer that reads statuses by grep, including the PM's sprint
grooming and this seat's own fallback scan.

**Still open.** The checker is a command, and per runtime-changes.md's
closing rule a gate is worth the number of commands that run it. Nothing
runs this one yet. Wiring it into `checks.yml` needs a `workflows`
permission this seat does not have, so it is filed in the ledger for the
owner rather than done here.

---

## INC-2026-09-25-budget-guard-estimates — the first link in two deploy chains failed the press for the tokenizer's absence (2026-09-25, engineer seat)

**Recorded under the standing rule as a repeat of incident 32's class,**
and under L-A17, which owes an entry for any diagnosis that took more
than a minute whether or not it repeats. Incident 32 is a quality gate
that returned `0 blocking` on an issue it could not parse.
INC-2026-09-24-test-suite-ran-zero-tests, recorded yesterday, is the same
shape one level up. This is the third occurrence of the class in two
days, and this one is in the command the chair runs before every deploy.

**What happened.** Running `python3 pipeline/budget.py` on a fresh
checkout, as the first gate of this run's own change, printed:

```
budget: exact tokenizer unavailable (No module named 'tiktoken'); using the 3.0 chars/token fallback
...
SELFTEST: selftest: trimming could not fit a prompt of 6667 tokens...
budget check FAILED (1 problem)
```

with the remedy the guard prints beside that failure: shorten the
generator prompt, lower the output reservation, or move the press to a
model with a larger budget. All three are wrong. The press fits
`kimi-k2.6` with 140,766 tokens of headroom, and the same command says so
eight lines further up in the same output.

**Why it happened.** `count_tokens` falls back to a
3.0-chars-per-token ratio when tiktoken is missing, and that ratio runs
high on purpose, which is the right conservative choice. `selftest`
case 1 deliberately squeezes a filler prompt against a tight model:
20,000 characters, about 4,600 tokens measured, 6,667 tokens estimated.
The estimate alone crosses `openai/gpt-oss-20b`'s 6,800-token usable
budget, so the trimmer cannot fit a request that in reality fits, and a
selftest designed to have no slack has none left for the estimate's
own margin.

**Why it matters more than a stray red line.** This command is the first
`&&` in the press deploy chain, and as of this PR it is also the first
`&&` in the MCP deploy chain. Both now stop for it. A gate that fails for
a reason that has nothing to do with what it guards is a gate that
teaches the person running it to pass it with `|| true`, and the org's
own law says the value of a gate is that a shell enforces it. The
failure mode is not a broken deploy, it is a trained-away deploy check.

**What was fixed here.** The verdict now carries its own confidence.
Token arithmetic run on estimated counts is reported `UNCONFIRMED` and
the command ends `budget check INCONCLUSIVE` naming the one command that
resolves it, `pip install tiktoken`. The exit code stays non-zero, now 2
rather than 1, because a deploy checked on estimates has not been
checked and the chain should still stop. Everything that does not depend
on a token count, which is drift, the model tables, the fallback lists
and availability, stays a hard failure at exit 1 either way. Five tests
in `tests/test_rag_fallback.py` hold both halves.

**The rule that would have caught it.** None, and that is the finding.
Entry 41 of the ban list, "the gate that reads the output and never the
input," is the writer seat's version of this class and is already law
for digests. Incident 32 named it for quality gates and yesterday's
entry named it for the test suite. Three occurrences in three different
gates say the class is not about any one gate. The generalization worth
promoting, which is a ledger proposal rather than something this seat
writes into a standard: **a gate states what it measured, and a gate
that could not measure says so instead of returning a verdict.** Pass,
fail, and cannot-tell are three outcomes, and every gate the org owns
currently has two.

## INC-2026-09-24-grading-has-no-truth-pass — The editorial instrument grades prose and cannot see a false claim (2026-09-24, writer seat)

**The number.** `INC-YYYY-MM-DD-slug` per the rule at the top of this
file. Not a sequential number, and nothing here is renumbered.

### What happened

Issue 2026-W39 opened its fell-behind section on this:

> Start with the number that turned out to be wrong. A prior benchmark
> result held that an expert-authored reference implementation achieves
> 82.2% success on τ^τ-Bench, establishing a high ceiling for agent
> construction tasks. DRG-MAPPO, a hierarchical multi-agent
> reinforcement learning method for cooperative air combat, now reports
> 87% win rate in high-fidelity simulations. The contexts differ, agent
> construction versus combat simulation, but the broader belief that
> expert-authored baselines set immovable ceilings took a hit this week.

82.2% is a task success rate on a benchmark for building agents. 87% is a
win rate for simulated fighter aircraft against a simulated adversary.
They are not measurements of the same thing, so no belief about
agent-construction ceilings is touched by the second number. Nothing
fell. The section whose entire job is to report what stopped being true
led with something that did not stop being true.

Four editorial passes ran over this issue on 2026-09-24 and none of them
found it. Three separate writer runs graded it, one of them rewrote the
passage in full, and the rewrite kept the claim and shortened the hedge:

> The domains are different and the comparison is loose. What broke is
> the belief that an expert-written baseline is a wall.

### Why the instrument could not see it

The canon's grading procedure ran four passes, in this order: the
outsider read, the taste gate, the laws, the ban list. Every one of them
asks how the issue is written. Not one of them asks whether what it says
is so.

That is not an oversight in any single pass. It is the shape of the whole
instrument. The writer seat was created to own the words as a craft, and
its grading procedure was built entirely out of craft questions, so a
claim that is false and well made scores clean on all four. The better
the prose, the more invisible the defect, which is why the rewrite made
it worse rather than catching it.

The hedge is how it survived contact with four careful readers. "The
contexts differ" is correct, it is honest, and it reads as exactly the
instrument honesty the owner ruled is part of the product. A reader
checking for honesty finds honesty and stops. Nobody asked what the
honest clause was doing there, which was licensing the claim behind it.

### Why this is a repeat and not a new finding

Third occurrence in two days of one shape: **a check passed something it
had no way to fail.**

1. **Incident 26.** The ASCII rule stated the class and the pre-output
   gate enforced a narrower form of it, so four of eight non-ASCII
   characters walked through a gate written to stop them.
2. **Incident 32.** `tools/check_digest_quality.py` returned `0
   blocking` on the issue the owner rejected, because `parse_items`
   read zero items out of it and every per-item rule then ran over
   nothing and reported nothing.
3. **This one.** The grading canon returns four clean passes on a false
   claim, because none of the four is a claim check.

The general form is worth stating for the ExO's pattern reading, because
incident 26 already produced one and this is its sharper version.
Incident 26 asked: when a fix enumerates, what is it an instance of?
This one asks the question one level up. **When a check passes, ask what
result it is capable of returning.** A gate whose possible outputs do
not include the defect in front of you has not examined it, and a green
light from such a gate is not evidence. Incident 32 named this about a
script. It is true of a procedure written in prose in exactly the same
way, and the procedure is the one nobody thought to audit because it
lives in a canon rather than in code.

### The fix, in this pull request

- **`docs/voice/canon.md`**: a fifth grading pass, the claims pass. It
  takes every comparison and every fallen belief in the issue and asks
  whether the two things measure the same quantity. It runs last, it is
  procedure rather than law, and it enforces laws 6 and 7, which already
  required the evidence grade to be aimed at the risk that is actually
  there.
- **`prompts/digest.md`**: the edge rule gains a second test. It had one,
  for strength, covering the `contradicts` edge that is really a scope
  limit. It now has one for kind, and the rule is that where two claims
  do not measure the same thing there is no edge at any strength.
  Alongside it, the hedge rule: if you find yourself writing the
  concession, you do not have the finding.
- **`docs/voice/ban-list.md` entry 50**: the hedge that licenses the
  claim it qualifies, with the W39 sentence as the specimen.

### What is still open, and it is not the writer seat's

The prompt can only refuse to print an edge the claim graph hands it.
The graph should not have produced this pair at all, because an
agent-construction benchmark claim and an air-combat simulation claim
share no measure and the edge between them is not a judgment call that
needs a language model. Filed in `docs/ideas.md` for the engineer.
Charter step 4 applies: the editorial half is in this pull request and
it is the last prompt edit worth making on this one.

### The second thing this run found, recorded because it is the same shape

`docs/voice/value.md` was specified on 2026-09-21 as phase zero of the
copy pipeline and did not exist on 2026-09-24. The writer charter says
plainly that while it is missing, drafting copy is the wrong work and
writing that page is the right work. Four writer runs happened in the
twenty-four hours before this one. All four graded the same unchanged
issue and none opened the file.

The cost was already paid before the file was specified: eight rounds of
site copy, all eight rejected, and the chair's own reading of them found
that every one described the issue or the mechanism and none described
the library. Incident 25 named the missing artifact. Nothing scheduled
it, so every run chose the work its charter described first and the
blocking work stayed last for four days.

The shape is the same as the one above. A seat that grades its own output
every run will find defects in its output every run, and will never find
the work it has not started. Drafted in this pull request and awaiting
her approval.

## INC-2026-09-24-prohibition-supplies-the-string — A rule recorded in five places was broken by one of the recordings (2026-09-24, writer seat)

**The number.** `INC-YYYY-MM-DD-slug` per the rule at the top of this
file. Not a sequential number, and nothing here is renumbered.

### What happened

2026-W39 was reprinted at 16:04 on 2026-09-24 under the new prose rules.
The reprint is headed, over its reading list:

> ## Read these yourself

That is one of the four internal framework names, printed verbatim at
the top of a section a subscriber reads. It is the violation the owner
has flagged twice, the second time in the word "AGAIN", and incident 20
exists because the first recording did not prevent the second
occurrence. This is the third occurrence.

Two things make it worse than a recurrence.

**It is a regression.** The stale 2026-09-19 generator, writing the same
slot from the same material eleven hours earlier, produced "## The hour
you should spend", which is the craft the ruling asks for. The patched
generator replaced a heading written from the day's news with the
skeleton's own label.

**The generator that did it was the fully patched one.** The digests row
carries `prompt_sha` `0f642e2ce9f3`, which is the sha of
`prompts/digest.md` on `origin/main`. Nine editorial runs had merged.
This is the first issue written by the current generator, so the defect
cannot be assigned to an unmerged fix.

### Why five recordings did not stop it

The rule was written down in five places before the issue was
generated. The owner's ruling in `docs/voice/taste.md`, given twice.
Canon law 12. Ban list entry 20. The heading slot in
`prompts/digest.md`. And the heading gate at the end of the same file,
which asks the correct class question and would have failed the line.

One of those five caused the failure. The heading slot read, in full:

> `## {The heading for the reading list, written fresh and never the
> words "Read these yourself". ...}`

The curly braces are the one position in the template the model is told
to replace with its own writing. The nearest quoted English at that
position is the forbidden phrase. The model wrote what was there.

All four heading slots were built this way, each quoting its own
forbidden name. Three more of them were still loaded when this incident
was written.

The same mechanism produced two more leaks in the same issue, both from
worked examples in the same file. The plain-meaning example and the
number-line example were drawn from W39's own material, because W39 is
the issue whose grade produced canon law 14, and both shipped nearly
verbatim when the generator was pointed at W39 again.

### The general form, for the ExO

**Recording count is not enforcement strength.** L-A9 says recording a
rule is not enforcing it, and L-A4 says a repeated correction is a
register defect. Both are right and neither predicts this, because both
are about rules that were written somewhere and not checked. This rule
was checked, by a gate that asks the right question, and it still
shipped, because a sixth recording was working against the other five.

So the question to put to any register, prompt or charter is not how
many places the rule appears in. It is: **read the instruction from the
position of the person who obeys it. If the nearest quoted example at
that position is the thing being banned, the prohibition is a supply.**
Hold specimens where output is read, never where it is written.

This generalizes past prompts. Any checklist, charter or standard that
quotes a rejected specimen next to the blank where the work goes has the
same defect, and this org quotes rejected specimens constantly and on
purpose, because the preference data is the product of eight rejected
copy rounds. The specimens are worth keeping. Where they sit is now a
question worth asking.

### Fixed in this PR

All four heading slots state their rule positively and quote nothing.
The four names move to the heading gate at the end of the file, run
after the class question and never instead of it, per ban list 36. The
two leaked examples are rewritten from a subject no payload can contain,
and the invariant that already forbade example leakage now carries the
evidence that it failed. Ban list entries 51, 53 and 54 are appended.

## INC-2026-09-24-fix-by-deletion — Three house-law elements left the issue while it was being repaired (2026-09-24, writer seat)

**The number.** `INC-YYYY-MM-DD-slug` per the rule at the top of this
file.

### What happened

The 2026-W39 reprint did what the previous grade asked. It is
measurably less dense: the longest paragraph fell from 191 words to 98,
paragraphs over 100 words from five to zero, numbers in the heaviest
paragraph from ten to zero. The false ceiling comparison that ban list
50 was written from is gone.

It paid for that with three things that were already house law.

- **The greeting.** The owner struck "You spent last week watching
  agents get faster by doing less at test time" for assuming a returning
  reader. The reprint has no greeting at all. It cleared canon law 13's
  gate, because an absent greeting assumes nothing, and the greeting is
  an element she asked for by name.
- **The evidence grades.** Four in the pre-reprint, zero in the reprint,
  in an issue whose four items all carry numbers. Law 6 calls the grade
  "product, not weakness" and the canon calls it "the difference between
  this and a press release".
- **The traction evidence.** "three independent papers building on it"
  in the pre-reprint, nothing of the kind in the reprint. Law 5 requires
  the ranking to say what earned each slot.

Each one is a clause. Every compression pass reaches for clauses.

### Why the links survived and the grades did not

This issue is close to a controlled experiment, which is why it is worth
the register's space. The link rule and the evidence-grade rule are
adjacent in `prompts/digest.md`, at lines 788 and 790 of the generator that
wrote the issue. The same model read both in the same pass. Links shipped five
out of five. Grades shipped zero out of four.

The only difference between the two rules is one sentence, which the
link rule has and the grade rule did not:

> Count the items. Count the links. They match, or the issue is not
> finished.

**A rule survives a compression pass only if something counts it
afterwards.** Prose describing a requirement is removed by the same
edit that removes anything else made of prose.

### The general form, for the ExO

This is a near neighbour of INC-2026-09-24-grading-has-no-truth-pass,
recorded earlier the same day, and the pair is more useful than either
alone. That one says: when a check passes, ask what result it was
capable of returning. This one says: when a rule is stated, ask what
counts it. Both are the same underlying question asked at different
ends, which is whether the mechanism can register the failure at all.

The second question has an answer that is cheap to act on anywhere in
the org. Any requirement that can be expressed as "there should be N of
these" gets a count beside it, and the count is the rule rather than a
reminder of it. Requirements expressed only as prose survive exactly as
long as nobody is editing for length.

The subtler half is the deletion itself, and it is ban list 52. A ruling
against how an element was written is never a ruling against the
element. Canon law 13 already says the repair "is never deletion", and
it said that about threads, so the generator deleted a greeting instead.
Every gate that names a fix should say what must still be there when the
fix is done.

### Fixed in this PR

The evidence grade gets the count the link rule already has. Canon law
13's "never deletion" clause is extended to bind the slot as well as the
sentence, with the opening's four jobs rechecked after any repair. Ban
list entry 52 is appended.

## INC-2026-09-25-tell-recorded-never-enforced — Two of four new ban-list entries never reached the generator, in the pull request that patched the other two (2026-09-25, writer seat)

**This is a repeat of incident 20 and of L-A9, recorded at the moment it
repeated, per the standing rule at the top of this file. What makes it worth
the entry is who committed it: the seat whose charter carries the "check the
register before you ship" rule, inside the artifact that rule governs.**

**What happened.** The editorial run of 2026-09-24 graded row 18 of
`digests`, wrote four patches into `prompts/digest.md`, and appended four new
tells to `docs/voice/ban-list.md` as entries 51 to 54. This run checked
whether those two lists line up. They do not. Entries 52 and 53 reached the
generator as patches 3 and 1. Entries 51, the rule's own name printed as a
label, and 54, the term introduced under one name and used under another,
were written down and left there. Both describe defects the graded issue
actually committed, both were findings of that same grade, and neither
changed the machine that writes.

**Why it happened, which is the transferable part.** A grade produces
findings of two kinds, and they leave the run through different doors. A
finding about a sentence the issue printed becomes a patch, because the
prompt has an obvious place to put it. A finding about a class of tell
becomes a ban-list entry, because that is what the ban list is for. Entries
51 and 54 are class findings. Writing them felt like finishing the work,
and the ban list had nothing in it that asked what happens next. The register
that exists to catch a pattern became the place the pattern went to rest.

**Why the existing gate did not catch it.** The charter's pre-ship check
reads the registers against the artifact, and the artifact it has in mind is
an issue or a page. On a day when the output IS the register, the check has
nothing to compare. The seat read `ban-list.md` that night, appended to it
correctly, and never asked whether what it appended had landed anywhere.

**The general form, for the ExO.** Every register in this org has a gate
that decides something gets written down. Incident 20 named the missing
second gate, the one that checks an artifact against the register before it
ships. This is a third gate, and it is missing everywhere the other two
exist: nothing checks that a register entry ever reached the thing it
governs. A rule is written, a rule is checked against output, and in between
sits the step where a rule becomes machinery. Worth asking of every register
in `docs/agents/registers.md`: for an entry written last week, what would be
different in the product if it had never been written? Where the answer is
nothing, the entry is a note.

**Fixed in this PR.**

- `docs/voice/ban-list.md` gains a standing rule in its header: a new entry
  ends either in the change to `prompts/digest.md` that enforces it, or in
  the ledger entry saying why no prompt change can reach it.
- Entry 54 is enforced. The first-use pass now counts the term the reader
  meets rather than the term the writer defined.
- Entry 51 is enforced. The internal-vocabulary test now names this file's
  own rule headings, where it had listed only the codebase's vocabulary.
- Both enforcement lines are written into entries 51 and 54 themselves, so
  the next reader of the register can see the ending without leaving the
  file.

**What is still open.** The standing rule binds `ban-list.md` only, because
that is the file in this seat's custody. Whether the same ending belongs on
entries in `docs/agents/incidents.md`, `docs/ideas.md` and
`docs/design/ban-list.md` is the ExO's call and not this seat's.

## INC-2026-09-24-dispatch-403 — ADR-033's proof did not transfer: the PM's own dispatch call 403s

The PM standup (pm/standup-2026-09-24-b, second run this day) tried to
exercise charter §5 for the first time since ADR-033 marked it ACTIVE:
`PM_DISPATCH_ENABLED` was `true`, the owner-present gate was clear
(10h40m since the last `workflow_dispatch`), and two well-evidenced
dispatch candidates were queued (market's stalled PR #93, engineer's
conflicting PR #60). Both attempts failed identically:

    gh workflow run agent-market.yml -f owner_instructions='...'
    could not create workflow dispatch event: HTTP 403: Resource not
    accessible by integration
    (https://api.github.com/repos/alexandrapaiz/alexandria/actions/workflows/360993730/dispatches)

Reproduced directly against the REST endpoint (`gh api
.../dispatches -X POST`), same 403, same message. This is not a typo
or a wrong workflow id: the endpoint, the ref, and the input all
matched `.github/workflows/agent-market.yml` exactly.

**Why this contradicts ADR-033.** The decision states plainly that "a
parent run started a child run with `GITHUB_TOKEN`" in HQ's
`dispatch-probe` workflow, and that "no App key is needed" given
`permissions: actions: write` on the calling workflow — which
`.github/workflows/agent-pm.yml` already declares. Alexandria's own PM
run, today, with that exact permission declared, could not create a
dispatch event with the token it was given. Either the probe's result
does not transfer from HQ's repo to this one (a different app
installation, a different org-level Actions setting, or a
fine-grained-PAT-vs-GITHUB_TOKEN difference nobody has isolated yet),
or something about this specific run's token was scoped down from what
the job's `permissions:` block requests. `gh auth status` in this run
showed the active token authenticated as `claude[bot]` (the Claude Code
app installation), not obviously the bare Actions-runner
`GITHUB_TOKEN` the workflow YAML sets as `GH_TOKEN: ${{ github.token
}}` — worth an engineer or ExO check of whether the two tokens are
actually the same value in this harness, since if they are not, ADR-033
was validated against a token this run never actually had.

**What this run did instead of pretending it worked.** Neither
dispatch fired. Both instructions are recorded in
`docs/sprints/dispatch-queue.md` under "Dispatched by the PM (attempted,
not fired)" with the exact 403 and the commands the owner or chair can
run by hand to get the same result manually. No run URL exists for
either because no run was created.

**Standing question for the ExO or engineer, not answered here.**
Confirm what token `github.token` actually resolves to inside a
`claude-code-action` step (versus a plain `run:` shell step in the same
job), and whether HQ's probe used the same execution path this seat
uses. Until that is answered, charter §5 should be read as unproven in
this repo specifically, not merely unproven in general.

---

## INC-2026-09-24-market-ranking-stub-only — a green run shipped the ship-first stub and nothing past it (2026-09-24, PM seat)

**Recorded by the PM seat under the standing rule**: a repeat of
incident 8's pattern ("run reports success, ships nothing"), so it is
recorded at the moment it repeats rather than left for a weekly pass.

**What happened.** The owner's evening dispatch (2026-09-24) asked the
market seat to rank issue 2026-W39 against newsletters builders
actually enjoy, rank alexandria against its $20/month competitive set,
write both ranks into a one-page decision brief for the PM, and then
dispatch the PM itself with the PR number once ready. Run `35958636133`
(market-agent, `workflow_dispatch`, 05:08:31Z–05:12:25Z) recorded
`"subtype": "success"`, `"is_error": false`, `"num_turns": 34`,
`"total_cost_usd": 1.7275`, well inside its 160-turn budget and no
sign of a cost or timeout cap. The branch it pushed, `market/2026-09-24-b`
(PR #93), holds exactly one commit: the ship-first stub. The file it was
meant to fill, `docs/market/briefs/2026-09-24-b.md`, still reads "This
stub is the ship-first commit. The full brief... land[s] in this same
file before the PR comes out of draft" — nothing after it ever landed.
Step 3 of the owner's own instructions, the `gh workflow run
agent-pm.yml` handoff, never fired: no `workflow_dispatch` run of
`agent-pm.yml` appears anywhere after 05:08Z until this seat's own
scheduled and message-triggered runs many hours later. Unlike incident
8's original case, ship-first worked and nothing was lost to sandbox
teardown; the gap is that a run reporting a clean, uncapped success
never did the work its own dispatch described past the placeholder.

**Why this belongs in the register rather than just the dispatch
queue.** The queue this seat writes is replaced in full every run and
is not a durable record; a pattern that has now repeated (incident 8,
then this) needs to survive past today's queue for the ExO's weekly
audit and for whichever seat next tunes how these runs report their own
completion.

**Not yet known.** Whether the run's 34 turns actually did the
research and lost it before writing the file, or never did it at all —
this seat has no transcript access beyond the job log's start and end
markers. That distinction matters for the fix and is worth pulling from
the uploaded `transcript-35958636133` artifact before treating this as
closed.

**No fix applied in this PR.** The PM seat's writable surface does not
extend to the market seat's workflow or prompt.

**Update, same run, before this PR came out of draft.** A separate
market run (`alexandria-market/2026-09-24-window`, PR #98) landed
independently in the same window and did finish the brief, superseding
PR #93. The deliverable gap this incident names is closed in substance;
this entry stands as the record of the pattern (a clean, uncapped
success shipping short of its own stated deliverable), left for the
ExO seat's weekly pattern read, the same seat that turned incident 8
into the original ship-first-commit rule. Whether the first run's 34
turns did the research and lost it, or never did it, is still unknown
and still worth pulling from the `transcript-35958636133` artifact.

---

## INC-2026-09-24-shallow-clone-merge-base-repeat — the shallow-clone merge-base gap, twice in one window (PM seat)

**Recorded under the standing rule at the top of this file**: any issue
occurring more than once is always recorded at the moment it repeats,
no exceptions, regardless of how fast it was diagnosed. This is the
second occurrence, not the first, so L-A17's one-minute leniency (which
market's PR #98 correctly claimed for the first one) does not apply
here — that clause covers a first occurrence, and the standing rule
above has no such carve-out for a repeat.

**What happened, first time.** PR #98 (market, this same window) hit a
shallow clone that hid the merge base with its own prior branch
(`market/2026-09-24-b`); `git fetch --unshallow` fixed it in under a
minute. Judged not to clear L-A17's bar, reasonably, for a first
occurrence fixed that fast.

**What happened, second time.** This run (`alexandria-pm/2026-09-24-window`),
building on PR #97 and PR #99 to reconcile them into one PR, hit the
identical symptom: `git merge-base origin/main
origin/alexandria-pm/2026-09-24-message` returned nothing, and
`git rev-parse --is-shallow-repository` confirmed the clone was shallow.
`git fetch --unshallow origin` fixed it in one command, and `origin/main`
itself moved during that fetch (504cc8d landed while this run's clone
was shallow), which is worth naming: a shallow clone in this harness
does not just hide history, it can hide a commit that landed on main
after the sandbox was provisioned.

**What it means.** The sandbox this org's agents run in defaults to a
shallow clone, and any run that needs `git merge-base` against a
sibling branch (adopting a prior run's work, resolving a same-day
collision, checking whether a branch is stale) will hit this. Two
independent seats hit it in the same afternoon. Worth a standing fix
rather than a per-run workaround: either the checkout step
(`.github/workflows/*`, ExO's to change) fetches full history by
default, or every seat's charter gets the one-line
`git fetch --unshallow` reflex before any merge-base check. Filed for
the ExO's weekly pattern read; not this seat's writable surface to fix
in the workflow files.

---

## INC-2026-09-26-deploy-workflow-no-smoke-run — a new workflow reached main and ran unattended with no smoke run behind it (2026-09-26, engineer seat)

**Recorded, not fixed.** This seat cannot push a workflow file, so this is
a finding for the owner and nothing more. It is addressed to her in the
pull request that carries it.

**What the §0 check found.** The engineer charter's daily machinery diff:

```
git log --since="36 hours ago" --format='%h %ci %an %s' -- .github/ pipeline/
```

returned `1baeb7f 2026-09-25 16:50:53 -0600 alexandrapaiz`, "Production
deploys via a deploy hook on main; seat branches no longer create Vercel
deployments (HQ Incident 5: the 100/day limit)". It adds
`.github/workflows/deploy-main.yml`, 29 new lines, and
`site/vercel.json`, 6 new lines.

The two questions docs/agents/runtime-changes.md exists to ask:

- **Did a merged pull request explain it?** No. `gh api
  repos/.../commits/1baeb7f/pulls` returns empty; the commit went
  straight to main.
- **Was there a smoke run behind it?** No. `gh run list
  --workflow=deploy-main.yml` holds exactly one run, at
  2026-09-25T22:50:57Z, `event: push`, `headBranch: main`. That run IS
  the first execution of the new machinery, which is the sentence the law
  is written to prevent: "the next cron is never the first execution of
  new machinery." A new workflow's first run is explicitly on the law's
  own list of runtime changes.

**It worked.** The run's conclusion is `success`, and the site deploys.
That is why this is a register entry and not an outage. The charter is
also explicit that the outcome does not decide whether it is recorded:
"Any runtime change with no smoke run behind it in `gh run list` is a
finding, recorded in the register whether or not it happened to work."

**Why it is a repeat, which is what makes recording it mandatory.**
Incident 23 is the same shape: a change to how runs execute, landing on
main without the ladder, and working or failing on its first unattended
execution rather than on a throwaway branch. Incident 23 failed and cost
four production failures. This one succeeded. The standing rule at the
top of this file covers the class and not the outcome, and the class has
now occurred at least twice.

**What is worth taking from it, blamelessly.** The gap is not that
anybody forgot the law. It is that the law's enforcement for workflow
files lives in a charter sentence, and the change was made by the one
participant no charter's §0 check runs before: the chair pushes directly
to main, so there is no PR for CI to gate and no seat's pre-flight to
read the register. Every other runtime in the org now has its gate in a
command rather than in prose. The press has the `&&` chain. The corpus
crons got theirs in this pull request. `.github/` has a charter sentence
and a Sunday audit.

The shape of a fix, for the owner and the ExO rather than for this seat:
a required check on main that fails a push touching `.github/workflows/`
unless a run of that workflow exists on a non-main branch. That is the
same idea as the rehearsal receipt, applied to a file instead of a model.
It is a workflow change, so it cannot come from here.

**Second and third sightings, recorded separately.** The same class recurred
twice more the same evening, when the chair rewrote the `Post run report` step
in all twelve `agent-*.yml` files in two direct pushes to main, nine minutes
apart, with no pull request and no run on a branch behind either. That is
INC-2026-09-26-slack-report-step-no-smoke-run, which has the shas and the
arithmetic. The class is now three pushes across two evenings, all with the
same fingerprint: a runtime change reaching main where no seat's pre-flight and
no CI gate can see it. One id per event, so it is not repeated here.

---

## INC-2026-09-26-kimi-concurrency-schedule-lock — the follow-up to INC-2026-09-24-kimi-org-concurrency: the schedule is now the lock (2026-09-26, engineer seat)

Its own id rather than a second heading under
INC-2026-09-24-kimi-org-concurrency, because ids in this file have to be
unique and `tests/test_check_registers.py` enforces it. Read it as a
continuation of that entry: this is the answer to the question it left
open for this seat.

That entry offered two options: "a scratch-row lock the callers check, or
a second Moonshot organization for rehearsals". The corpus move of
2026-09-26 (ADR-2026-09-26) needed a third, because it put two more
daily Kimi callers on the one slot and a lock between two Modal apps is
not something a single-process client can hold.

**What shipped instead.** `pipeline/llm.py` KIMI_WINDOWS declares the UTC
window every Kimi caller owns, and `budget.check_kimi_windows()` fails
`python3 pipeline/budget.py`, which is the first link in every deploy
chain, if two windows overlap or if a job's real `modal.Cron` minute
falls outside the window the table gives it. Today: the press and the
chair's manual rehearsal own 09:00 to 11:00, triage owns 12:00 to 13:00,
interpret owns 14:00 to 15:00, and 13:00 to 14:00 is deliberately empty
as the margin. No cron moved. What changed is that the slots are now
checked rather than coincidental.

**Why the schedule and not the lock.** A scratch-row lock is the stronger
mechanism and it is also the one that fails worse. A lock needs a
timeout, and a Kimi call that reasons for minutes makes that timeout hard
to pick: too short and the lock releases under a live call, which is the
bug it was built to prevent; too long and one crashed run blocks the
corpus until a human clears a row. A schedule with an hour of margin
needs no timeout and no cleanup, and its failure mode is the 429 the
backoff already survives.

**What is still open.** The chair's rehearsal is run by hand and cannot
be scheduled, which is why its band is two hours wide for a run that
takes minutes. The honest statement of the remaining risk: a rehearsal
started between 11:00 and 15:00 UTC can still collide with a corpus run,
and nothing prevents it. The backoff makes that survivable rather than
fatal, since both callers now wait 30 to 180 seconds rather than one.

---

## INC-2026-09-26-interpret-stale-third-sighting — The prompt fix for mis-typed contradictions has produced zero of the graph's 238 edges, seven days after merge, and the defect it fixes reached readers (2026-09-26, research seat)

**This is a repeat of incident 25, recorded at the moment it repeated, per
the standing rule at the top of this file. It is the third recorded sighting
of the same pattern and the first one with a published consequence attached.**

**What happened.** `prompts/interpret.md` was revised on 2026-09-19 by commit
a94a003, titled "Meta-review: sharpen interpret.md on contradictions, anaphora
and refines". The file at HEAD hashes to `6706ec7bffee`. Every edge in
`claim_links` — all 238 of them, created between 2026-09-08 and 2026-09-25 —
carries method `openai/gpt-oss-120b@fbe080261d6b`, and `fbe080261d6b` is the
sha of `prompts/interpret.md` as it stood on 2026-09-07. The revision has
produced no edges. It has never run.

**The consequence, which is what makes this different from the first two
sightings.** The undeployed revision sharpens the interpret layer on exactly
the error class the old prompt kept making. On 2026-09-19, the day the
revision was merged, the old prompt wrote edge 190 `contradicts` 188. Both
claims come from `arxiv:2609.10522`. A paper was recorded as contradicting
itself. Claim 188 was deprecated on the strength of that edge, and digest
2026-W39 published the deprecation to subscribers as something the field is
leaving behind. Two of the graph's other four `contradicts` edges are also
mis-typed: 12 -> 11 is two systems compared on one benchmark, and 85 -> 12 is
the same method measured on a harder subset. Three of five are wrong, and the
prompt that was written to stop this has been sitting merged for a week.

**Why the existing gate did not catch it.** The research charter's gate works
and worked. It says to compare the deployed sha against HEAD before spending
the week's proposal on an image-baked file, and it says that if the deployed
sha is stale, do not propose into that file. This run ran that check, found
the staleness, and correctly declined to propose into `interpret.md`. The gate
protects the proposal from being wasted. Nothing in it deploys anything, and
nothing escalates when the same file fails the check on three consecutive
runs. A gate that only ever says "not this week" is indistinguishable from a
gate that says "never" if no other step exists.

**The general form.** Incident 25 named this as a prompt that does not reach
production. Two runs have now found it still true at five days and at seven.
The missing piece is not detection, it is that detection has no destination:
the finding is written into a brief, the brief is read by whoever reads it,
and no deploy is owned by anyone on a clock. A merge to `main` changes nothing
in the pipeline by itself, which the charter states plainly, and the org has no
step between "merged" and "running" that anybody is accountable for. This is
worth the ExO's attention as a class, because the same freeze applies to
`prompts/digest.md`, `distill.md`, `triage.md`, `rag-answer.md`,
`skill-extract.md`, `sources.yaml`, and every file under `pipeline/`.

**A second gap found while checking.** `prompts/distill.md` records no sha
anywhere. `triage_log` has `prompt_sha`, `digests` has `prompt_sha`,
`claim_links` has `method`, and `claims` has nothing. The charter's staleness
gate cannot be run on the distill prompt at all. This run established its
deploy state by inference — `evidence_grade` is non-null on every claim from
2026-09-24 onward and null on every claim before, and that column was
introduced by the same commit that last touched `distill.md` — which only
worked because the change happened to be visible in the schema. The next one
may not be.

**Not fixed in this PR, and deliberately so.** The deploy is engineer lane and
`pipeline/` is frozen for this seat this week by the owner's dispatch. Routed
in `docs/research/briefs/2026-09-26.md` section 9, item 1, with the `claims`
`prompt_sha` column as item 4. This run spent its proposal on
`prompts/triage.md`, which was verified current, rather than stacking a second
fix behind an undeployed first one.

---

## INC-2026-09-26-engineer-run-twice-in-one-window — two engineer runs executed at once, four minutes apart (2026-09-26, engineer seat)

**Observed from inside one of them.** This entry is written by run
36208446311 while run 36208644267 is still executing.

```
2026-09-26T01:30:18Z  engineer-agent  workflow_dispatch  main  in_progress  36208644267
2026-09-26T01:26:48Z  engineer-agent  schedule           main  in_progress  36208446311
```

The scheduled run started first. The dispatched run started 3 minutes 30
seconds later, which is inside the window where the first run had a branch and
a draft pull request but nothing a reader would recognise as a claim on the
day's work.

**Why it happened, as far as this run can see it.** The PM's sync session (PR
#113, docs/sprints/dispatch-queue.md) queued an engineer dispatch for the
owner's priority 1 and wrote the trigger down explicitly: fire "once `gh run
list` shows that run finished," meaning PR #110's run. That condition was
correct and was met. What no condition covered is that this seat's own cron
fires twice a day under HQ ADR-035, so "the last run has finished" and "no run
is starting" are different questions, and the queue only asked the first.

**Why it is a repeat, which is what makes recording it mandatory.**
INC-2026-09-24-writer-dispatch-started-twice is the same shape, one seat with
two live runs. Incident 14 is the same shape with the sharper ending, two runs
of one dispatch racing on one branch, saved only by `--force-with-lease`. The
PM's own session notes tonight name incidents 6 and 14 as the reason not to
dispatch into a running seat, and then a queued dispatch went out to a seat
whose next scheduled run had already started. The rule was known, written down
the same hour, and the gap was in the condition rather than in the knowledge.

**What this run did about it, since it could not stop the other one.** The
draft pull request's description was rewritten to address run 36208644267 by
id, to name the files this branch already holds, and to tell it to merge this
branch rather than build a second store. That is the only channel between two
runs of one seat: the pull request list, which every charter's pre-flight reads.

**The shape of a fix, for the PM and the ExO rather than for this seat.** The
queue's trigger is one clause short. "No run of that seat is in progress" is
what it means, and `gh run list --workflow=agent-<seat>.yml --status in_progress`
answers it in one command, where the current condition reads only the last
run's conclusion. A second guard belongs in the seat's own pre-flight: a run
that finds another run of its own seat in progress should say so in its first
turns and take a different item, rather than discovering the collision at merge
time. Both are charter or workflow changes, so neither can come from here.

**Seen from the other run, and one fact only it had (added by run
36208644267, PR #116).** This entry was written by the scheduled run while the
dispatched run was still working. The dispatched run reached the same finding
independently, which is the duplication this incident is about: both runs also
wrote this register entry, and one of the two was deleted at merge so the
register keeps one entry per event. What the second run can add:

- The two runs opened pull requests three minutes apart, #115 at 01:31:37Z and
  #116 at 01:34Z, and both branches kept gaining commits afterwards.
- The charter's "your own last run may still be open" rule did work. #116
  checked `gh pr list` first, found #115, branched from its tip rather than from
  main, and said so at the top of its description. Nothing was lost and neither
  run force-pushed the other's branch. What the rule cannot prevent is the
  duplicated reading: #116 spent turns reading #115's diff to learn what its
  sibling had already built.
- The runtime has a lever the charters do not. `concurrency: { group:
  agent-engineer, cancel-in-progress: false }` on each seat's workflow makes
  GitHub hold the second run until the first finishes, which is what every
  charter sentence on this subject is trying to say in prose. It is a workflow
  change, so it cannot come from either run.
- Merge order for the two pull requests: #115 first, #116 second. #116
  supersedes #110 completely and merged #115 at `5ef872e`, so after #115 lands
  the second merge is conflict-free except in the append-only registers, where
  both sides are kept.

---

## INC-2026-09-26-slack-report-step-no-smoke-run — twelve live workflows changed on main twice in ten minutes, no pull request and no smoke run (2026-09-26, engineer seat)

**The third instance of the class this file recorded twice today.** The other
two are INC-2026-09-26-deploy-workflow-no-smoke-run, in this same pull
request's parent branch, and incident 23. Recording it is the standing rule at
the top of this file, not a judgment call.

**What the §0 machinery diff found.** The engineer charter's daily command,
`git log --since="36 hours ago" --format='%h %ci %an %s' -- .github/ pipeline/`:

```
4e06105 2026-09-25 19:23:27 -0600 alexandrapaiz  Slack run reports: five bullets, one line each
3389284 2026-09-25 19:14:48 -0600 alexandrapaiz  Run reports post prose to Slack
```

Both rewrite the `Post run report` step in all twelve `agent-*.yml` files, 12
files each, 10 minutes apart. The step is what every seat's run executes at the
end of itself, so this is a change to what a scheduled job does.

The two questions docs/agents/runtime-changes.md asks:

- **Did a merged pull request explain it?** No. `gh api
  repos/.../commits/<sha>/pulls` is empty for both. Both went straight to main.
- **Was there a smoke run behind it?** No. The first execution of 3389284's
  step was okr-agent 36207911573, a production run three minutes later at
  01:17:15Z. The first execution of 4e06105's step is one of the two
  engineer runs in flight as this is written, one of which is this one. The
  next scheduled run was again the first execution of new machinery, which is
  the one sentence the law exists to prevent.

**It is working.** okr-agent 36207911573 concluded `success`. The step is also
written defensively: the webhook guard is inside the script rather than in the
step's `if:`, with a correct comment about why, and the `curl` ends in
`|| true`, so a Slack outage cannot fail a seat's run. That care is visible in
the diff and it is the reason this is a register entry rather than an outage.

**Why it still gets recorded.** The charter's own words: the outcome does not
decide whether it is recorded. And the class is now three deep in three days,
all with the same fingerprint, which is the chair or the owner pushing a
runtime change to main where no seat's pre-flight and no CI gate can see it.
The fix already written out in INC-2026-09-26-deploy-workflow-no-smoke-run is
the same fix for this one, and it is a workflow change, so it cannot come from
here.

**One thing worth an eye, not an incident.** The new summary extracts the pull
request description's first five bullet lines. The board's run report, built in
this pull request, derives its own one-line result from the first bullet of the
same description for the same reason. Both now depend on a seat's first bullet
being a sentence about the run. That is a convention with two consumers and no
owner, which is the shape L-E6 describes, so it is named here before it becomes
an incident.

## INC-2026-09-26-run-report-dash-echo — the run report step failed every run in twelve workflows, and marked two finished runs as crashes (2026-09-26, engineer seat)

**This is the consequence half of
INC-2026-09-26-slack-report-step-no-smoke-run**, filed earlier tonight by this
same seat. That entry recorded the governance failure, a runtime change reaching
twelve live workflows with no pull request and no smoke run, and it concluded
**"It is working."** It was not working. It had already failed twice when that
sentence was written, and the runs it failed were the two runs that wrote it.

**The failure.** `Post run report`, in all twelve `.github/workflows/agent-*.yml`:

```
parse error: Invalid string: control characters from U+0000 through U+001F
must be escaped at line 190, column 1
##[error]Process completed with exit code 4.
```

**The mechanism.** The step declares no `shell:`, so GitHub runs it under the
container's default `sh -e {0}`, and `/bin/sh` in
`ghcr.io/alexandrapaiz/alexandria-agent` is a symlink to dash. Dash's builtin
`echo` expands backslash escapes, which bash's does not. So in

```sh
pr=$(gh pr list --head "$branch" --state all --json number,title,url,body --jq '.[0]')
title=$(echo "$pr" | jq -r '.title // "no PR opened"')
```

every `\n` that `gh` had correctly escaped inside the JSON string became a real
newline in the middle of that string before `jq` ever read it. `jq` then refused
its own input for containing unescaped control characters and exited 4, which
`sh -e` turned into a failed step.

It is deterministic for any pull request body containing a newline, which is
every body any seat has ever written. Reproduced this run against four seats'
real pull requests, in the agent container, under `sh`:

```
okr/2026-09                            dash-exit=4
engineer/2026-09-26-board-store        dash-exit=4
writer/2026-09-26-b                    dash-exit=4
research/2026-09-26                    dash-exit=4
```

and under `bash`, the same command on the same input exits 0. The shell is the
whole bug.

**What it cost, which is not the missing Slack message.** `engineer-agent`
36208446311 (schedule, 01:26:48Z) and 36208644267 (dispatch, 01:30:18Z) both
ran their full session, pushed their branches, and opened pull requests #115 and
#116. Both are recorded as `failure`. Run health is read off those statuses by
the PM's daily standup, by `docs/agents/delivery-health.md`, and by the ExO's
weekly audit, so two complete runs now read as two crashes, and the next seat to
audit the fleet will spend its time diagnosing runs that worked.

**Why the earlier entry got it wrong, which is the part worth learning.** It
tested the conclusion against one run, `okr-agent` 36207911573, and that run did
conclude `success`. Its report step produced no output whatsoever, which is the
signature of the path where `gh pr list` returns nothing for the current `HEAD`,
so `jq` received the string `null`, parsed it fine, and never met the bug. The
step's successful path and its silent-skip path are indistinguishable in a log,
because the only command that prints anything on success is a `curl` ending in
`>/dev/null`. A green step that prints nothing was read as proof, and it was the
absence of evidence. **L-A6 in the company standards says judge a run by its
artifacts. The artifact here was an empty log, and an empty log is not a pass.**

**The repeat, which is why this is filed rather than fixed quietly.** This is
incident 23's shape for the third time in three days: a runtime change lands on
main outside a pull request, no smoke run behind it, and the first seats to meet
it fail completely. Incident 23 cost four production failures on a Friday
evening. INC-2026-09-24-press-provider-migration cost four more. This one cost
two mislabelled runs and would have kept costing one per run indefinitely,
because nothing in the fleet fails loudly when a notification step fails: the
job goes red, and a red job on a seat that shipped its work looks like the
tripwire firing rather than like a broken step.

**The fix, and the reason it is not a two-character fix.** `shell: bash` on the
step would end this bug tonight. It would not touch the class. The class is
twenty lines of shell living inside twelve YAML files, where no test can reach
it and where one edit ships to the whole fleet at once. So the logic moved to
`tools/run_report.py`, whose `compose()` is a pure function, with eighteen tests
in `tests/test_run_report.py`: the real body that broke production, a body with
raw control characters, both of the owner's bullet rulings, the no-bullets
fallback that the shell version contained but could never reach, and one test
that runs the script under `sh -e` so the container's shell is under test
instead of in production. The step becomes one command.

The workflow edit itself is queued as item 10 in
[pending-workflow-changes.md](pending-workflow-changes.md), because no seat can
push `.github/workflows/`. **That queue is now the thing to watch.** The tested
script is on a branch, the broken step is in production, and the distance
between them is one human hand. Until that hand moves, every run of every seat
is still recorded as a failure.

**One behaviour change went in deliberately.** The new step cannot fail the job.
A notification is not the run's work, and a red job for an undelivered message
is precisely the lie this incident is made of. Delivery failures print as
`::warning::` and the exit status stays 0. The report is also printed into the
run log, so the artifact survives even when the channel is unreachable.

**The repeat, logged 2026-09-27 by the engineer seat, run 6.** The standing rule
at the top of this file says a repeat is recorded at the moment it repeats, so
here are the two that have happened since the entry above was written, both of
them this same seat:

```
engineer-agent  36250253554  2026-09-26 14:57:18Z  failure  Post run report
  parse error: Invalid string: control characters from U+0000 through U+001F
  must be escaped at line 99, column 1 ... exit code 4
engineer-agent  36285149176  2026-09-27 01:18:48Z  failure  Post run report
  ... at line 111, column 1 ... exit code 4
```

Four runs now, all four in `Post run report`, all four after the run had
pushed its branch and opened its pull request. Both of these opened a pull
request the owner can read: #118 and #120. The count matters for one reason
only, which is that the fleet's own health signal is the thing being
corrupted. Anyone reading `gh run list` for this seat sees four failures in
two days and a seat that shipped four pull requests in the same two days, and
the first reading is the wrong one.

**Nothing here is new to diagnose and nothing here is mine to fix.** The
mechanism is the entry above, the tested replacement is `tools/run_report.py`
on this branch, and the step that calls it is item 10 of
[pending-workflow-changes.md](pending-workflow-changes.md). A seat cannot push
`.github/workflows/`. What the repeat adds is the rate: one failed run per
seat run, indefinitely, until a hand applies that item. At the fleet's current
cadence that is roughly twenty mislabelled runs a week.

## INC-2026-09-27-filler-tokenizes-cheaper-than-a-paper — a measurement calibrated against fake data, wrong by 17x, in five places within one evening (2026-09-27, engineer seat)

**A repeat, which is why it is here rather than only in the ledger.** The
class is the one `budget._filler`'s own docstring names: "Not `'x' * n`,
which tokenizes far too cheaply and would make every estimate here look
better than it is." The seat that wrote that sentence saw the failure
mode exactly, guarded against its crudest form, and then shipped a
milder version of it. It is also the class of incident 20 and of
`registers.md`'s two-gates finding: something is written down correctly,
and nothing between the writing and the next use ever checks it against
the world.

**What was wrong.** `pipeline/budget.py` sizes each cron's request before
it is sent, and it has no access to the real payload, so it builds
filler of the right length. `_FILLER` is one clean English sentence and
runs **6.17 characters per token**. Distill's payload is not English
prose, it is the cleaned HTML of an arXiv paper, and that runs **3.35 to
4.93**, worst case 3.35. So every estimate of distill's request was low
by up to 69%.

The visible consequence, on 2026-09-26: the guard reported that
distill's full-text request missed Groq's usable free tier by **109
tokens**. The real miss, at `FULLTEXT_CHARS` of 24,000, was about
**1,900**.

**Where the wrong number went, inside about four hours.** Two entries in
`docs/ideas.md`. `pipeline/distill.py`'s module docstring. `rehearse()`'s
docstring. Two test files' docstrings and a test comment. The budget
guard's own printed output, under a heading written that evening. And
`docs/agents/press-rehearsal.md`. Every one of those was written by a
seat acting correctly on the output of a guard, which is what a guard is
for.

**What it would have cost.** The ledger proposed a fix off the wrong
number and priced it as free and probably sufficient: drop the assumed
2,000-token reservation to 1,400, "which puts the full-text request at
6,309 tokens with 491 to spare". Against real papers that request is
about 7,500 tokens and misses by roughly 1,300. Had it shipped, the
arithmetic would have said fixed, the job would have gone on reading
abstracts, and the next seat would have been debugging a closed ticket.

**Two things went right and are worth keeping.** The guard was honest
about the *kind* of thing it did not know: `reservation_assumed` was a
separate key precisely so the assumption stayed visible, and that is
what made the audit possible. And the arithmetic was reproducible from a
single command, so checking it cost minutes rather than a day.

**The second mistake, made while fixing the first.** The corrected
constant was measured over the first 24,000 characters of each paper and
gave 3.65 chars/token. `FULLTEXT_CHARS` was then set to 13,000 on that
basis, the guard said it fitted, and a real paper missed by 5 tokens.
Density is not uniform through a document: a paper opens with a title
block, an author list, an abstract and a table of contents, and only
then settles into prose, so its first 12,000 characters are denser than
its first 24,000. **Measuring a window other than the one the job sends
is the same error wearing different clothes**, and it survived one round
of fixing the error it is a form of.

**The fix.**

- `budget.FULLTEXT_CHARS_PER_TOKEN`, measured over the window the job
  actually sends, with `tools/fulltext_density.py` to reproduce it
  against live arXiv and `docs/evals/2026-09-27-fulltext-token-density.json`
  as the receipt CI reads instead of the network.
- `budget.request_text()`, one function where three call sites used to
  build filler independently, so a job that declares a density gets it
  everywhere or nowhere.
- `tests/test_distill_fulltext_budget.py`, twelve tests, including the
  one that matters: the rehearsal's payload must be heavier than the
  heaviest real paper measured. It was 750 tokens lighter, so gate 3
  would have passed a request the provider refuses.

**The rule this argues for, offered rather than asserted.** A guard that
estimates a payload it cannot see must state what it assumed the payload
looks like, and something must compare that assumption to the real thing
on a schedule. An estimate is a claim about the world and the org already
knows what to do with those: it gives them an evidence grade.

## INC-2026-09-27-suite-fails-without-the-tokenizer — five tests reported a production defect that was a missing local dependency (2026-09-27, engineer seat)

**Filed under L-A17** (docs/standards/lessons.md): a failure diagnosed in under
a minute gets an entry, because that is the kind the org rediscovers. Nothing
shipped broken and nothing in production was affected.

**What happened.** Run 6 ran `python3 -m pytest tests/ -q` on a fresh sandbox
and got five failures. Their messages:

```
distill degrades again: a full-text request stopped fitting, so the job is back
  to writing claims from abstracts while reporting success
12000 characters sized as a paper is 3583 tokens and as prose 4001; if these
  are close, the density override stopped applying
distill cannot send a paper to openai/gpt-oss-120b: ... DOES NOT FIT,
  headroom -189
```

Every one of those is a statement about the press being broken, and the press
was fine. `tiktoken` was not installed. `pipeline/budget.py` falls back to a
chars-per-token ratio when it cannot load the real tokenizer, so the tests that
assert measured counts were comparing the fallback ratio against itself, and
the fallback puts a 12,000-character paper at 4,001 tokens where the tokenizer
puts it at 3,583.

**Why it is worth the five minutes.** This is
`INC-2026-09-25-budget-guard-estimates` wearing a different hat: a number
produced by the fallback ratio, presented as a measurement, believed. That
incident was about the guard's printed output and this one is about the test
suite's failure messages, and the second is worse in one way, because a failing
test names a defect and a reader's first move is to go looking for it. The
repo already had the answer in the same week's code:
`tests/test_rag_fallback.py` guards its own three counting tests with
`pytest.importorskip("tiktoken")`, and the two files added on 2026-09-26 and
2026-09-27 did not.

**Fixed in this run.** The five tests carry
`pytest.importorskip("tiktoken", reason=NEEDS_TIKTOKEN)`, with the reason
naming the install command CI already runs. With the tokenizer, 421 pass and 1
skips, unchanged. Without it, the five skip and say why instead of accusing
distill. CI installs `tiktoken==0.8.0` in a named step, so nothing there is
newly skipped, and a failure of that step still fails the build on its own.

**The general form, which is the part worth keeping.** A guard that degrades to
an estimate must not be read by anything that asserts a measurement. Either the
assertion refuses to run without the real measurement, or the estimate has to
be labelled everywhere it can reach, and the first is cheaper. That is the
third time this shape has cost something in three days, after the guard's
printed output and after the filler that tokenized like prose
(`INC-2026-09-27-filler-tokenizes-cheaper-than-a-paper`).

## INC-2026-09-27-new-register-shipped-without-a-gate — ADR-35 created a register on Friday, twelve lines went into it on Saturday, and nothing read it until Sunday (2026-09-27, engineer seat)

**What happened.** ADR-35 (merged 2026-09-25) made reading a precondition of
skill creation and created `docs/research/reading-queue.md` to hold what a
skill seat could not read. The skill seat's first run under it
(36206676462, 2026-09-26) did its half correctly: it read five papers in full
and appended twelve lines naming papers it needed. The ADR names the research
seat and the engineer as the drains. Neither has a step that opens the file,
so for a day and a half the queue was a register with an archive-side gate and
no artifact-side gate. Five of the first six ids turned out not to be in
`papers` at all, so the corpus did not hold the papers a shipped skill is
built on, and nothing in any run would have said so.

**Why this is a repeat and not a new finding.** It is incident 20's class
exactly, which is L-A9 in `docs/standards/lessons.md`: recording a rule is not
enforcing it. `docs/agents/registers.md` exists because of incident 20, it was
swept on 2026-09-24, and the gap it exists to catch was created the next day by
an ADR that did not add a row to it. The register map catches registers that
have a gate and lose it. It does not catch a register that is born without one,
because nothing fires when a new file starts being a register.

**Fixed in this run.** `pipeline/distill.py` reads the queue at the top of
every run and distills what it finds ahead of the day's intake, printing each
id and its disposition so the research seat can strike the line. The register
map gets the row that ADR-35 should have carried.

**The general form, which is the part worth keeping.** A decision that creates
a register creates two gates, and the second one is work. The cheap repair is
at the point of authorship rather than at the weekly sweep: an ADR that names
a new file as a place where things get written down should not merge without
naming the step that reads it, in the same way a new cron does not deploy
without naming its rehearsal. That is a proposal to the chair, since ADRs are
the chair's, and it is recorded here rather than acted on for the same reason.

## INC-2026-09-28-dash-echo-sixth-failure — the engineer lane has read as six consecutive crashes for two days, with a pull request opened on every one of them (2026-09-28, engineer seat)

**What happened.** `INC-2026-09-26-run-report-dash-echo` is not fixed. It has
now failed every engineer run since it landed: 36208446311, 36208644267,
36250253554, 36285149176, 36330209631 and 36342225307, opening pull requests
#115, #116, #118, #120, #122 and #124 respectively, and being recorded
`failure` every time. The log of the sixth is the log of the first, to the
character: `parse error: Invalid string: control characters from U+0000 through
U+001F must be escaped at line 177, column 1`, then `Process completed with
exit code 4`. Every one of those runs did its whole job first. Only the
notification failed.

**Why it is recorded again rather than left as one entry.** The standing rule at
the top of this file is that a repeat is recorded at the moment it repeats, with
no exceptions. It has repeated four more times since the entry was written. More
usefully, the original entry got the blast radius wrong and the number is what
tells a reader how urgent this is.

**The correction: two workflows, not twelve.** The 2026-09-26 entry and
`docs/agents/pending-workflow-changes.md` item 10 both say "all twelve
workflows, on every run." Only `agent-engineer.yml` and `agent-frontend.yml`
declare a `container:`, and the container image is where `sh` is dash. The other
ten run on the runner host, where GitHub's default shell for a `run:` step is
bash, whose `echo` leaves the escapes alone. Checked by reading all twelve for
`container:` and `shell: bash`, and by reading conclusions: every `pm-agent`,
`writer-agent`, `okr-agent` and `exo-agent` run since the step landed is
`success`. `agent-frontend.yml` has not run since, so its next run will be its
first failure.

**Why it stayed broken, which is the part worth keeping.** The fix was written
on the day it was found. `tools/run_report.py` is tested, it is on this seat's
branch, and the one-line workflow diff has been item 10 in
`docs/agents/pending-workflow-changes.md` for two days. No seat can push a
workflow file, so the fix waits on the owner's hand, and the only thing that
travels to her is a pull request description she has not merged yet. Six runs is
what that queue costs when the thing waiting in it is the thing that colours the
queue red.

The org already has the shape of this problem registered twice: recording a rule
is not enforcing it (incident 20, L-A9). This is the operational twin. Writing a
fix is not shipping it, and a fix that cannot be shipped by the seat that wrote
it should be loud in proportion to what it is costing per day rather than
filed once and left. What this seat can do about that is bounded, so what it did
is put the daily cost in the entry and give the owner a two-line version of the
fix she can apply in a minute: add `shell: bash` to the `Post run report` step
in the two containerised workflows. That is not the right fix, because
untestable shell in YAML is the root cause, but it turns the engineer lane green
today.

## INC-2026-09-28-twelve-workflows-changed-again-no-smoke-run — a second fleet-wide runtime change reached main with no pull request and no smoke run, and this run was the first to meet it (2026-09-28, engineer seat)

**What happened.** Commit 6820ac1 (2026-09-27 19:24 UTC, owner) added
`BOARD_API_URL` and `BOARD_RUNTIME_TOKEN` to the `env:` block of all twelve
`.github/workflows/agent-*.yml`, plus §14 to `docs/standards/pm.md`. Two new
secrets a run reads, in twelve live workflows, on main, with no pull request.
`gh run list` shows no run of any workflow between the commit and this one, so
there was no smoke run and the first seat to meet the change is this one, which
is the daily engineer run of 2026-09-28.

**Why this is a repeat.** `INC-2026-09-26-slack-report-step-no-smoke-run` is the
same event two days earlier, in the same twelve files, from the same hand:
"twelve live workflows changed on main twice in ten minutes, no pull request and
no smoke run." `docs/agents/runtime-changes.md` names a change to a secret a run
reads as a runtime change explicitly. That law was written after the first one.

**What it cost this time: nothing, and that is worth saying plainly.** The
change is additive. Both variables are set, `GET /api/health` on the board
answers `{"ok": true, "companies": 6, "token_configured": true}`, and no
existing step reads either name, so a wrong value could not have broken a run.
This entry is not a complaint about a two-line diff. It is here because the
first one cost four production failures in one evening
(INC-2026-09-24-press-provider-migration), because the law's own words are that
a runtime change is a runtime change "even when it is two lines and obviously
correct," and because a rule that is enforced only when a change turns out badly
is not enforced.

**The one real finding underneath it.** The change was half a change. It put the
credentials in every run's environment and wrote the directive that every seat
uses the board, and it shipped no way for a seat to use them: nothing in this
repository read either variable until this run, and the board's `runs` array was
empty two days after the board was seeded. That is the same shape as
INC-2026-09-27-new-register-shipped-without-a-gate, one layer down. A directive
landed, the surface it names existed, and nothing between the two ever opened
it. Fixed in this run's pull request, which is what the board client is.

## INC-2026-09-28-probe-wrote-two-permanent-rows — mapping an undocumented endpoint on a live board left two blank run reports that no API can delete (2026-09-28, engineer seat)

**Not a repeat, recorded anyway.** The standing rule covers repeats and this is
a first occurrence, so this entry is voluntary. It is here because the cost is
permanent and because the next seat to meet an undocumented write endpoint will
be one command away from repeating it.

**What happened.** `docs/standards/pm.md` §14 documents five board routes and
says run reports live on the board, but names no route for posting one. The
board read returns a `runs` array, so the endpoint had to exist. This run found
it by posting progressively fuller bodies to `POST /api/runs` and reading the
400s, which is a sound way to learn a schema from a server that has no OpenAPI
document. Two of those bodies were complete enough to succeed, so the board now
holds two run rows with a seat and nothing else: `01069305-c634-46a9-9d0f-9f72b6e988b3`
and `a36965bf-68fe-4b6d-886c-f1298f8336ae`.

**Why they cannot be cleaned up.** The board's server implements GET and POST.
PATCH, PUT and DELETE all answer `501`. There is no API path by which the seat
that created them can remove them, correct them, or mark them as noise. Only the
owner, in the store on the host, can. Both rows are on `alexandria`'s board
permanently unless she removes them.

**The general form.** A 400 costs nothing and a 201 cannot be taken back, and on
an append-only surface those two live one field apart. Probing for *required*
fields is safe and probing for *sufficient* fields is a write. The order that
would have avoided this: find the cheapest read that reveals the schema first,
which here was the `runs` array the board read already returned, whose keys are
the payload's keys. This run read that array only after creating the rows. The
same lesson is already half-recorded elsewhere in this org's history: the
2026-09-18 sprint review notes that GraphQL mutations against the live Projects
board persisted from a run that died and shipped no pull request, so the board
was "already partway done" on the third attempt. Writes to a live external
surface outlive the run that made them, including the runs that fail.

**What changed because of it.** Every write command in `tools/board.py` takes
`--dry-run`, which prints the exact payload and posts nothing, and the tool's
docstring and `docs/board.md` both say why: on a surface with no DELETE, the
other way to find out what a report contains is to spend it.

## INC-2026-09-28-press-week-label-off-schedule — the run that existed to recover the missing week published under the next week's label, and 2026-W38 was lost for good (2026-09-28, engineer seat)

**What happened.** `2026-W38` has never existed. Incident 24 records the first
half of that: the press cron did not fire on Monday 2026-09-21, and the owner
found out from her own inbox three days later. The second half was found today
and had not been recorded anywhere. The recovery print went out on Wednesday
2026-09-23 and it labelled its issue `2026-W39`, not `2026-W38`, so the run
whose entire purpose was to recover the missing week wrote under the label of
the week that had not finished yet. `digests` is keyed on week. The following
Monday's scheduled run computed `2026-W39` as well and upserted straight over
what the recovery had left. One issue was written to cover two weeks, the
second write silently replaced the first, and the week the org was trying to
rescue was skipped permanently.

**Why, mechanically.** `week_just_ended()` in `pipeline/weekly.py` anchored on
`date.today() - timedelta(days=1)`, with the comment "yesterday is Sunday on
cron day". That is true on the Monday the cron runs and false on the other six
days. On Wednesday 2026-09-23, yesterday was Tuesday 2026-09-22, which ISO
week numbering puts inside W39. The same function's second half was wrong in a
different direction: `monday = y - timedelta(days=6)` is a Monday only when `y`
is a Sunday, so an off-schedule run also produced a reader-facing date range
that was not a calendar week at all. That day's payload said "September 16-22"
while carrying the label for September 21 to 27.

**Why nothing caught it.** The docstring of the manual path in this module's
own header says `modal run pipeline/weekly.py` is a supported one-off, and
every recovery this org has ever run has used it. So the off-schedule path is
not an edge case, it is the path taken on exactly the days something has
already gone wrong. Nothing tested it, because the scheduled path is the one a
test writer thinks about, and the scheduled path was correct.

**Fixed in this run.** Both halves now come off one anchor, the last Sunday
strictly before today, so the label and the range can never describe different
weeks. `tests/test_press_week_label.py` pins Monday's answer against the old
expression for all 52 Mondays of 2026, so the scheduled path is provably
unmoved, and holds the 2026-09-23 case as its own named test.

**Not fixed, and it needs the owner or the chair.** The `digests` row for
`2026-W39` and the file `site/content/issues/2026-W39.md` are still whatever
the most recent write left there, and no issue covering 2026-09-14 to
2026-09-20 exists. Whether to backfill W38 is an editorial call, not an
engineering one. With this fix deployed the command is one line and it will
now label itself correctly, which it would not have done yesterday.

**The general form.** A date function whose correctness depends on the day it
runs is a function that is correct in production and wrong in every recovery.
Recovery paths run only after something has already failed, which is the worst
moment for a second defect and the moment least likely to be under test.

## INC-2026-09-28-guardrail-4-had-no-reader — the law that says read the artifact was read by nothing, and the standup enforcing it used a proxy that cannot answer (2026-09-28, engineer seat)

**What happened.** `docs/agents/delivery-health.md` guardrail 4 has said since
2026-09-24 that only an outside observer catches a run that never started, that
the observer is the PM's daily standup, and that the evidence is the artifact:
the newest row in `digests`, the newest issue the live site publishes, a probe
of the MCP endpoint. Today's standup, four days later, could not check the
press. It said so honestly and then reached for the nearest visible thing,
which was whether a commit had appeared under `site/content/issues/`. That
signal cannot answer the question at all. Nothing in this repository publishes
a digest to the site. `site/lib/content.js` reads hand-committed markdown and
its own comment says the database lookup is a future swap, so the absence of a
commit reads identically on a perfect week and on a dead one. The sprint item
written off that reading opens with a premise no evidence supports.

**Why it happened.** Guardrail 4 names the evidence and names the seat, and no
seat holds a credential for two of the three artifacts it names. `DATABASE_URL`
is in the `neon` Modal secret and in no GitHub Actions environment. So the duty
was assigned to a seat that structurally could not perform it, and the honest
response to that is the one the standup gave: substitute something visible.

**Why this is a repeat.** Incident 20's class, L-A9 in
`docs/standards/lessons.md`: recording a rule is not enforcing it. It is also
`INC-2026-09-27-new-register-shipped-without-a-gate` one week on, with the
same shape and a different file. delivery-health.md was written to close a
monitoring gap and was itself written without a reader. The standing rule at
the top of this file is why it is here.

**Fixed in this run, partly.** `tools/delivery_health.py` makes guardrail 4 a
command. Two of its four surfaces, the site and the MCP server, need no
credential and answer today. The two that need `DATABASE_URL` report `unknown`
rather than green, and the exit status carries that as its own code, because a
check that cannot see the artifact must not read as a healthy product. That is
the distinction guardrail 1 already draws in its own words for the press's
availability check.

**Not fixed.** The credential. One read-only Neon connection string in the seat
workflows' environment turns two `unknown` surfaces into real answers, and no
seat can add it. Filed in the ledger for the owner.

## INC-2026-09-28-board-run-reports-still-503 — the board's run-report endpoint has been refusing writes across two runs and seventeen hours, while its health endpoint reports ok (2026-09-28, engineer seat)

**What happened.** `POST /api/runs` answered
`503 the board's database is unreachable` again in this run, on four
attempts, from a different session and a different runner than the one that
first met it. Run 8 recorded it in the ledger as `urgent` at roughly 01:40 UTC.
This run met the identical response at roughly 18:50 UTC. Everything else on
the board still works on the same token in the same session: `show` rendered
five columns, `item` created `11ecbd61-35ef-42d8-8cb0-15699bcb0fcd`, and
`comment` posted to it. Only run reports fail.

**Why it is registered rather than left in the ledger.** It has now happened
twice, seventeen hours apart, and the standing rule at the top of this file
admits no judgment call on that. The ledger entry from run 8 is a proposal
addressed to the owner. This is the record that it is not a transient.

**What it costs, which is more than it looks.** `docs/standards/pm.md` §14
makes the board the state of the work, and the run-report half is the half that
tells the org whether a seat ran. Two properties make this failure quiet. The
board's `GET /api/health` returns `{"ok": true, ...}` while this write path is
down, so a monitor built on the health endpoint calls the board green. And
`tools/board.py report` deliberately prints a `::warning::` and exits 0, which
is correct, because a notification is not the work and
`INC-2026-09-26-run-report-dash-echo` is what the other choice costs. Together
they mean the board's `runs` array stays empty while every other part of the
board fills up, and nothing anywhere turns red.

**Not fixable here.** The board server is on the host and is not in this
repository. Left `urgent` in the ledger, where run 8 filed it.

## INC-2026-09-29-dash-echo-eighth-failure — the engineer lane's crash streak reached eight, the fix has been written for three days, and the step that fails is the one that would have told anyone (2026-09-29, engineer seat)

**What happened.** `INC-2026-09-26-run-report-dash-echo` has failed twice more
since `INC-2026-09-28-dash-echo-sixth-failure` was written. Run 36366360908
opened #127 and run 36466106318 opened #130, and both were recorded `failure`.
The log of the eighth is the log of the first, to the character: `parse error:
Invalid string: control characters from U+0000 through U+001F must be escaped`,
then `Process completed with exit code 4`. This run's own execution, 36513112021,
will make nine, because nothing in the live workflow has changed.

Eight runs, eight pull requests, zero real failures:

| run | pull request | status |
| --- | --- | --- |
| 36208446311 | #115 | failure |
| 36208644267 | #116 | failure |
| 36250253554 | #118 | failure |
| 36285149176 | #120 | failure |
| 36330209631 | #122 | failure |
| 36342225307 | #124 | failure |
| 36366360908 | #127 | failure |
| 36466106318 | #130 | failure |

**Why it is recorded again rather than left as two entries.** The standing rule
at the top of this file admits no judgment call, and the count is the content.
An entry that says "six" while the number is eight understates the only thing a
reader needs from it.

**What is new, and it is the part worth reading.** This is no longer a bug
waiting on a diagnosis. `tools/run_report.py` is the fix, it has eighteen tests
in `tests/test_run_report.py`, one of which is the exact body that broke the
step, and `docs/agents/pending-workflow-changes.md` item 10 carries the
replacement step ready to paste. Everything that can be done inside this
repository has been done. What remains is one `git mv`-sized edit to
`.github/workflows/agent-engineer.yml` and `agent-frontend.yml`, and no seat's
token may touch that path (incident 12). So the entry the org should read here
is not about dash, it is about the interval between a fix being written and a
fix being live, which for this one is now three days and eight red runs.

**The compounding cost, which run 9 could not see and this run can.** The step
that fails is the step that posts the seat's report to the owner's Slack
channel. So the failure suppresses the notification that would tell her the
lane is failing. `docs/agents/registers.md` calls this class of defect a
register with a writing gate and no reading gate. This is sharper than that: it
is a reading gate that fails closed on itself. Every one of the eight runs
finished its work, opened its pull request, and then failed at exactly the
moment it tried to say so.

**Related, and not the same.** `INC-2026-09-28-board-run-reports-still-503` is
the other half of this. The board's `POST /api/runs` returns 503, and
`tools/board.py report` correctly exits 0 rather than failing the run. Between
the two of them, both of the org's run-report channels are down at once: one
fails loudly and marks a healthy run as a crash, the other fails quietly and
leaves the board's `runs` array empty. The owner has no working surface that
says whether a seat ran, other than `gh run list`, which has said `failure`
eight times about eight successful runs.

## INC-2026-09-29-receipts-step-had-no-paths — a CI step written, reasoned and queued the same morning could not have fired, because nothing it guards was in the workflow's trigger paths (2026-09-29, engineer seat)

**What happened.** Commit `ba63921`, at 02:56 UTC today, added a fifth step to
`.github/workflows-pending/checks.yml`:

```yaml
      - name: the skill library shows its receipts, and they describe today's text
        if: always()
        run: python3 -m pytest tests/test_skill_receipts.py -q
```

The step is correct. Its comment is correct, and it states the property the
step exists to hold: every receipt on `/skills` is pinned by sha to the exact
`SKILL.md` text, so editing a skill without re-running the trigger test turns
the pull request red. The same commit added nine lines to
`.github/workflows-pending/README.md` explaining it.

What neither the step nor the README touched is the workflow's `on:` block.
`checks.yml` fires on a `paths` list, and after that commit the list contained
neither `tests/test_skill_receipts.py`, nor `skills/**`, nor
`site/lib/skill-provenance.js`. So the pull request that the step exists to
turn red is precisely the pull request that would not have run it. The only way
it would ever have executed is a change to `pipeline/`, `db/schema.sql` or one
of the press files, which is to say on every occasion except the one it was
written for.

**Why it is in this register.** The repository has met this class before.
`INC-2026-09-27-new-register-shipped-without-a-gate` is a register created on a
Friday and read by nothing until Sunday, and the whole of
`.github/workflows-pending/` exists because a workflow sitting there is, in its
own README's words, "a guard that is not guarding yet". The standing rule at the
top of this file admits no judgment call once something has happened twice. The
company standard is sharper still: L-A16 in `docs/standards/lessons.md` says
configured is not in effect, and a capability counts as live only when a run log
proves it served a real turn.

**Why it is worth more than one line, which is the part to read.** The three
previous instances were all visible by looking at where a thing lived. A
register nobody opens, a workflow in the wrong directory, a decision accepted
but not deployed. This one is invisible by looking. The step is in the right
file, in the right job, with `if: always()` like its neighbours, and the fact
that it can never run is forty lines away in a `paths` list, in a different
section of the same document. Reading the step tells you nothing. Reading the
whole file and holding both halves in your head at once tells you, and nobody
reads a workflow that way.

**Fixed in this run**, in the pull request that supersedes the one that made it.
`skills/**`, `site/lib/skill-provenance.js`, `tests/test_skill_receipts.py`,
`tests/test_graph_audit.py` and `tools/graph_audit.py` are in both `paths` lists
now. Twenty-three entries each, and they were checked by parsing the file rather
than by reading it.

**The gate that does not exist yet**, filed as a ledger entry today: a check
that reads every workflow, takes each step's pytest target, and asserts that the
test and what it imports are matched by at least one `paths` entry. This
incident is a near miss only because the same seat happened to open the same
file eight hours later for an unrelated reason. That is not a control.

## INC-2026-09-29-board-run-reports-503-third-run — the board's run-report endpoint has now refused three consecutive runs across forty hours, and everything else on it still works (2026-09-29, engineer seat)

**What happened.** Recorded again rather than left as one entry, for the reason
the dash-echo entries give: the count is the content, and
`INC-2026-09-28-board-run-reports-still-503` says "two runs and seventeen
hours". It is three runs and about forty hours.

This run, at 17:20 UTC:

```
$ python3 tools/board.py report --seat engineer --status success ...
::warning::board: run report not posted, board said 503 to POST /api/runs:
the board's database is unreachable
$ python3 tools/board.py show --company alexandria
Library of Alexandria
...
This sprint  (12)
```

The asymmetry the 2026-09-28 entry found is unchanged. Reads serve the full
board in the same second that `POST /api/runs` answers 503 about an unreachable
database. Nothing in this repository can fix it, because the board server is on
the host.

**One thing this run can add.** `show` returns `sprint-2026-09-21` as the open
sprint. Sprint 2026-09-28 has been planned, is on PR #129, and has not been
merged, so the board is not wrong. It is showing a week-old sprint because that
is the newest one the owner has merged, and a reader looking at the board today
would conclude the org is a week behind rather than that a plan is waiting for
a merge. The run-report outage and this are the same shape: the board looks
healthy and is quietly describing a different week than the one the org is in.

**No fix applied and none available from here.** The ledger's urgent entry of
2026-09-28 is the record, and the first step in it is the owner's.

## INC-2026-09-26-slack-notify-jq-control-chars — the Slack notify step breaks the "Post run report" job on a PR body with unescaped control characters (2026-09-26, PM seat)

**Recorded under the standing rule at the top of this file:** the same
symptom hit twice today, in two different engineer-agent runs, so this
is a repeat by the time this entry is written, not a first occurrence
judged against L-A17's leniency.

**What happened.** Two engineer-agent runs today both finished their
actual work successfully (the `claude-code-action` step and the
"No-ship tripwire" step both report `success`) and then failed the job
at the "Post run report" step, each with the identical symptom:

- run `36208446311` (schedule, started 01:26:48Z, became PR #115):
  `parse error: Invalid string: control characters from U+0000 through
  U+001F must be escaped at line 178, column 1`, `Process completed with
  exit code 4`.
- run `36208644267` (workflow_dispatch, started 01:30:22Z, became PR
  #116): the same `parse error: Invalid string: control characters...`
  at line 190, exit code 4.

Both failures are inside the Slack-notify sub-step of "Post run report"
(the `curl` block that posts `*engineer-agent* · success · $title` to
`SLACK_WEBHOOK_URL`), which reads the PR's `title` and `body` back with
`gh pr list --jq '.[0]'` and then re-parses that value with a second
`jq` call. The ship-first check ahead of it (branch pushed, PR exists)
passed cleanly in both logs; only the Slack post failed.

**The work survived.** Both runs' PRs (#115, #116) exist, are complete,
and are open on GitHub. This is a reporting-step failure, not a
work-loss failure, which is exactly the distinction charter Β§1f asks
this seat to draw before calling anything a real incident.

**Why it belongs in the register rather than only in today's
run-health line.** The queue this seat writes is replaced in full every
run and is not a durable record (same reasoning as
`INC-2026-09-24-market-brief-stub-ship-first-gap`), and the symptom has
already repeated twice in one day, which the standing rule at the top
of this file treats as mandatory regardless of how quickly it was
diagnosed.

**Likely cause, not confirmed.** A PR body containing a raw, unescaped
control character (for example a literal byte in the 0x00-0x1F range
carried through from a heredoc or a code block in the PR description)
makes the JSON `gh pr list --jq '.[0]'` emits fail a later `jq` parse
of that same text. Ordinary markdown text does not carry raw control
bytes, so this most likely traces to something in the PR body itself
(a pasted terminal transcript, a fenced code block with a stray control
character) rather than to the `jq`/`curl` step's own logic, but this
seat has no transcript access to confirm which PR body byte triggered
it.

**No fix applied in this PR.** This seat's writable surface does not
extend to `.github/workflows/*`. Filed for the ExO's weekly pattern
read and for whichever seat next tunes the Slack-notify step: the fix
is most likely to sanitize or `jq -Rs`-wrap the PR body before the
second parse, so a stray control character degrades the Slack message
rather than failing the whole "Post run report" step.

**Third and fourth occurrences, 2026-09-27, still unfixed.** This
standup's `gh run list` review found two more engineer-agent runs with
the identical symptom, both after this entry was already open and
unmerged: run `36250253554` (schedule, started 2026-09-26T14:57:18Z,
became PR #118) and run `36285149176` (schedule, started
2026-09-27T01:18:48Z, became PR #120). Same step, same `jq` parse
error, same exit code 4, both PRs shipped complete and open before the
notify step failed, so the work-survived finding still holds. Four
occurrences now (two on 2026-09-26, two more by 2026-09-27), across
four different engineer-agent runs, zero fixes attempted: this is past
the point where "filed for the ExO's weekly pattern read" is doing
anything, since the weekly read has now had one full week's worth of
recurrences to read and the step has not changed. Escalating alongside
the dispatch-403 entry above, same reasoning: a fix belongs in
`.github/workflows/agent-engineer.yml`'s notify step (and, on
inspection, probably every seat's identical notify step, since the
`curl`/`jq` block quoted above is copy-pasted per workflow file), which
is outside every seat's writable surface except the ExO's.

---

## INC-2026-09-26-dispatch-403-repeat — the PM's own `gh workflow run` still 403s, and today a same-day dispatch through a different path succeeded (PM seat)

**Recorded under the standing rule**: `INC-2026-09-24-dispatch-403`
already named this exact symptom two days ago and flagged it
unresolved and untested since. It repeated today, verbatim, so this is
recorded at the moment it repeats rather than left for the ExO's weekly
pass, per the standing rule at the top of this file.

**What happened.** This standup, with `PM_DISPATCH_ENABLED=true`
confirmed in the job's own environment, charter §5 ACTIVE, no
synchronous-mode conflict (last dispatch by anyone was 13.5 hours
earlier), and a well-evidenced trigger for the frontend seat (HQ
ADR-037 priority 1, engineer's PR #115, the `board-ui` item already
queued on the board ref), the dispatch call failed identically to the
2026-09-24 incident:

    gh workflow run agent-frontend.yml -f owner_instructions='...'
    could not create workflow dispatch event: HTTP 403: Resource not
    accessible by integration
    (https://api.github.com/repos/alexandrapaiz/alexandria/actions/workflows/361059087/dispatches)

**New evidence this run adds: the same day, a dispatch through a
different path succeeded.** PR #113 ("PM sync session 2026-09-26")
fired an okr dispatch at 2026-09-26T01:17:15Z (run `36207911573`,
`event: workflow_dispatch`, `conclusion: success`) from the same
repository, the same `PM_DISPATCH_ENABLED` switch, and presumably the
same charter §5 authority, hours before this run's identical attempt
403'd. PR #113 describes itself as a "synchronous session, owner
present... directing live through the chair," which is a different
execution path from this seat's scheduled `agent-pm.yml` run: it is
unclear from this run's evidence alone whether that dispatch was fired
by a `claude-code-action` step's `GITHUB_TOKEN` (the same mechanism
this run used and which failed) or by the chair acting through a
different, more-privileged credential. That distinction is exactly the
open question `INC-2026-09-24-dispatch-403` left for the ExO or
engineer to confirm, and it now has a concrete same-day, same-repo pair
of one success and one failure to compare, rather than only failures.

**What this run did instead of pretending it worked.** The dispatch was
not fired. The instruction is recorded in `docs/sprints/dispatch-queue.md`
under "Dispatched by the PM (attempted, not fired)" with the exact 403
and the command the owner or chair can run by hand to get the same
result manually.

**One piece of the standing question now confirmed rather than
guessed.** `gh auth status` inside this run reports:

    Logged in to github.com account claude[bot] (GH_TOKEN)
    Token: ghs_************************************************

`ghs_` is a GitHub App server-to-server installation token (the Claude
Code app installation, `claude[bot]`), not the plain Actions-runner
`GITHUB_TOKEN` that `.github/workflows/agent-pm.yml`'s `env:` block sets
as `GH_TOKEN: ${{ github.token }}`. The `claude-code-action` step
evidently authenticates `gh` with its own app token rather than passing
through the job's runner token, and a GitHub App installation's
permissions are set on the App itself, separately from the
`permissions:` block a workflow YAML declares for the runner token. That
is a concrete, confirmed candidate cause: ADR-033's proof (HQ's
`dispatch-probe`) may have exercised the runner's `GITHUB_TOKEN` from a
plain `run:` step, which is a different credential than what this seat's
`gh` calls actually hold inside a `claude-code-action` step. Still
unconfirmed: whether PR #113's successful okr dispatch went through the
same app token or a different, more-privileged one.

**Standing question, sharpened rather than new.** Whoever next has
transcript or token access to compare: pull the execution context for
run `36207911573` (the one that succeeded) against this run's
(`agent-pm.yml`, scheduled, 2026-09-26 ~14:56 UTC) and diff what
`github.token` resolves to in each, and specifically whether either one
ran as a plain `run:` step versus inside `claude-code-action`. Until
that comparison exists, charter §5's dispatch mechanism should be
treated as proven only for whatever path fired PR #113's okr dispatch,
not for the scheduled `agent-pm.yml` run this charter otherwise
describes as the seat that holds the authority. The App installation's
permission grant is the first thing to check: if `claude[bot]` is not
granted `actions: write` on this repo at the App-installation level, no
workflow YAML `permissions:` block can fix it, and the fix is an App
settings change, not a charter or workflow change.

**Third occurrence, 2026-09-27, escalated.** This standup (`agent-pm.yml`,
scheduled) re-checked the same trigger (HQ ADR-037 priority 1, PR #115
still open, `board-ui` still `status: next, assignee: frontend` on the
board ref, unchanged since 2026-09-26) and re-ran the identical
`gh workflow run agent-frontend.yml` command. Identical failure,
identical message, same workflow id
(`.../workflows/361059087/dispatches`):

    could not create workflow dispatch event: HTTP 403: Resource not
    accessible by integration

Three occurrences now (2026-09-24, 2026-09-26, 2026-09-27), all from
`agent-pm.yml`'s scheduled run, all with the same `ghs_` app-installation
token, none of them ever the successful path (PR #113's chair-directed
okr dispatch, a different execution context, remains the only
`workflow_dispatch` this seat's authority has ever actually produced).
Per charter §1f ("a repeated one gets escalated to the ExO per the
standing rule"), this is now escalated rather than re-filed a fourth
time: the standing question two entries above (does `claude[bot]` hold
`actions: write` at the App-installation level, and does the
`claude-code-action` step's token differ from a plain `run:` step's
`github.token`) has gone unanswered for three days across three
identical failures, and no fix has been attempted by any seat with the
access to try one. Until the App-installation permission is checked,
charter §5 authority is real only for direct chair-driven sessions and
not for this seat's own scheduled runs, which is the majority of when it
would fire.

---

## INC-2026-09-28-merge-not-deployed-repeat — a second cron fix merges and sits inert, same shape as incident 24 (PM seat)

**Recorded under the standing rule.** Incident 24 (the Modal press
cron) established the pattern: a fix can merge to main and still not
run, because this org's pipeline crons deploy by a separate, manual
`modal deploy` step no seat's token can perform, and nothing checks
that a deploy actually followed a merge. That pattern has now recurred
on a second, independent cron.

**What happened.** PR #110 (2026-09-26, engineer) merged the fix for
the corpus stall the 2026-09-24 curation brief found: triage and
interpret move to Kimi K2, replacing Groq's shared rate ceiling. The PR
says so itself: "Nothing is live: the change is written, tested and
dormant, because this seat has no Modal CLI and the deploy belongs to
the chair." As of this Monday ceremony, two days later, no evidence of
a deploy was found (this seat cannot reach Modal directly, so this is
inferred from the corpus-stall symptoms the fix was meant to close
still being the best available read; PR #110 also carries no confirming
follow-up). The gap between merge and deploy, which incident 24 cost a
full missed weekly issue over, is open again on a second cron.

**Why this is a repeat and not a fresh incident.** Same root cause as
incident 24: a manual deploy step with no owner and no check. Different
symptom (a stalled claim graph rather than a missed send), same
structural gap.

**What this run did instead of leaving it implicit.** Sprint
2026-09-28 item 2 assigns the engineer seat to build a deploy-drift
guard: each cron records the code/prompt sha it is actually running,
compared against `HEAD`, alarmed through the existing notify channel
per delivery-health.md guardrail 1 if they drift more than a day. Item
3 of the "top three" in docs/sprints/pending.md asks the owner directly
to run the two deploy commands PR #110 is still waiting on.

**Not yet done.** The guard itself does not exist yet; this entry
records the second occurrence of the pattern per the standing rule, the
same run that schedules the fix rather than only naming it.

## INC-2026-09-28-kind-test-quoted-and-violated - The generator named the rule it was breaking, in the sentence that broke it (2026-09-28, research seat)

**This is a repeat in the L-A9 / L-A22 class ("recording a rule is not
enforcing it"; "the gate goes in the command, not in the charter"), recorded
at the moment it repeated, per the standing rule at the top of this file. It
also carries the fourth consecutive sighting of the interpret-stale pattern,
after INC-2026-09-26-interpret-stale-third-sighting.**

### What happened

`prompts/digest.md` was revised on 2026-09-24 by commit fbc0886, "Generator:
an edge must pass the kind test, and a hedge you have to write is a finding
you do not have". The passage names the failure it exists to stop, using the
published 2026-W39 issue as its worked example:

> The published 2026-W39 opened this section on a benchmark success rate of
> 82.2% for building agents and a win rate of 87% for simulated fighter
> aircraft, and declared a ceiling broken. The two numbers share a percent
> sign and nothing else, and nothing was broken.

and closes with a hard rule: "If you find yourself writing the concession,
you do not have the finding. [...] Delete the sentence, not the hedge."

The `digests` row for 2026-W39 was written on 2026-09-28 at 09:01 with
`prompt_sha = ea2d678d86e9`, which is the sha of `prompts/digest.md` at HEAD,
including that passage. The issue it produced contains a section headed "The
82.2% ceiling was not a ceiling", pairing the same 82.2% agent-construction
number with the same 87% air-combat win rate, and containing this sentence:

> The problem is that these numbers share a percent sign and little else.
> [...] The edge between them fails the kind test, and the ceiling that was
> not a ceiling is better understood as a category error.

The generator applied the test, reached the correct verdict, named the test
by its own internal name, wrote the concession the rule forbids, and printed
the section anyway. The rule was deployed. It was read. It was quoted. It
did not fire.

### Why this is different from a prompt that never ran

Every prior entry in this class is a fix that was merged and never deployed,
and the remedy was always "deploy it". This one was deployed. The sha on the
row matches HEAD, and the output demonstrates the model had the passage in
context, because it reproduced the passage's own vocabulary. So the failure
cannot be closed by a deploy, and it cannot be closed by clearer wording
either, which is exactly what L-A22 predicts: a rule enforced by prose in a
prompt is enforced at the reliability of a model reading a file, and this run
is the demonstration that the reliability is not 1.

The research charter's meta-review step would ordinarily answer a defect in
`digest.md` by proposing sharper text into `digest.md`. That was declined
this week for this reason, and the decline is recorded in
docs/research/briefs/2026-09-28.md section 11.

### Fourth sighting of the interpret-stale pattern

Recorded here rather than as a separate entry, because it is the same
pattern as INC-2026-09-26-interpret-stale-third-sighting and the standing
rule asks for the repeat, not a new investigation.

`prompts/interpret.md` at HEAD hashes to `6706ec7bffee`. All 257 rows in
`claim_links`, created 2026-09-08 through 2026-09-28, carry method
`openai/gpt-oss-120b@fbe080261d6b`, the file as it stood on 2026-09-07. The
2026-09-19 revision has produced zero edges in nine days. The third sighting
reported 238 edges at seven days; the count has grown by 19 and the sha has
not changed.

New evidence this sighting, which the earlier ones could not have: edge
265 `contradicts` 85 was created on **2026-09-26**, seven days after the fix
merged. It links MaP-WAM at 83.3% on RMBench to EmbodiedSkills at 12.5% on an
RMBench subset, which is "different systems measured on the same benchmark",
the case the merged text names as never a contradiction. The undeployed fix
is not only failing to repair old edges; the stale prompt is still producing
the specific errors the fix names, after it merged.

### The consequence, measured

Six `contradicts` edges exist in the graph. Four are wrong, two of those are
between two claims of one paper, and all six targets are marked deprecated,
because `deprecated_claims` requires only `relation = 'contradicts'` and
`confidence >= 0.7`, with no check that the contradicting claim is newer or
from a different paper, though the view's own comment says "a newer claim
contradicts it".

Both issues ever sent published false supersessions off this graph. 2026-W37
built four of its five "Left behind" bullets on mis-typed edges, including
one that inverted a paper's finding: it told readers that an expert reference
reaching 82.2% showed an earlier 23.9% ceiling "was far too low", when both
numbers are from one table in one paper and the paper's point is that agents
fall far short of a human expert. 2026-W39 published the same claim-12
cluster again. Detail in docs/research/briefs/2026-09-28.md sections 4 and 5.

### The general form

The org now has three distinct failure modes for one rule, and it has seen
all three in nine days:

1. The rule is merged and the image is frozen, so it never runs
   (`interpret.md`, four sightings).
2. The rule runs and the model does not comply (`digest.md`, this entry).
3. The record that would tell you which of the two happened is itself
   unreliable: `digests` is upserted on `week`, so the row reports the last
   generation rather than the one subscribers received, and `claims` records
   no prompt sha at all.

Mode 2 is the one with no remedy currently designed anywhere. A gate in the
deploy chain fixes mode 1. Nothing fixes mode 2 except a check on the output
after the model has written it, which is the pre-send quality gate's
territory (PR #60, open since 2026-09-20) and not a prompt's.

### Not fixed in this PR, and why

The deploy chain and `pipeline/` are engineer lane. Routed in
docs/research/briefs/2026-09-28.md section 10, items 2, 4 and 6. This run
spent no system diff at all, for the reasons in section 11 of that brief.

## INC-2026-09-29-same-anchor-ledger-conflict-repeat — incident 6's conflict, in the append-at-the-end era (2026-09-29, skill seat)

Recorded under the standing rule at the top of this file, which says any
issue occurring more than once is recorded at the moment it repeats.

**What happened.** This run merged PR #111's branch into its own, per the
org rule about a seat's own last run still being open. The merge conflicted
in `docs/ideas.md`. The frontend seat's 2026-09-26 entry and the skill
seat's 2026-09-26 entry had both been appended at the end of the file in
parallel branches, so git saw one region rewritten two ways. Resolution was
mechanical, both entries kept, frontend's first, and nothing was lost.

**Why it is incident 6 again and not a new thing.** Incident 6 named
same-anchor ledger appends at the `## Proposals` header and was marked FIXED
at charter level by a rule requiring seats to check open PRs touching
ideas.md and declare merge order. The file no longer has that header and
seats now append at the end, so the named anchor is gone and the failure is
not. The end of an append-only file is an anchor. Every seat that appends
there is writing at the same address as every other seat that appends there
in the same window, and the declare-merge-order rule does not prevent the
conflict, it only makes the conflict expected.

**The general form, for the ExO.** A fix written against the *instance* of a
shared write address survives only until the address moves. Incident 6's fix
named a header; the header was removed and the fix went with it while
reading as still in force. The durable version is a property of the file
rather than of a location in it: `docs/ideas.md` is append-only and
multi-writer, so concurrent branches conflict there by construction, and the
useful mitigations are a merge driver that concatenates, one file per entry
under a directory, or an accepted resolution recipe in the charter so every
seat resolves it the same way. This run resolved it correctly by guessing,
which is the part worth removing.

**Not fixed here.** A merge driver or a directory split is engineer surface
and a charter change is the ExO's. Filed in `docs/ideas.md` is the wrong
place for it, since the defect is that file, so it is recorded only here.

## INC-2026-09-29-cluster-references-absent-repeat — every work a read cluster is measured against is missing from the corpus, second run running (2026-09-29, skill seat)

Recorded under the standing rule. First occurrence 2026-09-26, the first
ADR-35 run, which found all twelve works its cluster built on absent from
the `papers` table and queued them.

**What happened.** This run read five papers in full and pulled fifteen
arXiv ids out of their reference lists, chosen because the skill's claims
rest on them. A single query against `papers` returned zero rows for all
fifteen. Two of the fifteen are the independent check on the skill's central
finding: one paper reaching the same conclusion in the opposite regime, and
one reporting the opposite result that the read paper argues is a protocol
confound. The library therefore holds a cluster's conclusions and neither
side of the argument they settle.

**Why this is a corpus defect rather than a reading-queue success.** The
queue works and both runs used it. What repeats is the cause: ingestion is
driven by a source feed rather than by the citation graph of what the
library already holds, so a paper becomes reachable when a feed mentions it
and never because something in the corpus depends on it. A second run
producing the same finding with a disjoint set of papers is evidence the
rate is close to total rather than a property of one cluster.

**The general form.** Every seat that reads a source in full can name its
references cheaply, and nothing in the pipeline consumes that. The backward
edge from a read paper to its own bibliography is the highest-precision
ingestion signal the org has and it is currently carried by hand in a
markdown checklist. Whether that is worth automating is the engineer's call
and the reading-queue drain in PR #124 is the nearest existing path.

## INC-2026-09-26-example-supplies-the-frame — a banned specimen's class recurred one day after the register recorded it and the generator enforced it (2026-09-26, writer seat)

**Recorded under the standing rule at the top of this file**: any issue
occurring more than once is always recorded at the moment it repeats.
This is the second occurrence of ban list 53's class, and the first
occurrence was itself recorded and patched, which is what makes this
worth an entry rather than a line in a review.

**What happened, first time.** On 2026-09-24 the writer seat found that
`prompts/digest.md` quoted the phrases it banned at the exact positions
where the model writes. All four heading slots carried their own
forbidden name inside the braces the model was told to replace, and the
issue printed "## Read these yourself". Recorded as ban list 53 with a
general test: read the instruction from the position the writer occupies
when they obey it, and if the nearest quoted English at that position is
the thing being banned, the sentence around it is not doing its job.
Enforced on 2026-09-25 in the four heading slots. **The enforcement
worked**, and the rehearsal print of 2026-09-26 prints none of the four
framework names.

**What happened, second time.** The same file's reading-list section
offered "Worth the hour if you are choosing between one agent and a
planner plus a separate verifier" as the model line, two sentences above
its own instruction to "let no two entries take the same shape". Across
the two prints of 2026-W39, five reading-list entries out of five open
with "Worth the hour if you are", and one completes it as "choosing
between shipping a complex harness or teaching its structure to the
model". The section became a catalogue, which is the one thing the
section's own rule says judgment was supposed to buy.

**Why the first fix did not reach the second case, which is the part
worth learning.** Entry 53 was written about a prohibition that quotes
the banned STRING, and the fix was to move the string. This specimen
copies no string. It copies the SHAPE, and every cure written for the
first form leaves the shape intact: moving the example, changing its
subject, or rewording it all preserve the frame. A register entry
generalized to the level of its specimen rather than to the level of its
cause, which is L-A4's shape one layer up.

**What it means.** An example sitting at a writing position is a template
whatever the instruction beside it says, so an example there earns its
place only when repeating it would be obviously absurd. That is the
general rule, it is now ban list 56, and it is enforced in this pull
request: the reading list's line names the frame as spent, refuses three
rewordings of it by name, and counts openings and grammatical shapes
across the section's entries.

**Second finding, filed rather than fixed.** Three rules that had already
been patched failed anyway in the print `ea2d678d86e9` produced: the
ASCII gate (five em dashes), the evidence grades (zero of three, with a
count already in the rule), and the first-use pass (NQ, SFT, VLMs and
RRSI bare). One cause covers all three and it is not a wording problem,
so per charter step 4 it is in `docs/ideas.md` for the engineer seat
rather than rewritten a third time. Not filed as three incidents here,
because it is one finding.

## INC-2026-09-26-fix-found-in-one-slot — the same file was patched twice in one day for a defect that belonged to the file, and the third instance printed a false claim about the product (2026-09-26, writer seat)

**Recorded under the standing rule at the top of this file**: any issue
occurring more than once is always recorded at the moment it repeats.
This is the third occurrence of ban list 56's class and the second entry
about it today, which is itself the finding.

**The class.** An example sitting at the position where a writer writes is
a template, whatever the instruction beside it says. Recorded this morning
as ban list 56, with the general test, after two occurrences in
`prompts/digest.md`: the four heading slots quoting their own banned names
(which printed "## Read these yourself"), and the reading list's model line
(which produced five entries out of five opening "Worth the hour if you
are"). Both were fixed where they were found.

**The third instance.** The closing slot of the same file, four hundred
lines below the second fix, read: `"3,558 papers read to get to these
five" is a fact about the product and earns its place.` A finished
sentence with a blank where a number goes, at the position where the
close gets written. The print of 2026-09-26 substituted the payload's
ingestion count and shipped "the library read 1,289 papers", which the
owner read and corrected. On that day 164 papers had ever been read in
full, out of 8,956 held.

**Why this one is worth an entry when the class already has one.** The
cost changed kind. The first two occurrences produced prose that read as
a catalogue, which is a craft failure a reader forgives. This one
produced a false statement about alexandria's own work, in the one
sentence of an issue that carries no link and cannot be checked by the
reader, and the email template promotes that exact line into its own
styled block. A register entry that records a class by its cheapest
instance will be read as being about prose.

**The cause, and it is not that a third example existed.** Both fixes
this morning were applied to the slot the specimen was found in. Neither
run read the rest of the file for the same shape, and the rest of the file
is where the third one was. A defect that is a property of a file's form,
which this one is, is not fixed by fixing its instances: the fix is a
pass over the whole file. That is L-A4 one level in, because the register
entry generalized correctly and the enforcement did not.

**What changes.** Ban list 56 stands as written. The enforcement changes:
when a tell is a property of the file's form rather than of one sentence,
the same run greps the whole file for the shape before it calls the fix
done. In this file that means every quoted English sentence sitting inside
a slot the model replaces. Fixed in this pull request for the closing slot,
with the specimen moved to the reading gate at the end of the file, where
finished output is read rather than written, per ban list 53's cure.

**Second finding, in the same shape and filed rather than fixed.** The
masthead carried the same false claim for the entire life of the product,
in `pipeline/weekly.py` as a string constant, and no editorial pass had
ever read it. Recorded as ban list 61. A reader-facing string in code is
exempt from every gate this org has, because the gates read what the model
writes. The owner gave this seat the masthead's wording on 2026-09-25 and
it is repaired in this pull request. The general rule is in the ban list
entry: every editorial run reads the reader-facing constants in code, and
every such constant carries a comment naming the register that governs it.

## INC-2026-09-26-grade-cleared-a-printed-violation — the editorial grade recorded a pass on a law the artifact visibly broke (2026-09-26, writer seat)

**What happened.** The rehearsal print of 2026-09-26, `press_rehearsals` id
1, carries `## Read these yourself` as its fourth heading. That string is one
of the four internal framework names, and printing one is the violation the
owner has flagged twice, in her words the second time "AGAIN", which is
incident 20 and canon law 12. The published 2026-W39 issue in the `digests`
table and the site reprint at `site/content/issues/2026-W39.md` both carry the
same heading on their own line 54.

Writer run 13 graded that print against all fourteen laws the same night. Its
verdict on law 12 reads "Fail, reprint. Pass, rehearsal, and the patch is
why." The rehearsal's heading is in the text. The grade cleared it.

**Why it matters more than the heading does.** The heading is a repeat of a
known violation and it is bad. The grade is worse, because the grade is the
instrument the owner is relying on so she does not have to be the editor. A
pass on a violation that is present in the artifact does not merely miss the
defect. It reports that the fix for that defect worked, which is the signal
that stops anyone looking again. Run 13's own words, "and the patch is why",
are a claim about a patch's effect derived from a misread of the output.

**Two causes, and the second is the reusable one.**

First, the run held two artifacts at once, the rehearsal print and the site
reprint, and graded the laws against both in one line each. A law with two
verdicts in one sentence is a law where an attribution error is invisible,
because both halves read as considered. Every other law that run graded
"Fail, both" or "Pass, both" was right.

Second, and this is the general form, no verdict in that review is checkable
without rereading the artifact. "Pass" is a word. The five counts in the
outsider pass were checkable, were checked, and were correct. The laws were
not, because a law's verdict carries a quoted line only when it fails. A pass
carries nothing, so a wrong pass looks exactly like a right one.

**Why this is a repeat.** Incident 32 records the pre-send quality gate
returning a pass on the issue the owner rejected. That was a tool and this is
a seat, and the shape is identical: a gate reporting a pass on an artifact
that fails, with nothing downstream able to tell the difference. L-A6 in
`docs/standards/lessons.md` says judge a run by its artifacts and never its
conclusion, and a grade is a conclusion.

**The fix, in this pull request.** A pass on a law that names a closed set of
strings cites the strings it checked and where it looked, the same way a fail
cites the line that failed. Applied to canon law 12 in the grading procedure:
the four names are grepped in the artifact and the grep is recorded, because
this is the one law in the canon that can be decided without judgment. Run
15's own grade of the same print does that and overturns the verdict.

**What is still open, and it belongs to the engineer.** The heading tripwire
naming those four strings was in the prompt that wrote the print. The slot
the heading is written into had already been cleared of the phrase. Both
in-model checks were correct, present and ineffective, so the string check
moves out of the model, and the ledger entry in this pull request specifies
it. The writer seat does not patch that gate a third time, per its charter's
structure watch.

## INC-2026-09-26-law-15-fixed-on-one-surface — the new law was applied to the sentence that produced it and left live on the home page (2026-09-26, writer seat)

**What happened.** Canon law 15 was written on 2026-09-26 from a print that
said "the library read 1,289 papers" over the ingestion count. The law says in
its own text that it binds every surface, naming the masthead, the email, the
site and any line of copy drafted under the canon. Writer run 14 repaired the
masthead the same night and filed the site's archived 2026-W39 line for the
frontend seat.

`site/app/page.jsx` line 49 prints `**{papersThisWeek}** papers read this
week`, and `weeklyIngestCount()` in `site/lib/metrics.js` reads the
`papers_ingested` field. Read at 2026-09-26 that is 4,243 papers arrived in
seven days, against 174 read in full in the life of the corpus and 55 read in
full this week. It is the same false sentence as the one the law was written
from, on the first screen a stranger sees, and it was live while the law was
being written.

**Why this is a repeat.** `INC-2026-09-26-fix-found-in-one-slot`, filed
earlier the same day, records a defect fixed twice in the slot where each
instance was found while a third instance sat elsewhere in the same file. This
is that incident one level out. The unit was a file then and it is a surface
now. Both times the run that generalized the defect correctly in the register
enforced it only where it had been standing.

**The cause.** A grep for the defect's own words would have found it in
seconds, and run 14 ran no such grep. The law's scope sentence names four
surfaces and the run read one of them, because the surface in front of it was
the one the dispatch was about. There is no charter step that turns a new law
into a sweep of the surfaces the law claims to bind.

**The fix, in this pull request.** Two parts. The repaired line is drafted in
`docs/voice/home-metric-line-2026-09-26.md` for the frontend seat to set, with
the count it needs specified in the ledger. And the general step: when a
writer run adds a law or a ban list entry, that run greps every reader-facing
surface for the defect's own words before it calls the fix done, which is
`pipeline/`, `site/` and the email templates, and reports what it found. A law
written from one sentence is not enforced until the surfaces it names have
been read. This run did that grep and this entry is what it returned.

## INC-2026-09-27-gate-unit-is-the-line — a ban list entry named a gate's defect and its fix, and the gate was not changed (2026-09-27, writer seat)

**This is a repeat of `INC-2026-09-25-tell-recorded-never-enforced`, recorded
at the moment it repeated, per the standing rule at the top of this file. The
seat is the same one, the register is the same one, and the entry that went
unenforced is the entry that diagnosed the machine.**

**What happened.** Ban list entry 46 was appended on 2026-09-24 by the grade
that found it. It names the label welded to the front of a sentence, lists six
specimens, and then does something a ban list entry rarely does. It names the
gate that should have caught them and says precisely why the gate could not:

> The gate missed them because it collects lines beginning with `#` and runs of
> bold or italic sitting alone, and a label welded to the front of a sentence
> sits alone in none of those ways.

The collection step in `prompts/digest.md` on 2026-09-27 is word for word what
that sentence describes. Three days, three editorial runs and eleven patches to
that file later, the step is unchanged. Two labels of exactly this shape are
live on the published 2026-W39, and neither is among entry 46's six: "For
builders:" and "The procedure is extractable:". A third, "**The number that
matters:**", is entry 51's own specimen.

**Why the gate could not catch it, which is the transferable part.** The gate's
question is correct. "Could this exact line sit over a different day's items
without changing a word?" rejects all three labels on sight. The gate never
asks it of them, because its unit of inspection is a line and a label is a
fragment of a line. Asked of the whole of "For builders: sequential
specialization is not free", the honest answer is no, that line is about
today's material, so it passes. The half that would have failed is never held
up on its own.

That is a defect of a shape worth naming for every gate in the org, not only
this one. **A gate has a question and a unit, and reviewing the question tells
you nothing about the unit.** Every run that read this gate read a question
that was getting sharper each time, and a correct question applied to the wrong
unit returns a pass forever. The four disguises the gate lists are all
line-shaped, so each rewrite widened the question inside a collection step that
could not reach the new shape.

**Why entry 46 went unenforced, and it is not carelessness.** The standing rule
in `ban-list.md`, that an entry ends in the change to `prompts/digest.md` that
enforces it or in the ledger entry saying why none can, was written on
2026-09-25 by the incident this one repeats. Entry 46 was written on 2026-09-24.
The rule binds new entries, so nothing ever asked whether entry 46 had landed,
and entries 1 to 50 have never been swept. The register that was fixed kept its
backlog.

Entry 51 shows the second way this fails. Its ending says "Enforced
2026-09-25", and that is true. The enforcement went into the
internal-vocabulary test, which sits in the traction section's guidance, is
advice to the writer composing a line, and has no reach over finished output.
The gate that reads finished output still could not see the string. **An
enforcement ending that names a place in the file rather than the gate the
defect would pass through is a note wearing a fix's clothes.**

**The fix, in this pull request.**

- `prompts/digest.md`: the heading gate takes the text in front of any colon as
  its own unit of inspection and puts the question to that fragment rather than
  to the line around it.
- Entry 46 gains its enforcement ending. Entry 51's ending is corrected to say
  which change reaches the gate.
- Ledger entry for this seat: sweep ban list entries 1 to 50 for enforcement
  endings, which is the backlog the 2026-09-25 rule does not cover.

**What is still open, for the ExO.** Two questions this entry raises and this
seat cannot answer. Does every other gate in the org have a unit that nobody
has reviewed, the way this one did? And do the other registers in
`docs/agents/registers.md` carry the same pre-rule backlog, where a standing
rule about endings binds entries written after the rule and leaves everything
before it unchecked?

## INC-2026-09-27-law-15-live-in-the-archive — the masthead was corrected in code and the false claim is still the second line a visitor reads (2026-09-27, writer seat)

**This is a repeat of `INC-2026-09-26-law-15-fixed-on-one-surface`, and the
third occurrence of law 15 being repaired on one surface while a live one keeps
the claim. Recorded per the standing rule.**

**What happened.** Run 14 cut the false reading claim from `MASTHEAD` in
`pipeline/weekly.py` on 2026-09-26. On 2026-09-27 the only published issue,
`site/content/issues/2026-W39.md` and the byte-identical body of `digests` row
18, still opens on it:

```
*The latest in AI research, read in full and distilled weekly: what's new,
what's gaining acceptance, and what newer evidence has overturned.*
```

2026-W37 is hidden, so that is the whole public archive.

**Why the fix does not reach it, and this cause is new.** The two earlier
occurrences were the same string standing in more than one place, and the fix
for those is a grep. This one is not a second copy of the string. `add_masthead`
splices the constant into the body before the body is stored, so the sentence is
baked into the artifact at write time rather than composed when a page renders,
and `site/lib/content.js` serves the stored body whole from either the markdown
fixture or Neon. Changing the constant governs the next issue and cannot reach
one that already exists. **A reader-facing string that joins its artifact before
storage passes out of the reach of every later correction.** Every issue keeps
the masthead it was printed with, permanently, and the archive is designed to
grow.

**The step added yesterday is what found this, and that is worth recording as
plainly as the failure.** `INC-2026-09-26-law-15-fixed-on-one-surface` ends by
requiring a writer run that adds a law or a ban list entry to grep `pipeline/`,
`site/` and the email templates for the defect's own words before calling the
fix done. This run ran that grep for "distilled weekly" and the archive file is
what came back. The step works. What it does not yet cover is the difference
between a surface that can be corrected by editing code and a surface that
holds a copy no edit can reach, and that distinction is the new finding rather
than the grep.

**Not fixed here, and the boundary is why.** The stored bodies are the
pipeline's and the page is the frontend seat's, and altering an issue that has
already been sent to subscribers is the owner's call rather than a seat's.
Filed in `docs/ideas.md` with both repairs stated: correct the stored bodies, or
stop baking the line in and compose it when a page renders. The second is the
one that stops this recurring.

**One inherited boundary crossing, flagged rather than reverted.** Run 14's
correction to `MASTHEAD` is a writer-seat edit to `pipeline/weekly.py`, and the
writer charter's boundary list says never pipeline code. That commit is in this
branch because this branch builds on it. Reverting it would restore a false
claim about the product in order to satisfy a boundary, so it stands and the
call is the owner's. The ledger entry above is where the correction would
arrive through the engineer instead.

## INC-2026-09-28-test-commissioned-the-banned-sentence — the struck opening printed a third time, out of a test list at the bottom of the slot that forbade it (2026-09-28, writer seat)

**This is a repeat of `INC-2026-09-26-example-supplies-the-frame` and the third
occurrence of one sentence shape the owner struck personally. Recorded per the
standing rule.**

**What happened.** `digests` row 18, written 2026-09-28 09:01:28 UTC by
`kimi-k2.6` at prompt `ea2d678d86e9`, opens:

```
You have spent the week watching agents get faster by thinking less at test time.
```

The history of that sentence. The owner struck "You spent last week watching
agents get faster by doing less at test time" on 2026-09-24 with the words
"dont assume readers read each issue", which became canon law 13. On 2026-09-26
the generator produced "You have spent the week watching the field argue about
whether agents need a heavy harness at deployment", which became the 2026-09-25
tightening of law 13 into a grammar rule, ban list 55, and
`INC-2026-09-26-example-supplies-the-frame`. This morning is the third, and the
first to be stored rather than caught in rehearsal.

**Why it printed, and the cause is new.** The two earlier occurrences were
diagnosed as a banned specimen quoted at the position where the line gets
written, and the fix was to move every specimen to the gate at the end of the
file. That fix held. No specimen is in the opening slot.

The opening slot ends on a list of tests the opening has to pass, and one of
them read:

```
the greeting sounds like a person who knows what the reader's week has been like
```

Two hundred lines above it, in the same slot, sits a hard rule with no
exceptions: never a past-tense verb with "you" as its subject. **A prohibition
is read as law and a test is read as the assignment, and the assignment was at
the bottom of the slot, which is the position writing gets done from.** Asked
for the reader's week, the only honest source for that noun is the reader's
past, so the greeting came back as a report on what they had been doing.

**The general form, for the ExO.** The three prior fixes in this chain all
asked what a prompt FORBIDS and where the forbidden thing is quoted. None asked
what it ASKS FOR. A file can forbid a shape in one paragraph and commission it
in another, and the commissioning paragraph wins, because it is the brief and
because position decides. **Auditing a prompt means reading its imperatives and
its success criteria against its prohibitions, and the check is whether any two
of them can both be satisfied.** This generalizes past prompts: any instruction
set with a rules section and an acceptance-criteria section can contradict
itself across the two, and the acceptance criteria are what the work aims at.

**The deeper cause, found after merging main, and it is the company standard
that arrived the same morning.** The opening slot also carried two quoted
specimens six lines apart: the owner's struck sentence, and the canon's repair
for it. Both verbatim, both at the position where the opening gets written. The
print spliced them. The subject and tense came from the struck sentence, and
"thinking less", "That trick has a ceiling" and "This week the field went
after" all came from the repair, the last two word for word. Not one clause of
that opening was written about the day's news.

`L-A23` in `docs/standards/lessons.md`, which landed on main in the HQ sync of
2026-09-28 (#128), states it exactly: read the instruction from the position of
whoever obeys it, and if the nearest quoted example at that position is the
thing being banned, the prohibition is a supply. The standard and its sharpest
local specimen arrived on the same day. **A negative example beside a positive
example, at the position of writing, is a menu.** Ban list 71.

**Fixed in this PR.** The test now says the reader's JOB, which is knowable
from where the generator sits. Both quotations left the opening slot: the
struck sentence joined the two already held at the stands-alone gate, and the
repair was rewritten about a subject no payload will hand the model. Ban list
65 carries the test tell and 71 carries the menu.

**This run committed the same failure in its own patches, and that is worth
recording.** The first pass at fixing the greeting quoted the banned sentence
inside the greeting slot. Four other patches did the same with their own
specimens. They were caught only because merging main brought L-A23 in and the
run applied it to itself before shipping. Four previous runs of this seat wrote
patches to this file without that standard available. **A seat's own output
needs the check it is writing into the generator**, and the cheap version of
that is one question at ship time: for every specimen this run quoted, is it at
a position where something gets written, or at a position where output gets
read?

## INC-2026-09-28-repair-written-never-deployed — four days of editorial fixes sat in open pull requests while the cron printed daily without them (2026-09-28, writer seat)

**This is a repeat of the law 15 chain, `INC-2026-09-26-law-15-fixed-on-one-surface`
and `INC-2026-09-27-law-15-live-in-the-archive`, and the fourth occurrence of a
correction that does not reach the artifact a reader gets. Recorded per the
standing rule.**

**What happened.** The false reading claim was cut from `MASTHEAD` in
`pipeline/weekly.py` on 2026-09-26. This morning's run wrote a brand new row,
and its second line is:

```
*The latest in AI research, read in full and distilled weekly: what's new,
what's gaining acceptance, and what newer evidence has overturned.*
```

`origin/main` still holds the uncorrected constant. The corrected one exists
only on `writer/2026-09-26-b` and the branches stacked on it. The cron runs from
main.

**How far this reaches, traced.** Five of the defects graded in
`docs/voice/reviews/2026-09-28.md` have a written repair that has never run:
the tense of the opening (law 13), the masthead (law 15), 44.3% against 30%
(ban list 63), "Worth the hour if you are" on every reading-list entry (ban
list 44), and the reading list's generic heading (ban list 62). All five were
fixed on 2026-09-26 or 2026-09-27. All five printed this morning.

**Why, and this cause is different from the three before it.** The earlier
occurrences were about where a string lives: a second copy that a grep would
find, then a constant baked into an artifact before storage. This one is not
about the code at all. **The repair was correct, complete and reviewed, and it
was on a branch.** `#107`, `#112`, `#119` and `#126` are all open, in a stack,
oldest for two days.

The writer seat writes every editorial repair and cannot deploy one. Its
charter forbids merging its own pull request, correctly. So the interval between
a fix being written and a fix taking effect is set by an owner review, it is
unbounded, and a daily cron prints into that interval. Ban list 64 named a fix
that reaches only what prints next. This morning it did not reach that either.

**The general form, for the ExO.** Every seat that writes a repair it cannot
deploy has this gap, and the org measures the writing rather than the
deploying. A fix is not a fix until the thing that runs has it. Two candidate
gates, both outside this seat: the press send could refuse when the deployed
`prompt_sha` does not match the prompt on main, which turns an undeployed fix
into a loud failure instead of a quiet daily cost. And an editorial fix to a
generator could merge on a faster gate than a full owner review, since the
owner's gate exists to protect her voice and these diffs are enforcement of
rulings she has already given. Filed in `docs/ideas.md` for the owner and the
engineer.

**The registers drifted with the prompt, and that is the part the company
standard already had a rule for.** `docs/standards/lessons.md` L-A18: a rule
cites only records reachable where it says they are, and a citation pointing
into an unmerged branch reads as evidence and is not one. On `origin/main` the
ban list ends at entry 54 and `docs/voice/canon.md` has no law 15. Law 15 is the
law this morning's masthead breaks. Entries 55 to 64 do not exist. Every
citation of them anywhere in this org, including in the charter checks that are
supposed to gate a run, points into a branch.

**Owed to HQ under L-A11.** L-A18's own evidence is HQ's register citing an
entry "still sitting in unmerged HQ PR #15", which is this defect in the parent.
L-A11 says a defect appearing in a second product belongs to HQ rather than
being fixed per product. This is the second product and the fix is owed upward.
Filed in `docs/ideas.md` for the ExO seat to carry into
`docs/agents/hq-relay.md`, which that seat owns and this one does not (L-A10).

**Not fixed in this PR, because no change to `prompts/digest.md` reaches it.**
Recorded, traced, and filed. This pull request supersedes all four open writer
branches so that one merge deploys four days of repairs and four days of
registers together.

## INC-2026-09-29-grade-cleared-link-coverage — a second editorial grade cleared a law the artifact visibly broke, and the law was the owner's own "you didn't show me the paper" (2026-09-29, writer seat)

**This is a repeat of `INC-2026-09-26-grade-cleared-a-printed-violation`,
recorded at the moment it repeated, per the standing rule at the top of this
file. Same seat, same register, same shape: a pass reported on an artifact
that fails.**

**What happened.** Writer run 17 graded `digests` id 18 on 2026-09-28 and
recorded, verbatim:

> **Law 8, links reach the full text. PASS.** Four distinct URLs, all
> `arxiv.org/html/`, no abstract landing pages.

Every word of that is true. The issue has five items. Its fell-behind section
names three separate pieces of research, the 82.2% RMBench reference
implementation, MaP-WAM at 83.3% and DRG-MAPPO at 87%, and carries no link to
any of them. Its second item links the newer paper and not the older claim it
replaces, where the generator requires both. Two of the six link instances in
the issue are the reading list reprinting links from sections one and two.

The same grade recorded canon law 6's presence half as a pass on "all three
items". There are five. The two in the fell-behind section carry no evidence
grade, and they carry three benchmark numbers between them.

**Why the verdict came out wrong, which is the reusable part.** The canon
requires every verdict to carry a quoted line as evidence. That requirement is
right and it has a blind spot nobody had named: **it steers a grade toward the
laws that can produce a quotation.** Law 8 and law 6 both forbid an absence.
An absence cannot be quoted. So the grade did the only thing quotation allows,
which is to inspect the links that exist, and inspecting what exists is
exactly the check that cannot find what is missing.

The first occurrence had a different cause, two artifacts sharing one verdict
line, and its fix was to make a pass carry evidence. This occurrence is what
that fix does not reach. A pass with evidence is still a reading, and coverage
is arithmetic.

**Why it matters.** Law 8 is the owner's ruling of 2026-09-19 in her own
words, "you didn't show me the paper". It failed on the fell-behind section,
which the canon calls the product's only real difference from every other
newsletter, and the instrument she relies on so she does not have to be the
editor reported it clean. A grade that clears a law does not merely miss the
defect. It reports that the generator is fine on that axis, which is what
stops the next run from looking.

**The fix, in this pull request.** Two halves and only the first is this
seat's to build.

In the canon's grading procedure: a law whose subject is "every item" or
"every issue" is graded by a count, with the command written down, never by a
reading. A pass on one of those with no number beside it has not been graded.
This is the same escalation the first occurrence applied to canon law 12,
which is graded by a grep, extended from the one law that names a closed set
of strings to the class of laws that assert coverage.

In `prompts/digest.md`: the link count and the grade count now run off one
shared list, which is every named piece of work in the finished issue rather
than every item. Recorded as ban list 72, 73 and 74.

**What is still open, and it belongs to the engineer.** Both counts are
arithmetic and both are therefore `L-A22` cases: enforced at the reliability
of a model reading a file when they could be links in the pre-send gate's
`&&` chain. Filed in `docs/ideas.md` against #60, beside the four run 17
filed there for the same reason. This seat has now written the same class of
check into the same prompt twice and does not get a third.

## INC-2026-09-29-gate-unit-three-more — the defect that produced one incident produced three more in a single print (2026-09-29, writer seat)

**This is a repeat of `INC-2026-09-27-gate-unit-is-the-line`, recorded at the
moment it repeated, per the standing rule at the top of this file.**

**What happened.** That incident found the heading gate in
`prompts/digest.md` asking the right question of the wrong unit: it collected
lines, and a label welded to the front of a sentence is a fragment of a line,
so the gate's own question was never put to the half that would have failed
it. The fix worked. The four framework names did not print on 2026-09-28 and
the fragment half of the gate caught what it was written for.

Grading that same print on 2026-09-29 turned up three more gates in the same
file with the identical defect, all three reporting a pass:

| Gate | Unit it inspects | Unit the defect lives in | What got through |
|---|---|---|---|
| Link coverage | the item | the named piece of work | one item naming three results, no link on any |
| The kind test | "the two claims" | one old claim against several new | one refusal written over two pairings, the valid one discarded |
| Reading-list overlap | the `new_claims` stream | any section of the issue | a pick covered in the traction section, recommended back |

**The transferable finding, which is why this is worth an entry rather than
three more ban-list lines.** The pattern is not in any of the four gates. It
is in how a gate gets written in this file. A gate is written from the
specimen that produced it, the specimen is always one instance, and the check
comes out phrased in the singular: "the item", "the two claims", "the stream",
"the line". The material arrives in groups. Every one of these gates then
passes on the group by answering for one member of it, and a pass is
indistinguishable from a real one, which is `L-A21` exactly.

So the question to put to every gate in that file, and to every gate any seat
writes: **name the unit this check inspects, then name the unit the defect
lives in, and say whether they are the same size.** Where the check is
singular and the material is plural, the gate will pass on the group. That
question is cheap, it is answerable without running anything, and it found
three live failures in one pass.

**The fix, in this pull request.** All three gates now name their unit
explicitly, and the two that are arithmetic count off one shared list. Ban
list 72 carries the tell.

**What is still open.** The charter's structure watch says that when the same
structural fix fails twice through prompt changes alone, the pipeline change
goes in the ledger instead of a third patch. Four gates, four prompt patches,
and the fourth is in this pull request. The ledger entry filed against #60 is
not another patch: it is the unit question above, as a standing check on the
pre-send gate, plus the two counts that are arithmetic. The writer seat does
not patch this class a fifth time.

## INC-2026-09-29-dispatch-403-repeat — the PM's dispatch call 403s a second time, five days after the first (PM seat)

**Recorded under the standing rule at the top of this file**: any issue
occurring more than once is always recorded at the moment it repeats,
no exceptions. `INC-2026-09-24-dispatch-403` is the first occurrence.
This is the second, not a rediscovery of the same open question.

**What happened.** Today's standup (`pm/standup-2026-09-29`) found a
well-evidenced trigger for the skill seat (its own Tuesday cron never
fired; sprint item 4 was ready and unblocked) and both charter §5
conditions held: `PM_DISPATCH_ENABLED` was `true`, and no
`workflow_dispatch` had fired in the prior two hours. The run attempted
to fire it for real, the same way the 2026-09-24 run did:

```
gh workflow run agent-skill.yml -f owner_instructions='...'
could not create workflow dispatch event: HTTP 403: Resource not
accessible by integration
(https://api.github.com/repos/alexandrapaiz/alexandria/actions/workflows/361031512/dispatches)
```

Identical failure shape to the first occurrence: same message, same
"Resource not accessible by integration" reason, against a different
workflow id (skill's, not market's), five days later, on
`.github/workflows/agent-pm.yml` unchanged in its `permissions:` block
since then (`actions: write` is still present, confirmed this run).

**What this means for the standing question.** The first entry left
open whether `github.token` inside this harness's execution path
actually carries the `actions: write` scope the workflow YAML requests,
or resolves to something narrower. Nothing between 2026-09-24 and today
answered that question in this file, in `docs/decisions.md`, or in any
PR this seat could find (`git log` on `.github/workflows/agent-pm.yml`
shows no permissions change in the window). A second identical failure,
five days apart, with the permissions block unchanged, is evidence
against "transient" and toward "structural": whatever gap ADR-033's
probe did not catch is still there.

**What this run did instead of pretending it worked.** The dispatch is
recorded as attempted, not fired, in `docs/sprints/dispatch-queue.md`,
with the exact 403 and the command the owner or chair can run by hand
(their own token would not hit this integration-scope wall). No run URL
exists because no run was created.

**Standing question, now overdue.** The same one the first entry left
for the ExO or engineer: confirm what `github.token` actually resolves
to inside this harness's execution path, and whether it differs from a
plain Actions runner token. Two occurrences five days apart with no
progress on that question is itself worth a line for the ExO's weekly
pattern read, separate from the technical question.

## INC-2026-09-27-post-run-step-audited-from-inside — the runtime audit that cleared a broken step, from inside the run the step was breaking (2026-09-27, ExO seat)

**This is a postmortem about the postmortem practice, which is this
seat's lane (charter §6), and not a rediagnosis.** The technical fault is
fully and correctly diagnosed in `INC-2026-09-26-run-report-dash-echo`,
filed by the engineer seat within hours, down to `/bin/sh` being a
symlink to dash in `ghcr.io/alexandrapaiz/alexandria-agent` and dash's
builtin `echo` expanding the backslash escapes inside a JSON string. This
seat reproduced that mechanism independently before reading the entry and
got the same error text at the same line number. There is nothing to add
to it.

What is worth recording is the entry before it.

### The count, per §2b

Five scheduled `engineer-agent` runs failed at the `Post run report`
step between 2026-09-26T01:26Z and 2026-09-27T15:36Z: 36208446311,
36208644267, 36250253554, 36285149176, 36330209631. Every one shipped
its work first, so five pull requests exist (#115, #116, #118, #120,
#122) and nothing was lost. Ship-first has now preserved the work in
every failure this register has recorded since incident 3.

The blast radius is the two containerised seats and only those. The
engineer and the frontend run in `container:` and get `sh -e {0}`, and
the other ten run on the host and get `bash -e {0}`, where the same
`echo` is harmless. The frontend seat has not run on a schedule since the change
landed, so it is the next one to fail and it has not failed yet.

### What this entry is actually about

`INC-2026-09-26-slack-report-step-no-smoke-run` is a careful, correct
governance finding: twelve live workflows changed on main twice in ten
minutes, no pull request, no smoke run. It asks the two questions
`runtime-changes.md` prescribes, answers both with evidence, and then
concludes, in bold:

> **It is working.**

It was not working. It had already failed twice, and the two runs it had
failed were the two runs that wrote that sentence. The seat corrected
itself in a second entry the same night, which is the practice working.
But the wrong verdict is the interesting part, because the reasoning
behind it was sound and would be sound again.

### Why a correct method produced a false clearance

The evidence for "it is working" was `okr-agent 36207911573 concluded
success`, a real run, three minutes after the change, read correctly.
That run is on the host. It could never have exercised the fault.

And the run doing the auditing could not observe itself, for a
structural reason rather than a careless one. **`Post run report` is a
post-run step.** It executes after the seat's agent step has finished, so
at the moment any seat writes its verdict, the step it is judging has
not run in its own job and cannot have. `job.status` read `success` in
the log of the very run that then failed. A seat auditing a post-run step
from inside a run is reading a value that is structurally premature.

So the general form, and it is the kind that recurs:

> **A change to machinery that runs after a seat's work cannot be
> cleared by the seat's own run. Its verdict comes from `gh run view` on
> a job that has already concluded, and from a job of the same kind as
> the one at risk.**

Two clauses, and the second matters as much as the first. Reading a
completed run is not enough if it is the wrong runtime: ten of twelve
workflows would have cleared this change forever.

### The fix, and where it goes

Both halves are now in `docs/agents/runtime-changes.md`, which is the law
both charters' §2 and §0 execute, under "Clearing a change is itself a
claim, so name the run that cleared it". That file is under
`docs/agents/`, which is this seat's writable surface, so it is applied
rather than queued. It carries the `grep -l "container:"` line that tells
a reader which runtimes a change actually reaches, because the shell split
is the part nobody knew.

The fix for the fault itself is `tools/run_report.py` on the engineer's
branch plus one workflow edit, and it is blocked on a hand, which is the
finding underneath all of this and the reason the queue page grew a
second lane in the same pull request as this entry.

### What the org should take from it, blamelessly

Nobody skipped a step. The owner made a small improvement to twelve files
because Slack was quiet, and it was written defensively: the webhook
guard is inside the script with a correct comment about why, and the
`curl` ends in `|| true`. The engineer's §0 check caught the governance
gap within hours and the fault within hours of that. The weekly audit
found neither first and was not supposed to.

The one thing that failed was a verdict, written in bold, on evidence
that could not support it. The lesson is small and cheap: **when you
clear a runtime change, say which run and which runtime cleared it.** The
sentence "it is working" with no job id beside it of the right kind is
the sentence to stop writing.

## INC-2026-09-30-engineer-run-twice-again

**A repeat, recorded because the standing rule at the top of this file has no
exceptions.** This is INC-2026-09-26-engineer-run-twice-in-one-window happening
again, four days later, with the queued fix still unapplied.

**What happened.** Two engineer-agent runs were alive at the same moment on
2026-09-30: a `workflow_dispatch` at 01:58:40Z carrying the owner's ADR-36
directive, and the ordinary `schedule` at 02:00:00Z carrying nothing. `gh run
list` shows both `in_progress`. Two skill-agent runs were also alive in the same
window, one dispatched at 01:58:42Z and one that had run at 17:08 the previous
evening, though only one of those was live.

**Why it is the same incident.** `docs/agents/pending-workflow-changes.md` item
9 is the fix. It is a four-line `concurrency:` block per seat workflow, with
`cancel-in-progress: false` so the second run queues rather than dies, and it
was queued on 2026-09-26 by the engineer seat with this exact failure as its
evidence. No seat's token can push a file under `.github/workflows/`, so it has
sat waiting for a hand for four days. The guardrails that do exist are all one
layer above the runtime: the PM's charter forbids dispatching into a seat with
an open pull request, and neither of these dispatches was the PM's.

**What it cost this time.** Less than last time, and the reason is worth
recording. The dispatched run branched from `origin/main` under a slug naming
its own work (`engineer/2026-09-30-skill-registrar-and-evals`) and opened its
draft pull request in its first few turns, so the two runs could not land on one
branch. What they can still collide on is `docs/ideas.md`, which both append to
at the same anchor, and that is incident 6 exactly. The dispatched run names the
expected merge order in its pull request, which is the charter's mitigation and
not a fix.

**What would actually fix it.** Item 9, applied. Nothing else in the repository
can, and this seat cannot apply it.

**One thing the owner should know that is not in item 9.** A dispatch and a cron
firing ninety seconds apart is not a coincidence: the owner dispatches when she
has a directive, and the directive usually arrives shortly before the daily
cron. So the two-runs case is the normal case on any day she dispatches, rather
than an unlucky one, and the concurrency block is worth more than its evidence
count suggests.

## INC-2026-09-30-conflict-markers-merged-to-main

**Unresolved merge conflict markers were committed to `main`** in
`docs/agents/registers.md`, and `checks` has been red on `main` since
2026-09-30T01:43Z as a result.

**What was in the file.** Three conflicts. Two were single table rows, where
both sides described the same register at different dates. The third spanned 176
lines and held two whole sections appended by two different runs, `## The
gate-3 row, corrected (engineer seat, 2026-09-26)` and `## The 2026-09-27
sweep`, with neither of them lost and neither of them readable.

**Why this one is worse than an ordinary red build.** The file is the org's map
of which register has a gate that fires before something ships, and the rule it
serves is the one every charter's ship check points at. So the artifact that
tells twelve seats what to read before shipping was itself unreadable, at the
exact place where the reading happens. Incident 20 is the ruling written into
the right register and violated by the next artifact anyway because nothing
opened the file. This is the same failure one layer down: the file was open and
said `<<<<<<< HEAD`.

**How it was resolved.** Twice, independently, by the two engineer runs of
2026-09-30, and they agreed. Row one: `main`'s side, which is newer and a strict
superset of the other, adding three rows. Row two: `main`'s newer cell kept its
text, and the other side's distinct fact, that `agent-pm.yml` carries no
`NEON_RO_URL`, was carried into it rather than dropped, since a table holds one
row per file. Conflict three: both sections kept, oldest first, because they are
additive and were never in conflict in any sense but the textual one. Nothing was
deleted.

That both runs reached the same three answers from the same evidence is the one
cheerful line in this entry. What it cost is the point: the same work twice, and
a fourth conflict in the making, since two PRs resolving one conflict differently
is a conflict on the second merge. PR #141 therefore took PR #142's version of
this file byte for byte, verified by `git hash-object`, so the two merge in
either order with nothing to resolve. That is the standing resolution for this
class and it is cheaper than either run's prose about it: when two seats fix one
file, the second one adopts the first's bytes rather than its own.

**The systemic half.** A repository whose tests can detect this already did:
`tests/test_check_registers.py` fails on a conflict marker and has for some
time. It runs in `pytest tests/`, and `pytest tests/` is not a step in
`checks.yml`; the workflow runs eleven named test files and this is not one of
them. So the guard existed, was correct, and was not wired to anything that runs
on a merge. That is this org's most repeated shape, and it is the same sentence
as PR #110 sitting merged and inert and as incident 24.

## INC-2026-09-30-two-checks-steps-red-on-main-for-days

**Two steps of `checks.yml` were failing on `main` and neither was a code
defect.** Both were tests asserting behaviour the organization had deliberately
changed, which is the failure mode where a red build teaches nobody anything
because everyone already knows it is red.

**The press's backoff.** `tests/test_press_resilience.py` asserted
`slept == [1.0, 1.0]` under a provider answering `retry-after: 1` twice. The
press was corrected on 2026-09-24 to treat `retry-after` as a floor and wait 30
then 60 seconds, because Moonshot answers a concurrency refusal with
`retry-after: 1`, the other call takes minutes, and a press that honours the
header burns every retry in three seconds. That is failure 2 of
INC-2026-09-24-press-provider-migration. The code is right, the test was left
behind, and the step has been red since.

**The run report's stdout.** `tests/test_run_report.py` parsed the whole of
stdout as JSON. `tools/run_report.py` prints `::warning::` lines to stdout on
purpose, because that is where GitHub Actions reads annotations, and it warns
when `gh pr list` refuses. `checks.yml` passes no `GH_TOKEN`, so `gh` always
refuses there, so the warning always landed in front of the JSON. The test
passed on every machine holding a token and failed in the only place it ran.

**Both fixed in PR #142**, the scheduled engineer run of the same day, which
found them independently and fixed the run report at the tool rather than at the
test: `tools/run_report.py` now prints `::warning::` to stderr, so `--dry-run`
keeps its promise that stdout is the payload. PR #141, the dispatched run, had
written a weaker fix on the test side and replaced it with #142's, byte for byte,
for the reason the entry above gives. Every step of `checks.yml` now passes
locally, run the way the workflow runs it and with `GH_TOKEN` unset: 613 passed,
1 skipped.

**The lesson is about who reads a red build.** `checks.yml` went live on
2026-09-29 and its first two runs on `main` were red. A workflow that is red on
its first day is indistinguishable from a workflow that is red forever, and the
only seat positioned to notice is the one that runs daily. Worth a guardrail:
the engineer seat's §0 machinery check reads `git log` over `.github/` and
`pipeline/`, and it should also read `gh run list --workflow=checks.yml
--branch=main`, because a merged workflow that fails is a runtime change that
announced itself and nobody answered.

## INC-2026-09-30-check-harness-green-under-pytest

**Two test files reported 130 assertions to nobody, and the repository's own
test command said green.** This is the mechanism behind the entry directly
above, not a second instance of it, and it is the reason that entry's two
defects sat on `main` for days with no one noticing.

`tests/test_press_resilience.py` and `tests/test_press_rehearsal.py` predate
pytest's presence here. Each carries its own harness: a module-level `FAILURES`
list, a `check(name, condition, detail)` that appends to it and prints either
`ok` or `FAIL`, and an `if __name__ == "__main__"` block that exits 1 when the
list is not empty. `.github/workflows/checks.yml` runs both as scripts, so CI
reads the exit code and the pattern does what it was built to do.

Under `python3 -m pytest tests/ -q` it does nothing at all. pytest never runs
`__main__`, nothing else reads `FAILURES`, and a test function that calls
`check()` and returns normally is a test function that passed. Every failure
prints `FAIL` to a stdout that `-q` swallows. That command is the one
`requirements-dev.txt` prescribes in its own comment and the one both files'
docstrings name.

**Proved rather than argued, on the branch of this entry's PR, with tiktoken
made unavailable:**

```
before the fix:  15 passed
after the fix:   1 check() failure(s) in test_the_press_fits_its_primary_at_full_caps
                   - the cost is in the range ADR-32 budgeted: $0.1628 an issue
                 1 failed, 14 passed
```

**Why it is a repeat, twice over.** The entry above records
`test_call_model_walks_and_backs_off` asserting a contract the press stopped
honouring on 2026-09-24. The only reason that was ever found is that
`checks.yml` happens to run its file as a script. Nobody running the repository's
own test command, on any day in those six, would have seen it. And the specific
check surfaced by the proof above is
`INC-2026-09-25-budget-guard-estimates` recurring in a second file: `count_tokens`
falls back to a pessimistic chars-per-token ratio when tiktoken is missing, so
the same request reads $0.1628 estimated and $0.1376 exact, and this check
compared whichever it got against a hard ceiling of 0.15. `pipeline/budget.py`
learned that on 2026-09-25 and separates its estimated findings from its exact
ones. The lesson was recorded in the code that produced it and nowhere else,
which is incident 20's shape: the register was written and the next artifact
never opened it.

**Fixed in this PR.** A hook in `tests/conftest.py` enforces `FAILURES` for any
test module that owns one, snapshotted per test so a failure is attributed to
the test that produced it, and leaving a raising test its own traceback.
`tests/test_check_helper_is_enforced.py` proves the hook by running pytest in a
subprocess against throwaway modules using the pattern: 6 passed, and 2 failed
with the hook deleted from `conftest.py`. The cost check now labels an estimate
`ESTIMATED` and declines to compare it, the way `budget.py` already did. Script
mode is untouched, because a conftest is not imported when a file runs directly.

**One finding this run could not fix, and it is the larger half.**
`checks.yml` names fourteen test files in its `paths` lists and no workflow in
this repository runs the whole suite. `tests/conftest.py` is in neither list, so
a change to the file that installs the Modal stub for every test module here
triggers no check at all. That file's own docstring records what a bad version
of it costs: the whole suite collecting zero tests and reporting one error. The
engineer seat cannot push a workflow file, so the edit is queued as item 13 in
`docs/agents/pending-workflow-changes.md` with both anchors verified.

**The lesson, blamelessly.** Every gate in this organization is asked whether it
passes. Almost none are asked whether they can still fail. These two files were
green for a reason that had nothing to do with the code they test, and a green
harness is indistinguishable from a working one from the outside, which is
exactly why `tests/test_check_helper_is_enforced.py` runs pytest rather than
reading the hook. The generalizable rule: a test harness that reports through
anything other than an exception needs a test that deletes the reporting path
and confirms red. Where the org has gates, it should keep a short list of which
ones have ever been observed failing on purpose.

**The guardrail the entry above proposed, executed.** That entry asks that the
engineer seat's §0 machinery check also read
`gh run list --workflow=checks.yml --branch=main`. This run did, before writing
any code, and it is what established the position: five consecutive failures on
`main` and green on this branch. Worth putting in the charter, which is the
owner's file, so it is a ledger entry rather than an edit here.

## INC-2026-09-30-dispatch-lost-with-no-model-call — incident 23's fingerprint on the Claude path, where its own diagnostic says to stop looking (2026-09-30, engineer seat)

**A repeat, recorded because the standing rule at the top of this file has no
exceptions.** Incident 23 wrote the fingerprint down so the next diagnosis
would be a lookup. It happened again on 2026-09-30, the lookup was run, and it
returned the wrong answer, because the one discriminator the entry gives is the
model name and this time the model name was a Claude model.

**What happened.** Engineer run 36667082941, a `workflow_dispatch` created
2026-09-30T04:02:26Z carrying the owner's ADR-37 directive on self-maintaining
skills. The result block:

```
"type": "result", "subtype": "success", "is_error": true,
"duration_ms": 435, "num_turns": 1, "total_cost_usd": 0,
"permission_denials_count": 0, "modelUsage": {}
```

with `"model": "claude-opus-5"` in the init line four hundred milliseconds
earlier. No commit, no branch, no pull request, and no model ever answered. The
owner's directive was silently dropped. Nothing reported it for thirteen hours,
until this run's machinery check read `gh run list` for its own seat.

**Why the register did not answer it.** Incident 23's fingerprint section ends
with a diagnostic command and this instruction: "If the model name is not a
Claude model and `modelUsage` is `{}`, the seat's problem is its endpoint and
not its charter." The condition is an `and`, and half of it is false here, so
the entry that describes this exact failure hands the reader nothing. The
generalizable defect is in the entry rather than in the runtime: **a fingerprint
written from one specimen encodes that specimen's cause as part of its
identity.** `modelUsage: {}` is the fingerprint. Open routing was the cause of
the one instance that produced it. Recording them as one fact makes the second
instance unrecognisable.

That is the same shape as `INC-2026-09-29-gate-unit-three-more`: a check phrased
from a single example, which then answers for the example instead of the class.

**The duration is the new discriminator, and it points somewhere else.**
Incident 23's instance ran 190 seconds before failing, which it correctly reads
as a network timeout. This one ran 435 milliseconds, which is a refusal
answered immediately. The two runs before it on the same
`CLAUDE_CODE_OAUTH_TOKEN` cost $10.46 (94 turns, finished 04:02:02Z) and $9.29
(100 turns, 2026-09-29 17:12Z), and this dispatch was created twenty-four
seconds after the first of those ended. A subscription usage ceiling reached
mid-day is the leading hypothesis and it is a hypothesis, not a finding,
because the action runs with full output hidden for security and the upstream
error is not recoverable from the log. That is incident 23's own second finding,
still open ten days later: **the org cannot read why any of its runs fail.**

**What it cost.** One dispatch carrying an owner directive, and the thirteen
hours before anyone noticed. It cost no money, which is the part that makes it
easy to miss: a $0 run in a cost report looks like a run that did not happen.

**Not concurrency, and worth saying so explicitly.** `INC-2026-09-30-engineer-
run-twice-again` is the day's other engineer-lane incident and item 9 on
`docs/agents/pending-workflow-changes.md` is its fix. It is not this. The two
runs did not overlap: 36665217714 completed at 04:02:02Z and this one's action
step began at 04:03:11Z. A `concurrency:` block would not have saved it.

**What would make the next one diagnosable, in the order they are worth doing.**

1. Amend incident 23's fingerprint section so the identity is `modelUsage: {}`
   alone, with the model name and the duration listed as discriminators among
   at least two known causes rather than as part of the test. That is a one
   paragraph edit to an ExO-owned section of this file and this entry is the
   request for it.
2. A `$0` run is a reportable outcome in its own right. `tools/run_report.py`
   already runs on `if: always()` in every seat workflow and already has the
   run's outcome; a run whose model usage is empty is a distinct fingerprint
   from a crash and should say so in the line it posts, rather than being one
   more red square.
3. The hidden-output problem is the owner's, not a seat's. Ten days and two
   incidents have now turned on an error message that exists and cannot be read.

## INC-2026-10-01-checks-red-on-main-across-four-prs — the fix for a red build has now shipped four times and landed none (2026-10-01, engineer seat)

**A repeat of `INC-2026-09-30-two-checks-steps-red-on-main-for-days`, recorded
because the standing rule at the top of this file has no exceptions.** That
entry's own closing line is "Both fixed in PR #142". Today, `checks.yml` on
`main` is still red, and #142 is still open.

**What the numbers are.** `gh run list --workflow checks.yml --branch main`
returns five runs and all five are `failure`, the newest at 2026-09-30T02:37Z.
`main` has had no push since 2026-09-30T02:39Z, so that red run is the current
state of the default branch and has been for twenty-four hours. The two failing
assertions are exactly the ones that entry diagnosed: the press's `retry-after`
floor in `tests/test_press_resilience.py`, and `tools/run_report.py` printing a
`::warning::` to stdout in front of the JSON in `tests/test_run_report.py`.

**Why it is a repeat rather than the same occurrence continuing.** The fix has
been written four separate times, by four runs of this seat, and carried forward
in a chain of superseding pull requests: #142, then #158, then #166, then this
run's #170. Each run surveyed the open PRs, found its predecessor, merged it
forward rather than rebuilding it, and shipped the same green suite again. Four
authors of the same correction is the definition the standing rule uses. What
none of them could do is merge.

**What it costs, which is not the red badge.** `checks.yml` is the gate that
holds the press's request inside the model's budget (incident 22), the
rehearsal's teeth, the board client, the skill receipts and the graph audit's
SQL. A permanently red gate cannot report a new failure, because there is no
state left for it to change into. Every one of those protections is currently
switched off in the only place it runs, and has been for two days, while the
repository contains a branch on which all of them pass.

**The engineer seat's queue is the mechanism.** Seven pull requests from this
seat are open at once, each superseding the last: #141, #142, #149, #153, #158,
#166, #170. The ship-first rule and L-E10's survey are both working exactly as
written, and the result is a correct, tested, seven-deep stack that protects
nothing until a hand merges it. L-E10 names this inventory one repository up;
this is it one repository down. The remedy is not another PR.

**What would actually fix it.** Merging the head of the chain, which is one
action. #141, #142, #149, #153, #158 and #166 can then be closed rather than
reviewed, because each is contained in its successor. Nothing in this repository
can do that, and this seat is forbidden to.

**Where to look next.** The incident this repeats left a guardrail suggestion:
that the engineer's §0 machinery check also read `gh run list --workflow
checks.yml --branch main`, because a merged workflow that fails is a runtime
change that announced itself and nobody answered. This run ran that command and
it is what found this. The suggestion is worth promoting into the charter, and
only the owner's merge can put it there, so it is in the ledger as a proposal
rather than here as a fix.

**Update, 2026-10-01, second window of the same day, same seat.** Not a new
entry, because this is the same occurrence continuing three hours later rather
than a fresh repeat, and the allocator at the top of this file has collided four
times already (incident 29). Two numbers move. The correction has now been
written **five** times, because this run merged #170 forward and shipped the
same green suite again. **Eight** pull requests from this seat are open at once:
#141, #142, #149, #153, #158, #166, #170 and this run's #172.

One clarification the earlier reading of this incident did not have, and it
matters for anyone checking the claim. `main`'s head is `6464f34` and
`checks.yml` has **no run at all** against it, because that commit touches only
`docs/decisions.md` and the workflow is path-triggered. The newest run on `main`
is the `failure` on `5a90fb3`, main's second-newest commit. Nothing checks.yml
tests changed between the two, so the gate is red and the state is current, but
the precise sentence is "the newest run that exists on main is red", not "main's
head is red". A reader who ran the command on the head sha and found nothing
would otherwise conclude this entry was stale.

The remedy is unchanged and this run cannot perform it either.

**Update, 2026-10-02, next day, same seat.** The correction has now been written
a **sixth** time, by this run, which merged #172 forward and measured the same
green suite again. Still not a new entry, for the reason the update above gives.
The newest `checks.yml` run on `main` is still the `failure` on `5a90fb3` and
nothing has changed on either side. Nine pull requests from this seat are open
at once now: #141, #142, #149, #153, #158, #166, #170, #172 and this run's #176.

**Update, 2026-10-03, next day, same seat.** The gate failed four more times on
2026-10-02, all four on `writer/2026-10-02`: runs 37059221342, 37060594494,
37060874090 and 37062267060. Same job, same two steps, and in every case the
branch's own diff was prose and a ban list, so the writer seat paid for a defect
it could not have caused and cannot fix. Six occurrences of the red gate are now
on the record. Both steps are green on this seat's chain, measured again today
the way the workflow runs them: `python3 tests/test_press_resilience.py` passes
every check, and `python3 -m pytest tests/test_run_report.py` passes eighteen
with `GH_TOKEN` unset, which is the condition that made it fail only in CI. So
the correction has now been written a **seventh** time and landed none of them.
Still not a new entry, for the reason the updates above give. What is new and
worth the owner's eye is that the cost has moved off this seat. A red gate that
only this seat's own pull requests carried was an embarrassment. A red gate that
turns another seat's clean pull request red is a tax every seat pays, and the
PM's 2026-10-02 standup named it the queue's top finding for that reason.

## INC-2026-10-02-urgent-entry-half-applied — the ledger entry asked for two things, the fix did one, and the newsletter kept the hole the archive closed (2026-10-02, engineer seat)

**What happened.** On 2026-09-19 the security seat filed an entry about the
archive rendering an issue body into `dangerouslySetInnerHTML` through a parser
that stopped sanitizing HTML at v8. PR #69 closed it on 2026-09-24, and closed
it well: `site/lib/markdown-core.js` allows no raw HTML through at all, checks
every href against a scheme list, decodes entities before it checks, and says in
its own header why a sanitizer was the wrong instrument.

Three days earlier, on 2026-09-22, this seat had filed the same finding against
the other surface, status `urgent`, and it asked for two things in one sentence:
escape raw HTML on the way into the email, and "refuse any href whose scheme is
not http, https or mailto".

The 2026-09-24 designed-template rewrite did the first. Every text slot in
`pipeline/email_render.py`'s `render` goes through `html.escape`. One slot does
not, `item_url`, and it lands in `<a href="{{item_url}}">` in
`site/emails/digest.html`. `inline` escapes a link's text before it builds the
anchor and never reads the scheme. And `legacy_html` in `pipeline/weekly.py`,
the fallback render, still ran the markdown library with `extensions=["extra"]`
over a body nothing had escaped.

So for ten days the archive was the safe surface and the newsletter was not,
which is the sentence the 2026-09-22 entry itself used, and it stayed true
across every engineer run in between.

**Measured, not argued.** Fourteen cases were written against the three sinks
before any fix. Seven were red on the branch point:

```
FAIL  test_a_quote_in_a_source_url_cannot_open_a_new_attribute
FAIL  test_a_javascript_source_url_does_not_survive
FAIL  test_a_data_source_url_does_not_survive
FAIL  test_inline_refuses_a_javascript_link_and_keeps_the_words
FAIL  test_the_fallback_email_escapes_raw_html
FAIL  test_the_fallback_email_refuses_a_javascript_href
FAIL  test_an_ampersand_in_a_source_url_is_escaped_and_still_the_same_link
```

A source URL is copied out of arXiv text by a model, so the path from a crafted
passage in a paper to a live attribute in a subscriber's inbox had no human in
it. That is the chain the 2026-09-19 entry described, on the surface the product
actually is.

**Why it is in this register.** Nothing was falsely closed. The entry still
reads `urgent` and no one ever marked it built, which makes this the cleaner and
more worrying version of the failure: the record was correct for ten days and no
gate ever asked it anything. That is `INC-2026-09-26-law-15-fixed-on-one-surface`
exactly, a rule applied to the surface that produced it and left live on the
other one, and it is `L-A9` in `docs/standards/lessons.md`, recording a rule is
not enforcing it. The engineer charter's own "Check the register before you ship"
step was written for this class and it names four registers. `docs/ideas.md` is
not one of them, and `docs/ideas.md` is where this sat.

**Fixed in this run.** `url_allowed` and `safe_href` in
`pipeline/email_render.py` apply the site's scheme list to every href the email
prints, `legacy_html` escapes before markdown sees the body and blanks any href
markdown built from a refused scheme, and the fourteen cases are in
`tests/test_email_template.py`, which is a file `checks.yml` already runs.

**The lesson, blamelessly, and it is about shape rather than care.** An entry
whose "What" paragraph names two requirements will be closed by a pull request
that satisfies one of them, because a pull request is reviewed against the
problem it describes and not against the ledger text it answers. The cheap
control is a test per requirement rather than a pull request per entry. The
second control, which this run also took: when two surfaces render one body,
the second surface's rule should read the first surface's constant rather than
restate it, so divergence is a red build instead of a discovery.

## INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had — the file holding the site's whole XSS defence says in its docstring that it runs in CI, and no workflow runs it (2026-10-02, engineer seat)

**What happened.** `tests/test_markdown.py` exists because of the 2026-09-19
finding, and its docstring says this of `tests/markdown.test.mjs`:

> It needs no node_modules, which is why it is the half that runs in CI.

No workflow in this repository runs `tests/test_markdown.py`. `checks.yml` runs
fourteen named test files as individual steps and that is not one of them.
`site/lib/markdown-core.js`, the module that decides what markdown is allowed to
become on the public site, is in neither of the workflow's two `paths` lists, so
a pull request that changes nothing but that file triggers no check at all.

The same is true of `tests/test_accounts.py` and `tests/accounts.test.mjs`,
which hold the account and entitlement layer.

**Measured this run.** `node --test tests/*.test.mjs` returns 122 pass, 0 fail,
so the step this needs would land green today and the gap is a missing gate
rather than a hidden break. Each of the five `.mjs` suites has a Python wrapper
that runs it in a subprocess, which is the established pattern here. Three of
the five wrappers are already reachable or already queued:
`tests/test_skill_receipts.py` is a live step, `tests/test_delivery_receipt.py`
is item 15 and `tests/test_issue_route.py` is item 16 in
`docs/agents/pending-workflow-changes.md`. The two that are neither are the two
named above.

**Why it is a repeat.** `INC-2026-09-29-receipts-step-had-no-paths` is a step
that could not fire because nothing it guarded was in the trigger paths, and
`INC-2026-09-30-check-harness-green-under-pytest` has a paragraph headed "One
finding this run could not fix" that is this finding one file over. The standing
rule at the top of this file admits no judgment once something has happened
twice, and this is at least the third time.

**What makes it worse than either, and it is the part to read.** Those two were
findable by looking at where a thing lived, or by running a command and reading
an exit code. This one is a sentence of prose, inside the test file, asserting
the coverage it does not have. A reader who opens the file to ask whether the
site's XSS defence is under CI gets told yes. The claim is forty lines of
docstring away from any workflow, in a file that has no way to check it, and it
reads as the most trustworthy kind of evidence there is, which is a note the
author left for exactly this question.

**Not fixed in this run, because this seat cannot push a workflow file** (the
structural blocker at the top of `docs/agents/pending-workflow-changes.md`).
Queued there as item 17, with both anchors verified against the live file.

**The docstring is corrected in this run rather than left standing.** The first
draft of this entry argued for leaving it, on the grounds that a false claim is
at least a legible trace. That is wrong, and it is wrong in the way this register
keeps catching: a trace nobody is looking for is not a control, and this entry is
the trace. So the sentence now says what is true, names this incident, and names
the queued item, which means a reader who opens the file to ask whether the
defence is under CI gets the real answer and the reason.

## INC-2026-10-02-pending-queue-number-collision — three open pull requests are allocating the same five numbers on the workflow queue, and incident 29 is the entry that already says why (2026-10-02, engineer seat)

**What happened.** `docs/agents/pending-workflow-changes.md` numbers its queued
items sequentially. `main` stops at item 11. Measured this run against the live
pull requests:

- this seat's chain, carried into PR #176, holds items 12 through 16 (skill
  registration, the conftest stub, the deploy-drift guard, the delivery receipt,
  the archive) and adds 17
- PR #174, the security seat, 2026-10-01, holds items 12 through 16 for five
  entirely different changes: action pinning, `PROJECTS_TOKEN`, the budget step,
  the no-ship tripwire, the register checker
- PR #160, the ExO seat, holds items 12 and 13 for two more

Thirteen items, six numbers. Every one of the three branches allocated correctly
against the `main` it could see, and every one of them is wrong about what the
highest number is, because the number depends on pull requests the branch cannot
read.

**Why it is a repeat, and it is the same words one file over.** Incident 29 is
this exact mechanism in `docs/agents/incidents.md`, where the sequential
allocator collided four times. The fix there was a slug: the note at the top of
that register now says to use `INC-YYYY-MM-DD-short-slug` and never the next
sequential number, with the reasoning that a seat writes on a branch so the
highest number it can see is not the highest number that exists. That reasoning
is about branches, not about incidents, and it transfers without a single change
to any register a seat appends to. One register got the fix. This one has the
same defect and more writers.

**Not fixed in this run, because fixing it well is not this seat's call alone.**
Renumbering would break the cross-references that already exist: this register
cites "item 13", "item 15" and "item 16" by number in three places, and so do
the pull request descriptions the owner reviews against. The structural fix is to
convert the page to slugs the way the incident register was converted, which is a
one-time edit to a page the ExO maintains, and it is filed as a ledger entry
today rather than performed here. What this run does instead is say the number is
provisional inside item 17 itself, so a reader who sees two items 12 after the
merges knows this was foreseen rather than botched.

**The generalizable rule, which is the reason this is worth more than a line.**
Any append-only file that many branches write to cannot carry a sequential
identifier, and the org now has two instances to prove it. The test to apply to
the next register someone creates: can two seats, each correct about `main`,
produce the same identifier. If yes, the identifier has to be derived from
something the branch owns, which is its date and its own words.

## INC-2026-10-02-fixture-pinned-to-a-wall-clock-date — a test with no code change behind it went red when the clock passed it (2026-10-02, engineer seat)

**`tests/test_delivery_receipt.py` failed this morning and nothing in the
repository had changed.** The file was written on 2026-10-01 by this seat's own
run and shipped green. Its `receipt()` fixture builds a delivery receipt whose
corpus "moved last night", and it built that timestamp from a hardcoded
`datetime(2026, 10, 1, 2, 0)` minus fourteen hours. `judge_pipeline` in
`tools/delivery_health.py` measures corpus age against the real clock, which is
correct: a corpus is stale when it stopped moving and no caller gets to decide
what day it is. `PIPELINE_STALE_DAYS` is 2. So the fixture read as fresh for
about 38 hours and then read as a two-day-old corpus forever, and the assertion
"a corpus that moved last night reads ok" became false at roughly 16:00 UTC on
2026-10-02.

**Why it matters more than one red file.** The same function in the same test
file already had the right pattern six lines below, where the stale case is
built as `datetime.now(timezone.utc) - timedelta(days=5)`. One case was
relative and the other was pinned, in one fixture, so the file looked
deliberate. And the failure is invisible where it would be caught: the file is
not one of the fourteen `checks.yml` names, so no pull request runs it, and the
only thing that would have shown it is `python3 -m pytest tests/ -q`, which is
the command the repository documents and no workflow runs.

**Fixed in the same pull request that found it** (engineer, 2026-10-02, second
window): the fixture derives its freshness from `datetime.now`, with the reason
written where the constant was, and `observed_at` is left pinned with a note
saying what has to change if a reader ever starts judging a receipt's own age.

**The repeat it belongs to.** INC-2026-09-30-two-checks-steps-red-on-main-for-days
is the same class seen from one angle: a test whose verdict depends on
something other than the code it tests. There it was the environment, a test
that "passed on every machine holding a token and failed in the only place it
ran". Here it is the clock. Both are assertions that decay, and the lesson
generalises to one line worth a gate: a test fixture that names a date is a
test that expires, so build every relative timestamp from `now` and keep the
absolute ones for the labels nothing measures an age against.

**What would have caught it earlier.** Nothing in this org runs the whole suite
on a schedule. Every check is attached to a pull request that touches a path,
which cannot catch a defect whose trigger is the passage of time. Filed in the
ledger as its own entry (2026-10-02, a daily run of the whole suite), because
the same gap hides anything else that expires: a pinned model id, a cap read
from a dated document, an API that deprecates on a date.

## INC-2026-10-03-panel-reviewer-claims-a-ci-step-it-never-had — a build note and the README both say the provenance reviewer runs on every pull request, and no workflow has ever run it (2026-10-03, engineer seat)

**A repeat of `INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had`,
one day later, by the same seat, in the same shape.** That entry is about
`tests/test_markdown.py`, whose docstring said it ran in CI while no workflow
named it. This entry is about the sentence this seat wrote the following
evening.

**What happened.** `docs/product/reviewer-panel.md`, written yesterday with the
panel's first reviewer, says the file half of that reviewer "runs on every pull
request that touches `skills/**` or `db/schema.sql`, inside the skill-receipts
step of `checks.yml`". The README's status line repeats it: "the file half runs
on every pull request that touches `skills/**`". Neither is true.
`.github/workflows/checks.yml` on this branch and on main contains no
`panel_provenance` step, and neither `tools/panel_provenance.py` nor
`tests/test_panel_provenance.py` is in either of its two `paths` lists. The
skill-receipts step runs `tests/test_skill_receipts.py` and nothing else. So the
46 tests in `tests/test_panel_provenance.py` have never been executed by CI, and
the one thing CI exists to hold about that reviewer, that its three statements
still resolve against `db/schema.sql`, has never been held.

**Why the same seat wrote the same defect twice in two days.** The first entry
blamed a docstring written at the same time as a queued workflow change, where
the queue entry covered a different file. This one has no queued workflow change
at all. The build shipped the reviewer, the schema, the tests and the prose
describing where it runs, and the step was simply never written, because
`.github/` is outside this seat's writable surface and the queue file is the
substitute. A change this seat cannot make is a change it has to remember to
file, and nothing in the run checked that the sentence had a queue entry behind
it.

**The general shape, which is worth more than either instance.** Both defects
are one sentence in prose asserting a mechanism in a file the author could not
edit. Neither was catchable by a test, because the prose was the only artifact
that said the mechanism existed. The cheap fix is the one already applied to
`tests/test_markdown.py`: a test that greps `checks.yml` for the step it claims.
This run adds the same gate for the adversary
(`tests/test_panel_adversary.py::test_the_adversary_has_no_files_only_mode_and_ci_never_runs_the_reviewer`),
which asserts the opposite direction: the reviewer must NOT be a CI command,
because CI holds no database credential and a green step could only ever mean
that nobody asked the graph.

**Fixed in this pull request, in three places.** The sentence in
`docs/product/reviewer-panel.md` and the README's status line now say the step
is queued rather than running, and item 18 of
`docs/agents/pending-workflow-changes.md` is the queue entry that was missing:
the two test files in both `paths` lists, two pytest steps, and the provenance
reviewer's `--files-only` command. The step itself still needs the chair's hand,
which is the part this seat cannot do and the reason the entry exists.
