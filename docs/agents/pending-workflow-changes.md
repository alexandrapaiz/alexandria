# Workflow changes the agents cannot apply themselves

**Enforced at:** prompts/exo-agent.md §5, which verifies each queued
item against the live workflow files every run.

## The lane this page exists for is open, and the page stays anyway (added 2026-10-18)

**Read this before the section below.** On 2026-10-18 this seat ran the
capability probe `prompts/exo-agent.md` §5 prescribes, which is a comment
appended to `.github/workflows/agent-exo.yml` on a throwaway ref, and **the
push succeeded.** The ref was deleted in the same turn and no pull request was
opened. Incident 12, the refusal this entire page is built on, no longer
applies to the credential the host hands a seat.

**Nothing on this page is being applied as a result, and that is a decision
rather than caution.** The lane did not open because `APP_PRIVATE_KEY` landed
and ADR-27's GitHub App was granted the `workflows` permission. It opened
because the 2026-10-17 runtime migration handed twelve seats the owner's own
account credentials, with `admin: true` on four repositories, which nobody
decided and nothing recorded. See
`INC-2026-10-18-the-host-runs-every-seat-as-the-owner`. Nineteen queued
workflow edits applied on the strength of an unintended escalation would be
the worst thing this seat has ever done, and the live instruction the host
gave this run says "never touch secrets or workflows" in those words.

So this page keeps its purpose until the owner either narrows the credential
or grants the lane on the record. When she grants it, the items below become
ordinary edits and this page is deleted, per §5. Until then the only thing
that changed is that the constraint is now a choice, and a reader should know
which of the two they are looking at.

## What decision 056 changed on this page, and what it did not (added 2026-10-18, corrected the same run)

**Read this before you apply anything below.** HQ decision 056 deleted every
seat's `schedule:` block from `.github/workflows/` on 2026-10-17 and moved
each seat's clock to a manifest on the company host. There have been zero
`*-agent` runs in this repository's Actions since 2026-10-17 17:59:54Z,
against dozens of host-started seat pull requests a day.

So a **seat** workflow is now a door that opens for an explicit
`workflow_dispatch` and nothing else. **Every item on this page that edits a
`prompt:` block or a `claude_args` line in an `agent-*.yml` file still
matters, and it matters only for a dispatched run.** Those are items 4a, 7,
13 and 15 for prompts and items 3, 14 and `2026-10-11-writers-cap` for caps.
They are marked here rather than deleted, because a dispatch is a real path
and the owner uses it.

**The first version of this heading said "everything on this page now governs
dispatches only" and that was wrong, so it is corrected in the same run it
was written in.** Decision 056 deleted `schedule:` blocks. It touched no
`pull_request` trigger, no `push` trigger and no `workflow_dispatch` trigger.
So the majority of this page is **completely unaffected**:

- The eight `checks.yml` items, which is the most contended file here, all
  run on `pull_request`. Fully live.
- The `hq-origin-notice.yml` item, which runs on `push` to main. Fully live.
- Every lane-one item in `.github/workflows-pending/`: `skill-gate.yml`,
  `adr-numbers.yml`, `subscriber-list.yml` on `pull_request`,
  `modal-deploy.yml` on `workflow_dispatch`. Fully live.
- `press-watch.yml` alone is in question, because it is the one staged file
  that uses `schedule:`. See below.

An over-broad heading on a page nineteen items long is the same defect as a
rotted ordering paragraph, and it fails in the worse direction, because a
reader who believes it stops applying eight live items. The §5 rule about
validating a new mechanical check against the artifact applies to a new
*claim* about the artifact just as much: this one was written from the seat
workflows in front of the run and asserted over a page that is mostly not
seat workflows.

**What has moved off this page entirely** is any change to a cadence, a cap,
a model, an event subscription or a credential. Those five now live in
`alexandrapaiz/alexandra-systems:runtime/agents/alexandria/<seat>/agent.toml`,
which this seat can read and cannot write, so they leave through
`docs/agents/hq-relay.md` as the exact `[trigger]` or `[runtime]` line
wanted. The test for which lane a change takes is one question: which
runtime does the thing you are changing belong to? See
`prompts/exo-agent.md` §5.

**The cost of getting that wrong is already measured.** Item 21's writer cap
was applied to `.github/workflows/agent-writer.yml` on 2026-10-12, correctly
and with full reasoning, and the file stopped governing the writer five days
later. The manifest still says 150. See
`INC-2026-10-18-the-writers-cap-raise-governs-a-door-nothing-opens`.

**And one item's mechanism is now in question rather than its anchors.**
`.github/workflows-pending/press-watch.yml`, staged on 2026-10-14, triggers
on a GitHub `schedule:` with `cron: "0 11 * * *"`. Decision 056's own words
are "No schedule here means no run starts on GitHub minutes by itself," and
whether that verdict covers a guard workflow or only a seat workflow is not
recorded anywhere a reader can check, because the decision's entire record
in this repository is one comment line repeated in ten files. **That
ambiguity is the finding, not the schedule.** The question is in the relay
entry for 2026-10-18 and item 21 should not be installed until it is
answered, because installing a cron the parent decision retired is worse
than leaving the guard unbuilt.

## The overlap table, regenerated every run

**Added 2026-10-11, and it replaces the rule that every item restate its own
neighbours.** That rule produced nineteen paragraphs each claiming to list
the other items touching its files, each written on a different day, each
rotting on its own. Four were false on 2026-10-04. Five of item 14's eight
lines were false on 2026-10-11. Seventeen of the nineteen omit at least one
neighbour today. **A fact about the whole page cannot be maintained in
nineteen places**, which is the same lesson as "two readers of one question
grow two answers" in `delivery-health.md`.

So the overlap lives here, once, and the ExO charter's §5 regenerates it
every run from the corrected sweep rather than asking each item to remember.

| Workflow file | Items that touch it | What each edits, so the order can be judged |
|---|---|---|
| `checks.yml` | 12-CI, 13-CI, 14-CI, 15-CI, 16, 17, 19, 20 | **the only real hazard on this page.** All eight add entries to the same two `paths:` lists and steps to the same job. Apply in ascending order and read each item's own "if item N is applied first" note; several already carry one |
| `agent-engineer.yml` | 5, 6, 9, 10, 14 | 5 adds a step, 6 adds an `env:` line, 9 adds a concurrency block, 10 replaces a step body, 14 edits `claude_args`. Disjoint; any order |
| `agent-pm.yml` | 5, 6, 14, 15 | 5 a step, 6 an `env:` line, 14 `claude_args`, 15 a `prompt:` block. Disjoint; any order |
| `agent-skill.yml` | 6, 12, 13, 14 | 6 and 12 both add to the `env:` block, so whichever lands second appends rather than replaces. 13 a `prompt:` block, 14 `claude_args` |
| `agent-writer.yml` | 4a, 6, `2026-10-11-writers-cap` | 4a a `prompt:` block, 6 an `env:` line, the slug a `claude_args` line. Disjoint, any order. **The slug was "item 21" until 2026-10-18**, when a second item 21 on main forced the rename |
| `agent-research.yml` | 6, 14 | an `env:` line and a `claude_args` line. Disjoint |
| `agent-exo.yml` | 7, 14 | 7 rewrites a prompt paragraph, 14 edits `claude_args`. Disjoint |
| `agent-market.yml`, `agent-security.yml`, `agent-frontend.yml`, `hq-origin-notice.yml` | one item each (14, 14, 10, 5) | nothing to order |

**The first version of this table, written an hour before this one, had three
errors in it**, and they are left on the record because they are the argument
for the table rather than against it. It said `agent-writer.yml` was touched
by item 20, which does not touch it; it said `agent-market.yml` was touched
by items 14 and 20, where it is item 14 alone; and it listed
`agent-finance.yml` and `agent-okr.yml` as having one item each when no item
names either. All three came from a splitter whose item boundaries ran past
the last `###` heading into this page's trailing sections, so the final
items absorbed text that was not theirs.

**Two things follow, and the second is the point.** First, an item-boundary
bug reads exactly like an overlap: both produce a filename attributed to an
item that does not contain it, which is why the error survived into a
published table. Second, **the regeneration rule caught it within the same
run that made it**, because the table is generated from one command and
re-checked against that command before shipping, which is precisely what
nineteen hand-maintained paragraphs could never do. A fact kept in one place
can be wrong. It cannot be quietly wrong in nineteen different ways.

**Read this table rather than an item's ordering paragraph where the two
disagree, and when you find a disagreement, delete the paragraph.** The
paragraphs are being retired as their items are touched rather than in one
sweep, because rewriting seventeen of them in a single run would be this
seat editing other seats' queued work on a day none of it is being applied.

**Four things to discount in the raw counts, re-checked 2026-10-18.** The
sweep over-counts three ways and under-counts one, and all four were present
the day it was published.

1. **A mention is not an edit.** The sweep finds a filename, not a verb.
2. **The self-references in this section count.** The paragraph above that
   lists `agent-finance.yml` and `agent-okr.yml` as the table's own earlier
   errors is itself two hits on each, which is why the raw sweep reported
   `agent-okr.yml: 2` and `agent-finance.yml: 2` on 2026-10-18 when no live
   item names either.
3. **The "Applied and deleted" section at the bottom counts.** It names four
   seat workflows, and those items are gone.
4. **The published regex cannot see the pending lane.** It matches
   `agent-*`, `checks`, `deploy-main`, `build-agent-image` and
   `hq-origin-notice` only, so it is blind to `press-watch.yml`,
   `skill-gate.yml`, `modal-deploy.yml`, `subscriber-list.yml` and
   `adr-numbers.yml`, which this page names nine times between them. Lane-one
   items are staged whole files and collide differently, but two items can
   still touch one staged file. The corrected pattern adds them:

   ```bash
   grep -oE '(\.github/workflows(-pending)?/)?(agent-[a-z]+|checks|deploy-main|build-agent-image|hq-origin-notice|press-watch|skill-gate|modal-deploy|subscriber-list|adr-numbers)\.yml' \
     docs/agents/pending-workflow-changes.md | sed 's#.*/##' | sort | uniq -c | sort -rn
   ```

   This is the **third** correction to this one command, after the full-path
   bug on 2026-10-11 and the item-boundary bug an hour earlier the same day.
   A sweep whose output is a table of counts is very hard to read as wrong,
   because every number looks like a number. The standing answer is the one
   the 2026-10-11 run wrote: validate the check against an instance confirmed
   by eye before publishing it. Here the instance is
   `agent-okr.yml`, which the table says no item touches and the raw sweep
   says two do. If a future version of this command reports `0` for
   `agent-okr.yml`, it is reading the page correctly.

**The edit sets in the table above are unchanged on 2026-10-18**, verified
against the corrected sweep with all four discounts applied. No item has
been added to this page since the table was generated except the pending
lane's README note, which touches no workflow.

**One human read is still required, and here is exactly which one.** Item 14 names
`agent-writer.yml` once, in the sentence saying the writer row moved to item
21, and the sweep reports it as a fifth item on that file. The table records
the **edit** set, so item 14 is not in the `agent-writer.yml` row. This is
§3b's rule that a grep finds vocabulary and not polarity, arriving in the
one place on this page where it changes an answer. Read each hit before you
put it in the table, and do not let a later run flip the row back on the raw
count.

**The command that regenerates it**, which is the corrected sweep from ExO
charter §5. The old version matched the full path only, so it missed every
bare filename on the page:

```bash
grep -oE '(\.github/workflows/)?(agent-[a-z]+|checks|deploy-main|build-agent-image|hq-origin-notice)\.yml' \
  docs/agents/pending-workflow-changes.md | sed 's#.*/##' | sort | uniq -c | sort -rn
```

## How to name an item on this page, and how to read the numbers that exist

**New items get a slug, never the next number** (rule added 2026-10-11 by
the ExO agent). Write `### 2026-10-11-writers-cap: <title>`. The reason is
`INC-2026-10-02-pending-queue-number-collision` and it is the same reason
`docs/agents/incidents.md` abandoned sequential numbers after four
collisions: every seat writes on its own branch, reads a different snapshot
of this file, and allocates from the highest number it can see. Three open
pull requests once held thirteen items claiming six numbers.

**The four live collisions, because renumbering them would break twenty-odd
cross-references written by seats that are no longer running.** Read an
`item N` reference by what the referring sentence is about, and use this
table when it is not obvious. Items 12 through 15 each name two different
changes:

| Number | The seat-workflow item | The `checks.yml` item |
|---|---|---|
| 12 | the skill seat's `GROQ_API_KEY` | skill registration checked on the PR |
| 13 | the skill seat's dispatch prompt | the Modal stub installer's missing check |
| 14 | the caps that go to the measured rule | the deploy-drift guard runs in CI |
| 15 | the PM's dispatch prompt | the delivery receipt runs in CI |

Items 21 and up, and every slug, are unique.

## The one structural blocker, for the owner

**No agent seat can fix the machinery that runs it.** Every cap raise,
every tripwire, every timeout change on this page has to pass through a
human hand, and that is the single reason this page exists.

The mechanism, verified by attempting it (incident 12): GitHub refuses
any push from `GITHUB_TOKEN` that touches a file under
`.github/workflows/`, with

```
refusing to allow a GitHub App to create or update workflow
`.github/workflows/agent-engineer.yml` without `workflows` permission
```

This is not a misconfiguration. There is no `workflows:` key to add to a
workflow's `permissions:` block, because `GITHUB_TOKEN` cannot hold that
scope at all. Only a personal access token carrying the `workflow` scope
can push these files.

**What it costs, concretely.** On 2026-09-18 six runs failed, all of
them turn-cap collisions, and not one of the seats affected could raise
its own cap. The chair applied every fix by hand. The caps are current
now (item 3 below), and the cost has moved to a sharper place: on
2026-09-20 the PM seat lost a whole run to a two-line workflow condition
that no seat could change (item 1b, incident 23).

**The decision that is yours, and only yours.** Mint a PAT with the
`workflow` scope, store it as a repository secret, and pass it to
`actions/checkout` in the agent workflows. That would let the seats
repair their own machinery, which is the autonomy tiebreak in vision.md
§0 pointing one way. It would also hand every agent run a token strong
enough to rewrite what runs the agents, which is an authority change
rather than a convenience. Both things are true at once, which is why
this seat states the tradeoff and does not decide it.

