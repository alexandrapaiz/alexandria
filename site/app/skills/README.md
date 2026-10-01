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
| `contract` | number | `1` today. A reader that does not know the number should render pending rather than guess. |
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

An arm summary:

```json
"with_skill": {
  "n": 30,
  "mean": 0.8,
  "successes": 24,
  "interval95": [0.6143, 0.9229],
  "reads": "24 of 30"
}
```

`successes`, `interval95` and `reads` appear only when every score in the run
was 0 or 1, which is the case when every task had a hard check. A run that
included a rubric produces fractional scores, and then `mean` and `n` are all
there is. The interval is Clopper-Pearson, exact rather than normal, because at
these sample sizes the normal approximation is simply wrong.

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

## An example task file

`skills/<slug>/evals/evals.json`, written by the skill seat, never by the
harness or by the skill's own author where the library can help it. The
disjointness argument is in `docs/product/skill-validation.md` §2.

The six suites on `skill/2026-09-30-skill-evals` are the real thing and they are
the format of record: `suite_version`, `kind: treatment|control`, `form:
prompt|project`, `prompt`, and rubric criteria carrying 0/1/2 anchors. The
harness reads that shape and also the shorter one below, which it proposed on
the same day. `tests/fixtures/skill-eval-suite/evals.json` holds one task of
every form and check type the real suites use.

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
