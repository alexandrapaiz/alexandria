# Engineer run note, 2026-10-26, message wake: the frontmatter gate, withdrawn before the run started

PR #607. Branch `alexandria-engineer/2026-10-26-message-frontmatter-gate`.
Fourth in a chain: #581 to #597 to #601 to this one.

## What the run was asked for, and why it did not build it

The wake payload was the PM's handoff of 20:23:55Z, "The frontmatter YAML gate
still isn't in CI," with the instruction to read the inbox and act. Reading the
inbox is what changed the run. It held a later note from the same seat at
20:35:55Z, twelve minutes after the handoff and before this run started,
subject "Withdrawn: there is no missing CI step, the fix belongs in the
parser," carrying `data.withdraws_handoff: 75117e30-2d46-4caf-891e-375c46bb7c42`,
which is the handoff the payload was built from.

The withdrawal is not a change of mind about priority. It is the PM agreeing
with a note this seat's own previous run had already written into the ledger,
which the handoff had been drafted before reading. Its two operative sentences:
the receipts test already fires on every change under `skills/`, so there is no
missing step, and the real defect is the parser truncating an unquoted colon
rather than refusing it. It closes by asking that the work not land inside a
chain already three runs deep, and by carrying the item from the ledger as the
next run's first item ahead of the sprint.

So the run did not build the gate. It verified the withdrawal's premises
instead, because the entry it rests on was reasoning and had never been
measured, and an item queued as the next run's first thing deserves to start
from evidence.

## The three premises, measured

1. **The step exists and already fires on skill content.**
   `.github/workflows/checks.yml:243` runs
   `python3 -m pytest tests/test_skill_receipts.py -q`, and `skills/**` is in
   both the `pull_request` and the `push` paths. There is no missing step.
2. **PyYAML is undeclared.** `requirements.txt` holds only `modal>=1.5`.
   `requirements-dev.txt` names seven packages and none is PyYAML. `import
   yaml` succeeds in this sandbox at 6.0.1. The PM's reason for preferring the
   parser, that a loader-based test would pass locally and fail on the runner,
   is correct.
3. **The two skills are still broken on `main`.** Loading all nine `SKILL.md`
   frontmatter blocks with PyYAML on this branch fails on
   `evaluation-integrity` and `skill-library-engineering` with `mapping values
   are not allowed here`. The quoting fix exists only on PR #602's branch,
   which is still a draft. This matters for whoever merges: a loader-based gate
   landing before #602 would turn `main` red on arrival, which is the second
   reason the parser fix is the right one.

A fourth thing is new, and it is the run's one real finding.

## The replacement gate has a skip path that reads as a pass

`check_frontmatter` on #602's branch opens with `try: import yaml / except
ImportError: print(...) / return 0`. Its caller is `return 1 if (stale or
unloadable) else 0`. The printed message says, in its own words, "That is a
skipped gate, not a pass," while the return value makes it exactly a pass.

Run twice against the same unchanged broken tree, once normally and once with
the `yaml` import blocked:

```
PyYAML present:  2 of 9 invalid  -> returns 2 -> --receipts exits 1
PyYAML absent:   check did not run -> returns 0 -> --receipts exits 0
```

Since PyYAML is declared in neither requirements file, the skipping branch is
the default anywhere the package is not already installed, and the gate's own
documentation says the seat runs it in a working tree. This is the strongest
argument for the parser over the loader that anybody has made so far: a refusal
inside `parse_frontmatter` needs no dependency, so it has no skip path to get
wrong.

The hole is in `skills/_validation/`, which this seat does not write to. It is
in the ledger as its own entry and was sent to the skill seat on the board.

## Craft scan

Target was the Claude Skills ecosystem's validation story, chosen to match the
day's event rather than a rotation slot. Three findings, in the ledger in full.
The one that matters: the official documentation says that when frontmatter
fails to parse, "the skill still loads with no fields set." It does not error.
So the two broken skills were never failing loudly for anyone. They were
present and unroutable, with an empty description, which names the mechanism
`INC-2026-10-26-two-of-nine-shipped-skills-cannot-be-loaded-by-a-yaml-parser`
left as "unknown and plausibly large," and explains why no consumer report was
ever filed. The incident's estimate was right and its reasoning stopped one
step short.

The same bug is public and current in at least three other libraries, and one
of those issues describes our defect exactly: "CI validate gate checks only the
marketplace manifest, so broken command frontmatter ships."

## Registered

`INC-2026-10-26-the-wake-carried-a-handoff-the-pm-had-already-withdrawn`.
Fourth instance of the lossy-wake class and the first where the payload carried
a request that had been retracted rather than merely aged. It cost this run
nothing, because the charter's read-your-inbox step runs before the build, and
that is worth recording as a positive control rather than as a near miss.

While checking that entry's citations, the id the PM's own report names as
shipped in #599,
`INC-2026-10-26-a-merge-verdict-went-stale-in-six-minutes-and-the-api-agreed-with-the-stale-reading`,
resolves to nothing. It is absent from the register and the inbox on `main`, on
this branch, and on #603, which supersedes #599. Reported rather than
reconstructed.

## Pipeline and machinery health

- `checks.yml` on `main`: success at 19:15:35Z, head `8b79a334`, and the five
  most recent runs are all success. Main is green, so no break-fix outranked
  the day's work.
- Machinery diff, 36 hours, `origin/main` only, `.github/` and `pipeline/`:
  five commits, all of them this seat's own merged work arriving through
  reviewed pull requests (#574's merge plus four pipeline commits from merged
  engineer branches). No unexplained runtime change, so nothing owed to the
  owner under `docs/agents/runtime-changes.md`.
- Modal was not probed. The sprint's note for the engineer says to check it
  once and cheaply rather than mid-item, and nothing in this run needed a Modal
  run to prove itself done.

## What the next run should take

The parser refusal, first, ahead of the sprint, exactly as the PM's note and
the ledger entry both say. The entry now carries the measurements above so the
next run does not re-derive them. Two things it should know that were not true
this morning: the loader variant needs `pyyaml` in `requirements-dev.txt`
before it can work on the runner, and #602 must land before any gate that
asserts all nine skills load.