**Until you decide, the standing arrangement holds:** workflow edits are
written out here in full, ready to apply, and the chair or you applies
them. Nothing here is blocked on analysis. It is blocked on a hand.

---

## Two lanes, and which change takes which

**Added 2026-09-27, because this page described one lane for eight days
after the org started using two.** The push is refused for paths under
`.github/workflows/` and for nothing else. So there is a second lane, and
it is better than this one wherever it applies.

| The change | The lane | What the owner does |
|---|---|---|
| A **new** workflow file | commit it to `.github/workflows-pending/`, with a section in that directory's README | `git mv` it one directory up |
| An **edit** to a workflow that already exists | a diff on this page, with every anchor verified against the live file | apply the diff by hand |

The engineer seat found the second lane on 2026-09-19 and has used it
four times since; `.github/workflows-pending/checks.yml` is the standing
example and it is still waiting for the move. Nothing in that directory
runs, which that README states plainly, so anything sitting there is a
guard that is not guarding yet. Audit it every run the same way this page
is audited.

**Why an edit does not get the better lane, which is the part worth
understanding before someone improves on this.** Pushing a full modified
copy of an existing workflow would also work and would also reduce the
owner's hand-work to a `git mv -f`. It trades a loud failure for a silent
one. A diff's anchor stops matching the moment the live file moves under
it, and the item is then visibly rotted, which is the entire mechanism of
the re-verification rule in `prompts/exo-agent.md` §5 and the only reason
incident 26 was caught before a hand applied it. A full copy taken on
Monday and moved on Sunday applies cleanly and silently reverts every
edit made in between. The owner edited these twelve files three times in
one week without a pull request, so that is not a hypothetical here.

Where a queued edit has grown too large to read as a diff, split the
item. Do not switch its lane.

---

Applied items get deleted from this file by the next ExO run, which
verifies against the workflow files themselves rather than trusting this
page.

---

## Pending, queued 2026-09-18 by the ExO agent

### 4a. The writer's dispatch prompt forbids the duty this PR assigns it

**Queued 2026-09-21 by the ExO agent. This is the item that makes the
rest of this pull request work, and without it the charter edits are
inert.**

**RE-VERIFIED 2026-09-27, unchanged and still unapplied on its sixth
day.** All three `-` lines below were grepped against the live
`.github/workflows/agent-writer.yml` this run and each appears exactly
once, at lines 40 to 42. Nothing has rotted. This item is the second
hand that incident 25's fix needs, so for six days the writer charter has
told that seat to draft site copy and the prompt it actually reads has
forbidden it. Incident 13 is the precedent for what a correct fix costs
while it waits, and it waited through sixteen pull requests.

**Why.** `.github/workflows/agent-writer.yml` line 40 carries this
sentence in the inline prompt the seat reads before anything else:

```
            Never edit taste.md, charters, site copy, pipeline code, sprints,
            or skills. Never merge your own PR, never push to main.
```

The owner's ruling of 2026-09-19 gave site copy drafting to this seat.
This PR corrects the charter to match. The workflow prompt still forbids
it, and the workflow prompt is the instruction that arrives last and
closest, so a seat holding both will most likely obey the prohibition.

This is worth stating as a general finding, because it changes what a
charter edit means. **Every seat's real charter is two files.** There is
`prompts/<seat>-agent.md`, which this seat can edit, and there is the
inline prompt inside `.github/workflows/agent-<seat>.yml`, which it
cannot. When the two disagree, the org has no way to know which one the
run obeyed. Incident 25's fix is the first time the disagreement has been
load-bearing, and it will not be the last: the prompts were written on
2026-09-18 and have been copied between seats since.

**How.** One edit to `.github/workflows/agent-writer.yml`. Remove the two
words that contradict the ruling and say what the seat may do, since
"never set it on the site" is still correct and still worth keeping.

```diff
-            Never edit taste.md, charters, site copy, pipeline code, sprints,
-            or skills. Never merge your own PR, never push to main. If the
-            charter file is missing, stop and fail loudly.
+            Never edit taste.md, charters, pipeline code, sprints, or skills.
+            You DRAFT reader-facing site copy into docs/voice/ when the run
+            calls for it, and you never SET it in site/, which is the
+            frontend seat's surface (docs/agents/copy-pipeline.md). Never
+            merge your own PR, never push to main. If the charter file is
+            missing, stop and fail loudly.
```

**Ordering against item 4.** Same file, and they do not overlap: 4a edits
the `prompt:` block and 4 edits the `claude_args:` line one line below it.
Apply either first. Do read both before committing, because they are two
hunks in a nine-line window.

**Cost.** $0.

**The wider sweep this implies, and it is not queued.** Every
`agent-*.yml` carries a prompt written by hand, and no seat has ever
diffed its inline prompt against its charter. That check belongs in this
seat's §2 and the charter edit is in this PR. The audit itself is the next
run's work, because finding a second contradiction is a run's worth of
reading and this run has one confirmed case to fix.

### 14. Six caps go to the measured rule. The writer's is item 21 and is urgent.

**Queued 2026-10-04 by the ExO agent, re-derived and split 2026-10-11 by
the ExO agent. This item replaces items 4 and 11**, which both proposed 200
and are both overtaken. Items 4 and 11 must not be applied.

**Split on 2026-10-11, and the reason is the whole lesson of this item.**
It was written as one item for seven seats on the argument that the diffs
share a justification and no order matters. Both halves of that were true.
What it did not account for is that **the seven lines did not share an
urgency, and bundling made the one line with a live cost wait behind six
without one.** The writer hit its cap on 2026-10-04, 54 minutes after this
item was queued, and again on 2026-10-09, losing an unpushed increment both
times. The owner reading this page five days running saw one item proposing
seven changes to seven workflow files, which is a sitting, not a keystroke.
The writer's line is now item 21, alone, with its own evidence. The
remaining six stay bundled, correctly, because none of them has failed.

**The general rule for this page, and it is new**: an item's grouping is by
urgency first and by convenience second. The moment one line in a bundle
acquires a real cost, it leaves the bundle.

**Re-derived 2026-10-11 and two of the seven numbers were already short.**
This is the same defect this item was created to fix in items 4 and 11,
arriving in this item in seven days. Peaks move on their own, so a proposed
cap is a measurement with a shelf life, and every re-verification of this
page must re-read the numbers and not only the anchors.

| Seat | Peak 2026-10-04 | Peak 2026-10-11 | Cap now | Cap after, revised | Was |
|---|---|---|---|---|---|
| skill | 156 | 156 | 180 | 350 | 350, unchanged |
| engineer | 168 | **184** | 200 | **400** | 350, now below the rule |
| market | 131 | 131 | 160 | 300 | 300, unchanged |
| research | 145 | 145 | 180 | 300 | 300, unchanged |
| security | 134 | 134 | 250 | 300 | 300, unchanged |
| exo | 134 | 134 | 200 | 300 | 300, unchanged |

The writer's row moved to item 21. The rule is `Required = 2 x peak, rounded
up to the next 50, floor 100`, from [turn-caps.md](turn-caps.md), and the
engineer's 184 doubles to 368, which rounds to 400.

**How. Every `-` line below was grepped against the live file in this run
and appears exactly once, except market, which is two steps and gets two
diffs.**

`.github/workflows/agent-skill.yml`:

```diff
-          claude_args: "--max-turns 180 --permission-mode bypassPermissions --model claude-opus-5"
+          claude_args: "--max-turns 350 --permission-mode bypassPermissions --model claude-opus-5"
```

`.github/workflows/agent-engineer.yml`:

```diff
-          claude_args: "--max-turns 200 --permission-mode bypassPermissions --model claude-opus-5"
+          claude_args: "--max-turns 400 --permission-mode bypassPermissions --model claude-opus-5"
```

`.github/workflows/agent-research.yml`:

```diff
-          claude_args: "--max-turns 180 --permission-mode bypassPermissions --model claude-opus-5"
+          claude_args: "--max-turns 300 --permission-mode bypassPermissions --model claude-opus-5"
```

`.github/workflows/agent-security.yml`:

```diff
-          claude_args: "--max-turns 250 --permission-mode bypassPermissions --model claude-opus-5"
+          claude_args: "--max-turns 300 --permission-mode bypassPermissions --model claude-opus-5"
```

`.github/workflows/agent-exo.yml`:

```diff
-          claude_args: "--max-turns 200 --permission-mode bypassPermissions --model claude-opus-5"
+          claude_args: "--max-turns 300 --permission-mode bypassPermissions --model claude-opus-5"
```

`.github/workflows/agent-market.yml` has **two** run steps, the
open-routed one and the Claude fallback, and either can be the step that
executes. Both get the raise, because a cap belongs to a job. This is the
incident 26 shape named in advance: one of two identical copies patched is
a cap that depends on which provider answered.

```diff
-          claude_args: "--max-turns 160 --permission-mode bypassPermissions --model ${{ vars.OPENROUTE_MODEL || 'kimi-k2.7-code' }}"
+          claude_args: "--max-turns 300 --permission-mode bypassPermissions --model ${{ vars.OPENROUTE_MODEL || 'kimi-k2.7-code' }}"
```

```diff
-          claude_args: "--max-turns 160 --permission-mode bypassPermissions --model claude-sonnet-5"
+          claude_args: "--max-turns 300 --permission-mode bypassPermissions --model claude-sonnet-5"
```

**Ordering, rewritten 2026-10-11 because the previous version was wrong on
five of its eight files.** It was written from the whole-page sweep
published in ExO charter §5, and that command matched
`.github/workflows/<name>.yml` only, while this page names files bare at
least as often. The under-count was inherited as a statement of fact. The
command is corrected in the charter and this is its output.

**The overlap table at the top of this page is the authority and it is
regenerated every run.** Read it rather than this paragraph. For this item's
files it says: `agent-skill.yml` with 6, 12 and 13, `agent-engineer.yml`
with 5, 6, 9 and 10, `agent-exo.yml` with 7, `agent-research.yml` with 6,
and `agent-market.yml` and `agent-security.yml` with nothing.

What the old paragraph got wrong, for the record: it called
`agent-research.yml` "named by this item alone" when item 6 also names it,
it listed three neighbours for `agent-engineer.yml` where there are four,
and it listed `agent-pm.yml`, which this item does not touch at all. It also
listed `agent-writer.yml`, which moved to item 21.

**Any order still works, and now for a checked reason rather than an
assumed one.** Every item in the right-hand column edits a `prompt:` block,
an `env:` block, a `secrets` line or a whole-file addition. This item edits
only `claude_args` lines. No anchor here sits inside any anchor there.

Items 4 and 11 are deleted by this item and must not be applied. Item 21
carries the writer's line and is independent of this item.

**Cost.** $0 unless a run uses the turns. A cap is a tripwire and not a
budget, and this is the sentence the page has repeated since 2026-09-18
because it is the one that keeps getting re-litigated.

**The smoke run this change owes, because a turn cap is a runtime change.**
[runtime-changes.md](runtime-changes.md) names `--max-turns` explicitly and
says no runtime change takes effect without a smoke run on a throwaway
branch. This seat cannot smoke it: the push that would create the branch is
the push the runner's token refuses, which is the first section of this
page. **So the obligation transfers to whoever applies the diffs, and
naming it here is the only way it survives.** One seat is enough, and
`agent-market.yml` is the right one because it is the only file in this item
with two steps: a dispatch of the market seat after the edit should print
`--max-turns 300` in whichever step executed, and the step that executed
should be the one the `OPENROUTE` condition selects. If it prints 160, one
of the two copies was missed, which is the failure this item was written to
prevent.

### 15. The PM's dispatch prompt forbids two duties its charter assigns

**Queued 2026-10-04 by the ExO agent, from the §2 charter-versus-prompt
check. This is the 4a shape in a second seat**, so the check is now worth
running across all twelve rather than only where a boundary was just
edited.

**The disagreement.** `prompts/pm-agent.md` §1b tells the seat to maintain
`docs/agents/org-chart.md`, and §4 as of 2026-10-04 tells it to write the
queue gauge. The inline `prompt:` block in `.github/workflows/agent-pm.yml`
says:

> You write only docs/sprints/ and grooming notes in docs/ideas.md.

`docs/agents/org-chart.md` is in neither place. So the workflow forbids a
duty the charter assigns, and the duty this run adds lands inside a
boundary the workflow does not describe.

**And the interesting half: the charter won.** The charter in
`prompts/exo-agent.md` §2 predicts the opposite, that "the inline prompt
arrives last and closest, so when the two disagree the run most likely
obeys the workflow and the charter edit is inert." The PM has in fact
written `docs/agents/org-chart.md` three times, most recently on
2026-09-28. The reason is in the prompt itself, two sentences earlier:
"Read prompts/pm-agent.md; it is your full charter." That licenses the
charter to extend the list, so the prohibition reads as a summary rather
than as a boundary.

**That makes this lower-severity than 4a and still worth fixing**, because
a seat that has to decide which of its two instruction files it believes is
a seat guessing at its own permissions, and the next run may guess the
other way. The prediction in the ExO charter is corrected in the same pull
request: the prompt does not reliably win, and the finding is the
disagreement itself rather than its direction.

**How.** Two edits to `.github/workflows/agent-pm.yml`. The file has two
run steps, open-routed and Claude fallback, with **identical** prompt
blocks, so each `-` line below appears exactly twice and **both copies get
the same edit**. This is the incident 26 shape named in advance: patching
one of two identical copies makes the seat's permissions depend on which
provider answered.

```diff
-            exactly one pull request with `gh pr create`. You write only
-            docs/sprints/ and grooming notes in docs/ideas.md. Never write
+            exactly one pull request with `gh pr create`. You write
+            docs/sprints/, grooming notes in docs/ideas.md, and
+            docs/agents/org-chart.md, which charter §1b assigns you. Never
+            write
```

**Ordering.** `agent-pm.yml` is also named by item 6, which adds
`NEON_RO_URL` to the `env:` block. This item edits only the two `prompt:`
blocks, so neither anchor moves the other and either order works. Verified
with the whole-page sweep in this run, after this item was written rather
than before it.

**Cost.** $0.

### 5. An HQ-origin commit should announce itself when it lands

**MOVED OUT OF THIS PAGE 2026-09-27. Do not apply it from here.** This is
a new workflow file, so it takes the other lane. The file is now
`.github/workflows-pending/hq-origin-notice.yml`, written out in full,
YAML-parsed, and one command from live:

    git mv .github/workflows-pending/hq-origin-notice.yml .github/workflows/hq-origin-notice.yml

The prose below is kept as the reasoning behind it, and the file's own
header comment carries the short version so the reasoning travels with
the artifact. Two changes were made to the YAML on the way across, both
recorded in the file: a `timeout-minutes: 5`, and an explicit
`shell: bash` on the run step, because
`INC-2026-09-26-run-report-dash-echo` is what an unstated shell cost the
org five days after this item was queued.

**Its trigger fired this week, which is the argument for moving it.**
Commit `1baeb7f` on 2026-09-25 changed how this repository deploys to
production, citing HQ Incident 5, and `grep -rn "HQ Incident 5" docs/`
returns nothing. The marker grep in this job matches that commit's
subject, verified against the live log this run.

**Queued 2026-09-24 by the ExO agent. Incident 23, and the cadence gap
recorded against the new row in unowned-duties.md.**

**Why.** §3f of the ExO charter now requires that every HQ decision
reaching this repository is read against local law. The trigger for that
duty is a merge, and merges do not respect a weekly cron. ADR-015 landed
on a Friday evening and was first read on a Sunday, after it had already
failed two PM runs. A weekly seat holding a merge-triggered duty is the
same cadence gap this org has already written down twice, and the
register's own rule says the fix is a cron change rather than another
sentence in a charter. Here the correct fix is not a cron at all, since
the trigger is an event.

**How.** A new workflow, `.github/workflows/hq-origin-notice.yml`, that
runs on push to main and does one cheap thing: if the pushed commits
carry an HQ marker, write a job summary naming them and open nothing.
No seat is dispatched and nothing is merged, so the blast radius is a
line of text in the Actions UI plus, once a seat can read it, an entry
the ExO run does not have to reconstruct from `git log`.

```yaml
name: hq-origin-notice

on:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  notice:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Flag HQ-origin commits
        run: |
          range="${{ github.event.before }}..${{ github.sha }}"
          hits=$(git log --pretty='%h %s' "$range" \
            | grep -iE 'ADR-0[0-9]{2}|HQ |company standard|vendored|centralizer' || true)
          if [ -n "$hits" ]; then
            {
              echo "### HQ-origin commits in this push"
              echo ""
              echo "$hits" | sed 's/^/- /'
              echo ""
              echo "Read these against local law before they take effect:"
              echo "docs/agents/cross-repo-law.md. The three questions are"
              echo "in prompts/exo-agent.md section 3f."
            } >> "$GITHUB_STEP_SUMMARY"
          fi
```

**What it does and does not do.** It makes an HQ-origin change visible
at the moment it lands rather than up to six days later, and it costs
one short job per push to main. It does not read the local law, it does
not block anything, and it cannot tell a real override from a commit
that merely mentions an ADR number. It is a smoke alarm, not a gate. The
judgment stays with the ExO run, which is correct, because deciding
whether a parent decision overrode a local safety clause is exactly the
kind of reading a grep cannot do.

**One honest caveat about `github.event.before`.** On a force push or a
first push it is unreliable, and the `|| true` means the step then says
nothing rather than failing. Silence on an edge case is the right
failure mode for a notifier whose backstop is a weekly human-read audit.

**Cost.** $0, a few seconds per push to main.

**Ordering.** **Corrected 2026-10-04**, because this paragraph said
"independent of every other item on this page" and that stopped being true
when items 9, 10, 14 and 15 were queued. This item edits the `env:` block
of `agent-engineer.yml` and `agent-pm.yml`. Item 14 edits `claude_args` in
the first, items 9 and 10 edit step bodies in the first, and item 15 edits
the two `prompt:` blocks in the second. No anchor here moves any anchor
there and any order works. The old sentence is the shape named in
`INC-2026-10-04-ordering-paragraph-rot-survived-its-own-rule`: a blanket
"independent of everything" cannot be kept true by anyone, because it has
to be rechecked whenever any other item is queued against any file, and
nothing points a reader at it.

### 3. The caps are not done. See item 14.

**Rewritten 2026-10-04, because this item asserted the opposite for
fifteen days and was read as a clearance.** Its original text said "every
cap in the org clears the measured rule", which was true of the
2026-09-19 measurement and stopped being true as the seats' turn demand
rose. The October re-derivation in [turn-caps.md](turn-caps.md) found
**seven of thirteen rows under the rule**, five of them above 80% of the
cap in force.

The raises are item 14. This item is kept rather than deleted because its
old sentence is the useful part: **a page of pending changes should never
carry a standing "nothing to do here" claim about a measured quantity.**
The claim does not expire, nothing re-checks it, and it reads as evidence
to the next person who opens the page looking for exactly this. The
earlier raises it describes (frontend 400 to 600, pm 250 to 300, security
200 to 250) were genuinely applied and verified in the 2026-09-19 run,
and that part of the record moves to "Applied and deleted" when item 14
lands.

### 6. The read-only database URL, for the engineer seat and now the PM seat

**Renumbered from 4 to 6 on 2026-09-27**, because this page carried two
items numbered 4 and the owner applies it by hand. Nothing else about the
engineer half changed.

Queued 2026-09-23 by the engineer agent. One line, in
`.github/workflows/agent-engineer.yml`, in the job's existing `env:`
block beside `GH_TOKEN` and `PROJECTS_TOKEN`:

```yaml
      NEON_RO_URL: ${{ secrets.NEON_RO_URL }}
```

The secret already exists and the research, writer and skill workflows
already read it, so this adds no new credential to the org, only an
existing one to a seat that cannot do its job without it.

**The same line, in `.github/workflows/agent-pm.yml`, added 2026-09-27 by
the ExO agent.** Identical diff, identical `env:` block, and a stronger
case than the engineer's, because the PM's is the only seat holding a
duty that is *defined* by this table.

```yaml
      NEON_RO_URL: ${{ secrets.NEON_RO_URL }}
```

Verified this run: `agent-pm.yml` does not contain `NEON_RO_URL`, and
`agent-research.yml`, `agent-writer.yml` and `agent-skill.yml` each do.

**Why the PM's need is the sharper one.** Guardrail 4 of
[delivery-health.md](delivery-health.md) defines the press's delivery
evidence as the newest row in `digests`, and assigns the daily watch to
the PM's standup. That seat has never been able to run the query. Every
standup since 2026-09-24 says so in the file, honestly, and substitutes
`libraryofalexandria.dev/library`, which is a weaker signal in the
direction that matters: a row written and never sent, a send that failed
after the row landed, and a page served from cache all read as healthy
there, and those are the three failures the guardrail exists to catch.
The full finding is in [unowned-duties.md](unowned-duties.md) under the
2026-09-27 rows, where it is the first example of a duty that passes the
wording, cadence and scope tests and fails on capability.

**Apply both at once.** They are one decision about one existing secret
reaching two more seats, and applying one without the other leaves the
question half answered. The scope note below covers both.

**Why it is queued rather than proposed.** The engineer charter's Observe
step assigns this seat pipeline health, and two ledger entries marked
`urgent` both reduce to one SQL query against the database of record. The
oldest asks whether the newsletter has sent once in eleven days, which is
a question about whether subscribers have been getting anything. Four
engineer runs have now written down that they could not run it. The
repeat is recorded in [incidents.md](incidents.md) under 2026-09-23.

**Scope, so the reader can judge the risk.** Read-only, no write path,
and no secret value ever reaches a PR. It does widen what a compromised
run can read, and from three seats to five, which is the honest cost and
the reason it is the owner's call rather than this seat's. Say no and the
right consequence is not that the guardrail stays as it is: it is that
`delivery-health.md`'s press row gets marked unwatched and the PM stops
being asked for a number it cannot get.

### 7. The ExO seat's own prompt grants it a lane the runtime refuses

**Queued 2026-09-27 by the ExO agent.** Found by the check in §2 of that
charter, which compares each seat's `prompts/<seat>-agent.md` against the
inline `prompt:` block in its workflow, and which this charter requires
whenever a run edits its own boundaries. This run edited §5.

**Why.** `.github/workflows/agent-exo.yml` tells the seat to

```
            orchestrate them as edits to the agent layer only (charters,
            agent workflows, org docs, your own charter included)
```

and `agent workflows` is not a lane this seat has. The push is refused,
verified again this run on a throwaway branch:

```
! [remote rejected] exo-probe-throwaway -> exo-probe-throwaway (refusing
to allow a GitHub App to create or update workflow
`.github/workflows/agent-exo.yml` without `workflows` permission)
```

The inline prompt arrives last and closest, so a run that believes it will
spend turns discovering incident 12 for itself. This is the same class as
item 4a, in the opposite direction: 4a is a prompt forbidding a duty the
charter grants, and this is a prompt granting a lane the runtime denies.

**How.** One edit to `.github/workflows/agent-exo.yml`, in the inline
prompt.

```diff
             decide at most three evidenced improvements, orchestrate them as
-            edits to the agent layer only (charters, agent workflows, org
-            docs, your own charter included), and write the learning log.
+            edits to the agent layer only (charters, org docs under
+            docs/agents/, and your own charter). You cannot push
+            .github/workflows/: queue edits to existing workflows as diffs
+            in docs/agents/pending-workflow-changes.md, and commit new
+            workflow files to .github/workflows-pending/ for a hand to move.
+            Then write the learning log.
```

Verified this run: the three `-` lines appear exactly once each in the live
file, at the prompt block. The seat's other prohibition list in that
prompt is consistent with the charter and is left alone, with one omission
worth noting rather than fixing: the prompt does not carry the charter's
"never set the ideas ledger's statuses", which is a narrowing the charter
supplies and the prompt does not contradict.

**Cost.** Six lines in one file, $0. It saves a run the turns it currently
spends rediscovering a four-week-old incident, and it is the only place a
seat is told the second lane exists at the moment it needs it.

**Ordering.** **Corrected 2026-10-04.** This said "independent of every
other item on this page", which stopped being true when item 14 was queued
against `agent-exo.yml`. Item 14 edits the `claude_args` line and this item
edits the `prompt:` block, so neither anchor moves the other and either
order works. Same shape as item 6's correction above, same run, same cause.

### 8. Every seat run reports onto the board

**Renumbered from 5 to 8 on 2026-10-04**, because this page carried two
items numbered 5 and the owner applies these by hand. The other 5 is the
HQ-origin notice above. Nothing else about this item changed. This is the
second time the page has had to do this, after the two items numbered 4
on 2026-09-27, and the cause is the same allocator the ADR numbers have
collided on four times: a run reads the page, takes the next number it
sees, and another run on another branch takes the same one. Numbers on
this page are now allocated by reading every `###` heading, not the last
one.

**Rewritten 2026-09-28.** The step is unchanged in shape and the diff below is
still one line, but everything this entry said about *why* it was safe was
written against a board that no longer exists. On 2026-09-26 the board was a
ref in this repository and the step's risk was a public ref and a contents-API
write. On 2026-09-27 the owner stood up the real board at
board.libraryofalexandria.dev and put `BOARD_API_URL` and
`BOARD_RUNTIME_TOKEN` into all twelve workflows herself, and `tools/board.py`
is now a client of it (ADR-2026-09-28-board-client). Reading the old version of
this entry and applying it would have been correct by accident: the command is
the same, the reasoning under it was wrong.

One step, identical in all twelve `.github/workflows/agent-*.yml`, placed
immediately after the existing `Post run report` step that writes to Slack:

```yaml
      # The board (docs/board.md), which pm.md §14 makes the state of the work.
      # Slack is the owner's window; the board is the org's state, and it is the
      # one a seat can read back next run. This step cannot fail the job:
      # tools/board.py prints ::warning:: and exits 0 when the board refuses,
      # because a red job for an undelivered report is the lie
      # INC-2026-09-26-run-report-dash-echo told six times.
      - name: Post run report to the board
        if: always()
        run: python3 tools/board.py report --status ${{ job.status }}
```

**It needs nothing new, and this time that is the owner's own doing.** Commit
6820ac1 already put `BOARD_API_URL` and `BOARD_RUNTIME_TOKEN` in every one of
the twelve `env:` blocks. Those two are all `tools/board.py report` reads
beyond what GitHub sets for free, plus `GH_TOKEN` for the pull request lookup,
which all twelve already have. Verified by reading the twelve files on main.

**Apply it whenever.** The old ordering caveat is void: there is no
`board/views.json` to wait for. Applied against a board that is down, the step
prints a warning and exits 0.

**Scope, so the reader can judge the risk.** The tool posts one row to
`POST /api/runs` on the owner's board and writes nothing in this repository. It
calls no model and spends nothing. What it widens is who can see a run: the
board is behind Caddy basic auth rather than public, so this is narrower
exposure than the old ref, which was world-readable because this repository is.

**One thing to know before applying it, because it cannot be undone.** The
board's server implements GET and POST only; PATCH, PUT and DELETE answer 501.
Run rows are permanent. The step runs under `if: always()` and posts exactly
once per job, so that is fine in the normal case, but a *re-run* of a job files
a second row for the same run, and no one can remove it. If that turns out to
matter, the fix is a check on `run_url` before the post, and it belongs in
`tools/board.py` rather than in the step.

**Smoke-tested before it was queued**, which is what
[runtime-changes.md](runtime-changes.md) asks of a change to what a scheduled
job does. The engineer run of 2026-09-28 ran the exact command the step runs,
against the live board, and its row is on `alexandria`'s board with this run's
pull request url and its one-line report. The `--dry-run` form was run first,
which is the only rehearsal a permanent write admits.

---

### 9. One run of a seat at a time, enforced by the runtime instead of by prose

**Queued 2026-09-26 by the engineer seat.
INC-2026-09-26-engineer-run-twice-in-one-window.**

Two engineer runs executed at once tonight, a scheduled one at 01:26:48Z and a
dispatched one at 01:30:18Z. Both opened a pull request, both wrote the same
five files, and both independently wrote the same two incident entries, one of
which had to be deleted at merge. Nothing was lost, because the charter's "your
own last run may still be open" rule made the second run branch from the
first's tip. What the rule cannot do is stop the duplicated work.

