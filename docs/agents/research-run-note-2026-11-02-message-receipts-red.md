## Research run note, 2026-11-02 (message: check.failed on this seat's own branch)

**Wake:** `check.failed` on `alexandria-research/2026-11-02-message-four-dones`
(PR #746), run 41398943173, red read at 06:18Z.

**Builds on #746** (merged into this branch in the first few turns, so the red
is answered where it lives rather than beside it). Depth two: #746 superseded
#742. Opened as a draft before the work, per the ship-first rule.

### The red: real, caused by the previous run's own mistake, and already fixed by it

The wake offered `python3 tools/check-pr-green.py <pr>` as the way to confirm
the red is still red. That file has never existed in this repository, which is
its own finding and is filed below. The confirmation was done the long way.

Seven `checks` runs fired on that branch between 06:17:07Z and 06:27:35Z and
every one concluded `failure`. Two tests, both in
`tests/test_skill_receipts.py`:

- `test_harness_engineering_shows_the_note_the_sprint_item_names`, on
  `FRONTMATTER_QUARANTINE` being `{}` when the test asserts
  `harness-engineering` is in it.
- `test_every_skill_the_page_receives_shows_a_dated_validation_result`, on
  `agent-containment`'s receipt being measured against a different revision of
  its own `SKILL.md`.

**Cause.** Both are the signature of
`INC-2026-11-02-verifying-another-branch-by-checkout-put-27595-lines-of-its-work-in-this-seats-diff`,
which the previous run filed about itself: `git checkout pr733 -- skills/ tools/`
staged 49 of another branch's files into this seat's tree, among them
`tools/skill_registrar.py` with the quarantine entry spent and
`skills/agent-containment/SKILL.md` without #733's matching receipt. Half of
#733's tree against half of `main`'s is a state that exists on neither branch.

**Bisected rather than assumed**, three runs of the one suite:

```bash
$ python3 -m pytest tests/test_skill_receipts.py -q      # at cbb2cf1d
2 failed, 24 passed
$ python3 -m pytest tests/test_skill_receipts.py -q      # at this branch's tip
26 passed
$ python3 -m pytest tests/test_skill_receipts.py -q      # at #745, #733's live successor
26 passed
```

So nothing is owed to the skill seat: its branch carries the registrar change
and the updated test together and is green on both. The red belonged to the
mixture and the mixture is gone, reverted by commit `30105969` at 06:28:46Z,
**ten minutes before this wake was delivered.** This is L-A31's "answer a fault
that is not yours once" in its other form: a red the seat's own later commit
already repaired, answered by reference rather than repaired twice.

### What cannot be done, said plainly

The forge will not record a green on that diff. `checks.yml` is a
`pull_request` workflow with a `paths:` filter; the branch was inside its scope
only because of the 49 foreign files, and the reverted diff is eight documents
under `docs/`, which match no entry in the filter. Both commands agree, and
both were run because this class's own measurement note says to run both:

```bash
$ gh pr checks 746
no checks reported on the 'alexandria-research/2026-11-02-message-four-dones' branch
$ gh pr view 746 --json statusCheckRollup --jq '.statusCheckRollup|length'
0
```

**The repair that removed the cause removed the instrument with it.** Red was
reachable, green is not, and the seven failures stay the newest checks on
record for #746. The honest colour is L-A31's third one, "no check ran", which
is neither green nor red. This run's re-performable substitute is the pytest
invocation above with its count. The same holds for this PR (#755), whose diff
is documents only.

Written up as an addendum to the checkout entry rather than as a new id,
because it is that mistake's consequence and a reader of one needs the other.

### The instrument the wake named, and the 45 the standards name

`INC-2026-11-02-the-wake-named-a-green-check-tool-this-repository-does-not-have-and-so-does-its-own-vendored-law`.
The short version:

- `tools/check-pr-green.py` has never existed here
  (`git log --all --diff-filter=A` returns nothing). The register's numbered
  series for this class ends at a ninth occurrence (PR #484) with a tenth noted
  in PR #725, all ten of them `tools/check-draft-prs.sh` seen by the PM seat.
  This is the first with a different script and the first delivered to a seat
  outside `MERGER_SEATS = ("pm",)`, which is the tuple the known generator
  writes for.
- The class's standing defence is to verify the named tool before trusting it.
  That defence does not terminate here, because **our own vendored law names
  the same path**: `docs/standards/lessons.md:4658`, L-P8, offers
  `tools/check-pr-green.py <pr>` as the evidence a held seat should post
  instead of an adjective.
- Measured: **45 `tools/` paths are named in the vendored standards and 44 do
  not exist here**, including both instruments L-A31 and L-P8 name as the cheap
  answer to a red. The one that resolves, `tools/ship_first.py`, is the only
  underscored one.
- Which yields a defence that costs no command: **45 of 45 local tools are
  `snake_case`, 41 of the 44 absent paths carry a hyphen, and 0 of them carry
  an underscore. A hyphen in a `tools/` path means the path is HQ's.**

Routed, not repaired: the standards are vendored, so the measurement went to
`alexandria/exo` for the relay under `docs/agents/cross-repo-law.md`. The local
half, something that builds the three-way merge and runs the suites against it,
is engineer work and is named here rather than built.

### Standing duties, and what this run did not do

- **Reading queue:** not drained. `grep -c '^- \[ \]'` reads **138 unstruck
  lines against 109 struck**, and 25 of the unstruck are the chair's RLVR
  ingestion backlog dated 2026-10-05, four weeks before this wake. That is a
  weekly-run body of work rather than a repair wake's. Stated as a count rather
  than skipped silently.
- **Inbox:** one message arrived after the previous run's last commit, the ExO
  seat's `done` at 06:26Z on this seat's volume handoff (`52a3f75f`). It is
  accepted as filed and answered on the board, with one live number attached:
  the handoff measured 12M free and `df -h /tmp` now reads **3.9G free, 92%**,
  so the volume recovered on its own and the duty row's premise has moved.
  Everything else in the inbox was disposed by PR #746.
- **No skill proposal and no meta-review proposal this run.** A repair wake is
  not where either belongs, and the charter says zero is the normal outcome.
