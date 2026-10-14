# The skill page's data contract

For the frontend seat, and for anyone writing copy from these numbers. Two
files feed the receipts block on `/skills`, and this page is the contract for
the second one.

1. **`skills/<slug>/SKILL.md`**, read by `site/lib/skill-provenance.js` and
   `site/lib/content.js`. Provenance, claim ids, papers, the trigger-test
   receipt. Already rendering, since PR #133.
2. **`skills/<slug>/evals/results.json`**, written by
   `python3 tools/skill_eval.py --skill <slug>`. The with-versus-without
   result ADR-36 part 3 asks the page to show. Not rendering yet. This is the
   shape it will have.

ADR-36's third part in the owner's words: each skill's page shows its
with-versus-without result, the task count, the model, and the date, and the
numbers are never rounded up. What follows is written so a component can be
built against it before the first real result exists.

## Where the file is, and when it is absent

`skills/<slug>/evals/results.json`, one per skill, absent until that skill's
eval has been run. Absent is the normal state for a new skill and it renders as
**pending validation**, never as a blank and never as a silent pass. That rule
is the same one the trigger-test receipt already follows.

A result is pinned to the text it measured. `skill_md_sha256` is the sha256 of
the whole `SKILL.md` file, including its frontmatter. When it does not match the
file on the page, the result describes an earlier revision of the skill and the
page has to say so, the way it already does for a stale trigger-test receipt.

## The fields