The guardrails that exist are all one layer above the runtime. The PM's charter
§4 forbids dispatching into a seat with an open pull request, and neither of
these was the PM's: one was a cron and one was the owner's. `gh workflow run`
asks no questions, and GitHub queues nothing, because no workflow declares a
concurrency group.

**The change, one block per seat workflow**, in all twelve `agent-*.yml`:

```yaml
concurrency:
  group: agent-engineer          # the seat's own name, one group per seat
  cancel-in-progress: false      # queue the second run, never kill the first
```

`cancel-in-progress: false` is the load-bearing half. A cancelled run is
incident 3 again, a run that dies with work in the sandbox, and
INC-2026-09-24-writer-dispatch-started-twice was a cancellation. Queuing costs
a delay and loses nothing.

**What it does not fix.** A queued run still starts eventually, and it starts
against a branch its sibling has since moved. That is the charter's pre-flight
rule's job, and it works. This item only stops the two runs from being alive at
the same moment.

**Not smoke-testable from a seat**, because the seat cannot push the file to
test it. The lowest-risk order is one seat first, `agent-engineer.yml`, whose
double run is the one with evidence behind it, and the other eleven after a
day of it behaving.

---

**Ordering.** **Added 2026-10-04; this item shipped with no ordering
paragraph at all, which is the third shape of the same defect and the
quietest.** A rotted paragraph is at least visible once someone looks. A
missing one gives a reader nothing to check and no signal that there was
anything to check. This item edits `agent-engineer.yml` and the other
eleven agent workflows' step bodies; items 6 and 14 edit the `env:` block
and the `claude_args` line of the same files, and item 10 edits the run
report step. Any order works.

### 10. The run report calls a tested script, because dash's echo ate the body

**Queued 2026-09-26 by the engineer seat.
INC-2026-09-26-run-report-dash-echo. Still live on main on 2026-09-28, two days
later, and it has now failed six consecutive engineer runs.**

The `Post run report` step added to all twelve `agent-*.yml` on 2026-09-26 at
01:14 and 01:23 UTC declares no `shell:`, so it runs under the container's
`sh`, which is dash. Dash's builtin `echo` expands backslash escapes. Every
`\n` that `gh pr list --json body` correctly escaped inside the pull request
body became a real newline before `jq` read it, so `jq` rejected its own input
and the step exited 4.

**Corrected 2026-09-28: it is two workflows, not twelve.** This entry said "all
twelve workflows, on every run," which overstated it and is worth fixing
because the number is what tells the owner how urgent this is. Only
`agent-engineer.yml` and `agent-frontend.yml` declare a `container:`, and the
container image is where `sh` is dash. The other ten run on the runner host,
where GitHub's default shell for a `run:` step is bash and `echo` leaves the
escapes alone. Checked by reading all twelve for `container:` and `shell: bash`
and by reading the conclusions: every `pm-agent`, `writer-agent`, `okr-agent`
and `exo-agent` run since the step landed is `success`.

It is deterministic for any pull request body containing a newline, which is all
of them, so those two workflows fail every single run. Six engineer runs so far,
every one of which finished its work and opened its pull request first:

| run | date | PR opened | conclusion |
|---|---|---|---|
| 36208446311 | 2026-09-26 01:26Z | #115 | failure |
| 36208644267 | 2026-09-26 01:30Z | #116 | failure |
| 36250253554 | 2026-09-26 14:57Z | #118 | failure |
| 36285149176 | 2026-09-27 01:18Z | #120 | failure |
| 36330209631 | 2026-09-27 15:36Z | #122 | failure |
| 36342225307 | 2026-09-27 18:51Z | #124 | failure |

The log of the last one is the same line as the first: `parse error: Invalid
string: control characters from U+0000 through U+001F must be escaped at line
177, column 1`, then `Process completed with exit code 4`. `agent-frontend.yml`
has not run since the step landed, so its first run will be its first failure.

**The cost is not the missing Slack message. It is the status.** A run that did
its whole job is recorded as `failure`, and run health is read off those
statuses by the PM's standup, by `docs/agents/delivery-health.md`, and by the
ExO's weekly audit. The engineer lane has read as six consecutive crashes for
two days while shipping a pull request every run.

**A one-character version of this fix exists, if the full one is too much to
apply today.** Adding `shell: bash` under `- name: Post run report` in
`agent-engineer.yml` and `agent-frontend.yml` alone stops the failures, because
bash's `echo` does not expand the escapes. It leaves the untestable shell in
place, which is the reason the real fix below is the real fix, but it is two
lines against twelve files' worth of replacement and it turns the engineer lane
green.

**The change, identical in all twelve `.github/workflows/agent-*.yml`.** Replace
the whole body of the `Post run report` step with one command:

```yaml
      # Visibility window (standards/operating-modes.md §3): the seat's run
      # report goes to the team's channel when the owner has created one.
      # Seats never read the channel; it is the owner's window only.
      #
      # The logic is in tools/run_report.py, not here, because shell embedded
      # in YAML cannot be tested and this step shipped broken to twelve
      # workflows at once (INC-2026-09-26-run-report-dash-echo). The webhook
      # guard stays inside the script for the reason the previous version's
      # comment gave: a step cannot read its own `env:` block from `if:`.
      - name: Post run report
        if: always()
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: python3 tools/run_report.py --workflow "${{ github.workflow }}" --status "${{ job.status }}"
```

**Why a script and not a two-character shell fix.** Adding `shell: bash` to the
step would fix this bug. It would not fix the class, and the class is the
expensive part: twenty lines of shell inside twelve YAML files that no test can
reach. `tools/run_report.py` has `compose()` as a pure function and eighteen
tests in `tests/test_run_report.py`, one of which is this exact body, and one of
which runs the script under `sh -e` so the container's shell is in the test
rather than in production. L-E0 asks for agents that can read and diagnose what
we build, and a seat can run this file and see its output.

**It needs nothing new.** No secret beyond `SLACK_WEBHOOK_URL`, which the step
already reads. No new permission. Python 3 and `gh` are both in the image and
both already used by other steps. Standard library only, so nothing to install.

**The behaviour is preserved exactly**, including both of the owner's rulings of
2026-09-26. The report is the pull request's own opening rather than a log line,
and it is the first five bullet lines, one line each, with `**` stripped, with a
fallback to the first two lines of prose when a body has no bullets. That
fallback is now proved by a test. In the shell version it was never reached.

**One deliberate behaviour change, and it is a fix.** The step can no longer
fail the job. A notification is not the run's work, and a red job for an
undelivered message is exactly the lie this incident is made of. Delivery
problems print as `::warning::` and the exit status stays 0. The report is also
printed into the run log, so the artifact exists even when the channel does not.

**Smoke-tested before it was queued**, as far as a seat can. Run against the
real `gh` API and the real body that broke production, under `sh -e`, which is
the exact shell the workflow gives a step with no `shell:` key:

```
$ sh -e -c 'echo "$pr" | jq -r ".title"'            # the live step's pipeline
parse error: Invalid string: control characters from U+0000 through U+001F
must be escaped at line 190, column 1
exit=4

$ sh -e -c 'python3 tools/run_report.py --status success \
    --workflow engineer-agent --branch engineer/2026-09-26-reasoning-rubric --dry-run'
{"text": "*engineer-agent* • success • Engineer 2026-09-26 (run 3): ...
exit=0
```

What a seat cannot test is the webhook itself, because no seat holds
`SLACK_WEBHOOK_URL`. The first real delivery is the chair's, on the first run
after this is applied. Everything a test can hold without the secret is held.

**Apply this before item 9 and before item 5.** It is the only item on this
page that is failing production runs as it sits here, and it is one line per
file.

---

**Ordering.** **Added 2026-10-04**, for the same reason item 9's was: this
item had none. It edits the run report step in all twelve agent workflows.
Items 6 and 14 edit the `env:` block and the `claude_args` line of the same
files, item 9 edits the concurrency block, and items 4a, 13 and 15 edit
`prompt:` blocks. None of those anchors touch a run report step, so any
order works.

### 12. The skill seat cannot measure a skill, because it has no `GROQ_API_KEY`

**Queued 2026-09-30 by the ExO agent, under the owner's directive of the
same day and ADR-38.** This is the capability half of the new row in
[unowned-duties.md](unowned-duties.md).

**Why.** ADR-38 makes a measured delta the gate on a skill's status, and
the seat that produces skills cannot produce a delta. `tools/skill_eval.py`
reaches its subject and judge through `pipeline/llm.py`, whose providers
are `moonshot` and `groq` in `pipeline/budget.py`. The measurement that
produced 5.4 against 5.3 used `qwen/qwen3.8-27b` as subject and
`openai/gpt-oss-120b` as judge, and `budget.MODELS` gives both of them
`"provider": "groq"`. So the arm needs `GROQ_API_KEY`:

```bash
grep -oE 'secrets\.[A-Z_]+' .github/workflows/agent-skill.yml | sort -u
# BOARD_API_URL BOARD_RUNTIME_TOKEN CLAUDE_CODE_OAUTH_TOKEN
# NEON_RO_URL PROJECTS_TOKEN SLACK_WEBHOOK_URL
grep -rlE 'secrets\.GROQ_API_KEY' .github/workflows/     # nothing
```

No workflow in the repository carries it. The key itself exists as the
Modal secret named `groq`, which is where the daily pipeline reads it, so
this is a secret to add at the repository level rather than a credential to
obtain, and the owner is the only one who can say whether exposing it to a
seat sandbox is acceptable.

**How.** One line in the `env:` block of
`.github/workflows/agent-skill.yml`, after `NEON_RO_URL`.

```diff
       NEON_RO_URL: ${{ secrets.NEON_RO_URL }}
+      GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
```

**Ordering.** **Corrected 2026-10-04.** This named item 11, which was
deleted and replaced by item 14 in that run. Item 14 touches the
`claude_args` line of this file and raises the skill cap to 350 rather than
200. Item 13 touches the `prompt:` block. This item touches the `env:`
block. All three can be applied in one hand, in any order.

**Cost.** $0. The groq free tier is what the daily pipeline already runs
on, and `budget.MODELS` prices both models at 0.0 in and 0.0 out. The rate
limits are the real constraint (8,000 tpm, 30 rpm, 1,000 rpd) and an eval
run of four tasks at two arms and two repetitions fits inside them.

**What this does not fix, and the owner should know it before applying.**
ADR-38 clause 6 makes `status: active` depend on a delta measured on the
model the product is actually used with, and there is no route to that
model at all: `pipeline/budget.py` has two providers and neither serves
it, and `grep -in anthropic pipeline/` returns nothing. That is pipeline
work on the engineer's surface, not a secret, and it is filed in
docs/ideas.md. Applying this item lets the seat run the cheap arm and
report a provisional number. It does not let the seat mark a skill active
under ADR-38 as written.

---

### 13. The skill seat's dispatch prompt names the trigger test and no measurement

**Queued 2026-09-30 by the ExO agent.** This is the §2 charter-versus-prompt
check, run because this PR edits that charter's run section. It is incident
25's shape exactly: a duty the charter has that the inline prompt omits.

**Why.** Every seat's charter is two files. There is
`prompts/skill-agent.md`, which the seat can edit, and there is the inline
`prompt:` block in `.github/workflows/agent-skill.yml`, which it cannot. The
inline prompt arrives last and closest, so when the two disagree the run most
likely obeys the workflow. The live block says:

> draft one evidence-backed skill under skills/ with provenance frontmatter
> and claim-id citations, include the trigger test in the PR

**The trigger test is the only evidence the dispatch asks for.** After this
PR the charter requires a differential eval suite, a bare-first pass, a
measured delta and a status decision, and the prompt still names the one
measurement that cannot say whether a skill helps. It also predates ADR-37,
so it says nothing about maintenance coming before creation, and it predates
ADR-35's reading requirement in everything but spirit.

A seat reading both files has to guess which one governs. That guess is what
incident 25 cost when the writer's prompt forbade the duty its charter
assigned, and that item (4a) has been on this page since 2026-09-21.

**How.** Replace the prompt body between `prompt: |` and the
`Owner instructions` line in `.github/workflows/agent-skill.yml`. This is an
edit to an existing workflow, so it stays a diff on this page rather than a
full file in the pending lane.

```diff
-            skills/ with provenance frontmatter and claim-id citations,
-            include the trigger test in the PR, and open exactly one pull
-            request on a branch named skill/YYYY-MM-DD-slug with `gh pr
-            create`. Write only under skills/, prompts/skill-extract.md,
+            skills/ with provenance frontmatter and claim-id citations.
+            Maintenance comes before creation (ADR-37): read every new
+            consumer report under skills/*/reviews/ and the reading queue
+            first. Meet the bar in the charter's "the bar a skill has to
+            clear" section (ADR-38): deltas the bare model does not already
+            give, procedures with their thresholds, the checklist first,
+            under 120 lines. Ship the skill's differential eval suite with
+            it and put the measured delta in the PR, or write the word
+            unmeasured and say which credential is missing. A trigger test
+            says the skill is found and never that it helps, so report both
+            and never one as the other. Open exactly one pull
+            request on a branch named skill/YYYY-MM-DD-slug with `gh pr
+            create`. Write only under skills/, prompts/skill-extract.md,
```

**Ordering.** Independent of items 12 and 14, which touch the `env:` block
and the `claude_args` line of the same file. All three can be applied in
one hand. **Corrected 2026-10-04:** this paragraph named item 11, which
was deleted and replaced by item 14 in that run, and the skill cap it
proposed changed from 200 to 350. An ordering paragraph that names a
deleted item is the same rot as one that misses a live item, and the
sweep that finds both is the `grep -oE '\.github/workflows/[a-z-]+\.yml'`
count in `prompts/exo-agent.md` §5.

**Cost.** $0, and it will raise the seat's turn demand, which is why the
skill seat's cap is re-measured in item 14 rather than left at 180.

---

### 12. Skill registration, checked on the pull request that adds a skill

**Queued 2026-09-30 by the engineer seat. ADR-36 part 1.**

Numbered 12 because 11 is the highest on this page today, and this page has
carried two items numbered 4 before, so the number is stated rather than
counted.

ADR-36 asks for "a check that fails when a skill on main has no row". That check
has to be in two halves, and the split is not a weakening.

The database half cannot run in GitHub Actions. This organization runs no
Postgres in CI, and CI holds no credential for the production one, which is the
same reason `tools/graph_audit.py`'s ten SELECTs are parsed rather than executed
in `checks.yml`. So the half that asks whether the row is actually in Neon runs
in `pipeline/skill_revision.py`, daily, where the `neon` secret already is, and
it repairs what it finds rather than only reporting it.

The half CI can run is the one that catches the failure mode ADR-36 actually
found. A skill cannot be registered when its provenance block cannot be read:
no `provenance:` map, no claim ids, a claim id that is not a number, a `name:`
that disagrees with its directory, a directory with no SKILL.md. Every one of
those ships green today and silently opts the skill out of revision forever.
`python3 tools/skill_registrar.py --files-only` exits 1 on each of them and
needs no database, no key and no network.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. `skills/**` and `db/schema.sql` are already in both `paths`
lists; these two lines go in both of them, beside the existing `tools/` entries
(verified against the live file this run: it carries `tools/board.py`,
`tools/run_report.py` and `tools/graph_audit.py` in that order, in both lists).

```yaml
      - "tools/skill_registrar.py"
      - "tests/test_skill_registrar.py"
```

Second, the step. It goes after the existing `the graph audit's SQL still
matches the schema, and still only reads` step, which is the last step in the
`digest-budget` job today.

```yaml
      # 2026-09-30, ADR-36 part 1. `skills_needing_revision` has been in
      # db/schema.sql since the founding and has never returned a row, because
      # the skill seat writes a SKILL.md and nothing writes the promotions row
      # the view joins. Seven claims are deprecated and no skill knows.
      #
      # Two things are held here. The registrar's three statements are parsed
      # with libpg_query and every relation and column resolved against
      # db/schema.sql, because no CI job in this organization can execute SQL
      # and a renamed column would otherwise turn a daily cron silently
      # useless. And every skill on the branch must be registrable: the failure
      # this catches is a merged skill whose provenance block cannot be read,
      # which ships green and opts that skill out of revision forever.
      - name: every skill can be registered, and the registrar's SQL matches the schema
        if: always()
        run: python3 -m pytest tests/test_skill_registrar.py -q

      - name: no skill on this branch is missing its provenance
        if: always()
        run: python3 tools/skill_registrar.py --files-only
```

**Smoke-tested from the seat, as far as a seat can.** Both commands were run in
this run's sandbox against the real six skills: the pytest step is 31 passed,
and `--files-only` exits 0. Both were also confirmed to fail on purpose, the
pytest step against a deliberate `promotionz` typo in the registrar's SQL and
the `--files-only` step against a fixture skill with an empty claims array. The
step cannot be smoke-tested on a branch as a workflow, because the seat cannot
push the file.

**Cost.** $0. No key, no network, no database.

### 13. The file that installs the suite's Modal stub triggers no check at all

**Queued 2026-09-30 by the engineer seat.**

Numbered 13 because 12 is the highest on this page today. Item 12 is queued
ahead of this one and both add a step after the graph-audit step, so whoever
applies them should apply 12 first and then append this one; if only one is
applied, either order works, because neither touches the other's lines.

**The hole.** `checks.yml` names fourteen test files in its two `paths` lists.
`tests/conftest.py` is in neither, and no job in any workflow runs the whole
suite. So a change to the one file that installs the Modal stub for every test
module in the repository triggers nothing. That file's own docstring records
what a bad version of it costs: four test files each carried their own copy of
the stub, the copy without `modal.Volume` won under `pytest tests/ -q`, and
"the whole suite reported a single error and ran nothing". A file with that
failure mode and no path entry is the gap this item closes.

`requirements-dev.txt` has the same shape and is deliberately left out of this
item: it is a version floor rather than logic, and a stale item is worse than a
narrow one.

**What the new test file is.** `tests/test_check_helper_is_enforced.py`, added
in the same pull request as this item. `tests/test_press_resilience.py` and
`tests/test_press_rehearsal.py` report failures by appending to a module-level
`FAILURES` list rather than by asserting, and only their `__main__` block reads
that list. Under `python3 -m pytest tests/ -q`, the command
`requirements-dev.txt` prescribes and both files' docstrings name, roughly 130
checks printed `FAIL` to a swallowed stdout and the suite said green. A hook in
`tests/conftest.py` now enforces the list under pytest as well.

CI reads those two files' exit codes today, because it runs them as scripts, so
the hook changes nothing about today's CI verdict and this item does not pretend
otherwise. What it buys is the day either file grows a pytest fixture, which is
the direction this suite has been moving all week: the moment one of them needs
`monkeypatch` or `capsys` it has to be run under pytest, and without the hook
that move silently retires 130 checks while every step stays green.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. These two lines go in both `paths` lists, after the existing
`tools/graph_audit.py` entry, which is the last entry in each list. Verified
against the live file this run: `      - "tools/graph_audit.py"` matches exactly
twice, once per list, and `tests/conftest.py` appears zero times in the file.

```yaml
      - "tests/conftest.py"
      - "tests/test_check_helper_is_enforced.py"
```

Second, the step. It goes at the end of the `digest-budget` job. The live file's
last three lines are the graph-audit step, verified this run:
`run: python3 -m pytest tests/test_graph_audit.py -q` matches exactly once.

```yaml
      # 2026-09-30. Two files in tests/ report failures by appending to a
      # module-level FAILURES list, and until today only their __main__ block
      # read it. Under `python3 -m pytest tests/ -q` every one of their ~130
      # checks printed FAIL to a stdout that -q swallows and the suite reported
      # green. That is how test_call_model_walks_and_backs_off came to assert a
      # contract the press stopped honouring on 2026-09-24 and go unnoticed:
      # the only reason it was ever caught is that this workflow happens to run
      # its file as a script.
      #
      # The hook lives in tests/conftest.py, which is the other half of this
      # item. That file installs the Modal stub for every test module here and
      # had no path entry, so a change to it triggered no check at all, and its
      # own docstring records a bad version of it making the whole suite collect
      # zero tests. These tests run pytest in a subprocess against throwaway
      # modules using the pattern, so they fail if the hook is deleted rather
      # than passing vacuously. Confirmed both ways from the seat.
      - name: the check() helper is enforced under pytest, not only as a script
        if: always()
        run: python3 -m pytest tests/test_check_helper_is_enforced.py -q
```

**Smoke-tested from the seat, as far as a seat can.** The command is 6 passed in
this run's sandbox, and 2 failed, 4 passed with the hook deleted from
`tests/conftest.py`, which is the only result that proves the tests are load
bearing. The step cannot be smoke-tested as a workflow, because the seat cannot
push the file.

**Cost.** $0. No key, no network, no database. The step adds about three seconds,
which is what a subprocess pytest costs six times over.

### 14. The deploy-drift guard runs in CI, so its own logic is under test

**Queued 2026-09-30 by the engineer seat, sprint 2026-09-28 item 2.**

Numbered 14 because 13 is the highest on this page today. Items 12, 13 and 14
all append a step at the end of the `digest-budget` job and two lines to each
`paths` list, and none of them touches another's lines, so any order works. If
all three are applied, applying them in number order keeps the file readable.

**What this protects.** `tools/delivery_health.py` grew a fifth surface,
`deploy`, which answers the one question none of the other four can: is the
code on main the code the crons are running. `modal deploy` bakes the
repository into an image, so a merge and a deploy are two events, and the gap
between them has cost the org twice. Incident 24 is the first. PR #110 is the
second, merged 2026-09-26 and inert for days while three documents described
its behaviour as live.

The guard's own logic is the kind CI exists to hold, because the way it fails
is by crying wolf. A seat's sandbox nearly always has uncommitted edits under
`pipeline/`, a branch carries commits that never merged, and a shallow clone
cannot date anything. All three must answer `unknown` rather than red, and a
change that quietly turned one of them into a verdict would make the standup
red every morning for a reason that resolves itself, which is how a report
teaches its reader to stop reading it.

**What the new test file is.** `tests/test_deploy_drift.py`, added in the same
pull request as this item. It builds a real git repository in a temporary
directory, because the dating and dirty-tree logic is `git log` and
`git status`, and mocking those would test the mock. No network, no database,
no Modal. `tests/test_delivery_health.py` joins the same step: its surface list
changed in this pull request and nothing in CI runs it today.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. These three lines go in both `paths` lists, after the
existing `tools/graph_audit.py` entry, which is the last entry in each list.
Verified against the live file this run: `      - "tools/graph_audit.py"`
matches exactly twice, once per list, and neither `tools/delivery_health.py`
nor `tests/test_deploy_drift.py` appears anywhere in the file.

```yaml
      - "tools/delivery_health.py"
      - "tests/test_deploy_drift.py"
      - "tests/test_delivery_health.py"
```

`pipeline/runtime_sha.py` needs no entry: `pipeline/**` already covers it, and
that is deliberate rather than lucky, because the digest this guard compares is
derived from the three job modules and moves whenever they do.

Second, the step. It goes at the end of the `digest-budget` job. The live
file's last three lines are the graph-audit step, verified this run:
`run: python3 -m pytest tests/test_graph_audit.py -q` matches exactly once.

```yaml
      # 2026-09-30, sprint 2026-09-28 item 2. The deploy-drift guard. Each of
      # triage, interpret and weekly now records a digest of the files it is
      # actually running from, and tools/delivery_health.py computes the same
      # digest from the checkout and compares. CI cannot run the guard against
      # production, because the recorded side lives in Neon and this org runs no
      # database in CI. What CI holds is the judgement, which is the half that
      # can rot: that a drift under a day reads as a pending deploy rather than
      # an alarm, that an uncommitted edit and an undatable checkout both answer
      # unknown rather than red, that a job which has never reported is never
      # green, and that the recording call cannot raise or abort the transaction
      # of the job it guards. The last one is why this is not optional: a
      # guardrail that can fail a production run is worse than no guardrail.
      - name: a stale deploy trips the alarm, and a real deploy clears it
        if: always()
        run: python3 -m pytest tests/test_deploy_drift.py tests/test_delivery_health.py -q
```

**Smoke-tested from the seat, as far as a seat can.** Both files pass in this
run's sandbox, as does the whole suite (638 passed, 9 skipped). The two
acceptance tests were confirmed to be load bearing by inverting the fixture:
with the recorded digest set to the current one the surface is green, and with
it set to a stale value on a checkout whose last commit is nine days old the
surface is red and names all three jobs. The step cannot be smoke-tested as a
workflow, because the seat cannot push the file.

**Cost.** $0. No key, no network, no database. The step adds about two seconds.

### 15. The delivery receipt runs in CI, so the endpoint cannot leak the product

**Queued 2026-10-01 by the engineer seat**, with the credential-free reader for
guardrail 4.

Numbered 15 because 14 is the highest on this page today. **It composes with
item 14 and does not depend on it.** Both add lines to the same two `paths`
lists and a step at the end of the same job, and neither touches the other's
lines, so either order works and either alone works. If both are applied, item
14's step and this one can be left as two steps; they test different files and
two names in the CI log are easier to read than one.

**What this protects.** `site/app/api/delivery/route.js` is a public,
unauthenticated endpoint that reads the production database. That sentence is
the whole reason this item exists. It is public on purpose, because no agent
seat holds a database credential and the receipt is what lets every seat answer
guardrail 4's question at all, and the price of that decision is that the
boundary between metadata and product has to be held by something that runs on
every change.

Two of the tests are the boundary itself. One asserts that the queries never
select `digests.body` or any claim text and never touch `subscribers`, and that
the only tables read are the four this answers for. The other builds a receipt
from a row that carries a body, a `prompt_sha` and an invented column, and
asserts that none of the three appears in the JSON, because every field is built
by name. A future change that widens a query, or spreads a row into the response
for convenience, publishes the paid product. That change would be two
characters long and it would look like a simplification.

The rest hold the states. A receipt this reader cannot understand, a version it
does not speak, a 404 from a route that is not deployed yet and a site that does
not answer must every one of them answer `unknown`, never a verdict about the
press, which is the argument `tools/delivery_health.py` already makes for its
own third state. And one test asserts the property that keeps the two readers
honest: a connection and a receipt carrying the same rows produce the same
state and the same headline, word for word, differing only in `read_via`.

**What the new files are.** `tests/test_delivery_receipt.py` (20 tests) and
`tests/delivery.test.mjs` (10 executed cases), both added in the same pull
request as this item. The Python file runs the `.mjs` file in a subprocess, the
way `tests/test_accounts.py` runs `tests/accounts.test.mjs`, so one pytest
command still covers the whole path and the `node` half degrades to a skip where
`node` is absent. No network, no database, no site: the only thing stubbed is
`dh.fetch`.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. These five lines go in both `paths` lists, after the existing
`tools/graph_audit.py` entry. Verified against the live file this run:
`      - "tools/graph_audit.py"` matches exactly twice, once per list, and none
of these five paths appears anywhere in the file. (Corrected 2026-10-01, second
window, same seat: this sentence said `tools/graph_audit.py` was the last entry
in each list and it is not. Three entries follow it, `db/schema.sql`,
`site/emails/digest.html` and `.github/workflows/checks.yml`. The instruction is
unchanged, because inserting after a line that matches exactly twice does not
depend on that line being last, but a hand reading "last entry" and finding
three more would have had to stop and work out which text to trust.)
If item 14 is applied first, these go after its three lines; the order inside
the list does not matter.

```yaml
      - "tests/test_delivery_receipt.py"
      - "tests/delivery.test.mjs"
      - "site/lib/delivery-core.js"
      - "site/lib/delivery.js"
      - "site/app/api/delivery/route.js"
```

The three `site/` entries are the point of the paths half. The tests read those
three files as source, so a change to the endpoint has to re-run them, and that
is exactly the change nobody will think to test.

Second, the step. It goes at the end of the `digest-budget` job. The live file's
last three lines are the graph-audit step, verified this run:
`run: python3 -m pytest tests/test_graph_audit.py -q` matches exactly once.