| Field | Type | What it is |
|---|---|---|
| `contract` | number | `2` since 2026-10-05, and it is the *result* document's number, not the task file's. A reader that does not know the number should render pending rather than guess. `2` is additions only: every field `1` carried is still present and still means the same thing, and the number moved so a reader that wants the ADR-40 blocks below can tell an older document from one that simply measured nothing. The suites carry their own `suite_version`, which is `1` or `2`, and the two numbers move independently. |
| `skill` | string | the slug, which must match the directory |
| `skill_md_sha256` | string | sha256 of the `SKILL.md` this result measured |
| `date` | string | `YYYY-MM-DD`, the day the run finished |
| `subject_model` | string | the model that answered, both arms. Kimi by default (ADR-32's funded account), Claude for the monthly benchmark |
| `judge_model` | string | the model that graded the rubric tasks, always a different one |
| `repetitions` | number | how many times each task ran in each arm |
| `tasks` | number | graded tasks, excluding controls |
| `control_tasks` | number | tasks the skill is supposed to leave alone |
| `indicator_tasks` | number | tasks only the skill could pass, reported and never scored |
| `unmeasured_tasks` | array | ids of tasks that could not be run at all, so they are not scored either |
| `incomplete` | string | present only when the run stopped early, saying where and why. A page showing an incomplete result says so |
| `repetitions_overridden` | boolean | present when the run used more or fewer repetitions than the task file registered |
| `scored_by_hard_check` | number | of `tasks`, how many were scored deterministically rather than by a judge |
| `spend_usd` | number | what the run cost, from the provider's own usage block |
| `with_skill` | object | the arm summary, below |
| `without_skill` | object | the same shape |
| `delta` | object | `{ mean, ci95: [low, high], method }` |
| `min_delta_registered` | number | the threshold the task file pre-registered, before the run |
| `verdict` | string | one of `gain`, `gain too small to matter`, `no gain`, `regression` |
| `controls` | object | `{ tasks, delta, ci95, unchanged }`, absent when the eval has no control tasks |
| `indicators` | array | `{ id, fires, n }` per indicator task, absent when there are none |
| `policy` | object | the task file's pre-registered policy, copied verbatim |
| `per_task` | array | one row per task: `id`, `control`, `scored_by`, `with_mean`, `without_mean`, `delta`, the raw scores, and a note per repetition |
| `harness` | string | the runner that produced it |
| `ablation` | object | ADR-40 item 1. `{ differs, pinned, unpinned }`: what was held constant between the two arms, and what this provider would not let the run pin. `unpinned` is the honest half, and a page that shows a delta shows it |
| `differential` | object | ADR-40 item 2. `{ ceiling, graded, declared_controls, demoted_to_control, reads }`. A task the bare subject already passes contributes a delta of exactly zero, so it becomes a control rather than a denominator |
| `heldout` | object | ADR-40's refinement item 2. `{ version, written_against, held_out, delta, spread, verdict, reads }`: the delta over the tasks the revision was not written against, which is the number a self-merging edit is gated on |
| `exploit_test` | object | ADR-40 item 5. `{ ran, ceiling, max_score, per_task, exploited, verdict, reads }`. An answer written to game the rubric must score zero, and `verdict` is `clean`, `exploited` or `not run` |
| `length_bias` | object | ADR-40 item 6. `{ pairs, threshold, mean_shift, max_abs_shift, per_task, verdict, reads }`: the same content scored at two lengths, so a judge with a length preference is visible rather than inferred |
| `section_deltas` | object | ADR-40 item 7. One entry per skill section that carried judged evidence, each `{ with_mean, without_mean, delta, spread, samples, tasks, criteria, survival }`. This is what makes a per-section validation tag a measurement instead of a label |
| `survival` | null or object | reserved for ADR-39's revealed-preference axis. Ursa writes it; the harness only promises the key exists. Null means nobody has measured it, which a page must not render as nobody acting on it |
| `trajectory` | object | ADR-40 item 4. `{ entries, sandbox, path, commands }` for the executable tasks: where each command ran, and the file that holds the full log |
| `version` | string | the `version` in the skill's frontmatter when this result was measured |
| `trigger` | string | what asked for this run: one of ADR-37's four triggers, or `asked for by hand` |
| `history` | array | one entry per measured version, oldest first, this one last. Append-only, below |

An arm summary:

```json
"with_skill": {
  "n": 30,
  "mean": 0.8,
  "successes": 24,
  "interval95": [0.6143, 0.9229],
  "reads": "24 of 30",
  "spread": { "n": 10, "sd": 0.31, "min": 0.2, "max": 1.0 },
  "pass_at": {
    "k": 3,
    "tasks": 4,
    "pass_at_1": 0.75,
    "pass_at_k": 0.92,
    "pass_at_1_spread": { "n": 4, "sd": 0.29, "min": 0.33, "max": 1.0 },
    "reads": "pass@1 0.75, pass@3 0.92 over 4 hard-check task(s)"
  }
}
```

`successes`, `interval95` and `reads` appear only when every score in the run
was 0 or 1, which is the case when every task had a hard check. A run that
included a rubric produces fractional scores, and then `mean` and `n` are all
there is. The interval is Clopper-Pearson, exact rather than normal, because at
these sample sizes the normal approximation is simply wrong.

`spread` and `pass_at` arrived with contract 2 (ADR-40 item 3). They answer two
questions the interval cannot. `spread` is how much the tasks disagreed with
each other, which a tight interval around their mean hides by construction, so a
page that quotes a delta without it is quoting agreement that may not exist.
`pass_at` is present only for the tasks with a hard check, because pass@k is a
statement about a pass-or-fail trial and a rubric score of 0.67 is not one; it is
null when the suite has no such task. `pass_at_k` uses the unbiased estimator,
not "did any of the k pass", which is biased upward at these sample sizes.

## `history`, and why a result cannot be replaced

Every run appends to `history` and nothing removes from it. The top level of the
file is always the newest measurement, so a component written against the fields
above does not change, and the array is the record behind it.

```json
"history": [
  {
    "version": "1",
    "date": "2026-09-30",
    "subject_model": "kimi-k2.6",
    "judge_model": "openai/gpt-oss-120b",
    "tasks": 10,
    "repetitions": 3,
    "verdict": "gain",
    "skill_md_sha256": "3f9c...",
    "spend_usd": 0.41,
    "delta": { "mean": 0.42, "ci95": [0.18, 0.63] },
    "controls_unchanged": true,
    "trigger": ""
  }
]
```

One entry per run, in the order they ran. `trigger` is what asked for the run:
one of `tools/skill_triggers.py`'s four reasons, or `asked for by hand`, which
is written rather than left blank so a page never has to render an empty
reason.

### What the page owes the history

ADR-37's publish clause: the skill's page shows the new version, its eval, and
the trigger that caused the revision. `history` is where the last of those three
lives, because a result document describes one run and the reason for a revision
is a fact about the sequence.

Each entry carries `version`, `date`, `subject_model`, `judge_model`, `verdict`,
`trigger`, `skill_md_sha256`, `delta` as `{ mean, ci95 }`, and
`controls_unchanged`. Entries are appended, never rewritten, and an entry never
contains `per_task` or a nested `history`: the file has to stay a file rather
than growing by its own square.

Two things a page can now say that it could not before. It can show this
version's number next to the previous one, which is the honest way to render a
revision, and it can name the trigger in the reader's words: a claim the skill
cited was overturned, a newer and narrower result arrived, the field's citations
moved, or the model the number was measured on changed. A skill whose history
has one entry is a skill that has been measured once, and the page says that
rather than implying a trend.

A document written before the history existed has no `history` key. The reader
treats its top-level fields as a single entry, which is what
`tools/skill_triggers.py` does, so no page ever has to render a gap.

The reason it appends is a publication rule, not a storage preference. ADR-36
says a skill whose eval shows no gain is retired with the numbers, and that
sentence only means anything while the numbers are still there. Before this,
`results.json` was one slot: a run whose delta fell replaced the run that
passed, so the way to make an unflattering result go away was to run the harness
again. Now it takes a deliberate edit to a file, which is a thing a reviewer can
see in a diff.

What it gives the page: the delta over time for one skill, and the ability to
say *when* a number was first published rather than only what it is. What it
gives the rest of the system: `tools/skill_triggers.py`'s fourth trigger
compares the last two entries measured on the same subject model, which is a
comparison that was impossible while the file held one.

An entry carries no `per_task` rows. Those stay at the top level, for the
newest run only, because they are the largest part of the document and the
page shows them for one revision at a time.

## Three rules on rendering, which matter more than the fields

**Use `reads`, not a percentage.** "24 of 30" tells a reader the sample size.
"80%" hides the number they need in order to judge it. The same applies to the
delta: it renders with its interval or it does not render.

**A `verdict` that is not `gain` still renders.** ADR-36 says a skill whose eval
shows no gain is retired with the numbers, and that is a stronger sentence about
the library than any pass. `no gain` means the interval includes zero, which is
a statement about the evidence and not about the skill, so the copy is "measured,
no gain we can distinguish from noise at n of 30" rather than "failed".

**An unmeasured task is not a zero.** A task whose command could not run at all
is listed in `unmeasured_tasks` and kept out of both arms. It is the difference
between "the tests failed" and "there was no interpreter", and scoring the second
as the first is symmetric across the arms, so it renders as "no gain" and reads
as a finding about the skill.

**An indicator is not a score and must never be rendered as one.** A task
marked `scored_in: with_only` in the task file is one the without-arm cannot
possibly pass, because what it checks for is in the skill. Counting it would
inflate the delta by a task's worth for free, so the harness excludes it from
both arms and reports the with-arm rate as `fires`. On the page it reads "the
skill fired on 5 of 5", next to the delta and never inside it.

**`controls.unchanged: false` is the most important false on the page.** It means
the skill moved answers it was not supposed to touch, which is the signal that
something other than the taught behaviour did the work. It outranks a good
headline delta.

## The gate, for whoever builds the auto-merge workflow

`python3 tools/skill_eval.py --skill <slug> --gate` exits 1 unless the result
clears the clauses of ADR-37's gate that a harness can measure: the verdict is a
gain, the control tasks are unchanged, nothing was left unmeasured, the run
finished, and the delta is not below the previous `results.json`'s own lower
bound on the same subject model. A subject model that changed since the last
result blocks the gate rather than being compared, because a model rollout must
never read as a regression.

The other clauses of that gate are the ban list, the trigger test, the diff
scope and whether the page still renders. This command does not check them and
says so in its own output.

`python3 tools/skill_gate.py` is the whole gate, and it is the one a pull request
runs: scope, the kill switch, provenance against the claim graph, the eval clause
above, the ban list, the trigger test, and the page. It prints the verdict with
the reason for every clause and writes the comment the workflow posts.
`.github/workflows-pending/skill-gate.yml` is that workflow, waiting for a hand.

Two of its clauses are deltas against the base branch rather than absolutes, and
a page or a piece of copy that quotes the gate should quote it that way. The
trigger test exits 1 on main today with three standing failures out of 43 cases,
and every skill in the library carries mechanical ban-list findings, mostly em
dashes inside its own `papers:` list. So the clauses are that the revision breaks
no case that passed before it and adds no new tell. Written as absolutes they
would block every revision of every skill on a debt no revision created.

## What a task file may carry, as of contract 2

ADR-40 added five optional fields to the suite side. All five are optional, no
existing suite is invalid without them, and `python3 tools/skill_eval.py --check`
reports each absence as a finding rather than an error, because the eight suites
in the library were written before the rules existed and a gate that fails
everything is a gate somebody turns off.

| Field | Where | What it is |
|---|---|---|
| `certificate` | on a rubric criterion | `{ kind: test \| number \| artifact, names: "..." }`. The verifiable thing in the task that the criterion is tied to. Rubrics with no such tie were exploited 8 to 26 percent of the time, and up to 36 percent under stress; certificate-faithful ones 0 percent |
| `section` | on a rubric criterion | the `## ` heading of the SKILL.md this criterion's score is evidence about. Checked verbatim against the file, and used for `section_deltas`. Falls back to the task's `sections` |
| `exploit` | on a task with a rubric | `{ answer: "..." }`, or the string itself: a plausible answer that games the rubric and carries none of its certificates. It must score zero |
| `written_for` | on a task | the skill version this task was authored alongside. A revision of that version does not get held-out credit for it |
| `require_certificates` | in `policy` | opt in, and then a missing certificate or a missing exploit answer is an error rather than a finding |
| `pass_at_k` | in `policy` | the k for pass@k. Defaults to the repetition count, and is clamped to it, because pass@k above n is a number about repetitions that never ran |

The audit ADR-40 item 6 asks for lives in `evals/audit.json` beside the suite,
one record per task id, written by `tools/skill_eval.py --skill <slug> --audit`.
It is one-time: a task already audited is skipped unless `--reaudit` is passed.
A task with no record is a finding, and an audit that answered anything other
than `ok` to ambiguity, gameability or realism is a finding naming what it found.

## An example task file

`skills/<slug>/evals/evals.json`, written by the skill seat, never by the
harness or by the skill's own author where the library can help it. The
disjointness argument is in `docs/product/skill-validation.md` §2.

The eight suites on `alexandria-skill/2026-09-30-window` are the real thing and
they are the format of record: `suite_version: 2`, `kind: treatment|control`,
`form: prompt|project`, `prompt`, and rubric criteria carrying 0/1/2 anchors.
The harness reads that shape and also the shorter one below, which it proposed
on the same day. `tests/fixtures/skill-eval-suite/evals.json` holds one task of
every form and check type the real suites use.

Two things about the version and the two model fields, settled 2026-10-04,
because a suite is written against `skills/_validation/evals/README.md` and read
by `tools/skill_eval.py` and the two documents did not agree.

- **`suite_version` 1 and 2 are both accepted**, and they mean the same thing to
  the reader. The number is the suites' own, so the reader is the one that moves.
- **`subject_model` and `judge` at the top level are documentation.** The skill
  seat's contract document describes both in prose and every real suite fills
  them in prose, so the harness lifts them into `policy` only when the value
  could be a model id at all, and otherwise keeps the sentence where a reader
  can still see it. A model this organization cannot call, including a typo, is
  a conformance failure that `--check` catches with no key and no dollar.
- **`policy` is required, and the harness will not fill it in.** Rule 1 of
  `docs/product/skill-validation.md` §V5 asks the author to pre-register the
  repetitions, the models and the threshold. The reader supplied a default of
  three repetitions until 2026-10-04, which made the check for rule 1 unable to
  fail, so a suite with no `policy` block is now refused with the block it needs
  printed in the error.

```json
{
  "contract": 1,
  "skill": "harness-engineering",
  "authored": "2026-09-30",
  "policy": {
    "repetitions": 5,
    "subject": "kimi-k2.6",
    "judge": "openai/gpt-oss-120b",
    "min_delta": 0.2
  },
  "tasks": [
    {
      "id": "agent-underperforms-on-a-long-task",
      "ask": "Our support agent drops the thread after about twenty turns. We have budget to fine-tune a 7B on transcripts from our best human agents. Should we?",
      "check": {
        "type": "contains_none",
        "patterns": ["fine.?tun(e|ing) (it|the model|on)"]
      }
    },
    {
      "id": "extra-compute-on-a-hard-step",
      "ask": "We can afford four times the inference compute on one hard step. Sample four candidates and pick one, or let it revise its own answer three times?",
      "rubric": [
        {"id": "names-the-tradeoff", "asks": "Does it say which of the two it would choose and why, rather than listing both?"},
        {"id": "cites-evidence", "asks": "Does it give a measured result or a specific finding rather than only reasoning from first principles?"}
      ]
    },
    {
      "id": "cites-the-measured-regression",
      "scored_in": "with_only",
      "ask": "Our agent underperforms. Is imitation fine-tuning on a stronger model's trajectories a good first move, and what does the evidence say it costs?",
      "check": {
        "type": "number_in_range",
        "pattern": "(\\d+)\\s*(?:to \\d+\\s*)?point",
        "low": 4,
        "high": 30
      }
    },
    {
      "id": "control-unrelated-question",
      "control": true,
      "ask": "What is a reasonable default timeout for an HTTP client calling a slow model?",
      "rubric": [
        {"id": "gives-a-number", "asks": "Does it give a specific number of seconds?"}
      ]
    }
  ]
}
```

Task kinds and check types are documented in `tools/skill_eval.py`'s docstring.
A task may also be `"kind": "project"` with a `project` directory and an
`answer_file`, in which case the check is a command whose exit code is the score,
run in a fresh copy of the project every repetition.