```yaml
      # 2026-10-01. The delivery receipt. `tools/delivery_health.py` answers
      # three of its five surfaces from a public endpoint now, because no agent
      # seat holds a database credential and that is why guardrail 4 went
      # unenforced for a week. The endpoint reads production and answers anyone,
      # so the boundary between metadata and product is held here: these tests
      # assert that no query selects the issue body or a claim, and that a row
      # carrying one anyway cannot escape through the shaping layer, which
      # builds every field by name. They also hold the third state, since a
      # receipt this reader cannot parse must answer `unknown` and never a
      # verdict about the press, and the property that keeps two readers from
      # becoming two answers: a connection and a receipt carrying the same rows
      # reach the same state and the same headline.
      - name: the delivery receipt publishes metadata and never the product
        if: always()
        run: python3 -m pytest tests/test_delivery_receipt.py -q
```

**Smoke-tested from the seat, as far as a seat can.** Both files pass in this
run's sandbox, as does the whole suite (668 passed, nothing skipped, with
`requirements-dev.txt` and `tiktoken==0.8.0` installed as this workflow installs
them). The harness was
confirmed load bearing against an artifact known to fail it: inverting one
assertion in `test_an_unreadable_database_is_a_503_and_not_an_empty_receipt`
turns `python3 -m pytest tests/test_delivery_receipt.py -q` red with the check's
own name in the report, and reverting it turns it green again. The step cannot
be smoke-tested as a workflow, because the seat cannot push the file.

**Cost.** $0. No key, no network, no database. The step adds about a second,
plus `node --test`, which needs no `npm install` because the module under test
has no imports.

**The fourth item on this page that is one more filename in two lists.** Items
12, 13, 14 and now 15 are all the same two-line hand edit, and
`INC-2026-09-29-receipts-step-had-no-paths` is what the pattern costs when the
hand adds the step and forgets the list. The ledger entry from 2026-09-30,
"checks.yml should run the suite, not fourteen filenames", is the structural fix
and it would delete this half of all four items.

### 16. The archive publishes the record, and that is checked on the pull request

**Queued 2026-10-01 by the engineer seat (second window)**, with the change
that makes a Monday send public on Monday.

Numbered 16 because 15 is the highest on this page today. **It composes with
items 14 and 15 and depends on neither.** All three add lines to the same two
`paths` lists and a step at the end of the same job, none of them touches
another's lines, so any order works and any one alone works.

**What this protects.** `site/lib/issues-live.js` decides which weeks the public
archive publishes, from the `digests` table rather than from files committed by
hand. The archive is the product's shop window and the issue is the free half of
what the company sells, so three properties now stand between a change to that
file and a public page, and every one of them is a way this could go wrong
quietly rather than loudly.

A database that cannot be read must publish exactly what the committed files
publish. That is the difference between a Neon outage being invisible and a Neon
outage emptying the archive, and the test drives it twice, once with no
connection and once with a query that throws.

`HIDDEN_WEEKS` must still retire a week that exists only as a row. That set is
the owner's veto over the archive (2026-W37, retired on her order 2026-09-19)
and the record is a second way in, so a row must not be able to walk past it.

The committed file must win over the row for a week that has both. Every
correction already made to a published issue lives in those files: the 2026-09-19
corrections to 2026-W37, the 2026-09-24 reprint of 2026-W39 under canon law 14.
A change that reversed this precedence would silently revert all of them, and it
would look like a simplification.

Two more are worth naming because they are about the query rather than the
rules. The week comes out of the URL, so one test asserts it is interpolated and
never concatenated, and that a week which does not match `^\d{4}-W\d{2}$` never
reaches the database at all. And the listing query reads only the first 4,000
characters of each body, so the shaping layer drops `body` from the listing
shape entirely: a page that rendered it would be showing a truncated issue as a
whole one.

**What the new files are.** `tests/test_issue_route.py` (7 tests, 23 checks) and
`tests/issues.test.mjs` (19 executed cases), both added in the same pull request
as this item. The Python file runs the `.mjs` file in a subprocess, the way
`tests/test_delivery_receipt.py` runs `tests/delivery.test.mjs`, so one pytest
command covers the whole path and the `node` half degrades to a skip where
`node` is absent. No network, no database, no `npm install`: the module under
test has no imports, which is why the queries live in it.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. These six lines go in both `paths` lists, after the existing
`tools/graph_audit.py` entry. Verified against the live file this run:
`      - "tools/graph_audit.py"` matches exactly twice, once per list, and none
of these six paths appears anywhere in the file. If items 14 or 15 are applied
first, these go after their lines. The order inside the list does not matter.

```yaml
      - "tests/test_issue_route.py"
      - "tests/issues.test.mjs"
      - "site/lib/issues-core.js"
      - "site/lib/issues-live.js"
      - "site/lib/content.js"
      - "site/app/library/**"
```

The four `site/` entries are the point of the paths half, and `site/lib/content.js`
is there for a reason worth stating: the record's bodies are parsed by that
file's `parseIssue`, which is now exported so there is one derivation rule
rather than two, and a change to it moves every title and excerpt in the
archive.

Second, the step. It goes at the end of the `digest-budget` job, after the
graph-audit step, which is the last step in the live file: `run: python3 -m
pytest tests/test_graph_audit.py -q` matches exactly once and is the file's last
line.

```yaml
      # 2026-10-01. The archive reads `digests` now, so an issue is public the
      # moment the press mails it instead of whenever somebody remembers to
      # commit a markdown file. Three properties stand between a change to
      # site/lib/issues-live.js and a public page: a database that cannot be
      # read publishes exactly what the committed files publish, HIDDEN_WEEKS
      # still retires a week that exists only as a row, and the committed file
      # still wins the text of any week that has one, which is what keeps every
      # correction already made to a published issue standing. The week comes
      # out of the URL, so the query half is held too.
      - name: the archive publishes the record, and fails closed to the files
        if: always()
        run: python3 -m pytest tests/test_issue_route.py -q
```

**Smoke-tested from the seat, as far as a seat can.** Both files pass in this
run's sandbox. The harness was confirmed load bearing against an artifact known
to fail it: changing one asserted string in `test_both_routes_read_the_record`
to one the route does not contain turns `python3 -m pytest
tests/test_issue_route.py -q` red with the check's own sentence in the report,
and reverting it turns it green again, which also exercises the `FAILURES` hook
in `tests/conftest.py` that makes a `check()` file legible to pytest at all. The
step cannot be smoke-tested as a workflow, because the seat cannot push the
file.

Separately and beyond what CI can hold, the route behaviour was measured against
a real production build of the site in this sandbox, because the change retires
a guard that existed to prevent a 500. `npm install && npx next build && npx
next start`, then six requests: `/` 200, `/library` 200, `/library/2026-W39` 200,
`/library/2026-W37` 404, `/library/2026-W01` 404, `/library/nonsense` 404. A
clean 404 on an unpublished week is the sentence the old guard was protecting,
and it holds without the guard because the route is dynamic from the start.

**One thing this item does not need to queue, verified rather than assumed.**
The same pull request adds a sixth surface to `tools/delivery_health.py`, the
`archive` comparison, with six tests in `tests/test_delivery_health.py`. Both of
those files are already queued into both `paths` lists and into a step by **item
14** above (`run: python3 -m pytest tests/test_deploy_drift.py
tests/test_delivery_health.py -q`), so applying item 14 covers them and this
item does not name them twice. If item 14 is never applied, those six tests run
under `python3 -m pytest tests/ -q` and nowhere in CI, which is the same hole
item 14 exists to close and not a new one.

**Cost.** $0. No key, no network, no database. The step adds under a second,
plus `node --test`, which needs no `npm install`.

**The fifth item on this page that is one more filename in two lists.** Items
12, 13, 14, 15 and now 16 are the same two-line hand edit five times over, and
`INC-2026-09-29-receipts-step-had-no-paths` is what the pattern costs when the
hand adds the step and forgets the list. The ledger entry from 2026-09-30,
"checks.yml should run the suite, not fourteen filenames", is the structural fix
and it would delete half of all five items. Five occurrences of one shape is no
longer a pattern worth noting, it is a backlog, so this run raises it from a
ledger line to a named recommendation to the owner in its pull request.

### 17. The site's XSS defence and the account layer run in CI, or checks.yml stops naming filenames

**Queued 2026-10-02 by the engineer seat**, from
`INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had`.

**Numbered 17 only relative to this branch, and the number is already wrong.**
`main` stops at item 11. Three open pull requests allocate numbers from 12
upward on this page right now and none of them can see the others: this seat's
chain takes 12 through 16, PR #174 takes 12 through 16 for five different
changes (action pinning, `PROJECTS_TOKEN`, the budget step, the no-ship
tripwire, the register checker), and PR #160 takes 12 and 13 for two more. After
all three merge, thirteen items will claim six numbers. That is incident 29's
sequential allocator, in the one register whose numbering was never converted to
slugs, and it is recorded this run as
`INC-2026-10-02-pending-queue-number-collision`. Read this item by its title,
not by its number, and expect to renumber at merge. It composes with every other
queued item and depends on none of them.

**What is wrong.** `tests/test_markdown.py` holds the 2026-09-19 finding, the
one where a crafted passage in an arXiv paper reached the public archive as live
HTML. Its docstring says of `tests/markdown.test.mjs`, "It needs no
node_modules, which is why it is the half that runs in CI." No workflow in this
repository runs either file. `site/lib/markdown-core.js`, which decides what
markdown is allowed to become on the public site, is in neither `paths` list, so
a pull request changing nothing but that file runs no check at all.

`tests/test_accounts.py` and `tests/accounts.test.mjs` are in the same position,
and they hold the account and entitlement layer.

Measured this run: `node --test tests/*.test.mjs` returns 122 pass, 0 fail, so
nothing is broken behind this. What is missing is the gate.

**The recommendation, which is the structural form.** Replace the fourteen named
pytest steps with one that runs the suite, and replace both `paths` lists with
the directories the suite covers. One step, one list, and items 12 through 16 on
this page lose their paths halves entirely:

```yaml
      - name: the test suite
        if: always()
        run: python3 -m pytest tests/ -q
```

This is the ledger entry of 2026-09-30, "checks.yml should run the suite, not
fourteen filenames", and this item is the sixth occurrence of the two-line hand
edit that entry exists to delete. Two things make it safe to do now that were
not true a week ago. `tests/conftest.py` enforces the `FAILURES` harness under
pytest since 2026-09-30, so the two script-mode files no longer go green by
default under a suite run (`INC-2026-09-30-check-harness-green-under-pytest`).
And the suite passes in full in this run's sandbox: 694 passed, 1 skipped, in 26
seconds. Keep the three script-mode invocations as they are if you want belt and
braces, because they cost under a second each.

**The minimal form, if the structural one is too large a change to make by
hand.** Four lines in both `paths` lists, after the existing
`      - "tools/graph_audit.py"` entry, which matches exactly twice in the live
file, once per list. None of these four appears anywhere in the file today,
verified this run:

```yaml
      - "tests/test_markdown.py"
      - "tests/markdown.test.mjs"
      - "site/lib/markdown-core.js"
      - "tests/test_accounts.py"
```

And one step at the end of the `digest-budget` job, after `run: python3 -m
pytest tests/test_graph_audit.py -q`, which matches exactly once and is the live
file's last line:

```yaml
      # 2026-10-02, INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had.
      # site/lib/markdown-core.js is the whole of the defence between a crafted
      # passage in an arXiv paper and live HTML on the public archive, and until
      # this step existed a pull request touching only that file ran no check.
      # The account layer is here for the same reason. Both files run their .mjs
      # half in a subprocess, so one pytest command covers each layer, and the
      # node half degrades to a skip where node is absent.
      - name: the archive refuses HTML, and the account layer holds
        if: always()
        run: python3 -m pytest tests/test_markdown.py tests/test_accounts.py -q
```

**Smoke-tested from the seat, as far as a seat can.** `python3 -m pytest
tests/test_markdown.py tests/test_accounts.py -q` passes in this sandbox, and
`node --test tests/*.test.mjs` passes at 122 of 122. The step cannot be
smoke-tested as a workflow, because the seat cannot push the file.

**Cost.** $0 either way. The minimal form adds under two seconds. The structural
form adds about 26 seconds and removes five pending items from this page.

**One thing this item deliberately does not do.** It does not add
`site/lib/account-core.js`, `site/lib/entitlement.js` or
`site/lib/markdown.js` to the minimal form's list, because the minimal form is
already the sixth instance of a pattern that this page says should be deleted
rather than extended, and a seventh filename argues the wrong way. The
structural form covers them by covering everything, which is the point.

**Update 2026-10-07, engineer seat: the structural form is now a file, and the
count in this item was low by a factor of eight.**

The file is `.github/workflows-pending/checks.yml`, written out in full, with
its own section in that directory's README. The apply is a force move, because
it replaces a live file rather than adding one:

    git mv -f .github/workflows-pending/checks.yml .github/workflows/checks.yml

This item named four test files. Measured by `python3 tools/ci_coverage.py`,
written the same run, the real number is **35 of the suite's 49**, counting the
two test files that run added. The four this item names are in it and so are
thirty-one others, among them
`tests/test_skill_eval.py`, `tests/test_reading_queue.py`,
`tests/test_oauth_redirect_uri.py` and `tests/test_delivery_health.py`. The
miss was not carelessness. The live file lists 24 `paths` entries against 14
steps against a directory of 47, and a filename in `paths` looks exactly like a
filename in a step while meaning the opposite thing, so the live file names
`tests/test_press_resilience.py` twice and executes it once.

Three things the staged file does that this item did not ask for, each with a
measurement behind it rather than a preference.

Both `paths` lists are deleted rather than rewritten. This item asked for "the
directories the suite covers", and an audit hook over one full `pytest tests/`
run showed that is `.github/`, `db/`, `docs/`, `mcp/`, `pipeline/`, `prompts/`,
`site/`, `skills/`, `tests/` and `tools/`: every directory in the repository.
A filter naming all of them is not a filter. This still deletes the `paths`
halves of items 12 through 16, which is what the recommendation above wanted.

Node is installed. Seven of the 47 are `*.test.mjs` and every Python wrapper
that runs them calls `pytest.skip` when node is missing, so without
`actions/setup-node` the account, markdown, unsubscribe and waitlist halves
would be named by the suite and still never run. A skip is not a pass. This
item's own smoke test passed `node --test tests/*.test.mjs` by hand and the
workflow form of that was never specified.

The coverage is under test. `tests/test_ci_coverage.py` pins today's uncovered
set so it can shrink and cannot grow, and it asserts that the staged file
covers all 47. Both halves were confirmed red on a deliberate break. The gate
caught itself on its first run, because a new test file in `tests/` that no
workflow names is exactly what it is built to catch and it was one.

**And it makes `subscriber-list.yml` unnecessary rather than wrong.** That
file is filed in `.github/workflows-pending/README.md` and has no numbered item
on this page, which is its own small instance of what the note at the top of
item 17 says about this register's numbering.
`subscriber-list.yml` runs `tests/test_waitlist.py` and
`tests/test_unsubscribe.py` and nothing else, both of which the suite step
covers. Apply the structural `checks.yml` and that file can be dropped. Apply
`subscriber-list.yml` alone if the one-step change is too large to take today.
Applying both leaves two duplicate steps on every pull request.

---

---

---

### 18. ADR-13's panel runs in CI, or three documents stop saying it does
### (amended 2026-10-03 second window: three reviewers, not two)

**Queued 2026-10-03 by the engineer seat.
INC-2026-10-03-panel-reviewer-claims-a-ci-step-it-never-had.**

Numbered 18 because 17 is the highest on this page today, and this page has
carried two items numbered 4 and two numbered 5 before, so the number is stated
rather than counted (incident 29).

The panel's first reviewer shipped on 2026-10-02 with a build note saying its
file half "runs on every pull request that touches `skills/**` or
`db/schema.sql`, inside the skill-receipts step of `checks.yml`". It does not.
That step runs `tests/test_skill_receipts.py` and nothing else, and neither
reviewer's file is in either `paths` list. So 46 tests have never run in CI, and
the thing only CI can hold about a reviewer in this organization, that its SQL
still resolves against `db/schema.sql`, has never been held.

**Why these tests belong in CI when the reviewers mostly do not.** No Postgres
exists in CI here, so the SELECTs are parsed with libpg_query and every relation
and column is resolved against the schema, exactly as `tools/graph_audit.py`'s
ten SELECTs already are in the `the graph audit's SQL still matches the schema`
step. A migration that renames `claim_links.to_claim` or
`claims.interpreted_at` should turn a pull request red, not turn a 16:00 UTC
cron silently useless.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. `skills/**` and `db/schema.sql` are already in both lists;
these five lines go in both, beside the existing `tools/` and `tests/` entries.

```yaml
      - "tools/panel.py"
      - "tools/panel_provenance.py"
      - "tools/panel_adversary.py"
      - "tools/panel_validator.py"
      - "tests/test_panel_provenance.py"
      - "tests/test_panel_adversary.py"
      - "tests/test_panel_validator.py"
```

Second, two steps. They go after `every skill can be registered, and the
registrar's SQL matches the schema` from item 12, because the panel reads what
the registrar writes and a reader wants them in that order. Item 12 is not a
prerequisite: these two steps stand alone if item 12 is still unapplied, and in
that case they go after the graph audit step instead, which is the last step in
the `digest-budget` job today.

```yaml
      # 2026-10-03, ADR-13. The panel's two built reviewers send five SELECTs
      # and two INSERTs between them, and no CI job in this organization can
      # execute any of them. So they are parsed with libpg_query and every
      # relation and column is resolved against db/schema.sql, the same
      # instrument the graph audit step above uses, for the same reason: a
      # renamed column would otherwise be discovered by a daily cron going
      # quietly useless rather than by the pull request that renamed it.
      #
      # Two reviewers, two steps, on purpose. A single step would go red for
      # either and the log line is where a reader learns which.
      - name: the provenance reviewer's SQL matches the schema, and its duties still decide
        if: always()
        run: python3 -m pytest tests/test_panel_provenance.py -q

      - name: the adversary reads the graph in the direction ADR-10 fixed
        if: always()
        run: python3 -m pytest tests/test_panel_adversary.py -q

      - name: the validator judges the trial receipt against the text under review
        if: always()
        run: python3 -m pytest tests/test_panel_validator.py -q
```

**Why there is no third step running the reviewer itself, which this entry
nearly got wrong.** The obvious companion to item 12's `python3
tools/skill_registrar.py --files-only` is `python3 tools/panel_provenance.py
--files-only`, and the first draft of this entry queued it and claimed it exits
0. It exits 2, over the real library, and always will. The reviewer's three
states are `0 nothing wrong`, `1 a finding`, `2 something could not be
measured`, and duty 2 is structurally unmeasurable for every skill until the
per-section claim id format lands, so that step would be red on every pull
request forever and would teach every seat to ignore it. The useful half of it
is a test instead:
`tests/test_panel_provenance.py::test_no_skill_on_this_branch_fails_a_file_level_check`
asserts that no skill carries a `fail` finding, which is the thing that should
block a merge, and lets an honest `unknown` through. It was added in the same
pull request as this entry.

**What must NOT be added, and this is the other half a reader will be tempted
by.**
There is no step that runs `tools/panel_adversary.py`. Nothing that reviewer
decides is in a SKILL.md: its whole input is the claim graph, so with no
credential it can only report that nobody asked the graph, and a green step
named for it would read as the graph agreeing.
`tests/test_panel_adversary.py` asserts that `checks.yml` never names that
command, so adding it turns the second step above red.

**Smoke-tested from the seat, as far as a seat can.** Both commands were run in
this run's sandbox against the real six skills: `tests/test_panel_provenance.py`
is 47 passed and `tests/test_panel_adversary.py` is 43 passed. Each was also
confirmed to fail on purpose, against a deliberately renamed column in its own
reviewer's SQL, and the adversary's suite was confirmed to fail against four
more deliberate defects: the threshold moved off the schema's 0.7, the edge read
in the wrong direction, the file dropped from the Modal image, and an
un-interpreted claim downgraded from `unknown` to a note. The steps cannot be
smoke-tested as a workflow on a branch, because the seat cannot push the file.

**Cost.** $0. No key, no network, no database.

**Amended 2026-10-03, same day, second window: the third reviewer.**
`tools/panel_validator.py` completes ADR-13's panel, so this entry now asks for
three steps rather than two and seven path lines rather than five. Amended in
place rather than queued as item 19, because an unapplied entry about exactly
this subsystem is one hand for the chair instead of two, and because a reader
who applied item 18 and then met a separate item 19 about the same two lists
would reasonably wonder which was current. `tests/test_panel_validator.py` is 66
passed in this run's sandbox and the whole suite is 848 passed, 9 skipped.

**And the reviewer command, which this entry can now offer for one of the
three.** The paragraph above explains at length why there is no step running
`tools/panel_provenance.py --files-only` (it exits 2 forever, because duty 2 is
structurally unmeasurable) and none running the adversary at all (it holds no
database credential, so a green step would read as the graph agreeing). The
validator is different in kind: **every finding it makes is a fact about a file
in the repository**, so its `--files-only` verdict is its whole verdict, and
`tests/test_panel_validator.py::test_the_files_only_half_and_the_live_half_return_the_same_verdict`
asserts that rather than claiming it.

It is still **not** queued as a step, and the reason is the same arithmetic that
killed the first one: it exits 1 today, on every pull request, because all six
skills on main say `status: active` with no eval behind them (ADR-36 part 2). A
step that is red on every pull request teaches every seat to ignore it, which is
worse than no step. The useful half is in the suite instead, as
`test_no_skill_on_this_branch_fails_a_check_this_reviewer_invented`, which
asserts that every `fail` over the real library traces to a sentence in ADR-36
and nothing else. **The day the skill seat's evals merge, this becomes the one
reviewer worth running as a command**, and that is the signal to come back to
this paragraph rather than a thing to do now.

### 19. The eval harness's own `--check` gate runs in CI, or its docstring stops calling itself one

**Queued 2026-10-04 by the engineer seat.
INC-2026-10-04-eval-check-gate-claims-a-ci-step-it-never-had.**

Numbered 19 because 18 is the highest on this page today, and this page has
carried two items numbered 4 and two numbered 5 before, so the number is stated
rather than counted (incident 29).

`tools/skill_eval.py`'s `conformance` carries this sentence, written the day the
harness was: "Its own function so `--check` can be a CI gate over every skill's
eval file without a key, a model or a dollar." Nothing runs it. Neither
`tools/skill_eval.py` nor `tests/test_skill_eval.py` is in either `paths` list
in `checks.yml`, and no step invokes either one. Fourth sighting of the shape
INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had named first.

**Why it belongs in CI, specifically.** The gate needs no key, no model and no
dollar, which is the whole reason `conformance` is a separate function. And the
thing it holds is a cross-seat seam: the suites are the skill seat's files, the
reader is the engineer's, and the two were written to different contract
documents, which is how eight suites spent four days unrunnable
(2026-10-03 urgent ledger entry, fixed in the reader on 2026-10-04). A pull
request that adds a suite the reader cannot run should be red on that pull
request.

**Two edits to `.github/workflows/checks.yml`.**

First, the paths. `skills/**` is already in both lists; these two lines go in
both, beside the existing `tools/` and `tests/` entries.

```yaml
      - "tools/skill_eval.py"
      - "tests/test_skill_eval.py"
```

Second, two steps, after the skill-receipts step. The exit codes matter and the
second step is written around them: `--check` exits 0 when every skill carries a
conformant suite, **2 when some skill carries none**, and 1 when a file exists
and is malformed. Unmeasured is an honest state under ADR-36 and must not turn a
build red, so 2 is accepted explicitly rather than by `|| true`, which would
accept 1 as well and make the step decorative. Today every skill is in state 2,
so this step passes while saying so in its log.

```yaml
      # 2026-10-04. `conformance` in tools/skill_eval.py was written to be this
      # step and never was one. It parses every skills/*/evals/evals.json,
      # resolves each registered model id against pipeline/budget.py's table,
      # and holds the one rule the harness must never satisfy on an author's
      # behalf: rule 1 of docs/product/skill-validation.md section V5, the
      # pre-registered policy. No key, no model, no network, no dollar.
      - name: the eval harness still measures what it should
        if: always()
        run: python3 tools/skill_eval.py --smoke

      # Exit 2 is "some skill has no suite yet", which is ADR-36's draft state
      # and not a failure. Exit 1 is a suite that exists and cannot be run.
      # Written out rather than `|| true`, which would swallow both.
      - name: every eval suite in the library can actually be run
        if: always()
        run: |
          python3 tools/skill_eval.py --check || status=$?
          if [ "${status:-0}" = "2" ]; then
            echo "some skills carry no suite yet, which ADR-36 calls draft"
            exit 0
          fi
          exit "${status:-0}"
```

The `--smoke` step is the cheaper half and the one worth having first: it runs
the whole measurement path against a scripted model, 24 calls and $0.00, and
it already asserts the arithmetic of the verdict rule. It has been a command
nobody runs since 2026-09-30.

### 19, amended 2026-10-04 (second window): two more files, and the module whose test file did not exist

Amended in place rather than queued as item 20, for the reason item 18 was
amended in place: the same two `paths` lists, in the same workflow, about the
same subsystem. A reader applying item 19 and then meeting a separate item 20
about those lists would have to work out which is current.

`INC-2026-10-04-the-property-was-checked-at-the-wrong-unit` and
`INC-2026-10-04-supersession-dropped-the-branch-it-superseded`.
`tools/skill_triggers.py` names `tests/test_skill_triggers.py` in its own
docstring as the thing that holds its one dangerous property, which is that no
maintenance line it writes may read as a request to fetch a paper. That file
was on PR #153's branch, unmerged since 2026-09-30, and this run wrote a second
copy before finding it. Both are merged here: 62 tests, no database, no model,
no network. Neither copy ran anywhere, and writing the second one found the
property false at the channel every line passes through.

`tools/skill_gate.py` and `tests/test_skill_gate.py` arrive in the same merge,
which is the subject of item 20 below.

So four paths rather than two, in **both** lists:

```yaml
      - "tools/skill_eval.py"
      - "tools/skill_triggers.py"
      - "tests/test_skill_eval.py"
      - "tests/test_skill_triggers.py"
```

And one more step, beside the two above. It takes no key and no model, and it
is the only thing in CI that would notice if a queue line started asking
`pipeline/reading_queue.py` to re-fetch a paper the corpus already holds:

```yaml
      - name: the staleness triggers, and the fetch request they must never write
        if: always()
        run: python3 -m pytest tests/test_skill_triggers.py tests/test_skill_eval.py -q
```

Both files are pytest, so one step covers them and `requirements-dev.txt` is
already installed by the step above. Verified in this run's sandbox: 62 passed
for the triggers, 95 passed for the harness, and the whole suite 976 passed, 1
skipped.

### 19, amended 2026-10-05: the step's log grew a third kind of line, and the suites need two edits before it can go green

Amended in place for the same reason as the 2026-10-04 amendment: same two
`paths` lists, same workflow, same subsystem. No new paths and no new steps.
What changed is what the second step prints and what makes it red.

`INC-2026-10-05-the-rewrite-staled-every-coverage-claim`. `--check` now also
resolves every task's `sections` list against its skill's `## ` headings. Three
kinds of line come out of it, and only one of them is a failure:

- `failing:` a suite that cannot be run. Now includes a `sections` entry naming
  a string that is no heading of that SKILL.md, which is a false coverage claim.
- `unmeasured:` a skill with no suite. ADR-36's draft state, exit 2, not red.
- `finding:` a heading no task exercises. Printed, never red, because the suite
  contract itself calls it a finding rather than an error.

It also prints one summary line, `N of M sections are exercised by at least one
task`, which is the number ADR-38's per-section `Validation:` tag needs.

**The sequencing an applier has to know.** Measured this run against all three
open skill-seat branches, each with the eight real suites:

```
#151 skill/2026-09-30-section-validation   exit 1   8 policy,  0 sections,  0 findings
#159 alexandria-skill/2026-09-30-window    exit 1   8 policy, 17 sections,  7 findings
#152 skill/2026-09-30-delta-rewrite        exit 1   8 policy, 60 sections, 22 findings
```

So the step is red on every one of them today, and it was already red on all
three before this check existed, for the `policy` block none of the eight
suites carries. Applying item 19 before the skill seat fixes both is how `main`
goes red for the fifth time this quarter. The order that works: the skill seat
adds the `policy` block to its eight suites and re-points the `sections` lists
at the headings its delta rewrite actually wrote, `--check` goes to exit 2, and
then this item is applied. Both edits are filed in `docs/ideas.md` for that
seat, and neither needs the engineer.

### 20. The skill gate's workflow, which has been written and queued since 2026-09-30

**Queued 2026-10-04 by the engineer seat, second window.** Numbered 20 because
19 is the highest on this page today, and the number is stated rather than
counted (incident 29).

`.github/workflows-pending/skill-gate.yml` arrives on main with this pull
request, through the merge of PR #153. It is a complete workflow file in the
lane this repository keeps for workflows no agent may push, and
`.github/workflows-pending/README.md` describes what it does. Nobody has
applied it, and until somebody does, `tools/skill_gate.py` is 642 lines of
ADR-37 gate that runs nowhere.

**The edit is a move, not a diff:** copy
`.github/workflows-pending/skill-gate.yml` to `.github/workflows/`. Read the
pending lane's README first, because it states the two preconditions the file
itself cannot: the gate exits non-zero on a skill whose eval has not been run,
and no skill in the library has one yet, so applying this before the skill
seat's suites and results merge makes every skill pull request red. The same
arithmetic that keeps the validator out of `checks.yml` today (item 18's last
paragraph) applies here, and the day it stops applying is the same day for
both.

Verified in this run's sandbox: `python3 tools/skill_gate.py --smoke` passes
every clause, and `tests/test_skill_gate.py` is in the 976.

### 21. The quiet-send guardrail's schedule, which is a reader and not a rule

**Queued 2026-10-14 by the engineer seat, second run.** Numbered 21 because 20
is the highest on this page today, and the number is stated rather than counted
(incident 29).

`.github/workflows-pending/press-watch.yml` arrives on main with this pull
request. It is sprint 2026-10-12 item 5, and the thing it schedules is
`tools/press_watch.py`.

**What it is for.** The press can only fail on a Monday, and Monday is the one
day nothing reads whether it did. The check that answers the question already
existed and was already right: `tools/delivery_health.py` knows the press's
deadline, which is `PRESS_CRON` plus `PRESS_GRACE`, and refuses to call a
missing issue a fault before that window closes. The only scheduled reader of
that surface is the PM's daily standup, which on a Monday runs the weekly
ceremony instead. So on 2026-10-12 the press cron started, wrote no row, and
the gap sat undetected for eleven hours. On 2026-10-14 at 15:51 UTC the same
week was still missing, 52.9 hours past its deadline, and the company board
carried nothing about it.

**The edit is a move, not a diff:**

    git mv .github/workflows-pending/press-watch.yml .github/workflows/

**The two secrets it needs are already set in twelve workflows.**
`BOARD_API_URL` and `BOARD_RUNTIME_TOKEN`, the same pair every seat workflow
passes to `tools/board.py`. Nothing else: no model, no database credential, no
dependency install, because the tool is standard library only and reads the
receipt the site already publishes. The job is seconds of runner time a day on
a public repository, so applying it costs $0.

**What it does when it fires.** It posts one card to the board, titled with
the week the press owes, and exits 1 so the scheduled run goes red and GitHub
mails about it too. A week that stays missing gets one comment a day and no
more. Running it seven times in a week posts one card, because the week in the
title is the dedupe, and that is what makes the daily schedule safe.

Verified in this run's sandbox: `python3 tools/press_watch.py --dry-run`
prints the 2026-W41 card against the live receipt, and
`python3 -m pytest tests/test_press_watch.py -q` is 41 passed. Six of those
tests read this staged file, so an edit that drops the schedule or adds a
branch trigger turns the pull request that makes it red.

### 2026-10-11-writers-cap: The writer's cap, alone, because this one has already cost two runs

**Queued 2026-10-11 by the ExO agent**, split out of item 14. This is the
only item on this page whose change has a measured cost rather than a
predicted one, and it is one line.

```diff
-          claude_args: "--max-turns 150 --permission-mode bypassPermissions --model claude-opus-5"
+          claude_args: "--max-turns 350 --permission-mode bypassPermissions --model claude-opus-5"
```

in `.github/workflows/agent-writer.yml`. The anchor was checked this run
with `grep -c -F -e` and appears exactly once.

**350 and not 300.** Item 14 proposed 300 off a peak of 136. The seat has
since hit its cap twice, so 136 is not the peak and 151 is not either: a
capped run is a floor on demand and not a measurement of it. The rule in
[turn-caps.md](turn-caps.md) gives `2 x 151 = 302`, rounded up to 350. Both
cap hits came from free-running editorial work, not from a routing failure,
so rule 1 does not disqualify either as a measurement.

**What it has cost, twice.** Run 37226048547 on 2026-10-04 at 18:51 UTC and
run 37986599276 on 2026-10-09 at 20:22 UTC, both `"subtype":
"error_max_turns"` with `"num_turns": 151` against `--max-turns 150`. Both
died mid-edit. Ship-first saved the pushed work both times and both times
the unpushed increment went with the sandbox; on 2026-10-09 that was
`docs/ideas.md`, `docs/voice/ban-list.md` and
`docs/voice/reviews/2026-10-09.md`, dirty and unpushed at teardown.
Registered as
`INC-2026-10-09-the-writer-hit-the-cap-its-own-raise-queued-five-days-earlier`
by the PM seat. The 2026-10-04 hit was registered by nobody and this run
found it; see the ExO learning log for why.

**The first hit landed 54 minutes after item 14 was queued.** The
measurement was right, the proposal was right, the lane was right, and the
seat still lost work twice, because the fix needs a hand and the hand saw
one item asking for seven edits.

**Ordering.** See the overlap table at the top of the page, which is the
authority. `agent-writer.yml` is named by items 4a and 6 as well as by this
one. Item 4a edits a `prompt:` block and item 6 adds an `env:` line, so
neither sits inside a `claude_args` line and any order works. Item 14 no
longer touches this file, because this item is the writer row that was
removed from it.

**Cost.** $0 unless a run uses the turns. A cap is a tripwire, not a budget.

**The smoke run it owes.** `--max-turns` is a runtime change under
[runtime-changes.md](runtime-changes.md) and this seat cannot smoke it,
because creating the branch needs the push the runner's token refuses. The
obligation transfers to whoever applies it: the writer's next run should
print `--max-turns 350` in its log, and if it prints 150 the edit did not
land.

**Renumbered to a slug on 2026-10-18, and the collision that forced it is
this page's fifth.** This item was queued as "item 21" on 2026-10-11, in the
very pull request that added the rule "New items get a slug, never the next
number" to this page. Three days later a second item 21 was queued on main,
which is the quiet-send guardrail's schedule directly above. The two then met
in a merge and the conflict was committed unresolved for 21 hours
(`INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register`).
Both items are real and both are kept. This one takes the slug because it is
the one whose own author wrote the rule, and because nothing outside this
page cites it. References to "item 21" at lines 334, 349, 371 and 447, and in
`docs/agents/learning-log.md`, mean this item and are left as written with
this paragraph as their key.

**ROT, found 2026-10-18, and the diff below is rewritten.** The anchor said
`--max-turns 150` and `grep -c -F -e` returns **0** against the live
`.github/workflows/agent-writer.yml`, because commit `971944e5` of
2026-10-12 already raised that line to 225. The item's own closing paragraph
still says "if it prints 150 the edit did not land", which was true when it
was written and is now the wrong test.

**And the item can no longer do what it was queued to do, which matters more
than the anchor.** Since HQ decision 056 on 2026-10-17 the writer's governing
cap is `[runtime].max_turns` in its host manifest, and that still reads 150.
Applying the diff below changes the cap for a `workflow_dispatch` and leaves
every real run at 150. **So this item is necessary and not sufficient**, and
its other half is ask 4 of the 2026-10-18 entry in
`docs/agents/hq-relay.md`. See
`INC-2026-10-18-the-writers-cap-raise-governs-a-door-nothing-opens`.

```diff
-          claude_args: "--max-turns 225 --permission-mode bypassPermissions --model claude-opus-5"
+          claude_args: "--max-turns 350 --permission-mode bypassPermissions --model claude-opus-5"
```

The new anchor was checked with `grep -c -F -e` against the live file on
2026-10-18 and appears exactly once. The test for whether it landed is now
that the writer's next dispatched run prints `--max-turns 350`, and if it
prints 225 the edit did not land.


## Not queued here, because it needs a key rather than a hand

The GitHub App token-mint step (ADR-27) is the change that makes this
whole page unnecessary. It is written out in
[app-identity-handover.md](app-identity-handover.md) rather than here,
because it is blocked on `APP_PRIVATE_KEY` existing, not on someone
applying an edit. `APP_ID` is already set.

**`modal-deploy.yml` needs two secrets and then a hand** (queued
2026-10-08 by the engineer seat). The file is written and waiting in
`.github/workflows-pending/modal-deploy.yml`, with its full section in
that directory's README, so it takes the better of the two lanes above
and the owner's part is a `git mv`. It is on this page as well because
the `git mv` alone leaves it broken: it reads `MODAL_TOKEN_ID` and
`MODAL_TOKEN_SECRET`, and neither repository secret exists today.

```bash
modal token new          # prints both halves
# then store them as repository secrets, names exactly:
#   MODAL_TOKEN_ID
#   MODAL_TOKEN_SECRET
```

Why it matters enough to be here: `grep -rln "modal deploy"
.github/workflows/` returns nothing, so no merged change to `pipeline/`
has ever reached production without somebody remembering a command.
This is the gap behind the `urgent` ledger entry of 2026-10-08 and
behind `triage` sitting 2.9 days behind `main` that morning.

Costs nothing. Modal's free plan already runs these apps and a deploy is
not a new paid service. The provider keys the rehearsal spends stay in
Modal's secret store and must not be added to GitHub: the runner holds a
token that can deploy and nothing that can spend.

**Nothing is blocked on this.** `tools/deploy_gate.py` runs the same
ladder by hand today, with no Actions and no secret, which is the half
this seat could ship alone.

## Applied and deleted

- **Item 2, the PM's daily cadence and ceremony cap** (queued 2026-09-19,
  cadence half applied 2026-09-23, cap half cancelled on measurement
  2026-09-30, **deleted 2026-10-04** as the 2026-09-30 run instructed).
  The Monday ceremony run of 2026-09-28 came in at 125 turns against a cap
  of 300, so there was never a shortfall. The item rotted three times
  before it was cancelled and it is the whole evidence behind the
  re-verification rule in `prompts/exo-agent.md` §5.
- **Item 4, the writer's cap goes to 200** (queued 2026-09-21, never
  applied, **deleted 2026-10-04 as overtaken**). The writer's measured
  peak is now 136, so the rule asks for 300 and 200 would have been a fix
  that left the seat short. Replaced by item 14. Its ordering paragraph
  still said "no other item on this page touches `agent-writer.yml`",
  which stopped being true when item 4a was queued on 2026-09-21, and it
  passed every anchor check for thirteen days.
- **Item 11, the skill seat's cap goes to 200** (queued 2026-09-27, never
  applied, **deleted 2026-10-04 as overtaken**). Measured peak is now 156,
  so the rule asks for 350. Replaced by item 14.

- **The open-routed step falls back instead of failing the run** (queued
  2026-09-20 as item 1b, incident 23, applied by the chair in commit
  2d3902d on 2026-09-24, verified against all four routed workflow files
  on 2026-09-27, and deleted from this page in the same run). Present in
  `agent-pm.yml`, `agent-market.yml`, `agent-okr.yml` and
  `agent-finance.yml`: each has `continue-on-error: true` on the
  open-routed step and gates the Claude step on its outcome. **The chair
  shipped it in a stronger form than the queued diff**, and the
  difference is worth the next run's attention. The diff proposed
  `steps.openrouted.outcome == 'failure'` and the live files read
  `steps.openrouted.outcome != 'success'`, which also covers `cancelled`
  and `skipped`. A step that is cancelled has done no work either, so
  the queued version would have lost the run in exactly the case the
  item was written to prevent. Recorded here because this page's habit is
  to note where the hand improved on the proposal, and because the third
  edit in the item, the `open-routed attempt:` line in the tripwire
  summary, was **not** applied: the failure is therefore fixed and still
  invisible in `gh run list`, which is incident 8's lesson left half
  learned. It is not re-queued, because the OPENROUTE secrets are absent
  from this repository and nothing is currently routed, so the line would
  report on a path that cannot run. Re-queue it in the same run that
  re-adds the key.
- **Turn caps, re-derived from run logs** (queued 2026-09-18, applied by
  the chair in c6bc2c4, verified against the workflow files on
  2026-09-18). The chair went further than the queued numbers on several
  seats.
- **The three remaining short caps** (queued 2026-09-18 evening, applied
  by the chair, verified against the workflow files on 2026-09-19).
  frontend is at 600, pm at 300, security at 250.
- **The no-ship tripwire, all twelve agent workflows** (queued
  2026-09-18 as item 1, applied by the chair in commit 440163a on
  2026-09-20 at 12:34, verified against all twelve workflow files on
  2026-09-21). Present in every `agent-*.yml`, in a better form than the
  queued diff: the chair's version came from the company template and
  ships a `Post run report` step beside it, which posts the run's result
  to Slack when `SLACK_WEBHOOK_URL` exists and exits quietly when it does
  not. Three things are worth the next run's attention. The webhook guard
  is inside the script rather than in the step's `if:`, with a comment
  explaining that a step cannot read its own `env:` block from `if:`, and
  that reasoning is correct. The tripwire's `exit 1` means a run can now
  be **red because it shipped nothing rather than because it crashed**,
  which is a new failure fingerprint for §2b to diagnose and it is
  recorded in the learning log. And the change reached twelve live
  workflows with no smoke run on a throwaway branch, which
  [runtime-changes.md](runtime-changes.md) requires, though three
  scheduled runs after it (engineer 14:40, exo 17:15, writer 18:20) all
  passed, so it worked. The law still binds the chair.
- **Container configuration for the frontend and engineer seats**
  (applied by the chair 2026-09-19, never queued here). `container:`,
  `credentials:` and `options: --user 1001:1001` against
  `ghcr.io/alexandrapaiz/alexandria-agent:latest`. Recorded as applied
  so the next run does not mistake it for drift. Incidents 17 and 18 are
  the two failures it took to get right.
